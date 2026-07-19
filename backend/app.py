import base64
import io
import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import mediapipe as mp
import pickle

# ── Load model and MediaPipe once at startup ───────────────────────
model = pickle.load(open(r'backend\models\gesture_model_full.pkl', 'rb'))

print("[OK] RandomForest model loaded!")

from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

# Load HandLandmarker model from emergency directory relative to this app
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, '..', 'emergency', 'models', 'hand_landmarker.task')

# Ensure the model exists
if not os.path.exists(model_path):
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    import urllib.request
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    print(f"Downloading MediaPipe hand model -> {model_path}")
    urllib.request.urlretrieve(url, model_path)

base_options = mp_python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)
landmarker = vision.HandLandmarker.create_from_options(options)
print("[OK] MediaPipe Tasks HandLandmarker loaded!")

app = Flask(__name__)
CORS(app)


# ── Helper functions ───────────────────────────────────────────────
def extract_hand(landmarks):
    """Wrist-center a single hand's 21 landmarks. Returns list of 63 values."""
    wx, wy, wz = landmarks[0].x, landmarks[0].y, landmarks[0].z
    row = []
    for point in landmarks:
        row.extend([point.x - wx, point.y - wy, point.z - wz])
    return row


def normalize(landmarks_relative):
    """Scale by bounding box so hand distance from camera doesn't affect values."""
    xs = landmarks_relative[0::3]
    ys = landmarks_relative[1::3]
    scale = max(max(xs) - min(xs), max(ys) - min(ys))
    if scale == 0:
        return landmarks_relative
    return [v / scale for v in landmarks_relative]


# ── State for letter confirmation + word building ──────────────────
# NOTE: this is per-server, not per-user. Fine for a hackathon demo
# (one laptop, one user at a time). Would need per-session tracking
# for multiple simultaneous users.
recent_predictions = []   # holds the last N raw predictions (for confirmation check)
CONFIRM_THRESHOLD = 15    # how many identical frames in a row = "confirmed"
current_word = ""         # the word being built letter by letter
last_confirmed_letter = None  # so we don't append the same letter twice in a row


# ── Predict endpoint ───────────────────────────────────────────────
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 1. Receive image from Flutter
        data = request.json
        image_data = data['image'].split(',')[1]

        # 2. Decode base64 → raw bytes → cv2 image
        decoded_bytes = base64.b64decode(image_data)
        frame = cv2.imdecode(np.frombuffer(decoded_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 3. Run MediaPipe Tasks HandLandmarker
        import mediapipe as mp
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = landmarker.detect(mp_image)

        if not result.hand_landmarks:
            return jsonify({'letter': 'No hand', 'confidence': '0%'})

        # Format to list of detections: [{"handedness": label, "xyz": [[x,y,z], ...]}]
        detections = []
        for lm_list, handedness_list in zip(result.hand_landmarks, result.handedness):
            # Tasks API NormalizedLandmark has x, y, z fields
            xyz = [[float(lm.x), float(lm.y), float(lm.z)] for lm in lm_list]
            handedness_label = handedness_list[0].category_name if handedness_list else ""
            detections.append({"handedness": handedness_label, "xyz": xyz})

        # 4. Build the 126-feature data row using Tasks API outputs
        def extract_hand_xyz(xyz):
            wx, wy, wz = xyz[0][0], xyz[0][1], xyz[0][2]
            row = []
            for p in xyz:
                row.extend([p[0] - wx, p[1] - wy, p[2] - wz])
            return row

        data_row = []
        num_hands = len(detections)

        if num_hands >= 2:
            detections_sorted = sorted(detections[:2], key=lambda x: x["handedness"])
            for d in detections_sorted:
                data_row.extend(extract_hand_xyz(d["xyz"]))
        elif num_hands == 1:
            d = detections[0]
            hand_data = extract_hand_xyz(d["xyz"])
            if d["handedness"] == 'Left':
                data_row = hand_data + [0] * 63
            else:
                data_row = [0] * 63 + hand_data

        if len(data_row) != 126:
            return jsonify({'letter': 'Error', 'confidence': '0%'})

        # 5. Normalize (same as training pipeline)
        data_row = normalize(data_row)

        # 6. Predict
        prediction = model.predict([data_row])[0]
        proba = model.predict_proba([data_row])[0]
        confidence = max(proba) * 100

      

        global recent_predictions, current_word, last_confirmed_letter

        recent_predictions.append(str(prediction))
        # Only keep the last CONFIRM_THRESHOLD predictions — we don't
        # care about anything older than that window
        if len(recent_predictions) > CONFIRM_THRESHOLD:
            recent_predictions.pop(0)

        letter_confirmed = False

        # Check: are the last CONFIRM_THRESHOLD predictions ALL the same letter?
        if len(recent_predictions) == CONFIRM_THRESHOLD and len(set(recent_predictions)) == 1:
            steady_letter = recent_predictions[0]

            # Only append if it's a NEW letter (avoids appending "H" 50 times
            # just because the hand stayed steady for 50 frames)
            if steady_letter != last_confirmed_letter:
                current_word += steady_letter
                last_confirmed_letter = steady_letter
                letter_confirmed = True
                print(f"[OK] Confirmed letter: {steady_letter} | Word so far: {current_word}")
        print(f"[PREDICT] Predicted: {prediction} ({confidence:.1f}%)")

      # 7. Send result back to Flutter
        return jsonify({
            'letter': str(prediction),
            'confidence': f"{confidence:.1f}%",
            'letter_confirmed': letter_confirmed,
            'current_word': current_word
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)