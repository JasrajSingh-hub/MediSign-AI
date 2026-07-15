import abc
import asyncio
import io
import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List

import speech_recognition as sr
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("tts_service")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@dataclass
class ApiError(Exception):
    status_code: int
    detail: str


@app.errorhandler(ApiError)
def handle_api_error(error: ApiError):
    return jsonify({"detail": error.detail}), error.status_code


@app.errorhandler(400)
def handle_bad_request(_error):
    return jsonify({"detail": "Invalid request payload"}), 400


# =====================================================================
# REQUEST VALIDATION & SANITIZATION
# =====================================================================

def sanitize_text(text: str) -> str:
    """Removes HTML/XML/SSML tags to prevent SSML injection and normalizes whitespace."""
    text = re.sub(r"<[^>]*>", "", text)
    return " ".join(text.split())


def validate_speak_request(payload: Dict[str, Any]) -> Dict[str, str]:
    if not isinstance(payload, dict):
        raise ApiError(422, "Request body must be a JSON object")

    required_fields = ("text", "language", "session_id")
    for field in required_fields:
        value = payload.get(field)
        if not isinstance(value, str):
            raise ApiError(422, f"Field '{field}' is required and must be a string")

    sanitized_text = sanitize_text(payload["text"])
    if not sanitized_text:
        raise ApiError(422, "Text content cannot be empty after sanitization")
    if len(sanitized_text) > 500:
        raise ApiError(422, "Text content must not exceed 500 characters")

    language = payload["language"]
    pattern = r"^[a-zA-Z]{2,3}(-[a-zA-Z]{2,4})?$"
    if not re.match(pattern, language):
        raise ApiError(422, "Invalid language tag format (must match BCP-47, e.g. en-IN, en-US)")

    return {
        "text": sanitized_text,
        "language": language,
        "session_id": payload["session_id"],
    }


# =====================================================================
# IN-MEMORY RATE LIMITER
# =====================================================================

class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.history = defaultdict(list)

    def check_rate_limit(self, client_id: str):
        now = time.time()
        self.history[client_id] = [
            timestamp
            for timestamp in self.history[client_id]
            if now - timestamp < self.window_seconds
        ]
        if len(self.history[client_id]) >= self.limit:
            logger.warning(f"Rate limit hit for client: {client_id}")
            raise ApiError(429, "Rate limit exceeded. Please try again later.")
        self.history[client_id].append(now)


rate_limiter = InMemoryRateLimiter(
    limit=int(os.getenv("RATE_LIMIT_LIMIT", "60")),
    window_seconds=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")),
)


# =====================================================================
# TTS PROVIDERS ABSTRACTION LAYER
# =====================================================================

class TTSProvider(abc.ABC):
    @abc.abstractmethod
    async def synthesize(self, text: str, language: str) -> bytes:
        """Synthesize text to speech bytes."""


class EdgeTTSProvider(TTSProvider):
    async def synthesize(self, text: str, language: str) -> bytes:
        import edge_tts

        voice = await self._resolve_voice(language)
        logger.info(f"Synthesizing using EdgeTTS with voice: {voice}")

        communicate = edge_tts.Communicate(text, voice)
        audio_buffer = io.BytesIO()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])

        audio_data = audio_buffer.getvalue()
        if not audio_data:
            raise RuntimeError("Edge-TTS synthesizer returned empty audio payload")
        return audio_data

    async def _resolve_voice(self, language: str) -> str:
        import edge_tts

        voices = await edge_tts.list_voices()
        lang_lower = language.lower()

        for voice in voices:
            if voice["Locale"].lower() == lang_lower:
                return voice["Name"]

        lang_prefix = lang_lower.split("-")[0]
        for voice in voices:
            if voice["Locale"].lower().startswith(lang_prefix):
                return voice["Name"]

        for voice in voices:
            if voice["Locale"].lower() == "en-us":
                return voice["Name"]

        return voices[0]["Name"] if voices else "en-US-AriaNeural"


