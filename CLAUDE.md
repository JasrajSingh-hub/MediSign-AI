# MediSign-AI Claude Code Context

Last updated: 2026-07-17

This file is the handoff/context document for Claude Code or any coding agent
resuming work in this repository. It records the current architecture, what has
already been built, verification status, and detailed pending work.

## Resume Snapshot

Start here when resuming:

- Main active area: `emergency/`, a standalone emergency gesture recognition
  subsystem for MediSign-AI.
- Active placeholder file: `emergency/dataset/.gitkeep`; the real generated
  feature dataset should eventually be written under `emergency/dataset/`.
- Main context file: `CLAUDE.md` at repo root.
- Dependency file: `emergency/requirements.txt`.
- Current known blocker: Python/venv execution is broken in this shell, so tests
  and compile checks could not be re-run on 2026-07-16.
- Next best action: fix Python/venv, install requirements, run compile/tests,
  then continue phases 10-12.
- Highest-risk code item to check after Python works:
  `emergency/utils/predictor.py` appears to use `Path` without importing it.

## Repository Overview

MediSign-AI is a healthcare sign-language assistant. The repository currently
contains two mostly separate AI paths:

- `backend/`: existing Flask/TensorFlow sign-language recognition backend.
- `frontend/medisign_app/`: Flutter client app.
- `emergency/`: new independent emergency gesture recognition module.
- `SOS/`: raw emergency gesture videos used by `emergency/`.
- `dataset/`: existing static sign-language image dataset for the original app.
- `.claude/settings.local.json`: local Claude Code command permissions only.

The emergency module is intentionally independent from `backend/` so it can be
developed, tested, and served without breaking the original sign-language flow.

## Claude Code Local Settings

`.claude/settings.local.json` currently grants a few local Bash command
permissions for checking Python import paths and imports:

- `.venv/Scripts/python -c "import sys; ..."`
- `.venv/Scripts/python -c "import numpy"`
- `command -v python`
- a partial Python importlib command pattern

There are no project instructions in `.claude/` besides these permissions.
Use this `CLAUDE.md` file as the main Claude Code project context.

## Existing App Context

Root `README.md` describes the original MediSign setup:

- Flutter app captures camera frames.
- Local Flask backend in `backend/app.py` serves model inference on port `5000`.
- Android device access is intended through `adb reverse tcp:5000 tcp:5000`.
- Existing backend model artifacts are in `backend/models/`.
- The original backend preprocessing rotates mobile frames, converts BGR/RGB,
  and normalizes pixels before TensorFlow/Keras inference.

Do not modify the existing `backend/` module unless the user explicitly asks for
integration. The emergency module was built as a separate service.

## Emergency Module Purpose

`emergency/` recognizes emergency gestures from patients who are speech- or
hearing-impaired so a clinician can be alerted quickly.

Configured classes in `emergency/config/config.toml`:

- `help`
- `doctor`
- `pain`
- `call`
- `accident`
- `hot`

The original spec reportedly listed 5 classes, but the real `SOS/` dataset has
6 folders. The extra `hot` class is included by decision and can be removed from
config if the product owner rejects it.

## Emergency Dataset

Raw videos live in `SOS/<class>/`.

Current structural scan:

- `accident`: 104 videos
- `call`: 104 videos
- `doctor`: 104 videos
- `help`: 104 videos
- `hot`: 104 videos
- `pain`: 104 videos
- Total: 624 `.avi` / `.AVI` files, about 2.5 GB

Dataset report:

- `emergency/reports/dataset_report.md`

Important caveat: OpenCV was not available when the report was generated, so
frame count, FPS, resolution, and full decode-level corruption checks were not
performed. The report is a structural scan only.

## Emergency Pipeline

Intended pipeline:

1. Analyze raw videos.
2. Extract frames from `SOS/`.
3. Clean/process frames.
4. Extract MediaPipe hand landmarks.
5. Engineer features.
6. Train Random Forest classifier.
7. Serve predictions through FastAPI.
8. Build a simple HTML test frontend.
9. Package with Docker/Compose.

