"""Weather providers for the P0021 weekly home optimizer POC."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timedelta
import json
import math
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

from .schema import HOURS_PER_WEEK, InputProfile


LATITUDE = "59.6214405"
LONGITUDE = "17.7336153"
OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
OPEN_METEO_PROVIDER = "open-meteo archive"
WEATHER_STRATEGY = "latest_completed_iso_week_or_previous_year"


class WeatherProfileError(Exception):
    """Raised when a weather provider cannot produce a valid profile."""


def _validate_week_number(week_number: int) -> int:
    week = int(week_number)
    if week < 1 or week > 53:
        raise ValueError("week must be in range 1..53")
    return week


def latest_completed_iso_year_for_week(week_number: int, today: date | None = None) -> int:
    """Select the latest year where the requested ISO week is complete."""

    week = _validate_week_number(week_number)
    current = today or date.today()
    candidate_year = current.isocalendar().year
    start = date.fromisocalendar(candidate_year, week, 1)
    complete_at = start + timedelta(days=7)
    if complete_at <= current:
        return candidate_year
    return candidate_year - 1


def operational_week_dates(year: int, week_number: int) -> tuple[date, date]:
    """Return request start/end dates covering Monday 06:00 to next Monday 06:00."""

    week = _validate_week_number(week_number)
    start = date.fromisocalendar(int(year), week, 1)
    end = start + timedelta(days=7)
    return start, end


def synthetic_fallback_profile(week_number: int, reason: str | None = None) -> InputProfile:
    """Build deterministic fallback weather with explicit metadata."""

    week = _validate_week_number(week_number)
    seasonal_angle = 2.0 * math.pi * ((week - 3) / 52.0)
    seasonal_temp = 7.0 - 13.0 * math.cos(seasonal_angle)
    coldness = max(0.0, min(1.0, (8.0 - seasonal_temp) / 18.0))
    outdoor_temp_c: list[float] = []
    outdoor_rh_pct: list[float] = []
    for hour in range(HOURS_PER_WEEK):
        day = hour // 24
        hour_of_day = (6 + hour) % 24
        daily_temp = 3.2 * math.sin(2.0 * math.pi * (hour_of_day - 14) / 24.0)
        weekly_wave = 1.8 * math.sin(2.0 * math.pi * (day + week % 7) / 7.0)
        temp = seasonal_temp + daily_temp + weekly_wave
        rh = 62.0 + 24.0 * coldness - 0.8 * daily_temp
        if temp > 10.0:
            rh += 8.0 * math.sin(2.0 * math.pi * (hour_of_day - 4) / 24.0)
        outdoor_temp_c.append(round(temp, 2))
        outdoor_rh_pct.append(round(max(35.0, min(98.0, rh)), 2))
    return InputProfile(
        week_number=week,
        outdoor_temp_c=tuple(outdoor_temp_c),
        outdoor_rh_pct=tuple(outdoor_rh_pct),
        weather_source="synthetic_fallback",
        weather_provider="internal synthetic profile",
        weather_profile_strategy=WEATHER_STRATEGY,
        weather_profile_year=None,
        weather_fallback_reason=reason,
    )


def parse_open_meteo_hourly(payload: dict[str, Any], year: int, week_number: int) -> InputProfile:
    """Parse an Open-Meteo hourly archive response into an operational-week profile."""

    week = _validate_week_number(week_number)
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        raise WeatherProfileError("missing hourly weather")
    times = hourly.get("time")
    temps = hourly.get("temperature_2m")
    rhs = hourly.get("relative_humidity_2m")
    if not isinstance(times, list) or not isinstance(temps, list) or not isinstance(rhs, list):
        raise WeatherProfileError("invalid hourly weather arrays")
    if not (len(times) == len(temps) == len(rhs)):
        raise WeatherProfileError("hourly weather arrays have different lengths")
    start_date, _ = operational_week_dates(year, week)
    start_dt = datetime.combine(start_date, datetime.min.time()).replace(hour=6)
    expected = [(start_dt + timedelta(hours=offset)).strftime("%Y-%m-%dT%H:%M") for offset in range(HOURS_PER_WEEK)]
    by_time = {str(timestamp): index for index, timestamp in enumerate(times)}
    outdoor_temp_c: list[float] = []
    outdoor_rh_pct: list[float] = []
    for timestamp in expected:
        index = by_time.get(timestamp)
        if index is None:
            raise WeatherProfileError(f"missing weather hour {timestamp}")
        try:
            temp = float(temps[index])
            rh = float(rhs[index])
        except (TypeError, ValueError) as exc:
            raise WeatherProfileError(f"invalid weather value {timestamp}") from exc
        outdoor_temp_c.append(round(temp, 2))
        outdoor_rh_pct.append(round(max(0.0, min(100.0, rh)), 2))
    return InputProfile(
        week_number=week,
        outdoor_temp_c=tuple(outdoor_temp_c),
        outdoor_rh_pct=tuple(outdoor_rh_pct),
        weather_source="real_open_meteo",
        weather_provider=OPEN_METEO_PROVIDER,
        weather_profile_strategy=WEATHER_STRATEGY,
        weather_profile_year=int(year),
        weather_fallback_reason=None,
    )


def build_open_meteo_archive_url(year: int, week_number: int) -> str:
    """Build the Open-Meteo archive URL for the operational week request."""

    start, end = operational_week_dates(year, week_number)
    query = urlencode(
        {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "hourly": "temperature_2m,relative_humidity_2m",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "timezone": "auto",
        }
    )
    return f"{OPEN_METEO_ARCHIVE_URL}?{query}"


def fetch_open_meteo_archive_profile(week_number: int, timeout: float = 5.0) -> InputProfile:
    """Fetch real weather for the requested week from Open-Meteo archive."""

    week = _validate_week_number(week_number)
    year = latest_completed_iso_year_for_week(week)
    url = build_open_meteo_archive_url(year, week)
    try:
        with urlopen(url, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except OSError as exc:
        raise WeatherProfileError(f"open-meteo fetch failed: {exc}") from exc
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise WeatherProfileError("open-meteo response is not JSON") from exc
    return parse_open_meteo_hourly(payload, year, week)


def weather_profile_for_week(week_number: int, prefer_real: bool = True) -> InputProfile:
    """Return real weather when available, otherwise explicit fallback weather."""

    if not prefer_real:
        return synthetic_fallback_profile(week_number, reason="real weather disabled")
    try:
        return fetch_open_meteo_archive_profile(week_number)
    except Exception as exc:
        fallback = synthetic_fallback_profile(week_number, reason=str(exc))
        return replace(fallback, weather_source="synthetic_fallback")
