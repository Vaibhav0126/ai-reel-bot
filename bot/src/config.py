from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BOT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BOT_ROOT.parent
load_dotenv(BOT_ROOT / ".env")

ASSETS_DIR = BOT_ROOT / "assets" / "nib"
RAW_DIR = ASSETS_DIR / "raw"
POSES_DIR = ASSETS_DIR / "poses"
BG_DIR = BOT_ROOT / "assets" / "bg"
FRIDGE_BG_PATH = BG_DIR / "fridge_open.png"
OUTPUT_DIR = BOT_ROOT / "output"
DATA_DIR = BOT_ROOT / "data"
USED_TOPICS_PATH = DATA_DIR / "used_topics.json"

HANDLE = "nibthefridgegoblin"
CHARACTER_NAME = "Nib"

# Instagram 9:16
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID", "").strip()
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "").strip()
# Cute cartoon voice for Nib (override in .env if you want)
EDGE_TTS_VOICE = os.getenv("EDGE_TTS_VOICE", "en-US-AnaNeural").strip()
EDGE_TTS_RATE = os.getenv("EDGE_TTS_RATE", "+20%").strip()
EDGE_TTS_PITCH = os.getenv("EDGE_TTS_PITCH", "+0Hz").strip()
AUTO_POST = os.getenv("AUTO_POST", "false").strip().lower() in {"1", "true", "yes"}

# Fridge-goblin palette
BG_TOP = (28, 52, 64)
BG_BOTTOM = (92, 168, 148)
CAPTION_FILL = (255, 252, 240)
CAPTION_STROKE = (20, 32, 36)
ACCENT = (255, 214, 74)

for path in (ASSETS_DIR, RAW_DIR, POSES_DIR, BG_DIR, OUTPUT_DIR, DATA_DIR):
    path.mkdir(parents=True, exist_ok=True)
