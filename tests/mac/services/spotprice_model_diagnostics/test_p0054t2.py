import unittest

from src.mac.services.spotprice_model_diagnostics import p0054t2


class P0054T2Tests(unittest.TestCase):
    def test_rowset_summary_counts_overlap(self):
        r_rows = [
            {"forecast_origin_timestamp_utc": "2025-01-01T11:00:00Z", "target_timestamp_utc": "2025-01-02T00:00:00Z", "horizon_h": 14},
            {"forecast_origin_timestamp_utc": "2025-01-02T11:00:00Z", "target_timestamp_utc": "2025-01-03T00:00:00Z", "horizon_h": 14},
        ]
        t_rows = [
            {"forecast_origin_timestamp_utc": "2025-01-01T11:00:00Z", "target_timestamp_utc": "2025-01-02T00:00:00Z", "horizon_h": 14},
            {"forecast_origin_timestamp_utc": "2025-01-03T11:00:00Z", "target_timestamp_utc": "2025-01-04T00:00:00Z", "horizon_h": 14},
        ]

        summary = p0054t2.rowset_summary(r_rows, t_rows)

        self.assertEqual(2, summary["p0054r_target_rows"])
        self.assertEqual(2, summary["p0054t_target_rows"])
        self.assertEqual(1, summary["intersection_rows"])
        self.assertEqual(1, summary["r_only_origins"])
        self.assertEqual(1, summary["t_only_origins"])

    def test_model_alias_summary_detects_equal_predictions(self):
        rows = [
            {"weighted": 10.0, "bias": 10.0},
            {"weighted": 12.0, "bias": 12.0},
        ]
        evidence = {"horizon_bias_mw": {"1": 0.0, "2": 0.0}}

        summary = p0054t2.model_alias_summary(rows, "weighted", "bias", evidence)

        self.assertTrue(summary["m1_equals_m2"])
        self.assertEqual(0, summary["nonzero_horizon_bias_count"])
        self.assertEqual(0.0, summary["max_abs_prediction_difference_mw"])

    def test_prediction_diff_summary_reports_top_difference(self):
        left = [
            {"forecast_origin_timestamp_utc": "o1", "target_timestamp_utc": "t1", "horizon_h": 1, "left": 100.0},
            {"forecast_origin_timestamp_utc": "o2", "target_timestamp_utc": "t2", "horizon_h": 2, "left": 200.0},
        ]
        right = [
            {"forecast_origin_timestamp_utc": "o1", "target_timestamp_utc": "t1", "horizon_h": 1, "right": 90.0},
            {"forecast_origin_timestamp_utc": "o2", "target_timestamp_utc": "t2", "horizon_h": 2, "right": 260.0},
        ]

        summary = p0054t2.prediction_diff_summary(left, right, "left", "right")

        self.assertEqual(2, summary["overlap_rows"])
        self.assertEqual(60.0, summary["top20"][0]["abs_prediction_difference_mw"])
        self.assertEqual(35.0, summary["mean_abs_prediction_difference_mw"])


if __name__ == "__main__":
    unittest.main()
