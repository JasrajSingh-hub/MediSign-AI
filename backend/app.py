import base64
import io
import cv2
import numpy as np
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import string
import mediapipe as mp
# import mediapipe.python.solutions.hands as mp_hands
# import mediapipe.python.solutions.drawing_utils as mp_drawing
import pickle
import uvicorn

class ImagePayLoad(BaseModel):
    image:str

BASE_DIR =os.path.dirname(os.path.abspath(__name__))

MODEL_PATH = os.path.join(BASE_DIR ,"backend","models","gesture_model_full.pkl")

# ── Load model and MediaPipe once at startup ───────────────────────
model = pickle.load(open(MODEL_PATH, 'rb'))

print("✅ RandomForest model loaded!")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=2)
print("✅ MediaPipe hands loaded!")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
@app.post('/predict')
async def predict(payload : ImagePayLoad):
    try:
        # 1. Receive image from Flutter
       
        image_data = payload.image.split(',')[1]

        # 2. Decode base64 → raw bytes → cv2 image
        decoded_bytes = base64.b64decode(image_data)
        frame = cv2.imdecode(np.frombuffer(decoded_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 3. Run MediaPipe to extract hand landmarks
        result = hands.process(rgb)

        if not result.multi_hand_landmarks:
            return {'letter': 'No hand', 'confidence': '0%'}

        # 4. Build the 126-feature data row
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
            if handedness == 'Left':
                data_row = hand_data + [0] * 63
            else:
                data_row = [0] * 63 + hand_data

        if len(data_row) != 126:
            return {'letter': 'Error', 'confidence': '0%'}

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
                print(f"✅ Confirmed letter: {steady_letter} | Word so far: {current_word}")
        print(f"🎯 Predicted: {prediction} ({confidence:.1f}%)")

      # 7. Send result back to Flutter
        return {
            'letter': str(prediction),
            'confidence': f"{confidence:.1f}%",
            'letter_confirmed': letter_confirmed,
            'current_word': current_word
        }

    except Exception as e:
        raise HTTPException(status_code =400,details=str(e))
    



# model code ends here
# =================================================================================
# text to sign starts here

class TextPayLoad(BaseModel):
    text: str


@app.post('/api/v1/avatar/parse')
async def parse_text_to_tokens(payload: TextPayLoad):
        """
        Parses incoming clinical text entirely into individual alphabet character tokens
        to perfectly match the 26 letters available in avatar_library.json.
        """
        try:
            raw_text = payload.text.strip()
            
            if not raw_text:
                raise HTTPException(status_code=400, detail="No text content provided")
                
            # Clean text: lowercase and remove punctuation marks
            clean_text = raw_text.lower().translate(str.maketrans('', '', string.punctuation))
            words = clean_text.split()
            
            final_token_sequence = []
            
            for word in words:
                # Break down EVERY word into its raw letters (A-Z)
                for letter in word:
                    if letter.isalpha():  
                        final_token_sequence.append(letter.upper())
                
                # Optional: Add a brief "PAUSE" token between words so the avatar doesn't 
                # smash words together. Flutter can read this to reset to a neutral pose.
                final_token_sequence.append("SPACE")
                
            # Remove the very last trailing SPACE token
            if final_token_sequence and final_token_sequence[-1] == "SPACE":
                final_token_sequence.pop()
                            
            return {
                "status": "success",
                "original_text": raw_text,
                "tokens": final_token_sequence
            }, 200
    
        
        except Exception as e:
            raise HTTPException(status_code=500 , detail={"status": "error", "message": str(e)})
           
    

    
if __name__ == '__main__':
    uvicorn.run( "app:app",host='127.0.0.1', port=5000, reload=True)


