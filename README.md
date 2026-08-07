# 🏥 MediSign AI

**MediSign AI** is an intelligent, cross-platform healthcare accessibility solution designed to break down communication barriers in clinical environments. It integrates real-time Sign Language Recognition, 3D Sign Avatar translation, Voice & Speech synthesis, Emergency Triage scoring, and AI-assisted Prescription & Allergy Safety auditing.

---

## 📌 Project Overview

| Feature Module | Description | Key Tech / Models |
| :--- | :--- | :--- |
| 🖐️ **Sign Language Recognition** | Translates hand gestures into letters and words in real time. | MediaPipe Hands, OpenCV, Scikit-Learn (Random Forest) |
| 🧍 **Text-to-Sign Avatar** | Parses clinical text into sign token sequences (A-Z, SPACE) for avatar rendering. | FastAPI, NLP tokenization |
| 🗣️ **Voice & Speech Assist** | Converts speech to text and text to speech for seamless doctor-patient interactions. | Edge-TTS, pyttsx3, SpeechRecognition |
| 🚨 **Emergency Triage** | Evaluates patient symptoms and assigns emergency risk scores. | Custom Triage Scoring Engine |
| 💊 **Module B: Prescription Safety** | Checks drug-drug interactions, allergy risks, handwritten prescription OCR, and alternative medications. | OCR Engine, Interaction Matrix (`drug_interactions.csv`) |
| 📱 **Cross-Platform Frontend** | Flutter mobile & desktop user interface. | Flutter (Dart), Camera, Geolocator, Audio Players |

---

## 🌐 Network Ports & Service Map

Default service end-points used across the application:

| Service | Host | Port | Endpoint URL / Description |
| :--- | :--- | :--- | :--- |
| **FastAPI Backend (Main)** | `0.0.0.0` / `127.0.0.1` | **`5000`** | `http://127.0.0.1:5000` |
| **Health Check** | `127.0.0.1` | `5000` | `GET http://127.0.0.1:5000/health` |
| **Sign Prediction** | `127.0.0.1` | `5000` | `POST http://127.0.0.1:5000/predict` |
| **Avatar Tokenizer** | `127.0.0.1` | `5000` | `POST http://127.0.0.1:5000/api/v1/avatar/parse` |
| **TTS Speak** | `127.0.0.1` | `5000` | `POST http://127.0.0.1:5000/api/v1/tts/speak` |
| **STT Transcribe** | `127.0.0.1` | `5000` | `POST http://127.0.0.1:5000/api/v1/stt/transcribe` |
| **Emergency Triage** | `127.0.0.1` | `5000` | `POST http://127.0.0.1:5000/api/v1/emergency/predict` |
| **Prescription OCR Audit** | `127.0.0.1` | `5000` | `POST http://127.0.0.1:5000/api/v1/prescription/ocr-audit` |
| **Flutter Web Frontend** *(Optional)* | `localhost` | **`8080`** | `http://localhost:8080` (or dynamic port) |

---

## 🚀 Step-by-Step Execution Guide

### Prerequisites

- **Python**: Version `3.9` to `3.11` recommended
- **Flutter SDK**: Installed and added to system `PATH`
- **C++ Build Tools** (for OpenCV / MediaPipe on Windows if needed)

---

### 1. Running the Backend Server

1. Open PowerShell / Command Prompt and navigate to the `backend` directory:
   ```powershell
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install required Python packages:
   ```powershell
   pip install -r requirements.txt
   ```

4. Launch the FastAPI backend server:
   ```powershell
   python main.py
   ```
   *Alternative entry point:*
   ```powershell
   python app.py
   ```
   > ✅ Backend will start listening on **`http://127.0.0.1:5000`**. Check `http://127.0.0.1:5000/health` to confirm it's running.

---

### 2. Running Module B (Prescription Safety Engine - Standalone)

If running the isolated Module B prescription audit backend:

```powershell
cd backend/module_b_backend
python main.py
```

---

### 3. Running the Flutter Frontend App

1. Open a new terminal and navigate to the Flutter application directory:
   ```powershell
   cd frontend/medisign_app
   ```

2. Fetch Flutter package dependencies:
   ```powershell
   flutter pub get
   ```

3. Run the application:
   - **For Windows Desktop:**
     ```powershell
     flutter run -d windows
     ```
   - **For Chrome Web (on port 8080):**
     ```powershell
     flutter run -d chrome --web-port 8080
     ```
   - **For Android Emulator:**
     ```powershell
     flutter run -d android
     ```

---

## 📁 Repository Structure

```text
MediSign-AI/
├── backend/                  # FastAPI Backend & Machine Learning Services
│   ├── app.py                # MediaPipe & RF Gesture Recognition Endpoint
│   ├── main.py               # Main FastAPI Router entry point (Port 5000)
│   ├── requirements.txt      # Python dependencies
│   ├── models/               # Pre-trained ML models (gesture_model_full.pkl)
│   ├── routers/              # Modular API routes (Avatar, Emergency, TTS, STT, Triage)
│   └── module_b_backend/     # Prescription safety & allergy analysis engine
├── frontend/
│   └── medisign_app/         # Flutter Cross-Platform Application
│       ├── lib/              # App screens, features & services
│       ├── assets/           # Sign avatar library & static resources
│       └── pubspec.yaml      # Flutter dependencies
└── dataset/                  # Machine learning datasets & trained weights
```
