from __future__ import annotations

import unittest

from src.mac.services.spotprice_model_diagnostics import p0056d


class P0056DTests(unittest.TestCase):
    def test_zone_weights_sum_to_one_per_area(self) -> None:
        sums: dict[str, float] = {}
        for row in p0056d.zone_weights():
            sums[str(row["area_code"])] = sums.get(str(row["area_code"]), 0.0) + float(row["zone_weight"])

        self.assertEqual(set(p0056d.SCOPED_AREAS), set(sums))
        for value in sums.values():
            self.assertAlmostEqual(1.0, value, places=9)

    def test_representative_locations_cover_every_zone(self) -> None:
        zone_ids = {zone.zone_id for zone in p0056d.weather_zones()}
        location_zone_ids = {location.zone_id for location in p0056d.representative_locations()}

        self.assertEqual(zone_ids, location_zone_ids)
        self.assertTrue(all(location.area_code in p0056d.SCOPED_AREAS for location in p0056d.representative_locations()))

    def test_weighted_area_weather_is_deterministic(self) -> None:
        zone_means = {
            "A": {"temperature_2m": 0.0, "apparent_temperature": -1.0, "wind_speed": 10.0, "cloud_cover": 20.0, "relative_humidity": 70.0, "precipitation": 1.0, "snowfall": 0.1, "heating_degree_proxy": 17.0, "cooling_degree_proxy": 0.0},
            "B": {"temperature_2m": 10.0, "apparent_temperature": 9.0, "wind_speed": 20.0, "cloud_cover": 80.0, "relative_humidity": 90.0, "precipitation": 3.0, "snowfall": 0.0, "heating_degree_proxy": 7.0, "cooling_degree_proxy": 0.0},
        }

        result = p0056d.weighted_area_weather(zone_means, {"A": 0.25, "B": 0.75})

        self.assertAlmostEqual(7.5, float(result["temperature_2m"]))
        self.assertAlmostEqual(65.0, float(result["cloud_cover"]))
        self.assertIsNone(result["snow_depth"])

    def test_compare_against_p0056c_decision_rules(self) -> None:
        baseline = p00556_baseline_like("SE1", dayahead=100.0, full36=100.0, daily=10.0)

        self.assertTrue(p0056d.percent_improvement(baseline["DayAhead_hourly_MAE"], 97.9) >= 2.0)
        self.assertTrue(p0056d.percent_improvement(baseline["full_36h_MAE"], 97.9) >= 2.0)
        self.assertTrue(p0056d.percent_improvement(baseline["daily_energy_error_percent_of_actual"], 9.4) >= 5.0)

    def test_feature_names_exclude_forbidden_terms(self) -> None:
        forbidden = ("price", "spot", "flow", "exchange", "a61", "capacity", "physical_balance", "future_actual")
        contract = p0056d.openmeteo_contract(p0056d.START_DATE, p0056d.END_DATE)

        self.assertFalse([variable for variable in contract["variables"] if any(term in str(variable).lower() for term in forbidden)])
        self.assertIn("chunks", str(contract["batching"]))

    def test_fetch_chunks_cover_required_period_without_overlap(self) -> None:
        chunks = p0056d.fetch_chunks(p0056d.START_DATE, p0056d.END_DATE)

        self.assertEqual(p0056d.START_DATE, chunks[0][0])
        self.assertEqual(p0056d.END_DATE, chunks[-1][1])
        for index in range(1, len(chunks)):
            self.assertEqual(chunks[index - 1][1] + p0056d.timedelta(days=1), chunks[index][0])
        self.assertEqual(16, len(chunks))

    def test_compact_hour_z_matches_stored_openmeteo_timestamp_shape(self) -> None:
        value = p0056d.datetime(2022, 8, 31, 23, tzinfo=p0056d.timezone.utc)

        self.assertEqual("2022-08-31T23:00Z", p0056d.compact_hour_z(value))


def p00556_baseline_like(area: str, *, dayahead: float, full36: float, daily: float) -> dict[str, float | str]:
    return {
        "area_code": area,
        "DayAhead_hourly_MAE": dayahead,
        "full_36h_MAE": full36,
        "daily_energy_error_percent_of_actual": daily,
    }


if __name__ == "__main__":
    unittest.main()
