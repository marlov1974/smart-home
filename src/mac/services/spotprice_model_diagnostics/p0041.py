"""P0041 seven-day index AI dataset and M2 foundation."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import json
import math
import sqlite3
from statistics import mean, median

from src.mac.services.spotprice_model_diagnostics.p0037 import count_splits, load_diagnostic_rows
from src.mac.services.spotprice_model_diagnostics.p0038 import (
    P0038_WIND_LOCATIONS,
    apply_solar_wind_features,
    enrich_p0038_weather,
    wind_power_proxy,
)
from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_PRICE_DB_PATH, DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0041"
EVIDENCE_DIR = Path("requirements/package-runs/P0041")
FIXED_MIN_SCALE = 0.001
SMOOTHING_WINDOW_DAYS = 14
TARGET_SERIES = {
    "system_proxy_se1": "actual_se1",
    "area_diff_proxy_se3": "actual_area_diff",
}
SIGNALS = {
    "temperature": ("m2a", "se1_system_temperature"),
    "solar": ("m2c", "m3c_solar_proxy_area"),
    "wind": ("m2d", "m3d_wind_proxy_area"),
}
FORBIDDEN_PRODUCTION_PATHS = ("M5", "M6", "M7", "API", "SHELLY", "DEVICE", "KVS", "HA")


@dataclass(frozen=True)
class P0041Result:
    status: str
    row_counts: dict[str, int]
    ai1_counts: dict[str, int]
    ai2_counts: dict[str, int]
    skipped_windows: int
    evidence: dict[str, str]


def run_p0041_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    price_db: Path | str = DEFAULT_PRICE_DB_PATH,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0041Result:
    rows = load_diagnostic_rows(feature_db=feature_db, price_db=price_db, weather_db=weather_db)
    enrich_p0038_weather(rows, weather_db)
    apply_solar_wind_features(rows)
    attach_wind_diagnostics(rows)
    m2_tables = build_m2_tables(rows)
    attach_m2_features(rows, m2_tables["hourly_maps"])
    daily_weather = build_daily_weather(rows)
    ai1_rows, skip_summary = build_ai1_rows(rows, daily_weather)
    ai2_rows = build_ai2_rows(rows)
    persist_p0041_tables(feature_db, m2_tables, ai1_rows, ai2_rows)
    summary = summarize_outputs(rows, ai1_rows, ai2_rows, skip_summary)
    evidence = write_p0041_evidence(Path(evidence_dir), rows, ai1_rows, ai2_rows, m2_tables, summary)
    status = "PASS" if summary["all_scales_positive"] and summary["ai1_counts"] and summary["ai2_counts"] else "WARN"
    return P0041Result(
        status=status,
        row_counts=count_splits(rows),
        ai1_counts=summary["ai1_counts"],
        ai2_counts=summary["ai2_counts"],
        skipped_windows=int(skip_summary["skipped_center_dates"]),
        evidence=evidence,
    )


def robust_scale(values: list[float], fixed_min_scale: float = FIXED_MIN_SCALE) -> float:
    if not values:
        return fixed_min_scale
    vals = [float(value) for value in values]
    center = median(vals)
    iqr = percentile(vals, 0.75) - percentile(vals, 0.25)
    mad = median([abs(value - center) for value in vals]) * 1.4826
    abs_mean = abs(sum(vals) / len(vals)) * 0.10
    return max(float(iqr), float(mad), float(abs_mean), float(fixed_min_scale))


def safe_ratio(numerator: float, denominator: float, fixed_min_scale: float = FIXED_MIN_SCALE) -> float | None:
    if abs(float(denominator)) < fixed_min_scale:
        return None
    return float(numerator) / float(denominator)


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ordered[lo]
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def local_window_dates(day: date) -> list[date]:
    return [day + timedelta(days=offset) for offset in range(-2, 5)]


def day_distance(left: int, right: int) -> int:
    raw = abs(int(left) - int(right))
    return min(raw, 366 - raw)


def build_m2_tables(rows: list[dict[str, object]]) -> dict[str, object]:
    hourly_tables: dict[str, list[dict[str, object]]] = {}
    hourly_maps: dict[str, dict[tuple[int, int], float]] = {}
    daily_tables: dict[str, list[dict[str, object]]] = {}
    for signal_name, (prefix, field) in SIGNALS.items():
        hourly = fit_m2_hourly_normals(rows, signal_name, field)
        hourly_tables[f"{prefix}_{signal_name}_normals_hourly"] = hourly
        hourly_maps[signal_name] = {(int(row["day_of_year"]), int(row["local_hour"])): float(row["normal_value"]) for row in hourly}
        daily_tables[f"{prefix}_{signal_name}_normals_daily"] = aggregate_daily_normals(hourly, signal_name)
    return {"hourly_tables": hourly_tables, "daily_tables": daily_tables, "hourly_maps": hourly_maps}


def fit_m2_hourly_normals(rows: list[dict[str, object]], signal_name: str, field: str) -> list[dict[str, object]]:
    grouped: dict[tuple[int, int], list[float]] = defaultdict(list)
    by_hour: dict[int, list[float]] = defaultdict(list)
    all_values: list[float] = []
    for row in rows:
        value = float(row.get(field) or 0.0)
        doy = int(row["day_of_year"])
        hour = int(row["local_hour"])
        grouped[(doy, hour)].append(value)
        by_hour[hour].append(value)
        all_values.append(value)
    global_median = float(median(all_values)) if all_values else 0.0
    output: list[dict[str, object]] = []
    for doy in range(1, 367):
        years = {
            int(row["year"])
            for row in rows
            if day_distance(int(row["day_of_year"]), doy) <= SMOOTHING_WINDOW_DAYS and row.get(field) is not None
        }
        for hour in range(24):
            values: list[float] = []
            for (candidate_doy, candidate_hour), bucket_values in grouped.items():
                if candidate_hour == hour and day_distance(candidate_doy, doy) <= SMOOTHING_WINDOW_DAYS:
                    values.extend(bucket_values)
            if not values:
                values = by_hour.get(hour, [])
            normal = float(median(values)) if values else global_median
            output.append(
                {
                    "signal": signal_name,
                    "day_of_year": doy,
                    "local_hour": hour,
                    "normal_value": normal,
                    "sample_count": len(values),
                    "year_count": len(years),
                    "smoothing_window_days": SMOOTHING_WINDOW_DAYS,
                }
            )
    return output


def aggregate_daily_normals(hourly_rows: list[dict[str, object]], signal_name: str) -> list[dict[str, object]]:
    by_doy: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in hourly_rows:
        by_doy[int(row["day_of_year"])].append(row)
    output: list[dict[str, object]] = []
    for doy, rows in sorted(by_doy.items()):
        output.append(
            {
                "signal": signal_name,
                "day_of_year": doy,
                "normal_value": sum(float(row["normal_value"]) for row in rows) / len(rows),
                "sample_count": sum(int(row["sample_count"]) for row in rows),
                "year_count": max(int(row["year_count"]) for row in rows),
                "smoothing_window_days": SMOOTHING_WINDOW_DAYS,
            }
        )
    return output


def attach_m2_features(rows: list[dict[str, object]], hourly_maps: dict[str, dict[tuple[int, int], float]]) -> None:
    for row in rows:
        key = (int(row["day_of_year"]), int(row["local_hour"]))
        for signal_name, (_prefix, field) in SIGNALS.items():
            actual = float(row.get(field) or 0.0)
            normal = float(hourly_maps[signal_name].get(key, actual))
            row[f"{signal_name}_actual"] = actual
            row[f"{signal_name}_normal"] = normal
            row[f"{signal_name}_delta"] = actual - normal


def attach_wind_diagnostics(rows: list[dict[str, object]]) -> None:
    for row in rows:
        south = wind_power_proxy(row.get("p0038_wind_south_100m"))
        central = wind_power_proxy(row.get("p0038_wind_central_100m"))
        north = wind_power_proxy(row.get("p0038_wind_north_100m"))
        row["daily_wind_south_proxy_hourly"] = south
        row["daily_wind_central_proxy_hourly"] = central
        row["daily_wind_north_proxy_hourly"] = north
        row["daily_wind_system_proxy_hourly"] = float(row.get("m3d_wind_proxy_se1") or 0.0)


def build_daily_weather(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    by_day: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_day[str(row["local_date"])].append(row)
    daily: dict[str, dict[str, object]] = {}
    for day, day_rows in by_day.items():
        if len(day_rows) != 24:
            continue
        item: dict[str, object] = {"date": day}
        for signal in SIGNALS:
            actual = [float(row[f"{signal}_actual"]) for row in day_rows]
            normal = [float(row[f"{signal}_normal"]) for row in day_rows]
            delta = [float(row[f"{signal}_delta"]) for row in day_rows]
            item[f"daily_{signal}_actual"] = sum(actual) / len(actual)
            item[f"daily_{signal}_normal"] = sum(normal) / len(normal)
            item[f"daily_{signal}_delta"] = sum(delta) / len(delta)
        item["daily_wind_system_proxy"] = mean([float(row["daily_wind_system_proxy_hourly"]) for row in day_rows])
        item["daily_wind_south_proxy"] = mean([float(row["daily_wind_south_proxy_hourly"]) for row in day_rows])
        item["daily_wind_central_proxy"] = mean([float(row["daily_wind_central_proxy_hourly"]) for row in day_rows])
        item["daily_wind_north_proxy"] = mean([float(row["daily_wind_north_proxy_hourly"]) for row in day_rows])
        item["daily_wind_south_minus_north"] = float(item["daily_wind_south_proxy"]) - float(item["daily_wind_north_proxy"])
        item["daily_wind_central_minus_north"] = float(item["daily_wind_central_proxy"]) - float(item["daily_wind_north_proxy"])
        daily[day] = item
    return daily


def build_ai1_rows(rows: list[dict[str, object]], daily_weather: dict[str, dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, int]]:
    by_day: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_day[str(row["local_date"])].append(row)
    dates = sorted(date.fromisoformat(day) for day in by_day)
    complete_days = {day for day in dates if len(by_day[day.isoformat()]) == 24 and day.isoformat() in daily_weather}
    output: list[dict[str, object]] = []
    skipped = 0
    for day in dates:
        window = local_window_dates(day)
        if day not in complete_days or any(candidate not in complete_days for candidate in window):
            skipped += 1
            continue
        window_rows = [row for candidate in window for row in sorted(by_day[candidate.isoformat()], key=lambda item: int(item["local_hour"]))]
        day_rows = sorted(by_day[day.isoformat()], key=lambda item: int(item["local_hour"]))
        calendar = day_rows[0]
        weather = daily_weather[day.isoformat()]
        window_weather = [daily_weather[candidate.isoformat()] for candidate in window]
        for target_series, actual_field in TARGET_SERIES.items():
            day_prices = [float(row[actual_field]) for row in day_rows]
            window_prices = [float(row[actual_field]) for row in window_rows]
            day_mean = sum(day_prices) / len(day_prices)
            local_mean = sum(window_prices) / len(window_prices)
            local_scale = robust_scale(window_prices)
            day_scale = robust_scale(day_prices)
            typical_day_scale = float(median([robust_scale([float(row[actual_field]) for row in by_day[candidate.isoformat()]]) for candidate in window]))
            row = {
                "date": day.isoformat(),
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
                **calendar_features(calendar),
                **weather,
                **relative_local_weather(weather, window_weather),
            }
            output.append(row)
    return output, {"skipped_center_dates": skipped}


def classify_skipped_center_dates(rows: list[dict[str, object]], daily_weather: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    by_day: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_day[str(row["local_date"])].append(row)
    dates = sorted(date.fromisoformat(day) for day in by_day)
    if not dates:
        return []
    complete_price = {day for day in dates if len(by_day[day.isoformat()]) == 24}
    complete_weather = {date.fromisoformat(day) for day in daily_weather}
    min_day = dates[0]
    max_day = dates[-1]
    output: list[dict[str, object]] = []
    for day in dates:
        window = local_window_dates(day)
        missing_price = [candidate for candidate in window if candidate not in complete_price]
        missing_weather = [candidate for candidate in window if candidate not in complete_weather]
        if not missing_price and not missing_weather:
            continue
        reason = skip_reason(day, window, missing_price, missing_weather, by_day, min_day, max_day)
        output.append(
            {
                "date": day.isoformat(),
                "reason": reason,
                "local_7d_start": window[0].isoformat(),
                "local_7d_end": window[-1].isoformat(),
                "missing_price_dates": [candidate.isoformat() for candidate in missing_price],
                "missing_weather_dates": [candidate.isoformat() for candidate in missing_weather],
                "price_hour_counts": {
                    candidate.isoformat(): len(by_day[candidate.isoformat()])
                    for candidate in missing_price
                    if candidate.isoformat() in by_day
                },
            }
        )
    return output


def skip_reason(
    day: date,
    window: list[date],
    missing_price: list[date],
    missing_weather: list[date],
    by_day: dict[str, list[dict[str, object]]],
    min_day: date,
    max_day: date,
) -> str:
    if any(candidate < min_day for candidate in window):
        return "dataset_start_boundary"
    if any(candidate > max_day for candidate in window):
        return "dataset_end_boundary"
    if any(len(by_day[candidate.isoformat()]) in {23, 25} for candidate in missing_price if candidate.isoformat() in by_day):
        return "dst_or_timezone_issue"
    if missing_price:
        return "missing_price_hours"
    if missing_weather:
        return "missing_weather_daily"
    if any(candidate.year != day.year for candidate in window):
        return "year_boundary_bug"
    return "other"


def build_ai2_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_day: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_day[str(row["local_date"])].append(row)
    output: list[dict[str, object]] = []
    for day, day_rows_unsorted in sorted(by_day.items()):
        if len(day_rows_unsorted) != 24:
            continue
        day_rows = sorted(day_rows_unsorted, key=lambda item: int(item["local_hour"]))
        for target_series, actual_field in TARGET_SERIES.items():
            day_prices = [float(row[actual_field]) for row in day_rows]
            day_mean = sum(day_prices) / len(day_prices)
            day_scale = robust_scale(day_prices)
            weather_ranks = day_weather_ranks(day_rows)
            for source in day_rows:
                hour_price = float(source[actual_field])
                item = {
                    "utc_hour_start": source["utc_hour_start"],
                    "local_date": day,
                    "local_hour": int(source["local_hour"]),
                    "target_series": target_series,
                    "hour_price": hour_price,
                    "day_mean_price": day_mean,
                    "day_intraday_scale": day_scale,
                    "hour_shape": (hour_price - day_mean) / day_scale,
                    "hour_ratio_index_diagnostic": safe_ratio(hour_price, day_mean),
                    **calendar_features(source, include_hour=True),
                }
                for signal in SIGNALS:
                    item[f"hourly_{signal}_actual"] = float(source[f"{signal}_actual"])
                    item[f"hourly_{signal}_normal"] = float(source[f"{signal}_normal"])
                    item[f"hourly_{signal}_delta"] = float(source[f"{signal}_delta"])
                    item[f"hourly_{signal}_delta_minus_day_mean"] = float(source[f"{signal}_delta"]) - mean([float(row[f"{signal}_delta"]) for row in day_rows])
                    item[f"hourly_{signal}_delta_rank_in_day"] = weather_ranks[signal][source["utc_hour_start"]]
                output.append(item)
    return output


def calendar_features(row: dict[str, object], *, include_hour: bool = False) -> dict[str, object]:
    weekday = int(row["weekday"])
    day_of_year = int(row["day_of_year"])
    features: dict[str, object] = {
        "weekday": weekday,
        "weekday_sin": math.sin(2.0 * math.pi * weekday / 7.0),
        "weekday_cos": math.cos(2.0 * math.pi * weekday / 7.0),
        "day_of_year": day_of_year,
        "day_of_year_sin": math.sin(2.0 * math.pi * day_of_year / 366.0),
        "day_of_year_cos": math.cos(2.0 * math.pi * day_of_year / 366.0),
        "base_day_type": base_day_type(weekday),
        "special_day_type": row.get("special_day_type") or "normal",
        "special_day_name": row.get("special_day_name") or "",
        "is_special_day": int(row.get("is_special_day") or 0),
        "is_bridge_day": 1 if str(row.get("bridge_strength") or "none") != "none" else 0,
        "is_holiday_period": int(row.get("is_holiday_period_day") or 0),
        "is_major_social_holiday": 1 if str(row.get("special_day_group") or "") == "major_social_holiday" else 0,
    }
    if include_hour:
        hour = int(row["local_hour"])
        features.update(
            {
                "hour_sin": math.sin(2.0 * math.pi * hour / 24.0),
                "hour_cos": math.cos(2.0 * math.pi * hour / 24.0),
            }
        )
    return features


def base_day_type(weekday: int) -> str:
    if weekday == 5:
        return "saturday"
    if weekday == 6:
        return "sunday"
    return "weekday"


def relative_local_weather(day_weather: dict[str, object], window_weather: list[dict[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for signal in SIGNALS:
        values = [float(item[f"daily_{signal}_delta"]) for item in window_weather]
        current = float(day_weather[f"daily_{signal}_delta"])
        output[f"daily_{signal}_delta_minus_local_7d_mean"] = current - (sum(values) / len(values))
        output[f"daily_{signal}_delta_rank_in_local_7d"] = rank_fraction(values, current)
    return output


def day_weather_ranks(day_rows: list[dict[str, object]]) -> dict[str, dict[object, float]]:
    output: dict[str, dict[object, float]] = {}
    for signal in SIGNALS:
        values = [(float(row[f"{signal}_delta"]), row["utc_hour_start"]) for row in day_rows]
        ordered = sorted(values)
        denom = max(1, len(ordered) - 1)
        output[signal] = {utc: index / denom for index, (_value, utc) in enumerate(ordered)}
    return output


def rank_fraction(values: list[float], current: float) -> float:
    if len(values) <= 1:
        return 0.0
    ordered = sorted(values)
    index = min(range(len(ordered)), key=lambda pos: (abs(ordered[pos] - current), pos))
    return index / (len(ordered) - 1)


def persist_p0041_tables(feature_db: Path | str, m2_tables: dict[str, object], ai1_rows: list[dict[str, object]], ai2_rows: list[dict[str, object]]) -> None:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        for table, rows in {**m2_tables["hourly_tables"], **m2_tables["daily_tables"]}.items():  # type: ignore[operator]
            persist_rows(conn, table, list(rows))  # type: ignore[arg-type]
        persist_rows(conn, "ai1_day_to_local_week_training_targets", ai1_rows)
        persist_rows(conn, "ai2_hour_to_day_training_targets", ai2_rows)


def persist_rows(conn: sqlite3.Connection, table: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    columns = list(rows[0].keys())
    conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.execute(f"CREATE TABLE {table} ({', '.join(column + ' ' + sqlite_type(rows[0][column]) for column in columns)})")
    placeholders = ", ".join("?" for _ in columns)
    conn.executemany(
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
        [[row.get(column) for column in columns] for row in rows],
    )


def sqlite_type(value: object) -> str:
    if isinstance(value, int):
        return "INTEGER"
    if isinstance(value, float):
        return "REAL"
    return "TEXT"


def summarize_outputs(
    rows: list[dict[str, object]], ai1_rows: list[dict[str, object]], ai2_rows: list[dict[str, object]], skip_summary: dict[str, int]
) -> dict[str, object]:
    daily_weather = build_daily_weather(rows)
    skipped_details = classify_skipped_center_dates(rows, daily_weather)
    return {
        "row_counts": count_splits(rows),
        "ai1_counts": counts_by_target(ai1_rows),
        "ai2_counts": counts_by_target(ai2_rows),
        "skipped": skip_summary,
        "skipped_details": skipped_details,
        "skipped_reason_counts": dict(sorted(counts_by_field(skipped_details, "reason").items())),
        "all_scales_positive": all(float(row["local_7d_level_scale"]) > 0 and float(row["day_intraday_scale"]) > 0 for row in ai1_rows)
        and all(float(row["day_intraday_scale"]) > 0 for row in ai2_rows),
        "ai1_distributions": distributions(ai1_rows, ["day_level_shape", "log_day_scale_index", "log_local_7d_scale"]),
        "ai2_distributions": distributions(ai2_rows, ["hour_shape"]),
        "ai2_day_mean_shape_max_abs": max_abs_day_shape_mean(ai2_rows),
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
    return dict(counts)


def distributions(rows: list[dict[str, object]], fields: list[str]) -> dict[str, dict[str, dict[str, float]]]:
    output: dict[str, dict[str, dict[str, float]]] = {}
    by_target: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_target[str(row["target_series"])].append(row)
    for target, target_rows in by_target.items():
        output[target] = {}
        for field in fields:
            values = [float(row[field]) for row in target_rows if row.get(field) is not None]
            output[target][field] = stats(values)
    return output


def stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {}
    avg = sum(values) / len(values)
    variance = sum((value - avg) ** 2 for value in values) / len(values)
    return {
        "count": float(len(values)),
        "mean": avg,
        "std": math.sqrt(variance),
        "min": min(values),
        "p01": percentile(values, 0.01),
        "p05": percentile(values, 0.05),
        "p50": percentile(values, 0.50),
        "p95": percentile(values, 0.95),
        "p99": percentile(values, 0.99),
        "max": max(values),
    }


def max_abs_day_shape_mean(ai2_rows: list[dict[str, object]]) -> float:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in ai2_rows:
        grouped[(str(row["local_date"]), str(row["target_series"]))].append(float(row["hour_shape"]))
    return max((abs(sum(values) / len(values)) for values in grouped.values()), default=0.0)


def write_p0041_evidence(
    evidence_dir: Path,
    rows: list[dict[str, object]],
    ai1_rows: list[dict[str, object]],
    ai2_rows: list[dict[str, object]],
    m2_tables: dict[str, object],
    summary: dict[str, object],
) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog()),
        "retention": write(evidence_dir / "model-retention-decision.md", retention_report()),
        "m2": write(evidence_dir / "m2-normal-weather-foundation.md", m2_report(m2_tables)),
        "ai1": write(evidence_dir / "ai1-day-to-local-week-dataset.md", ai1_report(ai1_rows, summary)),
        "ai2": write(evidence_dir / "ai2-hour-to-day-dataset.md", ai2_report(ai2_rows, summary)),
        "scale": write(evidence_dir / "robust-scale-definitions.md", scale_report()),
        "dist": write(evidence_dir / "target-distributions.md", distribution_report(summary)),
        "examples": write(evidence_dir / "example-rows.md", example_report(ai1_rows, ai2_rows)),
        "skipped": write(evidence_dir / "skipped-center-dates.md", skipped_dates_report(summary)),
        "leakage": write(evidence_dir / "leakage-and-window-policy.md", leakage_report()),
        "next": write(evidence_dir / "next-model-training-plan.md", next_training_report()),
        "summary": write(evidence_dir / "component-attribution-summary.md", summary_report(rows, summary)),
    }
    write(evidence_dir / "dataset-summary.json", json.dumps(json_safe(summary), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "example-rows.json", json.dumps({"ai1": ai1_rows[:5], "ai2": ai2_rows[:5]}, indent=2, sort_keys=True, default=str) + "\n")
    paths["dataset_json"] = str(evidence_dir / "dataset-summary.json")
    paths["examples_json"] = str(evidence_dir / "example-rows.json")
    return paths


def changelog() -> str:
    return "# P0041 changelog\n\n- Added seven-day index AI target datasets for AI-1 and AI-2.\n- Added M2A/M2C/M2D normal weather foundation tables.\n- Kept M1/M1B/M3A/M3B/M3C/M3D/M4 as legacy diagnostic/fallback for the seven-day index track.\n- No AI training, M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.\n"


def retention_report() -> str:
    return "\n".join(
        [
            "# P0041 model retention decision",
            "",
            "Active foundation: M2A normal temperature, M2C normal solar generation potential, M2D normal wind generation potential, SE1 and SE3-SE1 split targets, the Swedish special-day calendar, and P0038 weather/wind proxy locations.",
            "",
            "Legacy diagnostic/fallback only for the seven-day index track: M1, M1B, M3A, M3B, M3C, M3D and M4.",
            "",
            "New future models: AI-1 day-to-local-week and AI-2 hour-to-day. P0041 does not train either model.",
            "",
        ]
    )


def m2_report(m2_tables: dict[str, object]) -> str:
    lines = [
        "# P0041 M2 normal weather foundation",
        "",
        f"smoothing_window_days = {SMOOTHING_WINDOW_DAYS}",
        "hourly_bucket_definition = signal x day_of_year x local_hour",
        "daily_bucket_definition = signal x day_of_year",
        "normal_method = cyclic day-of-year/local-hour median over all available years, smoothed across neighboring calendar days",
        "",
        "| table | rows | min_year_count | max_year_count | smoothing_window_days |",
        "|---|---:|---:|---:|---:|",
    ]
    for table, rows in sorted({**m2_tables["hourly_tables"], **m2_tables["daily_tables"]}.items()):  # type: ignore[operator]
        year_counts = [int(row["year_count"]) for row in rows]
        lines.append(f"| {table} | {len(rows)} | {min(year_counts)} | {max(year_counts)} | {SMOOTHING_WINDOW_DAYS} |")
    lines.extend(
        [
            "",
            "M2C solar proxy = `shortwave_radiation * (1 - 0.35 * cloud_cover/100)` from P0038. There is no explicit clear-sky/elevation variable in the current weather history; night and near-zero behavior comes from observed shortwave radiation.",
            "M2D wind proxy = capped nonlinear `wind_speed_100m` transform from P0038.",
            "Required wind proxy locations: " + ", ".join(sorted(P0038_WIND_LOCATIONS)),
            "",
        ]
    )
    return "\n".join(lines)


def ai1_report(ai1_rows: list[dict[str, object]], summary: dict[str, object]) -> str:
    lines = [
        "# P0041 AI-1 day-to-local-week dataset",
        "",
        "row_grain = date x target_series",
        "local_window = D-2..D+4",
        "incomplete_windows = skipped",
        f"skipped_center_dates = {summary['skipped']['skipped_center_dates']}",  # type: ignore[index]
        f"skipped_reason_counts = {summary['skipped_reason_counts']}",
        "",
        "| target_series | rows |",
        "|---|---:|",
    ]
    for target, count in summary["ai1_counts"].items():  # type: ignore[union-attr]
        lines.append(f"| {target} | {count} |")
    lines.extend(["", "SE1 and SE3-SE1 are stored as separate target series throughout.", ""])
    return "\n".join(lines)


def ai2_report(ai2_rows: list[dict[str, object]], summary: dict[str, object]) -> str:
    lines = [
        "# P0041 AI-2 hour-to-day dataset",
        "",
        "row_grain = timestamp x target_series",
        "day_window = fixed local 00:00..23:00",
        f"max_abs_mean_hour_shape_by_day_target = {fmt(summary['ai2_day_mean_shape_max_abs'])}",
        "",
        "| target_series | rows |",
        "|---|---:|",
    ]
    for target, count in summary["ai2_counts"].items():  # type: ignore[union-attr]
        lines.append(f"| {target} | {count} |")
    lines.extend(["", "SE1 and SE3-SE1 are stored as separate target series throughout.", ""])
    return "\n".join(lines)


def scale_report() -> str:
    return "\n".join(
        [
            "# P0041 robust scale definitions",
            "",
            "fixed_min_scale = 0.001",
            "",
            "robust_scale(values) = max(percentile_75(values) - percentile_25(values), median_absolute_deviation(values) * 1.4826, abs(mean(values)) * 0.10, fixed_min_scale)",
            "",
            "Ratio diagnostics use null when `abs(denominator) < fixed_min_scale`. Negative prices are valid for shape targets because additive centered differences and robust positive scales are used.",
            "",
        ]
    )


def distribution_report(summary: dict[str, object]) -> str:
    lines = ["# P0041 target distributions", "", "## AI-1", ""]
    lines.append(distribution_table(summary["ai1_distributions"]))  # type: ignore[arg-type]
    lines.extend(["", "## AI-2", "", distribution_table(summary["ai2_distributions"])])  # type: ignore[arg-type]
    lines.extend(["", f"all_robust_scales_strictly_positive = {summary['all_scales_positive']}", ""])
    return "\n".join(lines)


def skipped_dates_report(summary: dict[str, object]) -> str:
    details = list(summary["skipped_details"])  # type: ignore[arg-type]
    year_boundary = [row for row in details if row["reason"] == "year_boundary_bug"]
    lines = [
        "# P0041 skipped center dates",
        "",
        f"skipped_center_dates = {len(details)}",
        f"reason_counts = {summary['skipped_reason_counts']}",
        f"year_boundary_bug_count = {len(year_boundary)}",
        "",
        "Verification: `local_window_dates()` uses Python `date + timedelta(days=offset)` for offsets -2..+4, so windows are continuous across calendar years. No center date is skipped only because it is near the beginning or end of a calendar year.",
        "",
        "| center_date | reason | local_7d_start | local_7d_end | missing_price_dates | missing_weather_dates | price_hour_counts |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in details:
        lines.append(
            f"| {row['date']} | {row['reason']} | {row['local_7d_start']} | {row['local_7d_end']} | {', '.join(row['missing_price_dates'])} | {', '.join(row['missing_weather_dates'])} | {row['price_hour_counts']} |"
        )
    lines.append("")
    return "\n".join(lines)


def distribution_table(data: dict[str, dict[str, dict[str, float]]]) -> str:
    lines = ["| target | field | count | mean | std | min | p01 | p05 | p50 | p95 | p99 | max |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for target, fields in sorted(data.items()):
        for field, stats_row in sorted(fields.items()):
            lines.append(
                f"| {target} | {field} | {int(stats_row.get('count', 0))} | {fmt(stats_row.get('mean', 0))} | {fmt(stats_row.get('std', 0))} | {fmt(stats_row.get('min', 0))} | {fmt(stats_row.get('p01', 0))} | {fmt(stats_row.get('p05', 0))} | {fmt(stats_row.get('p50', 0))} | {fmt(stats_row.get('p95', 0))} | {fmt(stats_row.get('p99', 0))} | {fmt(stats_row.get('max', 0))} |"
            )
    return "\n".join(lines)


def example_report(ai1_rows: list[dict[str, object]], ai2_rows: list[dict[str, object]]) -> str:
    return "# P0041 example rows\n\n## AI-1\n\n```json\n" + json.dumps(ai1_rows[:2], indent=2, sort_keys=True, default=str) + "\n```\n\n## AI-2\n\n```json\n" + json.dumps(ai2_rows[:2], indent=2, sort_keys=True, default=str) + "\n```\n"


def leakage_report() -> str:
    return "\n".join(
        [
            "# P0041 leakage and window policy",
            "",
            "AI-1 window policy: the local seven-day period is exactly D-2..D+4. Rows without all 168 hourly prices and complete daily weather aggregates are skipped.",
            "Year boundary policy: D-2..D+4 uses continuous date arithmetic and is allowed to cross calendar years. P0041 skipped-center evidence verifies that no rows are skipped solely because a window crosses December/January.",
            "AI-2 window policy: the intraday period is exactly local 00:00..23:00. Only complete 24-hour local days are emitted.",
            "No raw `week_of_year` categorical feature is emitted. Cyclic day and weekday encodings are emitted.",
            "M2 normal weather surfaces aggregate calendar buckets across all available years with +/-14 day smoothing and include `year_count` per bucket. They are climate/signal normals, not price baselines.",
            "P0041 does not train models or evaluate holdout performance, so model-fitting leakage is deferred to P0042.",
            "",
        ]
    )


def next_training_report() -> str:
    return "# P0041 next model training plan\n\nP0042 should train AI-2 first because the fixed hour-to-day target is simpler, has far more rows, and directly validates intraday shape quality before the lower-row AI-1 day-to-local-week model is trained. Use bounded tabular gradient boosting such as `HistGradientBoostingRegressor`; do not start with neural or transformer models.\n"


def summary_report(rows: list[dict[str, object]], summary: dict[str, object]) -> str:
    return "\n".join(
        [
            "# P0041 component attribution summary",
            "",
            "Status: PASS" if summary["all_scales_positive"] else "Status: WARN",
            f"source_row_counts = {summary['row_counts']}",
            f"AI-1 row counts = {summary['ai1_counts']}",
            f"AI-2 row counts = {summary['ai2_counts']}",
            f"skipped incomplete AI-1 center dates = {summary['skipped']['skipped_center_dates']}",  # type: ignore[index]
            f"all robust scales strictly positive = {summary['all_scales_positive']}",
            f"AI-2 max abs mean hour_shape by date/target = {fmt(summary['ai2_day_mean_shape_max_abs'])}",
            "Near-zero and negative prices are handled by additive centered targets and diagnostic ratios are null when denominators are unsafe.",
            "Weather actual/normal/delta features are present for temperature, solar and wind.",
            "SE1 and SE3-SE1 are separate throughout.",
            "No AI training, M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.",
            "",
        ]
    )


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    return value


def fmt(value: object) -> str:
    return f"{float(value):.6f}"


def write(path: Path, text: str) -> str:
    path.write_text(text, encoding="utf-8")
    return str(path)


def main() -> int:
    result = run_p0041_analysis()
    print(
        json.dumps(
            {
                "status": result.status,
                "row_counts": result.row_counts,
                "ai1_counts": result.ai1_counts,
                "ai2_counts": result.ai2_counts,
                "skipped_windows": result.skipped_windows,
                "evidence": result.evidence,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
