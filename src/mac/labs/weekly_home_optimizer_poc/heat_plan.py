"""Heat planning model for the weekly optimizer POC."""

from __future__ import annotations

from typing import Sequence

from .heat_optimizer import optimize_heat_dp
from .schema import HOURS_PER_WEEK, HeatPlan


HOUSE_LOSS_KWH_DAY_PER_C = 12.5
BASE_INTERNAL_KWH_DAY = 42.0


def _validate_hourly(values: Sequence[float], name: str) -> tuple[float, ...]:
    if len(values) != HOURS_PER_WEEK:
        raise ValueError(f"{name} must contain {HOURS_PER_WEEK} values")
    return tuple(float(value) for value in values)


def heat_need_for_hour(outdoor_temp_c: float, set_temp_c: float) -> float:
    """Calculate the package heat-need approximation for one hour."""

    heat_need_day_kWh = max(
        0.0,
        HOUSE_LOSS_KWH_DAY_PER_C * (set_temp_c - outdoor_temp_c) - BASE_INTERNAL_KWH_DAY,
    )
    return heat_need_day_kWh / 24.0


def plan_heat(
    outdoor_temp_c: Sequence[float],
    spot_index: Sequence[float],
    current_house_temp: float,
) -> HeatPlan:
    """Plan hourly heat production and heat-derived ventilation cost weights."""

    temps = _validate_hourly(outdoor_temp_c, "outdoor_temp_c")
    spots = _validate_hourly(spot_index, "spot_index")
    heat_need = tuple(heat_need_for_hour(temp, float(current_house_temp)) for temp in temps)
    return optimize_heat_dp(heat_need, spots)
