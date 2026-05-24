"""Mac-side Open-Meteo schema checks for P0015."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.error
import urllib.request
from typing import Any, Callable


LAT = "59.6214405"
LON = "17.7336153"
API_BASE = "https://api.open-meteo.com/v1/forecast"
DAILY_VARS = "shortwave_radiation_sum,temperature_2m_mean,relative_humidity_2m_mean"
HOURLY_VARS = "temperature_2m"
SOLAR_GAIN_FACTOR_KWH_PER_MJ = 2.0
DEFAULT_TIMEOUT_SECONDS = 10.0


class WeatherContractError(Exception):
    """Raised when Open-Meteo contract validation fails."""


OpenUrl = Callable[..., Any]


def today_str() -> str:
    """Return today's local date for Open-Meteo daily requests."""

    return dt.date.today().isoformat()


def build_daily_url(day: str, lat: str = LAT, lon: str = LON) -> str:
    """Build the P0015 daily Open-Meteo URL."""

    return (
        f"{API_BASE}?latitude={lat}&longitude={lon}"
        f"&daily={DAILY_VARS}&start_date={day}&end_date={day}&timezone=auto"
    )


def build_hourly_url(lat: str = LAT, lon: str = LON) -> str:
    """Build the P0015 hourly Open-Meteo URL."""

    return f"{API_BASE}?latitude={lat}&longitude={lon}&hourly={HOURLY_VARS}&forecast_hours=1&timezone=auto"


def fetch_json(
    url: str,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> tuple[dict[str, Any], int]:
    """Fetch one JSON response and return decoded data plus byte length."""

    open_url = opener or urllib.request.urlopen
    request = urllib.request.Request(url, method="GET")
    try:
        with open_url(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.URLError as exc:
        raise WeatherContractError(f"fetch failed: {exc}") from exc
    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise WeatherContractError("response is not valid JSON") from exc
    if not isinstance(data, dict):
        raise WeatherContractError("response root is not an object")
    return data, len(raw)


def _first_number(root: dict[str, Any], section: str, field: str) -> float:
    group = root.get(section)
    if not isinstance(group, dict):
        raise WeatherContractError(f"missing {section}")
    values = group.get(field)
    if not isinstance(values, list) or not values:
        raise WeatherContractError(f"missing {section}.{field}[0]")
    try:
        value = float(values[0])
    except (TypeError, ValueError) as exc:
        raise WeatherContractError(f"{section}.{field}[0] is not numeric") from exc
    return value


def clip(value: float, lower: float, upper: float) -> float:
    """Clip numeric value to inclusive bounds."""

    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


def round1(value: float) -> float:
    """Round to one decimal using the same shape as the Shelly runtime."""

    return round(float(value), 1)


def parse_daily(data: dict[str, Any]) -> dict[str, float]:
    """Validate daily schema and return normalized G2 weather fields."""

    swr = _first_number(data, "daily", "shortwave_radiation_sum")
    temp_avg = _first_number(data, "daily", "temperature_2m_mean")
    humidity = _first_number(data, "daily", "relative_humidity_2m_mean")
    return {
        "solar_kwh_today": int(round(clip(max(swr, 0.0) * SOLAR_GAIN_FACTOR_KWH_PER_MJ, 0, 999))),
        "temp_avg_today": round1(clip(temp_avg, -99.9, 99.9)),
        "humidity_avg_today": round1(clip(humidity, 0, 100)),
    }


def parse_hourly(data: dict[str, Any]) -> dict[str, float]:
    """Validate hourly schema and return normalized G2 weather fields."""

    temp_now = _first_number(data, "hourly", "temperature_2m")
    return {"temp_now": round1(clip(temp_now, -99.9, 99.9))}


def check_openmeteo(
    day: str | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> dict[str, Any]:
    """Run the P0015 Open-Meteo pre-live schema check."""

    checked_day = day or today_str()
    daily_url = build_daily_url(checked_day)
    hourly_url = build_hourly_url()
    daily_data, daily_len = fetch_json(daily_url, timeout=timeout, opener=opener)
    hourly_data, hourly_len = fetch_json(hourly_url, timeout=timeout, opener=opener)
    daily = parse_daily(daily_data)
    hourly = parse_hourly(hourly_data)
    weather = {
        "solar_kwh_today": daily["solar_kwh_today"],
        "temp_now": hourly["temp_now"],
        "temp_avg_today": daily["temp_avg_today"],
        "humidity_avg_today": daily["humidity_avg_today"],
    }
    return {
        "date": checked_day,
        "daily_url": daily_url,
        "hourly_url": hourly_url,
        "daily_response_bytes": daily_len,
        "hourly_response_bytes": hourly_len,
        "weather": weather,
        "required_fields": {
            "daily.shortwave_radiation_sum[0]": True,
            "daily.temperature_2m_mean[0]": True,
            "daily.relative_humidity_2m_mean[0]": True,
            "hourly.temperature_2m[0]": True,
        },
    }


def main(argv: list[str] | None = None) -> int:
    """Run weather contract tooling."""

    parser = argparse.ArgumentParser(prog="python3 -m src.mac.tools.weather_contract")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check-openmeteo")
    check_parser.add_argument("--date")
    check_parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)

    args = parser.parse_args(argv)
    try:
        if args.command == "check-openmeteo":
            result = check_openmeteo(day=args.date, timeout=args.timeout)
        else:
            return 1
    except WeatherContractError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0
