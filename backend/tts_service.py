import abc
import asyncio
import logging
import os
import re
import tempfile
import time
from collections import defaultdict
from typing import List, Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
import io

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("tts_service")

app = FastAPI(
    title="MediSign AI TTS Service",
    description="Microservice providing Text-to-Speech capability for MediSign AI",
    version="1.0.0"
)

# Enable CORS for Flutter app integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# REQUEST VALIDATION & SANITIZATION
# =====================================================================

def sanitize_text(text: str) -> str:
    """Removes HTML/XML/SSML tags to prevent SSML injection and normalizes whitespace."""
    # Strip XML/HTML tags
    text = re.sub(r"<[^>]*>", "", text)
    # Normalize multiple whitespace characters into single spaces
    text = " ".join(text.split())
    return text

class SpeakRequest(BaseModel):
    text: str = Field(..., description="Text content to be verbalized (max 500 characters)")
    language: str = Field(..., description="BCP-47 language tag (e.g., en-IN, en-US)")
    session_id: str = Field(..., description="UUID or session identifier")

    @field_validator("text")
    @classmethod
    def validate_and_sanitize_text(cls, v: str) -> str:
        sanitized = sanitize_text(v)
        if not sanitized:
            raise ValueError("Text content cannot be empty after sanitization")
        if len(sanitized) > 500:
            raise ValueError("Text content must not exceed 500 characters")
        return sanitized

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        # Regex validation for BCP-47 language codes
        pattern = r"^[a-zA-Z]{2,3}(-[a-zA-Z]{2,4})?$"
        if not re.match(pattern, v):
            raise ValueError("Invalid language tag format (must match BCP-47, e.g. en-IN, en-US)")
        return v

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
        # Evict timestamps older than the sliding window
        self.history[client_id] = [
            t for t in self.history[client_id] if now - t < self.window_seconds
        ]
        if len(self.history[client_id]) >= self.limit:
            logger.warning(f"Rate limit hit for client: {client_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        self.history[client_id].append(now)

rate_limiter = InMemoryRateLimiter(
    limit=int(os.getenv("RATE_LIMIT_LIMIT", "60")),
    window_seconds=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
)

# =====================================================================
# TTS PROVIDERS ABSTRACTION LAYER
# =====================================================================

class TTSProvider(abc.ABC):
    @abc.abstractmethod
    async def synthesize(self, text: str, language: str) -> bytes:
        """Synthesize text to speech bytes."""
        pass

# --- Edge-TTS Provider (Online) ---
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
        
        # 1. Look for exact locale match
        for v in voices:
            if v["Locale"].lower() == lang_lower:
                return v["Name"]
                
        # 2. Look for prefix match (e.g. "en" matches first "en-US", "en-IN" etc.)
        lang_prefix = lang_lower.split("-")[0]
        for v in voices:
            if v["Locale"].lower().startswith(lang_prefix):
                return v["Name"]
                
        # 3. Fallback to en-US
        for v in voices:
            if v["Locale"].lower() == "en-us":
                return v["Name"]
                
        # 4. Ultimate fallback to first voice in list
        return voices[0]["Name"] if voices else "en-US-AriaNeural"

# --- Pyttsx3 Provider (Offline) ---
class Pyttsx3Provider(TTSProvider):
    def __init__(self):
        self._lock = asyncio.Lock()

    async def synthesize(self, text: str, language: str) -> bytes:
        # pyttsx3 init/run loop is synchronous and thread-unsafe.
        # Run it in an executor thread with a lock to prevent concurrency conflicts.
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

            # 1. Search voice.languages list
            for v in voices:
                if hasattr(v, "languages") and v.languages:
                    if any(lang_lower in str(l).lower() or lang_prefix in str(l).lower() for l in v.languages):
                        selected_voice = v.id
                        break

            # 2. Search name or ID attributes
            if not selected_voice:
                for v in voices:
                    name_lower = v.name.lower()
                    id_lower = v.id.lower()
                    if lang_lower in name_lower or lang_lower in id_lower:
                        selected_voice = v.id
                        break
                    elif lang_prefix in name_lower or lang_prefix in id_lower:
                        selected_voice = v.id
                        break

            if selected_voice:
                logger.info(f"Synthesizing using Pyttsx3 with voice: {selected_voice}")
                engine.setProperty("voice", selected_voice)
            else:
                logger.info("Synthesizing using Pyttsx3 with default system voice")

            # Create an actual temp file path (with closed fd) so pyttsx3 engine can safely overwrite it
            fd, temp_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)

            try:
                engine.save_to_file(text, temp_path)
                engine.runAndWait()
                
                with open(temp_path, "rb") as f:
                    audio_bytes = f.read()
                    
                if not audio_bytes:
                    raise RuntimeError("Pyttsx3 synthesizer returned empty audio payload")
                return audio_bytes
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        finally:
            engine.stop()

