from __future__ import annotations

import json
import random
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

import httpx

from .config import GEMINI_API_KEY, USED_FACTS_PATH, USED_MEALS_PATH, USED_TOPICS_PATH
from .facts import CATEGORY_HASHTAGS, FACTS, format_fact_caption
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

_RECAP_PAT = re.compile(
    r"simple version|whole story|to recap|in short|that is the whole|"
    r"here is the simple|said already|same thing|once more|again[,:]|"
    r"let me say that again|in other words",
    re.I,
)


def _word_count(beats: list[dict[str, Any]]) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", " ".join(str(b.get("spoken") or "") for b in beats)))


def _is_recap_spoken(spoken: str, earlier: list[str]) -> bool:
    if _RECAP_PAT.search(spoken):
        return True
    words = set(re.findall(r"[a-z0-9']+", spoken.lower()))
    stop = {
        "a", "an", "the", "and", "or", "to", "of", "in", "on", "it", "is", "are",
        "that", "this", "you", "do", "know", "they", "for", "with",
    }
    words -= stop
    if len(words) < 5:
        return False
    prior = set(re.findall(r"[a-z0-9']+", " ".join(earlier).lower())) - stop
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
    beats = _drop_recap_beats(beats)
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
                return json.loads(text), model, ""
            except Exception as exc:
                last_err = f"{model}: {type(exc).__name__}"
                continue
    return None, "", last_err


def _prepare_fact_beats(fact: dict, raw_beats: list[Any]) -> list[dict[str, Any]]:
    beats = _normalize_beats(raw_beats, fact.get("beats") or [])
    beats = _drop_recap_beats(beats)
    if beats and not beats[0]["spoken"].lower().startswith("do you know"):
        beats[0]["spoken"] = "Do you know this? " + beats[0]["spoken"]
    return beats


