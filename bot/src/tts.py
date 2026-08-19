from __future__ import annotations

import asyncio
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import edge_tts
import imageio_ffmpeg

from .config import EDGE_TTS_PITCH, EDGE_TTS_RATE, EDGE_TTS_VOICE


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


async def _synthesize_with_timings(text: str, out_path: Path, voice: str) -> VoiceResult:
    communicate = edge_tts.Communicate(
        text,
        voice=voice,
        rate=EDGE_TTS_RATE,
        pitch=EDGE_TTS_PITCH,
    )
    words: list[WordTiming] = []
    audio_chunks: list[bytes] = []
    sentences: list[SentenceTiming] = []

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            start = chunk["offset"] / 10_000_000
            end = (chunk["offset"] + chunk["duration"]) / 10_000_000
            words.append(WordTiming(text=chunk["text"], start=start, end=end))
        elif chunk["type"] == "SentenceBoundary":
            start = chunk["offset"] / 10_000_000
            end = (chunk["offset"] + chunk["duration"]) / 10_000_000
            sentences.append(SentenceTiming(text=chunk["text"], start=start, end=end))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(b"".join(audio_chunks))

    if not words and sentences:
        for sent in sentences:
            words.extend(_words_from_sentence(sent.text, sent.start, sent.end))

    if not words:
        fallback = re.findall(r"[A-Za-z0-9']+", text)
        dur = max(8.0, len(fallback) * 0.28)
        words = _words_from_sentence(" ".join(fallback) or text, 0.0, dur)

    if not sentences and words:
        # Rebuild rough sentence spans from punctuation in original text
        parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", text) if p.strip()]
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

    # Prefer real file length — word boundaries often end before the last phoneme
    file_dur = _audio_file_duration(out_path)
    word_end = words[-1].end if words else 0.0
    duration = max(file_dur, word_end) + 0.25
    return VoiceResult(
        audio_path=out_path,
        words=words,
        duration=duration,
        sentences=sentences,
    )


def _audio_file_duration(path: Path) -> float:
    """Return mp3/audio duration in seconds via ffmpeg."""
    try:
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        proc = subprocess.run(
            [ffmpeg, "-i", str(path)],
            capture_output=True,
            text=True,
        )
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", proc.stderr or "")
        if m:
            h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
            return h * 3600 + mi * 60 + s
    except Exception:
        pass
    return 0.0


def generate_voiceover(text: str, out_path: Path, voice: str | None = None) -> VoiceResult:
    return asyncio.run(_synthesize_with_timings(text, out_path, voice or EDGE_TTS_VOICE))


def align_script_beats(
    beat_texts: list[tuple[str, str]],
    words: list[WordTiming],
    duration: float,
) -> list[tuple[str, str, float, float]]:
    """
    Map (beat_name, bubble_text) to real audio times using word alignment.
    Returns list of (beat, text, start, end).
    """
    cleaned = [(name, text.strip()) for name, text in beat_texts if text and text.strip()]
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
