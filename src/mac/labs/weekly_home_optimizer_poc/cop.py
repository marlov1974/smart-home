"""COP emulator and heat cost comparison for the P0023 weekly home POC."""

from __future__ import annotations

from typing import Sequence

from .schema import HOURS_PER_WEEK, HeatCostComparison


HEAT_COST_MODEL = "cop_emulated_v1"
COP_MODEL = "outdoor_temp_and_load_v1"
COP_MIN = 2.2
COP_MAX = 5.2


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _validate_hourly(values: Sequence[float], name: str) -> tuple[float, ...]:
    if len(values) != HOURS_PER_WEEK:
        raise ValueError(f"{name} must contain {HOURS_PER_WEEK} values")
    return tuple(float(value) for value in values)


def estimate_cop(outdoor_temp_c: float, heat_kw: float) -> float:
    """Estimate heat-pump COP from outdoor temperature and delivered thermal output."""

    temp = float(outdoor_temp_c)
    heat = float(heat_kw)
    if temp < 5.0:
        temp_adjustment = -0.055 * (5.0 - temp)
    else:
        temp_adjustment = min(0.4, 0.03 * (temp - 5.0))
    if heat <= 6.0:
        load_adjustment = 0.15
    elif heat <= 14.0:
        load_adjustment = 0.0
    elif heat <= 18.0:
        load_adjustment = -0.15
    else:
        load_adjustment = -0.35
    return round(_clamp(4.2 + temp_adjustment + load_adjustment, COP_MIN, COP_MAX), 4)


def _safe_avg_cop(thermal_kWh: float, electric_kWh: float) -> float | None:
    if electric_kWh <= 0.0:
        return None
    return round(thermal_kWh / electric_kWh, 4)


def compare_heat_costs(
    outdoor_temp_c: Sequence[float],
    heat_need_kWh: Sequence[float],
    optimized_heat_kWh: Sequence[float],
    heat_price_index: Sequence[float],
) -> HeatCostComparison:
    """Compare optimized heat cost with flat hourly heat-need production."""

    temps = _validate_hourly(outdoor_temp_c, "outdoor_temp_c")
    needs = _validate_hourly(heat_need_kWh, "heat_need_kWh")
    optimized = _validate_hourly(optimized_heat_kWh, "optimized_heat_kWh")
    prices = _validate_hourly(heat_price_index, "heat_price_index")
    cop_optimized = tuple(estimate_cop(temp, heat) for temp, heat in zip(temps, optimized))
    optimized_el_kWh = tuple(heat / cop for heat, cop in zip(optimized, cop_optimized))
    optimized_el_cost = tuple(el * price for el, price in zip(optimized_el_kWh, prices))
    flat_heat = tuple(needs)
    cop_flat = tuple(estimate_cop(temp, heat) for temp, heat in zip(temps, flat_heat))
    flat_el_kWh = tuple(heat / cop for heat, cop in zip(flat_heat, cop_flat))
    flat_el_cost = tuple(el * price for el, price in zip(flat_el_kWh, prices))

    optimized_el_kWh_total = sum(optimized_el_kWh)
    flat_el_kWh_total = sum(flat_el_kWh)
    optimized_el_cost_total = sum(optimized_el_cost)
    flat_el_cost_total = sum(flat_el_cost)
    warnings: list[str] = []
    if flat_el_cost_total <= 0.0:
        optimized_vs_flat_cost_pct = None
        optimized_saving_pct = None
        warnings.append("flat_heat_el_cost_zero")
    else:
        optimized_vs_flat_cost_pct = round(100.0 * optimized_el_cost_total / flat_el_cost_total, 2)
        optimized_saving_pct = round(100.0 - optimized_vs_flat_cost_pct, 2)

    return HeatCostComparison(
        heat_cost_model=HEAT_COST_MODEL,
        cop_model=COP_MODEL,
        cop_min=COP_MIN,
        cop_max=COP_MAX,
        optimized_heat_el_kWh=tuple(round(value, 4) for value in optimized_el_kWh),
        optimized_heat_el_cost=tuple(round(value, 4) for value in optimized_el_cost),
        cop_optimized=cop_optimized,
        flat_heat_kWh=tuple(round(value, 4) for value in flat_heat),
        flat_heat_el_kWh=tuple(round(value, 4) for value in flat_el_kWh),
        flat_heat_el_cost=tuple(round(value, 4) for value in flat_el_cost),
        cop_flat=cop_flat,
        optimized_heat_el_kWh_total=round(optimized_el_kWh_total, 4),
        flat_heat_el_kWh_total=round(flat_el_kWh_total, 4),
        optimized_heat_el_cost_total=round(optimized_el_cost_total, 4),
        flat_heat_el_cost_total=round(flat_el_cost_total, 4),
        optimized_vs_flat_cost_pct=optimized_vs_flat_cost_pct,
        optimized_saving_pct=optimized_saving_pct,
        avg_cop_optimized=_safe_avg_cop(sum(optimized), optimized_el_kWh_total),
        avg_cop_flat=_safe_avg_cop(sum(flat_heat), flat_el_kWh_total),
        heat_cost_comparison_warnings=tuple(warnings),
    )
