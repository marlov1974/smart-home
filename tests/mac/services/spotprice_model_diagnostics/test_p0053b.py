from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from src.mac.services.spotprice_model_diagnostics import p0053b


def source_rows(count: int = 400, start: datetime | None = None) -> list[dict[str, object]]:
    start = start or datetime(2024, 1, 1, tzinfo=timezone.utc)
    rows = []
    for idx in range(count):
        ts = start + timedelta(hours=idx)
        model = ts + timedelta(hours=1)
        rows.append({
            "timestamp_utc": ts.isoformat().replace("+00:00", "Z"),
            "model_cet_timestamp": model.isoformat().replace("+00:00", "Z"),
            "model_cet_date": model.date().isoformat(),
            "model_cet_hour": model.hour,
            "model_cet_weekday": model.weekday(),
            "model_cet_day_of_year": model.timetuple().tm_yday,
            "consumption_se1": 1000.0 + idx,
        })
    return rows


class P0053BTests(unittest.TestCase):
    def test_validate_target_contract_requires_unique_finite_positive_target(self):
        rows = source_rows(10)
        contract = p0053b.validate_target_contract(rows)
        self.assertTrue(contract["ok"])
        bad = rows + [dict(rows[-1])]
        self.assertFalse(p0053b.validate_target_contract(bad)["ok"])
        rows[0]["consumption_se1"] = -1
        self.assertFalse(p0053b.validate_target_contract(rows)["ok"])

    def test_lag_and_rolling_features_end_before_origin(self):
        values = [float(i) for i in range(300)]
        lags = p0053b.lag_features_at_origin(values, 200)
        rolls = p0053b.rolling_features_at_origin(values, 200)
        self.assertEqual(lags["consumption_se1_lag_1h"], 199.0)
        self.assertEqual(lags["consumption_se1_lag_168h"], 32.0)
        self.assertEqual(rolls["consumption_se1_roll_mean_6h"], sum(range(194, 200)) / 6)
        self.assertEqual(rolls["consumption_se1_roll_max_24h"], 199.0)

    def test_chronological_splits_use_target_date(self):
        rows = [
            {"target_timestamp_utc": "2024-12-31T23:00:00Z"},
            {"target_timestamp_utc": "2025-01-01T00:00:00Z"},
            {"target_timestamp_utc": "2025-06-01T00:00:00Z"},
        ]
        counts = p0053b.assign_chronological_splits(rows)
        self.assertEqual(counts, {"train": 1, "validate": 1, "holdout": 1})

    def test_direct_rows_filter_scored_targets_but_allow_context_lag_warmup(self):
        rows = source_rows(240, datetime(2022, 5, 24, tzinfo=timezone.utc))
        direct = p0053b.build_direct_horizon_rows(rows, {}, (1,))
        self.assertTrue(direct)
        self.assertGreaterEqual(min(row["target_timestamp_utc"] for row in direct), "2022-06-01T00:00:00Z")
        first = direct[0]
        self.assertLess(first["origin_timestamp_utc"], "2022-06-01T00:00:00Z")
        self.assertIn("consumption_se1_lag_168h", first)

    def test_train_profiles_are_train_only(self):
        train = [
            {"target_model_cet_weekday": 0, "target_model_cet_hour": 1, "target_month": 1, "target_consumption_se1_mw": 100.0},
            {"target_model_cet_weekday": 0, "target_model_cet_hour": 1, "target_month": 1, "target_consumption_se1_mw": 200.0},
        ]
        profiles = p0053b.fit_train_profiles(train)
        row = {"target_model_cet_weekday": 0, "target_model_cet_hour": 1, "target_month": 1}
        self.assertEqual(p0053b.profile_predict(profiles["calendar_hour_weekday"], row, ("target_model_cet_weekday", "target_model_cet_hour")), 150.0)

    def test_feature_group_contract_excludes_forbidden_forecast_features(self):
        contract = p0053b.feature_group_contract()
        self.assertEqual(contract["G6_diagnostic_historical_only_non_deployable"]["safety"], "historical_only_diagnostic")
        forecast_features = {
            feature
            for group in contract.values()
            if group["safety"] == "forecast_safe"
            for feature in group["features"]
        }
        forbidden = ("price", "production", "flow", "exchange", "a61", "future")
        self.assertFalse([feature for feature in forecast_features if any(part in feature.lower() for part in forbidden)])

    def test_path_origin_predictions_have_exact_168_hours(self):
        rows = source_rows(500, datetime(2025, 1, 1, tzinfo=timezone.utc))
        direct = p0053b.build_direct_horizon_rows(rows, {}, p0053b.HORIZONS)
        p0053b.assign_chronological_splits(direct)
        profiles = p0053b.fit_train_profiles([row for row in direct if row["split"] == "train"])
        metrics, path_rows = p0053b.evaluate_168h_paths(rows, profiles)
        self.assertTrue(path_rows)
        self.assertEqual({row["path_hours"] for row in path_rows}, {168})
        self.assertIn("B1_same_hour_previous_week_path", metrics)

    def test_metrics_are_reproducible(self):
        rows = [
            {"target_consumption_se1_mw": 10.0},
            {"target_consumption_se1_mw": 14.0},
        ]
        first = p0053b.regression_metric_from_predictions(rows, [9.0, 16.0])
        second = p0053b.regression_metric_from_predictions(rows, [9.0, 16.0])
        self.assertEqual(first, second)
        self.assertEqual(first["MAE"], 1.5)
        self.assertEqual(first["mean_actual_mw"], 12.0)
        self.assertEqual(first["median_actual_mw"], 12.0)
        self.assertAlmostEqual(first["MAE_percent_of_mean"], 12.5)


if __name__ == "__main__":
    unittest.main()