# Helper for Pyttsx3 voice listings
def get_pyttsx3_voices_sync() -> List[Dict[str, Any]]:
    import pyttsx3
    engine = pyttsx3.init()
    try:
        voices = engine.getProperty("voices")
        formatted = []
        for v in voices:
            formatted.append({
                "id": v.id,
                "name": v.name,
                "languages": getattr(v, "languages", []),
                "gender": getattr(v, "gender", "Unknown")
            })
        return formatted
    finally:
        engine.stop()

# --- Factory instantiator ---
def get_provider() -> TTSProvider:
    provider_name = os.getenv("TTS_PROVIDER", "edge").lower()
    if provider_name == "edge":
        return EdgeTTSProvider()
    elif provider_name == "pyttsx3":
        return Pyttsx3Provider()
    else:
        logger.warning(f"Unknown TTS_PROVIDER '{provider_name}', falling back to 'edge'")
        return EdgeTTSProvider()

# =====================================================================
# API ENDPOINTS
# =====================================================================

@app.get("/api/v1/tts/health")
async def health_check():
    """Simple status check reporting backend availability."""
    return {"status": "healthy"}

@app.get("/api/v1/tts/voices")
async def list_voices():
    """Returns available voices corresponding to the configured provider."""
    provider_name = os.getenv("TTS_PROVIDER", "edge").lower()
    if provider_name == "edge":
        try:
            import edge_tts
            voices = await edge_tts.list_voices()
            formatted = [
                {
                    "name": v["Name"],
                    "short_name": v.get("ShortName", v["Name"]),
                    "gender": v.get("Gender", "Unknown"),
                    "locale": v.get("Locale", "Unknown")
                } for v in voices
            ]
            return {"provider": "edge", "voices": formatted}
        except Exception as e:
            logger.error(f"Failed to fetch EdgeTTS voice index: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch EdgeTTS voices: {str(e)}")
    elif provider_name == "pyttsx3":
        try:
            voices = await asyncio.to_thread(get_pyttsx3_voices_sync)
            return {"provider": "pyttsx3", "voices": voices}
        except Exception as e:
            logger.error(f"Failed to fetch Pyttsx3 voice index: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch Pyttsx3 voices: {str(e)}")
    else:
        raise HTTPException(status_code=500, detail=f"Unsupported active provider: {provider_name}")

@app.post("/api/v1/tts/speak")
async def speak(request: SpeakRequest, http_request: Request):
    """
    Accepts text input and streams synthesized audio directly back.
    Includes validation, rate limiting, and secure logging of request metadata.
    """
    # 1. Enforce rate limiting
    client_ip = http_request.client.host if http_request.client else "unknown"
    rate_limiter.check_rate_limit(client_ip)

    # 2. Get the configured provider
    provider_name = os.getenv("TTS_PROVIDER", "edge").lower()
    provider = get_provider()

    # 3. Securely log request details (NEVER log raw text or audio)
    logger.info(
        f"TTS Request received - Provider: {provider_name} | Language: {request.language} | "
        f"Session ID: {request.session_id} | Text Length: {len(request.text)} characters"
    )

    try:
        # 4. Generate audio bytes in memory
        audio_bytes = await provider.synthesize(request.text, request.language)
        
        # 5. Determine media mime-type (edge-tts generates MP3, pyttsx3 generates WAV)
        media_type = "audio/mpeg" if provider_name == "edge" else "audio/wav"
        
        # 6. Stream audio buffer to client
        return StreamingResponse(io.BytesIO(audio_bytes), media_type=media_type)
        
    except Exception as e:
        logger.error(f"TTS synthesis failure: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"TTS synthesis failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("TTS_PORT", "5001"))
    logger.info(f"Launching TTS Service on port {port}...")
    uvicorn.run("tts_service:app", host="0.0.0.0", port=port, reload=True)
