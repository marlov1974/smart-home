from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.spot import load_actual_spot_prices


class SpotFixtureDstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prices = load_actual_spot_prices()

    def test_fixture_has_unique_utc_keys(self) -> None:
        self.assertEqual(len(self.prices), 8760)
        self.assertEqual(len(set(self.prices)), 8760)

    def test_fixture_preserves_spring_and_fall_dst_shape(self) -> None:
        rows = list(self.prices.values())
        spring = [row for row in rows if row.local_wall_hour.startswith("2025-03-30")]
        fall = [row for row in rows if row.local_wall_hour.startswith("2025-10-26")]
        fall_0200 = [row for row in fall if row.local_wall_hour == "2025-10-26 02:00"]

        self.assertEqual(len(spring), 23)
        self.assertEqual(len(fall), 25)
        self.assertEqual(len(fall_0200), 2)
        self.assertEqual({row.fold for row in fall_0200}, {0, 1})
        self.assertEqual({row.quarter_count for row in rows}, {4})


if __name__ == "__main__":
    unittest.main()
