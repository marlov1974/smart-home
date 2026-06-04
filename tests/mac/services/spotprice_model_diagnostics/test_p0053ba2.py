from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from src.mac.services.spotprice_model_diagnostics import p0053ba2


class P0053BA2Tests(unittest.TestCase):
    def test_compute_g7_features_uses_one_forecast_origin_path(self) -> None:
        rows = [{"forecast_se1_price_target_hour": float(index), "horizon_h": index + 1} for index in range(168)]

        p0053ba2.compute_g7_features(rows)

        self.assertEqual(rows[167]["forecast_se1_price_rank_in_168h"], 1)
        self.assertEqual(rows[0]["forecast_se1_price_low_168h_rank_flag"], 1)
        self.assertEqual(sum(int(row["forecast_se1_price_top4_forecast_day_flag"]) for row in rows[:24]), 4)
        self.assertEqual(sum(int(row["forecast_se1_price_top8_forecast_day_flag"]) for row in rows[:24]), 8)
        self.assertEqual(sum(int(row["forecast_se1_price_bottom4_forecast_day_flag"]) for row in rows[:24]), 4)
        self.assertAlmostEqual(float(rows[0]["forecast_se1_price_relative_to_forecast_168h_mean"]), -83.5)

    def test_select_weekly_holdout_origins_uses_every_seventh_complete_origin(self) -> None:
        rows = []
        start = datetime(2025, 6, 1, 23, tzinfo=timezone.utc)
        for origin_index in range(14):
            origin = (start + timedelta(days=origin_index)).isoformat().replace("+00:00", "Z")
            for horizon in range(168):
                rows.append({"split": "holdout", "forecast_origin_timestamp_utc": origin, "horizon_h": horizon + 1})

        weekly = p0053ba2.select_weekly_holdout_origins(rows)

        self.assertEqual(weekly["weekly_origin_count"], 2)
        self.assertEqual(weekly["first_weekly_origin"], "2025-06-01T23:00:00Z")
        self.assertEqual(weekly["last_weekly_origin"], "2025-06-08T23:00:00Z")
        self.assertEqual(weekly["complete_168h_path_count"], 14)

    def test_validate_leakage_and_fairness_accepts_matching_base_plus_rows(self) -> None:
        rows = []
        for split, origin_text in (("validate", "2025-01-01T23:00:00Z"), ("holdout", "2025-06-01T23:00:00Z")):
            origin = datetime.fromisoformat(origin_text.replace("Z", "+00:00"))
            for horizon in range(168):
                target = (origin + timedelta(hours=horizon)).isoformat().replace("+00:00", "Z")
                rows.append(
                    {
                        "row_id": f"{origin_text}|{target}",
                        "forecast_origin_timestamp_utc": origin_text,
                        "input_data_cutoff_utc": (origin - timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
                        "target_timestamp_utc": target,
                        "horizon_h": horizon + 1,
                        "split": split,
                        "weather_proxy_label": p0053ba2.WEATHER_PROXY_LABEL,
                    }
                )
        row_sets = {}
        for model_name, _group, _model_class, _base_model in p00553ba2_required_models():
            row_sets[model_name] = {}
            for horizon in p0053ba2.HORIZONS:
                row_sets[model_name][str(horizon)] = {
                    "validate_row_ids": sorted(row["row_id"] for row in rows if row["split"] == "validate" and row["horizon_h"] == horizon),
                    "holdout_row_ids": sorted(row["row_id"] for row in rows if row["split"] == "holdout" and row["horizon_h"] == horizon),
                }

        review = p0053ba2.validate_leakage_and_fairness(rows, row_sets, {"ok": True, "coverage_warning": "synthetic"})

        self.assertTrue(review["ok"])
        self.assertTrue(review["base_plus_identical_row_sets"])
        self.assertTrue(review["weather_actual_proxy_labeled"])


def p00553ba2_required_models():
    return p0053ba2.REQUIRED_MODELS


if __name__ == "__main__":
    unittest.main()
