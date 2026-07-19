# MediSign-AI: Backend Subsystem Design Plan

This document plans the implementation of the unified FastAPI Gateway, backend health monitoring, logging strategy, and error recovery paths.

---

## 1. Unified FastAPI Gateway Design

All API logic is unified into a single service running on port `8000`.

* **Model Loader**:
  * Loads `gesture_model_full.pkl` (Sign Language classifier) and `emergency_model.pkl` (Emergency classifier) at startup.
  * Lazily downloads and initializes the MediaPipe Tasks `HandLandmarker` model (`hand_landmarker.task`).
* **Endpoints**:
  * `GET /health` (Gateway health and system usage check)
  * `GET /status` (Model configurations and version check)
  * `POST /predict/sign` (Processes and classifies Indian Sign Language letters)
  * `POST /predict/emergency` (Processes and classifies emergency gestures)
  * `POST /ocr/extract` (Extracts structured labels from prescriptions)

---

## 2. Backend Health Monitoring

The `GET /health` endpoint acts as a monitoring interface:

* **Resource Usage**: Includes CPU percentage, memory usage, and execution latency statistics in the payload.
* **Model Loader Health**:
  * Verifies whether model files are present and loaded successfully.
  * Checks if GPU/CPU delegation is working.
* **Output Schema**:
  ```json
  {
    "status": "ok",
    "uptime_seconds": 3600,
    "system": {
      "cpu_percent": 12.5,
      "memory_used_mb": 240
    },
    "models": {
      "sign_language_loaded": true,
      "emergency_loaded": true,
      "hand_landmarker_loaded": true
    }
  }
  ```

---

## 3. Logging Strategy

* **Log Levels**:
  * `INFO`: Logs requests, predictions (labels + confidences), and startup sequences.
  * `WARNING`: Logs missing hand detections, slow predictions (>250ms), and failed health checks.
  * `ERROR`: Logs model failures, base64 decoding errors, and unhandled system exceptions.
* **Log Rotation**: Binds standard file logging handlers to write to `logs/gateway.log` with a maximum file size of **10MB** and a backup count of **5** logs to prevent disk storage build-up.
* **Format**: Supports both plain text formatting for local debugging and JSON formatting for production log parsers.

---

## 4. Error Recovery Flow

* **Model Reload Fallback**: If a model file is corrupted or fails to load at startup, log the error, continue running, and set the loader status to `false`. On incoming requests, return `HTTP 503 Service Unavailable` with details: `"Model not loaded. Run training script first."`.
* **MediaPipe Lock Recovery**: If MediaPipe crashes or locks up during multi-threaded frame processing:
  1. Catch the exception.
  2. Log the trace.
  3. Re-initialize the `HandLandmarker` instance.
  4. Return `HTTP 422` to trigger a client retry.
* **Multipart Decoding Guards**: Wrap image byte parsing in try-catch blocks. If decoding fails, return a clean `HTTP 400 Bad Request` instead of crashing the FastAPI process.
