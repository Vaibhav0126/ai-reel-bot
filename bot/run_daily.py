#!/usr/bin/env python3
"""Generate today's Nib curiosity-fact Short and (optionally) schedule it on YouTube."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.config import PUBLISH_HOUR, PUBLISH_TIMEZONE, REVIEW_WINDOW_HOURS  # noqa: E402
from src.pipeline import run_daily  # noqa: E402
from src.poses import extract_poses  # noqa: E402
from src.scheduling import next_publish_time, to_rfc3339  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Nib daily curiosity-fact Short")
    parser.add_argument("--extract-poses", action="store_true", help="Only extract pose PNGs")
    parser.add_argument(
        "--post",
        action="store_true",
        help="Upload to YouTube as private, scheduled for the next publish slot",
    )
    parser.add_argument(
        "--post-file",
        type=Path,
        help="Schedule an existing MP4 (+ sibling caption.txt) without generating",
    )
    args = parser.parse_args()

    if args.extract_poses:
        paths = extract_poses()
        print(f"Extracted {len(paths)} poses → bot/assets/nib/poses/")
        return

    if args.post_file:
        from src.tts import strip_pause_marks
        from src.youtube import post_short

        video = args.post_file.expanduser().resolve()
        caption_path = video.parent / "caption.txt"
        caption = caption_path.read_text() if caption_path.exists() else ""
        title = (caption.splitlines() or [video.stem])[0].strip()
        title = re.sub(r"\s+", " ", strip_pause_marks(title)).strip()[:90] or video.stem
        publish_at = to_rfc3339(
            next_publish_time(
                datetime.now(timezone.utc), PUBLISH_TIMEZONE, PUBLISH_HOUR, REVIEW_WINDOW_HOURS
            )
        )
        resp = post_short(video, title=f"{title} #Shorts", description=caption, publish_at=publish_at)
        print(f"Scheduled for {publish_at} UTC: {resp.get('url', resp)}")
        return

    result = run_daily(post=args.post)
    print("\nReady:")
    print(f"  video:   {result['video']}")
    print(f"  caption: {result['output_dir']}/caption.txt")
    if result.get("publish_at"):
        print(f"  goes live: {result['publish_at']} UTC (review it in YouTube Studio first)")


if __name__ == "__main__":
    main()
