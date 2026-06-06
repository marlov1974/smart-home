from __future__ import annotations

import unittest

from src.mac.services.spotprice_model_diagnostics import p0054w_esett_fetch as fetch


class P0054WEsettFetchTest(unittest.TestCase):
    def test_month_ranges(self) -> None:
        ranges = fetch.month_ranges("2022-06-15T00:00:00Z", "2022-08-01T00:00:00Z")
        self.assertEqual(ranges, [
            ("2022-06-15T00:00:00Z", "2022-07-01T00:00:00Z"),
            ("2022-07-01T00:00:00Z", "2022-08-01T00:00:00Z"),
        ])

    def test_infer_resolution_minutes(self) -> None:
        self.assertEqual(fetch.infer_resolution_minutes([
            "2025-01-01T00:00:00Z",
            "2025-01-01T00:15:00Z",
            "2025-01-01T00:30:00Z",
        ]), 15)
        self.assertEqual(fetch.infer_resolution_minutes([
            "2022-01-01T00:00:00Z",
            "2022-01-01T01:00:00Z",
        ]), 60)

    def test_native_rows_preserve_source_sign_and_resolution(self) -> None:
        rows = fetch.native_rows_from_payload(
            {"mgaCode": "STH", "mgaName": "Stockholm", "country": "SE"},
            [
                {"timestampUTC": "2025-01-01T00:00:00Z", "mgaCode": "STH", "mgaName": "Stockholm", "mba": "SE3", "quantity": -1.25},
                {"timestampUTC": "2025-01-01T00:15:00Z", "mgaCode": "STH", "mgaName": "Stockholm", "mba": "SE3", "quantity": -1.50},
            ],
        )
        self.assertEqual(rows[0]["value"], -1.25)
        self.assertEqual(rows[0]["unit"], "MWh")
        self.assertEqual(rows[0]["resolution_minutes"], 15)
        self.assertEqual(rows[0]["interval_end_utc"], "2025-01-01T00:15:00Z")
        self.assertEqual(rows[0]["settlement_class"], "profiled_load_profile")


if __name__ == "__main__":
    unittest.main()
