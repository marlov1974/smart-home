from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.heat_optimizer import derive_heat_cost_weight


class HeatCostWeightFromDpTests(unittest.TestCase):
    def test_cost_weight_reflects_dp_action_and_soc(self) -> None:
        self.assertEqual(derive_heat_cost_weight(10.0, 14.0, 80.0, 1.0), 0.5)
        self.assertEqual(derive_heat_cost_weight(10.0, 6.0, 80.0, 1.0), 2.0)
        self.assertEqual(derive_heat_cost_weight(10.0, 10.0, 80.0, 1.0), 1.0)
        self.assertEqual(derive_heat_cost_weight(10.0, 14.0, 10.0, 1.0), 2.0)
        self.assertEqual(derive_heat_cost_weight(10.0, 6.0, 80.0, 4.0), 2.5)


if __name__ == "__main__":
    unittest.main()
