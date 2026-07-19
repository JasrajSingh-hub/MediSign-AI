# MediSign-AI

MediSign-AI is an intelligent, low-latency sign-language translation and emergency communication platform designed to bridge the communication gap between healthcare clinicians and speech- or hearing-impaired patients in clinical environments.

---

## 1. Overview
In busy healthcare settings, patients who rely on sign language often face critical delays and barriers when communicating acute pain, needs, or symptoms to medical staff. MediSign-AI addresses this real-world healthcare communication problem by providing a dual-module real-time translation system:
1. **Indian Sign Language (ISL) Recognition**: Translates static sign language letters (A–Z) in real time.
2. **Emergency Gesture Recognition**: Detects dynamic patient gestures signaling critical situations (`help`, `pain`, `doctor`, `call`, `accident`, `hot`) and immediately alerts clinical personnel via visual, audio, haptic, and vocal indicators.

---

## 2. Features
* **Indian Sign Language Recognition**: High-precision recognition of ISL alphabetical signs.
* **Emergency Gesture Recognition**: Robust detection of 6 emergency gestural signs from video frames.
* **Speech-to-Text (STT) & Text-to-Speech (TTS)**: Dynamic vocal announcements and text displays.
* **Real-time Camera Recognition**: Continuous frame capture and inference loop (300–500ms intervals).
* **FastAPI Backend Microservice**: High-throughput, async Python backend managing inference pipelines and system diagnostics.
* **Flask Backend Microservice**: Legacy server backend supporting the original sign-language character classification features.
* **Flutter Mobile App**: Cross-platform application providing a smooth camera preview, configuration sliders, and persistent prediction logs.
* **MediaPipe Tasks API Integration**: Upgraded to the modern `HandLandmarker` model for skeletal hand tracking.
* **Developer Mode**: Hidden settings panel displaying API roundtrip latency (RTT), model metadata, and mock testing toggles.
* **Prediction History**: Persistent logs stored locally using `SharedPreferences`.
* **Alert System**: Pulse alert banner, pattern-based haptic vibrations, TTS notifications, and native ringtone alarms.
* **Background Processing**: Multi-threaded camera frame resizing and JPEG compression in a Flutter background isolate to maintain a solid 60 FPS UI.

---

## 3. Demo
*(Placeholders for release visual showcases)*
* **Screenshots**: `![MediSign UI Screenshot](docs/images/screenshot.png)`
* **GIFs**: `![Real-time Inference Loop](docs/images/inference_demo.gif)`
* **Video Demo**: `[Watch Project Demonstration Video](docs/video/demo.mp4)`

---

## 4. System Architecture

Below is the end-to-end data flow mapping frames from the patient's camera to the clinician alert:

```
[ Patient ] 
     │
     ▼ (Camera Feed)
[ Flutter Client App ] ──(Background Isolate Image Compression)
     │
     ▼ (Base64 JPEG via HTTP POST /predict)
[ FastAPI Backend Gateway ]
     │
     ▼ (BGR Array)
[ MediaPipe Tasks API ] ──(Extracts 21 Skeletal Landmarks)
     │
     ▼ (Wrist-centered & scale-normalized coordinates)
[ Custom Feature Engineering ] ──(Computes 294 Geometric Features)
     │
     ▼ (Spatial Vectors)
[ RandomForest Classifier ] ──(Predicts gesture class)
     │
     ▼ (Prediction JSON with Confidence)
[ Flutter Alert Engine ] ──(TTS Voice Alert + Haptics + Red Banner)
     │
     ▼ (Audible/Visual Signal)
[ Doctor/Clinician Alerted ]
```

---

## 5. Folder Structure

