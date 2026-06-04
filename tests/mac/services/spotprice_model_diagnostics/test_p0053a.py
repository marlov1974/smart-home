import sqlite3
import unittest
from datetime import datetime, timezone

from src.mac.services.spotprice_model_diagnostics import p0052, p0052a, p0053a


class P0053ATests(unittest.TestCase):
    def test_configs_are_a09_a11_only(self):
        docs = {config["document_type"] for config in p0053a.a09_a11_configs()}
        measures = {config["measure"] for config in p0053a.a09_a11_configs()}
        self.assertEqual(docs, {"A09", "A11"})
        self.assertEqual(measures, {"scheduled_exchange_mw", "physical_flow_mw"})

    def test_monthly_chunks_are_hour_inclusive_and_clipped(self):
        chunks = p0053a.monthly_chunks(
            datetime(2024, 1, 15, 3, tzinfo=timezone.utc),
            datetime(2024, 3, 2, 5, tzinfo=timezone.utc),
        )
        self.assertEqual(p0052a.format_utc(chunks[0][0]), "2024-01-15T03:00:00Z")
        self.assertEqual(p0052a.format_utc(chunks[0][1]), "2024-01-31T23:00:00Z")
        self.assertEqual(p0052a.format_utc(chunks[-1][1]), "2024-03-02T05:00:00Z")

    def test_derived_net_and_pressure_features(self):
        features = p0053a.derive_flow_exchange_features({
            "scheduled_exchange_se2_to_se3_mw": 900,
            "scheduled_exchange_se3_to_se2_mw": 100,
            "scheduled_exchange_se3_to_se4_mw": 300,
            "scheduled_exchange_se4_to_se3_mw": 450,
            "physical_flow_se2_to_se3_mw": 700,
            "physical_flow_se3_to_se2_mw": 50,
            "physical_flow_se3_to_se4_mw": 200,
            "physical_flow_se4_to_se3_mw": 25,
        })
        self.assertEqual(features["net_scheduled_exchange_se2_se3_mw"], 800)
        self.assertEqual(features["net_scheduled_exchange_se3_se4_mw"], -150)
        self.assertEqual(features["southward_exchange_pressure"], 800)
        self.assertEqual(features["net_physical_flow_se2_se3_mw"], 650)
        self.assertEqual(features["net_physical_flow_se3_se4_mw"], 175)
        self.assertEqual(features["southward_physical_flow_pressure"], 825)

    def test_plan_missing_fetch_tasks_excludes_a61(self):
        conn = sqlite3.connect(":memory:")
        p0052.create_long_table(conn, p0052.CANONICAL_TABLE, include_source_quarters=True)
        p0052.create_wide_table(conn, p0052.WIDE_TABLE)
        p0052.create_long_table(conn, p0052.RAW_TABLE, include_source_quarters=False)
        p0053a.ensure_p0053a_schema(conn)
        tasks, plan = p0053a.plan_missing_fetch_tasks(
            conn,
            datetime(2024, 1, 1, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(plan["documents"], ["A09", "A11"])
        self.assertFalse(plan["a61_requested"])
        self.assertTrue(tasks)
        self.assertEqual({task["safe"]["document_type"] for task in tasks}, {"A09", "A11"})

    def test_joined_analysis_uses_normalized_timestamp_text(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        p0052.create_long_table(conn, p0052.RAW_TABLE, include_source_quarters=False)
        p0052.create_long_table(conn, p0052.CANONICAL_TABLE, include_source_quarters=True)
        p0052.create_wide_table(conn, p0052.WIDE_TABLE)
        p0053a.ensure_p0053a_schema(conn)
        conn.execute(
            f"""
            INSERT INTO {p0052.WIDE_TABLE}
            (timestamp_utc, model_cet_timestamp, model_cet_date, model_cet_hour, flow_based_market_coupling_flag, flow_based_go_live_date, capacity_method_label, net_scheduled_exchange_se2_se3_mw)
            VALUES ('2024-01-01T00:00:00Z', '2024-01-01T01:00:00Z', '2024-01-01', 1, 0, '2024-10-29', 'not_capacity', 123.0)
            """
        )
        conn.execute(
            f"""
            CREATE TABLE {p0052.PHYSICAL_TABLE} (
                timestamp_utc TEXT PRIMARY KEY,
                model_cet_timestamp TEXT,
                model_cet_date TEXT,
                model_cet_hour INTEGER,
                consumption_se1 REAL, consumption_se2 REAL, consumption_se3 REAL, consumption_se4 REAL,
                production_se1 REAL, production_se2 REAL, production_se3 REAL, production_se4 REAL,
                net_load_se1 REAL, net_load_se2 REAL, net_load_se3 REAL, net_load_se4 REAL
            )
            """
        )
        conn.execute(
            f"INSERT INTO {p0052.PHYSICAL_TABLE} VALUES ('2024-01-01T00:00:00+00:00', '2024-01-01T01:00:00Z', '2024-01-01', 1, 1, 2, 3, 4, 5, 6, 7, 8, -4, -4, -4, -4)"
        )
        conn.execute(
            f"""
            CREATE TABLE {p0053a.PRICE_TABLE} (
                timestamp_utc TEXT PRIMARY KEY,
                se1_price REAL,
                se3_price REAL,
                se3_minus_se1 REAL
            )
            """
        )
        conn.execute(f"INSERT INTO {p0053a.PRICE_TABLE} VALUES ('2024-01-01T00:00:00+00:00', 10, 12, 2)")
        result = p0053a.create_joined_analysis_dataset(
            conn,
            datetime(2024, 1, 1, tzinfo=timezone.utc),
            datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(result["analysis_rows"], 1)
        row = conn.execute(f"SELECT se3_price, net_scheduled_exchange_se2_se3_mw FROM {p0053a.ANALYSIS_TABLE}").fetchone()
        self.assertEqual(row["se3_price"], 12)
        self.assertEqual(row["net_scheduled_exchange_se2_se3_mw"], 123)

    def test_p0053a_does_not_define_utilization_or_margin_columns(self):
        names = set(p0053a.DERIVED_WIDE_COLUMNS)
        self.assertFalse(any("utilization" in name or "margin" in name for name in names))


if __name__ == "__main__":
    unittest.main()
