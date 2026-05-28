from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.heat_optimizer import default_heat_optimizer_config, optimize_heat_dp


class HeatOptimizerConstraintsTests(unittest.TestCase):
    def test_default_constraints_and_metadata_are_respected(self) -> None:
        config = default_heat_optimizer_config()
        plan = optimize_heat_dp([9.0] * 168, [1.0] * 168, config)

        self.assertEqual(plan.heat_soc_capacity_kWh, 300.0)
        self.assertEqual(plan.heat_soc_step_kWh, 1.0)
        self.assertEqual(plan.start_soc_pct, 100.0)
        self.assertEqual(plan.end_soc_min_pct, 50.0)
        self.assertGreaterEqual(plan.min_heat_soc_pct, 0.0)
        self.assertLessEqual(max(plan.heat_soc_pct), 100.0)
        self.assertGreaterEqual(plan.end_heat_soc_pct, 50.0)
        self.assertEqual(plan.heat_optimizer_warnings, ())


if __name__ == "__main__":
    unittest.main()
