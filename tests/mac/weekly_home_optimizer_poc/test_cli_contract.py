from __future__ import annotations

import io
import json
import unittest

from src.mac.labs.weekly_home_optimizer_poc.cli import main, parse_args


class CliContractTests(unittest.TestCase):
    def test_required_inputs_do_not_include_reference_year_or_rh(self) -> None:
        args = parse_args(["--week", "2", "--ppm", "500", "--house-temp", "22"])

        self.assertEqual(args.week, 2)
        self.assertEqual(args.ppm, 500)
        self.assertEqual(args.house_temp, 22)
        self.assertEqual(args.people, 3)
        self.assertFalse(hasattr(args, "reference_year"))
        self.assertFalse(hasattr(args, "current_rh"))

    def test_people_input_is_available(self) -> None:
        args = parse_args(["--week", "2", "--ppm", "500", "--house-temp", "22", "--people", "6"])

        self.assertEqual(args.people, 6)

    def test_json_cli_produces_168_hour_plan(self) -> None:
        out = io.StringIO()

        status = main(
            ["--week", "2", "--ppm", "700", "--house-temp", "22", "--people", "6", "--format", "json", "--fixture-weather"],
            out,
        )

        payload = json.loads(out.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["metadata"]["hours"], 168)
        self.assertEqual(payload["metadata"]["people"], 6)
        self.assertEqual(payload["metadata"]["occupancy_gain_ppm_h"], 140)
        self.assertEqual(len(payload["rows"]), 168)


if __name__ == "__main__":
    unittest.main()
