import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from webfigs import build_manifest  # noqa: E402

PAGE = """\
<p>prose</p>
<figure data-fignum="1" id="fig-props" class='wide'><div class='intro-functional'></div>
<figcaption><span class="fig-num">Figure 1: </span>Five functional properties.</figcaption></figure>
<p>more prose</p>
<figure data-fignum="4" id="fig-jlens"><img src="./png/img_abc.png" alt="">
<figcaption><span class="fig-num">Figure 4: </span>The Jacobian lens.</figcaption></figure>
"""

BASE = "https://transformer-circuits.pub/2026/workspace/index.html"


class TestBuildManifest(unittest.TestCase):
    def setUp(self):
        self.figs = {f["num"]: f for f in build_manifest(PAGE, BASE)}

    def test_finds_every_figure(self):
        self.assertEqual(sorted(self.figs), [1, 4])

    def test_classifies_interactive(self):
        self.assertEqual(self.figs[1]["kind"], "interactive")
        self.assertIsNone(self.figs[1]["img_url"])

    def test_classifies_static_and_resolves_relative_url(self):
        self.assertEqual(self.figs[4]["kind"], "static")
        self.assertEqual(
            self.figs[4]["img_url"],
            "https://transformer-circuits.pub/2026/workspace/png/img_abc.png",
        )

    def test_selector_is_attribute_based(self):
        self.assertEqual(self.figs[1]["selector"], 'figure[data-fignum="1"]')

    def test_extracts_caption_without_the_fig_num_prefix(self):
        self.assertEqual(self.figs[1]["caption"], "Five functional properties.")


if __name__ == "__main__":
    unittest.main()