```
MediSign-AI/
├── .env                                 # Central environment configuration
├── .gitignore                           # Excludes build caches and venv
├── README.md                            # Comprehensive GitHub release guide
├── DATASET_ORGANIZATION_REPORT.md       # Video dataset statistics and moves
├── DATASET_SUMMARY.md                   # Video data augmentation metrics
├── MODEL_COMPARISON.md                  # Model V1 vs V2 performance analytics
├── FINAL_VERIFICATION.md                # Endpoint and count validations
│
├── backend/                             # Flask backend and shared model weights
│   ├── app.py                           # Flask backend server launcher
│   ├── models/                          # CENTRAL MODEL CACHE
│   │   ├── gesture_model_full.pkl       # Sign Language model weights
│   │   ├── medisign_model.keras         # TensorFlow ISL classifier weights
│   │   ├── emergency_model.pkl          # Emergency Gesture Model V1 (Fallback)
│   │   ├── emergency_model_v2.pkl       # Emergency Gesture Model V2 (Active Production)
│   │   ├── hand_landmarker.task         # MediaPipe Tasks Hand model
│   │   └── nonexistent_landmarker.task  # Mock landmarker task for test suite
│   └── emergency/                       # Video augmentation subsystem scripts
│       └── augmentation/
│           ├── README.md
│           ├── augment_videos.py
│           ├── augmentation_config.py
│           ├── augmentation_utils.py
│           ├── compare_models.py
│           └── preview.py
│
├── emergency/                           # FastAPI Emergency Gesture Module
│   ├── api.py                           # FastAPI gateway server launcher
│   ├── requirements.txt                 # FastAPI python requirements
│   ├── config/                          # Configuration parser package
│   │   ├── config.toml                  # Path configurations
│   │   ├── paths.py                     # Dynamically resolves models relative to project root
│   │   └── settings.py                  # Env overrides loader
│   ├── models/                          # Kept in Git as placeholder (.gitkeep)
│   ├── output/                          # Intermediary training outputs (Ignored by Git)
│   │   └── landmarks/                   # Extracted landmark coordinate datasets
│   ├── reports/                         # Landmark/feature reports
│   ├── scripts/                         # Frame extraction, landmarking, training scripts
│   ├── tests/                           # Pytest verification suites
│   └── utils/                           # Model manager, predictor abstractions
│
├── frontend/                            # Mobile client packages
│   └── medisign_app/                    # Flutter project workspace
│       ├── lib/                         # Dart files
│       │   ├── main.dart                # Tab shell and state orchestrator
│       │   └── emergency_view.dart      # Real-time capture, alerts, history
│       └── pubspec.yaml                 # Client dependencies
│
├── SOS/                                 # Merged Dataset Folder (Ignored by Git)
│   ├── accident/
│   ├── call/
│   ├── doctor/
│   ├── help/
│   ├── hot/
│   └── pain/
│
└── docs/                                # Project plans and phase reports
```

---

## 6. Tech Stack
* **Frontend**: Flutter SDK, Dart
* **Backend**: Python, FastAPI, Flask, OpenCV (cv2), MediaPipe, NumPy, Scikit-learn, Joblib
* **Machine Learning**: RandomForest Classifier, MediaPipe Tasks HandLandmarker, Custom Geometric Feature Engineering
* **Deployment**: Docker, Git, GitHub

---

## 7. Machine Learning Pipeline

The training and deployment pipeline consists of 11 distinct phases:

1. **Dataset**: Merged raw and augmented video clips grouped by class.
2. **Augmentation**: Generates synthetic video clips using randomized contrast, brightness, noise, zoom, translation, and rotational offsets.
3. **Frame Extraction**: Decodes `.avi` video containers into individual JPEG frame sequences.
4. **Image Processing**: Resizes images to `256x256` and applies CLAHE contrast, histogram equalization, and fast non-local means denoising.
5. **Landmark Extraction**: Detects 21 3D hand landmarks per frame using the MediaPipe Tasks API.
6. **Feature Engineering**: Computes 294 geometric features (joint angles, palm direction, pairwise distances, and finger states).
7. **Training**: Runs 5-fold stratified cross-validation and fits a `RandomForestClassifier`.
8. **Validation**: Measures accuracy, precision, recall, and Macro-F1.
9. **Comparison**: Tests models on a held-out test split to evaluate V1 vs V2 metrics.
10. **Deployment**: Relocates model files to `backend/models/` and loads them via the FastAPI gateway.
11. **Inference**: Exposes HTTP POST `/predict` to serve client frames.

---

## 8. Emergency Gesture Model
* **Dataset**: `1549` total video sequences (624 raw + 925 augmented).
* **Augmentations**: Enforces temporal consistency by applying identical random transforms across all frames of a clip.
* **Quality Gates**: Immediately validates augmented videos using MediaPipe Hands; discards any video where hand landmarks are tracked in `<80%` of frames. Removes clips with excessive blur or extreme over/under-exposure.
* **Features**: Combines 63 normalized coordinates with 231 engineered coordinates (joints, distances, states), totaling `294` features.
* **Classifier**: Trained a RandomForest model with `n_estimators=200` and `max_depth=20` evaluated via 5-Fold Stratified Cross-Validation.

### V1 vs V2 Comparison on Validation Test Split:
* **Model V1 (Original)**: Accuracy: `95.81%`, Macro F1: `95.77%`, Latency: `0.1045 ms/frame`
* **Model V2 (Augmented)**: Accuracy: `97.45%`, Macro F1: `97.44%`, Latency: `0.1157 ms/frame`
* **Improvement**: **+1.64% accuracy boost** and **+1.67% Macro-F1 boost**, confirming augmented training successfully increased model generalization under visual noise.

