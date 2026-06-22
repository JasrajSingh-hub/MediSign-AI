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

