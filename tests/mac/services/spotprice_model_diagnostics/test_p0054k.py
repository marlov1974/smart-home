import unittest
from datetime import datetime, timedelta, timezone

from src.mac.services.spotprice_model_diagnostics import p0054k


class P0054KTests(unittest.TestCase):
    def test_se3_price_forecast_rows_use_reconstructed_prices(self) -> None:
        origin = datetime(2022, 6, 8, 0, tzinfo=timezone.utc)
        rows = []
        prices = {}
        for offset in range(-168, 168):
            ts = origin + timedelta(hours=offset)
            key = p0054k.p0052.format_utc(ts)
            price = 100.0 + offset
            prices[key] = price
            if offset >= 0:
                rows.append({"timestamp_utc": key, "model_cet_hour": ts.hour})
        windows = [{"forecast_origin_timestamp_utc": p0054k.p0052.format_utc(origin), "hourly_rows": rows}]

        forecast = p0054k.build_se3_price_forecast_rows(windows, prices)

        self.assertEqual(168, len(forecast))
        self.assertEqual("SE3", forecast[0]["area"])
        self.assertEqual("system_proxy_se1 + area_diff_proxy_se3", forecast[0]["source_reconstruction"])
        self.assertEqual(prices[p0054k.p0052.format_utc(origin - timedelta(hours=168))], forecast[0]["predicted_price"])

    def test_se3_price_leakage_rejects_future_source_timestamp(self) -> None:
        origin = "2025-06-01T00:00:00Z"
        row = {
            "forecast_origin_timestamp_utc": origin,
            "input_data_cutoff_utc": "2025-05-31T23:00:00Z",
            "training_cutoff_utc": "2025-05-31T23:00:00Z",
            "target_timestamp_utc": "2025-06-01T01:00:00Z",
            "anchor_window_start_utc": "2025-05-30T00:00:00Z",
            "anchor_window_end_utc": "2025-05-31T23:00:00Z",
            "horizon_hours": 1,
            "prediction_source_timestamp_utc": origin,
        }

        review = p0054k.validate_se3_price_leakage([row])

        self.assertFalse(review["ok"])
        self.assertEqual(1, review["prediction_source_after_origin_error_count"])

    def test_feature_contract_has_se3_variant_and_no_forbidden_no_price_terms(self) -> None:
        contract = p0054k.feature_group_contract()

        self.assertIn("with_p0054k_se3_price_forecast", contract)
        self.assertTrue(p0054k.validate_feature_contract(contract)["ok"])
        self.assertFalse(any("price" in feature for feature in contract["no_price"]["features"]))

    def test_se3_vs_se1_comparison_positive_improvement_convention(self) -> None:
        ablation = {
            "per_model_family": [
                {
                    "family": "XGBoost",
                    "holdout_relative_change_percent": -2.5,
                    "weekly_relative_change_percent": -3.0,
                }
            ]
        }

        comparison = p0054k.se3_vs_se1_price_effect_comparison(ablation)

        self.assertEqual(2.5, comparison["se3_xgboost_holdout_relative_improvement_percent"])
        self.assertTrue(comparison["se3_stronger_than_se1_holdout"])


if __name__ == "__main__":
    unittest.main()
