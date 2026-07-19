# MediSign-AI: Technical Debt Registry

This document lists identified technical debt, recommends refactoring tasks, and provides estimated efforts.

---

## Technical Debt Register

### Debt Item 1: Monolithic Layout in `lib/main.dart`
* **Description**: Camera setup, HTTP connections, timer routines, and UI rendering are combined in a single file.
* **Priority**: High (Deferred to post-MVP Phase 4 refactoring).
* **Recommendation**: Following initial feature integration, refactor the codebase to modular structures (e.g. `providers/`, `services/`, `screens/`).
* **Estimated Effort**: 6 hours.

### Debt Item 2: MediaPipe Version Fragmentation
* **Description**: The Sign Language backend uses legacy MediaPipe Hand Solutions, while the Emergency backend uses the modern MediaPipe Tasks API.
* **Priority**: Medium
* **Recommendation**: Standardize both backends to use the modern MediaPipe Tasks API on the unified FastAPI server.
* **Estimated Effort**: 4 hours.

### Debt Item 3: Session Isolation for Word Building
* **Description**: The Flask backend uses global variables to track word building. This is not multi-session safe.
* **Priority**: High (Addressed during Flask-to-FastAPI gateway migration).
* **Recommendation**: Introduce session keys (using client host or session IDs) to isolate word construction states.
* **Estimated Effort**: 3 hours.

### Debt Item 4: Hardcoded Windows Paths in Training Scripts
* **Description**: `backend/track_hand.py` uses hardcoded path strings pointing to `D:/medsign/dataset`.
* **Priority**: High
* **Recommendation**: Refactor all file references to use dynamic, relative path construction.
* **Estimated Effort**: 1 hour.

### Debt Item 5: SharedPreferences to SQLite Migration
* **Description**: For the MVP, prediction history and OCR records are stored as serialized JSON strings in SharedPreferences. This is inefficient for large datasets.
* **Priority**: Low (Deferred to post-MVP Phase 4 database migration).
* **Recommendation**: Migrate history and OCR records storage to a local SQLite database (`sqflite`).
* **Estimated Effort**: 4 hours.
