import unittest
from datetime import datetime, timedelta, timezone

from src.mac.services.spotprice_model_diagnostics import p0054h


def z(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


class P0054HTests(unittest.TestCase):
    def test_predict_price_prefers_previous_week_when_before_origin(self):
        origin = datetime(2025, 1, 8, 23, tzinfo=timezone.utc)
        target = origin + timedelta(hours=5)
        previous = target - timedelta(hours=168)
        prices = {z(previous): 123.0}
        state = {"same_model_cet_hour": {5: [10.0, 20.0]}, "median": 15.0}
        hourly = {"timestamp_utc": z(target), "model_cet_hour": 5}

        predicted, rule, source = p0054h.predict_price(hourly, origin, state, prices)

        self.assertEqual(123.0, predicted)
        self.assertEqual("previous_week_same_hour", rule)
        self.assertEqual(z(previous), source)

    def test_predict_price_uses_hist48_same_hour_fallback(self):
        origin = datetime(2025, 1, 8, 23, tzinfo=timezone.utc)
        target = origin + timedelta(hours=5)
        state = {"same_model_cet_hour": {5: [10.0, 20.0]}, "median": 15.0}
        hourly = {"timestamp_utc": z(target), "model_cet_hour": 5}

        predicted, rule, source = p0054h.predict_price(hourly, origin, state, {})

        self.assertEqual(15.0, predicted)
        self.assertEqual("hist48_same_hour_mean", rule)
        self.assertIsNone(source)

    def test_validate_leakage_accepts_well_ordered_row(self):
        origin = datetime(2025, 1, 1, 23, tzinfo=timezone.utc)
        row = {
            "forecast_origin_timestamp_utc": z(origin),
            "input_data_cutoff_utc": z(origin - timedelta(hours=1)),
            "training_cutoff_utc": z(origin - timedelta(hours=1)),
            "anchor_window_start_utc": z(origin - timedelta(hours=48)),
            "anchor_window_end_utc": z(origin - timedelta(hours=1)),
            "target_timestamp_utc": z(origin + timedelta(hours=4)),
            "prediction_source_timestamp_utc": z(origin - timedelta(hours=164)),
            "horizon_hours": 4,
        }

        review = p0054h.validate_leakage([row])

        self.assertTrue(review["ok"])

    def test_validate_leakage_rejects_future_prediction_source(self):
        origin = datetime(2025, 1, 1, 23, tzinfo=timezone.utc)
        row = {
            "forecast_origin_timestamp_utc": z(origin),
            "input_data_cutoff_utc": z(origin - timedelta(hours=1)),
            "training_cutoff_utc": z(origin - timedelta(hours=1)),
            "anchor_window_start_utc": z(origin - timedelta(hours=48)),
            "anchor_window_end_utc": z(origin - timedelta(hours=1)),
            "target_timestamp_utc": z(origin + timedelta(hours=4)),
            "prediction_source_timestamp_utc": z(origin),
            "horizon_hours": 4,
        }

        review = p0054h.validate_leakage([row])

        self.assertFalse(review["ok"])
        self.assertEqual(1, review["prediction_source_after_origin_error_count"])

    def test_forecast_rows_have_required_columns(self):
        origin = datetime(2025, 1, 1, 23, tzinfo=timezone.utc)
        prices = {z(origin - timedelta(hours=offset)): float(offset) for offset in range(1, 49)}
        hourly = [
            {
                "timestamp_utc": z(origin + timedelta(hours=horizon)),
                "model_cet_hour": horizon % 24,
            }
            for horizon in range(2)
        ]
        rows = p0054h.build_forecast_rows(
            [{"forecast_origin_timestamp_utc": z(origin), "hourly_rows": hourly}],
            prices,
        )

        self.assertEqual(2, len(rows))
        self.assertTrue(set(p0054h.forecast_log_columns()).issubset(rows[0]))
        self.assertEqual("forecast_safe_origin_local_baseline_not_m4", rows[0]["quality_flag"])


if __name__ == "__main__":
    unittest.main()
