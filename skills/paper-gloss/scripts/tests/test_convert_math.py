"""Tests for convert_math.py.

Three groups matter most:
  * the contract table — every Tier 1 row of references/math-rendering.md
    must come out byte-identical, because that file is the spec;
  * the refusals — a timid converter is the whole design, so "did not touch
    it" is asserted as carefully as "converted it";
  * the regressions — each one is a way this actually broke a real page.
"""
import os
import sys
import unittest
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from convert_math import apply_edits, convert_body, masked, plan  # noqa: E402


def page(body):
    return (
        "<!doctype html>\n<html><head><title>t</title>"
        "<style>.x{color:red}</style></head>\n<body>\n"
        f"{body}\n</body></html>\n"
    )


class TestContractTable(unittest.TestCase):
    """Every Tier 1 row of references/math-rendering.md, verbatim."""

    def test_single_letter_variable_is_italic(self):
        self.assertEqual(convert_body("k"), "<i>k</i>")

    def test_text_subscript_is_upright(self):
        self.assertEqual(convert_body(r"n_{\text{vocab}}"),
                         "<i>n</i><sub>vocab</sub>")

    def test_model_subscript(self):
        self.assertEqual(convert_body(r"d_{\text{model}}"),
                         "<i>d</i><sub>model</sub>")

    def test_subscript_offset_uses_a_real_minus(self):
        self.assertEqual(convert_body("h_{l-1}"), "<i>h</i><sub>l−1</sub>")
        self.assertIn("−", convert_body("h_{l-1}"))

    def test_superscript_digit_is_upright(self):
        self.assertEqual(convert_body("x^2"), "<i>x</i><sup>2</sup>")

    def test_sub_and_superscript_together(self):
        self.assertEqual(convert_body("W_Q^{(l)}"),
                         "<i>W</i><sub>Q</sub><sup>(l)</sup>")

    def test_relation_between_two_subscripted_variables(self):
        self.assertEqual(convert_body(r"n_{\text{vocab}} &gt; d_{\text{model}}"),
                         "<i>n</i><sub>vocab</sub> &gt; <i>d</i><sub>model</sub>")

    def test_blackboard_bold_with_superscript(self):
        self.assertEqual(convert_body(r"\mathbb{R}^d"), "ℝ<sup>d</sup>")


class TestTypography(unittest.TestCase):
    def test_greek_macro_becomes_the_character(self):
        self.assertEqual(convert_body(r"\alpha"), "α")

    def test_macro_terminating_space_is_consumed(self):
        """In TeX the space after a control word ends the name; it is not a
        space in the output. `\\langle v` is "⟨v", never "⟨ v"."""
        self.assertEqual(convert_body(r"\alpha x"), "α<i>x</i>")

    def test_no_padding_inside_fences(self):
        self.assertEqual(convert_body(r"\langle v_t, h_\ell \rangle"),
                         "⟨<i>v</i><sub>t</sub>, <i>h</i><sub>ℓ</sub>⟩")

    def test_binary_relation_gets_visible_space(self):
        self.assertEqual(convert_body("a = b"), "<i>a</i> = <i>b</i>")

    def test_script_letters_are_not_italicised(self):
        """The contract renders script text upright, so the subscript of
        `v_t` is a label `t`, not a nested <i>t</i>."""
        self.assertEqual(convert_body("v_t"), "<i>v</i><sub>t</sub>")

    def test_nested_braces_in_a_subscript(self):
        self.assertEqual(convert_body(r"h_{\text{final},t'}"),
                         "<i>h</i><sub>final,t′</sub>")


class TestRefusals(unittest.TestCase):
    """Refusing is a normal outcome. Each of these must stay untouched."""

    def test_fraction_is_tier_two(self):
        self.assertIsNone(convert_body(r"\frac{a}{b}"))

    def test_sum_with_limits_is_tier_two(self):
        self.assertIsNone(convert_body(r"\sum_i a_i"))

    def test_unknown_macro_is_refused(self):
        self.assertIsNone(convert_body(r"V^\dagger"))

    def test_raw_markup_in_the_body_is_refused(self):
        self.assertIsNone(convert_body('<button class="gloss-term">softmax</button>'))

    def test_unbalanced_brace_is_refused(self):
        self.assertIsNone(convert_body(r"x_{i"))


