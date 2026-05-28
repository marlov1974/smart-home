from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.server import PlanRequest, parse_plan_query, plan_payload


class BrowserContractTests(unittest.TestCase):
    def test_parse_plan_query_accepts_public_inputs(self) -> None:
        request = parse_plan_query({"week": ["2"], "ppm": ["500"], "houseTemp": ["22"], "people": ["6"]})

        self.assertEqual(request.week, 2)
        self.assertEqual(request.ppm, 500)
        self.assertEqual(request.house_temp, 22)
        self.assertEqual(request.people, 6)

    def test_parse_plan_query_defaults_people(self) -> None:
        request = parse_plan_query({"week": ["2"], "ppm": ["500"], "houseTemp": ["22"]})

        self.assertEqual(request.people, 3)

    def test_plan_payload_contract(self) -> None:
        payload = plan_payload(PlanRequest(week=2, ppm=500.0, house_temp=22.0, people=6.0), prefer_real_weather=False)

        self.assertEqual(sorted(payload.keys()), ["hours", "input", "summary"])
        self.assertEqual(payload["summary"]["hours"], 168)
        self.assertEqual(payload["input"]["people"], 6)
        self.assertEqual(payload["summary"]["people"], 6)
        self.assertEqual(payload["summary"]["occupancy_gain_ppm_h"], 140)
        self.assertEqual(payload["summary"]["weather_source"], "synthetic_fallback")
        self.assertEqual(len(payload["hours"]), 168)
        self.assertIn("supply_pct", payload["hours"][0])
        self.assertIn("ppm_absolute", payload["hours"][0])

    def test_invalid_inputs_are_rejected(self) -> None:
        cases = [
            {"ppm": ["500"], "houseTemp": ["22"]},
            {"week": ["54"], "ppm": ["500"], "houseTemp": ["22"]},
            {"week": ["2"], "ppm": ["bad"], "houseTemp": ["22"]},
            {"week": ["2"], "ppm": ["500"], "houseTemp": ["bad"]},
            {"week": ["2"], "ppm": ["500"], "houseTemp": ["22"], "people": ["21"]},
        ]
        for query in cases:
            with self.subTest(query=query):
                with self.assertRaises(ValueError):
                    parse_plan_query(query)


if __name__ == "__main__":
    unittest.main()
