MediSign AI Deployment and System Configuration Guide
1. Executive Summary and Architecture Context
Platform Objective: MediSign AI provides an intelligent, low-latency cross-platform workspace engineered to translate real-time sign language gestures between healthcare clinicians and speech- or hearing-impaired patients.

Frontend Role: A high-frequency Flutter mobile app acts as a persistent client-side frame buffer, capturing images at a steady interval.

Backend Role: An isolated TensorFlow and Flask backend microservice hosts the custom-trained AI brain on the local laptop machine.

Network Tunneling: To circumvent network bottlenecks—like Access Point (AP) isolation, firewalls, and Android runtime exceptions—the architecture completely bypasses wireless connections. Data is routed through a physical Android Debug Bridge (adb) reverse TCP mapping tunnel on port 5000.

2. Backend Environment and Dependency Provisioning
Sandbox Isolation: Creating an isolated Python virtual environment prevents package collisions across your laptop's global system host.

Environment Creation: From the project's root repository directory, initialize the environment files by running:

PowerShell
python -m venv env
Workspace Activation:

Windows (PowerShell): .\env\Scripts\activate

macOS / Linux: source env/bin/activate

Package Optimization & Installation: Once the terminal is prefixed with the active (env) tag, upgrade your package manager and download the computer vision and machine learning frameworks:

PowerShell
python -m pip install --upgrade pip
pip install flask flask-cors tensorflow opencv-python numpy pillow
3. Frontend Client Installation and Verification
Workspace Synchronization: The mobile client relies on the Flutter SDK to handle camera interactions and parse UI elements. Move into your workspace core:

Bash
cd frontend/medisign_app
Cache Wiping: Clear away stale temporary binaries to avoid compilation mismatches:

Bash
flutter clean
Dependency Linking: Fetch and link the verified package ecosystem by executing:

Bash
flutter pub get
Locked Library Branches: The configuration uses exact production versions in your pubspec.yaml to ensure device-level stabilization:

camera: ^0.10.6 (Forces a stable, legacy-compatible hardware pipeline)

http: ^1.2.0 (Manages edge-to-server request layouts)

4. Execution Workflow and Synchronized Startup Sequence
Step 1: Start the Local Flask Engine

Run the server file from your dedicated Python terminal window:

PowerShell
python backend/app.py
Wait until the console outputs the verification text: ✅ Model loaded cleanly and successfully!

Step 2: Engage the Physical USB Bridge

Connect your Android phone to the laptop via a USB cable (ensure USB Debugging is turned on in Developer Options).

Open a separate laptop terminal workspace and execute the direct reverse tunnel mapping:

PowerShell
& "C:\Users\jasuj\AppData\Local\Android\Sdk\platform-tools\adb.exe" reverse tcp:5000 tcp:5000
Step 3: Deploy the Mobile UI

In your Flutter terminal workspace, compile and boot the app on your connected handset:

Bash
flutter run
Accept the native camera permission prompts on your phone screen to start processing.

5. Computer Vision Matrix Preprocessing and Standardization
Orientation Alignment: Mobile cameras record image bytes horizontally even when held vertically. Flask rotates the incoming base64 payload right-side up before inference to match the training data:

Python
image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
Color Channel Standardization: Flutter captures snapshots using standard RGB profiles, while OpenCV processes matrices as BGR arrays. The server switches the channels so the model interprets skin tones correctly:

Python
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
Pixel Grid Normalization: Incoming raw pixel arrays ranging from 0 to 255 are scaled to match the floating-point dimensions expected by the Keras layers:

Python
image = image.astype('float32') / 255.0


















## 6. Developer Knowledge Transfer (DKT) - Feature 2: Sign Language → Speech (The Verbalizer)

This section provides comprehensive details on the implementation of Feature 2, which introduces a reusable Text-to-Speech (TTS) module independent of hand sign detection, alongside a user interface in Flutter to compose and play speech.

### Backend Services Architecture

The backend of this project is split into two separate servers, each serving as a dedicated microservice for its respective feature:


1. **Sign-to-Text Inference Backend (Feature 1)**:
   - **File**: [backend/app.py](MediSign-AI/backend/app.py)
   - **Framework**: Flask (running on Port `5000`)
   - **Role**: Loads the custom Keras hand sign prediction model and provides the gesture translation API (`POST /predict`).

2. **Text-to-Speech Verbalizer Backend (Feature 2)**:
   - **File**: [backend/tts_service.py](MediSign-AI/backend/tts_service.py)
   - **Framework**: FastAPI (running on Port `5001`)
   - **Role**: Implements in-memory rate-limiting, text validation, SSML tag sanitization, online/offline voice synthesis, and returns raw audio binary streams (`POST /api/v1/tts/speak`).



### Technology Stack & Architecture
- **Framework**: FastAPI (chosen for high performance, automatic OpenAPI documentation, and asynchronous handling of streaming audio binary content).
- **TTS Core**: Python backend server running on port `5001`.
- **Audio Output**: Buffered binary stream played directly from client memory without file storage.

