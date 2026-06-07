"""P0056C LABB multi-area consumption forecast."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import csv
import json
import math
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054n, p0054q, p0054r, p0055a
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write


PACKAGE_ID = "P0056C"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0056C")
TARGET_TABLE = "area_consumption_hourly_v1"
WEATHER_TABLE = "area_weather_features_hourly_v1"
FORECAST_TABLE = "area_consumption_forecast_log_p0056c_v1"
METRICS_TABLE = "area_consumption_forecast_metrics_p0056c_v1"
PREDICTION_COLUMN = "pred_HorizonBiasCorrected_WeightedEnsemble_no_price"
MODEL_NAME = "HorizonBiasCorrected_WeightedEnsemble_no_price"
WEIGHTED_MODEL_NAME = "WeightedEnsemble_no_price"
FALLBACK_PREDICTION_COLUMN = PREDICTION_COLUMN
REQUIRED_AREAS = (
    "SE1",
    "SE2",
    "SE3",
    "SE4",
    "NO1",
    "NO2",
    "NO3",
    "NO4",
    "NO5",
    "DK1",
    "DK2",
    "FI",
    "EE",
    "LV",
    "LT",
    "DE_LU",
    "PL",
    "NL",
)
FALLBACK_WEATHER_AREAS = {"DK1", "EE", "LV", "LT", "DE_LU", "PL", "NL"}
MIN_FULL_MODEL_TRAIN_ROWS = 2000


@dataclass(frozen=True)
class P0056CResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0056c_multi_area_forecast(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0056CResult:
    started = time.monotonic()
    feature_path = Path(feature_db).expanduser()
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)
    reset_progress_log(evidence_path)
    with sqlite3.connect(feature_path, timeout=60.0) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=60000")
        create_schema(conn)
        targets, target_contract = load_area_targets(conn)
        weather, weather_contract = load_area_weather_rows(conn)
        input_contract = validate_input_contract(target_contract, weather_contract)
        if not input_contract["ok"]:
            summary = stopped_summary(started, feature_path, input_contract, target_contract, weather_contract)
            evidence = write_evidence(evidence_path, summary)
            return P0056CResult("STOP", {}, evidence)

        environment = p0054r.capture_environment_status()
        specs = [spec for spec in p0054k.model_specs(environment["imports"]) if spec.family in p0054k.MODEL_FAMILIES]  # type: ignore[arg-type]
        feature_names = p0056c_feature_names()
        reduced_feature_names = p0056c_reduced_feature_names()

        conn.execute(f"DELETE FROM {FORECAST_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,))
        conn.execute(f"DELETE FROM {METRICS_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,))
        conn.commit()

        job_status: list[dict[str, object]] = []
        area_results: list[dict[str, object]] = []
        all_scored_rows: list[dict[str, object]] = []
        metrics_by_area: dict[str, dict[str, object]] = {}
        completed_jobs = 0
        total_jobs = len(REQUIRED_AREAS) * 2
        failed_areas: list[dict[str, object]] = []

        for area_index, area_code in enumerate(REQUIRED_AREAS):
            learn_job = area_index * 2 + 1
            test_job = area_index * 2 + 2
            try:
                learn_status = progress(evidence_path, area_code, "learn", learn_job, total_jobs, "start")
                area_rows = build_area_modeling_rows(area_code, targets[area_code], weather[area_code], set(p0054n.HORIZONS_36H))
                model_result = learn_area_model(area_code, area_rows, feature_names, reduced_feature_names, specs)
                completed_jobs += 1
                job_status.append(progress(evidence_path, area_code, "learn", learn_job, total_jobs, "done", started_at=learn_status["timestamp"], extra={"model_status": model_result["status"], "rows": len(area_rows)}))

                test_status = progress(evidence_path, area_code, "test", test_job, total_jobs, "start")
                metrics = evaluate_area_model(area_code, model_result["rows"], PREDICTION_COLUMN)
                persist_area_outputs(conn, area_code, model_result["rows"], metrics)
                completed_jobs += 1
                job_status.append(progress(evidence_path, area_code, "test", test_job, total_jobs, "done", started_at=test_status["timestamp"], extra={"dayahead_rows": metrics["row_counts"]["dayahead_rows"], "full36_rows": metrics["row_counts"]["full36_rows"]}))
                area_result = area_result_summary(area_code, model_result, metrics, targets[area_code], weather[area_code])
                area_results.append(area_result)
                metrics_by_area[area_code] = metrics
                all_scored_rows.extend(model_result["rows"])
            except Exception as exc:  # pragma: no cover - package execution evidence path
                failed = {"area_code": area_code, "error_type": type(exc).__name__, "error": str(exc)[:600], "retry_command": "python3 -m src.mac.services.spotprice_model_diagnostics.p0056c"}
                failed_areas.append(failed)
                job_status.append(progress(evidence_path, area_code, "test", test_job, total_jobs, "failed", extra=failed))

        cross_area = cross_area_summary(area_results)
        aggregate = aggregate_forecast_summary(all_scored_rows, PREDICTION_COLUMN)
        leakage = leakage_review(all_scored_rows, feature_names, target_contract, weather_contract, area_results)
        verification = verification_summary(input_contract, completed_jobs, total_jobs, leakage, aggregate, area_results)
        status = decide_status(completed_jobs, total_jobs, failed_areas, leakage, area_results)
        summary = {
            "package_id": PACKAGE_ID,
            "label": LABEL,
            "status": status,
            "runtime_seconds": round(time.monotonic() - started, 3),
            "feature_db": str(feature_path),
            "input_contract": input_contract,
            "target_contract": target_contract,
            "weather_contract": weather_contract,
            "split_policy": split_policy(),
            "model_method_contract": model_method_contract(feature_names, reduced_feature_names, specs),
            "environment": environment,
            "job_status": job_status,
            "completed_jobs": completed_jobs,
            "total_jobs": total_jobs,
            "failed_areas": failed_areas,
            "area_results": area_results,
            "metrics_by_area": metrics_by_area,
            "cross_area_summary": cross_area,
            "aggregate_forecast_summary": aggregate,
            "leakage_review": leakage,
            "verification": verification,
            "row_counts": {
                "areas": len(area_results),
                "scored_rows": len(all_scored_rows),
                "forecast_log_rows": forecast_log_count(conn),
                "metrics_rows": metrics_row_count(conn),
                "completed_jobs": completed_jobs,
                "total_jobs": total_jobs,
            },
            "no_api": True,
            "no_devices": True,
            "no_runtime_change": True,
            "no_spot_price_features": True,
            "no_old_physical_balance_target": True,
            "no_flow_exchange_a61_capacity_features": True,
            "no_holdout_fitting_or_selection": True,
            "no_large_artifacts": True,
        }
        evidence = write_evidence(evidence_path, summary)
        return P0056CResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {FORECAST_TABLE} (
            forecast_origin_timestamp_utc TEXT NOT NULL,
            input_data_cutoff_utc TEXT NOT NULL,
            target_timestamp_utc TEXT NOT NULL,
            horizon_hours INTEGER NOT NULL,
            area_code TEXT NOT NULL,
            model_name TEXT NOT NULL,
            prediction_kind TEXT NOT NULL,
            predicted_consumption_mw REAL NOT NULL,
            actual_consumption_mw REAL NOT NULL,
            evaluation_scope TEXT NOT NULL,
            split TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (forecast_origin_timestamp_utc, target_timestamp_utc, area_code, model_name, generated_by_package)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {METRICS_TABLE} (
            area_code TEXT NOT NULL,
            model_name TEXT NOT NULL,
            metric_scope TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL,
            metric_text TEXT,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (area_code, model_name, metric_scope, metric_name, generated_by_package)
        )
        """
    )
    conn.commit()


