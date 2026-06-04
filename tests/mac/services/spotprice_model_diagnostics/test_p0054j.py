import unittest

from src.mac.services.spotprice_model_diagnostics import p0054j


class P0054JTests(unittest.TestCase):
    def test_p0054i_split_boundaries(self):
        self.assertEqual("outside", p0054j.p0054i_split("2022-05-31T23:00:00Z"))
        self.assertEqual("train_fit", p0054j.p0054i_split("2022-06-01T00:00:00Z"))
        self.assertEqual("train_fit", p0054j.p0054i_split("2025-05-31T23:00:00Z"))
        self.assertEqual("holdout", p0054j.p0054i_split("2025-06-01T00:00:00Z"))

    def test_price_path_features_are_origin_path_only(self):
        rows = [
            {"horizon_h": 1, "predicted_price": 10.0},
            {"horizon_h": 2, "predicted_price": 20.0},
            {"horizon_h": 3, "predicted_price": 30.0},
        ]
        features = p0054j.price_path_features(rows)

        self.assertEqual(10.0, features[1]["price_forecast_horizon_value"])
        self.assertEqual(20.0, features[2]["price_forecast_horizon_value"])
        self.assertEqual(20.0, features[3]["price_forecast_0_168h_mean"])
        self.assertEqual(10.0, features[2]["price_forecast_ramp_from_previous_horizon"])

    def test_feature_contract_forbidden_terms(self):
        review = p0054j.validate_feature_contract(p0054j.feature_group_contract())
        self.assertTrue(review["ok"], review)

    def test_validate_paired_row_sets_detects_mismatch(self):
        rows = [
            {
                "forecast_origin_timestamp_utc": "2025-06-01T23:00:00Z",
                "target_timestamp_utc": "2025-06-02T00:00:00Z",
                "horizon_h": 1,
                "pred_HGB_no_price": 1.0,
            },
            {
                "forecast_origin_timestamp_utc": "2025-06-01T23:00:00Z",
                "target_timestamp_utc": "2025-06-02T01:00:00Z",
                "horizon_h": 2,
                "pred_HGB_with_p0054h_price_forecast": 1.0,
            },
        ]
        review = p0054j.validate_paired_row_sets(rows, {"HGB_no_price": {}, "HGB_with_p0054h_price_forecast": {}})

        self.assertFalse(review["ok"])


if __name__ == "__main__":
    unittest.main()
