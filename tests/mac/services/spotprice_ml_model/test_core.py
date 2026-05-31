from pathlib import Path
import sqlite3
import tempfile
import unittest

from src.mac.services.spotprice_ml_model.core import (
    FEATURE_NAMES,
    TrainingRow,
    build_calendar_features,
    build_clipped_month_curves,
    build_feature_store,
    build_level_targets,
    fit_ridge,
    load_p0033_training_series,
    load_p0035_training_series,
    recompose_se3_predictions,
    split_for_date,
    train_m4,
    validate_m4_outputs,
)


def create_feature_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE m3_temp_normalized_prices_v1 (
              utc_hour_start TEXT PRIMARY KEY,
              local_date TEXT NOT NULL,
              local_hour INTEGER NOT NULL,
              temp_normalized_price_v1_se1 REAL NOT NULL,
              temp_normalized_area_diff_v1 REAL NOT NULL,
              temp_normalized_price_v1_se3 REAL NOT NULL,
              normal_price_v1_se1 REAL NOT NULL,
              normal_price_v1_area_diff REAL NOT NULL
            )
            """
        )
        rows = []
        for year in (2024, 2025, 2026):
            for day in range(1, 41):
                local_date = f"{year}-01-{((day - 1) % 31) + 1:02d}" if day <= 31 else f"{year}-02-{day - 31:02d}"
                for hour in range(24):
                    se1 = 1.0 + hour / 100.0 + (year - 2024) * 0.05
                    area = 0.2 + (day % 5) / 100.0
                    rows.append(
                        (
                            f"{local_date}T{hour:02d}:00Z",
                            local_date,
                            hour,
                            se1,
                            area,
                            se1 + area,
                            0.9,
                            0.15,
                        )
                    )
        conn.executemany("INSERT INTO m3_temp_normalized_prices_v1 VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows)


def create_p0035_feature_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE m3ab_normalized_prices (
              utc_hour_start TEXT PRIMARY KEY,
              local_date TEXT NOT NULL,
              local_hour INTEGER NOT NULL,
              actual_se1 REAL NOT NULL,
              actual_area_diff REAL NOT NULL,
              actual_se3 REAL NOT NULL,
              normal_price_v1_se1 REAL NOT NULL,
              normal_price_v1_area_diff REAL NOT NULL,
              m3a_temperature_delta_se1 REAL NOT NULL,
              m3a_temperature_delta_area_diff REAL NOT NULL,
              m3b_special_day_delta_se1 REAL NOT NULL,
              m3b_special_day_delta_area_diff REAL NOT NULL,
              m3ab_normalized_price_se1 REAL NOT NULL,
              m3ab_normalized_area_diff REAL NOT NULL,
              m3ab_normalized_se3 REAL NOT NULL,
              special_day_type TEXT NOT NULL,
              special_day_name TEXT NOT NULL,
              special_day_group TEXT NOT NULL,
              is_special_day INTEGER NOT NULL,
              run_id INTEGER NOT NULL
            )
            """
        )
        rows = []
        for year in (2024, 2025, 2026):
            for day in range(1, 41):
                local_date = f"{year}-01-{((day - 1) % 31) + 1:02d}" if day <= 31 else f"{year}-02-{day - 31:02d}"
                for hour in range(24):
                    baseline = 1.0 + hour / 100.0
                    area_base = 0.2
                    residual = (year - 2024) * 0.03
                    se1 = baseline + residual
                    area = area_base + residual / 2
                    rows.append(
                        (
                            f"{local_date}T{hour:02d}:00Z",
                            local_date,
                            hour,
                            se1,
                            area,
                            se1 + area,
                            baseline,
                            area_base,
                            0,
                            0,
                            0,
                            0,
                            se1,
                            area,
                            se1 + area,
                            "normal_weekday",
                            "normal",
                            "normal",
                            0,
                            1,
                        )
                    )
        conn.executemany("INSERT INTO m3ab_normalized_prices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)


class SpotpriceMlModelTests(unittest.TestCase):
    def test_load_p0033_training_series(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "features.sqlite3"
            create_feature_db(db)
            rows = load_p0033_training_series(db)
        self.assertEqual(3 * 40 * 24, len(rows))
        self.assertAlmostEqual(rows[0].target_se3, rows[0].target_se1 + rows[0].target_area_diff)

    def test_load_p0035_training_series_uses_residual_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "features.sqlite3"
            create_p0035_feature_db(db)
            rows = load_p0035_training_series(db)
        self.assertEqual(3 * 40 * 24, len(rows))
        self.assertAlmostEqual(rows[0].target_se1, rows[0].target_se3 - rows[0].target_area_diff)

    def test_feature_schema_excludes_weather(self):
        row = TrainingRow("u", "2025-01-01", 8, 1.0, 0.2, 1.2, 0.9, 0.1, 1.0)
        features = build_calendar_features([row])
        self.assertEqual(len(FEATURE_NAMES), len(features["u"]))
        self.assertFalse(any(token in name for name in FEATURE_NAMES for token in ("temp", "weather", "wind", "cloud")))

    def test_split_is_time_based(self):
        self.assertEqual("train", split_for_date("2024-12-31"))
        self.assertEqual("validate", split_for_date("2025-06-01"))
        self.assertEqual("holdout", split_for_date("2026-01-01"))

    def test_ridge_can_fit_linear_relation(self):
        coefficients = fit_ridge([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]], [1.0, 3.0, 5.0], 0.0)
        self.assertAlmostEqual(1.0, coefficients[0], places=6)
        self.assertAlmostEqual(2.0, coefficients[1], places=6)

    def test_clipped_month_curves_mean_to_one(self):
        rows = [
            TrainingRow(f"u{i}", "2025-01-31" if i < 24 else "2025-02-01", i % 24, 1.0 + (i % 3), 0.2, 1.2, 1, 0.2, 1.2)
            for i in range(48)
        ]
        levels = build_level_targets(rows)
        curves = build_clipped_month_curves(rows, levels)
        jan = [row["actual_index"] for row in curves if row["target"] == "system_proxy_se1" and row["curve_key"].startswith("2025-01")]
        feb = [row["actual_index"] for row in curves if row["target"] == "system_proxy_se1" and row["curve_key"].startswith("2025-02")]
        self.assertAlmostEqual(1.0, sum(jan) / len(jan))
        self.assertAlmostEqual(1.0, sum(feb) / len(feb))

    def test_recompose_se3_predictions(self):
        rows = recompose_se3_predictions([{"pred_se1": 1.0, "pred_area_diff": 0.25}])
        self.assertEqual(1.25, rows[0]["pred_se3"])

    def test_end_to_end_train_and_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            feature_db = Path(tmp) / "features.sqlite3"
            model_dir = Path(tmp) / "m4"
            create_feature_db(feature_db)
            feature_result = build_feature_store(feature_db=feature_db, model_dir=model_dir)
            train_result = train_m4(feature_db=feature_db, model_dir=model_dir)
            validation = validate_m4_outputs(feature_db=feature_db, model_dir=model_dir)
        self.assertTrue(feature_result["ok"])
        self.assertTrue(train_result["ok"])
        self.assertTrue(train_result["promotion"]["ok"])
        self.assertTrue(validation["ok"])
        self.assertEqual([], validation["forbidden_features"])


if __name__ == "__main__":
    unittest.main()