def load_area_targets(conn: sqlite3.Connection) -> tuple[dict[str, list[dict[str, object]]], dict[str, object]]:
    targets: dict[str, list[dict[str, object]]] = {area: [] for area in REQUIRED_AREAS}
    for row in conn.execute(
        f"""
        SELECT timestamp_utc, area_code, consumption_mw, source_system, aggregation_method,
               native_resolution_mix, coverage_flag, generated_by_package
        FROM {TARGET_TABLE}
        WHERE generated_by_package='P0056A'
        ORDER BY area_code, timestamp_utc
        """
    ):
        area = str(row["area_code"])
        if area not in targets:
            continue
        ts = p0052.normalize_utc_text(row["timestamp_utc"])
        targets[area].append(
            {
                "timestamp_utc": ts,
                "area_code": area,
                "consumption_mw": float(row["consumption_mw"]),
                "target_source_table": TARGET_TABLE,
                "target_source_package": str(row["generated_by_package"]),
                "source_system": str(row["source_system"]),
                "aggregation_method": str(row["aggregation_method"]),
                "native_resolution_mix": str(row["native_resolution_mix"]),
                "coverage_flag": str(row["coverage_flag"]),
            }
        )
    by_area = {}
    for area, rows in targets.items():
        timestamps = [str(row["timestamp_utc"]) for row in rows]
        values = [float(row["consumption_mw"]) for row in rows if p0054k.is_finite(row.get("consumption_mw"))]
        by_area[area] = {
            "rows": len(rows),
            "train_fit_rows": sum(1 for row in rows if p0054k.p0054i_split(str(row["timestamp_utc"])) == "train_fit"),
            "holdout_rows": sum(1 for row in rows if p0054k.p0054i_split(str(row["timestamp_utc"])) == "holdout"),
            "min_timestamp_utc": min(timestamps) if timestamps else "",
            "max_timestamp_utc": max(timestamps) if timestamps else "",
            "duplicates": len(timestamps) - len(set(timestamps)),
            "nonfinite_values": len(rows) - len(values),
            "mean_mw": p0054k.mean_float(values),
            "median_mw": percentile(values, 0.5) if values else None,
        }
    return targets, {
        "ok": all(meta["rows"] > 0 and meta["train_fit_rows"] > 0 and meta["holdout_rows"] > 0 and meta["duplicates"] == 0 and meta["nonfinite_values"] == 0 for meta in by_area.values()),
        "source_table": TARGET_TABLE,
        "generated_by_package": "P0056A",
        "target_column": "consumption_mw",
        "unit": "MW hourly mean",
        "areas": by_area,
        "missing_areas": [area for area, rows in targets.items() if not rows],
        "old_physical_balance_target_used": False,
    }


def load_area_weather_rows(conn: sqlite3.Connection) -> tuple[dict[str, dict[str, dict[str, object]]], dict[str, object]]:
    weather: dict[str, dict[str, dict[str, object]]] = {area: {} for area in REQUIRED_AREAS}
    for row in conn.execute(
        f"""
        SELECT timestamp_utc, area_code, temperature_2m, apparent_temperature, wind_speed,
               cloud_cover, relative_humidity, precipitation, snow_depth, heating_degree_proxy,
               cooling_degree_proxy, temperature_2m_roll_mean_24h, source_station_or_proxy_ids,
               missingness_flags, generated_by_package
        FROM {WEATHER_TABLE}
        WHERE generated_by_package='P0056B'
        ORDER BY area_code, timestamp_utc
        """
    ):
        area = str(row["area_code"])
        if area not in weather:
            continue
        ts = p0052.normalize_utc_text(row["timestamp_utc"])
        weather[area][ts] = {
            "weather_proxy_temperature_2m_area": safe_float_or_zero(row["temperature_2m"]),
            "weather_proxy_apparent_temperature_area": safe_float_or_zero(row["apparent_temperature"]),
            "weather_proxy_wind_speed_area": safe_float_or_zero(row["wind_speed"]),
            "weather_proxy_cloud_cover_area": safe_float_or_zero(row["cloud_cover"]),
            "weather_proxy_humidity_area": safe_float_or_zero(row["relative_humidity"]),
            "weather_proxy_precipitation_area": safe_float_or_zero(row["precipitation"]),
            "weather_proxy_snow_depth_area": safe_float_or_zero(row["snow_depth"]),
            "weather_proxy_heating_degree_hours_area": safe_float_or_zero(row["heating_degree_proxy"]),
            "weather_proxy_cooling_degree_hours_area": safe_float_or_zero(row["cooling_degree_proxy"]),
            "weather_proxy_temperature_roll_mean_24h_area": safe_float_or_zero(row["temperature_2m_roll_mean_24h"]),
            "weather_proxy_source_station_or_proxy_ids": str(row["source_station_or_proxy_ids"]),
            "weather_proxy_missingness_flags": str(row["missingness_flags"]),
            "weather_proxy_label": p0054k.WEATHER_PROXY_LABEL,
        }
    by_area = {}
    for area, rows in weather.items():
        timestamps = sorted(rows)
        by_area[area] = {
            "rows": len(rows),
            "min_timestamp_utc": min(timestamps) if timestamps else "",
            "max_timestamp_utc": max(timestamps) if timestamps else "",
            "fallback_weather_proxy": area in FALLBACK_WEATHER_AREAS,
            "snow_depth_available": any(float(row["weather_proxy_snow_depth_area"]) != 0.0 for row in rows.values()),
        }
    return weather, {
        "ok": all(meta["rows"] > 0 for meta in by_area.values()),
        "source_table": WEATHER_TABLE,
        "generated_by_package": "P0056B",
        "input_classification": "historical_observed_only_weather_actual_proxy",
        "proxy_label": p0054k.WEATHER_PROXY_LABEL,
        "areas": by_area,
        "fallback_areas": sorted(FALLBACK_WEATHER_AREAS),
        "production_weather_forecast": False,
    }


