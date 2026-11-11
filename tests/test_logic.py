"""Unit tests for the pure logic: publish scheduling and the views feedback loop.

Run: python -m unittest discover -s tests   (or: pytest)
"""
import random
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bot"))

from src.performance import apply_stats, category_weights, matured, weighted_choice  # noqa: E402
from src.scheduling import next_publish_time, to_rfc3339  # noqa: E402

UTC = timezone.utc


class SchedulingTests(unittest.TestCase):
    def test_noon_new_york_in_winter_is_17_utc(self):
        # 2026-11-12 03:17 UTC (12:17 JST, the cron time) -> 12:00 EST = 17:00 UTC same day
        got = next_publish_time(datetime(2026, 11, 12, 3, 17, tzinfo=UTC))
        self.assertEqual(got, datetime(2026, 11, 12, 17, 0, tzinfo=UTC))

    def test_noon_new_york_in_summer_is_16_utc(self):
        got = next_publish_time(datetime(2026, 7, 1, 3, 17, tzinfo=UTC))
        self.assertEqual(got, datetime(2026, 7, 1, 16, 0, tzinfo=UTC))

    def test_respects_review_window(self):
        # 12:00 UTC is 3h before 12:00 EST (17:00 UTC) -> too soon, use tomorrow
        got = next_publish_time(datetime(2026, 11, 12, 12, 0, tzinfo=UTC), min_lead_hours=6)
        self.assertEqual(got, datetime(2026, 11, 13, 17, 0, tzinfo=UTC))

    def test_india_audience(self):
        got = next_publish_time(datetime(2026, 11, 12, 0, 0, tzinfo=UTC), "Asia/Kolkata", 13, 6)
        self.assertEqual(got, datetime(2026, 11, 12, 7, 30, tzinfo=UTC))

    def test_rejects_naive_datetime(self):
        with self.assertRaises(ValueError):
            next_publish_time(datetime(2026, 11, 12, 3, 0))

    def test_rfc3339(self):
        self.assertEqual(to_rfc3339(datetime(2026, 11, 12, 17, 0, tzinfo=UTC)), "2026-11-12T17:00:00Z")


def _u(vid, cat, views, published="2026-11-01T17:00:00Z"):
    return {"video_id": vid, "category": cat, "views": views, "publish_at": published}


NOW = datetime(2026, 11, 12, 0, 0, tzinfo=UTC)
CATS = ["animals", "space", "history"]


class FeedbackTests(unittest.TestCase):
    def test_uniform_without_data(self):
        w = category_weights(CATS, [], NOW)
        for c in CATS:
            self.assertAlmostEqual(w[c], 1 / 3)

    def test_weights_sum_to_one_and_favour_winners(self):
        uploads = [_u("a", "animals", 900), _u("b", "animals", 1100), _u("c", "space", 100)]
        w = category_weights(CATS, uploads, NOW)
        self.assertAlmostEqual(sum(w.values()), 1.0)
        self.assertGreater(w["animals"], w["history"])  # untested category gets the average
        self.assertGreater(w["history"], w["space"])

    def test_every_category_keeps_some_chance(self):
        uploads = [_u("a", "animals", 10_000), _u("c", "space", 0)]
        w = category_weights(CATS, uploads, NOW, explore=0.25)
        self.assertGreaterEqual(w["space"], 0.25 / 3)

    def test_one_lucky_video_is_damped(self):
        uploads = [_u("a", "animals", 50_000)] + [_u(f"s{i}", "space", 1000) for i in range(5)]
        w = category_weights(CATS, uploads, NOW)
        self.assertLess(w["animals"], 0.8)

    def test_too_fresh_videos_are_ignored(self):
        fresh = [_u("a", "animals", 5000, published="2026-11-11T17:00:00Z")]  # 7h old
        self.assertEqual(matured(fresh, NOW), [])
        w = category_weights(CATS, fresh, NOW)
        self.assertAlmostEqual(w["animals"], 1 / 3)

    def test_apply_stats(self):
        uploads = [{"video_id": "x", "views": None}]
        apply_stats(uploads, {"x": {"views": 42, "likes": 3}}, NOW)
        self.assertEqual((uploads[0]["views"], uploads[0]["likes"]), (42, 3))

    def test_weighted_choice_is_deterministic_with_seed(self):
        w = {"a": 0.0, "b": 1.0}
        self.assertEqual(weighted_choice(w, random.Random(1)), "b")


if __name__ == "__main__":
    unittest.main()
