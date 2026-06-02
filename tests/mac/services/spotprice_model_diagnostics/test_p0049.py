from __future__ import annotations

import unittest

from src.mac.services.spotprice_model_diagnostics import p0049


class P0049Tests(unittest.TestCase):
    def test_validate_contract_checks_spread_arithmetic(self):
        rows = [{
            "timestamp_utc": "2025-01-01T00:00:00+00:00",
            "model_cet_timestamp": "2025-01-01T01:00:00+00:00",
            "model_cet_date": "2025-01-01",
            "model_cet_hour": 1,
            "model_cet_weekday": 2,
            "model_cet_day_of_year": 1,
            "se1_price": 1.0,
            "se3_price": 1.3,
            "se3_minus_se1": 0.3,
            "is_positive_bottleneck": 1,
            "is_positive_spike": 0,
            "split": "validate",
        }]
        self.assertTrue(p0049.validate_p0049_contract(rows)["ok"])
        rows[0]["se3_minus_se1"] = 0.2
        self.assertFalse(p0049.validate_p0049_contract(rows)["ok"])

    def test_chronological_splits_are_non_overlapping(self):
        rows = [
            {"timestamp_utc": "2025-01-01T00:00:00+00:00", "split": "train"},
            {"timestamp_utc": "2025-01-02T00:00:00+00:00", "split": "validate"},
            {"timestamp_utc": "2025-01-03T00:00:00+00:00", "split": "holdout"},
        ]
        self.assertTrue(p0049.validate_chronological_splits(rows)["ok"])
        rows.append({"timestamp_utc": "2025-01-04T00:00:00+00:00", "split": "train"})
        self.assertFalse(p0049.validate_chronological_splits(rows)["ok"])

    def test_daytype_features_are_deterministic(self):
        row = {"model_cet_weekday": 4, "model_cet_hour": 17, "is_special_day": 0, "is_bridge_day": 0, "is_holiday_period": 0}
        p0049.add_daytype_features([row])
        self.assertEqual(1, row["is_friday"])
        self.assertEqual(1, row["is_evening_peak"])
        self.assertEqual("friday", row["day_type_group"])

    def test_price_thresholds_fit_train_only(self):
        train = [{"model_cet_hour": 0, "se1_price": 1.0, "se3_price": 2.0}, {"model_cet_hour": 0, "se1_price": 3.0, "se3_price": 4.0}]
        thresholds = p0049.fit_price_thresholds(train)
        self.assertEqual(2.0, thresholds["se1_price"]["median"])
        self.assertEqual(3.0, thresholds["se3_price"]["median"])

    def test_rolling_features_are_backward_looking(self):
        rows = [{"se3_minus_se1": 1.0, "is_positive_bottleneck": 1, "is_positive_spike": 0, "se1_price": 1.0, "se3_price": 2.0, "wind_south_minus_north_actual": 0.0, "wind_central_minus_north_actual": 0.0, "wind_south_minus_system_actual": 0.0, "wind_north_minus_system_actual": 0.0, "solar_south_minus_north_actual": 0.0, "temperature_south_minus_north_actual": 0.0}, {"se3_minus_se1": 3.0, "is_positive_bottleneck": 1, "is_positive_spike": 0, "se1_price": 1.0, "se3_price": 2.0, "wind_south_minus_north_actual": 0.0, "wind_central_minus_north_actual": 0.0, "wind_south_minus_system_actual": 0.0, "wind_north_minus_system_actual": 0.0, "solar_south_minus_north_actual": 0.0, "temperature_south_minus_north_actual": 0.0}]
        p0049.add_rolling_features(rows, (1,))
        self.assertEqual(0.0, rows[0]["se3_minus_se1_rolling_1h_mean"])
        self.assertEqual(1.0, rows[1]["se3_minus_se1_rolling_1h_mean"])

    def test_horizon_targets_shift_forward(self):
        rows = [{"is_positive_bottleneck": 0, "is_positive_spike": 0, "se3_minus_se1": 0.1}, {"is_positive_bottleneck": 1, "is_positive_spike": 0, "se3_minus_se1": 0.4}]
        p0049.add_horizon_targets(rows, (1,))
        self.assertEqual(1, rows[0]["target_is_positive_bottleneck_h1"])
        self.assertEqual(0.4, rows[0]["target_spread_h1"])
        self.assertIsNone(rows[1]["target_spread_h1"])

    def test_forbidden_paths_include_no_api_or_device(self):
        self.assertIn("SE1_TO_SE3_ANCHORING", p0049.FORBIDDEN_PRODUCTION_PATHS)
        self.assertIn("SE3_API", p0049.FORBIDDEN_PRODUCTION_PATHS)
        self.assertIn("DEVICE", p0049.FORBIDDEN_PRODUCTION_PATHS)

    def test_reservoir_formulas_are_documented(self):
        rows = []
        for index in range(3):
            rows.append({
                "split": "train",
                "wind_south_minus_north_actual": float(index),
                "temperature_south_minus_north_actual": float(index),
                "solar_south_minus_north_actual": float(index),
                "se1_price_delta_from_train_median_by_hour": float(index),
                "is_evening_peak": 0,
                "is_morning_peak": 0,
                "se1_price_above_train_p90": 0,
                "wind_south_proxy_actual": 0.0,
                "se3_minus_se1_rolling_6h_trend": 0.0,
                "lag1_spread": 0.0,
                "is_friday": 0,
                "is_weekend": 0,
                "is_holiday": 0,
            })
        formulas = p0049.add_reservoir_features(rows)
        self.assertIn("base_pressure", formulas)
        self.assertIn("learned_pressure_score", formulas)
        self.assertIn("weather_pressure_ema_24h", rows[-1])


if __name__ == "__main__":
    unittest.main()
