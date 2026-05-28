from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.planner import build_weekly_plan
from src.mac.labs.weekly_home_optimizer_poc.ppm_plan import occupancy_gain_for_people, validate_people


class PeopleOccupancyLoadTests(unittest.TestCase):
    def test_occupancy_gain_scales_with_people(self) -> None:
        self.assertEqual(occupancy_gain_for_people(3), 70)
        self.assertEqual(occupancy_gain_for_people(6), 140)

    def test_people_range_validation(self) -> None:
        self.assertEqual(validate_people("0"), 0)
        self.assertEqual(validate_people("20"), 20)
        with self.assertRaises(ValueError):
            validate_people("21")

    def test_people_changes_plan_pressure(self) -> None:
        plan3 = build_weekly_plan(2, 500, 22, people=3, prefer_real_weather=False)
        plan6 = build_weekly_plan(2, 500, 22, people=6, prefer_real_weather=False)

        avg_supply3 = sum(plan3.ppm.supply_pct) / len(plan3.ppm.supply_pct)
        avg_supply6 = sum(plan6.ppm.supply_pct) / len(plan6.ppm.supply_pct)
        max_ppm3 = max(plan3.ppm.ppm_absolute)
        max_ppm6 = max(plan6.ppm.ppm_absolute)
        self.assertTrue(max_ppm6 > max_ppm3 or avg_supply6 > avg_supply3)
        self.assertEqual(plan6.people, 6)
        self.assertEqual(plan6.occupancy_gain_ppm_h, 140)


if __name__ == "__main__":
    unittest.main()
