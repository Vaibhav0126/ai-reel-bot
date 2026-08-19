from __future__ import annotations

import json
from datetime import datetime

from .config import AUTO_POST, OUTPUT_DIR
from .fact_image import generate_fact_images
from .fridge_video import render_fridge_reel
from .instagram import can_post, post_reel
from .meal_image import generate_meal_image
from .meal_video import render_meal_reel
from .poses import extract_poses, list_poses
from .script_gen import (
    ReelScript,
    ReelType,
    generate_script,
    mark_fact_used,
    mark_meal_used,
    mark_topic_used,
)
from .video import render_reel
from .youtube import can_post as can_post_youtube
from .youtube import post_short


def _normalize_reel_type(reel_type: ReelType | str) -> ReelType:
    if reel_type in {"fact", "fridge", "meal"}:
        return reel_type  # type: ignore[return-value]
    return "fact"


def _youtube_title(script: ReelScript) -> str:
    hook = (script.hook or script.topic).strip()
    title = hook if hook.endswith(("!", "?", ".")) else f"{hook}!"
    title = f"{title} #Shorts"
    return title[:100]


def _youtube_description(script: ReelScript) -> str:
    hashtags = " ".join(f"#{tag}" for tag in script.hashtags)
    return f"{script.caption}\n\n{hashtags} #Shorts".strip()


def run_daily(post: bool | None = None, reel_type: ReelType = "fact") -> dict:
    """Generate today's Nib reel (fact, fridge, or meal). Optionally publish."""
    should_post = AUTO_POST if post is None else post
    reel_type = _normalize_reel_type(reel_type)

    poses = list_poses()
    if len(poses) < 5:
        print("Extracting poses from character sheets…")
        extract_poses()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUTPUT_DIR / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"1/4 Writing {reel_type} script…")
    script = generate_script(reel_type=reel_type)
    print(f"   Topic: {script.topic}" + (f" ({script.category})" if script.category else ""))

    if reel_type == "fact":
        print("   Generating cartoon beat images…")
        generate_fact_images(script, out_dir)
    elif reel_type == "meal":
        print("   Generating plated meal image…")
        plate = generate_meal_image(script, out_dir)
        script.meal_image_path = str(plate)

    (out_dir / "script.json").write_text(json.dumps(script.to_dict(), indent=2))
    (out_dir / "caption.txt").write_text(script.caption)

    print("2/4 Rendering video + voice…")
    if reel_type == "meal":
        video_path = render_meal_reel(script, out_dir)
    elif reel_type == "fridge":
        video_path = render_fridge_reel(script, out_dir)
    else:
        video_path = render_reel(script, out_dir)
    print(f"   Video: {video_path}")

    if reel_type == "meal":
        mark_meal_used(script.topic_id)
    elif reel_type == "fridge":
        mark_topic_used(script.topic_id)
    else:
        mark_fact_used(script.topic_id)

    result = {
        "output_dir": str(out_dir),
        "video": str(video_path),
        "topic": script.topic,
        "reel_type": reel_type,
        "category": script.category,
        "caption": script.caption,
        "posted": False,
        "publish_response": None,
        "youtube_posted": False,
        "youtube_response": None,
    }

    if should_post:
        print("3/4 Posting to Instagram…")
        if not can_post():
            print("   Skipped: add INSTAGRAM_USER_ID + INSTAGRAM_ACCESS_TOKEN to bot/.env")
        else:
            try:
                resp = post_reel(video_path, script.caption)
                result["posted"] = True
                result["publish_response"] = resp
                print(f"   Posted: {resp}")
            except Exception as exc:  # noqa: BLE001
                result["publish_response"] = {"error": str(exc)}
                print(f"   Instagram post failed: {exc}")

        print("   Posting to YouTube Shorts…")
        if not can_post_youtube():
            print(
                "   Skipped: add YOUTUBE_CLIENT_ID/SECRET/REFRESH_TOKEN to bot/.env "
                "(see bot/get_youtube_refresh_token.py)"
            )
        else:
            try:
                yt_resp = post_short(
                    video_path,
                    title=_youtube_title(script),
                    description=_youtube_description(script),
                    tags=script.hashtags,
                )
                result["youtube_posted"] = True
                result["youtube_response"] = yt_resp
                print(f"   Posted: {yt_resp.get('url', yt_resp)}")
            except Exception as exc:  # noqa: BLE001
                result["youtube_response"] = {"error": str(exc)}
                print(f"   YouTube post failed: {exc}")
    else:
        print("3/4 Post skipped (AUTO_POST=false). Review the video first.")

    print("4/4 Done.")
    (out_dir / "result.json").write_text(json.dumps(result, indent=2))
    return result
