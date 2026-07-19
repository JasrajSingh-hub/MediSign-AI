# MediSign-AI: Project Risk Analysis

This document identifies potential technical, algorithmic, and performance risks along with mitigation plans.

---

## 1. Technical & Framework Risks

### A. iOS/Android Platform Divergence
* **Risk**: Flutter plugins (`vibration`, `camera`, `audioplayers`) behave differently across platforms. For example, iOS handles vibration in structured durations, whereas Android requires custom pattern waveforms.
* **Probability**: Medium | **Impact**: Medium | **Severity**: Medium
* **Mitigation**: Wrap platform-specific hardware calls in abstraction interfaces (e.g. `VibrationService`) and use target platform checks to apply custom parameters.

---

## 2. Machine Learning Risks

### A. Generalization Under Poor Lighting & Background Noise
* **Risk**: The Random Forest model trained on structured video datasets may fail in real-world clinic rooms with low light or cluttered backgrounds.
* **Probability**: High | **Impact**: High | **Severity**: High
* **Mitigation**: Implement a fallback mechanism. If MediaPipe's confidence score drops below 0.50, return a specific status code (`"No hand landmarks found"`), and display a UI prompt to the user: *"Please adjust lighting or hand positioning."*

### B. Landmark Extraction Latency
* **Risk**: Running MediaPipe landmark extraction on every frame on low-end servers can lead to prediction queue build-up.
* **Probability**: Medium | **Impact**: High | **Severity**: High
* **Mitigation**: Implement frame queue limits on the server. If the server is currently processing a frame, drop any new incoming frame requests instantly.

---

## 3. Flutter Application Performance Risks

### A. Main Thread Blocking (UI Jank)
* **Risk**: Periodic base64 image encoding and JSON generation can cause UI stuttering.
* **Probability**: High | **Impact**: High | **Severity**: High
* **Mitigation**: Offload base64 and JPEG compression to a background thread using Flutter's `compute()` isolate function.

### B. Memory Leaks from Camera Controllers
* **Risk**: Failing to properly dispose of the `CameraController` when leaving the page will lead to memory leaks.
* **Probability**: Medium | **Impact**: High | **Severity**: High
* **Mitigation**: Implement strict lifecycle management in `dispose()` callbacks. Verify that the capture loop timer is cancelled before disposing of the camera controller.

---

## 4. Privacy & Telemetry Risks (Future Analytics)

### A. Patient Data Leakage (HIPAA/GDPR Mismatches)
* **Risk**: Unintentional upload of patient names, doctor details, or camera images during crash reporting or usage telemetry.
* **Probability**: Low | **Impact**: Critical | **Severity**: Critical
* **Mitigation**:
  * Ensure crash report payloads are strictly stripped of all personally identifiable information (PII).
  * Do not upload images or audio to the cloud. All inferences are processed locally on the local server.
  * Turn off automatic telemetry by default, allowing clinical institutions to opt-in manually.
