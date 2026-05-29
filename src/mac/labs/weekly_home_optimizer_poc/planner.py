"""Weekly plan orchestration for the P0018 POC."""

from __future__ import annotations

from .cop import compare_heat_costs
from .heat_plan import plan_heat
from .input_profiles import build_input_profile
from .ppm_plan import DEFAULT_PEOPLE, occupancy_gain_for_people, optimize_ppm_plan, rh_weight_for_hour
from .schema import WeeklyPlan
from .spot import build_spot_plan


def build_weekly_plan(
    week_number: int,
    current_ppm: float,
    current_house_temp: float,
    people: float = DEFAULT_PEOPLE,
    prefer_real_weather: bool = True,
) -> WeeklyPlan:
    """Build a deterministic 168-hour weekly heat, PPM and RH-policy plan."""

    profile = build_input_profile(week_number, prefer_real_weather=prefer_real_weather)
    spot = build_spot_plan(week_number)
    heat = plan_heat(profile.outdoor_temp_c, spot.spot_index, current_house_temp)
    occupancy_gain_ppm_h = occupancy_gain_for_people(people)
    rh_weight = tuple(
        rh_weight_for_hour(temp, rh)
        for temp, rh in zip(profile.outdoor_temp_c, profile.outdoor_rh_pct)
    )
    heat_cost_comparison = compare_heat_costs(
        profile.outdoor_temp_c,
        heat.heat_need_kWh,
        heat.heat_kWh,
        heat.heat_price_index,
    )
    ppm = optimize_ppm_plan(
        heat.heat_cost_weight,
        rh_weight,
        current_ppm,
        occupancy_gain_ppm_h=occupancy_gain_ppm_h,
    )
    return WeeklyPlan(
        week_number=int(week_number),
        current_ppm=float(current_ppm),
        current_house_temp=float(current_house_temp),
        people=float(people),
        occupancy_gain_ppm_h=float(occupancy_gain_ppm_h),
        weather_source=profile.weather_source,
        weather_provider=profile.weather_provider,
        weather_profile_strategy=profile.weather_profile_strategy,
        weather_profile_year=profile.weather_profile_year,
        weather_fallback_reason=profile.weather_fallback_reason,
        outdoor_temp_c=profile.outdoor_temp_c,
        outdoor_rh_pct=profile.outdoor_rh_pct,
        spot_index=spot.spot_index,
        spot=spot,
        rh_weight=rh_weight,
        heat=heat,
        heat_cost_comparison=heat_cost_comparison,
        ppm=ppm,
    )
