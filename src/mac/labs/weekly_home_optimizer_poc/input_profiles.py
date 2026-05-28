"""Deterministic input profiles for the P0018 POC."""

from __future__ import annotations

import math
from typing import Sequence

from src.mac.services.spot_forecast.model import forecast_period_indexes

from .schema import HOURS_PER_PERIOD, HOURS_PER_WEEK, InputProfile, PERIODS_PER_WEEK


def _validate_week_number(week_number: int) -> int:
    week = int(week_number)
    if week < 1 or week > 53:
        raise ValueError("week must be in range 1..53")
    return week


def _validate_hourly(values: Sequence[float], name: str) -> tuple[float, ...]:
    if len(values) != HOURS_PER_WEEK:
        raise ValueError(f"{name} must contain {HOURS_PER_WEEK} values")
    return tuple(float(value) for value in values)


def build_input_profile(week_number: int) -> InputProfile:
    """Build a deterministic synthetic weather profile keyed by ISO week."""

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
    )


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
