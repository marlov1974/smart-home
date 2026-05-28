from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.input_profiles import expand_period_indexes_to_hours


class SpotExpansionTests(unittest.TestCase):
    def test_21_period_indexes_expand_to_168_hours(self) -> None:
        hourly = expand_period_indexes_to_hours(range(21))

        self.assertEqual(len(hourly), 168)
        self.assertEqual(hourly[:8], (0.0,) * 8)
        self.assertEqual(hourly[8:16], (1.0,) * 8)
        self.assertEqual(hourly[-8:], (20.0,) * 8)


if __name__ == "__main__":
    unittest.main()
