from __future__ import annotations

from datetime import datetime
import unittest
from zoneinfo import ZoneInfo

from src.mac.services.spotprice_model_diagnostics import p0056h


class P0056HLagProtocolTests(unittest.TestCase):
    def test_historical_origin_schedule_steps_every_five_days(self) -> None:
        start = datetime(2025, 6, 1, 6, 0, tzinfo=ZoneInfo("Europe/Stockholm"))
        origins = p0056h.historical_origin_schedule(start.date(), start.replace(day=16))
        self.assertEqual([origin.origin_local.day for origin in origins], [1, 6, 11, 16])
        self.assertEqual([origin.origin_local.weekday() for origin in origins], [6, 4, 2, 0])

    def test_anchored_historical_origin_schedule_includes_primary_phase(self) -> None:
        anchor = datetime(2025, 6, 1, 6, 0, tzinfo=ZoneInfo("Europe/Stockholm"))
        origins = p0056h.anchored_historical_origin_schedule(anchor.date().replace(year=2022), anchor, anchor)
        self.assertIn(anchor, [origin.origin_local for origin in origins])

    def test_classify_lag_marks_recursive_window(self) -> None:
        origin = "2025-06-01T04:00:00Z"
        target = "2025-06-01T14:00:00Z"
        self.assertEqual(p0056h.classify_lag(target, origin, 1), "requires_recursive_forecast")
        self.assertEqual(p0056h.classify_lag(target, origin, 24), "known_actual_before_origin")

    def test_metric_scope_returns_36h_mae(self) -> None:
        rows = [{"target_consumption_se3_mw": 100.0, p0056h.PREDICTION_COLUMN: 110.0} for _ in range(36)]
        metric = p0056h.metric_scope(rows, p0056h.PREDICTION_COLUMN)
        self.assertEqual(metric["rows"], 36)
        self.assertAlmostEqual(float(metric["MAE"]), 10.0)
        self.assertAlmostEqual(float(metric["bias"]), 10.0)


if __name__ == "__main__":
    unittest.main()
