import unittest

from src.mac.services.spotprice_model_diagnostics import p0054r, p0055a


class P0055ATests(unittest.TestCase):
    def test_cluster_weather_mapping_keeps_expected_zone(self):
        self.assertEqual("SE3_WEST_COAST_GOTHENBURG", p0055a.CLUSTER_WEATHER_ZONE["C24"])
        self.assertEqual("SE3_NORTHERN_INLAND", p0055a.CLUSTER_WEATHER_ZONE["C33"])

    def test_zero_forecast_sets_all_predictions_to_zero(self):
        rows = [{"target_timestamp_utc": "2025-06-01T00:00:00Z"}, {"target_timestamp_utc": "2025-06-01T01:00:00Z"}]
        evidence = p0055a.apply_zero_forecast(rows, "pred")
        self.assertEqual("F0_zero_forecast", evidence["method"])
        self.assertEqual([0.0, 0.0], [row["pred"] for row in rows])

    def test_aggregate_decomposition_sums_components(self):
        direct_rows = [
            {
                "forecast_origin_timestamp_utc": "2025-06-01T10:00:00Z",
                "target_timestamp_utc": "2025-06-01T12:00:00Z",
                "target_consumption_se3_mw": 15.0,
                p0055a.PREDICTION_COLUMN: 14.0,
            }
        ]
        component_results = {p0055a.DIRECT_COMPONENT: {"rows": direct_rows}}
        for index, component_id in enumerate(p0055a.ZERO_COMPONENT_IDS):
            component_results[component_id] = {
                "rows": [
                    {
                        "forecast_origin_timestamp_utc": "2025-06-01T10:00:00Z",
                        "target_timestamp_utc": "2025-06-01T12:00:00Z",
                        "target_consumption_se3_mw": 0.0,
                        p0055a.PREDICTION_COLUMN: 1.0 if index == 0 else 0.0,
                    }
                ]
            }
        component_results[p0055a.RESIDUAL_COMPONENT] = {
            "rows": [
                {
                    "forecast_origin_timestamp_utc": "2025-06-01T10:00:00Z",
                    "target_timestamp_utc": "2025-06-01T12:00:00Z",
                    "target_consumption_se3_mw": 14.0,
                    p0055a.PREDICTION_COLUMN: 13.0,
                }
            ]
        }
        rows = p0055a.aggregate_decomposition_rows(component_results, direct_rows)
        self.assertEqual(1, len(rows))
        self.assertEqual(14.0, rows[0][p0055a.DECOMPOSITION_PREDICTION_COLUMN])

    def test_reconciliation_uses_internal_validation_only(self):
        rows = [
            {
                p0054r.INTERNAL_SPLIT_FIELD: "internal_validation",
                "target_consumption_se3_mw": 100.0,
                p0055a.DIRECT_PREDICTION_COLUMN: 100.0,
                p0055a.DECOMPOSITION_PREDICTION_COLUMN: 80.0,
            },
            {
                p0054r.INTERNAL_SPLIT_FIELD: "internal_validation",
                "target_consumption_se3_mw": 120.0,
                p0055a.DIRECT_PREDICTION_COLUMN: 120.0,
                p0055a.DECOMPOSITION_PREDICTION_COLUMN: 80.0,
            },
            {
                p0054r.INTERNAL_SPLIT_FIELD: "not_train_fit",
                "target_consumption_se3_mw": 1000.0,
                p0055a.DIRECT_PREDICTION_COLUMN: 0.0,
                p0055a.DECOMPOSITION_PREDICTION_COLUMN: 1000.0,
            },
        ]
        evidence = p0055a.learn_reconciliation_weights(rows)
        self.assertEqual(2, evidence["internal_validation_rows"])
        self.assertFalse(evidence["holdout_used_for_weights_or_bias"])
        self.assertEqual(1.0, evidence["weights"]["direct"])

    def test_leakage_review_rejects_forbidden_features(self):
        review = p0055a.validate_p0055a_leakage(
            ["target_hour", "spot_price"],
            {},
            {"holdout_used_for_weights_or_bias": False},
            {"ok": True},
        )
        self.assertFalse(review["ok"])
        self.assertEqual(["spot_price"], review["forbidden_features"])


if __name__ == "__main__":
    unittest.main()
