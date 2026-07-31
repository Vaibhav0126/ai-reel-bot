from __future__ import annotations

import math
import subprocess
import threading
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from .config import (
    FPS,
    KITCHEN_BG_PATH,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
)
from .fonts import get_font
from .poses import list_poses
from .props import held_prop
from .script_gen import ReelScript
from .tts import VoiceResult, active_beat_at, align_script_beats, generate_voiceover
from .video import _ken_burns, _load_pose, _speech_bubble

POSE_FOR_BEAT = {
    "hook": "talk_wave",
    "ingredients": "talk_thumbs_up",
    "spices": "judge_excited",
    "cook": "judge_sincere",
    "benefit": "talk_cheer",
    "payoff": "celebrating",
}

# Clear recipe chapters shown on screen
_SECTION = {
    "hook": (0, "TODAY"),
    "ingredients": (1, "YOU NEED"),
    "spices": (2, "SPICES"),
    "cook": (3, "COOK"),
    "benefit": (3, "COOK"),
    "payoff": (4, "DONE"),
}

_MEAL_MAX_DURATION = 75.0


def _kitchen_base() -> Image.Image:
    if KITCHEN_BG_PATH.exists():
        bg = Image.open(KITCHEN_BG_PATH).convert("RGB")
        target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT
        w, h = bg.size
        ratio = w / max(h, 1)
        if ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            bg = bg.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 4
            bg = bg.crop((0, top, w, top + new_h))
        bg = bg.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
        bg = ImageEnhance.Color(bg).enhance(1.08)
        bg = ImageEnhance.Contrast(bg).enhance(1.05)
        return bg
    return _synthetic_kitchen()


def _synthetic_kitchen() -> Image.Image:
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (210, 185, 155))
    d = ImageDraw.Draw(img)
    for y in range(0, 900):
        t = y / 900
        d.line([(0, y), (VIDEO_WIDTH, y)], fill=(int(232 - 20 * t), int(218 - 15 * t), int(195 - 10 * t)))
    d.rectangle((0, 0, VIDEO_WIDTH, 280), fill=(120, 85, 60))
    d.rectangle((0, 280, VIDEO_WIDTH, 560), fill=(245, 240, 230))
    d.rectangle((0, 870, VIDEO_WIDTH, 1100), fill=(92, 68, 52))
    d.rectangle((0, 1100, VIDEO_WIDTH, VIDEO_HEIGHT), fill=(108, 78, 55))
    return img


def _dim_top(frame: Image.Image, bottom: int = 820, alpha: int = 110) -> None:
    """Soft dark panel so checklist text stays readable over kitchen."""
    overlay = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(0, bottom):
        a = int(alpha * (1.0 - y / bottom * 0.35))
        od.line([(0, y), (VIDEO_WIDTH, y)], fill=(20, 24, 28, a))
    frame.alpha_composite(overlay)


def _section_header(frame: Image.Image, beat: str, meal_name: str, mins: int) -> None:
    """Big chapter label so viewers always know where they are."""
    num, label = _SECTION.get(beat, (0, ""))
    draw = ImageDraw.Draw(frame, "RGBA")
    # Progress dots
    total = 4
    dot_y = 56
    gap = 28
    start_x = VIDEO_WIDTH // 2 - ((total - 1) * gap) // 2
    active = max(1, min(4, num if num else 1)) if beat != "hook" else 0
    for i in range(1, total + 1):
        cx = start_x + (i - 1) * gap
        fill = (255, 160, 70, 255) if i <= active else (255, 255, 255, 90)
        draw.ellipse((cx - 7, dot_y - 7, cx + 7, dot_y + 7), fill=fill)

    if beat == "hook":
        return

    # Chapter pill
    font = get_font(42)
    pill = f"{num}  {label}"
    bbox = draw.textbbox((0, 0), pill, font=font)
    tw = bbox[2] - bbox[0]
    x0 = 48
    y0 = 90
    accent = (255, 140, 60, 255) if beat != "spices" else (255, 100, 80, 255)
    if beat == "payoff":
        accent = (80, 190, 120, 255)
    draw.rounded_rectangle(
        (x0, y0, x0 + tw + 56, y0 + 70),
        radius=22,
        fill=(255, 252, 240, 240),
        outline=accent,
        width=5,
    )
    draw.text((x0 + 28, y0 + 14), pill, font=font, fill=(30, 35, 40, 255))

    # Tiny meal name under pill
    small = get_font(28)
    draw.text((x0 + 4, y0 + 82), f"{meal_name[:32]} · {mins} min", font=small, fill=(255, 252, 240, 220))


