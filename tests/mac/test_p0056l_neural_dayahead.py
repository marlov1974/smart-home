from __future__ import annotations

import unittest

from src.mac.services.spotprice_model_diagnostics import p0056l


class P0056LNeuralDayAheadTests(unittest.TestCase):
    def test_select_representative_origins_is_deterministic(self) -> None:
        origins = list(range(12))
        self.assertEqual(p0056l.select_representative_origins(origins, 4), [0, 4, 8])

    def test_sequence_feature_names_are_forecast_safe(self) -> None:
        forbidden = ("future_actual", "spot", "flow", "exchange", "a61", "capacity", "physical_balance")
        self.assertEqual(len(p0056l.SEQUENCE_FEATURES), 168)
        self.assertFalse([feature for feature in p0056l.SEQUENCE_FEATURES if any(term in feature.lower() for term in forbidden)])


if __name__ == "__main__":
    unittest.main()
