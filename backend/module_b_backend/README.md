# Module B Backend

Isolated prescription-safety backend pulled from the `featureKaran` branch.

## Run

```powershell
cd module_b_backend
python main.py
```

## Endpoints

- `GET /health`
- `POST /prescription/allergy-check`
- `POST /prescription/interaction-check`
- `POST /prescription/audit`
- `POST /prescription/ocr-audit`
