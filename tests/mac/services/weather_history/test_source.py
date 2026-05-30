from datetime import date
import json
import unittest

from src.mac.services.weather_history.models import WEATHER_VARIABLES
from src.mac.services.weather_history.source import parse_open_meteo_response, utc_request_dates_for_local_range
from src.mac.services.weather_history.storage import DEFAULT_LOCATIONS, expected_utc_hours_for_local_date


class WeatherSourceTests(unittest.TestCase):
    def test_parse_open_meteo_response_requires_all_variables(self):
        hours = expected_utc_hours_for_local_date(date(2025, 1, 2))
        payload = {
            "hourly": {
                "time": [hour.strftime("%Y-%m-%dT%H:%M") for hour in hours],
                **{name: [1.0] * len(hours) for name in WEATHER_VARIABLES},
            }
        }
        rows = parse_open_meteo_response(json.dumps(payload), DEFAULT_LOCATIONS[0], hours)

        self.assertEqual(24, len(rows))
        self.assertEqual("2025-01-01T23:00Z", rows[0].utc_hour_start)

    def test_missing_variable_fails(self):
        hours = expected_utc_hours_for_local_date(date(2025, 1, 2))
        payload = {"hourly": {"time": [hour.strftime("%Y-%m-%dT%H:%M") for hour in hours]}}

        with self.assertRaisesRegex(ValueError, "missing hourly variable"):
            parse_open_meteo_response(json.dumps(payload), DEFAULT_LOCATIONS[0], hours)

    def test_utc_request_dates_cover_local_day(self):
        start, end = utc_request_dates_for_local_range(date(2025, 1, 2), date(2025, 1, 2))

        self.assertEqual(date(2025, 1, 1), start)
        self.assertEqual(date(2025, 1, 2), end)


if __name__ == "__main__":
    unittest.main()
