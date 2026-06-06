import unittest

from src.mac.services.spotprice_model_diagnostics import p0054r


class P0054RTests(unittest.TestCase):
    def test_assign_internal_validation_splits_uses_train_fit_only(self):
        rows = [
            {"split": "train_fit", "target_timestamp_utc": "2025-02-28T23:00:00Z"},
            {"split": "train_fit", "target_timestamp_utc": "2025-03-01T00:00:00Z"},
            {"split": "holdout", "target_timestamp_utc": "2025-06-01T00:00:00Z"},
        ]
        counts = p0054r.assign_internal_validation_splits(rows)
        self.assertEqual(counts, {"internal_train": 1, "internal_validation": 1, "not_train_fit": 1})
        self.assertEqual(rows[0][p0054r.INTERNAL_SPLIT_FIELD], "internal_train")
        self.assertEqual(rows[1][p0054r.INTERNAL_SPLIT_FIELD], "internal_validation")
        self.assertEqual(rows[2][p0054r.INTERNAL_SPLIT_FIELD], "not_train_fit")

    def test_learn_inverse_mae_weights_prefers_best_validation_model(self):
        rows = [
            {"target_consumption_se3_mw": 100.0, "pred_a": 100.0, "pred_b": 90.0},
            {"target_consumption_se3_mw": 200.0, "pred_a": 200.0, "pred_b": 180.0},
        ]
        weights, evidence = p0054r.learn_inverse_mae_weights(rows, ["a", "b"])
        self.assertGreater(weights["a"], weights["b"])
        self.assertAlmostEqual(sum(weights.values()), 1.0)
        self.assertFalse(evidence["holdout_used_for_weights"])

    def test_apply_weighted_and_median_ensemble(self):
        rows = [{"pred_a": 10.0, "pred_b": 20.0, "pred_c": 30.0}]
        weighted_count = p0054r.apply_weighted_ensemble(rows, {"a": 0.25, "b": 0.75}, "pred_weighted")
        median_count = p0054r.apply_median_ensemble(rows, ["a", "b", "c"], "pred_median")
        self.assertEqual(weighted_count, 1)
        self.assertEqual(median_count, 1)
        self.assertEqual(rows[0]["pred_weighted"], 17.5)
        self.assertEqual(rows[0]["pred_median"], 20.0)

    def test_validate_p0054r_leakage_rejects_forbidden_feature(self):
        review = p0054r.validate_p0054r_leakage(
            {"ok": True},
            {"ok": True},
            {"ok": True, "source_table": "entsoe_consumption_area_hourly_v1"},
            {"no_price": {"features": ["target_hour", "a61_capacity"]}},
            [{"status": "advanced_completed"}],
        )
        self.assertFalse(review["ok"])


if __name__ == "__main__":
    unittest.main()
