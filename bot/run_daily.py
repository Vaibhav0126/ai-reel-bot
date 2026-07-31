#!/usr/bin/env python3
"""Generate (and optionally post) today's @nibthefridgegoblin reel."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.instagram import post_reel  # noqa: E402
from src.pipeline import run_daily  # noqa: E402
from src.poses import extract_poses  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Nib daily reel bot")
    parser.add_argument("--extract-poses", action="store_true", help="Only extract pose PNGs")
    parser.add_argument("--post", action="store_true", help="Publish to Instagram after generate")
    parser.add_argument("--no-post", action="store_true", help="Never publish (default)")
    parser.add_argument(
        "--type",
        choices=("fridge", "meal"),
        default="fridge",
        help="Reel type: fridge nutrition (1pm) or meal recipe (7pm). Default: fridge",
    )
    parser.add_argument(
        "--post-file",
        type=Path,
        help="Publish an existing MP4 + sibling caption.txt (skip generate)",
    )
    args = parser.parse_args()

    if args.extract_poses:
        paths = extract_poses()
        print(f"Extracted {len(paths)} poses → bot/assets/nib/poses/")
        return

    if args.post_file:
        video = args.post_file.expanduser().resolve()
        caption_path = video.parent / "caption.txt"
        caption = caption_path.read_text() if caption_path.exists() else ""
        print(f"Posting existing video: {video}")
        resp = post_reel(video, caption)
        print(f"Posted: {resp}")
        return

    post = True if args.post else False
    if args.no_post:
        post = False
    result = run_daily(post=post, reel_type=args.type)
    print("\nReady:")
    print(f"  type:    {result.get('reel_type', args.type)}")
    print(f"  video:   {result['video']}")
    print(f"  caption: {result['output_dir']}/caption.txt")


if __name__ == "__main__":
    main()
