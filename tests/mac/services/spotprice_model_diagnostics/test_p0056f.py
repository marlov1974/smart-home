from __future__ import annotations

import unittest

from src.mac.services.spotprice_model_diagnostics import p0056f


class P0056FTests(unittest.TestCase):
    def test_weather_stacks_are_cumulative_w0_to_w12(self) -> None:
        stacks = p0056f.weather_stacks()

        self.assertEqual([f"W{index}" for index in range(13)], [stack.stack_id for stack in stacks])
        self.assertEqual(0, len(stacks[0].weather_features))
        self.assertEqual(5, len(stacks[4].weather_features))
        self.assertIn("weather_proxy_cold_spell_flag_area", stacks[5].weather_features)
        for index in range(1, len(stacks)):
            self.assertTrue(set(stacks[index - 1].weather_features) <= set(stacks[index].weather_features))

    def test_fixed_non_weather_features_identical_across_stacks(self) -> None:
        fixed = p0056f.fixed_non_weather_features()

        for stack in p0056f.weather_stacks():
            local_fixed = [feature for feature in p0056f.feature_names_for_stack(stack.stack_id) if not feature.startswith("weather_proxy_")]
            self.assertEqual(fixed, local_fixed)

    def test_forbidden_terms_excluded(self) -> None:
        forbidden = ("price", "spot", "flow", "exchange", "a61", "capacity", "physical_balance", "future_actual")

        self.assertFalse([feature for stack in p0056f.weather_stacks() for feature in p0056f.feature_names_for_stack(stack.stack_id) if any(term in feature.lower() for term in forbidden)])

    def test_peak_efficiency_selects_smallest_near_best(self) -> None:
        results = [
            {"area_code": "SE1", "weather_stack_id": "W0", "weather_feature_count": 0, "DayAhead_hourly_MAE": 100.0, "full_36h_MAE": 100.0},
            {"area_code": "SE1", "weather_stack_id": "W1", "weather_feature_count": 1, "DayAhead_hourly_MAE": 99.8, "full_36h_MAE": 99.0},
            {"area_code": "SE1", "weather_stack_id": "W2", "weather_feature_count": 2, "DayAhead_hourly_MAE": 99.5, "full_36h_MAE": 99.0},
            {"area_code": "SE2", "weather_stack_id": "W0", "weather_feature_count": 0, "DayAhead_hourly_MAE": 200.0, "full_36h_MAE": 200.0},
            {"area_code": "SE2", "weather_stack_id": "W1", "weather_feature_count": 1, "DayAhead_hourly_MAE": 199.5, "full_36h_MAE": 199.0},
        ]
        marginal = p0056f.marginal_gain_rows(results)

        decision = p0056f.peak_efficiency_decision(results, marginal)

        self.assertEqual("W2", decision["SE1"]["best_holdout_weather_stack"])
        self.assertEqual("W1", decision["SE1"]["smallest_stack_within_0_5_percent_of_best"])


if __name__ == "__main__":
    unittest.main()
