from datetime import date, timedelta
import unittest

from src.mac.services.swedish_calendar.core import (
    all_saints_day,
    classify_special_day,
    easter_sunday,
    generate_calendar,
    midsummer_eve,
)


class SwedishCalendarTests(unittest.TestCase):
    def test_row_count_and_leap_days(self):
        rows = generate_calendar(2022, 2035)
        self.assertEqual(5113, len(rows))
        leap_days = {row["date"] for row in rows if row["is_leap_day"]}
        self.assertEqual({"2024-02-29", "2028-02-29", "2032-02-29"}, leap_days)

    def test_known_easter_dates_and_ascension(self):
        known = {2024: date(2024, 3, 31), 2025: date(2025, 4, 20), 2026: date(2026, 4, 5)}
        for year, expected in known.items():
            self.assertEqual(expected, easter_sunday(year))
            ascension = classify_special_day(expected + timedelta(days=39))
            self.assertEqual("ascension_day", ascension["special_day_name"])

    def test_friday_after_ascension_is_strong_bridge(self):
        row = classify_special_day(easter_sunday(2025) + timedelta(days=40))
        self.assertTrue(row["is_bridge_day"])
        self.assertEqual("strong", row["bridge_strength"])
        self.assertEqual("ascension_day", row["bridge_anchor"])

    def test_midsummer_and_all_saints(self):
        self.assertEqual(date(2025, 6, 20), midsummer_eve(2025))
        eve = classify_special_day(date(2025, 6, 20))
        day = classify_special_day(date(2025, 6, 21))
        self.assertEqual("midsummer_eve", eve["special_day_name"])
        self.assertEqual("midsummer_day", day["special_day_name"])
        self.assertTrue(day["is_major_social_holiday"])
        self.assertTrue(day["normal_weekday_override"])
        saints = all_saints_day(2025)
        self.assertEqual(5, saints.weekday())
        self.assertTrue(date(2025, 10, 31) <= saints <= date(2025, 11, 6))

    def test_christmas_period(self):
        row = classify_special_day(date(2025, 12, 24))
        self.assertEqual("christmas_eve", row["special_day_name"])
        self.assertTrue(row["is_major_social_holiday"])
        between = classify_special_day(date(2025, 12, 29))
        self.assertTrue(between["is_holiday_period_day"])
        self.assertEqual("christmas_new_year", between["period_name"])


if __name__ == "__main__":
    unittest.main()
