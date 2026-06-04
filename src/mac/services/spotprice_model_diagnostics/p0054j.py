"""P0054J LABB SE1 consumption models with/without P0054H price forecasts."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import csv
import importlib
import importlib.metadata as importlib_metadata
import json
import math
import sqlite3
import time

import numpy as np

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_model_diagnostics import p0052
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH
from src.mac.services.swedish_calendar.core import classify_special_day


PACKAGE_ID = "P0054J"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054J")
SOURCE_TABLE = "physical_balance_se1_se4_hourly_v1"
TARGET_COLUMN = "consumption_se1"
TARGET_FIELD = "target_consumption_se1_mw"
PRICE_TABLE = "anchored_absolute_price_forecast_log_p0054h_se1_v1"
WEATHER_TABLE = "weather_area_hourly"
WEATHER_AREA_PROXY = "se1_core_weather"
WEATHER_PROXY_LABEL = "weather_actual_as_forecast_proxy"
DATASET_KIND = "offline_labb_experiment_not_deployable"
RANDOM_SEED = 54
TRAIN_FIT_START = "2022-06-01T00:00:00Z"
HOLDOUT_START = "2025-06-01T00:00:00Z"
HORIZONS = (1, 3, 6, 12, 24, 48, 72, 96, 120, 144, 168)
PATH_HORIZONS = tuple(range(1, 169))
LAGS = (1, 2, 3, 6, 12, 24, 48, 72, 168)
ROLL_WINDOWS = (6, 12, 24, 48, 168)
FORBIDDEN_NO_PRICE_TERMS = ("price", "spot", "production", "flow", "export", "import", "a61", "capacity", "utilization", "margin", "continental")
FORBIDDEN_WITH_PRICE_TERMS = ("production", "flow", "export", "import", "a61", "capacity", "utilization", "margin", "continental", "actual_price")
MODEL_FAMILIES = ("HGB", "ExtraTrees", "LightGBM", "XGBoost")


@dataclass(frozen=True)
class Encoder:
    categories: dict[str, list[str]]
    means: dict[str, float]
    scales: dict[str, float]


@dataclass(frozen=True)
class P0054JResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


@dataclass(frozen=True)
class ModelSpec:
    family: str
    model: object
    model_class: str
    package: str
    hyperparameters: dict[str, object]


def run_p0054j_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054JResult:
    started = time.monotonic()
    feature_db = Path(feature_db).expanduser()
    source_rows = load_se1_consumption_rows(feature_db)
    target_contract = validate_target_contract(source_rows)
    if not target_contract["ok"]:
        raise RuntimeError(f"P0054J target contract failed: {target_contract}")
    weather_rows, weather_contract = load_weather_proxy_rows(weather_db)
    price_rows, price_contract = load_price_forecast_rows(feature_db)
    if not price_contract["ok"]:
        raise RuntimeError(f"P0054J price contract failed: {price_contract}")

    direct_rows = build_modeling_rows(source_rows, weather_rows, price_rows, set(HORIZONS))
    path_rows = build_modeling_rows(source_rows, weather_rows, price_rows, set(PATH_HORIZONS), holdout_weekly_only=True)
    split_counts = assign_p0054i_splits(direct_rows)
    assign_p0054i_splits(path_rows)
    profiles = fit_train_profiles([row for row in direct_rows if row["split"] == "train_fit"])
    apply_profile_features(direct_rows, profiles)
    apply_profile_features(path_rows, profiles)
    feature_contract = feature_group_contract()
    feature_review = validate_feature_contract(feature_contract)
    if not feature_review["ok"]:
        raise RuntimeError(f"P0054J feature contract failed: {feature_review}")
    environment = capture_environment_status()
    specs = model_specs(environment["imports"])  # type: ignore[arg-type]
    if not all(family in {spec.family for spec in specs} for family in ("HGB", "ExtraTrees", "LightGBM", "XGBoost")):
        missing = sorted(set(MODEL_FAMILIES) - {spec.family for spec in specs})
        raise RuntimeError(f"P0054J required model imports missing: {missing}; {environment['imports']}")

    model_results: dict[str, dict[str, object]] = {}
    scored_rows = [dict(row) for row in direct_rows]
    scored_path_rows = [dict(row) for row in path_rows]
    for spec in specs:
        for variant in ("no_price", "with_p0054h_price_forecast"):
            result = fit_variant_model(scored_rows, feature_contract[variant]["features"], spec, variant)  # type: ignore[index,arg-type]
            model_key = f"{spec.family}_{variant}"
            model_results[model_key] = result
            attach_predictions(scored_rows, result, prediction_column(model_key), holdout_only=True)
            attach_path_predictions(scored_path_rows, result, feature_contract[variant]["features"], prediction_column(model_key))  # type: ignore[index,arg-type]

    prediction_columns = tuple(prediction_column(key) for key in model_results)
    fairness = validate_paired_row_sets(scored_rows, model_results)
    matrix_review = validate_matrix_safety(scored_rows, feature_contract)
    direct_results = evaluate_direct_horizons(scored_rows, prediction_columns)
    weekly_summary, weekly_path_rows = evaluate_weekly_paths(scored_path_rows, prediction_columns)
    conditional_results = evaluate_conditional_regimes(scored_path_rows, prediction_columns)
    ablation = compare_price_ablation(model_results, weekly_summary, conditional_results)
    comparison = model_comparison(model_results, weekly_summary)
    importance = feature_importance_or_attribution(model_results)
    status = "PASS" if fairness["ok"] and matrix_review["ok"] and ablation["required_model_pairs_complete"] else "WARN"
    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "dataset_kind": DATASET_KIND,
        "split_policy": split_policy(),
        "source_table": SOURCE_TABLE,
        "target_contract": target_contract,
        "weather_contract": weather_contract,
        "price_forecast_contract": price_contract,
        "environment": environment,
        "feature_contract": feature_contract,
        "input_classification": input_classification(),
        "feature_review": feature_review,
        "matrix_safety_review": matrix_review,
        "split_counts": split_counts,
        "row_counts": {
            "source_rows": len(source_rows),
            "price_forecast_rows": len(price_rows),
            "direct_rows": len(direct_rows),
            "weekly_path_rows": len(path_rows),
            "weekly_path_origins": len({row["forecast_origin_timestamp_utc"] for row in path_rows}),
        },
        "model_training": {key: result["training"] for key, result in model_results.items()},
        "model_results": {key: result["metrics"] for key, result in model_results.items()},
        "price_forecast_ablation": ablation,
        "model_comparison": comparison,
        "direct_horizon_results": direct_results,
        "weekly_168h_path_results": weekly_summary,
        "conditional_regime_results": conditional_results,
        "feature_importance_or_attribution": importance,
        "fairness": fairness,
        "mlp_status": {"ran": False, "reason": "skipped_by_design_runtime_scope; package requires HGB/ExtraTrees/LightGBM/XGBoost, MLP optional"},
        "runtime_seconds": round(time.monotonic() - started, 3),
    }
    evidence = write_p0054j_evidence(Path(evidence_dir), scored_rows, weekly_path_rows, summary)
    return P0054JResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def load_se1_consumption_rows(feature_db: Path) -> list[dict[str, object]]:
    with sqlite3.connect(feature_db) as conn:
        conn.row_factory = sqlite3.Row
        if not table_exists(conn, SOURCE_TABLE):
            raise RuntimeError(f"source table missing: {SOURCE_TABLE}")
        rows = [
            normalize_source_row(dict(row))
            for row in conn.execute(
                f"""
                SELECT timestamp_utc, model_cet_timestamp, model_cet_date, model_cet_hour, consumption_se1
                FROM {SOURCE_TABLE}
                ORDER BY timestamp_utc
                """
            )
        ]
    return rows


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
        "consumption_se1": float(row["consumption_se1"]),
    }


def validate_target_contract(rows: list[dict[str, object]]) -> dict[str, object]:
    timestamps = [str(row["timestamp_utc"]) for row in rows]
    values = [float(row["consumption_se1"]) for row in rows if is_finite(row.get("consumption_se1"))]
    train_fit = [row for row in rows if p0054i_split(str(row["timestamp_utc"])) == "train_fit"]
    holdout = [row for row in rows if p0054i_split(str(row["timestamp_utc"])) == "holdout"]
    return {
        "ok": bool(rows) and len(timestamps) == len(set(timestamps)) and len(values) == len(rows) and bool(train_fit) and bool(holdout),
        "source_table": SOURCE_TABLE,
        "target_column": TARGET_COLUMN,
        "target_field": TARGET_FIELD,
        "unit": "MW hourly mean",
        "rows": len(rows),
        "train_fit_source_rows": len(train_fit),
        "holdout_source_rows": len(holdout),
        "start": min(timestamps) if timestamps else "",
        "end": max(timestamps) if timestamps else "",
        "duplicates": len(timestamps) - len(set(timestamps)),
        "nonfinite_values": len(rows) - len(values),
        "mean_mw": mean_float(values),
        "median_mw": percentile(values, 0.5) if values else None,
    }


def load_weather_proxy_rows(weather_db: Path | str) -> tuple[dict[str, dict[str, object]], dict[str, object]]:
    path = Path(weather_db).expanduser()
    if not path.exists():
        return {}, {"available": False, "reason": "weather_db_missing", "input_classification": "excluded_unavailable"}
    rows = {}
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        if not table_exists(conn, WEATHER_TABLE):
            return {}, {"available": False, "reason": "weather_table_missing", "input_classification": "excluded_unavailable"}
        for row in conn.execute(
            f"""
            SELECT utc_hour_start, weighted_temperature_2m, weighted_apparent_temperature,
                   weighted_wind_speed_100m, weighted_cloud_cover, weighted_shortwave_radiation,
                   weighted_precipitation, weighted_snowfall, weighted_relative_humidity_2m,
                   heating_degree_hours, cooling_degree_hours
            FROM {WEATHER_TABLE}
            WHERE area_proxy=?
            ORDER BY utc_hour_start
            """,
            (WEATHER_AREA_PROXY,),
        ):
            ts = p0052.normalize_utc_text(row["utc_hour_start"])
            rows[ts] = {
                "weather_proxy_temperature_2m_se1": safe_float(row["weighted_temperature_2m"]),
                "weather_proxy_apparent_temperature_se1": safe_float(row["weighted_apparent_temperature"]),
                "weather_proxy_wind_100m_se1": safe_float(row["weighted_wind_speed_100m"]),
                "weather_proxy_cloud_cover_se1": safe_float(row["weighted_cloud_cover"]),
                "weather_proxy_shortwave_radiation_se1": safe_float(row["weighted_shortwave_radiation"]),
                "weather_proxy_precipitation_se1": safe_float(row["weighted_precipitation"]),
                "weather_proxy_snowfall_se1": safe_float(row["weighted_snowfall"]),
                "weather_proxy_humidity_se1": safe_float(row["weighted_relative_humidity_2m"]),
                "weather_proxy_heating_degree_hours_se1": safe_float(row["heating_degree_hours"]),
                "weather_proxy_cooling_degree_hours_se1": safe_float(row["cooling_degree_hours"]),
                "weather_proxy_label": WEATHER_PROXY_LABEL,
            }
    return {
        key: value for key, value in rows.items()
    }, {
        "available": bool(rows),
        "table": WEATHER_TABLE,
        "area_proxy": WEATHER_AREA_PROXY,
        "rows": len(rows),
        "start": min(rows) if rows else "",
        "end": max(rows) if rows else "",
        "input_classification": "proxy",
        "proxy_label": WEATHER_PROXY_LABEL,
    }


def load_price_forecast_rows(feature_db: Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    with sqlite3.connect(feature_db) as conn:
        conn.row_factory = sqlite3.Row
        if not table_exists(conn, PRICE_TABLE):
            return [], {"ok": False, "reason": "price_table_missing", "table": PRICE_TABLE}
        rows = [
            normalize_price_row(dict(row))
            for row in conn.execute(
                f"""
                SELECT *
                FROM {PRICE_TABLE}
                WHERE area='SE1'
                  AND prediction_kind='anchored_absolute_price'
                  AND quality_flag='forecast_safe_origin_local_baseline_not_m4'
                  AND training_protocol='origin_local_no_fit_pre_origin_history'
                ORDER BY forecast_origin_timestamp_utc, horizon_hours
                """
            )
        ]
    train_fit = [row for row in rows if p0054i_split(str(row["target_timestamp_utc"])) == "train_fit"]
    holdout = [row for row in rows if p0054i_split(str(row["target_timestamp_utc"])) == "holdout"]
    return rows, {
        "ok": bool(train_fit) and bool(holdout),
        "table": PRICE_TABLE,
        "rows": len(rows),
        "train_fit_rows": len(train_fit),
        "holdout_rows": len(holdout),
        "min_target_timestamp_utc": min((str(row["target_timestamp_utc"]) for row in rows), default=""),
        "max_target_timestamp_utc": max((str(row["target_timestamp_utc"]) for row in rows), default=""),
        "label": "not M4; forecast-safe origin-local historical spot price baseline",
        "required_filters": {
            "area": "SE1",
            "prediction_kind": "anchored_absolute_price",
            "quality_flag": "forecast_safe_origin_local_baseline_not_m4",
            "training_protocol": "origin_local_no_fit_pre_origin_history",
        },
    }


def normalize_price_row(row: dict[str, object]) -> dict[str, object]:
    return {
        "forecast_origin_timestamp_utc": p0052.normalize_utc_text(row["forecast_origin_timestamp_utc"]),
        "input_data_cutoff_utc": p0052.normalize_utc_text(row["input_data_cutoff_utc"]),
        "target_timestamp_utc": p0052.normalize_utc_text(row["target_timestamp_utc"]),
        "horizon_h": int(row["horizon_hours"]) + 1,
        "predicted_price": float(row["predicted_price"]),
        "prediction_rule": str(row["prediction_rule"]),
    }


def build_modeling_rows(
    source_rows: list[dict[str, object]],
    weather_rows: dict[str, dict[str, object]],
    price_rows: list[dict[str, object]],
    horizons: set[int],
    *,
    holdout_weekly_only: bool = False,
) -> list[dict[str, object]]:
    source_by_ts = {str(row["timestamp_utc"]): row for row in source_rows}
    source_index = {str(row["timestamp_utc"]): index for index, row in enumerate(source_rows)}
    values = [float(row["consumption_se1"]) for row in source_rows]
    price_by_origin = group_by(price_rows, "forecast_origin_timestamp_utc")
    path_features = {origin: price_path_features(rows) for origin, rows in price_by_origin.items()}
    rows = []
    for price in price_rows:
        horizon = int(price["horizon_h"])
        if horizon not in horizons:
            continue
        origin_ts = str(price["forecast_origin_timestamp_utc"])
        target_ts = str(price["target_timestamp_utc"])
        if holdout_weekly_only:
            origin_dt = p0052.parse_utc(origin_ts)
            if origin_dt < p0052.parse_utc(HOLDOUT_START) or (origin_dt - p0052.parse_utc(HOLDOUT_START)).total_seconds() % (168 * 3600) != 23 * 3600:
                continue
        origin_index = source_index.get(origin_ts)
        target = source_by_ts.get(target_ts)
        if origin_index is None or target is None or origin_index < max(max(LAGS), max(ROLL_WINDOWS)):
            continue
        row = {
            "forecast_origin_timestamp_utc": origin_ts,
            "input_data_cutoff_utc": p0052.format_utc(p0052.parse_utc(origin_ts) - timedelta(hours=1)),
            "target_timestamp_utc": target_ts,
            "horizon_h": horizon,
            TARGET_FIELD: float(target["consumption_se1"]),
            "area_or_target": "SE1_consumption",
            "prediction_kind": "consumption_mw",
            "dataset_kind": DATASET_KIND,
            "weather_proxy_label": WEATHER_PROXY_LABEL if target_ts in weather_rows else "weather_proxy_missing",
            "price_forecast_source": "P0054H_origin_local_history_baseline_not_m4",
            "forecast_se1_price_target_hour": float(price["predicted_price"]),
        }
        attach_calendar_features(row, p0052.parse_utc(target_ts) + timedelta(hours=1))
        row.update(lag_features_at_origin(values, origin_index))
        row.update(rolling_features_at_origin(values, origin_index))
        row.update(weather_rows.get(target_ts, {}))
        row.update(path_features[origin_ts].get(horizon, {}))
        rows.append(row)
    return rows


def price_path_features(origin_rows: list[dict[str, object]]) -> dict[int, dict[str, object]]:
    ordered = sorted(origin_rows, key=lambda row: int(row["horizon_h"]))
    prices = [float(row["predicted_price"]) for row in ordered]
    ranks = rank_map(prices, high_rank=True)
    p90 = percentile(prices, 0.9) if prices else 0.0
    out = {}
    for index, row in enumerate(ordered):
        horizon = int(row["horizon_h"])
        price = float(row["predicted_price"])
        prev = prices[index - 1] if index > 0 else price
        out[horizon] = {
            "price_forecast_horizon_value": price,
            "price_forecast_0_24h_mean": mean_float(prices[:24]),
            "price_forecast_24_48h_mean": mean_float(prices[24:48]),
            "price_forecast_0_168h_mean": mean_float(prices[:168]),
            "price_forecast_rank_within_path": ranks[index],
            "price_forecast_spike_flag_within_path": 1 if price >= p90 else 0,
            "price_forecast_ramp_from_previous_horizon": price - prev,
            "price_forecast_peak_offpeak_indicator": 1 if price >= mean_float(prices[:168]) else 0,
        }
    return out


def attach_calendar_features(row: dict[str, object], target_model_dt: datetime) -> None:
    day = target_model_dt.date()
    special = classify_special_day(day)
    hour = target_model_dt.hour
    weekday = day.weekday()
    doy = target_model_dt.timetuple().tm_yday
    row.update(
        {
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
            "holiday_strength": float(special["holiday_strength"]),
            "special_day_type": str(special["special_day_type"]),
            "special_day_group": str(special["special_day_group"]),
        }
    )


def lag_features_at_origin(values: list[float], origin_index: int) -> dict[str, float]:
    return {f"consumption_se1_lag_{lag}h": values[origin_index - lag] for lag in LAGS}


def rolling_features_at_origin(values: list[float], origin_index: int) -> dict[str, float]:
    out = {}
    for window in ROLL_WINDOWS:
        subset = values[origin_index - window : origin_index]
        out[f"consumption_se1_roll_mean_{window}h"] = mean_float(subset)
    subset24 = values[origin_index - 24 : origin_index]
    mean24 = mean_float(subset24)
    out["consumption_se1_roll_min_24h"] = min(subset24)
    out["consumption_se1_roll_max_24h"] = max(subset24)
    out["consumption_se1_roll_std_24h"] = math.sqrt(sum((value - mean24) ** 2 for value in subset24) / len(subset24))
    out["consumption_se1_ramp_1h"] = values[origin_index - 1] - values[origin_index - 2]
    out["consumption_se1_ramp_24h"] = values[origin_index - 1] - values[origin_index - 24]
    out["consumption_se1_same_hour_24h_vs_168h"] = values[origin_index - 24] - values[origin_index - 168]
    return out


def assign_p0054i_splits(rows: list[dict[str, object]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        split = p0054i_split(str(row["target_timestamp_utc"]))
        row["split"] = split
        counts[split] += 1
    return dict(counts)


def p0054i_split(timestamp: str) -> str:
    dt = p0052.parse_utc(p0052.normalize_utc_text(timestamp))
    if dt < p0052.parse_utc(TRAIN_FIT_START):
        return "outside"
    if dt < p0052.parse_utc(HOLDOUT_START):
        return "train_fit"
    return "holdout"


def fit_train_profiles(train_rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "temperature_normals": grouped_mean(
            [row for row in train_rows if is_finite(row.get("weather_proxy_temperature_2m_se1"))],
            ("target_month", "target_model_cet_hour"),
            "weather_proxy_temperature_2m_se1",
        )
    }


def apply_profile_features(rows: list[dict[str, object]], profiles: dict[str, object]) -> None:
    for row in rows:
        row["weather_proxy_train_normal_temperature_2m_se1"] = profile_predict(profiles["temperature_normals"], row, ("target_month", "target_model_cet_hour"))
        row["weather_proxy_temperature_delta_from_train_normal_se1"] = safe_float(row.get("weather_proxy_temperature_2m_se1")) - safe_float(row.get("weather_proxy_train_normal_temperature_2m_se1"))
        row["weather_proxy_cold_spell_flag_se1"] = 1 if safe_float(row.get("weather_proxy_heating_degree_hours_se1")) >= 12 else 0


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
        "holiday_strength",
        "special_day_type",
        "special_day_group",
    ]
    lags = [f"consumption_se1_lag_{lag}h" for lag in LAGS]
    rollups = [f"consumption_se1_roll_mean_{window}h" for window in ROLL_WINDOWS] + [
        "consumption_se1_roll_min_24h",
        "consumption_se1_roll_max_24h",
        "consumption_se1_roll_std_24h",
        "consumption_se1_ramp_1h",
        "consumption_se1_ramp_24h",
        "consumption_se1_same_hour_24h_vs_168h",
    ]
    weather = [
        "weather_proxy_temperature_2m_se1",
        "weather_proxy_apparent_temperature_se1",
        "weather_proxy_wind_100m_se1",
        "weather_proxy_cloud_cover_se1",
        "weather_proxy_shortwave_radiation_se1",
        "weather_proxy_precipitation_se1",
        "weather_proxy_snowfall_se1",
        "weather_proxy_humidity_se1",
        "weather_proxy_heating_degree_hours_se1",
        "weather_proxy_cooling_degree_hours_se1",
        "weather_proxy_train_normal_temperature_2m_se1",
        "weather_proxy_temperature_delta_from_train_normal_se1",
        "weather_proxy_cold_spell_flag_se1",
    ]
    price = [
        "price_forecast_horizon_value",
        "price_forecast_0_24h_mean",
        "price_forecast_24_48h_mean",
        "price_forecast_0_168h_mean",
        "price_forecast_rank_within_path",
        "price_forecast_spike_flag_within_path",
        "price_forecast_ramp_from_previous_horizon",
        "price_forecast_peak_offpeak_indicator",
    ]
    base = calendar + lags + rollups + weather
    return {
        "no_price": {"input_classification": "mixed_forecast_safe_and_weather_proxy", "features": base},
        "with_p0054h_price_forecast": {"input_classification": "mixed_forecast_safe_price_and_weather_proxy", "features": base + price},
    }


def validate_feature_contract(contract: dict[str, dict[str, object]]) -> dict[str, object]:
    violations = []
    for group, meta in contract.items():
        forbidden = FORBIDDEN_NO_PRICE_TERMS if group == "no_price" else FORBIDDEN_WITH_PRICE_TERMS
        for feature in meta["features"]:  # type: ignore[index]
            lowered = str(feature).lower()
            for term in forbidden:
                if term in lowered:
                    violations.append({"group": group, "feature": feature, "term": term})
    return {"ok": not violations, "violations": violations}


def capture_environment_status() -> dict[str, object]:
    return {
        "packages": {name: package_version(name) for name in ("numpy", "scikit-learn", "lightgbm", "xgboost")},
        "imports": {name: import_status(name) for name in ("lightgbm", "xgboost")},
    }


def model_specs(imports: dict[str, dict[str, object]]) -> list[ModelSpec]:
    from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor

    specs = [
        ModelSpec(
            family="HGB",
            model_class="HistGradientBoostingRegressor",
            package="scikit-learn",
            model=HistGradientBoostingRegressor(max_iter=120, learning_rate=0.055, max_leaf_nodes=31, min_samples_leaf=80, random_state=RANDOM_SEED),
            hyperparameters={"max_iter": 120, "learning_rate": 0.055, "max_leaf_nodes": 31, "min_samples_leaf": 80, "random_state": RANDOM_SEED},
        ),
        ModelSpec(
            family="ExtraTrees",
            model_class="ExtraTreesRegressor",
            package="scikit-learn",
            model=ExtraTreesRegressor(n_estimators=180, max_features=0.75, min_samples_leaf=4, max_samples=0.80, bootstrap=True, n_jobs=-1, random_state=RANDOM_SEED),
            hyperparameters={"n_estimators": 180, "max_features": 0.75, "min_samples_leaf": 4, "max_samples": 0.80, "bootstrap": True, "n_jobs": -1, "random_state": RANDOM_SEED},
        ),
    ]
    if imports.get("lightgbm", {}).get("ok"):
        from lightgbm import LGBMRegressor

        specs.append(
            ModelSpec(
                family="LightGBM",
                model_class="LGBMRegressor",
                package="lightgbm",
                model=LGBMRegressor(objective="regression_l1", metric="mae", n_estimators=450, learning_rate=0.05, num_leaves=63, min_child_samples=80, subsample=0.85, subsample_freq=1, colsample_bytree=0.85, reg_lambda=0.2, random_state=RANDOM_SEED, n_jobs=-1, verbose=-1),
                hyperparameters={"objective": "regression_l1", "metric": "mae", "n_estimators": 450, "learning_rate": 0.05, "num_leaves": 63, "min_child_samples": 80, "subsample": 0.85, "colsample_bytree": 0.85, "reg_lambda": 0.2, "random_state": RANDOM_SEED, "n_jobs": -1},
            )
        )
    if imports.get("xgboost", {}).get("ok"):
        from xgboost import XGBRegressor

        specs.append(
            ModelSpec(
                family="XGBoost",
                model_class="XGBRegressor",
                package="xgboost",
                model=XGBRegressor(objective="reg:squarederror", eval_metric="mae", n_estimators=450, learning_rate=0.05, max_depth=7, min_child_weight=8, subsample=0.85, colsample_bytree=0.85, reg_lambda=1.0, random_state=RANDOM_SEED, n_jobs=-1, tree_method="hist"),
                hyperparameters={"objective": "reg:squarederror", "eval_metric": "mae", "n_estimators": 450, "learning_rate": 0.05, "max_depth": 7, "min_child_weight": 8, "subsample": 0.85, "colsample_bytree": 0.85, "reg_lambda": 1.0, "random_state": RANDOM_SEED, "n_jobs": -1, "tree_method": "hist"},
            )
        )
    return specs


def fit_variant_model(rows: list[dict[str, object]], features: list[str], spec: ModelSpec, variant: str) -> dict[str, object]:
    started = time.monotonic()
    train = [row for row in rows if row["split"] == "train_fit"]
    holdout = [row for row in rows if row["split"] == "holdout"]
    x_train, encoder, names = build_feature_matrix(train, features)
    y_train = np.array([float(row[TARGET_FIELD]) for row in train], dtype=float)
    model = clone_model(spec.model)
    model.fit(x_train, y_train)  # type: ignore[attr-defined]
    holdout_pred = predict_rows(model, encoder, holdout, features)
    return {
        "model": model,
        "encoder": encoder,
        "features": names,
        "predictions": {"holdout": holdout_pred},
        "metrics": {
            "model_family": spec.family,
            "variant": variant,
            "row_set": {"train_fit": len(train), "holdout": len(holdout), "features": len(names)},
            "holdout": regression_metric_from_predictions(holdout, holdout_pred),
        },
        "training": {
            "model_family": spec.family,
            "variant": variant,
            "model_class": spec.model_class,
            "package": spec.package,
            "hyperparameters": spec.hyperparameters,
            "training_rows": len(train),
            "holdout_rows": len(holdout),
            "feature_count": len(names),
            "training_duration_seconds": round(time.monotonic() - started, 3),
            "model_artifact_persisted": False,
        },
    }


def clone_model(model: object) -> object:
    from sklearn.base import clone

    return clone(model)


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


def predict_rows(model: object, encoder: Encoder, rows: list[dict[str, object]], features: list[str]) -> list[float]:
    if not rows:
        return []
    x, _, _ = build_feature_matrix(rows, features, encoder)
    return [float(value) for value in model.predict(x)]  # type: ignore[attr-defined]


def attach_predictions(rows: list[dict[str, object]], result: dict[str, object], column: str, *, holdout_only: bool) -> None:
    target_rows = [row for row in rows if row["split"] == "holdout"] if holdout_only else rows
    for row, pred in zip(target_rows, result["predictions"]["holdout"]):  # type: ignore[index]
        row[column] = float(pred)


def attach_path_predictions(path_rows: list[dict[str, object]], result: dict[str, object], features: list[str], column: str) -> None:
    predictions = predict_rows(result["model"], result["encoder"], path_rows, features)  # type: ignore[arg-type]
    for row, pred in zip(path_rows, predictions):
        row[column] = float(pred)


def prediction_column(model_key: str) -> str:
    return f"pred_{model_key}"


def evaluate_direct_horizons(rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> dict[str, object]:
    return {
        column: {str(horizon): metrics_by_split([row for row in rows if int(row["horizon_h"]) == horizon], column) for horizon in HORIZONS}
        for column in prediction_columns
    }


def evaluate_weekly_paths(rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> tuple[dict[str, object], list[dict[str, object]]]:
    by_origin = group_by(rows, "forecast_origin_timestamp_utc")
    complete_origins = [origin for origin, origin_rows in sorted(by_origin.items()) if len({int(row["horizon_h"]) for row in origin_rows}) == 168]
    selected_rows = [row for origin in complete_origins for row in by_origin[origin]]
    summary: dict[str, object] = {
        "weekly_origin_count": len(complete_origins),
        "first_weekly_origin": complete_origins[0] if complete_origins else "",
        "last_weekly_origin": complete_origins[-1] if complete_origins else "",
    }
    path_rows = []
    for column in prediction_columns:
        summary[column] = weekly_path_metric_summary(selected_rows, column)
    for origin in complete_origins:
        origin_rows = by_origin[origin]
        out = {"forecast_origin_timestamp_utc": origin, "row_count": len(origin_rows)}
        for column in prediction_columns:
            available = [row for row in origin_rows if row.get(column) is not None]
            out[f"{column}_MAE"] = regression_metric_from_predictions(available, [float(row[column]) for row in available])["MAE"]
        path_rows.append(out)
    return summary, path_rows


def weekly_path_metric_summary(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    available = [row for row in rows if row.get(prediction_column) is not None]
    metric = regression_metric_from_predictions(available, [float(row[prediction_column]) for row in available])
    buckets = {
        "MAE_0_24h": lambda row: 1 <= int(row["horizon_h"]) <= 24,
        "MAE_24_48h": lambda row: 25 <= int(row["horizon_h"]) <= 48,
        "MAE_48_72h": lambda row: 49 <= int(row["horizon_h"]) <= 72,
        "MAE_72_168h": lambda row: 73 <= int(row["horizon_h"]) <= 168,
    }
    out = {
        "MAE_full_168h": metric["MAE"],
        "bias_full_168h": metric["bias"],
        "p90_full_path_absolute_error": metric["p90_absolute_error"],
        "p95_full_path_absolute_error": metric["p95_absolute_error"],
        "daily_energy_error_proxy": daily_energy_error_proxy(available, prediction_column),
        "peak_load_hour_error": peak_load_hour_error(available, prediction_column),
    }
    for name, predicate in buckets.items():
        subset = [row for row in available if predicate(row)]
        out[name] = regression_metric_from_predictions(subset, [float(row[prediction_column]) for row in subset])["MAE"]
    return out


def evaluate_conditional_regimes(rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> dict[str, object]:
    scored = [row for row in rows if row["split"] == "holdout" and all(row.get(column) is not None for column in prediction_columns)]
    temps = [safe_float(row.get("weather_proxy_temperature_2m_se1")) for row in scored if is_finite(row.get("weather_proxy_temperature_2m_se1"))]
    price_values = [safe_float(row.get("price_forecast_horizon_value")) for row in scored if is_finite(row.get("price_forecast_horizon_value"))]
    ramps = [safe_float(row.get("price_forecast_ramp_from_previous_horizon")) for row in scored if is_finite(row.get("price_forecast_ramp_from_previous_horizon"))]
    temp_p25 = percentile(temps, 0.25) if temps else 0.0
    temp_p10 = percentile(temps, 0.1) if temps else 0.0
    price_p25 = percentile(price_values, 0.25) if price_values else 0.0
    price_p75 = percentile(price_values, 0.75) if price_values else 0.0
    ramp_p90 = percentile([abs(value) for value in ramps], 0.9) if ramps else 0.0
    regimes = {
        "cold_hours": lambda row: safe_float(row.get("weather_proxy_temperature_2m_se1")) <= temp_p25,
        "very_cold_hours": lambda row: safe_float(row.get("weather_proxy_temperature_2m_se1")) <= temp_p10,
        "weekday": lambda row: int(row["is_weekend"]) == 0,
        "weekend": lambda row: int(row["is_weekend"]) == 1,
        "holiday": lambda row: int(row["is_holiday"]) == 1,
        "morning_ramp": lambda row: 6 <= int(row["target_model_cet_hour"]) <= 9,
        "evening_peak": lambda row: 16 <= int(row["target_model_cet_hour"]) <= 20,
        "summer_low_load": lambda row: int(row["target_month"]) in (6, 7, 8),
        "winter_high_load": lambda row: int(row["target_month"]) in (12, 1, 2),
        "high_forecast_price": lambda row: safe_float(row.get("price_forecast_horizon_value")) >= price_p75,
        "low_forecast_price": lambda row: safe_float(row.get("price_forecast_horizon_value")) <= price_p25,
        "large_forecast_price_ramp": lambda row: abs(safe_float(row.get("price_forecast_ramp_from_previous_horizon"))) >= ramp_p90,
        "forecast_price_spike": lambda row: int(row.get("price_forecast_spike_flag_within_path") or 0) == 1,
    }
    return {
        name: {column: regression_metric_from_predictions(subset := [row for row in scored if predicate(row)], [float(row[column]) for row in subset]) for column in prediction_columns}
        for name, predicate in regimes.items()
    }


def compare_price_ablation(model_results: dict[str, dict[str, object]], weekly_summary: dict[str, object], conditional_results: dict[str, object]) -> dict[str, object]:
    rows = []
    for family in MODEL_FAMILIES:
        no_key = f"{family}_no_price"
        price_key = f"{family}_with_p0054h_price_forecast"
        if no_key not in model_results or price_key not in model_results:
            continue
        no_mae = float(model_results[no_key]["metrics"]["holdout"]["MAE"])  # type: ignore[index]
        price_mae = float(model_results[price_key]["metrics"]["holdout"]["MAE"])  # type: ignore[index]
        no_weekly = weekly_summary[prediction_column(no_key)]["MAE_full_168h"]  # type: ignore[index]
        price_weekly = weekly_summary[prediction_column(price_key)]["MAE_full_168h"]  # type: ignore[index]
        rows.append(
            {
                "family": family,
                "holdout_no_price_MAE": no_mae,
                "holdout_with_price_MAE": price_mae,
                "holdout_with_minus_no_MAE": price_mae - no_mae,
                "holdout_relative_change_percent": relative_change(price_mae, no_mae),
                "weekly_no_price_MAE_full_168h": no_weekly,
                "weekly_with_price_MAE_full_168h": price_weekly,
                "weekly_with_minus_no_MAE_full_168h": float(price_weekly) - float(no_weekly),
                "weekly_relative_change_percent": relative_change(float(price_weekly), float(no_weekly)),
                "price_helped_holdout": price_mae < no_mae,
                "price_helped_weekly": float(price_weekly) < float(no_weekly),
            }
        )
    conditional = conditional_price_help_summary(conditional_results)
    keep = should_keep_price_features(rows, conditional)
    return {
        "required_model_pairs_complete": len(rows) == len(MODEL_FAMILIES),
        "per_model_family": rows,
        "conditional_price_help_summary": conditional,
        "learning_threshold": "keep if holdout or weekly improves by >=2%, or >=3% in at least two important regimes without broad worsening",
        "price_forecast_should_be_kept_for_future_se1_experiments": keep,
        "interpretation_category": "supports_hypothesis" if keep else "no_effect_detected",
    }


def conditional_price_help_summary(conditional_results: dict[str, object]) -> dict[str, object]:
    out = {}
    interesting = []
    for regime, values in conditional_results.items():
        regime_out = {}
        for family in MODEL_FAMILIES:
            no_col = prediction_column(f"{family}_no_price")
            price_col = prediction_column(f"{family}_with_p0054h_price_forecast")
            if no_col not in values or price_col not in values:  # type: ignore[operator]
                continue
            no_mae = values[no_col]["MAE"]  # type: ignore[index]
            price_mae = values[price_col]["MAE"]  # type: ignore[index]
            change = relative_change(float(price_mae), float(no_mae)) if no_mae else None
            regime_out[family] = {"no_price_MAE": no_mae, "with_price_MAE": price_mae, "relative_change_percent": change}
            if change is not None and change <= -3.0:
                interesting.append({"regime": regime, "family": family, "relative_change_percent": change})
        out[regime] = regime_out
    return {"by_regime": out, "improvements_at_least_3_percent": interesting, "count": len(interesting)}


def should_keep_price_features(rows: list[dict[str, object]], conditional: dict[str, object]) -> bool:
    broad = any((row["holdout_relative_change_percent"] is not None and row["holdout_relative_change_percent"] <= -2.0) or (row["weekly_relative_change_percent"] is not None and row["weekly_relative_change_percent"] <= -2.0) for row in rows)
    conditional_count = int(conditional.get("count", 0))
    material_worsening = any(row["holdout_relative_change_percent"] is not None and row["holdout_relative_change_percent"] > 2.0 for row in rows)
    return broad or (conditional_count >= 2 and not material_worsening)


def model_comparison(model_results: dict[str, dict[str, object]], weekly_summary: dict[str, object]) -> dict[str, object]:
    direct = [{"model": key, "holdout_MAE": result["metrics"]["holdout"]["MAE"]} for key, result in model_results.items()]  # type: ignore[index]
    weekly = [{"model": key, "weekly_MAE_full_168h": weekly_summary[prediction_column(key)]["MAE_full_168h"]} for key in model_results]  # type: ignore[index]
    return {
        "best_no_price_by_holdout_MAE": min([row for row in direct if row["model"].endswith("_no_price")], key=lambda row: float(row["holdout_MAE"])),
        "best_with_price_by_holdout_MAE": min([row for row in direct if row["model"].endswith("_with_p0054h_price_forecast")], key=lambda row: float(row["holdout_MAE"])),
        "best_no_price_by_weekly_MAE_full_168h": min([row for row in weekly if row["model"].endswith("_no_price")], key=lambda row: float(row["weekly_MAE_full_168h"])),
        "best_with_price_by_weekly_MAE_full_168h": min([row for row in weekly if row["model"].endswith("_with_p0054h_price_forecast")], key=lambda row: float(row["weekly_MAE_full_168h"])),
        "direct_holdout": direct,
        "weekly_168h": weekly,
    }


def validate_paired_row_sets(rows: list[dict[str, object]], model_results: dict[str, dict[str, object]]) -> dict[str, object]:
    pair_results = {}
    ok = True
    for family in MODEL_FAMILIES:
        no_col = prediction_column(f"{family}_no_price")
        price_col = prediction_column(f"{family}_with_p0054h_price_forecast")
        no_ids = sorted(row_id(row) for row in rows if row.get(no_col) is not None)
        price_ids = sorted(row_id(row) for row in rows if row.get(price_col) is not None)
        pair_ok = bool(no_ids) and no_ids == price_ids
        pair_results[family] = {"ok": pair_ok, "no_price_rows": len(no_ids), "with_price_rows": len(price_ids)}
        ok = ok and pair_ok
    return {"ok": ok, "pairs": pair_results}


def validate_matrix_safety(rows: list[dict[str, object]], feature_contract: dict[str, dict[str, object]]) -> dict[str, object]:
    forbidden_columns = [column for row in rows[:1] for column in row if any(term in column.lower() for term in ("actual_price", "production", "flow", "export", "import", "a61", "capacity", "utilization", "continental"))]
    price_source_ok = all(row.get("price_forecast_source") == "P0054H_origin_local_history_baseline_not_m4" for row in rows)
    cutoff_ok = all(p0052.parse_utc(str(row["input_data_cutoff_utc"])) <= p0052.parse_utc(str(row["forecast_origin_timestamp_utc"])) <= p0052.parse_utc(str(row["target_timestamp_utc"])) for row in rows)
    return {"ok": not forbidden_columns and price_source_ok and cutoff_ok, "forbidden_columns": sorted(set(forbidden_columns)), "price_source_ok": price_source_ok, "cutoff_order_ok": cutoff_ok}


def feature_importance_or_attribution(model_results: dict[str, dict[str, object]]) -> dict[str, object]:
    output = {}
    for key, result in model_results.items():
        model = result["model"]
        names = result["features"]
        importances = getattr(model, "feature_importances_", None)
        if importances is None:
            output[key] = {"available": False, "reason": "model_has_no_feature_importances_attribute"}
            continue
        ranked = sorted([{"feature": name, "importance": float(value)} for name, value in zip(names, importances)], key=lambda row: abs(row["importance"]), reverse=True)
        output[key] = {"available": True, "top": ranked[:25]}
    return output


def metrics_by_split(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    return {
        split: regression_metric_from_predictions(subset := [row for row in rows if row["split"] == split and row.get(prediction_column) is not None], [float(row[prediction_column]) for row in subset])
        for split in ("train_fit", "holdout")
    }


def regression_metric_from_predictions(rows: list[dict[str, object]], pred: list[float]) -> dict[str, object]:
    actual = [float(row[TARGET_FIELD]) for row in rows]
    if not actual:
        return empty_metrics()
    abs_errors = [abs(a - p) for a, p in zip(actual, pred)]
    denom = [(abs(a) + abs(p)) / 2 for a, p in zip(actual, pred)]
    smape_values = [err / den for err, den in zip(abs_errors, denom) if den > 1e-9]
    mean_actual = mean_float(actual)
    median_actual = percentile(actual, 0.5)
    ss_tot = sum((a - mean_actual) ** 2 for a in actual)
    ss_res = sum((a - p) ** 2 for a, p in zip(actual, pred))
    mae_value = mae(actual, pred)
    return {
        "row_count": len(actual),
        "MAE": mae_value,
        "RMSE": rmse(actual, pred),
        "bias": mean_float([p - a for a, p in zip(actual, pred)]),
        "median_absolute_error": percentile(abs_errors, 0.5),
        "p90_absolute_error": percentile(abs_errors, 0.9),
        "p95_absolute_error": percentile(abs_errors, 0.95),
        "sMAPE": mean_float(smape_values) if smape_values else None,
        "R2": 1 - ss_res / ss_tot if ss_tot > 0 else None,
        "mean_actual_mw": mean_actual,
        "median_actual_mw": median_actual,
        "MAE_percent_of_mean_actual": mae_value / mean_actual * 100 if abs(mean_actual) > 1e-9 else None,
        "MAE_percent_of_median_actual": mae_value / median_actual * 100 if abs(median_actual) > 1e-9 else None,
    }


def empty_metrics() -> dict[str, object]:
    return {"row_count": 0, "MAE": None, "RMSE": None, "bias": None, "median_absolute_error": None, "p90_absolute_error": None, "p95_absolute_error": None, "sMAPE": None, "R2": None, "mean_actual_mw": None, "median_actual_mw": None, "MAE_percent_of_mean_actual": None, "MAE_percent_of_median_actual": None}


def daily_energy_error_proxy(rows: list[dict[str, object]], prediction_column: str) -> float | None:
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["forecast_origin_timestamp_utc"]), (int(row["horizon_h"]) - 1) // 24)].append(row)
    errors = [abs(sum(float(row[prediction_column]) for row in group) - sum(float(row[TARGET_FIELD]) for row in group)) for group in grouped.values()]
    return mean_float(errors) if errors else None


def peak_load_hour_error(rows: list[dict[str, object]], prediction_column: str) -> float | None:
    grouped = group_by(rows, "forecast_origin_timestamp_utc")
    errors = []
    for group in grouped.values():
        actual_peak = max(group, key=lambda row: float(row[TARGET_FIELD]))
        predicted_peak = max(group, key=lambda row: float(row[prediction_column]))
        errors.append(abs(int(actual_peak["horizon_h"]) - int(predicted_peak["horizon_h"])))
    return mean_float([float(value) for value in errors]) if errors else None


def write_p0054j_evidence(evidence_dir: Path, scored_rows: list[dict[str, object]], weekly_path_rows: list[dict[str, object]], summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "metrics-summary.json": write_json(evidence_dir / "metrics-summary.json", summary),
        "price-ablation-summary.json": write_json(evidence_dir / "price-ablation-summary.json", summary["price_forecast_ablation"]),
        "modeling-dataset-sample.csv": write_csv(evidence_dir / "modeling-dataset-sample.csv", scored_rows[:5000], dataset_sample_columns(summary)),
        "weekly-path-metrics.csv": write_csv(evidence_dir / "weekly-path-metrics.csv", weekly_path_rows, list(weekly_path_rows[0].keys()) if weekly_path_rows else []),
        "conditional-metrics.csv": write_csv(evidence_dir / "conditional-metrics.csv", flatten_conditional_rows(summary), conditional_columns()),
    }
    for name, text in evidence_markdowns(summary).items():
        files[name] = str(write(evidence_dir / name, text))
    return files


def evidence_markdowns(summary: dict[str, object]) -> dict[str, str]:
    common = f"# {PACKAGE_ID} {LABEL}\n\nStatus: `{summary['status']}`\n\n"
    return {
        "CHANGELOG.md": changelog_text(summary),
        "labb-label.md": common + "This package is LABB only. It is not G2-KANDIDAT and creates no deployable model artifact.\n",
        "split-policy-applied.md": common + json_block(summary["split_policy"]),
        "dataset-contract.md": common + json_block(summary["target_contract"]),
        "price-forecast-source-contract.md": common + json_block(summary["price_forecast_contract"]),
        "input-classification.md": common + json_block(summary["input_classification"]),
        "feature-groups.md": common + json_block(summary["feature_contract"]),
        "model-training-evidence.md": common + json_block(summary["model_training"]),
        "no-price-results.md": common + json_block({key: value for key, value in summary["model_results"].items() if key.endswith("_no_price")}),
        "with-price-forecast-results.md": common + json_block({key: value for key, value in summary["model_results"].items() if key.endswith("_with_p0054h_price_forecast")}),
        "price-forecast-ablation.md": common + json_block(summary["price_forecast_ablation"]),
        "model-comparison.md": common + json_block(summary["model_comparison"]),
        "direct-horizon-results.md": common + json_block(summary["direct_horizon_results"]),
        "weekly-168h-path-results.md": common + json_block(summary["weekly_168h_path_results"]),
        "conditional-regime-results.md": common + json_block(summary["conditional_regime_results"]),
        "feature-importance-or-attribution.md": common + json_block(summary["feature_importance_or_attribution"]),
        "interpretation.md": common + interpretation_text(summary),
        "what-we-learned.md": common + what_we_learned_text(summary),
        "next-package-recommendation.md": common + next_package_text(summary),
    }


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0054J Changelog

- Built SE1 consumption modeling rows under `LABB_P0054_TRAIN_THROUGH_MAY_2025`.
- Trained paired no-price and with-P0054H-price-forecast models for HGB, ExtraTrees, LightGBM and XGBoost.
- Used identical row sets for every no-price vs with-price model family.
- Skipped MLP by design because it is optional and the required tree/boosting families ran.
- Wrote direct, weekly path, conditional, ablation and feature-importance evidence.
- No actual future spot price, P0053C-B train feature, production/export/import/A61/future-flow, live API, device or runtime path was used.

Result status: {summary['status']}.
"""


