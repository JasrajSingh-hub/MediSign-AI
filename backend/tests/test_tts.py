import io
import os
import sys
import types

import pytest

# Set up testing environment variables before importing the app
os.environ["TTS_PROVIDER"] = "edge"
os.environ["TTS_PORT"] = "5001"
os.environ["RATE_LIMIT_LIMIT"] = "10"
os.environ["RATE_LIMIT_WINDOW_SECONDS"] = "6"

import tts_service
from tts_service import ApiError, EdgeTTSProvider, app, rate_limiter


@pytest.fixture()
def client(monkeypatch):
    async def mock_synthesize(self, text, language):
        return b"fake-audio-payload"

    async def mock_list_voices():
        return [
            {
                "Name": "en-US-TestNeural",
                "ShortName": "en-US-TestNeural",
                "Gender": "Female",
                "Locale": "en-US",
            }
        ]

    monkeypatch.setattr(EdgeTTSProvider, "synthesize", mock_synthesize)
    monkeypatch.setattr(tts_service, "get_audio_metadata", lambda *args, **kwargs: {
        "codec": "pcm_s16le",
        "sample_rate": "16000",
        "duration": "2.00s",
    })

    edge_tts = sys.modules.get("edge_tts")
    if edge_tts is None:
        edge_tts = types.SimpleNamespace()
        sys.modules["edge_tts"] = edge_tts

    monkeypatch.setattr(edge_tts, "list_voices", mock_list_voices)
    rate_limiter.history.clear()

    with app.test_client() as test_client:
        yield test_client

    rate_limiter.history.clear()


