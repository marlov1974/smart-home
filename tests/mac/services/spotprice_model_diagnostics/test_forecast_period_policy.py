from __future__ import annotations

import unittest

from src.mac.services.spotprice_model_diagnostics.forecast_period_policy import (
    canonical_split_for_timestamp,
    is_modeling_target_timestamp,
    policy_summary,
)


class ForecastPeriodPolicyTests(unittest.TestCase):
    def test_canonical_split_boundaries(self):
        self.assertEqual(canonical_split_for_timestamp("2022-06-01T00:00:00Z"), "train")
        self.assertEqual(canonical_split_for_timestamp("2024-12-31T23:00:00Z"), "train")
        self.assertEqual(canonical_split_for_timestamp("2025-01-01T00:00:00Z"), "validate")
        self.assertEqual(canonical_split_for_timestamp("2025-05-31T23:00:00Z"), "validate")
        self.assertEqual(canonical_split_for_timestamp("2025-06-01T00:00:00Z"), "holdout")

    def test_pre_policy_targets_are_not_modeling_rows(self):
        self.assertFalse(is_modeling_target_timestamp("2022-05-31T23:00:00Z"))
        self.assertTrue(is_modeling_target_timestamp("2022-06-01T00:00:00Z"))
        with self.assertRaises(ValueError):
            canonical_split_for_timestamp("2022-05-31T23:00:00Z")

    def test_policy_summary_documents_timestamp_boundary_identity(self):
        summary = policy_summary()
        self.assertEqual(summary["boundary_identity"], "timestamp_utc")
        self.assertTrue(summary["context_only_lag_warmup"])


if __name__ == "__main__":
    unittest.main()
