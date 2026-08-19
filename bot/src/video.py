from __future__ import annotations

import math
import subprocess
import threading
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter

from .config import ACCENT, FACT_BG, FPS, TARGET_REEL_SECONDS, VIDEO_HEIGHT, VIDEO_WIDTH
from .fonts import get_font
from .horns import fix_horn_colors
from .poses import list_poses
from .script_gen import ReelScript
from .tts import (
    VoiceResult,
    WordTiming,
    active_beat_at,
    active_word_index,
    align_script_beats,
    generate_voiceover,
)

POSE_FOR_INDEX = [
    "judge_think",
    "shocked",
    "talk_thumbs_up",
    "talk_wave",
    "judge_sincere",
    "celebrating",
]


def _load_pose(path: Path, max_h: int = 700) -> Image.Image:
    from .cutout import cutout_character

    nib = cutout_character(Image.open(path).convert("RGBA"))
    nib = fix_horn_colors(nib)
    bbox = nib.getbbox()
    if bbox:
        nib = nib.crop(bbox)
    ratio = max_h / max(nib.height, 1)
    w = max(1, int(nib.width * ratio))
    h = max(1, int(nib.height * ratio))
    if w > VIDEO_WIDTH - 80:
        ratio = (VIDEO_WIDTH - 80) / max(nib.width, 1)
        w = max(1, int(nib.width * ratio))
        h = max(1, int(nib.height * ratio))
    return nib.resize((w, h), Image.Resampling.LANCZOS)


def _still_base() -> Image.Image:
    return Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), FACT_BG)


def _object_sticker(img: Image.Image, max_size: int) -> Image.Image:
    """Place the cut-out object on the reel — no square card behind it."""
    rgba = img.convert("RGBA")
    extrema = rgba.getextrema()
    has_alpha = extrema[3][0] < 250 if extrema and len(extrema) > 3 else False
    if not has_alpha:
        from .cutout import cutout_object

        rgba = cutout_object(rgba)
    bbox = rgba.getbbox()
    if bbox:
        rgba = rgba.crop(bbox)
    w, h = rgba.size
    scale = min(max_size / max(w, 1), max_size / max(h, 1))
    nw = max(1, int(w * scale))
    nh = max(1, int(h * scale))
    return rgba.resize((nw, nh), Image.Resampling.LANCZOS)


CAPTION_TOP = 64
CAPTION_FONT_SIZE = 58
CAPTION_STROKE = 6
CAPTION_LINE_H = 78
CAPTION_MAX_CHARS = 22
CAPTION_MAX_LINES = 2
SPACE_W_SCALE = 0.32


def _wrap_words(words: list[WordTiming], max_chars: int = CAPTION_MAX_CHARS) -> list[list[WordTiming]]:
    lines: list[list[WordTiming]] = []
    cur: list[WordTiming] = []
    chars = 0
    for word in words:
        token = (word.text or "").strip()
        if not token:
            continue
        extra = len(token) + (1 if cur else 0)
        if cur and chars + extra > max_chars:
            lines.append(cur)
            cur = [word]
            chars = len(token)
        else:
            cur.append(word)
            chars += extra
    if cur:
        lines.append(cur)
    return lines


def _caption_groups(words: list[WordTiming]) -> list[list[WordTiming]]:
    """Pack timed words into 1–2 line karaoke chunks."""
    lines = _wrap_words(words)
    groups: list[list[WordTiming]] = []
    for i in range(0, len(lines), CAPTION_MAX_LINES):
        chunk: list[WordTiming] = []
        for line in lines[i : i + CAPTION_MAX_LINES]:
            chunk.extend(line)
        if chunk:
            groups.append(chunk)
    return groups


def _group_for_word(groups: list[list[WordTiming]], word_idx: int, words: list[WordTiming]) -> list[WordTiming]:
    if not groups or word_idx < 0 or not words:
        return []
    target = words[word_idx]
    for group in groups:
        if any(w is target for w in group):
            return group
    return groups[-1]


def _caption_bottom_y(line_count: int) -> int:
    n = max(line_count, 1)
    return CAPTION_TOP + CAPTION_LINE_H * n + 8


