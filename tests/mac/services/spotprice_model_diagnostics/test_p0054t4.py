import unittest

from src.mac.services.spotprice_model_diagnostics import p0054t4


class P0054T4Tests(unittest.TestCase):
    def test_temperature_feature_columns_excludes_derived_temperature_fields(self):
        rows = [{"weather_proxy_temperature_2m_se3": 1.0, "weather_proxy_train_normal_temperature_2m_se3": 2.0}]
        features = [
            "weather_proxy_temperature_2m_se3",
            "weather_proxy_apparent_temperature_se3",
            "weather_proxy_train_normal_temperature_2m_se3",
            "weather_proxy_temperature_delta_from_train_normal_se3",
            "weather_proxy_heating_degree_hours_se3",
        ]

        columns = p0054t4.temperature_feature_columns(rows, features)

        self.assertEqual(["weather_proxy_temperature_2m_se3"], columns)

    def test_apply_inference_temperature_noise_only_changes_holdout(self):
        rows = [
            {"split": "train_fit", "weather_proxy_temperature_2m_se3": 10.0},
            {"split": "holdout", "weather_proxy_temperature_2m_se3": 10.0},
        ]

        evidence = p0054t4.apply_inference_temperature_noise(rows, 1000, ["weather_proxy_temperature_2m_se3"], 2.0)

        self.assertEqual(10.0, rows[0]["weather_proxy_temperature_2m_se3"])
        self.assertNotEqual(10.0, rows[1]["weather_proxy_temperature_2m_se3"])
        self.assertFalse(evidence["train_fit_changed"])
        self.assertEqual(["holdout"], evidence["touched_splits"])
        self.assertTrue(evidence["bounds_ok"])

    def test_apply_fixed_horizon_bias_uses_existing_biases(self):
        rows = [{"horizon_h": 1, "weighted": 100.0}, {"horizon_h": 2, "weighted": 200.0}]

        applied = p0054t4.apply_fixed_horizon_bias(rows, {1: 10.0, 2: -5.0}, "weighted", "bias")

        self.assertEqual(2, applied)
        self.assertEqual(90.0, rows[0]["bias"])
        self.assertEqual(205.0, rows[1]["bias"])


if __name__ == "__main__":
    unittest.main()
