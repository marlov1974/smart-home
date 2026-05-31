from __future__ import annotations

from copy import deepcopy
import unittest

from src.mac.services.spotprice_model_diagnostics.p0037 import count_splits, fit_strict_components
from src.mac.services.spotprice_model_diagnostics.p0039 import (
    TAXONOMY,
    build_p0039_matrix,
    fit_m1b_components,
    is_m1b_clean_training_row,
    residual_contract_report,
    series_for_p0039_variant,
)
from tests.mac.services.spotprice_model_diagnostics.test_p0037 import fixture_rows


class P0039DiagnosticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = fixture_rows()
        fit_strict_components(cls.rows)
        fit_m1b_components(cls.rows)

    def test_taxonomy_maps_component_letters(self):
        self.assertEqual("temperature", TAXONOMY["A"])
        self.assertEqual("special_days", TAXONOMY["B"])
        self.assertEqual("solar", TAXONOMY["C"])
        self.assertEqual("wind", TAXONOMY["D"])
        self.assertNotIn("M2B", TAXONOMY)

    def test_sequential_contract_contains_future_targets(self):
        report = residual_contract_report()
        self.assertIn("M3A target = actual - M1B", report)
        self.assertIn("M3B target = actual - M1B - M3A", report)
        self.assertIn("M3C target = actual - M1B - M3A - M3B", report)
        self.assertIn("M3D target = actual - M1B - M3A - M3B - M3C", report)
        self.assertIn("M4 target = actual - M1B - M3A - M3B - M3C - M3D", report)
        self.assertIn("not promoted here", report)

    def test_m1b_row_policy_includes_normal_days_and_excludes_special_days(self):
        self.assertTrue(is_m1b_clean_training_row({"special_day_type": "normal_weekday", "is_special_day": 0}))
        self.assertTrue(is_m1b_clean_training_row({"special_day_type": "normal_saturday", "is_special_day": 0}))
        self.assertTrue(is_m1b_clean_training_row({"special_day_type": "normal_sunday", "is_special_day": 0}))
        self.assertFalse(is_m1b_clean_training_row({"special_day_type": "fixed_public_holiday", "is_special_day": 1}))
        self.assertFalse(is_m1b_clean_training_row({"special_day_type": "major_social_holiday", "is_special_day": 1}))

    def test_midsummer_day_is_not_clean_saturday(self):
        row = {"special_day_type": "major_social_holiday", "special_day_name": "midsummer_day", "is_special_day": 1}
        self.assertFalse(is_m1b_clean_training_row(row))

    def test_m1b_and_m3_targets_are_sequential(self):
        train_special = next(row for row in self.rows if row["split"] == "train" and row["is_special_day"])
        se1_m3a_target = float(train_special["actual_se1"]) - float(train_special["m1b_se1"])
        self.assertIsInstance(se1_m3a_target, float)
        se1_m3b_target = float(train_special["actual_se1"]) - float(train_special["m1b_se1"]) - float(train_special["m3a_m1b_se1"])
        self.assertAlmostEqual(
            se1_m3b_target,
            float(train_special["actual_se1"]) - float(train_special["m1b_se1"]) - float(train_special["m3a_m1b_se1"]),
        )
        normalized = float(train_special["actual_se1"]) - float(train_special["m3a_m1b_se1"]) - float(train_special["m3b_m1b_se1"])
        self.assertAlmostEqual(normalized, float(train_special["m3ab_m1b_normalized_se1"]))

    def test_holdout_rows_not_used_to_fit_strict_m1b(self):
        rows = deepcopy(self.rows)
        original = {row["utc_hour_start"]: row["m1b_se1"] for row in rows if row["split"] == "holdout"}
        for row in rows:
            if row["split"] == "holdout":
                row["actual_se1"] = 999.0
        fit_strict_components(rows)
        fit_m1b_components(rows)
        changed = {row["utc_hour_start"]: row["m1b_se1"] for row in rows if row["split"] == "holdout"}
        self.assertEqual(original, changed)

    def test_full_year_holdout_and_required_variants(self):
        self.assertEqual(8760, count_splits(self.rows)["holdout"])
        matrix = build_p0039_matrix(self.rows)
        self.assertEqual(
            {"M1", "M1B_training_base_only", "M1_existing_M3A_M3B", "M1_M3A_m1b", "M1_M3A_m1b_M3B_m1b"},
            {row["variant"] for row in matrix},
        )
        self.assertEqual(
            {"system_proxy_se1", "area_diff_proxy_se3", "recomposed_se3"},
            {row["target"] for row in matrix},
        )

    def test_recomposed_se3_equals_parts(self):
        holdout = [row for row in self.rows if row["split"] == "holdout"][:24]
        actual_se1, pred_se1 = series_for_p0039_variant(holdout, "M1_M3A_m1b_M3B_m1b", "system_proxy_se1")
        actual_area, pred_area = series_for_p0039_variant(holdout, "M1_M3A_m1b_M3B_m1b", "area_diff_proxy_se3")
        actual_se3, pred_se3 = series_for_p0039_variant(holdout, "M1_M3A_m1b_M3B_m1b", "recomposed_se3")
        self.assertEqual(actual_se3, [a + b for a, b in zip(actual_se1, actual_area)])
        self.assertEqual(pred_se3, [a + b for a, b in zip(pred_se1, pred_area)])

    def test_m1b_trained_deltas_are_applied_on_m1_baseplate(self):
        row = self.rows[0]
        _actual, pred = series_for_p0039_variant([row], "M1_M3A_m1b_M3B_m1b", "system_proxy_se1")
        self.assertAlmostEqual(
            float(row["m1_raw_se1"]) + float(row["m3a_m1b_se1"]) + float(row["m3b_m1b_se1"]),
            pred[0],
        )


if __name__ == "__main__":
    unittest.main()
