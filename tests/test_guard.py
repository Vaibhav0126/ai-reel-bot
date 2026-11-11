"""The upload guard: a template-written script must never reach YouTube.

Run: python -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bot"))

from src.pipeline import check_uploadable  # noqa: E402
from src.script_gen import ReelScript  # noqa: E402


def _script(source: str) -> ReelScript:
    return ReelScript(
        topic_id="t1",
        topic="octopuses have three hearts",
        item="octopus",
        item_emoji="fact",
        hook="",
        line_1="",
        line_2="",
        tip="",
        caption="",
        hashtags=[],
        voiceover="",
        discover="",
        react="",
        benefit="",
        extra="",
        payoff="",
        source=source,
    )


class UploadGuardTests(unittest.TestCase):
    def test_gemini_script_is_uploadable(self):
        check_uploadable(_script("gemini"))

    def test_template_script_is_refused(self):
        with self.assertRaises(RuntimeError):
            check_uploadable(_script("template"))

    def test_default_source_is_template(self):
        # Scripts built without an explicit source are treated as templates,
        # so forgetting to tag a Gemini script fails safe.
        self.assertEqual(ReelScript.__dataclass_fields__["source"].default, "template")


if __name__ == "__main__":
    unittest.main()
