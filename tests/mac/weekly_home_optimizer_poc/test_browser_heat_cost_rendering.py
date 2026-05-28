from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.html import render_result
from src.mac.labs.weekly_home_optimizer_poc.server import PlanRequest, plan_payload


class BrowserHeatCostRenderingTests(unittest.TestCase):
    def test_browser_renders_heat_cost_comparison(self) -> None:
        payload = plan_payload(PlanRequest(week=2, ppm=500.0, house_temp=22.0), prefer_real_weather=False)

        html = render_result(payload)

        self.assertIn("Heat Cost", html)
        self.assertIn("Opt vs Flat", html)
        self.assertIn("Estimated saving", html)
        self.assertIn("Optimized heat did the weekly job", html)
        self.assertIn("emulated POC", html)


if __name__ == "__main__":
    unittest.main()
