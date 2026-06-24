import os
import pytest
from fastapi.testclient import TestClient

# Set up environment variables
os.environ["DB_PATH"] = "test_unified.db"
os.environ["UPLOAD_DIR"] = "test_unified_uploads"

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_test_files():
    yield
    # Cleanup DB
    if os.path.exists("test_unified.db"):
        try:
            os.remove("test_unified.db")
        except Exception:
            pass
    # Cleanup directory
    if os.path.exists("test_unified_uploads"):
        try:
            import shutil
            shutil.rmtree("test_unified_uploads")
        except Exception:
            pass

def test_unified_routes_presence():
    """Verify that the unified app exposes all routes from app.py, tts_service, and ocr_service."""
    routes = []
    
    def extract_routes(routes_list):
        for r in routes_list:
            if hasattr(r, "path"):
                routes.append(r.path)
            # Check for FastAPI's _IncludedRouter which holds original_router
            if hasattr(r, "original_router") and r.original_router:
                extract_routes(r.original_router.routes)
            # Check for nested Mount routes
            elif hasattr(r, "routes"):
                extract_routes(r.routes)
                
    extract_routes(app.routes)
    
    # Sign Language endpoint
    assert "/predict" in routes
    
    # TTS & STT endpoints
    assert "/api/v1/tts/health" in routes
    assert "/api/v1/tts/voices" in routes
    assert "/api/v1/tts/speak" in routes
    assert "/api/v1/stt/transcribe" in routes
    
    # Prescription OCR endpoints
    assert "/api/v1/prescription/health" in routes
    assert "/api/v1/prescription/upload" in routes
    assert "/api/v1/prescription/process" in routes
    assert "/api/v1/prescription/{id}" in routes

def test_unified_predict_unloaded_model():
    """Verify predict endpoint handles requests and returns error if model is not loaded."""
    # Since we don't have the keras model loaded in this clean test environment,
    # it should raise/return a 503 Service Unavailable or 400 Bad Request
    response = client.post("/predict", json={"image": "data:image/jpeg;base64,AAAA"})
    # Since model could be None or load failed, it should return an error status code
    assert response.status_code in [400, 503]
