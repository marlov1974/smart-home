import unittest

from src.mac.services.spotprice_model_diagnostics import p0054l2, p0054s


class P0054STests(unittest.TestCase):
    def test_assign_internal_validation_splits(self):
        rows = [
            {"split": "train_fit", "target_timestamp_utc": "2025-02-28T23:00:00Z"},
            {"split": "train_fit", "target_timestamp_utc": "2025-03-01T00:00:00Z"},
            {"split": "holdout", "target_timestamp_utc": "2025-06-01T00:00:00Z"},
        ]
        counts = p0054s.assign_internal_validation_splits(rows)
        self.assertEqual(counts, {"internal_train": 1, "internal_validation": 1, "not_train_fit": 1})

    def test_inverse_mae_weights_use_validation_only(self):
        rows = [
            {"target_price": 10.0, p0054l2.prediction_column("A"): 10.0, p0054l2.prediction_column("B"): 20.0},
            {"target_price": 20.0, p0054l2.prediction_column("A"): 20.0, p0054l2.prediction_column("B"): 40.0},
        ]
        weights, evidence = p0054s.learn_inverse_mae_weights(rows, ["A", "B"])
        self.assertGreater(weights["A"], weights["B"])
        self.assertAlmostEqual(sum(weights.values()), 1.0)
        self.assertFalse(evidence["holdout_used_for_weights"])

    def test_weighted_and_median_ensemble(self):
        rows = [{p0054l2.prediction_column("A"): 10.0, p0054l2.prediction_column("B"): 20.0, p0054l2.prediction_column("C"): 30.0}]
        self.assertEqual(p0054s.apply_weighted_ensemble(rows, {"A": 0.25, "B": 0.75}, "weighted"), 1)
        self.assertEqual(p0054s.apply_median_ensemble(rows, ["A", "B", "C"], "median"), 1)
        self.assertEqual(rows[0]["weighted"], 17.5)
        self.assertEqual(rows[0]["median"], 20.0)

    def test_leakage_requires_advanced_method(self):
        review = p0054s.validate_p0054s_leakage({"ok": True}, [], {"decision": "none"})
        self.assertFalse(review["ok"])


if __name__ == "__main__":
    unittest.main()
