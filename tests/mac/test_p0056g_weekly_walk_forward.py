from __future__ import annotations

import unittest

from src.mac.services.spotprice_model_diagnostics import p0056g


class P0056GWeeklyWalkForwardTests(unittest.TestCase):
    def test_next_monday_after_primary_start(self) -> None:
        self.assertEqual(p0056g.next_monday(p0056g.PRIMARY_START_LOCAL).isoformat(), "2025-06-02")

    def test_metric_scope_counts_forward_rows(self) -> None:
        rows = []
        for hour in range(-6, 162):
            rows.append({
                "horizon_hours": hour,
                "target_consumption_se3_mw": 100.0,
                p0056g.PREDICTION_COLUMN: 110.0,
            })
        metrics = p0056g.metric_scope(rows, p0056g.PREDICTION_COLUMN)
        self.assertEqual(metrics["rows"], 168)
        self.assertAlmostEqual(float(metrics["MAE"]), 10.0)
        self.assertAlmostEqual(float(metrics["bias"]), 10.0)

    def test_leakage_review_rejects_forbidden_feature(self) -> None:
        review = p0056g.leakage_review(
            [{"forecast_rows_168h": 168, "forecast_rows_162h": 162}],
            [{"input_data_cutoff_utc": "2025-06-01T22:00:00Z", "forecast_origin_timestamp_utc": "2025-06-02T04:00:00Z"}],
            ["target_month", "spot_price"],
        )
        self.assertFalse(review["ok"])
        self.assertEqual(review["forbidden_features"], ["spot_price"])


if __name__ == "__main__":
    unittest.main()