def _expand_fact_beats(fact: dict, beats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """If the script is short, add NEW details — never a recap of earlier lines."""
    n = _word_count(beats)
    if n >= _MIN_VOICEOVER_WORDS or not GEMINI_API_KEY:
        return beats
    prompt = f"""
The spoken Instagram fact reel is only {n} words. Rewrite it to about {_TARGET_VOICEOVER_WORDS} words
({_MIN_VOICEOVER_WORDS}-{_MAX_VOICEOVER_WORDS}) so it lasts about 30 seconds. Topic: {fact['title']}
Seed truth (do not contradict): {json.dumps(fact.get('beats') or [], ensure_ascii=True)}
Current beats: {json.dumps(beats, ensure_ascii=True)}

Rules:
- 6 beats. Each beat MUST add a NEW true detail the previous beats did not already say.
- Do NOT recap, summarize, or rephrase earlier lines. Forbidden phrases: "simple version",
  "whole story", "in other words", "to recap", "that is the whole".
- MUST start beat 1 with exactly "Do you know"
- Last beat is a unique punchline, not a summary of the fact.
- Keep science accurate. No medical advice.
- Each beat: spoken, caption (2-6 words), image_prompt (one object, white background, no text, no mascot)

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
- {_MIN_VOICEOVER_WORDS} to {_MAX_VOICEOVER_WORDS} words total so a slightly fast voice lasts about 30 seconds
- Exactly 6 beats that MOVE THE STORY FORWARD
- Each beat introduces a NEW concrete detail. Never repeat or rephrase an earlier beat.
- No recap, no "simple version", no "that is the whole story", no closing summary of the same facts.
- The last beat is a new punchy closer, not a restatement.
- Each beat has:
  spoken: two short sentences that explain ONE new idea
  caption: 2 to 6 words for huge on-screen text (lowercase ok)
  image_prompt: ONE isolated real-world object or animal, large and centered, white background, no frame, no text, no mascot
- Keep facts accurate to the seed. Do not invent wild false claims.

Return ONLY JSON with keys:
title, hashtags (8 tags without #), beats (array of spoken, caption, image_prompt)
"""
    parsed, model, last_err = _gemini_json(prompt)
    if not parsed:
        print(f"   Gemini: failed ({last_err}) — using template script")
        return None

    beats = _prepare_fact_beats(fact, parsed.get("beats") or [])
    beats = _expand_fact_beats(fact, beats)
    title = str(parsed.get("title") or fact["title"]).strip()
    fact_out = {**fact, "title": title, "beats": beats}
    print(f"   Gemini: fact script via {model} ({_word_count(beats)} words)")
    return _script_from_beats(
        fact_out,
        beats,
        [str(h).lstrip("#") for h in parsed.get("hashtags", [])],
    )


def _story_script(story: dict) -> ReelScript:
    hook = story["hook"]
    if not hook.lower().startswith("do you know"):
        hook = f"Do you know this? {hook}"

    voiceover = " ".join(
        [
            hook,
            story["discover"],
            story["react"],
            story["benefit"],
            story.get("extra", ""),
            story["payoff"],
        ]
    ).strip()
    voiceover = re.sub(r"\s+", " ", voiceover)

    return ReelScript(
        topic_id=story["id"],
        topic=story["item"],
        item=story["item"],
        item_emoji=story["item_emoji"],
        hook=hook,
        line_1=story["discover"],
        line_2=story["react"],
        tip=story["benefit"],
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
        discover=story["discover"],
        react=story["react"],
        benefit=story["benefit"],
        extra=story.get("extra", ""),
        payoff=story["payoff"],
        reel_type="fridge",
    )


def _meal_script(meal: dict) -> ReelScript:
    hook = meal["hook"]
    ingredients_line = meal["ingredients_line"]
    spices_line = meal.get("spices_line") or (
        "Don't forget the spices listed in the caption — that is the flavor."
    )
    cook_line = meal["cook_line"]
    benefit = meal["benefit"]
    payoff = meal["payoff"]
    voiceover = " ".join(
        [hook, ingredients_line, spices_line, cook_line, benefit, payoff]
    ).strip()
    voiceover = re.sub(r"\s+", " ", voiceover)

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
Write a spoken Instagram Reel as Nib the Fridge Goblin.
MUST start the voiceover with exactly "Do you know" to build curiosity.
Setting: standing in front of an open home fridge, holding/showing: {story['item']}.
Core benefit: {story['benefit']}

Rules:
- First person, curious then helpful, playful fridge-goblin energy
- 45 to 60 words total voiceover (snappy Reel pace — no lingering)
- Mini story beats: curiosity hook -> find item -> react -> benefit -> extra tip -> payoff
- Short punchy sentences. No medical advice. No lecture tone.
- Make the audience lean in during the hook before revealing the item.
- Do not repeat the same claim in the last beats. Each beat adds something new.

Return ONLY JSON with keys:
hook, discover, react, benefit, extra, payoff, hashtags (8 tags without #), voiceover
Do NOT invent a caption — nutrition caption is added separately.
"""
    parsed, model, last_err = _gemini_json(prompt)
    if not parsed:
        print(f"   Gemini: fridge script failed ({last_err}) — using template script")
        return None

    voiceover = str(parsed.get("voiceover") or "").strip()
    if not voiceover.lower().startswith("do you know"):
        voiceover = "Do you know this? " + voiceover
    print(f"   Gemini: fridge script via {model}")
    return ReelScript(
        topic_id=story["id"],
        topic=story["item"],
        item=story["item"],
        item_emoji=story["item_emoji"],
        hook=str(parsed["hook"]).strip(),
        line_1=str(parsed["discover"]).strip(),
        line_2=str(parsed["react"]).strip(),
        tip=str(parsed["benefit"]).strip(),
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
        discover=str(parsed["discover"]).strip(),
        react=str(parsed["react"]).strip(),
        benefit=str(parsed["benefit"]).strip(),
        extra=str(parsed.get("extra", "")).strip(),
        payoff=str(parsed["payoff"]).strip(),
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
Write a spoken Instagram Reel as Nib the Fridge Goblin cooking in a home kitchen.
Meal: {meal['name']} (~{meal.get('time_mins', 15)} minutes).
Ingredients: {ingredient_names}.
Spices (MUST mention these by name in spices_line): {spice_names}.
Cooking outline: {step_summary}.
Core vibe: quick, easy, delicious, helpful teacher energy — playful fridge-goblin.

Rules:
- First person, kitchen setting (NOT standing at the fridge)
- 90 to 130 words total voiceover (longer, clearer recipe reel — not a rushed tip)
- Beats in order:
  1) hook — grab attention + name the meal
  2) ingredients_line — list the main ingredients clearly
  3) spices_line — name the spices and say they are listed in the caption
  4) cook_line — walk through the cooking process in clear order (2–4 short sentences)
  5) benefit — why it is worth making
  6) payoff — save/follow CTA, remind caption has full recipe
- Clear and easy to follow. No medical advice.
- Do NOT start with "Do you know" — this is a meal reel, not a fridge find.
- Do NOT invent ingredients, spices, or macros not listed above.

Return ONLY JSON with keys:
hook, ingredients_line, spices_line, cook_line, benefit, payoff, hashtags (8 tags without #), voiceover
Do NOT invent a caption — detailed recipe caption is added separately.
"""
    parsed, model, last_err = _gemini_json(prompt)
    if not parsed:
        print(f"   Gemini: meal script failed ({last_err}) — using template")
        return None

    hook = str(parsed["hook"]).strip()
    ingredients_line = str(parsed["ingredients_line"]).strip()
    spices_line = str(parsed.get("spices_line") or meal.get("spices_line") or "").strip()
    if not spices_line:
        spices_line = f"Add your spices — {spice_names}. Full amounts are in the caption."
    cook_line = str(parsed["cook_line"]).strip()
    benefit = str(parsed["benefit"]).strip()
    payoff = str(parsed["payoff"]).strip()
    voiceover = str(parsed.get("voiceover") or "").strip()
    if not voiceover:
        voiceover = " ".join(
            [hook, ingredients_line, spices_line, cook_line, benefit, payoff]
        )
    voiceover = re.sub(r"\s+", " ", voiceover).strip()
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

    fact = pick_fact()
    if topic and "id" in topic:
        match = next((f for f in FACTS if f["id"] == topic["id"]), None)
        if match:
            fact = match
    script = _gemini_fact_script(fact) or _fact_script(fact)
    if _word_count(script.beats) < _MIN_VOICEOVER_WORDS and GEMINI_API_KEY:
        expanded = _expand_fact_beats(fact, script.beats)
        if expanded is not script.beats:
            return _script_from_beats(fact, expanded, script.hashtags)
    return script
