import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from entries import build_entries, index_checks, index_figures  # noqa: E402

LEDGER = [
    {"num": 1, "caption": "First figure."},
    {"num": 2, "caption": "Second figure."},
    {"num": 3, "caption": "Third figure."},
]


class TestIndexFigures(unittest.TestCase):
    def _dir(self, names):
        d = tempfile.mkdtemp()
        for n in names:
            open(os.path.join(d, n), "wb").close()
        return d

    def test_maps_zero_padded_names_to_ints(self):
        d = self._dir(["fig-01.png", "fig-47.png"])
        self.assertEqual(sorted(index_figures(d)), [1, 47])

    def test_accepts_jpeg_variants(self):
        d = self._dir(["fig-02.jpg", "fig-03.jpeg"])
        self.assertEqual(sorted(index_figures(d)), [2, 3])

    def test_ignores_unrelated_files(self):
        d = self._dir(["fig-01.png", "notes.txt", "sheet.html", "fig-x.png"])
        self.assertEqual(sorted(index_figures(d)), [1])

    def test_missing_directory_is_not_an_error(self):
        self.assertEqual(index_figures("/nonexistent/figures/dir"), {})


class TestIndexChecks(unittest.TestCase):
    def test_pulls_verdict_and_reason_by_figure_number(self):
        checks = {
            "results": [
                {"path": "/x/fig-01.png", "verdict": "pass", "reason": ""},
                {"path": "/x/fig-02.png", "verdict": "fail", "reason": "blank"},
            ]
        }
        self.assertEqual(index_checks(checks)[2], ("fail", "blank"))

    def test_none_payload_yields_empty_map(self):
        self.assertEqual(index_checks(None), {})


class TestBuildEntries(unittest.TestCase):
    def test_every_ledger_slot_produces_an_entry(self):
        out = build_entries(LEDGER, {}, {})
        self.assertEqual([e["num"] for e in out], [1, 2, 3])

    def test_uncaptured_figure_is_marked_missing_not_dropped(self):
        # The ledger contract forbids silently losing a slot.
        out = build_entries(LEDGER, {1: "/x/fig-01.png"}, {})
        self.assertEqual(out[1]["verdict"], "missing")
        self.assertIsNone(out[1]["path"])

    def test_captured_figure_carries_its_check_verdict(self):
        out = build_entries(
            LEDGER, {2: "/x/fig-02.png"}, {2: ("fail", "blank or unrendered")}
        )
        self.assertEqual(out[1]["verdict"], "fail")
        self.assertEqual(out[1]["reason"], "blank or unrendered")

    def test_captured_but_unchecked_defaults_to_pass(self):
        out = build_entries(LEDGER, {3: "/x/fig-03.png"}, {})
        self.assertEqual(out[2]["verdict"], "pass")

    def test_caption_comes_from_the_ledger(self):
        out = build_entries(LEDGER, {}, {})
        self.assertEqual(out[0]["caption"], "First figure.")

    def test_deliberate_skip_reason_is_surfaced(self):
        ledger = [{"num": 1, "caption": "c", "skip_reason": "no static asset"}]
        out = build_entries(ledger, {}, {})
        self.assertEqual(out[0]["verdict"], "missing")
        self.assertEqual(out[0]["reason"], "no static asset")


if __name__ == "__main__":
    unittest.main()
