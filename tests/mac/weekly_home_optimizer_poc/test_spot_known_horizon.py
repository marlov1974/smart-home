from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.mac.labs.weekly_home_optimizer_poc.server import PlanRequest, plan_payload
from src.mac.labs.weekly_home_optimizer_poc.spot import (
    build_spot_plan,
    build_spot_plan_for_window,
    resolve_week_utc_hours,
)
from src.mac.labs.weekly_home_optimizer_poc.tables import rows_for_plan
from src.mac.labs.weekly_home_optimizer_poc.planner import build_weekly_plan


def _write_fixture(path: Path, utc_hours: tuple[str, ...], count: int = 168) -> None:
    lines = [
        "utc_hour_start,local_hour_start,local_wall_hour,utc_offset,fold,quarter_count,price_mean,price_min,price_max\n"
    ]
    for index, utc_hour in enumerate(utc_hours[:count]):
        price = float(index + 1)
        lines.append(f"{utc_hour},{utc_hour},{utc_hour},+01:00,0,4,{price},{price},{price}\n")
    path.write_text("".join(lines), encoding="utf-8")


class SpotKnownHorizonTests(unittest.TestCase):
    def test_fixed_20_hour_known_horizon(self) -> None:
        plan = build_spot_plan(48)

        self.assertEqual(plan.spot_actual_horizon_hours, 20)
        self.assertEqual(plan.spot_actual_patched_hours, 20)
        self.assertEqual(plan.spot_forecast_hours, 148)
        self.assertEqual(plan.spot_planning_source[:20], ("actual_horizon_patched",) * 20)
        self.assertEqual(set(plan.spot_planning_source[20:]), {"forecast"})
        self.assertEqual(plan.spot_actual_patched_hours + plan.spot_forecast_hours, 168)

    def test_horizon_patch_preserves_forecast_sum(self) -> None:
        plan = build_spot_plan(48)

        self.assertAlmostEqual(sum(plan.spot_planning_index[:20]), sum(plan.spot_forecast_index[:20]))

    def test_optimizer_does_not_see_future_actuals(self) -> None:
        plan = build_spot_plan(48)

        self.assertTrue(all(plan.spot_actual_available))
        self.assertEqual(plan.spot_planning_index[20:], plan.spot_forecast_index[20:])
        self.assertTrue(any(value is not None for value in plan.spot_actual_outcome_index[20:]))

    def test_forecast_vs_actual_diagnostics_are_rendered(self) -> None:
        plan = build_weekly_plan(48, 500.0, 22.0, people=4, prefer_real_weather=False)

        row = rows_for_plan(plan)[20]

        self.assertEqual(row["spot_planning_source"], "forecast")
        self.assertTrue(row["spot_actual_available"])
        self.assertIn("spot_forecast_index", row)
        self.assertIn("spot_planning_index", row)
        self.assertIsNotNone(row["spot_actual_outcome_index"])
        self.assertIsNotNone(row["spot_forecast_error_index"])
        self.assertIsNotNone(row["spot_forecast_error_pct"])

    def test_partial_actual_horizon_shorter_than_20(self) -> None:
        utc_hours = resolve_week_utc_hours(8, iso_year=2026)
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "spot_2026_partial.csv"
            _write_fixture(path, utc_hours, count=11)

            plan = build_spot_plan_for_window(8, iso_year=2026, actual_fixture_path=path)

        self.assertEqual(plan.spot_actual_known_hours, 11)
        self.assertEqual(plan.spot_actual_patched_hours, 11)
        self.assertEqual(plan.spot_forecast_hours, 157)
        self.assertEqual(plan.spot_planning_source[:11], ("actual_horizon_patched",) * 11)
        self.assertEqual(set(plan.spot_planning_source[11:]), {"forecast"})
        self.assertIn("actual_horizon_short", plan.spot_patch_warnings)
        self.assertEqual(sum(plan.spot_actual_available), 11)
        self.assertIsNone(plan.spot_actual_outcome_index[11])

    def test_2026_comparison_fixture_path(self) -> None:
        utc_hours = resolve_week_utc_hours(8, iso_year=2026)
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "spot_2026_week8.csv"
            _write_fixture(path, utc_hours)

            plan = build_spot_plan_for_window(8, iso_year=2026, actual_fixture_path=path)

        self.assertEqual(plan.spot_actual_patched_hours, 20)
        self.assertEqual(plan.spot_planning_source[20], "forecast")
        self.assertTrue(plan.spot_actual_available[20])
        self.assertIsNotNone(plan.spot_forecast_error_index[20])

    def test_backward_compatible_api_smoke(self) -> None:
        payload = plan_payload(PlanRequest(week=48, ppm=500.0, house_temp=22.0, people=4), prefer_real_weather=False)

        self.assertEqual(set(payload), {"input", "summary", "hours"})
        self.assertEqual(len(payload["hours"]), 168)
        self.assertEqual(payload["summary"]["spot_actual_horizon_hours"], 20)


if __name__ == "__main__":
    unittest.main()
