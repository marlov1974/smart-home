import unittest

from src.mac.services.spotprice_model_diagnostics import p0054v2


class P0054V2Tests(unittest.TestCase):
    def test_relaxed_baseline_gate_accepts_p0054v_delta(self):
        self.assertTrue(p0054v2.relaxed_baseline_passes(1.2733356730141168, 0.5019))
        self.assertFalse(p0054v2.relaxed_baseline_passes(3.0, 1.5))

    def test_stitched_prices_use_actual_train_and_forecast_holdout(self):
        rows = [
            {
                "split": "train_fit",
                "forecast_origin_timestamp_utc": "2025-01-01T00:00:00Z",
                "target_timestamp_utc": "2025-01-01T01:00:00Z",
            },
            {
                "split": "holdout",
                "forecast_origin_timestamp_utc": "2025-06-01T00:00:00Z",
                "target_timestamp_utc": "2025-06-01T01:00:00Z",
            },
        ]
        actual = {"2025-01-01T01:00:00Z": 12.0, "2025-06-01T01:00:00Z": 99.0}
        forecast = {("2025-06-01T00:00:00Z", "2025-06-01T01:00:00Z"): {"predicted_price": 34.0}}

        p0054v2.attach_basic_stitched_prices(rows, actual, forecast)

        self.assertEqual(12.0, rows[0]["p0054v2_stitched_spot_target_hour"])
        self.assertEqual("actual_train_fit_target_hour", rows[0]["p0054v2_price_value_kind"])
        self.assertEqual(34.0, rows[1]["p0054v2_stitched_spot_target_hour"])
        self.assertEqual("forecast_holdout_future_target_hour", rows[1]["p0054v2_price_value_kind"])

    def test_anchor_features_are_strictly_before_origin(self):
        origin = "2025-06-01T12:00:00Z"
        actual = {
            "2025-06-01T11:00:00Z": 1.0,
            "2025-05-31T12:00:00Z": 24.0,
            "2025-05-30T12:00:00Z": 48.0,
            "2025-06-01T12:00:00Z": 999.0,
        }

        features, audit = p0054v2.build_anchor_features(origin, actual)

        self.assertEqual(1.0, features["actual_spot_lag_1h"])
        self.assertEqual(24.0, features["actual_spot_lag_24h"])
        self.assertEqual(48.0, features["actual_spot_lag_48h"])
        self.assertTrue(all(source < origin for source in audit.values()))

    def test_coverage_summary_rejects_missing_stitched_price(self):
        rows = [
            {
                "split": "holdout",
                "forecast_origin_timestamp_utc": "2025-06-01T00:00:00Z",
                "target_timestamp_utc": "2025-06-01T01:00:00Z",
                "horizon_h": 2,
            }
        ]

        summary = p0054v2.coverage_summary(rows)

        self.assertFalse(summary["complete"])
        self.assertEqual(1, summary["missing_stitched_price_rows"])


if __name__ == "__main__":
    unittest.main()