def _draw_karaoke_captions(
    frame: Image.Image,
    group: list[WordTiming],
    active: WordTiming | None,
) -> int:
    """Draw live captions; highlight the word currently being spoken."""
    if not group:
        return CAPTION_TOP
    lines = _wrap_words(group)
    draw = ImageDraw.Draw(frame)
    font = get_font(CAPTION_FONT_SIZE)
    space_w = max(10, int(font.size * SPACE_W_SCALE))
    y = CAPTION_TOP
    idle = (235, 235, 242)
    spoken = (255, 255, 255)
    for line in lines:
        widths = []
        for word in line:
            bbox = draw.textbbox((0, 0), word.text, font=font, stroke_width=CAPTION_STROKE)
            widths.append(bbox[2] - bbox[0])
        total = sum(widths) + space_w * max(len(line) - 1, 0)
        x = max(20, (VIDEO_WIDTH - total) // 2)
        for word, w in zip(line, widths):
            is_active = active is not None and word is active
            already = active is not None and word.start < active.start
            fill = ACCENT if is_active else (spoken if already else idle)
            draw.text(
                (x, y),
                word.text,
                font=font,
                fill=fill,
                stroke_width=CAPTION_STROKE,
                stroke_fill=(20, 18, 36),
            )
            x += w + space_w
        y += CAPTION_LINE_H
    return y


def render_reel(script: ReelScript, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_path = out_dir / "voice.mp3"
    final_path = out_dir / "reel.mp4"

    voice: VoiceResult = generate_voiceover(script.voiceover, audio_path)
    duration = max(TARGET_REEL_SECONDS, voice.duration + 0.35)
    duration = min(duration, 40.0)

    beats = script.beats or []
    beat_texts = [(f"beat_{i}", b.get("spoken") or "") for i, b in enumerate(beats)]
    timeline = align_script_beats(beat_texts, voice.words, duration)
    caption_groups = _caption_groups(voice.words)

    print("   Caption sync beats:")
    for name, text, start, end in timeline:
        print(f"     {start:5.2f}-{end:5.2f}s  [{name}] {text[:48]}")

    poses = list_poses()
    pose_cache = {
        name: _load_pose(path)
        for name, path in poses.items()
        if name != "fridge"
    }
    if not pose_cache:
        pose_cache = {name: _load_pose(path) for name, path in poses.items()}

    stickers: dict[str, Image.Image] = {}
    for i, path_str in enumerate(script.beat_image_paths):
        p = Path(path_str)
        if p.exists():
            stickers[f"beat_{i}"] = _object_sticker(Image.open(p), 720)

    base = _still_base()
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
    pose_names = list(pose_cache.keys())

    try:
        for i in range(total_frames):
            t = i / FPS
            beat, _spoken = active_beat_at(timeline, t)
            if beat != last_beat:
                punch = 1.0
                last_beat = beat
            punch *= 0.88

            frame = base.copy().convert("RGBA")

            beat_idx = 0
            if beat.startswith("beat_"):
                try:
                    beat_idx = int(beat.split("_", 1)[1])
                except ValueError:
                    beat_idx = 0
            preferred = POSE_FOR_INDEX[min(beat_idx, len(POSE_FOR_INDEX) - 1)]
            pose_name = preferred if preferred in pose_cache else (
                "idle" if "idle" in pose_cache else pose_names[beat_idx % len(pose_names)]
            )
            nib = pose_cache[pose_name]
            bounce = int(6 * math.sin(t * 2 * math.pi * 1.1))
            scale = 1.0 + 0.045 * punch
            sway = int(4 * math.sin(t * 2 * math.pi * 0.35))
            nib_r = nib.resize(
                (max(1, int(nib.width * scale)), max(1, int(nib.height * scale))),
                Image.Resampling.BILINEAR,
            )

            shadow = Image.new("RGBA", (nib_r.width, 70), (0, 0, 0, 0))
            sd = ImageDraw.Draw(shadow)
            sd.ellipse((24, 14, nib_r.width - 24, 58), fill=(0, 0, 0, 90))
            shadow = shadow.filter(ImageFilter.GaussianBlur(8))

            nx = (VIDEO_WIDTH - nib_r.width) // 2 + sway
            ny = VIDEO_HEIGHT - nib_r.height - 80 + bounce
            nx = max(10, min(VIDEO_WIDTH - nib_r.width - 10, nx))
            ny = max(520, min(VIDEO_HEIGHT - nib_r.height - 20, ny))

            word_idx = active_word_index(voice.words, t)
            active_word = voice.words[word_idx] if word_idx >= 0 else None
            caption_group = _group_for_word(caption_groups, word_idx, voice.words)
            caption_lines = _wrap_words(caption_group) if caption_group else []
            caption_bottom = _caption_bottom_y(len(caption_lines))

            sticker = stickers.get(beat)
            if sticker is not None:
                pop = 0.94 + 0.06 * punch
                sw = max(1, int(sticker.width * pop))
                sh = max(1, int(sticker.height * pop))
                art = sticker.resize((sw, sh), Image.Resampling.LANCZOS)
                ax = (VIDEO_WIDTH - art.width) // 2
                ay = caption_bottom + 18 + int(4 * math.sin(t * 2.0))
                max_ay = ny - art.height - 12
                if max_ay > 0:
                    ay = min(ay, max_ay)
                ay = max(caption_bottom + 8, ay)
                glow = Image.new("RGBA", (art.width + 80, art.height + 80), (0, 0, 0, 0))
                gd = ImageDraw.Draw(glow)
                gd.ellipse((12, 12, glow.width - 12, glow.height - 12), fill=(0, 0, 0, 55))
                glow = glow.filter(ImageFilter.GaussianBlur(16))
                frame.alpha_composite(glow, (ax - 40, ay - 40))
                frame.alpha_composite(art, (ax, ay))

            frame.alpha_composite(shadow, (nx, ny + nib_r.height - 50))
            frame.alpha_composite(nib_r, (nx, ny))
            _draw_karaoke_captions(frame, caption_group, active_word)

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


def _ken_burns(base: Image.Image, progress: float) -> Image.Image:
    """Kept for leftover meal_video imports; fact reels use a still background."""
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
    """Kept for leftover meal_video imports."""
    if not text:
        return
    from .config import CAPTION_STROKE

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
    for i, ln in enumerate(lines):
        draw.text((x + pad_x, y + pad_y + i * line_h), ln, font=font, fill=CAPTION_STROKE)
