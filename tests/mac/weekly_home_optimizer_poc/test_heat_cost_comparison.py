from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.cop import compare_heat_costs, estimate_cop


class HeatCostComparisonTests(unittest.TestCase):
    def test_hourly_fields_are_numerically_consistent(self) -> None:
        temps = [0.0] * 168
        needs = [10.0] * 168
        optimized = [12.0] * 168
        prices = [1.5] * 168

        comparison = compare_heat_costs(temps, needs, optimized, prices)

        self.assertEqual(len(comparison.optimized_heat_el_kWh), 168)
        self.assertAlmostEqual(comparison.optimized_heat_el_kWh[0], 12.0 / estimate_cop(0.0, 12.0), places=4)
        self.assertAlmostEqual(
            comparison.optimized_heat_el_cost[0],
            comparison.optimized_heat_el_kWh[0] * 1.5,
            places=4,
        )
        self.assertEqual(comparison.heat_cost_comparison_warnings, ())

    def test_flat_baseline_uses_heat_need(self) -> None:
        temps = [5.0] * 168
        needs = [8.0] * 168
        optimized = [12.0] * 168
        prices = [1.0] * 168

        comparison = compare_heat_costs(temps, needs, optimized, prices)

        self.assertEqual(comparison.flat_heat_kWh[0], 8.0)
        self.assertAlmostEqual(comparison.flat_heat_el_kWh[0], 8.0 / estimate_cop(5.0, 8.0), places=4)

    def test_relative_cost_percentage(self) -> None:
        comparison = compare_heat_costs([5.0] * 168, [10.0] * 168, [10.0] * 168, [1.0] * 168)

        self.assertEqual(comparison.optimized_vs_flat_cost_pct, 100.0)
        self.assertEqual(comparison.optimized_saving_pct, 0.0)

    def test_zero_denominator_warning(self) -> None:
        comparison = compare_heat_costs([5.0] * 168, [0.0] * 168, [0.0] * 168, [1.0] * 168)

        self.assertIsNone(comparison.optimized_vs_flat_cost_pct)
        self.assertIsNone(comparison.optimized_saving_pct)
        self.assertIn("flat_heat_el_cost_zero", comparison.heat_cost_comparison_warnings)


if __name__ == "__main__":
    unittest.main()
