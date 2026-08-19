# Nib — Daily Fact Reel Bot

Automated pipeline for [@nibthefridgegoblin](https://instagram.com/nibthefridgegoblin).

## What it does

Two daily **curiosity-fact** reels (same format both times):

| Slot | Schedule (JST) | Content |
|------|----------------|---------|
| morning | 1:00 PM | Nib tells a fact (animals, food, psychology, body, nature, science) |
| evening | 7:00 PM | Another unused fact, category rotated vs the last post |

Each run:

1. Picks an unused fact (no repeats until the list cycles)
2. Writes a script in Nib’s voice (template mode free; Gemini optional)
3. Generates cartoon images per beat via free Pollinations.ai (Gemini image optional; shape last resort)
4. Generates voiceover with free Edge TTS
5. Builds a 9:16 reel: still color BG + centered Nib + beat art + huge top captions
6. Optionally posts to Instagram (Graph API) **and** YouTube Shorts (Data API v3)

## Setup

```bash
cd "/Users/Vaibhav/Desktop/AI Reel bot"
python3 -m venv .venv
source .venv/bin/activate
pip install -r bot/requirements.txt
cp bot/.env.example bot/.env
```

Extract poses from your character sheets (once):

```bash
.venv/bin/python bot/run_daily.py --extract-poses
```

## Generate a reel (no post)

```bash
.venv/bin/python bot/run_daily.py
# same as:
.venv/bin/python bot/run_daily.py --type fact
```

`--type fridge` / `--type meal` map to the same fact format.

Output lands in `bot/output/<timestamp>/reel.mp4` with `caption.txt` and `beat_*.png`.

## Optional: smarter scripts + beat images (Gemini)

1. Get a key: https://aistudio.google.com/apikey  
2. Put it in `bot/.env` as `GEMINI_API_KEY=...`

Gemini (optional) powers punchier voiceovers. Beat illustrations use free [Pollinations.ai](https://pollinations.ai) by default — no paid Gemini image quota needed.

## Instagram auto-post

Official posting needs a **Professional** Instagram account linked to a **Facebook Page**.

> **Full step-by-step walkthrough (including every gotcha we hit while setting this up):**
> see [`bot/INSTAGRAM_TOKEN_GUIDE.md`](INSTAGRAM_TOKEN_GUIDE.md). Use that doc whenever generating
> or renewing the token — the summary below covers the same steps more briefly.

### Recommended: Facebook Page token (most reliable for local MP4s)

Instagram Login tokens (`IGAA…`) require a public `video_url`. Meta often fails to download free hosts / Cloudflare tunnels. A **Page token** (`EAA…`) can upload the file directly (resumable).

1. Open [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app → add permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
3. Generate token → approve the Facebook Page linked to `@nibthefridgegoblin`
4. Call `GET /me/accounts?fields=name,access_token,instagram_business_account`
5. Copy:
   - Page `access_token` → `INSTAGRAM_ACCESS_TOKEN` (should start with `EAA`)
   - `instagram_business_account.id` → `INSTAGRAM_USER_ID` (often starts with `178414…`)
6. Put them in `bot/.env`:

```env
INSTAGRAM_USER_ID=178414...
INSTAGRAM_ACCESS_TOKEN=EAAxxxx...
AUTO_POST=false
```

### Also supported: Instagram Login token (`IGAA…`)

Works if Meta can fetch a temporary public URL of your MP4. Use dashboard ID `178414…` or the `/me` id; the bot auto-resolves `/me`.

Post one reel when ready:

```bash
.venv/bin/python bot/run_daily.py --type fact --post
# or retry an existing file:
.venv/bin/python bot/run_daily.py --post-file bot/output/<stamp>/reel.mp4
```

## Run every day (GitHub Actions)

The bot posts from GitHub Actions so your Mac does not need to stay on.

| Workflow | Cron (UTC) | JST | Command |
|----------|------------|-----|---------|
| [daily-reel.yml](../.github/workflows/daily-reel.yml) | `7 4 * * *` | **1:00 PM** | `--type fact --post` |
| [daily-meal-reel.yml](../.github/workflows/daily-meal-reel.yml) | `9 10 * * *` | **7:00 PM** | `--type fact --post` |

### Required repo secrets

Settings → Secrets and variables → Actions:

- `INSTAGRAM_USER_ID`
- `INSTAGRAM_ACCESS_TOKEN` (Facebook **Page** token, `EAA…`)
- `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN` (see [YouTube Shorts auto-post](#youtube-shorts-auto-post))
- `GEMINI_API_KEY` (recommended — scripts + image fallback)

Or set via CLI:

```bash
gh secret set INSTAGRAM_USER_ID <<<"178414..."
gh secret set INSTAGRAM_ACCESS_TOKEN <<<"EAAxxxx..."
gh secret set YOUTUBE_CLIENT_ID <<<"....apps.googleusercontent.com"
gh secret set YOUTUBE_CLIENT_SECRET <<<"..."
gh secret set YOUTUBE_REFRESH_TOKEN <<<"..."
gh secret set GEMINI_API_KEY <<<"..."
```

### Manual test run

GitHub → Actions → **Daily Nib Reel** or **Daily Nib Meal Reel** → **Run workflow**

Or:

```bash
gh workflow run daily-reel.yml
gh workflow run daily-meal-reel.yml
```

### Token refresh

Page access tokens expire (~60 days). Follow [`bot/INSTAGRAM_TOKEN_GUIDE.md`](INSTAGRAM_TOKEN_GUIDE.md)
to regenerate it, then update the `INSTAGRAM_ACCESS_TOKEN` **secret** (and local `bot/.env` if you
still test locally).

## YouTube Shorts auto-post

The same video that gets posted as an Instagram Reel is also uploaded as a YouTube Short (title/description get `#Shorts` appended, which is what routes a ≤60s 9:16 upload into the Shorts shelf — there's no separate "Shorts" endpoint).

### One-time setup

1. [Google Cloud Console](https://console.cloud.google.com/) → create/select a project
2. **APIs & Services → Library** → enable **YouTube Data API v3**
3. **APIs & Services → OAuth consent screen** → configure it (External is fine; Testing mode works as long as your Google account is added as a test user)
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID** → Application type **Desktop app** → download the JSON, save it as `bot/client_secret.json`
5. Run the one-time helper locally (opens a browser to approve upload access for the channel you want the bot to post to):

```bash
.venv/bin/python bot/get_youtube_refresh_token.py
```

6. Copy the printed values into `bot/.env`:

```env
YOUTUBE_CLIENT_ID=....apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=...
YOUTUBE_REFRESH_TOKEN=...
YOUTUBE_PRIVACY_STATUS=public
```

7. Delete `bot/client_secret.json` afterward (or keep it out of git — it's already covered by `.gitignore`-worthy secrets, don't commit it).

### Required repo secrets (for GitHub Actions)

Add alongside the Instagram ones:

```bash
gh secret set YOUTUBE_CLIENT_ID <<<"....apps.googleusercontent.com"
gh secret set YOUTUBE_CLIENT_SECRET <<<"..."
gh secret set YOUTUBE_REFRESH_TOKEN <<<"..."
```

Notes:

- The refresh token doesn't expire from time alone — it stays valid until you revoke it in [Google Account permissions](https://myaccount.google.com/permissions) or leave the project in OAuth "Testing" mode for >7 days without publishing the app (unverified apps in Testing mode expire refresh tokens after 7 days — for a long-running bot, either publish the OAuth consent screen, or keep the app in "Testing" and re-run `get_youtube_refresh_token.py` if it stops working).
- If either `INSTAGRAM_*` or `YOUTUBE_*` creds are missing, the bot just skips that platform and still posts to the other — no crash.

## Project layout

```text
bot/
  assets/nib/raw/      # your original sheets
  assets/nib/poses/    # auto-cropped poses
  data/                # used_facts.json
  src/                 # facts, script, voice, video, Instagram
  output/              # generated reels
  run_daily.py
```
