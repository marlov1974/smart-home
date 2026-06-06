from __future__ import annotations

import unittest

from src.mac.services.spotprice_model_diagnostics import p0054y2


class P0054Y2Test(unittest.TestCase):
    def test_cluster_id_for(self) -> None:
        self.assertEqual(
            p0054y2.cluster_id_for("EAST_COAST_MALARDALEN_STOCKHOLM", "BIG_CITY_APARTMENT_SERVICE"),
            "C11",
        )
        self.assertEqual(
            p0054y2.cluster_id_for("SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND", "RURAL_SPARSE_AGRICULTURE"),
            "C44",
        )

    def test_compute_residual_rows(self) -> None:
        cluster_rows = [
            {"timestamp_utc": "2025-01-01T00:00:00Z", "cluster_id": "C11", "cluster_label": "a", "consumption_mw": 10.0},
            {"timestamp_utc": "2025-01-01T00:00:00Z", "cluster_id": "C12", "cluster_label": "b", "consumption_mw": 15.0},
            {"timestamp_utc": "2025-01-01T01:00:00Z", "cluster_id": "C11", "cluster_label": "a", "consumption_mw": 20.0},
        ]
        residual, decomposition = p0054y2.compute_residual_rows(cluster_rows, {"2025-01-01T00:00:00Z": 100.0})
        self.assertEqual(len(residual), 1)
        self.assertEqual(residual[0]["residual_metered_non_profiled_mw"], 75.0)
        self.assertEqual(len(decomposition), 3)

    def test_quality_summary_negative_count(self) -> None:
        validation = p0054y2.build_validation_summary(
            [],
            [
                {
                    "timestamp_utc": "a",
                    "residual_metered_non_profiled_mw": 5.0,
                    "entsoe_total_consumption_mw": 10.0,
                    "profiled_cluster_sum_mw": 5.0,
                    "profiled_share_of_total": 0.5,
                    "residual_share_of_total": 0.5,
                },
                {
                    "timestamp_utc": "b",
                    "residual_metered_non_profiled_mw": -1.0,
                    "entsoe_total_consumption_mw": 10.0,
                    "profiled_cluster_sum_mw": 11.0,
                    "profiled_share_of_total": 1.1,
                    "residual_share_of_total": -0.1,
                },
            ],
            {},
        )
        self.assertEqual(validation["negative_residual_hours_count"], 1)
        self.assertEqual(validation["negative_residual_hours_examples"], ["b"])


if __name__ == "__main__":
    unittest.main()
