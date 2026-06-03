from __future__ import annotations

import sqlite3
import unittest

from src.mac.services.spotprice_model_diagnostics import p0051


class P0051Tests(unittest.TestCase):
    def test_parse_consumption_normalizes_sign_to_positive(self):
        payload = [{"timestampUTC": "2024-01-01T00:00:00Z", "mba": "SE1", "metered": -3.0, "profiled": -2.0, "flex": None, "total": -5.0}]
        rows = p0051.parse_esett_consumption(payload, "SE1")
        total = [row for row in rows if row["measure"] == "consumption_total"][0]
        self.assertEqual(5.0, total["value"])
        self.assertEqual("MW", total["unit"])

    def test_parse_production_keeps_total_and_type(self):
        payload = [{"timestampUTC": "2024-01-01T00:00:00Z", "mba": "SE1", "hydro": 10.0, "wind": 2.0, "total": 12.0}]
        rows = p0051.parse_esett_production(payload, "SE1")
        measures = {row["measure"] for row in rows}
        self.assertIn("production_total", measures)
        self.assertIn("production_hydro", measures)
        self.assertIn("production_wind", measures)

    def test_fixed_cet_fields_are_utc_plus_one(self):
        fields = p0051.fixed_cet_fields("2024-03-31T00:00:00Z")
        self.assertEqual("2024-03-31", fields["model_cet_date"])
        self.assertEqual(1, fields["model_cet_hour"])

    def test_hourly_aggregation_uses_mean_of_quarters(self):
        observations = [
            p0051.source_observation(f"2024-01-01T00:{minute:02d}:00Z", "SE1", "consumption_total", None, value, "MW", "test")
            for minute, value in ((0, 1.0), (15, 3.0), (30, 5.0), (45, 7.0))
        ]
        rows = p0051.aggregate_hourly(observations)
        self.assertEqual(1, len(rows))
        self.assertEqual(4.0, rows[0]["value"])
        self.assertEqual("ok", rows[0]["quality_flag"])

    def test_wide_rows_compute_net_load_and_aggregates(self):
        hourly = []
        for zone in ("SE1", "SE2", "SE3", "SE4"):
            hourly.append({"timestamp_utc": "2024-01-01T00:00:00Z", **p0051.fixed_cet_fields("2024-01-01T00:00:00Z"), "bidding_zone": zone, "measure": "consumption_total", "value": 10.0})
            hourly.append({"timestamp_utc": "2024-01-01T00:00:00Z", **p0051.fixed_cet_fields("2024-01-01T00:00:00Z"), "bidding_zone": zone, "measure": "production_total", "value": 7.0})
        wide = p0051.build_wide_hourly(hourly)
        self.assertEqual(3.0, wide[0]["net_load_se1"])
        self.assertEqual(6.0, wide[0]["net_load_north"])
        self.assertEqual(0.0, wide[0]["net_load_south_minus_north"])

    def test_persist_is_idempotent_by_rebuild(self):
        hourly = [{"timestamp_utc": "2024-01-01T00:00:00Z", **p0051.fixed_cet_fields("2024-01-01T00:00:00Z"), "source_name": "test", "source_dataset": "test", "bidding_zone": "SE1", "measure": "consumption_total", "production_type": "", "value": 1.0, "unit": "MW", "ingested_at_utc": "2024-01-01T00:00:00Z", "source_updated_at_utc": "", "quality_flag": "ok"}]
        wide = [{"timestamp_utc": "2024-01-01T00:00:00Z", **p0051.fixed_cet_fields("2024-01-01T00:00:00Z"), "consumption_se1": 1.0, "production_se1": 0.0, "net_load_se1": 1.0}]
        conn = sqlite3.connect(":memory:")
        p0051.persist_physical_balance(conn, hourly, wide)
        p0051.persist_physical_balance(conn, hourly, wide)
        self.assertEqual(1, conn.execute(f"SELECT COUNT(*) FROM {p0051.CANONICAL_TABLE}").fetchone()[0])

    def test_forbidden_paths_include_continental_api_and_device(self):
        self.assertIn("CONTINENTAL_PRICE_PRESSURE", p0051.FORBIDDEN_PRODUCTION_PATHS)
        self.assertIn("SE3_API", p0051.FORBIDDEN_PRODUCTION_PATHS)
        self.assertIn("DEVICE", p0051.FORBIDDEN_PRODUCTION_PATHS)


if __name__ == "__main__":
    unittest.main()
