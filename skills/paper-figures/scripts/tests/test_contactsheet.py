import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contactsheet import build_sheet  # noqa: E402


class TestContactSheet(unittest.TestCase):
    def setUp(self):
        d = os.path.dirname(__file__)
        self.p = os.path.join(d, "_cs.png")
        with open(self.p, "wb") as fh:
            fh.write(b"\x89PNG\r\n\x1a\n" + b"data" * 10)
        self.entries = [
            {"num": 1, "path": self.p, "caption": "First figure.", "verdict": "pass"},
            {"num": 2, "path": self.p, "caption": "Second & <odd>.", "verdict": "fail",
             "reason": "blank or unrendered"},
            {"num": 3, "path": None, "caption": "Not captured.", "verdict": "missing",
             "reason": "no static asset and screenshot failed"},
        ]
        self.out = build_sheet(self.entries, "Test Paper")

    def tearDown(self):
        os.remove(self.p)

    def test_every_entry_appears(self):
        for n in (1, 2, 3):
            self.assertIn(f"Figure {n}", self.out)

    def test_captured_figures_are_inlined(self):
        self.assertEqual(self.out.count("data:image/png;base64,"), 2)

    def test_failures_are_visibly_marked(self):
        self.assertIn("blank or unrendered", self.out)
        self.assertIn('class="entry fail"', self.out)

    def test_missing_figure_has_no_img(self):
        self.assertIn('class="entry missing"', self.out)
        self.assertIn("no static asset and screenshot failed", self.out)

    def test_captions_are_escaped(self):
        self.assertIn("Second &amp; &lt;odd&gt;.", self.out)
        self.assertNotIn("<odd>", self.out)

    def test_summary_counts_are_present(self):
        self.assertIn("3 figures", self.out)
        self.assertIn("1 pass", self.out)

    def test_thumbnails_are_downscaled_not_inlined_whole(self):
        """The sheet exists to be small enough to send. Inlining the originals
        produced a 26MB file on a 94-figure paper, so a real capture must come
        out materially smaller than inlining it verbatim."""
        import shutil
        import tempfile
        src = os.path.join(os.path.dirname(__file__), "_cs_big.png")
        # a real PNG sips can actually resample: 1200x800 of RGB noise
        try:
            subprocess = __import__("subprocess")
            if not shutil.which("sips"):
                self.skipTest("sips unavailable")
            subprocess.run(
                ["sips", "-s", "format", "png", "-z", "800", "1200",
                 "/System/Library/CoreServices/DefaultDesktop.heic", "--out", src],
                capture_output=True, check=True)
        except Exception:
            self.skipTest("could not synthesise a resamplable source image")
        try:
            entries = [{"num": 1, "path": src, "caption": "big", "verdict": "pass"}]
            with tempfile.TemporaryDirectory() as tmp:
                small = build_sheet(entries, "T", 320, tmp)
            whole = build_sheet(entries, "T", 0, None)
            self.assertLess(len(small), len(whole) / 2,
                            "thumbnail sheet should be far smaller than inlining originals")
        finally:
            if os.path.exists(src):
                os.remove(src)


if __name__ == "__main__":
    unittest.main()
