"""Read-only spot price source parsing for P0030."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone
import json
from typing import Any
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from .models import HourlySpotPrice


STOCKHOLM = ZoneInfo("Europe/Stockholm")
ELPRISETJUSTNU_URL = "https://www.elprisetjustnu.se/api/v1/prices/{year}/{month_day}_{area}.json"
SE_ELPRIS_COMPACT_URL = "https://se.elpris.eu/api/v1/prices/{year}/{month_day}_{area}.json?avg24"


def source_url(area: str, target_date: date, compact: bool = False) -> str:
    template = SE_ELPRIS_COMPACT_URL if compact else ELPRISETJUSTNU_URL
    return template.format(
        year=target_date.strftime("%Y"),
        month_day=target_date.strftime("%m-%d"),
        area=area,
    )


def fetch_source_day(area: str, target_date: date, timeout: float = 20.0) -> bytes:
    url = source_url(area, target_date)
    request = Request(url, headers={"User-Agent": "G2-Smart-Home-P0030/1.0"})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_source_day_with_retry(area: str, target_date: date, timeout: float = 45.0, attempts: int = 3) -> bytes:
    last_error: Exception | None = None
    for _ in range(max(1, attempts)):
        try:
            return fetch_source_day(area, target_date, timeout=timeout)
        except Exception as exc:  # pragma: no cover - exercised by live source failures.
            last_error = exc
    raise RuntimeError(f"fetch failed for {area} {target_date}: {last_error}") from last_error


def parse_price_day(payload: bytes | str, area: str, source: str) -> list[HourlySpotPrice]:
    raw = payload.decode("utf-8") if isinstance(payload, bytes) else payload
    parsed = json.loads(raw)
    if isinstance(parsed, list):
        return _parse_object_list(parsed, area, source)
    if isinstance(parsed, dict) and isinstance(parsed.get("p"), list):
        return _parse_compact(parsed, area, source)
    raise ValueError("unsupported spot price payload shape")


def _parse_object_list(items: list[Any], area: str, source: str) -> list[HourlySpotPrice]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"price item {index} is not an object")
        local_dt = _parse_local_timestamp(item.get("time_start"))
        hour_dt = local_dt.replace(minute=0, second=0, microsecond=0)
        buckets[hour_dt.isoformat()].append(item)

    rows: list[HourlySpotPrice] = []
    resolution = "quarter-hour" if any(len(values) > 1 for values in buckets.values()) else "hour"
    for hour_key in sorted(buckets):
        samples = buckets[hour_key]
        local_hour = datetime.fromisoformat(hour_key)
        rows.append(
            _row_from_values(
                area=area,
                local_hour=local_hour,
                sek_values=[_float(sample.get("SEK_per_kWh"), "SEK_per_kWh") for sample in samples],
                eur_values=[_optional_float(sample.get("EUR_per_kWh"), "EUR_per_kWh") for sample in samples],
                exr_values=[_optional_float(sample.get("EXR"), "EXR") for sample in samples],
                source=source,
                source_resolution=resolution,
                samples=len(samples),
            )
        )
    return rows


def _parse_compact(root: dict[str, Any], area: str, source: str) -> list[HourlySpotPrice]:
    t0 = _parse_local_timestamp(root.get("t0"))
    step_seconds = int(root.get("s"))
    prices = [_float(value, "p") for value in root["p"]]
    if step_seconds not in (900, 3600):
        raise ValueError(f"unsupported compact step seconds: {step_seconds}")

    buckets: dict[str, list[float]] = defaultdict(list)
    for index, price in enumerate(prices):
        local_dt = (t0.astimezone(timezone.utc).timestamp() + index * step_seconds)
        sample_local = datetime.fromtimestamp(local_dt, timezone.utc).astimezone(STOCKHOLM)
        hour_dt = sample_local.replace(minute=0, second=0, microsecond=0)
        buckets[hour_dt.isoformat()].append(price)

    resolution = "quarter-hour" if step_seconds == 900 else "hour"
    return [
        _row_from_values(
            area=area,
            local_hour=datetime.fromisoformat(hour_key),
            sek_values=values,
            eur_values=[],
            exr_values=[],
            source=source,
            source_resolution=resolution,
            samples=len(values),
        )
        for hour_key, values in sorted(buckets.items())
    ]


def _row_from_values(
    *,
    area: str,
    local_hour: datetime,
    sek_values: list[float],
    eur_values: list[float | None],
    exr_values: list[float | None],
    source: str,
    source_resolution: str,
    samples: int,
) -> HourlySpotPrice:
    if not sek_values:
        raise ValueError("hour has no SEK price samples")
    utc_hour = local_hour.astimezone(timezone.utc)
    return HourlySpotPrice(
        area=area,
        utc_hour_start=utc_hour.strftime("%Y-%m-%dT%H:00Z"),
        local_hour_start=local_hour.isoformat(),
        local_date=local_hour.date().isoformat(),
        local_hour=local_hour.hour,
        utc_offset=_offset_text(local_hour),
        fold=int(getattr(local_hour, "fold", 0)),
        price_sek_per_kwh=sum(sek_values) / len(sek_values),
        price_eur_per_kwh=_mean_optional(eur_values),
        exchange_rate=_mean_optional(exr_values),
        source=source,
        source_resolution=source_resolution,
        samples=samples,
    )


def _parse_local_timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp is missing or not a string")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include UTC offset")
    return parsed


def _float(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} is not numeric") from exc


def _optional_float(value: Any, field: str) -> float | None:
    if value is None:
        return None
    return _float(value, field)


def _mean_optional(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return sum(present) / len(present)


def _offset_text(dt: datetime) -> str:
    offset = dt.strftime("%z")
    return f"{offset[:3]}:{offset[3:]}"
