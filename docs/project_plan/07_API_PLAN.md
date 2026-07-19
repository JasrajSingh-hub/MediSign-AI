# MediSign-AI: API Specification Plan

This document details the interface specifications, payloads, status codes, and JSON schemas for the unified FastAPI Gateway service running on port `8000`.

---

## 1. Unified Gateway Endpoints

### A. Health Monitoring Check
* **Endpoint**: `GET /health`
* **Success Response (200 OK)**:
  ```json
  {
    "status": "ok",
    "uptime_seconds": 1240,
    "system": {
      "cpu_percent": 8.4,
      "memory_used_mb": 182.5
    },
    "models": {
      "sign_language_loaded": true,
      "emergency_loaded": true,
      "hand_landmarker_loaded": true
    }
  }
  ```

### B. Gateway Status & Configurations
* **Endpoint**: `GET /status`
* **Success Response (200 OK)**:
  ```json
  {
    "status": "ok",
    "version": "0.1.0",
    "classes": {
      "sign_language": ["A", "B", "C", "D", "E", "F", "G", "I", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Z"],
      "emergency": ["help", "doctor", "pain", "call", "accident", "hot"]
    },
    "confidence_thresholds": {
      "sign_language": 0.70,
      "emergency": 0.80
    }
  }
  ```

### C. Real-Time Sign Language Recognition
* **Endpoint**: `POST /predict/sign`
* **Content-Type**: `application/json`
* **Request Body**:
  ```json
  {
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJR..."
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "letter": "A",
    "confidence": "98.5%",
    "letter_confirmed": false,
    "current_word": "HELLO",
    "available": true
  }
  ```
* **No Hands Error Response (200 OK)**:
  ```json
  {
    "letter": "No hand",
    "confidence": "0%",
    "available": false
  }
  ```

### D. Real-Time Emergency Gesture Recognition
* **Endpoint**: `POST /predict/emergency`
* **Content-Type**: `multipart/form-data`
* **Request Fields**:
  * `file`: (Optional, binary file upload)
  * `image_base64`: (Optional, base64 data string)
* **Success Response (200 OK)**:
  ```json
  {
    "label": "help",
    "confidence": 0.942,
    "probabilities": {
      "help": 0.942,
      "doctor": 0.012,
      "pain": 0.021,
      "call": 0.011,
      "accident": 0.009,
      "hot": 0.005
    },
    "is_emergency": true,
    "available": true
  }
  ```

### E. Prescription OCR Extraction
* **Endpoint**: `POST /ocr/extract`
* **Content-Type**: `multipart/form-data`
* **Request Fields**:
  * `file`: (Binary prescription image file)
* **Success Response (200 OK)**:
  ```json
  {
    "hospital": "City General Hospital",
    "doctor": "Dr. Sarah Smith",
    "patient": "John Doe",
    "medicines": [
      {
        "name": "Amoxicillin",
        "dosage": "500mg",
        "frequency": "Three times daily"
      }
    ],
    "raw_text": "City General Hospital\nDr. Sarah Smith\nPatient: John Doe\nAmoxicillin 500mg three times daily"
  }
  ```