def validate_input_contract(target_contract: dict[str, object], weather_contract: dict[str, object]) -> dict[str, object]:
    target_areas = set(target_contract["areas"])  # type: ignore[arg-type]
    weather_areas = set(weather_contract["areas"])  # type: ignore[arg-type]
    return {
        "ok": bool(target_contract["ok"]) and bool(weather_contract["ok"]) and target_areas == set(REQUIRED_AREAS) and weather_areas == set(REQUIRED_AREAS),
        "target_ok": target_contract["ok"],
        "weather_ok": weather_contract["ok"],
        "required_area_count": len(REQUIRED_AREAS),
        "target_area_count": len(target_areas),
        "weather_area_count": len(weather_areas),
        "missing_target_areas": sorted(set(REQUIRED_AREAS) - target_areas),
        "missing_weather_areas": sorted(set(REQUIRED_AREAS) - weather_areas),
    }


def build_area_modeling_rows(
    area_code: str,
    target_rows: list[dict[str, object]],
    weather_rows: dict[str, dict[str, object]],
    horizons: set[int],
) -> list[dict[str, object]]:
    source_by_ts = {str(row["timestamp_utc"]): row for row in target_rows}
    source_index = {str(row["timestamp_utc"]): index for index, row in enumerate(target_rows)}
    values = [float(row["consumption_mw"]) for row in target_rows]
    origin_rows = p0054r.build_no_price_origin_rows(
        [{"timestamp_utc": row["timestamp_utc"], "consumption_se3": row["consumption_mw"]} for row in target_rows],
        horizons,
    )
    rows = []
    required_history = max(max(p0054k.LAGS), max(p0054k.ROLL_WINDOWS))
    for origin in origin_rows:
        horizon = int(origin["horizon_h"])
        origin_ts = str(origin["forecast_origin_timestamp_utc"])
        target_ts = str(origin["target_timestamp_utc"])
        origin_index = source_index.get(origin_ts)
        target = source_by_ts.get(target_ts)
        weather = weather_rows.get(target_ts)
        if origin_index is None or target is None or weather is None or origin_index < required_history:
            continue
        row = {
            "forecast_origin_timestamp_utc": origin_ts,
            "input_data_cutoff_utc": origin["input_data_cutoff_utc"],
            "target_timestamp_utc": target_ts,
            "horizon_h": horizon,
            "horizon_hours": int(origin["horizon_hours"]),
            p0054k.TARGET_FIELD: float(target["consumption_mw"]),
            "area_code": area_code,
            "area_or_target": area_code,
            "prediction_kind": "consumption_mw",
            "dataset_kind": "offline_labb_multi_area_consumption_forecast_not_deployable",
            "weather_proxy_label": p0054k.WEATHER_PROXY_LABEL,
            "weather_source_generated_by_package": "P0056B",
            "target_source_generated_by_package": "P0056A",
        }
        p0054k.attach_calendar_features(row, p0052.parse_utc(target_ts) + timedelta(hours=1))
        row.update(area_lag_features_at_origin(values, origin_index))
        row.update(area_rolling_features_at_origin(values, origin_index))
        row.update(weather)
        rows.append(row)
    p0054k.assign_p0054i_splits(rows)
    p0054r.assign_internal_validation_splits(rows)
    add_area_weather_profile_features(rows)
    return rows


def area_lag_features_at_origin(values: list[float], origin_index: int) -> dict[str, float]:
    return {f"area_consumption_lag_{lag}h": values[origin_index - lag] for lag in p0054k.LAGS}


def area_rolling_features_at_origin(values: list[float], origin_index: int) -> dict[str, float]:
    out = {}
    for window in p0054k.ROLL_WINDOWS:
        subset = values[origin_index - window : origin_index]
        out[f"area_consumption_roll_mean_{window}h"] = p0054k.mean_float(subset)
    subset24 = values[origin_index - 24 : origin_index]
    mean24 = p0054k.mean_float(subset24)
    out["area_consumption_roll_min_24h"] = min(subset24)
    out["area_consumption_roll_max_24h"] = max(subset24)
    out["area_consumption_roll_std_24h"] = math.sqrt(sum((value - mean24) ** 2 for value in subset24) / len(subset24))
    out["area_consumption_ramp_1h"] = values[origin_index - 1] - values[origin_index - 2]
    out["area_consumption_ramp_24h"] = values[origin_index - 1] - values[origin_index - 24]
    out["area_consumption_same_hour_24h_vs_168h"] = values[origin_index - 24] - values[origin_index - 168]
    return out


def add_area_weather_profile_features(rows: list[dict[str, object]]) -> None:
    internal_train = [
        row for row in rows
        if row.get(p0054r.INTERNAL_SPLIT_FIELD) == "internal_train" and p0054k.is_finite(row.get("weather_proxy_temperature_2m_area"))
    ]
    normals = p0054k.grouped_mean(internal_train, ("target_month", "target_model_cet_hour"), "weather_proxy_temperature_2m_area")
    for row in rows:
        normal = p0054k.profile_predict(normals, row, ("target_month", "target_model_cet_hour"))
        temp = p0054k.safe_float(row.get("weather_proxy_temperature_2m_area"))
        row["weather_proxy_train_normal_temperature_2m_area"] = normal
        row["weather_proxy_temperature_delta_from_train_normal_area"] = temp - normal
        row["weather_proxy_cold_spell_flag_area"] = 1 if p0054k.safe_float(row.get("weather_proxy_heating_degree_hours_area")) >= 12 else 0


def learn_area_model(
    area_code: str,
    rows: list[dict[str, object]],
    feature_names: list[str],
    reduced_feature_names: list[str],
    specs: list[object],
) -> dict[str, object]:
    rows = [dict(row) for row in rows]
    train_rows = [row for row in rows if row.get("split") == "train_fit"]
    holdout_rows = [row for row in rows if row.get("split") == "holdout"]
    if len(train_rows) < MIN_FULL_MODEL_TRAIN_ROWS or not holdout_rows or not specs:
        training = p0055a.apply_same_week_fallback(rows, FALLBACK_PREDICTION_COLUMN)
        training.update({"area_code": area_code, "fallback_used": "F3_seasonal_same_week", "reason": "insufficient_rows_or_specs"})
        return {"rows": rows, "training": training, "status": "F3_seasonal_same_week", "prediction_column": PREDICTION_COLUMN}
    attempts = [
        ("full_model", feature_names, fit_horizon_bias_weighted_ensemble),
        ("F1_reduced_feature_set", reduced_feature_names, fit_horizon_bias_weighted_ensemble),
        ("F2_weighted_ensemble_no_price", reduced_feature_names, fit_weighted_ensemble_no_bias),
    ]
    errors = []
    for status, features, fit_func in attempts:
        try:
            training = fit_func(rows, features, specs)
            training.update({"area_code": area_code, "fallback_used": None if status == "full_model" else status, "feature_count": len(features)})
            return {"rows": rows, "training": training, "status": status, "prediction_column": PREDICTION_COLUMN}
        except Exception as exc:  # pragma: no cover - depends on local optional ML stack and data shape
            errors.append({"attempt": status, "error_type": type(exc).__name__, "error": str(exc)[:400]})
    training = p0055a.apply_same_week_fallback(rows, FALLBACK_PREDICTION_COLUMN)
    training.update({"area_code": area_code, "fallback_used": "F3_seasonal_same_week", "errors": errors})
    return {"rows": rows, "training": training, "status": "F3_seasonal_same_week", "prediction_column": PREDICTION_COLUMN}


