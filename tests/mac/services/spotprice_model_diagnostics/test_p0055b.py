import unittest

from src.mac.services.spotprice_model_diagnostics import p0055a, p0055b


class P0055BTests(unittest.TestCase):
    def test_monotonicity_detects_readable_increase(self):
        rows = [("2024-01-01T00:00:00Z", 0.20), ("2024-02-01T00:00:00Z", 0.21), ("2024-03-01T00:00:00Z", 0.23)]
        metrics = p0055b.monotonicity_for_pairs(rows)
        self.assertGreater(metrics["monthly_share_slope"], 0.0)
        self.assertTrue(metrics["is_one_way_readable"])

    def test_fit_train_share_models_reference_uses_train_fit_only(self):
        monthly = [
            {"month_start_utc": "2025-04-01T00:00:00Z", "component_id": "C11", "component_type": "cluster", "observed_share": 0.2, "split": "train_fit"},
            {"month_start_utc": "2025-04-01T00:00:00Z", "component_id": p0055a.RESIDUAL_COMPONENT, "component_type": "residual", "observed_share": 0.8, "split": "train_fit"},
            {"month_start_utc": "2025-05-01T00:00:00Z", "component_id": "C11", "component_type": "cluster", "observed_share": 0.3, "split": "train_fit"},
            {"month_start_utc": "2025-05-01T00:00:00Z", "component_id": p0055a.RESIDUAL_COMPONENT, "component_type": "residual", "observed_share": 0.7, "split": "train_fit"},
            {"month_start_utc": "2025-06-01T00:00:00Z", "component_id": "C11", "component_type": "cluster", "observed_share": 0.9, "split": "holdout"},
            {"month_start_utc": "2025-06-01T00:00:00Z", "component_id": p0055a.RESIDUAL_COMPONENT, "component_type": "residual", "observed_share": 0.1, "split": "holdout"},
        ]
        model = p0055b.fit_train_share_models(monthly)
        self.assertEqual("2025-05-01T00:00:00Z", model["reference_month"])
        self.assertFalse(model["holdout_used_for_reference"])
        self.assertFalse(model["holdout_used_for_share_model"])

    def test_normalize_hourly_components_preserves_total(self):
        aligned = [
            {
                "timestamp_utc": "2025-04-01T00:00:00Z",
                "month_start_utc": "2025-04-01T00:00:00Z",
                "total_mw": 100.0,
                "components": {"C11": 20.0, p0055a.RESIDUAL_COMPONENT: 80.0},
            }
        ]
        model = {
            "method": "test",
            "reference_month": "2025-04-01T00:00:00Z",
            "reference_shares": {"C11": 0.5, p0055a.RESIDUAL_COMPONENT: 0.5},
            "monthly_rows": [
                {"month_start_utc": "2025-04-01T00:00:00Z", "component_id": "C11", "smoothed_share": 0.2},
                {"month_start_utc": "2025-04-01T00:00:00Z", "component_id": p0055a.RESIDUAL_COMPONENT, "smoothed_share": 0.8},
            ],
        }
        rows, validation = p0055b.normalize_hourly_components(aligned, model)
        self.assertTrue(validation["ok"])
        self.assertAlmostEqual(100.0, sum(row["normalized_consumption_mw"] for row in rows))

    def test_leakage_rejects_holdout_reference(self):
        review = p0055b.validate_p0055b_leakage(
            {"holdout_used_for_reference": True, "holdout_used_for_share_model": False},
            {"reconciliation": {"holdout_used_for_weights_or_bias": False}},
            {"ok": True},
        )
        self.assertFalse(review["ok"])


if __name__ == "__main__":
    unittest.main()
