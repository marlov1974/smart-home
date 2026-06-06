import unittest

from src.mac.services.spotprice_model_diagnostics import p0054t3


class P0054T3Tests(unittest.TestCase):
    def test_row_keys_use_origin_target_horizon(self):
        rows = [
            {"forecast_origin_timestamp_utc": "o", "target_timestamp_utc": "t", "horizon_h": 1},
            {"forecast_origin_timestamp_utc": "o", "target_timestamp_utc": "t", "horizon_h": 2},
        ]

        self.assertEqual({("o", "t", 1), ("o", "t", 2)}, p0054t3.row_keys(rows))

    def test_m1_m2_diagnostic_detects_non_alias(self):
        rows = [
            {"weighted": 10.0, "bias": 11.0},
            {"weighted": 20.0, "bias": 18.0},
            {"weighted": 30.0, "bias": 33.0},
        ]
        evidence = {"horizon_bias_mw": {"1": 1.0, "2": 0.0, "3": -2.0}}

        diag = p0054t3.m1_m2_diagnostic(rows, "weighted", "bias", evidence)

        self.assertFalse(diag["m1_equals_m2"])
        self.assertEqual(2, diag["horizon_bias_nonzero_count"])
        self.assertEqual(2.0, diag["max_abs_horizon_bias_mw"])

    def test_aggregate_matrix_results_groups_w1_seeds(self):
        rows = [
            {"model": "M", "weather_mode": "W1_tempNoise2C", "price_mode": "P", "coverage_label": "c", "hourly_MAE_delivery_day": 10.0},
            {"model": "M", "weather_mode": "W1_tempNoise2C", "price_mode": "P", "coverage_label": "c", "hourly_MAE_delivery_day": 14.0},
        ]

        summary = p0054t3.aggregate_matrix_results(rows)

        self.assertEqual(1, len(summary))
        self.assertEqual(2, summary[0]["seed_count"])
        self.assertEqual(12.0, summary[0]["hourly_MAE_delivery_day_mean"])


if __name__ == "__main__":
    unittest.main()
