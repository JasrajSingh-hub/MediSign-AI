import base64

import cv2
import numpy as np
from services.isl_sign_model import get_model

try:
    import mediapipe as mp

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=True, max_num_hands=2)
except Exception:
    mp = None
    mp_hands = None
    hands = None
recent_predictions = []
CONFIRM_THRESHOLD = 15
current_word = ""
last_confirmed_letter = None


def extract_hand(landmarks):
    wrist_x, wrist_y, wrist_z = landmarks[0].x, landmarks[0].y, landmarks[0].z
    row = []
    for point in landmarks:
        row.extend([point.x - wrist_x, point.y - wrist_y, point.z - wrist_z])
    return row


def normalize(landmarks_relative):
    xs = landmarks_relative[0::3]
    ys = landmarks_relative[1::3]
    scale = max(max(xs) - min(xs), max(ys) - min(ys))
    if scale == 0:
        return landmarks_relative
    return [value / scale for value in landmarks_relative]


def landmarks_to_points(landmarks):
    return [{"x": float(point.x), "y": float(point.y), "z": float(point.z)} for point in landmarks]


def predict_sign(image_data: str) -> dict:
    if hands is None:
        return {"letter": "Unavailable", "confidence": "0%", "landmarks": []}

    model = get_model()
    decoded_bytes = base64.b64decode(image_data.split(",")[1])
    frame = cv2.imdecode(np.frombuffer(decoded_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if not result.multi_hand_landmarks:
        return {"letter": "No hand", "confidence": "0%", "landmarks": []}

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
        return {"letter": "Error", "confidence": "0%", "landmarks": []}

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

    hand_landmarks = []
    if num_hands == 2:
        hands_data = list(zip(result.multi_hand_landmarks, result.multi_handedness))
        hands_data.sort(key=lambda x: x[1].classification[0].label)
        hand_landmarks = [landmarks_to_points(hand.landmark) for hand, _ in hands_data]
    elif num_hands == 1:
        hand_landmarks = [landmarks_to_points(result.multi_hand_landmarks[0].landmark)]

    return {
        "letter": str(prediction),
        "confidence": f"{confidence:.1f}%",
        "letter_confirmed": letter_confirmed,
        "current_word": current_word,
        "landmarks": hand_landmarks,
    }
