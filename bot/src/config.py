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
KITCHEN_BG_PATH = BG_DIR / "kitchen.png"
OUTPUT_DIR = BOT_ROOT / "output"
DATA_DIR = BOT_ROOT / "data"
USED_TOPICS_PATH = DATA_DIR / "used_topics.json"
USED_MEALS_PATH = DATA_DIR / "used_meals.json"
USED_FACTS_PATH = DATA_DIR / "used_facts.json"

HANDLE = "nibthefridgegoblin"
CHARACTER_NAME = "Nib"

# Instagram 9:16
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID", "").strip()
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "").strip()
# YouTube Data API v3 (OAuth2 "installed app" client + a one-time refresh token —
# see bot/get_youtube_refresh_token.py)
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "").strip()
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "").strip()
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "").strip()
YOUTUBE_PRIVACY_STATUS = os.getenv("YOUTUBE_PRIVACY_STATUS", "public").strip()
# Clear adult male voice — states the fact, does not hype it
EDGE_TTS_VOICE = os.getenv("EDGE_TTS_VOICE", "en-US-GuyNeural").strip()
EDGE_TTS_RATE = os.getenv("EDGE_TTS_RATE", "-8%").strip()
EDGE_TTS_PITCH = os.getenv("EDGE_TTS_PITCH", "+0Hz").strip()
AUTO_POST = os.getenv("AUTO_POST", "false").strip().lower() in {"1", "true", "yes"}
# Target length for curiosity-fact reels (seconds of video)
TARGET_REEL_SECONDS = 30.0

# Fridge-goblin palette
BG_TOP = (28, 52, 64)
BG_BOTTOM = (92, 168, 148)
CAPTION_FILL = (255, 252, 240)
CAPTION_STROKE = (20, 32, 36)
ACCENT = (255, 214, 74)
# Still backdrop for curiosity-fact reels (muted indigo)
FACT_BG = (84, 81, 129)

for path in (ASSETS_DIR, RAW_DIR, POSES_DIR, BG_DIR, OUTPUT_DIR, DATA_DIR):
    path.mkdir(parents=True, exist_ok=True)
