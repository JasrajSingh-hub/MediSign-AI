# MediSign-AI: Hierarchical Task Tree

This file documents the structured, hierarchical task tree mapping out all components to be implemented or verified across the MediSign-AI application.

```
MediSign-AI Project Tasks
├── [x] Assessment Report (Completed)
├── [/] Project Planning (In Progress)
├── [ ] Unified Backend Gateway (Port 8000)
│   ├── [ ] Migrate Sign Language Recognition from Flask
│   │   ├── [ ] Port preprocessing & normalization helper functions
│   │   ├── [ ] Configure loading of gesture_model_full.pkl
│   │   └── [ ] Add POST /predict/sign route
│   ├── [ ] Train Emergency Classifier Model
│   │   ├── [ ] Run frame extraction & landmarker scripts
│   │   └── [ ] Train Random Forest classifier to generate emergency_model.pkl
│   ├── [ ] Add Health & Status Monitoring Routes
│   │   ├── [ ] GET /health (monitoring CPU, memory, and model load)
│   │   └── [ ] GET /status (model metadata and configurations)
│   └── [ ] Docker Integration & Packaging
├── [ ] Flutter Application (MVP Direct Integration)
│   ├── [ ] MVP Setup & Configurations
│   │   ├── [ ] Link dependencies in pubspec.yaml
│   │   └── [ ] Integrate Dashboard tab shell in main.dart
│   ├── [ ] Lazy Permissions Management
│   │   ├── [ ] Request camera and microphone access dynamically
│   │   └── [ ] Add permission-denied fallback screens
│   ├── [ ] Connection Monitoring & Health Checker
│   │   ├── [ ] Periodic GET /health ping checks
│   │   └── [ ] Pause/Resume frame loop states based on connection status
│   ├── [ ] Frame Capture & Prediction Loop
│   │   ├── [ ] Periodic frame grabber (300-500ms intervals)
│   │   ├── [ ] Isolate-based JPEG compression & base64 transforms
│   │   └── [ ] Call POST /predict/emergency endpoint
│   ├── [ ] Alert Trigger Engine
│   │   ├── [ ] Loop vibration patterns
│   │   ├── [ ] Play audible alarm sound
│   │   └── [ ] Speak prediction labels using Text-to-Speech (TTS)
│   ├── [ ] MVP Caching Persistence
│   │   ├── [ ] Save user settings to SharedPreferences
│   │   └── [ ] Cache prediction history as serialized JSON lists
│   ├── [ ] Prescription OCR Screen
│   │   ├── [ ] Camera snap integration
│   │   └── [ ] Structured details list display
│   ├── [ ] Speech Translation Screen
│   │   ├── [ ] Speech-to-Text dynamic transcription
│   │   └── [ ] Text-to-Speech synthesizer interface
│   ├── [ ] Developer Mode & Performance HUD
│   │   ├── [ ] Tap-to-unlock Developer mode toggles
│   │   ├── [ ] Mock API response options
│   │   └── [ ] Performance HUD overlay (FPS, latency, dropped frames)
│   └── [ ] Post-MVP Enhancements (Phase 2)
│       ├── [ ] Refactor to Clean Architecture structure
│       └── [ ] Migrate histories to SQLite database
└── [ ] Testing, QA & Deployment
    ├── [ ] Pytest suite validation (target >90% coverage)
    ├── [ ] Flutter unit, widget, and latency integration tests
    └── [ ] Signed Release APK build
```
