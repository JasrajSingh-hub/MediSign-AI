# MediSign AI

MediSign AI is a local sign-language workspace with a Flutter mobile app and multiple Python backends.

The app is designed to run with the backend services on your laptop and the Flutter client on an Android phone or emulator. For a physical phone over USB, use `adb reverse` so the app can reach the local servers through `127.0.0.1`.

## What This Repo Contains

- `backend/app.py`: sign-language to text and avatar token parsing on port `5000`
- `backend/tts_service.py`: text-to-speech and speech-to-text on port `5001`
- `module_b_backend/main.py`: prescription safety backend on port `8002`
- `frontend/medisign_app`: Flutter client that talks to the local services

## Prerequisites

- Python 3.10 or newer
- Flutter 3.10+ with the Android toolchain configured
- Android SDK platform-tools (`adb`)
- FFmpeg and FFprobe on your PATH
- A physical Android phone with USB debugging enabled, or an Android emulator

## Install

### 1) Clone the repository

```powershell
git clone https://github.com/JasrajSingh-hub/MediSign-AI.git
cd MediSign-AI
```

### 2) Set up the main backend

```powershell
cd backend
python -m venv env
. .\env\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Set up the Flutter app

```powershell
cd ..\frontend\medisign_app
flutter pub get
```

### 4) Optional: set up the prescription backend

```powershell
cd ..\..\module_b_backend
python -m venv env
. .\env\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

Open separate terminals for each service.

### Main sign-language backend

```powershell
cd backend
. .\env\Scripts\Activate.ps1
python app.py
```

This serves:

- `POST /predict`
- `POST /api/v1/avatar/parse`

### TTS and STT backend

```powershell
cd backend
. .\env\Scripts\Activate.ps1
python tts_service.py
```

This serves:

- `GET /api/v1/tts/health`
- `GET /api/v1/tts/voices`
- `POST /api/v1/tts/speak`
- `POST /api/v1/stt/transcribe`

### Prescription backend

```powershell
cd module_b_backend
. .\env\Scripts\Activate.ps1
python main.py
```

This serves the prescription safety routes on port `8002`.

### Flutter app

```powershell
cd frontend/medisign_app
flutter run
```

## USB Connection

If you are using a physical Android phone, forward the local ports to the device before launching the app:

```powershell
adb reverse tcp:5000 tcp:5000
adb reverse tcp:5001 tcp:5001
adb reverse tcp:8002 tcp:8002
```

If you later enable the emergency service on port `8001`, add:

```powershell
adb reverse tcp:8001 tcp:8001
```

## How The App Reaches The Servers

The Flutter client currently points to local URLs in `frontend/medisign_app/lib/core/config/backend_endpoints.dart`.

- Sign prediction uses `http://127.0.0.1:5000`
- TTS and STT use `http://127.0.0.1:5001`
- Prescription safety uses `http://127.0.0.1:8002`

That means the phone or emulator must be able to reach your laptop on those ports.

## Troubleshooting

- `Connection refused` usually means the backend is not running, the port is wrong, or `adb reverse` is missing.
- `No module named edge_tts` means the TTS backend was started in the wrong Python environment. Reinstall `backend/requirements.txt` in the same venv you use to run `tts_service.py`.
- If STT fails, make sure FFmpeg and FFprobe are installed and visible on PATH.
- If Flutter keeps using stale generated files, run `flutter clean` inside `frontend/medisign_app` and then `flutter pub get`.

## Notes

- The repository includes trained model and asset files that the app expects at runtime.
- Keep the generated files, virtual environments, and local datasets out of version control. The root `.gitignore` already covers the common ones.
