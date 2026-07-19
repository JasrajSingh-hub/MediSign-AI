"""Interactive preview tool to visualize original and augmented video frames side-by-side.

Allows selecting specific augmentation types (or random combinations) to visually verify
parameters and quality before launching the batch pipeline.
"""
from __future__ import annotations

import os
import sys
import random
from pathlib import Path

import cv2
import numpy as np

# Add parent directories to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import augmentation_config as cfg
import augmentation_utils as utils

AUGMENTATION_OPTIONS = {
    "1": "Brightness (Low/High)",
    "2": "Contrast (Low/High)",
    "3": "Gamma Correction (Dark/Bright)",
    "4": "CLAHE Histogram Equalization",
    "5": "Gaussian Blur",
    "6": "Gaussian Noise",
    "7": "ISO Sensor Noise",
    "8": "White Balance (Color Temperature)",
    "9": "Simulated Overlay Shadow",
    "10": "Motion Blur",
    "11": "Lossy JPEG Compression",
    "12": "Small Rotation (Border Reflection)",
    "13": "Small Center Zoom",
    "14": "Small Translation (Warp Affine)",
    "15": "Randomized Combo 1 (Geometric + Light)",
    "16": "Randomized Combo 2 (Lighting + Blur + Noise)",
    "R": "Select a new random video"
}


def print_menu():
    """Print the selection menu in the console."""
    print("\n" + "=" * 60)
    print(" MediSign-AI Data Augmentation Preview Tool")
    print("=" * 60)
    print("Select an augmentation to preview on the video stream:")
    for key, name in AUGMENTATION_OPTIONS.items():
        print(f"  [{key}] {name}")
    print("  [ESC/Q] Quit the previewer")
    print("=" * 60)


