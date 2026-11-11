from __future__ import annotations

import re
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from .config import (
    YOUTUBE_CLIENT_ID,
    YOUTUBE_CLIENT_SECRET,
    YOUTUBE_PRIVACY_STATUS,
    YOUTUBE_REFRESH_TOKEN,
)
from .tts import strip_pause_marks

TOKEN_URI = "https://oauth2.googleapis.com/token"
# upload: post Shorts. readonly: read view counts for the feedback loop.
# Re-run bot/get_youtube_refresh_token.py once to grant readonly; until then
# uploads still work and the feedback loop is skipped.
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


class YouTubeConfigError(RuntimeError):
    pass


def can_post() -> bool:
    return bool(YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET and YOUTUBE_REFRESH_TOKEN)


def _client():
    if not can_post():
        raise YouTubeConfigError(
            "Missing YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET / YOUTUBE_REFRESH_TOKEN "
            "in bot/.env. Run `python bot/get_youtube_refresh_token.py` once to get them."
        )
    # No `scopes=` here: refresh with whatever the token was granted, so an
    # older upload-only token keeps working.
    creds = Credentials(
        token=None,
        refresh_token=YOUTUBE_REFRESH_TOKEN,
        token_uri=TOKEN_URI,
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_CLIENT_SECRET,
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def _clean_title(title: str) -> str:
    title = re.sub(r"\s+", " ", strip_pause_marks(title))
    title = re.sub(r"\bpause\b", " ", title, flags=re.I)
    return re.sub(r"\s+", " ", title).strip()


def post_short(
    video_path: Path,
    title: str,
    description: str,
    tags: list[str] | None = None,
    publish_at: str | None = None,
    category_id: str = "27",  # "Education"
) -> dict:
    """
    Upload a vertical video as a YouTube Short via the Data API v3.

    With `publish_at` (RFC 3339 UTC), the video is uploaded private and YouTube
    publishes it automatically at that time; until then you can watch it in
    YouTube Studio and unschedule or delete it. Adding #Shorts (plus <=60s,
    9:16) routes it into the Shorts shelf.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(video_path)

    youtube = _client()

    if "#shorts" not in title.lower() and "#shorts" not in description.lower():
        description = f"{description}\n\n#Shorts".strip()

    status: dict = {"selfDeclaredMadeForKids": False}
    if publish_at:
        status["privacyStatus"] = "private"  # required by the API for publishAt
        status["publishAt"] = publish_at
    else:
        status["privacyStatus"] = YOUTUBE_PRIVACY_STATUS

    body = {
        "snippet": {
            "title": _clean_title(title)[:100],
            "description": description[:5000],
            "tags": (tags or [])[:500],
            "categoryId": category_id,
        },
        "status": status,
    }

    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True, chunksize=-1)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    try:
        while response is None:
            progress, response = request.next_chunk()
            if progress:
                print(f"   YouTube upload: {int(progress.progress() * 100)}%")
    except HttpError as exc:
        raise RuntimeError(f"YouTube upload failed: {exc}") from exc

    video_id = response.get("id")
    response["url"] = f"https://youtube.com/shorts/{video_id}" if video_id else None
    return response


def fetch_stats(video_ids: list[str]) -> dict[str, dict]:
    """{video_id: {"views": int, "likes": int}}. Needs the youtube.readonly scope."""
    ids = [v for v in dict.fromkeys(video_ids) if v]
    if not ids:
        return {}
    youtube = _client()
    out: dict[str, dict] = {}
    for i in range(0, len(ids), 50):  # API max 50 ids per call
        resp = youtube.videos().list(part="statistics", id=",".join(ids[i : i + 50])).execute()
        for item in resp.get("items", []):
            st = item.get("statistics", {})
            out[item["id"]] = {
                "views": int(st.get("viewCount", 0)),
                "likes": int(st.get("likeCount", 0)),
            }
    return out
