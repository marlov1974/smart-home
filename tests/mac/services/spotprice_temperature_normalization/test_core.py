from datetime import date
from pathlib import Path
import sqlite3
import tempfile
import unittest

from src.mac.services.spotprice_temperature_normalization.core import (
    build_temp_normalized_training_series,
    compute_m1_calm_normal_price,
    compute_m2_climate_anomalies,
    compute_m2_climate_normals,
    compute_m3_statistical_temperature_delta,
    dump_p0032_location_weights,
    initialize_schema,
    open_feature_database,
    select_m2_target_weights,
    temperature_bucket,
    validate_training_foundation,
)
from src.mac.services.spotprice_temperature_normalization.launchd import LABEL, render_launchd_plist


def sample_rows():
    rows = []
    for day in range(1, 61):
        anomaly = -6.0 if day <= 20 else 0.0 if day <= 40 else 6.0
        price = 1.0 + (0.2 if anomaly < 0 else -0.1 if anomaly > 0 else 0.0)
        rows.append(
            {
                "utc_hour_start": f"2025-01-{((day - 1) % 30) + 1:02d}T00:00Z-{day}",
                "local_date": f"2025-01-{((day - 1) % 30) + 1:02d}",
                "local_hour": 1,
                "day_of_year": day,
                "iso_week": (day // 7) + 1,
                "weekday": day % 7,
                "actual_se1": price,
                "actual_area_diff": 0.2 + (0.05 if anomaly < 0 else -0.03 if anomaly > 0 else 0.0),
                "actual_se3": price + 0.2,
                "se1_system_temperature": 3.0 + anomaly,
                "se1_system_apparent_temperature": 2.0 + anomaly,
                "se1_system_heating_degree": max(0.0, 14.0 - anomaly),
                "se1_system_cooling_degree": max(0.0, anomaly - 14.0),
                "se3_load_temperature": 5.0 + anomaly,
                "temp_gradient_se3_load_minus_se1_core": anomaly,
                "apparent_temp_gradient_se3_load_minus_se1_core": anomaly,
                "heating_degree_gradient_se3_load_minus_se1_core": -anomaly,
                "south_temp_gradient_minus_se1_core": anomaly / 2.0,
            }
        )
    return rows


class TemperatureNormalizationCoreTests(unittest.TestCase):
    def test_dump_p0032_location_weights(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "weather.sqlite3"
            with sqlite3.connect(db) as conn:
                conn.execute(
                    """
                    CREATE TABLE weather_locations (
                      area_proxy TEXT, name TEXT, latitude REAL, longitude REAL, weight REAL
                    )
                    """
                )
                conn.execute(
                    "INSERT INTO weather_locations VALUES ('se1_core_weather','Kiruna',67.8,20.2,0.11)"
                )
            rows = dump_p0032_location_weights(db)
        self.assertEqual(1, len(rows))
        self.assertEqual("se1_core_weather", rows[0]["area_proxy"])

    def test_m1_uses_calendar_price_rows(self):
        rows = sample_rows()
        m1 = compute_m1_calm_normal_price(rows)
        self.assertEqual(len(rows) * 2, len(m1))
        self.assertTrue(all(row["method"].startswith("median_same_weekday") for row in m1))
        self.assertIn("normal_price", m1[0])

    def test_m2_normals_and_anomalies(self):
        rows = sample_rows()
        normals = compute_m2_climate_normals(rows)
        anomalies = compute_m2_climate_anomalies(rows, normals)
        self.assertEqual(len(normals), len(anomalies))
        self.assertTrue(any(row["signal"] == "se1_system_temperature" for row in anomalies))
        self.assertTrue(any(row["signal"] == "se3_load_temperature" for row in anomalies))

    def test_m1_m2_buckets_aggregate_across_years(self):
        rows = []
        for year, price, temp in ((2023, 1.0, -4.0), (2024, 3.0, 0.0), (2025, 100.0, 4.0)):
            row = sample_rows()[0].copy()
            row.update(
                {
                    "utc_hour_start": f"{year}-01-02T00:00Z",
                    "local_date": f"{year}-01-02",
                    "actual_se1": price,
                    "actual_area_diff": price / 10.0,
                    "actual_se3": price + price / 10.0,
                    "iso_week": 1,
                    "weekday": 0,
                    "day_of_year": 2,
                    "se1_system_temperature": temp,
                    "se3_load_temperature": temp + 2.0,
                }
            )
            rows.append(row)

        m1 = compute_m1_calm_normal_price(rows)
        se1_m1 = [row for row in m1 if row["target"] == "system_proxy_se1"]
        self.assertTrue(all(row["bucket_year_count"] == 3 for row in se1_m1))
        self.assertTrue(all(row["normal_price"] == 3.0 for row in se1_m1))

        m2 = compute_m2_climate_normals(rows)
        se1_temp = [row for row in m2 if row["signal"] == "se1_system_temperature"]
        self.assertTrue(all(row["bucket_year_count"] == 3 for row in se1_temp))
        self.assertTrue(all(row["normal_value"] == 0.0 for row in se1_temp))
        se3_temp = [row for row in m2 if row["signal"] == "se3_load_temperature"]
        self.assertTrue(all(row["bucket_year_count"] == 3 for row in se3_temp))
        self.assertTrue(all(row["normal_value"] == 2.0 for row in se3_temp))

    def test_level2_weight_selection(self):
        weights = select_m2_target_weights()
        se1_temp = [row for row in weights if row["target"] == "se1_system_temperature"]
        self.assertEqual(3, len(se1_temp))
        self.assertAlmostEqual(1.0, sum(float(row["weight"]) for row in se1_temp))

    def test_m3_dead_zone_and_normalized_series(self):
        rows = sample_rows()
        m1 = compute_m1_calm_normal_price(rows)
        normals = compute_m2_climate_normals(rows)
        anomalies = compute_m2_climate_anomalies(rows, normals)
        deltas, buckets = compute_m3_statistical_temperature_delta(rows, m1, anomalies)
        normalized = build_temp_normalized_training_series(rows, m1, deltas)
        self.assertIn("normal", {row["bucket"] for row in buckets})
        normal_deltas = [row for row in deltas if row["bucket"] == "normal"]
        self.assertTrue(normal_deltas)
        self.assertTrue(all(abs(float(row["temp_delta"])) < 0.000001 for row in normal_deltas))
        first = normalized[0]
        self.assertAlmostEqual(
            first["temp_normalized_price_v1_se3"],
            first["temp_normalized_price_v1_se1"] + first["temp_normalized_area_diff_v1"],
        )

    def test_schema_validation_detects_empty_db(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "features.sqlite3"
            with open_feature_database(db) as conn:
                initialize_schema(conn)
                m1_columns = {row["name"] for row in conn.execute("PRAGMA table_info(m1_normal_price_v1)")}
                m2_columns = {row["name"] for row in conn.execute("PRAGMA table_info(m2_climate_normals)")}
                report = validate_training_foundation(conn)
        self.assertIn("bucket_year_count", m1_columns)
        self.assertIn("bucket_year_count", m2_columns)
        self.assertFalse(report["ok"])

    def test_temperature_bucket_boundaries(self):
        self.assertEqual("extreme_cold", temperature_bucket(-8.0))
        self.assertEqual("cold", temperature_bucket(-3.0))
        self.assertEqual("normal", temperature_bucket(0.0))
        self.assertEqual("warm", temperature_bucket(3.0))
        self.assertEqual("extreme_warm", temperature_bucket(8.0))

    def test_launchd_plist_rebuilds_daily_at_1600(self):
        plist = render_launchd_plist(
            price_db="/tmp/spot.sqlite3",
            weather_db="/tmp/weather.sqlite3",
            feature_db="/tmp/features.sqlite3",
            python_executable="/usr/bin/python3",
        )

        self.assertIn(LABEL, plist)
        self.assertIn("src.mac.services.spotprice_temperature_normalization", plist)
        self.assertIn("<string>build</string>", plist)
        self.assertIn("<integer>16</integer>", plist)
        self.assertIn("<integer>0</integer>", plist)
        self.assertIn("/tmp/spot.sqlite3", plist)
        self.assertIn("/tmp/weather.sqlite3", plist)
        self.assertIn("/tmp/features.sqlite3", plist)


if __name__ == "__main__":
    unittest.main()
