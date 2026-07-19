# MediSign-AI: Flutter Application Implementation Plan

This document maps out the implementation strategy for the **MediSign-AI** Flutter client, prioritizing feature integration first and refactoring later, using SharedPreferences for MVP persistence, and detailing permission, error, and connection monitoring systems.

---

## 1. Integration-First Strategy (No Immediate Refactoring)

To ensure rapid delivery and stability, the Emergency feature will be integrated directly into the current layout structure of the application. The directory cleanup and folder separation will be executed as a subsequent Phase 2 task.

* **MVP File Layout**:
  * Keep `lib/main.dart` as the central visual widget.
  * Implement the new pages, widgets, and services as separate classes within the existing folders, referencing them from the sandbox view.
  * Extend `TestDashboard` or wrap it in a simple `StatefulWidget` switcher to toggle between **Sign Language Mode**, **Emergency Mode**, **Prescription OCR**, and **Voice Translation**.

---

## 2. Core Subsystem Designs

### A. Permission Management
* **Required Permissions**:
  * `Permission.camera`: For frame capture on Sign, Emergency, and OCR screens.
  * `Permission.microphone`: For Speech-to-Text translation.
* **UX Flow**:
  * Permissions are requested lazily when navigating to a specific tab.
  * If a permission is denied:
    * Display an overlay card: *"Camera access is required for real-time translation. Enable in Settings."*
    * Provide a button linking to system settings: `openAppSettings()`.
    * Freeze camera viewports and loop timers until permission status shifts to granted.

### B. Connection Monitor & Backend Health Monitoring
* **Function**: A background monitor tracking server availability.
* **Mechanism**:
  * Periodically (every 5 seconds), the app sends a lightweight `GET /health` call to the FastAPI server.
  * If a response is received, update connection status to **Connected**.
  * If a connection times out or fails (e.g., ADB tunnel disconnected):
    * Change status to **Disconnected**.
    * Display a banner warning: *"Server unavailable. Check USB cable and ADB reverse forward."*
    * Pause the frame capture loop to avoid wasteful thread processing and network overhead.

### C. Offline Queue Strategy
* **Objective**: Manage predictions when connection drops.
* **Rules**:
  * Real-time gesture predictions are ephemeral; if the connection drops, frames are dropped rather than queued, as real-time context is lost.
  * For **Prescription OCR** and **History Logs**:
    * If the client is offline, write the event/prescription data locally to a temporary JSON list in `SharedPreferences`.
    * Once the Connection Monitor restores connection status, flush the offline queue by uploading the cached prescription records to `/ocr/extract` and clearing the queue.

### D. Developer Mode
* **Feature**: A hidden panel for debug configurations.
* **Activation**: Tap the App Title on the Settings or Dashboard page 7 times.
* **Controls**:
  * Toggle mock prediction responses (forces a mock JSON response without sending HTTP requests).
  * Direct URL overriding input box (e.g. configure custom port or local IP).
  * Custom prediction interval adjustments (from 100ms up to 1000ms).
  * Show/Hide debug performance indicators overlay.

### E. Performance Monitoring
* **Metrics Tracked**:
  * **Capture FPS**: Frequency of frames captured and compressed by the camera system.
  * **Prediction FPS**: Frequency of successful API predictions returning from the server.
  * **Latency (ms)**: Round-trip duration for each prediction request.
  * **Dropped Frames**: Count of frames captured but skipped because the previous prediction request was still active.
* **Display**: Rendered in a small transparent overlay at the top corner of the screen when Developer Mode is active.

### F. Error Recovery Flow
* **Connection Timeout**: If a POST request exceeds 500ms, cancel the request, increment a consecutive error counter, and proceed to the next frame.
* **Consecutive Failures**: If 3 consecutive requests fail:
  * Force-pause the capture loop.
  * Trigger a reconnect check.
  * Show reconnection status: *"Reconnecting..."*.
* **Camera Crash Recovery**: If the `CameraController` encounters an error (e.g. hardware lock), call `dispose()`, show an error banner, and provide a `Restart Camera` button.

---

## 3. Lightweight MVP Persistence (SharedPreferences)

We will use `shared_preferences: ^2.2.0` for MVP configurations and prediction history storage.

* **Settings Cache**: Stores threshold values, URLs, and alert flags.
* **Prediction History Log**:
  * Convert prediction records to JSON strings and store them in a list under the key `cached_prediction_history`.
  * Append new predictions to the top of the list.
  * Bound the list to **50** records.
* **SQLite Database**: Deferred to Phase 2 refactoring.
