import json
import unittest

from src.mac.services.spotprice_history.source import parse_price_day


class SourceParserTests(unittest.TestCase):
    def test_parses_hourly_elprisetjustnu_payload(self):
        payload = [
            {
                "SEK_per_kWh": 1.0,
                "EUR_per_kWh": 0.1,
                "EXR": 10.0,
                "time_start": "2022-05-30T00:00:00+02:00",
                "time_end": "2022-05-30T01:00:00+02:00",
            },
            {
                "SEK_per_kWh": 2.0,
                "EUR_per_kWh": 0.2,
                "EXR": 10.0,
                "time_start": "2022-05-30T01:00:00+02:00",
                "time_end": "2022-05-30T02:00:00+02:00",
            },
        ]

        rows = parse_price_day(json.dumps(payload), "SE3", "fixture")

        self.assertEqual(2, len(rows))
        self.assertEqual("2022-05-29T22:00Z", rows[0].utc_hour_start)
        self.assertEqual(1, rows[0].samples)
        self.assertEqual("hour", rows[0].source_resolution)

    def test_aggregates_quarter_hour_payload(self):
        payload = [
            {
                "SEK_per_kWh": value,
                "EUR_per_kWh": value / 10,
                "EXR": 10.0,
                "time_start": f"2026-05-29T00:{minute:02d}:00+02:00",
                "time_end": f"2026-05-29T00:{minute + 15:02d}:00+02:00" if minute < 45 else "2026-05-29T01:00:00+02:00",
            }
            for minute, value in ((0, 1.0), (15, 2.0), (30, 3.0), (45, 4.0))
        ]

        rows = parse_price_day(json.dumps(payload), "SE3", "fixture")

        self.assertEqual(1, len(rows))
        self.assertEqual(2.5, rows[0].price_sek_per_kwh)
        self.assertEqual(4, rows[0].samples)
        self.assertEqual("quarter-hour", rows[0].source_resolution)


if __name__ == "__main__":
    unittest.main()
