from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

from .config import BOT_ROOT

_BUNDLED = BOT_ROOT / "assets" / "fonts" / "Roboto-Bold.ttf"

_FALLBACKS = (
    _BUNDLED,
    Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    Path("/Library/Fonts/Arial Bold.ttf"),
    Path("/System/Library/Fonts/Supplemental/Impact.ttf"),
    Path("/System/Library/Fonts/Helvetica.ttc"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"),
)


@lru_cache(maxsize=16)
def get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Bold sans used for speech bubbles / prop labels (bundled for CI)."""
    for path in _FALLBACKS:
        try:
            return ImageFont.truetype(str(path), size=size)
        except OSError:
            continue
    return ImageFont.load_default()
