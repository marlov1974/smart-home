from __future__ import annotations

from datetime import date, datetime, timezone
import unittest

from src.mac.services.spotprice_model_diagnostics import p0056k, p0056m


class P0056MErrorSliceTests(unittest.TestCase):
    def test_bins_are_deterministic(self) -> None:
        self.assertEqual(p0056m.season_for_month(1), "winter")
        self.assertEqual(p0056m.season_for_month(4), "spring")
        self.assertEqual(p0056m.season_for_month(7), "summer")
        self.assertEqual(p0056m.season_for_month(10), "autumn")
        self.assertEqual(p0056m.temperature_bin(-12.0), "very_cold")
        self.assertEqual(p0056m.temperature_bin(5.0), "mild")
        self.assertEqual(p0056m.horizon_bin(24), "24-29")
        self.assertEqual(p0056m.horizon_bin(36), "36+")

    def test_day_metrics_uses_forecast_minus_actual_bias(self) -> None:
        origin = p0056k.Origin(
            datetime(2025, 5, 31, 12, tzinfo=p0056k.STOCKHOLM),
            "2025-05-31T10:00:00Z",
            date(2025, 6, 1),
        )
        rows = []
        for hour in range(24):
            rows.append({
                "actual_mw": 100.0 + hour,
                "forecast_mw": 110.0 + hour,
                "error_mw": 10.0,
                "absolute_error_mw": 10.0,
                "temperature_2m": 4.0,
                "heating_degree_hours": 14.0,
                "local_hour": hour,
                "is_holiday": 0,
                "is_weekend": 1,
            })
        metrics = p0056m.build_day_metrics(origin, rows)
        self.assertEqual(metrics["weekday"], "Sunday")
        self.assertEqual(metrics["day_type"], "weekend")
        self.assertAlmostEqual(metrics["hourly_MAE"], 10.0)
        self.assertAlmostEqual(metrics["bias_mw"], 10.0)
        self.assertAlmostEqual(metrics["signed_daily_energy_error_MWh"], 240.0)
        self.assertEqual(metrics["temperature_bin"], "mild")
        self.assertEqual(metrics["heating_degree_bin"], "high")

    def test_slice_summary_and_top_bottom(self) -> None:
        rows = [
            {"delivery_date": "2025-06-01", "weekday": "Sunday", "hourly_MAE": 5.0, "bias_mw": 1.0, "absolute_daily_energy_error_MWh": 10.0, "daily_energy_error_percent": 1.0, "mean_actual_load_mw": 100.0, "mean_temperature_2m": 10.0},
            {"delivery_date": "2025-06-02", "weekday": "Monday", "hourly_MAE": 20.0, "bias_mw": -2.0, "absolute_daily_energy_error_MWh": 50.0, "daily_energy_error_percent": 5.0, "mean_actual_load_mw": 200.0, "mean_temperature_2m": 5.0},
        ]
        summary = p0056m.slice_summary(rows, "weekday")
        self.assertEqual([row["slice"] for row in summary], ["Monday", "Sunday"])
        best, worst = p0056m.top_bottom_tests(rows)
        self.assertEqual(best[0]["delivery_date"], "2025-06-01")
        self.assertEqual(worst[0]["delivery_date"], "2025-06-02")

    def test_leakage_review_inherits_p0056k_forbidden_feature_check(self) -> None:
        review = p0056m.leakage_review()
        self.assertTrue(review["ok"])
        self.assertFalse(review["future_actual_load_feature_used_for_prediction"])


if __name__ == "__main__":
    unittest.main()
