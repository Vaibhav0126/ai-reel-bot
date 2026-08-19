from __future__ import annotations

import json
import random
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

import httpx

from .config import GEMINI_API_KEY, USED_FACTS_PATH
from .facts import CATEGORY_HASHTAGS, FACTS, format_fact_caption

ReelType = Literal["fact", "fridge", "meal"]

_GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-flash-latest",
]


@dataclass
class ReelScript:
    topic_id: str
    topic: str
    item: str
    item_emoji: str
    hook: str
    line_1: str
    line_2: str
    tip: str
    caption: str
    hashtags: list[str]
    voiceover: str
    discover: str
    react: str
    benefit: str
    extra: str
    payoff: str
    reel_type: ReelType = "fact"
    category: str = ""
    beats: list[dict[str, Any]] = field(default_factory=list)
    beat_image_paths: list[str] = field(default_factory=list)
    ingredients: list[dict[str, Any]] = field(default_factory=list)
    spices: list[dict[str, Any]] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    meal_image_path: str = ""
    time_mins: int = 0
    plate_prompt: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_used(path) -> list[str]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return []


def _save_used(path, used: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(used[-200:], indent=2))


def pick_fact() -> dict:
    used = _load_used(USED_FACTS_PATH)
    known = {f["id"] for f in FACTS}
    used = [uid for uid in used if uid in known]
    unused = [f for f in FACTS if f["id"] not in used]
    if not unused:
        unused = list(FACTS)
        used = []
        _save_used(USED_FACTS_PATH, [])

    last_cat = None
    if used:
        last = next((f for f in FACTS if f["id"] == used[-1]), None)
        if last:
            last_cat = last.get("category")
    rotated = [f for f in unused if f.get("category") != last_cat]
    pool = rotated or unused
    return random.choice(pool)


def mark_fact_used(fact_id: str) -> None:
    used = _load_used(USED_FACTS_PATH)
    if fact_id not in used:
        used.append(fact_id)
        _save_used(USED_FACTS_PATH, used)


def unused_fact_ids() -> list[str]:
    used = set(_load_used(USED_FACTS_PATH)) & {f["id"] for f in FACTS}
    return [f["id"] for f in FACTS if f["id"] not in used]


_TARGET_VOICEOVER_WORDS = 85


def _word_count(beats: list[dict[str, Any]]) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", " ".join(str(b.get("spoken") or "") for b in beats)))


def _expand_beats_for_length(beats: list[dict[str, Any]], fact: dict[str, Any]) -> list[dict[str, Any]]:
    """Pad short templates so TTS lands near a 30-second reel."""
    out = [dict(b) for b in beats]
    if _word_count(out) >= _TARGET_VOICEOVER_WORDS - 13:
        return out
    title = str(fact.get("title") or "this fact")
    recap_bits = [str(b.get("caption") or "").strip() for b in out]
    recap_bits = [c for c in recap_bits if c]
    last_prompt = str(out[-1].get("image_prompt") or "") if out else ""
    last_caption = recap_bits[-1] if recap_bits else title
    rest = " ".join(str(b.get("spoken") or "") for b in out[1:3]).strip()
    if rest.lower().startswith("do you know"):
        rest = rest[11:].lstrip(" ,.?")
    extra = (
        f"Here is the simple version. {title}. {rest} That is the whole story."
        if rest
        else f"Here is the simple version. {title}. That is the whole story."
    )
    out.append(
        {
            "spoken": extra,
            "caption": last_caption,
            "image_prompt": last_prompt or f"isolated cartoon of {title} on white",
        }
    )
    return out


def _normalize_beats(raw: list[Any], fallback: list[dict[str, Any]]) -> list[dict[str, Any]]:
    beats: list[dict[str, Any]] = []
    for i, item in enumerate(raw or []):
        if not isinstance(item, dict):
            continue
        spoken = str(item.get("spoken") or "").strip()
        caption = str(item.get("caption") or "").strip()
        prompt = str(item.get("image_prompt") or "").strip()
        if not spoken:
            continue
        if not caption:
            caption = " ".join(spoken.split()[:5])
        if not prompt and i < len(fallback):
            prompt = str(fallback[i].get("image_prompt") or "")
        beats.append({"spoken": spoken, "caption": caption, "image_prompt": prompt})
    return beats or [dict(b) for b in fallback]


def _default_hashtags(category: str) -> list[str]:
    return [
        "didyouknow",
        "facts",
        "reels",
        "shorts",
        "nibthefridgegoblin",
        *CATEGORY_HASHTAGS.get(category, ["curious"]),
    ]


