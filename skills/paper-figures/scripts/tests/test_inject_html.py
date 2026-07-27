import base64
import json
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inject_html import caption_of, data_uri, inject_html, lightbox_js  # noqa: E402

DOC = """\
<html><head><style>:root { --fg: #111; }</style></head><body>
<p>prose</p>
<div class="figure-placeholder">[Figure 1] — Figure 1: Five functional properties.</div>
<div class="figure-placeholder">[Figure 4] — Figure 4: The Jacobian lens. <span class="img-note">(image available at https://example.com/a.png)</span></div>
</body></html>
"""


class TestCaption(unittest.TestCase):
    def test_strips_the_bracket_lead_in(self):
        self.assertEqual(
            caption_of("[Figure 1] — Figure 1: Five functional properties."),
            "Figure 1: Five functional properties.",
        )

    def test_accepts_an_entity_encoded_dash(self):
        # A glossed file that entity-escapes the separator must still parse,
        # otherwise the figure is silently dropped.
        for sep in ("&mdash;", "&#8212;", "--", "-", "–"):
            with self.subTest(sep=sep):
                self.assertEqual(
                    caption_of(f"[Figure 1] {sep} Figure 1: A caption."),
                    "Figure 1: A caption.",
                )

    def test_drops_the_img_note_span(self):
        raw = '[Figure 4] — Figure 4: The lens. <span class="img-note">(image available at http://x/a.png)</span>'
        self.assertEqual(caption_of(raw), "Figure 4: The lens.")


class TestDataURI(unittest.TestCase):
    def test_png_mime(self):
        path = os.path.join(os.path.dirname(__file__), "_u.png")
        with open(path, "wb") as fh:
            fh.write(b"\x89PNG\r\n\x1a\n" + b"0" * 40)
        try:
            uri = data_uri(path)
            self.assertTrue(uri.startswith("data:image/png;base64,"))
            self.assertIn(base64.b64encode(b"\x89PNG")[:6].decode(), uri)
        finally:
            os.remove(path)

    def test_jpeg_mime(self):
        path = os.path.join(os.path.dirname(__file__), "_u.jpg")
        with open(path, "wb") as fh:
            fh.write(b"\xff\xd8\xff" + b"0" * 40)
        try:
            self.assertTrue(data_uri(path).startswith("data:image/jpeg;base64,"))
        finally:
            os.remove(path)


class TestInjectHTML(unittest.TestCase):
    def setUp(self):
        d = os.path.dirname(__file__)
        self.p1 = os.path.join(d, "_f1.png")
        self.p4 = os.path.join(d, "_f4.png")
        for p in (self.p1, self.p4):
            with open(p, "wb") as fh:
                fh.write(b"\x89PNG\r\n\x1a\n" + os.path.basename(p).encode() * 5)
        self.out = inject_html(DOC, {1: self.p1, 4: self.p4})

    def tearDown(self):
        for p in (self.p1, self.p4):
            if os.path.exists(p):
                os.remove(p)

    def test_placeholders_replaced(self):
        self.assertNotIn("figure-placeholder", self.out)
        self.assertEqual(self.out.count('<figure class="paper-figure"'), 2)

    def test_images_are_data_uris(self):
        self.assertEqual(self.out.count('src="data:image/png;base64,'), 2)

    def test_no_external_sources_remain(self):
        self.assertNotIn('src="http', self.out)
        self.assertNotIn("img-note", self.out)

    def test_alt_text_is_the_caption(self):
        self.assertIn('alt="Figure 1: Five functional properties."', self.out)

    def test_figcaption_present(self):
        self.assertIn("<figcaption>Figure 1: Five functional properties.</figcaption>", self.out)

    def test_css_and_lightbox_injected_once(self):
        self.assertEqual(self.out.count(".paper-figure {"), 1)
        self.assertEqual(self.out.count('id="figure-lightbox"'), 1)

    def test_unmapped_figure_keeps_its_placeholder(self):
        out = inject_html(DOC, {1: self.p1})
        self.assertIn("[Figure 4]", out)
        self.assertEqual(out.count('<figure class="paper-figure"'), 1)

    def test_every_gloss_surface_has_both_a_hook_and_its_own_fallback(self):
        """Glossed pages generated before paper-gloss exported
        window.closeGlossPopover / closeGlossPanel keep those functions private
        to an IIFE, and a page may export one hook without the other. Each
        surface must therefore carry its own fallback, independent of whether a
        *different* surface's hook happened to exist."""
        from inject_html import GLOSS_SURFACES
        self.assertGreaterEqual(len(GLOSS_SURFACES), 2)
        for s in GLOSS_SURFACES:
            self.assertTrue(s["hook"], "each surface needs an exported-hook name")
            self.assertTrue(s["ids"] or s.get("classes"),
                            f"{s['hook']} has no DOM fallback of its own")

    def test_no_shared_flag_gates_the_per_surface_fallbacks(self):
        """The original defect: one `viaHooks` boolean set by either hook
        suppressed the fallback for BOTH surfaces."""
        js = lightbox_js()
        self.assertNotIn("viaHooks", js)
        # the hook is looked up per surface, not as two hard-coded calls
        self.assertIn("window[surface.hook]", js)

    def test_one_missing_hook_still_closes_the_other_surface(self):
        """Simulate the emitted logic against a page that exports only the
        popover hook: the panel must still be hidden via its own fallback."""
        surfaces = json.loads(
            re.search(r"var GLOSS_SURFACES = (\[.*?\]);", lightbox_js(), re.S).group(1)
        )
        exported = {"closeGlossPopover"}          # panel hook absent
        hidden, called = set(), set()
        for s in surfaces:                        # mirrors closeGlossSurfaces()
            if s["hook"] in exported:
                called.add(s["hook"])
                continue
            hidden.update(s["ids"])
        self.assertIn("closeGlossPopover", called)
        self.assertIn("gloss-panel", hidden,
                      "panel must fall back to the DOM when its hook is missing")
        self.assertIn("gloss-backdrop", hidden)

    def test_fallback_ids_match_the_markup_paper_gloss_specifies(self):
        """The fallback drives ids by name, so they must exist in the sibling
        skill's spec — a typo or an undocumented id fails silently in a browser."""
        gloss = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "..", "..", "paper-gloss", "SKILL.md")
        if not os.path.exists(gloss):
            self.skipTest("paper-gloss/SKILL.md not present")
        with open(gloss, encoding="utf-8") as fh:
            spec = fh.read()
        from inject_html import GLOSS_SURFACES
        for s in GLOSS_SURFACES:
            for el in s["ids"] + s.get("expanded", []):
                self.assertIn(el, spec,
                              f"#{el} is driven by the lightbox but undocumented in paper-gloss")


if __name__ == "__main__":
    unittest.main()
