from datetime import date
from pathlib import Path
import tempfile
import unittest

from src.mac.services.weather_history.models import WEATHER_VARIABLES, WeatherObservation
from src.mac.services.weather_history.storage import (
    AREA_PROXY,
    compute_area_proxy_hourly,
    configured_locations,
    connect_db,
    expected_utc_hours_for_local_date,
    initialize_schema,
    upsert_weather_observations,
    validate_weather_continuity,
)


def observation(location_id, utc_dt, value=10.0):
    from src.mac.services.weather_history.storage import iso_z, local_parts

    local_hour_start, local_date, local_hour, utc_offset, fold = local_parts(utc_dt)
    return WeatherObservation(
        location_id=location_id,
        utc_hour_start=iso_z(utc_dt),
        local_hour_start=local_hour_start,
        local_date=local_date,
        local_hour=local_hour,
        timezone="Europe/Stockholm",
        utc_offset=utc_offset,
        fold=fold,
        values={name: value for name in WEATHER_VARIABLES},
        source_model="era5_seamless",
        source="fixture",
    )


class WeatherStorageTests(unittest.TestCase):
    def test_expected_hours_handle_dst(self):
        self.assertEqual(23, len(expected_utc_hours_for_local_date(date(2025, 3, 30))))
        self.assertEqual(25, len(expected_utc_hours_for_local_date(date(2025, 10, 26))))
        self.assertEqual(24, len(expected_utc_hours_for_local_date(date(2025, 1, 2))))

    def test_schema_locations_and_area_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "weather.sqlite3"
            initialize_schema(db)
            with connect_db(db) as conn:
                locations = configured_locations(conn)
                hours = expected_utc_hours_for_local_date(date(2025, 1, 2))
                rows = [observation(location.location_id, hour, value=10.0) for location in locations for hour in hours]
                self.assertEqual(96, upsert_weather_observations(conn, rows, ingest_run_id=1))
                self.assertEqual(24, compute_area_proxy_hourly(conn, area_proxy=AREA_PROXY, start_date=date(2025, 1, 2), end_date=date(2025, 1, 2), ingest_run_id=1))
                report = validate_weather_continuity(conn, date(2025, 1, 2), date(2025, 1, 2), db_path=str(db))

        self.assertTrue(report.complete)
        self.assertEqual(96, report.location_row_count)
        self.assertEqual(24, report.area_row_count)
        self.assertEqual(0, report.area_gap_count)


if __name__ == "__main__":
    unittest.main()
