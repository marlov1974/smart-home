"""P0055A LABB SE3 direct vs profiled clusters plus residual forecast."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import csv
import json
import math
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054n, p0054q, p0054r
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write


PACKAGE_ID = "P0055A"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0055A")
CLUSTER_TABLE = "se3_profiled_mga_cluster_hourly_v1"
RESIDUAL_TABLE = "se3_consumption_metered_residual_hourly_v1"
WEATHER_TABLE = "se3_climate_zone_weather_hourly_v1"
DIRECT_COMPONENT = "forecast_direct_se3_best"
RESIDUAL_COMPONENT = "forecast_residual_metered_non_profiled"
DECOMPOSITION_COMPONENT = "forecast_decomposition_total"
RECONCILED_COMPONENT = "forecast_reconciled_total"
PREDICTION_COLUMN = "pred_HorizonBiasCorrected_WeightedEnsemble_no_price"
DIRECT_PREDICTION_COLUMN = "pred_direct"
DECOMPOSITION_PREDICTION_COLUMN = "pred_decomposition_total"
RECONCILED_PREDICTION_COLUMN = "pred_reconciled_total"
ZERO_COMPONENT_IDS = tuple(f"C{climate}{load}" for climate in range(1, 5) for load in range(1, 5))
INTERNAL_VALIDATION_START = p0054r.INTERNAL_VALIDATION_START
MIN_FULL_MODEL_TRAIN_ROWS = 2000

CLUSTER_WEATHER_ZONE = {
    "C11": "SE3_EAST_COAST_MALARDALEN_STOCKHOLM",
    "C12": "SE3_EAST_COAST_MALARDALEN_STOCKHOLM",
    "C13": "SE3_EAST_COAST_MALARDALEN_STOCKHOLM",
    "C14": "SE3_EAST_COAST_MALARDALEN_STOCKHOLM",
    "C21": "SE3_WEST_COAST_GOTHENBURG",
    "C22": "SE3_WEST_COAST_GOTHENBURG",
    "C23": "SE3_WEST_COAST_GOTHENBURG",
    "C24": "SE3_WEST_COAST_GOTHENBURG",
    "C31": "SE3_NORTHERN_INLAND",
    "C32": "SE3_NORTHERN_INLAND",
    "C33": "SE3_NORTHERN_INLAND",
    "C34": "SE3_NORTHERN_INLAND",
    "C41": "SE3_SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND",
    "C42": "SE3_SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND",
    "C43": "SE3_SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND",
    "C44": "SE3_SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND",
}

WEATHER_FEATURE_MAP = {
    "temperature_2m": "weather_proxy_temperature_2m_se3",
    "apparent_temperature": "weather_proxy_apparent_temperature_se3",
    "wind_speed_100m": "weather_proxy_wind_100m_se3",
    "cloud_cover": "weather_proxy_cloud_cover_se3",
    "precipitation": "weather_proxy_precipitation_se3",
    "snowfall": "weather_proxy_snowfall_se3",
    "relative_humidity": "weather_proxy_humidity_se3",
    "heating_degree_proxy": "weather_proxy_heating_degree_hours_se3",
    "cooling_degree_proxy": "weather_proxy_cooling_degree_hours_se3",
    "temperature_2m_roll_mean_24h": "weather_proxy_temperature_roll_mean_24h_se3",
}


@dataclass(frozen=True)
class P0055AResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0055a_analysis(*, feature_db: Path | str = DEFAULT_FEATURE_DB, evidence_dir: Path | str = EVIDENCE_DIR) -> P0055AResult:
    started = time.monotonic()
    feature_db = Path(feature_db).expanduser()
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    direct_targets = load_direct_target_rows(feature_db)
    components, component_meta = load_component_target_rows(feature_db)
    weather_rows, weather_contract = load_climate_zone_weather_rows(feature_db)
    input_contract = validate_input_contract(direct_targets, components, weather_rows)
    if not input_contract["ok"]:
        raise RuntimeError(f"P0055A input contract failed: {input_contract}")

    environment = p0054r.capture_environment_status()
    specs = [spec for spec in p0054k.model_specs(environment["imports"]) if spec.family in p0054k.MODEL_FAMILIES]  # type: ignore[arg-type]
    feature_names = p0055a_feature_names()
    component_results: dict[str, dict[str, object]] = {}

    direct_rows = build_component_modeling_rows(direct_targets, DIRECT_COMPONENT, "SE3_BROAD_PROXY", weather_rows, set(p0054n.HORIZONS_36H))
    component_results[DIRECT_COMPONENT] = fit_component_forecast(DIRECT_COMPONENT, "direct_se3_total", direct_rows, feature_names, specs, zero_history=False)

    for cluster_id in ZERO_COMPONENT_IDS:
        targets = components.get(cluster_id, [])
        zone = CLUSTER_WEATHER_ZONE[cluster_id]
        rows = build_component_modeling_rows(targets, f"forecast_cluster_{cluster_id}", zone, weather_rows, set(p0054n.HORIZONS_36H))
        zero_history = float(component_meta.get(cluster_id, {}).get("total_mwh", 0.0)) == 0.0
        component_results[cluster_id] = fit_component_forecast(cluster_id, "profiled_load_profile_cluster", rows, feature_names, specs, zero_history=zero_history)

    residual_rows = build_component_modeling_rows(components[RESIDUAL_COMPONENT], RESIDUAL_COMPONENT, "SE3_BROAD_PROXY", weather_rows, set(p0054n.HORIZONS_36H))
    component_results[RESIDUAL_COMPONENT] = fit_component_forecast(RESIDUAL_COMPONENT, "metered_non_profiled_residual_calculated", residual_rows, feature_names, specs, zero_history=False)

    direct_scored_rows = component_results[DIRECT_COMPONENT]["rows"]  # type: ignore[assignment]
    decomposition_rows = aggregate_decomposition_rows(component_results, direct_scored_rows)
    reconciliation = learn_reconciliation_weights(decomposition_rows)
    apply_reconciled_forecast(decomposition_rows, reconciliation["weights"])  # type: ignore[arg-type]
    metrics = compute_all_metrics(direct_scored_rows, decomposition_rows)
    comparison = comparison_vs_direct(metrics)
    leakage_review = validate_p0055a_leakage(feature_names, component_results, reconciliation, input_contract)
    status = "PASS" if leakage_review["ok"] and metrics["direct_se3"]["dayahead"] and metrics["decomposition_total"]["dayahead"] else "WARN"

    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "input_contract": input_contract,
        "weather_contract": weather_contract,
        "split_policy": split_policy(),
        "feature_contract": feature_contract(),
        "input_classification": input_classification(),
        "environment": environment,
        "component_training": {key: result["training"] for key, result in component_results.items()},
        "component_status": component_status_rows(component_results, component_meta),
        "component_metrics": component_metrics(component_results),
        "total_metrics": metrics,
        "comparison_vs_direct": comparison,
        "reconciliation": reconciliation,
        "error_contribution": error_contribution_analysis(decomposition_rows, component_results),
        "leakage_review": leakage_review,
        "interpretation": interpretation(comparison, metrics),
        "what_we_learned": what_we_learned(comparison, component_results),
        "next_package_recommendation": next_package_recommendation(comparison),
        "row_counts": {
            "direct_target_rows": len(direct_targets),
            "component_count": len(component_results),
            "weather_zones": len(weather_rows),
            "direct_modeling_rows": len(direct_rows),
            "decomposition_rows": len(decomposition_rows),
            "component_prediction_rows": sum(len(result["rows"]) for result in component_results.values()),  # type: ignore[arg-type]
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
    evidence = write_p0055a_evidence(evidence_dir, summary)
    return P0055AResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def load_direct_target_rows(feature_db: Path | str) -> list[dict[str, object]]:
    return [{"timestamp_utc": row["timestamp_utc"], "consumption_se3": row["consumption_se3"]} for row in p0054q.load_entsoe_se3_target_rows(feature_db)]


def load_component_target_rows(feature_db: Path | str) -> tuple[dict[str, list[dict[str, object]]], dict[str, dict[str, object]]]:
    components: dict[str, list[dict[str, object]]] = {cluster_id: [] for cluster_id in ZERO_COMPONENT_IDS}
    meta: dict[str, dict[str, object]] = {cluster_id: {"component_type": "profiled_load_profile_cluster", "total_mwh": 0.0} for cluster_id in ZERO_COMPONENT_IDS}
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        require_table(conn, CLUSTER_TABLE)
        require_table(conn, RESIDUAL_TABLE)
        for row in conn.execute(
            f"""
            SELECT timestamp_utc, cluster_id, cluster_label, consumption_mw, mga_count
            FROM {CLUSTER_TABLE}
            WHERE generated_by_package='P0054Y2'
            ORDER BY cluster_id, timestamp_utc
            """
        ):
            cluster_id = str(row["cluster_id"])
            components.setdefault(cluster_id, []).append({"timestamp_utc": p0052.normalize_utc_text(row["timestamp_utc"]), "consumption_se3": float(row["consumption_mw"])})
            target_meta = meta.setdefault(cluster_id, {"component_type": "profiled_load_profile_cluster", "total_mwh": 0.0})
            target_meta["cluster_label"] = str(row["cluster_label"])
            target_meta["mga_count"] = int(row["mga_count"])
            target_meta["total_mwh"] = float(target_meta.get("total_mwh", 0.0)) + float(row["consumption_mw"])
        residual = []
        for row in conn.execute(
            f"""
            SELECT timestamp_utc, residual_metered_non_profiled_mw
            FROM {RESIDUAL_TABLE}
            WHERE generated_by_package='P0054Y2' AND area='SE3'
            ORDER BY timestamp_utc
            """
        ):
            residual.append({"timestamp_utc": p0052.normalize_utc_text(row["timestamp_utc"]), "consumption_se3": float(row["residual_metered_non_profiled_mw"])})
        components[RESIDUAL_COMPONENT] = residual
        meta[RESIDUAL_COMPONENT] = {"component_type": "metered_non_profiled_residual_calculated", "total_mwh": sum(float(row["consumption_se3"]) for row in residual)}
    for rows in components.values():
        rows.sort(key=lambda row: str(row["timestamp_utc"]))
    return components, meta


def load_climate_zone_weather_rows(feature_db: Path | str) -> tuple[dict[str, dict[str, dict[str, object]]], dict[str, object]]:
    rows: dict[str, dict[str, dict[str, object]]] = defaultdict(lambda: defaultdict(dict))
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        require_table(conn, WEATHER_TABLE)
        for row in conn.execute(
            f"""
            SELECT timestamp_utc, climate_zone_id, feature_name, feature_value
            FROM {WEATHER_TABLE}
            WHERE generated_by_package='P0054Z'
            ORDER BY climate_zone_id, timestamp_utc, feature_name
            """
        ):
            zone = str(row["climate_zone_id"])
            ts = p0052.normalize_utc_text(row["timestamp_utc"])
            feature = WEATHER_FEATURE_MAP.get(str(row["feature_name"]))
            if feature:
                rows[zone][ts][feature] = float(row["feature_value"])
                rows[zone][ts]["weather_proxy_label"] = p0054k.WEATHER_PROXY_LABEL
    materialized = {zone: dict(hours) for zone, hours in rows.items()}
    add_weather_derived_features(materialized)
    timestamps = [ts for hours in materialized.values() for ts in hours]
    return materialized, {
        "table": WEATHER_TABLE,
        "generated_by_package": "P0054Z",
        "zones": sorted(materialized),
        "rows_by_zone": {zone: len(hours) for zone, hours in materialized.items()},
        "start": min(timestamps) if timestamps else "",
        "end": max(timestamps) if timestamps else "",
        "input_classification": "proxy",
        "proxy_label": p0054k.WEATHER_PROXY_LABEL,
    }


def add_weather_derived_features(weather_rows: dict[str, dict[str, dict[str, object]]]) -> None:
    for _zone, by_ts in weather_rows.items():
        train_values = [
            float(row["weather_proxy_temperature_2m_se3"])
            for ts, row in by_ts.items()
            if "weather_proxy_temperature_2m_se3" in row and p0054k.p0054i_split(ts) == "train_fit" and ts < INTERNAL_VALIDATION_START
        ]
        normal = p0054k.mean_float(train_values) if train_values else 0.0
        for row in by_ts.values():
            temp = float(row.get("weather_proxy_temperature_2m_se3", normal))
            row["weather_proxy_train_normal_temperature_2m_se3"] = normal
            row["weather_proxy_temperature_delta_from_train_normal_se3"] = temp - normal
            row["weather_proxy_cold_spell_flag_se3"] = 1 if temp <= 0.0 else 0


def build_component_modeling_rows(
    target_rows: list[dict[str, object]],
    component_id: str,
    climate_zone_id: str,
    weather_rows: dict[str, dict[str, dict[str, object]]],
    horizons: set[int],
) -> list[dict[str, object]]:
    if not target_rows:
        return []
    source_by_ts = {str(row["timestamp_utc"]): row for row in target_rows}
    source_index = {str(row["timestamp_utc"]): index for index, row in enumerate(target_rows)}
    values = [float(row["consumption_se3"]) for row in target_rows]
    origin_rows = p0054r.build_no_price_origin_rows(target_rows, horizons)
    zone_weather = weather_rows.get(climate_zone_id, {})
    rows = []
    for origin in origin_rows:
        horizon = int(origin["horizon_h"])
        origin_ts = str(origin["forecast_origin_timestamp_utc"])
        target_ts = str(origin["target_timestamp_utc"])
        origin_index = source_index.get(origin_ts)
        target = source_by_ts.get(target_ts)
        if origin_index is None or target is None or origin_index < max(max(p0054k.LAGS), max(p0054k.ROLL_WINDOWS)):
            continue
        row = {
            "forecast_origin_timestamp_utc": origin_ts,
            "input_data_cutoff_utc": origin["input_data_cutoff_utc"],
            "target_timestamp_utc": target_ts,
            "horizon_h": horizon,
            "horizon_hours": int(origin["horizon_hours"]),
            p0054k.TARGET_FIELD: float(target["consumption_se3"]),
            "component_id": component_id,
            "area_or_target": component_id,
            "prediction_kind": "consumption_mw",
            "climate_zone_id": climate_zone_id,
            "dataset_kind": "offline_labb_component_decomposition_not_deployable",
            "weather_proxy_label": p0054k.WEATHER_PROXY_LABEL if target_ts in zone_weather else "weather_proxy_missing",
        }
        p0054k.attach_calendar_features(row, p0052.parse_utc(target_ts) + timedelta(hours=1))
        row.update(p0054k.lag_features_at_origin(values, origin_index))
        row.update(p0054k.rolling_features_at_origin(values, origin_index))
        row.update(zone_weather.get(target_ts, {}))
        rows.append(row)
    p0054k.assign_p0054i_splits(rows)
    p0054r.assign_internal_validation_splits(rows)
    return rows


def fit_component_forecast(
    component_id: str,
    component_type: str,
    rows: list[dict[str, object]],
    features: list[str],
    specs: list[object],
    *,
    zero_history: bool,
) -> dict[str, object]:
    rows = [dict(row) for row in rows]
    if zero_history:
        training = apply_zero_forecast(rows, PREDICTION_COLUMN)
        training.update({"component_id": component_id, "component_type": component_type})
        return {"rows": rows, "training": training, "status": "zero_forecast", "prediction_column": PREDICTION_COLUMN}
    train_rows = [row for row in rows if row.get("split") == "train_fit"]
    holdout_rows = [row for row in rows if row.get("split") == "holdout"]
    if len(train_rows) < MIN_FULL_MODEL_TRAIN_ROWS or not holdout_rows or not specs:
        training = apply_same_week_fallback(rows, PREDICTION_COLUMN)
        training.update({"component_id": component_id, "component_type": component_type, "reason": "insufficient_rows_or_specs"})
        return {"rows": rows, "training": training, "status": "fallback_same_week", "prediction_column": PREDICTION_COLUMN}
    try:
        training = fit_horizon_bias_weighted_ensemble(rows, features, specs)
        training.update({"component_id": component_id, "component_type": component_type})
        return {"rows": rows, "training": training, "status": "full_model", "prediction_column": PREDICTION_COLUMN}
    except Exception as exc:  # pragma: no cover - exercised only when optional local ML stack fails
        training = apply_same_week_fallback(rows, PREDICTION_COLUMN)
        training.update({"component_id": component_id, "component_type": component_type, "fallback_after_error": type(exc).__name__, "error": str(exc)[:400]})
        return {"rows": rows, "training": training, "status": "fallback_after_model_error", "prediction_column": PREDICTION_COLUMN}


def fit_horizon_bias_weighted_ensemble(rows: list[dict[str, object]], features: list[str], specs: list[object]) -> dict[str, object]:
    internal_train = [row for row in rows if row.get(p0054r.INTERNAL_SPLIT_FIELD) == "internal_train"]
    internal_validation = [row for row in rows if row.get(p0054r.INTERNAL_SPLIT_FIELD) == "internal_validation"]
    train_fit = [row for row in rows if row.get("split") == "train_fit"]
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
    weighted_col = p0054k.prediction_column("WeightedEnsemble_no_price")
    p0054r.apply_weighted_ensemble(internal_validation, weights, weighted_col)
    p0054r.apply_weighted_ensemble(rows, weights, weighted_col)
    bias_evidence = p0054r.fit_and_apply_horizon_bias_correction(internal_validation, rows, "WeightedEnsemble_no_price", PREDICTION_COLUMN)
    return {
        "method": "HorizonBiasCorrected_WeightedEnsemble_no_price",
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


def apply_zero_forecast(rows: list[dict[str, object]], output_column: str) -> dict[str, object]:
    for row in rows:
        row[output_column] = 0.0
    return {"method": "F0_zero_forecast", "status": "zero_forecast", "applied_rows": len(rows), "holdout_used_for_fit": False}


def apply_same_week_fallback(rows: list[dict[str, object]], output_column: str) -> dict[str, object]:
    by_ts = {str(row["target_timestamp_utc"]): float(row[p0054k.TARGET_FIELD]) for row in rows if p0052.parse_utc(str(row["target_timestamp_utc"])) < p0052.parse_utc(str(row["forecast_origin_timestamp_utc"]))}
    global_history = [float(row[p0054k.TARGET_FIELD]) for row in rows if row.get("split") == "train_fit"]
    default = p0054k.mean_float(global_history) if global_history else 0.0
    applied = 0
    for row in rows:
        target_dt = p0052.parse_utc(str(row["target_timestamp_utc"]))
        previous_week = p0052.format_utc(target_dt - timedelta(hours=168))
        row[output_column] = float(by_ts.get(previous_week, default))
        applied += 1
    return {"method": "F1_previous_week_same_hour_else_train_fit_mean", "status": "fallback_same_week", "applied_rows": applied, "holdout_used_for_fit": False}


def aggregate_decomposition_rows(component_results: dict[str, dict[str, object]], direct_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    component_by_key: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for component_id, result in component_results.items():
        if component_id == DIRECT_COMPONENT:
            continue
        for row in result["rows"]:  # type: ignore[union-attr]
            key = (str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"]))
            if row.get(PREDICTION_COLUMN) is not None:
                component_by_key[key].append(row)
    direct_by_key = {(str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"])): row for row in direct_rows}
    out = []
    required_count = len(ZERO_COMPONENT_IDS) + 1
    for key, parts in sorted(component_by_key.items()):
        if len(parts) != required_count or key not in direct_by_key:
            continue
        direct = direct_by_key[key]
        decomposition = sum(float(row[PREDICTION_COLUMN]) for row in parts)
        actual_component_sum = sum(float(row[p0054k.TARGET_FIELD]) for row in parts)
        out.append(
            {
                **direct,
                DIRECT_PREDICTION_COLUMN: direct.get(PREDICTION_COLUMN),
                DECOMPOSITION_PREDICTION_COLUMN: decomposition,
                "actual_component_sum_mw": actual_component_sum,
                "decomposition_part_count": len(parts),
                "decomposition_actual_equals_direct_delta_mw": actual_component_sum - float(direct[p0054k.TARGET_FIELD]),
            }
        )
    return out


def learn_reconciliation_weights(rows: list[dict[str, object]]) -> dict[str, object]:
    validation = [
        row
        for row in rows
        if row.get(p0054r.INTERNAL_SPLIT_FIELD) == "internal_validation"
        and row.get(DIRECT_PREDICTION_COLUMN) is not None
        and row.get(DECOMPOSITION_PREDICTION_COLUMN) is not None
    ]
    best = {"direct": 1.0, "decomposition": 0.0, "bias": 0.0}
    best_mae = math.inf
    for direct_weight in [index / 20.0 for index in range(21)]:
        decomp_weight = 1.0 - direct_weight
        raw_errors = [
            direct_weight * float(row[DIRECT_PREDICTION_COLUMN]) + decomp_weight * float(row[DECOMPOSITION_PREDICTION_COLUMN]) - float(row[p0054k.TARGET_FIELD])
            for row in validation
        ]
        bias = p0054k.mean_float(raw_errors) if raw_errors else 0.0
        abs_errors = [abs(error - bias) for error in raw_errors]
        mae = p0054k.mean_float(abs_errors) if abs_errors else math.inf
        if mae < best_mae:
            best_mae = mae
            best = {"direct": direct_weight, "decomposition": decomp_weight, "bias": bias}
    return {
        "status": "run" if validation else "skipped_no_internal_validation_rows",
        "weights": best,
        "internal_validation_rows": len(validation),
        "internal_validation_mae_mw": None if math.isinf(best_mae) else best_mae,
        "fit_data": "internal_validation_only",
        "holdout_used_for_weights_or_bias": False,
    }


def apply_reconciled_forecast(rows: list[dict[str, object]], weights: dict[str, float]) -> None:
    for row in rows:
        if row.get(DIRECT_PREDICTION_COLUMN) is None or row.get(DECOMPOSITION_PREDICTION_COLUMN) is None:
            continue
        row[RECONCILED_PREDICTION_COLUMN] = (
            float(weights["direct"]) * float(row[DIRECT_PREDICTION_COLUMN])
            + float(weights["decomposition"]) * float(row[DECOMPOSITION_PREDICTION_COLUMN])
            - float(weights.get("bias", 0.0))
        )


def compute_all_metrics(direct_rows: list[dict[str, object]], decomposition_rows: list[dict[str, object]]) -> dict[str, object]:
    direct_common = [row for row in decomposition_rows if row.get(DIRECT_PREDICTION_COLUMN) is not None]
    return {
        "direct_se3": compute_total_metrics(direct_common, DIRECT_PREDICTION_COLUMN),
        "decomposition_total": compute_total_metrics(decomposition_rows, DECOMPOSITION_PREDICTION_COLUMN),
        "reconciled_total": compute_total_metrics(decomposition_rows, RECONCILED_PREDICTION_COLUMN),
        "direct_all_available": compute_total_metrics(direct_rows, PREDICTION_COLUMN),
    }


def compute_total_metrics(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    prediction_columns = (prediction_column,)
    full36, _full36_rows = p0054n.evaluate_full_36h_paths(rows, prediction_columns)
    dayahead, dayahead_rows = p0054n.evaluate_dayahead_delivery_days(rows, prediction_columns)
    selected_full36 = p0054q.selected_full36_rows(rows)
    selected_dayahead = p0054q.selected_dayahead_rows(rows)
    p0054q.add_percent_metrics(full36, selected_full36, prediction_columns, "full36")
    p0054q.add_percent_metrics(dayahead, selected_dayahead, prediction_columns, "dayahead")
    daily = p0054q.daily_energy_error_summary(selected_dayahead, prediction_columns)
    regimes = total_regime_metrics(selected_dayahead, prediction_column)
    return {
        "full36": full36.get(prediction_column, {}),
        "dayahead": dayahead.get(prediction_column, {}),
        "daily_energy": daily.get(prediction_column, {}),
        "regimes": regimes,
        "row_counts": {
            "input_rows": len(rows),
            "full36_selected_rows": len(selected_full36),
            "dayahead_selected_rows": len(selected_dayahead),
        },
    }


def total_regime_metrics(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    groups = {
        "offpeak": [row for row in rows if int(row["target_model_cet_hour"]) in set(range(0, 6)) | set(range(22, 24))],
        "morning_ramp": [row for row in rows if 6 <= int(row["target_model_cet_hour"]) <= 9],
        "evening_peak": [row for row in rows if 16 <= int(row["target_model_cet_hour"]) <= 20],
        "weekday": [row for row in rows if int(row.get("is_weekend", 0)) == 0],
        "weekend": [row for row in rows if int(row.get("is_weekend", 0)) == 1],
        "holiday": [row for row in rows if int(row.get("is_holiday", 0)) == 1],
        "cold_high_load": [row for row in rows if float(row.get("weather_proxy_temperature_2m_se3", 99.0)) <= 0.0],
        "ramp": [row for row in rows if abs(float(row.get("consumption_se3_ramp_24h", 0.0))) >= 500.0],
    }
    out = {}
    for name, subset in groups.items():
        available = [row for row in subset if row.get(prediction_column) is not None]
        metric = p0054k.regression_metric_from_predictions(available, [float(row[prediction_column]) for row in available])
        out[name] = {"rows": len(available), "MAE": metric["MAE"], "RMSE": metric["RMSE"], "bias": metric["bias"]}
    return out


def comparison_vs_direct(metrics: dict[str, object]) -> dict[str, object]:
    direct = metrics["direct_se3"]  # type: ignore[index]
    decomposition = metrics["decomposition_total"]  # type: ignore[index]
    reconciled = metrics["reconciled_total"]  # type: ignore[index]
    direct_mae = metric_value(direct, "dayahead", "hourly_MAE_delivery_day")
    decomp_mae = metric_value(decomposition, "dayahead", "hourly_MAE_delivery_day")
    direct_energy = metric_value(direct, "daily_energy", "absolute_daily_energy_error_MWh")
    decomp_energy = metric_value(decomposition, "daily_energy", "absolute_daily_energy_error_MWh")
    full_direct = metric_value(direct, "full36", "MAE_full_36h")
    full_decomp = metric_value(decomposition, "full36", "MAE_full_36h")
    rec_mae = metric_value(reconciled, "dayahead", "hourly_MAE_delivery_day")
    return {
        "decomposition_delta_vs_direct_MW": none_delta(decomp_mae, direct_mae),
        "decomposition_delta_vs_direct_percent": relative_delta(decomp_mae, direct_mae),
        "daily_energy_delta_vs_direct_percent": relative_delta(decomp_energy, direct_energy),
        "full36_delta_vs_direct_percent": relative_delta(full_decomp, full_direct),
        "reconciled_delta_vs_direct_MW": none_delta(rec_mae, direct_mae),
        "reconciled_delta_vs_direct_percent": relative_delta(rec_mae, direct_mae),
        "decomposition_beats_direct_threshold": threshold_decomposition(direct_mae, decomp_mae, direct_energy, decomp_energy, full_direct, full_decomp),
        "reconciled_beats_direct_threshold": threshold_reconciled(direct_mae, rec_mae),
    }


def metric_value(container: object, section: str, key: str) -> float | None:
    try:
        value = container[section][key]  # type: ignore[index]
    except KeyError:
        return None
    return None if value is None else float(value)


def none_delta(value: float | None, baseline: float | None) -> float | None:
    if value is None or baseline is None:
        return None
    return value - baseline


def relative_delta(value: float | None, baseline: float | None) -> float | None:
    if value is None or baseline in (None, 0.0):
        return None
    return (value - baseline) / baseline * 100.0


def threshold_decomposition(direct_mae: float | None, decomp_mae: float | None, direct_energy: float | None, decomp_energy: float | None, direct_full: float | None, decomp_full: float | None) -> bool:
    return bool(
        direct_mae
        and decomp_mae
        and (
            relative_delta(decomp_mae, direct_mae) is not None
            and relative_delta(decomp_mae, direct_mae) <= -2.0
            or (direct_energy and decomp_energy and relative_delta(decomp_energy, direct_energy) is not None and relative_delta(decomp_energy, direct_energy) <= -5.0 and relative_delta(decomp_mae, direct_mae) <= 1.0)
            or (direct_full and decomp_full and relative_delta(decomp_full, direct_full) is not None and relative_delta(decomp_full, direct_full) <= -2.0 and relative_delta(decomp_mae, direct_mae) <= 0.0)
        )
    )


def threshold_reconciled(direct_mae: float | None, rec_mae: float | None) -> bool:
    return bool(direct_mae and rec_mae and relative_delta(rec_mae, direct_mae) is not None and relative_delta(rec_mae, direct_mae) <= -1.0)


def error_contribution_analysis(decomposition_rows: list[dict[str, object]], component_results: dict[str, dict[str, object]]) -> dict[str, object]:
    by_component = []
    total_abs = 0.0
    for component_id, result in component_results.items():
        if component_id == DIRECT_COMPONENT:
            continue
        rows = [row for row in result["rows"] if row.get("split") == "holdout" and row.get(PREDICTION_COLUMN) is not None]  # type: ignore[union-attr]
        errors = [abs(float(row[PREDICTION_COLUMN]) - float(row[p0054k.TARGET_FIELD])) for row in rows]
        mae = p0054k.mean_float(errors) if errors else None
        if mae is not None:
            total_abs += mae
        by_component.append({"component_id": component_id, "holdout_rows": len(rows), "MAE": mae, "status": result["status"]})
    for row in by_component:
        row["share_of_component_mae_sum"] = None if not total_abs or row["MAE"] is None else float(row["MAE"]) / total_abs
    residual = next((row for row in by_component if row["component_id"] == RESIDUAL_COMPONENT), {})
    cluster_sum = sum(float(row["MAE"] or 0.0) for row in by_component if str(row["component_id"]).startswith("C"))
    return {"component_rows": by_component, "residual_error_contribution": residual, "cluster_sum_mae": cluster_sum, "component_mae_sum": total_abs}


def component_status_rows(component_results: dict[str, dict[str, object]], component_meta: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for component_id, result in sorted(component_results.items()):
        model_rows = result["rows"]  # type: ignore[assignment]
        values = [float(row[p0054k.TARGET_FIELD]) for row in model_rows]
        rows.append(
            {
                "component_id": component_id,
                "component_type": component_meta.get(component_id, {}).get("component_type", "direct_se3_total" if component_id == DIRECT_COMPONENT else ""),
                "status": result["status"],
                "modeling_rows": len(model_rows),
                "train_fit_rows": sum(1 for row in model_rows if row.get("split") == "train_fit"),
                "holdout_rows": sum(1 for row in model_rows if row.get("split") == "holdout"),
                "mean_actual_mw": p0054k.mean_float(values) if values else None,
                "total_mwh": component_meta.get(component_id, {}).get("total_mwh"),
            }
        )
    return rows


def component_metrics(component_results: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for component_id, result in sorted(component_results.items()):
        if component_id == DIRECT_COMPONENT:
            continue
        scored = [row for row in result["rows"] if row.get("split") == "holdout" and row.get(PREDICTION_COLUMN) is not None]  # type: ignore[union-attr]
        actuals = [float(row[p0054k.TARGET_FIELD]) for row in scored]
        metric = p0054k.regression_metric_from_predictions(scored, [float(row[PREDICTION_COLUMN]) for row in scored])
        rows.append(
            {
                "component_id": component_id,
                "status": result["status"],
                "holdout_rows": len(scored),
                "mean_actual_mw": p0054k.mean_float(actuals) if actuals else None,
                "DayAhead_MAE": compute_total_metrics(scored, PREDICTION_COLUMN)["dayahead"].get("hourly_MAE_delivery_day"),
                "full_36h_MAE": compute_total_metrics(scored, PREDICTION_COLUMN)["full36"].get("MAE_full_36h"),
                "holdout_MAE": metric["MAE"],
                "holdout_RMSE": metric["RMSE"],
                "holdout_bias": metric["bias"],
                "p90_abs_error": metric["p90_absolute_error"],
                "p95_abs_error": metric["p95_absolute_error"],
                "MAE_percent_of_component_mean": None if not actuals or not p0054k.mean_float(actuals) else float(metric["MAE"] or 0.0) / p0054k.mean_float(actuals) * 100.0,
            }
        )
    return rows


def validate_input_contract(direct_targets: list[dict[str, object]], components: dict[str, list[dict[str, object]]], weather_rows: dict[str, dict[str, dict[str, object]]]) -> dict[str, object]:
    missing_clusters = [cluster_id for cluster_id in ZERO_COMPONENT_IDS if cluster_id not in components]
    required_zones = set(CLUSTER_WEATHER_ZONE.values()) | {"SE3_BROAD_PROXY"}
    missing_zones = sorted(required_zones - set(weather_rows))
    return {
        "ok": bool(direct_targets) and RESIDUAL_COMPONENT in components and not missing_clusters and not missing_zones,
        "direct_source_table": p0054q.TARGET_TABLE,
        "cluster_table": CLUSTER_TABLE,
        "residual_table": RESIDUAL_TABLE,
        "weather_table": WEATHER_TABLE,
        "direct_rows": len(direct_targets),
        "component_rows": {key: len(value) for key, value in components.items()},
        "missing_clusters": missing_clusters,
        "missing_weather_zones": missing_zones,
        "residual_is_observed_per_mga": False,
    }


def validate_p0055a_leakage(features: list[str], component_results: dict[str, dict[str, object]], reconciliation: dict[str, object], input_contract: dict[str, object]) -> dict[str, object]:
    forbidden_terms = ("price", "spot", "physical_balance", "flow", "export", "import", "a61", "capacity", "utilization", "future_actual")
    forbidden_features = [feature for feature in features if any(term in feature.lower() for term in forbidden_terms)]
    holdout_fit_flags = []
    for result in component_results.values():
        training = result["training"]  # type: ignore[assignment]
        if training.get("holdout_used_for_weights_or_bias") or training.get("holdout_used_for_fit"):
            holdout_fit_flags.append(training.get("component_id"))
    ok = input_contract["ok"] and not forbidden_features and not holdout_fit_flags and not reconciliation.get("holdout_used_for_weights_or_bias")
    return {
        "ok": ok,
        "input_contract_ok": input_contract["ok"],
        "forbidden_features": forbidden_features,
        "holdout_fit_flags": holdout_fit_flags,
        "reconciliation_holdout_used": bool(reconciliation.get("holdout_used_for_weights_or_bias")),
        "spot_price_features_used": False,
        "old_physical_balance_target_used": False,
        "flow_exchange_a61_capacity_used": False,
        "future_actual_target_feature_used": False,
        "residual_treated_as_observed_per_mga": False,
        "weather_proxy_label_preserved": True,
    }


def p0055a_feature_names() -> list[str]:
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
        "is_holiday",
        "is_bridge_day",
        "is_holiday_period",
        "holiday_strength",
        "special_day_type",
        "special_day_group",
    ]
    lags = [f"consumption_se3_lag_{lag}h" for lag in p0054k.LAGS]
    rollups = [f"consumption_se3_roll_mean_{window}h" for window in p0054k.ROLL_WINDOWS] + [
        "consumption_se3_roll_min_24h",
        "consumption_se3_roll_max_24h",
        "consumption_se3_roll_std_24h",
        "consumption_se3_ramp_1h",
        "consumption_se3_ramp_24h",
        "consumption_se3_same_hour_24h_vs_168h",
    ]
    weather = [
        "weather_proxy_temperature_2m_se3",
        "weather_proxy_apparent_temperature_se3",
        "weather_proxy_wind_100m_se3",
        "weather_proxy_cloud_cover_se3",
        "weather_proxy_precipitation_se3",
        "weather_proxy_snowfall_se3",
        "weather_proxy_humidity_se3",
        "weather_proxy_heating_degree_hours_se3",
        "weather_proxy_cooling_degree_hours_se3",
        "weather_proxy_temperature_roll_mean_24h_se3",
        "weather_proxy_train_normal_temperature_2m_se3",
        "weather_proxy_temperature_delta_from_train_normal_se3",
        "weather_proxy_cold_spell_flag_se3",
    ]
    return calendar + lags + rollups + weather


def feature_contract() -> dict[str, object]:
    return {
        "model": "HorizonBiasCorrected_WeightedEnsemble_no_price",
        "features": p0055a_feature_names(),
        "source": "P0055A local no-price contract matched to P0054Z weather table",
        "spot_price_features": [],
    }


def input_classification() -> dict[str, str]:
    return {
        "calendar": "forecast_safe",
        "historical_component_lags_rollups": "forecast_safe",
        "direct_entsoe_se3_target": "historical_observed_only",
        "profiled_load_profile_clusters": "historical_observed_only",
        "metered_non_profiled_residual": "historical_observed_only",
        "weather": "proxy",
        "spot_price": "excluded_leakage",
        "flows_exchanges_a61_capacity": "excluded_leakage",
        "future_actual_targets": "excluded_leakage",
    }


def split_policy() -> dict[str, str]:
    return p0054r.split_policy()


def interpretation(comparison: dict[str, object], metrics: dict[str, object]) -> dict[str, object]:
    beats = bool(comparison.get("decomposition_beats_direct_threshold"))
    return {
        "primary_answer": "decomposition_beats_direct" if beats else "direct_remains_default",
        "decomposition_threshold_met": beats,
        "reconciled_threshold_met": bool(comparison.get("reconciled_beats_direct_threshold")),
        "labb_not_g2_candidate": True,
        "weather_proxy_limitation": "P0054Z actual weather is used as actual-as-forecast proxy.",
    }


def what_we_learned(comparison: dict[str, object], component_results: dict[str, dict[str, object]]) -> list[str]:
    zeroed = sorted(component_id for component_id, result in component_results.items() if result["status"] == "zero_forecast")
    return [
        f"Zero-volume clusters were forecast as zero: {', '.join(zeroed) if zeroed else 'none'}.",
        f"Decomposition DayAhead delta vs direct: {comparison.get('decomposition_delta_vs_direct_percent')} percent.",
        "Residual remains calculated from SE3 total minus profiled/load-profile clusters, not observed measured MGA data.",
        "Direct SE3 should remain default unless threshold metrics show decomposition improvement.",
    ]


def next_package_recommendation(comparison: dict[str, object]) -> str:
    if comparison.get("decomposition_beats_direct_threshold"):
        return "P0055B should stress-test decomposition under forecast-weather realism and season/regime splits before any G2-KANDIDAT evaluation."
    return "P0055B should keep direct SE3 as default and use decomposition for diagnostics/error attribution; improve component taxonomy before more hierarchy."


def write_p0055a_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", "# P0055A LABB label\n\nLabel: `LABB`. This is not a G2-KANDIDAT evaluation.\n"),
        "input-source-contract.md": write(evidence_dir / "input-source-contract.md", json_report("P0055A input source contract", summary["input_contract"])),
        "split-policy-applied.md": write(evidence_dir / "split-policy-applied.md", json_report("P0055A split policy", summary["split_policy"])),
        "weather-feature-contract.md": write(evidence_dir / "weather-feature-contract.md", json_report("P0055A weather feature contract", summary["weather_contract"])),
        "component-target-contract.md": write(evidence_dir / "component-target-contract.md", json_report("P0055A component target contract", summary["component_status"])),
        "model-method-contract.md": write(evidence_dir / "model-method-contract.md", json_report("P0055A model method contract", summary["feature_contract"])),
        "component-training-evidence.md": write(evidence_dir / "component-training-evidence.md", json_report("P0055A component training evidence", summary["component_training"])),
        "component-forecast-status.md": write(evidence_dir / "component-forecast-status.md", markdown_table("P0055A component forecast status", summary["component_status"])),
        "component-results.md": write(evidence_dir / "component-results.md", markdown_table("P0055A component results", summary["component_metrics"])),
        "direct-se3-results.md": write(evidence_dir / "direct-se3-results.md", json_report("P0055A direct SE3 results", summary["total_metrics"]["direct_se3"])),
        "decomposition-total-results.md": write(evidence_dir / "decomposition-total-results.md", json_report("P0055A decomposition total results", summary["total_metrics"]["decomposition_total"])),
        "reconciled-results.md": write(evidence_dir / "reconciled-results.md", json_report("P0055A reconciled results", {"metrics": summary["total_metrics"]["reconciled_total"], "reconciliation": summary["reconciliation"]})),
        "comparison-vs-direct.md": write(evidence_dir / "comparison-vs-direct.md", json_report("P0055A comparison vs direct", summary["comparison_vs_direct"])),
        "error-contribution-analysis.md": write(evidence_dir / "error-contribution-analysis.md", json_report("P0055A error contribution analysis", summary["error_contribution"])),
        "dayahead-results.md": write(evidence_dir / "dayahead-results.md", json_report("P0055A DayAhead results", {key: value["dayahead"] for key, value in summary["total_metrics"].items()})),
        "full-36h-results.md": write(evidence_dir / "full-36h-results.md", json_report("P0055A full 36h results", {key: value["full36"] for key, value in summary["total_metrics"].items()})),
        "daily-energy-error-results.md": write(evidence_dir / "daily-energy-error-results.md", json_report("P0055A daily energy error results", {key: value["daily_energy"] for key, value in summary["total_metrics"].items()})),
        "leakage-review.md": write(evidence_dir / "leakage-review.md", json_report("P0055A leakage review", summary["leakage_review"])),
        "interpretation.md": write(evidence_dir / "interpretation.md", json_report("P0055A interpretation", summary["interpretation"])),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", "# P0055A what we learned\n\n" + "\n".join(f"- {line}" for line in summary["what_we_learned"]) + "\n"),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", "# P0055A next package recommendation\n\n" + str(summary["next_package_recommendation"]) + "\n"),
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(json_safe(summary), indent=2, sort_keys=True) + "\n"),
    }
    files["component-results.csv"] = write_csv(evidence_dir / "component-results.csv", summary["component_metrics"])
    files["forecast-status.csv"] = write_csv(evidence_dir / "forecast-status.csv", summary["component_status"])
    files["total-comparison.csv"] = write_csv(evidence_dir / "total-comparison.csv", [summary["comparison_vs_direct"]])
    files["error-contribution.csv"] = write_csv(evidence_dir / "error-contribution.csv", summary["error_contribution"]["component_rows"])
    return files


def changelog(summary: dict[str, object]) -> str:
    comparison = summary["comparison_vs_direct"]
    return f"""# P0055A changelog

