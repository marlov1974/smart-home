from __future__ import annotations

import unittest

from src.mac.services.spotprice_model_diagnostics import p0054r, p0056e


class P0056ETests(unittest.TestCase):
    def test_required_variant_ids_exist(self) -> None:
        self.assertEqual([f"V{index}" for index in range(9)], [variant.variant_id for variant in p0056e.variant_specs()])

    def test_feature_groups_exclude_forbidden_market_terms(self) -> None:
        forbidden = ("price", "spot", "flow", "exchange", "a61", "capacity", "physical_balance", "future_actual")
        for features in p0056e.feature_groups().values():
            self.assertFalse([feature for feature in features if any(term in feature.lower() for term in forbidden)])

    def test_decision_rule_accepts_full36_improvement_without_dayahead_worsening(self) -> None:
        result = {
            "area_code": "SE2",
            "variant_id": "VX",
            "model_name": "test",
            "DayAhead_hourly_MAE": p0056e.P0056D_BASELINES["SE2"]["DayAhead_hourly_MAE"],
            "full_36h_MAE": p0056e.P0056D_BASELINES["SE2"]["full_36h_MAE"] * 0.97,
            "daily_energy_error_percent_of_actual": p0056e.P0056D_BASELINES["SE2"]["daily_energy_error_percent_of_actual"],
        }

        comparison = p0056e.compare_variant_to_baseline(result)

        self.assertTrue(comparison["candidate_default"])

    def test_regime_correction_uses_internal_validation_only(self) -> None:
        rows = [
            row("internal_validation", "train_fit", 100.0, 110.0, 0.0),
            row("internal_validation", "train_fit", 200.0, 210.0, 0.0),
            row("not_train_fit", "holdout", 300.0, 500.0, 0.0),
        ]

        evidence = p0056e.apply_internal_validation_regime_correction(rows, "base", "corrected")

        self.assertFalse(evidence["holdout_used_for_fit"])
        self.assertAlmostEqual(490.0, rows[2]["corrected"])


def row(internal_split: str, split: str, actual: float, prediction: float, temp: float) -> dict[str, object]:
    return {
        p0054r.INTERNAL_SPLIT_FIELD: internal_split,
        "split": split,
        "base": prediction,
        "weather_proxy_temperature_2m_area": temp,
        "is_weekend": 0,
        "area_consumption_ramp_24h": 0.0,
        "target_consumption_se3_mw": actual,
    }


if __name__ == "__main__":
    unittest.main()
