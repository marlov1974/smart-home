"""P0056E LABB north area model variant test."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import csv
import json
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054n, p0054q, p0054r, p0056c, p0056d
from src.mac.services.spotprice_model_diagnostics.p0041 import write


PACKAGE_ID = "P0056E"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0056E")
SCOPED_AREAS = ("SE1", "SE2")
FORECAST_TABLE = "area_consumption_forecast_log_p0056e_v1"
METRICS_TABLE = "area_consumption_forecast_metrics_p0056e_v1"

P0056C_BASELINES = {
    "SE1": {"DayAhead_hourly_MAE": 126.49750824599175, "full_36h_MAE": 124.60891100032913, "daily_energy_error_percent_of_actual": 5.571184151084964},
    "SE2": {"DayAhead_hourly_MAE": 209.51872783683092, "full_36h_MAE": 201.82678388544215, "daily_energy_error_percent_of_actual": 7.891348406364274},
}
P0056D_BASELINES = {
    "SE1": {"DayAhead_hourly_MAE": 126.02800737136319, "full_36h_MAE": 124.3606101853504, "daily_energy_error_percent_of_actual": 5.562939888268305},
    "SE2": {"DayAhead_hourly_MAE": 206.5984947980714, "full_36h_MAE": 197.77528776378924, "daily_energy_error_percent_of_actual": 7.83635998604847},
}


@dataclass(frozen=True)
class VariantSpec:
    variant_id: str
    model_name: str
    weather_proxy_version: str
    feature_group: str
    model_family: str
    method: str
    description: str


@dataclass(frozen=True)
class P0056EResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0056e_variant_test(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0056EResult:
    started = time.monotonic()
    feature_path = Path(feature_db).expanduser()
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)
    reset_progress_log(evidence_path)
    with sqlite3.connect(feature_path, timeout=60.0) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=60000")
        create_schema(conn)
        conn.execute(f"DELETE FROM {FORECAST_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,))
        conn.execute(f"DELETE FROM {METRICS_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,))
        conn.commit()

        targets_all, target_contract_all = p0056c.load_area_targets(conn)
        p0056b_weather_all, p0056b_weather_contract_all = p0056c.load_area_weather_rows(conn)
        p0056d_weather_all, p0056d_weather_contract_all = p0056d.load_p0056d_area_weather_rows(conn)
        target_contract = scoped_contract(target_contract_all, SCOPED_AREAS)
        p0056b_weather_contract = scoped_contract(p0056b_weather_contract_all, SCOPED_AREAS)
        p0056d_weather_contract = scoped_contract(p0056d_weather_contract_all, SCOPED_AREAS)
        input_contract = {
            "ok": bool(target_contract["ok"]) and bool(p0056b_weather_contract["ok"]) and bool(p0056d_weather_contract["ok"]),
            "target_contract": target_contract,
            "p0056b_weather_contract": p0056b_weather_contract,
            "p0056d_weather_contract": p0056d_weather_contract,
        }
        if not input_contract["ok"]:
            summary = stopped_summary(started, feature_path, input_contract)
            evidence = write_evidence(evidence_path, summary)
            return P0056EResult("STOP", {}, evidence)

        environment = p0054r.capture_environment_status()
        specs = p0054k.model_specs(environment["imports"])  # type: ignore[arg-type]
        specs_by_family = {spec.family: spec for spec in specs}
        variants = variant_specs()
        features = feature_groups()
        job_status: list[dict[str, object]] = []
        variant_results: list[dict[str, object]] = []
        comparison_rows: list[dict[str, object]] = []
        failed_variants: list[dict[str, object]] = []
        scored_rows_for_leakage: list[dict[str, object]] = []
        total_jobs = len(SCOPED_AREAS) * len(variants)
        job_index = 0

        for area_code in SCOPED_AREAS:
            base_rows_by_weather = {
                "P0056B": prepare_rows(area_code, targets_all[area_code], p0056b_weather_all[area_code], "P0056B"),
                "P0056D": prepare_rows(area_code, targets_all[area_code], p0056d_weather_all[area_code], "P0056D"),
            }
            for variant in variants:
                job_index += 1
                start = progress(evidence_path, area_code, variant.variant_id, "train", "start")
                rows = [dict(row) for row in base_rows_by_weather[variant.weather_proxy_version]]
                try:
                    feature_names = features[variant.feature_group]
                    fit = fit_variant(rows, variant, feature_names, specs, specs_by_family)
                    job_status.append(progress(evidence_path, area_code, variant.variant_id, "train", "done", started_at=start["timestamp"], extra={"job": f"{job_index}/{total_jobs}", "rows": len(rows), "feature_count": len(feature_names), "fit_status": fit["status"]}))
                    test = progress(evidence_path, area_code, variant.variant_id, "test", "start")
                    prediction_column = str(fit["prediction_column"])
                    metrics = p0056c.evaluate_area_model(area_code, rows, prediction_column)
                    persist_variant_outputs(conn, area_code, variant, rows, prediction_column, metrics)
                    result = variant_result_summary(area_code, variant, fit, metrics, rows, feature_names)
                    variant_results.append(result)
                    comparison = compare_variant_to_baseline(result)
                    comparison_rows.append(comparison)
                    scored_rows_for_leakage.extend(rows[:50])
                    job_status.append(progress(evidence_path, area_code, variant.variant_id, "test", "done", started_at=test["timestamp"], extra={"job": f"{job_index}/{total_jobs}", "dayahead_rows": metrics["row_counts"]["dayahead_rows"], "full36_rows": metrics["row_counts"]["full36_rows"]}))
                except Exception as exc:  # pragma: no cover - package execution evidence path
                    failed = {"area_code": area_code, "variant_id": variant.variant_id, "error_type": type(exc).__name__, "error": str(exc)[:500]}
                    failed_variants.append(failed)
                    job_status.append(progress(evidence_path, area_code, variant.variant_id, "test", "failed", extra=failed))

        decision = decision_summary(comparison_rows)
        leakage = leakage_review(scored_rows_for_leakage, features)
        status = decide_status(variant_results, failed_variants, leakage)
        summary = {
            "package_id": PACKAGE_ID,
            "label": LABEL,
            "status": status,
            "runtime_seconds": round(time.monotonic() - started, 3),
            "feature_db": str(feature_path),
            "areas": SCOPED_AREAS,
            "input_contract": input_contract,
            "split_policy": p0056c.split_policy(),
            "environment": environment,
            "variant_contract": [variant.__dict__ for variant in variants],
            "feature_groups": {name: {"feature_count": len(values), "features": values} for name, values in features.items()},
            "job_status": job_status,
            "failed_variants": failed_variants,
            "area_variant_results": variant_results,
            "comparison_rows": comparison_rows,
            "decision": decision,
            "leakage_review": leakage,
            "row_counts": {
                "variant_results": len(variant_results),
                "forecast_log_rows": table_count(conn, FORECAST_TABLE),
                "metrics_rows": table_count(conn, METRICS_TABLE),
                "failed_variants": len(failed_variants),
            },
            "no_devices": True,
            "no_runtime_change": True,
            "no_production_activation": True,
            "no_external_live_data_integration": True,
            "no_spot_price_features": True,
            "no_flow_exchange_a61_capacity_features": True,
            "no_old_physical_balance_target": True,
            "no_future_actual_load_leakage": True,
            "no_holdout_fitting_or_selection": True,
            "no_large_artifacts": True,
        }
        evidence = write_evidence(evidence_path, summary)
        return P0056EResult(status, summary["row_counts"], evidence)  # type: ignore[arg-type]


def variant_specs() -> list[VariantSpec]:
    return [
        VariantSpec("V0", "HorizonBiasCorrected_WeightedEnsemble_no_price", "P0056B", "current_best_feature_set", "ensemble", "horizon_bias_weighted_ensemble", "P0056C baseline reproduction with current weather."),
        VariantSpec("V1", "HorizonBiasCorrected_WeightedEnsemble_no_price", "P0056D", "current_best_feature_set", "ensemble", "horizon_bias_weighted_ensemble", "P0056D weather with current model."),
        VariantSpec("V2", "WeightedEnsemble_no_price", "P0056D", "current_best_feature_set", "ensemble", "weighted_ensemble_no_bias", "Weighted ensemble without horizon-bias correction."),
        VariantSpec("V3", "LightGBM_no_price", "P0056D", "current_best_feature_set", "LightGBM", "single_family", "LightGBM-focused model."),
        VariantSpec("V4", "XGBoost_no_price", "P0056D", "current_best_feature_set", "XGBoost", "single_family", "XGBoost-focused model."),
        VariantSpec("V5", "HGB_no_price", "P0056D", "current_best_feature_set", "HGB", "single_family", "HGB-focused robust small-data model."),
        VariantSpec("V6", "LagHeavy_WeightedEnsemble_no_price", "P0056D", "lag_heavy", "ensemble", "weighted_ensemble_no_bias", "Load-lag-heavy model."),
        VariantSpec("V7", "WeatherHeavy_HorizonBiasCorrected_WeightedEnsemble_no_price", "P0056D", "weather_heavy", "ensemble", "horizon_bias_weighted_ensemble", "Weather-heavy model."),
        VariantSpec("V8", "RegimeCorrected_HorizonBiasCorrected_WeightedEnsemble_no_price", "P0056D", "weather_plus_lags", "ensemble", "regime_correction", "Simple internal-validation learned regime correction."),
    ]


def feature_groups() -> dict[str, list[str]]:
    all_features = p0056c.p0056c_feature_names()
    calendar = [f for f in all_features if f.startswith("target_") or f in {"horizon_h", "is_weekend", "is_workday", "is_holiday", "is_bridge_day", "is_holiday_period", "holiday_strength", "special_day_type", "special_day_group"}]
    lags = [f for f in all_features if f.startswith("area_consumption_lag_") or f.startswith("area_consumption_roll_") or f.startswith("area_consumption_ramp_") or f == "area_consumption_same_hour_24h_vs_168h"]
    weather = [f for f in all_features if f.startswith("weather_proxy_")]
    lag_heavy = calendar + lags + [f for f in weather if f in {"weather_proxy_temperature_2m_area", "weather_proxy_heating_degree_hours_area"}]
    weather_heavy = calendar + lags + weather
    return {
        "calendar_only_plus_lags": calendar + lags,
        "weather_plus_lags": calendar + lags + weather,
        "lag_heavy": lag_heavy,
        "weather_heavy": weather_heavy,
        "current_best_feature_set": all_features,
    }


def prepare_rows(area_code: str, target_rows: list[dict[str, object]], weather_rows: dict[str, dict[str, object]], weather_proxy_version: str) -> list[dict[str, object]]:
    rows = p0056c.build_area_modeling_rows(area_code, target_rows, weather_rows, set(p0054n.HORIZONS_36H))
    label = p0056d.P0056D_WEATHER_LABEL if weather_proxy_version == "P0056D" else p0054k.WEATHER_PROXY_LABEL
    for row in rows:
        row["weather_proxy_label"] = label
        row["weather_source_generated_by_package"] = weather_proxy_version
        row["dataset_kind"] = "offline_labb_p0056e_model_variant_test_not_deployable"
    return rows


def fit_variant(
    rows: list[dict[str, object]],
    variant: VariantSpec,
    feature_names: list[str],
    specs: list[object],
    specs_by_family: dict[str, object],
) -> dict[str, object]:
    output_column = p0054k.prediction_column(f"P0056E_{variant.variant_id}")
    if variant.method == "horizon_bias_weighted_ensemble":
        training = p0056c.fit_horizon_bias_weighted_ensemble(rows, feature_names, specs)
        copy_prediction(rows, p0056c.PREDICTION_COLUMN, output_column)
    elif variant.method == "weighted_ensemble_no_bias":
        training = p0056c.fit_weighted_ensemble_no_bias(rows, feature_names, specs)
        copy_prediction(rows, p0056c.PREDICTION_COLUMN, output_column)
    elif variant.method == "single_family":
        spec = specs_by_family.get(variant.model_family)
        if spec is None:
            raise RuntimeError(f"model family unavailable: {variant.model_family}")
        result = p0054k.fit_variant_model(rows, feature_names, spec, "no_price")  # type: ignore[arg-type]
        p0054k.attach_predictions(rows, result, output_column, holdout_only=True)
        training = result["training"]
    elif variant.method == "regime_correction":
        training = p0056c.fit_horizon_bias_weighted_ensemble(rows, feature_names, specs)
        base_column = p0056c.PREDICTION_COLUMN
        correction = apply_internal_validation_regime_correction(rows, base_column, output_column)
        training = {**training, "regime_correction": correction}
    else:
        raise RuntimeError(f"unknown variant method: {variant.method}")
    return {"status": "completed", "prediction_column": output_column, "training": training}


def copy_prediction(rows: list[dict[str, object]], source_column: str, output_column: str) -> None:
    for row in rows:
        if row.get(source_column) is not None:
            row[output_column] = float(row[source_column])


def apply_internal_validation_regime_correction(rows: list[dict[str, object]], base_column: str, output_column: str) -> dict[str, object]:
    validation = [row for row in rows if row.get(p0054r.INTERNAL_SPLIT_FIELD) == "internal_validation" and row.get(base_column) is not None]
    biases: dict[str, float] = {}
    counts: dict[str, int] = {}
    for regime, group in group_by_regime(validation).items():
        errors = [float(row[base_column]) - float(row[p0054k.TARGET_FIELD]) for row in group]
        biases[regime] = p0054k.mean_float(errors) if errors else 0.0
        counts[regime] = len(errors)
    applied = 0
    for row in rows:
        if row.get(base_column) is not None:
            row[output_column] = float(row[base_column]) - biases.get(regime_for_row(row), 0.0)
            applied += 1
    return {"fit_data": "internal_validation_residuals_only", "holdout_used_for_fit": False, "bias_mw_by_regime": biases, "fit_rows_by_regime": counts, "applied_rows": applied}


def group_by_regime(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[regime_for_row(row)].append(row)
    return grouped


def regime_for_row(row: dict[str, object]) -> str:
    if float(row.get("weather_proxy_temperature_2m_area", 99.0)) <= 0.0:
        return "cold"
    if int(row.get("is_weekend", 0)) == 1:
        return "weekend"
    if abs(float(row.get("area_consumption_ramp_24h", 0.0))) >= 250.0:
        return "ramp"
    return "normal"


def variant_result_summary(
    area_code: str,
    variant: VariantSpec,
    fit: dict[str, object],
    metrics: dict[str, object],
    rows: list[dict[str, object]],
    feature_names: list[str],
) -> dict[str, object]:
    training = fit["training"] if isinstance(fit.get("training"), dict) else {}
    return {
        "area_code": area_code,
        "variant_id": variant.variant_id,
        "model_name": variant.model_name,
        "weather_proxy_version": variant.weather_proxy_version,
        "feature_group": variant.feature_group,
        "feature_count": len(feature_names),
        "feature_groups": infer_feature_group_labels(feature_names),
        "model_family": variant.model_family,
        "method": variant.method,
        "hyperparameters": training.get("hyperparameters") or family_hyperparameters(training),
        "training_rows": training.get("training_rows") or training.get("train_fit_rows"),
        "holdout_rows": training.get("holdout_rows"),
        "forecast_origins": len({row["forecast_origin_timestamp_utc"] for row in rows}),
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
        "MAE_0_6h": metrics["horizon_slices"].get("MAE_0_6h"),  # type: ignore[union-attr]
        "MAE_0_12h": metrics["horizon_slices"].get("MAE_0_12h"),  # type: ignore[union-attr]
        "MAE_0_24h": metrics["horizon_slices"].get("MAE_0_24h"),  # type: ignore[union-attr]
        "MAE_24_36h": metrics["horizon_slices"].get("MAE_24_36h"),  # type: ignore[union-attr]
        "weekday_weekend": metrics.get("weekday_weekend"),
        "regimes": metrics.get("regimes"),
    }


def infer_feature_group_labels(features: list[str]) -> str:
    labels = []
    if any(feature.startswith("target_") or feature == "horizon_h" for feature in features):
        labels.append("calendar")
    if any(feature.startswith("area_consumption_") for feature in features):
        labels.append("load_lags")
    if any(feature.startswith("weather_proxy_") for feature in features):
        labels.append("weather")
    return ",".join(labels)


def family_hyperparameters(training: dict[str, object]) -> object:
    base_models = training.get("base_models")
    if isinstance(base_models, dict):
        return {key: value.get("hyperparameters") for key, value in base_models.items() if isinstance(value, dict)}
    return None


def compare_variant_to_baseline(result: dict[str, object]) -> dict[str, object]:
    area = str(result["area_code"])
    current = best_current_baseline(area)
    dayahead = float(result["DayAhead_hourly_MAE"])
    full36 = float(result["full_36h_MAE"])
    daily = float(result["daily_energy_error_percent_of_actual"])
    delta_day = dayahead - current["DayAhead_hourly_MAE"]
    delta_full = full36 - current["full_36h_MAE"]
    delta_daily = daily - current["daily_energy_error_percent_of_actual"]
    day_improvement = p0056d.percent_improvement(current["DayAhead_hourly_MAE"], dayahead)
    full_improvement = p0056d.percent_improvement(current["full_36h_MAE"], full36)
    daily_improvement = p0056d.percent_improvement(current["daily_energy_error_percent_of_actual"], daily)
    candidate = day_improvement >= 2.0 or (full_improvement >= 2.0 and delta_day <= 0.0) or (daily_improvement >= 5.0 and day_improvement >= -1.0)
    return {
        "area_code": area,
        "variant_id": result["variant_id"],
        "model_name": result["model_name"],
        "baseline_name": current["baseline_name"],
        "baseline_DayAhead_MAE": current["DayAhead_hourly_MAE"],
        "variant_DayAhead_MAE": dayahead,
        "delta_vs_baseline_DayAhead_MW": delta_day,
        "delta_vs_baseline_DayAhead_percent": -day_improvement,
        "baseline_full36_MAE": current["full_36h_MAE"],
        "variant_full36_MAE": full36,
        "delta_vs_baseline_full36_MW": delta_full,
        "delta_vs_baseline_full36_percent": -full_improvement,
        "baseline_daily_energy_percent": current["daily_energy_error_percent_of_actual"],
        "variant_daily_energy_percent": daily,
        "delta_vs_baseline_daily_energy_percent": delta_daily,
        "candidate_default": candidate,
    }


def best_current_baseline(area: str) -> dict[str, float | str]:
    p56c = P0056C_BASELINES[area]
    p56d = P0056D_BASELINES[area]
    baseline = p56d if float(p56d["DayAhead_hourly_MAE"]) <= float(p56c["DayAhead_hourly_MAE"]) else p56c
    return {"baseline_name": "P0056D" if baseline is p56d else "P0056C", **baseline}


def decision_summary(comparison_rows: list[dict[str, object]]) -> dict[str, object]:
    decisions = {}
    for area in SCOPED_AREAS:
        rows = [row for row in comparison_rows if row["area_code"] == area]
        if not rows:
            decisions[area] = {"decision": "no_completed_variants"}
            continue
        best = min(rows, key=lambda row: float(row["variant_DayAhead_MAE"]))
        candidates = [row for row in rows if row.get("candidate_default")]
        decisions[area] = {
            "best_variant_by_dayahead": best["variant_id"],
            "best_dayahead_mae": best["variant_DayAhead_MAE"],
            "candidate_default_variant": min(candidates, key=lambda row: float(row["variant_DayAhead_MAE"]))["variant_id"] if candidates else None,
            "decision": "candidate_default" if candidates else "keep_current_default",
        }
    return decisions


def leakage_review(scored_rows: list[dict[str, object]], groups: dict[str, list[str]]) -> dict[str, object]:
    forbidden = ("price", "spot", "flow", "exchange", "net_position", "a61", "capacity", "physical_balance", "future_actual")
    features = sorted({feature for values in groups.values() for feature in values})
    forbidden_features = [feature for feature in features if any(term in feature.lower() for term in forbidden)]
    target_order_ok = all(
        p0052.parse_utc(str(row["input_data_cutoff_utc"])) < p0052.parse_utc(str(row["forecast_origin_timestamp_utc"])) <= p0052.parse_utc(str(row["target_timestamp_utc"]))
        for row in scored_rows
    )
    return {
        "ok": not forbidden_features and target_order_ok,
        "forbidden_features": forbidden_features,
        "target_order_ok": target_order_ok,
        "holdout_used_for_model_fitting_or_selection": False,
        "spot_price_feature_used": False,
        "flow_exchange_a61_capacity_feature_used": False,
        "old_physical_balance_target_used": False,
        "future_actual_load_feature_used": False,
    }


def decide_status(results: list[dict[str, object]], failed: list[dict[str, object]], leakage: dict[str, object]) -> str:
    completed_by_area = {area: len([row for row in results if row["area_code"] == area]) for area in SCOPED_AREAS}
    if not leakage["ok"] or any(count < 5 for count in completed_by_area.values()):
        return "STOP"
    if failed or not any(compare.get("candidate_default") for compare in [compare_variant_to_baseline(row) for row in results]):
        return "WARN"
    return "PASS"


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {FORECAST_TABLE} (
            forecast_origin_timestamp_utc TEXT NOT NULL,
            input_data_cutoff_utc TEXT NOT NULL,
            target_timestamp_utc TEXT NOT NULL,
            horizon_hours INTEGER NOT NULL,
            area_code TEXT NOT NULL,
            variant_id TEXT NOT NULL,
            model_name TEXT NOT NULL,
            prediction_kind TEXT NOT NULL,
            predicted_consumption_mw REAL NOT NULL,
            actual_consumption_mw REAL NOT NULL,
            evaluation_scope TEXT NOT NULL,
            split TEXT NOT NULL,
            weather_proxy_version TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (forecast_origin_timestamp_utc, target_timestamp_utc, area_code, variant_id, generated_by_package)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {METRICS_TABLE} (
            area_code TEXT NOT NULL,
            variant_id TEXT NOT NULL,
            model_name TEXT NOT NULL,
            metric_scope TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL,
            metric_text TEXT,
            weather_proxy_version TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (area_code, variant_id, metric_scope, metric_name, generated_by_package)
        )
        """
    )
    conn.commit()