The module is config-driven through `emergency/config/config.toml`. Paths are
resolved in code and should not be hardcoded.

## Emergency Project Layout

Key directories and files:

- `emergency/README.md`: module overview and quick start.
- `emergency/requirements.txt`: runtime, training, API, and test dependencies.
- `emergency/config/`: TOML settings, path resolution, constants, logging config.
- `emergency/utils/`: reusable pipeline utilities.
- `emergency/scripts/`: runnable batch scripts.
- `emergency/tests/`: pytest suite with heavy dependencies guarded/skipped.
- `emergency/docs/`: progress, decisions, changelog, TODOs, bugs, limitations.
- `emergency/api.py`: FastAPI app.
- `emergency/pytest.ini`: pytest config.
- `emergency/.coveragerc`: coverage config.
- `emergency/models/.gitkeep`: placeholder for trained model artifacts.
- `emergency/reports/dataset_report.md`: generated dataset analysis.

Counts at this handoff:

- 12 utility Python files in `emergency/utils/`
- 8 scripts in `emergency/scripts/`
- 15 test files in `emergency/tests/`

## Implemented Emergency Phases

According to `emergency/docs/AI_PROGRESS.md`, phases 1 through 9 are complete:

- Phase 1: project backbone, config, paths, logger, docs.
- Phase 2: dataset analysis and reports.
- Phase 3: frame extraction with corrupted-skip and manifest support.
- Phase 4: image processing transforms.
- Phase 5: MediaPipe landmark extraction to CSV/Parquet/report.
- Phase 6: feature engineering, producing 294 features per sample.
- Phase 7: Random Forest training and model save flow.
- Phase 8: singleton prediction engine.
- Phase 9: FastAPI service.

Remaining planned phases in `AI_PROGRESS.md`:

- Phase 10: testing completion / coverage target.
- Phase 11: HTML testing frontend.
- Phase 12: packaging.

## Important Implementation Notes

- Config format is TOML via Python standard-library `tomllib`, requiring Python
  3.11 or newer.
- Heavy dependencies are lazy-imported where possible so offline/pure unit tests
  can still run.
- Parquet output is best-effort and skipped if pandas/pyarrow are missing.
- Landmark detection requires real hand imagery and MediaPipe installed.
- Single-hand detection is the default: `max_num_hands = 1`.
- Emergency API is standalone FastAPI on port `8000`, separate from Flask on
  port `5000`.
- Prediction endpoint accepts either an uploaded file or JSON base64 image.
- Swagger UI should be available at `/docs` when FastAPI runs.

## Current Git State

Observed git state across recent checks:

- Modified: `.gitignore`
- Untracked: `.claude/settings.local.json`
- Untracked: `SOS/`
- Untracked: `emergency/`
- Untracked: `CLAUDE.md`
- Untracked in focused status check: `emergency/requirements.txt`

`.gitignore` has been modified to ignore generated emergency artifacts:

- `emergency/output/`
- `emergency/logs/`
- `emergency/models/*.pkl`
- `emergency/reports/*.json`
- `emergency/dataset/`

There are many generated `__pycache__/` files under `emergency/`. They are
currently untracked and should be cleaned or ignored before commit.

`emergency/dataset/.gitkeep` exists only to preserve the empty dataset artifact
directory. It is not the trained/processed dataset.

Git warning seen during status:

- Unable to access `C:\Users\kamle/.config/git/ignore`: permission denied.

This warning is external to the repo and does not block local work.

## Verification Status

Commands attempted on 2026-07-16:

- `pytest emergency\tests -q`
  - Failed because `pytest` is not installed on PATH.
- `python --version`
  - Failed with a Windows logon/session error.
- `.venv\Scripts\python.exe --version`
  - Failed because the venv points to a WindowsApps Python executable that
    cannot create a process.
- `.venv\Scripts\python.exe -m compileall -q emergency`
  - Failed for the same venv/Python launcher issue.

Earlier docs claim pure-Python compile and offline tests passed, but that could
not be re-verified in this current shell.

