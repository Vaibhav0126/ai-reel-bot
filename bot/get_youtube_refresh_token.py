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

This opens your browser once. Approve the "upload videos" permission for the
YouTube channel you want the bot to post to, then copy the printed values into
bot/.env:
    YOUTUBE_CLIENT_ID=...
    YOUTUBE_CLIENT_SECRET=...
    YOUTUBE_REFRESH_TOKEN=...
"""

from __future__ import annotations

import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main() -> None:
    root = Path(__file__).resolve().parent
    client_secret_path = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "client_secret.json"

    if not client_secret_path.exists():
        print(f"Could not find {client_secret_path}")
        print("Download an OAuth 'Desktop app' client JSON from Google Cloud Console")
        print("(APIs & Services -> Credentials) and save it there, or pass its path:")
        print("  .venv/bin/python bot/get_youtube_refresh_token.py /path/to/client_secret.json")
        raise SystemExit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), SCOPES)
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
