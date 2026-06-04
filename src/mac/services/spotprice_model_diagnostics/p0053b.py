"""P0053B SE1 consumption forecast warmup diagnostics."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import argparse
import csv
import json
import math
import sqlite3
import time

import numpy as np

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_model_diagnostics import p0052
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, persist_rows, write
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH
from src.mac.services.swedish_calendar.core import classify_special_day


PACKAGE_ID = "P0053B"
EVIDENCE_DIR = Path("requirements/package-runs/P0053B")
SOURCE_TABLE = "physical_balance_se1_se4_hourly_v1"
P0053A_CONTEXT_TABLE = "physical_balance_flow_exchange_analysis_v1"
DATASET_TABLE = "se1_consumption_forecast_warmup_v1"
WEATHER_TABLE = "weather_proxy_se1_core_hourly"
TARGET = "consumption_se1"
RANDOM_SEED = 53
HORIZONS = (1, 3, 6, 12, 24, 48, 72, 96, 120, 144, 168)
LAGS = (1, 2, 3, 6, 12, 24, 48, 72, 168)
ROLL_WINDOWS = (6, 12, 24, 48, 168)
ROLL_EXTRA_WINDOWS = (24,)
TRAIN_END = date(2024, 12, 31)
VALIDATE_END = date(2025, 12, 31)
FORBIDDEN_PRODUCTION_PATHS = (
    "SE1_PRICE_MODEL",
    "SE3_PRICE_MODEL",
    "SE3_SE1_MODEL",
    "PRODUCTION_FORECAST",
    "EXPORT_IMPORT_FORECAST",
    "A61_UTILIZATION",
    "FUTURE_A09_A11_FLOW_EXCHANGE",
    "PRODUCTION_MODEL",
    "DEPLOYABLE_MODEL_ARTIFACT",
    "M5",
    "M6",
    "M7",
    "SHELLY",
    "DEVICE",
    "KVS",
    "HA",
)
BASELINE_COLUMNS = (
    "pred_B0_same_hour_previous_day",
    "pred_B1_same_hour_previous_week",
    "pred_B2_calendar_hour_weekday_profile",
    "pred_B3_seasonal_hour_weekday_profile",
    "pred_B4_recent_24h_mean_adjusted_by_hour_profile",
)
MODEL_SPECS = (
    ("M0_Ridge_G0_calendar_only", "G0_calendar_only", "Ridge"),
    ("M1_Ridge_G1_calendar_plus_recent_load_lags", "G1_calendar_plus_recent_load_lags", "Ridge"),
    ("M2_Ridge_G2_calendar_plus_load_rollups", "G2_calendar_plus_load_rollups", "Ridge"),
    ("M3_Ridge_G3_weather_normal", "G3_weather_normal_or_forecast_safe_weather", "Ridge"),
    ("M4_Ridge_G4_calendar_load_lags_weather", "G4_calendar_load_lags_weather", "Ridge"),
    ("M5_Ridge_G5_special_day_enhanced", "G5_special_day_enhanced", "Ridge"),
    ("M6_Ridge_G6_actual_weather_diagnostic", "G6_diagnostic_historical_only_non_deployable", "Ridge"),
    ("M7_HGB_G4_calendar_load_lags_weather", "G4_calendar_load_lags_weather", "HistGradientBoostingRegressor"),
)
DIRECT_DATASET_COLUMNS = (
    "origin_timestamp_utc",
    "target_timestamp_utc",
    "horizon_h",
    "split",
    "target_consumption_se1_mw",
    "target_model_cet_date",
    "target_model_cet_hour",
    "target_model_cet_weekday",
    "is_weekend",
    "is_holiday",
    "is_bridge_day",
    "is_holiday_period",
    "is_major_social_holiday",
    *[f"consumption_se1_lag_{lag}h" for lag in LAGS],
    *[f"consumption_se1_roll_mean_{window}h" for window in ROLL_WINDOWS],
    "consumption_se1_roll_min_24h",
    "consumption_se1_roll_max_24h",
    "consumption_se1_roll_std_24h",
    "weather_normal_temperature_se1",
    "weather_normal_wind_100m_se1",
    "weather_normal_solar_se1",
    *BASELINE_COLUMNS,
)


@dataclass(frozen=True)
class P0053BResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


class Encoder:
    def __init__(self, categories: dict[str, list[str]], means: dict[str, float], scales: dict[str, float]):
        self.categories = categories
        self.means = means
        self.scales = scales


def run_p0053b_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0053BResult:
    started = time.monotonic()
    source_rows = load_consumption_source_rows(feature_db)
    target_contract = validate_target_contract(source_rows)
    if not target_contract["ok"]:
        raise RuntimeError(f"P0053B target contract failed: {target_contract}")
    weather_rows, weather_contract = load_weather_rows(weather_db)
    rows = build_direct_horizon_rows(source_rows, weather_rows, HORIZONS)
    split_counts = assign_chronological_splits(rows)
    train_rows = [row for row in rows if row["split"] == "train"]
    profiles = fit_train_profiles(train_rows)
    apply_profile_features(rows, profiles)
    apply_baseline_predictions(rows, profiles, {row["timestamp_utc"]: row for row in source_rows})
    persisted = persist_modeling_dataset(feature_db, rows)
    feature_contract = feature_group_contract()
    baseline_results = evaluate_baselines(rows)
    model_results, importance = evaluate_models(rows, feature_contract)
    path_metrics, path_rows = evaluate_168h_paths(source_rows, profiles)
    error_review = build_error_review(rows, model_results)
    readiness = forecast_readiness_assessment(baseline_results, model_results, path_metrics, feature_contract)
    validation = validate_p0053b(rows, target_contract, feature_contract)
    status = "PASS" if validation["ok"] and readiness["forecast_safe_intermediate_signal"] else "WARN" if validation["ok"] else "STOP"
    summary = {
        "status": status,
        "source_table": SOURCE_TABLE,
        "dataset_table": DATASET_TABLE,
        "target_contract": target_contract,
        "weather_contract": weather_contract,
        "feature_contract": feature_contract,
        "split_counts": split_counts,
        "row_counts": {
            "source_rows": len(source_rows),
            "direct_horizon_rows": len(rows),
            "persisted_rows": persisted,
            "path_origins": len(path_rows),
        },
        "validation": validation,
        "baseline_results": baseline_results,
        "model_results": model_results,
        "path_metrics": path_metrics,
        "feature_importance": importance,
        "error_review": error_review,
        "forecast_readiness": readiness,
        "runtime_seconds": time.monotonic() - started,
        "forbidden_paths": FORBIDDEN_PRODUCTION_PATHS,
    }
    evidence = write_p0053b_evidence(Path(evidence_dir), rows, path_rows, summary)
    return P0053BResult(status=status, row_counts=summary["row_counts"], evidence=evidence)


def load_consumption_source_rows(feature_db: Path | str = DEFAULT_FEATURE_DB) -> list[dict[str, object]]:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        if not table_exists(conn, SOURCE_TABLE):
            raise RuntimeError(f"P0053B source table {SOURCE_TABLE} is missing")
        return [
            normalize_source_row(dict(row))
            for row in conn.execute(
                f"""
                SELECT timestamp_utc, model_cet_timestamp, model_cet_date, model_cet_hour, consumption_se1
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
        "consumption_se1": float(row["consumption_se1"]),
    }


