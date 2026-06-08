"""P0056K LABB realistic DayAhead AI model restart."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time as dt_time, timedelta, timezone
from pathlib import Path
import csv
import json
import math
import sqlite3
import sys
import time
import warnings
from zoneinfo import ZoneInfo

import numpy as np

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0056c, p0056d, p0056f
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write


PACKAGE_ID = "P0056K"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0056K")
SCOPED_AREAS = ("SE1", "SE2", "SE3", "FI")
STOCKHOLM = ZoneInfo("Europe/Stockholm")
FIRST_EVAL_DELIVERY_DAY = date(2025, 6, 1)
FIRST_MODELING_DELIVERY_DAY = date(2022, 6, 15)
EXPANDING_TRAIN_START_UTC = "2022-06-01T00:00:00Z"
PREDICTION_COLUMN = "prediction"
TARGET = p0054k.TARGET_FIELD

FEATURES = [
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
    "safe_same_hour_lag_168h",
    "safe_same_hour_lag_336h",
    "safe_same_hour_delta_168_336h",
    "origin_consumption_lag_1h",
    "origin_consumption_lag_24h",
    "origin_consumption_lag_168h",
    "origin_roll_mean_24h",
    "origin_roll_mean_168h",
    "origin_roll_std_24h",
    "weather_proxy_temperature_2m_area",
    "weather_proxy_apparent_temperature_area",
    "weather_proxy_wind_speed_area",
    "weather_proxy_cloud_cover_area",
    "weather_proxy_humidity_area",
    "weather_proxy_precipitation_area",
    "weather_proxy_snow_depth_area",
    "weather_proxy_heating_degree_hours_area",
    "weather_proxy_cooling_degree_hours_area",
    "weather_proxy_temperature_roll_mean_24h_area",
]

OLD_STATIC_BASELINES = {
    "SE1": 124.166,
    "SE2": 197.547,
    "SE3": 250.928,
    "FI": 311.189,
}
ROLLING_BASELINES = {
    "P0056G_weekly": {"SE1": 131.253, "SE2": 207.757, "SE3": 282.365, "FI": 422.324},
    "P0056H2_static_style_36h": {"SE1": 142.010, "SE2": 228.549, "SE3": 282.424, "FI": 340.798},
}


@dataclass(frozen=True)
class Origin:
    origin_local: datetime
    origin_utc: str
    delivery_day: date


@dataclass(frozen=True)
class P0056KResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0056k_realistic_dayahead_restart(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0056KResult:
    started = time.monotonic()
    warnings.filterwarnings("ignore", message="X does not have valid feature names.*")
    feature_path = Path(feature_db).expanduser()
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)
    initialize_progress(evidence_path)
    with sqlite3.connect(feature_path, timeout=60.0) as conn:
        conn.row_factory = sqlite3.Row
        targets_all, target_contract_all = p0056c.load_area_targets(conn)
        p0056b_weather_all, p0056b_contract_all = p0056c.load_area_weather_rows(conn)
        p0056d_weather_all, p0056d_contract_all = p0056d.load_p0056d_area_weather_rows(conn)

    input_contract = input_source_contract(target_contract_all, p0056b_contract_all, p0056d_contract_all)
    if not input_contract["ok"]:
        summary = stopped_summary(started, feature_path, input_contract)
        evidence = write_evidence(evidence_path, summary)
        return P0056KResult("STOP", summary["row_counts"], evidence)  # type: ignore[arg-type]

    environment = p0054k.capture_environment_status()
    specs = model_specs_for_p0056k(environment)
    model_order = ["M0", "M1"] + [f"M{index}" for index in range(2, 6) if f"M{index}" in specs] + ["M6", "M7"]
    origin_results: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    skipped_models: list[dict[str, object]] = neural_skips()
    origin_counts_by_area = {
        area: len(dayahead_origins(targets_all[area], p0056b_weather_all[area] if area == "SE3" else p0056d_weather_all[area], FIRST_EVAL_DELIVERY_DAY))
        for area in SCOPED_AREAS
    }
    total_jobs = sum(count * len(model_order) for count in origin_counts_by_area.values())
    completed_jobs = 0

    for area in SCOPED_AREAS:
        weather_rows = p0056b_weather_all[area] if area == "SE3" else p0056d_weather_all[area]
        origins = dayahead_origins(targets_all[area], weather_rows, FIRST_EVAL_DELIVERY_DAY)
        modeling_origins = dayahead_origins(targets_all[area], weather_rows, FIRST_MODELING_DELIVERY_DAY)
        base_rows = build_dayahead_rows(area, targets_all[area], weather_rows, modeling_origins)
        rows_by_origin: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in base_rows:
            rows_by_origin[str(row["forecast_origin_timestamp_utc"])].append(row)
        prior_model_mae: dict[str, list[float]] = defaultdict(list)
        prior_m6_residual_by_horizon: dict[int, list[float]] = defaultdict(list)
        for origin_index, origin in enumerate(origins, start=1):
            forecast_rows_source = rows_by_origin.get(origin.origin_utc, [])
            if len(forecast_rows_source) != 24:
                failures.append({"area": area, "origin_utc": origin.origin_utc, "error": f"incomplete forecast rows {len(forecast_rows_source)}"})
                continue
            train_rows = [dict(row) for row in base_rows if EXPANDING_TRAIN_START_UTC <= str(row["target_timestamp_utc"]) < origin.origin_utc]
            if len(train_rows) < 1000:
                failures.append({"area": area, "origin_utc": origin.origin_utc, "error": f"insufficient train rows {len(train_rows)}"})
                continue
            base_predictions: dict[str, list[float]] = {}
            pending_m6_residuals: list[tuple[int, float]] = []
            for model_id in model_order:
                job_started = time.monotonic()
                progress(evidence_path, area, origin, model_id, origin_index, len(origins), "start", completed_jobs, total_jobs)
                forecast_rows = [dict(row) for row in forecast_rows_source]
                try:
                    if model_id == "M0":
                        predictions = [float(row["safe_same_hour_lag_168h"]) for row in forecast_rows]
                        training = {"model_family": "seasonal_naive", "train_rows": 0, "feature_count": 1}
                    elif model_id == "M1":
                        predictions, training = fit_predict_ridge(train_rows, forecast_rows)
                        base_predictions[model_id] = predictions
                    elif model_id in specs:
                        predictions, training = fit_predict_spec(train_rows, forecast_rows, specs[model_id])
                        base_predictions[model_id] = predictions
                    elif model_id == "M6":
                        predictions, training = weighted_ensemble_predictions(base_predictions, prior_model_mae, forecast_rows)
                    elif model_id == "M7":
                        m6_predictions = base_predictions.get("M6")
                        if m6_predictions is None:
                            m6_predictions, _ = weighted_ensemble_predictions(base_predictions, prior_model_mae, forecast_rows)
                        predictions, training = horizon_bias_corrected_predictions(m6_predictions, prior_m6_residual_by_horizon, forecast_rows)
                    else:
                        raise RuntimeError(f"unknown model_id: {model_id}")
                    result = score_origin(area, origin, model_id, forecast_rows, predictions, training, time.monotonic() - job_started)
                    origin_results.append(result)
                    if model_id in {"M1", "M2", "M3", "M4", "M5"}:
                        prior_model_mae[model_id].append(float(result["DayAhead_hourly_MAE"]))
                    if model_id == "M6":
                        pending_m6_residuals = [(int(row["horizon_h"]), float(prediction) - float(row[TARGET])) for row, prediction in zip(forecast_rows, predictions)]
                        base_predictions["M6"] = predictions
                    completed_jobs += 1
                    progress(evidence_path, area, origin, model_id, origin_index, len(origins), "done", completed_jobs, total_jobs, extra={"MAE": result["DayAhead_hourly_MAE"], "seconds": round(time.monotonic() - job_started, 3)})
                except Exception as exc:  # pragma: no cover - long-run evidence path
                    failures.append({"area": area, "origin_utc": origin.origin_utc, "model_id": model_id, "error_type": type(exc).__name__, "error": str(exc)[:600]})
                    completed_jobs += 1
                    progress(evidence_path, area, origin, model_id, origin_index, len(origins), "failed", completed_jobs, total_jobs, extra={"error_type": type(exc).__name__, "error": str(exc)[:160]})
            for horizon, residual in pending_m6_residuals:
                prior_m6_residual_by_horizon[horizon].append(residual)

    area_model_results = aggregate_area_model_results(origin_results)
    ranking = model_ranking(area_model_results)
    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": decide_status(area_model_results, failures),
        "runtime_seconds": round(time.monotonic() - started, 3),
        "feature_db": str(feature_path),
        "areas": SCOPED_AREAS,
        "model_order": model_order,
        "input_contract": input_contract,
        "weather_protocol": weather_protocol(),
        "lag_protocol": lag_protocol(),
        "model_family_contract": model_family_contract(specs, skipped_models),
        "bias_correction_contract": bias_correction_contract(),
        "forecast_taxonomy": forecast_taxonomy(),
        "dayahead_protocol": dayahead_protocol(),
        "area_model_results": area_model_results,
        "model_ranking": ranking,
        "comparison_vs_old_static": comparison_vs_old_static(area_model_results),
        "comparison_vs_rolling_tests": comparison_vs_rolling(area_model_results),
        "leakage_review": leakage_review(),
        "decision": decision(ranking),
        "what_we_learned": what_we_learned(ranking),
        "next_package_recommendation": next_package_recommendation(ranking),
        "failures": failures,
        "skipped_models": skipped_models,
        "row_counts": {
            "origin_results": len(origin_results),
            "area_model_results": len(area_model_results),
            "failures": len(failures),
            "completed_jobs": completed_jobs,
            "planned_jobs": total_jobs,
        },
        "no_api": True,
        "no_devices": True,
        "no_runtime_change": True,
        "no_production_activation": True,
        "no_spot_price_features": True,
        "no_flow_exchange_a61_capacity_features": True,
        "no_old_physical_balance_target": True,
        "no_future_actual_load_features": True,
        "no_large_artifacts": True,
    }
    evidence = write_evidence(evidence_path, summary, origin_results)
    return P0056KResult(str(summary["status"]), summary["row_counts"], evidence)  # type: ignore[arg-type]


def model_specs_for_p0056k(environment: dict[str, object]) -> dict[str, object]:
    from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor

    specs: dict[str, object] = {
        "M2": p0054k.ModelSpec("HGB", HistGradientBoostingRegressor(max_iter=120, learning_rate=0.055, max_leaf_nodes=31, min_samples_leaf=80, random_state=p0054k.RANDOM_SEED), "HistGradientBoostingRegressor", "scikit-learn", {"max_iter": 120, "learning_rate": 0.055, "max_leaf_nodes": 31, "min_samples_leaf": 80, "random_state": p0054k.RANDOM_SEED}),
        "M3": p0054k.ModelSpec("ExtraTrees", ExtraTreesRegressor(n_estimators=120, max_features=0.75, min_samples_leaf=4, max_samples=0.80, bootstrap=True, n_jobs=-1, random_state=p0054k.RANDOM_SEED), "ExtraTreesRegressor", "scikit-learn", {"n_estimators": 120, "max_features": 0.75, "min_samples_leaf": 4, "max_samples": 0.80, "bootstrap": True, "n_jobs": -1, "random_state": p0054k.RANDOM_SEED}),
    }
    imports = environment.get("imports", {}) if isinstance(environment.get("imports"), dict) else {}
    if imports.get("lightgbm", {}).get("ok"):
        from lightgbm import LGBMRegressor
        specs["M4"] = p0054k.ModelSpec("LightGBM", LGBMRegressor(objective="regression_l1", metric="mae", n_estimators=260, learning_rate=0.05, num_leaves=63, min_child_samples=80, subsample=0.85, subsample_freq=1, colsample_bytree=0.85, reg_lambda=0.2, random_state=p0054k.RANDOM_SEED, n_jobs=-1, verbose=-1), "LGBMRegressor", "lightgbm", {"n_estimators": 260, "learning_rate": 0.05, "num_leaves": 63})
    if imports.get("xgboost", {}).get("ok"):
        from xgboost import XGBRegressor
        specs["M5"] = p0054k.ModelSpec("XGBoost", XGBRegressor(objective="reg:squarederror", eval_metric="mae", n_estimators=260, learning_rate=0.05, max_depth=7, min_child_weight=8, subsample=0.85, colsample_bytree=0.85, reg_lambda=1.0, random_state=p0054k.RANDOM_SEED, n_jobs=-1, tree_method="hist"), "XGBRegressor", "xgboost", {"n_estimators": 260, "learning_rate": 0.05, "max_depth": 7, "tree_method": "hist"})
    return specs


def dayahead_origins(target_rows: list[dict[str, object]], weather_rows: dict[str, dict[str, object]], first_delivery_day: date = FIRST_EVAL_DELIVERY_DAY) -> list[Origin]:
    target_timestamps = {str(row["timestamp_utc"]) for row in target_rows}
    weather_timestamps = set(weather_rows)
    latest_target = max(p0052.parse_utc(ts) for ts in target_timestamps)
    latest_weather = max(p0052.parse_utc(ts) for ts in weather_timestamps)
    latest = min(latest_target, latest_weather)
    latest_local_day = latest.astimezone(STOCKHOLM).date()
    origins = []
    day = first_delivery_day
    while day <= latest_local_day:
        origin_local = datetime.combine(day - timedelta(days=1), dt_time(12, 0), tzinfo=STOCKHOLM)
        origin_utc = p0052.format_utc(origin_local)
        targets = delivery_day_target_utc_hours(day)
        history_targets = [p0052.format_utc(p0052.parse_utc(origin_utc) - timedelta(hours=hours)) for hours in range(1, 169)]
        seasonal_targets = [p0052.format_utc(p0052.parse_utc(target_ts) - timedelta(hours=hours)) for target_ts in targets for hours in (168, 336)]
        if all(ts in target_timestamps and ts in weather_timestamps for ts in targets) and all(ts in target_timestamps for ts in history_targets + seasonal_targets):
            origins.append(Origin(origin_local, origin_utc, day))
        day += timedelta(days=1)
    return origins


def delivery_day_target_utc_hours(day: date) -> list[str]:
    return [p0052.format_utc(datetime.combine(day, dt_time(hour, 0), tzinfo=STOCKHOLM)) for hour in range(24)]


def build_dayahead_rows(area: str, target_rows: list[dict[str, object]], weather_rows: dict[str, dict[str, object]], origins: list[Origin]) -> list[dict[str, object]]:
    target_by_ts = {str(row["timestamp_utc"]): row for row in target_rows}
    values_by_ts = {str(row["timestamp_utc"]): float(row["consumption_mw"]) for row in target_rows}
    rows = []
    for origin in origins:
        origin_dt = p0052.parse_utc(origin.origin_utc)
        history = origin_history_features(values_by_ts, origin_dt)
        for target_ts in delivery_day_target_utc_hours(origin.delivery_day):
            target_dt = p0052.parse_utc(target_ts)
            target = target_by_ts[target_ts]
            row = {
                "forecast_origin_timestamp_utc": origin.origin_utc,
                "forecast_origin_local": origin.origin_local.isoformat(),
                "delivery_day_local": origin.delivery_day.isoformat(),
                "target_timestamp_utc": target_ts,
                "horizon_h": int((target_dt - origin_dt).total_seconds() // 3600) + 1,
                TARGET: float(target["consumption_mw"]),
                "area_code": area,
                "split": "holdout" if target_ts >= "2025-06-01T00:00:00Z" else "train_fit",
                **history,
            }
            p0054k.attach_calendar_features(row, target_dt + timedelta(hours=1))
            row.update(seasonal_safe_features(values_by_ts, target_dt))
            row.update(weather_rows[target_ts])
            rows.append(row)
    return rows


def origin_history_features(values_by_ts: dict[str, float], origin_dt: datetime) -> dict[str, float]:
    def value(hours: int) -> float:
        return values_by_ts[p0052.format_utc(origin_dt - timedelta(hours=hours))]
    last24 = [value(hour) for hour in range(1, 25)]
    last168 = [value(hour) for hour in range(1, 169)]
    mean24 = p0054k.mean_float(last24)
    return {
        "origin_consumption_lag_1h": value(1),
        "origin_consumption_lag_24h": value(24),
        "origin_consumption_lag_168h": value(168),
        "origin_roll_mean_24h": mean24,
        "origin_roll_mean_168h": p0054k.mean_float(last168),
        "origin_roll_std_24h": math.sqrt(sum((item - mean24) ** 2 for item in last24) / len(last24)),
    }


def seasonal_safe_features(values_by_ts: dict[str, float], target_dt: datetime) -> dict[str, float]:
    lag168 = values_by_ts[p0052.format_utc(target_dt - timedelta(hours=168))]
    lag336 = values_by_ts[p0052.format_utc(target_dt - timedelta(hours=336))]
    return {"safe_same_hour_lag_168h": lag168, "safe_same_hour_lag_336h": lag336, "safe_same_hour_delta_168_336h": lag168 - lag336}


def fit_predict_ridge(train_rows: list[dict[str, object]], forecast_rows: list[dict[str, object]]) -> tuple[list[float], dict[str, object]]:
    from sklearn.linear_model import Ridge

    started = time.monotonic()
    x_train, encoder, names = p0054k.build_feature_matrix(train_rows, FEATURES)
    y_train = np.array([float(row[TARGET]) for row in train_rows], dtype=float)
    model = Ridge(alpha=1.0, random_state=p0054k.RANDOM_SEED)
    model.fit(x_train, y_train)
    predictions = p0054k.predict_rows(model, encoder, forecast_rows, FEATURES)
    return predictions, {"model_family": "Ridge", "train_rows": len(train_rows), "feature_count": len(names), "train_seconds": round(time.monotonic() - started, 3)}


def fit_predict_spec(train_rows: list[dict[str, object]], forecast_rows: list[dict[str, object]], spec: object) -> tuple[list[float], dict[str, object]]:
    started = time.monotonic()
    x_train, encoder, names = p0054k.build_feature_matrix(train_rows, FEATURES)
    y_train = np.array([float(row[TARGET]) for row in train_rows], dtype=float)
    model = p0054k.clone_model(spec.model)  # type: ignore[attr-defined]
    model.fit(x_train, y_train)  # type: ignore[attr-defined]
    predictions = p0054k.predict_rows(model, encoder, forecast_rows, FEATURES)
    return predictions, {"model_family": spec.family, "model_class": spec.model_class, "train_rows": len(train_rows), "feature_count": len(names), "train_seconds": round(time.monotonic() - started, 3), "hyperparameters": spec.hyperparameters}


def weighted_ensemble_predictions(base_predictions: dict[str, list[float]], prior_model_mae: dict[str, list[float]], forecast_rows: list[dict[str, object]]) -> tuple[list[float], dict[str, object]]:
    usable = {model: preds for model, preds in base_predictions.items() if model in {"M1", "M2", "M3", "M4", "M5"}}
    if not usable:
        predictions = [float(row["safe_same_hour_lag_168h"]) for row in forecast_rows]
        return predictions, {"model_family": "WeightedEnsemble", "reason": "fallback_to_M0_no_base_predictions"}
    weights = {}
    for model in usable:
        maes = prior_model_mae.get(model, [])
        weights[model] = 1.0 / max(p0054k.mean_float(maes) if maes else 1.0, 1e-6)
    total = sum(weights.values())
    predictions = []
    for index in range(len(forecast_rows)):
        predictions.append(sum(usable[model][index] * weights[model] / total for model in usable))
    return predictions, {"model_family": "WeightedEnsemble", "weights": weights, "train_rows": 0, "feature_count": len(FEATURES)}


def horizon_bias_corrected_predictions(predictions: list[float], residuals_by_horizon: dict[int, list[float]], forecast_rows: list[dict[str, object]]) -> tuple[list[float], dict[str, object]]:
    corrected = []
    biases = {}
    for row, prediction in zip(forecast_rows, predictions):
        horizon = int(row["horizon_h"])
        bias = p0054k.mean_float(residuals_by_horizon.get(horizon, [])) if residuals_by_horizon.get(horizon) else 0.0
        biases[str(horizon)] = bias
        corrected.append(float(prediction) - bias)
    return corrected, {"model_family": "HorizonBiasCorrectedWeightedEnsemble", "biases": biases, "bias_source": "prior_origins_only"}


def score_origin(area: str, origin: Origin, model_id: str, rows: list[dict[str, object]], predictions: list[float], training: dict[str, object], seconds: float) -> dict[str, object]:
    errors = [float(pred) - float(row[TARGET]) for pred, row in zip(predictions, rows)]
    abs_errors = [abs(error) for error in errors]
    actuals = [float(row[TARGET]) for row in rows]
    return {
        "area_code": area,
        "model_id": model_id,
        "forecast_origin_utc": origin.origin_utc,
        "forecast_origin_local": origin.origin_local.isoformat(),
        "delivery_day_local": origin.delivery_day.isoformat(),
        "rows": len(rows),
        "DayAhead_hourly_MAE": p0054k.mean_float(abs_errors),
        "DayAhead_RMSE": math.sqrt(p0054k.mean_float([error * error for error in errors])),
        "DayAhead_bias": p0054k.mean_float(errors),
        "MAE_percent_of_mean_actual": p0054k.mean_float(abs_errors) / p0054k.mean_float(actuals) * 100.0,
        "MAE_percent_of_median_actual": p0054k.mean_float(abs_errors) / percentile(actuals, 0.5) * 100.0,
        "absolute_daily_energy_error_MWh": abs(sum(errors)),
        "signed_daily_energy_error_MWh": sum(errors),
        "daily_energy_error_percent_of_actual": abs(sum(errors)) / sum(actuals) * 100.0,
        "p90_absolute_error": percentile(abs_errors, 0.9),
        "p95_absolute_error": percentile(abs_errors, 0.95),
        "weekday": origin.delivery_day.weekday(),
        "month": origin.delivery_day.month,
        "train_rows": training.get("train_rows"),
        "feature_count": training.get("feature_count"),
        "model_family": training.get("model_family"),
        "seconds": round(seconds, 3),
    }


def aggregate_area_model_results(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for area in SCOPED_AREAS:
        for model_id in sorted({str(row["model_id"]) for row in rows}):
            selected = [row for row in rows if row["area_code"] == area and row["model_id"] == model_id]
            if not selected:
                continue
            out.append({
                "area_code": area,
                "model_id": model_id,
                "origin_count": len(selected),
                "delivery_day_count": len(selected),
                "DayAhead_hourly_MAE": p0054k.mean_float([float(row["DayAhead_hourly_MAE"]) for row in selected]),
                "DayAhead_RMSE": p0054k.mean_float([float(row["DayAhead_RMSE"]) for row in selected]),
                "DayAhead_bias": p0054k.mean_float([float(row["DayAhead_bias"]) for row in selected]),
                "MAE_percent_of_mean_actual": p0054k.mean_float([float(row["MAE_percent_of_mean_actual"]) for row in selected]),
                "MAE_percent_of_median_actual": p0054k.mean_float([float(row["MAE_percent_of_median_actual"]) for row in selected]),
                "absolute_daily_energy_error_MWh": p0054k.mean_float([float(row["absolute_daily_energy_error_MWh"]) for row in selected]),
                "signed_daily_energy_error_MWh": p0054k.mean_float([float(row["signed_daily_energy_error_MWh"]) for row in selected]),
                "daily_energy_error_percent_of_actual": p0054k.mean_float([float(row["daily_energy_error_percent_of_actual"]) for row in selected]),
                "p90_absolute_error": p0054k.mean_float([float(row["p90_absolute_error"]) for row in selected]),
                "p95_absolute_error": p0054k.mean_float([float(row["p95_absolute_error"]) for row in selected]),
                "mean_seconds_per_origin": p0054k.mean_float([float(row["seconds"]) for row in selected]),
                "weekday_weekend_split": split_metric(selected, lambda row: "weekend" if int(row["weekday"]) >= 5 else "weekday"),
                "monthly_split": split_metric(selected, lambda row: str(row["month"])),
            })
    return out


def split_metric(rows: list[dict[str, object]], key_func: object) -> dict[str, dict[str, float | int]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[key_func(row)].append(row)  # type: ignore[operator]
    return {key: {"count": len(value), "DayAhead_hourly_MAE": p0054k.mean_float([float(row["DayAhead_hourly_MAE"]) for row in value])} for key, value in sorted(groups.items())}


def model_ranking(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for area in SCOPED_AREAS:
        selected = sorted([row for row in rows if row["area_code"] == area], key=lambda row: float(row["DayAhead_hourly_MAE"]))
        for rank, row in enumerate(selected, start=1):
            out.append({"area_code": area, "rank": rank, "model_id": row["model_id"], "DayAhead_hourly_MAE": row["DayAhead_hourly_MAE"]})
    overall = []
    for model_id in sorted({row["model_id"] for row in rows}):
        selected = [row for row in rows if row["model_id"] == model_id]
        if selected:
            overall.append({"area_code": "ALL", "rank": 0, "model_id": model_id, "DayAhead_hourly_MAE": p0054k.mean_float([float(row["DayAhead_hourly_MAE"]) for row in selected])})
    overall = sorted(overall, key=lambda row: float(row["DayAhead_hourly_MAE"]))
    for rank, row in enumerate(overall, start=1):
        row["rank"] = rank
    return out + overall


def progress(evidence_dir: Path, area: str, origin: Origin, model_id: str, origin_index: int, origin_count: int, status: str, completed: int, total: int, extra: dict[str, object] | None = None) -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload = {"timestamp_utc": now, "area": area, "model_id": model_id, "origin_utc": origin.origin_utc, "delivery_day": origin.delivery_day.isoformat(), "origin_index": origin_index, "origin_count": origin_count, "status": status, "completed_jobs": completed, "planned_jobs": total, **(extra or {})}
    line = json.dumps(payload, sort_keys=True)
    with (evidence_dir / "progress-log.md").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    append_job_status(evidence_dir, payload)
    write_status_md(evidence_dir, payload)
    if should_print_progress(status, completed, total):
        print(line, flush=True)


def should_print_progress(status: str, completed: int, total: int) -> bool:
    return status == "failed" or completed == 0 or completed == total or (status == "done" and completed % 250 == 0)


def initialize_progress(evidence_dir: Path) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    write(evidence_dir / "progress-log.md", "")
    write(evidence_dir / "job-status.csv", "")
    write(evidence_dir / "job-status.md", "# P0056K Job Status\n\nNo jobs yet.\n")
    write(evidence_dir / "checkpoint-resume.md", checkpoint_resume_md())


def append_job_status(evidence_dir: Path, payload: dict[str, object]) -> None:
    path = evidence_dir / "job-status.csv"
    exists = path.exists() and path.stat().st_size > 0
    fields = sorted(payload)
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        if not exists:
            writer.writeheader()
        writer.writerow(payload)


def write_status_md(evidence_dir: Path, payload: dict[str, object]) -> None:
    write(evidence_dir / "job-status.md", "\n".join(["# P0056K Job Status", "", f"- Last status: `{payload.get('status')}`", f"- Area: `{payload.get('area')}`", f"- Model: `{payload.get('model_id')}`", f"- Origin: `{payload.get('origin_index')}/{payload.get('origin_count')}`", f"- Completed jobs: `{payload.get('completed_jobs')}/{payload.get('planned_jobs')}`", f"- Timestamp UTC: `{payload.get('timestamp_utc')}`", ""]))


def status_report(evidence_dir: Path = EVIDENCE_DIR) -> dict[str, object]:
    status_path = evidence_dir / "job-status.md"
    progress_path = evidence_dir / "progress-log.md"
    last = ""
    if progress_path.exists() and progress_path.stat().st_size:
        with progress_path.open("r", encoding="utf-8") as handle:
            lines = [line.strip() for line in handle if line.strip()]
            last = lines[-1] if lines else ""
    return {"status_md": str(status_path), "progress_log": str(progress_path), "last_progress": json.loads(last) if last else None}


def input_source_contract(target_contract: dict[str, object], p0056b_weather_contract: dict[str, object], p0056d_weather_contract: dict[str, object]) -> dict[str, object]:
    target_areas = target_contract.get("areas", {}) if isinstance(target_contract.get("areas"), dict) else {}
    p0056b_areas = p0056b_weather_contract.get("areas", {}) if isinstance(p0056b_weather_contract.get("areas"), dict) else {}
    p0056d_areas = p0056d_weather_contract.get("areas", {}) if isinstance(p0056d_weather_contract.get("areas"), dict) else {}
    weather_ok = all((area in p0056b_areas if area == "SE3" else area in p0056d_areas) for area in SCOPED_AREAS)
    return {"ok": all(area in target_areas for area in SCOPED_AREAS) and weather_ok, "target_source": "area_consumption_hourly_v1/P0056A", "weather_source_by_area": {"SE1": "P0056D", "SE2": "P0056D", "SE3": "P0056B", "FI": "P0056D"}, "areas": SCOPED_AREAS}


def weather_protocol() -> dict[str, object]:
    return {"weather_protocol": "actual_weather_proxy_LABB", "production_weather_forecast": False}


def lag_protocol() -> dict[str, object]:
    return {"lag_protocol": "DA-L3 seasonal_safe", "future_actual_load_used": False, "features": [feature for feature in FEATURES if "lag" in feature or "origin_" in feature or "safe_same_hour" in feature]}


def model_family_contract(specs: dict[str, object], skipped: list[dict[str, object]]) -> dict[str, object]:
    return {"models": ["M0", "M1"] + sorted(specs) + ["M6", "M7"], "skipped_models": skipped}


def bias_correction_contract() -> dict[str, object]:
    return {"M7": "horizon bias correction uses prior-origin M6 residuals only; no holdout-wide hindsight correction"}


def forecast_taxonomy() -> dict[str, object]:
    return {"primary_result": "realistic_DayAhead_delivery_day_24h", "old_static_label": "old_static_not_representative_DA"}


def dayahead_protocol() -> dict[str, object]:
    return {"forecast_origin": "D-1 12:00 Europe/Stockholm", "delivery_day": "D 00:00..23:00 Europe/Stockholm", "horizon_hours": "target - origin", "train_end": "strictly before forecast_origin"}


def leakage_review() -> dict[str, object]:
    forbidden = [feature for feature in FEATURES if any(term in feature.lower() for term in ("price", "spot", "flow", "exchange", "a61", "capacity", "physical_balance", "future_actual"))]
    return {"ok": not forbidden, "forbidden_features": forbidden, "future_actual_load_feature_used": False, "spot_price_feature_used": False, "flow_exchange_a61_capacity_feature_used": False, "old_physical_balance_target_used": False}


def comparison_vs_old_static(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{"area_code": row["area_code"], "model_id": row["model_id"], "old_static_not_representative_DA_MAE": OLD_STATIC_BASELINES[row["area_code"]], "new_realistic_DA_MAE": row["DayAhead_hourly_MAE"], "delta_MW": float(row["DayAhead_hourly_MAE"]) - OLD_STATIC_BASELINES[row["area_code"]]} for row in rows]


def comparison_vs_rolling(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        for name, values in ROLLING_BASELINES.items():
            out.append({"area_code": row["area_code"], "model_id": row["model_id"], "baseline_name": name, "baseline_MAE": values[row["area_code"]], "new_realistic_DA_MAE": row["DayAhead_hourly_MAE"], "delta_MW": float(row["DayAhead_hourly_MAE"]) - values[row["area_code"]]})
    return out


def decision(ranking: list[dict[str, object]]) -> dict[str, object]:
    overall = [row for row in ranking if row["area_code"] == "ALL"]
    best = overall[0] if overall else {}
    return {"recommended_new_baseline_for_emulator_consumption_input": best.get("model_id"), "reason": "lowest mean realistic DayAhead MAE across scoped areas", "production_ready": False}


def what_we_learned(ranking: list[dict[str, object]]) -> dict[str, object]:
    return {"old_static_representative_DA": False, "realistic_DA_baseline_created": bool(ranking), "DA_L2_recursive_deferred": True}


def next_package_recommendation(ranking: list[dict[str, object]]) -> str:
    best = next((row for row in ranking if row["area_code"] == "ALL" and row["rank"] == 1), {})
    return f"P0056L: test DA-L2 recursive lag protocol against P0056K best model `{best.get('model_id')}`."


def decide_status(rows: list[dict[str, object]], failures: list[dict[str, object]]) -> str:
    areas = {row["area_code"] for row in rows}
    models = {row["model_id"] for row in rows}
    if set(SCOPED_AREAS) - areas or len(models) < 5:
        return "STOP"
    return "WARN" if failures else "WARN"


def neural_skips() -> list[dict[str, object]]:
    return [{"model_id": "M8", "reason": "optional neural smoke test skipped by runtime scope"}, {"model_id": "M9", "reason": "optional sequence model skipped by runtime scope"}]


def stopped_summary(started: float, feature_path: Path, input_contract: dict[str, object]) -> dict[str, object]:
    return {"package_id": PACKAGE_ID, "label": LABEL, "status": "STOP", "runtime_seconds": round(time.monotonic() - started, 3), "feature_db": str(feature_path), "input_contract": input_contract, "row_counts": {}}


def write_evidence(evidence_dir: Path, summary: dict[str, object], origin_results: list[dict[str, object]] | None = None) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog_md(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", "# P0056K LABB Label\n\nP0056K is LABB-only realistic DayAhead model comparison. It is not G2-KANDIDAT or production activation.\n"),
        "forecast-taxonomy.md": write(evidence_dir / "forecast-taxonomy.md", json_report("P0056K Forecast Taxonomy", summary.get("forecast_taxonomy", {}))),
        "dayahead-protocol.md": write(evidence_dir / "dayahead-protocol.md", json_report("P0056K DayAhead Protocol", summary.get("dayahead_protocol", {}))),
        "input-source-contract.md": write(evidence_dir / "input-source-contract.md", json_report("P0056K Input Source Contract", summary.get("input_contract", {}))),
        "weather-protocol.md": write(evidence_dir / "weather-protocol.md", json_report("P0056K Weather Protocol", summary.get("weather_protocol", {}))),
        "lag-protocol.md": write(evidence_dir / "lag-protocol.md", json_report("P0056K Lag Protocol", summary.get("lag_protocol", {}))),
        "model-family-contract.md": write(evidence_dir / "model-family-contract.md", json_report("P0056K Model Family Contract", summary.get("model_family_contract", {}))),
        "bias-correction-contract.md": write(evidence_dir / "bias-correction-contract.md", json_report("P0056K Bias Correction Contract", summary.get("bias_correction_contract", {}))),
        "area-model-results.md": write(evidence_dir / "area-model-results.md", table_md("P0056K Area Model Results", summary.get("area_model_results", []))),
        "model-ranking.md": write(evidence_dir / "model-ranking.md", table_md("P0056K Model Ranking", summary.get("model_ranking", []))),
        "comparison-vs-old-static.md": write(evidence_dir / "comparison-vs-old-static.md", table_md("P0056K Comparison Vs Old Static", summary.get("comparison_vs_old_static", []))),
        "comparison-vs-rolling-tests.md": write(evidence_dir / "comparison-vs-rolling-tests.md", table_md("P0056K Comparison Vs Rolling Tests", summary.get("comparison_vs_rolling_tests", []))),
        "leakage-review.md": write(evidence_dir / "leakage-review.md", json_report("P0056K Leakage Review", summary.get("leakage_review", {}))),
        "decision.md": write(evidence_dir / "decision.md", json_report("P0056K Decision", summary.get("decision", {}))),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", json_report("P0056K What We Learned", summary.get("what_we_learned", {}))),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", f"# P0056K Next Package Recommendation\n\n{summary.get('next_package_recommendation')}\n"),
        "area-model-results.csv": write_csv(evidence_dir / "area-model-results.csv", summary.get("area_model_results", [])),
        "model-ranking.csv": write_csv(evidence_dir / "model-ranking.csv", summary.get("model_ranking", [])),
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(p0056c.json_safe(compact_summary(summary)), indent=2, sort_keys=True) + "\n"),
    }
    return evidence


def changelog_md(summary: dict[str, object]) -> str:
    rows = summary.get("row_counts", {})
    return "\n".join(["# P0056K Changelog", "", f"- Status: `{summary.get('status')}`", f"- Completed jobs: `{rows.get('completed_jobs') if isinstance(rows, dict) else None}/{rows.get('planned_jobs') if isinstance(rows, dict) else None}`", f"- Area/model rows: `{rows.get('area_model_results') if isinstance(rows, dict) else None}`", "- No API, devices, runtime changes, production activation, spot price, flow/exchange/A61/capacity or old physical_balance features.", ""])


def checkpoint_resume_md() -> str:
    return "\n".join(["# P0056K Checkpoint Resume", "", "- Run command: `PYTHONPYCACHEPREFIX=/private/tmp/p0056k-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0056k run`", "- Poll command: `PYTHONPYCACHEPREFIX=/private/tmp/p0056k-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0056k status`", "- Progress log: `requirements/package-runs/P0056K/progress-log.md`", ""])


def compact_summary(summary: dict[str, object]) -> dict[str, object]:
    return {key: summary.get(key) for key in ("package_id", "status", "runtime_seconds", "row_counts", "area_model_results", "model_ranking", "decision", "leakage_review", "failures", "skipped_models")}


def table_md(title: str, rows: object) -> str:
    values = rows if isinstance(rows, list) else []
    if not values:
        return f"# {title}\n\nNo rows.\n"
    keys = sorted({key for row in values if isinstance(row, dict) for key in row if not isinstance(row.get(key), (dict, list))})
    lines = [f"# {title}", "", "| " + " | ".join(keys) + " |", "| " + " | ".join("---" for _ in keys) + " |"]
    for row in values:
        lines.append("| " + " | ".join(str(row.get(key, "")) for key in keys) + " |")
    lines.append("")
    return "\n".join(lines)


def json_report(title: str, value: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(p0056c.json_safe(value), indent=2, sort_keys=True)}\n```\n"


def write_csv(path: Path, rows: object) -> str:
    values = rows if isinstance(rows, list) else []
    if not values:
        return write(path, "")
    keys = sorted({key for row in values if isinstance(row, dict) for key in row if not isinstance(row.get(key), (dict, list))})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        for row in values:
            writer.writerow({key: row.get(key) for key in keys})
    return str(path)


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "run"
    if command == "status":
        print(json.dumps(status_report(), indent=2, sort_keys=True))
        return
    result = run_p0056k_realistic_dayahead_restart()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
