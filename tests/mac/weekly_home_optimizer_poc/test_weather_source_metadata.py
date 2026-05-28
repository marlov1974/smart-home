from __future__ import annotations

import json
import unittest

from src.mac.labs.weekly_home_optimizer_poc.planner import build_weekly_plan
from src.mac.labs.weekly_home_optimizer_poc.tables import format_json


class WeatherSourceMetadataTests(unittest.TestCase):
    def test_plan_carries_weather_metadata(self) -> None:
        plan = build_weekly_plan(2, 500, 22, people=3, prefer_real_weather=False)

        self.assertEqual(plan.weather_source, "synthetic_fallback")
        self.assertEqual(plan.weather_provider, "internal synthetic profile")
        self.assertEqual(plan.people, 3)
        self.assertEqual(plan.occupancy_gain_ppm_h, 70)

    def test_json_metadata_contains_weather_and_people(self) -> None:
        plan = build_weekly_plan(2, 500, 22, people=6, prefer_real_weather=False)
        payload = json.loads(format_json(plan))

        self.assertEqual(payload["metadata"]["people"], 6)
        self.assertEqual(payload["metadata"]["occupancy_gain_ppm_h"], 140)
        self.assertEqual(payload["metadata"]["weather_source"], "synthetic_fallback")


if __name__ == "__main__":
    unittest.main()
