from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import sqlite3
import tempfile
import unittest

from src.mac.services.spotprice_model_diagnostics import p0043


def make_row(day: date, hour: int, target: str = "system_proxy_se1") -> dict[str, object]:
    return {
        "timestamp_utc": f"{day.isoformat()}T{hour:02d}:00:00+00:00",
        "model_cet_date": day.isoformat(),
        "model_cet_hour": hour,
        "model_cet_weekday": day.weekday(),
        "model_cet_day_of_year": int(day.strftime("%j")),
        "model_cet_hour_sin": 0.0,
        "model_cet_hour_cos": 1.0,
        "model_cet_day_of_year_sin": 0.0,
        "model_cet_day_of_year_cos": 1.0,
        "weekday_sin": 0.0,
        "weekday_cos": 1.0,
        "stockholm_is_dst": 0,
        "stockholm_utc_offset_hours": 1,
        "stockholm_local_hour": hour,
        "target_series": target,
        "hour_shape": float(hour - 12) / 12.0,
        "base_day_type": "weekday",
        "special_day_type": "normal_weekday",
        "special_day_name": "normal",
        "is_special_day": 0,
        "is_bridge_day": 0,
        "is_holiday_period": 0,
        "is_major_social_holiday": 0,
        "hourly_temperature_actual": 5.0,
        "hourly_temperature_normal": 4.0,
        "hourly_temperature_delta": 1.0,
        "hourly_temperature_delta_minus_day_mean": 0.0,
        "hourly_temperature_delta_rank_in_day": hour / 23.0,
        "hourly_solar_actual": 10.0,
        "hourly_solar_normal": 9.0,
        "hourly_solar_delta": 1.0,
        "hourly_solar_delta_minus_day_mean": 0.0,
        "hourly_solar_delta_rank_in_day": hour / 23.0,
        "hourly_wind_actual": 0.2,
        "hourly_wind_normal": 0.1,
        "hourly_wind_delta": 0.1,
        "hourly_wind_delta_minus_day_mean": 0.0,
        "hourly_wind_delta_rank_in_day": hour / 23.0,
    }


class P0043Tests(unittest.TestCase):
    def test_assign_splits_are_chronological(self):
        rows = [make_row(date(2024, 12, 31), 0), make_row(date(2025, 1, 1), 0), make_row(date(2026, 1, 1), 0)]
        p0043.assign_splits(rows)
        self.assertEqual(["train", "validate", "holdout"], [row["split"] for row in rows])

    def test_baselines_fit_on_train_only(self):
        train = [make_row(date(2024, 1, 1), hour) for hour in range(24)]
        baseline = p0043.fit_baselines(train)["B1_hour_of_day_mean"]
        validate = [make_row(date(2025, 1, 1), 0)]
        validate[0]["hour_shape"] = 999.0
        self.assertAlmostEqual(train[0]["hour_shape"], p0043.predict_baseline(validate, baseline)[0])

    def test_categorical_encoding_is_deterministic(self):
        rows = [make_row(date(2024, 1, 1), 0), make_row(date(2024, 1, 2), 1)]
        rows[1]["base_day_type"] = "saturday"
        x1, enc = p0043.build_feature_matrix(rows, "F1_time_plus_calendar")
        x2, _ = p0043.build_feature_matrix(list(reversed(rows)), "F1_time_plus_calendar", enc)
        self.assertEqual(enc.categories["base_day_type"], ["saturday", "weekday"])
        self.assertEqual(len(x1[0]), len(x2[0]))

    def test_center_predictions_by_day_zeroes_daily_mean(self):
        rows = [make_row(date(2024, 1, 1), hour) for hour in range(24)]
        centered = p0043.center_predictions_by_day(rows, [2.0] * 24)
        self.assertAlmostEqual(0.0, sum(centered) / len(centered))

    def test_dataset_loader_requires_p0042_v2_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "features.sqlite3"
            sqlite3.connect(db).close()
            with self.assertRaises(RuntimeError):
                p0043.load_ai2_rows(db)

    def test_forbidden_paths_constant(self):
        self.assertEqual(("AI1", "M5", "M6", "M7", "API", "SHELLY", "DEVICE", "KVS", "HA"), p0043.FORBIDDEN_PRODUCTION_PATHS)


if __name__ == "__main__":
    unittest.main()
