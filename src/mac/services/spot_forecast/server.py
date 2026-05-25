"""HTTP and CLI entry points for the P0017 spot forecast service."""

from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from typing import Sequence
from urllib.parse import parse_qs, urlparse


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from src.mac.services.spot_forecast.model import (  # noqa: E402
    HistoricalWeek,
    SpotForecastError,
    WeekNotFoundError,
    forecast_period_indexes,
    load_history,
)
from src.mac.services.spot_forecast.schema import InvalidWeekError, compact_json, parse_week  # noqa: E402


ERROR_INVALID_WEEK = {"error": "invalid week"}
ERROR_WEEK_NOT_FOUND = {"error": "week not found"}
ERROR_NOT_FOUND = {"error": "not found"}


def _write_json(handler: BaseHTTPRequestHandler, status: HTTPStatus, body: object) -> None:
    payload = compact_json(body).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


def _query_week(path: str) -> int:
    query = parse_qs(urlparse(path).query, keep_blank_values=True)
    values = query.get("week")
    raw = values[0] if values else None
    return parse_week(raw)


def build_handler(history: Sequence[HistoricalWeek]) -> type[BaseHTTPRequestHandler]:
    """Create a request handler bound to historical model records."""

    records = list(history)

    class SpotForecastHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/spot/period-index":
                _write_json(self, HTTPStatus.NOT_FOUND, ERROR_NOT_FOUND)
                return
            try:
                week = _query_week(self.path)
                response = forecast_period_indexes(week, records)
            except InvalidWeekError:
                _write_json(self, HTTPStatus.BAD_REQUEST, ERROR_INVALID_WEEK)
                return
            except WeekNotFoundError:
                _write_json(self, HTTPStatus.NOT_FOUND, ERROR_WEEK_NOT_FOUND)
                return
            except SpotForecastError as exc:
                _write_json(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})
                return
            _write_json(self, HTTPStatus.OK, response)

        def log_message(self, format: str, *args: object) -> None:
            return

    return SpotForecastHandler


def run_once(week_arg: str | None, out=sys.stdout, err=sys.stderr) -> int:
    """Print one compact period-index response and exit."""

    try:
        week = parse_week(week_arg)
        response = forecast_period_indexes(week)
    except InvalidWeekError:
        print(compact_json(ERROR_INVALID_WEEK), file=err)
        return 2
    except WeekNotFoundError:
        print(compact_json(ERROR_WEEK_NOT_FOUND), file=err)
        return 3
    except SpotForecastError as exc:
        print(compact_json({"error": str(exc)}), file=err)
        return 1
    print(compact_json(response), file=out)
    return 0


def serve(host: str, port: int, history: Sequence[HistoricalWeek] | None = None) -> None:
    """Run the trusted-local spot forecast HTTP service."""

    records = list(history) if history is not None else load_history()
    server = ThreadingHTTPServer((host, port), build_handler(records))
    try:
        server.serve_forever()
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> int:
    """Run the spot forecast CLI."""

    parser = argparse.ArgumentParser(prog="python3 -m src.mac.services.spot_forecast")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--week")
    args = parser.parse_args(argv)

    if args.once:
        return run_once(args.week)
    serve(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

