# Running the Emergency module with Docker

The `Dockerfile` and `docker-compose.yml` package the FastAPI emergency
gesture-recognition service (port `8000`, separate from the Flask backend on
`5000`).

## Build & run

```bash
# from the repository root
docker compose -f emergency/docker-compose.yml up --build
```

Or build/run the image directly:

```bash
docker build -t medisign-emergency emergency
docker run -p 8000:8000 -v emergency-models:/app/models medisign-emergency
```

The service is then available at:

- `http://localhost:8000/health`     — liveness probe
- `http://localhost:8000/status`     — model/version/class info
- `http://localhost:8000/docs`       — Swagger UI
- `http://localhost:8000/frontend/`  — webcam test UI (Phase 11)
- `http://localhost:8000/predict`    — POST an image file or `image_base64` form field

A Docker healthcheck pings `/health` every 30s.

## Artifact mounts

| Artifact | Where | Notes |
|----------|-------|-------|
| Trained model `models/emergency_model.pkl` | `/app/models` (named volume `emergency-models`) | Produced by Phase-7 training; persisted across container restarts. |
| MediaPipe model `models/hand_landmarker.task` | `/app/models` | Auto-downloaded on first use (needs outbound network). Cached in the same volume. |
| Raw videos `SOS/` | mount `../SOS:/app/SOS:ro` (commented out) | Only needed to run the full pipeline (frame extraction → landmarks → training) inside the container. |
| Pipeline outputs `output/` | mount `emergency-output:/app/output` (commented out) | Frames/landmarks/features. Git-ignored. |

To enable the full pipeline inside the container, uncomment the `../SOS` and
`emergency-output` volume lines in `docker-compose.yml` and run the scripts via
`docker compose exec emergency-api python -m scripts.train` (after extracting
frames and landmarks).

## Model availability

`/predict` returns HTTP 422 with `{"detail": "..."}` when no hand is detected or
the model is unavailable — this is expected until Phase-7 training has written
`emergency_model.pkl` into the mounted `models` volume. `/status` reports
`model_loaded` so clients can check before predicting.
