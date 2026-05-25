import unittest

from src.mac.services.spot_forecast.model import (
    HistoricalWeek,
    WeekNotFoundError,
    forecast_period_indexes,
    normalize_indexes,
    week_weight,
    weighted_average_indexes,
)


def record(week, values):
    return HistoricalWeek(iso_year=2025, iso_week=week, price_index=tuple(values))


class WeekWeightModelTests(unittest.TestCase):
    def test_week_weight_table(self):
        self.assertEqual(1.0, week_weight(0))
        self.assertEqual(0.7, week_weight(1))
        self.assertEqual(0.4, week_weight(2))
        self.assertEqual(0.0, week_weight(3))

    def test_weighted_average_uses_only_distance_two_or_less(self):
        history = [
            record(10, [10.0] * 21),
            record(11, [20.0] * 21),
            record(12, [40.0] * 21),
            record(13, [1000.0] * 21),
        ]

        averaged = weighted_average_indexes(10, history)

        expected = ((10.0 * 1.0) + (20.0 * 0.7) + (40.0 * 0.4)) / (1.0 + 0.7 + 0.4)
        self.assertEqual([expected] * 21, averaged)

    def test_normalization_mean_is_one_before_rounding(self):
        normalized = normalize_indexes([1.0, 2.0, 3.0] * 7)

        self.assertAlmostEqual(1.0, sum(normalized) / 21)

    def test_forecast_returns_rounded_twenty_one_values(self):
        history = [record(2, [1.004, 1.115, 0.881] * 7)]

        forecast = forecast_period_indexes(2, history)

        self.assertEqual(21, len(forecast))
        self.assertEqual([round(value, 2) for value in forecast], forecast)

    def test_missing_model_data_raises_week_not_found(self):
        with self.assertRaises(WeekNotFoundError):
            forecast_period_indexes(25, [record(2, [1.0] * 21)])


if __name__ == "__main__":
    unittest.main()

