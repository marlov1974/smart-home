from __future__ import annotations

import json
import unittest
from io import BytesIO

from src.mac.labs.weekly_home_optimizer_poc.server import build_handler, main


class _FakeSocket:
    def __init__(self, request: bytes) -> None:
        self._request = BytesIO(request)
        self.response = BytesIO()

    def makefile(self, mode: str, buffering: int | None = None):
        if "r" in mode:
            return self._request
        return self.response

    def sendall(self, data: bytes) -> None:
        self.response.write(data)


def _request(path: str) -> tuple[int, dict[str, str], str]:
    raw = f"GET {path} HTTP/1.1\r\nHost: test.local\r\nConnection: close\r\n\r\n".encode("ascii")
    fake = _FakeSocket(raw)
    handler_class = build_handler()
    handler_class(fake, ("127.0.0.1", 12345), object())
    response = fake.response.getvalue().decode("utf-8")
    header_text, _, body = response.partition("\r\n\r\n")
    header_lines = header_text.split("\r\n")
    status = int(header_lines[0].split()[1])
    headers = {}
    for line in header_lines[1:]:
        key, _, value = line.partition(":")
        headers[key.lower()] = value.strip()
    return status, headers, body


class BrowserServerTests(unittest.TestCase):

    def test_health_endpoint(self) -> None:
        status, _, body = _request("/health")
        payload = json.loads(body)

        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "ok")

    def test_root_form(self) -> None:
        status, _, html = _request("/")

        self.assertEqual(status, 200)
        self.assertIn('name="week"', html)
        self.assertIn('name="ppm"', html)
        self.assertIn('name="houseTemp"', html)

    def test_html_plan_result(self) -> None:
        status, _, html = _request("/?week=2&ppm=500&houseTemp=22")

        self.assertEqual(status, 200)
        self.assertIn("Weekly Home POC", html)
        self.assertIn("<table>", html)
        self.assertIn("ppm_absolute", html)

    def test_json_plan_result(self) -> None:
        status, _, body = _request("/api/weekly-home-poc?week=2&ppm=500&houseTemp=22")
        payload = json.loads(body)

        self.assertEqual(status, 200)
        self.assertEqual(payload["input"]["week"], 2)
        self.assertEqual(payload["summary"]["hours"], 168)
        self.assertEqual(len(payload["hours"]), 168)

    def test_invalid_api_returns_400_json(self) -> None:
        status, _, body = _request("/api/weekly-home-poc?week=bad&ppm=500&houseTemp=22")

        self.assertEqual(status, 400)
        payload = json.loads(body)
        self.assertIn("error", payload)

    def test_once_smoke(self) -> None:
        self.assertEqual(main(["--once-smoke"]), 0)


if __name__ == "__main__":
    unittest.main()