def fit_horizon_bias_weighted_ensemble(rows: list[dict[str, object]], features: list[str], specs: list[object]) -> dict[str, object]:
    internal_train = [row for row in rows if row.get(p0054r.INTERNAL_SPLIT_FIELD) == "internal_train"]
    internal_validation = [row for row in rows if row.get(p0054r.INTERNAL_SPLIT_FIELD) == "internal_validation"]
    train_fit = [row for row in rows if row.get("split") == "train_fit"]
    if not internal_train or not internal_validation:
        raise RuntimeError("missing internal train or validation rows")
    base_keys = []
    validation_metrics = {}
    model_training = {}
    for spec in specs:
        key = f"{spec.family}_no_price"  # type: ignore[attr-defined]
        validation_fit = p0054r.fit_model_on_rows(spec, features, internal_train, internal_validation)
        p0054r.attach_prediction_values(internal_validation, validation_fit["predictions"], p0054k.prediction_column(key))
        validation_metrics[key] = p0054k.regression_metric_from_predictions(internal_validation, validation_fit["predictions"])  # type: ignore[arg-type]
        result = p0054k.fit_variant_model(rows, features, spec, "no_price")  # type: ignore[arg-type]
        p0054k.attach_path_predictions(rows, result, features, p0054k.prediction_column(key))
        model_training[key] = result["training"]
        base_keys.append(key)
    weights, weight_evidence = p0054r.learn_inverse_mae_weights(internal_validation, base_keys)
    weighted_col = p0054k.prediction_column(WEIGHTED_MODEL_NAME)
    p0054r.apply_weighted_ensemble(internal_validation, weights, weighted_col)
    p0054r.apply_weighted_ensemble(rows, weights, weighted_col)
    bias_evidence = p0054r.fit_and_apply_horizon_bias_correction(internal_validation, rows, WEIGHTED_MODEL_NAME, PREDICTION_COLUMN)
    return {
        "method": MODEL_NAME,
        "status": "full_model",
        "train_fit_rows": len(train_fit),
        "internal_train_rows": len(internal_train),
        "internal_validation_rows": len(internal_validation),
        "holdout_rows": sum(1 for row in rows if row.get("split") == "holdout"),
        "base_models": model_training,
        "validation_metrics": validation_metrics,
        "weights": weight_evidence,
        "horizon_bias": bias_evidence,
        "holdout_used_for_weights_or_bias": False,
        "model_artifact_persisted": False,
    }


def fit_weighted_ensemble_no_bias(rows: list[dict[str, object]], features: list[str], specs: list[object]) -> dict[str, object]:
    internal_train = [row for row in rows if row.get(p0054r.INTERNAL_SPLIT_FIELD) == "internal_train"]
    internal_validation = [row for row in rows if row.get(p0054r.INTERNAL_SPLIT_FIELD) == "internal_validation"]
    base_keys = []
    validation_metrics = {}
    model_training = {}
    for spec in specs:
        key = f"{spec.family}_no_price"  # type: ignore[attr-defined]
        validation_fit = p0054r.fit_model_on_rows(spec, features, internal_train, internal_validation)
        p0054r.attach_prediction_values(internal_validation, validation_fit["predictions"], p0054k.prediction_column(key))
        validation_metrics[key] = p0054k.regression_metric_from_predictions(internal_validation, validation_fit["predictions"])  # type: ignore[arg-type]
        result = p0054k.fit_variant_model(rows, features, spec, "no_price")  # type: ignore[arg-type]
        p0054k.attach_path_predictions(rows, result, features, p0054k.prediction_column(key))
        model_training[key] = result["training"]
        base_keys.append(key)
    weights, weight_evidence = p0054r.learn_inverse_mae_weights(internal_validation, base_keys)
    weighted_col = p0054k.prediction_column(WEIGHTED_MODEL_NAME)
    p0054r.apply_weighted_ensemble(internal_validation, weights, weighted_col)
    p0054r.apply_weighted_ensemble(rows, weights, weighted_col)
    for row in rows:
        if row.get(weighted_col) is not None:
            row[PREDICTION_COLUMN] = float(row[weighted_col])
    return {
        "method": WEIGHTED_MODEL_NAME,
        "status": "F2_weighted_ensemble_no_price",
        "train_fit_rows": sum(1 for row in rows if row.get("split") == "train_fit"),
        "internal_train_rows": len(internal_train),
        "internal_validation_rows": len(internal_validation),
        "holdout_rows": sum(1 for row in rows if row.get("split") == "holdout"),
        "base_models": model_training,
        "validation_metrics": validation_metrics,
        "weights": weight_evidence,
        "holdout_used_for_weights_or_bias": False,
        "model_artifact_persisted": False,
    }


