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
