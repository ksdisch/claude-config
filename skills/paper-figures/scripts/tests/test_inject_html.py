import base64
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inject_html import caption_of, data_uri, inject_html  # noqa: E402

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


if __name__ == "__main__":
    unittest.main()
