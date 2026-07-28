import os
import shutil
import subprocess
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

    def test_case_variant_dst_dir_is_refused(self):
        """abspath string comparison is not a same-directory test: this is
        macOS-only tooling and the default APFS volume is case-INSENSITIVE, so
        `Figs` and `figs` are one directory."""
        upper = os.path.join(self.d, "Figs")
        os.makedirs(upper)
        src = os.path.join(upper, "fig-01.png")
        with open(src, "wb") as fh:
            fh.write(b"\x89PNG\r\n\x1a\n" + b"y" * 4096)
        lower = os.path.join(self.d, "figs")
        if not os.path.exists(lower):
            self.skipTest("filesystem is case-sensitive; this bypass cannot arise here")
        with open(src, "rb") as fh:
            before = fh.read()
        rc = normalize_main([upper, lower, "--count", "94"])
        self.assertNotEqual(rc, 0)
        with open(src, "rb") as fh:
            self.assertEqual(fh.read(), before, "the original must survive a case-variant dst")

    def test_symlinked_dst_dir_is_refused(self):
        """abspath does not resolve symlinks either."""
        real = os.path.join(self.d, "real")
        os.makedirs(real)
        src = os.path.join(real, "fig-01.png")
        with open(src, "wb") as fh:
            fh.write(b"\x89PNG\r\n\x1a\n" + b"z" * 4096)
        link = os.path.join(self.d, "link")
        os.symlink(real, link)
        with open(src, "rb") as fh:
            before = fh.read()
        rc = normalize_main([real, link, "--count", "94"])
        self.assertNotEqual(rc, 0)
        with open(src, "rb") as fh:
            self.assertEqual(fh.read(), before, "the original must survive a symlinked dst")

    def test_resample_raises_when_the_output_is_stale_rather_than_absent(self):
        """The step-down branch. `dst` always exists there — it was written by
        the first pass — so the existence check can never fire on that path. A
        silent sips no-op therefore leaves the previous file in place while the
        manifest reports the width and size of output that was never written.
        This is the branch the width assertion exists for, and the one the
        existence test does not reach."""
        if not shutil.which("sips"):
            self.skipTest("sips unavailable")
        src = os.path.join(self.d, "big.png")
        subprocess.run(["sips", "-s", "format", "png", "-z", "1300", "2000",
                        "/System/Library/CoreServices/DefaultDesktop.heic", "--out", src],
                       capture_output=True)
        if not os.path.exists(src):
            self.skipTest("could not synthesise a resamplable source image")
        dst = os.path.join(self.d, "out.jpg")
        resample(src, dst, 1400, "jpeg", 70)          # first pass writes dst at 1400px
        self.assertTrue(os.path.exists(dst))
        os.rename(src, src + ".moved")                # now make sips a silent no-op
        with self.assertRaises(RuntimeError) as ctx:
            resample(src, dst, 900, "jpeg", 70)       # step-down against a missing source
        self.assertIn("did not resample", str(ctx.exception))

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
