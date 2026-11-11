"""Caption alignment must survive hyphenated words (Edge TTS reports them whole).

Run: python -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bot"))

from src.tts import WordTiming, align_script_beats  # noqa: E402


class HyphenAlignmentTests(unittest.TestCase):
    def test_hyphenated_word_does_not_shift_later_beats(self):
        # Edge gives "forty-three-pound" as one word; the script text splits it.
        words = [
            WordTiming("Result", 0.0, 0.5),
            WordTiming("A", 0.5, 0.6),
            WordTiming("forty-three-pound", 0.6, 1.6),
            WordTiming("slab.", 1.6, 2.0),
            WordTiming("Next", 2.0, 2.5),
            WordTiming("beat.", 2.5, 3.0),
        ]
        beats = [("b0", "Result? A forty-three-pound slab."), ("b1", "Next beat.")]

        timeline = align_script_beats(beats, words, duration=3.5)

        b1_start = timeline[1][2]
        # "Next" begins at 2.0s in the audio; the caption leads it by 0.08s.
        self.assertAlmostEqual(b1_start, 1.92, places=2)


if __name__ == "__main__":
    unittest.main()
