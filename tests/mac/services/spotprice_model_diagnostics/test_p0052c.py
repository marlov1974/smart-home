import unittest

from src.mac.services.spotprice_model_diagnostics import p0052c


class P0052CTests(unittest.TestCase):
    def test_safe_ratio_handles_missing_and_invalid_capacity(self):
        self.assertEqual(p0052c.safe_ratio(10, None), (None, "missing_capacity"))
        self.assertEqual(p0052c.safe_ratio(10, 0), (None, "invalid_capacity"))
        self.assertEqual(p0052c.safe_ratio(-10, 20), (0.5, "ok"))

    def test_flow_based_era_boundary(self):
        self.assertEqual(p0052c.flow_based_era("2024-10-28T23:00:00Z"), "pre_flow_based")
        self.assertEqual(p0052c.flow_based_era("2024-10-29T00:00:00Z"), "post_flow_based")

    def test_ratio_metrics_counts_violations(self):
        observations = [
            {"window_id": "w", "era": "post_flow_based", "contract_type": "A02", "border_direction": "SE1->SE2", "comparison_type": "scheduled_exchange", "ratio": 0.5},
            {"window_id": "w", "era": "post_flow_based", "contract_type": "A02", "border_direction": "SE1->SE2", "comparison_type": "scheduled_exchange", "ratio": 1.06},
        ]
        metrics = p0052c.ratio_metrics(observations, {})
        self.assertEqual(metrics[0]["count_compared"], 2)
        self.assertEqual(metrics[0]["count_ratio_gt_1_05"], 1)
        self.assertEqual(metrics[0]["max_ratio"], 1.06)

    def test_classification_detects_exchange_exceeds(self):
        row = {
            "window_id": "w",
            "era": "post_flow_based",
            "contract_type": "A02",
            "border_direction": "SE1->SE2",
            "comparison_type": "scheduled_exchange",
            "count_compared": 24,
            "max_ratio": 1.20,
            "count_ratio_gt_1_05": 1,
        }
        physical = dict(row, comparison_type="physical_flow", max_ratio=0.8, count_ratio_gt_1_05=0)
        result = p0052c.classify_contract_types([row, physical])
        self.assertEqual(result["A02"]["market_classification"], "not_capacity_ceiling_exchange_exceeds")
        self.assertEqual(result["A02"]["recommendation"], "keep_blocked")

    def test_worst_examples_have_no_request_or_token_fields(self):
        observations = [
            {
                "timestamp_utc": "2025-01-01T00:00:00Z",
                "from_area": "SE1",
                "to_area": "SE2",
                "contract_type": "A02",
                "comparison_type": "scheduled_exchange",
                "capacity_mw": 100.0,
                "flow_or_exchange_mw": 110.0,
                "ratio": 1.1,
                "capacity_source_dataset": "A61",
                "flow_source_dataset": "A09",
                "window_id": "w",
                "era": "post_flow_based",
                "securityToken": "bad",
            }
        ]
        worst = p0052c.worst_ratio_examples(observations)
        self.assertNotIn("securityToken", worst[0])


if __name__ == "__main__":
    unittest.main()
