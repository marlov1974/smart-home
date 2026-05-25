import io
import json
import unittest

from src.mac.services.spot_forecast.model import HistoricalWeek
from src.mac.services.spot_forecast.server import build_handler


def record(week, values):
    return HistoricalWeek(iso_year=2025, iso_week=week, price_index=tuple(values))


def call_handler(history, path):
    handler_class = build_handler(history)
    handler = object.__new__(handler_class)
    handler.path = path
    handler.wfile = io.BytesIO()
    captured = {"status": None, "headers": []}
    handler.send_response = lambda status: captured.__setitem__("status", status)
    handler.send_header = lambda key, value: captured["headers"].append((key, value))
    handler.end_headers = lambda: None
    handler.do_GET()
    return captured["status"], handler.wfile.getvalue().decode("utf-8")


class PeriodIndexApiTests(unittest.TestCase):
    def test_valid_week_returns_compact_array(self):
        history = [record(2, [1.0] * 21)]
        status, body = call_handler(history, "/spot/period-index?week=2")

        self.assertEqual(200, status)
        self.assertEqual([1.0] * 21, json.loads(body))
        self.assertTrue(body.startswith("["))
        self.assertNotIn(" ", body)

    def test_invalid_week_returns_400(self):
        history = [record(2, [1.0] * 21)]
        status, body = call_handler(history, "/spot/period-index?week=abc")

        self.assertEqual(400, status)
        self.assertEqual({"error": "invalid week"}, json.loads(body))

    def test_missing_week_returns_400(self):
        history = [record(2, [1.0] * 21)]
        status, body = call_handler(history, "/spot/period-index")

        self.assertEqual(400, status)
        self.assertEqual({"error": "invalid week"}, json.loads(body))

    def test_unmodelable_week_returns_404(self):
        history = [record(2, [1.0] * 21)]
        status, body = call_handler(history, "/spot/period-index?week=25")

        self.assertEqual(404, status)
        self.assertEqual({"error": "week not found"}, json.loads(body))


if __name__ == "__main__":
    unittest.main()