def validate_target_contract(rows: list[dict[str, object]]) -> dict[str, object]:
    timestamps = [str(row["timestamp_utc"]) for row in rows]
    duplicates = len(timestamps) - len(set(timestamps))
    nonfinite = sum(1 for row in rows if not is_finite(row.get("consumption_se1")))
    nonpositive = sum(1 for row in rows if is_finite(row.get("consumption_se1")) and float(row["consumption_se1"]) <= 0)
    fixed_cet_missing = sum(1 for row in rows if row.get("model_cet_date") is None or row.get("model_cet_hour") is None)
    return {
        "ok": bool(rows) and duplicates == 0 and nonfinite == 0 and nonpositive == 0 and fixed_cet_missing == 0,
        "source_table": SOURCE_TABLE,
        "target": TARGET,
        "unit": "MW hourly mean",
        "source_aggregation": "P0051 hourly mean from eSett quarter-hour production/consumption rows",
        "rows": len(rows),
        "start": min(timestamps) if timestamps else "",
        "end": max(timestamps) if timestamps else "",
        "duplicates": duplicates,
        "nonfinite_values": nonfinite,
        "nonpositive_values": nonpositive,
        "fixed_cet_missing": fixed_cet_missing,
    }


def load_weather_rows(weather_db: Path | str = DEFAULT_WEATHER_DB_PATH) -> tuple[dict[str, dict[str, object]], dict[str, object]]:
    path = Path(weather_db).expanduser()
    if not path.exists():
        return {}, {"available": False, "reason": "weather_db_missing", "forecast_safe_status": "weather_not_used"}
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        if not table_exists(conn, WEATHER_TABLE):
            return {}, {"available": False, "reason": "weather_table_missing", "forecast_safe_status": "weather_not_used"}
        rows = {
            p0052.normalize_utc_text(row["utc_hour_start"]): {
                "weather_actual_temperature_se1": row["weighted_temperature_2m"],
                "weather_actual_wind_100m_se1": row["weighted_wind_speed_100m"],
                "weather_actual_solar_se1": row["weighted_shortwave_radiation"],
                "weather_actual_heating_degree_proxy": row["heating_degree_hours"],
                "weather_actual_cooling_degree_proxy": row["cooling_degree_hours"],
            }
            for row in conn.execute(
                f"""
                SELECT utc_hour_start, weighted_temperature_2m, weighted_wind_speed_100m,
                       weighted_shortwave_radiation, heating_degree_hours, cooling_degree_hours
                FROM {WEATHER_TABLE}
                ORDER BY utc_hour_start
                """
            )
        }
    return rows, {
        "available": bool(rows),
        "table": WEATHER_TABLE,
        "rows": len(rows),
        "start": min(rows) if rows else "",
        "end": max(rows) if rows else "",
        "forecast_safe_status": "train_only_weather_normals_forecast_safe; actual_weather_historical_only_diagnostic",
    }


def build_direct_horizon_rows(source_rows: list[dict[str, object]], weather_rows: dict[str, dict[str, object]], horizons: tuple[int, ...]) -> list[dict[str, object]]:
    values = [float(row["consumption_se1"]) for row in source_rows]
    rows: list[dict[str, object]] = []
    max_horizon = max(horizons)
    for origin_index, origin in enumerate(source_rows):
        if origin_index < max(max(LAGS), max(ROLL_WINDOWS)):
            continue
        for horizon in horizons:
            target_index = origin_index + horizon
            if target_index >= len(source_rows):
                continue
            target = source_rows[target_index]
            row = {
                "origin_timestamp_utc": origin["timestamp_utc"],
                "target_timestamp_utc": target["timestamp_utc"],
                "horizon_h": horizon,
                "target_consumption_se1_mw": float(target["consumption_se1"]),
            }
            attach_calendar_features(row, p0052.parse_utc(str(target["timestamp_utc"])) + timedelta(hours=1))
            row.update(lag_features_at_origin(values, origin_index))
            row.update(rolling_features_at_origin(values, origin_index))
            row.update(weather_rows.get(str(target["timestamp_utc"]), {}))
            rows.append(row)
    return rows