def _checklist_panel(
    frame: Image.Image,
    items: list[dict],
    t: float,
    beat_start: float,
    *,
    accent: tuple[int, int, int, int] = (255, 150, 70, 255),
) -> None:
    """Reveal a clear checklist one row at a time (much easier to follow than flying props)."""
    if not items:
        return
    draw = ImageDraw.Draw(frame, "RGBA")
    font = get_font(36)
    amount_font = get_font(28)
    # Show at most 6 rows so it stays readable
    rows = items[:6]
    stagger = 0.45
    panel_x = 40
    panel_y = 220
    row_h = 88
    panel_h = 40 + row_h * len(rows)
    draw.rounded_rectangle(
        (panel_x, panel_y, VIDEO_WIDTH - 40, panel_y + panel_h),
        radius=28,
        fill=(255, 252, 245, 235),
        outline=accent,
        width=4,
    )

    for i, item in enumerate(rows):
        appear = beat_start + 0.15 + i * stagger
        local = min(1.0, max(0.0, (t - appear) / 0.3))
        if local <= 0:
            continue
        y = panel_y + 24 + i * row_h
        # Slide in from left
        x_off = int(40 * (1.0 - local))
        alpha = int(255 * local)

        # Checkbox
        box = (panel_x + 28 + x_off, y + 18, panel_x + 62 + x_off, y + 52)
        draw.rounded_rectangle(box, radius=8, outline=accent[:3] + (alpha,), width=4)
        if local > 0.7:
            draw.line(
                [(box[0] + 8, y + 35), (box[0] + 14, y + 44), (box[0] + 28, y + 24)],
                fill=(80, 180, 100, alpha),
                width=5,
            )

        # Mini prop icon
        key = item.get("key") or "box"
        try:
            icon = held_prop(key, size=72)
            icon = icon.resize((64, 64), Image.Resampling.BILINEAR)
            if local < 0.99:
                import numpy as np

                a = np.array(icon)
                a[:, :, 3] = (a[:, :, 3].astype(np.float32) * local).astype(np.uint8)
                icon = Image.fromarray(a, "RGBA")
            frame.alpha_composite(icon, (panel_x + 78 + x_off, y + 6))
        except Exception:
            pass

        label = (item.get("label") or key)[:22]
        amount = (item.get("amount") or "")[:28]
        draw.text(
            (panel_x + 160 + x_off, y + 8),
            label,
            font=font,
            fill=(30, 35, 40, alpha),
        )
        if amount:
            draw.text(
                (panel_x + 160 + x_off, y + 48),
                amount,
                font=amount_font,
                fill=(100, 80, 60, alpha),
            )


