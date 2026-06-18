import os
import cv2
import keras
import tensorflow as tf
import matplotlib.pyplot as plt

# 1. Point directly to your clean Indian Sign Language folders
dataset_path = "D:/medsign/dataset"
print(f"📂 Scanning directory: {dataset_path}")

# 2. Run your directory check (This part works perfectly!)
labels = []
for i in os.listdir(dataset_path):
    if os.path.isdir(os.path.join(dataset_path, i)):
        labels.append(i)
print(f"Found {len(labels)} folders: {labels}\n")

# =====================================================================
# TENSORFLOW DATA PIPELINE (Replaces the old MediaPipe loader/splits)
# =====================================================================
print("📦 Loading and splitting dataset into Training and Validation sets...")

# Load 80% of your images into the study box (Textbook)
train_data = tf.keras.utils.image_dataset_from_directory(
    dataset_path,
    validation_split=0.2,       # Set aside 20% for testing/validation
    subset="training",          # Lock this bucket to training
    seed=123,                   # Ensures random choices stay consistent
    image_size=(128, 128),      # Resize all Kaggle photos to 128x128 pixels
    batch_size=32               # Group images into blocks of 32
)

# Load the remaining 20% into your testing box (Pop Quiz / Final Exam)
validation_data = tf.keras.utils.image_dataset_from_directory(
    dataset_path,
    validation_split=0.2,
    subset="validation",        # Lock this bucket to validation
    seed=123,
    image_size=(128, 128),
    batch_size=32
)

print("\n🚀 Dataset is perfectly partitioned and ready for neural network training!")


model = tf.keras.Sequential([
    tf.keras.layers.Rescaling(1./255, input_shape=(128,128,3)),

    tf.keras.layers.Conv2D(32, (3,3), activation="relu"),
    tf.keras.layers.MaxPooling2D((2,2)),

    tf.keras.layers.Conv2D(64, (3,3), activation="relu"),
      tf.keras.layers.MaxPooling2D((2,2)),

    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation="relu"),
    tf.keras.layers.Dense(24, activation="softmax")
])


# =====================================================================
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(),
    metrics=['accuracy'] # <--- This tells TensorFlow to calculate accuracy!
)

print("\n🏃‍♂️ Starting the training sessions... WATCH BELOW FOR ACCURACY!")

# Putting 'verbose=1' forces TensorFlow to print progress bars and accuracy scores live!
model.fit(
    train_data,
    validation_data=validation_data,
    epochs=10,
    verbose=1 
)

os.makedirs("D:/medsign/backend/models", exist_ok=True)
model.save("D:/medsign/backend/models/medisign_model.keras")
print("🎉 Done! Model saved successfully.")

