# MediSign-AI: Testing and QA Plan

This document establishes the testing strategy, frameworks, coverage goals, and performance benchmarks for the MediSign-AI platform.

---

## 1. Test Architecture Matrix

```
[Testing Strategy]
  ├── Backend Python (pytest) ──> Coverage Goal: >90% (currently 92.42%)
  └── Flutter Client (flutter_test)
        ├── Unit Tests: Models, Settings, Caching
        ├── Widget Tests: Dashboard, Banners, Cards
        └── Integration Tests: E2E capture pipelines and network latency
```

---

## 2. Python Backend Test Suite

* **Framework**: `pytest`, `pytest-cov`, `httpx` (for FastAPI client).
* **Test Command**:
  ```powershell
  python -m pytest emergency/tests --cov=config --cov=utils --cov=api --cov-report=term-missing --cov-fail-under=90
  ```

---

## 3. Flutter Client Test Suite

### A. Unit Tests (`test/unit/`)
* **Focus**: Data parsing, and settings updates.
* **Coverage Targets**:
  * Verify that JSON parser helper methods map coordinates without loss of precision.
  * Verify settings serialization to `SharedPreferences`.

### B. Widget Tests (`test/widget/`)
* **Focus**: UI layout and state transitions.
* **Coverage Targets**:
  * Verify the tab navigation bar transitions screens correctly on click.
  * Verify that the `EmergencyBanner` is displayed when state flags change.
  * Verify button click updates toggle states inside providers.

### C. Integration Tests (`integration_test/`)
* **Focus**: Real-time camera streams and backend API integrations.
* **Coverage Targets**:
  * Measure camera frame capture latency (ensure time to capture remains under 100ms).
  * Validate correct connection status rendering on emulator networks.
  * Profile RAM and CPU usage over a 15-minute runtime to verify there are no memory leaks from unreleased camera controllers or timers.

---

## 4. Performance & Latency Benchmarks

| Metric | Target Value | Testing Method |
| :--- | :--- | :--- |
| **Capture FPS** | `3.0 - 5.3 FPS` (interval: 300-500ms) | Log and measure timestamps between camera stream captures on device. |
| **Prediction FPS** | `> 2.5 FPS` (under stable network) | Measure response frequency on HTTP predictions from port 8000. |
| **Average Latency** | `< 180 ms` (physical USB connection) | Record round-trip HTTP request-response durations. |
| **Dropped Frames** | `< 5%` under continuous operation | Track frames skipped because previous request was active. |
| **Memory Leak Tolerance**| `0MB` leak over 15 minutes of scan | Profile heap memory usage using Dart DevTools Memory profiler. |