def input_classification() -> dict[str, object]:
    return {
        "calendar": "forecast_safe",
        "historical_se1_consumption_lags_rollups": "forecast_safe",
        "weather": "proxy",
        "weather_proxy_label": WEATHER_PROXY_LABEL,
        "p0054h_price_forecast": "forecast_safe",
        "actual_future_spot_price": "excluded_leakage",
        "production_flow_export_import_a61": "excluded_leakage",
    }


def split_policy() -> dict[str, str]:
    return {"policy_name": "LABB_P0054_TRAIN_THROUGH_MAY_2025", "train_fit": "2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z", "holdout": "target_timestamp_utc >= 2025-06-01T00:00:00Z"}


def interpretation_text(summary: dict[str, object]) -> str:
    ablation = summary["price_forecast_ablation"]  # type: ignore[assignment]
    comparison = summary["model_comparison"]  # type: ignore[assignment]
    keep = ablation["price_forecast_should_be_kept_for_future_se1_experiments"]
    return (
        f"Best no-price holdout model: `{comparison['best_no_price_by_holdout_MAE']['model']}`.\n\n"
        f"Best with-price holdout model: `{comparison['best_with_price_by_holdout_MAE']['model']}`.\n\n"
        f"Keep price forecast for future SE1 experiments: `{keep}`.\n\n"
        "P0054H price input is not M4; it is a forecast-safe origin-local historical price baseline. Weather remains LABB actual-as-forecast proxy.\n"
    )