## Environment Blockers

Resolve these before running the full pipeline:

1. Fix Python execution.
   The current `python.exe` and `.venv\Scripts\python.exe` fail to start. Rebuild
   the venv with a working Python 3.11+ interpreter.

2. Install dependencies.
   Run from repo root after venv activation:

   ```powershell
   pip install -r emergency/requirements.txt
   ```

3. Re-run tests and compile checks:

   ```powershell
   python -m compileall -q emergency
   python -m pytest emergency/tests -q
   python -m pytest emergency/tests -q --cov=config --cov=utils --cov=scripts --cov=api --cov-report=term-missing --cov-fail-under=90
   ```

4. Run real pipeline steps after dependencies install:

   ```powershell
   cd emergency
   python -m scripts.analyze_dataset
   python -m scripts.extract_frames
   python -m scripts.process_images
   python -m scripts.extract_landmarks
   python -m scripts.feature_engineering
   python -m scripts.train
   uvicorn api:app --reload --port 8000
   ```

## Detailed Pending Work

This is the authoritative pending-work list for Claude Code. Keep it updated
after each meaningful change.

### P0 - Fix environment

- Recreate `.venv` using a working Python 3.11+ installation.
- Ensure `python`, `pip`, and `python -m pytest` work from the repo root.
- Install `emergency/requirements.txt`.
- Confirm OpenCV, MediaPipe, sklearn, FastAPI, and pytest import.
- After reinstall, avoid relying on the broken WindowsApps Python shim. Prefer
  the activated venv interpreter or a known full Python install path.

### P0 - Re-verify code health

- Run `python -m compileall -q emergency`.
- Run pure/unit tests.
- Run full pytest suite after dependencies are installed.
- Record the results in `emergency/docs/AI_PROGRESS.md` or a new verification
  section in this file.
- If tests fail because heavy dependencies are unavailable, confirm the skip
  behavior is intentional and documented rather than silently hiding real
  failures.

### P0 - Check likely import bug

`emergency/utils/predictor.py` uses `Path` in type hints and runtime path
construction but does not import it from `pathlib`.

Expected fix:

```python
from pathlib import Path
```

Add that import near the top and run the predictor tests.

Suggested validation after the fix:

```powershell
python -m pytest emergency/tests/test_predictor.py -q
python -m pytest emergency/tests/test_predictor_integration.py -q
```

### P1 - Clean generated files before commit

- Add `__pycache__/`, `.pytest_cache/`, `.coverage`, and similar Python cache
  outputs to `.gitignore` if not already covered.
- Remove untracked `__pycache__/` files from the working tree.
- Decide whether raw `SOS/` videos should be committed. They are large
  untracked data files; usually they should live outside Git or in Git LFS.
- Decide whether `.claude/settings.local.json` should be committed. It is local
  permission config and may be better kept untracked.
- Decide whether `CLAUDE.md` should be committed as shared project memory. If it
  should remain local, add it to `.git/info/exclude` rather than `.gitignore`
  unless the whole team wants it ignored.

### P1 - Fix documentation drift

`emergency/docs/AI_PROGRESS.md` says phases 1-9 are complete, but
`emergency/docs/TODO.md` still marks phases 2-9 as unchecked.

Update `TODO.md` so it matches reality:

- Mark phases 2-9 complete if verified.
- Leave phases 10-12 pending.
- Keep open questions about `hot` semantics and backend integration.

### P1 - Run real data pipeline

After dependencies are installed:

- Re-run dataset analysis with OpenCV available to capture FPS, frame count, and
  resolution metadata.
- Extract frames into `emergency/output/frames/`.
- Process frames into `emergency/output/processed/`.
- Extract landmarks into `emergency/output/landmarks/`.
- Generate features into `emergency/dataset/`.
- Train model into `emergency/models/emergency_model.pkl`.
- Review generated reports and confirm class balance.
- Confirm generated `emergency/dataset/` contents are ignored or intentionally
  tracked. The current `.gitignore` ignores `emergency/dataset/`, which may also
  hide `.gitkeep` depending on Git state.

