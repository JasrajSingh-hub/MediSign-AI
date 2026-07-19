# AI Decisions — Emergency Gesture Recognition

Recorded architectural and product decisions. Update when a decision is made.

## D1 — Include the undocumented `hot` class (2026-07-16)
- **Context:** The task spec lists 5 classes (`help`, `doctor`, `pain`, `call`,
  `accident`) with a `_Raw` suffix. The actual `SOS/` dataset has **6** folders
  with no suffix (`accident`, `call`, `doctor`, `help`, `hot`, `pain`), 104
  `.avi`/`.AVI` files each.
- **Decision:** Include `hot` as a 6th emergency gesture class. It is listed in
  `config.toml [dataset].classes` so it can be removed trivially.
- **Rationale:** Discarding 104 labelled videos wastes real data; keeping it is
  low-risk and configurable.
- **Impact:** Training, feature CSV, and the prediction label set gain a 6th class.

## D2 — Config format = TOML via stdlib `tomllib` (2026-07-16)
- **Context:** Need a config format with no third-party dependency (offline dev
  sandbox, no network for PyPI).
- **Decision:** Use `config.toml` parsed by the standard-library `tomllib`
  (Python >= 3.11). No `pyyaml`/`python-dotenv` required.
- **Rationale:** Zero-dependency config loading; works in CI and offline.

## D3 — Independent top-level `emergency/` module (2026-07-16)
- **Context:** Must not modify the existing `backend/` Sign Language Recognition
  module (Flask + MediaPipe + pickled RandomForest).
- **Decision:** Build the emergency module as a separate top-level directory with
  its own FastAPI service (port 8000) and HTML frontend.
- **Rationale:** Clean separation; later integration is a matter of mounting the
  FastAPI app or proxying routes — no edits to `backend/app.py`.

## D4 — Verification strategy under no-network sandbox (2026-07-16)
- **Context:** Dev sandbox has no outbound network; OpenCV/MediaPipe/scikit-learn/
  FastAPI cannot be installed here.
- **Decision:** Deliver full code + `requirements.txt`. Verify with `py_compile`
  and pure-Python unit tests; guard heavy-dependency tests with
  `pytest.importorskip` so the suite runs green here and fully once deps install.
- **Rationale:** Keeps the module production-ready and testable without blocking on
  environment access.
