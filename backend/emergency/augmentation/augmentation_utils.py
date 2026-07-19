"""Utility functions for performing frame-level data augmentations and quality evaluations.

All functions use OpenCV and NumPy, optimized for speed. Includes MediaPipe HandLandmarker
validation stubs to ensure hand landmark trackability in augmented clips.
"""
from __future__ import annotations

import cv2
import numpy as np
from typing import Tuple, List, Dict, Any

# --- Quality Metrics Evaluators ---

def compute_quality_metrics(frame: np.ndarray) -> Tuple[float, float]:
    """Compute Laplacian variance (blur metric) and grayscale mean (exposure metric).
    
    Returns:
        Tuple[float, float]: (laplacian_variance, mean_exposure)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur_metric = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    exposure_metric = float(gray.mean())
    return blur_metric, exposure_metric


# --- MediaPipe Hands Validator Class ---

class HandDetectorValidator:
    """Wrapper around MediaPipe HandLandmarker Tasks API to validate hand visibility."""
    
    def __init__(self, model_path: str | Any) -> None:
        """Initialize the Tasks API landmarker model."""
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision
        
        base_options = mp_python.BaseOptions(model_asset_path=str(model_path))
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=0.4,  # slightly lenient for augmented variations
            min_hand_presence_confidence=0.4,
            min_tracking_confidence=0.4,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

    def has_hand(self, frame: np.ndarray) -> bool:
        """Run landmarker detection and return True if at least one hand is visible."""
        import mediapipe as mp
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.landmarker.detect(mp_image)
        return bool(result.hand_landmarks)

    def close(self) -> None:
        """Close the landmarker instance."""
        try:
            self.landmarker.close()
        except Exception:
            pass


# --- Individual Augmentation Operations ---

def apply_brightness(frame: np.ndarray, factor: float) -> np.ndarray:
    """Adjust frame brightness inside HSV space to preserve color metrics."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = np.array(hsv, dtype=np.float64)
    hsv[:, :, 2] *= factor
    hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
    hsv = np.array(hsv, dtype=np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def apply_contrast(frame: np.ndarray, alpha: float, beta: float = 0.0) -> np.ndarray:
    """Scale frame contrast linearly using convertScaleAbs."""
    return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)


def apply_gamma(frame: np.ndarray, gamma: float) -> np.ndarray:
    """Apply lookup table (LUT) based non-linear gamma correction."""
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(frame, table)


def apply_clahe(frame: np.ndarray, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) on L channel."""
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)


def apply_gaussian_blur(frame: np.ndarray, kernel_size: int) -> np.ndarray:
    """Apply Gaussian Blur smoothing filter."""
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)


def apply_gaussian_noise(frame: np.ndarray, std: float) -> np.ndarray:
    """Add Gaussian zero-mean noise to the frame."""
    noise = np.random.normal(0, std, frame.shape)
    noisy = frame.astype(np.float64) + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)


def apply_iso_noise(frame: np.ndarray, amount: float) -> np.ndarray:
    """Simulate high ISO sensor grain by layering luma and chroma grain."""
    noise_luma = np.random.normal(0, amount, frame.shape[:2])
    noise_chroma = np.random.normal(0, amount * 0.5, frame.shape)
    noisy = frame.astype(np.float64)
    noisy[:, :, 0] += noise_chroma[:, :, 0] + noise_luma
    noisy[:, :, 1] += noise_chroma[:, :, 1] + noise_luma
    noisy[:, :, 2] += noise_chroma[:, :, 2] + noise_luma
    return np.clip(noisy, 0, 255).astype(np.uint8)


def apply_white_balance(frame: np.ndarray, factor: float) -> np.ndarray:
    """Adjust red and blue channels to shift color temperature warm or cool."""
    result = frame.astype(np.float64)
    if factor > 1.0:
        # Warm shift: boost red (index 2), scale down blue (index 0)
        result[:, :, 2] *= factor
        result[:, :, 0] /= factor
    else:
        # Cool shift: boost blue, scale down red
        result[:, :, 0] *= (2.0 - factor)
        result[:, :, 2] /= (2.0 - factor)
    return np.clip(result, 0, 255).astype(np.uint8)


def apply_shadow(frame: np.ndarray, shadow_poly: np.ndarray, opacity: float) -> np.ndarray:
    """Overlay a semi-transparent black polygonal shadow to simulate overhead blockage."""
    overlay = frame.copy()
    cv2.fillPoly(overlay, [shadow_poly], (0, 0, 0))
    return cv2.addWeighted(overlay, opacity, frame, 1.0 - opacity, 0)


def apply_motion_blur(frame: np.ndarray, kernel_size: int, angle: float) -> np.ndarray:
    """Apply motion blur along a specific directional angle vector."""
    if kernel_size % 2 == 0:
        kernel_size += 1
    M = cv2.getRotationMatrix2D((kernel_size / 2.0, kernel_size / 2.0), angle, 1.0)
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[int(kernel_size / 2.0), :] = 1.0
    kernel = cv2.warpAffine(kernel, M, (kernel_size, kernel_size))
    kernel /= np.sum(kernel)
    return cv2.filter2D(frame, -1, kernel)


def apply_jpeg_compression(frame: np.ndarray, quality: int) -> np.ndarray:
    """Simulate lossy JPEG transmission artifacts."""
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    result, encimg = cv2.imencode('.jpg', frame, encode_param)
    if result:
        return cv2.imdecode(encimg, 1)
    return frame


def apply_rotation(frame: np.ndarray, angle: float) -> np.ndarray:
    """Rotate the frame around its center using border reflection to fill margins."""
    h, w = frame.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), angle, 1.0)
    return cv2.warpAffine(frame, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)


def apply_zoom(frame: np.ndarray, scale: float) -> np.ndarray:
    """Zoom in by cropping the center section and scaling back to original size."""
    h, w = frame.shape[:2]
    if scale <= 1.0:
        return frame
    new_h, new_w = int(h / scale), int(w / scale)
    dy = (h - new_h) // 2
    dx = (w - new_w) // 2
    cropped = frame[dy:dy+new_h, dx:dx+new_w]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)


def apply_translation(frame: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """Shift the frame horizontally and vertically, reflecting borders."""
    h, w = frame.shape[:2]
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(frame, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
