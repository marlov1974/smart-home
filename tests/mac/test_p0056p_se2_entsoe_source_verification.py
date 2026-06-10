from __future__ import annotations

from datetime import date, datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from src.mac.services.spotprice_model_diagnostics import p0056p


XML_SAMPLE = b"""<?xml version="1.0" encoding="UTF-8"?>
<Publication_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0">
  <TimeSeries>
    <outBiddingZone_Domain.mRID>10Y1001A1001A45N</outBiddingZone_Domain.mRID>
    <quantity_Measure_Unit.name>MAW</quantity_Measure_Unit.name>
    <Period>
      <timeInterval>
        <start>2026-03-27T23:00Z</start>
        <end>2026-03-28T00:00Z</end>
      </timeInterval>
      <resolution>PT15M</resolution>
      <Point><position>1</position><quantity>1000</quantity></Point>
      <Point><position>2</position><quantity>1100</quantity></Point>
      <Point><position>3</position><quantity>1200</quantity></Point>
      <Point><position>4</position><quantity>1300</quantity></Point>
    </Period>
  </TimeSeries>
</Publication_MarketDocument>
"""


class P0056PSourceVerificationTests(unittest.TestCase):
    def test_request_contract_is_actual_total_load_only(self) -> None:
        params, safe = p0056p.build_p0056p_entsoe_request(
            "SE2",
            datetime(2026, 3, 27, 23, tzinfo=timezone.utc),
            datetime(2026, 3, 30, 22, tzinfo=timezone.utc),
        )

        self.assertEqual(params["documentType"], "A65")
        self.assertEqual(params["processType"], "A16")
        self.assertEqual(params["outBiddingZone_Domain"], "10Y1001A1001A45N")
        forbidden = " ".join(params)
        self.assertNotIn("A09", json.dumps(params))
        self.assertNotIn("A11", json.dumps(params))
        self.assertNotIn("A61", json.dumps(params))
        self.assertNotIn("capacity", forbidden.lower())
        self.assertEqual(safe["source_measure"], "actual_total_load")

    def test_parser_preserves_native_resolution_and_local_day(self) -> None:
        _params, safe = p0056p.build_p0056p_entsoe_request(
            "SE2",
            datetime(2026, 3, 27, 23, tzinfo=timezone.utc),
            datetime(2026, 3, 28, 0, tzinfo=timezone.utc),
        )

        rows, meta = p0056p.parse_entsoe_actual_load_xml(XML_SAMPLE, safe)

        self.assertEqual(meta["points"], 4)
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["interval_start_utc"], "2026-03-27T23:00:00Z")
        self.assertEqual(rows[0]["native_resolution_minutes"], 15)
        self.assertEqual(rows[0]["unit"], "MW")
        self.assertEqual(rows[0]["local_date"], "2026-03-28")

    def test_aggregate_native_to_hourly_uses_mean_mw(self) -> None:
        _params, safe = p0056p.build_p0056p_entsoe_request(
            "SE2",
            datetime(2026, 3, 27, 23, tzinfo=timezone.utc),
            datetime(2026, 3, 28, 0, tzinfo=timezone.utc),
        )
        rows, _meta = p0056p.parse_entsoe_actual_load_xml(XML_SAMPLE, safe)

        hourly = p0056p.aggregate_native_to_hourly_for_audit(rows)

        self.assertEqual(len(hourly), 1)
        self.assertEqual(hourly[0]["input_row_count"], 4)
        self.assertEqual(hourly[0]["coverage_flag"], "ok")
        self.assertAlmostEqual(float(hourly[0]["consumption_mw"]), 1150.0)

    def test_classification_detects_local_bug_when_fresh_lacks_spike(self) -> None:
        decision = p0056p.classify_2026_03_28_anomaly(
            "SE2",
            {"row_count": 96, "has_7279_or_equivalent_spike": False},
            {
                "has_7279_or_equivalent_spike": True,
                "by_local_date": {"2026-03-28": {"expected_rows": 96, "observed_rows": 94}},
            },
            {"local_has_7279_or_equivalent_spike": True, "hourly_aggregation_ok": False},
        )

        self.assertEqual(decision["classification"], "verified_local_bug")
        self.assertEqual(decision["model_selection_action"], "fix_local_ingestion_before_modeling")

    def test_classification_detects_source_observed_anomaly(self) -> None:
        decision = p0056p.classify_2026_03_28_anomaly(
            "SE2",
            {"row_count": 96, "has_7279_or_equivalent_spike": True},
            {
                "has_7279_or_equivalent_spike": True,
                "by_local_date": {"2026-03-28": {"expected_rows": 96, "observed_rows": 94}},
            },
            {"local_has_7279_or_equivalent_spike": True, "hourly_aggregation_ok": True},
        )

        self.assertEqual(decision["classification"], "source_observed_anomaly")
        self.assertEqual(decision["model_selection_action"], "exclude_until_independently_verified")

    def test_evidence_writer_does_not_emit_token_fields(self) -> None:
        summary = {
            "status": "PASS",
            "request_contract": {"document_type": "A65", "process_type": "A16"},
            "fresh_fetch": {"status": 200, "row_count": 1},
            "token_safety": {"token_source": "local_secret_file_outside_repo", "secret_safe": True},
            "fresh_native_summary": {"row_count": 1},
            "local_native_summary": {"row_count": 1},
            "hourly_aggregation_summary": {"hourly_aggregation_ok": True},
            "reference_hourly_summary": {"hourly_aggregation_ok": True},
            "decision": {
                "classification": "source_observed_anomaly",
                "fresh_entsoe_has_spike": True,
                "local_native_has_spike": True,
                "hourly_aggregation_ok": True,
                "model_selection_action": "exclude_until_independently_verified",
                "recommended_next_package": "P0056Q",
                "native_rows_observed": 94,
                "native_rows_expected": 96,
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            paths = p0056p.write_p0056p_evidence(Path(tmp), summary, [], [])
            combined = "\n".join(Path(path).read_text(encoding="utf-8") for path in paths.values())

        self.assertNotIn("securityToken", combined)
        self.assertNotIn("ENTSOE_SECURITY_TOKEN", combined)


if __name__ == "__main__":
    unittest.main()
