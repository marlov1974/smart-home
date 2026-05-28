from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.cop import COP_MAX, COP_MIN, estimate_cop


class CopEmulatorTests(unittest.TestCase):
    def test_cop_clamps_plausible_range(self) -> None:
        self.assertGreaterEqual(estimate_cop(-50.0, 22.0), COP_MIN)
        self.assertLessEqual(estimate_cop(40.0, 2.0), COP_MAX)

    def test_cop_decreases_in_cold_weather(self) -> None:
        mild = estimate_cop(5.0, 12.0)
        cold = estimate_cop(-10.0, 12.0)

        self.assertLessEqual(cold, mild)

    def test_cop_penalizes_high_output(self) -> None:
        moderate = estimate_cop(5.0, 12.0)
        high = estimate_cop(5.0, 22.0)

        self.assertLessEqual(high, moderate)

    def test_expected_reference_points(self) -> None:
        self.assertAlmostEqual(estimate_cop(-10.0, 22.0), 3.025, places=3)
        self.assertAlmostEqual(estimate_cop(0.0, 12.0), 3.925, places=3)
        self.assertAlmostEqual(estimate_cop(5.0, 8.0), 4.2, places=3)
        self.assertAlmostEqual(estimate_cop(7.0, 5.0), 4.41, places=3)


if __name__ == "__main__":
    unittest.main()
