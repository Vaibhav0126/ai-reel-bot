from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from .config import POSES_DIR, RAW_DIR
from .cutout import cutout_character
from .horns import fix_horn_colors


def _content_mask(im: Image.Image) -> np.ndarray:
    arr = np.array(im.convert("RGBA"))
    rgb = arr[:, :, :3].astype(np.int16)
    alpha = arr[:, :, 3]
    whiteness = (rgb[:, :, 0] > 235) & (rgb[:, :, 1] > 235) & (rgb[:, :, 2] > 235)
    return (alpha > 20) & (~whiteness)


def _find_boxes(mask: np.ndarray, min_area: int = 5000) -> list[tuple[int, int, int, int, int]]:
    h, w = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    boxes: list[tuple[int, int, int, int, int]] = []
    for y in range(h):
        for x in range(w):
            if not mask[y, x] or visited[y, x]:
                continue
            stack = [(y, x)]
            visited[y, x] = True
            minx = maxx = x
            miny = maxy = y
            area = 0
            while stack:
                cy, cx = stack.pop()
                area += 1
                minx = min(minx, cx)
                maxx = max(maxx, cx)
                miny = min(miny, cy)
                maxy = max(maxy, cy)
                for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((ny, nx))
            if area >= min_area:
                boxes.append((minx, miny, maxx + 1, maxy + 1, area))
    boxes.sort(key=lambda b: (b[1] // 80, b[0]))
    return boxes


def _trim(im: Image.Image, pad: int = 12) -> Image.Image:
    mask = _content_mask(im)
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return im
    left, right = int(xs.min()), int(xs.max()) + 1
    top, bottom = int(ys.min()), int(ys.max()) + 1
    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(im.width, right + pad)
    bottom = min(im.height, bottom + pad)
    return im.crop((left, top, right, bottom))


def _save_crop(im: Image.Image, box: tuple[int, int, int, int], name: str) -> Path:
    crop = _trim(im.crop(box))
    crop = cutout_character(crop)
    crop = fix_horn_colors(crop)
    bbox = crop.getbbox()
    if bbox:
        crop = crop.crop(bbox)
    out = POSES_DIR / f"{name}.png"
    crop.save(out)
    return out


def extract_poses() -> list[Path]:
    """Crop individual Nib poses from the raw sheets into assets/nib/poses/."""
    POSES_DIR.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    master = Image.open(RAW_DIR / "Nib_master.png")
    saved.append(_save_crop(master, (176, 240, 1252, 1420), "idle"))

    expr = Image.open(RAW_DIR / "Nib_expression.png")
    expr_boxes = [
        ("front", (148, 188, 732, 832)),
        ("side", (1188, 172, 1696, 832)),
        ("three_quarter", (2100, 184, 2680, 832)),
        ("happy", (100, 972, 688, 1420)),
        ("shocked", (776, 956, 1364, 1420)),
        ("judging", (1444, 972, 2028, 1420)),
        ("celebrating", (2068, 976, 2772, 1420)),
    ]
    for name, box in expr_boxes:
        saved.append(_save_crop(expr, box, name))

    talk = Image.open(RAW_DIR / "nib_talk.png")
    talk_names = ["wave", "chew", "bite", "thumbs_up", "laugh", "content", "cheer"]
    talk_boxes = _find_boxes(_content_mask(talk), min_area=180000)
    for name, box in zip(talk_names, talk_boxes[:7]):
        saved.append(_save_crop(talk, box[:4], f"talk_{name}"))

    judge = Image.open(RAW_DIR / "nib_judge.png")
    judge_names = ["bored", "shrug", "think", "approve", "serious", "sincere", "excited"]
    judge_boxes = _find_boxes(_content_mask(judge), min_area=180000)
    for name, box in zip(judge_names, judge_boxes[:7]):
        saved.append(_save_crop(judge, box[:4], f"judge_{name}"))

    return saved


def list_poses() -> dict[str, Path]:
    poses = {p.stem: p for p in sorted(POSES_DIR.glob("*.png"))}
    if len(poses) < 5:
        extract_poses()
        poses = {p.stem: p for p in sorted(POSES_DIR.glob("*.png"))}
    return poses


MOOD_TO_POSES = {
    "hook": ["shocked", "talk_wave", "judge_excited", "talk_cheer"],
    "myth": ["judging", "judge_shrug", "judge_bored", "judge_think"],
    "tip": ["talk_thumbs_up", "front", "idle", "judge_sincere", "three_quarter"],
    "payoff": ["celebrating", "talk_cheer", "happy", "judge_approve", "talk_laugh"],
}


def pick_pose(mood: str, index: int = 0) -> Path:
    poses = list_poses()
    candidates = MOOD_TO_POSES.get(mood, MOOD_TO_POSES["tip"])
    available = [poses[name] for name in candidates if name in poses]
    if not available:
        available = list(poses.values())
    return available[index % len(available)]
