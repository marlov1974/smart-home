from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.html import render_result
from src.mac.labs.weekly_home_optimizer_poc.server import PlanRequest, plan_payload


class BrowserSpotRenderingTests(unittest.TestCase):
    def test_browser_renders_spot_metadata_and_source(self) -> None:
        payload = plan_payload(PlanRequest(week=2, ppm=500.0, house_temp=22.0), prefer_real_weather=False)

        html = render_result(payload)

        self.assertIn("Spot Model", html)
        self.assertIn("Spot Horizon", html)
        self.assertIn("Spot Patched", html)
        self.assertIn("spot_source", html)
        self.assertIn("spot_planning_source", html)
        self.assertIn("actual_horizon_patched", html)


if __name__ == "__main__":
    unittest.main()
