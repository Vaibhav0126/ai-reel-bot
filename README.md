# Nib — AI Curiosity-Fact Shorts Bot

A fully automated pipeline that writes, voices, illustrates, renders and
schedules one vertical **YouTube Short** a day, starring **Nib**, a cartoon
goblin who tells surprising (true) curiosity facts.

Everything runs on the **GitHub Actions free tier**. Each day the bot uploads
the Short as **private with a scheduled publish time**, so a human can watch it
first and unschedule it if it isn't good enough.

## What happens every day

1. **Learn from yesterday.** Fetch view counts for past uploads from the
   YouTube API and update `bot/data/uploads.json`.
2. **Pick a category**, weighted by how well each category has performed
   (never the same as yesterday's).
3. **Invent a fact.** Gemini picks a true but *lesser-known* fact in that
   category, avoiding the overused viral ones and everything already posted
   (`bot/data/used_facts.json`), then writes a 6-beat script in Nib's voice.
   If Gemini can't write it, the run stops instead of uploading a template.
4. **Illustrate.** One image per beat (Cloudflare Workers AI → Pollinations →
   geometric fallback).
5. **Voice.** Free Edge TTS (Microsoft neural voice), with real silences for
   `[pause]` marks.
6. **Render** a 1080×1920 video frame by frame with Pillow + FFmpeg: a hard-hitting
   first second (big zoom-in hook image with shake, Nib sliding in, flash cut),
   karaoke captions synced to the voice, and a new illustration per beat.
7. **Schedule.** Upload to YouTube as private with `publishAt` set to the next
   12:00 in the target audience's timezone (default US Eastern), at least
   6 hours away.

## Tech stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.12, GitHub Actions (daily cron) |
| Scripts | Gemini API (JSON mode); a run stops rather than upload a template script |
| Voice | Edge TTS (free, no API key) |
| Images | Cloudflare Workers AI (Flux), Pollinations, geometric fallback |
| Video | Pillow + NumPy frame rendering, FFmpeg (imageio-ffmpeg) |
| Publishing | YouTube Data API v3 (scheduled private uploads) |
| Feedback | YouTube Data API v3 statistics → category weighting |

## Repository layout

```
bot/
  run_daily.py             CLI entry point
  get_youtube_refresh_token.py   one-time OAuth helper
  src/
    script_gen.py          fact invention + script writing (Gemini)
    facts.py               fallback fact bank + categories
    fact_image.py          beat illustrations
    tts.py                 Edge voice with word timings
    video.py               frame renderer (hook motion, captions, Nib)
    scheduling.py          next publish slot in the audience's timezone
    performance.py         view tracking + category weighting
    youtube.py             upload + statistics
    pipeline.py            ties the steps together
  data/
    used_facts.json        everything already posted (anti-repetition)
    uploads.json           video ids, categories, view counts
tests/test_logic.py        unit tests for scheduling + feedback loop
.github/workflows/daily-fact-reel.yml
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r bot/requirements.txt
cp bot/.env.example bot/.env      # fill in the keys
python bot/run_daily.py --extract-poses   # one-time: cut Nib's poses from the character sheets
python bot/run_daily.py                   # generate a Short locally, no upload
python bot/run_daily.py --post            # generate + schedule on YouTube
```

**YouTube access (one time):** create an OAuth client ("Desktop app") in Google
Cloud with the YouTube Data API v3 enabled, save it as `bot/client_secret.json`
(git-ignored), then run `python bot/get_youtube_refresh_token.py`. It requests
upload + read-only access; read-only is what lets the feedback loop see view
counts.

**GitHub Actions secrets:** `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`,
`YOUTUBE_REFRESH_TOKEN`, `GEMINI_API_KEY`, `CLOUDFLARE_ACCOUNT_ID`,
`CLOUDFLARE_API_TOKEN`.

**Configuration** (env vars, see `bot/.env.example`): `PUBLISH_TIMEZONE`,
`PUBLISH_HOUR`, `REVIEW_WINDOW_HOURS`, `EDGE_TTS_VOICE`.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Results and lessons from version 1

Version 1 posted three times a day to Instagram Reels and YouTube Shorts for
about five weeks: **286 unattended runs at a 95% success rate**. Technically it
worked. The channel did not grow. Looking back at the code, the reasons were
in the design, not the infrastructure:

- **Overused content.** The prompt asked for "well-established, widely
  documented" facts, which steered the model straight to the most-reposted
  facts on the platform.
- **No single niche.** Curiosity facts, fridge food facts and cooking recipes
  all on one account, so the algorithm never found a stable audience.
- **Wrong timezone.** English content posted at 1pm/4pm/7pm Japan time, which
  is late night and early morning in the US.
- **Weak first second** (a still background and a small image) and a
  recognisable stock TTS voice.
- **Volume over quality, and no feedback loop.** Three unreviewed posts a day,
  and the bot never looked at its own view counts.

Version 2 (this code) addresses each one: lesser-known facts, curiosity facts
only, US-timed scheduling, a stronger hook and voice, one reviewed Short a day,
and view-count-driven category selection.

## License

MIT