def what_we_learned_text(summary: dict[str, object]) -> str:
    keep = summary["price_forecast_ablation"]["price_forecast_should_be_kept_for_future_se1_experiments"]  # type: ignore[index]
    if keep:
        return "P0054H forecast-safe price features met the LABB learning threshold in at least one broad or conditional comparison. A stricter follow-up can test whether a better train-covered price forecast improves the effect.\n"
    return "The P0054H forecast-safe price baseline did not meet the LABB learning threshold. This argues against keeping this simple price feature for generic SE1 consumption models unless a more specific regime hypothesis is tested.\n"


def next_package_text(summary: dict[str, object]) -> str:
    keep = summary["price_forecast_ablation"]["price_forecast_should_be_kept_for_future_se1_experiments"]  # type: ignore[index]
    if keep:
        return "Recommended next package: inspect SE1 regimes where P0054H price helped and test a narrower price-response/regime model.\n"
    return "Recommended next package: return to the P0054A recommendation and open the advanced SE3-SE1 spread/flaskhalsregime LABB rather than continuing generic SE1 price-feature ablations.\n"


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return bool(conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone())


def grouped_mean(rows: list[dict[str, object]], keys: tuple[str, ...], field: str) -> dict[str, object]:
    grouped: dict[tuple[object, ...], list[float]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[key] for key in keys)].append(safe_float(row.get(field)))
    values = {key: mean_float(items) for key, items in grouped.items()}
    return {"values": values, "global": mean_float([safe_float(row.get(field)) for row in rows])}


