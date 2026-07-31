from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .config import AUTO_POST, OUTPUT_DIR
from .instagram import can_post, post_reel
from .poses import extract_poses, list_poses
from .script_gen import generate_script, mark_topic_used
from .video import render_reel


def run_daily(post: bool | None = None) -> dict:
    """Generate today's Nib reel. Optionally publish to Instagram."""
    should_post = AUTO_POST if post is None else post

    poses = list_poses()
    if len(poses) < 5:
        print("Extracting poses from character sheets…")
        extract_poses()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUTPUT_DIR / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    print("1/4 Writing script…")
    script = generate_script()
    (out_dir / "script.json").write_text(json.dumps(script.to_dict(), indent=2))
    (out_dir / "caption.txt").write_text(script.caption)

    print(f"   Topic: {script.topic}")
    print("2/4 Rendering video + voice…")
    video_path = render_reel(script, out_dir)
    print(f"   Video: {video_path}")

    mark_topic_used(script.topic_id)

    result = {
        "output_dir": str(out_dir),
        "video": str(video_path),
        "topic": script.topic,
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