def test_health_check(client):
    response = client.get("/api/v1/tts/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_list_voices(client):
    response = client.get("/api/v1/tts/voices")
    assert response.status_code == 200
    data = response.get_json()
    assert "provider" in data
    assert data["provider"] == "edge"
    assert "voices" in data
    assert isinstance(data["voices"], list)
    if data["voices"]:
        voice = data["voices"][0]
        assert "name" in voice
        assert "gender" in voice
        assert "locale" in voice


def test_speak_successful(client):
    payload = {
        "text": "Hello, this is a test from MediSign AI.",
        "language": "en-US",
        "session_id": "test-uuid-12345",
    }
    response = client.post("/api/v1/tts/speak", json=payload)
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith(("audio/mpeg", "audio/wav"))
    assert len(response.data) > 0


def test_speak_empty_text(client):
    payload = {
        "text": "    ",
        "language": "en-US",
        "session_id": "test-uuid-empty",
    }
    response = client.post("/api/v1/tts/speak", json=payload)
    assert response.status_code == 422
    assert "Text content cannot be empty" in response.get_json()["detail"]


def test_speak_text_too_long(client):
    payload = {
        "text": "A" * 501,
        "language": "en-US",
        "session_id": "test-uuid-long",
    }
    response = client.post("/api/v1/tts/speak", json=payload)
    assert response.status_code == 422
    assert "must not exceed 500 characters" in response.get_json()["detail"]


def test_speak_invalid_language_tag(client):
    payload = {
        "text": "Valid text content",
        "language": "invalid_lang_tag_123",
        "session_id": "test-uuid-lang",
    }
    response = client.post("/api/v1/tts/speak", json=payload)
    assert response.status_code == 422
    assert "Invalid language tag format" in response.get_json()["detail"]


def test_speak_html_sanitization(client):
    payload = {
        "text": "<p>Hello <b>world</b>! <speak>This should be clean.</speak></p>",
        "language": "en-US",
        "session_id": "test-uuid-sanitize",
    }
    response = client.post("/api/v1/tts/speak", json=payload)
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith(("audio/mpeg", "audio/wav"))


def test_rate_limiting(client):
    rate_limiter.history.clear()
    original_limit = rate_limiter.limit
    rate_limiter.limit = 2

    payload = {
        "text": "Rate limiting check",
        "language": "en-US",
        "session_id": "test-uuid-rate",
    }

    try:
        resp1 = client.post("/api/v1/tts/speak", json=payload)
        assert resp1.status_code == 200

        resp2 = client.post("/api/v1/tts/speak", json=payload)
        assert resp2.status_code == 200

        resp3 = client.post("/api/v1/tts/speak", json=payload)
        assert resp3.status_code == 429
        assert "Rate limit exceeded" in resp3.get_json()["detail"]
    finally:
        rate_limiter.limit = original_limit
        rate_limiter.history.clear()


def test_pyttsx3_provider_synthesize():
    import asyncio

    from tts_service import Pyttsx3Provider

    provider = Pyttsx3Provider()
    audio_bytes = asyncio.run(provider.synthesize("Test offline speech capability.", "en-US"))
    assert isinstance(audio_bytes, bytes)
    assert len(audio_bytes) > 0


def generate_dummy_wav() -> bytes:
    import wave

    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wav_file:
        wav_file.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
        wav_file.writeframes(b"\x00" * 32000)
    return wav_io.getvalue()


def test_transcribe_audio_wav_success(client, monkeypatch):
    def mock_recognize_google(self, audio_data, language="en-US"):
        return "hello world"

    def mock_convert_to_wav(input_path, is_raw_pcm=False):
        return input_path

    monkeypatch.setattr(tts_service.sr.Recognizer, "recognize_google", mock_recognize_google)
    monkeypatch.setattr(tts_service, "convert_to_wav", mock_convert_to_wav)

    dummy_wav = generate_dummy_wav()
    response = client.post(
        "/api/v1/stt/transcribe",
        data={
            "language": "en-US",
            "file": (io.BytesIO(dummy_wav), "test.wav", "audio/wav"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.get_json() == {"text": "hello world", "language": "en-US"}


def test_transcribe_audio_m4a_success(client, monkeypatch):
    def mock_recognize_google(self, audio_data, language="en-US"):
        return "m4a transcription"

    import tempfile

    def mock_convert_to_wav(input_path, is_raw_pcm=False):
        dummy_wav = generate_dummy_wav()
        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        with open(path, "wb") as file_handle:
            file_handle.write(dummy_wav)
        return path

    monkeypatch.setattr(tts_service.sr.Recognizer, "recognize_google", mock_recognize_google)
    monkeypatch.setattr(tts_service, "convert_to_wav", mock_convert_to_wav)
    monkeypatch.setattr(tts_service, "get_audio_metadata", lambda *args, **kwargs: {
        "codec": "aac",
        "sample_rate": "44100",
        "duration": "1.50s",
    })

    response = client.post(
        "/api/v1/stt/transcribe",
        data={
            "language": "en-US",
            "file": (io.BytesIO(b"dummy m4a bytes"), "test.m4a", "audio/x-m4a"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.get_json() == {"text": "m4a transcription", "language": "en-US"}


def test_transcribe_audio_webm_success(client, monkeypatch):
    def mock_recognize_google(self, audio_data, language="en-US"):
        return "webm transcription"

    import tempfile

    def mock_convert_to_wav(input_path, is_raw_pcm=False):
        dummy_wav = generate_dummy_wav()
        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        with open(path, "wb") as file_handle:
            file_handle.write(dummy_wav)
        return path

    monkeypatch.setattr(tts_service.sr.Recognizer, "recognize_google", mock_recognize_google)
    monkeypatch.setattr(tts_service, "convert_to_wav", mock_convert_to_wav)
    monkeypatch.setattr(tts_service, "get_audio_metadata", lambda *args, **kwargs: {
        "codec": "opus",
        "sample_rate": "48000",
        "duration": "3.20s",
    })

    response = client.post(
        "/api/v1/stt/transcribe",
        data={
            "language": "en-US",
            "file": (io.BytesIO(b"dummy webm bytes"), "test.webm", "audio/webm"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.get_json() == {"text": "webm transcription", "language": "en-US"}


def test_transcribe_audio_empty_file(client):
    response = client.post(
        "/api/v1/stt/transcribe",
        data={
            "language": "en-US",
            "file": (io.BytesIO(b""), "empty.wav", "audio/wav"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "Empty files are not supported" in response.get_json()["detail"]


def test_transcribe_audio_large_file(client):
    large_bytes = b"0" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/api/v1/stt/transcribe",
        data={
            "language": "en-US",
            "file": (io.BytesIO(large_bytes), "large.wav", "audio/wav"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 413
    assert "File size exceeds the 10 MB limit" in response.get_json()["detail"]


def test_transcribe_audio_invalid_mime(client):
    response = client.post(
        "/api/v1/stt/transcribe",
        data={
            "language": "en-US",
            "file": (io.BytesIO(b"pdf content"), "doc.pdf", "application/pdf"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.get_json()["detail"]


def test_transcribe_audio_corrupted_ffmpeg(client, monkeypatch):
    def mock_convert_to_wav(input_path, is_raw_pcm=False):
        raise ApiError(status_code=500, detail="Audio conversion failed")

    monkeypatch.setattr(tts_service, "convert_to_wav", mock_convert_to_wav)

    dummy_wav = generate_dummy_wav()
    response = client.post(
        "/api/v1/stt/transcribe",
        data={
            "language": "en-US",
            "file": (io.BytesIO(dummy_wav), "test.wav", "audio/wav"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 500
