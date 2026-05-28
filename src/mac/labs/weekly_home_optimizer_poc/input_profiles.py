"""Input profiles for the weekly home optimizer POC."""

from __future__ import annotations

from typing import Sequence

from src.mac.services.spot_forecast.model import forecast_period_indexes

from .schema import HOURS_PER_PERIOD, HOURS_PER_WEEK, InputProfile, PERIODS_PER_WEEK
from .weather import synthetic_fallback_profile, weather_profile_for_week


def _validate_week_number(week_number: int) -> int:
    week = int(week_number)
    if week < 1 or week > 53:
        raise ValueError("week must be in range 1..53")
    return week


def _validate_hourly(values: Sequence[float], name: str) -> tuple[float, ...]:
    if len(values) != HOURS_PER_WEEK:
        raise ValueError(f"{name} must contain {HOURS_PER_WEEK} values")
    return tuple(float(value) for value in values)


def build_input_profile(week_number: int, prefer_real_weather: bool = True) -> InputProfile:
    """Build a weather profile with real-weather preference and explicit fallback."""

    return weather_profile_for_week(week_number, prefer_real=prefer_real_weather)


def build_fixture_input_profile(week_number: int) -> InputProfile:
    """Build deterministic fixture weather for tests and offline development."""

    return synthetic_fallback_profile(week_number, reason="fixture weather requested")


def expand_period_indexes_to_hours(period_indexes: Sequence[float]) -> tuple[float, ...]:
    """Expand 21 operational 8h period indexes to 168 hourly values."""

    if len(period_indexes) != PERIODS_PER_WEEK:
        raise ValueError(f"period_indexes must contain {PERIODS_PER_WEEK} values")
    hourly: list[float] = []
    for value in period_indexes:
        hourly.extend([float(value)] * HOURS_PER_PERIOD)
    return tuple(hourly)


def spot_indexes_for_week(week_number: int) -> tuple[float, ...]:
    """Return 168 hourly spot indexes by reusing the P0017 model."""

    period_indexes = forecast_period_indexes(_validate_week_number(week_number))
    return expand_period_indexes_to_hours(period_indexes)
