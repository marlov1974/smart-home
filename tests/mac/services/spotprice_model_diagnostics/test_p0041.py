from __future__ import annotations

from datetime import date, datetime, timedelta
import unittest

from src.mac.services.spotprice_model_diagnostics import p0041
from src.mac.services.spotprice_model_diagnostics.p0038 import P0038_WIND_LOCATIONS


def fixture_row(day: date, hour: int, se1: float, area: float = 0.2) -> dict[str, object]:
    stamp = datetime(day.year, day.month, day.day, hour)
    return {
        "utc_hour_start": stamp.isoformat() + "+00:00",
        "local_date": day.isoformat(),
        "local_hour": hour,
        "weekday": day.weekday(),
        "day_of_year": int(day.strftime("%j")),
        "year": day.year,
        "actual_se1": se1,
        "actual_area_diff": area,
        "special_day_type": "normal",
        "special_day_name": "",
        "is_special_day": 0,
        "bridge_strength": "none",
        "is_holiday_period_day": 0,
        "special_day_group": "normal",
        "temperature_actual": 5.0 + hour / 24.0,
        "temperature_normal": 4.0,
        "temperature_delta": 1.0 + hour / 24.0,
        "solar_actual": float(max(0, 12 - abs(hour - 12))),
        "solar_normal": 1.0,
        "solar_delta": float(max(0, 12 - abs(hour - 12))) - 1.0,
        "wind_actual": 0.3,
        "wind_normal": 0.2,
        "wind_delta": 0.1,
        "daily_wind_system_proxy_hourly": 0.3,
        "daily_wind_south_proxy_hourly": 0.4,
        "daily_wind_central_proxy_hourly": 0.2,
        "daily_wind_north_proxy_hourly": 0.1,
    }


class P0041DatasetTests(unittest.TestCase):
    def test_robust_scale_is_positive_for_flat_near_zero_and_negative_values(self):
        self.assertGreater(p0041.robust_scale([0.0] * 24), 0.0)
        self.assertGreater(p0041.robust_scale([0.00001, -0.00001]), 0.0)
        self.assertGreater(p0041.robust_scale([-5.0, -5.0, -5.0]), 0.0)

    def test_ratio_diagnostic_nulls_unsafe_denominator(self):
        self.assertIsNone(p0041.safe_ratio(10.0, 0.0001))
        self.assertEqual(2.0, p0041.safe_ratio(10.0, 5.0))

    def test_local_window_is_d_minus_2_through_d_plus_4(self):
        day = date(2026, 3, 16)
        window = p0041.local_window_dates(day)
        self.assertEqual(7, len(window))
        self.assertEqual(date(2026, 3, 14), window[0])
        self.assertEqual(date(2026, 3, 20), window[-1])

    def test_ai1_formula_hand_fixture(self):
        start = date(2026, 3, 14)
        rows = []
        for offset in range(7):
            day = start + timedelta(days=offset)
            for hour in range(24):
                rows.append(fixture_row(day, hour, se1=float(offset + hour / 100.0), area=0.1 * offset))
        daily = p0041.build_daily_weather(rows)
        ai1, skipped = p0041.build_ai1_rows(rows, daily)
        center_rows = [row for row in ai1 if row["date"] == "2026-03-16" and row["target_series"] == "system_proxy_se1"]
        self.assertEqual(1, len(center_rows))
        row = center_rows[0]
        self.assertEqual("2026-03-14", row["local_7d_start"])
        self.assertEqual("2026-03-20", row["local_7d_end"])
        self.assertEqual(168, row["local_7d_row_count"])
        self.assertAlmostEqual(
            (row["day_mean_price"] - row["local_7d_mean_price"]) / row["local_7d_level_scale"],
            row["day_level_shape"],
        )
        self.assertEqual(6, skipped["skipped_center_dates"])

    def test_ai2_formula_and_day_mean_shape(self):
        day = date(2026, 3, 16)
        rows = [fixture_row(day, hour, se1=float(hour), area=1.0) for hour in range(24)]
        ai2 = p0041.build_ai2_rows(rows)
        se1_rows = [row for row in ai2 if row["target_series"] == "system_proxy_se1"]
        self.assertEqual(24, len(se1_rows))
        self.assertAlmostEqual(0.0, sum(float(row["hour_shape"]) for row in se1_rows) / len(se1_rows))
        first = se1_rows[0]
        self.assertAlmostEqual((first["hour_price"] - first["day_mean_price"]) / first["day_intraday_scale"], first["hour_shape"])

    def test_m2_fields_present_after_attach(self):
        rows = [fixture_row(date(2026, 3, 16), hour, se1=float(hour)) for hour in range(24)]
        hourly_maps = {
            signal: {(int(row["day_of_year"]), int(row["local_hour"])): 1.0 for row in rows}
            for signal in p0041.SIGNALS
        }
        for row in rows:
            row["se1_system_temperature"] = 2.0
            row["m3c_solar_proxy_area"] = 3.0
            row["m3d_wind_proxy_area"] = 4.0
        p0041.attach_m2_features(rows, hourly_maps)
        for signal in p0041.SIGNALS:
            self.assertIn(f"{signal}_actual", rows[0])
            self.assertIn(f"{signal}_normal", rows[0])
            self.assertIn(f"{signal}_delta", rows[0])

    def test_required_wind_locations_present(self):
        self.assertEqual({"Malmo", "Kalmar", "Kristinehamn", "Pitea", "Ange", "Harnosand"}, set(P0038_WIND_LOCATIONS))

    def test_package_forbids_production_device_paths(self):
        self.assertEqual(("M5", "M6", "M7", "API", "SHELLY", "DEVICE", "KVS", "HA"), p0041.FORBIDDEN_PRODUCTION_PATHS)


if __name__ == "__main__":
    unittest.main()