def profile_predict(profile: dict[str, object], row: dict[str, object], keys: tuple[str, ...]) -> float:
    values = profile["values"]  # type: ignore[assignment]
    return float(values.get(tuple(row[key] for key in keys), profile["global"]))  # type: ignore[union-attr]


def group_by(rows: list[dict[str, object]], key: str) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[key])].append(row)
    return grouped


def row_id(row: dict[str, object]) -> str:
    return f"{row['forecast_origin_timestamp_utc']}|{row['target_timestamp_utc']}|{row['horizon_h']}"


def mean_float(values: list[float]) -> float:
    return sum(float(value) for value in values) / len(values) if values else 0.0


def std_float(values: list[float]) -> float:
    if not values:
        return 0.0
    avg = mean_float(values)
    return math.sqrt(sum((float(value) - avg) ** 2 for value in values) / len(values))


def safe_float(value: object) -> float:
    try:
        out = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0
    return out if math.isfinite(out) else 0.0


def is_finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False


def rank_map(values: list[float], *, high_rank: bool) -> list[float]:
    ordered = sorted(range(len(values)), key=lambda index: values[index], reverse=high_rank)
    ranks = [0.0] * len(values)
    for rank, index in enumerate(ordered, start=1):
        ranks[index] = float(rank)
    return ranks


