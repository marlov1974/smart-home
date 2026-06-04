from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from src.mac.services.spotprice_model_diagnostics import p0054d, p0054e


class P0054ETests(unittest.TestCase):
    def test_optional_model_specs_include_installed_boosting_packages(self) -> None:
        specs = p0054e.optional_model_specs(
            {
                "lightgbm": {"ok": True, "version": "test"},
                "xgboost": {"ok": True, "version": "test"},
            }
        )

        self.assertEqual(
            [spec.name for spec in specs],
            [
                p0054e.EXTRATREES_MODEL_NAME,
                p0054e.LIGHTGBM_MODEL_NAME,
                p0054e.XGBOOST_MODEL_NAME,
            ],
        )

    def test_optional_model_specs_can_run_with_only_one_boosting_package(self) -> None:
        specs = p0054e.optional_model_specs(
            {
                "lightgbm": {"ok": False, "error": "missing libomp"},
                "xgboost": {"ok": True, "version": "test"},
            }
        )

        self.assertEqual([spec.name for spec in specs], [p0054e.EXTRATREES_MODEL_NAME, p0054e.XGBOOST_MODEL_NAME])

    def test_feature_contract_excludes_forbidden_market_and_grid_inputs(self) -> None:
        review = p0054d.validate_feature_contract(p0054d.feature_group_contract())

        self.assertTrue(review["ok"])
        self.assertEqual(review["violations"], [])

    def test_weekly_origin_selection_uses_dynamic_prediction_columns(self) -> None:
        columns = (
            p0054e.MODEL_TO_COLUMN[p0054e.EXTRATREES_MODEL_NAME],
            p0054e.MODEL_TO_COLUMN[p0054e.LIGHTGBM_MODEL_NAME],
            p0054e.MODEL_TO_COLUMN[p0054e.XGBOOST_MODEL_NAME],
        )
        rows = []
        start = datetime(2025, 6, 1, 0, tzinfo=timezone.utc)
        for week in range(2):
            origin = (start + timedelta(days=7 * week)).isoformat().replace("+00:00", "Z")
            last_horizon = 168 if week == 0 else 167
            for horizon in range(1, last_horizon + 1):
                row = {
                    "split": "holdout",
                    "forecast_origin_timestamp_utc": origin,
                    "horizon_h": horizon,
                }
                for column in columns:
                    row[column] = float(horizon)
                rows.append(row)

        selection = p0054e.select_weekly_holdout_origins(rows, columns)

        self.assertEqual(selection["weekly_origin_count"], 1)
        self.assertEqual(selection["weekly_origins"], ["2025-06-01T00:00:00Z"])
        self.assertEqual(selection["skipped_origins_with_reason"][0]["available_horizons"], 167)

    def test_identical_row_set_validation_uses_dynamic_prediction_columns(self) -> None:
        columns = (
            p0054e.MODEL_TO_COLUMN[p0054e.EXTRATREES_MODEL_NAME],
            p0054e.MODEL_TO_COLUMN[p0054e.LIGHTGBM_MODEL_NAME],
        )
        rows = []
        for split in ("validate", "holdout"):
            for horizon in p0054d.HORIZONS:
                row = {
                    "split": split,
                    "forecast_origin_timestamp_utc": f"2025-06-01T{horizon % 24:02d}:00:00Z",
                    "target_timestamp_utc": f"2025-06-02T{horizon % 24:02d}:00:00Z",
                    "horizon_h": horizon,
                    "weather_proxy_label": p0054d.WEATHER_PROXY_LABEL,
                }
                for column in columns:
                    row[column] = 1.0
                rows.append(row)

        review = p0054e.validate_identical_row_sets(rows, columns)

        self.assertTrue(review["ok"])
        self.assertTrue(review["weather_actual_proxy_labeled"])

    def test_relative_change_threshold_is_negative_for_improvement(self) -> None:
        self.assertEqual(p0054e.relative_change(98.0, 100.0), -2.0)


if __name__ == "__main__":
    unittest.main()