---

## 9. Algorithms & Mathematical Methods
* **MediaPipe Hands**: Employs a single-stage detector and hand landmarker tracking model.
* **Joint Angles**: Computes interior angles between bone segments using vector dot-products:
  $$\theta = \arccos\left(\frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|}\right)$$
* **Landmark Normalization**: Wrist-centers coordinates and scales them by the bounding box span:
  $$x_{\text{norm}} = \frac{x - x_{\text{wrist}}}{\max(x_{\text{span}}, y_{\text{span}})}$$
* **Image Adjustments**:
  * **CLAHE (Contrast Limited Adaptive Histogram Equalization)**: Limits noise amplification in local tiles.
  * **Gamma Correction**: Adjusts pixel intensities using a power-law transformation:
    $$V_{\text{out}} = A V_{\text{in}}^{\gamma}$$
  * **Filters**: Gaussian Blur, Gaussian Noise, and JPEG compression mapping.

---

## 10. API Documentation

### `GET /health`
* **Request**: None
* **Response**:
  ```json
  {
    "status": "ok",
    "system": {
      "platform": "win32",
      "cpu_count": 16,
      "cpu_percent": 0.0,
      "memory_used_mb": 0
    },
    "models": {
      "sign_language_loaded": true,
      "emergency_loaded": true,
      "hand_landmarker_loaded": true
    }
  }
  ```

### `GET /status`
* **Request**: None
* **Response**: Exposes versioning metadata, confidence thresholds, classes, and absolute file system paths for all loaded models.

### `POST /predict`
* **Request**: Multipart file upload (`file`) OR base64 Jpeg string (`image_base64`).
* **Response**:
  ```json
  {
    "label": "accident",
    "confidence": 0.975833,
    "probabilities": {
      "accident": 0.975833,
      "call": 0.004166,
      "doctor": 0.0,
      "help": 0.015,
      "hot": 0.005,
      "pain": 0.0
    },
    "is_emergency": true,
    "available": true
  }
  ```

### `POST /predict/sign`
* **Request**: Multipart file upload (`file`) OR base64 Jpeg string (`image_base64`).
* **Response**: JSON prediction payload for Indian Sign Language characters.

---

## 11. Installation

### Prerequisites
* Python 3.9+
* Flutter SDK (3.19.0+)

### Virtual Environment Setup (Windows/Linux/Mac)
1. Clone the repository and navigate to root:
   ```bash
   git clone https://github.com/DharmenderKumar/MediSign-AI.git
   cd MediSign-AI
   ```
2. Create and activate a Python virtual environment:
   * **Windows**:
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```
   * **macOS / Linux**:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
3. Install backend dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r emergency/requirements.txt
   ```

### Flutter Client Setup
1. Navigate to client folder:
   ```bash
   cd frontend/medisign_app
   ```
2. Clean and fetch packages:
   ```bash
   flutter clean
   flutter pub get
   ```

---

## 12. Running the Application

### 1. Launch the FastAPI Backend
Start the server from the `emergency/` directory:
```bash
cd emergency
..\.venv\Scripts\python.exe -m uvicorn api:app --port 8000
```
Ensure the terminal displays model loading completion messages.

### 2. Engage ADB Reverse Port Tunneling (Android Only)
Map the mobile port to the laptop localhost via USB Debugging:
```powershell
adb reverse tcp:8000 tcp:8000
```

### 3. Deploy the Mobile App
From `frontend/medisign_app`:
```bash
flutter run
```

---

