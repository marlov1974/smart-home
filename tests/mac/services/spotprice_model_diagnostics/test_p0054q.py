import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.mac.services.spotprice_model_diagnostics import p0054q


class P0054QTests(unittest.TestCase):
    def test_load_entsoe_se3_target_rows_maps_correct_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "features.sqlite3"
            with sqlite3.connect(db) as conn:
                conn.execute(
                    f"""
                    CREATE TABLE {p0054q.TARGET_TABLE} (
                        timestamp_utc TEXT, area TEXT, consumption_mw REAL,
                        source_system TEXT, source_measure TEXT, source_area_code TEXT,
                        resolution TEXT, unit TEXT, timezone_handling TEXT,
                        package_id TEXT, quality_flag TEXT
                    )
                    """
                )
                conn.executemany(
                    f"INSERT INTO {p0054q.TARGET_TABLE} VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    [
                        ("2022-06-01T00:00:00Z", "SE3", 8000.0, "ENTSO-E", "actual_total_load", "10Y1001A1001A46L", "PT60M", "MW", "UTC", "P0054P2", "ok"),
                        ("2025-06-01T00:00:00Z", "SE3", 9000.0, "ENTSO-E", "actual_total_load", "10Y1001A1001A46L", "PT60M", "MW", "UTC", "P0054P2", "ok"),
                    ],
                )
            rows = p0054q.load_entsoe_se3_target_rows(db)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["target_source_table"], p0054q.TARGET_TABLE)
        self.assertEqual(rows[0]["target_source_column"], "consumption_mw")
        self.assertEqual(rows[0]["consumption_se3"], 8000.0)

    def test_validate_entsoe_target_contract_rejects_old_source(self):
        rows = [
            {
                "timestamp_utc": "2022-06-01T00:00:00Z",
                "consumption_se3": 8000.0,
                "target_source_table": "physical_balance_se1_se4_hourly_v1",
                "target_source_column": "consumption_se3",
                "target_source_measure": "proxy",
                "target_source_area": "SE3",
                "target_source_package_id": "old",
            },
            {
                "timestamp_utc": "2025-06-01T00:00:00Z",
                "consumption_se3": 9000.0,
                "target_source_table": "physical_balance_se1_se4_hourly_v1",
                "target_source_column": "consumption_se3",
                "target_source_measure": "proxy",
                "target_source_area": "SE3",
                "target_source_package_id": "old",
            },
        ]
        self.assertFalse(p0054q.validate_entsoe_target_contract(rows)["ok"])

    def test_percent_metrics(self):
        rows = [
            {"target_consumption_se3_mw": 100.0, "pred_model": 110.0},
            {"target_consumption_se3_mw": 300.0, "pred_model": 270.0},
        ]
        summary = {"pred_model": {}}
        p0054q.add_percent_metrics(summary, rows, ("pred_model",), "dayahead")
        self.assertEqual(summary["pred_model"]["hourly_MAE_delivery_day"], 20.0)
        self.assertEqual(summary["pred_model"]["MAE_percent_of_mean_actual"], 10.0)

    def test_leakage_review_rejects_forbidden_columns(self):
        review = p0054q.validate_p0054q_leakage(
            {"ok": True},
            {"ok": True},
            {"ok": True},
            {"ok": True, "source_table": p0054q.TARGET_TABLE},
            {"no_price": {"features": ["target_hour"]}},
            [{"physical_balance_target": 1}],
        )
        self.assertFalse(review["ok"])


if __name__ == "__main__":
    unittest.main()
