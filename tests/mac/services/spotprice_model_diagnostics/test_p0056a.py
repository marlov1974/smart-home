import unittest

from src.mac.services.spotprice_model_diagnostics import p0056a


class P0056ATests(unittest.TestCase):
    def test_area_catalog_contains_all_primary_areas(self):
        areas = {row["area_code"] for row in p0056a.area_catalog()}
        self.assertEqual(set(p0056a.PRIMARY_AREAS), areas)
        self.assertIn("NO5", areas)
        self.assertIn("NL", areas)

    def test_yearly_chunks_split_on_year_boundary(self):
        chunks = p0056a.yearly_chunks(
            p0056a.datetime(2024, 12, 31, 22, tzinfo=p0056a.timezone.utc),
            p0056a.datetime(2025, 1, 1, 2, tzinfo=p0056a.timezone.utc),
        )
        self.assertEqual(2, len(chunks))
        self.assertEqual("2025-01-01T00:00:00+00:00", chunks[0][1].isoformat())

    def test_aggregate_native_to_hourly_time_weights_subhourly_rows(self):
        rows = [
            {
                "area_code": "SE3",
                "interval_start_utc": "2025-01-01T00:00:00Z",
                "interval_end_utc": "2025-01-01T00:15:00Z",
                "value": 100.0,
                "native_resolution_minutes": 15,
            },
            {
                "area_code": "SE3",
                "interval_start_utc": "2025-01-01T00:15:00Z",
                "interval_end_utc": "2025-01-01T01:00:00Z",
                "value": 300.0,
                "native_resolution_minutes": 45,
            },
        ]
        hourly = p0056a.aggregate_native_to_hourly(rows)
        self.assertEqual(1, len(hourly))
        self.assertAlmostEqual(250.0, hourly[0]["consumption_mw"])
        self.assertEqual("15+45", hourly[0]["native_resolution_mix"])
        self.assertEqual("ok", hourly[0]["coverage_flag"])

    def test_aggregate_native_to_hourly_marks_partial_hour(self):
        rows = [
            {
                "area_code": "SE3",
                "interval_start_utc": "2025-01-01T00:00:00Z",
                "interval_end_utc": "2025-01-01T00:30:00Z",
                "value": 100.0,
                "native_resolution_minutes": 30,
            }
        ]
        hourly = p0056a.aggregate_native_to_hourly(rows)
        self.assertEqual("partial_hour", hourly[0]["coverage_flag"])


if __name__ == "__main__":
    unittest.main()