## 13. Model Files Index
The following model and helper files land under `backend/models/` and are tracked in Git:
* **[gesture_model_full.pkl](file:///c:/Users/kamle/OneDrive/Desktop/MediSign-AI/backend/models/gesture_model_full.pkl)**: Sign Language RF weights.
* **[emergency_model.pkl](file:///c:/Users/kamle/OneDrive/Desktop/MediSign-AI/backend/models/emergency_model.pkl)**: Emergency Gesture Model V1 (Fallback).
* **[emergency_model_v2.pkl](file:///c:/Users/kamle/OneDrive/Desktop/MediSign-AI/backend/models/emergency_model_v2.pkl)**: Active Emergency Gesture Model V2 (Production).
* **[hand_landmarker.task](file:///c:/Users/kamle/OneDrive/Desktop/MediSign-AI/backend/models/hand_landmarker.task)**: MediaPipe hand tracking binary task file.

---

## 14. Dataset & Augmentation

> [!IMPORTANT]
> The **SOS** training dataset is intentionally excluded from this GitHub repository due to its large size (~8.7 GB of raw video files). It is ignored via `.gitignore` to prevent repository bloating.

### Recreating or Obtaining the Dataset:
1. **Original Raw Videos**: The original raw dataset consists of `624` video sequences (104 per class) representing patients signing gestural requests. These are organized into class folders under `SOS/` (`accident`, `call`, `doctor`, `help`, `hot`, `pain`).
2. **Augmentation Subsystem**: The augmented videos can be regenerated synthetically by placing the original raw videos in `SOS/` and executing the data augmentation pipeline:
   ```bash
   python backend/emergency/augmentation/augment_videos.py --workers 10
   ```
   This generates `925` verified augmented video clips inside `SOS_Augmented/` which can be merged with the originals inside `SOS/` (resulting in a total of `1549` video clips).

### Dataset Statistics & Structure:
* **Classes**: `accident`, `call`, `doctor`, `help`, `hot`, `pain`
* **Original Videos**: `624` clips
* **Augmented Videos**: `925` clips
* **Merged Dataset Count**: `1549` clips
* **Folder Structure**:
  * `SOS/accident/`: 247 videos
  * `SOS/call/`: 270 videos
  * `SOS/doctor/`: 251 videos
  * `SOS/help/`: 204 videos
  * `SOS/hot/`: 282 videos
  * `SOS/pain/`: 295 videos

---

## 15. Documentation Index
All structural plans and verification reports are stored within the repository:
* **Project Specifications**:
  * [01 Implementation Plan](file:///c:/Users/kamle/OneDrive/Desktop/MediSign-AI/docs/project_plan/01_IMPLEMENTATION_PLAN.md)
  * [02 Phases Guide](file:///c:/Users/kamle/OneDrive/Desktop/MediSign-AI/docs/project_plan/02_PHASES.md)
  * [03 Project Tasks Checklist](file:///c:/Users/kamle/OneDrive/Desktop/MediSign-AI/docs/project_plan/03_TASKS.md)
  * [04 System Architecture Design](file:///c:/Users/kamle/OneDrive/Desktop/MediSign-AI/docs/project_plan/04_ARCHITECTURE.md)
* **Model Reports**:
  * [Augmentation Pipeline Report](file:///c:/Users/kamle/OneDrive/Desktop/MediSign-AI/AUGMENTATION_REPORT.md)
  * [Dataset Summary Report](file:///c:/Users/kamle/OneDrive/Desktop/MediSign-AI/DATASET_SUMMARY.md)
  * [Model V1 vs V2 Comparison Report](file:///c:/Users/kamle/OneDrive/Desktop/MediSign-AI/MODEL_COMPARISON.md)
  * [Validation Report V2](file:///c:/Users/kamle/OneDrive/Desktop/MediSign-AI/VALIDATION_REPORT_V2.md)
  * [Final Dataset Organization Report](file:///c:/Users/kamle/OneDrive/Desktop/MediSign-AI/DATASET_ORGANIZATION_REPORT.md)
  * [Final Verification Report](file:///c:/Users/kamle/OneDrive/Desktop/MediSign-AI/FINAL_VERIFICATION.md)

---

## 16. Challenges Faced & Resolved
* **MediaPipe Tasks API Migration**: Solved version conflicts by replacing legacy `solutions.hands` with the modern `HandLandmarker` Tasks API and TFLite bindings.
* **Flutter Web Compatibility**: Replaced file stream writes (`File` from `dart:io`) with browser-safe `XFile.readAsBytes()` buffers.
* **Data Augmentation Constraints**: Designed filter loops rejecting videos that failed exposure bounds or landmarks tracking rates `<80%`.
* **Path Instability**: Converted all relative paths to project-root resolved paths via `pathlib` so the uvicorn backend executes cleanly from any Cwd.

---

## 17. Future Scope
* **Prescription OCR**: Integrate optical character recognition to parse medical prescription terms.
* **Offline Inference**: Support compiled TensorFlow Lite models for running client-side predictions completely offline.
* **Cloud Deployment**: Containerize the FastAPI backend via Kubernetes/Docker for deployment on AWS/GCP nodes.
* **More Gestures**: Train on a wider range of emergency words.
* **Deep Learning Models**: Benchmark against LSTMs and 3D CNNs.

---

## 18. Contributors
* **Repository Owner**: **Dharmender Kumar**
  * [GitHub Profile](https://github.com/DharmenderKumar)
  * [LinkedIn Profile](https://www.linkedin.com/in/dharmender-kumar)

---

## 19. License
This project is licensed under the MIT License. See `LICENSE` for details.
