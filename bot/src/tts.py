from __future__ import annotations

import asyncio
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

import edge_tts
import imageio_ffmpeg

from .config import EDGE_TTS_PITCH, EDGE_TTS_RATE, EDGE_TTS_VOICE

_PAUSE_MARK_RE = re.compile(r"\[pause(?::(short|long|beat))?\]", re.I)
# Micro-beats, not dead air. Fast talk + a smirk of silence.
_PAUSE_MS = {"short": 130, "beat": 190, "long": 360}
_DEFAULT_PAUSE_MS = 220
_TICKS_PER_SECOND = 10_000_000


def strip_pause_marks(text: str) -> str:
    return re.sub(r"\s+", " ", _PAUSE_MARK_RE.sub(" ", text or "")).strip()


def _pause_segments(text: str) -> tuple[int, list[tuple[str, int]]]:
    """Split performed script into (spoken, pause_after_ms) plus a leading silence."""
    raw = text or ""
    leading_ms = 0
    parts: list[tuple[str, int]] = []
    last = 0
    for match in _PAUSE_MARK_RE.finditer(raw):
        spoken = re.sub(r"\s+", " ", raw[last : match.start()]).strip()
        kind = (match.group(1) or "").lower()
        ms = _PAUSE_MS.get(kind, _DEFAULT_PAUSE_MS)
        if spoken:
            parts.append((spoken, ms))
        elif parts:
            prev_text, prev_ms = parts[-1]
            parts[-1] = (prev_text, prev_ms + ms)
        else:
            leading_ms += ms
        last = match.end()
    tail = re.sub(r"\s+", " ", raw[last:]).strip()
    if tail:
        parts.append((tail, 0))
    if not parts:
        stripped = strip_pause_marks(raw)
        if stripped:
            parts.append((stripped, 0))
    return leading_ms, parts


@dataclass
class WordTiming:
    text: str
    start: float
    end: float


@dataclass
class SentenceTiming:
    text: str
    start: float
    end: float


@dataclass
class VoiceResult:
    audio_path: Path
    words: list[WordTiming]
    duration: float
    sentences: list[SentenceTiming] = field(default_factory=list)


def _words_from_sentence(text: str, start: float, end: float) -> list[WordTiming]:
    tokens = re.findall(r"[A-Za-z0-9']+|[^\sA-Za-z0-9]", text)
    spoken = [t for t in tokens if re.search(r"[A-Za-z0-9]", t)]
    if not spoken:
        return [WordTiming(text=text.strip(), start=start, end=end)]

    weights = [max(len(w), 1) for w in spoken]
    total_w = sum(weights)
    span = max(end - start, 0.05)
    cursor = start
    out: list[WordTiming] = []
    for word, weight in zip(spoken, weights):
        dur = span * (weight / total_w)
        out.append(WordTiming(text=word, start=cursor, end=cursor + dur))
        cursor += dur
    if out:
        out[-1].end = end
    return out


def _normalize_token(text: str) -> str:
    return re.sub(r"[^a-z0-9']+", "", text.lower())


async def _stream_plain(
    text: str, voice: str
) -> tuple[bytes, list[WordTiming], list[SentenceTiming]]:
    communicate = edge_tts.Communicate(
        text,
        voice=voice,
        rate=EDGE_TTS_RATE,
        pitch=EDGE_TTS_PITCH,
        boundary="WordBoundary",
    )
    words: list[WordTiming] = []
    sentences: list[SentenceTiming] = []
    audio_chunks: list[bytes] = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            start = chunk["offset"] / _TICKS_PER_SECOND
            end = (chunk["offset"] + chunk["duration"]) / _TICKS_PER_SECOND
            words.append(WordTiming(text=chunk["text"], start=start, end=end))
        elif chunk["type"] == "SentenceBoundary":
            start = chunk["offset"] / _TICKS_PER_SECOND
            end = (chunk["offset"] + chunk["duration"]) / _TICKS_PER_SECOND
            sentences.append(SentenceTiming(text=chunk["text"], start=start, end=end))
    audio = b"".join(audio_chunks)
    if not audio:
        raise RuntimeError("edge-tts returned no audio")
    return audio, words, sentences


def _run_ffmpeg(args: list[str]) -> subprocess.CompletedProcess[str]:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    proc = subprocess.run(
        [ffmpeg, *args],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "ffmpeg failed")[-1500:]
        raise RuntimeError(err)
    return proc


def _ffmpeg_info(path: Path) -> str:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    proc = subprocess.run(
        [ffmpeg, "-i", str(path)],
        capture_output=True,
        text=True,
    )
    return proc.stderr or ""


def _audio_file_duration(path: Path) -> float:
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", _ffmpeg_info(path))
    if not m:
        return 0.0
    h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mi * 60 + s


