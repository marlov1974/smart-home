"""Data structures for the P0018 weekly home optimizer POC."""

from __future__ import annotations

from dataclasses import dataclass


HOURS_PER_WEEK = 168
PERIODS_PER_WEEK = 21
HOURS_PER_PERIOD = 8
SUPPLY_MODES = (25, 28, 31, 34, 37, 40, 43, 46, 49, 52, 55)
VENT_COST_BY_SUPPLY = {
    25: 0.0,
    28: 1.0,
    31: 3.0,
    34: 6.0,
    37: 10.0,
    40: 15.0,
    43: 21.0,
    46: 28.0,
    49: 36.0,
    52: 45.0,
    55: 55.0,
}
REQUIRED_COLUMNS = (
    "hour",
    "weekday_hour",
    "outdoor_temp_c",
    "outdoor_rh_pct",
    "spot_index",
    "spot_source",
    "spot_planning_index",
    "spot_planning_source",
    "spot_forecast_index",
    "spot_actual_price",
    "spot_actual_proto_index",
    "spot_patched_actual_index",
    "spot_actual_outcome_index",
    "spot_actual_available",
    "spot_forecast_error_index",
    "spot_forecast_error_pct",
    "heat_need_kWh",
    "heat_kWh",
    "heat_soc_pct",
    "heat_cost_weight",
    "rh_weight",
    "supply_pct",
    "flow_lps",
    "vent_cost",
    "ppm_delta",
    "ppm_absolute",
    "rh_delta",
    "ppm_cost",
    "heat_vent_cost",
    "rh_cost",
    "total_cost",
)


@dataclass(frozen=True)
class InputProfile:
    week_number: int
    outdoor_temp_c: tuple[float, ...]
    outdoor_rh_pct: tuple[float, ...]
    weather_source: str
    weather_provider: str
    weather_profile_strategy: str
    weather_profile_year: int | None = None
    weather_fallback_reason: str | None = None


@dataclass(frozen=True)
class HeatPlan:
    heat_need_kWh: tuple[float, ...]
    heat_kWh: tuple[float, ...]
    heat_soc_pct: tuple[float, ...]
    heat_cost_weight: tuple[float, ...]
    heat_optimizer: str = "heuristic"
    heat_modes_kw: tuple[int, ...] = ()
    heat_soc_capacity_kWh: float = 0.0
    heat_soc_step_kWh: float = 0.0
    start_soc_pct: float = 0.0
    end_soc_min_pct: float = 0.0
    min_heat_soc_pct: float = 0.0
    end_heat_soc_pct: float = 0.0
    heat_optimizer_warnings: tuple[str, ...] = ()
    heat_price_index: tuple[float, ...] = ()
    heat_action_kw: tuple[int, ...] = ()
    heat_dp_cost_component: tuple[float, ...] = ()
    soc_penalty_component: tuple[float, ...] = ()


@dataclass(frozen=True)
class PpmPlan:
    supply_pct: tuple[int, ...]
    flow_lps: tuple[float, ...]
    vent_cost: tuple[float, ...]
    ppm_delta: tuple[float, ...]
    ppm_absolute: tuple[float, ...]
    rh_delta: tuple[float, ...]
    ppm_cost: tuple[float, ...]
    heat_vent_cost: tuple[float, ...]
    rh_cost: tuple[float, ...]
    total_cost: tuple[float, ...]


@dataclass(frozen=True)
class HeatCostComparison:
    heat_cost_model: str
    cop_model: str
    cop_min: float
    cop_max: float
    optimized_heat_el_kWh: tuple[float, ...]
    optimized_heat_el_cost: tuple[float, ...]
    cop_optimized: tuple[float, ...]
    flat_heat_kWh: tuple[float, ...]
    flat_heat_el_kWh: tuple[float, ...]
    flat_heat_el_cost: tuple[float, ...]
    cop_flat: tuple[float, ...]
    optimized_heat_el_kWh_total: float
    flat_heat_el_kWh_total: float
    optimized_heat_el_cost_total: float
    flat_heat_el_cost_total: float
    optimized_vs_flat_cost_pct: float | None
    optimized_saving_pct: float | None
    avg_cop_optimized: float | None
    avg_cop_flat: float | None
    heat_cost_comparison_warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class SpotPlan:
    spot_index: tuple[float, ...]
    spot_source: tuple[str, ...]
    spot_planning_index: tuple[float, ...]
    spot_planning_source: tuple[str, ...]
    spot_forecast_index: tuple[float, ...]
    spot_actual_price: tuple[float | None, ...]
    spot_actual_proto_index: tuple[float | None, ...]
    spot_patched_actual_index: tuple[float | None, ...]
    spot_actual_outcome_index: tuple[float | None, ...]
    spot_actual_available: tuple[bool, ...]
    spot_forecast_error_index: tuple[float | None, ...]
    spot_forecast_error_pct: tuple[float | None, ...]
    spot_model: str
    spot_resolution: str
    spot_actual_fixture_path: str
    spot_actual_horizon_hours: int
    spot_actual_known_hours: int
    spot_forecast_hours: int
    spot_actual_patched_hours: int
    spot_patch_strategy: str
    spot_index_min: float
    spot_index_max: float
    spot_index_avg: float
    spot_patch_warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class WeeklyPlan:
    week_number: int
    current_ppm: float
    current_house_temp: float
    people: float
    occupancy_gain_ppm_h: float
    weather_source: str
    weather_provider: str
    weather_profile_strategy: str
    weather_profile_year: int | None
    weather_fallback_reason: str | None
    outdoor_temp_c: tuple[float, ...]
    outdoor_rh_pct: tuple[float, ...]
    spot_index: tuple[float, ...]
    spot: SpotPlan
    rh_weight: tuple[float, ...]
    heat: HeatPlan
    heat_cost_comparison: HeatCostComparison
    ppm: PpmPlan
