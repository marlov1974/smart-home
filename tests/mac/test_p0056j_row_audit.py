from __future__ import annotations

import unittest

from src.mac.services.spotprice_model_diagnostics import p0056j


class P0056JRowAuditTests(unittest.TestCase):
    def test_intersect_rows_uses_origin_and_target_key(self) -> None:
        static = [
            {"forecast_origin_timestamp_utc": "o1", "target_timestamp_utc": "t1", "prediction": 1.0},
            {"forecast_origin_timestamp_utc": "o2", "target_timestamp_utc": "t2", "prediction": 2.0},
        ]
        rolling = [
            {"forecast_origin_timestamp_utc": "o2", "target_timestamp_utc": "t2", "prediction": 3.0},
            {"forecast_origin_timestamp_utc": "o1", "target_timestamp_utc": "different", "prediction": 4.0},
        ]

        pairs = p0056j.intersect_rows(static, rolling)

        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["forecast_origin_timestamp_utc"], "o2")
        self.assertEqual(pairs[0]["target_timestamp_utc"], "t2")

    def test_feature_diff_counts_numeric_matches_and_deltas(self) -> None:
        pairs = [
            {"key": ("o1", "t1"), "static": {"x": 1.0, "label": "a"}, "rolling": {"x": 1.0, "label": "a"}},
            {"key": ("o1", "t2"), "static": {"x": 2.0, "label": "a"}, "rolling": {"x": 5.0, "label": "b"}},
        ]

        summary = {row["feature"]: row for row in p0056j.summarize_feature_diffs(pairs, ["x", "label"])}

        self.assertEqual(summary["x"]["exact_match_count"], 1)
        self.assertEqual(summary["x"]["mismatch_count"], 1)
        self.assertEqual(summary["x"]["max_abs_delta"], 3.0)
        self.assertEqual(summary["label"]["mismatch_count"], 1)


if __name__ == "__main__":
    unittest.main()
