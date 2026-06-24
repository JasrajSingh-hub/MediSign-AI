import os
# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient

# Set up testing environment variables before importing the app
os.environ["TTS_PROVIDER"] = "edge"
os.environ["TTS_PORT"] = "5001"
os.environ["RATE_LIMIT_LIMIT"] = "10"
os.environ["RATE_LIMIT_WINDOW_SECONDS"] = "6"

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tts_service import app, rate_limiter

client = TestClient(app)

def test_health_check():
    """Verify that the health check endpoint returns healthy status code 200."""
    response = client.get("/api/v1/tts/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_list_voices():
    """Verify that the voices endpoint returns provider details and a list of voices."""
    response = client.get("/api/v1/tts/voices")
    assert response.status_code == 200
    data = response.json()
    assert "provider" in data
    assert data["provider"] == "edge"
    assert "voices" in data
    assert isinstance(data["voices"], list)
    if len(data["voices"]) > 0:
        voice = data["voices"][0]
        assert "name" in voice
        assert "gender" in voice
        assert "locale" in voice

def test_speak_successful():
    """Verify that a valid TTS request returns a stream of audio bytes."""
    payload = {
        "text": "Hello, this is a test from MediSign AI.",
        "language": "en-US",
        "session_id": "test-uuid-12345"
    }
    response = client.post("/api/v1/tts/speak", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] in ["audio/mpeg", "audio/wav"]
    assert len(response.content) > 0

def test_speak_empty_text():
    """Verify that empty or whitespace-only text is rejected."""
    payload = {
        "text": "    ",
        "language": "en-US",
        "session_id": "test-uuid-empty"
    }
    response = client.post("/api/v1/tts/speak", json=payload)
    # FastAPI returns 422 Unprocessable Entity for Pydantic validation errors
    assert response.status_code == 422
    assert "value_error" in response.text

def test_speak_text_too_long():
    """Verify that text exceeding 500 characters is rejected."""
    payload = {
        "text": "A" * 501,
        "language": "en-US",
        "session_id": "test-uuid-long"
    }
    response = client.post("/api/v1/tts/speak", json=payload)
    assert response.status_code == 422
    assert "value_error" in response.text

def test_speak_invalid_language_tag():
    """Verify that invalid BCP-47 language codes are rejected."""
    payload = {
        "text": "Valid text content",
        "language": "invalid_lang_tag_123",
        "session_id": "test-uuid-lang"
    }
    response = client.post("/api/v1/tts/speak", json=payload)
    assert response.status_code == 422
    assert "value_error" in response.text

def test_speak_html_sanitization():
    """Verify that HTML/XML tags are stripped out and successfully processed."""
    payload = {
        "text": "<p>Hello <b>world</b>! <speak>This should be clean.</speak></p>",
        "language": "en-US",
        "session_id": "test-uuid-sanitize"
    }
    response = client.post("/api/v1/tts/speak", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] in ["audio/mpeg", "audio/wav"]

def test_rate_limiting():
    """Verify that exceeding the rate limit triggers 429 Too Many Requests."""
    # Clear history to isolate from other tests
    rate_limiter.history.clear()
    # Temporarily set limit to a very low value for testing
    original_limit = rate_limiter.limit
    rate_limiter.limit = 2
    
    payload = {
        "text": "Rate limiting check",
        "language": "en-US",
        "session_id": "test-uuid-rate"
    }
    
    try:
        # First request - OK
        resp1 = client.post("/api/v1/tts/speak", json=payload)
        assert resp1.status_code == 200
        
        # Second request - OK
        resp2 = client.post("/api/v1/tts/speak", json=payload)
        assert resp2.status_code == 200
        
        # Third request - Limit exceeded (429)
        resp3 = client.post("/api/v1/tts/speak", json=payload)
        assert resp3.status_code == 429
        assert "Rate limit exceeded" in resp3.json()["detail"]
    finally:
        # Restore the original rate limit
        rate_limiter.limit = original_limit
        rate_limiter.history.clear()

def test_pyttsx3_provider_synthesize():
    """Verify that Pyttsx3Provider can successfully synthesize text offline."""
    import asyncio
    from tts_service import Pyttsx3Provider
    provider = Pyttsx3Provider()
    audio_bytes = asyncio.run(provider.synthesize("Test offline speech capability.", "en-US"))
    assert isinstance(audio_bytes, bytes)
    assert len(audio_bytes) > 0


def generate_dummy_wav() -> bytes:
    import wave
    import io
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wav_file:
        wav_file.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
        wav_file.writeframes(b'\x00' * 32000)
    return wav_io.getvalue()


def test_transcribe_audio_wav_success(monkeypatch):
    """Verify that audio transcription succeeds with valid WAV file and mocked Google Speech API."""
    def mock_recognize_google(self, audio_data, language="en-US"):
        return "hello world"

    def mock_convert_to_wav(input_path, is_raw_pcm=False):
        return input_path

    def mock_get_metadata(file_path, is_raw_pcm=False):
        return {"codec": "pcm_s16le", "sample_rate": "16000", "duration": "2.00s"}

    import speech_recognition as sr
    import tts_service
    monkeypatch.setattr(sr.Recognizer, "recognize_google", mock_recognize_google)
    monkeypatch.setattr(tts_service, "convert_to_wav", mock_convert_to_wav)
    monkeypatch.setattr(tts_service, "get_audio_metadata", mock_get_metadata)

    dummy_wav = generate_dummy_wav()
    response = client.post(
        "/api/v1/stt/transcribe",
        files={"file": ("test.wav", dummy_wav, "audio/wav")},
        data={"language": "en-US"}
    )
    assert response.status_code == 200
    assert response.json() == {"text": "hello world", "language": "en-US"}


def test_transcribe_audio_m4a_success(monkeypatch):
    """Verify that a valid M4A file is successfully accepted and transcoded."""
    def mock_recognize_google(self, audio_data, language="en-US"):
        return "m4a transcription"

    import tts_service
    import tempfile
    
    def mock_convert_to_wav(input_path, is_raw_pcm=False):
        dummy_wav = generate_dummy_wav()
        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        with open(path, "wb") as f:
            f.write(dummy_wav)
        return path

    def mock_get_metadata(file_path, is_raw_pcm=False):
        return {"codec": "aac", "sample_rate": "44100", "duration": "1.50s"}

    import speech_recognition as sr
    monkeypatch.setattr(sr.Recognizer, "recognize_google", mock_recognize_google)
    monkeypatch.setattr(tts_service, "convert_to_wav", mock_convert_to_wav)
    monkeypatch.setattr(tts_service, "get_audio_metadata", mock_get_metadata)

    response = client.post(
        "/api/v1/stt/transcribe",
        files={"file": ("test.m4a", b"dummy m4a bytes", "audio/x-m4a")},
        data={"language": "en-US"}
    )
    assert response.status_code == 200
    assert response.json() == {"text": "m4a transcription", "language": "en-US"}


def test_transcribe_audio_webm_success(monkeypatch):
    """Verify that a valid WEBM file is successfully accepted and transcoded."""
    def mock_recognize_google(self, audio_data, language="en-US"):
        return "webm transcription"

    import tts_service
    import tempfile
    
    def mock_convert_to_wav(input_path, is_raw_pcm=False):
        dummy_wav = generate_dummy_wav()
        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        with open(path, "wb") as f:
            f.write(dummy_wav)
        return path

    def mock_get_metadata(file_path, is_raw_pcm=False):
        return {"codec": "opus", "sample_rate": "48000", "duration": "3.20s"}

    import speech_recognition as sr
    monkeypatch.setattr(sr.Recognizer, "recognize_google", mock_recognize_google)
    monkeypatch.setattr(tts_service, "convert_to_wav", mock_convert_to_wav)
    monkeypatch.setattr(tts_service, "get_audio_metadata", mock_get_metadata)

    response = client.post(
        "/api/v1/stt/transcribe",
        files={"file": ("test.webm", b"dummy webm bytes", "audio/webm")},
        data={"language": "en-US"}
    )
    assert response.status_code == 200
    assert response.json() == {"text": "webm transcription", "language": "en-US"}


def test_transcribe_audio_empty_file():
    """Verify that empty file uploads are rejected with 400 Bad Request."""
    response = client.post(
        "/api/v1/stt/transcribe",
        files={"file": ("empty.wav", b"", "audio/wav")},
        data={"language": "en-US"}
    )
    assert response.status_code == 400
    assert "Empty files are not supported" in response.json()["detail"]


def test_transcribe_audio_large_file():
    """Verify that files exceeding the size limit are rejected with 413 Payload Too Large."""
    large_bytes = b"0" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/api/v1/stt/transcribe",
        files={"file": ("large.wav", large_bytes, "audio/wav")},
        data={"language": "en-US"}
    )
    assert response.status_code == 413
    assert "File size exceeds the 10 MB limit" in response.json()["detail"]


def test_transcribe_audio_invalid_mime():
    """Verify that unsupported MIME types / extensions are rejected with 400."""
    response = client.post(
        "/api/v1/stt/transcribe",
        files={"file": ("doc.pdf", b"pdf content", "application/pdf")},
        data={"language": "en-US"}
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_transcribe_audio_corrupted_ffmpeg(monkeypatch):
    """Verify that audio conversion failures lead to HTTP 500 error."""
    import tts_service
    def mock_convert_to_wav(input_path):
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Audio conversion failed")

    monkeypatch.setattr(tts_service, "convert_to_wav", mock_convert_to_wav)

    dummy_wav = generate_dummy_wav()
    response = client.post(
        "/api/v1/stt/transcribe",
        files={"file": ("test.wav", dummy_wav, "audio/wav")},
        data={"language": "en-US"}
    )
    assert response.status_code == 500