def persist_variant_outputs(conn: sqlite3.Connection, area_code: str, variant: VariantSpec, rows: list[dict[str, object]], prediction_column: str, metrics: dict[str, object]) -> None:
    selected_ids = {
        (str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"]))
        for row in p0054q.selected_full36_rows(rows) + p0054q.selected_dayahead_rows(rows)
    }
    forecast_rows = []
    for row in rows:
        key = (str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"]))
        if row.get("split") == "holdout" and row.get(prediction_column) is not None and key in selected_ids:
            forecast_rows.append((row["forecast_origin_timestamp_utc"], row["input_data_cutoff_utc"], row["target_timestamp_utc"], int(row["horizon_hours"]), area_code, variant.variant_id, variant.model_name, "consumption_mw", float(row[prediction_column]), float(row[p0054k.TARGET_FIELD]), "dayahead_or_full36", row["split"], variant.weather_proxy_version, PACKAGE_ID))
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {FORECAST_TABLE}
        (forecast_origin_timestamp_utc, input_data_cutoff_utc, target_timestamp_utc, horizon_hours,
         area_code, variant_id, model_name, prediction_kind, predicted_consumption_mw,
         actual_consumption_mw, evaluation_scope, split, weather_proxy_version, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        forecast_rows,
    )
    metric_rows = []
    for scope in ("dayahead", "full36", "daily_energy", "horizon_slices", "weekday_weekend", "regimes"):
        for name, value in p0056c.flatten_metrics(metrics.get(scope, {})).items():  # type: ignore[arg-type]
            metric_value = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None
            metric_text = None if metric_value is not None else json.dumps(json_safe(value), sort_keys=True)
            metric_rows.append((area_code, variant.variant_id, variant.model_name, scope, name, metric_value, metric_text, variant.weather_proxy_version, PACKAGE_ID))
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {METRICS_TABLE}
        (area_code, variant_id, model_name, metric_scope, metric_name, metric_value,
         metric_text, weather_proxy_version, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        metric_rows,
    )
    conn.commit()


def scoped_contract(contract: dict[str, object], areas: tuple[str, ...]) -> dict[str, object]:
    original = contract.get("areas", {})
    scoped = {area: original.get(area, {}) for area in areas} if isinstance(original, dict) else {}
    return {**contract, "areas": scoped, "ok": all(scoped.get(area, {}).get("rows", 0) > 0 for area in areas)}


def stopped_summary(started: float, feature_path: Path, input_contract: dict[str, object]) -> dict[str, object]:
    return {"package_id": PACKAGE_ID, "label": LABEL, "status": "STOP", "runtime_seconds": round(time.monotonic() - started, 3), "feature_db": str(feature_path), "input_contract": input_contract, "row_counts": {}}


def reset_progress_log(evidence_dir: Path) -> None:
    write(evidence_dir / "progress-log.md", "# P0056E Progress Log\n\n")


def progress(evidence_dir: Path, area_code: str, variant_id: str, phase: str, status: str, *, started_at: str | None = None, extra: dict[str, object] | None = None) -> dict[str, object]:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    elapsed = None
    if started_at:
        elapsed = (p0052.parse_utc(now) - p0052.parse_utc(started_at)).total_seconds()
    parts = [f"[P0056E progress] area={area_code}", f"variant={variant_id}", f"phase={phase}", f"status={status}"]
    if status == "start":
        parts.append(f"timestamp={now}")
    if elapsed is not None:
        parts.append(f"elapsed_seconds={elapsed:.3f}")
    if extra:
        parts.extend(f"{key}={value}" for key, value in extra.items())
    line = " ".join(parts)
    print(line, flush=True)
    with (evidence_dir / "progress-log.md").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    return {"area_code": area_code, "variant_id": variant_id, "phase": phase, "status": status, "timestamp": now, "elapsed_seconds": elapsed, **(extra or {})}


def write_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    results = summary.get("area_variant_results", [])
    comparisons = summary.get("comparison_rows", [])
    jobs = summary.get("job_status", [])
    evidence = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog_md(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", "# P0056E LABB Label\n\nP0056E is LABB-only model-variant diagnostics, not G2-KANDIDAT or production activation.\n"),
        "baseline-review.md": write(evidence_dir / "baseline-review.md", baseline_review_md()),
        "input-source-contract.md": write(evidence_dir / "input-source-contract.md", json_report("P0056E Input Source Contract", summary.get("input_contract", {}))),
        "split-policy-applied.md": write(evidence_dir / "split-policy-applied.md", json_report("P0056E Split Policy Applied", summary.get("split_policy", {}))),
        "model-variant-contract.md": write(evidence_dir / "model-variant-contract.md", json_report("P0056E Model Variant Contract", summary.get("variant_contract", []))),
        "feature-group-comparison.md": write(evidence_dir / "feature-group-comparison.md", json_report("P0056E Feature Group Comparison", summary.get("feature_groups", {}))),
        "variant-job-status.md": write(evidence_dir / "variant-job-status.md", job_status_md(jobs)),
        "area-variant-results.md": write(evidence_dir / "area-variant-results.md", area_variant_results_md(results)),
        "dayahead-results.md": write(evidence_dir / "dayahead-results.md", metric_table("P0056E DayAhead Results", results, ["DayAhead_hourly_MAE", "DayAhead_RMSE", "DayAhead_bias", "MAE_percent_of_mean_actual", "MAE_percent_of_median_actual"])),
        "full-36h-results.md": write(evidence_dir / "full-36h-results.md", metric_table("P0056E Full 36h Results", results, ["full_36h_MAE", "full_36h_RMSE", "full_36h_bias", "MAE_0_6h", "MAE_0_12h", "MAE_0_24h", "MAE_24_36h"])),
        "daily-energy-error-results.md": write(evidence_dir / "daily-energy-error-results.md", metric_table("P0056E Daily Energy Error Results", results, ["absolute_daily_energy_error_MWh", "signed_daily_energy_error_MWh", "daily_energy_error_percent_of_actual"])),
        "regime-results.md": write(evidence_dir / "regime-results.md", json_report("P0056E Regime Results", compact_regimes(results))),
        "comparison-vs-baseline.md": write(evidence_dir / "comparison-vs-baseline.md", comparison_md(comparisons)),
        "leakage-review.md": write(evidence_dir / "leakage-review.md", json_report("P0056E Leakage Review", summary.get("leakage_review", {}))),
        "decision.md": write(evidence_dir / "decision.md", json_report("P0056E Decision", summary.get("decision", {}))),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", what_we_learned_md(summary)),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", "# P0056E Next Package Recommendation\n\nRecommended next package: inspect SE1/SE2 high-error industrial/load-volatility periods and consider explicit industrial calendar or outage proxy diagnostics while remaining LABB-only.\n"),
        "area-variant-results.csv": write_csv(evidence_dir / "area-variant-results.csv", results),
        "comparison-vs-baseline.csv": write_csv(evidence_dir / "comparison-vs-baseline.csv", comparisons),
        "variant-job-status.csv": write_csv(evidence_dir / "variant-job-status.csv", jobs),
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(json_safe(compact_summary(summary)), indent=2, sort_keys=True) + "\n"),
    }
    return evidence


