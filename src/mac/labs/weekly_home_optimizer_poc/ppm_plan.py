"""PPM, ventilation and RH-policy optimizer for the P0018 POC."""

from __future__ import annotations

import math
from typing import Sequence

from .schema import HOURS_PER_WEEK, PpmPlan, SUPPLY_MODES, VENT_COST_BY_SUPPLY


HOUSE_VOLUME_M3 = 780.0
OUTDOOR_PPM = 420.0
DEFAULT_OCCUPANCY_GAIN_PPM_H = 70.0
BASE_PEOPLE = 3.0
DEFAULT_PEOPLE = 3.0
MIN_PEOPLE = 0.0
MAX_PEOPLE = 20.0
STATE_MIN_PPM = 400
STATE_MAX_PPM = 1400
STATE_STEP_PPM = 10

_PPM_COST_POINTS = (
    (500, 0),
    (525, 1),
    (550, 3),
    (575, 6),
    (600, 10),
    (625, 15),
    (650, 21),
    (675, 28),
    (700, 36),
    (725, 45),
    (750, 55),
    (775, 66),
    (800, 78),
    (825, 91),
    (850, 105),
    (875, 120),
    (900, 136),
    (925, 153),
    (950, 171),
    (975, 190),
    (1000, 210),
)


def validate_people(people: float | int | str) -> float:
    """Validate public POC people input."""

    try:
        value = float(people)
    except (TypeError, ValueError) as exc:
        raise ValueError("people invalid") from exc
    if value < MIN_PEOPLE or value > MAX_PEOPLE:
        raise ValueError("people invalid")
    return value


def occupancy_gain_for_people(people: float | int | str = DEFAULT_PEOPLE) -> float:
    """Scale PPM occupancy pressure from people count."""

    value = validate_people(people)
    return DEFAULT_OCCUPANCY_GAIN_PPM_H * value / BASE_PEOPLE


def _validate_hourly(values: Sequence[float], name: str) -> tuple[float, ...]:
    if len(values) != HOURS_PER_WEEK:
        raise ValueError(f"{name} must contain {HOURS_PER_WEEK} values")
    return tuple(float(value) for value in values)


def flow_lps_for_supply(supply_pct: int) -> float:
    """Convert POC supply percentage to flow in l/s."""

    return float(supply_pct) / 100.0 * 240.0


def rh_weight_for_hour(outdoor_temp_c: float, outdoor_rh_pct: float) -> float:
    """Convert weather to an RH ventilation policy weight."""

    if outdoor_temp_c <= -4.0 and outdoor_rh_pct >= 70.0:
        return 2.5
    if outdoor_temp_c <= 5.0 and outdoor_rh_pct >= 60.0:
        return 1.5
    if outdoor_temp_c >= 11.0 and outdoor_rh_pct >= 62.0:
        return -1.0
    return 0.0


def ppm_after_hour(
    ppm: float,
    supply_pct: int,
    occupancy_gain_ppm_h: float = DEFAULT_OCCUPANCY_GAIN_PPM_H,
) -> float:
    """Compute one-hour PPM after occupancy gain and ventilation dilution."""

    flow_lps = flow_lps_for_supply(supply_pct)
    removal = flow_lps * 3.6 / HOUSE_VOLUME_M3 * max(0.0, ppm - OUTDOOR_PPM)
    return max(OUTDOOR_PPM, ppm + float(occupancy_gain_ppm_h) - removal)


def ppm_cost(ppm: float) -> float:
    """Return discomfort cost for an absolute PPM value."""

    value = float(ppm)
    if value <= 500.0:
        return 0.0
    if value > 1000.0:
        steps = math.ceil((value - 1000.0) / 25.0)
        return 210.0 + 25.0 * steps + steps * steps
    for index in range(1, len(_PPM_COST_POINTS)):
        low_ppm, low_cost = _PPM_COST_POINTS[index - 1]
        high_ppm, high_cost = _PPM_COST_POINTS[index]
        if value <= high_ppm:
            ratio = (value - low_ppm) / (high_ppm - low_ppm)
            return low_cost + ratio * (high_cost - low_cost)
    return 210.0


def _state_for_ppm(ppm: float) -> int:
    rounded = int(round(float(ppm) / STATE_STEP_PPM) * STATE_STEP_PPM)
    return max(STATE_MIN_PPM, min(STATE_MAX_PPM, rounded))


