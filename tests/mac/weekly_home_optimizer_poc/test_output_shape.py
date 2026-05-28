from __future__ import annotations

import csv
import io
import json
import unittest

from src.mac.labs.weekly_home_optimizer_poc.planner import build_weekly_plan
from src.mac.labs.weekly_home_optimizer_poc.schema import REQUIRED_COLUMNS
from src.mac.labs.weekly_home_optimizer_poc.tables import format_csv, format_json, format_table, rows_for_plan


class OutputShapeTests(unittest.TestCase):
    def test_rows_contain_required_columns(self) -> None:
        plan = build_weekly_plan(2, 500, 22, prefer_real_weather=False)
        rows = rows_for_plan(plan)

        self.assertEqual(len(rows), 168)
        for column in REQUIRED_COLUMNS:
            self.assertIn(column, rows[0])

    def test_table_json_and_csv_outputs_are_complete(self) -> None:
        plan = build_weekly_plan(2, 500, 22, prefer_real_weather=False)

        table = format_table(plan)
        payload = json.loads(format_json(plan))
        csv_rows = list(csv.DictReader(io.StringIO(format_csv(plan))))

        self.assertIn("hour weekday_hour", table)
        self.assertEqual(len(payload["rows"]), 168)
        self.assertEqual(payload["metadata"]["weather_source"], "synthetic_fallback")
        self.assertEqual(len(csv_rows), 168)


if __name__ == "__main__":
    unittest.main()
