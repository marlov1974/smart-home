from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.server import PlanRequest, plan_payload
from src.mac.labs.weekly_home_optimizer_poc.tables import format_json
from src.mac.labs.weekly_home_optimizer_poc.planner import build_weekly_plan


class SpotSummaryFieldsTests(unittest.TestCase):
    def test_server_summary_exposes_spot_metadata(self) -> None:
        payload = plan_payload(PlanRequest(week=2, ppm=500.0, house_temp=22.0), prefer_real_weather=False)
        summary = payload["summary"]
        first_hour = payload["hours"][0]

        self.assertEqual(summary["spot_model"], "hourly_forecast_with_actual_horizon_patch_v1")
        self.assertEqual(summary["spot_resolution"], "hourly")
        self.assertEqual(summary["spot_patch_strategy"], "actual_shape_forecast_sum_horizon")
        self.assertEqual(summary["spot_actual_fixture_path"], "data/spot/spot_2025_hourly_europe_stockholm.csv")
        self.assertEqual(summary["spot_actual_horizon_hours"], 20)
        self.assertEqual(summary["spot_actual_known_hours"], 20)
        self.assertEqual(summary["spot_actual_patched_hours"], 20)
        self.assertEqual(summary["spot_forecast_hours"], 148)
        self.assertIn("spot_source", first_hour)
        self.assertIn("spot_planning_index", first_hour)
        self.assertIn("spot_planning_source", first_hour)
        self.assertIn("spot_forecast_index", first_hour)
        self.assertIn("spot_actual_price", first_hour)
        self.assertIn("spot_actual_proto_index", first_hour)
        self.assertIn("spot_patched_actual_index", first_hour)
        self.assertIn("spot_actual_outcome_index", first_hour)
        self.assertIn("spot_actual_available", first_hour)
        self.assertIn("spot_forecast_error_index", first_hour)
        self.assertIn("spot_forecast_error_pct", first_hour)

    def test_cli_metadata_exposes_spot_metadata(self) -> None:
        plan = build_weekly_plan(2, 500.0, 22.0, prefer_real_weather=False)
        payload = format_json(plan)

        self.assertIn('"spot_model":"hourly_forecast_with_actual_horizon_patch_v1"', payload)
        self.assertIn('"spot_actual_horizon_hours":20', payload)
        self.assertIn('"spot_source":"actual_horizon_patched"', payload)


if __name__ == "__main__":
    unittest.main()
