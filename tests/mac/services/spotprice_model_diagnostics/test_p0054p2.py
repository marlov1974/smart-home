import sqlite3
import unittest
from datetime import datetime, timezone

from src.mac.services.spotprice_model_diagnostics import p0054p2


ACTUAL_LOAD_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0">
  <TimeSeries>
    <outBiddingZone_Domain.mRID codingScheme="A01">10Y1001A1001A46L</outBiddingZone_Domain.mRID>
    <quantity_Measure_Unit.name>MAW</quantity_Measure_Unit.name>
    <Period>
      <timeInterval>
        <start>2025-06-01T00:00Z</start>
        <end>2025-06-01T01:00Z</end>
      </timeInterval>
      <resolution>PT15M</resolution>
      <Point><position>1</position><quantity>100</quantity></Point>
      <Point><position>2</position><quantity>120</quantity></Point>
      <Point><position>3</position><quantity>140</quantity></Point>
      <Point><position>4</position><quantity>160</quantity></Point>
    </Period>
  </TimeSeries>
</GL_MarketDocument>
"""


class P0054P2Tests(unittest.TestCase):
    def test_build_actual_load_params_use_a65_a16_bidding_zone_not_flow(self):
        params, safe = p0054p2.build_actual_load_params(
            "SE3",
            datetime(2025, 6, 1, tzinfo=timezone.utc),
            datetime(2025, 7, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(params["documentType"], "A65")
        self.assertEqual(params["processType"], "A16")
        self.assertEqual(params["outBiddingZone_Domain"], "10Y1001A1001A46L")
        self.assertNotIn("out_Domain", params)
        self.assertNotIn("in_Domain", params)
        self.assertNotIn("securityToken", params)
        self.assertEqual(safe["source_type"], "actual_total_load")
        self.assertEqual(safe["usable_for_consumption_target"], "true")

    def test_parse_actual_load_document_and_hourly_mean(self):
        rows, response = p0054p2.parse_actual_load_document(
            ACTUAL_LOAD_XML,
            {
                "area": "SE3",
                "source_area_code": "10Y1001A1001A46L",
                "source_type": "actual_total_load",
                "area_scope": "bidding_zone_internal_consumption_or_load",
            },
        )
        self.assertEqual(response["points"], 4)
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["timestamp_utc"], "2025-06-01T00:00:00Z")
        self.assertEqual(rows[0]["unit"], "MW")
        hourly = p0054p2.aggregate_hourly_load(rows)
        self.assertEqual(len(hourly), 1)
        self.assertEqual(hourly[0]["consumption_mw"], 130.0)
        self.assertEqual(hourly[0]["source_measure"], "actual_total_load")

    def test_persist_actual_load_rows_idempotent(self):
        rows, _ = p0054p2.parse_actual_load_document(
            ACTUAL_LOAD_XML,
            {
                "area": "SE3",
                "source_area_code": "10Y1001A1001A46L",
                "source_type": "actual_total_load",
                "area_scope": "bidding_zone_internal_consumption_or_load",
            },
        )
        hourly = p0054p2.aggregate_hourly_load(rows)
        with sqlite3.connect(":memory:") as conn:
            p0054p2.persist_actual_load_rows(conn, hourly)
            p0054p2.persist_actual_load_rows(conn, hourly)
            self.assertEqual(conn.execute(f"SELECT COUNT(*) FROM {p0054p2.TARGET_TABLE}").fetchone()[0], 1)
            row = conn.execute(f"SELECT area, source_measure, consumption_mw FROM {p0054p2.TARGET_TABLE}").fetchone()
            self.assertEqual(row[0], "SE3")
            self.assertEqual(row[1], "actual_total_load")
            self.assertEqual(row[2], 130.0)

    def test_cross_border_flow_file_classification_is_not_target(self):
        classification = p0054p2.classify_cross_border_flow_file()
        self.assertEqual(classification["classification"], "net_cross_border_physical_flows")
        self.assertFalse(classification["usable_for_consumption_target"])


if __name__ == "__main__":
    unittest.main()
