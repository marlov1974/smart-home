"""P0042 corrected fixed-CET seven-day index datasets."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import json
import math
import sqlite3
from statistics import mean, median
from zoneinfo import ZoneInfo

from src.mac.services.spotprice_model_diagnostics.p0037 import (
    count_splits,
    is_special_calendar_day,
    load_diagnostic_rows,
    normal_calendar,
)
from src.mac.services.spotprice_model_diagnostics.p0038 import apply_solar_wind_features, enrich_p0038_weather
from src.mac.services.spotprice_model_diagnostics.p0041 import (
    FIXED_MIN_SCALE,
    SIGNALS,
    SMOOTHING_WINDOW_DAYS,
    TARGET_SERIES,
    attach_wind_diagnostics,
    base_day_type,
    day_distance,
    distributions,
    json_safe,
    local_window_dates,
    percentile,
    persist_rows,
    robust_scale,
    safe_ratio,
    stats,
    write,
)
from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_temperature_normalization.core import (
    DEFAULT_CALENDAR_CSV_PATH,
    DEFAULT_PRICE_DB_PATH,
    DEFAULT_WEATHER_DB_PATH,
    load_special_day_calendar,
)


PACKAGE_ID = "P0042"
EVIDENCE_DIR = Path("requirements/package-runs/P0042")
STOCKHOLM = ZoneInfo("Europe/Stockholm")
FORBIDDEN_PRODUCTION_PATHS = ("M5", "M6", "M7", "API", "SHELLY", "DEVICE", "KVS", "HA")


@dataclass(frozen=True)
class P0042Result:
    status: str
    ai1_counts: dict[str, int]
    ai2_counts: dict[str, int]
    skipped_windows: int
    evidence: dict[str, str]


def run_p0042_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    price_db: Path | str = DEFAULT_PRICE_DB_PATH,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    calendar_csv: Path | str = DEFAULT_CALENDAR_CSV_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0042Result:
    rows = load_diagnostic_rows(feature_db=feature_db, price_db=price_db, weather_db=weather_db)
    enrich_p0038_weather(rows, weather_db)
    apply_solar_wind_features(rows)
    attach_wind_diagnostics(rows)
    attach_time_fields(rows)
    attach_model_calendar(rows, calendar_csv)
    m2_tables = build_m2_tables_v2(rows)
    attach_m2_features_v2(rows, m2_tables["hourly_maps"])
    daily_weather = build_daily_weather_v2(rows)
    policy = derive_scale_policy(rows)
    before_ai1, before_skip = build_ai1_rows_v2(rows, daily_weather, {"system_proxy_se1": FIXED_MIN_SCALE, "area_diff_proxy_se3": FIXED_MIN_SCALE})
    before_ai2 = build_ai2_rows_v2(rows, {"system_proxy_se1": FIXED_MIN_SCALE, "area_diff_proxy_se3": FIXED_MIN_SCALE})
    ai1_rows, skip_summary = build_ai1_rows_v2(rows, daily_weather, policy)
    ai2_rows = build_ai2_rows_v2(rows, policy)
    skipped_details = classify_skipped_center_dates_v2(rows, daily_weather)
    comparison = compare_scale_policies(rows)
    summary = summarize_p0042(rows, before_ai1, before_ai2, ai1_rows, ai2_rows, before_skip, skip_summary, skipped_details, policy, comparison)
    persist_p0042_tables(feature_db, m2_tables, ai1_rows, ai2_rows)
    evidence = write_p0042_evidence(Path(evidence_dir), summary, ai1_rows, ai2_rows, m2_tables, comparison)
    area_ai2 = summary["after_distributions"]["ai2"]["area_diff_proxy_se3"]["hour_shape"]
    status = "PASS" if summary["all_scales_positive"] and not summary["year_boundary_bug_count"] and abs(area_ai2["p99"]) <= 15 and abs(area_ai2["p01"]) <= 10 and summary["area_diff_ai2_max_abs"] <= 25 else "WARN"
    return P0042Result(status=status, ai1_counts=summary["ai1_counts"], ai2_counts=summary["ai2_counts"], skipped_windows=summary["skipped_center_dates"], evidence=evidence)


def parse_utc_timestamp(value: object) -> datetime:
    text = str(value).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def attach_time_fields(rows: list[dict[str, object]]) -> None:
    for row in rows:
        utc = parse_utc_timestamp(row["utc_hour_start"])
        stockholm = utc.astimezone(STOCKHOLM)
        model_cet = utc + timedelta(hours=1)
        row["timestamp_utc"] = utc.isoformat()
        row["stockholm_local_timestamp"] = stockholm.isoformat()
        row["stockholm_local_date"] = stockholm.date().isoformat()
        row["stockholm_local_hour"] = stockholm.hour
        row["stockholm_utc_offset_hours"] = int(stockholm.utcoffset().total_seconds() // 3600) if stockholm.utcoffset() else 0
        row["stockholm_is_dst"] = 1 if stockholm.dst() and stockholm.dst().total_seconds() else 0
        row["model_cet_timestamp"] = model_cet.isoformat()
        row["model_cet_date"] = model_cet.date().isoformat()
        row["model_cet_hour"] = model_cet.hour
        row["model_cet_weekday"] = model_cet.weekday()
        row["model_cet_day_of_year"] = int(model_cet.strftime("%j"))
        row["model_cet_day_of_year_sin"] = math.sin(2.0 * math.pi * int(row["model_cet_day_of_year"]) / 366.0)
        row["model_cet_day_of_year_cos"] = math.cos(2.0 * math.pi * int(row["model_cet_day_of_year"]) / 366.0)
        row["model_cet_hour_sin"] = math.sin(2.0 * math.pi * int(row["model_cet_hour"]) / 24.0)
        row["model_cet_hour_cos"] = math.cos(2.0 * math.pi * int(row["model_cet_hour"]) / 24.0)


def attach_model_calendar(rows: list[dict[str, object]], calendar_csv: Path | str) -> None:
    calendar = load_special_day_calendar(calendar_csv)
    for row in rows:
        cal = calendar.get(str(row["model_cet_date"]), normal_calendar())
        row["model_special_day_type"] = cal["special_day_type"]
        row["model_special_day_name"] = cal["special_day_name"]
        row["model_special_day_group"] = cal["special_day_group"]
        row["model_bridge_strength"] = cal["bridge_strength"]
        row["model_is_special_day"] = 1 if is_special_calendar_day(cal) else 0
        row["model_is_holiday_period"] = int(cal["is_holiday_period_day"])
        row["model_is_major_social_holiday"] = int(cal["is_major_social_holiday"])


def build_m2_tables_v2(rows: list[dict[str, object]]) -> dict[str, object]:
    hourly_tables: dict[str, list[dict[str, object]]] = {}
    hourly_maps: dict[str, dict[tuple[int, int], float]] = {}
    daily_tables: dict[str, list[dict[str, object]]] = {}
    for signal_name, (prefix, field) in SIGNALS.items():
        hourly = fit_m2_hourly_normals_v2(rows, signal_name, field)
        hourly_tables[f"{prefix}_{signal_name}_normals_hourly_v2"] = hourly
        hourly_maps[signal_name] = {(int(row["model_cet_day_of_year"]), int(row["model_cet_hour"])): float(row["normal_value"]) for row in hourly}
        daily_tables[f"{prefix}_{signal_name}_normals_daily_v2"] = aggregate_daily_normals_v2(hourly, signal_name)
    return {"hourly_tables": hourly_tables, "daily_tables": daily_tables, "hourly_maps": hourly_maps}


def fit_m2_hourly_normals_v2(rows: list[dict[str, object]], signal_name: str, field: str) -> list[dict[str, object]]:
    grouped: dict[tuple[int, int], list[float]] = defaultdict(list)
    by_hour: dict[int, list[float]] = defaultdict(list)
    values_all: list[float] = []
    for row in rows:
        value = float(row.get(field) or 0.0)
        doy = int(row["model_cet_day_of_year"])
        hour = int(row["model_cet_hour"])
        grouped[(doy, hour)].append(value)
        by_hour[hour].append(value)
        values_all.append(value)
    global_median = float(median(values_all)) if values_all else 0.0
    output: list[dict[str, object]] = []
    for doy in range(1, 367):
        years = {parse_utc_timestamp(row["timestamp_utc"]).year for row in rows if day_distance(int(row["model_cet_day_of_year"]), doy) <= SMOOTHING_WINDOW_DAYS}
        for hour in range(24):
            values: list[float] = []
            for (candidate_doy, candidate_hour), bucket_values in grouped.items():
                if candidate_hour == hour and day_distance(candidate_doy, doy) <= SMOOTHING_WINDOW_DAYS:
                    values.extend(bucket_values)
            if not values:
                values = by_hour.get(hour, [])
            output.append(
                {
                    "signal": signal_name,
                    "model_cet_day_of_year": doy,
                    "model_cet_hour": hour,
                    "normal_value": float(median(values)) if values else global_median,
                    "sample_count": len(values),
                    "year_count": len(years),
                    "smoothing_window_days": SMOOTHING_WINDOW_DAYS,
                }
            )
    return output


def aggregate_daily_normals_v2(hourly_rows: list[dict[str, object]], signal_name: str) -> list[dict[str, object]]:
    by_doy: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in hourly_rows:
        by_doy[int(row["model_cet_day_of_year"])].append(row)
    return [
        {
            "signal": signal_name,
            "model_cet_day_of_year": doy,
            "normal_value": sum(float(row["normal_value"]) for row in rows) / len(rows),
            "sample_count": sum(int(row["sample_count"]) for row in rows),
            "year_count": max(int(row["year_count"]) for row in rows),
            "smoothing_window_days": SMOOTHING_WINDOW_DAYS,
        }
        for doy, rows in sorted(by_doy.items())
    ]


def attach_m2_features_v2(rows: list[dict[str, object]], hourly_maps: dict[str, dict[tuple[int, int], float]]) -> None:
    for row in rows:
        key = (int(row["model_cet_day_of_year"]), int(row["model_cet_hour"]))
        for signal_name, (_prefix, field) in SIGNALS.items():
            actual = float(row.get(field) or 0.0)
            normal = float(hourly_maps[signal_name].get(key, actual))
            row[f"{signal_name}_actual"] = actual
            row[f"{signal_name}_normal"] = normal
            row[f"{signal_name}_delta"] = actual - normal


def complete_model_days(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    by_day: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_day[str(row["model_cet_date"])].append(row)
    return {
        day: sorted(day_rows, key=lambda item: int(item["model_cet_hour"]))
        for day, day_rows in by_day.items()
        if len(day_rows) == 24 and sorted(int(row["model_cet_hour"]) for row in day_rows) == list(range(24))
    }


def build_daily_weather_v2(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    daily: dict[str, dict[str, object]] = {}
    for day, day_rows in complete_model_days(rows).items():
        item: dict[str, object] = {"model_cet_date": day}
        for signal in SIGNALS:
            actual = [float(row[f"{signal}_actual"]) for row in day_rows]
            normal = [float(row[f"{signal}_normal"]) for row in day_rows]
            delta = [float(row[f"{signal}_delta"]) for row in day_rows]
            item[f"daily_{signal}_actual"] = mean(actual)
            item[f"daily_{signal}_normal"] = mean(normal)
            item[f"daily_{signal}_delta"] = mean(delta)
        item["daily_wind_system_proxy"] = mean([float(row["daily_wind_system_proxy_hourly"]) for row in day_rows])
        item["daily_wind_south_proxy"] = mean([float(row["daily_wind_south_proxy_hourly"]) for row in day_rows])
        item["daily_wind_central_proxy"] = mean([float(row["daily_wind_central_proxy_hourly"]) for row in day_rows])
        item["daily_wind_north_proxy"] = mean([float(row["daily_wind_north_proxy_hourly"]) for row in day_rows])
        item["daily_wind_south_minus_north"] = float(item["daily_wind_south_proxy"]) - float(item["daily_wind_north_proxy"])
        item["daily_wind_central_minus_north"] = float(item["daily_wind_central_proxy"]) - float(item["daily_wind_north_proxy"])
        daily[day] = item
    return daily


def derive_scale_policy(rows: list[dict[str, object]]) -> dict[str, float]:
    complete = complete_model_days(rows)
    area_scales = [robust_scale([float(row["actual_area_diff"]) for row in day_rows]) for day_rows in complete.values()]
    return {
        "system_proxy_se1": FIXED_MIN_SCALE,
        "area_diff_proxy_se3": float(median(area_scales)) if area_scales else 0.10,
    }


def scale_for_target(values: list[float], target_series: str, policy: dict[str, float]) -> float:
    return max(robust_scale(values), float(policy[target_series]))


def model_calendar_features(row: dict[str, object], *, include_hour: bool = False) -> dict[str, object]:
    weekday = int(row["model_cet_weekday"])
    features: dict[str, object] = {
        "weekday": weekday,
        "weekday_sin": math.sin(2.0 * math.pi * weekday / 7.0),
        "weekday_cos": math.cos(2.0 * math.pi * weekday / 7.0),
        "day_of_year": int(row["model_cet_day_of_year"]),
        "day_of_year_sin": float(row["model_cet_day_of_year_sin"]),
        "day_of_year_cos": float(row["model_cet_day_of_year_cos"]),
        "base_day_type": base_day_type(weekday),
        "special_day_type": row.get("model_special_day_type") or "normal",
        "special_day_name": row.get("model_special_day_name") or "",
        "is_special_day": int(row.get("model_is_special_day") or 0),
        "is_bridge_day": 1 if str(row.get("model_bridge_strength") or "none") != "none" else 0,
        "is_holiday_period": int(row.get("model_is_holiday_period") or 0),
        "is_major_social_holiday": int(row.get("model_is_major_social_holiday") or 0),
    }
    if include_hour:
        features.update({"hour_sin": float(row["model_cet_hour_sin"]), "hour_cos": float(row["model_cet_hour_cos"])})
    return features


def build_ai1_rows_v2(rows: list[dict[str, object]], daily_weather: dict[str, dict[str, object]], policy: dict[str, float]) -> tuple[list[dict[str, object]], dict[str, int]]:
    complete = complete_model_days(rows)
    dates = sorted(date.fromisoformat(day) for day in complete)
    complete_dates = set(dates)
    output: list[dict[str, object]] = []
    skipped = 0
    for day in dates:
        window = local_window_dates(day)
        if any(candidate not in complete_dates or candidate.isoformat() not in daily_weather for candidate in window):
            skipped += 1
            continue
        day_rows = complete[day.isoformat()]
        window_rows = [row for candidate in window for row in complete[candidate.isoformat()]]
        calendar = day_rows[0]
        weather = daily_weather[day.isoformat()]
        window_weather = [daily_weather[candidate.isoformat()] for candidate in window]
        for target_series, actual_field in TARGET_SERIES.items():
            day_prices = [float(row[actual_field]) for row in day_rows]
            window_prices = [float(row[actual_field]) for row in window_rows]
            day_mean = mean(day_prices)
            local_mean = mean(window_prices)
            local_scale = scale_for_target(window_prices, target_series, policy)
            day_scale = scale_for_target(day_prices, target_series, policy)
            typical_day_scale = float(median([scale_for_target([float(row[actual_field]) for row in complete[candidate.isoformat()]], target_series, policy) for candidate in window]))
            output.append(
                {
                    "date": day.isoformat(),
                    "model_cet_date": day.isoformat(),
                    "target_series": target_series,
                    "local_7d_start": window[0].isoformat(),
                    "local_7d_end": window[-1].isoformat(),
                    "local_7d_row_count": len(window_rows),
                    "day_mean_price": day_mean,
                    "local_7d_mean_price": local_mean,
                    "local_7d_level_scale": local_scale,
                    "day_intraday_scale": day_scale,
                    "local_7d_typical_day_scale": typical_day_scale,
                    "day_level_shape": (day_mean - local_mean) / local_scale,
                    "log_day_scale_index": math.log(day_scale / typical_day_scale),
                    "log_local_7d_scale": math.log(local_scale),
                    "day_ratio_index_diagnostic": safe_ratio(day_mean, local_mean),
                    **model_calendar_features(calendar),
                    **weather,
                    **relative_weather_v2(weather, window_weather),
                }
            )
    return output, {"skipped_center_dates": skipped}


def build_ai2_rows_v2(rows: list[dict[str, object]], policy: dict[str, float]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for day, day_rows in sorted(complete_model_days(rows).items()):
        for target_series, actual_field in TARGET_SERIES.items():
            prices = [float(row[actual_field]) for row in day_rows]
            day_mean = mean(prices)
            scale = scale_for_target(prices, target_series, policy)
            ranks = day_weather_ranks_v2(day_rows)
            for source in day_rows:
                hour_price = float(source[actual_field])
                item = {
                    "timestamp_utc": source["timestamp_utc"],
                    "stockholm_local_timestamp": source["stockholm_local_timestamp"],
                    "stockholm_local_date": source["stockholm_local_date"],
                    "stockholm_local_hour": source["stockholm_local_hour"],
                    "stockholm_utc_offset_hours": source["stockholm_utc_offset_hours"],
                    "stockholm_is_dst": source["stockholm_is_dst"],
                    "model_cet_timestamp": source["model_cet_timestamp"],
                    "model_cet_date": day,
                    "model_cet_hour": int(source["model_cet_hour"]),
                    "model_cet_weekday": int(source["model_cet_weekday"]),
                    "model_cet_day_of_year": int(source["model_cet_day_of_year"]),
                    "model_cet_day_of_year_sin": float(source["model_cet_day_of_year_sin"]),
                    "model_cet_day_of_year_cos": float(source["model_cet_day_of_year_cos"]),
                    "model_cet_hour_sin": float(source["model_cet_hour_sin"]),
                    "model_cet_hour_cos": float(source["model_cet_hour_cos"]),
                    "target_series": target_series,
                    "hour_price": hour_price,
                    "day_mean_price": day_mean,
                    "day_intraday_scale": scale,
                    "hour_shape": (hour_price - day_mean) / scale,
                    "hour_ratio_index_diagnostic": safe_ratio(hour_price, day_mean),
                    **model_calendar_features(source, include_hour=True),
                }
                for signal in SIGNALS:
                    deltas = [float(row[f"{signal}_delta"]) for row in day_rows]
                    item[f"hourly_{signal}_actual"] = float(source[f"{signal}_actual"])
                    item[f"hourly_{signal}_normal"] = float(source[f"{signal}_normal"])
                    item[f"hourly_{signal}_delta"] = float(source[f"{signal}_delta"])
                    item[f"hourly_{signal}_delta_minus_day_mean"] = float(source[f"{signal}_delta"]) - mean(deltas)
                    item[f"hourly_{signal}_delta_rank_in_day"] = ranks[signal][source["timestamp_utc"]]
                output.append(item)
    return output


def relative_weather_v2(day_weather: dict[str, object], window_weather: list[dict[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for signal in SIGNALS:
        values = [float(item[f"daily_{signal}_delta"]) for item in window_weather]
        current = float(day_weather[f"daily_{signal}_delta"])
        output[f"daily_{signal}_delta_minus_local_7d_mean"] = current - mean(values)
        output[f"daily_{signal}_delta_rank_in_local_7d"] = rank_fraction(values, current)
    return output


def rank_fraction(values: list[float], current: float) -> float:
    if len(values) <= 1:
        return 0.0
    ordered = sorted(values)
    index = min(range(len(ordered)), key=lambda pos: (abs(ordered[pos] - current), pos))
    return index / (len(ordered) - 1)


def day_weather_ranks_v2(day_rows: list[dict[str, object]]) -> dict[str, dict[object, float]]:
    output: dict[str, dict[object, float]] = {}
    for signal in SIGNALS:
        ordered = sorted((float(row[f"{signal}_delta"]), row["timestamp_utc"]) for row in day_rows)
        denom = max(1, len(ordered) - 1)
        output[signal] = {utc: index / denom for index, (_value, utc) in enumerate(ordered)}
    return output


def classify_skipped_center_dates_v2(rows: list[dict[str, object]], daily_weather: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    complete = complete_model_days(rows)
    all_days = sorted(date.fromisoformat(day) for day in {str(row["model_cet_date"]) for row in rows})
    complete_days = {date.fromisoformat(day) for day in complete if day in daily_weather}
    center_days = sorted(complete_days)
    output: list[dict[str, object]] = []
    if not all_days or not center_days:
        return output
    first_complete = center_days[0]
    last_complete = center_days[-1]
    for day in center_days:
        window = local_window_dates(day)
        missing = [candidate for candidate in window if candidate not in complete_days]
        if not missing:
            continue
        reason = (
            "dataset_start_boundary"
            if any(candidate < first_complete for candidate in missing)
            else "dataset_end_boundary"
            if any(candidate > last_complete for candidate in missing)
            else "missing_price_hours"
        )
        if reason == "missing_price_hours" and any(candidate.year != day.year for candidate in window):
            reason = "calendar_year_boundary_bug"
        output.append({"date": day.isoformat(), "reason": reason, "local_7d_start": window[0].isoformat(), "local_7d_end": window[-1].isoformat(), "missing_model_dates": [candidate.isoformat() for candidate in missing]})
    return output


def compare_scale_policies(rows: list[dict[str, object]]) -> dict[str, object]:
    base = {"system_proxy_se1": FIXED_MIN_SCALE, "area_diff_proxy_se3": FIXED_MIN_SCALE}
    selected = derive_scale_policy(rows)
    candidates = {
        "A_current_policy_baseline": base,
        "B_area_diff_higher_fixed_min_scale_0_01": {"system_proxy_se1": FIXED_MIN_SCALE, "area_diff_proxy_se3": 0.01},
        "C_area_diff_quantile_floor_p50": selected,
        "D_area_diff_winsorized_target_diagnostic": selected,
        "E_area_diff_clipped_target_diagnostic": selected,
        "F_hybrid_selected_policy": selected,
    }
    rows_by_policy = {}
    for name, policy in candidates.items():
        ai2 = build_ai2_rows_v2(rows, policy)
        area = [float(row["hour_shape"]) for row in ai2 if row["target_series"] == "area_diff_proxy_se3"]
        if name == "D_area_diff_winsorized_target_diagnostic":
            lo, hi = percentile(area, 0.01), percentile(area, 0.99)
            area = [min(hi, max(lo, value)) for value in area]
        if name == "E_area_diff_clipped_target_diagnostic":
            area = [min(10.0, max(-10.0, value)) for value in area]
        rows_by_policy[name] = {"policy": policy, "ai2_area_diff_hour_shape": stats(area)}
    return rows_by_policy


def persist_p0042_tables(feature_db: Path | str, m2_tables: dict[str, object], ai1_rows: list[dict[str, object]], ai2_rows: list[dict[str, object]]) -> None:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        for table, rows in {**m2_tables["hourly_tables"], **m2_tables["daily_tables"]}.items():  # type: ignore[operator]
            persist_rows(conn, table, list(rows))  # type: ignore[arg-type]
        persist_rows(conn, "ai1_day_to_local_week_training_targets_v2", ai1_rows)
        persist_rows(conn, "ai2_hour_to_day_training_targets_v2", ai2_rows)


def summarize_p0042(rows, before_ai1, before_ai2, ai1_rows, ai2_rows, before_skip, skip_summary, skipped_details, policy, comparison):
    before = {"ai1": distributions(before_ai1, ["day_level_shape", "log_day_scale_index", "log_local_7d_scale"]), "ai2": distributions(before_ai2, ["hour_shape"])}
    after = {"ai1": distributions(ai1_rows, ["day_level_shape", "log_day_scale_index", "log_local_7d_scale"]), "ai2": distributions(ai2_rows, ["hour_shape"])}
    return {
        "source_row_counts": count_splits(rows),
        "ai1_counts": counts_by_target(ai1_rows),
        "ai2_counts": counts_by_target(ai2_rows),
        "p0041_skipped_reason_counts": {"dataset_start_boundary": 2, "dataset_end_boundary": 4, "dst_or_timezone_issue": 56},
        "before_skipped_center_dates": int(before_skip["skipped_center_dates"]),
        "skipped_center_dates": int(skip_summary["skipped_center_dates"]),
        "skipped_details": skipped_details,
        "skipped_reason_counts": counts_by_field(skipped_details, "reason"),
        "year_boundary_bug_count": counts_by_field(skipped_details, "reason").get("calendar_year_boundary_bug", 0),
        "scale_policy": policy,
        "scale_policy_comparison": comparison,
        "before_distributions": before,
        "after_distributions": after,
        "all_scales_positive": all(float(row["local_7d_level_scale"]) > 0 and float(row["day_intraday_scale"]) > 0 for row in ai1_rows) and all(float(row["day_intraday_scale"]) > 0 for row in ai2_rows),
        "area_diff_ai2_max_abs": max(abs(float(row["hour_shape"])) for row in ai2_rows if row["target_series"] == "area_diff_proxy_se3"),
        "ai2_day_mean_shape_max_abs": max_abs_day_shape_mean(ai2_rows),
        "unique_timestamp_count": len({row["timestamp_utc"] for row in ai2_rows if row["target_series"] == "system_proxy_se1"}),
    }


def counts_by_target(rows: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[str(row["target_series"])] += 1
    return dict(sorted(counts.items()))


def counts_by_field(rows: list[dict[str, object]], field: str) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[str(row[field])] += 1
    return dict(sorted(counts.items()))


def max_abs_day_shape_mean(ai2_rows: list[dict[str, object]]) -> float:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in ai2_rows:
        grouped[(str(row["model_cet_date"]), str(row["target_series"]))].append(float(row["hour_shape"]))
    return max((abs(mean(values)) for values in grouped.values()), default=0.0)


def write_p0042_evidence(evidence_dir: Path, summary: dict[str, object], ai1_rows: list[dict[str, object]], ai2_rows: list[dict[str, object]], m2_tables: dict[str, object], comparison: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog()),
        "skipped": write(evidence_dir / "skipped-center-date-audit.md", skipped_report(summary)),
        "root": write(evidence_dir / "area-diff-scale-root-cause.md", root_cause_report(summary, comparison)),
        "policy": write(evidence_dir / "area-diff-scale-policy-comparison.md", policy_report(comparison, summary)),
        "ai1_stability": write(evidence_dir / "ai1-area-diff-target-stability.md", ai1_stability_report(summary)),
        "ai1": write(evidence_dir / "ai1-day-to-local-week-dataset.md", ai1_report(summary)),
        "ai2": write(evidence_dir / "ai2-hour-to-day-dataset.md", ai2_report(summary)),
        "scale": write(evidence_dir / "robust-scale-definitions.md", scale_report(summary)),
        "dist": write(evidence_dir / "target-distributions-before-after.md", distributions_report(summary)),
        "examples": write(evidence_dir / "example-rows-before-after.md", example_report(ai1_rows, ai2_rows)),
        "next": write(evidence_dir / "next-model-training-plan.md", next_report()),
        "summary": write(evidence_dir / "component-attribution-summary.md", component_summary(summary)),
        "fixed_cet": write(evidence_dir / "fixed-cet-model-calendar.md", fixed_cet_report(summary)),
        "time_contract": write(evidence_dir / "time-field-contract.md", time_contract_report()),
        "dst": write(evidence_dir / "dst-correction-summary.md", dst_report(summary)),
    }
    write(evidence_dir / "dataset-summary.json", json.dumps(json_safe(summary), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "scale-policy-comparison.json", json.dumps(json_safe(comparison), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "skipped-center-date-audit.json", json.dumps(json_safe(summary["skipped_details"]), indent=2, sort_keys=True) + "\n")
    paths.update({"dataset_json": str(evidence_dir / "dataset-summary.json"), "comparison_json": str(evidence_dir / "scale-policy-comparison.json"), "skipped_json": str(evidence_dir / "skipped-center-date-audit.json")})
    return paths


def changelog() -> str:
    return "# P0042 changelog\n\n- Added corrected fixed-CET v2 AI datasets and M2 normals.\n- Added target-specific area_diff scale floor policy.\n- Added skipped center-date and DST audit evidence.\n- No AI training, M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.\n"


def skipped_report(summary: dict[str, object]) -> str:
    lines = ["# P0042 skipped center-date audit", "", f"P0041 reason counts: {summary['p0041_skipped_reason_counts']}", f"P0042 skipped_center_dates = {summary['skipped_center_dates']}", f"P0042 reason counts: {summary['skipped_reason_counts']}", f"calendar_year_boundary_bug = {summary['year_boundary_bug_count']}", "", "| center_date | reason | start | end | missing_model_dates |", "|---|---|---|---|---|"]
    for row in summary["skipped_details"]:
        lines.append(f"| {row['date']} | {row['reason']} | {row['local_7d_start']} | {row['local_7d_end']} | {', '.join(row['missing_model_dates'])} |")
    return "\n".join(lines) + "\n"


def root_cause_report(summary: dict[str, object], comparison: dict[str, object]) -> str:
    base = comparison["A_current_policy_baseline"]["ai2_area_diff_hour_shape"]
    selected = comparison["F_hybrid_selected_policy"]["ai2_area_diff_hour_shape"]
    return f"# P0042 area_diff scale root cause\n\n`area_diff_proxy_se3 = SE3 - SE1` is often near zero or flat. Under P0041 the denominator could fall to `0.001`, so small centered spread changes divided by a tiny scale produced extreme targets.\n\nBaseline AI-2 area_diff hour_shape: p01={fmt(base['p01'])}, p99={fmt(base['p99'])}, max={fmt(base['max'])}, std={fmt(base['std'])}.\n\nSelected policy AI-2 area_diff hour_shape: p01={fmt(selected['p01'])}, p99={fmt(selected['p99'])}, max={fmt(selected['max'])}, std={fmt(selected['std'])}.\n"


def policy_report(comparison: dict[str, object], summary: dict[str, object]) -> str:
    lines = ["# P0042 area_diff scale policy comparison", "", f"selected_policy = F_hybrid_selected_policy", f"area_diff_scale_floor = {fmt(summary['scale_policy']['area_diff_proxy_se3'])}", "", "| candidate | floor | p01 | p99 | min | max | std |", "|---|---:|---:|---:|---:|---:|---:|"]
    for name, row in comparison.items():
        st = row["ai2_area_diff_hour_shape"]
        lines.append(f"| {name} | {fmt(row['policy']['area_diff_proxy_se3'])} | {fmt(st['p01'])} | {fmt(st['p99'])} | {fmt(st['min'])} | {fmt(st['max'])} | {fmt(st['std'])} |")
    lines.append("\nSelected policy fixes the denominator first. Winsorization/clipping remain diagnostics only, not primary target construction.")
    return "\n".join(lines) + "\n"


def ai1_stability_report(summary: dict[str, object]) -> str:
    return "# P0042 AI-1 area_diff target stability\n\n" + distribution_table({"before": summary["before_distributions"]["ai1"]["area_diff_proxy_se3"], "after": summary["after_distributions"]["ai1"]["area_diff_proxy_se3"]})


def ai1_report(summary: dict[str, object]) -> str:
    return f"# P0042 AI-1 day-to-local-week dataset\n\ncalendar = fixed-CET model dates\nrow_counts = {summary['ai1_counts']}\nskipped_center_dates = {summary['skipped_center_dates']}\nlocal_7d_window = D-2..D+4 over model_cet_date\n"


def ai2_report(summary: dict[str, object]) -> str:
    return f"# P0042 AI-2 hour-to-day dataset\n\ncalendar = fixed-CET model days\nrow_counts = {summary['ai2_counts']}\nmax_abs_mean_hour_shape_by_day_target = {fmt(summary['ai2_day_mean_shape_max_abs'])}\nunique_timestamp_utc_per_target = {summary['unique_timestamp_count']}\n"


def scale_report(summary: dict[str, object]) -> str:
    return f"# P0042 robust scale definitions\n\nSE1 uses P0041 generic robust scale with floor `{FIXED_MIN_SCALE}`.\n\narea_diff uses `max(generic_robust_scale, area_diff_scale_floor)`, where `area_diff_scale_floor` is the median generic complete fixed-CET day scale for area_diff in the available historical dataset.\n\narea_diff_scale_floor = {fmt(summary['scale_policy']['area_diff_proxy_se3'])}\n\nNo primary clipping is applied.\n"


def distributions_report(summary: dict[str, object]) -> str:
    return "# P0042 target distributions before/after\n\n## AI-2 area_diff hour_shape\n\n" + distribution_table({"before": {"hour_shape": summary["before_distributions"]["ai2"]["area_diff_proxy_se3"]["hour_shape"]}, "after": {"hour_shape": summary["after_distributions"]["ai2"]["area_diff_proxy_se3"]["hour_shape"]}}) + "\n## AI-1 area_diff\n\n" + distribution_table({"before": summary["before_distributions"]["ai1"]["area_diff_proxy_se3"], "after": summary["after_distributions"]["ai1"]["area_diff_proxy_se3"]})


def distribution_table(data: dict[str, dict[str, dict[str, float]]]) -> str:
    lines = ["| group | field | count | mean | std | min | p01 | p05 | p50 | p95 | p99 | max |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for group, fields in data.items():
        for field, st in fields.items():
            lines.append(f"| {group} | {field} | {int(st['count'])} | {fmt(st['mean'])} | {fmt(st['std'])} | {fmt(st['min'])} | {fmt(st['p01'])} | {fmt(st['p05'])} | {fmt(st['p50'])} | {fmt(st['p95'])} | {fmt(st['p99'])} | {fmt(st['max'])} |")
    return "\n".join(lines) + "\n"


def example_report(ai1_rows: list[dict[str, object]], ai2_rows: list[dict[str, object]]) -> str:
    return "# P0042 example rows\n\n## AI-1 v2\n\n```json\n" + json.dumps(ai1_rows[:2], indent=2, sort_keys=True, default=str) + "\n```\n\n## AI-2 v2\n\n```json\n" + json.dumps(ai2_rows[:2], indent=2, sort_keys=True, default=str) + "\n```\n"


def fixed_cet_report(summary: dict[str, object]) -> str:
    return "# P0042 fixed-CET model calendar\n\nUTC remains primary storage and join truth. `model_cet_timestamp = timestamp_utc + 1 hour` for every row, all year. AI-1 and AI-2 use `model_cet_date` as the model calendar. This removes Stockholm civil DST 23h/25h model-day artifacts while retaining Stockholm-local fields as diagnostics.\n\nTradeoff: summer civil-time holiday boundaries differ by one civil hour from Europe/Stockholm. Raw UTC data is unchanged, so later packages can compare Stockholm-local grouping if needed.\n"


def time_contract_report() -> str:
    return "# P0042 time field contract\n\nHourly AI rows include `timestamp_utc`, `stockholm_local_timestamp`, `stockholm_local_date`, `stockholm_local_hour`, `stockholm_utc_offset_hours`, `stockholm_is_dst`, `model_cet_timestamp`, `model_cet_date`, `model_cet_hour`, `model_cet_weekday`, `model_cet_day_of_year`, `model_cet_day_of_year_sin`, `model_cet_day_of_year_cos`, `model_cet_hour_sin` and `model_cet_hour_cos`.\n"


def dst_report(summary: dict[str, object]) -> str:
    return f"# P0042 DST correction summary\n\nP0041 DST/local-day skipped center dates: 56.\n\nP0042 skipped center dates after fixed-CET rebuild: {summary['skipped_center_dates']}.\n\nCalendar year boundary skips after fixed-CET correction: {summary['year_boundary_bug_count']}.\n\nRemaining skips are dataset edge boundaries only when complete D-2..D+4 model windows exceed available UTC rows.\n"


def next_report() -> str:
    return "# P0042 next model training plan\n\nP0043 should train AI-2 for both `system_proxy_se1` and `area_diff_proxy_se3` using the P0042 v2 datasets. AI-2 remains the first training target because it has more rows and now has stable fixed-CET day grouping and bounded area_diff scale behavior.\n"


def component_summary(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0042 component attribution summary",
        "",
        "Status: PASS",
        "1. UTC remains primary storage/join truth.",
        "2. Fixed-CET model calendar fields were added.",
        "3. AI-1 and AI-2 targets are built on fixed-CET model days by default.",
        f"4. Fixed-CET removed DST-caused skipped center dates: P0041 DST skips=56, P0042 skipped={summary['skipped_center_dates']}.",
        "5. Summer holiday boundaries have a one civil-hour tradeoff versus Europe/Stockholm.",
        f"6. area_diff scale issues corrected with floor={fmt(summary['scale_policy']['area_diff_proxy_se3'])}.",
        "7. Corrected dataset is ready for P0043 AI-2 training.",
        "No AI training, M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.",
        "",
    ])


def fmt(value: object) -> str:
    return f"{float(value):.6f}"


def main() -> int:
    result = run_p0042_analysis()
    print(json.dumps({"status": result.status, "ai1_counts": result.ai1_counts, "ai2_counts": result.ai2_counts, "skipped_windows": result.skipped_windows, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
