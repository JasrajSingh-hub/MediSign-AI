# TODO — Emergency Gesture Recognition

- [x] Phase 2: dataset analysis report (`reports/dataset_report.md/.json`)
- [x] Phase 3: AVI frame extraction with corruption skip + progress bar
- [x] Phase 4: image cleaning (resize, normalize, contrast, histogram eq, denoise)
- [x] Phase 5: MediaPipe landmark extraction → CSV/Parquet + reports
- [x] Phase 6: feature engineering (distance, angle, finger state, palm direction)
- [x] Phase 7: Random Forest training, CV, grid search, evaluation, save model
- [x] Phase 8: singleton prediction engine with confidence + logging
- [x] Phase 9: FastAPI (health, status, predict, Swagger, logging)
- [ ] Phase 10: pytest suite, target 90% coverage
- [ ] Phase 11: HTML testing frontend (camera, prediction, emergency banner, alarm)
- [ ] Phase 12: Docker + Compose + docs

## Verification (2026-07-17)
- Python 3.12.10 available (`.venv`); `compileall -q emergency` passes (exit 0).
- Fixed missing `from pathlib import Path` in `utils/predictor.py` (P0 bug from
  handoff — `Path` was used in type hints and `model_path` construction).
- `emergency/requirements.txt` installed into `.venv`; full pytest + coverage
  run pending completion of Phase 10.

## Open questions
- Confirm semantics of the `hot` gesture with domain expert (not in original spec).
- Decide final integration point with the existing `backend/` service.
