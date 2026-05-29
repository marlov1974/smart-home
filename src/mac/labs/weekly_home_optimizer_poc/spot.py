"""Hourly spot model with actual-price patching for the weekly home POC."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Mapping, Sequence
from zoneinfo import ZoneInfo

from src.mac.services.spot_forecast.model import forecast_period_indexes

from .schema import HOURS_PER_PERIOD, HOURS_PER_WEEK, PERIODS_PER_WEEK, SpotPlan


SPOT_MODEL = "hourly_forecast_with_actual_horizon_patch_v1"
SPOT_RESOLUTION = "hourly"
SPOT_PATCH_STRATEGY = "actual_shape_forecast_sum_horizon"
DEFAULT_ACTUAL_HORIZON_HOURS = 20
SPOT_FIXTURE_YEAR = 2025
SPOT_TIMEZONE = ZoneInfo("Europe/Stockholm")
DEFAULT_ACTUAL_SPOT_PATH = Path("data/spot/spot_2025_hourly_europe_stockholm.csv")


@dataclass(frozen=True)
class ActualSpotPrice:
    utc_hour_start: str
    local_hour_start: str
    local_wall_hour: str
    utc_offset: str
    fold: int
    quarter_count: int
    price_mean: float
    price_min: float
    price_max: float


def validate_week_number(week_number: int) -> int:
    """Validate the POC week range."""

    week = int(week_number)
    if week < 1 or week > 53:
        raise ValueError("week must be in range 1..53")
    return week


def expand_period_indexes_to_hours(period_indexes: Sequence[float]) -> tuple[float, ...]:
    """Expand 21 operational 8h period indexes to 168 hourly values."""

    if len(period_indexes) != PERIODS_PER_WEEK:
        raise ValueError(f"period_indexes must contain {PERIODS_PER_WEEK} values")
    hourly: list[float] = []
    for value in period_indexes:
        hourly.extend([float(value)] * HOURS_PER_PERIOD)
    return tuple(hourly)


def forecast_spot_index_for_week(week_number: int) -> tuple[float, ...]:
    """Build the hourly forecast baseline for a requested week."""

    period_indexes = forecast_period_indexes(validate_week_number(week_number))
    return expand_period_indexes_to_hours(period_indexes)


def resolve_week_utc_hours(week_number: int, iso_year: int = SPOT_FIXTURE_YEAR) -> tuple[str, ...]:
    """Return 168 chronological UTC hour keys for an operational week."""

    week = validate_week_number(week_number)
    try:
        start_local = datetime.fromisocalendar(int(iso_year), week, 1).replace(
            hour=6,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=SPOT_TIMEZONE,
        )
    except ValueError:
        return ()
    start_utc = start_local.astimezone(timezone.utc)
    return tuple(
        (start_utc + timedelta(hours=hour)).strftime("%Y-%m-%dT%H:00Z")
        for hour in range(HOURS_PER_WEEK)
    )


def load_actual_spot_prices(path: Path | str = DEFAULT_ACTUAL_SPOT_PATH) -> dict[str, ActualSpotPrice]:
    """Load actual hourly spot prices keyed by UTC hour start."""

    fixture_path = Path(path)
    if not fixture_path.exists():
        raise FileNotFoundError(f"actual spot fixture missing: {fixture_path}")

    prices: dict[str, ActualSpotPrice] = {}
    with fixture_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            utc_hour_start = row["utc_hour_start"]
            if utc_hour_start in prices:
                raise ValueError(f"duplicate utc_hour_start in actual spot fixture: {utc_hour_start}")
            quarter_count = int(row["quarter_count"])
            if quarter_count != 4:
                raise ValueError(f"incomplete actual spot fixture hour at line {row_number}: {utc_hour_start}")
            prices[utc_hour_start] = ActualSpotPrice(
                utc_hour_start=utc_hour_start,
                local_hour_start=row["local_hour_start"],
                local_wall_hour=row["local_wall_hour"],
                utc_offset=row["utc_offset"],
                fold=int(row["fold"]),
                quarter_count=quarter_count,
                price_mean=float(row["price_mean"]),
                price_min=float(row["price_min"]),
                price_max=float(row["price_max"]),
            )
    return prices


def normalize_actual_indexes(
    actual_prices_by_index: Mapping[int, float],
    forecast_index: Sequence[float],
) -> tuple[dict[int, float], dict[int, float], tuple[str, ...]]:
    """Normalize actual prices onto the same sum basis as matching forecast indexes."""

    if not actual_prices_by_index:
        return {}, {}, ("no_actual_overlap",)
    actual_mean = sum(actual_prices_by_index.values()) / len(actual_prices_by_index)
    if actual_mean == 0.0:
        return {}, {}, ("actual_mean_zero",)
    proto = {
        index: float(actual_price) / actual_mean
        for index, actual_price in actual_prices_by_index.items()
    }
    proto_sum = sum(proto.values())
    if proto_sum == 0.0:
        return proto, {}, ("actual_proto_sum_zero",)
    forecast_sum = sum(float(forecast_index[index]) for index in actual_prices_by_index)
    scale = forecast_sum / proto_sum
    normalized = {index: value * scale for index, value in proto.items()}
    return proto, normalized, ()


def patch_forecast_with_actual_prices(
    forecast_index: Sequence[float],
    utc_hours: Sequence[str],
    actual_prices: Mapping[str, ActualSpotPrice],
    actual_fixture_path: Path | str = DEFAULT_ACTUAL_SPOT_PATH,
    actual_horizon_hours: int = DEFAULT_ACTUAL_HORIZON_HOURS,
) -> SpotPlan:
    """Patch only the known actual horizon and compute future outcome diagnostics."""

    if len(forecast_index) != HOURS_PER_WEEK:
        raise ValueError(f"forecast_index must contain {HOURS_PER_WEEK} values")
    if len(utc_hours) != HOURS_PER_WEEK:
        warnings = ("actual_fixture_week_unavailable",)
        return _forecast_only_plan(forecast_index, actual_fixture_path, actual_horizon_hours, warnings)

    forecast = tuple(float(value) for value in forecast_index)
    actual_price: list[float | None] = [None] * HOURS_PER_WEEK
    actual_proto_index: list[float | None] = [None] * HOURS_PER_WEEK
    patched_actual_index: list[float | None] = [None] * HOURS_PER_WEEK
    actual_outcome_index: list[float | None] = [None] * HOURS_PER_WEEK
    actual_available = [False] * HOURS_PER_WEEK
    forecast_error_index: list[float | None] = [None] * HOURS_PER_WEEK
    forecast_error_pct: list[float | None] = [None] * HOURS_PER_WEEK
    spot_planning_index = list(forecast)
    spot_planning_source = ["forecast"] * HOURS_PER_WEEK
    warnings: list[str] = []
    horizon = max(0, min(int(actual_horizon_hours), HOURS_PER_WEEK))

    actual_by_index: dict[int, float] = {}
    horizon_actual_by_index: dict[int, float] = {}
    for index, utc_hour in enumerate(utc_hours):
        actual = actual_prices.get(utc_hour)
        if actual is None:
            continue
        actual_price[index] = actual.price_mean
        actual_available[index] = True
        actual_by_index[index] = actual.price_mean
        if index < horizon:
            horizon_actual_by_index[index] = actual.price_mean

    outcome_proto, outcome_normalized, outcome_warnings = normalize_actual_indexes(actual_by_index, forecast)
    if outcome_warnings and actual_by_index:
        warnings.extend(f"outcome_{warning}" for warning in outcome_warnings)
    for index, value in outcome_proto.items():
        actual_proto_index[index] = value
    for index, value in outcome_normalized.items():
        actual_outcome_index[index] = value
        forecast_error_index[index] = value - forecast[index]
        if forecast[index] != 0.0:
            forecast_error_pct[index] = (value - forecast[index]) / forecast[index] * 100

    horizon_proto, horizon_normalized, horizon_warnings = normalize_actual_indexes(horizon_actual_by_index, forecast)
    if horizon_warnings:
        warnings.extend(horizon_warnings)
    for index, value in horizon_proto.items():
        actual_proto_index[index] = value
    for index, value in horizon_normalized.items():
        patched_actual_index[index] = value
        spot_planning_index[index] = value
        spot_planning_source[index] = "actual_horizon_patched"

    if len(horizon_actual_by_index) < horizon:
        warnings.append("actual_horizon_short")

    return _spot_plan(
        spot_index=tuple(spot_planning_index),
        spot_source=tuple(spot_planning_source),
        spot_planning_index=tuple(spot_planning_index),
        spot_planning_source=tuple(spot_planning_source),
        spot_forecast_index=forecast,
        spot_actual_price=tuple(actual_price),
        spot_actual_proto_index=tuple(actual_proto_index),
        spot_patched_actual_index=tuple(patched_actual_index),
        spot_actual_outcome_index=tuple(actual_outcome_index),
        spot_actual_available=tuple(actual_available),
        spot_forecast_error_index=tuple(forecast_error_index),
        spot_forecast_error_pct=tuple(forecast_error_pct),
        actual_fixture_path=actual_fixture_path,
        actual_horizon_hours=horizon,
        actual_known_hours=len(horizon_actual_by_index),
        forecast_hours=HOURS_PER_WEEK - len(horizon_normalized),
        patched_hours=sum(1 for source in spot_planning_source if source == "actual_horizon_patched"),
        warnings=tuple(warnings),
    )


def build_spot_plan(
    week_number: int,
    actual_fixture_path: Path | str = DEFAULT_ACTUAL_SPOT_PATH,
) -> SpotPlan:
    """Build the complete hourly spot plan for a requested week."""

    return build_spot_plan_for_window(week_number, SPOT_FIXTURE_YEAR, actual_fixture_path, DEFAULT_ACTUAL_HORIZON_HOURS)


def build_spot_plan_for_window(
    week_number: int,
    iso_year: int = SPOT_FIXTURE_YEAR,
    actual_fixture_path: Path | str = DEFAULT_ACTUAL_SPOT_PATH,
    actual_horizon_hours: int = DEFAULT_ACTUAL_HORIZON_HOURS,
) -> SpotPlan:
    """Build an hourly spot plan for a fixture year and known actual horizon."""

    forecast_index = forecast_spot_index_for_week(week_number)
    utc_hours = resolve_week_utc_hours(week_number, iso_year=iso_year)
    actual_prices = load_actual_spot_prices(actual_fixture_path)
    return patch_forecast_with_actual_prices(
        forecast_index,
        utc_hours,
        actual_prices,
        actual_fixture_path,
        actual_horizon_hours=actual_horizon_hours,
    )


def spot_indexes_for_week(week_number: int) -> tuple[float, ...]:
    """Return final 168 hourly spot indexes for compatibility callers."""

    return build_spot_plan(week_number).spot_index


def _forecast_only_plan(
    forecast_index: Sequence[float],
    actual_fixture_path: Path | str,
    actual_horizon_hours: int,
    warnings: tuple[str, ...],
) -> SpotPlan:
    forecast = tuple(float(value) for value in forecast_index)
    empty_debug = tuple(None for _ in range(HOURS_PER_WEEK))
    unavailable = tuple(False for _ in range(HOURS_PER_WEEK))
    return _spot_plan(
        spot_index=forecast,
        spot_source=tuple("forecast" for _ in range(HOURS_PER_WEEK)),
        spot_planning_index=forecast,
        spot_planning_source=tuple("forecast" for _ in range(HOURS_PER_WEEK)),
        spot_forecast_index=forecast,
        spot_actual_price=empty_debug,
        spot_actual_proto_index=empty_debug,
        spot_patched_actual_index=empty_debug,
        spot_actual_outcome_index=empty_debug,
        spot_actual_available=unavailable,
        spot_forecast_error_index=empty_debug,
        spot_forecast_error_pct=empty_debug,
        actual_fixture_path=actual_fixture_path,
        actual_horizon_hours=actual_horizon_hours,
        actual_known_hours=0,
        forecast_hours=HOURS_PER_WEEK,
        patched_hours=0,
        warnings=warnings,
    )


def _spot_plan(
    *,
    spot_index: tuple[float, ...],
    spot_source: tuple[str, ...],
    spot_planning_index: tuple[float, ...],
    spot_planning_source: tuple[str, ...],
    spot_forecast_index: tuple[float, ...],
    spot_actual_price: tuple[float | None, ...],
    spot_actual_proto_index: tuple[float | None, ...],
    spot_patched_actual_index: tuple[float | None, ...],
    spot_actual_outcome_index: tuple[float | None, ...],
    spot_actual_available: tuple[bool, ...],
    spot_forecast_error_index: tuple[float | None, ...],
    spot_forecast_error_pct: tuple[float | None, ...],
    actual_fixture_path: Path | str,
    actual_horizon_hours: int,
    actual_known_hours: int,
    forecast_hours: int,
    patched_hours: int,
    warnings: tuple[str, ...],
) -> SpotPlan:
    return SpotPlan(
        spot_index=spot_index,
        spot_source=spot_source,
        spot_planning_index=spot_planning_index,
        spot_planning_source=spot_planning_source,
        spot_forecast_index=spot_forecast_index,
        spot_actual_price=spot_actual_price,
        spot_actual_proto_index=spot_actual_proto_index,
        spot_patched_actual_index=spot_patched_actual_index,
        spot_actual_outcome_index=spot_actual_outcome_index,
        spot_actual_available=spot_actual_available,
        spot_forecast_error_index=spot_forecast_error_index,
        spot_forecast_error_pct=spot_forecast_error_pct,
        spot_model=SPOT_MODEL,
        spot_resolution=SPOT_RESOLUTION,
        spot_actual_fixture_path=str(actual_fixture_path),
        spot_actual_horizon_hours=int(actual_horizon_hours),
        spot_actual_known_hours=int(actual_known_hours),
        spot_forecast_hours=int(forecast_hours),
        spot_actual_patched_hours=int(patched_hours),
        spot_patch_strategy=SPOT_PATCH_STRATEGY,
        spot_index_min=min(spot_index),
        spot_index_max=max(spot_index),
        spot_index_avg=sum(spot_index) / len(spot_index),
        spot_patch_warnings=warnings,
    )
