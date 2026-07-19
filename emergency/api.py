"""FastAPI service for the Emergency Gesture Recognition module (Phase 9).

Endpoints
---------
* ``GET  /health``  -> ``{"status": "ok"}``
* ``GET  /status``  -> model/version/class info
* ``POST /predict`` -> accepts an uploaded image file **or** an ``image_base64``
  form field (raw base64 or a ``data:`` URI) and returns the prediction (label,
  confidence, per-class probabilities, ``is_emergency`` flag).

FastAPI auto-serves Swagger UI at ``/docs`` and the OpenAPI schema at
``/openapi.json``. Run with::

    uvicorn api:app --reload --port 8000
"""
from __future__ import annotations

import base64
from typing import Optional

import config
from config import CONSTANTS
from config.constants import DEFAULT_CONFIDENCE_THRESHOLD
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from utils.inference import predict_from_image_bytes
from utils.logger import get_logger
from utils.predictor import get_predictor

logger = get_logger("api")

app = FastAPI(
    title=config.CONFIG["project"]["name"],
    version=config.CONFIG["project"]["version"],
    description="Real-time emergency hand-gesture recognition API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


from pydantic import BaseModel
from utils.model_manager import get_model_manager

class SignRequest(BaseModel):
    image: str


@app.get("/health")
def health() -> dict:
    """Liveness probe with system and model diagnostics."""
    import sys
    import os
    
    system_info = {
        "platform": sys.platform,
        "cpu_count": os.cpu_count() or 1,
    }
    
    try:
        import psutil
        system_info["cpu_percent"] = psutil.cpu_percent()
        system_info["memory_used_mb"] = int(psutil.Process().memory_info().rss / (1024 * 1024))
    except ImportError:
        system_info["cpu_percent"] = 0.0
        system_info["memory_used_mb"] = 0
        
    manager = get_model_manager()
    
    return {
        "status": "ok",
        "system": system_info,
        "models": {
            "sign_language_loaded": manager.load_sign_model(),
            "emergency_loaded": manager.load_emergency_model(),
            "hand_landmarker_loaded": manager.load_landmarker(),
        }
    }


@app.get("/status")
def status() -> dict:
    """Model availability, version, and supported classes."""
    manager = get_model_manager()
    metadata = manager.get_metadata()
    
    return {
        "status": "ok",
        "model_loaded": metadata["models"]["emergency"]["loaded"],
        "version": metadata["version"],
        "classes": metadata["models"]["emergency"]["classes"],
        "confidence_threshold": config.CONFIG["api"]["emergency_confidence_threshold"],
        "details": metadata
    }


@app.post("/predict")
def predict(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
) -> dict:
    """Predict the emergency gesture in an image.

    Accepts either a multipart file upload (``file``) or a ``image_base64`` form
    field containing a raw base64 string or a ``data:`` URI.
    """
    if file is not None:
        data = file.file.read()
    elif image_base64:
        try:
            data = base64.b64decode(image_base64.split(",")[-1])
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid base64 payload: {exc}")
    else:
        raise HTTPException(status_code=400, detail="Provide an image via file upload or 'image_base64'.")

    logger.info("Predict request received (bytes=%d)", len(data))
    result = predict_from_image_bytes(data)
    if not result.get("available"):
        raise HTTPException(status_code=422, detail=result.get("error", "Prediction unavailable"))
    return result


@app.post("/predict/sign")
def predict_sign(payload: SignRequest) -> dict:
    """Predict the Indian Sign Language letter in an image.

    Replicates Flask /predict endpoint on the FastAPI gateway (incremental migration).
    """
    try:
        image_data = payload.image.split(",")[-1]
        decoded_bytes = base64.b64decode(image_data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid base64 payload: {exc}")

    logger.info("Sign language predict request received (bytes=%d)", len(decoded_bytes))
    manager = get_model_manager()
    result = manager.predict_sign(decoded_bytes)
    if not result.get("available"):
        raise HTTPException(status_code=422, detail=result.get("error", "Prediction unavailable"))
    
    # Maintain compatibility with the original Flask format
    return {
        "letter": result.get("letter", "No hand"),
        "confidence": result.get("confidence", "0%"),
        "letter_confirmed": False,
        "current_word": ""
    }


# Serve the standalone HTML test frontend (Phase 11) at /frontend.
from fastapi.staticfiles import StaticFiles
from pathlib import Path as _Path

_FRONTEND_DIR = _Path(__file__).resolve().parent / "frontend"
if _FRONTEND_DIR.is_dir():
    app.mount("/frontend", StaticFiles(directory=str(_FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    api_cfg = config.CONFIG["api"]
    uvicorn.run(app, host=api_cfg.get("host", "0.0.0.0"), port=int(api_cfg.get("port", 8000)))
