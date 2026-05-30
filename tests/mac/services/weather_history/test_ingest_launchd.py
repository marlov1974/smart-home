from datetime import date
import json
from pathlib import Path
import tempfile
import unittest

from src.mac.services.weather_history.ingest import ingest_daily, latest_safe_complete_day
from src.mac.services.weather_history.launchd import LABEL, render_launchd_plist
from src.mac.services.weather_history.models import WEATHER_VARIABLES
from src.mac.services.weather_history.storage import connect_db, expected_utc_hours_for_local_date, initialize_schema


def payload_for(hours):
    return json.dumps(
        {
            "hourly": {
                "time": [hour.strftime("%Y-%m-%dT%H:%M") for hour in hours],
                **{name: [1.0] * len(hours) for name in WEATHER_VARIABLES},
            }
        }
    ).encode("utf-8")


class WeatherIngestLaunchdTests(unittest.TestCase):
    def test_latest_safe_complete_day_uses_six_day_delay(self):
        self.assertEqual(date(2026, 5, 24), latest_safe_complete_day(date(2026, 5, 30)))

    def test_daily_ingest_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "weather.sqlite3"
            initialize_schema(db)
            calls = []

            def fetcher(location, start_utc_date, end_utc_date):
                calls.append(location.location_id)
                return payload_for(expected_utc_hours_for_local_date(date(2026, 5, 24)))

            with connect_db(db) as conn:
                first = ingest_daily(conn, db_path=str(db), today=date(2026, 5, 30), fetcher=fetcher)
                second = ingest_daily(conn, db_path=str(db), today=date(2026, 5, 30), fetcher=fetcher)

        self.assertEqual("ok", first.status)
        self.assertEqual("no_new_complete_day_available", second.status)
        self.assertEqual(4, len(calls))

    def test_launchd_plist_contract(self):
        plist = render_launchd_plist(db_path="/tmp/weather.sqlite3", python_executable="/usr/bin/python3")

        self.assertIn(LABEL, plist)
        self.assertIn("src.mac.services.weather_history", plist)
        self.assertIn("<integer>15</integer>", plist)
        self.assertIn("<integer>30</integer>", plist)
        self.assertIn("weather-history-daily.out.log", plist)


if __name__ == "__main__":
    unittest.main()
