from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.heat_plan import plan_heat


class HeatPlanTests(unittest.TestCase):
    def test_heat_plan_uses_discrete_dp_defaults(self) -> None:
        temps = [-5.0] * 168
        spots = [1.0] * 168

        plan = plan_heat(temps, spots, current_house_temp=22.0)

        self.assertEqual(len(plan.heat_kWh), 168)
        self.assertEqual(plan.heat_optimizer, "discrete_dp")
        self.assertEqual(plan.heat_modes_kw, tuple(range(2, 23)))
        self.assertTrue(all(value in plan.heat_modes_kw for value in plan.heat_action_kw))
        self.assertTrue(all(0.0 <= value <= 100.0 for value in plan.heat_soc_pct))
        self.assertTrue(all(0.25 <= value <= 2.5 for value in plan.heat_cost_weight))
        self.assertGreaterEqual(plan.end_heat_soc_pct, plan.end_soc_min_pct)


if __name__ == "__main__":
    unittest.main()
