from __future__ import annotations

from datetime import date, timedelta
import math
import unittest

from src.mac.services.spotprice_model_diagnostics import p0045


def make_hour(day: date, hour: int, series: str = "system_proxy_se1") -> dict[str, object]:
    return {
        "timestamp_utc": f"{day.isoformat()}T{hour:02d}:00:00+00:00",
        "model_cet_date": day.isoformat(),
        "model_cet_hour": hour,
        "model_cet_weekday": day.weekday(),
        "target_series": series,
        "hour_price": float(hour + day.day),
        "hour_shape": float(hour - 12) / 12.0,
        "day_intraday_scale": 2.0,
        "is_special_day": 0,
        "is_bridge_day": 0,
        "is_holiday_period": 0,
        "hourly_temperature_delta": 1.0,
        "hourly_solar_actual": 10.0,
        "hourly_wind_actual": 0.2,
    }


def make_ai1(day: date, series: str = "system_proxy_se1") -> dict[str, object]:
    return {
        "model_cet_date": day.isoformat(),
        "target_series": series,
        "day_level_shape": 0.1,
        "log_day_scale_index": 0.0,
        "log_local_7d_scale": math.log(2.0),
    }


class P0045Tests(unittest.TestCase):
    def test_centered_shape_has_zero_mean(self):
        centered = p0045.center([1.0, 2.0, 3.0])
        self.assertAlmostEqual(0.0, sum(centered))

    def test_build_forecast_windows_requires_168_hours(self):
        start = date(2026, 1, 1)
        ai1 = [make_ai1(start + timedelta(days=offset)) for offset in range(7)]
        ai2 = [make_hour(start + timedelta(days=day), hour) for day in range(7) for hour in range(24)]
        windows = p0045.build_forecast_windows(ai1, ai2)
        self.assertEqual(1, len(windows))
        self.assertEqual(168, len(windows[0]["hourly_rows"]))

    def test_build_forecast_windows_rejects_incomplete_window(self):
        start = date(2026, 1, 1)
        ai1 = [make_ai1(start + timedelta(days=offset)) for offset in range(7)]
        ai2 = [make_hour(start + timedelta(days=day), hour) for day in range(7) for hour in range(23)]
        self.assertEqual([], p0045.build_forecast_windows(ai1, ai2))

    def test_area_diff_weak_scale_policy_is_fallback(self):
        self.assertEqual("fallback_zero", p0045.AI1_SELECTED_GROUPS["area_diff_proxy_se3"]["log_day_scale_index"])
        self.assertEqual("fallback_train_mean", p0045.AI1_SELECTED_GROUPS["area_diff_proxy_se3"]["log_local_7d_scale"])

    def test_combine_window_scales_are_finite_and_centered(self):
        start = date(2026, 1, 1)
        hourly = [make_hour(start + timedelta(days=day), hour) for day in range(7) for hour in range(24)]
        window = {"target_series": "system_proxy_se1", "origin_date": start.isoformat(), "split": "holdout", "hourly_rows": hourly}
        ai1 = {"system_proxy_se1": {(start + timedelta(days=day)).isoformat(): {"day_level_shape": 0.1, "log_day_scale_index": 0.0, "log_local_7d_scale": math.log(2.0)} for day in range(7)}}
        ai2 = {"system_proxy_se1": {p0045.hour_key(row): 0.1 for row in hourly}}
        pred = p0045.combine_window(window, ai1, ai2, "scaled")
        self.assertEqual(168, len(pred))
        self.assertAlmostEqual(0.0, sum(pred), places=9)
        self.assertTrue(all(math.isfinite(value) for value in pred))

    def test_oracles_are_not_deployable_predictors(self):
        for predictor in p0045.ORACLE_PREDICTORS:
            self.assertNotIn(predictor, p0045.DEPLOYABLE_PREDICTORS)

    def test_forbidden_paths_constant(self):
        self.assertEqual(("NEW_AI_TRAINING", "ABSOLUTE_API", "M5", "M6", "M7", "API", "SHELLY", "DEVICE", "KVS", "HA"), p0045.FORBIDDEN_PRODUCTION_PATHS)


if __name__ == "__main__":
    unittest.main()
