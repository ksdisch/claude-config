import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ledger import build_ledger  # noqa: E402

PLAIN = """\
Some prose paragraph.

[Figure 1]

Figure 1: Five functional properties of a global workspace.

More prose.
"""

WITH_IMAGE = """\
![Figure 4](https://example.com/png/img_abc.png)

Figure 4: The Jacobian lens.
"""


class TestBuildLedger(unittest.TestCase):
    def test_plain_placeholder(self):
        entries = build_ledger(PLAIN)
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual(e["num"], 1)
        self.assertIsNone(e["existing_url"])
        self.assertEqual(
            e["caption"], "Five functional properties of a global workspace."
        )

    def test_image_placeholder_keeps_url(self):
        entries = build_ledger(WITH_IMAGE)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["num"], 4)
        self.assertEqual(
            entries[0]["existing_url"], "https://example.com/png/img_abc.png"
        )
        self.assertEqual(entries[0]["caption"], "The Jacobian lens.")

    def test_line_index_points_at_placeholder(self):
        entries = build_ledger(PLAIN)
        self.assertEqual(PLAIN.split("\n")[entries[0]["line"]], "[Figure 1]")

    def test_inline_figure_reference_is_not_a_slot(self):
        # "(Figure 5)" inside prose must not create a ledger entry
        entries = build_ledger("We show this in prose (Figure 5) here.\n")
        self.assertEqual(entries, [])


if __name__ == "__main__":
    unittest.main()
