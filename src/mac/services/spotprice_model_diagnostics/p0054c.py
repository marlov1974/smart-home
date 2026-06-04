"""P0054C LABB SE4 consumption advanced AI without price."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
import argparse
import csv
import json
import math
import sqlite3
import time
import warnings

import numpy as np

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_model_diagnostics import p0052
from src.mac.services.spotprice_model_diagnostics.forecast_period_policy import (
    canonical_split_for_timestamp,
    is_modeling_target_timestamp,
    policy_summary,
)
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH
from src.mac.services.swedish_calendar.core import classify_special_day


PACKAGE_ID = "P0054C"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054C")
SOURCE_TABLE = "physical_balance_se1_se4_hourly_v1"
WEATHER_TABLE = "weather_area_hourly"
WEATHER_AREA_PROXY = "south_connected_weather"
TARGET = "consumption_se4"
TARGET_FIELD = "target_consumption_se4_mw"
WEATHER_PROXY_LABEL = "weather_actual_as_forecast_proxy"
DATASET_KIND = "offline_labb_experiment_not_deployable"
RANDOM_SEED = 54
HORIZONS = (1, 3, 6, 12, 24, 48, 72, 96, 120, 144, 168)
PATH_HORIZONS = tuple(range(1, 169))
LAGS = (1, 2, 3, 6, 12, 24, 48, 72, 168)
ROLL_WINDOWS = (6, 12, 24, 48, 168)
HOLDOUT_START = "2025-06-01T00:00:00Z"
FORBIDDEN_FEATURE_TERMS = (
    "price",
    "m4",
    "spot",
    "production",
    "flow",
    "export",
    "import",
    "a61",
    "capacity",
    "utilization",
    "margin",
    "continental",
)
BASELINE_COLUMNS = (
    "pred_B0_same_hour_previous_day",
    "pred_B1_same_hour_previous_week",
    "pred_B2_train_calendar_profile",
    "pred_B3_train_seasonal_profile",
    "pred_B4_recent_24h_mean_adjusted_by_hour_profile",
)
HGB_PREDICTION_COLUMN = "pred_HGB_G4_calendar_load_lags_rollups_weather_proxy"
MLP_PREDICTION_COLUMN = "pred_MLP_G4_calendar_load_lags_rollups_weather_proxy"


@dataclass(frozen=True)
class Encoder:
    categories: dict[str, list[str]]
    means: dict[str, float]
    scales: dict[str, float]


@dataclass(frozen=True)
class P0054CResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054c_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054CResult:
    started = time.monotonic()
    source_rows = load_se4_consumption_rows(feature_db)
    target_contract = validate_target_contract(source_rows)
    if not target_contract["ok"]:
        raise RuntimeError(f"P0054C target contract failed: {target_contract}")

    weather_rows, weather_contract = load_weather_proxy_rows(weather_db)
    rows = build_direct_horizon_rows(source_rows, weather_rows, HORIZONS)
    path_candidate_rows = build_weekly_path_candidate_rows(source_rows, weather_rows)
    split_counts = assign_global_splits(rows)
    assign_global_splits(path_candidate_rows)
    train_rows = [row for row in rows if row["split"] == "train"]
    profiles = fit_train_profiles(train_rows)
    apply_profile_features(rows, profiles)
    apply_profile_features(path_candidate_rows, profiles)
    source_by_ts = {str(row["timestamp_utc"]): row for row in source_rows}
    apply_baseline_predictions(rows, profiles, source_by_ts)
    apply_baseline_predictions(path_candidate_rows, profiles, source_by_ts)

    feature_contract = feature_group_contract()
    feature_review = validate_feature_contract(feature_contract)
    if not feature_review["ok"]:
        raise RuntimeError(f"P0054C forbidden feature contract: {feature_review}")

    baseline_results = evaluate_baselines(rows)
    hgb_result, hgb_importance = fit_hgb_benchmark(rows, feature_contract["G4_calendar_load_lags_rollups_weather_proxy"]["features"])
    mlp_result = fit_advanced_mlp(rows, feature_contract["G4_calendar_load_lags_rollups_weather_proxy"]["features"])
    scored_rows = attach_model_predictions(rows, hgb_result["predictions"], mlp_result["predictions"])
    scored_path_rows = attach_path_predictions(
        path_candidate_rows,
        hgb_result,
        mlp_result,
        feature_contract["G4_calendar_load_lags_rollups_weather_proxy"]["features"],
    )

    comparison = compare_hgb_vs_mlp(hgb_result, mlp_result)
    direct_results = evaluate_direct_horizons(scored_rows, (HGB_PREDICTION_COLUMN, MLP_PREDICTION_COLUMN))
    weekly_summary, weekly_path_rows = evaluate_weekly_168h_paths(scored_path_rows, (HGB_PREDICTION_COLUMN, MLP_PREDICTION_COLUMN))
    conditional_results = evaluate_conditional_regimes(scored_rows, (HGB_PREDICTION_COLUMN, MLP_PREDICTION_COLUMN))
    pattern_assessment = assess_se3_pattern(comparison, weekly_summary)
    fairness = validate_identical_row_sets(scored_rows, (HGB_PREDICTION_COLUMN, MLP_PREDICTION_COLUMN))
    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": "PASS" if fairness["ok"] and feature_review["ok"] else "WARN",
        "dataset_kind": DATASET_KIND,
        "split_policy": policy_summary(),
        "source_table": SOURCE_TABLE,
        "weather_table": WEATHER_TABLE,
        "target_contract": target_contract,
        "weather_contract": weather_contract,
        "weather_proxy_label": WEATHER_PROXY_LABEL,
        "feature_contract": feature_contract,
        "feature_review": feature_review,
        "split_counts": split_counts,
        "row_counts": {
            "source_rows": len(source_rows),
            "direct_horizon_rows": len(rows),
            "path_candidate_rows": len(path_candidate_rows),
            "weekly_path_origins": int(weekly_summary["weekly_origin_count"]),
        },
        "baseline_results": baseline_results,
        "strongest_baseline": strongest_baseline_by_holdout_mae(baseline_results),
        "hgb_results": hgb_result["metrics"],
        "advanced_ai_results": mlp_result["metrics"],
        "advanced_ai_training": mlp_result["training"],
        "hgb_vs_advanced_ai_comparison": comparison,
        "direct_horizon_results": direct_results,
        "weekly_168h_path_results": weekly_summary,
        "conditional_regime_results": conditional_results,
        "se3_pattern_assessment": pattern_assessment,
        "feature_importance_or_attribution": hgb_importance,
        "fairness": fairness,
        "runtime_seconds": round(time.monotonic() - started, 3),
    }
    evidence = write_p0054c_evidence(Path(evidence_dir), scored_rows, scored_path_rows, weekly_path_rows, summary)
    return P0054CResult(status=str(summary["status"]), row_counts=summary["row_counts"], evidence=evidence)


def load_se4_consumption_rows(feature_db: Path | str = DEFAULT_FEATURE_DB) -> list[dict[str, object]]:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        if not table_exists(conn, SOURCE_TABLE):
            raise RuntimeError(f"P0054C source table missing: {SOURCE_TABLE}")
        return [
            normalize_source_row(dict(row))
            for row in conn.execute(
                f"""
                SELECT timestamp_utc, model_cet_timestamp, model_cet_date, model_cet_hour, consumption_se4
                FROM {SOURCE_TABLE}
                ORDER BY timestamp_utc
                """
            )
        ]


def normalize_source_row(row: dict[str, object]) -> dict[str, object]:
    ts = p0052.normalize_utc_text(row["timestamp_utc"])
    dt = p0052.parse_utc(ts)
    model = dt + timedelta(hours=1)
    return {
        "timestamp_utc": ts,
        "model_cet_timestamp": p0052.format_utc(model),
        "model_cet_date": model.date().isoformat(),
        "model_cet_hour": model.hour,
        "model_cet_weekday": model.weekday(),
        "model_cet_day_of_year": model.timetuple().tm_yday,
        "consumption_se4": float(row["consumption_se4"]),
    }


def validate_target_contract(rows: list[dict[str, object]]) -> dict[str, object]:
    timestamps = [str(row["timestamp_utc"]) for row in rows]
    values = [float(row["consumption_se4"]) for row in rows if is_finite(row.get("consumption_se4"))]
    duplicates = len(timestamps) - len(set(timestamps))
    nonfinite = len(rows) - len(values)
    nonpositive = sum(1 for value in values if value <= 0)
    target_rows = [row for row in rows if is_modeling_target_timestamp(str(row["timestamp_utc"]))]
    return {
        "ok": bool(rows) and duplicates == 0 and nonfinite == 0 and nonpositive == 0 and bool(target_rows),
        "source_table": SOURCE_TABLE,
        "target": TARGET,
        "unit": "MW hourly mean",
        "rows": len(rows),
        "target_rows_from_2022_06_01": len(target_rows),
        "start": min(timestamps) if timestamps else "",
        "end": max(timestamps) if timestamps else "",
        "duplicates": duplicates,
        "nonfinite_values": nonfinite,
        "nonpositive_values": nonpositive,
        "mean_mw": mean_float(values),
        "median_mw": percentile(values, 0.5) if values else None,
        "p10_mw": percentile(values, 0.1) if values else None,
        "p90_mw": percentile(values, 0.9) if values else None,
    }


def load_weather_proxy_rows(weather_db: Path | str = DEFAULT_WEATHER_DB_PATH) -> tuple[dict[str, dict[str, object]], dict[str, object]]:
    path = Path(weather_db).expanduser()
    if not path.exists():
        return {}, {"available": False, "reason": "weather_db_missing", "input_classification": "excluded_unavailable"}
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        if not table_exists(conn, WEATHER_TABLE):
            return {}, {"available": False, "reason": "weather_table_missing", "input_classification": "excluded_unavailable"}
        rows = {}
        for row in conn.execute(
            f"""
            SELECT utc_hour_start, weighted_temperature_2m, weighted_apparent_temperature,
                   weighted_wind_speed_100m, weighted_cloud_cover, weighted_shortwave_radiation,
                   weighted_precipitation, weighted_snowfall, weighted_relative_humidity_2m,
                   heating_degree_hours, cooling_degree_hours, source, source_model
            FROM {WEATHER_TABLE}
            WHERE area_proxy = ?
            ORDER BY utc_hour_start
            """,
            (WEATHER_AREA_PROXY,),
        ):
            ts = p0052.normalize_utc_text(row["utc_hour_start"])
            rows[ts] = {
                "weather_proxy_temperature_2m_se4": safe_float(row["weighted_temperature_2m"]),
                "weather_proxy_apparent_temperature_se4": safe_float(row["weighted_apparent_temperature"]),
                "weather_proxy_wind_100m_se4": safe_float(row["weighted_wind_speed_100m"]),
                "weather_proxy_cloud_cover_se4": safe_float(row["weighted_cloud_cover"]),
                "weather_proxy_shortwave_radiation_se4": safe_float(row["weighted_shortwave_radiation"]),
                "weather_proxy_precipitation_se4": safe_float(row["weighted_precipitation"]),
                "weather_proxy_snowfall_se4": safe_float(row["weighted_snowfall"]),
                "weather_proxy_humidity_se4": safe_float(row["weighted_relative_humidity_2m"]),
                "weather_proxy_heating_degree_hours_se4": safe_float(row["heating_degree_hours"]),
                "weather_proxy_cooling_degree_hours_se4": safe_float(row["cooling_degree_hours"]),
                "weather_proxy_label": WEATHER_PROXY_LABEL,
            }
    return rows, {
        "available": bool(rows),
        "table": WEATHER_TABLE,
        "area_proxy": WEATHER_AREA_PROXY,
        "rows": len(rows),
        "start": min(rows) if rows else "",
        "end": max(rows) if rows else "",
        "input_classification": "proxy",
        "proxy_label": WEATHER_PROXY_LABEL,
        "forecast_safety": "not_a_separate_forecast_model; LABB proxy only",
    }


def build_direct_horizon_rows(
    source_rows: list[dict[str, object]],
    weather_rows: dict[str, dict[str, object]],
    horizons: tuple[int, ...],
) -> list[dict[str, object]]:
    values = [float(row["consumption_se4"]) for row in source_rows]
    rows: list[dict[str, object]] = []
    min_origin_index = max(max(LAGS), max(ROLL_WINDOWS))
    for origin_index, origin in enumerate(source_rows):
        if origin_index < min_origin_index:
            continue
        for horizon in horizons:
            target_index = origin_index + horizon
            if target_index >= len(source_rows):
                continue
            target = source_rows[target_index]
            target_ts = str(target["timestamp_utc"])
            if not is_modeling_target_timestamp(target_ts):
                continue
            row = {
                "forecast_origin_timestamp_utc": origin["timestamp_utc"],
                "input_data_cutoff_utc": p0052.format_utc(p0052.parse_utc(str(origin["timestamp_utc"])) - timedelta(hours=1)),
                "target_timestamp_utc": target_ts,
                "horizon_h": horizon,
                TARGET_FIELD: float(target["consumption_se4"]),
                "area_or_target": "SE4_consumption",
                "prediction_kind": "consumption_mw",
                "dataset_kind": DATASET_KIND,
                "weather_proxy_label": WEATHER_PROXY_LABEL if target_ts in weather_rows else "weather_proxy_missing",
            }
            attach_calendar_features(row, p0052.parse_utc(target_ts) + timedelta(hours=1))
            row.update(lag_features_at_origin(values, origin_index))
            row.update(rolling_features_at_origin(values, origin_index))
            row.update(weather_rows.get(target_ts, {}))
            rows.append(row)
    return rows


def build_weekly_path_candidate_rows(
    source_rows: list[dict[str, object]],
    weather_rows: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    values = [float(row["consumption_se4"]) for row in source_rows]
    min_origin_index = max(max(LAGS), max(ROLL_WINDOWS))
    rows: list[dict[str, object]] = []
    for origin_index, origin in enumerate(source_rows):
        if origin_index < min_origin_index:
            continue
        if p0052.parse_utc(str(origin["timestamp_utc"])) < p0052.parse_utc(HOLDOUT_START):
            continue
        if (p0052.parse_utc(str(origin["timestamp_utc"])) - p0052.parse_utc(HOLDOUT_START)).total_seconds() % (168 * 3600) != 0:
            continue
        if origin_index + 168 >= len(source_rows):
            continue
        for horizon in PATH_HORIZONS:
            target = source_rows[origin_index + horizon]
            target_ts = str(target["timestamp_utc"])
            row = {
                "forecast_origin_timestamp_utc": origin["timestamp_utc"],
                "input_data_cutoff_utc": p0052.format_utc(p0052.parse_utc(str(origin["timestamp_utc"])) - timedelta(hours=1)),
                "target_timestamp_utc": target_ts,
                "horizon_h": horizon,
                TARGET_FIELD: float(target["consumption_se4"]),
                "area_or_target": "SE4_consumption",
                "prediction_kind": "consumption_mw",
                "dataset_kind": DATASET_KIND,
                "weather_proxy_label": WEATHER_PROXY_LABEL if target_ts in weather_rows else "weather_proxy_missing",
            }
            attach_calendar_features(row, p0052.parse_utc(target_ts) + timedelta(hours=1))
            row.update(lag_features_at_origin(values, origin_index))
            row.update(rolling_features_at_origin(values, origin_index))
            row.update(weather_rows.get(target_ts, {}))
            rows.append(row)
    return rows


def attach_calendar_features(row: dict[str, object], target_model_dt: datetime) -> None:
    day = target_model_dt.date()
    special = classify_special_day(day)
    hour = target_model_dt.hour
    weekday = day.weekday()
    doy = target_model_dt.timetuple().tm_yday
    row.update(
        {
            "target_model_cet_timestamp": p0052.format_utc(target_model_dt),
            "target_model_cet_date": day.isoformat(),
            "target_model_cet_hour": hour,
            "target_model_cet_weekday": weekday,
            "target_model_cet_day_of_year": doy,
            "target_month": day.month,
            "target_hour_sin": math.sin(2 * math.pi * hour / 24),
            "target_hour_cos": math.cos(2 * math.pi * hour / 24),
            "target_dayofyear_sin": math.sin(2 * math.pi * doy / 366),
            "target_dayofyear_cos": math.cos(2 * math.pi * doy / 366),
            "is_weekend": 1 if weekday >= 5 else 0,
            "is_workday": 1 if weekday < 5 and not special["is_public_holiday"] else 0,
            "is_holiday": int(bool(special["is_public_holiday"]) or bool(special["is_major_social_holiday"])),
            "is_bridge_day": int(bool(special["is_bridge_day"])),
            "is_holiday_period": int(bool(special["is_holiday_period_day"])),
            "is_major_social_holiday": int(bool(special["is_major_social_holiday"])),
            "holiday_strength": float(special["holiday_strength"]),
            "special_day_type": str(special["special_day_type"]),
            "special_day_group": str(special["special_day_group"]),
        }
    )


def lag_features_at_origin(values: list[float], origin_index: int) -> dict[str, float]:
    return {f"consumption_se4_lag_{lag}h": values[origin_index - lag] for lag in LAGS}


def rolling_features_at_origin(values: list[float], origin_index: int) -> dict[str, float]:
    out: dict[str, float] = {}
    for window in ROLL_WINDOWS:
        subset = values[origin_index - window : origin_index]
        out[f"consumption_se4_roll_mean_{window}h"] = sum(subset) / len(subset)
    subset24 = values[origin_index - 24 : origin_index]
    mean24 = sum(subset24) / len(subset24)
    out["consumption_se4_roll_min_24h"] = min(subset24)
    out["consumption_se4_roll_max_24h"] = max(subset24)
    out["consumption_se4_roll_std_24h"] = math.sqrt(sum((value - mean24) ** 2 for value in subset24) / len(subset24))
    out["consumption_se4_ramp_1h"] = values[origin_index - 1] - values[origin_index - 2]
    out["consumption_se4_ramp_24h"] = values[origin_index - 1] - values[origin_index - 24]
    out["consumption_se4_same_hour_24h_vs_168h"] = values[origin_index - 24] - values[origin_index - 168]
    return out


def assign_global_splits(rows: list[dict[str, object]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        split = canonical_split_for_timestamp(str(row["target_timestamp_utc"]))
        row["split"] = split
        counts[split] += 1
    return dict(counts)


def fit_train_profiles(train_rows: list[dict[str, object]]) -> dict[str, object]:
    profiles: dict[str, object] = {}
    profiles["calendar_hour_weekday"] = grouped_mean(train_rows, ("target_model_cet_weekday", "target_model_cet_hour"), TARGET_FIELD)
    profiles["seasonal_hour_weekday"] = grouped_mean(train_rows, ("target_month", "target_model_cet_weekday", "target_model_cet_hour"), TARGET_FIELD)
    profiles["temperature_normals"] = grouped_mean(
        [row for row in train_rows if is_finite(row.get("weather_proxy_temperature_2m_se4"))],
        ("target_month", "target_model_cet_hour"),
        "weather_proxy_temperature_2m_se4",
    )
    return profiles


def apply_profile_features(rows: list[dict[str, object]], profiles: dict[str, object]) -> None:
    for row in rows:
        row["weather_proxy_train_normal_temperature_2m_se4"] = profile_predict(profiles["temperature_normals"], row, ("target_month", "target_model_cet_hour"))
        if is_finite(row.get("weather_proxy_temperature_2m_se4")):
            row["weather_proxy_temperature_delta_from_train_normal_se4"] = (
                float(row["weather_proxy_temperature_2m_se4"]) - float(row["weather_proxy_train_normal_temperature_2m_se4"])
            )
        else:
            row["weather_proxy_temperature_delta_from_train_normal_se4"] = 0.0
        row["weather_proxy_cold_spell_flag_se4"] = 1 if safe_float(row.get("weather_proxy_heating_degree_hours_se4")) >= 12 else 0


def apply_baseline_predictions(rows: list[dict[str, object]], profiles: dict[str, object], source_by_ts: dict[str, dict[str, object]]) -> None:
    global_mean = float(profiles["calendar_hour_weekday"]["global"])  # type: ignore[index]
    for row in rows:
        target_dt = p0052.parse_utc(str(row["target_timestamp_utc"]))
        origin_dt = p0052.parse_utc(str(row["forecast_origin_timestamp_utc"]))
        row["pred_B0_same_hour_previous_day"] = forecast_safe_history_lookup(source_by_ts, target_dt - timedelta(hours=24), origin_dt, row)
        row["pred_B1_same_hour_previous_week"] = forecast_safe_history_lookup(source_by_ts, target_dt - timedelta(hours=168), origin_dt, row)
        row["pred_B2_train_calendar_profile"] = profile_predict(profiles["calendar_hour_weekday"], row, ("target_model_cet_weekday", "target_model_cet_hour"))
        row["pred_B3_train_seasonal_profile"] = profile_predict(profiles["seasonal_hour_weekday"], row, ("target_month", "target_model_cet_weekday", "target_model_cet_hour"))
        profile_delta = float(row["pred_B2_train_calendar_profile"]) - global_mean
        row["pred_B4_recent_24h_mean_adjusted_by_hour_profile"] = float(row["consumption_se4_roll_mean_24h"]) + profile_delta


def forecast_safe_history_lookup(
    source_by_ts: dict[str, dict[str, object]],
    desired_dt: datetime,
    origin_dt: datetime,
    row: dict[str, object],
) -> float:
    if desired_dt < origin_dt:
        source = source_by_ts.get(p0052.format_utc(desired_dt))
        if source:
            return float(source["consumption_se4"])
    target_hour = int(row["target_model_cet_hour"])
    for offset in range(24, 24 * 28 + 1, 24):
        candidate = origin_dt - timedelta(hours=offset)
        source = source_by_ts.get(p0052.format_utc(candidate))
        if source and int(source["model_cet_hour"]) == target_hour:
            return float(source["consumption_se4"])
    return float(row["consumption_se4_roll_mean_168h"])


def feature_group_contract() -> dict[str, dict[str, object]]:
    calendar = [
        "horizon_h",
        "target_model_cet_hour",
        "target_model_cet_weekday",
        "target_model_cet_day_of_year",
        "target_month",
        "target_hour_sin",
        "target_hour_cos",
        "target_dayofyear_sin",
        "target_dayofyear_cos",
        "is_weekend",
        "is_workday",
        "is_holiday",
        "is_bridge_day",
        "is_holiday_period",
        "is_major_social_holiday",
        "holiday_strength",
        "special_day_type",
        "special_day_group",
    ]
    lags = [f"consumption_se4_lag_{lag}h" for lag in LAGS]
    rollups = [f"consumption_se4_roll_mean_{window}h" for window in ROLL_WINDOWS] + [
        "consumption_se4_roll_min_24h",
        "consumption_se4_roll_max_24h",
        "consumption_se4_roll_std_24h",
        "consumption_se4_ramp_1h",
        "consumption_se4_ramp_24h",
        "consumption_se4_same_hour_24h_vs_168h",
    ]
    weather = [
        "weather_proxy_temperature_2m_se4",
        "weather_proxy_apparent_temperature_se4",
        "weather_proxy_wind_100m_se4",
        "weather_proxy_cloud_cover_se4",
        "weather_proxy_shortwave_radiation_se4",
        "weather_proxy_precipitation_se4",
        "weather_proxy_snowfall_se4",
        "weather_proxy_humidity_se4",
        "weather_proxy_heating_degree_hours_se4",
        "weather_proxy_cooling_degree_hours_se4",
        "weather_proxy_train_normal_temperature_2m_se4",
        "weather_proxy_temperature_delta_from_train_normal_se4",
        "weather_proxy_cold_spell_flag_se4",
    ]
    return {
        "G0_calendar_only": {"input_classification": "forecast_safe", "features": calendar},
        "G1_calendar_plus_load_lags": {"input_classification": "forecast_safe", "features": calendar + lags},
        "G2_calendar_plus_load_lags_rollups": {"input_classification": "forecast_safe", "features": calendar + lags + rollups},
        "G3_calendar_weather_proxy": {"input_classification": "proxy", "features": calendar + weather, "proxy_label": WEATHER_PROXY_LABEL},
        "G4_calendar_load_lags_rollups_weather_proxy": {
            "input_classification": "mixed_forecast_safe_and_proxy",
            "features": calendar + lags + rollups + weather,
            "proxy_label": WEATHER_PROXY_LABEL,
        },
    }


def validate_feature_contract(contract: dict[str, dict[str, object]]) -> dict[str, object]:
    violations = []
    for group, meta in contract.items():
        for feature in meta["features"]:  # type: ignore[index]
            lowered = str(feature).lower()
            for term in FORBIDDEN_FEATURE_TERMS:
                if term in lowered:
                    violations.append({"group": group, "feature": feature, "term": term})
    return {"ok": not violations, "violations": violations, "forbidden_terms": FORBIDDEN_FEATURE_TERMS}


def evaluate_baselines(rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        baseline: {
            str(horizon): metrics_by_split([row for row in rows if int(row["horizon_h"]) == horizon], baseline)
            for horizon in HORIZONS
        }
        for baseline in BASELINE_COLUMNS
    }


def fit_hgb_benchmark(rows: list[dict[str, object]], features: list[str]) -> tuple[dict[str, object], list[dict[str, object]]]:
    from sklearn.ensemble import HistGradientBoostingRegressor

    result = fit_model(
        rows,
        features,
        HistGradientBoostingRegressor(max_iter=120, learning_rate=0.055, max_leaf_nodes=31, min_samples_leaf=80, random_state=RANDOM_SEED),
        "HistGradientBoostingRegressor",
    )
    importance = permutation_importance_light(result["model"], result["encoder"], [row for row in rows if row["split"] == "validate"], features)
    return result, importance


def fit_advanced_mlp(rows: list[dict[str, object]], features: list[str]) -> dict[str, object]:
    from sklearn.exceptions import ConvergenceWarning
    from sklearn.neural_network import MLPRegressor

    started = time.monotonic()
    model = MLPRegressor(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        alpha=0.0005,
        batch_size=512,
        learning_rate_init=0.001,
        max_iter=70,
        early_stopping=True,
        validation_fraction=0.12,
        n_iter_no_change=8,
        random_state=RANDOM_SEED,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        result = fit_model(rows, features, model, "MLPRegressor")
    result["training"] = {
        "advanced_ai_type": "small_mlp",
        "advanced_model_type": "MLPRegressor",
        "architecture_summary": "sklearn MLPRegressor hidden_layer_sizes=(64, 32), relu, adam, early_stopping=True",
        "sequence_model_status": "blocked_missing_torch_tensorflow_keras",
        "random_seed": RANDOM_SEED,
        "hidden_layer_sizes": [64, 32],
        "max_iter": 70,
        "n_iter_observed": int(getattr(result["model"], "n_iter_", 0)),
        "epochs_or_iterations_completed": int(getattr(result["model"], "n_iter_", 0)),
        "loss_observed": float(getattr(result["model"], "loss_", 0.0)),
        "training_duration_seconds": round(time.monotonic() - started, 3),
        "early_stopping_reason": "stopped_by_sklearn_early_stopping_or_max_iter",
        "training_rows": sum(1 for row in rows if row["split"] == "train"),
        "validation_rows": sum(1 for row in rows if row["split"] == "validate"),
        "holdout_rows": sum(1 for row in rows if row["split"] == "holdout"),
        "warnings": [str(item.message) for item in caught],
    }
    return result


def fit_model(rows: list[dict[str, object]], features: list[str], model: object, model_class: str) -> dict[str, object]:
    train = [row for row in rows if row["split"] == "train"]
    validate = [row for row in rows if row["split"] == "validate"]
    holdout = [row for row in rows if row["split"] == "holdout"]
    x_train, encoder, names = build_feature_matrix(train, features)
    y_train = np.array([float(row[TARGET_FIELD]) for row in train], dtype=float)
    model.fit(x_train, y_train)  # type: ignore[attr-defined]
    predictions = {
        "validate": predict_rows(model, encoder, validate, features),
        "holdout": predict_rows(model, encoder, holdout, features),
    }
    metrics = {
        "model_class": model_class,
        "row_set": {
            "train": len(train),
            "validate": len(validate),
            "holdout": len(holdout),
            "features": len(names),
        },
        "validate": regression_metric_from_predictions(validate, predictions["validate"]),
        "holdout": regression_metric_from_predictions(holdout, predictions["holdout"]),
    }
    return {"model": model, "encoder": encoder, "metrics": metrics, "predictions": predictions, "features": names, "training": {}}


def predict_rows(model: object, encoder: Encoder, rows: list[dict[str, object]], features: list[str]) -> list[float]:
    if not rows:
        return []
    x, _, _ = build_feature_matrix(rows, features, encoder)
    return [float(value) for value in model.predict(x)]  # type: ignore[attr-defined]


def attach_model_predictions(
    rows: list[dict[str, object]],
    hgb_predictions: dict[str, list[float]],
    mlp_predictions: dict[str, list[float]],
) -> list[dict[str, object]]:
    by_split = {
        "validate": [row for row in rows if row["split"] == "validate"],
        "holdout": [row for row in rows if row["split"] == "holdout"],
    }
    for split, split_rows in by_split.items():
        for row, hgb_pred, mlp_pred in zip(split_rows, hgb_predictions.get(split, []), mlp_predictions.get(split, [])):
            row[HGB_PREDICTION_COLUMN] = hgb_pred
            row[MLP_PREDICTION_COLUMN] = mlp_pred
    return rows


def attach_path_predictions(
    rows: list[dict[str, object]],
    hgb_result: dict[str, object],
    mlp_result: dict[str, object],
    features: list[str],
) -> list[dict[str, object]]:
    hgb_pred = predict_rows(hgb_result["model"], hgb_result["encoder"], rows, features)  # type: ignore[arg-type]
    mlp_pred = predict_rows(mlp_result["model"], mlp_result["encoder"], rows, features)  # type: ignore[arg-type]
    for row, hgb_value, mlp_value in zip(rows, hgb_pred, mlp_pred):
        row[HGB_PREDICTION_COLUMN] = hgb_value
        row[MLP_PREDICTION_COLUMN] = mlp_value
    return rows


def build_feature_matrix(rows: list[dict[str, object]], features: list[str], encoder: Encoder | None = None) -> tuple[np.ndarray, Encoder, list[str]]:
    categorical = [feature for feature in ("special_day_type", "special_day_group") if feature in features]
    numeric = [feature for feature in features if feature not in categorical]
    if encoder is None:
        categories = {feature: sorted({str(row.get(feature, "")) for row in rows}) for feature in categorical}
        values_by_column = defaultdict(list)
        for row in rows:
            for feature in numeric:
                values_by_column[feature].append(safe_float(row.get(feature)))
        means = {feature: mean_float(values) for feature, values in values_by_column.items()}
        scales = {feature: std_float(values) or 1.0 for feature, values in values_by_column.items()}
        encoder = Encoder(categories=categories, means=means, scales=scales)
    names = numeric + [f"{feature}={category}" for feature in categorical for category in encoder.categories[feature]]
    matrix = []
    for row in rows:
        current = []
        for feature in numeric:
            current.append((safe_float(row.get(feature)) - encoder.means.get(feature, 0.0)) / encoder.scales.get(feature, 1.0))
        for feature in categorical:
            value = str(row.get(feature, ""))
            current.extend(1.0 if value == category else 0.0 for category in encoder.categories[feature])
        matrix.append(current)
    return np.asarray(matrix, dtype=float), encoder, names


def permutation_importance_light(model: object, encoder: Encoder, rows: list[dict[str, object]], features: list[str]) -> list[dict[str, object]]:
    sample = rows[: min(2500, len(rows))]
    if not sample:
        return []
    baseline_pred = predict_rows(model, encoder, sample, features)
    baseline_mae = mae([float(row[TARGET_FIELD]) for row in sample], baseline_pred)
    output = []
    numeric_features = [feature for feature in features if feature not in ("special_day_type", "special_day_group")]
    for feature in numeric_features[:40]:
        shuffled = [dict(row) for row in sample]
        values = [row.get(feature) for row in shuffled]
        rotated = values[1:] + values[:1]
        for row, value in zip(shuffled, rotated):
            row[feature] = value
        pred = predict_rows(model, encoder, shuffled, features)
        output.append({"feature": feature, "mae_increase": mae([float(row[TARGET_FIELD]) for row in shuffled], pred) - baseline_mae})
    return sorted(output, key=lambda item: abs(float(item["mae_increase"])), reverse=True)[:20]


def compare_hgb_vs_mlp(hgb_result: dict[str, object], mlp_result: dict[str, object]) -> dict[str, object]:
    hgb_metrics = hgb_result["metrics"]  # type: ignore[index]
    mlp_metrics = mlp_result["metrics"]  # type: ignore[index]
    out = {"identical_row_set": hgb_metrics["row_set"] == mlp_metrics["row_set"]}  # type: ignore[index]
    for split in ("validate", "holdout"):
        hgb_mae = float(hgb_metrics[split]["MAE"])  # type: ignore[index]
        mlp_mae = float(mlp_metrics[split]["MAE"])  # type: ignore[index]
        out[f"{split}_winner_by_MAE"] = "MLP" if mlp_mae < hgb_mae else "HGB"
        out[f"{split}_mlp_minus_hgb_MAE"] = mlp_mae - hgb_mae
        out[f"{split}_mlp_relative_MAE_change_percent"] = (mlp_mae - hgb_mae) / hgb_mae * 100 if hgb_mae else None
    return out


def strongest_baseline_by_holdout_mae(baseline_results: dict[str, object]) -> dict[str, object]:
    candidates = []
    for baseline, horizon_results in baseline_results.items():
        total_rows = 0
        weighted_mae = 0.0
        for result in horizon_results.values():  # type: ignore[union-attr]
            holdout = result["holdout"]  # type: ignore[index]
            rows = int(holdout["row_count"])
            mae_value = holdout["MAE"]
            if rows and mae_value is not None:
                total_rows += rows
                weighted_mae += float(mae_value) * rows
        if total_rows:
            candidates.append({"baseline": baseline, "weighted_holdout_MAE": weighted_mae / total_rows, "row_count": total_rows})
    if not candidates:
        return {"baseline": "", "weighted_holdout_MAE": None, "row_count": 0}
    return min(candidates, key=lambda item: float(item["weighted_holdout_MAE"]))


def assess_se3_pattern(comparison: dict[str, object], weekly_summary: dict[str, object]) -> dict[str, object]:
    holdout_change = float(comparison["holdout_mlp_relative_MAE_change_percent"])
    hgb_weekly = weekly_summary[HGB_PREDICTION_COLUMN]  # type: ignore[index]
    mlp_weekly = weekly_summary[MLP_PREDICTION_COLUMN]  # type: ignore[index]
    hgb_weekly_mae = float(hgb_weekly["MAE_full_168h"])  # type: ignore[index]
    mlp_weekly_mae = float(mlp_weekly["MAE_full_168h"])  # type: ignore[index]
    weekly_change = (mlp_weekly_mae - hgb_weekly_mae) / hgb_weekly_mae * 100 if hgb_weekly_mae else 0.0
    direct_confirms = holdout_change <= -2.0
    weekly_confirms = weekly_change <= -2.0
    return {
        "question": "Does SE4 confirm the SE3 pattern that MLP can beat HGB without price input?",
        "direct_holdout_mlp_relative_MAE_change_percent": holdout_change,
        "weekly_168h_mlp_relative_MAE_change_percent": weekly_change,
        "learning_threshold": "confirm if MLP improves holdout MAE or weekly MAE_full_168h by at least 2%",
        "direct_holdout_confirms_se3_pattern": direct_confirms,
        "weekly_168h_confirms_se3_pattern": weekly_confirms,
        "assessment": "confirms" if direct_confirms or weekly_confirms else "contradicts",
    }


def evaluate_direct_horizons(rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> dict[str, object]:
    output: dict[str, object] = {}
    for prediction_column in prediction_columns:
        output[prediction_column] = {
            str(horizon): metrics_by_split([row for row in rows if int(row["horizon_h"]) == horizon], prediction_column)
            for horizon in HORIZONS
        }
    return output


def select_weekly_holdout_origins(scored_rows: list[dict[str, object]]) -> dict[str, object]:
    complete = []
    skipped = []
    by_origin: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in scored_rows:
        if row.get("split") == "holdout" and p0052.parse_utc(str(row["forecast_origin_timestamp_utc"])) >= p0052.parse_utc(HOLDOUT_START):
            by_origin[str(row["forecast_origin_timestamp_utc"])].append(row)
    for origin, rows in sorted(by_origin.items()):
        horizons = {int(row["horizon_h"]) for row in rows if row.get(HGB_PREDICTION_COLUMN) is not None and row.get(MLP_PREDICTION_COLUMN) is not None}
        if all(horizon in horizons for horizon in PATH_HORIZONS):
            complete.append(origin)
        else:
            skipped.append({"forecast_origin_timestamp_utc": origin, "reason": "incomplete_168h_prediction_path", "available_horizons": len(horizons)})
    weekly = complete
    return {
        "complete_168h_path_count": len(complete),
        "weekly_origin_count": len(weekly),
        "weekly_origins": weekly,
        "first_weekly_origin": weekly[0] if weekly else "",
        "last_weekly_origin": weekly[-1] if weekly else "",
        "skipped_origins_with_reason": skipped,
    }


def evaluate_weekly_168h_paths(scored_rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> tuple[dict[str, object], list[dict[str, object]]]:
    selection = select_weekly_holdout_origins(scored_rows)
    weekly_set = set(selection["weekly_origins"])  # type: ignore[arg-type]
    rows = [
        row
        for row in scored_rows
        if str(row["forecast_origin_timestamp_utc"]) in weekly_set and 1 <= int(row["horizon_h"]) <= 168
    ]
    path_rows = []
    summary: dict[str, object] = dict(selection)
    for prediction_column in prediction_columns:
        summary[prediction_column] = weekly_path_metric_summary(rows, prediction_column)
    for origin in selection["weekly_origins"]:  # type: ignore[union-attr]
        origin_rows = [row for row in rows if row["forecast_origin_timestamp_utc"] == origin]
        out = {"forecast_origin_timestamp_utc": origin, "row_count": len(origin_rows)}
        for prediction_column in prediction_columns:
            out[f"{prediction_column}_MAE"] = regression_metric_from_predictions(
                [row for row in origin_rows if row.get(prediction_column) is not None],
                [float(row[prediction_column]) for row in origin_rows if row.get(prediction_column) is not None],
            )["MAE"]
        path_rows.append(out)
    return summary, path_rows


def weekly_path_metric_summary(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    available = [row for row in rows if row.get(prediction_column) is not None]
    buckets = {
        "MAE_0_24h": lambda row: 1 <= int(row["horizon_h"]) <= 24,
        "MAE_24_48h": lambda row: 25 <= int(row["horizon_h"]) <= 48,
        "MAE_48_72h": lambda row: 49 <= int(row["horizon_h"]) <= 72,
        "MAE_72_168h": lambda row: 73 <= int(row["horizon_h"]) <= 168,
    }
    out: dict[str, object] = {
        "MAE_full_168h": regression_metric_from_predictions(available, [float(row[prediction_column]) for row in available])["MAE"],
        "bias_full_168h": regression_metric_from_predictions(available, [float(row[prediction_column]) for row in available])["bias"],
        "p90_full_path_absolute_error": regression_metric_from_predictions(available, [float(row[prediction_column]) for row in available])["p90_absolute_error"],
        "p95_full_path_absolute_error": regression_metric_from_predictions(available, [float(row[prediction_column]) for row in available])["p95_absolute_error"],
    }
    for name, predicate in buckets.items():
        subset = [row for row in available if predicate(row)]
        out[name] = regression_metric_from_predictions(subset, [float(row[prediction_column]) for row in subset])["MAE"]
    out["daily_energy_error_proxy_mean_abs_mwh"] = daily_energy_error_proxy(available, prediction_column)
    out["peak_load_hour_error_mean_abs_hours"] = peak_load_hour_error(available, prediction_column)
    return out


def daily_energy_error_proxy(rows: list[dict[str, object]], prediction_column: str) -> float | None:
    if not rows:
        return None
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        day_index = (int(row["horizon_h"]) - 1) // 24
        grouped[(str(row["forecast_origin_timestamp_utc"]), day_index)].append(row)
    errors = []
    for group_rows in grouped.values():
        actual = sum(float(row[TARGET_FIELD]) for row in group_rows)
        predicted = sum(float(row[prediction_column]) for row in group_rows)
        errors.append(abs(predicted - actual))
    return mean_float(errors) if errors else None


def peak_load_hour_error(rows: list[dict[str, object]], prediction_column: str) -> float | None:
    if not rows:
        return None
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["forecast_origin_timestamp_utc"])].append(row)
    errors = []
    for group_rows in grouped.values():
        if not group_rows:
            continue
        actual_peak = max(group_rows, key=lambda row: float(row[TARGET_FIELD]))
        predicted_peak = max(group_rows, key=lambda row: float(row[prediction_column]))
        errors.append(abs(int(actual_peak["horizon_h"]) - int(predicted_peak["horizon_h"])))
    return mean_float([float(value) for value in errors]) if errors else None


def evaluate_conditional_regimes(rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> dict[str, object]:
    scored = [row for row in rows if row.get(HGB_PREDICTION_COLUMN) is not None and row.get(MLP_PREDICTION_COLUMN) is not None]
    temps = [safe_float(row.get("weather_proxy_temperature_2m_se4")) for row in scored if is_finite(row.get("weather_proxy_temperature_2m_se4"))]
    deltas = [safe_float(row.get("weather_proxy_temperature_delta_from_train_normal_se4")) for row in scored if is_finite(row.get("weather_proxy_temperature_delta_from_train_normal_se4"))]
    temp_p25 = percentile(temps, 0.25) if temps else 0.0
    temp_p10 = percentile(temps, 0.1) if temps else 0.0
    delta_p10 = percentile(deltas, 0.1) if deltas else 0.0
    regimes = {
        "cold_hours_temperature_p25_or_lower": lambda row: safe_float(row.get("weather_proxy_temperature_2m_se4")) <= temp_p25,
        "very_cold_hours_temperature_p10_or_lower": lambda row: safe_float(row.get("weather_proxy_temperature_2m_se4")) <= temp_p10,
        "rapid_temperature_drop_proxy_p10_or_lower": lambda row: safe_float(row.get("weather_proxy_temperature_delta_from_train_normal_se4")) <= delta_p10,
        "weekday": lambda row: int(row["is_weekend"]) == 0,
        "weekend": lambda row: int(row["is_weekend"]) == 1,
        "holiday": lambda row: int(row["is_holiday"]) == 1,
        "morning_ramp_06_09": lambda row: 6 <= int(row["target_model_cet_hour"]) <= 9,
        "evening_peak_16_20": lambda row: 16 <= int(row["target_model_cet_hour"]) <= 20,
        "summer_low_load_months": lambda row: int(row["target_month"]) in (6, 7, 8),
        "winter_high_load_months": lambda row: int(row["target_month"]) in (12, 1, 2),
    }
    output: dict[str, object] = {}
    for name, predicate in regimes.items():
        subset = [row for row in scored if predicate(row)]
        output[name] = {prediction_column: metrics_by_split(subset, prediction_column) for prediction_column in prediction_columns}
    return output


def validate_identical_row_sets(rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> dict[str, object]:
    row_sets = {}
    for prediction_column in prediction_columns:
        row_sets[prediction_column] = sorted(
            f"{row['forecast_origin_timestamp_utc']}|{row['target_timestamp_utc']}|{row['horizon_h']}"
            for row in rows
            if row.get(prediction_column) is not None
        )
    values = list(row_sets.values())
    return {
        "ok": bool(values) and all(value == values[0] for value in values),
        "row_counts": {name: len(ids) for name, ids in row_sets.items()},
        "weather_actual_proxy_labeled": all(row.get("weather_proxy_label") in (WEATHER_PROXY_LABEL, "weather_proxy_missing") for row in rows),
    }


def metrics_by_split(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    output = {}
    for split in ("train", "validate", "holdout"):
        subset = [row for row in rows if row["split"] == split and row.get(prediction_column) is not None]
        output[split] = regression_metric_from_predictions(subset, [float(row[prediction_column]) for row in subset])
    return output


def regression_metric_from_predictions(rows: list[dict[str, object]], pred: list[float]) -> dict[str, object]:
    actual = [float(row[TARGET_FIELD]) for row in rows]
    if not actual:
        return empty_metrics()
    abs_errors = [abs(a - p) for a, p in zip(actual, pred)]
    denom = [(abs(a) + abs(p)) / 2 for a, p in zip(actual, pred)]
    smape_values = [err / den for err, den in zip(abs_errors, denom) if den > 1e-9]
    mean_actual = sum(actual) / len(actual)
    median_actual = percentile(actual, 0.5)
    ss_tot = sum((a - mean_actual) ** 2 for a in actual)
    ss_res = sum((a - p) ** 2 for a, p in zip(actual, pred))
    mae_value = mae(actual, pred)
    return {
        "row_count": len(actual),
        "MAE": mae_value,
        "RMSE": rmse(actual, pred),
        "median_absolute_error": percentile(abs_errors, 0.5),
        "p90_absolute_error": percentile(abs_errors, 0.9),
        "p95_absolute_error": percentile(abs_errors, 0.95),
        "bias": sum(p - a for a, p in zip(actual, pred)) / len(actual),
        "sMAPE": sum(smape_values) / len(smape_values) if smape_values else None,
        "R2": 1 - ss_res / ss_tot if ss_tot > 0 else None,
        "mean_actual_mw": mean_actual,
        "median_actual_mw": median_actual,
        "p10_actual_mw": percentile(actual, 0.1),
        "p90_actual_mw": percentile(actual, 0.9),
        "MAE_percent_of_mean": mae_value / mean_actual * 100 if abs(mean_actual) > 1e-9 else None,
        "MAE_percent_of_median": mae_value / median_actual * 100 if abs(median_actual) > 1e-9 else None,
    }


def empty_metrics() -> dict[str, object]:
    return {
        "row_count": 0,
        "MAE": None,
        "RMSE": None,
        "median_absolute_error": None,
        "p90_absolute_error": None,
        "p95_absolute_error": None,
        "bias": None,
        "sMAPE": None,
        "R2": None,
        "mean_actual_mw": None,
        "median_actual_mw": None,
        "p10_actual_mw": None,
        "p90_actual_mw": None,
        "MAE_percent_of_mean": None,
        "MAE_percent_of_median": None,
    }


def write_p0054c_evidence(
    evidence_dir: Path,
    rows: list[dict[str, object]],
    path_candidate_rows: list[dict[str, object]],
    weekly_path_rows: list[dict[str, object]],
    summary: dict[str, object],
) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}
    files["summary_json"] = write_json(evidence_dir / "summary.json", summary)
    files["scored_rows_csv"] = write_csv(
        evidence_dir / "p0054c_scored_direct_rows_sample.csv",
        rows[:5000],
        direct_output_columns(),
    )
    files["weekly_path_csv"] = write_csv(evidence_dir / "weekly_168h_path_rows.csv", weekly_path_rows, list(weekly_path_rows[0].keys()) if weekly_path_rows else [])
    files["forecast_origin_log_csv"] = write_csv(
        evidence_dir / "forecast-origin-log.csv",
        forecast_origin_log_rows(path_candidate_rows),
        [
            "forecast_origin_timestamp_utc",
            "input_data_cutoff_utc",
            "target_timestamp_utc",
            "horizon_hours",
            "area_or_target",
            "predicted_price_or_index",
            "prediction_kind",
        ],
    )
    markdowns = evidence_markdowns(summary)
    for filename, content in markdowns.items():
        files[filename] = str(write(evidence_dir / filename, content))
    return files


def forecast_origin_log_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    for row in rows:
        if row.get(MLP_PREDICTION_COLUMN) is None:
            continue
        output.append(
            {
                "forecast_origin_timestamp_utc": row["forecast_origin_timestamp_utc"],
                "input_data_cutoff_utc": row["input_data_cutoff_utc"],
                "target_timestamp_utc": row["target_timestamp_utc"],
                "horizon_hours": row["horizon_h"],
                "area_or_target": "SE4_consumption",
                "predicted_price_or_index": row[MLP_PREDICTION_COLUMN],
                "prediction_kind": "LABB_consumption_mw_not_price_or_index_weather_proxy",
            }
        )
    return output


def evidence_markdowns(summary: dict[str, object]) -> dict[str, str]:
    hgb_holdout = summary["hgb_results"]["holdout"]  # type: ignore[index]
    mlp_holdout = summary["advanced_ai_results"]["holdout"]  # type: ignore[index]
    comparison = summary["hgb_vs_advanced_ai_comparison"]  # type: ignore[index]
    pattern = summary["se3_pattern_assessment"]  # type: ignore[index]
    strongest_baseline = summary["strongest_baseline"]  # type: ignore[index]
    common_header = f"# {PACKAGE_ID} {LABEL}\n\n"
    return {
        "CHANGELOG.md": common_header + "Built an offline SE4 consumption LABB experiment with HGB benchmark and small MLP advanced AI. No API, devices, runtime writes, price, production, flow, export/import or A61 inputs were used.\n",
        "labb-label.md": common_header + "This package is LABB only. It is not G2-KANDIDAT and produces no deployable model artifact.\n",
        "dataset-contract.md": common_header + json_block(summary["target_contract"]),
        "input-classification.md": common_header + json_block({
            "calendar": "forecast_safe",
            "historical_se4_load_lags_rollups": "forecast_safe",
            "weather": "proxy",
            "spot_price": "excluded_leakage",
            "production_flow_export_import_a61": "excluded_leakage",
        }),
        "weather-proxy-policy.md": common_header + json_block(summary["weather_contract"]),
        "feature-groups.md": common_header + json_block(summary["feature_contract"]),
        "baseline-results.md": common_header + "Strongest baseline by weighted holdout MAE:\n\n" + json_block(strongest_baseline) + "\nFull baseline results:\n\n" + json_block(summary["baseline_results"]),
        "hgb-results.md": common_header + json_block(summary["hgb_results"]),
        "advanced-ai-design.md": common_header + "Advanced AI is a deterministic sklearn MLPRegressor because sequence-aware neural runtimes are unavailable locally. It uses the same G4 feature set and row set as HGB.\n",
        "advanced-ai-training-evidence.md": common_header + json_block(summary["advanced_ai_training"]),
        "advanced-ai-results.md": common_header + json_block(summary["advanced_ai_results"]),
        "hgb-vs-advanced-ai-comparison.md": common_header + json_block(summary["hgb_vs_advanced_ai_comparison"]),
        "direct-horizon-results.md": common_header + json_block(summary["direct_horizon_results"]),
        "weekly-168h-path-results.md": common_header + json_block(summary["weekly_168h_path_results"]),
        "conditional-regime-results.md": common_header + json_block(summary["conditional_regime_results"]),
        "feature-importance-or-attribution.md": common_header + json_block(summary["feature_importance_or_attribution"]),
        "component-attribution-summary.md": common_header + "Component attribution is limited to feature groups, baselines and HGB light permutation importance. The LABB run isolates calendar, historical SE4 load state and weather proxy. Price and grid components are intentionally absent.\n",
        "interpretation.md": common_header
        + f"HGB holdout MAE: {hgb_holdout['MAE']:.3f} MW. MLP holdout MAE: {mlp_holdout['MAE']:.3f} MW. Holdout winner by MAE: {comparison['holdout_winner_by_MAE']}. SE4 {pattern['assessment']} the SE3 MLP-over-HGB pattern under the package threshold. Weather-assisted numbers are LABB proxy results because realized archive weather is not a separate forecast model.\n",
        "what-we-learned.md": common_header
        + "P0054C shows that SE4 does not automatically inherit the P0054B SE3 pattern. In this LABB setup, HGB is stronger on direct holdout while MLP is only competitive on some weekly path submetrics. Later spread/flaskhals-regime work should treat SE4 consumption residuals separately instead of assuming one advanced model family generalizes across bidding areas.\n\n"
        + json_block(pattern),
        "next-package-recommendation.md": common_header
        + "Recommended next package remains an advanced AI LABB for SE4-SE1 spread and bottleneck regimes, using P0054A LABB governance and keeping forecast_safe/proxy/oracle inputs separated.\n",
    }


def direct_output_columns() -> list[str]:
    return [
        "forecast_origin_timestamp_utc",
        "input_data_cutoff_utc",
        "target_timestamp_utc",
        "horizon_h",
        "split",
        TARGET_FIELD,
        "weather_proxy_label",
        *BASELINE_COLUMNS,
        HGB_PREDICTION_COLUMN,
        MLP_PREDICTION_COLUMN,
    ]


def write_json(path: Path, payload: object) -> str:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return str(path)


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> str:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column) for column in columns})
    return str(path)


def json_block(value: object) -> str:
    return "```json\n" + json.dumps(value, indent=2, sort_keys=True, default=str) + "\n```\n"


def grouped_mean(rows: list[dict[str, object]], keys: tuple[str, ...], field: str) -> dict[object, float]:
    grouped: dict[tuple[object, ...], list[float]] = defaultdict(list)
    values = []
    for row in rows:
        if row.get(field) is None or not is_finite(row.get(field)):
            continue
        value = float(row[field])
        grouped[tuple(row[key] for key in keys)].append(value)
        values.append(value)
    global_mean = mean_float(values)
    return {"global": global_mean, **{key: mean_float(vals) for key, vals in grouped.items()}}


def profile_predict(profile: object, row: dict[str, object], keys: tuple[str, ...]) -> float:
    profile_dict = profile if isinstance(profile, dict) else {"global": 0.0}
    key = tuple(row[key] for key in keys)
    return float(profile_dict.get(key, profile_dict.get("global", 0.0)))  # type: ignore[union-attr]


def safe_float(value: object) -> float:
    try:
        output = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0
    return output if math.isfinite(output) else 0.0


def is_finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False


def mean_float(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def std_float(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = mean_float(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table_name,)).fetchone()
    return row is not None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feature-db", type=Path, default=DEFAULT_FEATURE_DB)
    parser.add_argument("--weather-db", type=Path, default=DEFAULT_WEATHER_DB_PATH)
    parser.add_argument("--evidence-dir", type=Path, default=EVIDENCE_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_p0054c_analysis(feature_db=args.feature_db, weather_db=args.weather_db, evidence_dir=args.evidence_dir)
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
