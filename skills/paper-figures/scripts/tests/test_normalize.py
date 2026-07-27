import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from normalize import (  # noqa: E402
    main as normalize_main,
    per_figure_budget,
    plan_width,
    resample,
)


class TestBudget(unittest.TestCase):
    def test_many_figures_get_a_small_share(self):
        # 94 figures against a 6MB total -> ~64KB each
        b = per_figure_budget(94)
        self.assertGreater(b, 60_000)
        self.assertLess(b, 70_000)

    def test_few_figures_are_capped_not_inflated(self):
        # 8 figures would compute to 750KB; the per-figure cap holds it down
        self.assertEqual(per_figure_budget(8), 250_000)

    def test_single_figure_still_capped(self):
        self.assertEqual(per_figure_budget(1), 250_000)

    def test_zero_figures_does_not_divide_by_zero(self):
        self.assertEqual(per_figure_budget(0), 250_000)


class TestPlanWidth(unittest.TestCase):
    def test_never_upscales_beyond_source_width(self):
        """Sampled across the whole reachable range, not just at 700 — the one
        value where the old constant-600 fallback happened to satisfy this."""
        for src in (120, 200, 300, 400, 500, 599, 600, 650, 700, 900, 1400, 4000):
            self.assertLessEqual(
                plan_width(source_width=src, budget_bytes=250_000), src,
                f"a {src}px source must never be planned wider than {src}px")

    def test_sub_minimum_source_is_left_at_its_own_width(self):
        # a downscaling tool must not spend the byte budget on interpolated pixels
        self.assertEqual(plan_width(source_width=300, budget_bytes=1), 300)
        self.assertEqual(plan_width(source_width=120, budget_bytes=250_000), 120)

    def test_wide_source_capped_at_max(self):
        self.assertEqual(plan_width(source_width=4000, budget_bytes=250_000), 1400)

    def test_small_budget_forces_a_narrower_width(self):
        w = plan_width(source_width=4000, budget_bytes=64_000)
        self.assertLessEqual(w, 1000)
        self.assertGreaterEqual(w, 600)


class TestOriginalsAreNeverDestroyed(unittest.TestCase):
    """The full-resolution originals in src_dir are committed and are what the
    injected markdown references by path. Normalizing in place resamples each
    onto itself and then deletes the loser of the png/jpeg comparison — silent,
    total, unrecoverable loss. Both the docstring and capture-recipes.md
    promise it cannot happen, so something has to enforce it."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.src = os.path.join(self.d, "fig-01.png")
        with open(self.src, "wb") as fh:
            fh.write(b"\x89PNG\r\n\x1a\n" + b"x" * 4096)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_same_src_and_dst_dir_is_refused(self):
        with open(self.src, "rb") as fh:
            before = fh.read()
        rc = normalize_main([self.d, self.d, "--count", "94"])
        self.assertNotEqual(rc, 0, "in-place normalization must not report success")
        self.assertTrue(os.path.exists(self.src), "the original must survive")
        with open(self.src, "rb") as fh:
            self.assertEqual(fh.read(), before, "the original must be byte-identical")

    def test_resample_refuses_to_write_onto_its_own_input(self):
        with self.assertRaises(ValueError):
            resample(self.src, self.src, 600, "jpeg", 70)

    def test_resample_raises_when_sips_produces_nothing(self):
        """`sips` exits 0 on a missing input, so check=True proves nothing;
        without an existence check the manifest describes a file that is not
        there."""
        missing = os.path.join(self.d, "does-not-exist.png")
        out = os.path.join(self.d, "out.jpg")
        if not shutil.which("sips"):
            self.skipTest("sips unavailable")
        with self.assertRaises(Exception):
            resample(missing, out, 600, "jpeg", 70)


if __name__ == "__main__":
    unittest.main()
