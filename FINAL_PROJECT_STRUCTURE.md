# MediSign-AI Final Project Structure

Below is the complete final repository layout for the MediSign-AI project, showcasing the centralized model storage and merged dataset hierarchy.

```
MediSign-AI/
│
├── .env                                 # Central environment configuration
├── .gitignore                           # Excludes large binaries/datasets
├── CLAUDE.md                            # Claude Code project context
├── DATASET_ORGANIZATION_REPORT.md       # Dataset organization report
├── DATASET_SUMMARY.md                   # Video data augmentation statistics
├── FINAL_PROJECT_STRUCTURE.md           # This structure overview document
├── FINAL_VERIFICATION.md                # Verification report
├── MODEL_COMPARISON.md                  # Comparative analytics (Model V1 vs V2)
├── VALIDATION_REPORT.md                 # Model V1 validation report
├── VALIDATION_REPORT_V2.md              # Model V2 validation report
│
├── backend/                             # Original Flask backend package
│   ├── app.py                           # Flask backend server launcher
│   ├── requirements.txt                 # Backend dependencies
│   ├── models/                          # CENTRAL MODEL FOLDER
│   │   ├── gesture_model_full.pkl       # Indian Sign Language model
│   │   ├── medisign_model.keras         # Original TensorFlow model
│   │   ├── emergency_model.pkl          # Emergency Gesture Model V1 (Fallback)
│   │   ├── emergency_model_v2.pkl       # Emergency Gesture Model V2 (Active Production)
│   │   ├── hand_landmarker.task         # MediaPipe Tasks Hand model
│   │   └── nonexistent_landmarker.task  # Mock landmarker for testing
│   └── emergency/                       # Video augmentation subsystem scripts
│       └── augmentation/
│           ├── README.md
│           ├── augment_videos.py
│           ├── augmentation_config.py
│           ├── augmentation_utils.py
│           ├── compare_models.py
│           ├── preview.py
│           └── logs/
│
├── emergency/                           # Emergency module codebase
│   ├── api.py                           # FastAPI gateway server launcher
│   ├── requirements.txt                 # FastAPI dependencies
│   ├── config/                          # Configuration loader package
│   │   ├── __init__.py
│   │   ├── config.toml                  # Settings file (models_dir points to backend/models)
│   │   ├── constants.py
│   │   ├── logging_config.py
│   │   ├── paths.py                     # Dynamically resolves models_dir relative to project root
│   │   └── settings.py
│   ├── models/                          # Empty model folder (kept in git via .gitkeep)
│   │   └── .gitkeep
│   ├── output/                          # Intermediary training artifacts
│   │   ├── frames/                      # Extracted frame images
│   │   ├── processed/                   # Cleaned frame images
│   │   └── landmarks/                   # Extracted landmark coordinates (.csv)
│   ├── reports/                         # Training, features & landmarks execution logs
│   ├── scripts/                         # Phase scripts (extraction, processing, train)
│   ├── tests/                           # Subsystem pytest integration files
│   └── utils/                           # Core utilities (model manager, predictor)
│
├── frontend/                            # Client application package
│   └── medisign_app/                    # Flutter project directory
│       ├── lib/                         # Dart source files
│       │   ├── main.dart                # Tabbed UI Shell (Sign language, Emergency)
│       │   ├── emergency_view.dart      # Direct vision capture, TTS, alerts
│       │   └── ...
│       ├── pubspec.yaml
│       └── ...
│
├── SOS/                                 # Merged Dataset Folder
│   ├── accident/                        # Contains both raw and augmented videos
│   ├── call/
│   ├── doctor/
│   ├── help/
│   ├── hot/
│   └── pain/
│
└── docs/                                # Documentation and project plans
```