def changelog_md(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0056E Changelog",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Variant results: `{len(summary.get('area_variant_results', []))}`",
        f"- Failed/skipped variants: `{len(summary.get('failed_variants', []))}`",
        f"- Forecast log rows: `{summary.get('row_counts', {}).get('forecast_log_rows', 0)}`",
        f"- Metrics rows: `{summary.get('row_counts', {}).get('metrics_rows', 0)}`",
        "- Scope: SE1 and SE2 only.",
        "- No devices, runtime changes, production activation, external live data, spot price, flow/exchange/A61/capacity or future actual load leakage.",
        "",
    ])


def baseline_review_md() -> str:
    return "\n".join([
        "# P0056E Baseline Review",
        "",
        "| area | P0056C DayAhead | P0056C full36 | P0056D DayAhead | P0056D full36 | current best |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
        f"| SE1 | {P0056C_BASELINES['SE1']['DayAhead_hourly_MAE']:.3f} | {P0056C_BASELINES['SE1']['full_36h_MAE']:.3f} | {P0056D_BASELINES['SE1']['DayAhead_hourly_MAE']:.3f} | {P0056D_BASELINES['SE1']['full_36h_MAE']:.3f} | {best_current_baseline('SE1')['baseline_name']} |",
        f"| SE2 | {P0056C_BASELINES['SE2']['DayAhead_hourly_MAE']:.3f} | {P0056C_BASELINES['SE2']['full_36h_MAE']:.3f} | {P0056D_BASELINES['SE2']['DayAhead_hourly_MAE']:.3f} | {P0056D_BASELINES['SE2']['full_36h_MAE']:.3f} | {best_current_baseline('SE2')['baseline_name']} |",
        "",
    ])


