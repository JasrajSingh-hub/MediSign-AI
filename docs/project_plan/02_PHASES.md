# MediSign-AI: Phased Development Plan

This document outlines the detailed execution phases, task lists, and verification criteria for completing the MediSign-AI integration.

---

## Phase 1: Unified Backend Integration & Model Training

* **Goal**: Port the Flask prediction endpoint to the FastAPI gateway on port `8000`, train the Random Forest emergency classifier, and verify backend status.
* **Architecture**: Standalone FastAPI application running on port `8000` loading both model picklings and the MediaPipe Tasks HandLandmarker.
* **Tasks**:
  1. Port the Flask prediction endpoint `/predict` to FastAPI `/predict/sign`.
  2. Run the landmark extraction and feature engineering scripts on raw `SOS/` videos.
  3. Execute training to generate the Random Forest model.
* **Subtasks**:
  * Implement `/predict/sign` in `emergency/api.py` (loading `gesture_model_full.pkl`).
  * Run frame extraction, landmarks extraction, feature engineering, and model training scripts in the `emergency/` folder.
  * Verify `GET /health` and `GET /status` endpoints on port `8000`.
* **Deliverables**:
  * Unified FastAPI backend.
  * Trained Random Forest model `emergency_model.pkl` in `emergency/models/`.
* **Files Created**:
  * `emergency/models/emergency_model.pkl` (Generated)
* **Files Modified**:
  * `emergency/api.py` (added sign language routing)
* **Verification**:
  * Run `pytest emergency/tests` to confirm test coverage.
  * Call `GET /health` and check system resource indicators.
* **Acceptance Criteria**:
  * Single FastAPI server active on port 8000.
  * Successfully handles predictions for both general signs and emergency gestures.
* **Estimated Time**: 6 hours.
* **Risk Level**: Medium.
* **STOP POINT**: Validate sign and emergency endpoints using sample payloads before moving to Flutter.

---

## Phase 2: MVP Flutter Setup & Direct Integration

* **Goal**: Implement the Emergency tab and alert triggers (sound, haptics, TTS) directly within the existing Flutter app structure.
* **Architecture**: Single Flutter application structure incorporating `SharedPreferences` settings and camera stream isolates.
* **Tasks**:
  1. Add required dependencies to `pubspec.yaml` (`shared_preferences`, `vibration`, `flutter_tts`, `audioplayers`).
  2. Implement Dashboard navigation tabs (Sign Language and Emergency) directly.
  3. Set up the camera capturing and background compression loop.
  4. Integrate alert engines (audio, haptics, and TTS).
* **Subtasks**:
  * Request lazy camera permissions on startup.
  * Implement the frame capture loop (every 300–500ms) with isolate-based base64 compression.
  * Hook up prediction connections targeting port 8000 `/predict/emergency`.
  * Trigger vibration pulses, play alarm buzzer sound, and read out warning texts on emergency flags.
* **Deliverables**:
  * Tab navigation shell with direct layout pages.
  * Active audible/haptic/visual warning system.
* **Files Created**: None (code is added within existing `lib/main.dart` or alongside it in simple files).
* **Files Modified**:
  * `frontend/medisign_app/pubspec.yaml`
  * `frontend/medisign_app/lib/main.dart`
* **Verification**:
  * Measure frame capture rate (ensure 300-500ms intervals are maintained).
  * Confirm that UI remains responsive and does not experience thread locks during frame compression.
* **Acceptance Criteria**:
  * Displays warning banner, vibrates the device, and speaks the warning text when an emergency is detected.
* **Estimated Time**: 12 hours.
* **Risk Level**: High.
* **STOP POINT**: Verify alert features on physical device before expanding to OCR.

---

## Phase 3: OCR, Speech & Persistence Caching in SharedPreferences

* **Goal**: Implement Prescription OCR, Speech Translation, and save settings and history logs using SharedPreferences.
* **Architecture**: Local client-side preferences cache mapping historical events and settings configurations.
* **Tasks**:
  1. Create Settings screen with sliders, URL configuration, and developer mode.
  2. Implement local history caching using JSON-serialized lists in SharedPreferences.
  3. Integrate Prescription OCR scan page and voice translation page.
* **Subtasks**:
  * Configure threshold, URL, and alert toggles in Settings screen.
  * Save and read predictions history in SharedPreferences (limited to 50 entries).
  * Set up OCR snap button and parsed text displays.
  * Implement Voice to Text and Text to Voice screens.
* **Deliverables**:
  * Configurable Settings panel and Developer mode.
  * Searchable historical records list.
* **Files Created/Modified**:
  * `frontend/medisign_app/lib/main.dart` (modified to add views)
* **Verification**:
  * Verify settings configurations persist across app restarts.
  * Verify offline mode triggers warn users when the server is offline.
* **Acceptance Criteria**:
  * Settings persist on restarts.
  * Predictions are written to local history.
* **Estimated Time**: 12 hours.
* **Risk Level**: Medium.
* **STOP POINT**: Restart the application and verify settings remain intact.

---

## Phase 4: Refactor to Clean Architecture & SQLite Migration (Post-MVP)

* **Goal**: Restructure the Flutter codebase to Clean Architecture and migrate data storage from SharedPreferences to an SQLite database.
* **Architecture**: Clean Architecture structure with layers representing Core, Features, Services, and Providers.
* **Tasks**:
  1. Reorganize directories under `lib/`.
  2. Introduce `Provider` state management.
  3. Migrate history caching from SharedPreferences JSON lists to SQLite database (`sqflite`).
* **Deliverables**:
  * Modular Flutter project structure.
  * Relational database tables for predictions and OCR records.
* **Files Created**:
  * Modular files under `lib/core/`, `lib/features/`, `lib/services/`, `lib/providers/`.
* **Files Modified**:
  * `frontend/medisign_app/lib/main.dart` (broken up into separate components)
* **Verification**:
  * Run `flutter analyze` to ensure zero compilation or lint errors.
* **Acceptance Criteria**:
  * App compiles and runs without warnings.
  * Historical records are read and written to the SQLite database.
* **Estimated Time**: 10 hours.
* **Risk Level**: Medium.
* **STOP POINT**: Complete verification checks and ensure no regression issues occur.

---

## Phase 5: Verification, Packaging & Deployment

* **Goal**: Package the unified FastAPI gateway using Docker and compile a signed release APK.
* **Tasks**:
  1. Build Docker images.
  2. Run Flutter test suites.
  3. Compile release builds.
* **Verification**:
  * Perform health check API responses on Docker containers.
* **Acceptance Criteria**:
  * All tests pass successfully.
  * The release APK is generated and loads without errors.
* **Estimated Time**: 6 hours.
* **Risk Level**: Low.
* **STOP POINT**: Docker containers running and APK successfully installed on hardware.