class TestCurrencyGuard(unittest.TestCase):
    """The converter must share the gate's judgement about what is money.

    Without it a prose price parses as arithmetic: `$5-$10` becomes
    `<span class="math">5−</span>10`, both `$` deleted and a number invented —
    and check_math, the <p> count and the term tally all still pass, so it
    reaches the reader looking like a clean conversion.
    """

    def _unchanged(self, body):
        html = page(f"<p>{body}</p>")
        edits, _, _ = plan(html)
        self.assertEqual(edits, [], f"should not have converted: {body}")
        self.assertEqual(apply_edits(html, edits), html)

    def test_a_tight_price_range_with_a_hyphen(self):
        self._unchanged("Inference runs $5-$10 per million tokens.")

    def test_a_tight_price_range_with_magnitudes(self):
        self._unchanged("Training cost $1M-$2M in compute.")

    def test_a_tight_price_range_with_a_slash(self):
        self._unchanged("Pricing is $100k/$1M for the tier.")

    def test_a_bare_number_in_dollars_is_money_not_math(self):
        self._unchanged("We paid $100$ for it.")

    def test_a_spaced_pair_of_amounts(self):
        self._unchanged("we spent $5M and $8M on training")

    def test_real_math_still_converts(self):
        """The guard must not buy safety with a miss — including for bodies
        past the gate's six-character acceptance ceiling, which is a detection
        heuristic and not a statement about what is convertible."""
        self.assertEqual(convert_body("k"), "<i>k</i>")
        self.assertEqual(convert_body("2x"), "2<i>x</i>")
        self.assertEqual(convert_body("x_i"), "<i>x</i><sub>i</sub>")
        self.assertEqual(convert_body("d = 768"), "<i>d</i> = 768")
        self.assertEqual(convert_body("N = 512"), "<i>N</i> = 512")
        self.assertEqual(convert_body("a + b = c"),
                         "<i>a</i> + <i>b</i> = <i>c</i>")
        self.assertEqual(convert_body("y = mx + b"),
                         "<i>y</i> = <i>m</i><i>x</i> + <i>b</i>")

    def test_letter_free_notation_is_never_silently_skipped(self):
        """The skipped bucket is outside the exit code AND invisible to the
        gate, so a wrong classification there is a silent ship — the one
        outcome this skill exists to prevent. Bodies with an operator are
        notation and must convert; a bare amount is ambiguous and must reach
        the worklist, never the skip pile."""
        for body, expect in [("1/8", "convert"), ("1 + 2 = 3", "convert"),
                             ("0.5", "worklist"), ("3.14", "worklist"),
                             ("100", "worklist"), ("1,000", "worklist")]:
            html = page(f"<p>value ${body}$ here</p>")
            edits, refused, skipped = plan(html)
            self.assertEqual(skipped, Counter(),
                             f"${body}$ must not be dropped from the exit code")
            if expect == "convert":
                self.assertEqual(len(edits), 1, f"${body}$ should convert")
            else:
                self.assertEqual(edits, [], f"${body}$ should not convert")
                self.assertEqual(sum(refused.values()), 1,
                                 f"${body}$ should reach the worklist")

    def test_money_is_skipped_not_filed_as_work(self):
        """A price is not math, so it is not the operator's worklist either.
        Filing it under "hand-author this by the ladder" invites exactly the
        manual corruption the guard exists to prevent — and pins the exit code
        at 1 forever on any page that quotes a cost."""
        html = page("<p>Inference runs $5-$10, training $1M-$2M.</p>")
        edits, refused, skipped = plan(html)
        self.assertEqual(edits, [])
        self.assertEqual(refused, Counter(), "money must not enter the worklist")
        self.assertEqual(sum(skipped.values()), 2)


