"""Standard-library browser server for the P0020 weekly home POC UI."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import sys
from typing import Mapping, Sequence
from urllib.parse import parse_qs, urlparse

from .html import render_form, render_page, render_result
from .planner import build_weekly_plan
from .ppm_plan import DEFAULT_PEOPLE, validate_people
from .tables import rows_for_plan


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8081
SERVICE_NAME = "weekly_home_optimizer_poc"


class RequestError(ValueError):
    """Raised when an HTTP request cannot be converted into planner input."""


@dataclass(frozen=True)
class PlanRequest:
    week: int
    ppm: float
    house_temp: float
    people: float = DEFAULT_PEOPLE


def _single_value(query: Mapping[str, list[str]], key: str) -> str:
    values = query.get(key)
    if not values or values[0] == "":
        raise RequestError(f"{key} missing")
    return values[0]


def parse_plan_query(query: Mapping[str, list[str]]) -> PlanRequest:
    """Parse weekly POC planner inputs from HTTP query parameters."""

    try:
        week = int(_single_value(query, "week"))
    except ValueError as exc:
        raise RequestError("week invalid") from exc
    if week < 1 or week > 53:
        raise RequestError("week invalid")
    try:
        ppm = float(_single_value(query, "ppm"))
    except ValueError as exc:
        raise RequestError("ppm invalid") from exc
    if ppm < 350 or ppm > 3000:
        raise RequestError("ppm invalid")
    try:
        house_temp = float(_single_value(query, "houseTemp"))
    except ValueError as exc:
        raise RequestError("houseTemp invalid") from exc
    if house_temp < 5 or house_temp > 35:
        raise RequestError("houseTemp invalid")
    try:
        people = validate_people(query.get("people", [str(DEFAULT_PEOPLE)])[0])
    except ValueError as exc:
        raise RequestError("people invalid") from exc
    return PlanRequest(week=week, ppm=ppm, house_temp=house_temp, people=people)


def plan_payload(request: PlanRequest, prefer_real_weather: bool = True) -> dict[str, object]:
    """Build the JSON-serializable payload for API and HTML responses."""

    plan = build_weekly_plan(
        request.week,
        request.ppm,
        request.house_temp,
        people=request.people,
        prefer_real_weather=prefer_real_weather,
    )
    rows = rows_for_plan(plan)
    summary = {
        "hours": len(rows),
        "min_ppm": round(min(row["ppm_absolute"] for row in rows), 1),
        "max_ppm": round(max(row["ppm_absolute"] for row in rows), 1),
        "avg_supply_pct": round(sum(row["supply_pct"] for row in rows) / len(rows), 1),
        "total_heat_kWh": round(sum(row["heat_kWh"] for row in rows), 1),
        "total_cost": round(sum(row["total_cost"] for row in rows), 1),
        "people": plan.people,
        "occupancy_gain_ppm_h": round(plan.occupancy_gain_ppm_h, 1),
        "weather_source": plan.weather_source,
        "weather_provider": plan.weather_provider,
        "weather_profile_strategy": plan.weather_profile_strategy,
        "weather_profile_year": plan.weather_profile_year,
        "spot_model": plan.spot.spot_model,
        "spot_resolution": plan.spot.spot_resolution,
        "spot_actual_fixture_path": plan.spot.spot_actual_fixture_path,
        "spot_actual_known_hours": plan.spot.spot_actual_known_hours,
        "spot_forecast_hours": plan.spot.spot_forecast_hours,
        "spot_actual_patched_hours": plan.spot.spot_actual_patched_hours,
        "spot_patch_strategy": plan.spot.spot_patch_strategy,
        "spot_index_min": round(plan.spot.spot_index_min, 4),
        "spot_index_max": round(plan.spot.spot_index_max, 4),
        "spot_index_avg": round(plan.spot.spot_index_avg, 4),
        "spot_patch_warnings": plan.spot.spot_patch_warnings,
        "heat_optimizer": plan.heat.heat_optimizer,
        "heat_modes_kw": plan.heat.heat_modes_kw,
        "heat_soc_capacity_kWh": plan.heat.heat_soc_capacity_kWh,
        "heat_soc_step_kWh": plan.heat.heat_soc_step_kWh,
        "start_soc_pct": plan.heat.start_soc_pct,
        "end_soc_min_pct": plan.heat.end_soc_min_pct,
        "min_heat_soc_pct": plan.heat.min_heat_soc_pct,
        "end_heat_soc_pct": plan.heat.end_heat_soc_pct,
        "heat_optimizer_warnings": plan.heat.heat_optimizer_warnings,
        "heat_cost_model": plan.heat_cost_comparison.heat_cost_model,
        "cop_model": plan.heat_cost_comparison.cop_model,
        "cop_min": plan.heat_cost_comparison.cop_min,
        "cop_max": plan.heat_cost_comparison.cop_max,
        "optimized_heat_el_kWh": plan.heat_cost_comparison.optimized_heat_el_kWh_total,
        "flat_heat_el_kWh": plan.heat_cost_comparison.flat_heat_el_kWh_total,
        "optimized_heat_el_cost": plan.heat_cost_comparison.optimized_heat_el_cost_total,
        "flat_heat_el_cost": plan.heat_cost_comparison.flat_heat_el_cost_total,
        "optimized_vs_flat_cost_pct": plan.heat_cost_comparison.optimized_vs_flat_cost_pct,
        "optimized_saving_pct": plan.heat_cost_comparison.optimized_saving_pct,
        "avg_cop_optimized": plan.heat_cost_comparison.avg_cop_optimized,
        "avg_cop_flat": plan.heat_cost_comparison.avg_cop_flat,
        "heat_cost_comparison_warnings": plan.heat_cost_comparison.heat_cost_comparison_warnings,
    }
    if plan.weather_fallback_reason:
        summary["weather_fallback_reason"] = plan.weather_fallback_reason
    return {
        "input": {
            "week": request.week,
            "ppm": request.ppm,
            "houseTemp": request.house_temp,
            "people": request.people,
        },
        "summary": summary,
        "hours": rows,
    }


def _compact_json(payload: object) -> bytes:
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def build_handler() -> type[BaseHTTPRequestHandler]:
    """Create the HTTP handler class for the weekly home POC server."""

    class WeeklyHomePocHandler(BaseHTTPRequestHandler):
        server_version = "WeeklyHomePoc/0.1"

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            if parsed.path == "/health":
                self._send_json(HTTPStatus.OK, {"status": "ok", "service": SERVICE_NAME})
                return
            if parsed.path == "/api/weekly-home-poc":
                self._handle_api(query)
                return
            if parsed.path == "/":
                self._handle_root(query)
                return
            self._send_html(
                HTTPStatus.NOT_FOUND,
                render_page("Not Found", "<p>Not found.</p>"),
            )

        def log_message(self, format: str, *args: object) -> None:
            sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))

        def _handle_root(self, query: Mapping[str, list[str]]) -> None:
            if not query:
                self._send_html(HTTPStatus.OK, render_form())
                return
            try:
                request = parse_plan_query(query)
                payload = plan_payload(request)
            except Exception as exc:  # Keep browser endpoint human-readable.
                self._send_html(HTTPStatus.BAD_REQUEST, render_form(_form_values(query), str(exc)))
                return
            self._send_html(HTTPStatus.OK, render_result(payload))

        def _handle_api(self, query: Mapping[str, list[str]]) -> None:
            try:
                request = parse_plan_query(query)
                payload = plan_payload(request)
            except Exception as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return
            self._send_json(HTTPStatus.OK, payload)

        def _send_json(self, status: HTTPStatus, payload: object) -> None:
            body = _compact_json(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, status: HTTPStatus, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return WeeklyHomePocHandler


def _form_values(query: Mapping[str, list[str]]) -> dict[str, str]:
    return {key: values[0] for key, values in query.items() if values}


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """Run the read-only local HTTP server until interrupted."""

    server = ThreadingHTTPServer((host, int(port)), build_handler())
    print(f"Serving weekly home POC on http://{host}:{int(port)}/")
    try:
        server.serve_forever()
    finally:
        server.server_close()


def run_once_smoke() -> int:
    """Run a deterministic non-blocking server smoke check."""

    payload = plan_payload(
        PlanRequest(week=2, ppm=500.0, house_temp=22.0, people=DEFAULT_PEOPLE),
        prefer_real_weather=False,
    )
    html = render_result(payload)
    health = _compact_json({"status": "ok", "service": SERVICE_NAME})
    if len(payload["hours"]) != 168:
        return 1
    if "Weekly Home POC" not in html or b'"status":"ok"' not in health:
        return 1
    print("weekly_home_optimizer_poc server smoke ok")
    return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse server CLI arguments."""

    parser = argparse.ArgumentParser(description="Serve the weekly home POC browser UI.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--once-smoke", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run smoke verification or start the HTTP server."""

    args = parse_args(argv)
    if args.once_smoke:
        return run_once_smoke()
    run_server(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
