"""Input profiles for the weekly home optimizer POC."""

from __future__ import annotations

from typing import Sequence

from .schema import HOURS_PER_WEEK, InputProfile
from .spot import expand_period_indexes_to_hours, spot_indexes_for_week
from .weather import synthetic_fallback_profile, weather_profile_for_week


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
