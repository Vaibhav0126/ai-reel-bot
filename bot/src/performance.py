"""
Feedback loop: learn which fact categories get views and pick those more often.

The first version of the bot never looked at its own results, so it kept
making the same kind of content for weeks. Now every upload is recorded in
data/uploads.json, view counts are refreshed from the YouTube API on each run,
and category choice is weighted by how well each category has done.

Weighting (all pure functions, unit-tested):
  * Only videos published at least `min_age_hours` ago count (fresh videos
    haven't had time to get views yet).
  * Each category's average views is shrunk toward the overall average
    (Bayesian prior worth `prior_weight` videos), so one lucky video doesn't
    take over.
  * `explore` (default 25%) of the probability is spread evenly across all
    categories, so new or unlucky categories still get tried.
"""
from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable


def load_uploads(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def save_uploads(path: Path, uploads: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(uploads, indent=2) + "\n")


def record_upload(
    path: Path,
    video_id: str,
    category: str,
    title: str,
    publish_at: str,
) -> None:
    uploads = load_uploads(path)
    uploads.append(
        {
            "video_id": video_id,
            "category": category,
            "title": title,
            "publish_at": publish_at,
            "views": None,
            "likes": None,
            "stats_updated": None,
        }
    )
    save_uploads(path, uploads)


def apply_stats(uploads: list[dict], stats: dict[str, dict], now_utc: datetime) -> list[dict]:
    """Merge {video_id: {"views": int, "likes": int}} into the upload records."""
    stamp = now_utc.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for u in uploads:
        s = stats.get(u.get("video_id", ""))
        if s:
            u["views"] = int(s.get("views", 0))
            u["likes"] = int(s.get("likes", 0))
            u["stats_updated"] = stamp
    return uploads


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def matured(uploads: Iterable[dict], now_utc: datetime, min_age_hours: float = 48) -> list[dict]:
    """Uploads that went public long enough ago and have a view count."""
    cutoff = now_utc - timedelta(hours=min_age_hours)
    out = []
    for u in uploads:
        published = _parse_ts(u.get("publish_at"))
        if published and published <= cutoff and isinstance(u.get("views"), int):
            out.append(u)
    return out


def category_weights(
    categories: list[str],
    uploads: Iterable[dict],
    now_utc: datetime,
    min_age_hours: float = 48,
    prior_weight: float = 2.0,
    explore: float = 0.25,
) -> dict[str, float]:
    """Probability of picking each category. Sums to 1."""
    if not categories:
        return {}
    data = matured(uploads, now_utc, min_age_hours)
    uniform = {c: 1 / len(categories) for c in categories}
    if not data:
        return uniform

    global_mean = sum(u["views"] for u in data) / len(data)
    if global_mean <= 0:
        return uniform

    scores = {}
    for c in categories:
        views = [u["views"] for u in data if u.get("category") == c]
        # Shrink toward the global mean: unknown categories score the average.
        scores[c] = (sum(views) + prior_weight * global_mean) / (len(views) + prior_weight)

    total = sum(scores.values())
    exploit = {c: s / total for c, s in scores.items()}
    return {c: explore * uniform[c] + (1 - explore) * exploit[c] for c in categories}


def weighted_choice(weights: dict[str, float], rng: random.Random | None = None) -> str:
    rng = rng or random.Random()
    items = [(c, w) for c, w in weights.items() if w > 0]
    if not items:
        raise ValueError("no positive weights")
    r = rng.random() * sum(w for _, w in items)
    for c, w in items:
        r -= w
        if r <= 0:
            return c
    return items[-1][0]


def summary(uploads: Iterable[dict], now_utc: datetime, min_age_hours: float = 48) -> str:
    data = matured(uploads, now_utc, min_age_hours)
    if not data:
        return "no matured uploads yet"
    by_cat: dict[str, list[int]] = {}
    for u in data:
        by_cat.setdefault(u.get("category", "?"), []).append(u["views"])
    parts = [
        f"{c}: {sum(v) / len(v):.0f} avg views ({len(v)})"
        for c, v in sorted(by_cat.items(), key=lambda kv: -sum(kv[1]) / len(kv[1]))
    ]
    return "; ".join(parts)
