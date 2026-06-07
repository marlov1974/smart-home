from __future__ import annotations

from datetime import timedelta
import unittest

from src.mac.services.spotprice_model_diagnostics import p0052, p0054n, p0056c


class P0056CTests(unittest.TestCase):
    def test_feature_names_exclude_forbidden_market_terms(self) -> None:
        forbidden = ("price", "spot", "flow", "exchange", "a61", "capacity", "physical_balance")

        features = p0056c.p0056c_feature_names()

        self.assertTrue(features)
        self.assertFalse([feature for feature in features if any(term in feature.lower() for term in forbidden)])

    def test_build_area_modeling_rows_uses_target_weather_and_split(self) -> None:
        target_rows = []
        start = p0052.parse_utc("2025-02-20T00:00:00Z")
        for index in range(24 * 130):
            ts = p0052.format_utc(start + timedelta(hours=index))
            target_rows.append({"timestamp_utc": ts, "consumption_mw": 1000.0 + index % 24})
        weather_rows = {
            row["timestamp_utc"]: {
                "weather_proxy_temperature_2m_area": 3.0,
                "weather_proxy_apparent_temperature_area": 2.0,
                "weather_proxy_wind_speed_area": 20.0,
                "weather_proxy_cloud_cover_area": 50.0,
                "weather_proxy_humidity_area": 80.0,
                "weather_proxy_precipitation_area": 0.0,
                "weather_proxy_snow_depth_area": 0.0,
                "weather_proxy_heating_degree_hours_area": 14.0,
                "weather_proxy_cooling_degree_hours_area": 0.0,
                "weather_proxy_temperature_roll_mean_24h_area": 3.0,
                "weather_proxy_label": "weather_actual_as_forecast_proxy",
            }
            for row in target_rows
        }

        rows = p0056c.build_area_modeling_rows("SE1", target_rows, weather_rows, set(p0054n.HORIZONS_36H))

        self.assertTrue(rows)
        self.assertIn("area_consumption_lag_168h", rows[0])
        self.assertIn("weather_proxy_temperature_delta_from_train_normal_area", rows[0])
        self.assertTrue({row["split"] for row in rows} <= {"train_fit", "holdout", "outside"})
        self.assertTrue(
            all(
                p0052.parse_utc(str(row["input_data_cutoff_utc"]))
                < p0052.parse_utc(str(row["forecast_origin_timestamp_utc"]))
                <= p0052.parse_utc(str(row["target_timestamp_utc"]))
                for row in rows
            )
        )

    def test_aggregate_forecast_requires_all_areas(self) -> None:
        rows = []
        delivery_day = p0052.parse_utc("2025-06-02T00:00:00Z").date()
        origin = p0054n.dayahead_origin_utc_for_delivery_day(delivery_day)
        targets = p0054n.delivery_day_target_utc_hours(delivery_day)
        for area in p0056c.REQUIRED_AREAS:
            for horizon, target in enumerate(targets, start=1):
                rows.append(
                    {
                        "area_code": area,
                        "split": "holdout",
                        "forecast_origin_timestamp_utc": origin,
                        "target_timestamp_utc": target,
                        "horizon_h": horizon,
                        "target_consumption_se3_mw": 10.0,
                        p0056c.PREDICTION_COLUMN: 11.0,
                    }
                )

        summary = p0056c.aggregate_forecast_summary(rows, p0056c.PREDICTION_COLUMN)

        self.assertEqual(24, summary["aggregate_rows"])
        self.assertEqual(4320.0, summary["total_northern_europe_actual_load"])
        self.assertEqual(4752.0, summary["sum_of_area_forecasts"])
        self.assertTrue(summary["aggregate_forecast_equals_sum_of_area_forecasts"])

    def test_leakage_review_ignores_no_price_prediction_output_columns(self) -> None:
        rows = [
            {
                "input_data_cutoff_utc": "2025-05-31T09:00:00Z",
                "forecast_origin_timestamp_utc": "2025-05-31T10:00:00Z",
                "target_timestamp_utc": "2025-06-01T00:00:00Z",
                "pred_HGB_no_price": 1.0,
                "pred_HorizonBiasCorrected_WeightedEnsemble_no_price": 1.0,
            }
        ]

        review = p0056c.leakage_review(
            rows,
            p0056c.p0056c_feature_names(),
            {"ok": True},
            {"ok": True},
            [],
        )

        self.assertTrue(review["ok"])
        self.assertEqual([], review["forbidden_columns"])


if __name__ == "__main__":
    unittest.main()
