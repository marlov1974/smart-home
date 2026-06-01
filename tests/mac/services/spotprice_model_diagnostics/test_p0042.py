from __future__ import annotations

from datetime import date, datetime, timezone, timedelta
import unittest

from src.mac.services.spotprice_model_diagnostics import p0042


def row(utc: datetime, se1: float = 1.0, area: float = 0.1) -> dict[str, object]:
    return {
        "utc_hour_start": utc.astimezone(timezone.utc).isoformat(),
        "actual_se1": se1,
        "actual_area_diff": area,
        "se1_system_temperature": 5.0,
        "m3c_solar_proxy_area": 10.0,
        "m3d_wind_proxy_area": 0.2,
        "daily_wind_system_proxy_hourly": 0.2,
        "daily_wind_south_proxy_hourly": 0.3,
        "daily_wind_central_proxy_hourly": 0.2,
        "daily_wind_north_proxy_hourly": 0.1,
        "model_special_day_type": "normal_weekday",
        "model_special_day_name": "normal",
        "model_special_day_group": "normal",
        "model_bridge_strength": "none",
        "model_is_special_day": 0,
        "model_is_holiday_period": 0,
        "model_is_major_social_holiday": 0,
    }


def fixed_cet_day(model_day: date) -> list[dict[str, object]]:
    # model CET 00:00 is UTC previous day 23:00.
    start = datetime(model_day.year, model_day.month, model_day.day, tzinfo=timezone.utc) - timedelta(hours=1)
    rows = [row(start + timedelta(hours=hour), se1=float(hour), area=0.01 * (hour % 2)) for hour in range(24)]
    p0042.attach_time_fields(rows)
    for item in rows:
        for signal in p0042.SIGNALS:
            item[f"{signal}_actual"] = 1.0
            item[f"{signal}_normal"] = 0.5
            item[f"{signal}_delta"] = 0.5
    return rows


class P0042Tests(unittest.TestCase):
    def test_model_cet_timestamp_is_utc_plus_one_hour(self):
        rows = [row(datetime(2026, 3, 29, 0, tzinfo=timezone.utc))]
        p0042.attach_time_fields(rows)
        self.assertEqual("2026-03-29T01:00:00+00:00", rows[0]["model_cet_timestamp"])
        self.assertEqual("2026-03-29", rows[0]["model_cet_date"])
        self.assertEqual(1, rows[0]["model_cet_hour"])

    def test_dst_transition_has_24_fixed_cet_model_hours(self):
        rows = fixed_cet_day(date(2026, 3, 29))
        complete = p0042.complete_model_days(rows)
        self.assertEqual(1, len(complete))
        hours = [item["model_cet_hour"] for item in complete["2026-03-29"]]
        self.assertEqual(list(range(24)), hours)
        self.assertTrue(any(item["stockholm_is_dst"] for item in rows))

    def test_ai2_groups_by_model_cet_date_not_stockholm_date(self):
        rows = fixed_cet_day(date(2026, 3, 29))
        ai2 = p0042.build_ai2_rows_v2(rows, {"system_proxy_se1": 0.001, "area_diff_proxy_se3": 0.1})
        self.assertEqual({"2026-03-29"}, {item["model_cet_date"] for item in ai2})
        self.assertGreater(len({item["stockholm_local_date"] for item in ai2}), 1)

    def test_ai1_window_crosses_calendar_year(self):
        rows = []
        for offset in range(7):
            rows.extend(fixed_cet_day(date(2025, 12, 30) + timedelta(days=offset)))
        daily = p0042.build_daily_weather_v2(rows)
        ai1, skipped = p0042.build_ai1_rows_v2(rows, daily, {"system_proxy_se1": 0.001, "area_diff_proxy_se3": 0.1})
        center = [item for item in ai1 if item["model_cet_date"] == "2026-01-01" and item["target_series"] == "system_proxy_se1"]
        self.assertEqual(1, len(center))
        self.assertEqual("2025-12-30", center[0]["local_7d_start"])
        self.assertEqual("2026-01-05", center[0]["local_7d_end"])
        self.assertEqual(6, skipped["skipped_center_dates"])

    def test_area_diff_scale_floor_is_target_specific(self):
        policy = {"system_proxy_se1": 0.001, "area_diff_proxy_se3": 0.1}
        self.assertEqual(0.001, p0042.scale_for_target([0.0] * 24, "system_proxy_se1", policy))
        self.assertEqual(0.1, p0042.scale_for_target([0.0] * 24, "area_diff_proxy_se3", policy))

    def test_forbidden_paths_constant(self):
        self.assertEqual(("M5", "M6", "M7", "API", "SHELLY", "DEVICE", "KVS", "HA"), p0042.FORBIDDEN_PRODUCTION_PATHS)


if __name__ == "__main__":
    unittest.main()
