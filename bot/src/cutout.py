from __future__ import annotations

from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image


def cutout_character(im: Image.Image, bg_thresh: float = 38.0) -> Image.Image:
    """
    Remove sheet/cream backgrounds behind Nib.
    Only removes background connected to the image border — keeps white eye sclera.
    """
    rgba = im.convert("RGBA")
    arr = np.array(rgba)
    h, w = arr.shape[:2]
    rgb = arr[:, :, :3].astype(np.float32)

    border = np.concatenate(
        [rgb[0, :, :], rgb[-1, :, :], rgb[:, 0, :], rgb[:, -1, :]],
        axis=0,
    )
    bg = np.median(border, axis=0)
    dist = np.sqrt(((rgb - bg) ** 2).sum(axis=2))

    # Background candidate: close to sheet color OR very cream/off-white near sheet
    is_bg_color = dist < bg_thresh
    cream = (
        (rgb[:, :, 0] > 228)
        & (rgb[:, :, 1] > 222)
        & (rgb[:, :, 2] > 210)
        & (dist < 95)
    )
    candidate = is_bg_color | cream

    # Flood-fill ONLY from edges — interior whites (eyes) stay
    bg_mask = np.zeros((h, w), dtype=bool)
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        for y in (0, h - 1):
            if candidate[y, x]:
                bg_mask[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if candidate[y, x] and not bg_mask[y, x]:
                bg_mask[y, x] = True
                q.append((y, x))

    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and not bg_mask[ny, nx] and candidate[ny, nx]:
                bg_mask[ny, nx] = True
                q.append((ny, nx))

    alpha = np.where(bg_mask, 0, 255).astype(np.uint8)

    # Tiny fringe cleanup: only cream pixels touching actual background
    padded = np.pad(bg_mask, 1, constant_values=False)
    touch_bg = (
        padded[:-2, 1:-1]
        | padded[2:, 1:-1]
        | padded[1:-1, :-2]
        | padded[1:-1, 2:]
    )
    fringe = cream & touch_bg & ~bg_mask
    alpha[fringe] = 0

    out = arr.copy()
    out[:, :, 3] = alpha

    # Restore eye whites if they were punched out: fill small transparent
    # holes fully enclosed by opaque character pixels with white.
    out = _fill_interior_holes_white(out)
    return Image.fromarray(out, "RGBA")


def _fill_interior_holes_white(arr: np.ndarray, max_hole: int = 8000) -> np.ndarray:
    """Fill small fully-enclosed transparent holes with opaque white (eyes)."""
    h, w = arr.shape[:2]
    alpha = arr[:, :, 3]
    transparent = alpha < 40
    visited = np.zeros((h, w), dtype=bool)

    for y in range(h):
        for x in range(w):
            if not transparent[y, x] or visited[y, x]:
                continue
            # flood this transparent component
            stack = [(y, x)]
            visited[y, x] = True
            cells: list[tuple[int, int]] = []
            touches_border = False
            while stack:
                cy, cx = stack.pop()
                cells.append((cy, cx))
                if cy == 0 or cx == 0 or cy == h - 1 or cx == w - 1:
                    touches_border = True
                for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                    if 0 <= ny < h and 0 <= nx < w and transparent[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((ny, nx))
            if touches_border or len(cells) > max_hole or len(cells) < 20:
                continue
            # Interior hole → paint white sclera
            for cy, cx in cells:
                arr[cy, cx, 0] = 255
                arr[cy, cx, 1] = 255
                arr[cy, cx, 2] = 255
                arr[cy, cx, 3] = 255
    return arr


def cutout_file(src: Path, dst: Path | None = None) -> Path:
    dst = dst or src
    im = Image.open(src)
    cut = cutout_character(im)
    bbox = cut.getbbox()
    if bbox:
        cut = cut.crop(bbox)
    dst.parent.mkdir(parents=True, exist_ok=True)
    cut.save(dst)
    return dst
