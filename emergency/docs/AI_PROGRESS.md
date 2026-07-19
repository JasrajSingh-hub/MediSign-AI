# AI Progress — Emergency Gesture Recognition

Auto-maintained log of module progress. One entry per completed phase.

| Phase | Name                     | Status      | Date       | Notes |
|-------|--------------------------|-------------|------------|-------|
| 1     | Project Backbone         | Complete    | 2026-07-16 | config, paths, logger, constants, README created; imports + SOS scan (624 videos) verified. |
| 2     | Dataset Analysis         | Complete    | 2026-07-16 | Scanned 624 videos / 6 classes / 2.58 GB; reports written to reports/. |
| 3     | Frame Extraction         | Complete    | 2026-07-16 | Lazy OpenCV extraction, corrupted-skip, tqdm progress, manifest.json. Offline: orchestration + corrupted-path verified; decode runs once cv2 installed. |
| 4     | Image Processing         | Complete    | 2026-07-16 | lazy cv2 transforms (resize/contrast/equalise/denoise/normalize), config-driven plan, processed manifest. Offline: plan + orchestration verified. |
| 5     | Landmark Extraction      | Complete    | 2026-07-16 | MediaPipe (lazy), 21-landmark normalize, CSV (stdlib) + Parquet (best-effort), landmark report. Offline: pure logic + offline batch verified. |
| 6     | Feature Engineering      | Complete    | 2026-07-16 | Pure-Python distance/angle/finger-state/palm-direction features (231 engineered + 63 base = 294). Fully offline-testable; batch reads landmarks.csv -> features.csv + report. |
| 7     | Training                 | Complete    | 2026-07-16 | Pure split + metrics (offline); sklearn RF + CV + grid search + save pkl (gated). Offline: load/split/metrics + graceful skip verified. |
| 8     | Prediction Engine        | Complete    | 2026-07-16 | Singleton `EmergencyPredictor`, injectable model (offline-testable), confidence + per-class probs + threshold flag + logging. Offline: logic verified via stub model. |
| 9     | FastAPI                  | Complete    | 2026-07-16 | `api.py`: /health, /status, /predict (file or base64), Swagger /docs, CORS, logging. Pipeline in `utils/inference.py` (lazy cv2/MediaPipe). Offline: compile + inference error-path verified; route/Swagger tests gated. |
| 10    | Testing                  | Complete    | 2026-07-17 | 93→140+ pytest tests green; **coverage 92.4%** (target 90% met). Added `httpx` dep, scripts/api/inference/dataset/feature-engineering coverage tests. Fixed `run_feature_engineering` missing `skipped` key. |
| 11    | HTML Testing Frontend    | Complete    | 2026-07-17 | `frontend/index.html`: webcam capture, POST to `/predict`, label/confidence/per-class bars, emergency banner + Web Audio alarm, model status, error log. Served at `/frontend/` (mounted in `api.py`). |
| 12    | Packaging                | Complete    | 2026-07-17 | `Dockerfile` (py3.12-slim + OpenCV/MediaPipe libs), `docker-compose.yml` (port 8000, models volume, `/health` healthcheck), `.dockerignore`, `DOCKER.md`. |

## Summary
- Module is fully independent of the existing Sign Language Recognition backend.
- Config-driven (TOML, stdlib `tomllib`); no hardcoded paths.
- 6 emergency classes (incl. undocumented `hot`); configurable.
- Parquet output is best-effort (skipped with a note when `pandas`/`pyarrow` are
  absent); the CSV is the authoritative training artefact. Landmark *detection*
  needs real hand imagery, so it is validated by MediaPipe at runtime, not by
  synthetic offline tests (the no-hand path is covered by integration tests).

## Verification — 2026-07-17
Environment unblocked and code health re-verified this session:

- **Python 3.12.10** runs from `.venv` (the earlier "python fails to start"
  blocker from the handoff is resolved in this environment).
- `emergency/requirements.txt` installed into `.venv` (sklearn 1.9, cv2 5.0,
  mediapipe 0.10.35, fastapi, pytest-cov). Added **`httpx`** — required by the
  FastAPI `TestClient` and previously missing from the requirements.
- `python -m compileall -q emergency` passes (exit 0).
- **Full suite: 93 tests, all green** (`pytest emergency/tests -q`, exit 0).

### Bugs fixed this session
- `utils/predictor.py`: added the missing `from pathlib import Path` (P0 from
  handoff). Also fixed `list(getattr(model, "classes_", []) or [])` which raised
  `ValueError: ambiguous truth value` when `classes_` was a NumPy array — now
  uses an explicit `is not None` check (both the `__init__` and `ensure_loaded`
  paths).
- `utils/inference.py`: guard empty image bytes (previously crashed
  `cv2.imdecode`); wrap MediaPipe `create_hands`/`detect_landmarks` so any
  failure returns `{"available": False, "error": ...}` instead of raising.
- `utils/model_utils.py`: `run_training` now always sets `skipped` in its result
  (the success path previously omitted it, causing `KeyError: 'skipped'`);
  added a tiny-dataset guard that skips training when there are too few samples
  for the requested CV folds.
- **MediaPipe API port (significant):** `utils/landmark_utils.py` used the legacy
  `mp.solutions.hands` API, which **was removed in MediaPipe 0.10.10+**. On
  Python 3.12 only `mediapipe>=0.10.10` installs, so the code could not run.
  `create_hands` and `detect_landmarks` were ported to the **Tasks API**
  (`mp.tasks.vision.HandLandmarker`). The `hand_landmarker.task` model is
  auto-downloaded on first use (gitignored; not committed). `api.py`/`inference.py`
  updated to the new detection result shape.

### Test-expectation corrections (installed-environment fixes)
- `test_feature_utils.py::test_angles_in_range`: upper bound was `3.14159265`
  (slightly below π); changed to `math.pi`.
- `test_landmark_extraction_integration.py::test_normalize_with_numpy_input`:
  expected 63 for a 3-point input; the function returns variable length (9),
  matching its docstring and the pure-landmark test — corrected the assertion.
- `test_video_utils.py::test_extract_dataset_frames_writes_manifest`: test built
  4 fake files but asserted 2; corrected to 4.
- `test_utils_misc.py::test_read_class_directories_handles_missing`: test
  `mkdir`'d a *file* path then `write_bytes` onto it (Windows `PermissionError`);
  fixed the setup to create the directory first.
- `test_inference.py::test_predict_offline_returns_unavailable`: cv2 is now
  installed, so the undecodable path returns a "decode" error rather than the
  cv2-absent error; assertion relaxed to accept either.
- `test_predictor_integration.py::test_predictor_singleton_with_file`: the
  singleton is lazy, so `ensure_loaded()` must be called before `is_loaded` is
  `True` (matches the sibling test).

### Real-data smoke validation
Extracted 24 frames from a real `SOS/accident` video; the ported HandLandmarker
detected 1 hand (21 landmarks, confidence 0.99) on the first frame and produced
a 63-length normalized vector. Phases 3/5/6 are validated end-to-end on real data.

### Remaining
- Phase 10: raise coverage from 73% → 90% (cover `scripts/`, `api.py`,
  `utils/inference.py`, `utils/dataset_utils.py`).
- Phase 11: HTML test frontend. Phase 12: Docker packaging.
- Re-run `scripts.analyze_dataset` with OpenCV present to capture FPS/frame
  counts/resolution (handoff P1).
