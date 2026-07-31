from __future__ import annotations

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

TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeConfigError(RuntimeError):
    pass


def can_post() -> bool:
    return bool(YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET and YOUTUBE_REFRESH_TOKEN)


def _require_creds() -> Credentials:
    if not can_post():
        raise YouTubeConfigError(
            "Missing YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET / YOUTUBE_REFRESH_TOKEN "
            "in bot/.env. Run `python bot/get_youtube_refresh_token.py` once to get them."
        )
    creds = Credentials(
        token=None,
        refresh_token=YOUTUBE_REFRESH_TOKEN,
        token_uri=TOKEN_URI,
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_CLIENT_SECRET,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def post_short(
    video_path: Path,
    title: str,
    description: str,
    tags: list[str] | None = None,
    category_id: str = "26",  # "Howto & Style"
) -> dict:
    """
    Upload a vertical video as a YouTube Short via the Data API v3.
    Adding #Shorts in the title/description (plus <=60s, 9:16 video) is what
    routes it into the Shorts shelf — there is no separate "Shorts" upload endpoint.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(video_path)

    creds = _require_creds()
    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)

    if "#shorts" not in title.lower() and "#shorts" not in description.lower():
        description = f"{description}\n\n#Shorts".strip()

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": (tags or [])[:500],
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": YOUTUBE_PRIVACY_STATUS,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True, chunksize=-1)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    try:
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   YouTube upload: {int(status.progress() * 100)}%")
    except HttpError as exc:
        raise RuntimeError(f"YouTube upload failed: {exc}") from exc

    video_id = response.get("id")
    response["url"] = f"https://youtube.com/shorts/{video_id}" if video_id else None
    return response
