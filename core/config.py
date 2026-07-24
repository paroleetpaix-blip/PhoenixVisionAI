"""
========================================================
PHOENIX VISION AI
config.py

Configuration du logiciel

Phoenix Security Technologies
========================================================
"""

from core import constants

# ======================================================
# APPLICATION
# ======================================================

APP_NAME = constants.APP_NAME
VERSION = constants.VERSION

# ======================================================
# IA
# ======================================================

MODEL_NAME = "YOLOv8"

MODEL_PATH = "models/yolov8n.pt"

CONFIDENCE = 0.35

# ======================================================
# VIDÉO
# ======================================================

DEFAULT_VIDEO = "videos/route.mp4"

CAMERA_INDEX = 0

# ======================================================
# SORTIES
# ======================================================

OUTPUT_FOLDER = constants.OUTPUTS_FOLDER

SAVE_IMAGES = True

SAVE_VIDEO = True

SAVE_JSON = True

# ======================================================
# LOGS
# ======================================================

DEBUG = True