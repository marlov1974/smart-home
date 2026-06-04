from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from src.mac.services.spotprice_model_diagnostics import p0054b


class P0054BTests(unittest.TestCase):
    def test_lag_and_rollup_features_use_rows_strictly_before_origin(self) -> None:
        values = [float(index) for index in range(200)]
        origin_index = 168

        lags = p0054b.lag_features_at_origin(values, origin_index)
        rollups = p0054b.rolling_features_at_origin(values, origin_index)

        self.assertEqual(lags["consumption_se3_lag_1h"], 167.0)
        self.assertEqual(lags["consumption_se3_lag_168h"], 0.0)
        self.assertNotIn(168.0, [lags["consumption_se3_lag_1h"], lags["consumption_se3_lag_168h"]])
        self.assertAlmostEqual(rollups["consumption_se3_roll_mean_24h"], sum(range(144, 168)) / 24)
        self.assertEqual(rollups["consumption_se3_roll_max_24h"], 167.0)

    def test_feature_contract_excludes_forbidden_market_and_grid_inputs(self) -> None:
        review = p0054b.validate_feature_contract(p0054b.feature_group_contract())

        self.assertTrue(review["ok"])
        self.assertEqual(review["violations"], [])

    def test_weekly_holdout_origin_selection_requires_complete_168h_paths(self) -> None:
        rows = []
        start = datetime(2025, 6, 1, 0, tzinfo=timezone.utc)
        for week in range(3):
            origin = (start + timedelta(days=7 * week)).isoformat().replace("+00:00", "Z")
            last_horizon = 168 if week != 1 else 167
            for horizon in range(1, last_horizon + 1):
                rows.append(
                    {
                        "split": "holdout",
                        "forecast_origin_timestamp_utc": origin,
                        "horizon_h": horizon,
                        p0054b.HGB_PREDICTION_COLUMN: float(horizon),
                        p0054b.MLP_PREDICTION_COLUMN: float(horizon),
                    }
                )

        selection = p0054b.select_weekly_holdout_origins(rows)

        self.assertEqual(selection["weekly_origin_count"], 2)
        self.assertEqual(selection["weekly_origins"][0], "2025-06-01T00:00:00Z")
        self.assertEqual(selection["weekly_origins"][1], "2025-06-15T00:00:00Z")
        self.assertEqual(selection["complete_168h_path_count"], 2)

    def test_identical_row_set_validation_detects_matching_predictions(self) -> None:
        rows = []
        for split in ("validate", "holdout"):
            for horizon in p0054b.HORIZONS:
                rows.append(
                    {
                        "split": split,
                        "forecast_origin_timestamp_utc": f"2025-06-01T{horizon % 24:02d}:00:00Z",
                        "target_timestamp_utc": f"2025-06-02T{horizon % 24:02d}:00:00Z",
                        "horizon_h": horizon,
                        "weather_proxy_label": p0054b.WEATHER_PROXY_LABEL,
                        p0054b.HGB_PREDICTION_COLUMN: 1.0,
                        p0054b.MLP_PREDICTION_COLUMN: 2.0,
                    }
                )

        review = p0054b.validate_identical_row_sets(rows, (p0054b.HGB_PREDICTION_COLUMN, p0054b.MLP_PREDICTION_COLUMN))

        self.assertTrue(review["ok"])
        self.assertTrue(review["weather_actual_proxy_labeled"])


if __name__ == "__main__":
    unittest.main()
