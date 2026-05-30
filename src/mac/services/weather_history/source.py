"""Open-Meteo source client for P0031 weather history."""

from __future__ import annotations

from datetime import date, datetime, timezone
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import WEATHER_VARIABLES, WeatherLocation, WeatherObservation
from .storage import SOURCE, SOURCE_MODEL, expected_utc_hours_for_range, iso_z, local_parts


ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def build_open_meteo_url(location: WeatherLocation, start_utc_date: date, end_utc_date: date) -> str:
    query = urlencode(
        {
            "latitude": f"{location.latitude:.4f}",
            "longitude": f"{location.longitude:.4f}",
            "start_date": start_utc_date.isoformat(),
            "end_date": end_utc_date.isoformat(),
            "hourly": ",".join(WEATHER_VARIABLES),
            "timezone": "GMT",
            "models": SOURCE_MODEL,
        }
    )
    return f"{ARCHIVE_URL}?{query}"


def fetch_open_meteo_range(
    location: WeatherLocation,
    start_utc_date: date,
    end_utc_date: date,
    timeout: float = 60.0,
) -> bytes:
    url = build_open_meteo_url(location, start_utc_date, end_utc_date)
    request = Request(url, headers={"User-Agent": "G2-Smart-Home-P0031/1.0"})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_open_meteo_range_with_retry(
    location: WeatherLocation,
    start_utc_date: date,
    end_utc_date: date,
    timeout: float = 60.0,
    attempts: int = 3,
) -> bytes:
    last_error: Exception | None = None
    for _ in range(max(1, attempts)):
        try:
            return fetch_open_meteo_range(location, start_utc_date, end_utc_date, timeout=timeout)
        except Exception as exc:  # pragma: no cover - live network failure path.
            last_error = exc
    raise RuntimeError(
        f"open-meteo fetch failed for {location.location_id} {start_utc_date}..{end_utc_date}: {last_error}"
    ) from last_error


def parse_open_meteo_response(
    payload: bytes | str,
    location: WeatherLocation,
    expected_hours: tuple[datetime, ...],
) -> list[WeatherObservation]:
    raw = payload.decode("utf-8") if isinstance(payload, bytes) else payload
    root = json.loads(raw)
    hourly = root.get("hourly")
    if not isinstance(hourly, dict):
        raise ValueError("missing hourly weather")
    times = hourly.get("time")
    if not isinstance(times, list):
        raise ValueError("missing hourly time array")
    for variable in WEATHER_VARIABLES:
        values = hourly.get(variable)
        if not isinstance(values, list):
            raise ValueError(f"missing hourly variable: {variable}")
        if len(values) != len(times):
            raise ValueError(f"hourly variable length mismatch: {variable}")

    by_time = {str(value): index for index, value in enumerate(times)}
    observations: list[WeatherObservation] = []
    for utc_dt in expected_hours:
        key = utc_dt.strftime("%Y-%m-%dT%H:%M")
        index = by_time.get(key)
        if index is None:
            raise ValueError(f"missing weather hour {key} for {location.location_id}")
        values: dict[str, float] = {}
        for variable in WEATHER_VARIABLES:
            value = hourly[variable][index]
            if value is None:
                raise ValueError(f"null {variable} at {key} for {location.location_id}")
            values[variable] = float(value)
        local_hour_start, local_date, local_hour, utc_offset, fold = local_parts(utc_dt)
        observations.append(
            WeatherObservation(
                location_id=location.location_id,
                utc_hour_start=iso_z(utc_dt),
                local_hour_start=local_hour_start,
                local_date=local_date,
                local_hour=local_hour,
                timezone="Europe/Stockholm",
                utc_offset=utc_offset,
                fold=fold,
                values=values,
                source_model=SOURCE_MODEL,
                source=SOURCE,
            )
        )
    return observations


def utc_request_dates_for_local_range(start_date: date, end_date: date) -> tuple[date, date]:
    hours = expected_utc_hours_for_range(start_date, end_date)
    return hours[0].date(), hours[-1].date()
