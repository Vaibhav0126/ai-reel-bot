from __future__ import annotations

import json
import random
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

import httpx

from .config import GEMINI_API_KEY, USED_FACTS_PATH, USED_MEALS_PATH, USED_TOPICS_PATH
from .facts import CATEGORY_HASHTAGS, FACT_CATEGORIES, FACTS, format_fact_caption
from .meals import MEALS, format_meal_caption
from .topics import STORIES, format_nutrition_caption

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


_USED_FACTS_KEEP = 8000
_TITLE_STOP = {
    "a", "an", "the", "and", "or", "to", "of", "in", "on", "it", "is", "are",
    "that", "this", "you", "do", "they", "for", "with", "have", "has", "than",
    "their", "can", "from", "was", "were", "be", "by",
}


def _fact_id_from_title(category: str, title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", (title or "").lower()).strip("_")[:72]
    cat = re.sub(r"[^a-z0-9]+", "_", (category or "fact").lower()).strip("_")
    return f"{cat}_{slug}" if slug else f"{cat}_fact"


def _norm_fact_title(title: str) -> str:
    text = re.sub(r"[^a-z0-9\s]", " ", (title or "").lower())
    return re.sub(r"\s+", " ", text).strip()


def _title_tokens(title: str) -> set[str]:
    return set(_norm_fact_title(title).split()) - _TITLE_STOP


def _is_repeat_title(title: str, used_titles: list[str]) -> bool:
    key = _norm_fact_title(title)
    if not key:
        return True
    used_keys = {_norm_fact_title(t) for t in used_titles if t}
    if key in used_keys:
        return True
    words = _title_tokens(title)
    if len(words) < 3:
        return False
    for other in used_titles:
        other_words = _title_tokens(other)
        if len(other_words) < 3:
            continue
        overlap = len(words & other_words) / min(len(words), len(other_words))
        if overlap >= 0.72:
            return True
    return False


def _load_used_fact_entries() -> list[dict[str, str]]:
    if not USED_FACTS_PATH.exists():
        return []
    try:
        raw = json.loads(USED_FACTS_PATH.read_text())
    except json.JSONDecodeError:
        return []
    items = raw if isinstance(raw, list) else raw.get("entries") if isinstance(raw, dict) else []
    entries: list[dict[str, str]] = []
    for item in items or []:
        if isinstance(item, str):
            known = next((f for f in FACTS if f["id"] == item), None)
            entries.append(
                {
                    "id": item,
                    "title": str(known["title"]) if known else item.replace("_", " "),
                    "category": str(known.get("category") or "") if known else "",
                }
            )
        elif isinstance(item, dict) and item.get("id"):
            entries.append(
                {
                    "id": str(item["id"]),
                    "title": str(item.get("title") or ""),
                    "category": str(item.get("category") or ""),
                }
            )
    return entries


def _save_used_fact_entries(entries: list[dict[str, str]]) -> None:
    USED_FACTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    USED_FACTS_PATH.write_text(json.dumps(entries[-_USED_FACTS_KEEP:], indent=2))


def pick_fact_category() -> str:
    entries = _load_used_fact_entries()
    last_cat = ""
    if entries:
        last_cat = entries[-1].get("category") or ""
        if not last_cat:
            last = next((f for f in FACTS if f["id"] == entries[-1].get("id")), None)
            last_cat = str(last.get("category") or "") if last else ""
    pool = [c for c in FACT_CATEGORIES if c != last_cat] or list(FACT_CATEGORIES)
    return random.choice(pool)


def _used_fact_titles() -> list[str]:
    return [e["title"] for e in _load_used_fact_entries() if e.get("title")]


def pick_fallback_fact() -> dict:
    """Template bank only — used when Gemini cannot invent a new claim."""
    used_ids = {e["id"] for e in _load_used_fact_entries()}
    unused = [f for f in FACTS if f["id"] not in used_ids]
    last_cat = None
    entries = _load_used_fact_entries()
    if entries:
        last_cat = entries[-1].get("category") or None
    pool = unused or list(FACTS)
    rotated = [f for f in pool if f.get("category") != last_cat]
    return random.choice(rotated or pool)


def pick_fact() -> dict:
    category = pick_fact_category()
    invented = _gemini_invent_fact(category)
    if invented:
        return invented
    print("   Gemini: invent skipped — using leftover template fact")
    return pick_fallback_fact()


def mark_fact_used(fact_id: str, title: str = "", category: str = "") -> None:
    entries = _load_used_fact_entries()
    if any(e.get("id") == fact_id for e in entries):
        return
    known = next((f for f in FACTS if f["id"] == fact_id), None)
    entries.append(
        {
            "id": fact_id,
            "title": title or str(known["title"] if known else fact_id),
            "category": category or str(known.get("category") or "" if known else ""),
        }
    )
    _save_used_fact_entries(entries)


def unused_fact_ids() -> list[str]:
    used = {e["id"] for e in _load_used_fact_entries()}
    return [f["id"] for f in FACTS if f["id"] not in used]


def pick_story() -> dict:
    used = set(_load_used(USED_TOPICS_PATH))
    known = {s["id"] for s in STORIES}
    used &= known
    unused = [s for s in STORIES if s["id"] not in used]
    if not unused:
        unused = list(STORIES)
        _save_used(USED_TOPICS_PATH, [])
    return random.choice(unused)


def pick_meal() -> dict:
    used = set(_load_used(USED_MEALS_PATH))
    known = {m["id"] for m in MEALS}
    used &= known
    unused = [m for m in MEALS if m["id"] not in used]
    if not unused:
        unused = list(MEALS)
        _save_used(USED_MEALS_PATH, [])
    return random.choice(unused)


def mark_topic_used(topic_id: str) -> None:
    used = _load_used(USED_TOPICS_PATH)
    if topic_id not in used:
        used.append(topic_id)
        _save_used(USED_TOPICS_PATH, used)


def mark_meal_used(meal_id: str) -> None:
    used = _load_used(USED_MEALS_PATH)
    if meal_id not in used:
        used.append(meal_id)
        _save_used(USED_MEALS_PATH, used)


# ~84 words at EDGE_TTS_RATE=+12% is about 30 seconds. Do not pad with a recap.
_TARGET_VOICEOVER_WORDS = 90
_MIN_VOICEOVER_WORDS = 80
_MAX_VOICEOVER_WORDS = 100

_PAUSE_MARK_RE = re.compile(r"\[pause(?::(short|long|beat))?\]", re.I)
_KID_OPENER_RE = re.compile(
    r"^\s*(do you know(?: this)?|did you know|fun fact|here(?:'| i)?s a fact)\b[\s,.:;?!-]*",
    re.I,
)

# Gemini writes in this voice. Pause marks become real TTS breaths in tts.py.
_NIB_VOICE = """
You are Nib: a charismatic fridge goblin. Adult. Magnetic. Slightly dangerous in a fun way.
You are NOT a child, NOT a teacher, NOT a Wikipedia narrator, NOT a cute mascot reciting trivia.

WHO YOU ARE:
- The goblin who already knew the secret and is letting the viewer in on it.
- Party-magnet energy: lean in, smirk, drop the fact like a plot twist, then explain.
- First person when it helps ("I swear", "watch this", "stay with me") — never a lecture.

HOOK (first 2 seconds MUST stop the scroll):
- Open with a dare, a secret, a visual punch, a conspiracy, or a smirk. Then the fact.
- Forbidden openers: "Do you know", "Did you know", "Fun fact", "Today I will", "Let me tell you",
  "Here's a fact", "Interesting fact", "So basically".

CADENCE (this is acting, not copywriting):
- Mix tiny hits ("Listen.") with one longer winding sentence, then a punch.
- Fragments. Asides. Then land the science like you were saving it.
- Uneven rhythm. Never six sentences the same length. Never "subject verb fact. subject verb fact."

PAUSES (you decide the performance):
- Insert [pause], [pause:short], or [pause:long] where a human would breathe, smirk, or let it land.
- [pause:short] after a tease. [pause] after the hook or a reveal. [pause:long] before the twist or closer.
- 3 to 6 pause marks per reel. BETWEEN thoughts, never mid-word, never in captions.
- Do not stack three pauses. Do not pause after every sentence.

TONE:
- Charisma first, facts second — but the facts stay true.
- Dry mischief, not hype-bro, not "you won't BELIEVE".
- No medical/legal advice. No begging (follow/save) except meal-reel payoff if asked.
"""

_FACT_VOICE = """
FACT REELS are scroll-stoppers, not museum plaques.

Beat 1 is a hook that would make a stranger look up from their phone. Then you earn the science.
Every later beat still sounds like Nib talking — never like a textbook that grew a mouth.

FORBIDDEN CADENCE (instant fail):
- Equal-length "fact. fact. fact."
- "X is Y. This is because Z."
- "That is why…", "It is usually…", "Scientists study…", "Botany says…"
- Copying the seed sentences even a little

GOOD (copy this energy, not these facts):
- "Don't look away. [pause] This thing is running three hearts like a crime syndicate."
- "Two of them are on gill duty. [pause] The third one bosses the rest of the body."
- "And when it swims? [pause:short] That body heart just… stops. That's why it would rather crawl."

BAD (never write like this):
- "Two pump blood to the gills. One pumps blood to the rest of the body."
- "Sharks showed up around four hundred million years ago. Trees came later."

The seed is TRUTH ONLY. Throw away its wording. If a line could be on a plaque, rewrite it.
"""


def _strip_pause_marks(text: str) -> str:
    return re.sub(r"\s+", " ", _PAUSE_MARK_RE.sub(" ", text or "")).strip()


def _count_pauses(text: str) -> int:
    return len(_PAUSE_MARK_RE.findall(text or ""))


def _normalize_pause_marks(text: str) -> str:
    """Keep only canonical [pause] / [pause:short] / [pause:long] / [pause:beat]."""

    def repl(match: re.Match[str]) -> str:
        kind = (match.group(1) or "").lower()
        if kind in {"short", "long", "beat"}:
            return f"[pause:{kind}]"
        return "[pause]"

    cleaned = _PAUSE_MARK_RE.sub(repl, text or "")
    return re.sub(r"\s+", " ", cleaned).strip()


def _join_spoken(parts: list[str]) -> str:
    chunks = [_normalize_pause_marks(p) for p in parts if str(p or "").strip()]
    if not chunks:
        return ""
    blob = re.sub(r"\s+", " ", " ".join(chunks)).strip()
    if _count_pauses(blob) >= 3:
        return blob
    out = [chunks[0]]
    for chunk in chunks[1:]:
        if chunk.lower().startswith("[pause"):
            out.append(chunk)
        else:
            out.append(f"[pause] {chunk}")
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def _unschool_opener(spoken: str) -> str:
    stripped = _KID_OPENER_RE.sub("", spoken or "").strip()
    return stripped or (spoken or "").strip()


def _ensure_acting_pauses(beats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """If the writer skipped pause marks, add a few scene-change breaths."""
    spoken_all = " ".join(str(b.get("spoken") or "") for b in beats)
    if _count_pauses(spoken_all) >= 3:
        return beats
    stamped: list[dict[str, Any]] = []
    last_i = len(beats) - 1
    for i, beat in enumerate(beats):
        item = dict(beat)
        spoken = _normalize_pause_marks(str(item.get("spoken") or ""))
        if i in {1, 3} or i == last_i:
            if spoken and not spoken.lower().startswith("[pause"):
                spoken = f"[pause] {spoken}"
        item["spoken"] = spoken
        stamped.append(item)
    return stamped

_RECAP_PAT = re.compile(
    r"simple version|whole story|to recap|in short|that is the whole|"
    r"here is the simple|said already|same thing|once more|again[,:]|"
    r"let me say that again|in other words",
    re.I,
)


def _truth_only(fact: dict[str, Any]) -> str:
    """Science the model must keep — not sentences it is allowed to copy."""
    lines = [f"Title: {fact.get('title')}", f"Category: {fact.get('category')}"]
    for i, beat in enumerate(fact.get("beats") or [], 1):
        spoken = _strip_pause_marks(str(beat.get("spoken") or ""))
        if spoken:
            lines.append(f"{i}. {spoken}")
    return "\n".join(lines)


def _word_count(beats: list[dict[str, Any]]) -> int:
    blob = _strip_pause_marks(" ".join(str(b.get("spoken") or "") for b in beats))
    return len(re.findall(r"[A-Za-z0-9']+", blob))


def _is_recap_spoken(spoken: str, earlier: list[str]) -> bool:
    if _RECAP_PAT.search(spoken):
        return True
    words = set(re.findall(r"[a-z0-9']+", _strip_pause_marks(spoken).lower()))
    stop = {
        "a", "an", "the", "and", "or", "to", "of", "in", "on", "it", "is", "are",
        "that", "this", "you", "do", "know", "they", "for", "with",
    }
    words -= stop
    if len(words) < 5:
        return False
    prior = set(re.findall(r"[a-z0-9']+", _strip_pause_marks(" ".join(earlier)).lower())) - stop
    overlap = len(words & prior) / max(len(words), 1)
    return overlap >= 0.55


def _drop_recap_beats(beats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    earlier: list[str] = []
    for beat in beats:
        spoken = str(beat.get("spoken") or "").strip()
        if kept and _is_recap_spoken(spoken, earlier):
            continue
        kept.append(dict(beat))
        earlier.append(spoken)
    return kept or [dict(b) for b in beats]


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
        spoken = _normalize_pause_marks(_unschool_opener(spoken))
        caption = _strip_pause_marks(caption)
        if not caption:
            caption = " ".join(_strip_pause_marks(spoken).split()[:5])
        if not prompt and i < len(fallback):
            prompt = str(fallback[i].get("image_prompt") or "")
        beats.append({"spoken": spoken, "caption": caption, "image_prompt": prompt})
    return beats or [dict(b) for b in fallback]


def _default_hashtags(category: str) -> list[str]:
    extra = CATEGORY_HASHTAGS.get(category) or [
        re.sub(r"[^a-z0-9]+", "", category.lower()) or "curious"
    ]
    return [
        "didyouknow",
        "facts",
        "reels",
        "shorts",
        "nibthefridgegoblin",
        *extra,
    ]


def _script_from_beats(
    fact: dict[str, Any],
    beats: list[dict[str, Any]],
    hashtags: list[str] | None = None,
) -> ReelScript:
    beats = _drop_recap_beats(beats)
    beats = _ensure_acting_pauses(beats)
    voiceover = re.sub(
        r"\s+", " ", " ".join(_normalize_pause_marks(b["spoken"]) for b in beats)
    ).strip()
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


def _humanize_plaque(spoken: str) -> str:
    """Keep fallback templates from reading like a museum guide."""
    spoken = _normalize_pause_marks(_unschool_opener(spoken))
    if not spoken or _PAUSE_MARK_RE.search(spoken):
        return spoken
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", spoken) if p.strip()]
    if len(parts) >= 2:
        return f"{parts[0]} [pause] {' '.join(parts[1:])}"
    spoken = re.sub(r"^That is why\b", "That's why", spoken)
    spoken = re.sub(r"^It is\b", "It's", spoken)
    return spoken


def _fact_script(fact: dict) -> ReelScript:
    beats = []
    for b in fact.get("beats") or []:
        item = dict(b)
        item["spoken"] = _humanize_plaque(str(item.get("spoken") or ""))
        beats.append(item)
    return _script_from_beats(fact, beats)


def _gemini_json(prompt: str) -> tuple[dict[str, Any] | None, str, str]:
    """Return (parsed_json, model_name, last_error)."""
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
                            "temperature": 1.05,
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
                return json.loads(text), model, ""
            except Exception as exc:
                last_err = f"{model}: {type(exc).__name__}"
                continue
    return None, "", last_err


def _prepare_fact_beats(fact: dict, raw_beats: list[Any]) -> list[dict[str, Any]]:
    beats = _normalize_beats(raw_beats, fact.get("beats") or [])
    beats = _drop_recap_beats(beats)
    return _ensure_acting_pauses(beats)


def _expand_fact_beats(fact: dict, beats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """If the script is short, add NEW details — never a recap of earlier lines."""
    n = _word_count(beats)
    if n >= _MIN_VOICEOVER_WORDS or not GEMINI_API_KEY:
        return beats
    prompt = f"""
The spoken Instagram fact reel is only {n} words. Rewrite it to about {_TARGET_VOICEOVER_WORDS} words
({_MIN_VOICEOVER_WORDS}-{_MAX_VOICEOVER_WORDS}) so it lasts about 30 seconds.

Truth only (do not copy this wording):
{_truth_only(fact)}

Current beats (rewrite the voice, keep the science): {json.dumps(beats, ensure_ascii=True)}

{_NIB_VOICE}
{_FACT_VOICE}

Rules:
- 6 beats. Each beat MUST add a NEW true detail the previous beats did not already say.
- Do NOT recap, summarize, or rephrase earlier lines. Forbidden phrases: "simple version",
  "whole story", "in other words", "to recap", "that is the whole".
- Last beat is a unique punchline, not a summary of the fact.
- Keep science accurate. No medical advice.
- Each beat: spoken (with [pause] marks), caption (2-6 words, no pause marks), image_prompt (one scroll-stopping object, white background, no text, no mascot)

Return ONLY JSON: beats (array of spoken, caption, image_prompt)
"""
    parsed, model, err = _gemini_json(prompt)
    if not parsed:
        print(f"   Gemini: lengthen skipped ({err})")
        return beats
    expanded = _prepare_fact_beats(fact, parsed.get("beats") or [])
    if _word_count(expanded) >= n:
        print(f"   Gemini: expanded fact script to {_word_count(expanded)} words via {model}")
        return expanded
    return beats


def _gemini_invent_fact(category: str) -> dict | None:
    """Ask Gemini for a brand-new true fact in this genre. None if the API is down."""
    if not GEMINI_API_KEY:
        return None

    all_used = _used_fact_titles() + [str(f.get("title") or "") for f in FACTS]
    all_used = [t for t in all_used if t]
    blocked = all_used[-140:]
    blocked_lines = "\n".join(f"- {t}" for t in blocked) or "- (none yet)"
    last_err = ""
    for attempt in range(3):
        prompt = f"""
Pick ONE brand-new, well-established curiosity fact in this category: {category}
(Attempt {attempt + 1} of 3 — if this is a retry, pick a more obscure but still true fact.)

Already used — do NOT repeat, rephrase, or cover the same subject:
{blocked_lines}

The fact must be:
- True and widely documented (textbooks, encyclopedias, official records, reputable science)
- Specific (a concrete claim with a real detail — not "sports are popular")
- A different subject from every line above
- Safe: no medical advice, no conspiracy, no cruelty, no living-person gossip

Then write 4 short truth beats (plain English, not a lecture). These are the SCIENCE only;
another pass will make them charismatic.

Return ONLY JSON:
title: lowercase short claim (e.g. "octopuses have three hearts")
category: {category}
beats: array of 4 objects with spoken, caption (2-6 words), image_prompt
  (one isolated object, white background, no text, no mascot)
"""
        parsed, model, last_err = _gemini_json(prompt)
        if not parsed:
            continue
        title = str(parsed.get("title") or "").strip()
        if not title or _is_repeat_title(title, all_used):
            print(f"   Gemini: invented a repeat ({title!r}) — retrying")
            all_used.append(title)
            blocked.append(title)
            blocked_lines = "\n".join(f"- {t}" for t in blocked[-140:])
            continue
        beats = parsed.get("beats") or []
        if not isinstance(beats, list) or len(beats) < 3:
            continue
        fact_id = _fact_id_from_title(category, title)
        if any(e.get("id") == fact_id for e in _load_used_fact_entries()):
            print(f"   Gemini: invented a used id ({fact_id}) — retrying")
            blocked.append(title)
            continue
        print(f"   Gemini: new {category} fact via {model}: {title}")
        return {
            "id": fact_id,
            "category": category,
            "title": title[0].lower() + title[1:] if title else title,
            "beats": beats,
            "source": "gemini",
        }
    if last_err:
        print(f"   Gemini: invent failed ({last_err})")
    return None


def _gemini_fact_script(fact: dict) -> ReelScript | None:
    if not GEMINI_API_KEY:
        print("   Gemini: no GEMINI_API_KEY — using template script")
        return None

    prompt = f"""
Write a spoken Instagram fact Reel as Nib. This must GRAB ATTENTION in the first second.

Topic: {fact['title']}
Category: {fact.get('category')}

Truth only — rewrite every sentence. Do not quote or lightly edit these:
{_truth_only(fact)}

{_NIB_VOICE}
{_FACT_VOICE}

Rules:
- {_MIN_VOICEOVER_WORDS} to {_MAX_VOICEOVER_WORDS} words total so a slightly fast voice lasts about 30 seconds
- Exactly 6 beats
- Beat 1 = scroll-stop. A dare, a smirk, a visual punch. Then the fact. Not a definition.
- Beats 2–5 = new true details, still spoken like gossip you are proud of
- Beat 6 = a closer with teeth, not a recap
- Never repeat or rephrase an earlier beat
- Each beat has:
  spoken: PERFORMED, with [pause] marks
  caption: 2 to 6 words, huge on-screen text, no pause marks
  image_prompt: ONE isolated object or animal, large, centered, white background, no frame, no text, no mascot. Beat 1's image should be the most striking.
- Keep facts accurate. Do not invent wild false claims.

Return ONLY JSON with keys:
title, hashtags (8 tags without #), beats (array of spoken, caption, image_prompt)
"""
    parsed, model, last_err = _gemini_json(prompt)
    if not parsed:
        print(f"   Gemini: failed ({last_err}) — using template script")
        return None

    beats = _prepare_fact_beats(fact, parsed.get("beats") or [])
    beats = _expand_fact_beats(fact, beats)
    title = str(fact.get("title") or parsed.get("title") or "").strip()
    fact_out = {**fact, "title": title, "beats": beats}
    print(f"   Gemini: fact script via {model} ({_word_count(beats)} words)")
    return _script_from_beats(
        fact_out,
        beats,
        [str(h).lstrip("#") for h in parsed.get("hashtags", [])],
    )


def _story_script(story: dict) -> ReelScript:
    hook = _normalize_pause_marks(_unschool_opener(story["hook"]))
    discover = _normalize_pause_marks(story["discover"])
    react = _normalize_pause_marks(story["react"])
    benefit = _normalize_pause_marks(story["benefit"])
    extra = _normalize_pause_marks(story.get("extra", ""))
    payoff = _normalize_pause_marks(story["payoff"])
    voiceover = _join_spoken([hook, discover, react, benefit, extra, payoff])

    return ReelScript(
        topic_id=story["id"],
        topic=story["item"],
        item=story["item"],
        item_emoji=story["item_emoji"],
        hook=hook,
        line_1=discover,
        line_2=react,
        tip=benefit,
        caption=format_nutrition_caption(story),
        hashtags=[
            "nutrition",
            "fitness",
            "fridgefinds",
            "healthtips",
            "mealprep",
            "nibthefridgegoblin",
            "fridgegoblin",
            "reels",
        ],
        voiceover=voiceover,
        discover=discover,
        react=react,
        benefit=benefit,
        extra=extra,
        payoff=payoff,
        reel_type="fridge",
    )


def _meal_script(meal: dict) -> ReelScript:
    hook = _normalize_pause_marks(_unschool_opener(meal["hook"]))
    ingredients_line = _normalize_pause_marks(meal["ingredients_line"])
    spices_line = _normalize_pause_marks(
        meal.get("spices_line")
        or "Don't forget the spices listed in the caption — that is the flavor."
    )
    cook_line = _normalize_pause_marks(meal["cook_line"])
    benefit = _normalize_pause_marks(meal["benefit"])
    payoff = _normalize_pause_marks(meal["payoff"])
    voiceover = _join_spoken(
        [hook, ingredients_line, spices_line, cook_line, benefit, payoff]
    )

    return ReelScript(
        topic_id=meal["id"],
        topic=meal["name"],
        item=meal["name"],
        item_emoji=meal["ingredients"][0]["key"] if meal.get("ingredients") else "box",
        hook=hook,
        line_1=ingredients_line,
        line_2=cook_line,
        tip=benefit,
        caption=format_meal_caption(meal),
        hashtags=[
            "easymeals",
            "quickrecipes",
            "mealprep",
            "healthyrecipes",
            "highprotein",
            "nibthefridgegoblin",
            "fridgegoblin",
            "reels",
        ],
        voiceover=voiceover,
        discover=ingredients_line,
        react=cook_line,
        benefit=benefit,
        extra=spices_line,
        payoff=payoff,
        reel_type="meal",
        ingredients=list(meal.get("ingredients") or []),
        spices=list(meal.get("spices") or []),
        steps=list(meal.get("steps") or []),
        time_mins=int(meal.get("time_mins") or 15),
        plate_prompt=str(meal.get("plate_prompt") or ""),
    )


def _gemini_script(story: dict) -> ReelScript | None:
    if not GEMINI_API_KEY:
        print("   Gemini: no GEMINI_API_KEY — using template script")
        return None

    prompt = f"""
Write a spoken Instagram Reel as Nib, standing in front of an open home fridge, holding/showing: {story['item']}.
Core benefit (keep true): {story['benefit']}

{_NIB_VOICE}

Rules:
- 45 to 70 words total in voiceover (snappy Reel — pauses count as acting, not extra lecture)
- Mini story beats: hook (stop the scroll, delay the item a half-second) -> discover the item -> react -> benefit -> extra tip -> payoff
- Put [pause] marks in the spoken fields. Also put them in voiceover in the same places.
- No medical advice. No kid-quiz voice. No "Do you know".
- Do not repeat the same claim in the last beats. Each beat adds something new.

Return ONLY JSON with keys:
hook, discover, react, benefit, extra, payoff, hashtags (8 tags without #), voiceover
Do NOT invent a caption — nutrition caption is added separately.
"""
    parsed, model, last_err = _gemini_json(prompt)
    if not parsed:
        print(f"   Gemini: fridge script failed ({last_err}) — using template script")
        return None

    hook = _normalize_pause_marks(_unschool_opener(str(parsed["hook"])))
    discover = _normalize_pause_marks(str(parsed["discover"]))
    react = _normalize_pause_marks(str(parsed["react"]))
    benefit = _normalize_pause_marks(str(parsed["benefit"]))
    extra = _normalize_pause_marks(str(parsed.get("extra", "")))
    payoff = _normalize_pause_marks(str(parsed["payoff"]))
    voiceover = _normalize_pause_marks(_unschool_opener(str(parsed.get("voiceover") or "")))
    if _count_pauses(voiceover) < 3:
        voiceover = _join_spoken([hook, discover, react, benefit, extra, payoff])
    print(f"   Gemini: fridge script via {model}")
    return ReelScript(
        topic_id=story["id"],
        topic=story["item"],
        item=story["item"],
        item_emoji=story["item_emoji"],
        hook=hook,
        line_1=discover,
        line_2=react,
        tip=benefit,
        caption=format_nutrition_caption(story),
        hashtags=[str(h).lstrip("#") for h in parsed.get("hashtags", [])][:10]
        or [
            "nutrition",
            "fitness",
            "fridgefinds",
            "healthtips",
            "mealprep",
            "nibthefridgegoblin",
            "fridgegoblin",
            "reels",
        ],
        voiceover=voiceover,
        discover=discover,
        react=react,
        benefit=benefit,
        extra=extra,
        payoff=payoff,
        reel_type="fridge",
    )


def _gemini_meal_script(meal: dict) -> ReelScript | None:
    if not GEMINI_API_KEY:
        print("   Gemini: no GEMINI_API_KEY — using template meal script")
        return None

    ingredient_names = ", ".join(
        ing.get("label") or ing.get("key", "") for ing in meal.get("ingredients") or []
    )
    spice_names = ", ".join(
        sp.get("label") or sp.get("key", "") for sp in meal.get("spices") or []
    ) or "salt, black pepper"
    step_summary = " | ".join((meal.get("steps") or [])[:4])
    prompt = f"""
Write a spoken Instagram Reel as Nib cooking in a home kitchen.
Meal: {meal['name']} (~{meal.get('time_mins', 15)} minutes).
Ingredients: {ingredient_names}.
Spices (MUST mention these by name in spices_line): {spice_names}.
Cooking outline: {step_summary}.

{_NIB_VOICE}

You are a goblin chef who makes people hungry AND stay to cook — not a recipe-card robot.

Rules:
- First person, kitchen setting (NOT standing at the fridge)
- 90 to 130 words total voiceover
- Beats in order, each with [pause] marks where you'd actually breathe:
  1) hook — stop the scroll, name the meal like it's a heist
  2) ingredients_line — list the main ingredients clearly
  3) spices_line — name the spices and say they are listed in the caption
  4) cook_line — walk through cooking in order (still charismatic, still clear)
  5) benefit — why it's worth making
  6) payoff — save/follow CTA, remind caption has full recipe
- No medical advice. No "Do you know". No kid-show host.
- Do NOT invent ingredients, spices, or macros not listed above.

Return ONLY JSON with keys:
hook, ingredients_line, spices_line, cook_line, benefit, payoff, hashtags (8 tags without #), voiceover
Do NOT invent a caption — detailed recipe caption is added separately.
"""
    parsed, model, last_err = _gemini_json(prompt)
    if not parsed:
        print(f"   Gemini: meal script failed ({last_err}) — using template")
        return None

    hook = _normalize_pause_marks(_unschool_opener(str(parsed["hook"])))
    ingredients_line = _normalize_pause_marks(str(parsed["ingredients_line"]))
    spices_line = _normalize_pause_marks(
        str(parsed.get("spices_line") or meal.get("spices_line") or "")
    )
    if not spices_line:
        spices_line = f"Add your spices — {spice_names}. Full amounts are in the caption."
    cook_line = _normalize_pause_marks(str(parsed["cook_line"]))
    benefit = _normalize_pause_marks(str(parsed["benefit"]))
    payoff = _normalize_pause_marks(str(parsed["payoff"]))
    voiceover = _normalize_pause_marks(_unschool_opener(str(parsed.get("voiceover") or "")))
    if _count_pauses(voiceover) < 3:
        voiceover = _join_spoken(
            [hook, ingredients_line, spices_line, cook_line, benefit, payoff]
        )
    print(f"   Gemini: meal script via {model}")
    return ReelScript(
        topic_id=meal["id"],
        topic=meal["name"],
        item=meal["name"],
        item_emoji=meal["ingredients"][0]["key"] if meal.get("ingredients") else "box",
        hook=hook,
        line_1=ingredients_line,
        line_2=cook_line,
        tip=benefit,
        caption=format_meal_caption(meal),
        hashtags=[str(h).lstrip("#") for h in parsed.get("hashtags", [])][:10]
        or [
            "easymeals",
            "quickrecipes",
            "mealprep",
            "healthyrecipes",
            "highprotein",
            "nibthefridgegoblin",
            "fridgegoblin",
            "reels",
        ],
        voiceover=voiceover,
        discover=ingredients_line,
        react=cook_line,
        benefit=benefit,
        extra=spices_line,
        payoff=payoff,
        reel_type="meal",
        ingredients=list(meal.get("ingredients") or []),
        spices=list(meal.get("spices") or []),
        steps=list(meal.get("steps") or []),
        time_mins=int(meal.get("time_mins") or 15),
        plate_prompt=str(meal.get("plate_prompt") or ""),
    )


def generate_script(
    topic: dict | None = None,
    reel_type: ReelType = "fact",
) -> ReelScript:
    if reel_type == "meal":
        meal = pick_meal()
        if topic and "id" in topic:
            match = next((m for m in MEALS if m["id"] == topic["id"]), None)
            if match:
                meal = match
        return _gemini_meal_script(meal) or _meal_script(meal)

    if reel_type == "fridge":
        story = pick_story()
        if topic and "id" in topic:
            match = next((s for s in STORIES if s["id"] == topic["id"]), None)
            if match:
                story = match
        return _gemini_script(story) or _story_script(story)

    fact = None
    if topic and topic.get("id"):
        fact = next((f for f in FACTS if f["id"] == topic["id"]), None) or topic
    if fact is None:
        fact = pick_fact()
    script = _gemini_fact_script(fact) or _fact_script(fact)
    if _word_count(script.beats) < _MIN_VOICEOVER_WORDS and GEMINI_API_KEY:
        expanded = _expand_fact_beats(fact, script.beats)
        if expanded is not script.beats:
            return _script_from_beats(fact, expanded, script.hashtags)
    return script
