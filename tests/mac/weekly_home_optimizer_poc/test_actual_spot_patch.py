from __future__ import annotations

import unittest

from src.mac.labs.weekly_home_optimizer_poc.spot import ActualSpotPrice, patch_forecast_with_actual_prices


def _actual(utc_hour_start: str, price: float) -> ActualSpotPrice:
    return ActualSpotPrice(
        utc_hour_start=utc_hour_start,
        local_hour_start=utc_hour_start,
        local_wall_hour=utc_hour_start,
        utc_offset="+01:00",
        fold=0,
        quarter_count=4,
        price_mean=price,
        price_min=price,
        price_max=price,
    )


class ActualSpotPatchTests(unittest.TestCase):
    def test_actual_shape_preserves_forecast_overlap_sum(self) -> None:
        forecast = (1.0, 1.0, 2.0, 2.0) + (1.0,) * 164
        utc_hours = tuple(f"h{hour}" for hour in range(168))
        actual = {
            "h0": _actual("h0", 10.0),
            "h1": _actual("h1", 20.0),
            "h2": _actual("h2", 30.0),
            "h3": _actual("h3", 40.0),
        }

        plan = patch_forecast_with_actual_prices(forecast, utc_hours, actual, actual_horizon_hours=4)

        for actual, expected in zip(plan.spot_index[:4], (0.6, 1.2, 1.8, 2.4)):
            self.assertAlmostEqual(actual, expected)
        self.assertAlmostEqual(sum(plan.spot_index[:4]), 6.0)
        self.assertEqual(plan.spot_source[:4], ("actual_horizon_patched",) * 4)
        self.assertEqual(plan.spot_planning_source[:4], ("actual_horizon_patched",) * 4)
        self.assertEqual(plan.spot_forecast_index[:4], (1.0, 1.0, 2.0, 2.0))
        self.assertEqual(plan.spot_actual_proto_index[:4], (0.4, 0.8, 1.2, 1.6))
        for actual, expected in zip(plan.spot_patched_actual_index[:4], (0.6, 1.2, 1.8, 2.4)):
            self.assertAlmostEqual(actual, expected)
        self.assertEqual(plan.spot_actual_patched_hours, 4)
        self.assertEqual(plan.spot_patch_warnings, ())

    def test_no_overlap_keeps_forecast_and_warns(self) -> None:
        forecast = (1.0,) * 168
        utc_hours = tuple(f"h{hour}" for hour in range(168))

        plan = patch_forecast_with_actual_prices(forecast, utc_hours, {})

        self.assertEqual(plan.spot_index, forecast)
        self.assertEqual(set(plan.spot_source), {"forecast"})
        self.assertEqual(plan.spot_actual_patched_hours, 0)
        self.assertEqual(plan.spot_patch_warnings, ("no_actual_overlap", "actual_horizon_short"))


if __name__ == "__main__":
    unittest.main()
