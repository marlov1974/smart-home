from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.ppm_plan import optimize_ppm_plan
from src.mac.labs.weekly_home_optimizer_poc.schema import SUPPLY_MODES


class PpmOptimizerPolicyCaseTests(unittest.TestCase):
    def test_supply_bounds(self) -> None:
        plan = optimize_ppm_plan([1.0] * 168, [0.0] * 168, current_ppm=650)

        self.assertTrue(set(plan.supply_pct).issubset(set(SUPPLY_MODES)))

    def test_favorable_conditions_move_ppm_toward_500_without_unneeded_55(self) -> None:
        plan = optimize_ppm_plan([0.25] * 168, [-1.0] * 168, current_ppm=800)

        self.assertLess(plan.ppm_absolute[-1], 650)
        self.assertLessEqual(max(plan.supply_pct[-24:]), 49)

    def test_expensive_drying_conditions_allow_higher_ppm_than_favorable(self) -> None:
        dry = optimize_ppm_plan([2.5] * 168, [2.5] * 168, current_ppm=650)
        neutral = optimize_ppm_plan([2.5] * 168, [0.0] * 168, current_ppm=650)
        favorable = optimize_ppm_plan([0.25] * 168, [-1.0] * 168, current_ppm=650)

        self.assertLessEqual(min(dry.supply_pct[:24]), 28)
        self.assertGreater(sum(dry.ppm_absolute) / 168, sum(neutral.ppm_absolute) / 168)
        self.assertGreater(sum(neutral.ppm_absolute) / 168, sum(favorable.ppm_absolute) / 168)

    def test_high_occupancy_can_push_ppm_toward_upper_normal_range(self) -> None:
        plan = optimize_ppm_plan(
            [2.5] * 168,
            [2.5] * 168,
            current_ppm=650,
            occupancy_gain_ppm_h=130,
        )

        self.assertGreater(max(plan.ppm_absolute), 780)


if __name__ == "__main__":
    unittest.main()
