from __future__ import annotations

import json
import random
import re
from dataclasses import asdict, dataclass
from typing import Any

import httpx

from .config import GEMINI_API_KEY, USED_TOPICS_PATH
from .topics import STORIES, format_nutrition_caption


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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_used() -> list[str]:
    if not USED_TOPICS_PATH.exists():
        return []
    try:
        return json.loads(USED_TOPICS_PATH.read_text())
    except json.JSONDecodeError:
        return []


def _save_used(used: list[str]) -> None:
    USED_TOPICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    USED_TOPICS_PATH.write_text(json.dumps(used[-200:], indent=2))


def pick_story() -> dict:
    used = set(_load_used())
    # Ignore orphan IDs from older topic lists
    known = {s["id"] for s in STORIES}
    used &= known
    unused = [s for s in STORIES if s["id"] not in used]
    if not unused:
        unused = list(STORIES)
        _save_used([])
    return random.choice(unused)


def mark_topic_used(topic_id: str) -> None:
    used = _load_used()
    if topic_id not in used:
        used.append(topic_id)
        _save_used(used)


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
                )
            except Exception as exc:
                last_err = f"{model}: {type(exc).__name__}"
                continue

    print(f"   Gemini: failed ({last_err}) — using template script")
    return None


def generate_script(topic: dict | None = None) -> ReelScript:
    story = pick_story()
    if topic and "id" in topic:
        match = next((s for s in STORIES if s["id"] == topic["id"]), None)
        if match:
            story = match
    return _gemini_script(story) or _story_script(story)


def unused_story_ids() -> list[str]:
    used = set(_load_used()) & {s["id"] for s in STORIES}
    return [s["id"] for s in STORIES if s["id"] not in used]
