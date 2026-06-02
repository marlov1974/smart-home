from __future__ import annotations

from datetime import date, timedelta
import unittest

from src.mac.services.spotprice_model_diagnostics import p0048


def ai2_row(day: date, hour: int, series: str, price: float) -> dict[str, object]:
    return {
        "timestamp_utc": f"{day.isoformat()}T{hour:02d}:00:00+00:00",
        "model_cet_timestamp": f"{day.isoformat()}T{hour:02d}:00:00+00:00",
        "model_cet_date": day.isoformat(),
        "model_cet_hour": hour,
        "model_cet_weekday": day.weekday(),
        "model_cet_day_of_year": int(day.strftime("%j")),
        "model_cet_hour_sin": 0.0,
        "model_cet_hour_cos": 1.0,
        "model_cet_day_of_year_sin": 0.0,
        "model_cet_day_of_year_cos": 1.0,
        "target_series": series,
        "hour_price": price,
        "base_day_type": "weekday",
        "special_day_type": "normal_weekday",
        "special_day_name": "normal",
        "is_special_day": 0,
        "is_bridge_day": 0,
        "is_holiday_period": 0,
        "is_major_social_holiday": 0,
        "stockholm_is_dst": 0,
        "stockholm_utc_offset_hours": 1,
        "stockholm_local_hour": hour,
    }


class P0048Tests(unittest.TestCase):
    def test_build_base_spread_rows_reconstructs_se3_minus_se1(self):
        day = date(2025, 1, 1)
        rows = [
            ai2_row(day, 0, p0048.TARGET_SE1, 1.0),
            ai2_row(day, 0, p0048.TARGET_SPREAD, 0.25),
        ]
        built = p0048.build_base_spread_rows(rows)
        self.assertEqual(1, len(built))
        self.assertAlmostEqual(1.25, built[0]["se3_price"])
        self.assertAlmostEqual(built[0]["se3_price"] - built[0]["se1_price"], built[0]["se3_minus_se1"])

    def test_gradient_formulas_are_reproducible(self):
        row = {
            "wind_south_proxy_actual": 0.8,
            "wind_central_proxy_actual": 0.5,
            "wind_north_proxy_actual": 0.2,
            "wind_system_proxy_actual": 0.4,
            "solar_south_proxy_actual": 10.0,
            "solar_north_proxy_actual": 2.0,
            "solar_system_proxy_actual": 5.0,
            "temperature_south_proxy_actual": 8.0,
            "temperature_north_proxy_actual": 1.0,
            "temperature_system_proxy_actual": 3.0,
        }
        p0048.add_gradient_features(row)
        self.assertAlmostEqual(0.6, row["wind_south_minus_north_actual"])
        self.assertAlmostEqual(0.3, row["wind_central_minus_north_actual"])
        self.assertAlmostEqual(8.0, row["solar_south_minus_north_actual"])
        self.assertAlmostEqual(7.0, row["temperature_south_minus_north_actual"])

    def test_regime_labels_match_thresholds(self):
        rows = [{"se3_minus_se1": 0.0}, {"se3_minus_se1": 0.3}, {"se3_minus_se1": 1.0}, {"se3_minus_se1": -0.4}]
        p0048.add_regime_labels(rows, p0048.P0047_THRESHOLDS)
        self.assertEqual(1, rows[0]["is_near_zero"])
        self.assertEqual(1, rows[1]["is_positive_bottleneck"])
        self.assertEqual(1, rows[2]["is_positive_spike"])
        self.assertEqual("negative_or_spike_negative", rows[3]["spread_regime"])

    def test_chronological_splits_are_non_overlapping(self):
        rows = []
        for day in (date(2024, 12, 31), date(2025, 1, 1), date(2026, 1, 1)):
            rows.append({"model_cet_date": day.isoformat()})
        counts = p0048.assign_chronological_splits(rows)
        self.assertEqual({"holdout": 1, "train": 1, "validate": 1}, counts)
        self.assertEqual(["train", "validate", "holdout"], [row["split"] for row in rows])

    def test_lagged_features_use_previous_rows_only(self):
        day = date(2025, 1, 1)
        rows = []
        for hour, spread in enumerate([0.1, 0.5]):
            row = {
                "timestamp_utc": f"{day.isoformat()}T{hour:02d}:00:00+00:00",
                "se3_minus_se1": spread,
                "is_positive_bottleneck": 1 if spread > 0.2 else 0,
                "is_positive_spike": 0,
                "spread_regime": "positive" if spread > 0.2 else "near_zero",
            }
            rows.append(row)
        p0048.add_lagged_features(rows)
        self.assertEqual(0.0, rows[0]["lag1_spread"])
        self.assertEqual(0.1, rows[1]["lag1_spread"])
        self.assertEqual(0, rows[1]["lag1_is_positive_bottleneck"])

    def test_forbidden_paths_include_no_api_or_device(self):
        self.assertIn("SE1_TO_SE3_ANCHORING", p0048.FORBIDDEN_PRODUCTION_PATHS)
        self.assertIn("SE3_API", p0048.FORBIDDEN_PRODUCTION_PATHS)
        self.assertIn("DEVICE", p0048.FORBIDDEN_PRODUCTION_PATHS)


if __name__ == "__main__":
    unittest.main()
