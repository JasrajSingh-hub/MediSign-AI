# Known Limitations — Emergency Gesture Recognition

Non-blocking constraints and trade-offs that will not be fixed in the current
scope. Update as the module matures.

## Environment
- **No network in dev sandbox.** OpenCV, MediaPipe, scikit-learn, FastAPI,
  pandas could not be installed/executed here (2026-07-16). The pipeline and
  training must be run in an environment with these packages installed
  (`pip install -r emergency/requirements.txt`). Tests that need them are guarded
  with `pytest.importorskip` and skip cleanly here.

## Dataset
- The `hot` class is undocumented in the original spec; its gesture semantics are
  unconfirmed. It is included by decision (see `docs/AI_DECISIONS.md`) and is
  configurable.
- Class folder names in the raw `SOS/` dataset do **not** carry the `_Raw` suffix
  mentioned in the spec; the loader uses the folder name directly as the label.
- `.AVI` (uppercase) and `.avi` (lowercase) extensions are both present; all
  extension matching is case-insensitive.

## Model
- Phase 7 uses a Random Forest on engineered landmark features (per spec). Deep
  models (TensorFlow/XGBoost/SVM listed under "Future") are out of scope for v1.
- Single-hand landmarks are the default (`max_num_hands = 1`); two-hand support is
  a config change, not a code change.

## Integration
- The emergency API runs as a standalone FastAPI service on port 8000, separate
  from the existing Flask sign-language backend (port 5000). A combined gateway is
  future work.