def _to_wav(src: Path, dest: Path, sample_rate: int) -> None:
    _run_ffmpeg(
        [
            "-y",
            "-i",
            str(src),
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            str(dest),
        ]
    )


def _silence_wav(dest: Path, seconds: float, sample_rate: int) -> None:
    _run_ffmpeg(
        [
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"anullsrc=r={sample_rate}:cl=mono",
            "-t",
            f"{max(seconds, 0.05):.3f}",
            str(dest),
        ]
    )


def _concat_wavs(paths: list[Path], dest: Path) -> None:
    if len(paths) == 1:
        shutil.copyfile(paths[0], dest)
        return
    list_path = dest.with_suffix(".concat.txt")
    list_path.write_text(
        "".join(f"file '{p.resolve()}'\n" for p in paths),
        encoding="utf-8",
    )
    try:
        _run_ffmpeg(
            [
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_path),
                "-c",
                "copy",
                str(dest),
            ]
        )
    finally:
        list_path.unlink(missing_ok=True)


def _wav_to_mp3(src: Path, dest: Path) -> None:
    try:
        _run_ffmpeg(
            ["-y", "-i", str(src), "-c:a", "libmp3lame", "-q:a", "4", str(dest)]
        )
    except RuntimeError:
        _run_ffmpeg(["-y", "-i", str(src), str(dest)])


def _shift(items: list, offset: float):
    for item in items:
        item.start += offset
        item.end += offset


def _fill_missing_timings(
    text: str,
    words: list[WordTiming],
    sentences: list[SentenceTiming],
) -> tuple[list[WordTiming], list[SentenceTiming]]:
    if not words and sentences:
        for sent in sentences:
            words.extend(_words_from_sentence(sent.text, sent.start, sent.end))

    if not words:
        fallback = re.findall(r"[A-Za-z0-9']+", strip_pause_marks(text))
        dur = max(8.0, len(fallback) * 0.28)
        words = _words_from_sentence(" ".join(fallback) or text, 0.0, dur)

    if not sentences and words:
        parts = [
            p.strip()
            for p in re.split(r"(?<=[.!?])\s+", strip_pause_marks(text))
            if p.strip()
        ]
        if parts:
            total_chars = sum(max(len(p), 1) for p in parts) or 1
            cursor = words[0].start
            end_all = words[-1].end
            span = max(end_all - cursor, 0.1)
            for p in parts:
                dur = span * (max(len(p), 1) / total_chars)
                sentences.append(SentenceTiming(text=p, start=cursor, end=cursor + dur))
                cursor += dur
            sentences[-1].end = end_all
    return words, sentences


async def _synthesize_with_timings(text: str, out_path: Path, voice: str) -> VoiceResult:
    # Plain-text Edge calls (same as the working other repo), with real silence
    # stitched in for [pause] marks. Do not inject SSML into communicate.texts.
    leading_ms, segments = _pause_segments(text)
    if not segments:
        raise RuntimeError("voiceover text was empty after stripping pause marks")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    words: list[WordTiming] = []
    sentences: list[SentenceTiming] = []
    wav_parts: list[Path] = []
    cursor = 0.0
    sample_rate = 24000

    with tempfile.TemporaryDirectory(prefix="nib-tts-") as tmp:
        tmp_dir = Path(tmp)
        n = 0

        def add_silence(ms: int) -> None:
            nonlocal cursor, n
            if ms <= 0:
                return
            sil = tmp_dir / f"sil_{n:02d}.wav"
            _silence_wav(sil, ms / 1000.0, sample_rate)
            wav_parts.append(sil)
            cursor += ms / 1000.0
            n += 1

        add_silence(leading_ms)

        for spoken, pause_after_ms in segments:
            mp3_part = tmp_dir / f"part_{n:02d}.mp3"
            audio, part_words, part_sentences = await _stream_plain(spoken, voice)
            mp3_part.write_bytes(audio)
            wav_part = tmp_dir / f"part_{n:02d}.wav"
            _to_wav(mp3_part, wav_part, sample_rate)
            wav_parts.append(wav_part)

            _shift(part_words, cursor)
            _shift(part_sentences, cursor)
            words.extend(part_words)
            sentences.extend(part_sentences)

            spoken_dur = _audio_file_duration(wav_part)
            if spoken_dur <= 0 and part_words:
                spoken_dur = part_words[-1].end - cursor
            cursor += spoken_dur
            n += 1
            add_silence(pause_after_ms)

        merged = tmp_dir / "voice.wav"
        _concat_wavs(wav_parts, merged)
        _wav_to_mp3(merged, out_path)

    words, sentences = _fill_missing_timings(text, words, sentences)
    file_dur = _audio_file_duration(out_path)
    word_end = words[-1].end if words else 0.0
    duration = max(file_dur, word_end, cursor) + 0.25
    return VoiceResult(
        audio_path=out_path,
        words=words,
        duration=duration,
        sentences=sentences,
    )


