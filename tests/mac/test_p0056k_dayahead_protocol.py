from __future__ import annotations

from datetime import date
import unittest

from src.mac.services.spotprice_model_diagnostics import p0056k


class P0056KDayAheadProtocolTests(unittest.TestCase):
    def test_delivery_day_has_24_target_hours(self) -> None:
        hours = p0056k.delivery_day_target_utc_hours(date(2025, 6, 1))
        self.assertEqual(len(hours), 24)
        self.assertEqual(len(set(hours)), 24)

    def test_lag_protocol_features_are_forecast_safe_names(self) -> None:
        forbidden = ("future_actual", "spot", "flow", "exchange", "a61", "capacity", "physical_balance")
        self.assertFalse([feature for feature in p0056k.FEATURES if any(term in feature.lower() for term in forbidden)])
        self.assertIn("safe_same_hour_lag_168h", p0056k.FEATURES)
        self.assertIn("origin_consumption_lag_1h", p0056k.FEATURES)


if __name__ == "__main__":
    unittest.main()
