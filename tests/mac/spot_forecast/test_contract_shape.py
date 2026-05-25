import ast
import io
import json
import unittest
from pathlib import Path

from src.mac.services.spot_forecast.model import load_history
from src.mac.services.spot_forecast.schema import InvalidWeekError, compact_json, parse_week
from src.mac.services.spot_forecast.server import run_once


class ContractShapeTests(unittest.TestCase):
    def test_parse_week_accepts_iso_week_range(self):
        self.assertEqual(1, parse_week("1"))
        self.assertEqual(53, parse_week("53"))

    def test_parse_week_rejects_invalid_input(self):
        for value in (None, "", "0", "54", "x"):
            with self.subTest(value=value):
                with self.assertRaises(InvalidWeekError):
                    parse_week(value)

    def test_compact_json_uses_no_spaces(self):
        self.assertEqual("[1,2,{\"a\":3}]", compact_json([1, 2, {"a": 3}]))

    def test_committed_history_loads_with_twenty_one_indexes(self):
        history = load_history()

        self.assertGreaterEqual(len(history), 1)
        self.assertTrue(all(len(record.price_index) == 21 for record in history))

    def test_run_once_valid_week_prints_array_only(self):
        out = io.StringIO()
        err = io.StringIO()

        code = run_once("2", out=out, err=err)

        self.assertEqual(0, code)
        self.assertEqual("", err.getvalue())
        parsed = json.loads(out.getvalue())
        self.assertIsInstance(parsed, list)
        self.assertEqual(21, len(parsed))

    def test_run_once_unmodelable_week_returns_error_code(self):
        out = io.StringIO()
        err = io.StringIO()

        code = run_once("25", out=out, err=err)

        self.assertEqual(3, code)
        self.assertEqual("", out.getvalue())
        self.assertEqual({"error": "week not found"}, json.loads(err.getvalue()))

    def test_service_uses_standard_library_imports_only(self):
        package_root = Path(__file__).resolve().parents[3] / "src" / "mac" / "services" / "spot_forecast"
        allowed_roots = {
            "__future__",
            "argparse",
            "dataclasses",
            "http",
            "json",
            "pathlib",
            "src",
            "sys",
            "typing",
            "urllib",
        }

        for path in package_root.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    imports.add(node.module.split(".")[0])
            self.assertLessEqual(imports, allowed_roots, path)


if __name__ == "__main__":
    unittest.main()
