from __future__ import annotations

from datetime import date, timedelta
import unittest

from src.mac.services.spotprice_model_diagnostics.p0040 import (
    anchor_predictions,
    build_variant_predictions,
    center,
    compute_shape_metrics,
    forecast_origins,
)


def row(day: date, hour: int, se1: float = 1.0, area: float = 0.1) -> dict[str, object]:
    return {
        "local_date": day.isoformat(),
        "local_hour": hour,
        "actual_se1": se1 + hour / 100.0,
        "actual_area_diff": area,
        "actual_se3": se1 + area + hour / 100.0,
        "m1_raw_se1": se1,
        "m1_raw_area": area,
        "m3a_se1": 0.01,
        "m3a_area": 0.02,
        "m3b_se1": 0.03,
        "m3b_area": 0.04,
        "m3a_m1b_se1": 0.05,
        "m3a_m1b_area": 0.06,
        "m3b_m1b_se1": 0.07,
        "m3b_m1b_area": 0.08,
        "m3c_se1": 0.01,
        "m3c_area": 0.01,
        "m3d_se1": -0.01,
        "m3d_area": -0.02,
        "m4_area": 0.09,
        "se1_system_temperature": 5.0,
        "m3d_wind_proxy_area": 0.2,
        "m3c_solar_proxy_area": 80.0,
        "is_special_day": 0,
        "bridge_strength": "none",
        "special_day_group": "normal",
    }


class P0040DiagnosticsTests(unittest.TestCase):
    def test_forecast_origin_requires_monday_16_known_and_168_horizon(self):
        monday = date(2025, 6, 2)
        rows = [row(monday + timedelta(days=offset), hour) for offset in range(7) for hour in range(24)]
        origins = forecast_origins(rows, date(2025, 6, 1), date(2025, 6, 30))
        self.assertEqual(1, len(origins))
        self.assertEqual(monday, origins[0].origin_date)
        self.assertEqual("06:00", origins[0].origin_local_time)
        self.assertEqual(16, len(origins[0].known_rows))
        self.assertEqual(168, len(origins[0].horizon_rows))

    def test_anchor_mean_is_additive_and_handles_negative_values(self):
        anchored, meta = anchor_predictions([-1.0, 1.0], [0.0, 2.0], [10.0, -10.0], "anchor_16h_mean")
        self.assertEqual([9.0, -11.0], anchored)
        self.assertAlmostEqual(-1.0, meta["offset"])

    def test_centered_shape_is_invariant_to_additive_shift(self):
        actual = [1.0, 2.0, 3.0, 4.0] * 42
        predicted = [value + 100.0 for value in actual]
        self.assertEqual(center(actual), center(predicted))
        metrics = compute_shape_metrics(actual, predicted)
        self.assertAlmostEqual(0.0, metrics["weekly_centered_shape_MAE"])

    def test_recomposed_se3_equals_parts_for_variant(self):
        rows = [row(date(2025, 6, 2), hour) for hour in range(24)]
        pred = build_variant_predictions(rows, "V3_M1_plus_M3A_m1b_M3B_m1b")
        self.assertEqual(
            pred["recomposed_se3"],
            [a + b for a, b in zip(pred["system_proxy_se1"], pred["area_diff_proxy_se3"])],
        )

    def test_m1b_trained_deltas_are_applied_on_m1_baseplate(self):
        sample = row(date(2025, 6, 2), 0)
        pred = build_variant_predictions([sample], "V3_M1_plus_M3A_m1b_M3B_m1b")
        self.assertAlmostEqual(1.0 + 0.05 + 0.07, pred["system_proxy_se1"][0])
        self.assertAlmostEqual(0.1 + 0.06 + 0.08, pred["area_diff_proxy_se3"][0])


if __name__ == "__main__":
    unittest.main()
