from __future__ import annotations

import base64
import io
import re
from pathlib import Path
from urllib.parse import quote

import httpx
from PIL import Image, ImageDraw, ImageEnhance

from .config import CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN
from .cutout import cutout_object
from .script_gen import ReelScript

_CF_MODEL = "@cf/black-forest-labs/flux-1-schnell"

_STYLE = (
    "isolated sticker of one large clear object, centered, "
    "children's book illustration, bold saturated colors, thick clean outlines, "
    "sharp focus, high contrast, plain solid white background, "
    "no frame, no square, no border, no card, no collage, no blur, "
    "no text, no letters, no numbers, no watermark, no logo, no mascot, no people"
)


def _enrich_prompt(prompt: str, caption: str, spoken: str) -> str:
    subject = (prompt or "").strip().rstrip(".")
    caption = (caption or "").strip()
    spoken = re.sub(r"\[pause(?::\w+)?\]", " ", spoken or "")
    spoken = re.sub(r"\s+", " ", spoken).strip()
    gist = spoken[:120]
    bits = [p for p in (subject, caption, gist) if p]
    unique: list[str] = []
    for bit in bits:
        if bit.lower() not in {u.lower() for u in unique}:
            unique.append(bit)
    scene = ". ".join(unique[:2]) or "a curious science object"
    return f"{scene}. {_STYLE}"


def _boost_clarity(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Color(img).enhance(1.18)
    img = ImageEnhance.Contrast(img).enhance(1.12)
    img = ImageEnhance.Sharpness(img).enhance(1.25)
    return img


def _to_object_png(img: Image.Image, out_path: Path) -> Path:
    """Crop to the subject with a transparent backdrop."""
    rgb = img.convert("RGB")
    side = 1024
    w, h = rgb.size
    if w != h:
        crop = min(w, h)
        left = (w - crop) // 2
        top = (h - crop) // 2
        rgb = rgb.crop((left, top, left + crop, top + crop))
    rgb = rgb.resize((side, side), Image.Resampling.LANCZOS)
    rgb = _boost_clarity(rgb)

    cut = cutout_object(rgb)
    bbox = cut.getbbox()
    opaque = 0
    if bbox:
        hist = cut.getchannel("A").histogram()
        opaque = sum(hist[21:])
    if not bbox or opaque < (side * side * 0.08):
        rgb.convert("RGBA").save(out_path, "PNG")
        return out_path

    cut = cut.crop(bbox)
    pad = 28
    canvas = Image.new("RGBA", (cut.width + pad * 2, cut.height + pad * 2), (0, 0, 0, 0))
    canvas.paste(cut, (pad, pad), cut)
    canvas.save(out_path, "PNG")
    return out_path


def _cloudflare_cartoon(prompt: str, out_path: Path) -> Path | None:
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        return None
    url = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{CLOUDFLARE_ACCOUNT_ID}/ai/run/{_CF_MODEL}"
    )
    payload = {
        "prompt": prompt[:2048],
        "steps": 8,
    }
    try:
        with httpx.Client(timeout=90) as client:
            resp = client.post(
                url,
                headers={
                    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        if resp.status_code >= 400:
            print(f"   Cloudflare: HTTP {resp.status_code} {resp.text[:180]}")
            return None
        data = resp.json()
        b64 = (data.get("result") or {}).get("image")
        if not b64:
            print("   Cloudflare: no image in response")
            return None
        raw = base64.b64decode(b64)
        img = Image.open(io.BytesIO(raw))
        _to_object_png(img, out_path)
        print(f"   Image: Cloudflare Flux → {out_path.name}")
        return out_path
    except Exception as exc:
        print(f"   Cloudflare: failed ({type(exc).__name__})")
        return None


def _pollinations_cartoon(prompt: str, out_path: Path) -> Path | None:
    encoded = quote(prompt, safe="")
    urls = [
        (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=1024&height=1024&nologo=true&model=flux&enhance=true"
        ),
        (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=1024&height=1024&nologo=true&model=flux"
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
                is_image = (
                    ctype.startswith("image")
                    or resp.content[:2] == b"\xff\xd8"
                    or resp.content[:8].startswith(b"\x89PNG")
                )
                if not is_image:
                    last_err = f"non-image ({ctype})"
                    continue
                img = Image.open(io.BytesIO(resp.content)).convert("RGB")
                _to_object_png(img, out_path)
                print(f"   Fact art: Pollinations → {out_path.name}")
                return out_path
            except Exception as exc:
                last_err = f"{type(exc).__name__}"
                continue
    print(f"   Pollinations: failed ({last_err})")
    return None


def cartoon_shape_fallback(prompt: str, out_path: Path, index: int, caption: str = "") -> Path:
    """Simple isolated shape on transparent pixels — no card."""
    palettes = [
        (255, 214, 74),
        (120, 210, 180),
        (255, 160, 120),
        (160, 180, 255),
        (255, 120, 160),
    ]
    fill = palettes[index % len(palettes)]
    img = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((160, 160, 864, 864), fill=fill + (255,), outline=(28, 28, 40, 255), width=18)
    draw.ellipse((340, 300, 520, 480), fill=(28, 28, 40, 255))
    img.save(out_path, "PNG")
    print(f"   Fact art fallback → {out_path.name} ({(caption or prompt)[:40]})")
    return out_path


def generate_one_beat_image(
    prompt: str,
    out_path: Path,
    index: int,
    caption: str = "",
    spoken: str = "",
) -> Path:
    full = _enrich_prompt(prompt, caption, spoken)
    result = _cloudflare_cartoon(full, out_path)
    if result is not None:
        return result
    result = _pollinations_cartoon(full, out_path)
    if result is not None:
        return result
    return cartoon_shape_fallback(prompt, out_path, index, caption)


def generate_fact_images(script: ReelScript, out_dir: Path) -> list[Path]:
    """Generate one isolated cartoon object per script beat."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    beats = script.beats or []
    for i, beat in enumerate(beats):
        prompt = str(beat.get("image_prompt") or script.topic or "curious fact icon")
        caption = str(beat.get("caption") or "")
        spoken = str(beat.get("spoken") or "")
        out_path = out_dir / f"beat_{i}.png"
        paths.append(generate_one_beat_image(prompt, out_path, i, caption, spoken))
    script.beat_image_paths = [str(p) for p in paths]
    return paths