class Pyttsx3Provider(TTSProvider):
    def __init__(self):
        self._lock = asyncio.Lock()

    async def synthesize(self, text: str, language: str) -> bytes:
        async with self._lock:
            return await asyncio.to_thread(self._synthesize_sync, text, language)

    def _synthesize_sync(self, text: str, language: str) -> bytes:
        import pyttsx3

        engine = pyttsx3.init()
        try:
            voices = engine.getProperty("voices")
            selected_voice = None
            lang_lower = language.lower()
            lang_prefix = lang_lower.split("-")[0]

            for voice in voices:
                if hasattr(voice, "languages") and voice.languages:
                    if any(
                        lang_lower in str(item).lower() or lang_prefix in str(item).lower()
                        for item in voice.languages
                    ):
                        selected_voice = voice.id
                        break

            if not selected_voice:
                for voice in voices:
                    name_lower = voice.name.lower()
                    id_lower = voice.id.lower()
                    if (
                        lang_lower in name_lower
                        or lang_lower in id_lower
                        or lang_prefix in name_lower
                        or lang_prefix in id_lower
                    ):
                        selected_voice = voice.id
                        break

            if selected_voice:
                logger.info(f"Synthesizing using Pyttsx3 with voice: {selected_voice}")
                engine.setProperty("voice", selected_voice)
            else:
                logger.info("Synthesizing using Pyttsx3 with default system voice")

            fd, temp_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)

            try:
                engine.save_to_file(text, temp_path)
                engine.runAndWait()

                with open(temp_path, "rb") as file_handle:
                    audio_bytes = file_handle.read()

                if not audio_bytes:
                    raise RuntimeError("Pyttsx3 synthesizer returned empty audio payload")
                return audio_bytes
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        finally:
            engine.stop()


def get_pyttsx3_voices_sync() -> List[Dict[str, Any]]:
    import pyttsx3

    engine = pyttsx3.init()
    try:
        voices = engine.getProperty("voices")
        return [
            {
                "id": voice.id,
                "name": voice.name,
                "languages": getattr(voice, "languages", []),
                "gender": getattr(voice, "gender", "Unknown"),
            }
            for voice in voices
        ]
    finally:
        engine.stop()


def get_provider() -> TTSProvider:
    provider_name = os.getenv("TTS_PROVIDER", "edge").lower()
    if provider_name == "edge":
        return EdgeTTSProvider()
    if provider_name == "pyttsx3":
        return Pyttsx3Provider()

    logger.warning(f"Unknown TTS_PROVIDER '{provider_name}', falling back to 'edge'")
    return EdgeTTSProvider()


def resolve_executable(name: str) -> str:
    path = shutil.which(name)
    if path:
        return path
    if os.name == "nt":
        user_profile = os.environ.get("USERPROFILE", "")
        fallback_path = os.path.join(
            user_profile,
            "AppData",
            "Local",
            "Microsoft",
            "WinGet",
            "Links",
            f"{name}.exe",
        )
        if os.path.exists(fallback_path):
            return fallback_path
    return name


FFMPEG_PATH = resolve_executable("ffmpeg")
FFPROBE_PATH = resolve_executable("ffprobe")


def check_audio_dependencies():
    ffmpeg_found = shutil.which(FFMPEG_PATH) is not None or os.path.exists(FFMPEG_PATH)
    ffprobe_found = shutil.which(FFPROBE_PATH) is not None or os.path.exists(FFPROBE_PATH)

    if ffmpeg_found and ffprobe_found:
        logger.info(
            f"STT Dependency check: ffmpeg and ffprobe are available (ffmpeg: {FFMPEG_PATH}, ffprobe: {FFPROBE_PATH})."
        )
    else:
        logger.warning(
            "STT Dependency check warning: ffmpeg or ffprobe was not found! "
            "Audio transcoding and duration extraction will fail. "
            f"(ffmpeg found: {ffmpeg_found}, ffprobe found: {ffprobe_found})"
        )