### Python Backend Packages Added
- `fastapi` & `uvicorn` (ASGI web framework and web server)
- `edge-tts` (Microsoft Edge high-quality online speech engine)
- `pyttsx3` (Offline native OS voice synthesizer)
- `python-dotenv` (Load configuration parameters)
- `pytest` & `httpx` (API test suite and async client checks)

### Flutter Client Packages Added
- `audioplayers: ^6.0.0` (Native audio streaming and memory-buffer player support)

### API References (FastAPI - Port 5001)

#### 1. TTS Synthesis Route
- **Endpoint**: `POST /api/v1/tts/speak`
- **Request Type**: `application/json`
- **Request Parameters**:
  ```json
  {
    "text": "I have chest pain",
    "language": "en-IN",
    "session_id": "uuid-identifier-string"
  }
  ```
- **Constraints & Validations**:
  - Maximum text length: 500 characters.
  - Rejects empty or whitespace-only inputs (validated via Pydantic model).
  - Language code must follow BCP-47 formatting tag (validated via regular expressions).
  - Automatically strips XML/HTML tags from text inputs to prevent SSML injection.
  - In-memory rate limiting applied (returns `429 Too Many Requests` on exceeding limits).
- **Response**: Binary audio stream payload (`audio/mpeg` for EdgeTTS, `audio/wav` for Pyttsx3).

#### 2. Get Voices Index Route
- **Endpoint**: `GET /api/v1/tts/voices`
- **Request Type**: None
- **Response**: `application/json`
- **Response Structure (Example - Edge provider)**:
  ```json
  {
    "provider": "edge",
    "voices": [
      {
        "name": "en-US-AriaNeural",
        "short_name": "en-US-AriaNeural",
        "gender": "Female",
        "locale": "en-US"
      }
    ]
  }
  ```

#### 3. Health check Route
- **Endpoint**: `GET /api/v1/tts/health`
- **Request Type**: None
- **Response**: `application/json`
  ```json
  {
    "status": "healthy"
  }
  ```

### Developer Implementation Details
1. **TTSProvider Abstraction**: A baseline abstract class defines the `synthesize(text, language)` routine. Underneath, `EdgeTTSProvider` handles chunk-by-chunk stream buffers programmatically. `Pyttsx3Provider` encapsulates Windows SAPI5 engines inside a thread-safe `asyncio.Lock` and delegates blocking execution to worker threads, creating and cleaning up temporary files immediately.
2. **Patient Data Security**: Zero-footprint audio processing. Patient speech arrays are generated directly in RAM buffers and streamed immediately. No audio clips are saved locally, and raw query strings are omitted from log summaries.
3. **Flutter Sentence Builder Layout**: Users can click `Append` next to the camera prediction text to insert letters into the active text editor box, write custom phrases manually, switch locale voices from the dropdown list dynamically, and click `Play Speech` to play audio bytes via `BytesSource` memory streams.

### Repository Feature Map

Below is a map indicating which files implement which features in the repository:

| Feature Name | Component | File Path | Description |
| :--- | :--- | :--- | :--- |
| **Feature 1: Sign Language → Text** | Backend Flask API | [backend/app.py](MediSign-AI/backend/app.py) | Hosts the `/predict` route, loads the Keras model, processes images, and outputs raw predicted letters. |
| **Feature 1: Sign Language → Text** | Model Training | [backend/track_hand.py](MediSign-AI/backend/track_hand.py) | Script to compile, study and output the Keras network model. |
| **Feature 1: Sign Language → Text** | Neural Network Model | [backend/models/medisign_model.keras](MediSign-AI/backend/models/medisign_model.keras) | The trained Indian Sign Language (ISL) Keras model weights. |
| **Feature 2: Sign Language → Speech** | Backend FastAPI | [backend/tts_service.py](MediSign-AI/backend/tts_service.py) | Microservice containing speak/voices endpoints, sanitizers, and online/offline TTS providers. |
| **Feature 2: Sign Language → Speech** | Config Template | [backend/.env.example](MediSign-AI/backend/.env.example) | Template file outlining provider, port, and rate limiting options. |
| **Feature 2: Sign Language → Speech** | Active Config | [backend/.env](MediSign-AI/backend/.env) | Running configuration parameter file. |
| **Feature 2: Sign Language → Speech** | Unit Tests | [backend/tests/test_tts.py](MediSign-AI/backend/tests/test_tts.py) | Python test suite verifying health, voice directories, validation, and rate limit triggers. |
| **Feature 2: Sign Language → Speech** | Client UI Integration | [frontend/medisign_app/lib/main.dart](MediSign-AI/frontend/medisign_app/lib/main.dart) | Connects camera inference to a text panel and embeds the sentence-builder tools, voice dropdown selectors, and play action using `audioplayers`. |
| **Feature 2: Sign Language → Speech** | Dependencies | [frontend/medisign_app/pubspec.yaml](MediSign-AI/frontend/medisign_app/pubspec.yaml) | Linked package dependencies including `audioplayers`. |
| **Feature 2: Sign Language → Speech** | Client Integration Tests | [frontend/medisign_app/test/widget_test.dart](MediSign-AI/frontend/medisign_app/test/widget_test.dart) | Contains client UI widget tests. |