def relative_change(value: float, baseline: float) -> float | None:
    if abs(baseline) < 1e-9:
        return None
    return (value - baseline) / baseline * 100


def package_version(package_name: str) -> str:
    try:
        return importlib_metadata.version(package_name)
    except importlib_metadata.PackageNotFoundError:
        return "not_installed"


def import_status(module_name: str) -> dict[str, object]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error_type": type(exc).__name__, "error": str(exc)}
    return {"ok": True, "version": str(getattr(module, "__version__", package_version(module_name)))}


def dataset_sample_columns(summary: dict[str, object]) -> list[str]:
    columns = ["forecast_origin_timestamp_utc", "target_timestamp_utc", "horizon_h", "split", TARGET_FIELD, "weather_proxy_label", "price_forecast_source", "forecast_se1_price_target_hour"]
    columns.extend(prediction_column(key) for key in summary["model_results"])  # type: ignore[operator]
    return columns


def flatten_conditional_rows(summary: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for regime, values in summary["conditional_regime_results"].items():  # type: ignore[union-attr]
        for column, metric in values.items():
            rows.append({"regime": regime, "prediction_column": column, **metric})
    return rows


def conditional_columns() -> list[str]:
    return ["regime", "prediction_column", "row_count", "MAE", "RMSE", "bias", "R2"]


def write_json(path: Path, payload: object) -> str:
    path.write_text(json.dumps(json_safe(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(path)


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> str:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})
    return str(path)


def json_block(value: object) -> str:
    return "```json\n" + json.dumps(json_safe(value), indent=2, sort_keys=True) + "\n```\n"


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feature-db", type=Path, default=DEFAULT_FEATURE_DB)
    parser.add_argument("--weather-db", type=Path, default=DEFAULT_WEATHER_DB_PATH)
    parser.add_argument("--evidence-dir", type=Path, default=EVIDENCE_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_p0054j_analysis(feature_db=args.feature_db, weather_db=args.weather_db, evidence_dir=args.evidence_dir)
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
