"""Offline regression checks for lossless Notion description chunking."""
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "v1"))
# The converter's logger dependency is optional for this isolated offline test.
try:
    import loguru
except ImportError:
    sys.modules["loguru"] = MagicMock()

from leetcode_converter import LeetCodeNotionConverter


class SplitDescriptionTests(unittest.TestCase):
    def test_lossless_whitespace_and_punctuation(self):
        examples = [
            "a" * 5000,
            "a" * 1500 + ". " + " b" * 1200,
            "a" * 1999 + "  " + "b" * 2000,
            "a" * 1200 + "\n  " + "b" * 1200,
            "a" * 1200 + "。" + " b" * 1200,
        ]
        converter = LeetCodeNotionConverter()
        for original in examples:
            with self.subTest(length=len(original)):
                chunks = converter._split_text(original)
                self.assertEqual("".join(chunks), original)
                self.assertTrue(all(0 < len(chunk) <= 2000 for chunk in chunks))

    def test_empty_and_limit_boundaries(self):
        converter = LeetCodeNotionConverter()
        for original in ("", "x" * 2000, "x" * 2001):
            self.assertEqual("".join(converter._split_text(original)), original)


if __name__ == "__main__":
    unittest.main()
