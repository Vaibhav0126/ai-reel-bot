from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from .config import (
    AUTO_POST,
    OUTPUT_DIR,
    PUBLISH_HOUR,
    PUBLISH_TIMEZONE,
    REVIEW_WINDOW_HOURS,
    UPLOADS_PATH,
)
from .fact_image import generate_fact_images
from .performance import apply_stats, load_uploads, record_upload, save_uploads, summary
from .poses import extract_poses, list_poses
from .scheduling import next_publish_time, to_rfc3339
from .script_gen import ReelScript, generate_script, mark_fact_used
from .tts import strip_pause_marks
from .video import render_reel
from .youtube import can_post as can_post_youtube
from .youtube import fetch_stats, post_short


def _youtube_title(script: ReelScript) -> str:
    hook = strip_pause_marks(script.hook or script.topic)
    hook = re.sub(r"\bpause\b", " ", hook, flags=re.I)
    hook = re.sub(r"\s+", " ", hook).strip(" .")
    title = hook if hook.endswith(("!", "?", ".")) else f"{hook}!"
    return f"{title} #Shorts"[:100]


def _youtube_description(script: ReelScript) -> str:
    hashtags = " ".join(f"#{tag}" for tag in script.hashtags)
    return f"{script.caption}\n\n{hashtags} #Shorts".strip()


def refresh_performance() -> None:
    """Pull view counts for past uploads. Never fails the run."""
    uploads = load_uploads(UPLOADS_PATH)
    if not uploads or not can_post_youtube():
        return
    try:
        stats = fetch_stats([u["video_id"] for u in uploads if u.get("video_id")])
    except Exception as exc:  # noqa: BLE001
        print(
            f"   Feedback loop skipped ({type(exc).__name__}). If this says insufficient "
            "permissions, re-run bot/get_youtube_refresh_token.py to grant read access."
        )
        return
    now = datetime.now(timezone.utc)
    save_uploads(UPLOADS_PATH, apply_stats(uploads, stats, now))
    print(f"   Performance so far: {summary(uploads, now)}")


def check_uploadable(script: ReelScript) -> None:
    """Refuse to publish a hand-written template script.

    The template bank is only for local testing. If Gemini was down, a
    scheduled run should fail loudly instead of uploading a canned fact.
    """
    if script.source != "gemini":
        raise RuntimeError(
            "Gemini did not write this script (template fallback), so nothing was "
            "uploaded. Check GEMINI_API_KEY and the Gemini billing/quota, then re-run."
        )


def run_daily(post: bool | None = None) -> dict:
    """Generate today's curiosity-fact Short and optionally schedule it on YouTube."""
    should_post = AUTO_POST if post is None else post

    if should_post:
        print("0/4 Refreshing view counts for the feedback loop…")
        refresh_performance()

    poses = list_poses()
    if len(poses) < 5:
        print("Extracting poses from character sheets…")
        extract_poses()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUTPUT_DIR / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    print("1/4 Writing script…")
    script = generate_script()
    print(f"   Topic: {script.topic}" + (f" ({script.category})" if script.category else ""))
    if should_post:
        check_uploadable(script)
    print("   Generating beat images…")
    generate_fact_images(script, out_dir)

    (out_dir / "script.json").write_text(json.dumps(script.to_dict(), indent=2))
    (out_dir / "caption.txt").write_text(script.caption)

    print("2/4 Rendering video + voice…")
    video_path = render_reel(script, out_dir)
    print(f"   Video: {video_path}")
    mark_fact_used(script.topic_id, title=script.topic, category=script.category)

    result = {
        "output_dir": str(out_dir),
        "video": str(video_path),
        "topic": script.topic,
        "category": script.category,
        "caption": script.caption,
        "youtube_posted": False,
        "youtube_response": None,
        "publish_at": None,
    }

    if should_post:
        print("3/4 Uploading to YouTube (private, scheduled)…")
        if not can_post_youtube():
            print(
                "   Skipped: add YOUTUBE_CLIENT_ID/SECRET/REFRESH_TOKEN to bot/.env "
                "(see bot/get_youtube_refresh_token.py)"
            )
        else:
            publish_at = to_rfc3339(
                next_publish_time(
                    datetime.now(timezone.utc),
                    tz_name=PUBLISH_TIMEZONE,
                    hour=PUBLISH_HOUR,
                    min_lead_hours=REVIEW_WINDOW_HOURS,
                )
            )
            try:
                yt_resp = post_short(
                    video_path,
                    title=_youtube_title(script),
                    description=_youtube_description(script),
                    tags=script.hashtags,
                    publish_at=publish_at,
                )
                result.update(youtube_posted=True, youtube_response=yt_resp, publish_at=publish_at)
                record_upload(
                    UPLOADS_PATH,
                    video_id=yt_resp.get("id", ""),
                    category=script.category,
                    title=script.topic,
                    publish_at=publish_at,
                )
                print(f"   Scheduled for {publish_at} UTC: {yt_resp.get('url')}")
                print("   Review it in YouTube Studio > Content before then.")
            except Exception as exc:  # noqa: BLE001
                result["youtube_response"] = {"error": str(exc)}
                print(f"   YouTube upload failed: {exc}")
                raise
    else:
        print("3/4 Upload skipped. Review the video in the output folder.")

    print("4/4 Done.")
    (out_dir / "result.json").write_text(json.dumps(result, indent=2))
    return result
