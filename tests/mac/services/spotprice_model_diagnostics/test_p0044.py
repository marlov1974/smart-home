from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import math
import sqlite3
import tempfile
import unittest

from src.mac.services.spotprice_model_diagnostics import p0044


def make_row(day: date, series: str = "system_proxy_se1") -> dict[str, object]:
    return {
        "model_cet_date": day.isoformat(),
        "target_series": series,
        "local_7d_start": (day - timedelta(days=2)).isoformat(),
        "local_7d_end": (day + timedelta(days=4)).isoformat(),
        "local_7d_row_count": 168,
        "day_level_shape": float(day.day % 7) / 3.0 - 1.0,
        "log_day_scale_index": float(day.weekday()) / 10.0,
        "log_local_7d_scale": 0.5,
        "weekday": day.weekday(),
        "weekday_sin": 0.0,
        "weekday_cos": 1.0,
        "day_of_year": int(day.strftime("%j")),
        "day_of_year_sin": 0.0,
        "day_of_year_cos": 1.0,
        "base_day_type": "weekday",
        "special_day_type": "normal_weekday",
        "special_day_name": "normal",
        "is_special_day": 0,
        "is_bridge_day": 0,
        "is_holiday_period": 0,
        "is_major_social_holiday": 0,
        "daily_temperature_actual": 5.0,
        "daily_temperature_normal": 4.0,
        "daily_temperature_delta": 1.0,
        "daily_solar_actual": 10.0,
        "daily_solar_normal": 9.0,
        "daily_solar_delta": 1.0,
        "daily_wind_actual": 0.2,
        "daily_wind_normal": 0.1,
        "daily_wind_delta": 0.1,
        "daily_wind_system_proxy": 0.2,
        "daily_wind_south_proxy": 0.3,
        "daily_wind_central_proxy": 0.2,
        "daily_wind_north_proxy": 0.1,
        "daily_wind_south_minus_north": 0.2,
        "daily_wind_central_minus_north": 0.1,
        "daily_temperature_delta_minus_local_7d_mean": 0.0,
        "daily_temperature_delta_rank_in_local_7d": 0.5,
        "daily_solar_delta_minus_local_7d_mean": 0.0,
        "daily_solar_delta_rank_in_local_7d": 0.5,
        "daily_wind_delta_minus_local_7d_mean": 0.0,
        "daily_wind_delta_rank_in_local_7d": 0.5,
    }


class P0044Tests(unittest.TestCase):
    def test_dataset_loader_requires_p0042_v2_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "features.sqlite3"
            sqlite3.connect(db).close()
            with self.assertRaises(RuntimeError):
                p0044.load_ai1_rows(db)

    def test_assign_splits_are_chronological(self):
        rows = [make_row(date(2024, 12, 31)), make_row(date(2025, 1, 1)), make_row(date(2026, 1, 1))]
        p0044.assign_splits(rows)
        self.assertEqual(["train", "validate", "holdout"], [row["split"] for row in rows])

    def test_target_constants_do_not_include_absolute_or_ratio_targets(self):
        self.assertEqual(("day_level_shape", "log_day_scale_index", "log_local_7d_scale"), p0044.TARGET_NAMES)
        self.assertNotIn("day_mean_price", p0044.TARGET_NAMES)
        self.assertNotIn("day_ratio_index_diagnostic", p0044.TARGET_NAMES)

    def test_baselines_fit_on_train_only(self):
        train = [make_row(date(2024, 1, 1) + timedelta(days=offset)) for offset in range(14)]
        baseline = p0044.fit_baselines(train, "day_level_shape")["B1_weekday_mean"]
        validate = [make_row(date(2025, 1, 6))]
        validate[0]["day_level_shape"] = 999.0
        self.assertNotEqual(999.0, p0044.predict_baseline(validate, baseline)[0])

    def test_categorical_encoding_is_deterministic(self):
        rows = [make_row(date(2024, 1, 1)), make_row(date(2024, 1, 2))]
        rows[1]["base_day_type"] = "saturday"
        x1, enc = p0044.build_feature_matrix(rows, "F1_time_plus_calendar")
        x2, _ = p0044.build_feature_matrix(list(reversed(rows)), "F1_time_plus_calendar", enc)
        self.assertEqual(enc.categories["base_day_type"], ["saturday", "weekday"])
        self.assertEqual(len(x1[0]), len(x2[0]))

    def test_local_window_metrics_cross_calendar_year(self):
        rows = [make_row(date(2025, 12, 29) + timedelta(days=offset)) for offset in range(10)]
        preds = [float(index) for index, _row in enumerate(rows)]
        metrics = p0044.local_window_rank_metrics(rows, preds, "day_level_shape")
        self.assertGreater(metrics["local_window_count"], 0.0)

    def test_predictions_are_finite_on_small_synthetic_training_set(self):
        train = [make_row(date(2024, 1, 1) + timedelta(days=offset)) for offset in range(120)]
        model, encoder = p0044.train_hgb_model(train, "F0_time_only", "day_level_shape")
        preds = p0044.predict_model(model, encoder, train[:5], "F0_time_only")
        self.assertTrue(all(math.isfinite(value) for value in preds))

    def test_forbidden_paths_constant(self):
        self.assertEqual(("AI2_RETRAIN", "COMBINED_168H", "M5", "M6", "M7", "API", "SHELLY", "DEVICE", "KVS", "HA"), p0044.FORBIDDEN_PRODUCTION_PATHS)


if __name__ == "__main__":
    unittest.main()
