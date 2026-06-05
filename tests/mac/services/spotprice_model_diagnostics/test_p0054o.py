import unittest

from src.mac.services.spotprice_model_diagnostics import p0054k, p0054n, p0054o


class P0054OTests(unittest.TestCase):
    def test_temperature_feature_selection_uses_source_temperature_columns(self) -> None:
        discovery = p0054o.temperature_feature_columns(p0054n.p0054n_feature_contract())

        self.assertIn("weather_proxy_temperature_2m_se3", discovery["selected_for_noise"])
        self.assertIn("weather_proxy_apparent_temperature_se3", discovery["selected_for_noise"])
        self.assertIn("weather_proxy_temperature_delta_from_train_normal_se3", discovery["derived_recomputed_after_noise"])

    def test_temperature_noise_is_deterministic_and_bounded(self) -> None:
        rows = [
            {"weather_proxy_temperature_2m_se3": 10.0, "weather_proxy_apparent_temperature_se3": 9.0},
            {"weather_proxy_temperature_2m_se3": -2.0, "weather_proxy_apparent_temperature_se3": -4.0},
        ]

        left, left_audit = p0054o.apply_temperature_noise(rows, ["weather_proxy_temperature_2m_se3"], seed=1000, amplitude=2.0)
        right, right_audit = p0054o.apply_temperature_noise(rows, ["weather_proxy_temperature_2m_se3"], seed=1000, amplitude=2.0)

        self.assertEqual(left, right)
        self.assertEqual(left_audit["min_noise"], right_audit["min_noise"])
        for original, noisy in zip(rows, left):
            delta = noisy["weather_proxy_temperature_2m_se3"] - original["weather_proxy_temperature_2m_se3"]
            self.assertGreaterEqual(delta, -2.0)
            self.assertLessEqual(delta, 2.0)
            self.assertEqual(original["weather_proxy_apparent_temperature_se3"], noisy["weather_proxy_apparent_temperature_se3"])

    def test_daily_energy_error_percent(self) -> None:
        rows = [
            {"forecast_origin_timestamp_utc": "2025-06-01T10:00:00Z", p0054k.TARGET_FIELD: 100.0, "pred": 110.0},
            {"forecast_origin_timestamp_utc": "2025-06-01T10:00:00Z", p0054k.TARGET_FIELD: 100.0, "pred": 90.0},
            {"forecast_origin_timestamp_utc": "2025-06-02T10:00:00Z", p0054k.TARGET_FIELD: 200.0, "pred": 220.0},
        ]

        result = p0054o.daily_energy_error_percent(rows, "pred")

        self.assertAlmostEqual(10.0, result["absolute_daily_energy_error_MWh"])
        self.assertAlmostEqual(10.0, result["signed_daily_energy_error_MWh"])
        self.assertAlmostEqual(5.0, result["daily_energy_error_percent_of_actual"])


if __name__ == "__main__":
    unittest.main()
