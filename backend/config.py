from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
MODULE_B_DIR = BASE_DIR / "module_b_backend"

TTS_PORT = int(os.getenv("TTS_PORT", "5001"))
EMERGENCY_PORT = int(os.getenv("EMERGENCY_PORT", "8001"))
MAIN_PORT = int(os.getenv("MAIN_PORT", "5000"))















