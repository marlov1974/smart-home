from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.spot import build_spot_plan, forecast_spot_index_for_week


class HourlySpotForecastTests(unittest.TestCase):
    def test_forecast_baseline_is_hourly(self) -> None:
        forecast = forecast_spot_index_for_week(2)

        self.assertEqual(len(forecast), 168)
        self.assertTrue(all(isinstance(value, float) for value in forecast))

    def test_spot_plan_is_hourly_with_provenance(self) -> None:
        plan = build_spot_plan(2)

        self.assertEqual(len(plan.spot_index), 168)
        self.assertEqual(len(plan.spot_source), 168)
        self.assertEqual(len(plan.spot_forecast_index), 168)
        self.assertEqual(len(plan.spot_actual_price), 168)
        self.assertEqual(len(plan.spot_actual_proto_index), 168)
        self.assertEqual(len(plan.spot_patched_actual_index), 168)
        self.assertEqual(plan.spot_model, "hourly_forecast_with_actual_patch_v1")
        self.assertEqual(plan.spot_resolution, "hourly")
        self.assertGreater(plan.spot_actual_patched_hours, 0)
        self.assertIn("actual_patched", plan.spot_source)


if __name__ == "__main__":
    unittest.main()
