import sqlite3
import unittest
from datetime import datetime, timezone

from src.mac.services.spotprice_model_diagnostics import p0052, p0052a, p0052b


class P0052BTests(unittest.TestCase):
    def test_capacity_concept_mapping_is_conservative(self):
        review = p0052b.capacity_concept_review()
        self.assertEqual(review["contract_types"]["A02"]["meaning"], "Weekly")
        self.assertEqual(review["contract_types"]["A03"]["meaning"], "Monthly")
        self.assertEqual(review["contract_types"]["A04"]["meaning"], "Yearly")
        self.assertFalse(review["utilization_allowed"])

    def test_chunk_windows(self):
        chunks = p0052b.chunk_windows(
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 10, 23, tzinfo=timezone.utc),
            max_days=5,
        )
        self.assertEqual(len(chunks), 2)
        self.assertEqual(p0052a.format_utc(chunks[0][1]), "2025-01-05T23:00:00Z")

    def test_metadata_for_config(self):
        meta = p0052b.metadata_for_config(p0052a.DOCUMENT_CONFIGS[2], {})
        self.assertEqual(meta["document_type"], "A61")
        self.assertEqual(meta["contract_type"], "A02")
        self.assertEqual(meta["business_type"], "A61")
        self.assertEqual(meta["capacity_concept_status"], p0052b.CAPACITY_CONCEPT_STATUS)

    def test_schema_migration_adds_metadata_columns(self):
        with sqlite3.connect(":memory:") as conn:
            p0052.create_long_table(conn, p0052.RAW_TABLE, include_source_quarters=False)
            p0052.create_long_table(conn, p0052.CANONICAL_TABLE, include_source_quarters=True)
            p0052.create_wide_table(conn, p0052.WIDE_TABLE)
            p0052b.ensure_p0052b_schema(conn)
            self.assertIn("document_type", p0052.table_columns(conn, p0052.CANONICAL_TABLE))
            self.assertIn("north_to_south_utilization_max", p0052.table_columns(conn, p0052.WIDE_TABLE))

    def test_capacity_utilization_blocked_when_concept_uncertain(self):
        self.assertIsNone(p0052b.capacity_utilization_safe(10, 20, p0052b.capacity_concept_review()))

    def test_normalized_join_handles_z_and_offset(self):
        with sqlite3.connect(":memory:") as conn:
            p0052.create_wide_table(conn, p0052.WIDE_TABLE)
            conn.execute("CREATE TABLE se3_se1_demand_response_analysis_v1(timestamp_utc TEXT, se3_price REAL, se3_minus_se1 REAL)")
            conn.execute(
                f"INSERT INTO {p0052.WIDE_TABLE}(timestamp_utc, model_cet_timestamp, model_cet_date, model_cet_hour, flow_based_market_coupling_flag, flow_based_go_live_date, capacity_method_label) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("2026-05-01T00:00:00Z", "2026-05-01T01:00:00Z", "2026-05-01", 1, 1, "2024-10-29T00:00:00Z", "x"),
            )
            conn.execute("INSERT INTO se3_se1_demand_response_analysis_v1 VALUES (?, ?, ?)", ("2026-05-01T00:00:00+00:00", 50.0, 2.0))
            analysis = p0052b.run_join_fix_analysis(conn)
            self.assertEqual(analysis["exact_join_rows"], 0)
            self.assertEqual(analysis["normalized_join_rows"], 1)

    def test_wide_update_inserts_missing_timestamp(self):
        row = p0052a.source_observation(datetime(2025, 1, 1, tzinfo=timezone.utc), "A09", "SE2", "SE3", "SE2_SE3", "scheduled_exchange_mw", 100.0, "MAW", "not_capacity", "scheduled_exchange", "ok")
        row.update(p0052b.metadata_for_config(p0052a.DOCUMENT_CONFIGS[0], {}))
        hourly = p0052b.aggregate_hourly_p0052b([row])
        with sqlite3.connect(":memory:") as conn:
            p0052.create_long_table(conn, p0052.RAW_TABLE, include_source_quarters=False)
            p0052.create_long_table(conn, p0052.CANONICAL_TABLE, include_source_quarters=True)
            p0052.create_wide_table(conn, p0052.WIDE_TABLE)
            p0052b.ensure_p0052b_schema(conn)
            summary = p0052b.update_wide_entsoe_features_p0052b(conn, hourly, p0052b.capacity_concept_review())
            self.assertEqual(summary["wide_rows_inserted"], 1)
            stored = conn.execute(f"SELECT scheduled_exchange_se2_to_se3_mw, flow_or_exchange_se2_to_se3_mw FROM {p0052.WIDE_TABLE}").fetchone()
            self.assertEqual(stored[0], 100.0)
            self.assertEqual(stored[1], 100.0)

    def test_clipped_capacity_expansion_limits_long_period(self):
        rows = p0052b.expand_entsoe_value_clipped(
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            p0052a.resolution_to_timedelta(
                "P1M",
                period_start=datetime(2025, 1, 1, tzinfo=timezone.utc),
                period_end=datetime(2025, 2, 1, tzinfo=timezone.utc),
            ),
            1000.0,
            {
                "measure": "capacity_mw",
                "source_dataset": "A61",
                "capacity_method_label": "forecasted_transfer_capacity_explicit_A03",
                "flow_type_label": "not_flow",
            },
            {"from_area": "SE2", "to_area": "SE3", "border_id": "SE2_SE3", "unit": "MAW"},
            datetime(2025, 1, 3, tzinfo=timezone.utc),
            datetime(2025, 1, 4, 23, tzinfo=timezone.utc),
        )
        self.assertEqual(len(rows), 48)
        self.assertEqual(rows[0]["timestamp_utc"], "2025-01-03T00:00:00Z")
        self.assertEqual(rows[-1]["timestamp_utc"], "2025-01-04T23:00:00Z")

    def test_forbidden_price_document_still_rejected(self):
        with self.assertRaises(RuntimeError):
            p0052a.build_entsoe_params(
                {"document_type": "A44", "measure": "price", "source_dataset": "price", "capacity_method_label": "not_capacity", "flow_type_label": "not_flow"},
                "SE1",
                "SE2",
                datetime(2025, 1, 1, tzinfo=timezone.utc),
                datetime(2025, 1, 2, tzinfo=timezone.utc),
            )


if __name__ == "__main__":
    unittest.main()
