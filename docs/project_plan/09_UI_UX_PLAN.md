# MediSign-AI: UI/UX Screen Design Plan

This document details the interface layout, screen designs, navigation flows, and user interactions for MediSign-AI.

---

## 1. Bottom Navigation Tabs

The app uses a bottom navigation bar layout:
* **Tab 1: Sign Language**: Translates static hand signs.
* **Tab 2: Emergency**: Continuous camera scan and alarm.
* **Tab 3: Prescription OCR**: Prescription capture and parsing.
* **Tab 4: Speech Translation**: Audio translation.
* **Tab 5: Settings**: System settings and Developer tools.

---

## 2. Screen Blueprints & Wireframes

### A. Settings & Developer Mode Page
* **Standard Panel**: Render configuration controls (URL, threshold slider, alert toggles).
* **Secret Switch**: Tapping the "MediSign Settings" page header 7 times toggles the Boolean `pref_developer_mode`.
* **Developer Controls View**: When active, a new section appears at the bottom:
  * *Mock Backend Outputs*: Toggle switches that force the UI to render mock prediction values.
  * *Adjust FPS Interval Slider*: Tweak frames per second values from 1 FPS to 10 FPS.
  * *Display Performance HUD*: Toggle overlay displaying Capture FPS, Prediction FPS, Latency (ms), and Dropped Frames.
  * *Console Log Inspector*: Button opening a scrollable terminal view displaying runtime app logs.

### B. Model Information Screen
* **Navigation**: Accessible via a card on the Settings tab named: `Model & System Info`.
* **Content Cards**:
  * **Sign Language Model**:
    * Type: Random Forest Classifier
    * Features: 126 hand coordinates (normalized)
    * Source: `gesture_model_full.pkl`
  * **Emergency Gesture Model**:
    * Type: Random Forest Classifier
    * Features: 294 inputs (angles, distances, states)
    * Source: `emergency_model.pkl`
  * **Landmarker Pipeline**:
    * Engine: MediaPipe HandLandmarker Tasks API
    * Model: `hand_landmarker.task`

### C. Lazy Permissions Overlay Widget
* Rendered on camera/mic screens when permissions are not granted.
* Displays a centered lock icon, a text prompt: *"Camera access is required for real-time translation."*, and a primary button: `Grant Permissions`. Clicking this triggers native permission requests. If permanently denied, redirect users to device settings using `openAppSettings()`.

---

## 3. Dynamic Alerts UX (Emergency Screen)

When an emergency gesture (e.g. *PAIN*) is predicted with confidence exceeding the user-configured threshold:

```
[Normal View] ──(Emergency Detected)──> [Warning State]
                                              │
                    ┌─────────────────────────┴────────────────────────┐
                    ▼                                                  ▼
           [Active Alarm UI]                                  [Native Triggers]
      - Red flashing banner overlay                       - Loop vibration pulses
      - "DISMISS ALERT" button                            - Audio buzzer alert
                                                          - TTS voice announcement
```
* The alert state can be closed by pressing the **DISMISS ALERT** button, which suspends alarms for 30 seconds.