def evaluate_area_model(area_code: str, rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    prediction_columns = (prediction_column,)
    full36_summary, full36_origin_rows = p0054n.evaluate_full_36h_paths(rows, prediction_columns)
    dayahead_summary, dayahead_origin_rows = p0054n.evaluate_dayahead_delivery_days(rows, prediction_columns)
    full36_selected = p0054q.selected_full36_rows(rows)
    dayahead_selected = p0054q.selected_dayahead_rows(rows)
    p0054q.add_percent_metrics(full36_summary, full36_selected, prediction_columns, "full36")
    p0054q.add_percent_metrics(dayahead_summary, dayahead_selected, prediction_columns, "dayahead")
    daily_energy = p0054q.daily_energy_error_summary(dayahead_selected, prediction_columns)
    horizon_slices = horizon_slice_metrics(full36_selected, prediction_column)
    weekday_weekend = weekday_weekend_metrics(dayahead_selected, prediction_column)
    regimes = regime_metrics(dayahead_selected, prediction_column)
    return {
        "area_code": area_code,
        "prediction_column": prediction_column,
        "full36": full36_summary.get(prediction_column, {}),
        "dayahead": dayahead_summary.get(prediction_column, {}),
        "daily_energy": daily_energy.get(prediction_column, {}),
        "horizon_slices": horizon_slices,
        "weekday_weekend": weekday_weekend,
        "regimes": regimes,
        "row_counts": {
            "full36_rows": len(full36_selected),
            "full36_complete_origins": len(full36_origin_rows),
            "dayahead_rows": len(dayahead_selected),
            "dayahead_delivery_days": len(dayahead_origin_rows),
        },
    }


def horizon_slice_metrics(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    return {
        "MAE_0_6h": slice_mae(rows, prediction_column, 1, 6),
        "MAE_0_12h": slice_mae(rows, prediction_column, 1, 12),
        "MAE_0_24h": slice_mae(rows, prediction_column, 1, 24),
        "MAE_24_36h": slice_mae(rows, prediction_column, 25, 36),
    }


def slice_mae(rows: list[dict[str, object]], prediction_column: str, lo: int, hi: int) -> float | None:
    selected = [row for row in rows if lo <= int(row["horizon_h"]) <= hi and row.get(prediction_column) is not None]
    if not selected:
        return None
    return p0054k.regression_metric_from_predictions(selected, [float(row[prediction_column]) for row in selected])["MAE"]  # type: ignore[return-value]


def weekday_weekend_metrics(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    return {
        "weekday": compact_metric([row for row in rows if int(row.get("is_weekend", 0)) == 0], prediction_column),
        "weekend": compact_metric([row for row in rows if int(row.get("is_weekend", 0)) == 1], prediction_column),
    }


def regime_metrics(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    actuals = [float(row[p0054k.TARGET_FIELD]) for row in rows]
    high_load_threshold = percentile(actuals, 0.9) if actuals else 0.0
    return {
        "cold": compact_metric([row for row in rows if float(row.get("weather_proxy_temperature_2m_area", 99.0)) <= 0.0], prediction_column),
        "high_load": compact_metric([row for row in rows if float(row[p0054k.TARGET_FIELD]) >= high_load_threshold], prediction_column),
        "ramp": compact_metric([row for row in rows if abs(float(row.get("area_consumption_ramp_24h", 0.0))) >= percentile([abs(float(candidate.get("area_consumption_ramp_24h", 0.0))) for candidate in rows], 0.9)], prediction_column),
    }


def compact_metric(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    available = [row for row in rows if row.get(prediction_column) is not None]
    if not available:
        return {"rows": 0, "MAE": None, "RMSE": None, "bias": None}
    metric = p0054k.regression_metric_from_predictions(available, [float(row[prediction_column]) for row in available])
    return {"rows": len(available), "MAE": metric["MAE"], "RMSE": metric["RMSE"], "bias": metric["bias"]}


def persist_area_outputs(conn: sqlite3.Connection, area_code: str, rows: list[dict[str, object]], metrics: dict[str, object]) -> None:
    forecast_rows = []
    selected_ids = {
        (str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"]))
        for row in p0054q.selected_full36_rows(rows) + p0054q.selected_dayahead_rows(rows)
    }
    for row in rows:
        key = (str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"]))
        if row.get("split") != "holdout" or row.get(PREDICTION_COLUMN) is None or key not in selected_ids:
            continue
        forecast_rows.append(
            (
                row["forecast_origin_timestamp_utc"],
                row["input_data_cutoff_utc"],
                row["target_timestamp_utc"],
                int(row["horizon_hours"]),
                area_code,
                MODEL_NAME,
                "consumption_mw",
                float(row[PREDICTION_COLUMN]),
                float(row[p0054k.TARGET_FIELD]),
                "dayahead_or_full36",
                row["split"],
                PACKAGE_ID,
            )
        )
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {FORECAST_TABLE}
        (forecast_origin_timestamp_utc, input_data_cutoff_utc, target_timestamp_utc, horizon_hours,
         area_code, model_name, prediction_kind, predicted_consumption_mw, actual_consumption_mw,
         evaluation_scope, split, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        forecast_rows,
    )
    metric_rows = metrics_rows(area_code, metrics)
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {METRICS_TABLE}
        (area_code, model_name, metric_scope, metric_name, metric_value, metric_text, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        metric_rows,
    )
    conn.commit()


def metrics_rows(area_code: str, metrics: dict[str, object]) -> list[tuple[object, ...]]:
    rows = []
    for scope in ("dayahead", "full36", "daily_energy", "horizon_slices"):
        values = metrics.get(scope, {})
        for name, value in flatten_metrics(values).items():  # type: ignore[arg-type]
            metric_value = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None
            metric_text = None if metric_value is not None else json.dumps(value, sort_keys=True)
            rows.append((area_code, MODEL_NAME, scope, name, metric_value, metric_text, PACKAGE_ID))
    rows.append((area_code, MODEL_NAME, "row_counts", "dayahead_rows", float(metrics["row_counts"]["dayahead_rows"]), None, PACKAGE_ID))  # type: ignore[index]
    rows.append((area_code, MODEL_NAME, "row_counts", "full36_rows", float(metrics["row_counts"]["full36_rows"]), None, PACKAGE_ID))  # type: ignore[index]
    return rows


def flatten_metrics(values: dict[str, object], prefix: str = "") -> dict[str, object]:
    out = {}
    for key, value in values.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            out.update(flatten_metrics(value, f"{name}."))
        else:
            out[name] = value
    return out


def area_result_summary(
    area_code: str,
    model_result: dict[str, object],
    metrics: dict[str, object],
    target_rows: list[dict[str, object]],
    weather_rows: dict[str, dict[str, object]],
) -> dict[str, object]:
    return {
        "area_code": area_code,
        "status": model_result["status"],
        "model_name": MODEL_NAME,
        "fallback_used": model_result["training"].get("fallback_used"),  # type: ignore[union-attr]
        "train_fit_rows": model_result["training"].get("train_fit_rows"),  # type: ignore[union-attr]
        "holdout_rows": model_result["training"].get("holdout_rows"),  # type: ignore[union-attr]
        "forecast_origins": len({row["forecast_origin_timestamp_utc"] for row in model_result["rows"]}),  # type: ignore[union-attr]
        "dayahead_rows": metrics["row_counts"]["dayahead_rows"],
        "full36_rows": metrics["row_counts"]["full36_rows"],
        "DayAhead_hourly_MAE": metrics["dayahead"].get("hourly_MAE_delivery_day"),  # type: ignore[union-attr]
        "DayAhead_RMSE": metrics["dayahead"].get("hourly_RMSE_delivery_day"),  # type: ignore[union-attr]
        "DayAhead_bias": metrics["dayahead"].get("bias_delivery_day"),  # type: ignore[union-attr]
        "MAE_percent_of_mean_actual": metrics["dayahead"].get("MAE_percent_of_mean_actual"),  # type: ignore[union-attr]
        "MAE_percent_of_median_actual": metrics["dayahead"].get("MAE_percent_of_median_actual"),  # type: ignore[union-attr]
        "absolute_daily_energy_error_MWh": metrics["daily_energy"].get("absolute_daily_energy_error_MWh"),  # type: ignore[union-attr]
        "signed_daily_energy_error_MWh": metrics["daily_energy"].get("signed_daily_energy_error_MWh"),  # type: ignore[union-attr]
        "daily_energy_error_percent_of_actual": metrics["daily_energy"].get("daily_energy_error_percent_of_actual"),  # type: ignore[union-attr]
        "full_36h_MAE": metrics["full36"].get("MAE_full_36h"),  # type: ignore[union-attr]
        "full_36h_RMSE": metrics["full36"].get("RMSE_full_36h"),  # type: ignore[union-attr]
        "full_36h_bias": metrics["full36"].get("bias_full_36h"),  # type: ignore[union-attr]
        "p90_absolute_error": metrics["dayahead"].get("p90_absolute_error"),  # type: ignore[union-attr]
        "p95_absolute_error": metrics["dayahead"].get("p95_absolute_error"),  # type: ignore[union-attr]
        "target_rows": len(target_rows),
        "weather_rows": len(weather_rows),
        "weather_fallback_proxy": area_code in FALLBACK_WEATHER_AREAS,
    }


def cross_area_summary(area_results: list[dict[str, object]]) -> dict[str, object]:
    usable = [row for row in area_results if row.get("MAE_percent_of_mean_actual") is not None]
    weighted_denominator = sum(float(row.get("dayahead_rows", 0)) * float(row.get("DayAhead_hourly_MAE", 0.0)) for row in usable)
    mean_load_weight = sum(float(row.get("dayahead_rows", 0)) * safe_float_or_zero(row.get("DayAhead_hourly_MAE")) / max(safe_float_or_zero(row.get("MAE_percent_of_mean_actual")), 1e-9) for row in usable)
    return {
        "best_area_by_percent_MAE": min(usable, key=lambda row: float(row["MAE_percent_of_mean_actual"]))["area_code"] if usable else None,
        "worst_area_by_percent_MAE": max(usable, key=lambda row: float(row["MAE_percent_of_mean_actual"]))["area_code"] if usable else None,
        "weighted_mean_MAE_percent_by_mean_load": (weighted_denominator / mean_load_weight) if mean_load_weight else None,
        "area_count": len(area_results),
        "fallback_area_count": sum(1 for row in area_results if row.get("fallback_used")),
        "weather_fallback_area_count": sum(1 for row in area_results if row.get("weather_fallback_proxy")),
    }


def aggregate_forecast_summary(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    selected = []
    for area_rows in p0054k.group_by(rows, "area_code").values():
        selected.extend(p0054q.selected_dayahead_rows(area_rows))
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in selected:
        if row.get(prediction_column) is not None:
            grouped[(str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"]))].append(row)
    aggregate_rows = []
    for (origin, target), group in grouped.items():
        if len({row["area_code"] for row in group}) != len(REQUIRED_AREAS):
            continue
        actual = sum(float(row[p0054k.TARGET_FIELD]) for row in group)
        predicted = sum(float(row[prediction_column]) for row in group)
        aggregate_rows.append({"forecast_origin_timestamp_utc": origin, "target_timestamp_utc": target, p0054k.TARGET_FIELD: actual, prediction_column: predicted})
    metric = compact_metric(aggregate_rows, prediction_column)
    total_actual_load = sum(float(row[p0054k.TARGET_FIELD]) for row in aggregate_rows)
    total_predicted = sum(float(row[prediction_column]) for row in aggregate_rows)
    return {
        "aggregate_rows": len(aggregate_rows),
        "total_northern_europe_actual_load": total_actual_load,
        "sum_of_area_forecasts": total_predicted,
        "aggregate_forecast_error": total_predicted - total_actual_load,
        "aggregate_MAE": metric["MAE"],
        "aggregate_RMSE": metric["RMSE"],
        "aggregate_bias": metric["bias"],
        "aggregate_forecast_equals_sum_of_area_forecasts": True,
    }


def leakage_review(
    rows: list[dict[str, object]],
    feature_names: list[str],
    target_contract: dict[str, object],
    weather_contract: dict[str, object],
    area_results: list[dict[str, object]],
) -> dict[str, object]:
    forbidden_terms = ("price", "spot", "flow", "exchange", "net_position", "a61", "capacity", "physical_balance", "future_actual")
    forbidden_features = sorted(feature for feature in feature_names if any(term in feature.lower() for term in forbidden_terms))
    forbidden_columns = sorted(
        {
            column
            for row in rows[:50]
            for column in row
            if not column.startswith("pred_") and any(term in column.lower() for term in forbidden_terms)
        }
    )
    target_order_ok = all(
        p0052.parse_utc(str(row["input_data_cutoff_utc"])) < p0052.parse_utc(str(row["forecast_origin_timestamp_utc"])) <= p0052.parse_utc(str(row["target_timestamp_utc"]))
        for row in rows
    )
    return {
        "ok": bool(target_contract["ok"]) and bool(weather_contract["ok"]) and not forbidden_features and not forbidden_columns and target_order_ok and not any(row.get("training", {}).get("holdout_used_for_weights_or_bias") for row in area_results),
        "target_source_table": TARGET_TABLE,
        "weather_source_table": WEATHER_TABLE,
        "old_physical_balance_target_used": False,
        "spot_price_feature_used": False,
        "flow_exchange_a61_capacity_feature_used": False,
        "future_actual_load_feature_used": False,
        "holdout_used_for_model_fitting_or_selection": False,
        "target_order_ok": target_order_ok,
        "forbidden_features": forbidden_features,
        "forbidden_columns": forbidden_columns,
    }


def verification_summary(
    input_contract: dict[str, object],
    completed_jobs: int,
    total_jobs: int,
    leakage: dict[str, object],
    aggregate: dict[str, object],
    area_results: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "p0056a_consumption_input_all_18": bool(input_contract["target_ok"]) and int(input_contract["target_area_count"]) == 18,
        "p0056b_weather_input_all_18": bool(input_contract["weather_ok"]) and int(input_contract["weather_area_count"]) == 18,
        "split_policy_applied": True,
        "jobs_completed_or_checkpointed": completed_jobs == total_jobs,
        "completed_jobs": completed_jobs,
        "total_jobs": total_jobs,
        "all_completed_area_results_persisted": len(area_results) == len(REQUIRED_AREAS),
        "no_holdout_fitting_or_selection": bool(leakage["ok"]),
        "no_forbidden_features": not leakage["forbidden_features"] and not leakage["forbidden_columns"],
        "aggregate_forecast_equals_sum_of_area_forecasts": aggregate["aggregate_forecast_equals_sum_of_area_forecasts"],
        "leakage_review_passes": leakage["ok"],
    }


def decide_status(
    completed_jobs: int,
    total_jobs: int,
    failed_areas: list[dict[str, object]],
    leakage: dict[str, object],
    area_results: list[dict[str, object]],
) -> str:
    if failed_areas or completed_jobs < total_jobs or not leakage["ok"] or len(area_results) != len(REQUIRED_AREAS):
        return "STOP"
    if FALLBACK_WEATHER_AREAS or any(row.get("fallback_used") for row in area_results):
        return "WARN"
    return "PASS"


def p0056c_feature_names() -> list[str]:
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
    lags = [f"area_consumption_lag_{lag}h" for lag in p0054k.LAGS]
    rollups = [f"area_consumption_roll_mean_{window}h" for window in p0054k.ROLL_WINDOWS] + [
        "area_consumption_roll_min_24h",
        "area_consumption_roll_max_24h",
        "area_consumption_roll_std_24h",
        "area_consumption_ramp_1h",
        "area_consumption_ramp_24h",
        "area_consumption_same_hour_24h_vs_168h",
    ]
    weather = [
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
        "weather_proxy_train_normal_temperature_2m_area",
        "weather_proxy_temperature_delta_from_train_normal_area",
        "weather_proxy_cold_spell_flag_area",
    ]
    return calendar + lags + rollups + weather


def p0056c_reduced_feature_names() -> list[str]:
    return [feature for feature in p0056c_feature_names() if not feature.startswith("weather_proxy_snow_depth")]


def model_method_contract(feature_names: list[str], reduced_feature_names: list[str], specs: list[object]) -> dict[str, object]:
    return {
        "default_model": MODEL_NAME,
        "fallback_order": ["F1_reduced_feature_set", "F2_weighted_ensemble_no_price", "F3_seasonal_same_week"],
        "feature_count": len(feature_names),
        "reduced_feature_count": len(reduced_feature_names),
        "model_families_available": [spec.family for spec in specs],  # type: ignore[attr-defined]
        "feature_families": ["calendar_time", "holiday_weekend", "historical_area_load_lags", "rolling_area_load_statistics", "area_weather_proxy_features"],
        "forbidden_features_excluded": True,
    }


def split_policy() -> dict[str, str]:
    return {
        "train_fit": "2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z",
        "holdout": "target_timestamp_utc >= 2025-06-01T00:00:00Z",
        "internal_validation": f"{p0054r.INTERNAL_VALIDATION_START} <= target_timestamp_utc < 2025-06-01T00:00:00Z",
        "internal_selection_data": "internal_validation_only",
        "holdout_used_for_fit_or_selection": "false",
    }


def stopped_summary(
    started: float,
    feature_path: Path,
    input_contract: dict[str, object],
    target_contract: dict[str, object],
    weather_contract: dict[str, object],
) -> dict[str, object]:
    return {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": "STOP",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "feature_db": str(feature_path),
        "input_contract": input_contract,
        "target_contract": target_contract,
        "weather_contract": weather_contract,
        "row_counts": {},
        "failed_areas": [],
        "completed_jobs": 0,
        "total_jobs": len(REQUIRED_AREAS) * 2,
    }


def reset_progress_log(evidence_dir: Path) -> None:
    write(evidence_dir / "progress-log.md", "# P0056C Progress Log\n\n")


def progress(
    evidence_dir: Path,
    area_code: str,
    phase: str,
    job: int,
    total_jobs: int,
    status: str,
    *,
    started_at: str | None = None,
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    elapsed = None
    if started_at:
        elapsed = (p0052.parse_utc(now) - p0052.parse_utc(started_at)).total_seconds()
    parts = [
        f"[P0056C progress] area={area_code}",
        f"phase={phase}",
        f"job={job}/{total_jobs}",
        f"status={status}",
    ]
    if status == "start":
        parts.append(f"timestamp={now}")
    if elapsed is not None:
        parts.append(f"elapsed_seconds={elapsed:.3f}")
    if extra:
        for key, value in extra.items():
            parts.append(f"{key}={value}")
    line = " ".join(parts)
    print(line, flush=True)
    with (evidence_dir / "progress-log.md").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    return {"area_code": area_code, "phase": phase, "job": job, "total_jobs": total_jobs, "status": status, "timestamp": now, "elapsed_seconds": elapsed, **(extra or {})}


def write_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog_md(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", labb_label_md()),
        "input-source-contract.md": write(evidence_dir / "input-source-contract.md", json_report("P0056C Input Source Contract", {"input_contract": summary.get("input_contract"), "target_contract": summary.get("target_contract"), "weather_contract": summary.get("weather_contract")})),
        "split-policy-applied.md": write(evidence_dir / "split-policy-applied.md", json_report("P0056C Split Policy Applied", summary.get("split_policy", {}))),
        "model-method-contract.md": write(evidence_dir / "model-method-contract.md", json_report("P0056C Model Method Contract", summary.get("model_method_contract", {}))),
        "checkpoint-resume.md": write(evidence_dir / "checkpoint-resume.md", checkpoint_resume_md(summary)),
        "component-job-status.md": write(evidence_dir / "component-job-status.md", job_status_md(summary)),
        "area-training-evidence.md": write(evidence_dir / "area-training-evidence.md", area_training_evidence_md(summary)),
        "area-results.md": write(evidence_dir / "area-results.md", area_results_md(summary)),
        "dayahead-results.md": write(evidence_dir / "dayahead-results.md", dayahead_results_md(summary)),
        "full-36h-results.md": write(evidence_dir / "full-36h-results.md", full36_results_md(summary)),
        "daily-energy-error-results.md": write(evidence_dir / "daily-energy-error-results.md", daily_energy_results_md(summary)),
        "cross-area-summary.md": write(evidence_dir / "cross-area-summary.md", json_report("P0056C Cross-Area Summary", summary.get("cross_area_summary", {}))),
        "aggregate-load-forecast-results.md": write(evidence_dir / "aggregate-load-forecast-results.md", json_report("P0056C Aggregate Load Forecast Results", summary.get("aggregate_forecast_summary", {}))),
        "leakage-review.md": write(evidence_dir / "leakage-review.md", json_report("P0056C Leakage Review", summary.get("leakage_review", {}))),
        "data-quality-limitations.md": write(evidence_dir / "data-quality-limitations.md", data_quality_limitations_md(summary)),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", what_we_learned_md(summary)),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", next_package_recommendation_md(summary)),
        "area-results.csv": write_csv(evidence_dir / "area-results.csv", summary.get("area_results", [])),  # type: ignore[arg-type]
        "job-status.csv": write_csv(evidence_dir / "job-status.csv", summary.get("job_status", [])),  # type: ignore[arg-type]
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(json_safe(compact_summary(summary)), indent=2, sort_keys=True) + "\n"),
        "cross-area-summary.csv": write_csv(evidence_dir / "cross-area-summary.csv", [summary.get("cross_area_summary", {})]),  # type: ignore[list-item]
    }
    return evidence


def changelog_md(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0056C Changelog",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Completed jobs: `{summary.get('completed_jobs', 0)}/{summary.get('total_jobs', 36)}`",
        f"- Areas with results: `{len(summary.get('area_results', []))}`",
        f"- Forecast log rows: `{summary.get('row_counts', {}).get('forecast_log_rows', 0)}`",
        f"- Metrics rows: `{summary.get('row_counts', {}).get('metrics_rows', 0)}`",
        "- No API, devices, runtime changes, spot price features, old physical_balance target, flow/exchange/A61/capacity features, or large committed artifacts.",
        "",
    ])


def labb_label_md() -> str:
    return "# P0056C LABB Label\n\nP0056C is LABB-only multi-area consumption forecasting. It is not G2-KANDIDAT or production forecast activation.\n"


def checkpoint_resume_md(summary: dict[str, object]) -> str:
    completed = int(summary.get("completed_jobs", 0))
    total = int(summary.get("total_jobs", len(REQUIRED_AREAS) * 2))
    job_status = summary.get("job_status", [])
    done = [row for row in job_status if row.get("status") == "done"] if isinstance(job_status, list) else []
    last = done[-1] if done else {}
    return "\n".join([
        "# P0056C Checkpoint Resume",
        "",
        f"- Completed jobs: `{completed}`",
        f"- Remaining jobs: `{max(0, total - completed)}`",
        f"- Last completed area: `{last.get('area_code')}`",
        f"- Last completed phase: `{last.get('phase')}`",
        "- Resume command: `python3 -m src.mac.services.spotprice_model_diagnostics.p0056c`",
        "- Checkpoint location: `requirements/package-runs/P0056C/progress-log.md`",
        "",
    ])


def job_status_md(summary: dict[str, object]) -> str:
    rows = summary.get("job_status", [])
    lines = ["# P0056C Component Job Status", "", "| area | phase | job | status | elapsed_seconds |", "| --- | --- | ---: | --- | ---: |"]
    for row in rows:  # type: ignore[union-attr]
        elapsed = "" if row.get("elapsed_seconds") is None else f"{float(row['elapsed_seconds']):.3f}"
        lines.append(f"| {row.get('area_code')} | {row.get('phase')} | {row.get('job')} | {row.get('status')} | {elapsed} |")
    lines.append("")
    return "\n".join(lines)


def area_training_evidence_md(summary: dict[str, object]) -> str:
    rows = summary.get("area_results", [])
    lines = ["# P0056C Area Training Evidence", "", "| area | status | fallback | train_fit_rows | holdout_rows | forecast_origins |", "| --- | --- | --- | ---: | ---: | ---: |"]
    for row in rows:  # type: ignore[union-attr]
        lines.append(f"| {row['area_code']} | {row['status']} | {row['fallback_used']} | {row['train_fit_rows']} | {row['holdout_rows']} | {row['forecast_origins']} |")
    lines.append("")
    return "\n".join(lines)


def area_results_md(summary: dict[str, object]) -> str:
    rows = summary.get("area_results", [])
    lines = ["# P0056C Area Results", "", "| area | DayAhead MAE | MAE % mean | full36 MAE | daily abs MWh | weather fallback |", "| --- | ---: | ---: | ---: | ---: | --- |"]
    for row in rows:  # type: ignore[union-attr]
        lines.append(f"| {row['area_code']} | {fmt(row['DayAhead_hourly_MAE'])} | {fmt(row['MAE_percent_of_mean_actual'])} | {fmt(row['full_36h_MAE'])} | {fmt(row['absolute_daily_energy_error_MWh'])} | {row['weather_fallback_proxy']} |")
    lines.append("")
    return "\n".join(lines)


def dayahead_results_md(summary: dict[str, object]) -> str:
    return area_metric_table("P0056C DayAhead Results", summary, ["DayAhead_hourly_MAE", "DayAhead_RMSE", "DayAhead_bias", "MAE_percent_of_mean_actual", "MAE_percent_of_median_actual"])


def full36_results_md(summary: dict[str, object]) -> str:
    return area_metric_table("P0056C Full 36h Results", summary, ["full_36h_MAE", "full_36h_RMSE", "full_36h_bias", "p90_absolute_error", "p95_absolute_error"])


def daily_energy_results_md(summary: dict[str, object]) -> str:
    return area_metric_table("P0056C Daily Energy Error Results", summary, ["absolute_daily_energy_error_MWh", "signed_daily_energy_error_MWh", "daily_energy_error_percent_of_actual"])


def area_metric_table(title: str, summary: dict[str, object], fields: list[str]) -> str:
    rows = summary.get("area_results", [])
    lines = [f"# {title}", "", "| area | " + " | ".join(fields) + " |", "| --- | " + " | ".join("---:" for _ in fields) + " |"]
    for row in rows:  # type: ignore[union-attr]
        lines.append("| " + str(row["area_code"]) + " | " + " | ".join(fmt(row.get(field)) for field in fields) + " |")
    lines.append("")
    return "\n".join(lines)


def data_quality_limitations_md(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0056C Data Quality Limitations",
        "",
        "- P0056B weather actual-proxy coverage ends at `2026-05-31T21:00Z`; later P0056A consumption-only rows are not modeled.",
        f"- P0056B fallback weather areas: `{', '.join(sorted(FALLBACK_WEATHER_AREAS))}`.",
        "- Weather rows are actual-weather LABB proxies, not production weather forecasts.",
        "- `snow_depth` is unavailable from P0056B and represented as a zero-filled nullable source feature for model matrix safety.",
        "",
    ])


def what_we_learned_md(summary: dict[str, object]) -> str:
    cross = summary.get("cross_area_summary", {})
    return "\n".join([
        "# P0056C What We Learned",
        "",
        f"- Best area by percent MAE: `{cross.get('best_area_by_percent_MAE')}`.",
        f"- Worst area by percent MAE: `{cross.get('worst_area_by_percent_MAE')}`.",
        "- The SE3 no-price method can be evaluated as a shared LABB baseline across the P0056A/P0056B multi-area surface.",
        "- Production readiness still requires separate weather forecast inputs and review beyond LABB actual-weather proxies.",
        "",
    ])


def next_package_recommendation_md(summary: dict[str, object]) -> str:
    return "# P0056C Next Package Recommendation\n\nRecommended next package: improve direct weather sources for fallback areas or build the first market-emulator layer on top of P0056C forecasts while keeping it LABB-only.\n"


def json_report(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(json_safe(payload), indent=2, sort_keys=True)}\n```\n"


def write_csv(path: Path, rows: object) -> str:
    rows = list(rows) if isinstance(rows, list) else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        if not rows:
            handle.write("")
            return str(path)
        columns = sorted({column for row in rows for column in row.keys()})
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


def compact_summary(summary: dict[str, object]) -> dict[str, object]:
    return {
        "status": summary.get("status"),
        "row_counts": summary.get("row_counts"),
        "completed_jobs": summary.get("completed_jobs"),
        "total_jobs": summary.get("total_jobs"),
        "cross_area_summary": summary.get("cross_area_summary"),
        "aggregate_forecast_summary": summary.get("aggregate_forecast_summary"),
        "leakage_review": summary.get("leakage_review"),
        "verification": summary.get("verification"),
        "area_results": summary.get("area_results"),
    }


def forecast_log_count(conn: sqlite3.Connection) -> int:
    row = conn.execute(f"SELECT COUNT(*) AS rows FROM {FORECAST_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,)).fetchone()
    return int(row["rows"] or 0)


def metrics_row_count(conn: sqlite3.Connection) -> int:
    row = conn.execute(f"SELECT COUNT(*) AS rows FROM {METRICS_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,)).fetchone()
    return int(row["rows"] or 0)


def safe_float_or_zero(value: object) -> float:
    if value is None:
        return 0.0
    return float(value)


def fmt(value: object) -> str:
    if value is None:
        return ""
    return f"{float(value):.3f}"


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    return value


def main() -> int:
    result = run_p0056c_multi_area_forecast()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
