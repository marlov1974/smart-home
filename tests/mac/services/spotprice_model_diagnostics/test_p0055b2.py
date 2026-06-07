import unittest

from src.mac.services.spotprice_model_diagnostics import p0055a, p0055b2


class P0055B2Tests(unittest.TestCase):
    def test_pava_non_decreasing_flattens_backtrack(self):
        fitted = p0055b2.pava_non_decreasing([0.30, 0.20, 0.25, 0.40])
        self.assertEqual(len(fitted), 4)
        self.assertTrue(all(prev <= cur for prev, cur in zip(fitted, fitted[1:])))
        self.assertAlmostEqual(fitted[0], fitted[1])

    def test_cluster_delta_metrics_has_required_operator_fields(self):
        metrics = p0055b2.cluster_delta_metrics(
            [
                ("2025-01-01T00:00:00Z", 0.10),
                ("2025-02-01T00:00:00Z", 0.12),
                ("2025-03-01T00:00:00Z", 0.11),
            ]
        )
        for key in (
            "monthly_share_start",
            "monthly_share_end",
            "monthly_delta_series",
            "positive_delta_sum",
            "negative_delta_sum",
            "max_monthly_positive_delta",
            "max_monthly_negative_delta",
            "number_of_negative_delta_months",
            "number_of_zero_or_flat_months",
            "one_way_score",
            "is_monotone_enough",
        ):
            self.assertIn(key, metrics)
        self.assertEqual(1, metrics["number_of_negative_delta_months"])

    def test_fit_reference_window_uses_train_fit_only(self):
        monthly = []
        months = ["2025-03-01T00:00:00Z", "2025-04-01T00:00:00Z", "2025-05-01T00:00:00Z", "2025-06-01T00:00:00Z"]
        for month in months:
            split = "holdout" if month.startswith("2025-06") else "train_fit"
            monthly.append({"month_start_utc": month, "component_id": "C11", "component_type": "cluster", "observed_share": 0.2 if split == "train_fit" else 0.9, "total_mwh": 1000.0, "split": split})
            monthly.append({"month_start_utc": month, "component_id": p0055a.RESIDUAL_COMPONENT, "component_type": "residual", "observed_share": 0.8 if split == "train_fit" else 0.1, "total_mwh": 1000.0, "split": split})
            for cluster_id in p0055a.ZERO_COMPONENT_IDS:
                if cluster_id != "C11":
                    monthly.append({"month_start_utc": month, "component_id": cluster_id, "component_type": "cluster", "observed_share": 0.0, "total_mwh": 1000.0, "split": split})
        model = p0055b2.fit_cluster_specific_monotone_model(monthly)
        self.assertEqual(
            ["2025-03-01T00:00:00Z", "2025-04-01T00:00:00Z", "2025-05-01T00:00:00Z"],
            model["reference_months"],
        )
        self.assertFalse(model["holdout_used_for_reference"])
        self.assertFalse(model["holdout_used_for_share_model"])
        self.assertAlmostEqual(0.2, model["reference_shares"]["C11"])

    def test_fit_sets_holdout_smoothed_to_reference(self):
        monthly = []
        for month, split, share in [
            ("2025-04-01T00:00:00Z", "train_fit", 0.10),
            ("2025-05-01T00:00:00Z", "train_fit", 0.20),
            ("2025-06-01T00:00:00Z", "holdout", 0.90),
        ]:
            monthly.append({"month_start_utc": month, "component_id": "C11", "component_type": "cluster", "observed_share": share, "total_mwh": 1000.0, "split": split})
            monthly.append({"month_start_utc": month, "component_id": p0055a.RESIDUAL_COMPONENT, "component_type": "residual", "observed_share": 1.0 - share, "total_mwh": 1000.0, "split": split})
            for cluster_id in p0055a.ZERO_COMPONENT_IDS:
                if cluster_id != "C11":
                    monthly.append({"month_start_utc": month, "component_id": cluster_id, "component_type": "cluster", "observed_share": 0.0, "total_mwh": 1000.0, "split": split})
        model = p0055b2.fit_cluster_specific_monotone_model(monthly)
        holdout_c11 = [
            row
            for row in model["monthly_rows"]
            if row["month_start_utc"] == "2025-06-01T00:00:00Z" and row["component_id"] == "C11"
        ][0]
        self.assertAlmostEqual(model["reference_shares"]["C11"], holdout_c11["smoothed_share"])


if __name__ == "__main__":
    unittest.main()