Expected artifact flow:

- `emergency/output/frames/`: extracted video frames.
- `emergency/output/processed/`: cleaned frames.
- `emergency/output/landmarks/`: landmark CSV/Parquet/manifest outputs.
- `emergency/dataset/`: engineered feature CSV and train-ready artifacts.
- `emergency/models/emergency_model.pkl`: trained classifier.
- `emergency/reports/`: human-readable reports; JSON reports are ignored.

### P1 - Complete Phase 10 testing

- Reach the documented 90% coverage target.
- Confirm heavy-dependency tests are not silently skipping in the real dev env.
- Add regression tests around API request parsing, missing model behavior, and
  model-loaded status.
- Test the full path from a sample image to prediction.
- Add or verify tests for config path resolution, empty/missing dataset
  behavior, corrupted video skip behavior, no-hand landmark behavior, and model
  threshold behavior.
- Save final command output summary in `emergency/docs/AI_PROGRESS.md`.

### P2 - Complete Phase 11 HTML testing frontend

Build a simple emergency test UI that can:

- Access webcam/camera.
- Capture frames.
- Send frames to FastAPI `/predict`.
- Show predicted label, confidence, and per-class probabilities.
- Display a prominent emergency banner when confidence clears threshold.
- Play an alarm or show visual alert for emergency predictions.
- Show API/model status and useful error messages.

Keep this separate from the Flutter app until integration is explicitly planned.

Suggested location:

- `emergency/frontend/` or `emergency/static/`, depending on whether it is a
  standalone HTML page or served by FastAPI.

Minimum acceptance criteria:

- Page loads without a build step.
- Camera permission failure is handled visibly.
- API offline/model missing states are displayed.
- Successful predictions show label, confidence, probabilities, and alert state.

### P2 - Complete Phase 12 packaging

- Add `emergency/Dockerfile` if not already present.
- Add `emergency/docker-compose.yml` if not already present.
- Document how to mount model/data artifacts.
- Include API healthcheck.
- Confirm image builds after dependencies are available.
- Confirm OpenCV/MediaPipe system requirements are satisfied inside the image.
- Ensure model files are volume-mounted or copied intentionally; do not bake
  large generated artifacts into the image unless explicitly required.

### P2 - Decide integration strategy

Open product/architecture questions:

- Should emergency FastAPI remain a separate service on port `8000`?
- Should the existing Flask backend proxy or mount emergency predictions?
- Should Flutter call both services independently?
- How should emergency alerts be surfaced in the Flutter UI?
- Should Android `adb reverse` also map port `8000`?

### P2 - Validate `hot` class semantics

The `hot` gesture exists in raw data but was not in the original class spec.
Before production use:

- Confirm what `hot` means clinically.
- Decide whether it is an emergency alert or a non-emergency condition.
- Keep it, rename it, or remove it from `config.toml`.
- Retrain if the class list changes.

## Suggested Next Commands

Once Python is fixed:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r emergency/requirements.txt
python -m compileall -q emergency
python -m pytest emergency/tests -q
```

Then fix any failures, especially `emergency/utils/predictor.py` if the missing
`Path` import is confirmed by the test run.

Useful focused checks:

```powershell
python -m pytest emergency/tests/test_dataset_utils.py -q
python -m pytest emergency/tests/test_feature_utils.py -q
python -m pytest emergency/tests/test_model_utils.py -q
python -m pytest emergency/tests/test_predictor.py -q
python -m pytest emergency/tests/test_api_integration.py -q
```

## Commit Preparation Checklist

Before committing:

- Fix or document Python/venv state.
- Fix confirmed code bugs.
- Update `TODO.md` to match `AI_PROGRESS.md`.
- Remove Python cache files.
- Decide whether to track `SOS/` data.
- Decide whether to track `.claude/settings.local.json`.
- Include `CLAUDE.md` if the team wants Claude Code project memory in Git.
- Re-run tests and paste summary into the commit message or PR notes.
