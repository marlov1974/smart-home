import sqlite3
import unittest
from datetime import datetime, timezone

from src.mac.services.spotprice_model_diagnostics import p0052


SAMPLE_PAYLOAD = {
    "Data": [
        {
            "id": "1",
            "data": [
                {"id": "SE1_SE2", "value": 100.0},
                {"id": "SE2_SE3", "value": -50.0},
                {"id": "SE3_SE4", "value": 25.0},
                {"id": "NO4_SE1", "value": 10.0},
            ],
        },
        {
            "id": "2",
            "data": [
                {
                    "id": "SE",
                    "ElectricalAreas": [
                        {"AreaName": "SE1", "Import": 10.0, "Export": 100.0},
                        {"AreaName": "SE2", "Import": 100.0, "Export": 50.0},
                        {"AreaName": "SE3", "Import": 50.0, "Export": 25.0},
                        {"AreaName": "SE4", "Import": 25.0, "Export": 0.0},
                    ],
                }
            ],
        },
    ],
    "LastUpdated": 1780461900000,
}


class P0052Tests(unittest.TestCase):
    def test_parse_svk_flow_payload(self):
        rows = p0052.parse_svk_flow_payload(SAMPLE_PAYLOAD, datetime(2026, 6, 3, tzinfo=timezone.utc))
        measures = {row["measure"] for row in rows}
        self.assertIn("signed_flow_mw", measures)
        self.assertIn("flow_mw", measures)
        self.assertIn("import_mw", measures)
        self.assertIn("export_mw", measures)
        self.assertIn("net_import_mw", measures)

    def test_direction_mapping(self):
        ts = datetime(2026, 6, 3, tzinfo=timezone.utc)
        positive = p0052.directed_border_values(ts, "SE1_SE2", 12.0)[0]
        negative = p0052.directed_border_values(ts, "SE1_SE2", -7.0)[0]
        self.assertEqual((positive["from_area"], positive["to_area"], positive["value"]), ("SE1", "SE2", 12.0))
        self.assertEqual((negative["from_area"], negative["to_area"], negative["value"]), ("SE2", "SE1", 7.0))

    def test_hourly_aggregation(self):
        rows = []
        for minute, value in [(0, 1.0), (15, 3.0), (30, 5.0), (45, 7.0)]:
            rows.append(p0052.source_observation(datetime(2026, 6, 3, 10, minute, tzinfo=timezone.utc), "s", "d", "SE1", "SE2", "SE1_SE2", "flow_mw", value, "MW", "m", "f", "", "ok"))
        hourly = p0052.aggregate_hourly(rows)
        self.assertEqual(len(hourly), 1)
        self.assertEqual(hourly[0]["value"], 4.0)
        self.assertEqual(hourly[0]["source_quarter_hours"], 4)

    def test_import_export_and_residual(self):
        ts = datetime(2026, 6, 3, tzinfo=timezone.utc)
        rows = p0052.aggregate_hourly(p0052.parse_svk_flow_payload(SAMPLE_PAYLOAD, ts))
        physical = {
            "2026-06-03T00:00:00Z": {
                "production_se1": 1000.0,
                "consumption_se1": 900.0,
                "production_se2": 0.0,
                "consumption_se2": 0.0,
                "production_se3": 0.0,
                "consumption_se3": 0.0,
                "production_se4": 0.0,
                "consumption_se4": 0.0,
            }
        }
        wide = p0052.build_wide_hourly(rows, physical)[0]
        self.assertEqual(wide["net_import_se1_mw"], -90.0)
        self.assertEqual(wide["south_import_pressure"], 50.0)
        self.assertEqual(wide["balance_residual_se1"], 10.0)

    def test_capacity_utilization(self):
        self.assertIsNone(p0052.capacity_utilization(10.0, None))
        self.assertIsNone(p0052.capacity_utilization(10.0, 0.0))
        self.assertEqual(p0052.capacity_utilization(10.0, 20.0), 0.5)

    def test_flow_based_flag(self):
        self.assertEqual(p0052.flow_based_market_coupling_flag("2024-10-28T23:00:00Z"), 0)
        self.assertEqual(p0052.flow_based_market_coupling_flag("2024-10-29T00:00:00Z"), 1)

    def test_idempotent_persistence_and_join_validation(self):
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE physical_balance_se1_se4_hourly_v1 (timestamp_utc TEXT PRIMARY KEY, consumption_se1 REAL, production_se1 REAL, consumption_se2 REAL, production_se2 REAL, consumption_se3 REAL, production_se3 REAL, consumption_se4 REAL, production_se4 REAL)")
        conn.execute("INSERT INTO physical_balance_se1_se4_hourly_v1 VALUES ('2026-06-03T00:00:00Z', 1, 2, 1, 2, 1, 2, 1, 2)")
        ts = datetime(2026, 6, 3, tzinfo=timezone.utc)
        raw = p0052.parse_svk_flow_payload(SAMPLE_PAYLOAD, ts)
        hourly = p0052.aggregate_hourly(raw)
        wide = p0052.build_wide_hourly(hourly, p0052.load_physical_rows(conn))
        p0052.persist_transfer_flow(conn, raw, hourly, wide)
        p0052.persist_transfer_flow(conn, raw, hourly, wide)
        count = conn.execute(f"SELECT COUNT(*) FROM {p0052.WIDE_TABLE}").fetchone()[0]
        self.assertEqual(count, 1)
        validation = p0052.validate_transfer_flow(conn, hourly, wide, {"final_ingested_range": {"start": "2026-06-03T00:00:00Z", "end": "2026-06-03T00:00:00Z"}})
        self.assertEqual(validation["duplicates"], 0)
        self.assertEqual(validation["joined_p0051_hours"], 1)

    def test_forbidden_paths_are_not_added(self):
        self.assertIn("CONTINENTAL_PRICE_PRESSURE", p0052.FORBIDDEN_PRODUCTION_PATHS)
        self.assertIn("SHELLY", p0052.FORBIDDEN_PRODUCTION_PATHS)


if __name__ == "__main__":
    unittest.main()
