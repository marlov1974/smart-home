from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.ppm_plan import ppm_after_hour, ppm_cost


class PpmDynamicsTests(unittest.TestCase):
    def test_more_supply_removes_more_ppm(self) -> None:
        low = ppm_after_hour(800, 25, occupancy_gain_ppm_h=70)
        high = ppm_after_hour(800, 55, occupancy_gain_ppm_h=70)

        self.assertLess(high, low)

    def test_ppm_cost_continues_above_1000(self) -> None:
        self.assertGreater(ppm_cost(1050), ppm_cost(1000))
        self.assertGreater(ppm_cost(1200), ppm_cost(1050))


if __name__ == "__main__":
    unittest.main()