def main():
    # Verify input directory
    if not cfg.INPUT_DIR.exists():
        print(f"ERROR: Input directory {cfg.INPUT_DIR} does not exist.")
        sys.exit(1)

    # Collect video files
    valid_exts = {".avi", ".mp4", ".mov", ".mkv", ".wmv"}
    video_files = []
    for folder in cfg.INPUT_DIR.iterdir():
        if folder.is_dir():
            for f in folder.iterdir():
                if f.is_file() and f.suffix.lower() in valid_exts:
                    video_files.append(f)

    if not video_files:
        print(f"ERROR: No valid video files found in {cfg.INPUT_DIR}")
        sys.exit(1)

    # Pick first random video
    current_video = random.choice(video_files)
    print(f"Loaded source video: {current_video.parent.name}/{current_video.name}")

    # Set default augmentation to Brightness
    selection = "1"
    print_menu()
    print(f"Active Augmentation: {AUGMENTATION_OPTIONS[selection]}")

    cv2.namedWindow("MediSign-AI Data Augmentation Preview (Left: Orig | Right: Aug)", cv2.WINDOW_AUTOSIZE)

    cap = cv2.VideoCapture(str(current_video))
    if not cap.isOpened():
        print(f"ERROR: Cannot open video: {current_video}")
        sys.exit(1)

    # Generate constants for the video (shadow vertices, seeds, etc.)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    
    # Generate constant random parameters for preview modes
    seed = random.randint(0, 999999)
    rng = np.random.default_rng(seed)
    
    # Shadow polygon vertices
    shadow_pts = np.array([
        [int(rng.uniform(0, width)), int(rng.uniform(0, height))]
        for _ in range(rng.integers(3, 5))
    ], dtype=np.int32)

    while True:
        ret, frame = cap.read()
        
        # Loop video indefinitely
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        aug_frame = frame.copy()

        # Apply the chosen augmentation based on current selection
        if selection == "1":
            # Toggle between dark (0.75) and bright (1.25) factor based on frame index
            factor = 0.75 if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % 50 < 25 else 1.25
            aug_frame = utils.apply_brightness(frame, factor)
        elif selection == "2":
            alpha = 0.7 if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % 50 < 25 else 1.3
            aug_frame = utils.apply_contrast(frame, alpha=alpha)
        elif selection == "3":
            gamma = 0.6 if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % 50 < 25 else 1.7
            aug_frame = utils.apply_gamma(frame, gamma)
        elif selection == "4":
            aug_frame = utils.apply_clahe(frame, clip_limit=2.5)
        elif selection == "5":
            aug_frame = utils.apply_gaussian_blur(frame, kernel_size=5)
        elif selection == "6":
            aug_frame = utils.apply_gaussian_noise(frame, std=8.0)
        elif selection == "7":
            aug_frame = utils.apply_iso_noise(frame, amount=12.0)
        elif selection == "8":
            factor = 0.8 if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % 50 < 25 else 1.2
            aug_frame = utils.apply_white_balance(frame, factor)
        elif selection == "9":
            aug_frame = utils.apply_shadow(frame, shadow_pts, opacity=0.45)
        elif selection == "10":
            aug_frame = utils.apply_motion_blur(frame, kernel_size=7, angle=45)
        elif selection == "11":
            aug_frame = utils.apply_jpeg_compression(frame, quality=40)
        elif selection == "12":
            aug_frame = utils.apply_rotation(frame, angle=-5.0)
        elif selection == "13":
            aug_frame = utils.apply_zoom(frame, scale=1.12)
        elif selection == "14":
            dx, dy = width * 0.05, height * 0.05
            aug_frame = utils.apply_translation(frame, dx, dy)
        elif selection == "15":
            # Combo 1: Zoom (1.10) + Rotation (4.0) + Brightness (1.15) + Noise (4.0)
            aug_frame = utils.apply_zoom(frame, 1.10)
            aug_frame = utils.apply_rotation(aug_frame, 4.0)
            aug_frame = utils.apply_brightness(aug_frame, 1.15)
            aug_frame = utils.apply_gaussian_noise(aug_frame, 4.0)
        elif selection == "16":
            # Combo 2: Contrast (1.25) + Motion Blur (5, 90) + Shadow + ISO Noise (8.0)
            aug_frame = utils.apply_contrast(frame, 1.25)
            aug_frame = utils.apply_motion_blur(aug_frame, 5, 90.0)
            aug_frame = utils.apply_shadow(aug_frame, shadow_pts, 0.35)
            aug_frame = utils.apply_iso_noise(aug_frame, 8.0)

        # Merge side-by-side
        side_by_side = np.hstack((frame, aug_frame))
        
        # Display helper HUD
        cv2.putText(side_by_side, f"Original: {current_video.parent.name}/{current_video.name}", (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(side_by_side, f"Augmented: {AUGMENTATION_OPTIONS[selection]}", (width + 15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(side_by_side, "Press [1-16] to switch modes, [R] to change video, [Q] to quit", (15, height - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow("MediSign-AI Data Augmentation Preview (Left: Orig | Right: Aug)", side_by_side)

        # Listen for key press matching the video FPS frame rate
        key = cv2.waitKey(int(1000 / fps)) & 0xFF
        
        if key == 27 or key == ord('q') or key == ord('Q'):
            break
        elif key == ord('r') or key == ord('R'):
            # Load new random video
            cap.release()
            current_video = random.choice(video_files)
            print(f"Loaded new random video: {current_video.parent.name}/{current_video.name}")
            cap = cv2.VideoCapture(str(current_video))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            
            # Generate new constants for the video
            seed = random.randint(0, 999999)
            rng = np.random.default_rng(seed)
            shadow_pts = np.array([
                [int(rng.uniform(0, width)), int(rng.uniform(0, height))]
                for _ in range(rng.integers(3, 5))
            ], dtype=np.int32)
        elif chr(key) in AUGMENTATION_OPTIONS:
            selection = chr(key)
            print(f"Switched Augmentation to: {AUGMENTATION_OPTIONS[selection]}")
        else:
            # Check double digit choices (10 to 16)
            # Wait a short moment to capture second character if '1' is typed
            if key == ord('1'):
                second_key = cv2.waitKey(200) & 0xFF
                if chr(second_key) in ['0', '1', '2', '3', '4', '5', '6']:
                    selection = "1" + chr(second_key)
                    print(f"Switched Augmentation to: {AUGMENTATION_OPTIONS[selection]}")

    cap.release()
    cv2.destroyAllWindows()
    print("Previewer terminated.")


if __name__ == "__main__":
    main()
