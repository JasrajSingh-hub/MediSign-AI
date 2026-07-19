# MediSign-AI: Project Implementation Plan

This document serves as the high-level roadmap and project management blueprint for completing the integration and expansion of **MediSign-AI**.

---

## 1. Project Roadmap Overview

MediSign-AI is transitioning to a single, unified FastAPI backend gateway and integrating the Emergency recognition features directly into the existing Flutter app structure. Clean architecture refactoring and SQLite databases are deferred to post-MVP development phases.

```
[Phase A: Unified Backend & ML] ──> [Phase B: MVP Integration] ──> [Phase C: Refactor & Database]
- Port Flask logic to FastAPI      - Camera integrations        - Clean Architecture
- Train emergency model            - Sound, Haptics, & TTS      - SQLite migration
- Establish health routes          - SharedPreferences cache    - Docker Compose
```

---

## 2. Remaining Work Breakdown

The remaining tasks required to bring MediSign-AI to production status are:

1. **Unified FastAPI Backend**:
   - Port Flask prediction endpoint `/predict` to FastAPI `/predict/sign`.
   - Train the Random Forest emergency classifier on the `SOS/` video dataset to generate `emergency/models/emergency_model.pkl`.
   - Verify the FastAPI service local prediction pipeline and health checks.
2. **Direct Flutter Integration (Integration-First)**:
   - Do not perform early folder refactoring. Integrate Emergency features directly within the current `lib/main.dart` or alongside it using the existing project structure.
   - Install required dependencies (`shared_preferences`, `vibration`, `flutter_tts`, `audioplayers`).
3. **Emergency Gesture Integration**:
   - Build the `EmergencyScreen` layout containing camera preview, status banners, statistics overlays, and inline charts.
   - Establish frame capture loops (every 300–500ms) running base64 transformations in background isolates.
   - Implement client haptic vibration, alarm audio, and Text-to-Speech (TTS) announcement engines triggered on emergency detections.
4. **MVP Persistence**:
   - Save user settings and prediction histories locally using `SharedPreferences`.
5. **Prescription OCR & Speech Modules**:
   - Set up simple OCR snapped image capture and parsed data display.
   - Build text-to-speech and speech-to-text voice panels.
6. **Optional Refactoring & Database (Post-MVP)**:
   - Refactor codebase to Clean Architecture directory layout.
   - Migrate SharedPreferences cache histories to SQLite databases.

---

## 3. Milestones and Estimated Timeline

| Milestone | Deliverable | Target Timeline | Priority |
| :--- | :--- | :--- | :--- |
| **M1: Unified Backend** | Port Flask to FastAPI port 8000, train `emergency_model.pkl`, confirm health endpoints. | Day 1-2 | P0 |
| **M2: MVP Setup** | Add dependencies, configure lazy permission requests, and set up Dashboard tab shell. | Day 2-3 | P0 |
| **M3: Emergency Integration** | Camera stream capture, FastAPI integration, alert triggers (Alarm/Haptics/TTS), and SharedPreferences caching. | Day 4-5 | P0 |
| **M4: OCR & Speech** | OCR capture parser and STT/TTS voice screen. | Day 6-7 | P1 |
| **M5: Refactor & Release** | Refactor Flutter directories, migrate history to SQLite, verify Docker and compile APK. | Day 8-9 | P1 |

---

## 4. Key Dependencies

1. **FastAPI Port 8000**: Both sign and emergency features require the gateway server running on port 8000.
2. **MediaPipe Tasks API**: Requires the landmarker model file `hand_landmarker.task`.
3. **Flutter Hardware APIs**: Camera feeds, vibration drivers, and audio players rely on native platform channel capabilities (`camera`, `vibration`, `audioplayers`, `flutter_tts`).
4. **Network Access**: Physical connection over USB utilizing ADB reverse mapping `tcp:8000 tcp:8000` is required for local emulator/device testing.