Status: `{summary['status']}`

- Built LABB direct-vs-decomposition SE3 consumption forecast comparison.
- Direct model: `HorizonBiasCorrected_WeightedEnsemble_no_price` no-price contract.
- Component forecasts: `{summary['row_counts']['component_count']}` including direct, 16 clusters and calculated residual.
- Decomposition delta vs direct DayAhead MAE: `{comparison.get('decomposition_delta_vs_direct_percent')}` percent.
- Reconciled delta vs direct DayAhead MAE: `{comparison.get('reconciled_delta_vs_direct_percent')}` percent.
- No API, devices, runtime writes, spot-price features, old physical_balance target, flow/A61/capacity features, model binaries or large raw prediction dumps.
"""


def json_report(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(json_safe(payload), indent=2, sort_keys=True)}\n```\n"


def markdown_table(title: str, rows: object) -> str:
    rows = list(rows) if isinstance(rows, list) else []
    if not rows:
        return f"# {title}\n\nNo rows.\n"
    headers = list(rows[0].keys())
    lines = [f"# {title}", "", "| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(fmt_cell(row.get(header)) for header in headers) + " |")
    return "\n".join(lines) + "\n"


def write_csv(path: Path, rows: object) -> str:
    rows = list(rows) if isinstance(rows, list) else []
    if not rows:
        path.write_text("")
        return str(path)
    headers = list(rows[0].keys())
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({header: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value for header, value in row.items()})
    return str(path)


def fmt_cell(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return ""
    return str(value)


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def require_table(conn: sqlite3.Connection, table: str) -> None:
    if not p0054k.table_exists(conn, table):
        raise RuntimeError(f"missing required table: {table}")


def main() -> None:
    result = run_p0055a_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
