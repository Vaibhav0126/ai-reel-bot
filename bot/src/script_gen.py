from __future__ import annotations

import json
import random
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

import httpx

from .config import GEMINI_API_KEY, USED_MEALS_PATH, USED_TOPICS_PATH
from .meals import MEALS, format_meal_caption
from .topics import STORIES, format_nutrition_caption

ReelType = Literal["fridge", "meal"]


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
    reel_type: ReelType = "fridge"
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

Return ONLY JSON with keys:
hook, discover, react, benefit, extra, payoff, hashtags (8 tags without #), voiceover
Do NOT invent a caption — nutrition caption is added separately.
"""

    models = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-flash-latest",
    ]
    last_err = ""
    with httpx.Client(timeout=60) as client:
        for model in models:
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
                            "temperature": 0.95,
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
                voiceover = str(parsed.get("voiceover") or "").strip()
                if not voiceover.lower().startswith("do you know"):
                    voiceover = "Do you know this? " + voiceover
                print(f"   Gemini: script via {model}")
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
            except Exception as exc:
                last_err = f"{model}: {type(exc).__name__}"
                continue

    print(f"   Gemini: failed ({last_err}) — using template script")
    return None


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

    models = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-flash-latest",
    ]
    last_err = ""
    with httpx.Client(timeout=60) as client:
        for model in models:
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
                            "temperature": 0.95,
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
                hook = str(parsed["hook"]).strip()
                ingredients_line = str(parsed["ingredients_line"]).strip()
                spices_line = str(
                    parsed.get("spices_line") or meal.get("spices_line") or ""
                ).strip()
                if not spices_line:
                    spices_line = (
                        f"Add your spices — {spice_names}. Full amounts are in the caption."
                    )
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
            except Exception as exc:
                last_err = f"{model}: {type(exc).__name__}"
                continue

    print(f"   Gemini: meal script failed ({last_err}) — using template")
    return None


def generate_script(
    topic: dict | None = None,
    reel_type: ReelType = "fridge",
) -> ReelScript:
    if reel_type == "meal":
        meal = pick_meal()
        if topic and "id" in topic:
            match = next((m for m in MEALS if m["id"] == topic["id"]), None)
            if match:
                meal = match
        return _gemini_meal_script(meal) or _meal_script(meal)

    story = pick_story()
    if topic and "id" in topic:
        match = next((s for s in STORIES if s["id"] == topic["id"]), None)
        if match:
            story = match
    return _gemini_script(story) or _story_script(story)


def unused_story_ids() -> list[str]:
    used = set(_load_used(USED_TOPICS_PATH)) & {s["id"] for s in STORIES}
    return [s["id"] for s in STORIES if s["id"] not in used]


def unused_meal_ids() -> list[str]:
    used = set(_load_used(USED_MEALS_PATH)) & {m["id"] for m in MEALS}
    return [m["id"] for m in MEALS if m["id"] not in used]
