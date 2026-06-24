import sys
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import base64
import io
import cv2
import numpy as np
import tensorflow as tf
import h5py
import zipfile
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import os
from contextlib import asynccontextmanager

# Ensure we can import from backend dir
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Call dependencies checks for nested services on startup
    from tts_service import check_audio_dependencies
    try:
        check_audio_dependencies()
    except Exception as e:
        print(f"Unified Backend Startup Warning: {e}")
    yield

app = FastAPI(
    title="MediSign AI Unified Backend",
    description="Unified API server hosting gesture predictions, TTS/STT, and prescription OCR.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import sub-service routers
from tts_service import router as tts_router
from ocr_service import router as ocr_router

# Include routers
app.include_router(tts_router)
app.include_router(ocr_router)

# 1. Define your 24 alphabet folders in the exact correct order
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'K', 'L', 'M', 'N', 'none', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Z']

print("Loading your custom trained MediSign AI model...")
# Resolve the model relative to this file so the backend works from any checkout.
model_path = os.path.join(os.path.dirname(__file__), "models", "medisign_model.keras")


def load_legacy_model(path):
    """Load this TensorFlow 2.13 model under Keras 3 on Windows."""
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(128, 128, 3)),
        tf.keras.layers.Rescaling(1.0 / 255),
        tf.keras.layers.Conv2D(32, 3, activation="relu", name="conv2d"),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(64, 3, activation="relu", name="conv2d_1"),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation="relu", name="dense"),
        tf.keras.layers.Dense(24, activation="softmax", name="dense_1"),
    ])

    layer_groups = {
        "conv2d": r"_layer_checkpoint_dependencies\conv2d",
        "conv2d_1": r"_layer_checkpoint_dependencies\conv2d_2",
        "dense": r"_layer_checkpoint_dependencies\dense",
        "dense_1": r"_layer_checkpoint_dependencies\dense_2",
    }
    with zipfile.ZipFile(path) as archive:
        weights_data = io.BytesIO(archive.read("model.weights.h5"))
    with h5py.File(weights_data, "r") as weights_file:
        for layer_name, group_name in layer_groups.items():
            group = weights_file[f"{group_name}/vars"]
            model.get_layer(layer_name).set_weights([group["0"][:], group["1"][:]])
    return model

model = None
if os.path.exists(model_path):
    try:
        model = load_legacy_model(model_path)
        print("Model loaded cleanly and successfully!")
    except Exception as e:
        print(f"Failed to load legacy model: {e}")
else:
    print(f"ERROR: Could not find your model file at {model_path}. Please make sure your training script completed.")


class PredictRequest(BaseModel):
    image: str


@app.post('/predict')
async def predict(request: PredictRequest):
    try:
        if model is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ML prediction model is not loaded."
            )
        
        # 2. Receive the raw image package sent from your Flutter Dart code
        image_data = request.image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # 3. Decode the text string back into a digital pixel image matrix
        decoded_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(decoded_bytes)).convert('RGB')
        frame = np.array(image)
        
        # 4. Standardize the image to 128x128 pixels to match our neural network input layer
        resized_frame = cv2.resize(frame, (128, 128))
        input_data = np.expand_dims(resized_frame, axis=0)
        
        # 5. Run prediction through your 4 layers
        predictions = model.predict(input_data, verbose=0)
        highest_score_index = np.argmax(predictions[0])
        
        predicted_letter = labels[highest_score_index]
        confidence = float(predictions[0][highest_score_index] * 100)
        
        # 6. Reply to your Flutter app with the clean answer text data
        print(f"Predicted Sign: {predicted_letter} ({confidence:.1f}%)")
        return {
            'letter': predicted_letter,
            'confidence': f"{confidence:.1f}%"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

if __name__ == '__main__':
    import uvicorn
    # Start the server locally on your machine at port 5000
    uvicorn.run("app:app", host='0.0.0.0', port=5000, reload=True)
