"""Discrete DP heat optimizer for the P0022 weekly home POC."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .schema import HOURS_PER_WEEK, HeatPlan


HEAT_MODES_KW = tuple(range(2, 23))


@dataclass(frozen=True)
class HeatOptimizerConfig:
    heat_modes_kw: tuple[int, ...] = HEAT_MODES_KW
    heat_soc_capacity_kWh: int = 300
    heat_soc_step_kWh: int = 1
    start_soc_pct: float = 100.0
    end_soc_min_pct: float = 50.0
    min_soc_pct: float = 0.0
    max_soc_pct: float = 100.0
    low_soc_threshold_pct: float = 25.0
    low_soc_penalty_scale: float = 40.0
    overflow_penalty_scale: float = 8.0


def default_heat_optimizer_config() -> HeatOptimizerConfig:
    """Return the P0022 default heat optimizer config."""

    return HeatOptimizerConfig()


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _validate_hourly(values: Sequence[float], name: str) -> tuple[float, ...]:
    if len(values) != HOURS_PER_WEEK:
        raise ValueError(f"{name} must contain {HOURS_PER_WEEK} values")
    return tuple(float(value) for value in values)


def low_soc_penalty(soc_pct: float, threshold_pct: float = 25.0, scale: float = 40.0) -> float:
    """Return convex comfort penalty below the low-SOC threshold."""

    if soc_pct >= threshold_pct:
        return 0.0
    distance = (threshold_pct - max(0.0, soc_pct)) / max(1.0, threshold_pct)
    return scale * distance * distance


def derive_heat_cost_weight(
    heat_need_kWh: float,
    heat_action_kw: float,
    heat_soc_pct: float,
    heat_price_index: float,
    margin: float = 0.25,
) -> float:
    """Derive the ventilation heat-cost signal from optimized heat state."""

    if heat_action_kw > heat_need_kWh + margin:
        multiplier = 0.5
    elif heat_action_kw < heat_need_kWh - margin:
        multiplier = 2.0
    else:
        multiplier = 1.0
    if heat_soc_pct < 25.0:
        multiplier = max(multiplier, 2.0)
    return round(_clamp(float(heat_price_index) * multiplier, 0.25, 2.5), 4)


def optimize_heat_dp(
    heat_need_kWh: Sequence[float],
    heat_price_index: Sequence[float],
    config: HeatOptimizerConfig | None = None,
) -> HeatPlan:
    """Optimize hourly heat output with discrete SOC dynamic programming."""

    cfg = config or default_heat_optimizer_config()
    needs = _validate_hourly(heat_need_kWh, "heat_need_kWh")
    prices = _validate_hourly(heat_price_index, "heat_price_index")
    capacity = int(cfg.heat_soc_capacity_kWh / cfg.heat_soc_step_kWh)
    start_state = int(round(capacity * cfg.start_soc_pct / 100.0))
    end_min_state = int(round(capacity * cfg.end_soc_min_pct / 100.0))
    states = range(capacity + 1)
    dp: dict[int, float] = {start_state: 0.0}
    back: list[dict[int, tuple[int, int, float, float]]] = []
    for hour in range(HOURS_PER_WEEK):
        next_dp: dict[int, float] = {}
        next_back: dict[int, tuple[int, int, float, float]] = {}
        need = needs[hour]
        price = prices[hour]
        for state, cost_so_far in dp.items():
            soc_kWh = state * cfg.heat_soc_step_kWh
            for mode in cfg.heat_modes_kw:
                raw_next = soc_kWh + float(mode) - need
                overflow = max(0.0, raw_next - cfg.heat_soc_capacity_kWh)
                clipped_next = _clamp(raw_next, 0.0, cfg.heat_soc_capacity_kWh)
                next_state = int(round(clipped_next / cfg.heat_soc_step_kWh))
                next_state = max(0, min(capacity, next_state))
                next_soc_pct = 100.0 * next_state / capacity
                energy_cost = float(mode) * price
                soc_cost = low_soc_penalty(next_soc_pct, cfg.low_soc_threshold_pct, cfg.low_soc_penalty_scale)
                overflow_cost = overflow * overflow * cfg.overflow_penalty_scale
                tie_break = 0.0001 * float(mode)
                cost = cost_so_far + energy_cost + soc_cost + overflow_cost + tie_break
                if cost < next_dp.get(next_state, float("inf")):
                    next_dp[next_state] = cost
                    next_back[next_state] = (state, int(mode), energy_cost, soc_cost + overflow_cost)
        dp = next_dp
        back.append(next_back)
    warnings: list[str] = []
    feasible_final = {state: cost for state, cost in dp.items() if state >= end_min_state}
    if feasible_final:
        final_state = min(feasible_final, key=feasible_final.get)
    else:
        final_state = min(dp, key=dp.get)
        warnings.append("end_soc_below_target")
    actions: list[int] = []
    soc_states: list[int] = []
    heat_cost_components: list[float] = []
    soc_penalty_components: list[float] = []
    state = final_state
    for hour in range(HOURS_PER_WEEK - 1, -1, -1):
        prev_state, mode, energy_cost, soc_cost = back[hour][state]
        actions.append(mode)
        soc_states.append(state)
        heat_cost_components.append(round(energy_cost, 4))
        soc_penalty_components.append(round(soc_cost, 4))
        state = prev_state
    actions.reverse()
    soc_states.reverse()
    heat_cost_components.reverse()
    soc_penalty_components.reverse()
    soc_pct = tuple(round(100.0 * state / capacity, 2) for state in soc_states)
    heat_cost_weight = tuple(
        derive_heat_cost_weight(need, action, soc, price)
        for need, action, soc, price in zip(needs, actions, soc_pct, prices)
    )
    if any(value <= 0.0 for value in soc_pct):
        warnings.append("heat_soc_reached_zero")
    return HeatPlan(
        heat_need_kWh=tuple(round(value, 4) for value in needs),
        heat_kWh=tuple(float(action) for action in actions),
        heat_soc_pct=soc_pct,
        heat_cost_weight=heat_cost_weight,
        heat_optimizer="discrete_dp",
        heat_modes_kw=tuple(cfg.heat_modes_kw),
        heat_soc_capacity_kWh=float(cfg.heat_soc_capacity_kWh),
        heat_soc_step_kWh=float(cfg.heat_soc_step_kWh),
        start_soc_pct=float(cfg.start_soc_pct),
        end_soc_min_pct=float(cfg.end_soc_min_pct),
        min_heat_soc_pct=round(min(soc_pct), 2),
        end_heat_soc_pct=round(soc_pct[-1], 2),
        heat_optimizer_warnings=tuple(dict.fromkeys(warnings)),
        heat_price_index=tuple(round(value, 4) for value in prices),
        heat_action_kw=tuple(actions),
        heat_dp_cost_component=tuple(heat_cost_components),
        soc_penalty_component=tuple(soc_penalty_components),
    )
