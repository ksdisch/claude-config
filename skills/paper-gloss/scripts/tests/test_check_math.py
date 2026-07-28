import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from check_math import find_hits, looks_like_math, main as check_main, scannable  # noqa: E402


def page(body):
    return (
        "<!doctype html><html><head><title>T</title></head><body>\n"
        + body
        + "\n</body></html>\n"
    )


class TestRenderedMathIsClean(unittest.TestCase):
    """Tier 1 and Tier 2 output must not trip the gate that exists to catch
    their absence — a checker that flags correct output is worse than none."""

    def test_tier1_unicode_html_is_clean(self):
        html = page(
            '<p>there are <span class="math"><i>n</i><sub>vocab</sub></span> vectors '
            'in <span class="math"><i>d</i><sub>model</sub></span>-dimensional space, '
            'with <span class="math"><i>n</i><sub>vocab</sub> &gt; '
            '<i>d</i><sub>model</sub></span>.</p>'
        )
        self.assertEqual(find_hits(html), [])

    def test_tier2_mathml_is_clean(self):
        html = page(
            '<div class="scroll-x"><math display="block"><mrow><mi>a</mi><mo>=</mo>'
            "<mfrac><mn>1</mn><mi>k</mi></mfrac></mrow></math></div>"
        )
        self.assertEqual(find_hits(html), [])

    def test_greek_and_relations_as_characters_are_clean(self):
        html = page('<p>where <span class="math">α ≤ β ∈ ℝ</span> holds.</p>')
        self.assertEqual(find_hits(html), [])


class TestResidualTexIsCaught(unittest.TestCase):
    def test_the_reported_bug(self):
        """The literal §2.3 text that shipped to a reader."""
        html = page(r"<p>there are $n_{\text{vocab}}$ vectors (one per token)</p>")
        hits = find_hits(html)
        self.assertEqual(len(hits), 1)
        self.assertIn("inline-dollars", hits[0]["kinds"])

    def test_one_expression_reports_as_one_hit_not_four(self):
        r"""`$n_{\text{vocab}}$` trips inline-dollars, braced-sub-superscript,
        and macro-with-argument at once. Counting regex matches instead of
        merged spans would inflate one missed variable into three or four, and
        an inflated count is the same lie as a manifest count."""
        html = page(r"<p>with $n_{\text{vocab}} > d_{\text{model}}$ we get more.</p>")
        hits = find_hits(html)
        self.assertEqual(len(hits), 1, hits)
        self.assertGreater(len(hits[0]["kinds"]), 1, "the merged hit keeps every reason")

    def test_two_separate_expressions_on_one_line_are_two_hits(self):
        html = page("<p>compare $a$ against $b$ directly</p>")
        self.assertEqual(len(find_hits(html)), 2)

    def test_display_dollars(self):
        self.assertEqual(len(find_hits(page("<p>$$a = b$$</p>"))), 1)

    def test_latex_delimiters(self):
        self.assertEqual(len(find_hits(page(r"<p>the value \(x\) is fixed</p>"))), 2)

    def test_bare_macro_outside_dollars(self):
        self.assertEqual(len(find_hits(page(r"<p>summed with \sum over i</p>"))), 1)

    def test_untriaged_equation_pre_is_scanned(self):
        r"""A `<pre class="equation">` with no `data-math-verbatim="1"` is an
        equation nobody triaged. Exempting every `<pre>` would let the exact
        construct this gate exists for pass silently."""
        html = page(r'<pre class="equation">a = \frac{1}{2}</pre>')
        self.assertEqual(len(find_hits(html)), 1)

    def test_line_numbers_are_true_to_the_original_file(self):
        html = page("<p>one</p>\n<p>two</p>\n" + r"<p>$x_{i}$</p>")
        hits = find_hits(html)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["line"], 4)  # doctype line, one, two, then the hit
        self.assertIn("$x_{i}$", hits[0]["context"])


