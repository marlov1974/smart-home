from __future__ import annotations

from datetime import date
import unittest

from src.mac.services.spotprice_model_diagnostics import p0047


def row(day: date, hour: int, series: str, price: float) -> dict[str, object]:
    return {
        "timestamp_utc": f"{day.isoformat()}T{hour:02d}:00:00+00:00",
        "model_cet_timestamp": f"{day.isoformat()}T{hour:02d}:00:00+00:00",
        "model_cet_date": day.isoformat(),
        "model_cet_hour": hour,
        "model_cet_weekday": day.weekday(),
        "model_cet_day_of_year": int(day.strftime("%j")),
        "target_series": series,
        "hour_price": price,
        "base_day_type": "weekday",
        "special_day_type": "normal_weekday",
        "special_day_name": "normal_weekday",
        "is_special_day": 0,
        "is_bridge_day": 0,
        "is_holiday_period": 0,
        "is_major_social_holiday": 0,
        "hourly_temperature_actual": 1.0,
        "hourly_solar_actual": 2.0,
        "hourly_wind_actual": 0.3,
    }


class P0047Tests(unittest.TestCase):
    def test_validate_contract_requires_fixed_cet_fields(self):
        contract = p0047.validate_p0047_contract([{"target_series": p0047.TARGET_SE1, "hour_price": 1.0}])
        self.assertFalse(contract["ok"])
        self.assertIn("timestamp_utc", contract["missing_required_fields"])

    def test_join_spread_rows_reconstructs_se3(self):
        day = date(2025, 1, 1)
        rows = [
            row(day, 0, p0047.TARGET_SE1, 1.25),
            row(day, 0, p0047.TARGET_SPREAD, 0.10),
            row(day, 1, p0047.TARGET_SE1, 1.00),
            row(day, 1, p0047.TARGET_SPREAD, -0.20),
        ]
        joined = p0047.join_spread_rows(rows, day, day)
        self.assertEqual(2, len(joined))
        self.assertAlmostEqual(1.35, joined[0]["se3_price"])
        self.assertAlmostEqual(0.10, joined[0]["se3_minus_se1"])
        self.assertAlmostEqual(0.80, joined[1]["se3_price"])

    def test_threshold_candidates_are_reproducible(self):
        thresholds = p0047.threshold_candidates([-0.5, -0.1, 0.0, 0.1, 0.5])
        self.assertIn("T1_fixed_ore_or_currency_thresholds", thresholds)
        self.assertIn("T2_quantile_thresholds", thresholds)
        self.assertIn("T3_robust_sigma_thresholds", thresholds)
        self.assertGreater(thresholds["T3_robust_sigma_thresholds"]["spike_positive"], thresholds["T3_robust_sigma_thresholds"]["positive"])

    def test_assign_spread_regime_distinguishes_core_regimes(self):
        thresholds = {
            "near_zero_abs": 0.02,
            "positive": 0.05,
            "negative": -0.05,
            "spike_positive": 0.20,
            "spike_negative": -0.20,
        }
        self.assertEqual(("zero", "spread_near_zero"), p0047.assign_spread_regime(0.01, thresholds))
        self.assertEqual(("positive", "spread_positive"), p0047.assign_spread_regime(0.10, thresholds))
        self.assertEqual(("negative", "spread_negative"), p0047.assign_spread_regime(-0.10, thresholds))
        self.assertEqual(("positive", "spread_spike_positive"), p0047.assign_spread_regime(0.25, thresholds))
        self.assertEqual(("negative", "spread_spike_negative"), p0047.assign_spread_regime(-0.25, thresholds))

    def test_regime_runs_and_transitions_are_deterministic(self):
        day = date(2025, 1, 1)
        rows = []
        for hour, regime in enumerate(["spread_near_zero", "spread_near_zero", "spread_positive", "spread_negative"]):
            item = p0047.join_spread_rows(
                [row(day, hour, p0047.TARGET_SE1, 1.0), row(day, hour, p0047.TARGET_SPREAD, 0.0)],
                day,
                day,
            )[0]
            item["spread_regime"] = regime
            rows.append(item)
        persistence = p0047.analyze_persistence(rows)
        self.assertEqual(3, len(persistence["run_lengths"]))
        self.assertEqual(1, persistence["transition_matrix"]["spread_near_zero"]["spread_positive"])
        self.assertEqual(1, persistence["transition_matrix"]["spread_positive"]["spread_negative"])

    def test_forbidden_paths_include_no_anchoring_or_api(self):
        self.assertIn("SE1_TO_SE3_ANCHORING", p0047.FORBIDDEN_PRODUCTION_PATHS)
        self.assertIn("SE3_API", p0047.FORBIDDEN_PRODUCTION_PATHS)
        self.assertIn("DEVICE", p0047.FORBIDDEN_PRODUCTION_PATHS)


if __name__ == "__main__":
    unittest.main()
