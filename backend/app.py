import base64
import string

import cv2
import mediapipe as mp
import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.isl_sign_model import get_model


class ImagePayLoad(BaseModel):
    image: str


class TextPayLoad(BaseModel):
    text: str


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=2)
model = get_model()
print("✅ ISL JSON model loaded!")
print(f"✅ Training samples: {len(model.labels)}")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

recent_predictions = []
CONFIRM_THRESHOLD = 15
current_word = ""
last_confirmed_letter = None


def extract_hand(landmarks):
    wx, wy, wz = landmarks[0].x, landmarks[0].y, landmarks[0].z
    row = []
    for point in landmarks:
        row.extend([point.x - wx, point.y - wy, point.z - wz])
    return row


def normalize(landmarks_relative):
    xs = landmarks_relative[0::3]
    ys = landmarks_relative[1::3]
    scale = max(max(xs) - min(xs), max(ys) - min(ys))
    if scale == 0:
        return landmarks_relative
    return [value / scale for value in landmarks_relative]


@app.post("/predict")
async def predict(payload: ImagePayLoad):
    try:
        image_data = payload.image.split(",")[1]
        decoded_bytes = base64.b64decode(image_data)
        frame = cv2.imdecode(np.frombuffer(decoded_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if not result.multi_hand_landmarks:
            return {"letter": "No hand", "confidence": "0%"}

        data_row = []
        num_hands = len(result.multi_hand_landmarks)

        if num_hands == 2:
            hands_data = list(zip(result.multi_hand_landmarks, result.multi_handedness))
            hands_data.sort(key=lambda x: x[1].classification[0].label)
            for hand, _ in hands_data:
                data_row.extend(extract_hand(hand.landmark))
        elif num_hands == 1:
            hand = result.multi_hand_landmarks[0]
            handedness = result.multi_handedness[0].classification[0].label
            hand_data = extract_hand(hand.landmark)
            data_row = hand_data + [0] * 63 if handedness == "Left" else [0] * 63 + hand_data

        if len(data_row) != 126:
            return {"letter": "Error", "confidence": "0%"}

        data_row = normalize(data_row)
        prediction_result = model.predict_one(data_row)
        prediction = prediction_result["letter"]
        confidence = prediction_result["confidence"]

        global recent_predictions, current_word, last_confirmed_letter
        recent_predictions.append(str(prediction))
        if len(recent_predictions) > CONFIRM_THRESHOLD:
            recent_predictions.pop(0)

        letter_confirmed = False
        if len(recent_predictions) == CONFIRM_THRESHOLD and len(set(recent_predictions)) == 1:
            steady_letter = recent_predictions[0]
            if steady_letter != last_confirmed_letter:
                current_word += steady_letter
                last_confirmed_letter = steady_letter
                letter_confirmed = True

        return {
            "letter": str(prediction),
            "confidence": f"{confidence:.1f}%",
            "letter_confirmed": letter_confirmed,
            "current_word": current_word,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/v1/avatar/parse")
async def parse_text_to_tokens(payload: TextPayLoad):
    raw_text = payload.text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="No text content provided")
    clean_text = raw_text.lower().translate(str.maketrans("", "", string.punctuation))
    words = clean_text.split()
    final_token_sequence = []
    for word in words:
        for letter in word:
            if letter.isalpha():
                final_token_sequence.append(letter.upper())
        final_token_sequence.append("SPACE")
    if final_token_sequence and final_token_sequence[-1] == "SPACE":
        final_token_sequence.pop()
    return {"status": "success", "original_text": raw_text, "tokens": final_token_sequence}


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