def _hour_cost(ppm_after: float, supply_pct: int, heat_weight: float, rh_weight: float) -> float:
    vent_cost = VENT_COST_BY_SUPPLY[supply_pct]
    tie_break = 0.015 * (supply_pct - min(SUPPLY_MODES))
    high_supply_penalty = 0.0
    if rh_weight < 0.0 and supply_pct > 49:
        high_supply_penalty = 2.0 * (supply_pct - 49) ** 2
    return (
        ppm_cost(ppm_after)
        + heat_weight * vent_cost
        + rh_weight * vent_cost
        + tie_break
        + high_supply_penalty
    )


def optimize_ppm_plan(
    heat_cost_weight: Sequence[float],
    rh_weight: Sequence[float],
    current_ppm: float,
    occupancy_gain_ppm_h: float = DEFAULT_OCCUPANCY_GAIN_PPM_H,
) -> PpmPlan:
    """Choose normal-operation supply modes with dynamic programming."""

    heat_weights = _validate_hourly(heat_cost_weight, "heat_cost_weight")
    rh_weights = _validate_hourly(rh_weight, "rh_weight")
    states = list(range(STATE_MIN_PPM, STATE_MAX_PPM + STATE_STEP_PPM, STATE_STEP_PPM))
    dp: dict[int, float] = {_state_for_ppm(current_ppm): 0.0}
    back: list[dict[int, tuple[int, int]]] = []
    for hour in range(HOURS_PER_WEEK):
        next_dp: dict[int, float] = {}
        next_back: dict[int, tuple[int, int]] = {}
        for state, cost_so_far in dp.items():
            for supply in SUPPLY_MODES:
                next_ppm = ppm_after_hour(state, supply, occupancy_gain_ppm_h)
                next_state = _state_for_ppm(next_ppm)
                cost = cost_so_far + _hour_cost(next_ppm, supply, heat_weights[hour], rh_weights[hour])
                if cost < next_dp.get(next_state, float("inf")):
                    next_dp[next_state] = cost
                    next_back[next_state] = (state, supply)
        dp = next_dp
        back.append(next_back)
    state = min(dp, key=dp.get)
    supplies: list[int] = []
    for hour in range(HOURS_PER_WEEK - 1, -1, -1):
        prev_state, supply = back[hour][state]
        supplies.append(supply)
        state = prev_state
    supplies.reverse()
    return _simulate_ppm_outputs(supplies, heat_weights, rh_weights, current_ppm, occupancy_gain_ppm_h)


def _simulate_ppm_outputs(
    supplies: Sequence[int],
    heat_weights: tuple[float, ...],
    rh_weights: tuple[float, ...],
    current_ppm: float,
    occupancy_gain_ppm_h: float,
) -> PpmPlan:
    ppm = float(current_ppm)
    flow_lps: list[float] = []
    vent_cost: list[float] = []
    ppm_delta: list[float] = []
    ppm_absolute: list[float] = []
    rh_delta: list[float] = []
    ppm_costs: list[float] = []
    heat_vent_cost: list[float] = []
    rh_cost: list[float] = []
    total_cost: list[float] = []
    for hour, supply in enumerate(supplies):
        after = ppm_after_hour(ppm, supply, occupancy_gain_ppm_h)
        delta = after - ppm
        vent = VENT_COST_BY_SUPPLY[int(supply)]
        pcost = ppm_cost(after)
        hcost = heat_weights[hour] * vent
        rcost = rh_weights[hour] * vent
        flow_lps.append(round(flow_lps_for_supply(int(supply)), 2))
        vent_cost.append(vent)
        ppm_delta.append(round(delta, 2))
        ppm_absolute.append(round(after, 2))
        rh_delta.append(round(-rh_weights[hour] * (int(supply) - 25) / 30.0, 3))
        ppm_costs.append(round(pcost, 3))
        heat_vent_cost.append(round(hcost, 3))
        rh_cost.append(round(rcost, 3))
        total_cost.append(round(pcost + hcost + rcost, 3))
        ppm = after
    return PpmPlan(
        supply_pct=tuple(int(value) for value in supplies),
        flow_lps=tuple(flow_lps),
        vent_cost=tuple(vent_cost),
        ppm_delta=tuple(ppm_delta),
        ppm_absolute=tuple(ppm_absolute),
        rh_delta=tuple(rh_delta),
        ppm_cost=tuple(ppm_costs),
        heat_vent_cost=tuple(heat_vent_cost),
        rh_cost=tuple(rh_cost),
        total_cost=tuple(total_cost),
    )
