"""Weekly plan orchestration for the P0018 POC."""

from __future__ import annotations

from .heat_plan import plan_heat
from .input_profiles import build_input_profile, spot_indexes_for_week
from .ppm_plan import DEFAULT_OCCUPANCY_GAIN_PPM_H, optimize_ppm_plan, rh_weight_for_hour
from .schema import WeeklyPlan


def build_weekly_plan(
    week_number: int,
    current_ppm: float,
    current_house_temp: float,
    occupancy_gain_ppm_h: float = DEFAULT_OCCUPANCY_GAIN_PPM_H,
) -> WeeklyPlan:
    """Build a deterministic 168-hour weekly heat, PPM and RH-policy plan."""

    profile = build_input_profile(week_number)
    spot_index = spot_indexes_for_week(week_number)
    heat = plan_heat(profile.outdoor_temp_c, spot_index, current_house_temp)
    rh_weight = tuple(
        rh_weight_for_hour(temp, rh)
        for temp, rh in zip(profile.outdoor_temp_c, profile.outdoor_rh_pct)
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
        occupancy_gain_ppm_h=float(occupancy_gain_ppm_h),
        outdoor_temp_c=profile.outdoor_temp_c,
        outdoor_rh_pct=profile.outdoor_rh_pct,
        spot_index=spot_index,
        rh_weight=rh_weight,
        heat=heat,
        ppm=ppm,
    )
