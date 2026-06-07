from __future__ import annotations

import unittest

from src.mac.services.spotprice_model_diagnostics import p0056b


class P0056BTests(unittest.TestCase):
    def test_area_proxy_selection_covers_required_areas(self) -> None:
        areas = {str(row["area_code"]) for row in p0056b.area_proxy_selection()}

        self.assertEqual(set(p0056b.REQUIRED_AREAS), areas)
        self.assertEqual(18, len(areas))

    def test_se3_reuses_existing_broad_proxy(self) -> None:
        se3_sources = [row for row in p0056b.area_proxy_selection() if row["area_code"] == "SE3"]

        self.assertEqual(1, len(se3_sources))
        self.assertEqual("area_proxy", se3_sources[0]["source_kind"])
        self.assertEqual("se3_load_weather", se3_sources[0]["source_id"])
        self.assertFalse(se3_sources[0]["fallback_proxy"])

    def test_fallback_areas_are_flagged(self) -> None:
        fallback_areas = {
            str(row["area_code"])
            for row in p0056b.area_proxy_selection()
            if bool(row["fallback_proxy"])
        }

        self.assertEqual(set(p0056b.FALLBACK_AREAS), fallback_areas)
        self.assertIn("DE_LU", fallback_areas)
        self.assertIn("NL", fallback_areas)

    def test_build_features_for_area_derives_degrees_and_rolling_mean(self) -> None:
        source_rows = [
            (
                {"source_id": "a", "weight": 0.75, "fallback_proxy": False},
                {
                    "2022-06-01T00:00Z": {
                        "temperature_2m": 10.0,
                        "apparent_temperature": 9.0,
                        "wind_speed": 20.0,
                        "cloud_cover": 30.0,
                        "relative_humidity": 50.0,
                        "precipitation": 0.0,
                    },
                    "2022-06-01T01:00Z": {
                        "temperature_2m": 20.0,
                        "apparent_temperature": 19.0,
                        "wind_speed": 25.0,
                        "cloud_cover": 35.0,
                        "relative_humidity": 55.0,
                        "precipitation": 1.0,
                    },
                },
            ),
            (
                {"source_id": "b", "weight": 0.25, "fallback_proxy": False},
                {
                    "2022-06-01T00:00Z": {
                        "temperature_2m": 14.0,
                        "apparent_temperature": 13.0,
                        "wind_speed": 24.0,
                        "cloud_cover": 34.0,
                        "relative_humidity": 54.0,
                        "precipitation": 4.0,
                    },
                    "2022-06-01T01:00Z": {
                        "temperature_2m": 24.0,
                        "apparent_temperature": 23.0,
                        "wind_speed": 29.0,
                        "cloud_cover": 39.0,
                        "relative_humidity": 59.0,
                        "precipitation": 5.0,
                    },
                },
            ),
        ]

        rows = p0056b.build_features_for_area("TEST", source_rows)

        self.assertEqual(2, len(rows))
        self.assertAlmostEqual(11.0, rows[0]["temperature_2m"])
        self.assertAlmostEqual(6.0, rows[0]["heating_degree_proxy"])
        self.assertAlmostEqual(0.0, rows[0]["cooling_degree_proxy"])
        self.assertAlmostEqual(21.0, rows[1]["temperature_2m"])
        self.assertAlmostEqual(0.0, rows[1]["heating_degree_proxy"])
        self.assertAlmostEqual(0.0, rows[1]["cooling_degree_proxy"])
        self.assertAlmostEqual(16.0, rows[1]["temperature_2m_roll_mean_24h"])
        self.assertIn("snow_depth_unavailable", rows[0]["missingness_flags"])


if __name__ == "__main__":
    unittest.main()