check_audio_dependencies()


def get_audio_metadata(file_path: str, is_raw_pcm: bool = False) -> dict:
    cmd = [FFPROBE_PATH, "-v", "error"]
    if is_raw_pcm:
        cmd.extend(["-f", "s16le", "-ac", "1", "-ar", "16000"])
    cmd.extend(
        [
            "-show_entries",
            "format=duration",
            "-show_entries",
            "stream=codec_name,sample_rate",
            "-of",
            "json",
            file_path,
        ]
    )
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        metadata = json.loads(result.stdout.decode("utf-8", errors="ignore"))
        streams = metadata.get("streams", [])
        fmt = metadata.get("format", {})

        codec = streams[0].get("codec_name", "unknown") if streams else "unknown"
        sample_rate = streams[0].get("sample_rate", "unknown") if streams else "unknown"
        duration_raw = fmt.get("duration", "unknown")

        try:
            duration = f"{float(duration_raw):.2f}s"
        except ValueError:
            duration = "unknown"

        return {
            "codec": codec,
            "sample_rate": sample_rate,
            "duration": duration,
        }
    except Exception as error:
        logger.error(f"ffprobe metadata extraction failed: {error}")
        return {"codec": "unknown", "sample_rate": "unknown", "duration": "unknown"}


def convert_to_wav(input_path: str, is_raw_pcm: bool = False) -> str:
    fd, output_path = tempfile.mkstemp(suffix="_converted.wav")
    os.close(fd)

    cmd = [FFMPEG_PATH, "-y"]
    if is_raw_pcm:
        cmd.extend(["-f", "s16le", "-ac", "1", "-ar", "16000"])
    cmd.extend(
        [
            "-i",
            input_path,
            "-acodec",
            "pcm_s16le",
            "-ac",
            "1",
            "-ar",
            "16000",
            output_path,
        ]
    )
    try:
        logger.info(f"STT: Converting audio using ffmpeg: {' '.join(cmd)}")
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return output_path
    except subprocess.CalledProcessError as error:
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except OSError:
                pass
        err_msg = error.stderr.decode("utf-8", errors="ignore")
        logger.error(f"STT: FFmpeg conversion failed: {err_msg}")
        raise ApiError(500, f"Audio conversion failed: {err_msg}")


# =====================================================================
# API ENDPOINTS
# =====================================================================

@app.get("/api/v1/tts/health")
def health_check():
    return jsonify({"status": "healthy"})


@app.get("/api/v1/tts/voices")
def list_voices():
    provider_name = os.getenv("TTS_PROVIDER", "edge").lower()
    if provider_name == "edge":
        try:
            import edge_tts

            voices = asyncio.run(edge_tts.list_voices())
            formatted = [
                {
                    "name": voice["Name"],
                    "short_name": voice.get("ShortName", voice["Name"]),
                    "gender": voice.get("Gender", "Unknown"),
                    "locale": voice.get("Locale", "Unknown"),
                }
                for voice in voices
            ]
            return jsonify({"provider": "edge", "voices": formatted})
        except Exception as error:
            logger.error(f"Failed to fetch EdgeTTS voice index: {error}")
            raise ApiError(500, f"Failed to fetch EdgeTTS voices: {error}")
    if provider_name == "pyttsx3":
        try:
            voices = get_pyttsx3_voices_sync()
            return jsonify({"provider": "pyttsx3", "voices": voices})
        except Exception as error:
            logger.error(f"Failed to fetch Pyttsx3 voice index: {error}")
            raise ApiError(500, f"Failed to fetch Pyttsx3 voices: {error}")

    raise ApiError(500, f"Unsupported active provider: {provider_name}")


