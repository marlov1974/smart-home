"""Heat planning model for the P0018 weekly optimizer POC."""

from __future__ import annotations

from typing import Sequence

from .schema import HOURS_PER_WEEK, HeatPlan


HOUSE_LOSS_KWH_DAY_PER_C = 12.5
BASE_INTERNAL_KWH_DAY = 42.0
MIN_HEAT_KWH_PER_H = 2.0
MAX_HEAT_KWH_PER_H = 25.0
HEAT_COST_MARGIN_KWH = 0.25


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


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


def _allocate_heat(heat_need: tuple[float, ...], spot_index: tuple[float, ...]) -> list[float]:
    total_need = sum(heat_need)
    if total_need <= 0:
        return [0.0] * HOURS_PER_WEEK
    available = [True] * HOURS_PER_WEEK
    heat = [0.0] * HOURS_PER_WEEK
    remaining = total_need
    while remaining > 1e-6 and any(available):
        weights = [1.0 / max(0.2, spot_index[i]) if available[i] else 0.0 for i in range(HOURS_PER_WEEK)]
        total_weight = sum(weights)
        if total_weight <= 0:
            break
        changed = False
        for i, weight in enumerate(weights):
            if not available[i]:
                continue
            proposed = heat[i] + remaining * weight / total_weight
            capped = _clamp(proposed, MIN_HEAT_KWH_PER_H, MAX_HEAT_KWH_PER_H)
            if capped >= MAX_HEAT_KWH_PER_H - 1e-9:
                available[i] = False
            if abs(capped - heat[i]) > 1e-9:
                changed = True
            heat[i] = capped
        new_remaining = total_need - sum(heat)
        if not changed or new_remaining >= remaining - 1e-6:
            break
        remaining = new_remaining
    scale = total_need / sum(heat) if sum(heat) > 0 else 0.0
    if scale < 1.0:
        heat = [value * scale for value in heat]
    return heat


def plan_heat(
    outdoor_temp_c: Sequence[float],
    spot_index: Sequence[float],
    current_house_temp: float,
) -> HeatPlan:
    """Plan hourly heat production and heat-derived ventilation cost weights."""

    temps = _validate_hourly(outdoor_temp_c, "outdoor_temp_c")
    spots = _validate_hourly(spot_index, "spot_index")
    heat_need = tuple(heat_need_for_hour(temp, float(current_house_temp)) for temp in temps)
    heat = _allocate_heat(heat_need, spots)
    battery_kWh = max(80.0, sum(heat_need) / 7.0)
    soc = battery_kWh
    soc_values: list[float] = []
    heat_cost_weight: list[float] = []
    for need, production, spot in zip(heat_need, heat, spots):
        soc = _clamp(soc + production - need, 0.0, battery_kWh)
        soc_values.append(round(100.0 * soc / battery_kWh, 2))
        if production > need + HEAT_COST_MARGIN_KWH:
            weight = 0.5 * spot
        elif production < need - HEAT_COST_MARGIN_KWH:
            weight = 2.0 * spot
        else:
            weight = spot
        heat_cost_weight.append(round(_clamp(weight, 0.25, 2.5), 4))
    return HeatPlan(
        heat_need_kWh=tuple(round(value, 4) for value in heat_need),
        heat_kWh=tuple(round(value, 4) for value in heat),
        heat_soc_pct=tuple(soc_values),
        heat_cost_weight=tuple(heat_cost_weight),
    )
