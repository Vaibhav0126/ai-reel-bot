from __future__ import annotations

import json
from datetime import datetime

from .config import AUTO_POST, OUTPUT_DIR
from .instagram import can_post, post_reel
from .meal_image import generate_meal_image
from .meal_video import render_meal_reel
from .poses import extract_poses, list_poses
from .script_gen import ReelType, generate_script, mark_meal_used, mark_topic_used
from .video import render_reel


def run_daily(post: bool | None = None, reel_type: ReelType = "fridge") -> dict:
    """Generate today's Nib reel (fridge or meal). Optionally publish to Instagram."""
    should_post = AUTO_POST if post is None else post
    reel_type = "meal" if reel_type == "meal" else "fridge"

    poses = list_poses()
    if len(poses) < 5:
        print("Extracting poses from character sheets…")
        extract_poses()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUTPUT_DIR / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"1/4 Writing {reel_type} script…")
    script = generate_script(reel_type=reel_type)
    print(f"   Topic: {script.topic}")

    if reel_type == "meal":
        print("   Generating plated meal image…")
        plate = generate_meal_image(script, out_dir)
        script.meal_image_path = str(plate)

    (out_dir / "script.json").write_text(json.dumps(script.to_dict(), indent=2))
    (out_dir / "caption.txt").write_text(script.caption)

    print("2/4 Rendering video + voice…")
    if reel_type == "meal":
        video_path = render_meal_reel(script, out_dir)
    else:
        video_path = render_reel(script, out_dir)
    print(f"   Video: {video_path}")

    if reel_type == "meal":
        mark_meal_used(script.topic_id)
    else:
        mark_topic_used(script.topic_id)

    result = {
        "output_dir": str(out_dir),
        "video": str(video_path),
        "topic": script.topic,
        "reel_type": reel_type,
        "caption": script.caption,
        "posted": False,
        "publish_response": None,
    }

    if should_post:
        print("3/4 Posting to Instagram…")
        if not can_post():
            print("   Skipped: add INSTAGRAM_USER_ID + INSTAGRAM_ACCESS_TOKEN to bot/.env")
        else:
            resp = post_reel(video_path, script.caption)
            result["posted"] = True
            result["publish_response"] = resp
            print(f"   Posted: {resp}")
    else:
        print("3/4 Post skipped (AUTO_POST=false). Review the video first.")

    print("4/4 Done.")
    (out_dir / "result.json").write_text(json.dumps(result, indent=2))
    return result
