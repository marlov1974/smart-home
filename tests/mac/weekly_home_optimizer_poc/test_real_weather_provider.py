from __future__ import annotations

from datetime import date, datetime, timedelta
import unittest
from unittest.mock import patch

from src.mac.labs.weekly_home_optimizer_poc.weather import (
    latest_completed_iso_year_for_week,
    parse_open_meteo_hourly,
    synthetic_fallback_profile,
    weather_profile_for_week,
)


def _open_meteo_fixture(year: int, week: int) -> dict[str, object]:
    start = datetime.combine(date.fromisocalendar(year, week, 1), datetime.min.time())
    hours = 8 * 24
    return {
        "hourly": {
            "time": [(start + timedelta(hours=offset)).strftime("%Y-%m-%dT%H:%M") for offset in range(hours)],
            "temperature_2m": [float(offset % 24) for offset in range(hours)],
            "relative_humidity_2m": [60.0 + float(offset % 10) for offset in range(hours)],
        }
    }


class RealWeatherProviderTests(unittest.TestCase):
    def test_latest_completed_iso_year_strategy(self) -> None:
        self.assertEqual(latest_completed_iso_year_for_week(2, today=date(2026, 5, 28)), 2026)
        self.assertEqual(latest_completed_iso_year_for_week(52, today=date(2026, 5, 28)), 2025)

    def test_open_meteo_fixture_parses_to_168_operational_hours(self) -> None:
        profile = parse_open_meteo_hourly(_open_meteo_fixture(2026, 2), 2026, 2)

        self.assertEqual(len(profile.outdoor_temp_c), 168)
        self.assertEqual(len(profile.outdoor_rh_pct), 168)
        self.assertEqual(profile.weather_source, "real_open_meteo")
        self.assertEqual(profile.weather_profile_year, 2026)
        self.assertEqual(profile.outdoor_temp_c[0], 6.0)

    def test_synthetic_fallback_has_explicit_metadata(self) -> None:
        profile = synthetic_fallback_profile(2, reason="offline")

        self.assertEqual(profile.weather_source, "synthetic_fallback")
        self.assertEqual(profile.weather_fallback_reason, "offline")

    def test_weather_profile_fallback_is_not_silent(self) -> None:
        with patch(
            "src.mac.labs.weekly_home_optimizer_poc.weather.fetch_open_meteo_archive_profile",
            side_effect=RuntimeError("network unavailable"),
        ):
            profile = weather_profile_for_week(2, prefer_real=True)

        self.assertEqual(profile.weather_source, "synthetic_fallback")
        self.assertIn("network unavailable", profile.weather_fallback_reason or "")


if __name__ == "__main__":
    unittest.main()