_TTS_ATTEMPTS = 5
_TTS_BACKOFF_SEC = 3.0


def generate_voiceover(text: str, out_path: Path, voice: str | None = None) -> VoiceResult:
    chosen = voice or EDGE_TTS_VOICE
    print(f"   Voice: {chosen} @ {EDGE_TTS_RATE}")
    last_err: Exception | None = None
    for attempt in range(1, _TTS_ATTEMPTS + 1):
        try:
            return asyncio.run(_synthesize_with_timings(text, out_path, chosen))
        except Exception as exc:
            last_err = exc
            if attempt >= _TTS_ATTEMPTS:
                break
            wait = _TTS_BACKOFF_SEC * (2 ** (attempt - 1))
            print(
                f"   TTS: attempt {attempt}/{_TTS_ATTEMPTS} failed "
                f"({type(exc).__name__}: {exc}) — retrying in {wait:.0f}s"
            )
            time.sleep(wait)
    assert last_err is not None
    raise last_err


def align_script_beats(
    beat_texts: list[tuple[str, str]],
    words: list[WordTiming],
    duration: float,
) -> list[tuple[str, str, float, float]]:
    """
    Map (beat_name, bubble_text) to real audio times using word alignment.
    Returns list of (beat, text, start, end).
    """
    cleaned = [
        (name, strip_pause_marks(text))
        for name, text in beat_texts
        if strip_pause_marks(text)
    ]
    if not cleaned:
        return [("hook", "", 0.0, duration)]

    if not words:
        # equal split fallback
        slot = duration / len(cleaned)
        return [
            (name, text, i * slot, (i + 1) * slot)
            for i, (name, text) in enumerate(cleaned)
        ]

    tokens = [_normalize_token(w.text) for w in words]
    token_starts = [w.start for w in words]
    token_ends = [w.end for w in words]

    timeline: list[tuple[str, str, float, float]] = []
    search_from = 0

    for name, text in cleaned:
        want = [_normalize_token(t) for t in re.findall(r"[A-Za-z0-9']+", text)]
        want = [t for t in want if t]
        if not want:
            continue

        # Find best sequential match starting at/after search_from
        idx = _find_sequence(tokens, want, search_from)
        if idx is None:
            # fallback: take next unused word cluster by length
            idx = min(search_from, len(words) - 1)
            end_idx = min(idx + max(len(want), 1) - 1, len(words) - 1)
        else:
            end_idx = min(idx + len(want) - 1, len(words) - 1)

        start = token_starts[idx]
        end = token_ends[end_idx]
        # Slight lead so bubble appears with/just before speech (never late)
        start = max(0.0, start - 0.08)
        timeline.append((name, text, start, end))
        search_from = end_idx + 1

    if not timeline:
        return [("hook", cleaned[0][1], 0.0, duration)]

    # Stretch ends to next beat start for continuous coverage
    fixed: list[tuple[str, str, float, float]] = []
    for i, (name, text, start, end) in enumerate(timeline):
        if i + 1 < len(timeline):
            next_start = timeline[i + 1][2]
            end = max(end, next_start)
        else:
            end = max(end, duration)
        fixed.append((name, text, start, end))
    # Ensure first beat covers from 0
    name0, text0, _, end0 = fixed[0]
    fixed[0] = (name0, text0, 0.0, end0)
    return fixed


def _find_sequence(tokens: list[str], want: list[str], start_at: int) -> int | None:
    if not want or not tokens:
        return None
    # Prefer exact contiguous match
    n = len(want)
    for i in range(start_at, len(tokens) - n + 1):
        if tokens[i : i + n] == want:
            return i
    # Fuzzy: match first 3+ tokens
    probe = want[: min(3, len(want))]
    m = len(probe)
    for i in range(start_at, len(tokens) - m + 1):
        if tokens[i : i + m] == probe:
            return i
    # Single first-word match
    for i in range(start_at, len(tokens)):
        if tokens[i] == want[0]:
            return i
    return None


def active_word_index(words: list[WordTiming], t: float) -> int:
    """Index of the word being spoken at time t, or the last spoken word."""
    if not words:
        return -1
    for i, word in enumerate(words):
        if word.start <= t < word.end:
            return i
        if t < word.start:
            return max(i - 1, 0)
    return len(words) - 1


def active_beat_at(
    timeline: list[tuple[str, str, float, float]],
    t: float,
) -> tuple[str, str]:
    if not timeline:
        return "hook", ""
    for name, text, start, end in timeline:
        if start <= t < end:
            return name, text
    # after last / between gaps → nearest past
    past = [b for b in timeline if b[2] <= t]
    if past:
        return past[-1][0], past[-1][1]
    return timeline[0][0], timeline[0][1]
