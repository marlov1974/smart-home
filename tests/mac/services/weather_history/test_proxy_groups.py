from datetime import date
from pathlib import Path
import tempfile
import unittest

from src.mac.services.weather_history.models import WEATHER_VARIABLES, WeatherObservation
from src.mac.services.weather_history.storage import (
    all_area_proxies,
    compute_all_area_proxy_hourly,
    configured_locations,
    connect_db,
    expected_utc_hours_for_local_date,
    initialize_schema,
    local_parts,
    iso_z,
    upsert_weather_observations,
    validate_proxy_groups,
)


def observation(location_id, utc_dt, value):
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


class WeatherProxyGroupTests(unittest.TestCase):
    def test_proxy_groups_and_gradients_compute(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "weather.sqlite3"
            initialize_schema(db)
            with connect_db(db) as conn:
                proxies = all_area_proxies(conn)
                self.assertIn("se1_core_weather", proxies)
                self.assertIn("se3_load_weather", proxies)
                self.assertLess(
                    sum(loc.weight for loc in configured_locations(conn, "south_connected_weather")),
                    sum(loc.weight for loc in configured_locations(conn, "se1_core_weather")) + 0.001,
                )
                hours = expected_utc_hours_for_local_date(date(2025, 1, 2))
                rows = []
                for area_proxy in ("se1_core_weather", "nordic_connected_weather", "south_connected_weather", "se3_load_weather"):
                    for location in configured_locations(conn, area_proxy):
                        for hour in hours:
                            rows.append(observation(location.location_id, hour, 10.0))
                upsert_weather_observations(conn, rows, ingest_run_id=1)
                compute_all_area_proxy_hourly(conn, start_date=date(2025, 1, 2), end_date=date(2025, 1, 2), ingest_run_id=1)
                report = validate_proxy_groups(conn, date(2025, 1, 2), date(2025, 1, 2), db_path=str(db))

        self.assertTrue(report["complete"])
        self.assertEqual(24, report["gradient_row_count"])
        self.assertEqual(0, report["gradient_null_count"])


if __name__ == "__main__":
    unittest.main()
