import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inject import inject_markdown  # noqa: E402

DOC = """\
Intro paragraph.

[Figure 1]

Figure 1: Five functional properties.

Body text mentioning (Figure 1) inline.

[Figure 2]

Figure 2: Second figure.
"""


class TestInjectMarkdown(unittest.TestCase):
    def setUp(self):
        self.images = {1: "figures/paper/fig-01.png", 2: "figures/paper/fig-02.png"}
        self.out = inject_markdown(DOC, self.images)

    def test_placeholders_become_images(self):
        self.assertIn("![Figure 1](figures/paper/fig-01.png)", self.out)
        self.assertIn("![Figure 2](figures/paper/fig-02.png)", self.out)

    def test_bare_placeholders_are_gone(self):
        self.assertNotIn("\n[Figure 1]\n", self.out)
        self.assertNotIn("\n[Figure 2]\n", self.out)

    def test_captions_untouched(self):
        self.assertIn("Figure 1: Five functional properties.", self.out)
        self.assertIn("Figure 2: Second figure.", self.out)

    def test_inline_mentions_untouched(self):
        self.assertIn("Body text mentioning (Figure 1) inline.", self.out)

    def test_line_count_unchanged(self):
        self.assertEqual(len(DOC.split("\n")), len(self.out.split("\n")))

    def test_missing_image_leaves_placeholder(self):
        out = inject_markdown(DOC, {1: "figures/paper/fig-01.png"})
        self.assertIn("![Figure 1](figures/paper/fig-01.png)", out)
        self.assertIn("[Figure 2]", out)


if __name__ == "__main__":
    unittest.main()