class TestUprightWordsKeepTheirHyphen(unittest.TestCase):
    """U+2212 is a math rule. `\\text{}` holds ordinary words."""

    def test_cross_entropy(self):
        self.assertEqual(convert_body(r"\text{cross-entropy}"), "cross-entropy")

    def test_top_k(self):
        self.assertEqual(convert_body(r"\text{top-k}"), "top-k")

    def test_minus_is_still_a_minus_in_math(self):
        self.assertEqual(convert_body("h_{l-1}"), "<i>h</i><sub>l−1</sub>")


class TestSharedScopeWithTheGate(unittest.TestCase):
    """Two tools that disagree on scope hand the operator a failing gate and
    an empty worklist. These assert they agree."""

    def test_verbatim_tier_three_blocks_are_left_byte_identical(self):
        html = page('<pre class="equation" data-math-verbatim="1">'
                    r"$\mathcal{L}$ = stuff</pre>")
        edits, _, _ = plan(html)
        self.assertEqual(edits, [])
        self.assertEqual(apply_edits(html, edits), html)

    def test_numbered_references_cut_matches_the_gate(self):
        """Asserting no-hits on BOTH sides, not just no-edits: an edits==[]
        assertion alone passes whether the region was cut or merely had
        nothing convertible, so it cannot detect a divergence."""
        from check_math import find_hits
        html = page("<h2>7. References</h2>\n<p>Smith. On $L_p$ norms.</p>")
        edits, _, _ = plan(html)
        self.assertEqual(edits, [])
        self.assertEqual(find_hits(html), [])

    def test_unnumbered_references_cut_matches_the_gate(self):
        from check_math import find_hits
        html = page("<h2>References</h2>\n<p>Smith. On $L_p$ norms.</p>")
        self.assertEqual(plan(html)[0], [])
        self.assertEqual(find_hits(html), [])


class TestDisplayBlocksReachTheWorklist(unittest.TestCase):
    """Masked so their interiors are safe, but still reported — otherwise a
    page of untypeset display equations prints `refused: 0` and exits 0."""

    def test_a_display_block_is_counted_as_refused(self):
        html = page('<div class="scroll-x"><pre class="equation">$$\n'
                    r"a = \frac{b}{c}" "\n$$</pre></div>")
        edits, refused, _ = plan(html)
        self.assertEqual(edits, [])
        self.assertEqual(sum(refused.values()), 1)
        self.assertIn("$$", next(iter(refused)))

    def test_display_block_counted_even_alongside_a_convertible_span(self):
        html = page("<p>$k$</p>\n<pre>$$\na = b\n$$</pre>")
        edits, refused, _ = plan(html)
        self.assertEqual(len(edits), 1)
        self.assertEqual(sum(refused.values()), 1)


class TestDisplayCountingRespectsTheMasks(unittest.TestCase):
    """Counting `$$` over the raw string is F4's divergence with the sides
    swapped: the converter would pin exit 1 on a region the gate reports
    clean, and on a Tier 3 fallback the entry could never be cleared."""

    def _no_work(self, body):
        html = page(body)
        edits, refused, _ = plan(html)
        self.assertEqual(edits, [])
        self.assertEqual(refused, Counter(),
                         f"out-of-scope $$ must not become work: {body[:60]}")

    def test_dollars_inside_a_verbatim_block(self):
        self._no_work('<pre class="equation" data-math-verbatim="1">'
                      "$$\na = b\n$$</pre>")

    def test_dollars_inside_a_code_element(self):
        self._no_work("<p>write <code>$$a = b$$</code> for display</p>")

    def test_dollars_inside_a_script(self):
        self._no_work('<script>const s = "$$a = b$$";</script>')

    def test_dollars_after_the_references_heading(self):
        self._no_work("<h2>References</h2>\n<p>Smith. $$a = b$$</p>")

    def test_a_real_display_block_is_still_counted(self):
        """The intended population must survive the narrowing."""
        html = page('<div class="scroll-x"><pre class="equation">'
                    "$$\na = b\n$$</pre></div>")
        edits, refused, _ = plan(html)
        self.assertEqual(edits, [])
        self.assertEqual(sum(refused.values()), 1)


