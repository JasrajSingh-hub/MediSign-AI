"""Configuration settings for the Emergency Gesture Video Augmentation Pipeline.

Allows customization of augmentation ranges, enabling/disabling specific transformations,
specifying quality metrics thresholds, and adjusting downstream MediaPipe validation targets.
"""
from pathlib import Path

# --- Repository Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
INPUT_DIR = BASE_DIR / "SOS"
OUTPUT_DIR = BASE_DIR / "SOS_Augmented"
LANDMARKER_PATH = BASE_DIR / "emergency" / "models" / "hand_landmarker.task"
LOG_DIR = BASE_DIR / "backend" / "emergency" / "augmentation" / "logs"
REPORT_DIR = BASE_DIR / "backend" / "emergency" / "augmentation" / "reports"

# --- Pipeline Settings ---
AUGMENTATIONS_PER_VIDEO = 3  # Number of randomized combo variations to generate per original video
NUM_WORKERS = 4              # Threads for parallel video generation
OUTPUT_CODEC = "MJPG"        # Codec for OpenCV VideoWriter (.avi)
TARGET_SIZE = None           # Tuple (width, height) to resize, or None to preserve original resolution

# --- Quality Metrics Limits ---
# Reject videos if their frame average metrics fall outside these boundaries
MIN_LAPLACIAN_VAR = 15.0     # Minimum blur metric (Laplacian variance) to avoid excessively blurry videos
MIN_EXPOSURE = 35.0          # Minimum luma average to reject extremely dark/underexposed videos
MAX_EXPOSURE = 220.0         # Maximum luma average to reject washed out/overexposed videos

# --- MediaPipe Hands Validation ---
MIN_DETECTION_RATE = 0.80    # Discard augmented video if hands are detected on <80% of its frames

# --- Individual Augmentation Ranges ---
BRIGHTNESS_RANGE = [0.7, 1.3]       # Multiplicative factor range
CONTRAST_RANGE = [0.7, 1.3]         # Alpha factor range
GAMMA_RANGE = [0.5, 2.0]            # Gamma correction exponent range
GAUSSIAN_BLUR_KERNELS = [3, 5]      # Odd integers only
GAUSSIAN_NOISE_STD = [2.0, 10.0]    # Std deviation range for luma noise
ISO_NOISE_LEVEL = [5.0, 15.0]       # Noise level range
TEMP_WARM_FACTOR = [1.05, 1.25]     # White balance warm scale factor
TEMP_COOL_FACTOR = [0.75, 0.95]     # White balance cool scale factor
SHADOW_OPACITY = [0.3, 0.6]         # Max opacity of simulated shadow overlay
MOTION_BLUR_KERNELS = [3, 7]        # Kernel size range
JPEG_QUALITY_RANGE = [50, 95]       # Quality compression level
ROTATION_ANGLE_RANGE = [-8.0, 8.0]  # Degrees (positive or negative)
ZOOM_RANGE = [1.0, 1.15]            # Magnification factor range
TRANSLATION_MAX_PCT = 0.08          # Max translation offset as % of frame dimension

# --- Toggle Switches ---
# Enable/disable specific transformations when assembling randomized combo pipelines
ENABLE_BRIGHTNESS = True
ENABLE_CONTRAST = True
ENABLE_GAMMA = True
ENABLE_CLAHE = True
ENABLE_GAUSSIAN_BLUR = True
ENABLE_GAUSSIAN_NOISE = True
ENABLE_ISO_NOISE = True
ENABLE_WHITE_BALANCE = True
ENABLE_SHADOW = True
ENABLE_MOTION_BLUR = True
ENABLE_JPEG_COMPRESSION = True
ENABLE_ROTATION = True
ENABLE_ZOOM = True
ENABLE_TRANSLATION = True
