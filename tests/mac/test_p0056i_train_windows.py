from __future__ import annotations

import unittest

from src.mac.services.spotprice_model_diagnostics import p0056i


class P0056ITrainWindowTests(unittest.TestCase):
    def test_train_window_start_uses_calendar_years(self) -> None:
        origin = "2025-06-01T04:00:00Z"
        self.assertEqual(p0056i.train_window_start_utc("TW2", origin), "2023-06-01T04:00:00Z")
        self.assertEqual(p0056i.train_window_start_utc("TW3", origin), "2022-06-01T04:00:00Z")
        self.assertEqual(p0056i.train_window_start_utc("TWX", origin), "2022-06-01T00:00:00Z")

    def test_filter_train_rows_is_start_inclusive_and_origin_exclusive(self) -> None:
        rows = [
            {"target_timestamp_utc": "2023-05-31T23:00:00Z", "value": "before"},
            {"target_timestamp_utc": "2023-06-01T04:00:00Z", "value": "start"},
            {"target_timestamp_utc": "2025-06-01T03:00:00Z", "value": "last"},
            {"target_timestamp_utc": "2025-06-01T04:00:00Z", "value": "origin"},
        ]

        selected = p0056i.filter_train_rows_for_window(rows, "2025-06-01T04:00:00Z", "TW2")

        self.assertEqual([row["value"] for row in selected], ["start", "last"])


if __name__ == "__main__":
    unittest.main()
