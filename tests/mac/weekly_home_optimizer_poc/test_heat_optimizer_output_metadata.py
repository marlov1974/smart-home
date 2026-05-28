from __future__ import annotations

import json
import unittest

from src.mac.labs.weekly_home_optimizer_poc.planner import build_weekly_plan
from src.mac.labs.weekly_home_optimizer_poc.server import PlanRequest, plan_payload
from src.mac.labs.weekly_home_optimizer_poc.tables import format_json, rows_for_plan


class HeatOptimizerOutputMetadataTests(unittest.TestCase):
    def test_rows_metadata_and_api_summary_include_dp_fields(self) -> None:
        plan = build_weekly_plan(2, 500, 22, prefer_real_weather=False)
        row = rows_for_plan(plan)[0]
        metadata = json.loads(format_json(plan))["metadata"]
        payload = plan_payload(PlanRequest(week=2, ppm=500.0, house_temp=22.0), prefer_real_weather=False)

        self.assertEqual(metadata["heat_optimizer"], "discrete_dp")
        self.assertEqual(payload["summary"]["heat_optimizer"], "discrete_dp")
        self.assertIn("heat_price_index", row)
        self.assertIn("heat_action_kw", row)
        self.assertIn("heat_dp_cost_component", row)
        self.assertIn("soc_penalty_component", row)


if __name__ == "__main__":
    unittest.main()