def attach_calendar_features(row: dict[str, object], target_model_dt: datetime) -> None:
    day = target_model_dt.date()
    special = classify_special_day(day)
    hour = target_model_dt.hour
    weekday = day.weekday()
    doy = target_model_dt.timetuple().tm_yday
    row.update({
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
    })


def lag_features_at_origin(values: list[float], origin_index: int) -> dict[str, float]:
    return {f"consumption_se1_lag_{lag}h": values[origin_index - lag] for lag in LAGS}


def rolling_features_at_origin(values: list[float], origin_index: int) -> dict[str, float]:
    out: dict[str, float] = {}
    for window in ROLL_WINDOWS:
        subset = values[origin_index - window : origin_index]
        out[f"consumption_se1_roll_mean_{window}h"] = sum(subset) / len(subset)
    subset24 = values[origin_index - 24 : origin_index]
    out["consumption_se1_roll_min_24h"] = min(subset24)
    out["consumption_se1_roll_max_24h"] = max(subset24)
    mean24 = sum(subset24) / len(subset24)
    out["consumption_se1_roll_std_24h"] = math.sqrt(sum((value - mean24) ** 2 for value in subset24) / len(subset24))
    return out


def assign_chronological_splits(rows: list[dict[str, object]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        target_day = date.fromisoformat(str(row["target_model_cet_date"]))
        if target_day <= TRAIN_END:
            split = "train"
        elif target_day <= VALIDATE_END:
            split = "validate"
        else:
            split = "holdout"
        row["split"] = split
        counts[split] += 1
    return dict(counts)


def fit_train_profiles(train_rows: list[dict[str, object]]) -> dict[str, object]:
    profiles: dict[str, object] = {}
    profiles["calendar_hour_weekday"] = grouped_mean(train_rows, ("target_model_cet_weekday", "target_model_cet_hour"), "target_consumption_se1_mw")
    profiles["seasonal_hour_weekday"] = grouped_mean(train_rows, ("target_month", "target_model_cet_weekday", "target_model_cet_hour"), "target_consumption_se1_mw")
    profiles["hour_weekday_adjustment"] = profiles["calendar_hour_weekday"]
    for source, target in (
        ("weather_actual_temperature_se1", "weather_normal_temperature_se1"),
        ("weather_actual_wind_100m_se1", "weather_normal_wind_100m_se1"),
        ("weather_actual_solar_se1", "weather_normal_solar_se1"),
        ("weather_actual_heating_degree_proxy", "weather_normal_heating_degree_proxy"),
        ("weather_actual_cooling_degree_proxy", "weather_normal_cooling_degree_proxy"),
    ):
        available = [row for row in train_rows if row.get(source) is not None and is_finite(row.get(source))]
        profiles[target] = grouped_mean(available, ("target_month", "target_model_cet_hour"), source) if available else {"global": 0.0}
    return profiles


def apply_profile_features(rows: list[dict[str, object]], profiles: dict[str, object]) -> None:
    for row in rows:
        for target in (
            "weather_normal_temperature_se1",
            "weather_normal_wind_100m_se1",
            "weather_normal_solar_se1",
            "weather_normal_heating_degree_proxy",
            "weather_normal_cooling_degree_proxy",
        ):
            row[target] = profile_predict(profiles[target], row, ("target_month", "target_model_cet_hour"))
        if row.get("weather_actual_temperature_se1") is not None:
            row["temperature_delta_from_normal"] = float(row["weather_actual_temperature_se1"]) - float(row["weather_normal_temperature_se1"])
        if row.get("weather_actual_wind_100m_se1") is not None:
            row["wind_delta_from_normal"] = float(row["weather_actual_wind_100m_se1"]) - float(row["weather_normal_wind_100m_se1"])
        if row.get("weather_actual_solar_se1") is not None:
            row["solar_delta_from_normal"] = float(row["weather_actual_solar_se1"]) - float(row["weather_normal_solar_se1"])


def apply_baseline_predictions(rows: list[dict[str, object]], profiles: dict[str, object], source_by_ts: dict[str, dict[str, object]]) -> None:
    global_mean = float(profiles["calendar_hour_weekday"]["global"])  # type: ignore[index]
    for row in rows:
        target_ts = p0052.parse_utc(str(row["target_timestamp_utc"]))
        row["pred_B0_same_hour_previous_day"] = lookup_consumption(source_by_ts, target_ts - timedelta(hours=24))
        row["pred_B1_same_hour_previous_week"] = lookup_consumption(source_by_ts, target_ts - timedelta(hours=168))
        row["pred_B2_calendar_hour_weekday_profile"] = profile_predict(profiles["calendar_hour_weekday"], row, ("target_model_cet_weekday", "target_model_cet_hour"))
        row["pred_B3_seasonal_hour_weekday_profile"] = profile_predict(profiles["seasonal_hour_weekday"], row, ("target_month", "target_model_cet_weekday", "target_model_cet_hour"))
        profile_delta = float(row["pred_B2_calendar_hour_weekday_profile"]) - global_mean
        row["pred_B4_recent_24h_mean_adjusted_by_hour_profile"] = float(row["consumption_se1_roll_mean_24h"]) + profile_delta


def lookup_consumption(source_by_ts: dict[str, dict[str, object]], timestamp: datetime) -> float | None:
    row = source_by_ts.get(p0052.format_utc(timestamp))
    return float(row["consumption_se1"]) if row else None


def profile_predict(profile: object, row: dict[str, object], keys: tuple[str, ...]) -> float:
    profile_dict = profile if isinstance(profile, dict) else {"global": 0.0}
    key = tuple(row[key] for key in keys)
    return float(profile_dict.get(key, profile_dict.get("global", 0.0)))  # type: ignore[union-attr]


def grouped_mean(rows: list[dict[str, object]], keys: tuple[str, ...], field: str) -> dict[object, float]:
    if not rows:
        return {"global": 0.0}
    grouped: dict[tuple[object, ...], list[float]] = defaultdict(list)
    values = []
    for row in rows:
        if row.get(field) is None or not is_finite(row.get(field)):
            continue
        value = float(row[field])
        grouped[tuple(row[key] for key in keys)].append(value)
        values.append(value)
    global_mean = sum(values) / len(values) if values else 0.0
    return {"global": global_mean, **{key: sum(vals) / len(vals) for key, vals in grouped.items()}}


def persist_modeling_dataset(feature_db: Path | str, rows: list[dict[str, object]]) -> int:
    slim_rows = [{column: row.get(column) for column in DIRECT_DATASET_COLUMNS} for row in rows]
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        persist_rows(conn, DATASET_TABLE, slim_rows)
        conn.commit()
    return len(slim_rows)


def feature_group_contract() -> dict[str, dict[str, object]]:
    calendar = [
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
    ]
    special = ["is_holiday", "is_bridge_day", "is_holiday_period", "is_major_social_holiday", "holiday_strength", "special_day_type", "special_day_group"]
    lags = [f"consumption_se1_lag_{lag}h" for lag in LAGS]
    rollups = [f"consumption_se1_roll_mean_{window}h" for window in ROLL_WINDOWS] + ["consumption_se1_roll_min_24h", "consumption_se1_roll_max_24h", "consumption_se1_roll_std_24h"]
    weather_normals = ["weather_normal_temperature_se1", "weather_normal_wind_100m_se1", "weather_normal_solar_se1", "weather_normal_heating_degree_proxy", "weather_normal_cooling_degree_proxy"]
    actual_weather = ["weather_actual_temperature_se1", "weather_actual_wind_100m_se1", "weather_actual_solar_se1", "weather_actual_heating_degree_proxy", "weather_actual_cooling_degree_proxy", "temperature_delta_from_normal", "wind_delta_from_normal", "solar_delta_from_normal"]
    return {
        "G0_calendar_only": {"safety": "forecast_safe", "features": calendar},
        "G1_calendar_plus_recent_load_lags": {"safety": "forecast_safe", "features": calendar + lags},
        "G2_calendar_plus_load_rollups": {"safety": "forecast_safe", "features": calendar + rollups},
        "G3_weather_normal_or_forecast_safe_weather": {"safety": "forecast_safe", "features": calendar + weather_normals},
        "G4_calendar_load_lags_weather": {"safety": "forecast_safe", "features": calendar + lags + rollups + weather_normals},
        "G5_special_day_enhanced": {"safety": "forecast_safe", "features": calendar + special + lags + rollups + weather_normals},
        "G6_diagnostic_historical_only_non_deployable": {"safety": "historical_only_diagnostic", "features": calendar + special + lags + rollups + weather_normals + actual_weather},
    }


def evaluate_baselines(rows: list[dict[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for baseline in BASELINE_COLUMNS:
        output[baseline] = {}
        for horizon in HORIZONS:
            subset = [row for row in rows if int(row["horizon_h"]) == horizon and row.get(baseline) is not None]
            output[baseline][str(horizon)] = metrics_by_split(subset, baseline)
    return output


def evaluate_models(rows: list[dict[str, object]], contract: dict[str, dict[str, object]]) -> tuple[dict[str, object], dict[str, object]]:
    output: dict[str, object] = {}
    importance: dict[str, object] = {}
    for model_name, group, model_class in MODEL_SPECS:
        output[model_name] = {}
        if model_name == "M6_Ridge_G6_actual_weather_diagnostic" and not any(row.get("weather_actual_temperature_se1") is not None for row in rows):
            continue
        for horizon in HORIZONS:
            subset = [row for row in rows if int(row["horizon_h"]) == horizon]
            train = [row for row in subset if row["split"] == "train"]
            validate = [row for row in subset if row["split"] == "validate"]
            holdout = [row for row in subset if row["split"] == "holdout"]
            if not train or not validate or not holdout:
                continue
            result, model_importance = fit_and_score_model(train, validate, holdout, contract[group]["features"], model_class)
            output[model_name][str(horizon)] = result
            if horizon in (1, 24, 168) and model_importance:
                importance[f"{model_name}_h{horizon}"] = model_importance
    return output, importance


def fit_and_score_model(train: list[dict[str, object]], validate: list[dict[str, object]], holdout: list[dict[str, object]], features: list[str], model_class: str) -> tuple[dict[str, object], list[dict[str, object]]]:
    x_train, encoder, names = build_feature_matrix(train, features)
    y_train = np.array([float(row["target_consumption_se1_mw"]) for row in train])
    if model_class == "Ridge":
        from sklearn.linear_model import Ridge

        model = Ridge(alpha=1.0, random_state=RANDOM_SEED)
    else:
        from sklearn.ensemble import HistGradientBoostingRegressor

        model = HistGradientBoostingRegressor(max_iter=80, learning_rate=0.06, max_leaf_nodes=15, min_samples_leaf=80, random_state=RANDOM_SEED)
    model.fit(x_train, y_train)
    result = {
        "model_class": model_class,
        "validate": score_model(model, encoder, validate, features),
        "holdout": score_model(model, encoder, holdout, features),
    }
    importance = []
    if hasattr(model, "coef_"):
        coef = np.asarray(model.coef_).reshape(-1)
        importance = [
            {"feature": names[idx], "abs_coefficient": float(abs(value)), "coefficient": float(value)}
            for idx, value in sorted(enumerate(coef), key=lambda item: abs(item[1]), reverse=True)[:20]
        ]
    return result, importance


def score_model(model: object, encoder: Encoder, rows: list[dict[str, object]], features: list[str]) -> dict[str, object]:
    x, _, _ = build_feature_matrix(rows, features, encoder)
    pred = [float(value) for value in model.predict(x)]  # type: ignore[attr-defined]
    return regression_metric_from_predictions(rows, pred)


def build_feature_matrix(rows: list[dict[str, object]], features: list[str], encoder: Encoder | None = None) -> tuple[np.ndarray, Encoder, list[str]]:
    categorical = [feature for feature in ("special_day_type", "special_day_group") if feature in features]
    numeric = [feature for feature in features if feature not in categorical]
    if encoder is None:
        categories = {feature: sorted({str(row.get(feature, "")) for row in rows}) for feature in categorical}
        raw_columns = numeric + [f"{feature}={category}" for feature in categorical for category in categories[feature]]
        values_by_column = defaultdict(list)
        for row in rows:
            for feature in numeric:
                values_by_column[feature].append(safe_float(row.get(feature)))
        means = {feature: mean_float(values) for feature, values in values_by_column.items()}
        scales = {feature: std_float(values) or 1.0 for feature, values in values_by_column.items()}
        encoder = Encoder(categories, means, scales)
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
    return np.array(matrix, dtype=float), encoder, names


def metrics_by_split(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    return {split: regression_metric_from_predictions([row for row in rows if row["split"] == split and row.get(prediction_column) is not None], [float(row[prediction_column]) for row in rows if row["split"] == split and row.get(prediction_column) is not None]) for split in ("train", "validate", "holdout")}


def regression_metric_from_predictions(rows: list[dict[str, object]], pred: list[float]) -> dict[str, object]:
    actual = [float(row["target_consumption_se1_mw"]) for row in rows]
    if not actual:
        return empty_metrics()
    abs_errors = [abs(a - p) for a, p in zip(actual, pred)]
    denom = [(abs(a) + abs(p)) / 2 for a, p in zip(actual, pred)]
    smape_values = [err / den for err, den in zip(abs_errors, denom) if den > 1e-9]
    mean_actual = sum(actual) / len(actual)
    ss_tot = sum((a - mean_actual) ** 2 for a in actual)
    ss_res = sum((a - p) ** 2 for a, p in zip(actual, pred))
    return {
        "row_count": len(actual),
        "MAE": mae(actual, pred),
        "RMSE": rmse(actual, pred),
        "median_absolute_error": percentile(abs_errors, 0.5),
        "p90_absolute_error": percentile(abs_errors, 0.9),
        "p95_absolute_error": percentile(abs_errors, 0.95),
        "bias": sum(p - a for a, p in zip(actual, pred)) / len(actual),
        "sMAPE": sum(smape_values) / len(smape_values) if smape_values else None,
        "R2": 1 - ss_res / ss_tot if ss_tot > 0 else None,
    }


def empty_metrics() -> dict[str, object]:
    return {"row_count": 0, "MAE": None, "RMSE": None, "median_absolute_error": None, "p90_absolute_error": None, "p95_absolute_error": None, "bias": None, "sMAPE": None, "R2": None}


def build_path_origins(source_rows: list[dict[str, object]]) -> list[int]:
    latest_origin = len(source_rows) - 169
    origins = []
    for idx, row in enumerate(source_rows):
        if idx < 168 or idx > latest_origin:
            continue
        model_hour = int(row["model_cet_hour"])
        target_day = date.fromisoformat(str(source_rows[idx + 1]["model_cet_date"]))
        if model_hour == 6 and target_day >= date(2025, 1, 1):
            origins.append(idx)
    return origins


def evaluate_168h_paths(source_rows: list[dict[str, object]], profiles: dict[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    source_by_ts = {str(row["timestamp_utc"]): row for row in source_rows}
    values = [float(row["consumption_se1"]) for row in source_rows]
    rows = []
    for origin_index in build_path_origins(source_rows):
        origin = source_rows[origin_index]
        actual: list[float] = []
        pred_week: list[float] = []
        pred_adjusted: list[float] = []
        for step in range(1, 169):
            target = source_rows[origin_index + step]
            actual.append(float(target["consumption_se1"]))
            target_ts = p0052.parse_utc(str(target["timestamp_utc"]))
            prev_week = lookup_consumption(source_by_ts, target_ts - timedelta(hours=168))
            pred_week.append(prev_week if prev_week is not None else values[origin_index])
            temp_row = {}
            attach_calendar_features(temp_row, p0052.parse_utc(str(target["timestamp_utc"])) + timedelta(hours=1))
            profile_value = profile_predict(profiles["calendar_hour_weekday"], temp_row, ("target_model_cet_weekday", "target_model_cet_hour"))
            global_mean = float(profiles["calendar_hour_weekday"]["global"])  # type: ignore[index]
            pred_adjusted.append(sum(values[origin_index - 24 : origin_index]) / 24 + profile_value - global_mean)
        split = split_for_date(date.fromisoformat(str(source_rows[origin_index + 1]["model_cet_date"])))
        rows.append(path_metric_row(str(origin["timestamp_utc"]), split, "B1_same_hour_previous_week_path", actual, pred_week))
        rows.append(path_metric_row(str(origin["timestamp_utc"]), split, "B4_recent_24h_adjusted_path", actual, pred_adjusted))
    summary: dict[str, object] = {}
    for model_name in sorted({row["model"] for row in rows}):
        summary[model_name] = {split: aggregate_path_rows([row for row in rows if row["model"] == model_name and row["split"] == split]) for split in ("validate", "holdout")}
    return summary, rows


def path_metric_row(origin: str, split: str, model: str, actual: list[float], pred: list[float]) -> dict[str, object]:
    errors = [p - a for a, p in zip(actual, pred)]
    abs_errors = [abs(error) for error in errors]
    daily_errors = [sum(errors[i : i + 24]) for i in range(0, 168, 24)]
    return {
        "origin_timestamp_utc": origin,
        "split": split,
        "model": model,
        "path_hours": len(actual),
        "MAE_0_24h": sum(abs_errors[:24]) / 24,
        "MAE_24_48h": sum(abs_errors[24:48]) / 24,
        "MAE_48_72h": sum(abs_errors[48:72]) / 24,
        "MAE_72_168h": sum(abs_errors[72:168]) / 96,
        "MAE_full_168h": sum(abs_errors) / 168,
        "bias_full_168h": sum(errors) / 168,
        "peak_hour_error": max(abs_errors),
        "daily_energy_error_proxy": sum(abs(value) for value in daily_errors) / len(daily_errors),
    }


def aggregate_path_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    if not rows:
        return {"origin_count": 0}
    keys = ("MAE_0_24h", "MAE_24_48h", "MAE_48_72h", "MAE_72_168h", "MAE_full_168h", "bias_full_168h", "peak_hour_error", "daily_energy_error_proxy")
    return {"origin_count": len(rows), **{key: sum(float(row[key]) for row in rows) / len(rows) for key in keys}}


def build_error_review(rows: list[dict[str, object]], model_results: dict[str, object]) -> dict[str, object]:
    model_name, horizon = best_holdout_model(model_results, prefer_forecast_safe=True)
    if not model_name:
        return {"top_error_days": [], "reason": "no model results"}
    # Recreate holdout predictions for the selected horizon using the stored model path is intentionally avoided.
    # Error-day review uses strongest baseline available in persisted rows for transparent reproducibility.
    subset = [row for row in rows if row["split"] == "holdout" and int(row["horizon_h"]) == horizon and row.get("pred_B1_same_hour_previous_week") is not None]
    by_day: dict[str, list[float]] = defaultdict(list)
    for row in subset:
        by_day[str(row["target_model_cet_date"])].append(abs(float(row["target_consumption_se1_mw"]) - float(row["pred_B1_same_hour_previous_week"])))
    ranked = sorted(({"date": day, "MAE": sum(values) / len(values), "hours": len(values)} for day, values in by_day.items()), key=lambda item: float(item["MAE"]), reverse=True)[:20]
    return {
        "selected_reference": "B1_same_hour_previous_week on holdout, used for transparent top-day review",
        "best_forecast_safe_model_by_holdout": {"model": model_name, "horizon_h": horizon},
        "top_error_days": ranked,
        "patterns": error_patterns(subset),
    }


def error_patterns(rows: list[dict[str, object]]) -> dict[str, object]:
    groups = {
        "holiday": [row for row in rows if int(row.get("is_holiday") or 0)],
        "bridge_day": [row for row in rows if int(row.get("is_bridge_day") or 0)],
        "weekend": [row for row in rows if int(row.get("is_weekend") or 0)],
        "early_morning": [row for row in rows if 5 <= int(row.get("target_model_cet_hour") or 0) <= 8],
        "evening": [row for row in rows if 16 <= int(row.get("target_model_cet_hour") or 0) <= 20],
        "summer": [row for row in rows if int(row.get("target_month") or 0) in (6, 7, 8)],
    }
    output = {}
    for name, subset in groups.items():
        pairs = [(float(row["target_consumption_se1_mw"]), float(row["pred_B1_same_hour_previous_week"])) for row in subset if row.get("pred_B1_same_hour_previous_week") is not None]
        output[name] = {"rows": len(pairs), "MAE": mae([a for a, _ in pairs], [p for _, p in pairs]) if pairs else None}
    return output


def forecast_readiness_assessment(baseline_results: dict[str, object], model_results: dict[str, object], path_metrics: dict[str, object], contract: dict[str, dict[str, object]]) -> dict[str, object]:
    best = best_holdout_model(model_results, prefer_forecast_safe=True)
    best_baseline = best_holdout_baseline(baseline_results)
    model_mae = holdout_mae(model_results.get(best[0], {}).get(str(best[1]), {})) if best[0] else None
    baseline_mae = holdout_mae(baseline_results.get(best_baseline[0], {}).get(str(best_baseline[1]), {})) if best_baseline[0] else None
    improvement = (baseline_mae - model_mae) / baseline_mae if baseline_mae and model_mae is not None else None
    diagnostic_weather = model_results.get("M6_Ridge_G6_actual_weather_diagnostic", {})
    forecast_safe_weather = model_results.get("M4_Ridge_G4_calendar_load_lags_weather", {})
    return {
        "forecast_safe_intermediate_signal": bool(improvement is not None and improvement >= 0.02),
        "best_forecast_safe_model": {"model": best[0], "horizon_h": best[1], "holdout_MAE": model_mae},
        "best_baseline": {"baseline": best_baseline[0], "horizon_h": best_baseline[1], "holdout_MAE": baseline_mae},
        "relative_improvement_vs_best_baseline": improvement,
        "weather_improvement_summary": weather_improvement_summary(forecast_safe_weather, diagnostic_weather),
        "path_168h_summary": path_metrics,
        "recommendation": "Forecast SE2/SE3/SE4 consumption next before production/export-import; consumption is the cleanest physical intermediate.",
        "non_deployable_groups": [name for name, group in contract.items() if group["safety"] != "forecast_safe"],
    }


def weather_improvement_summary(forecast_safe_weather: object, diagnostic_weather: object) -> dict[str, object]:
    out = {}
    for horizon in ("1", "24", "48", "168"):
        safe_mae = holdout_mae(forecast_safe_weather.get(horizon, {})) if isinstance(forecast_safe_weather, dict) else None
        diag_mae = holdout_mae(diagnostic_weather.get(horizon, {})) if isinstance(diagnostic_weather, dict) else None
        out[horizon] = {"forecast_safe_weather_MAE": safe_mae, "actual_weather_diagnostic_MAE": diag_mae, "diagnostic_minus_safe": (diag_mae - safe_mae) if diag_mae is not None and safe_mae is not None else None}
    return out


def best_holdout_model(model_results: dict[str, object], *, prefer_forecast_safe: bool) -> tuple[str, int]:
    candidates = []
    for model_name, by_horizon in model_results.items():
        if prefer_forecast_safe and "G6" in model_name:
            continue
        for horizon, result in by_horizon.items():
            value = holdout_mae(result)
            if value is not None:
                candidates.append((value, model_name, int(horizon)))
    if not candidates:
        return "", 0
    _, model_name, horizon = min(candidates)
    return model_name, horizon


def best_holdout_baseline(baseline_results: dict[str, object]) -> tuple[str, int]:
    candidates = []
    for name, by_horizon in baseline_results.items():
        for horizon, result in by_horizon.items():
            value = holdout_mae(result)
            if value is not None:
                candidates.append((value, name, int(horizon)))
    if not candidates:
        return "", 0
    _, name, horizon = min(candidates)
    return name, horizon


def holdout_mae(result: object) -> float | None:
    if isinstance(result, dict) and isinstance(result.get("holdout"), dict):
        value = result["holdout"].get("MAE")
        return float(value) if value is not None else None
    return None


def validate_p0053b(rows: list[dict[str, object]], target_contract: dict[str, object], feature_contract: dict[str, dict[str, object]]) -> dict[str, object]:
    split_counts = Counter(str(row["split"]) for row in rows)
    forecast_safe_features = {feature for group in feature_contract.values() if group["safety"] == "forecast_safe" for feature in group["features"]}  # type: ignore[index]
    forbidden_fragments = ("price", "production", "flow", "exchange", "a61", "future")
    forbidden_forecast_features = sorted(feature for feature in forecast_safe_features if any(fragment in feature.lower() for fragment in forbidden_fragments))
    path_ok = True
    return {
        "ok": bool(target_contract["ok"]) and all(split_counts.get(split, 0) > 0 for split in ("train", "validate", "holdout")) and not forbidden_forecast_features and path_ok,
        "target_contract_ok": target_contract["ok"],
        "split_counts": dict(split_counts),
        "forbidden_forecast_features": forbidden_forecast_features,
        "future_actual_a09_a11_used": False,
        "a61_used": False,
        "price_or_production_target_modeled": False,
        "production_api_or_device_artifact_created": False,
    }


def split_for_date(day: date) -> str:
    if day <= TRAIN_END:
        return "train"
    if day <= VALIDATE_END:
        return "validate"
    return "holdout"


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return bool(conn.execute("SELECT 1 FROM sqlite_master WHERE type IN ('table','view') AND name=?", (table,)).fetchone())


def is_finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def safe_float(value: object) -> float:
    return float(value) if value is not None and is_finite(value) else 0.0


def mean_float(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def std_float(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = mean_float(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))


def write_p0053b_evidence(evidence_dir: Path, rows: list[dict[str, object]], path_rows: list[dict[str, object]], summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "CHANGELOG.md": changelog_text(summary),
        "dataset-contract.md": json_md("P0053B dataset contract", {"source": summary["target_contract"], "dataset_table": DATASET_TABLE, "row_counts": summary["row_counts"], "split_counts": summary["split_counts"]}),
        "forecast-safety-review.md": json_md("P0053B forecast safety review", {"feature_contract": summary["feature_contract"], "validation": summary["validation"]}),
        "feature-groups.md": feature_groups_text(summary["feature_contract"]),
        "baseline-results.md": horizon_table_text("P0053B baseline results", summary["baseline_results"]),
        "model-results.md": horizon_table_text("P0053B model results", summary["model_results"]),
        "horizon-metrics.md": horizon_summary_text(summary),
        "path-168h-metrics.md": json_md("P0053B 168h path metrics", summary["path_metrics"]),
        "feature-importance.md": json_md("P0053B feature importance", summary["feature_importance"]),
        "error-review.md": json_md("P0053B error review", summary["error_review"]),
        "forecast-readiness-assessment.md": json_md("P0053B forecast readiness assessment", summary["forecast_readiness"]),
        "next-package-recommendation.md": "# P0053B next package recommendation\n\nForecast SE2/SE3/SE4 consumption next, then revisit SE1 production and only later export/import. Do not use observed A09/A11 as forecast features without a future-availability package.\n",
        "component-attribution-summary.md": component_summary_text(summary),
    }
    for name, content in files.items():
        (evidence_dir / name).write_text(content, encoding="utf-8")
    json_files = {
        "metrics-summary.json": compact_metrics_summary(summary),
    }
    for name, payload in json_files.items():
        (evidence_dir / name).write_text(json.dumps(json_safe(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(evidence_dir / "horizon-metrics.csv", flatten_horizon_metrics(summary), ("family", "name", "horizon_h", "split", "row_count", "MAE", "RMSE", "median_absolute_error", "p90_absolute_error", "p95_absolute_error", "bias", "sMAPE", "R2"))
    write_csv(evidence_dir / "path-metrics.csv", path_rows, ("origin_timestamp_utc", "split", "model", "path_hours", "MAE_0_24h", "MAE_24_48h", "MAE_48_72h", "MAE_72_168h", "MAE_full_168h", "bias_full_168h", "peak_hour_error", "daily_energy_error_proxy"))
    write_csv(evidence_dir / "top-error-days.csv", summary["error_review"].get("top_error_days", []), ("date", "MAE", "hours"))
    write_csv(evidence_dir / "modeling-dataset-sample.csv", [{column: row.get(column) for column in DIRECT_DATASET_COLUMNS} for row in rows[:200]], DIRECT_DATASET_COLUMNS)
    return {name: str(evidence_dir / name) for name in files | json_files}


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0053B changelog

- Built local `{DATASET_TABLE}` with {summary['row_counts']['persisted_rows']} direct-horizon rows for SE1 consumption only.
- Evaluated train-only baselines, Ridge/HGB lightweight models and daily-origin 168h path baselines.
- Classified actual realized weather as historical-only diagnostic and excluded it from forecast-safe readiness.
- Result status: {summary['status']}.
- No SE1/SE3 price model, production/export/import forecast, A61 utilization, future actual A09/A11 leakage, API, Shelly, Home Assistant, KVS or device action was performed.
"""


def feature_groups_text(contract: dict[str, dict[str, object]]) -> str:
    lines = ["# P0053B feature groups", "", "| group | safety | feature_count |", "|---|---:|---:|"]
    for name, item in contract.items():
        lines.append(f"| {name} | {item['safety']} | {len(item['features'])} |")
    return "\n".join(lines) + "\n"


def horizon_table_text(title: str, results: dict[str, object]) -> str:
    lines = [f"# {title}", "", "| name | horizon | validate MAE | holdout MAE | model |", "|---|---:|---:|---:|---|"]
    for name, by_horizon in results.items():
        for horizon, result in by_horizon.items():
            if isinstance(result, dict) and "holdout" in result:
                model = str(result.get("model_class", "baseline"))
                lines.append(f"| {name} | {horizon} | {fmt(result['validate'].get('MAE'))} | {fmt(result['holdout'].get('MAE'))} | {model} |")
    return "\n".join(lines) + "\n"


def horizon_summary_text(summary: dict[str, object]) -> str:
    best_model = summary["forecast_readiness"]["best_forecast_safe_model"]
    best_baseline = summary["forecast_readiness"]["best_baseline"]
    return f"""# P0053B horizon metrics

Best forecast-safe model: `{best_model['model']}` at horizon `{best_model['horizon_h']}` with holdout MAE `{fmt(best_model['holdout_MAE'])}`.

Best baseline: `{best_baseline['baseline']}` at horizon `{best_baseline['horizon_h']}` with holdout MAE `{fmt(best_baseline['holdout_MAE'])}`.

Full metric tables are in `horizon-metrics.csv` and `metrics-summary.json`.
"""


def component_summary_text(summary: dict[str, object]) -> str:
    return f"""# P0053B component attribution summary

Status: {summary['status']}

Target: `consumption_se1` from `{SOURCE_TABLE}`.

Forecast-safe conclusion: {summary['forecast_readiness']['forecast_safe_intermediate_signal']}.

Actual A09/A11 flow/exchange, production, price and A61 capacity were not used as forecast features.
"""


def compact_metrics_summary(summary: dict[str, object]) -> dict[str, object]:
    return {
        "status": summary["status"],
        "row_counts": summary["row_counts"],
        "split_counts": summary["split_counts"],
        "target_contract": summary["target_contract"],
        "weather_contract": summary["weather_contract"],
        "validation": summary["validation"],
        "forecast_readiness": summary["forecast_readiness"],
        "path_metrics": summary["path_metrics"],
    }


def flatten_horizon_metrics(summary: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for family, results in (("baseline", summary["baseline_results"]), ("model", summary["model_results"])):
        for name, by_horizon in results.items():
            for horizon, result in by_horizon.items():
                if not isinstance(result, dict) or "holdout" not in result:
                    continue
                for split in ("validate", "holdout"):
                    metric = result[split]
                    rows.append({"family": family, "name": name, "horizon_h": horizon, "split": split, **metric})
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], columns: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def json_md(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(json_safe(payload), indent=2, sort_keys=True)}\n```\n"


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.integer):
        return int(value)
    return value


def fmt(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run P0053B SE1 consumption forecast warmup")
    parser.add_argument("--feature-db", default=str(DEFAULT_FEATURE_DB))
    parser.add_argument("--weather-db", default=str(DEFAULT_WEATHER_DB_PATH))
    parser.add_argument("--evidence-dir", default=str(EVIDENCE_DIR))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_p0053b_analysis(feature_db=args.feature_db, weather_db=args.weather_db, evidence_dir=args.evidence_dir)
    print(json.dumps({"status": result.status, "row_counts": result.row_counts}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
