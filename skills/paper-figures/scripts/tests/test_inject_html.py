import base64
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inject_html import caption_of, data_uri, inject_html, lightbox_js  # noqa: E402

# Minimal DOM sufficient to run the emitted lightbox script under node.
STUB_DOM = """
const els = {};
function mk(id) {
  return {
    id, hidden: true,
    setAttribute() {}, removeAttribute() {},
    classList: { remove() {}, add() {} },
    querySelector() { return { src: '', alt: '', removeAttribute() {} }; },
  };
}
['gloss-popover', 'gloss-panel', 'gloss-backdrop', 'gloss-panel-toggle',
 'figure-lightbox'].forEach(id => { els[id] = mk(id); });
globalThis.document = {
  getElementById: id => els[id] || null,
  querySelectorAll: () => [],
  addEventListener: () => {},
};
globalThis.window = globalThis;
"""

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

    def test_close_logic_never_aggregates_across_surfaces(self):
        """Node-independent guard, so the real check below cannot silently skip
        a machine into a green run.

        Every form of the F5 defect works the same way: compute something over
        ALL surfaces, then let it suppress an individual surface's fallback.
        The per-surface loop therefore must not aggregate — no `.some(`,
        `.every(`, or `.filter(` over the table inside closeGlossSurfaces."""
        js = lightbox_js()
        body = re.search(r"function closeGlossSurfaces\(\) \{(.*?)\n  \}", js, re.S)
        self.assertIsNotNone(body, "closeGlossSurfaces must be present and parseable")
        for agg in (".some(", ".every(", ".filter(", ".reduce("):
            self.assertNotIn(
                agg, body.group(1),
                f"aggregating with {agg} across GLOSS_SURFACES is how F5 recurs: "
                "one surface's state must never gate another's fallback")

    def test_one_missing_hook_still_closes_the_other_surface(self):
        """Executes the REAL emitted closeGlossSurfaces() against a stub DOM.

        Asserting on a Python re-implementation of the loop, or grepping the
        generated JS for the string `viaHooks`, both pass against a clean
        reintroduction of the defect under any other variable name. The only
        test that can actually fail is one that runs the shipped code.

        node is a test-only dependency and is not required to use the skill;
        when it is absent this skips and the structural guard above still
        stands."""
        node = shutil.which("node")
        if not node:
            self.skipTest("node unavailable — structural guard still applies")

        js = lightbox_js()
        script = (
            STUB_DOM
            # the failure page: exports the popover hook, NOT the panel hook
            + "window.closeGlossPopover = function () "
              "{ document.getElementById('gloss-popover').hidden = true; };\n"
            + js.replace("<script>", "").replace("</script>", "")
            + "\n"
            "document.getElementById('gloss-popover').hidden = false;\n"
            "document.getElementById('gloss-panel').hidden = false;\n"
            "document.getElementById('gloss-backdrop').hidden = false;\n"
            "window.closeGlossSurfaces();\n"
            "console.log(JSON.stringify({\n"
            "  popover: document.getElementById('gloss-popover').hidden,\n"
            "  panel: document.getElementById('gloss-panel').hidden,\n"
            "  backdrop: document.getElementById('gloss-backdrop').hidden,\n"
            "}));\n"
        )
        proc = subprocess.run([node, "-e", script], capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        state = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertTrue(state["popover"], "popover must close via its exported hook")
        self.assertTrue(state["panel"],
                        "panel must close via its own DOM fallback when its hook is absent")
        self.assertTrue(state["backdrop"], "the panel's backdrop must close with it")

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
