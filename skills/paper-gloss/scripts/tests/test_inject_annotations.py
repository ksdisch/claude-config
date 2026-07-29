import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inject_annotations import (  # noqa: E402
    check_page,
    derive_slug,
    embed_assets,
    set_slug,
    stamp_ids,
)

FIXTURE = """<!doctype html>
<html><head><title>T</title><style>:root { --fg: #111; }</style></head>
<body>
<h2>Heading</h2>
<p>alpha paragraph</p>
<p id="keep-me">beta paragraph</p>
<pre class="equation" data-math-verbatim="1">$x$</pre>
<ul><li>an item</li></ul>
<dl><dt><span class="math"><i>Q</i></span></dt><dd>the queries</dd></dl>
</body></html>
"""


class TestStampIds(unittest.TestCase):
    def setUp(self):
        self.out, self.added = stamp_ids(FIXTURE)

    def test_stamps_every_block(self):
        # h2, BOTH p (including the one carrying its own id), li, dd
        self.assertEqual(self.added, 5)
        for frag in ('<h2 data-pg-block="pg-p-0001">',
                     '<p data-pg-block="pg-p-0002">',
                     '<p data-pg-block="pg-p-0003" id="keep-me">',
                     '<li data-pg-block="pg-p-0004">',
                     '<dd data-pg-block="pg-p-0005">'):
            self.assertIn(frag, self.out)

    def test_existing_id_preserved(self):
        # ids are never the marker: real pages have 77/79 headings and all
        # footnotes already carrying ids, and those must stay annotatable
        self.assertIn('id="keep-me"', self.out)

    def test_pre_is_not_stamped(self):
        self.assertIn('<pre class="equation" data-math-verbatim="1">', self.out)
        self.assertNotIn('<pre data-pg-block=', self.out)

    def test_dt_is_not_stamped(self):
        self.assertIn("<dt>", self.out)

    def test_idempotent(self):
        again, added = stamp_ids(self.out)
        self.assertEqual(added, 0)
        self.assertEqual(again, self.out)

    def test_numbering_continues_past_existing_markers(self):
        doc = '<body><p data-pg-block="pg-p-0007">a</p><p>b</p></body>'
        out, added = stamp_ids(doc)
        self.assertEqual(added, 1)
        self.assertIn('<p data-pg-block="pg-p-0008">b</p>', out)

    def test_ignores_block_lookalikes_inside_scripts(self):
        # The runtime JS (and GLOSS_TERMS) contain strings like '<h2>…</h2>';
        # stamping inside a <script> span would corrupt the JS and break
        # idempotency on a second run.
        doc = ('<body><script>var s = "<p>fake</p><h2>x</h2>";</script>'
               '<p>real</p></body>')
        out, added = stamp_ids(doc)
        self.assertEqual(added, 1)
        self.assertIn('<script>var s = "<p>fake</p><h2>x</h2>";</script>', out)
        self.assertIn('<p data-pg-block="pg-p-0001">real</p>', out)


class TestSlug(unittest.TestCase):
    def test_derive_slug(self):
        self.assertEqual(
            derive_slug("/x/y/forge-gap-eli5-glossed.html"), "forge-gap"
        )

    def test_derive_slug_without_suffix_uses_stem(self):
        self.assertEqual(derive_slug("/x/oddball.html"), "oddball")

    def test_set_slug_adds_attribute(self):
        out = set_slug("<body>\n<p>x</p></body>", "forge-gap")
        self.assertIn('<body data-pg-slug="forge-gap">', out)

    def test_set_slug_replaces_existing(self):
        out = set_slug('<body data-pg-slug="old" class="c">x</body>', "new")
        self.assertIn('data-pg-slug="new"', out)
        self.assertNotIn('data-pg-slug="old"', out)
        self.assertIn('class="c"', out)


class TestEmbed(unittest.TestCase):
    CSS = ".pg-hl { background: gold; }"
    JS = "window.closeAnnotationUI = function () {};"

    def test_embeds_both_blocks_once(self):
        out = embed_assets(FIXTURE, self.CSS, self.JS)
        self.assertEqual(out.count('<style id="pg-annot-css">'), 1)
        self.assertEqual(out.count('<script id="pg-annot-js">'), 1)
        self.assertLess(out.index("pg-annot-css"), out.index("</head>"))
        self.assertLess(out.index("pg-annot-js"), out.index("</body>"))

    def test_rerun_replaces_not_duplicates(self):
        once = embed_assets(FIXTURE, self.CSS, self.JS)
        twice = embed_assets(once, ".pg-hl { background: red; }", self.JS)
        self.assertEqual(twice.count('<style id="pg-annot-css">'), 1)
        self.assertIn("background: red", twice)
        self.assertNotIn("background: gold", twice)


class TestCheck(unittest.TestCase):
    CSS = ".pg-hl { background: gold; }"
    JS = "window.closeAnnotationUI = function () {};"

    def full(self):
        out, _ = stamp_ids(FIXTURE)
        out = set_slug(out, "t-paper")
        return embed_assets(out, self.CSS, self.JS)

    def test_clean_page_passes(self):
        self.assertEqual(check_page(self.full()), [])

    def test_raw_page_fails_with_named_problems(self):
        problems = check_page(FIXTURE)
        joined = " ".join(problems)
        self.assertIn("pg-annot-css", joined)
        self.assertIn("pg-annot-js", joined)
        self.assertIn("data-pg-slug", joined)
        self.assertIn("unstamped", joined)


if __name__ == "__main__":
    unittest.main()
