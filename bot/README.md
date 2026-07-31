# Nib the Fridge Goblin — Daily Reel Bot

Automated pipeline for [@nibthefridgegoblin](https://instagram.com/nibthefridgegoblin).

## What it does

Two daily reel types:

| Type | Schedule (JST) | Content |
|------|----------------|---------|
| **fridge** | 1:00 PM | Fridge-find nutrition tip in front of the open fridge |
| **meal** | 7:00 PM | Quick easy delicious meal in the kitchen — animated ingredients + plated finale |

Each run:

1. Picks a topic/meal (no repeats until the list cycles)
2. Writes a script in Nib’s voice (template mode free; Gemini optional)
3. For meals: generates a plated photo via free Pollinations.ai (Gemini image optional; cartoon last resort)
4. Generates voiceover with free Edge TTS
5. Builds a 9:16 reel from Nib poses + captions
6. Optionally posts to Instagram via Graph API

Meal Instagram captions include **ingredients**, **spices**, **detailed how-to steps**, and **macros**. Meal voiceovers are longer (~90–130 words) so Nib walks through spices and cooking clearly.

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

Fridge nutrition (default):

```bash
.venv/bin/python bot/run_daily.py
# same as:
.venv/bin/python bot/run_daily.py --type fridge
```

Meal recipe:

```bash
.venv/bin/python bot/run_daily.py --type meal
```

Output lands in `bot/output/<timestamp>/reel.mp4` with `caption.txt` (and `plate.png` for meals).

## Optional: smarter scripts + meal plate photos (Gemini)

1. Get a key: https://aistudio.google.com/apikey  
2. Put it in `bot/.env` as `GEMINI_API_KEY=...`

Gemini (optional) powers punchier voiceovers. Meal plate photos use free [Pollinations.ai](https://pollinations.ai) by default — no paid Gemini image quota needed.

## Instagram auto-post

Official posting needs a **Professional** Instagram account linked to a **Facebook Page**.

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
.venv/bin/python bot/run_daily.py --type fridge --post
.venv/bin/python bot/run_daily.py --type meal --post
# or retry an existing file:
.venv/bin/python bot/run_daily.py --post-file bot/output/<stamp>/reel.mp4
```

## Run every day (GitHub Actions)

The bot posts from GitHub Actions so your Mac does not need to stay on.

| Workflow | Cron (UTC) | JST | Command |
|----------|------------|-----|---------|
| [daily-reel.yml](../.github/workflows/daily-reel.yml) | `0 4 * * *` | **1:00 PM** | `--type fridge --post` |
| [daily-meal-reel.yml](../.github/workflows/daily-meal-reel.yml) | `0 10 * * *` | **7:00 PM** | `--type meal --post` |

### Required repo secrets

Settings → Secrets and variables → Actions:

- `INSTAGRAM_USER_ID`
- `INSTAGRAM_ACCESS_TOKEN` (Facebook **Page** token, `EAA…`)
- `GEMINI_API_KEY` (recommended — scripts + meal plate photos)

Or set via CLI:

```bash
gh secret set INSTAGRAM_USER_ID <<<"178414..."
gh secret set INSTAGRAM_ACCESS_TOKEN <<<"EAAxxxx..."
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

Page access tokens expire (~60 days). Re-generate from Graph API Explorer and update the `INSTAGRAM_ACCESS_TOKEN` **secret** (and local `bot/.env` if you still test locally).

## Project layout

```text
bot/
  assets/bg/           # fridge_open.png, kitchen.png
  assets/nib/raw/      # your original sheets
  assets/nib/poses/    # auto-cropped poses
  data/                # used_topics.json, used_meals.json
  src/                 # script, voice, video, meal render, Instagram
  output/              # generated reels
  run_daily.py
```
