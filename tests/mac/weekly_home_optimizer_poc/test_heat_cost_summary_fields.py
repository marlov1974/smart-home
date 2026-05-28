from __future__ import annotations

import json
import unittest

from src.mac.labs.weekly_home_optimizer_poc.planner import build_weekly_plan
from src.mac.labs.weekly_home_optimizer_poc.server import PlanRequest, plan_payload
from src.mac.labs.weekly_home_optimizer_poc.tables import format_json, rows_for_plan


class HeatCostSummaryFieldsTests(unittest.TestCase):
    def test_full_poc_output_includes_comparison_fields(self) -> None:
        plan = build_weekly_plan(2, 500, 22, prefer_real_weather=False)
        metadata = json.loads(format_json(plan))["metadata"]
        row = rows_for_plan(plan)[0]
        payload = plan_payload(PlanRequest(week=2, ppm=500.0, house_temp=22.0), prefer_real_weather=False)

        for field in (
            "heat_cost_model",
            "cop_model",
            "optimized_heat_el_kWh",
            "flat_heat_el_kWh",
            "optimized_heat_el_cost",
            "flat_heat_el_cost",
            "optimized_vs_flat_cost_pct",
            "optimized_saving_pct",
            "avg_cop_optimized",
            "avg_cop_flat",
        ):
            self.assertIn(field, metadata)
            self.assertIn(field, payload["summary"])
        for field in (
            "cop_optimized",
            "heat_el_kWh",
            "heat_el_cost",
            "flat_heat_kWh",
            "cop_flat",
            "flat_heat_el_kWh",
            "flat_heat_el_cost",
        ):
            self.assertIn(field, row)

        self.assertEqual(metadata["heat_cost_model"], "cop_emulated_v1")
        self.assertGreater(metadata["flat_heat_el_cost"], 0.0)


if __name__ == "__main__":
    unittest.main()
