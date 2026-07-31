from __future__ import annotations

import base64
import io
from pathlib import Path
from urllib.parse import quote

import httpx
from PIL import Image, ImageDraw, ImageFilter

from .config import GEMINI_API_KEY, VIDEO_HEIGHT, VIDEO_WIDTH
from .fonts import get_font
from .props import held_prop
from .script_gen import ReelScript

# Pollinations first (free). Gemini image optional if quota exists.
_GEMINI_IMAGE_MODELS = [
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-lite-image",
    "gemini-3.1-flash-image",
]


def _extract_image_bytes(data: dict) -> bytes | None:
    try:
        parts = data["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError, TypeError):
        return None
    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            return base64.b64decode(inline["data"])
    return None


def _save_original_ratio(img: Image.Image, out_path: Path) -> Path:
    """Save plate photo without stretching — keep native aspect ratio."""
    img = img.convert("RGB")
    # Cap longest side for file size; never distort
    max_side = 1600
    w, h = img.size
    longest = max(w, h)
    if longest > max_side:
        scale = max_side / longest
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
    img.save(out_path, "PNG")
    return out_path


def _pollinations_plate_photo(prompt: str, out_path: Path) -> Path | None:
    """Free photoreal plate via Pollinations.ai (Flux)."""
    full_prompt = (
        f"{prompt}, professional food photography, appetizing, sharp focus, "
        "home kitchen plating, no text, no watermark, no logo, no people"
    )
    encoded = quote(full_prompt, safe="")
    # Prefer natural food-photo ratios (not forced 9:16 stretch)
    urls = [
        (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=1024&height=1024&nologo=true&model=flux&enhance=true"
        ),
        (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=1024&height=1280&nologo=true&model=flux"
        ),
    ]
    last_err = ""
    with httpx.Client(timeout=180, follow_redirects=True) as client:
        for url in urls:
            try:
                resp = client.get(url)
                if resp.status_code >= 400:
                    last_err = f"HTTP {resp.status_code}"
                    continue
                ctype = resp.headers.get("content-type", "")
                is_image = ctype.startswith("image") or resp.content[:2] == b"\xff\xd8" or resp.content[:8].startswith(
                    b"\x89PNG"
                )
                if not is_image:
                    last_err = f"non-image ({ctype})"
                    continue
                img = Image.open(io.BytesIO(resp.content)).convert("RGB")
                _save_original_ratio(img, out_path)
                print(f"   Plate photo: Pollinations.ai (flux) {img.size[0]}x{img.size[1]}")
                return out_path
            except Exception as exc:
                last_err = f"{type(exc).__name__}"
                continue
    print(f"   Pollinations: failed ({last_err})")
    return None


def _gemini_plate_photo(prompt: str, out_path: Path) -> Path | None:
    if not GEMINI_API_KEY:
        return None
    with httpx.Client(timeout=120) as client:
        for model in _GEMINI_IMAGE_MODELS:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model}:generateContent?key={GEMINI_API_KEY}"
            )
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "responseModalities": ["TEXT", "IMAGE"],
                    "imageConfig": {"aspectRatio": "9:16"},
                },
            }
            try:
                resp = client.post(url, json=payload)
                if resp.status_code >= 400:
                    continue
                raw = _extract_image_bytes(resp.json())
                if not raw:
                    continue
                img = Image.open(io.BytesIO(raw)).convert("RGB")
                _save_original_ratio(img, out_path)
                print(f"   Plate photo: Gemini ({model}) {img.size[0]}x{img.size[1]}")
                return out_path
            except Exception:
                continue
    return None


def cartoon_plate_fallback(script: ReelScript, out_path: Path) -> Path:
    """Last-resort stylized plate if all image APIs fail."""
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (40, 55, 50))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(VIDEO_HEIGHT):
        t = y / VIDEO_HEIGHT
        draw.line(
            [(0, y), (VIDEO_WIDTH, y)],
            fill=(int(45 + 40 * t), int(55 + 35 * t), int(48 + 20 * t)),
        )
    cx, cy = VIDEO_WIDTH // 2, VIDEO_HEIGHT // 2 - 80
    plate_r = 420
    shadow = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse(
        (cx - plate_r + 20, cy - plate_r + 40, cx + plate_r + 20, cy + plate_r + 40),
        fill=(0, 0, 0, 90),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.ellipse(
        (cx - plate_r, cy - plate_r, cx + plate_r, cy + plate_r),
        fill=(245, 242, 235),
        outline=(40, 40, 40),
        width=8,
    )
    keys = [ing.get("key", "plate") for ing in (script.ingredients or [])[:4]] or [
        script.item_emoji or "plate"
    ]
    positions = [
        (cx - 160, cy - 140),
        (cx + 40, cy - 100),
        (cx - 100, cy + 40),
        (cx + 80, cy + 60),
    ]
    rgba = img.convert("RGBA")
    for key, (px, py) in zip(keys, positions):
        rgba.alpha_composite(held_prop(key, size=220), (px, py))
    draw = ImageDraw.Draw(rgba)
    title = script.topic or script.item or "Meal"
    bar_y = VIDEO_HEIGHT - 280
    draw.rounded_rectangle(
        (60, bar_y, VIDEO_WIDTH - 60, bar_y + 140),
        radius=28,
        fill=(255, 252, 240, 235),
        outline=(255, 140, 70, 255),
        width=5,
    )
    tw = min(len(title) * 28, VIDEO_WIDTH - 160)
    draw.text(((VIDEO_WIDTH - tw) // 2, bar_y + 40), title[:36], font=get_font(56), fill=(30, 35, 40, 255))
    rgba.convert("RGB").save(out_path, "PNG")
    print(f"   Cartoon plate fallback → {out_path.name}")
    return out_path


def generate_meal_image(script: ReelScript, out_dir: Path) -> Path:
    """Generate plated meal image (Pollinations → Gemini → cartoon)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "plate.png"
    prompt = script.plate_prompt or (
        f"Photoreal plated home-cooked {script.topic}, appetizing kitchen photo"
    )
    result = _pollinations_plate_photo(prompt, out_path)
    if result is not None:
        return result
    result = _gemini_plate_photo(prompt, out_path)
    if result is not None:
        return result
    return cartoon_plate_fallback(script, out_path)
