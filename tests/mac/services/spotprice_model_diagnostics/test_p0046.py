from __future__ import annotations

from datetime import date, timedelta
import math
import unittest

from src.mac.services.spotprice_model_diagnostics import p0045, p0046
from tests.mac.services.spotprice_model_diagnostics.test_p0045 import make_ai1, make_hour


class P0046Tests(unittest.TestCase):
    def test_build_origin_windows_uses_monday_06_and_exact_168_hours(self):
        start = date(2026, 1, 5)
        ai1 = [make_ai1(start + timedelta(days=offset)) for offset in range(8)]
        ai2 = [make_hour(start + timedelta(days=day), hour) for day in range(8) for hour in range(24)]
        windows = p0046.build_origin_windows(ai1, ai2)
        self.assertEqual(1, len(windows))
        self.assertEqual("holdout", windows[0]["split"])
        self.assertEqual(6, windows[0]["origin_hour"])
        self.assertEqual(168, len(windows[0]["hourly_rows"]))
        self.assertEqual(6, windows[0]["hourly_rows"][0]["model_cet_hour"])
        self.assertEqual(5, windows[0]["hourly_rows"][-1]["model_cet_hour"])

    def test_build_origin_windows_rejects_incomplete_window(self):
        start = date(2026, 1, 5)
        ai1 = [make_ai1(start + timedelta(days=offset)) for offset in range(7)]
        ai2 = [make_hour(start + timedelta(days=day), hour) for day in range(7) for hour in range(24)]
        self.assertEqual([], p0046.build_origin_windows(ai1, ai2))

    def test_anchor_scenarios_use_only_first_n_hours_and_eval_excludes_anchor(self):
        window = {
            "target_series": "system_proxy_se1",
            "origin_date": "2026-01-05",
            "origin_hour": 6,
            "split": "holdout",
            "hourly_rows": [make_hour(date(2026, 1, 5) + timedelta(days=index // 24), index % 24) for index in range(168)],
        }
        forecast = [float(index) for index in range(168)]
        row = p0046.evaluate_anchored_window(window, "x", "direct", 16, forecast)
        self.assertEqual(152, row["evaluation_hours"])

    def test_fit_anchor_guardrails_return_finite_positive_scale(self):
        params = p0046.fit_anchor("L2_level_scale", [1.0] * 16, [0.0] * 16, 16)
        self.assertEqual(1.0, params["scale"])
        forecast = p0046.apply_anchor(params, [0.0, 1.0, -1.0])
        self.assertTrue(all(math.isfinite(value) for value in forecast))

    def test_l3_scale_shrinks_toward_prior(self):
        actual = [float(index) * 10.0 for index in range(16)]
        shape = [float(index) for index in range(16)]
        l2 = p0046.fit_anchor("L2_level_scale", actual, shape, 16)
        l3 = p0046.fit_anchor("L3_shrink_scale", actual, shape, 16)
        self.assertLess(float(l3["scale"]), float(l2["scale"]))
        self.assertGreater(float(l3["scale"]), 1.0)

    def test_p0046_uses_p0045_selected_shape_source(self):
        self.assertIn("P0045_combined_scaled", p0046.SHAPE_PREDICTORS)
        self.assertEqual("combined_scaled", p0045.select_formulas({"system_proxy_se1": {"validate": {"combined_scaled": {"shape_MAE_scaled": 1.0}, "combined_dimensionless": {"shape_MAE_scaled": 2.0}}}, "area_diff_proxy_se3": {"validate": {"combined_scaled": {"shape_MAE_scaled": 1.0}, "combined_dimensionless": {"shape_MAE_scaled": 2.0}}}})["system_proxy_se1"])

    def test_oracle_is_not_in_shape_predictors(self):
        for predictor in p0046.ORACLE_PREDICTORS:
            self.assertNotIn(predictor, p0046.SHAPE_PREDICTORS)

    def test_forbidden_paths_constant(self):
        self.assertEqual(("AI1_RETRAIN", "AI2_RETRAIN", "PRODUCTION_API", "M5", "M6", "M7", "SHELLY", "DEVICE", "KVS", "HA"), p0046.FORBIDDEN_PRODUCTION_PATHS)


if __name__ == "__main__":
    unittest.main()
