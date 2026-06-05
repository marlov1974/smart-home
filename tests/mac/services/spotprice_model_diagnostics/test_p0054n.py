import unittest
from datetime import date

from src.mac.services.spotprice_model_diagnostics import p0054k, p0054n


class P0054NTests(unittest.TestCase):
    def test_dayahead_origin_uses_stockholm_dst(self) -> None:
        self.assertEqual("2025-06-01T10:00:00Z", p0054n.dayahead_origin_utc_for_delivery_day(date(2025, 6, 2)))
        self.assertEqual("2025-12-01T11:00:00Z", p0054n.dayahead_origin_utc_for_delivery_day(date(2025, 12, 2)))

    def test_delivery_day_target_hours_are_local_day(self) -> None:
        hours = p0054n.delivery_day_target_utc_hours(date(2025, 6, 2))

        self.assertEqual(24, len(hours))
        self.assertEqual("2025-06-01T22:00:00Z", hours[0])
        self.assertEqual("2025-06-02T21:00:00Z", hours[-1])

    def test_full_36h_requires_complete_holdout_origin(self) -> None:
        rows = []
        for horizon in range(1, 37):
            rows.append(
                {
                    "forecast_origin_timestamp_utc": "2025-06-01T10:00:00Z",
                    "target_timestamp_utc": f"2025-06-02T{horizon % 24:02d}:00:00Z",
                    "horizon_h": horizon,
                    "split": "holdout",
                    p0054k.TARGET_FIELD: 100.0,
                    "pred_model": 101.0,
                }
            )
        rows.append(
            {
                "forecast_origin_timestamp_utc": "2025-06-02T10:00:00Z",
                "target_timestamp_utc": "2025-06-03T00:00:00Z",
                "horizon_h": 1,
                "split": "holdout",
                p0054k.TARGET_FIELD: 100.0,
                "pred_model": 101.0,
            }
        )

        summary, compact = p0054n.evaluate_full_36h_paths(rows, ("pred_model",))

        self.assertEqual(1, summary["complete_origin_count"])
        self.assertEqual(36, summary["target_row_count"])
        self.assertEqual(1, len(compact))

    def test_matrix_safety_rejects_holdout_protocol_in_train_rows(self) -> None:
        review = p0054n.validate_p0054n_matrix_safety(
            [
                {
                    "forecast_origin_timestamp_utc": "2025-03-01T11:00:00Z",
                    "input_data_cutoff_utc": "2025-03-01T10:00:00Z",
                    "target_timestamp_utc": "2025-03-01T11:00:00Z",
                    "price_feature_protocol": "p0054l2_holdout_safe_ensemble",
                }
            ],
            p0054n.p0054n_feature_contract(),
        )

        self.assertFalse(review["ok"])
        self.assertFalse(review["train_protocol_ok"])

    def test_ablation_positive_improvement_convention(self) -> None:
        model_results = {
            "HGB_no_price": {"metrics": {"holdout": {"MAE": 100.0}}},
            "HGB_with_p0054n_exact_dayahead_advanced_price": {"metrics": {"holdout": {"MAE": 90.0}}},
        }
        full36 = {
            "pred_HGB_no_price": {"MAE_full_36h": 100.0},
            "pred_HGB_with_p0054n_exact_dayahead_advanced_price": {"MAE_full_36h": 90.0},
        }
        dayahead = {
            "pred_HGB_no_price": {"hourly_MAE_delivery_day": 100.0},
            "pred_HGB_with_p0054n_exact_dayahead_advanced_price": {"hourly_MAE_delivery_day": 95.0},
        }

        result = p0054n.compare_advanced_price_ablation_36h(model_results, full36, dayahead)

        self.assertEqual(-10.0, result["per_model_family"][0]["full36_relative_change_percent"])
        self.assertTrue(result["per_model_family"][0]["advanced_price_helped_full36"])


if __name__ == "__main__":
    unittest.main()