def _cook_step_card(
    frame: Image.Image,
    steps: list[str],
    t: float,
    cook_start: float,
    cook_end: float,
) -> None:
    """Show one big numbered step at a time during the cook section."""
    if not steps:
        return
    span = max(cook_end - cook_start, 0.5)
    # Leave a little lead-in, then divide remaining time across steps
    local_t = max(0.0, t - cook_start - 0.2)
    usable = max(span - 0.4, 0.5)
    idx = min(len(steps) - 1, int(local_t / usable * len(steps)))
    idx = max(0, idx)
    step = steps[idx]
    draw = ImageDraw.Draw(frame, "RGBA")

    # Big number circle
    nfont = get_font(72)
    sfont = get_font(40)
    hint = get_font(28)
    card_y = 210
    draw.rounded_rectangle(
        (40, card_y, VIDEO_WIDTH - 40, card_y + 420),
        radius=32,
        fill=(255, 252, 245, 240),
        outline=(255, 140, 70, 255),
        width=5,
    )
    draw.ellipse((70, card_y + 40, 190, card_y + 160), fill=(255, 140, 70, 255))
    num = str(idx + 1)
    nb = draw.textbbox((0, 0), num, font=nfont)
    nw = nb[2] - nb[0]
    draw.text((130 - nw // 2, card_y + 58), num, font=nfont, fill=(255, 255, 255, 255))

    draw.text((220, card_y + 70), f"Step {idx + 1} of {len(steps)}", font=hint, fill=(120, 90, 60, 255))

    # Wrap step text
    words = step.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) > 28:
            if cur:
                lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    lines = lines[:5]
    for i, ln in enumerate(lines):
        draw.text((70, card_y + 190 + i * 48), ln, font=sfont, fill=(30, 35, 40, 255))

    # Step progress bar
    bar_x0, bar_x1 = 70, VIDEO_WIDTH - 70
    bar_y = card_y + 380
    draw.rounded_rectangle((bar_x0, bar_y, bar_x1, bar_y + 14), radius=7, fill=(230, 220, 210, 255))
    fill_w = int((bar_x1 - bar_x0) * ((idx + 1) / len(steps)))
    draw.rounded_rectangle((bar_x0, bar_y, bar_x0 + max(14, fill_w), bar_y + 14), radius=7, fill=(255, 140, 70, 255))


def _benefit_card(frame: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    font = get_font(40)
    draw.rounded_rectangle(
        (40, 220, VIDEO_WIDTH - 40, 520),
        radius=32,
        fill=(255, 252, 245, 240),
        outline=(80, 180, 120, 255),
        width=5,
    )
    draw.text((70, 250), "Why it works", font=get_font(32), fill=(80, 140, 90, 255))
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) > 26:
            if cur:
                lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    for i, ln in enumerate(lines[:4]):
        draw.text((70, 310 + i * 48), ln, font=font, fill=(30, 35, 40, 255))


def _plate_payoff_frame(plate: Image.Image, progress: float) -> Image.Image:
    """
    Show the plated meal at its original aspect ratio (no stretch).
    Blurred cover fill behind + contained photo centered with a gentle zoom.
    """
    # Soft blurred background (cover-crop is OK here — it's only bokeh fill)
    bg = plate.copy()
    bw, bh = bg.size
    target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT
    ratio = bw / max(bh, 1)
    if ratio > target_ratio:
        new_w = int(bh * target_ratio)
        left = (bw - new_w) // 2
        bg = bg.crop((left, 0, left + new_w, bh))
    else:
        new_h = int(bw / target_ratio)
        top = max(0, (bh - new_h) // 3)
        bg = bg.crop((0, top, bw, min(bh, top + new_h)))
    bg = bg.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(36))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    frame = bg.convert("RGBA")

    # Foreground: contain — never distort width/height independently
    pad = 0.88  # leave margin for UI
    zoom = 1.0 + 0.05 * progress  # gentle Ken Burns zoom, aspect locked
    fit = min(VIDEO_WIDTH / plate.width, VIDEO_HEIGHT / plate.height) * pad * zoom
    nw = max(1, int(plate.width * fit))
    nh = max(1, int(plate.height * fit))
    fg = plate.resize((nw, nh), Image.Resampling.LANCZOS).convert("RGBA")

    # Soft shadow under the photo
    shadow = Image.new("RGBA", (nw + 40, nh + 40), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((10, 10, nw + 30, nh + 30), radius=28, fill=(0, 0, 0, 100))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    x = (VIDEO_WIDTH - nw) // 2
    y = (VIDEO_HEIGHT - nh) // 2 - 40  # slightly high so bottom CTA fits
    frame.alpha_composite(shadow, (x - 20, y - 10))

    # Rounded mask so it feels like a photo card, still unstretched
    mask = Image.new("L", (nw, nh), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, nw, nh), radius=28, fill=255)
    rounded = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
    rounded.paste(fg, (0, 0))
    rounded.putalpha(mask)
    frame.alpha_composite(rounded, (x, y))
    return frame


def _hook_card(frame: Image.Image, title: str, mins: int) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    draw.rounded_rectangle(
        (40, 120, VIDEO_WIDTH - 40, 380),
        radius=32,
        fill=(255, 252, 245, 240),
        outline=(255, 140, 70, 255),
        width=6,
    )
    draw.text((70, 150), "QUICK MEAL", font=get_font(32), fill=(255, 120, 50, 255))
    # Title wrap
    font = get_font(52)
    words = title.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) > 18:
            if cur:
                lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    for i, ln in enumerate(lines[:2]):
        draw.text((70, 210 + i * 60), ln, font=font, fill=(30, 35, 40, 255))
    draw.text((70, 320), f"~{mins} min  ·  follow the steps", font=get_font(34), fill=(90, 70, 50, 255))


