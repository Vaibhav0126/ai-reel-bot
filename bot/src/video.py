from __future__ import annotations

import math
import subprocess
import threading
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from .config import (
    CAPTION_STROKE,
    FPS,
    FRIDGE_BG_PATH,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
)
from .fonts import get_font
from .horns import fix_horn_colors
from .poses import list_poses
from .props import held_prop
from .script_gen import ReelScript
from .tts import VoiceResult, active_beat_at, align_script_beats, generate_voiceover

# One stable pose per beat (no rapid cycling)
POSE_FOR_BEAT = {
    "hook": "judge_think",
    "find": "shocked",
    "react": "talk_thumbs_up",
    "fact": "talk_wave",
    "extra": "judge_sincere",
    "payoff": "celebrating",
}


def _load_pose(path: Path, max_h: int = 900) -> Image.Image:
    from .cutout import cutout_character

    nib = cutout_character(Image.open(path).convert("RGBA"))
    nib = fix_horn_colors(nib)
    bbox = nib.getbbox()
    if bbox:
        nib = nib.crop(bbox)
    ratio = max_h / max(nib.height, 1)
    w = max(1, int(nib.width * ratio))
    h = max(1, int(nib.height * ratio))
    if w > VIDEO_WIDTH - 40:
        ratio = (VIDEO_WIDTH - 40) / max(nib.width, 1)
        w = max(1, int(nib.width * ratio))
        h = max(1, int(nib.height * ratio))
    return nib.resize((w, h), Image.Resampling.LANCZOS)


def _fridge_base() -> Image.Image:
    if not FRIDGE_BG_PATH.exists():
        return Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (30, 90, 110))
    bg = Image.open(FRIDGE_BG_PATH).convert("RGB")
    target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT
    w, h = bg.size
    ratio = w / h
    if ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        bg = bg.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 5
        bg = bg.crop((0, top, w, top + new_h))
    bg = bg.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
    bg = ImageEnhance.Color(bg).enhance(1.12)
    bg = ImageEnhance.Contrast(bg).enhance(1.06)
    return bg


def _ken_burns(base: Image.Image, progress: float) -> Image.Image:
    scale = 1.0 + 0.05 * progress
    w = int(VIDEO_WIDTH * scale)
    h = int(VIDEO_HEIGHT * scale)
    framed = base.resize((w, h), Image.Resampling.BILINEAR)
    max_x = w - VIDEO_WIDTH
    max_y = h - VIDEO_HEIGHT
    x = int(max_x * (0.4 + 0.2 * math.sin(progress * math.pi)))
    y = int(max_y * (0.3 + 0.15 * progress))
    return framed.crop((x, y, x + VIDEO_WIDTH, y + VIDEO_HEIGHT))


