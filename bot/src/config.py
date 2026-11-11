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
OUTPUT_DIR = BOT_ROOT / "output"
DATA_DIR = BOT_ROOT / "data"
USED_FACTS_PATH = DATA_DIR / "used_facts.json"
UPLOADS_PATH = DATA_DIR / "uploads.json"

CHARACTER_NAME = "Nib"

# Vertical 9:16 Shorts
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
# YouTube Data API v3 (OAuth2 "installed app" client + a one-time refresh token —
# see bot/get_youtube_refresh_token.py)
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "").strip()
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "").strip()
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "").strip()
# Uploads go up as "private" with a scheduled publishAt, so a human can watch
# each Short before it goes live (and unschedule it if it's bad).
YOUTUBE_PRIVACY_STATUS = os.getenv("YOUTUBE_PRIVACY_STATUS", "private").strip()
# Publish time is chosen for the target audience, not the machine's timezone.
PUBLISH_TIMEZONE = os.getenv("PUBLISH_TIMEZONE", "America/New_York").strip()
PUBLISH_HOUR = int(os.getenv("PUBLISH_HOUR", "12"))
# Minimum hours between upload and publish, so there is time to review.
REVIEW_WINDOW_HOURS = float(os.getenv("REVIEW_WINDOW_HOURS", "6"))
# Voice: free Edge TTS only (no paid API). Andrew is warmer than Guy.
# Slightly fast so Shorts stay punchy; [pause] marks add the breaths.
EDGE_TTS_VOICE = os.getenv("EDGE_TTS_VOICE", "en-US-AndrewNeural").strip()
EDGE_TTS_RATE = os.getenv("EDGE_TTS_RATE", "+18%").strip()
EDGE_TTS_PITCH = os.getenv("EDGE_TTS_PITCH", "+0Hz").strip()
AUTO_POST = os.getenv("AUTO_POST", "false").strip().lower() in {"1", "true", "yes"}
# Video length follows the voiceover (plus a short tail). Do not pad to a
# fixed 30s — YouTube loops the file, so leftover silence looks
# like the reel restarting. Cap under 60s so YouTube still treats it as a Short.
MIN_REEL_SECONDS = 6.0
MAX_REEL_SECONDS = 59.5

# Palette
BG_TOP = (28, 52, 64)
BG_BOTTOM = (92, 168, 148)
CAPTION_FILL = (255, 252, 240)
CAPTION_STROKE = (20, 32, 36)
ACCENT = (255, 214, 74)
# Still backdrop for curiosity-fact reels (muted indigo)
FACT_BG = (84, 81, 129)

for path in (ASSETS_DIR, RAW_DIR, POSES_DIR, BG_DIR, OUTPUT_DIR, DATA_DIR):
    path.mkdir(parents=True, exist_ok=True)
