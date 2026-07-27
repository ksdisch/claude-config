import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from normalize import per_figure_budget, plan_width  # noqa: E402


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
        self.assertEqual(plan_width(source_width=700, budget_bytes=250_000), 700)

    def test_wide_source_capped_at_max(self):
        self.assertEqual(plan_width(source_width=4000, budget_bytes=250_000), 1400)

    def test_small_budget_forces_a_narrower_width(self):
        w = plan_width(source_width=4000, budget_bytes=64_000)
        self.assertLessEqual(w, 1000)
        self.assertGreaterEqual(w, 600)


if __name__ == "__main__":
    unittest.main()