def _place_nib(
    frame: Image.Image,
    nib: Image.Image,
    t: float,
    punch: float,
    *,
    scale: float = 0.72,
    side: str = "right",
) -> None:
    bounce = int(5 * math.sin(t * 2 * math.pi * 1.1))
    s = scale * (1.0 + 0.03 * punch)
    nib_r = nib.resize(
        (max(1, int(nib.width * s)), max(1, int(nib.height * s))),
        Image.Resampling.BILINEAR,
    )
    if side == "right":
        nx = VIDEO_WIDTH - nib_r.width - 10
    else:
        nx = (VIDEO_WIDTH - nib_r.width) // 2
    ny = VIDEO_HEIGHT - nib_r.height - 20 + bounce
    ny = max(900, min(VIDEO_HEIGHT - nib_r.height - 8, ny))
    shadow = Image.new("RGBA", (nib_r.width, 50), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse((15, 8, nib_r.width - 15, 42), fill=(0, 0, 0, 80))
    shadow = shadow.filter(ImageFilter.GaussianBlur(7))
    frame.alpha_composite(shadow, (nx, ny + nib_r.height - 36))
    frame.alpha_composite(nib_r, (nx, ny))


def render_meal_reel(script: ReelScript, out_dir: Path) -> Path:
    """Kitchen meal reel with clear recipe chapters (less confusing, more engaging)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_path = out_dir / "voice.mp3"
    final_path = out_dir / "reel.mp4"

    voice: VoiceResult = generate_voiceover(script.voiceover, audio_path)
    duration = max(20.0, min(voice.duration + 0.5, _MEAL_MAX_DURATION))

    timeline = align_script_beats(
        [
            ("hook", script.hook),
            ("ingredients", script.discover),
            ("spices", script.extra),
            ("cook", script.react),
            ("benefit", script.benefit),
            ("payoff", script.payoff),
        ],
        voice.words,
        duration,
    )
    ingredients_start = next((s for n, _, s, _ in timeline if n == "ingredients"), duration * 0.12)
    spices_start = next((s for n, _, s, _ in timeline if n == "spices"), duration * 0.28)
    cook_start = next((s for n, _, s, _ in timeline if n == "cook"), duration * 0.45)
    # Cook steps span cook + benefit so numbered cards have enough time
    cook_end = next((e for n, _, _, e in timeline if n == "benefit"), duration * 0.85)
    benefit_start = next((s for n, _, s, _ in timeline if n == "benefit"), cook_end)

    print("   Meal caption sync beats:")
    for name, text, start, end in timeline:
        print(f"     {start:5.2f}-{end:5.2f}s  [{name}] {text[:48]}")

    poses = list_poses()
    pose_cache = {
        name: _load_pose(path, max_h=900)
        for name, path in poses.items()
        if name != "fridge"
    }
    if not pose_cache:
        pose_cache = {name: _load_pose(path) for name, path in poses.items()}

    kitchen = _kitchen_base()
    plate_path = Path(script.meal_image_path) if script.meal_image_path else None
    plate_img: Image.Image | None = None
    if plate_path and plate_path.exists():
        # Keep original aspect ratio — never stretch to 9:16
        plate_img = Image.open(plate_path).convert("RGB")
        print(f"   Plate aspect preserved: {plate_img.size[0]}x{plate_img.size[1]}")

    small_nib = None
    for name in ("celebrating", "talk_cheer", "happy", "idle"):
        if name in pose_cache:
            small_nib = pose_cache[name].copy()
            small_nib = small_nib.resize(
                (max(1, small_nib.width // 2), max(1, small_nib.height // 2)),
                Image.Resampling.LANCZOS,
            )
            break

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{VIDEO_WIDTH}x{VIDEO_HEIGHT}", "-r", str(FPS),
        "-i", "-",
        "-i", str(audio_path),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-profile:v", "main", "-level", "4.0",
        "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
        "-t", f"{duration:.3f}",
        "-movflags", "+faststart",
        str(final_path),
    ]
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        bufsize=10**8,
    )
    assert proc.stdin is not None
    stderr_chunks: list[bytes] = []

    def _drain() -> None:
        assert proc.stderr is not None
        while True:
            chunk = proc.stderr.read(4096)
            if not chunk:
                break
            stderr_chunks.append(chunk)

    drain = threading.Thread(target=_drain, daemon=True)
    drain.start()

    total_frames = int(duration * FPS)
    punch = 0.0
    last_beat = ""
    mins = script.time_mins or 15
    steps = list(script.steps or [])

    try:
        for i in range(total_frames):
            t = i / FPS
            progress = t / duration
            beat, bubble = active_beat_at(timeline, t)
            if beat != last_beat:
                punch = 1.0
                last_beat = beat
            punch *= 0.9

            preferred = POSE_FOR_BEAT.get(beat, "idle")
            pose_name = preferred if preferred in pose_cache else (
                "idle" if "idle" in pose_cache else next(iter(pose_cache))
            )
            nib = pose_cache[pose_name]

            if beat == "payoff" and plate_img is not None:
                frame = _plate_payoff_frame(plate_img, progress)
                overlay = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
                od = ImageDraw.Draw(overlay)
                for y in range(VIDEO_HEIGHT - 420, VIDEO_HEIGHT):
                    a = int(160 * ((y - (VIDEO_HEIGHT - 420)) / 420))
                    od.line([(0, y), (VIDEO_WIDTH, y)], fill=(0, 0, 0, a))
                frame = Image.alpha_composite(frame, overlay)
                _section_header(frame, beat, script.topic, mins)
                draw = ImageDraw.Draw(frame, "RGBA")
                draw.rounded_rectangle(
                    (40, VIDEO_HEIGHT - 360, VIDEO_WIDTH - 40, VIDEO_HEIGHT - 160),
                    radius=28,
                    fill=(255, 252, 245, 240),
                    outline=(80, 190, 120, 255),
                    width=5,
                )
                draw.text((70, VIDEO_HEIGHT - 330), script.topic[:30], font=get_font(44), fill=(30, 35, 40, 255))
                draw.text(
                    (70, VIDEO_HEIGHT - 260),
                    f"~{mins} min · full recipe in caption",
                    font=get_font(34),
                    fill=(70, 100, 70, 255),
                )
                draw.text(
                    (70, VIDEO_HEIGHT - 210),
                    "SAVE this · spices + steps below",
                    font=get_font(32),
                    fill=(255, 120, 50, 255),
                )
                if small_nib is not None:
                    bounce = int(4 * math.sin(t * 2 * math.pi * 1.2))
                    nx = VIDEO_WIDTH - small_nib.width - 20
                    ny = VIDEO_HEIGHT - small_nib.height - 20 + bounce
                    frame.alpha_composite(small_nib, (nx, ny))
            else:
                frame = _ken_burns(kitchen, progress).convert("RGBA")

                if beat in {"ingredients", "spices", "cook", "benefit"}:
                    _dim_top(frame, bottom=860, alpha=120)

                _section_header(frame, beat, script.topic, mins)

                if beat == "hook":
                    _hook_card(frame, script.topic, mins)
                    _place_nib(frame, nib, t, punch, scale=0.85, side="center")
                    # Short bubble only on hook
                    short = bubble
                    if short and len(short) > 70:
                        short = short[:67] + "…"
                    _speech_bubble(frame, short, VIDEO_WIDTH // 2 + 80, 420)

                elif beat == "ingredients":
                    _checklist_panel(
                        frame,
                        script.ingredients,
                        t,
                        ingredients_start,
                        accent=(255, 150, 70, 255),
                    )
                    _place_nib(frame, nib, t, punch, scale=0.62, side="right")

                elif beat == "spices":
                    spice_items = script.spices or [{"key": "spices", "label": "Spices", "amount": "see caption"}]
                    _checklist_panel(
                        frame,
                        spice_items,
                        t,
                        spices_start,
                        accent=(255, 100, 80, 255),
                    )
                    _place_nib(frame, nib, t, punch, scale=0.62, side="right")

                elif beat == "cook":
                    _cook_step_card(frame, steps, t, cook_start, cook_end)
                    _place_nib(frame, nib, t, punch, scale=0.58, side="right")

                elif beat == "benefit":
                    # Finish last cook steps, then show why-it-works card
                    benefit_span = max(cook_end - benefit_start, 0.3)
                    if t < benefit_start + benefit_span * 0.4 and steps:
                        _cook_step_card(frame, steps, t, cook_start, cook_end)
                    else:
                        _benefit_card(frame, script.benefit)
                    _place_nib(frame, nib, t, punch, scale=0.58, side="right")

                else:
                    _place_nib(frame, nib, t, punch, scale=0.8, side="center")
                    _speech_bubble(frame, bubble, VIDEO_WIDTH // 2, 400)

            rgb = frame.convert("RGB")
            try:
                proc.stdin.write(rgb.tobytes())
            except BrokenPipeError:
                err = b"".join(stderr_chunks).decode("utf-8", errors="ignore")
                raise RuntimeError(f"ffmpeg pipe closed early:\n{err[-2000:]}") from None
            if i % (FPS * 4) == 0:
                print(f"  animating {i}/{total_frames} [{beat}]")

        proc.stdin.close()
        drain.join(timeout=30)
        code = proc.wait(timeout=120)
    except RuntimeError:
        try:
            proc.stdin.close()
        except Exception:
            pass
        proc.kill()
        drain.join(timeout=5)
        raise
    except Exception as exc:
        try:
            proc.stdin.close()
        except Exception:
            pass
        proc.kill()
        drain.join(timeout=5)
        err = b"".join(stderr_chunks).decode("utf-8", errors="ignore")
        raise RuntimeError(f"meal render failed: {exc}\n{err[-2000:]}") from None

    err = b"".join(stderr_chunks).decode("utf-8", errors="ignore")
    if code != 0 or not final_path.exists():
        raise RuntimeError(f"ffmpeg encode failed:\n{err[-2000:]}")
    return final_path
