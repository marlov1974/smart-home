from __future__ import annotations

import sqlite3
import unittest

from src.mac.services.spotprice_model_diagnostics import p0054w


class P0054WTest(unittest.TestCase):
    def test_classify_table_candidate_detects_mga_consumption(self) -> None:
        result = p0054w.classify_table_candidate(
            "esett_mga_consumption_native_v1",
            ["mga_id", "interval_start_utc", "settlement_class", "value"],
        )
        self.assertTrue(result["is_candidate"])
        self.assertTrue(result["has_mga_term"])
        self.assertTrue(result["has_consumption_term"])
        self.assertTrue(result["has_esett_term"])

    def test_settlement_class_from_measure(self) -> None:
        self.assertEqual(p0054w.settlement_class_from_measure("consumption_profiled"), "profiled_or_monthly_settled")
        self.assertEqual(p0054w.settlement_class_from_measure("consumption_metered"), "metered_settled_unknown_native_resolution")
        self.assertEqual(p0054w.settlement_class_from_measure("consumption_total"), "aggregate_consumption_total")
        self.assertEqual(p0054w.settlement_class_from_measure("production_total"), "unknown_or_not_consumption")

    def test_resolution_transition_summary_detects_mixed_resolution(self) -> None:
        summary = p0054w.resolution_transition_summary([
            "2025-01-01T00:00:00Z",
            "2025-01-01T01:00:00Z",
            "2025-01-01T01:15:00Z",
            "2025-01-01T01:30:00Z",
        ])
        self.assertEqual(summary["observed_time_deltas_minutes"], {"15": 2, "60": 1})
        self.assertTrue(summary["mixed_resolution_periods"])
        self.assertEqual(summary["share_60m"], 1 / 3)
        self.assertEqual(summary["share_15m"], 2 / 3)
        self.assertEqual(summary["transition_date_candidate"], "2025-01-01T01:15:00Z")

    def test_sqlite_table_inventory_filters_candidates(self) -> None:
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("CREATE TABLE esett_mga_consumption_native_v1 (mga_id TEXT, interval_start_utc TEXT, settlement_class TEXT)")
        conn.execute("INSERT INTO esett_mga_consumption_native_v1 VALUES ('SE-MGA-1', '2025-01-01T00:00:00Z', 'hourly_settled')")
        conn.execute("CREATE TABLE unrelated (id INTEGER)")
        inventory = p0054w.sqlite_table_inventory(conn)
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0]["source_name"], "esett_mga_consumption_native_v1")
        self.assertEqual(inventory[0]["row_count"], 1)
        self.assertEqual(inventory[0]["min_timestamp"], "2025-01-01T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