def _script_from_beats(
    fact: dict[str, Any],
    beats: list[dict[str, Any]],
    hashtags: list[str] | None = None,
) -> ReelScript:
    beats = _expand_beats_for_length(beats, fact)
    voiceover = re.sub(r"\s+", " ", " ".join(b["spoken"] for b in beats)).strip()
    tags = [str(h).lstrip("#") for h in (hashtags or [])][:12] or _default_hashtags(
        str(fact.get("category") or "")
    )
    spoken_parts = [b["spoken"] for b in beats]
    while len(spoken_parts) < 6:
        spoken_parts.append("")
    hook, discover, react, benefit, extra, payoff = spoken_parts[:6]
    return ReelScript(
        topic_id=fact["id"],
        topic=fact["title"],
        item=fact["title"],
        item_emoji=str(fact.get("category") or "fact"),
        hook=hook,
        line_1=discover,
        line_2=react,
        tip=benefit,
        caption=format_fact_caption(fact, tags),
        hashtags=tags,
        voiceover=voiceover,
        discover=discover,
        react=react,
        benefit=benefit,
        extra=extra,
        payoff=payoff,
        reel_type="fact",
        category=str(fact.get("category") or ""),
        beats=beats,
    )


def _fact_script(fact: dict) -> ReelScript:
    beats = [dict(b) for b in fact.get("beats") or []]
    return _script_from_beats(fact, beats)


def _gemini_fact_script(fact: dict) -> ReelScript | None:
    if not GEMINI_API_KEY:
        print("   Gemini: no GEMINI_API_KEY — using template script")
        return None

    beat_preview = json.dumps(fact.get("beats") or [], ensure_ascii=True)
    prompt = f"""
Write a spoken Instagram Reel as Nib, a male cartoon mascot who tells curious facts.
Topic: {fact['title']}
Category: {fact.get('category')}
Seed beats (keep the science true; keep the voice calm): {beat_preview}

Voice:
- He gets attention by stating the surprising fact itself, then explaining it.
- Dry, curious, confident. Like a smart friend pointing at something interesting.
- Do NOT sound attention-seeking: no "wait for it", "you won't believe", "hold onto this",
  "save this", "follow me", "the takeaway", "drop this fact", or begging the viewer.
- No hype, no lecture, no medical or legal advice.

Rules:
- MUST start the first spoken line with exactly "Do you know"
- 80 to 100 words total across all spoken lines so a slightly fast speaking pace lasts about 30 seconds
- 5 or 6 beats
- Each spoken line: short concrete sentences, one idea, easy to hear
- Each beat has:
  spoken: two short sentences that explain the idea
  caption: 2 to 6 words for huge on-screen text (lowercase ok)
  image_prompt: ONE isolated real-world object or animal, large and centered, white background, no frame, no text, no mascot
- Keep facts accurate to the seed. Do not invent wild false claims.

Return ONLY JSON with keys:
title, hashtags (8 tags without #), beats (array of spoken, caption, image_prompt)
"""

    last_err = ""
    with httpx.Client(timeout=60) as client:
        for model in _GEMINI_MODELS:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model}:generateContent?key={GEMINI_API_KEY}"
            )
            try:
                resp = client.post(
                    url,
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.9,
                            "responseMimeType": "application/json",
                        },
                    },
                )
                if resp.status_code >= 400:
                    last_err = f"{model} HTTP {resp.status_code}"
                    continue
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                text = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()
                parsed = json.loads(text)
                beats = _normalize_beats(parsed.get("beats") or [], fact.get("beats") or [])
                if beats and not beats[0]["spoken"].lower().startswith("do you know"):
                    beats[0]["spoken"] = "Do you know this? " + beats[0]["spoken"]
                title = str(parsed.get("title") or fact["title"]).strip()
                fact_out = {**fact, "title": title, "beats": beats}
                print(f"   Gemini: fact script via {model}")
                return _script_from_beats(
                    fact_out,
                    beats,
                    [str(h).lstrip("#") for h in parsed.get("hashtags", [])],
                )
            except Exception as exc:
                last_err = f"{model}: {type(exc).__name__}"
                continue

    print(f"   Gemini: failed ({last_err}) — using template script")
    return None


def generate_script(
    topic: dict | None = None,
    reel_type: ReelType = "fact",
) -> ReelScript:
    fact = pick_fact()
    if topic and "id" in topic:
        match = next((f for f in FACTS if f["id"] == topic["id"]), None)
        if match:
            fact = match
    return _gemini_fact_script(fact) or _fact_script(fact)
