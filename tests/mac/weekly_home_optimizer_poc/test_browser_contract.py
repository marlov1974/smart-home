from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.server import PlanRequest, parse_plan_query, plan_payload


class BrowserContractTests(unittest.TestCase):
    def test_parse_plan_query_accepts_public_inputs(self) -> None:
        request = parse_plan_query({"week": ["2"], "ppm": ["500"], "houseTemp": ["22"]})

        self.assertEqual(request.week, 2)
        self.assertEqual(request.ppm, 500)
        self.assertEqual(request.house_temp, 22)

    def test_plan_payload_contract(self) -> None:
        payload = plan_payload(PlanRequest(week=2, ppm=500.0, house_temp=22.0))

        self.assertEqual(sorted(payload.keys()), ["hours", "input", "summary"])
        self.assertEqual(payload["summary"]["hours"], 168)
        self.assertEqual(len(payload["hours"]), 168)
        self.assertIn("supply_pct", payload["hours"][0])
        self.assertIn("ppm_absolute", payload["hours"][0])

    def test_invalid_inputs_are_rejected(self) -> None:
        cases = [
            {"ppm": ["500"], "houseTemp": ["22"]},
            {"week": ["54"], "ppm": ["500"], "houseTemp": ["22"]},
            {"week": ["2"], "ppm": ["bad"], "houseTemp": ["22"]},
            {"week": ["2"], "ppm": ["500"], "houseTemp": ["bad"]},
        ]
        for query in cases:
            with self.subTest(query=query):
                with self.assertRaises(ValueError):
                    parse_plan_query(query)


if __name__ == "__main__":
    unittest.main()
