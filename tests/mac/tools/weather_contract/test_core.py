import ast
import json
import unittest
from pathlib import Path

from src.mac.tools.weather_contract.core import (
    WeatherContractError,
    build_daily_url,
    build_hourly_url,
    check_openmeteo,
    parse_daily,
    parse_hourly,
)


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


class FakeOpener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, request, timeout=0):
        self.requests.append((request, timeout))
        if not self.responses:
            raise AssertionError("no fake response queued")
        return self.responses.pop(0)


def response(data):
    return FakeResponse(json.dumps(data).encode("utf-8"))


DAILY = {
    "daily": {
        "time": ["2026-05-24"],
        "shortwave_radiation_sum": [26.11],
        "temperature_2m_mean": [18.44],
        "relative_humidity_2m_mean": [62],
    }
}

HOURLY = {
    "hourly": {
        "time": ["2026-05-24T13:00"],
        "temperature_2m": [21.94],
    }
}


class WeatherContractTests(unittest.TestCase):
    def test_build_urls_use_p0015_fields(self):
        daily_url = build_daily_url("2026-05-24")
        hourly_url = build_hourly_url()

        self.assertIn("shortwave_radiation_sum,temperature_2m_mean,relative_humidity_2m_mean", daily_url)
        self.assertIn("start_date=2026-05-24", daily_url)
        self.assertIn("end_date=2026-05-24", daily_url)
        self.assertIn("hourly=temperature_2m", hourly_url)
        self.assertIn("forecast_hours=1", hourly_url)

    def test_parse_daily_normalizes_contract(self):
        parsed = parse_daily(DAILY)

        self.assertEqual(
            {"solar_kwh_today": 52, "temp_avg_today": 18.4, "humidity_avg_today": 62.0},
            parsed,
        )

    def test_parse_hourly_normalizes_contract(self):
        self.assertEqual({"temp_now": 21.9}, parse_hourly(HOURLY))

    def test_missing_schema_is_rejected(self):
        with self.assertRaisesRegex(WeatherContractError, "missing daily.relative_humidity_2m_mean"):
            parse_daily({"daily": {"shortwave_radiation_sum": [1], "temperature_2m_mean": [2]}})

    def test_check_openmeteo_fetches_daily_and_hourly(self):
        opener = FakeOpener([response(DAILY), response(HOURLY)])

        result = check_openmeteo(day="2026-05-24", opener=opener)

        self.assertEqual("2026-05-24", result["date"])
        self.assertEqual(52, result["weather"]["solar_kwh_today"])
        self.assertEqual(21.9, result["weather"]["temp_now"])
        self.assertTrue(result["required_fields"]["hourly.temperature_2m[0]"])
        self.assertEqual(2, len(opener.requests))

    def test_tool_uses_standard_library_imports_only(self):
        package_root = Path(__file__).resolve().parents[4] / "src" / "mac" / "tools" / "weather_contract"
        allowed_roots = {
            "__future__",
            "argparse",
            "datetime",
            "json",
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