class TestMasking(unittest.TestCase):
    def test_masking_preserves_length_and_line_numbers(self):
        html = page("<p>one</p>\n<script>var a = 1;</script>\n<p>two</p>")
        self.assertEqual(len(masked(html)), len(html))
        self.assertEqual(masked(html).count("\n"), html.count("\n"))

    def test_script_bodies_are_not_converted(self):
        html = page('<script>const T = {"a": "$k$"};</script>')
        edits, _, _ = plan(html)
        self.assertEqual(edits, [])

    def test_code_elements_are_not_converted(self):
        html = page(r"<p>write <code>$x_i$</code> for that</p>")
        edits, _, _ = plan(html)
        self.assertEqual(edits, [])

    def test_references_section_is_not_converted(self):
        html = page("<h2>References</h2>\n<p>Smith. On $L_p$ norms.</p>")
        edits, _, _ = plan(html)
        self.assertEqual(edits, [])

    def test_a_numbered_references_heading_also_cuts(self):
        html = page("<h2>7. References</h2>\n<p>Smith. On $L_p$ norms.</p>")
        edits, _, _ = plan(html)
        self.assertEqual(edits, [])


class TestRegressions(unittest.TestCase):
    """Each of these broke a real page before it was fixed."""

    def test_math_inside_an_attribute_is_never_converted(self):
        """The converter once matched `$…$` inside an <img alt="...">, which
        injected a <span> into an attribute value and broke the tag. The gate
        cannot catch it: check_math.py blanks tags before scanning, so
        attributes are outside its reach entirely."""
        html = page(r'<figure><img src="x.png" alt="The lens $W_U J_\ell$."></figure>')
        edits, _, _ = plan(html)
        self.assertEqual(edits, [])
        self.assertEqual(apply_edits(html, edits), html)

    def test_a_gloss_button_nested_in_math_is_refused_not_deleted(self):
        """Masking tag interiors makes this span *look* like plain text.
        Converting it would delete a gloss-term button silently and leave the
        per-term tally short with nothing to account for the drop."""
        body = (r'<p>$\text{lens}(h) = \text{'
                r'<button type="button" class="gloss-term" data-term-id="softmax">'
                r"softmax</button>}(x)$</p>")
        html = page(body)
        edits, refused, _ = plan(html)
        self.assertEqual(edits, [])
        self.assertEqual(sum(refused.values()), 1)
        self.assertIn("gloss-term", next(iter(refused)))

    def test_display_blocks_are_left_whole(self):
        """Without masking `$$…$$` first, a match starting at the second `$`
        eats the block's interior and leaves stray delimiters behind."""
        html = page('<pre class="equation">$$\na = b_k\n$$</pre>')
        edits, _, _ = plan(html)
        self.assertEqual(edits, [])
        self.assertIn("$$", apply_edits(html, edits))

    def test_conversion_does_not_disturb_surrounding_prose(self):
        html = page("<p>the value $k$ and the word model</p>")
        edits, _, _ = plan(html)
        out = apply_edits(html, edits)
        self.assertIn("the value ", out)
        self.assertIn(" and the word model", out)
        self.assertIn('<span class="math"><i>k</i></span>', out)
        self.assertNotIn("$", out)

    def test_paragraph_count_is_never_changed(self):
        html = page("<p>$k$</p>\n<p>$x_i$</p>\n<p>$\\alpha$</p>")
        out = apply_edits(html, plan(html)[0])
        self.assertEqual(out.count("<p"), html.count("<p"))


class TestPlanAndApply(unittest.TestCase):
    def test_plan_writes_nothing_and_apply_is_offset_safe(self):
        html = page("<p>$a$ then $b$ then $c$</p>")
        edits, _, _ = plan(html)
        self.assertEqual(len(edits), 3)
        out = apply_edits(html, edits)
        for letter in "abc":
            self.assertIn(f"<span class=\"math\"><i>{letter}</i></span>", out)

    def test_applying_an_empty_plan_is_a_no_op(self):
        html = page("<p>no math here</p>")
        self.assertEqual(apply_edits(html, plan(html)[0]), html)


if __name__ == "__main__":
    unittest.main()
