# AI Changelog — Emergency Gesture Recognition

All notable changes to this module are documented here. Format: date — type — summary.

## 2026-07-16 — feat — Phase 9 (FastAPI)
- Added `utils/inference.py`: `predict_from_image_bytes` (lazy cv2/MediaPipe)
  image->landmark->feature->predict glue with graceful `available=False` errors.
- Added `api.py`: FastAPI app with `GET /health`, `GET /status`, `POST /predict`
  (UploadFile or base64 JSON), CORS, request logging; Swagger at `/docs`,
  OpenAPI at `/openapi.json`. Runs via `uvicorn api:app --port 8000`.
- Added `python-multipart` to `requirements.txt` (file uploads).
- Added `tests/test_inference.py` (offline error-path) and
  `tests/test_api_integration.py` (TestClient: health/status/openapi/docs/400;
  skipped without fastapi).

## 2026-07-16 — feat — Phase 8 (Prediction Engine)
- Added `utils/predictor.py`: `EmergencyPredictor` (lazy model load, `predict`,
  `predict_from_xyz`, `is_emergency` threshold flag, prediction logging) and the
  `get_predictor()` singleton (+ `reset_predictor`). A model object can be
  injected so the engine is unit-testable without scikit-learn.
- Added `scripts/predict.py` (`python -m scripts.predict [features.csv]`).
- Added `tests/test_predictor.py` (13 offline assertions via stub model) and
  `tests/test_predictor_integration.py` (train->save->load->predict; skipped
  without sklearn/joblib).

## 2026-07-16 — feat — Phase 7 (Training)
- Added `utils/model_utils.py`: pure `load_features_csv`, `train_test_split_stratified`
  (deterministic, reproducible), `classification_metrics` (pure accuracy /
  per-class P/R/F1 / macro-F1 / confusion matrix); lazy-sklearn `build_model`,
  `cross_validate`, `grid_search`, `save_model`/`load_model`/`predict`;
  `write_training_report` (md+json) and `run_training` (graceful sklearn skip).
- Added `scripts/train.py` (`python -m scripts.train`) with sklearn/joblib guard.
- Added `tests/test_model_utils.py` (17 offline assertions) and
  `tests/test_training_integration.py` (synthetic separable dataset; skipped
  without sklearn/numpy/joblib).

## 2026-07-16 — feat — Phase 6 (Feature Engineering)
- Added `utils/feature_utils.py`: pure-Python `pairwise_distances` (210),
  `joint_angles` (14), `finger_states` (5, rotation-invariant extension cue),
  `palm_direction` (2), `build_feature_vector` (63 base + 231 engineered = 294),
  `write_features_csv` (stdlib), `write_feature_report`, and
  `run_feature_engineering` (graceful skip when landmarks.csv is absent).
- Added `scripts/feature_engineering.py` (`python -m scripts.feature_engineering`)
  — no OpenCV/MediaPipe required, so it runs offline.
- Added `tests/test_feature_utils.py` (28 offline assertions; pytest-compatible).

## 2026-07-16 — feat — Phase 5 (Landmark Extraction)
- Added `utils/landmark_utils.py`: pure `normalize_landmarks` (wrist-centre +
  scale; accepts any count, 21 -> 63 values), `landmark_obj_to_xyz`,
  `landmark_feature_columns`, lazy `create_hands`/`detect_landmarks`,
  `write_landmark_dataset` (CSV via stdlib; Parquet best-effort), and
  `extract_dataset_landmarks` (writes `landmarks.csv`/`.parquet`/`manifest.json`
  + `landmark_report.md`/`.json`). Frames without a hand are excluded from CSV.
- Added `scripts/extract_landmarks.py` (`python -m scripts.extract_landmarks`).
- Added `tests/test_landmark_utils.py` (pure offline) and
  `tests/test_landmark_extraction_integration.py` (cv2/mediapipe/numpy-gated;
  blank-frame no-hand path + model build).

## 2026-07-16 — feat — Phase 4 (Image Processing)
- Added `utils/image_utils.py`: `build_processing_plan` (config-driven ordered
  transform list), individual transforms (`resize_image`, `adjust_contrast`
  CLAHE, `equalize_histogram`, `denoise` NL-means, `normalize_image` z-score→
  uint8), `process_frame`, and `process_dataset_images` (writes
  `processed/manifest.json`). All transforms keep `uint8` BGR for MediaPipe.
- Added `scripts/process_images.py` (`python -m scripts.process_images`) with
  cv2-missing guard.
- Added `tests/test_image_utils.py` (plan + offline orchestration) and
  `tests/test_image_processing_integration.py` (per-transform + flow; skipped
  without cv2/numpy).

## 2026-07-16 — feat — Phase 3 (Frame Extraction)
- Added `utils/progress.py`: tqdm wrapper with a no-op fallback (no hard tqdm dep).
- Added `utils/video_utils.py`: `sample_frame_indices` (pure sampling math; short
  clips keep all frames, longer clips sampled at `fps_target` and capped),
  `build_frame_path`, `extract_video_frames` (lazy cv2, corrupted-skip, idempotent
  resume), `extract_dataset_frames` (writes `frames/manifest.json`).
- Added `scripts/extract_frames.py` (`python -m scripts.extract_frames`) with a
  clear cv2-missing guard.
- Added `tests/test_video_utils.py` (pure + offline corrupted/manifest tests) and
  `tests/test_frame_extraction_integration.py` (synthetic-video tests, skipped
  when cv2 absent).

## 2026-07-16 — feat — Phase 2 (Dataset Analysis)
- Added `utils/dataset_utils.py`: `scan_videos`, lazy OpenCV `_probe_video`
  (frame/fps/resolution + corruption flag), `render_markdown`, `write_reports`,
  and `analyze` entry point. Pure-stdlib structural scan; metadata extracted only
  when cv2 is installed.
- Added `scripts/analyze_dataset.py` (`python -m scripts.analyze_dataset`).
- Added `tests/test_dataset_utils.py` (pytest-compatible, stdlib-only).
- Generated `reports/dataset_report.md` + `reports/dataset_report.json` for the
  real SOS dataset: 624 videos, 6 classes, 2.58 GB, 0 corrupted (structural;
  full frame-level corruption check deferred until cv2 is installed).
- Appended Emergency module artifacts to repo `.gitignore`.

## 2026-07-16 — init — Phase 1 (Project Backbone)
- Added `config/` package: `config.toml`, `settings.py`, `paths.py`,
  `constants.py`, `logging_config.py`, `__init__.py`.
- Added `utils/` package: `logger.py`, `io_utils.py`, `__init__.py`.
- Added `conftest.py`, `requirements.txt`, and module `README.md`.
- Added `docs/`: AI_PROGRESS, AI_DECISIONS, AI_CHANGELOG, TODO, BUGS,
  KNOWN_LIMITATIONS.
- Created artifact directories (`dataset/`, `models/`, `reports/`, `output/...`,
  `logs/`).
- Verification: pure-Python modules import cleanly; `py_compile` passes.
