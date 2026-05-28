from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.heat_optimizer import optimize_heat_dp


class HeatOptimizerDpTests(unittest.TestCase):
    def test_dp_shifts_heat_toward_cheaper_hours(self) -> None:
        needs = [10.0] * 168
        prices = [2.0 if hour < 84 else 0.5 for hour in range(168)]

        plan = optimize_heat_dp(needs, prices)

        first_half = sum(plan.heat_action_kw[:84]) / 84
        second_half = sum(plan.heat_action_kw[84:]) / 84
        self.assertLess(first_half, second_half)
        self.assertEqual(len(plan.heat_action_kw), 168)
        self.assertEqual(len(plan.heat_price_index), 168)


if __name__ == "__main__":
    unittest.main()
