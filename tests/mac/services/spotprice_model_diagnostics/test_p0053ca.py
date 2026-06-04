from __future__ import annotations

from datetime import date, timedelta
import math
import unittest

from src.mac.services.spotprice_model_diagnostics import p0053ca


def make_hour(day: date, hour: int, series: str = "system_proxy_se1") -> dict[str, object]:
    ts = day.isoformat() + f"T{hour:02d}:00:00Z"
    return {
        "timestamp_utc": ts,
        "model_cet_date": day.isoformat(),
        "model_cet_hour": hour,
        "model_cet_weekday": day.weekday(),
        "target_series": series,
        "hour_price": float(hour),
        "hour_shape": float(hour - 12) / 12.0,
        "day_intraday_scale": 2.0,
        "is_special_day": 0,
        "is_bridge_day": 0,
        "is_holiday_period": 0,
        "hourly_temperature_delta": 0.0,
        "hourly_solar_actual": 1.0,
        "hourly_wind_actual": 1.0,
    }


def make_ai1(day: date, series: str = "system_proxy_se1") -> dict[str, object]:
    return {
        "model_cet_date": day.isoformat(),
        "target_series": series,
        "day_level_shape": 0.0,
        "log_day_scale_index": 0.0,
        "log_local_7d_scale": math.log(2.0),
    }


class P0053CATests(unittest.TestCase):
    def test_filter_ai2_policy_rows_drops_pre_start_targets(self):
        rows = [make_hour(date(2022, 5, 31), 23), make_hour(date(2022, 6, 1), 0)]
        filtered = p0053ca.filter_ai2_policy_rows(rows)
        self.assertEqual(["2022-06-01T00:00:00Z"], [row["timestamp_utc"] for row in filtered])

    def test_build_policy_windows_requires_one_canonical_split(self):
        start = date(2025, 5, 28)
        ai1 = [make_ai1(start + timedelta(days=offset)) for offset in range(7)]
        ai2 = [make_hour(start + timedelta(days=day), hour) for day in range(7) for hour in range(24)]
        p0053ca.assign_ai1_policy_splits(ai1)
        p0053ca.assign_policy_splits(ai2, "timestamp_utc")
        self.assertEqual([], p0053ca.build_policy_forecast_windows(ai1, ai2))

    def test_forecast_origin_log_has_required_timestamp_order(self):
        start = date(2025, 6, 1)
        hourly = [make_hour(start + timedelta(days=day), hour) for day in range(7) for hour in range(24)]
        window = {"target_series": "system_proxy_se1", "origin_date": start.isoformat(), "split": "holdout", "hourly_rows": hourly}
        ai1 = {"system_proxy_se1": {(start + timedelta(days=day)).isoformat(): {"day_level_shape": 0.0, "log_day_scale_index": 0.0, "log_local_7d_scale": math.log(2.0)} for day in range(7)}}
        ai2 = {"system_proxy_se1": {f"system_proxy_se1|{row['timestamp_utc']}": 0.1 for row in hourly}}
        rows = p0053ca.build_forecast_origin_log_rows([window], {"system_proxy_se1": "combined_scaled"}, ai1, ai2)
        self.assertEqual(168, len(rows))
        first = rows[0]
        self.assertEqual("shape_index", first["prediction_kind"])
        self.assertEqual("2025-06-01T00:00:00Z", first["forecast_origin_timestamp_utc"])
        self.assertLessEqual(first["input_data_cutoff_utc"], first["forecast_origin_timestamp_utc"])
        self.assertLessEqual(first["forecast_origin_timestamp_utc"], first["target_timestamp_utc"])
        self.assertEqual(set(p0053ca.forecast_log_columns()), set(first))


if __name__ == "__main__":
    unittest.main()
