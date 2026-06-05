import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.mac.services.spotprice_model_diagnostics import p0052, p0054l2


class P0054L2Tests(unittest.TestCase):
    def test_price_history_features_use_sources_before_origin(self) -> None:
        origin = datetime(2025, 6, 1, 0, tzinfo=timezone.utc)
        target = origin + timedelta(hours=24)
        prices = {}
        meta = {}
        for offset in range(-400, 200):
            ts = origin + timedelta(hours=offset)
            key = p0052.format_utc(ts)
            prices[key] = 100.0 + offset
            meta[key] = {"model_cet_hour": (ts + timedelta(hours=1)).hour, "model_cet_weekday": (ts + timedelta(hours=1)).weekday()}

        features, audit = p0054l2.price_history_features_at_origin(origin, target, prices, meta, 24)

        self.assertIn("se3_price_previous_week_same_target_hour", features)
        for source_ts in audit.values():
            self.assertLess(p0052.parse_utc(source_ts), origin)

    def test_feature_matrix_safety_rejects_forbidden_feature_names(self) -> None:
        row = {
            "forecast_origin_timestamp_utc": "2025-06-01T00:00:00Z",
            "input_data_cutoff_utc": "2025-05-31T23:00:00Z",
            "target_timestamp_utc": "2025-06-01T01:00:00Z",
            "feature_source_audit": {"safe": "2025-05-31T23:00:00Z"},
        }

        review = p0054l2.validate_feature_matrix_safety([row], ["future_actual_price"])

        self.assertFalse(review["ok"])
        self.assertEqual(["future_actual_price"], review["forbidden_feature_names"])

    def test_checkpoint_writer_creates_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = p0054l2.write_model_checkpoint(Path(tmp), "HGB", {"status": "completed", "training": {"train_rows": 1}, "metrics": {"holdout": {"MAE": 1.0}}, "leakage_status": "ok"})

            self.assertTrue(Path(paths["json"]).exists())
            self.assertTrue(Path(paths["markdown"]).exists())

    def test_ranking_metrics_detect_top_path_overlap(self) -> None:
        rows = []
        origin = "2025-06-01T00:00:00Z"
        for hour in range(168):
            rows.append(
                {
                    "forecast_origin_timestamp_utc": origin,
                    "target_price": float(hour),
                    "pred": float(hour),
                    "features": {"se3_price_previous_week_same_target_hour": float(hour - 1)},
                }
            )

        metrics = p0054l2.evaluate_ranking_spike_ramp_metrics(rows, "pred", {"spike_price_p90": 150.0, "low_price_p10": 20.0, "ramp_abs_p90": 10.0})

        self.assertEqual(1.0, metrics["top20_168h_precision"])
        self.assertEqual(1.0, metrics["bottom20_168h_precision"])


if __name__ == "__main__":
    unittest.main()
