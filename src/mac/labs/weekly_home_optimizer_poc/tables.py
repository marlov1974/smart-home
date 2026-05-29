"""Output rendering for the P0018 weekly optimizer POC."""

from __future__ import annotations

import csv
import io
import json
from typing import Any

from .schema import HOURS_PER_WEEK, REQUIRED_COLUMNS, WeeklyPlan


def _round_optional(value: float | None, digits: int) -> float | None:
    if value is None:
        return None
    return round(value, digits)


def weekday_hour(hour: int) -> str:
    """Return operational-week weekday/hour label for an hour index."""

    weekdays = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
    absolute_hour = 6 + hour
    day = (absolute_hour // 24) % 7
    hour_of_day = absolute_hour % 24
    return f"{weekdays[day]} {hour_of_day:02d}:00"


def rows_for_plan(plan: WeeklyPlan) -> list[dict[str, Any]]:
    """Flatten a weekly plan into required output rows."""

    rows: list[dict[str, Any]] = []
    for hour in range(HOURS_PER_WEEK):
        rows.append(
            {
                "hour": hour,
                "weekday_hour": weekday_hour(hour),
                "outdoor_temp_c": round(plan.outdoor_temp_c[hour], 2),
                "outdoor_rh_pct": round(plan.outdoor_rh_pct[hour], 2),
                "spot_index": round(plan.spot_index[hour], 2),
                "spot_source": plan.spot.spot_source[hour],
                "spot_forecast_index": round(plan.spot.spot_forecast_index[hour], 4),
                "spot_actual_price": _round_optional(plan.spot.spot_actual_price[hour], 6),
                "spot_actual_proto_index": _round_optional(plan.spot.spot_actual_proto_index[hour], 6),
                "spot_patched_actual_index": _round_optional(plan.spot.spot_patched_actual_index[hour], 6),
                "heat_need_kWh": round(plan.heat.heat_need_kWh[hour], 3),
                "heat_kWh": round(plan.heat.heat_kWh[hour], 3),
                "heat_soc_pct": round(plan.heat.heat_soc_pct[hour], 2),
                "heat_cost_weight": round(plan.heat.heat_cost_weight[hour], 3),
                "heat_price_index": round(plan.heat.heat_price_index[hour], 4),
                "heat_action_kw": plan.heat.heat_action_kw[hour],
                "heat_dp_cost_component": round(plan.heat.heat_dp_cost_component[hour], 4),
                "soc_penalty_component": round(plan.heat.soc_penalty_component[hour], 4),
                "cop_optimized": round(plan.heat_cost_comparison.cop_optimized[hour], 3),
                "heat_el_kWh": round(plan.heat_cost_comparison.optimized_heat_el_kWh[hour], 4),
                "heat_el_cost": round(plan.heat_cost_comparison.optimized_heat_el_cost[hour], 4),
                "flat_heat_kWh": round(plan.heat_cost_comparison.flat_heat_kWh[hour], 4),
                "cop_flat": round(plan.heat_cost_comparison.cop_flat[hour], 3),
                "flat_heat_el_kWh": round(plan.heat_cost_comparison.flat_heat_el_kWh[hour], 4),
                "flat_heat_el_cost": round(plan.heat_cost_comparison.flat_heat_el_cost[hour], 4),
                "rh_weight": round(plan.rh_weight[hour], 2),
                "supply_pct": plan.ppm.supply_pct[hour],
                "flow_lps": round(plan.ppm.flow_lps[hour], 2),
                "vent_cost": round(plan.ppm.vent_cost[hour], 2),
                "ppm_delta": round(plan.ppm.ppm_delta[hour], 2),
                "ppm_absolute": round(plan.ppm.ppm_absolute[hour], 2),
                "rh_delta": round(plan.ppm.rh_delta[hour], 3),
                "ppm_cost": round(plan.ppm.ppm_cost[hour], 3),
                "heat_vent_cost": round(plan.ppm.heat_vent_cost[hour], 3),
                "rh_cost": round(plan.ppm.rh_cost[hour], 3),
                "total_cost": round(plan.ppm.total_cost[hour], 3),
            }
        )
    return rows


def _metadata(plan: WeeklyPlan) -> dict[str, Any]:
    return {
        "week_number": plan.week_number,
        "current_ppm": plan.current_ppm,
        "current_house_temp": plan.current_house_temp,
        "people": plan.people,
        "occupancy_gain_ppm_h": plan.occupancy_gain_ppm_h,
        "weather_source": plan.weather_source,
        "weather_provider": plan.weather_provider,
        "weather_profile_strategy": plan.weather_profile_strategy,
        "weather_profile_year": plan.weather_profile_year,
        "weather_fallback_reason": plan.weather_fallback_reason,
        "spot_model": plan.spot.spot_model,
        "spot_resolution": plan.spot.spot_resolution,
        "spot_actual_fixture_path": plan.spot.spot_actual_fixture_path,
        "spot_actual_known_hours": plan.spot.spot_actual_known_hours,
        "spot_forecast_hours": plan.spot.spot_forecast_hours,
        "spot_actual_patched_hours": plan.spot.spot_actual_patched_hours,
        "spot_patch_strategy": plan.spot.spot_patch_strategy,
        "spot_index_min": plan.spot.spot_index_min,
        "spot_index_max": plan.spot.spot_index_max,
        "spot_index_avg": plan.spot.spot_index_avg,
        "spot_patch_warnings": plan.spot.spot_patch_warnings,
        "heat_optimizer": plan.heat.heat_optimizer,
        "heat_modes_kw": plan.heat.heat_modes_kw,
        "heat_soc_capacity_kWh": plan.heat.heat_soc_capacity_kWh,
        "heat_soc_step_kWh": plan.heat.heat_soc_step_kWh,
        "start_soc_pct": plan.heat.start_soc_pct,
        "end_soc_min_pct": plan.heat.end_soc_min_pct,
        "min_heat_soc_pct": plan.heat.min_heat_soc_pct,
        "end_heat_soc_pct": plan.heat.end_heat_soc_pct,
        "heat_optimizer_warnings": plan.heat.heat_optimizer_warnings,
        "heat_cost_model": plan.heat_cost_comparison.heat_cost_model,
        "cop_model": plan.heat_cost_comparison.cop_model,
        "cop_min": plan.heat_cost_comparison.cop_min,
        "cop_max": plan.heat_cost_comparison.cop_max,
        "optimized_heat_el_kWh": plan.heat_cost_comparison.optimized_heat_el_kWh_total,
        "flat_heat_el_kWh": plan.heat_cost_comparison.flat_heat_el_kWh_total,
        "optimized_heat_el_cost": plan.heat_cost_comparison.optimized_heat_el_cost_total,
        "flat_heat_el_cost": plan.heat_cost_comparison.flat_heat_el_cost_total,
        "optimized_vs_flat_cost_pct": plan.heat_cost_comparison.optimized_vs_flat_cost_pct,
        "optimized_saving_pct": plan.heat_cost_comparison.optimized_saving_pct,
        "avg_cop_optimized": plan.heat_cost_comparison.avg_cop_optimized,
        "avg_cop_flat": plan.heat_cost_comparison.avg_cop_flat,
        "heat_cost_comparison_warnings": plan.heat_cost_comparison.heat_cost_comparison_warnings,
        "hours": HOURS_PER_WEEK,
    }


def format_table(plan: WeeklyPlan) -> str:
    """Render a fixed-width human-readable plan table."""

    rows = rows_for_plan(plan)
    lines = [
        (
            f"# week={plan.week_number} current_ppm={plan.current_ppm:.1f} "
            f"house_temp={plan.current_house_temp:.1f} "
            f"people={plan.people:g} "
            f"occupancy_gain_ppm_h={plan.occupancy_gain_ppm_h:.1f} "
            f"weather_source={plan.weather_source} "
            f"weather_provider={plan.weather_provider} "
            f"weather_profile_year={plan.weather_profile_year} "
            f"weather_fallback_reason={plan.weather_fallback_reason or ''} "
            f"spot_model={plan.spot.spot_model} "
            f"spot_actual_patched_hours={plan.spot.spot_actual_patched_hours} "
            f"spot_patch_warnings={','.join(plan.spot.spot_patch_warnings)} "
            f"heat_cost_model={plan.heat_cost_comparison.heat_cost_model} "
            f"optimized_vs_flat_cost_pct={plan.heat_cost_comparison.optimized_vs_flat_cost_pct} "
            f"optimized_saving_pct={plan.heat_cost_comparison.optimized_saving_pct}"
        ),
        (
            "hour weekday_hour temp rh spot need heat soc hcw rhw sup flow "
            "vcost ppm_d ppm rh_d pcost hvcost rhcost total"
        ),
    ]
    for row in rows:
        lines.append(
            "{hour:3d} {weekday_hour:>9s} {outdoor_temp_c:5.1f} {outdoor_rh_pct:5.1f} "
            "{spot_index:4.2f} {heat_need_kWh:5.2f} {heat_kWh:5.2f} "
            "{heat_soc_pct:5.1f} {heat_cost_weight:4.2f} {rh_weight:4.1f} "
            "{supply_pct:3d} {flow_lps:5.1f} {vent_cost:5.1f} "
            "{ppm_delta:6.1f} {ppm_absolute:6.1f} {rh_delta:5.2f} "
            "{ppm_cost:6.1f} {heat_vent_cost:6.1f} {rh_cost:6.1f} {total_cost:6.1f}".format(**row)
        )
    return "\n".join(lines) + "\n"


def format_json(plan: WeeklyPlan) -> str:
    """Render compact JSON output."""

    return json.dumps({"metadata": _metadata(plan), "rows": rows_for_plan(plan)}, separators=(",", ":")) + "\n"


def format_csv(plan: WeeklyPlan) -> str:
    """Render CSV output."""

    rows = rows_for_plan(plan)
    output = io.StringIO()
    fieldnames = tuple(dict.fromkeys((*REQUIRED_COLUMNS, *rows[0].keys())))
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