@app.post("/api/v1/tts/speak")
def speak():
    payload = validate_speak_request(request.get_json(silent=True))
    client_ip = request.remote_addr or "unknown"
    rate_limiter.check_rate_limit(client_ip)

    provider_name = os.getenv("TTS_PROVIDER", "edge").lower()
    provider = get_provider()

    logger.info(
        f"TTS Request received - Provider: {provider_name} | Language: {payload['language']} | "
        f"Session ID: {payload['session_id']} | Text Length: {len(payload['text'])} characters"
    )

    try:
        audio_bytes = asyncio.run(provider.synthesize(payload["text"], payload["language"]))
        media_type = "audio/mpeg" if provider_name == "edge" else "audio/wav"
        return Response(audio_bytes, mimetype=media_type)
    except ApiError:
        raise
    except Exception as error:
        logger.error(f"TTS synthesis failure: {error}")
        raise ApiError(500, f"TTS synthesis failed: {error}")


@app.post("/api/v1/stt/transcribe")
def transcribe_audio():
    upload = request.files.get("file")
    if upload is None:
        raise ApiError(400, "Audio file is required")

    language = request.form.get("language", "en-US")
    content = upload.read()
    file_size = len(content)
    upload.stream.seek(0)

    if file_size == 0:
        logger.warning("STT: Rejected empty file upload.")
        raise ApiError(400, "Empty files are not supported")

    max_file_size = 10 * 1024 * 1024
    if file_size > max_file_size:
        logger.warning(f"STT: Rejected file exceeding size limit: {file_size} bytes.")
        raise ApiError(413, "File size exceeds the 10 MB limit")

    accepted_types = {
        "audio/wav",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp4",
        "audio/aac",
        "audio/webm",
        "audio/x-m4a",
        "audio/ogg",
        "application/octet-stream",
    }
    accepted_extensions = {".wav", ".mp3", ".m4a", ".mp4", ".webm", ".aac", ".ogg"}

    filename = upload.filename or ""
    file_ext = os.path.splitext(filename.lower())[1] if filename else ""
    if upload.mimetype not in accepted_types and file_ext not in accepted_extensions:
        logger.warning(f"STT: Unsupported file type uploaded: {upload.filename} ({upload.mimetype})")
        raise ApiError(400, "Unsupported file type. Accepted types are WAV, MP3, M4A, AAC, WEBM.")

    fd, temp_input_path = tempfile.mkstemp(suffix=file_ext or ".raw")
    os.close(fd)

    is_raw_pcm = (not content.startswith(b"RIFF")) and (
        file_ext == ".wav" or upload.mimetype == "audio/wav"
    )

    temp_wav_path = None
    try:
        with open(temp_input_path, "wb") as buffer:
            buffer.write(content)

        metadata = get_audio_metadata(temp_input_path, is_raw_pcm=is_raw_pcm)
        logger.info(
            f"STT: Request Details | Filename: {upload.filename} | MIME Type: {upload.mimetype} | "
            f"File Size: {file_size} bytes | Duration: {metadata['duration']} | "
            f"Detected Codec: {metadata['codec']} | Sample Rate: {metadata['sample_rate']}"
        )

        temp_wav_path = convert_to_wav(temp_input_path, is_raw_pcm=is_raw_pcm)

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav_path) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data, language=language)

        logger.info(f"STT: Successfully transcribed audio ({len(text)} characters) in language: {language}")
        return jsonify({"text": text, "language": language})
    except sr.UnknownValueError:
        logger.warning("STT: Google Speech Recognition could not understand the audio")
        raise ApiError(422, "Speech was not clear enough or could not be recognized")
    except sr.RequestError as error:
        logger.error(f"STT: Google Speech Recognition service error: {error}")
        raise ApiError(502, "Speech recognition service is currently unavailable")
    except ApiError:
        raise
    except Exception as error:
        logger.error(f"STT: Transcription error: {error}")
        raise ApiError(500, f"Transcription failed: {error}")
    finally:
        if os.path.exists(temp_input_path):
            try:
                os.remove(temp_input_path)
            except OSError:
                pass
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except OSError:
                pass


if __name__ == "__main__":
    port = int(os.getenv("TTS_PORT", "5001"))
    logger.info(f"Launching TTS Service on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
