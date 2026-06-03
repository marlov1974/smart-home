import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.mac.services.spotprice_model_diagnostics import p0052, p0052a


SUCCESS_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<Publication_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3">
  <TimeSeries>
    <out_Domain.mRID codingScheme="A01">10Y1001A1001A44P</out_Domain.mRID>
    <in_Domain.mRID codingScheme="A01">10Y1001A1001A45N</in_Domain.mRID>
    <quantity_Measure_Unit.name>MAW</quantity_Measure_Unit.name>
    <Period>
      <timeInterval>
        <start>2026-05-01T00:00Z</start>
        <end>2026-05-01T02:00Z</end>
      </timeInterval>
      <resolution>PT60M</resolution>
      <Point><position>1</position><quantity>100</quantity></Point>
      <Point><position>2</position><quantity>120</quantity></Point>
    </Period>
  </TimeSeries>
</Publication_MarketDocument>
"""


ACK_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<Acknowledgement_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-1:acknowledgementdocument:8:1">
  <Reason><text>No matching data found</text></Reason>
</Acknowledgement_MarketDocument>
"""


class P0052ATests(unittest.TestCase):
    def test_mask_token(self):
        self.assertEqual(p0052a.mask_token("abc secret xyz", "secret"), "abc <ENTSOE_TOKEN> xyz")

    def test_domain_mapping_covers_se_zones(self):
        for zone in ("SE1", "SE2", "SE3", "SE4"):
            self.assertIn(zone, p0052a.DOMAINS)

    def test_request_builder_excludes_token(self):
        params, safe = p0052a.build_entsoe_params(p0052a.DOCUMENT_CONFIGS[0], "SE1", "SE2", datetime(2026, 5, 1, tzinfo=timezone.utc), datetime(2026, 5, 2, tzinfo=timezone.utc))
        self.assertNotIn("securityToken", params)
        self.assertNotIn("securityToken", safe)
        self.assertEqual(params["out_Domain"], p0052a.DOMAINS["SE1"])
        self.assertEqual(params["in_Domain"], p0052a.DOMAINS["SE2"])

    def test_forbidden_price_document_type_rejected(self):
        with self.assertRaises(RuntimeError):
            p0052a.build_entsoe_params(
                {"document_type": "A44", "measure": "price", "source_dataset": "price", "capacity_method_label": "not_capacity", "flow_type_label": "not_flow"},
                "SE1",
                "SE2",
                datetime(2026, 5, 1, tzinfo=timezone.utc),
                datetime(2026, 5, 2, tzinfo=timezone.utc),
            )

    def test_parse_success_document(self):
        meta = {
            "from_area": "SE1",
            "to_area": "SE2",
            "measure": "scheduled_exchange_mw",
            "source_dataset": "A09 scheduled commercial exchange",
            "capacity_method_label": "not_capacity",
            "flow_type_label": "scheduled_exchange",
        }
        rows, response = p0052a.parse_entsoe_document(SUCCESS_XML, meta)
        self.assertEqual(response["points"], 2)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["timestamp_utc"], "2026-05-01T00:00:00Z")
        self.assertEqual(rows[0]["from_area"], "SE1")
        self.assertEqual(rows[0]["to_area"], "SE2")

    def test_parse_acknowledgement(self):
        rows, response = p0052a.parse_entsoe_document(ACK_XML, {"from_area": "SE1", "to_area": "SE2"})
        self.assertEqual(rows, [])
        self.assertEqual(response["root"], "Acknowledgement_MarketDocument")

    def test_daily_capacity_expands_hourly(self):
        rows = p0052a.expand_entsoe_value(
            datetime(2026, 5, 1, tzinfo=timezone.utc),
            p0052a.resolution_to_timedelta("P1D"),
            1000.0,
            {
                "measure": "capacity_mw",
                "source_dataset": "A61",
                "capacity_method_label": "forecasted_transfer_capacity_explicit_A02",
                "flow_type_label": "not_flow",
            },
            {"from_area": "SE1", "to_area": "SE2", "border_id": "SE1_SE2", "unit": "MAW"},
        )
        self.assertEqual(len(rows), 24)
        self.assertEqual(rows[-1]["timestamp_utc"], "2026-05-01T23:00:00Z")

    def test_monthly_capacity_resolution_uses_period_bounds(self):
        step = p0052a.resolution_to_timedelta(
            "P1M",
            period_start=datetime(2026, 5, 1, tzinfo=timezone.utc),
            period_end=datetime(2026, 6, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(step.days, 31)

    def test_aggregate_hourly(self):
        row1 = p0052a.source_observation(datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc), "A09", "SE1", "SE2", "SE1_SE2", "scheduled_exchange_mw", 10.0, "MAW", "not_capacity", "scheduled_exchange", "ok")
        row2 = p0052a.source_observation(datetime(2026, 5, 1, 0, 30, tzinfo=timezone.utc), "A09", "SE1", "SE2", "SE1_SE2", "scheduled_exchange_mw", 20.0, "MAW", "not_capacity", "scheduled_exchange", "ok")
        hourly = p0052a.aggregate_hourly([row1, row2])
        self.assertEqual(len(hourly), 1)
        self.assertEqual(hourly[0]["value"], 15.0)

    def test_source_observation_fixed_cet_fields(self):
        row = p0052a.source_observation(datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc), "A09", "SE1", "SE2", "SE1_SE2", "scheduled_exchange_mw", 10.0, "MAW", "not_capacity", "scheduled_exchange", "ok")
        self.assertEqual(row["model_cet_timestamp"], "2026-05-01T01:00:00Z")
        self.assertEqual(row["model_cet_date"], "2026-05-01")
        self.assertEqual(row["model_cet_hour"], 1)

    def test_persist_entsoe_rows_is_idempotent(self):
        raw = [
            p0052a.source_observation(datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc), "A09", "SE1", "SE2", "SE1_SE2", "scheduled_exchange_mw", 10.0, "MAW", "not_capacity", "scheduled_exchange", "ok")
        ]
        hourly = p0052a.aggregate_hourly(raw)
        with sqlite3.connect(":memory:") as conn:
            p0052.create_long_table(conn, p0052.RAW_TABLE, include_source_quarters=False)
            p0052.create_long_table(conn, p0052.CANONICAL_TABLE, include_source_quarters=True)
            p0052.create_wide_table(conn, p0052.WIDE_TABLE)
            p0052a.persist_entsoe_rows(conn, raw, hourly)
            p0052a.persist_entsoe_rows(conn, raw, hourly)
            self.assertEqual(conn.execute(f"SELECT COUNT(*) FROM {p0052.RAW_TABLE}").fetchone()[0], 1)
            self.assertEqual(conn.execute(f"SELECT COUNT(*) FROM {p0052.CANONICAL_TABLE}").fetchone()[0], 1)

    def test_capacity_utilization(self):
        self.assertIsNone(p0052a.capacity_utilization(10, None))
        self.assertIsNone(p0052a.capacity_utilization(10, 0))
        self.assertEqual(p0052a.capacity_utilization(10, 20), 0.5)

    def test_token_loader_environment(self):
        old = os.environ.get("ENTSOE_SECURITY_TOKEN")
        try:
            os.environ["ENTSOE_SECURITY_TOKEN"] = "test-token"
            token = p0052a.load_entsoe_token()
            self.assertEqual(token.token, "test-token")
            self.assertEqual(token.source_label, "environment")
        finally:
            if old is None:
                os.environ.pop("ENTSOE_SECURITY_TOKEN", None)
            else:
                os.environ["ENTSOE_SECURITY_TOKEN"] = old

    def test_secret_safety_outside_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "token"
            path.write_text("x", encoding="utf-8")
            os.chmod(tmp, 0o700)
            os.chmod(path, 0o600)
            safety = p0052a.verify_secret_safety(p0052a.TokenSource("x", "local_secret_file_outside_repo", path))
            self.assertTrue(safety["secret_safe"])


if __name__ == "__main__":
    unittest.main()
