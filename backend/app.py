import base64
import io
import cv2
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import os

app = Flask(__name__)
CORS(app)  # Allows your Flutter app to talk to this server without security blocks

# 1. Define your 24 alphabet folders in the exact correct order
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'K', 'L', 'M', 'N', 'none', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Z']

print("🧠 Loading your custom trained MediSign AI brain...")
# Load the .keras file that was frozen on your D drive yesterday
model_path = "D:/medsign/backend/models/medisign_model.keras"

if os.path.exists(model_path):
    model = tf.keras.models.load_model(model_path)
    print("✅ Model loaded cleanly and successfully!")
else:
    print(f"❌ ERROR: Could not find your model file at {model_path}. Please make sure your training script completed.")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 2. Receive the raw image package sent from your Flutter Dart code
        data = request.json
        image_data = data['image'].split(',')[1]
        
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
        print(f"🎯 Predicted Sign: {predicted_letter} ({confidence:.1f}%)")
        return jsonify({
            'letter': predicted_letter,
            'confidence': f"{confidence:.1f}%"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Start the server locally on your machine at port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)