class TestFalsePositiveDiscipline(unittest.TestCase):
    """A gate that cries wolf gets ignored, and an ignored gate is how the
    original bug shipped. Each of these must stay silent."""

    def test_a_single_currency_amount(self):
        self.assertEqual(find_hits(page("<p>roughly $5M in compute</p>")), [])

    def test_two_currency_amounts_on_one_line(self):
        """The naive `$…$` pair rule reads 'and' as a math body. The
        no-whitespace-inside-the-delimiters rule is what rejects it."""
        self.assertEqual(find_hits(page("<p>we spent $5M and $8M on training</p>")), [])

    def test_a_price_range(self):
        self.assertEqual(find_hits(page("<p>between $100 and $200 per run</p>")), [])

    def test_tex_inside_a_code_element(self):
        html = page(r"<p>write <code>\frac{a}{b}</code> to get a fraction</p>")
        self.assertEqual(find_hits(html), [])

    def test_dollars_and_braces_inside_a_script(self):
        html = page(
            '<script>const GLOSS_TERMS = {"a_{b}": {term: "$5", expansion: "x_{i}"}};</script>'
        )
        self.assertEqual(find_hits(html), [])

    def test_the_references_section_is_not_scanned(self):
        html = page(r"<h2>References</h2><p>Smith et al. On $L_{p}$ norms. 2023.</p>")
        self.assertEqual(find_hits(html), [])

    def test_prose_before_references_is_still_scanned(self):
        html = page(r"<p>see $x_{i}$ above</p><h2>References</h2><p>Smith $y_{j}$</p>")
        self.assertEqual(len(find_hits(html)), 1)

    def test_an_underscore_in_prose_is_not_math(self):
        html = page("<p>the file is named some_name and the flag is --no_cache</p>")
        self.assertEqual(find_hits(html), [])


class TestVerbatimFallback(unittest.TestCase):
    def test_a_marked_verbatim_block_is_permitted(self):
        html = page(
            r'<pre class="equation" data-math-verbatim="1">'
            r"\mathcal{L} = \mathbb{E}_{x}\left[ f(x) \right]</pre>"
        )
        self.assertEqual(find_hits(html), [])

    def test_verbatim_blocks_are_counted_for_the_report(self):
        html = page(
            r'<pre class="equation" data-math-verbatim="1">\frac{a}{b}</pre>'
            r'<pre class="equation" data-math-verbatim="1">\sum_i x_i</pre>'
        )
        d = tempfile.mkdtemp()
        try:
            src, out = os.path.join(d, "p.html"), os.path.join(d, "hits.json")
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(html)
            rc = check_main([src, "-o", out])
            with open(out) as fh:
                payload = json.load(fh)
            self.assertEqual(rc, 0)
            self.assertEqual(payload["found"], 0)
            self.assertEqual(payload["verbatim_blocks"], 2)
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TestExitCode(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def _write(self, html):
        p = os.path.join(self.d, "p.html")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(html)
        return p

    def test_clean_page_exits_zero(self):
        self.assertEqual(check_main([self._write(page("<p><i>k</i> vectors</p>"))]), 0)

    def test_dirty_page_exits_nonzero(self):
        p = self._write(page(r"<p>$n_{\text{vocab}}$ vectors</p>"))
        self.assertNotEqual(check_main([p]), 0, "a page with unrendered math must not pass")

    def test_reported_count_matches_the_hits_actually_found(self):
        """inject.py:60 prints a manifest count rather than what it did, so
        skipped work reports as success. This gate must never acquire the same
        habit — the number printed is len(hits), nothing declared upfront."""
        p = self._write(page("<p>$a$ and $b$ and $c$</p>"))
        out = os.path.join(self.d, "hits.json")
        check_main([p, "-o", out])
        with open(out) as fh:
            payload = json.load(fh)
        self.assertEqual(payload["found"], len(payload["hits"]))
        self.assertEqual(payload["found"], 3)


class TestHelpers(unittest.TestCase):
    def test_scannable_preserves_offsets(self):
        html = "<p>ab</p>\n<p>cd</p>"
        blanked = scannable(html)
        self.assertEqual(len(blanked), len(html))
        self.assertEqual(blanked.count("\n"), html.count("\n"))

    def test_looks_like_math(self):
        self.assertTrue(looks_like_math(r"n_{\text{vocab}}"))
        self.assertTrue(looks_like_math("k"))
        self.assertFalse(looks_like_math("100"))
        self.assertFalse(looks_like_math("a much longer sentence fragment"))


if __name__ == "__main__":
    unittest.main()