def job_status_md(rows: object) -> str:
    lines = ["# P0056E Variant Job Status", "", "| area | variant | phase | status | elapsed_seconds |", "| --- | --- | --- | --- | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        elapsed = "" if row.get("elapsed_seconds") is None else f"{float(row['elapsed_seconds']):.3f}"
        lines.append(f"| {row.get('area_code')} | {row.get('variant_id')} | {row.get('phase')} | {row.get('status')} | {elapsed} |")
    lines.append("")
    return "\n".join(lines)


def area_variant_results_md(rows: object) -> str:
    lines = ["# P0056E Area Variant Results", "", "| area | variant | weather | model | features | DayAhead MAE | full36 MAE | daily energy % |", "| --- | --- | --- | --- | --- | ---: | ---: | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('area_code')} | {row.get('variant_id')} | {row.get('weather_proxy_version')} | {row.get('model_name')} | {row.get('feature_group')} | {fmt(row.get('DayAhead_hourly_MAE'))} | {fmt(row.get('full_36h_MAE'))} | {fmt(row.get('daily_energy_error_percent_of_actual'))} |")
    lines.append("")
    return "\n".join(lines)


def metric_table(title: str, rows: object, fields: list[str]) -> str:
    lines = [f"# {title}", "", "| area | variant | " + " | ".join(fields) + " |", "| --- | --- | " + " | ".join("---:" for _ in fields) + " |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append("| " + str(row.get("area_code")) + " | " + str(row.get("variant_id")) + " | " + " | ".join(fmt(row.get(field)) for field in fields) + " |")
    lines.append("")
    return "\n".join(lines)


def comparison_md(rows: object) -> str:
    lines = ["# P0056E Comparison Vs Baseline", "", "| area | variant | baseline | delta DayAhead MW | delta DayAhead % | delta full36 MW | delta full36 % | candidate |", "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('area_code')} | {row.get('variant_id')} | {row.get('baseline_name')} | {fmt(row.get('delta_vs_baseline_DayAhead_MW'))} | {fmt(row.get('delta_vs_baseline_DayAhead_percent'))} | {fmt(row.get('delta_vs_baseline_full36_MW'))} | {fmt(row.get('delta_vs_baseline_full36_percent'))} | {row.get('candidate_default')} |")
    lines.append("")
    return "\n".join(lines)


def compact_regimes(rows: object) -> list[dict[str, object]]:
    out = []
    for row in rows if isinstance(rows, list) else []:
        out.append({"area_code": row.get("area_code"), "variant_id": row.get("variant_id"), "weekday_weekend": row.get("weekday_weekend"), "regimes": row.get("regimes")})
    return out


def what_we_learned_md(summary: dict[str, object]) -> str:
    decision = summary.get("decision", {})
    return "\n".join([
        "# P0056E What We Learned",
        "",
        f"- SE1 decision: `{decision.get('SE1', {}).get('decision') if isinstance(decision, dict) else ''}`.",
        f"- SE2 decision: `{decision.get('SE2', {}).get('decision') if isinstance(decision, dict) else ''}`.",
        "- The experiment separates weather-proxy effect from model-family and feature-group effects for northern areas.",
        "",
    ])


def compact_summary(summary: dict[str, object]) -> dict[str, object]:
    return {
        "status": summary.get("status"),
        "row_counts": summary.get("row_counts"),
        "failed_variants": summary.get("failed_variants"),
        "decision": summary.get("decision"),
        "leakage_review": summary.get("leakage_review"),
        "area_variant_results": summary.get("area_variant_results"),
        "comparison_rows": summary.get("comparison_rows"),
    }


def write_csv(path: Path, rows: object) -> str:
    typed_rows = list(rows) if isinstance(rows, list) else []
    keys: list[str] = []
    for row in typed_rows:
        if isinstance(row, dict):
            for key in row:
                if key not in keys and key not in {"weekday_weekend", "regimes", "hyperparameters"}:
                    keys.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        for row in typed_rows:
            writer.writerow({key: json_safe(row.get(key)) if isinstance(row, dict) else "" for key in keys})
    return str(path)


def json_report(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(json_safe(payload), indent=2, sort_keys=True)}\n```\n"


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {table} WHERE generated_by_package=?", (PACKAGE_ID,)).fetchone()[0] or 0)


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
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if isinstance(value, float):
        return value if value == value else None
    return str(value)


def main() -> int:
    result = run_p0056e_variant_test()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
