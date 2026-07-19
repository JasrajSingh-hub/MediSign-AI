# MediSign-AI: Deployment and Packaging Plan

This document details the configuration for deploying the MediSign-AI backend services, compiling the Flutter client, and planning telemetry/analytics systems.

---

## 1. Unified Backend Deployment (Docker & Compose)

### A. Dockerfile Configuration
Binds the service using a Python 3.12 slim base image and OpenCV/MediaPipe requirements:

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### B. docker-compose.yml
```yaml
version: '3.8'

services:
  gateway-api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    environment:
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 2. Flutter Mobile Deployment (Android)

* **Build Profiling**: Compile the application using the `--release` flag to strip debugging shims and enable engine optimization.
* **Command**:
  ```bash
  flutter build apk --release --target-platform android-arm64
  ```
* **Permissions Manifest**: Add necessary permissions to `android/app/src/main/AndroidManifest.xml`:
  ```xml
  <uses-permission android:name="android.permission.CAMERA" />
  <uses-permission android:name="android.permission.RECORD_AUDIO" />
  <uses-permission android:name="android.permission.VIBRATE" />
  <uses-permission android:name="android.permission.INTERNET" />
  ```

---

## 3. Analytics & Crash Reporting (Future Setup)

To prepare the application for real-world clinical deployments, the following crash logging and telemetry systems are planned:

* **Crash Reporting (Firebase Crashlytics / Sentry)**:
  * Catch and log all unhandled exceptions on both the Flutter client and the Python backend.
  * Captures device model, OS version, stack trace, and logs up to the error state.
* **Clinical Usage Telemetry**:
  * Track user interaction events (e.g. tabs opened, settings adjusted, alerts dismissed).
  * Record prediction metrics anonymously (confidence distributions and average round-trip latencies).
  * *Important Privacy Rule*: Never upload image bytes or raw camera/audio captures to cloud services. All analysis must be performed locally on the device or backend server to comply with healthcare privacy regulations.
