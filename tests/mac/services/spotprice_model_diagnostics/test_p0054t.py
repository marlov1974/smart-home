import unittest

from src.mac.services.spotprice_model_diagnostics import p0054t


class P0054TTests(unittest.TestCase):
    def test_temperature_noise_columns(self):
        rows = [{"weather_proxy_temperature_2m_se3": 1.0, "weather_proxy_apparent_temperature_se3": 2.0, "weather_proxy_wind_100m_se3": 3.0}]
        self.assertEqual(p0054t.temperature_noise_columns(rows), ["weather_proxy_apparent_temperature_se3", "weather_proxy_temperature_2m_se3"])

    def test_apply_temperature_noise_bounds(self):
        rows = [{"split": "train_fit", "weather_proxy_temperature_2m_se3": 10.0} for _ in range(20)]
        evidence = p0054t.apply_temperature_noise(rows, 1000, ["weather_proxy_temperature_2m_se3"])
        self.assertTrue(evidence["bounds_ok"])
        self.assertEqual(evidence["changed_values"], 20)
        self.assertTrue(all(8.0 <= row["weather_proxy_temperature_2m_se3"] <= 12.0 for row in rows))

    def test_aggregate_matrix_results_produces_seed_summary(self):
        rows = [
            {"model": "M", "weather_mode": "W1_tempNoise2C", "price_mode": "P0_noPrice", "seed": 1000, "hourly_MAE_delivery_day": 10.0, "hourly_MAE_percent_of_mean_actual": 1.0, "MAE_full_36h": 9.0, "absolute_daily_energy_error_MWh": 100.0, "daily_energy_error_percent_of_actual": 2.0},
            {"model": "M", "weather_mode": "W1_tempNoise2C", "price_mode": "P0_noPrice", "seed": 1001, "hourly_MAE_delivery_day": 12.0, "hourly_MAE_percent_of_mean_actual": 1.2, "MAE_full_36h": 11.0, "absolute_daily_energy_error_MWh": 120.0, "daily_energy_error_percent_of_actual": 2.4},
        ]
        summary = p0054t.aggregate_matrix_results(rows)
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["seed_count"], 2)
        self.assertEqual(summary[0]["hourly_MAE_delivery_day_mean"], 11.0)


if __name__ == "__main__":
    unittest.main()
