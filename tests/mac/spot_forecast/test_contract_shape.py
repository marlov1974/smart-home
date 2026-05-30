import ast
from datetime import date, timedelta
import io
import json
import unittest
from pathlib import Path
import tempfile

from src.mac.services.spot_forecast.model import load_history, load_history_from_db
from src.mac.services.spot_forecast.schema import InvalidWeekError, compact_json, parse_week
from src.mac.services.spot_forecast.server import run_once
from src.mac.services.spotprice_history.models import HourlySpotPrice
from src.mac.services.spotprice_history.storage import (
    connect_db,
    expected_utc_hours_for_local_date,
    init_db,
    upsert_prices,
)


def build_fixture_db(path):
    init_db(path)
    rows = []
    local = date(2022, 5, 30)
    for day in range(7):
        current = local + timedelta(days=day)
        expected = expected_utc_hours_for_local_date(current)
        for index, utc_hour in enumerate(expected):
            rows.append(
                HourlySpotPrice(
                    area="SE3",
                    utc_hour_start=utc_hour.strftime("%Y-%m-%dT%H:00Z"),
                    local_hour_start=f"{current.isoformat()}T{index % 24:02d}:00:00+02:00",
                    local_date=current.isoformat(),
                    local_hour=index % 24,
                    utc_offset="+02:00",
                    fold=0,
                    price_sek_per_kwh=1.0 + (index // 8),
                    price_eur_per_kwh=None,
                    exchange_rate=None,
                    source="fixture",
                    source_resolution="hour",
                    samples=1,
                )
            )
    with connect_db(path) as conn:
        upsert_prices(conn, rows)


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

        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "history.sqlite3"
            build_fixture_db(db)
            code = run_once("22", db_path=db, out=out, err=err)

        self.assertEqual(0, code)
        self.assertEqual("", err.getvalue())
        parsed = json.loads(out.getvalue())
        self.assertIsInstance(parsed, list)
        self.assertEqual(21, len(parsed))

    def test_run_once_unmodelable_week_returns_error_code(self):
        out = io.StringIO()
        err = io.StringIO()

        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "history.sqlite3"
            build_fixture_db(db)
            code = run_once("2", db_path=db, out=out, err=err)

        self.assertEqual(3, code)
        self.assertEqual("", out.getvalue())
        self.assertEqual({"error": "week not found"}, json.loads(err.getvalue()))

    def test_db_history_missing_db_fails_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(Exception, "spot history DB missing"):
                load_history_from_db(Path(tmp) / "missing.sqlite3")

    def test_service_uses_standard_library_imports_only(self):
        package_root = Path(__file__).resolve().parents[3] / "src" / "mac" / "services" / "spot_forecast"
        allowed_roots = {
            "__future__",
            "argparse",
            "dataclasses",
            "datetime",
            "http",
            "json",
            "pathlib",
            "sqlite3",
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
