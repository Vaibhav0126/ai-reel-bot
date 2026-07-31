from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

# Canonical Nib horn/hand color (slate blue)
HORN_RGB = np.array([74, 96, 122], dtype=np.float32)


def fix_horn_colors(im: Image.Image) -> Image.Image:
    """
    Recolor mismatched brown horns to Nib's slate-blue horns.
    Leaves yellow sticky note and mint body alone.
    """
    rgba = im.convert("RGBA")
    arr = np.array(rgba)
    h, w = arr.shape[:2]
    rgb = arr[:, :, :3].astype(np.float32)
    alpha = arr[:, :, 3]

    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    # Brown / tan horn pixels (not yellow sticky note, not mint body)
    brown = (
        (alpha > 40)
        & (r > 95)
        & (r < 210)
        & (g < 165)
        & (b < 140)
        & (r > g + 8)
        & (r > b + 15)
        & ~((r > 200) & (g > 175) & (b < 130))  # sticky note yellow
        & ~((g > r + 15) & (g > 140))  # mint body
    )
    # Mostly upper half (horns live on head)
    yy = np.arange(h)[:, None]
    brown &= yy < int(h * 0.55)

    if not brown.any():
        return rgba

    # Preserve shading via luminance remapping onto slate blue
    lum = (0.3 * r + 0.5 * g + 0.2 * b) / 255.0
    target = HORN_RGB[None, None, :]
    shaded = np.clip(target * (0.55 + 0.9 * lum[:, :, None]), 0, 255)
    rgb[brown] = shaded[brown]
    arr[:, :, :3] = rgb.astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def fix_pose_file(path: Path) -> Path:
    im = Image.open(path)
    fixed = fix_horn_colors(im)
    fixed.save(path)
    return path


def fix_all_poses(poses_dir: Path) -> list[Path]:
    fixed: list[Path] = []
    for path in sorted(poses_dir.glob("*.png")):
        fix_pose_file(path)
        fixed.append(path)
    return fixed
