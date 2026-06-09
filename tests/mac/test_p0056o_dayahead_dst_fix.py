from __future__ import annotations

from datetime import date, datetime, time as dt_time, timedelta
import unittest

from src.mac.services.spotprice_model_diagnostics import p0052, p0056k, p0056n


class P0056ODayAheadDstFixTests(unittest.TestCase):
    def test_spring_forward_day_has_23_unique_utc_rows_and_no_local_02(self) -> None:
        rows = p0056k.delivery_day_target_rows(date(2026, 3, 29))
        timestamps = [row.target_timestamp_utc for row in rows]
        self.assertEqual(len(rows), 23)
        self.assertEqual(len(set(timestamps)), 23)
        self.assertEqual(timestamps, sorted(timestamps))
        self.assertNotIn(2, {row.local_hour for row in rows})
        self.assertTrue(all(row.is_dst_transition_day for row in rows))
        self.assertTrue(all(row.is_spring_forward_day for row in rows))
        self.assertFalse(any(row.is_fall_back_day for row in rows))

    def test_2025_fall_back_day_has_25_unique_utc_rows_and_repeated_local_02(self) -> None:
        self.assert_fall_back_day(date(2025, 10, 26))

    def test_2026_fall_back_day_has_25_unique_utc_rows_and_repeated_local_02(self) -> None:
        self.assert_fall_back_day(date(2026, 10, 25))

    def test_standard_day_has_24_rows(self) -> None:
        rows = p0056k.delivery_day_target_rows(date(2026, 3, 28))
        timestamps = [row.target_timestamp_utc for row in rows]
        self.assertEqual(len(rows), 24)
        self.assertEqual(len(set(timestamps)), 24)
        self.assertFalse(any(row.is_dst_transition_day for row in rows))
        self.assertEqual({row.local_hour_occurrence_index for row in rows}, {0})

    def test_old_spring_forward_bug_condition_is_fixed(self) -> None:
        old_targets = p0056n.legacy_fixed_24_delivery_day_target_utc_hours(date(2026, 3, 29))
        new_targets = p0056k.delivery_day_target_utc_hours(date(2026, 3, 29))
        self.assertEqual(len(old_targets), 24)
        self.assertEqual(len(set(old_targets)), 23)
        self.assertEqual(len(new_targets), 23)
        self.assertEqual(len(set(new_targets)), 23)

    def test_build_dayahead_rows_include_required_dst_schema(self) -> None:
        delivery_day = date(2026, 3, 29)
        origin_local = datetime.combine(date(2026, 3, 28), dt_time(12, 0), tzinfo=p0056k.STOCKHOLM)
        origin = p0056k.Origin(origin_local, p0052.format_utc(origin_local), delivery_day)
        origin_utc = p0052.parse_utc(origin.origin_utc)
        start_utc = origin_utc - timedelta(hours=360)
        end_utc = p0052.parse_utc(p0056k.delivery_day_target_utc_hours(delivery_day)[-1]) + timedelta(hours=1)
        target_rows = []
        current = start_utc
        while current < end_utc:
            target_rows.append({"timestamp_utc": p0052.format_utc(current), "consumption_mw": 1000.0})
            current += timedelta(hours=1)
        weather_rows = {target: {} for target in p0056k.delivery_day_target_utc_hours(delivery_day)}

        rows = p0056k.build_dayahead_rows("SE2", target_rows, weather_rows, [origin])

        self.assertEqual(len(rows), 23)
        self.assertEqual(len({row["target_timestamp_utc"] for row in rows}), 23)
        self.assertFalse(any(row["local_hour"] == 2 for row in rows))
        required = {
            "forecast_origin_utc",
            "forecast_origin_local",
            "delivery_date_local",
            "target_timestamp_utc",
            "target_timestamp_local",
            "local_date",
            "local_hour",
            "utc_offset_minutes",
            "is_dst_transition_day",
            "is_spring_forward_day",
            "is_fall_back_day",
            "local_hour_occurrence_index",
            "horizon_h",
        }
        self.assertTrue(required <= set(rows[0]))

    def assert_fall_back_day(self, local_day: date) -> None:
        rows = p0056k.delivery_day_target_rows(local_day)
        timestamps = [row.target_timestamp_utc for row in rows]
        repeated = [row for row in rows if row.local_hour == 2]
        self.assertEqual(len(rows), 25)
        self.assertEqual(len(set(timestamps)), 25)
        self.assertEqual(timestamps, sorted(timestamps))
        self.assertEqual(len(repeated), 2)
        self.assertEqual({row.utc_offset_minutes for row in repeated}, {60, 120})
        self.assertEqual([row.local_hour_occurrence_index for row in repeated], [0, 1])
        self.assertTrue(all(row.is_dst_transition_day for row in rows))
        self.assertFalse(any(row.is_spring_forward_day for row in rows))
        self.assertTrue(all(row.is_fall_back_day for row in rows))


if __name__ == "__main__":
    unittest.main()
