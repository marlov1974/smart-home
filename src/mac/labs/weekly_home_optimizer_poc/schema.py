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
    rh_weight: tuple[float, ...]
    heat: HeatPlan
    ppm: PpmPlan
