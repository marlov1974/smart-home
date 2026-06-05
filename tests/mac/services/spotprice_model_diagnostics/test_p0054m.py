import unittest

from src.mac.services.spotprice_model_diagnostics import p0054m


class P0054MTests(unittest.TestCase):
    def test_feature_contract_keeps_no_price_clean(self) -> None:
        contract = p0054m.p0054m_feature_contract()

        self.assertIn(p0054m.VARIANT_NO_PRICE, contract)
        self.assertIn(p0054m.VARIANT_WITH_ADVANCED, contract)
        self.assertTrue(p0054m.validate_feature_contract(contract)["ok"])
        self.assertFalse(any("price" in feature for feature in contract[p0054m.VARIANT_NO_PRICE]["features"]))

    def test_matrix_safety_rejects_holdout_protocol_in_train_rows(self) -> None:
        row = {
            "forecast_origin_timestamp_utc": "2025-03-02T00:00:00Z",
            "input_data_cutoff_utc": "2025-03-01T23:00:00Z",
            "target_timestamp_utc": "2025-03-02T01:00:00Z",
            "price_feature_protocol": "p0054l2_holdout_safe_ensemble",
        }

        review = p0054m.validate_p0054m_matrix_safety([row], p0054m.p0054m_feature_contract())

        self.assertFalse(review["ok"])
        self.assertFalse(review["train_protocol_ok"])

    def test_ablation_positive_improvement_convention(self) -> None:
        model_results = {
            "HGB_no_price": {"metrics": {"holdout": {"MAE": 100.0}}},
            "HGB_with_p0054l2_ensemble_price_forecast": {"metrics": {"holdout": {"MAE": 90.0}}},
        }
        weekly = {
            "pred_HGB_no_price": {"MAE_full_168h": 100.0},
            "pred_HGB_with_p0054l2_ensemble_price_forecast": {"MAE_full_168h": 95.0},
        }

        result = p0054m.compare_advanced_price_ablation(model_results, weekly, {})

        self.assertEqual(-10.0, result["per_model_family"][0]["holdout_relative_change_percent"])
        self.assertTrue(result["per_model_family"][0]["advanced_price_helped_holdout"])


if __name__ == "__main__":
    unittest.main()