def _speech_bubble(frame: Image.Image, text: str, anchor_x: int, anchor_y: int) -> None:
    if not text:
        return
    draw = ImageDraw.Draw(frame, "RGBA")
    font = get_font(44)
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) > 22:
            if cur:
                lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    lines = lines[:4]
    line_h = 52
    pad_x, pad_y = 26, 20
    tw = max(draw.textbbox((0, 0), ln, font=font)[2] for ln in lines)
    th = line_h * len(lines)
    bw = tw + pad_x * 2
    bh = th + pad_y * 2
    x = max(30, min(anchor_x, VIDEO_WIDTH - bw - 30))
    y = max(40, min(anchor_y, VIDEO_HEIGHT - bh - 300))

    draw.rounded_rectangle((x + 6, y + 8, x + bw + 6, y + bh + 8), radius=26, fill=(0, 0, 0, 90))
    draw.rounded_rectangle((x, y, x + bw, y + bh), radius=26, fill=(255, 252, 245, 245))
    draw.rounded_rectangle((x, y, x + bw, y + bh), radius=26, outline=(255, 180, 70, 255), width=4)
    tail_x = x + min(90, bw // 3)
    draw.polygon(
        [(tail_x, y + bh - 2), (tail_x + 34, y + bh - 2), (tail_x + 10, y + bh + 34)],
        fill=(255, 252, 245, 245),
    )
    for i, ln in enumerate(lines):
        draw.text((x + pad_x, y + pad_y + i * line_h), ln, font=font, fill=CAPTION_STROKE)


def _hand_anchor(pose_name: str, nib_w: int, nib_h: int) -> tuple[int, int]:
    """Approximate hand position relative to Nib top-left for prop placement."""
    # fractions of nib box → (x, y) offsets for prop center
    anchors = {
        "talk_thumbs_up": (0.82, 0.42),
        "talk_wave": (0.85, 0.35),
        "celebrating": (0.78, 0.22),
        "shocked": (0.75, 0.45),
        "judge_excited": (0.80, 0.30),
        "judge_approve": (0.78, 0.40),
        "happy": (0.72, 0.48),
        "talk_cheer": (0.80, 0.25),
    }
    fx, fy = anchors.get(pose_name, (0.78, 0.40))
    return int(nib_w * fx), int(nib_h * fy)


def render_reel(script: ReelScript, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_path = out_dir / "voice.mp3"
    final_path = out_dir / "reel.mp4"

    voice: VoiceResult = generate_voiceover(script.voiceover, audio_path)
    # Follow full voiceover — old 22s cap cut off the last words
    duration = max(14.0, min(voice.duration + 0.4, 45.0))

    # Sync bubbles/poses to real speech times (fixes late captions)
    timeline = align_script_beats(
        [
            ("hook", script.hook),
            ("find", script.discover),
            ("react", script.react),
            ("fact", script.benefit),
            ("extra", script.extra),
            ("payoff", script.payoff),
        ],
        voice.words,
        duration,
    )
    find_start = next((s for name, _, s, _ in timeline if name == "find"), duration * 0.2)
    print("   Caption sync beats:")
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

    fridge = _fridge_base()
    prop = held_prop(script.item_emoji, size=280)

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{VIDEO_WIDTH}x{VIDEO_HEIGHT}", "-r", str(FPS),
        "-i", "-",
        "-i", str(audio_path),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-profile:v", "main", "-level", "4.0",
        # Instagram rejects many edge-tts rates (24 kHz); Reels expect AAC @ 48 kHz
        "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
        # Keep full audio; -shortest would still risk cutting if video frames lag
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

    try:
        for i in range(total_frames):
            t = i / FPS
            progress = t / duration
            beat, bubble = active_beat_at(timeline, t)
            if beat != last_beat:
                punch = 1.0
                last_beat = beat
            punch *= 0.9

            frame = _ken_burns(fridge, progress).convert("RGBA")

            preferred = POSE_FOR_BEAT.get(beat, "idle")
            pose_name = preferred if preferred in pose_cache else (
                "idle" if "idle" in pose_cache else next(iter(pose_cache))
            )
            show_prop = beat != "hook"

            nib = pose_cache[pose_name]
            # Gentle bob only — no frantic shake
            bounce = int(6 * math.sin(t * 2 * math.pi * 1.1))
            scale = 1.0 + 0.04 * punch
            sway = int(4 * math.sin(t * 2 * math.pi * 0.35))
            nib_r = nib.resize(
                (max(1, int(nib.width * scale)), max(1, int(nib.height * scale))),
                Image.Resampling.BILINEAR,
            )

            shadow = Image.new("RGBA", (nib_r.width, 60), (0, 0, 0, 0))
            sd = ImageDraw.Draw(shadow)
            sd.ellipse((20, 10, nib_r.width - 20, 50), fill=(0, 0, 0, 90))
            shadow = shadow.filter(ImageFilter.GaussianBlur(8))

            nx = (VIDEO_WIDTH - nib_r.width) // 2 + sway
            ny = VIDEO_HEIGHT - nib_r.height - 36 + bounce
            nx = max(10, min(VIDEO_WIDTH - nib_r.width - 10, nx))
            ny = max(350, min(VIDEO_HEIGHT - nib_r.height - 10, ny))

            frame.alpha_composite(shadow, (nx, ny + nib_r.height - 45))
            frame.alpha_composite(nib_r, (nx, ny))

            if show_prop:
                local = 1.0
                if beat == "find":
                    local = min(1.0, max(0.0, (t - find_start) / 0.25))
                pop = 0.75 + 0.25 * local + 0.04 * math.sin(t * 3)
                pw = max(1, int(prop.width * pop))
                ph = max(1, int(prop.height * pop))
                prop_r = prop.resize((pw, ph), Image.Resampling.BILINEAR)
                if local < 0.99:
                    import numpy as np

                    a = np.array(prop_r)
                    a[:, :, 3] = (a[:, :, 3].astype(np.float32) * local).astype(np.uint8)
                    prop_r = Image.fromarray(a, "RGBA")

                hx, hy = _hand_anchor(pose_name, nib_r.width, nib_r.height)
                px = nx + int(nib_r.width * 0.62)
                py = ny + int(nib_r.height * 0.28) + int(6 * math.sin(t * 2.2))
                if pose_name in {"talk_thumbs_up", "celebrating", "talk_wave", "judge_approve"}:
                    px = nx + hx - prop_r.width // 4
                    py = ny + hy - prop_r.height // 3
                px = max(20, min(VIDEO_WIDTH - prop_r.width - 20, px))
                py = max(120, min(VIDEO_HEIGHT - prop_r.height - 160, py))

                glow = Image.new("RGBA", (prop_r.width + 70, prop_r.height + 70), (0, 0, 0, 0))
                gd = ImageDraw.Draw(glow)
                gd.ellipse((0, 0, glow.width, glow.height), fill=(255, 230, 120, 75))
                glow = glow.filter(ImageFilter.GaussianBlur(14))
                frame.alpha_composite(glow, (px - 35, py - 35))
                frame.alpha_composite(prop_r, (px, py))

            _speech_bubble(frame, bubble, nx + nib_r.width - 40, max(50, ny - 30))

            rgb = frame.convert("RGB")
            try:
                proc.stdin.write(rgb.tobytes())
            except BrokenPipeError:
                err = b"".join(stderr_chunks).decode("utf-8", errors="ignore")
                raise RuntimeError(f"ffmpeg pipe closed early:\n{err[-2000:]}") from None
            if i % (FPS * 4) == 0:
                print(f"  animating {i}/{total_frames} [{beat}/{pose_name}]")

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
        raise RuntimeError(f"render failed: {exc}\n{err[-2000:]}") from None

    err = b"".join(stderr_chunks).decode("utf-8", errors="ignore")
    if code != 0 or not final_path.exists():
        raise RuntimeError(f"ffmpeg encode failed:\n{err[-2000:]}")
    return final_path
