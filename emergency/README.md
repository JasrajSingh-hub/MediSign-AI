# MediSign-AI — Emergency Gesture Recognition

An **independent** AI module that recognises emergency hand gestures performed by
speech/hearing-impaired patients, so a clinician can be alerted instantly. It is a
self-contained subsystem of [MediSign-AI](../README.md) and does **not** modify the
existing Sign Language Recognition (`backend/`) module.

## Emergency gesture classes

| Class     | Meaning                                            |
|-----------|----------------------------------------------------|
| `help`    | Call for help                                      |
| `doctor`  | Need a doctor                                      |
| `pain`    | In pain                                            |
| `call`    | Call someone / phone                               |
| `accident`| Accident / emergency situation                     |
| `hot`     | Present in raw data; included by decision (see `docs/AI_DECISIONS.md`). Removable via config. |

> The raw videos live at the repository root in `SOS/<class>/` (624 `.avi` files:
> 104 per class). The spec listed 5 classes without a `_Raw` suffix; the actual
> dataset has 6 folders and no suffix.

## Pipeline

```
AVI videos → frame extraction → image cleaning → MediaPipe Hands (21 landmarks)
→ landmark normalisation → feature engineering → CSV/Parquet → train/test split
→ Random Forest → cross-validation → evaluation → prediction engine → FastAPI → frontend
```

## Project layout

```
emergency/
├── config/      settings (config.toml, paths, constants, logger config)
├── utils/       logger, io, video, image, landmark, feature, model helpers
├── scripts/     batch scripts (extract → process → landmarks → features → train → predict)
├── dataset/     derived dataset artifacts
├── models/      trained model artifacts (emergency_model.pkl)
├── reports/     dataset / landmark / evaluation reports
├── output/      frames/, processed/, landmarks/
├── docs/        AI_PROGRESS, AI_CHANGELOG, AI_DECISIONS, TODO, BUGS, KNOWN_LIMITATIONS
├── tests/       pytest suite (heavy deps guarded via importorskip)
├── api.py       FastAPI service (health / status / predict)
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Quick start

```bash
# 1. Create & activate a virtual environment (Python >= 3.11)
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # macOS / Linux

# 2. Install dependencies
pip install -r emergency/requirements.txt

# 3. Run the batch pipeline (phases 2-7)
python -m scripts.extract_frames
python -m scripts.process_images
python -m scripts.extract_landmarks
python -m scripts.feature_engineering
python -m scripts.train

# 4. Start the API
uvicorn api:app --reload --port 8000
# Open http://127.0.0.1:8000/docs for the Swagger UI.

# 5. Run the test suite
pytest emergency/tests -q

# With coverage (target 90%):
pytest emergency/tests -q --cov=config --cov=utils --cov=scripts --cov=api \
    --cov-report=term-missing --cov-fail-under=90

```

All behaviour is configured in [`config/config.toml`](config/config.toml); no
paths are hardcoded in source. The merged configuration is available at runtime as
``config.CONFIG`` (a dict); paths as ``config.PATHS``; structural constants as
``config.CONSTANTS``. See `docs/` for progress, decisions, and known limitations.
