from __future__ import annotations

from datetime import date
import unittest

from src.mac.services.spotprice_model_diagnostics import p0056n


class P0056NDstAuditTests(unittest.TestCase):
    def test_expected_stockholm_spring_forward_day_has_23_hours(self) -> None:
        rows = p0056n.expected_local_hours_for_day(date(2026, 3, 29))
        self.assertEqual(len(rows), 23)
        self.assertNotIn(2, {row["local_hour"] for row in rows})
        self.assertIn(3, {row["local_hour"] for row in rows})

    def test_p0056k_mapping_duplicates_utc_on_spring_forward_day(self) -> None:
        rows = p0056n.p0056k_delivery_day_mapping(date(2026, 3, 29))
        timestamps = [row["target_timestamp_utc"] for row in rows]
        self.assertEqual(len(rows), 24)
        self.assertEqual(len(set(timestamps)), 23)
        self.assertTrue(any(row["is_duplicate_utc"] for row in rows))
        self.assertTrue(any(row["forced_nonexistent_or_shifted_local_hour"] for row in rows))

    def test_standard_day_has_24_valid_hours_and_no_duplicate_mapping(self) -> None:
        expected = p0056n.expected_local_hours_for_day(date(2026, 3, 28))
        mapped = p0056n.p0056k_delivery_day_mapping(date(2026, 3, 28))
        self.assertEqual(len(expected), 24)
        self.assertEqual(len({row["target_timestamp_utc"] for row in mapped}), 24)
        self.assertFalse(any(row["is_duplicate_utc"] for row in mapped))

    def test_target_classification_marks_source_observed_outlier(self) -> None:
        hourly = [
            {"day": "2026-03-21", "mean_actual_mw": 1800.0},
            {"day": "2026-03-25", "mean_actual_mw": 1820.0},
            {"day": "2026-03-26", "mean_actual_mw": 2220.0},
            {"day": "2026-03-27", "mean_actual_mw": 1830.0},
            {"day": "2026-03-28", "mean_actual_mw": 5480.0, "duplicate_utc_timestamp_count": 0, "missing_expected_utc_hour_count": 0, "coverage_flag_distribution": "ok:24"},
            {"day": "2026-03-29", "mean_actual_mw": 1820.0},
            {"day": "2026-03-30", "mean_actual_mw": 1930.0},
            {"day": "2026-03-31", "mean_actual_mw": 1980.0},
            {"day": "2026-04-04", "mean_actual_mw": 1800.0},
        ]
        native = [{"day": "2026-03-28", "mean_mw": 5480.0}]
        forecast = [{"delivery_date_local": "2026-03-29", "p0056k_duplicate_utc_for_delivery_day": True}]
        spikes = [{"actual_mw": 7200.0}]
        result = p0056n.target_anomaly_classification(hourly, native, forecast, spikes)
        self.assertEqual(result["classification"], "probable_target_source_anomaly")
        self.assertTrue(result["source_observed_in_native_rows"])
        self.assertTrue(result["separate_dst_bug_confirmed_for_2026_03_29"])


if __name__ == "__main__":
    unittest.main()
