#!/usr/bin/env python3
"""Regression checks for the read-only attempt11 identification analyzer."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


MODULAR_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = MODULAR_ROOT / "tools/analyze_energy_field.py"
ATTEMPT11_FIXTURE = Path(__file__).resolve().parent / "fixtures/attempt11"
SPEC = importlib.util.spec_from_file_location("analyze_energy_field", MODULE_PATH)
assert SPEC and SPEC.loader
FIELD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = FIELD
SPEC.loader.exec_module(FIELD)


class FieldAnalyzerTests(unittest.TestCase):
    def test_pair_split_matches_shelly_upward_ties(self):
        self.assertEqual(FIELD.rounded_device_target(6000), 3000)
        self.assertEqual(FIELD.rounded_device_target(6500), 3500)
        self.assertEqual(FIELD.rounded_device_target(13500), 7000)

    def test_attempt11_facts_and_restoration(self):
        directory = ATTEMPT11_FIXTURE
        result = FIELD.analyze(directory / "events.jsonl", directory / "restoration.json")
        self.assertEqual(result["energy"]["measured_wh"], 16151)
        self.assertEqual(result["energy"]["error_wh"], 151)
        self.assertTrue(result["restoration"]["verified"])

        split = result["command_split"]
        self.assertGreater(split["up_rounded_fraction"], 0.54)
        self.assertLess(split["up_rounded_fraction"], 0.55)
        self.assertAlmostEqual(split["extra_requested_command_area_wh"], 477.7, delta=0.2)

        fourth = result["energy"]["quarters"][3]
        self.assertEqual(fourth["both_limited_samples"], 27)
        self.assertAlmostEqual(fourth["both_limited_power_mean_w"], 10517, delta=1)
        self.assertAlmostEqual(fourth["measured_wh"], 2628, delta=1)

        first_model = result["devices"]["1"]["hz_to_power"]
        second_model = result["devices"]["2"]["hz_to_power"]
        self.assertEqual(first_model["lag_samples"], 2)
        self.assertEqual(second_model["lag_samples"], 1)
        self.assertAlmostEqual(first_model["gain_w_per_hz"], 133.2, delta=1)
        self.assertAlmostEqual(second_model["gain_w_per_hz"], 128.2, delta=1)


if __name__ == "__main__":
    unittest.main()
