from __future__ import annotations

import unittest

from src.mac.services.spotprice_model_diagnostics import p0050


def base_row(index: int, *, split: str = "train", price: float = 1.0, spread: float = 0.1, temp: float = 5.0) -> dict[str, object]:
    return {
        "timestamp_utc": f"2025-01-01T{index:02d}:00:00+00:00",
        "model_cet_timestamp": f"2025-01-01T{index + 1:02d}:00:00+00:00",
        "model_cet_date": "2025-01-01",
        "model_cet_hour": index,
        "model_cet_weekday": 2,
        "model_cet_day_of_year": 1,
        "se1_price": price - spread,
        "se3_price": price,
        "se3_minus_se1": spread,
        "spread_regime": "near_zero",
        "is_near_zero": 1,
        "is_positive_bottleneck": 0,
        "is_positive_spike": 0,
        "temperature_south_proxy_actual": temp,
        "temperature_south_proxy_delta": temp - 4.0,
        "is_special_day": 0,
        "is_bridge_day": 0,
        "is_holiday_period": 0,
        "split": split,
        "lag1_spread": 0.0,
        "p0049_weather_pressure_ema_24h": 0.0,
    }


class P0050Tests(unittest.TestCase):
    def test_validate_contract_checks_fixed_cet_and_spread(self):
        rows = [base_row(0, price=1.3, spread=0.3)]
        self.assertTrue(p0050.validate_p0050_contract(rows)["ok"])
        rows[0]["se3_minus_se1"] = 0.2
        self.assertFalse(p0050.validate_p0050_contract(rows)["ok"])

    def test_chronological_splits_are_non_overlapping(self):
        rows = [
            {"timestamp_utc": "2025-01-01T00:00:00+00:00", "split": "train"},
            {"timestamp_utc": "2025-01-02T00:00:00+00:00", "split": "validate"},
            {"timestamp_utc": "2025-01-03T00:00:00+00:00", "split": "holdout"},
        ]
        self.assertTrue(p0050.validate_chronological_splits(rows)["ok"])
        rows.append({"timestamp_utc": "2025-01-04T00:00:00+00:00", "split": "train"})
        self.assertFalse(p0050.validate_chronological_splits(rows)["ok"])

    def test_baseline_is_fit_from_train_rows(self):
        rows = [base_row(0, split="train", spread=0.2), base_row(0, split="validate", spread=2.0)]
        p0050.add_daytype_features(rows)
        baselines = p0050.fit_spread_baselines([rows[0]])
        p0050.apply_spread_baselines(rows, baselines)
        p0050.apply_selected_residual(rows, "B0_hour_weekday")
        self.assertEqual(0.2, rows[1]["expected_spread_baseline"])
        self.assertAlmostEqual(1.8, rows[1]["spread_residual"])

    def test_day_rank_tie_handling_is_deterministic(self):
        rows = [base_row(0, price=2.0), base_row(1, price=2.0), base_row(2, price=0.5)]
        p0050.add_local_se3_rank_features(rows)
        self.assertEqual(1, rows[0]["se3_rank_in_day"])
        self.assertEqual(2, rows[1]["se3_rank_in_day"])
        self.assertEqual(1, rows[2]["se3_is_bottom2_day"])

    def test_topn_counts_are_backward_looking(self):
        rows = [base_row(i, price=float(i)) for i in range(6)]
        p0050.add_local_se3_rank_features(rows)
        p0050.add_consumer_optimizer_response_features(rows)
        self.assertEqual(0, rows[0]["top4_day_hours_last_6h"])
        self.assertGreaterEqual(rows[5]["top4_day_hours_last_6h"], 1)

    def test_oracle_fields_are_labeled(self):
        for field in p0050.ORACLE_FIELDS:
            self.assertTrue(field.endswith("_oracle"))

    def test_heat_pump_pressure_formula_is_reproducible(self):
        rows = [base_row(i, price=float(i), temp=float(10 - i)) for i in range(8)]
        p0050.add_local_se3_rank_features(rows)
        p0050.add_consumer_optimizer_response_features(rows)
        formulas = p0050.add_heat_pump_pressure_features(rows, rows[:4])
        self.assertIn("heat_debt_pressure", formulas)
        self.assertIn("heat_debt_pressure_ema_24h", rows[-1])

    def test_forbidden_paths_include_no_api_or_device(self):
        self.assertIn("SE1_TO_SE3_ANCHORING", p0050.FORBIDDEN_PRODUCTION_PATHS)
        self.assertIn("SE3_API", p0050.FORBIDDEN_PRODUCTION_PATHS)
        self.assertIn("DEVICE", p0050.FORBIDDEN_PRODUCTION_PATHS)


if __name__ == "__main__":
    unittest.main()
