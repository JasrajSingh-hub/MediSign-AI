# MediSign-AI — Emergency Gesture Recognition API
# Build context is the `emergency/` directory.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

# Minimal runtime libs for OpenCV / MediaPipe.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the module (api.py, utils/, config/, scripts/, frontend/, ...).
COPY . /app

# Persist the trained model and the auto-downloaded MediaPipe model.
VOLUME ["/app/models"]

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
