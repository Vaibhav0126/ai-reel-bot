#!/usr/bin/env python3
"""
One-time local helper: opens a browser so you can grant YouTube upload access,
then prints the refresh token to paste into bot/.env (and your GitHub secrets).

Setup before running:
1. https://console.cloud.google.com/ -> create/select a project
2. Enable the "YouTube Data API v3" (APIs & Services -> Library)
3. APIs & Services -> OAuth consent screen -> configure it (External is fine;
   "Testing" mode is OK as long as your Google account is added as a test user)
4. APIs & Services -> Credentials -> Create Credentials -> OAuth client ID
   -> Application type: "Desktop app" -> download the JSON
5. Save that JSON next to this script as bot/client_secret.json
   (or pass its path as the first CLI argument)

Run:
    .venv/bin/python bot/get_youtube_refresh_token.py

Google no longer lets you re-download an existing client secret. If
YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET are already in bot/.env, this
script uses those and you do not need a JSON file.

If you lost the secret: on the Desktop client page click "Add secret", copy
the new value into bot/.env as YOUTUBE_CLIENT_SECRET, then re-run this script.

This opens your browser once. Approve the "upload videos" permission for the
YouTube channel you want the bot to post to, then copy the printed
YOUTUBE_REFRESH_TOKEN into bot/.env (and GitHub secrets if you use Actions).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    # read view counts for the feedback loop (bot/src/performance.py)
    "https://www.googleapis.com/auth/youtube.readonly",
]


def _flow_from_env(root: Path) -> InstalledAppFlow | None:
    load_dotenv(root / ".env")
    client_id = os.getenv("YOUTUBE_CLIENT_ID", "").strip()
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        return None
    return InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        },
        SCOPES,
    )


def main() -> None:
    root = Path(__file__).resolve().parent
    client_secret_path = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "client_secret.json"

    if client_secret_path.exists():
        flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), SCOPES)
    else:
        flow = _flow_from_env(root)
        if flow is None:
            print(f"Could not find {client_secret_path}")
            print("and bot/.env is missing YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET.")
            print("On the Desktop client page, click Add secret, put the new values in")
            print("bot/.env, then re-run this script.")
            raise SystemExit(1)

    creds = flow.run_local_server(port=0, prompt="consent")

    print("\nAdd these to bot/.env (and as GitHub Actions secrets):\n")
    print(f"YOUTUBE_CLIENT_ID={creds.client_id}")
    print(f"YOUTUBE_CLIENT_SECRET={creds.client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}")

    if not creds.refresh_token:
        print(
            "\nNo refresh token returned — Google only issues one the first time you "
            "consent. Revoke access at https://myaccount.google.com/permissions and "
            "run this script again."
        )


if __name__ == "__main__":
    main()
