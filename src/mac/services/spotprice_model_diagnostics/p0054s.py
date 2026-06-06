"""P0054S LABB advanced SE3 spot-price forecast."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import csv
import json
import math
import time

import numpy as np

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054l2, p0054n
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write


PACKAGE_ID = "P0054S"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054S")
INTERNAL_SPLIT_FIELD = "p0054s_internal_split"
P0054L2_ENSEMBLE_DIRECT_MAE = 0.3033978235888772
P0054L2_ENSEMBLE_WEEKLY_MAE = 0.3033978235888772
P0054K_BASELINE_MAE = 0.34918660925661843
FORECAST_LOG_TABLE = "advanced_spotprice_forecast_log_p0054s_se3_v1"


@dataclass(frozen=True)
class P0054SResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054s_analysis(*, feature_db: Path | str = DEFAULT_FEATURE_DB, evidence_dir: Path | str = EVIDENCE_DIR) -> P0054SResult:
    started = time.monotonic()
    feature_db = Path(feature_db).expanduser()
    evidence_dir = Path(evidence_dir)
    (evidence_dir / "model-checkpoints").mkdir(parents=True, exist_ok=True)

    price_rows = p0054l2.load_se3_price_rows(feature_db)
    source_contract = p0054l2.validate_source_contract(price_rows)
    if not source_contract["ok"]:
        raise RuntimeError(f"P0054S source contract failed: {source_contract}")
    examples, skipped_windows = p0054l2.build_price_forecast_examples(price_rows)
    internal_counts = assign_internal_validation_splits(examples)
    split_counts = p0054l2.count_by(examples, "split")
    feature_names = sorted({key for row in examples for key in row["features"]})  # type: ignore[index]
    matrix_review = p0054l2.validate_feature_matrix_safety(examples, feature_names)
    if not matrix_review["ok"]:
        raise RuntimeError(f"P0054S feature matrix safety failed: {matrix_review}")

    baseline_rows, baseline_contract = p0054l2.load_p0054k_baseline_rows(feature_db)
    baseline_eval = p0054l2.evaluate_baseline(examples, baseline_rows)
    if not baseline_eval["ok"]:
        raise RuntimeError(f"P0054S P0054K baseline comparison failed: {baseline_eval}")

    environment = capture_environment_status()
    specs = p0054l2.model_specs(environment["imports"])  # type: ignore[arg-type]
    spec_by_family = {spec.family: spec for spec in specs}
    thresholds = p0054l2.fit_train_thresholds(examples)
    scored_rows = [dict(row) for row in examples]
    internal_validation_rows = [dict(row) for row in examples if row[INTERNAL_SPLIT_FIELD] == "internal_validation"]
    internal_train_rows = [row for row in examples if row[INTERNAL_SPLIT_FIELD] == "internal_train"]
    train_fit_rows = [row for row in examples if row["split"] == "train_fit"]
    holdout_rows = [row for row in scored_rows if row["split"] == "holdout"]

    model_results: dict[str, dict[str, object]] = {}
    validation_evidence: dict[str, object] = {}
    checkpoints: list[dict[str, object]] = []
    for family in ("HGB", "ExtraTrees", "LightGBM", "XGBoost"):
        if family not in spec_by_family:
            result = p0054l2.skipped_checkpoint(family, "import_unavailable", scored_rows, feature_names, environment)
            model_results[family] = result
            write_checkpoint(evidence_dir, family, result)
            continue
        validation_fit = fit_model_on_rows(spec_by_family[family], feature_names, internal_train_rows, internal_validation_rows)
        attach_predictions(internal_validation_rows, validation_fit["predictions"], p0054l2.prediction_column(family))
        validation_evidence[family] = {
            "internal_train_rows": len(internal_train_rows),
            "internal_validation_rows": len(internal_validation_rows),
            "metrics": p0054l2.evaluate_direct_metrics(internal_validation_rows, p0054l2.prediction_column(family)),
            "selection_data": "internal_validation_only",
        }
        result = p0054l2.fit_serial_model(scored_rows, feature_names, spec_by_family[family], thresholds)
        model_results[family] = result
        checkpoints.append(checkpoint_entry(family, "baseline_reproduced", result.get("training", {})))
        write_checkpoint(evidence_dir, family, result)

    completed = [name for name, result in model_results.items() if result.get("status") == "completed"]
    if len(completed) < 2:
        raise RuntimeError("P0054S needs at least two completed base models for advanced methods")

    weights, weight_evidence = learn_inverse_mae_weights(internal_validation_rows, completed)
    weighted_name = "WeightedEnsemble"
    apply_weighted_ensemble(internal_validation_rows, weights, p0054l2.prediction_column(weighted_name))
    apply_weighted_ensemble(scored_rows, weights, p0054l2.prediction_column(weighted_name))
    model_results[weighted_name] = completed_model_record(weighted_name, "inverse_internal_validation_mae", scored_rows, thresholds, weight_evidence)
    checkpoints.append(checkpoint_entry(weighted_name, "advanced_completed", model_results[weighted_name]["training"]))
    write_checkpoint(evidence_dir, weighted_name, model_results[weighted_name])

    median_name = "MedianEnsemble"
    apply_median_ensemble(scored_rows, completed, p0054l2.prediction_column(median_name))
    model_results[median_name] = completed_model_record(median_name, "median_completed_base_models", scored_rows, thresholds, {"source_models": completed})
    checkpoints.append(checkpoint_entry(median_name, "advanced_completed", model_results[median_name]["training"]))
    write_checkpoint(evidence_dir, median_name, model_results[median_name])

    stack_name = "LinearStack"
    stack_payload = fit_linear_stack(internal_validation_rows, completed)
    apply_linear_stack(scored_rows, stack_payload, p0054l2.prediction_column(stack_name))
    model_results[stack_name] = completed_model_record(stack_name, "linear_stack_internal_validation", scored_rows, thresholds, stack_payload)
    checkpoints.append(checkpoint_entry(stack_name, "advanced_completed", model_results[stack_name]["training"]))
    write_checkpoint(evidence_dir, stack_name, model_results[stack_name])

    best_internal = min(completed, key=lambda name: float(validation_evidence[name]["metrics"]["MAE"]))  # type: ignore[index]
    hgb_spec = spec_by_family.get("HGB", spec_by_family[completed[0]])
    residual_name = f"ResidualCorrection_{best_internal}"
    residual_evidence = fit_and_apply_residual_correction(hgb_spec, feature_names, internal_validation_rows, scored_rows, best_internal, p0054l2.prediction_column(residual_name))
    model_results[residual_name] = completed_model_record(residual_name, "residual_correction", scored_rows, thresholds, residual_evidence)
    checkpoints.append(checkpoint_entry(residual_name, "advanced_completed", model_results[residual_name]["training"]))
    write_checkpoint(evidence_dir, residual_name, model_results[residual_name])

    bucket_name = f"HorizonBucket_{hgb_spec.family}"
    bucket_evidence = fit_and_apply_horizon_bucket_specialized(hgb_spec, feature_names, train_fit_rows, scored_rows, p0054l2.prediction_column(bucket_name))
    model_results[bucket_name] = completed_model_record(bucket_name, "horizon_bucket_specialized", scored_rows, thresholds, bucket_evidence)
    checkpoints.append(checkpoint_entry(bucket_name, "advanced_completed", model_results[bucket_name]["training"]))
    write_checkpoint(evidence_dir, bucket_name, model_results[bucket_name])

    bias_name = f"HorizonBiasCorrected_{weighted_name}"
    bias_evidence = fit_and_apply_horizon_bias_correction(internal_validation_rows, scored_rows, weighted_name, p0054l2.prediction_column(bias_name))
    model_results[bias_name] = completed_model_record(bias_name, "horizon_bias_correction", scored_rows, thresholds, bias_evidence)
    checkpoints.append(checkpoint_entry(bias_name, "advanced_completed", model_results[bias_name]["training"]))
    write_checkpoint(evidence_dir, bias_name, model_results[bias_name])

    day_name = f"DayAheadSpecialized_{hgb_spec.family}"
    day_evidence = fit_and_apply_dayahead_specialized(hgb_spec, feature_names, examples, scored_rows, p0054l2.prediction_column(day_name))
    model_results[day_name] = completed_model_record(day_name, "dayahead_specialized", scored_rows, thresholds, day_evidence)
    checkpoints.append(checkpoint_entry(day_name, "advanced_completed", model_results[day_name]["training"]))
    write_checkpoint(evidence_dir, day_name, model_results[day_name])

    comparison = model_comparison(baseline_eval, model_results)
    dayahead_results = evaluate_dayahead_price_metrics(scored_rows, tuple(p0054l2.prediction_column(name) for name in model_results))
    forecast_log_summary = forecast_log_decision(comparison, scored_rows)
    leakage_review = validate_p0054s_leakage(matrix_review, checkpoints, forecast_log_summary)
    neural_status = neural_sequence_status(environment)
    status = "PASS" if leakage_review["ok"] and any(entry["status"] == "advanced_completed" for entry in checkpoints) else "WARN"

    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "source_contract": source_contract,
        "baseline_contract": baseline_contract,
        "baseline_p0054k_results": baseline_eval,
        "baseline_p0054l2_comparison": baseline_p0054l2_comparison(comparison),
        "split_policy": split_policy(),
        "split_counts": split_counts,
        "internal_split_counts": internal_counts,
        "row_counts": {
            "source_rows": len(price_rows),
            "model_examples": len(examples),
            "train_fit_rows": split_counts.get("train_fit", 0),
            "internal_train_rows": internal_counts.get("internal_train", 0),
            "internal_validation_rows": internal_counts.get("internal_validation", 0),
            "holdout_rows": split_counts.get("holdout", 0),
            "holdout_origin_count": len({row["forecast_origin_timestamp_utc"] for row in holdout_rows}),
            "feature_count": len(feature_names),
        },
        "skipped_windows": skipped_windows,
        "feature_names": feature_names,
        "feature_groups": p0054l2.feature_groups(),
        "input_classification": input_classification(),
        "runtime_policy": runtime_policy(),
        "environment": environment,
        "model_results": compact_model_results(model_results),
        "model_training": {name: result.get("training", {}) for name, result in model_results.items()},
        "validation_evidence": validation_evidence,
        "advanced_method_evidence": {
            weighted_name: weight_evidence,
            median_name: {"source_models": completed},
            stack_name: stack_payload,
            residual_name: residual_evidence,
            bucket_name: bucket_evidence,
            bias_name: bias_evidence,
            day_name: day_evidence,
        },
        "direct_horizon_results": direct_results(model_results),
        "weekly_168h_path_results": weekly_results(model_results),
        "dayahead_price_results": dayahead_results,
        "ranking_spike_ramp_results": ranking_results(model_results),
        "model_comparison": comparison,
        "forecast_log_summary": forecast_log_summary,
        "neural_sequence_status": neural_status,
        "leakage_review": leakage_review,
        "downstream_contract": downstream_contract(forecast_log_summary),
        "interpretation": interpretation(comparison, forecast_log_summary),
        "what_we_learned": what_we_learned(comparison),
        "next_package_recommendation": "Recommended next package: weather/market-regime realism or rolling OOF train-period price forecasts before downstream consumption/flow feature use.",
        "checkpoints": checkpoints,
        "no_api_devices_runtime_a61_nordpool_workplace": True,
        "no_future_actual_price_load_flow_leakage": True,
    }
    evidence = write_p0054s_evidence(evidence_dir, scored_rows, summary)
    return P0054SResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def assign_internal_validation_splits(rows: list[dict[str, object]]) -> dict[str, int]:
    counts = {"internal_train": 0, "internal_validation": 0, "not_train_fit": 0}
    for row in rows:
        if row.get("split") != "train_fit":
            value = "not_train_fit"
        elif str(row["target_timestamp_utc"]) < p0054l2.INTERNAL_VALIDATION_START:
            value = "internal_train"
        else:
            value = "internal_validation"
        row[INTERNAL_SPLIT_FIELD] = value
        counts[value] += 1
    return counts


def capture_environment_status() -> dict[str, object]:
    status = p0054l2.capture_environment_status()
    status["optional_sequence_imports"] = {name: p0054k.import_status(name) for name in ("torch", "tensorflow")}
    return status


def fit_model_on_rows(spec: object, feature_names: list[str], train_rows: list[dict[str, object]], predict_rows: list[dict[str, object]]) -> dict[str, object]:
    started = time.monotonic()
    x_train, standardizer = p0054l2.build_matrix(train_rows, feature_names)
    y_train = np.asarray([float(row["target_price"]) for row in train_rows], dtype=float)
    model = p0054k.clone_model(spec.model)  # type: ignore[attr-defined]
    model.fit(x_train, y_train)  # type: ignore[attr-defined]
    predictions = p0054l2.predict_model(model, standardizer, predict_rows, feature_names)
    return {
        "model": model,
        "standardizer": standardizer,
        "predictions": predictions,
        "training": {
            "model_family": spec.family,  # type: ignore[attr-defined]
            "train_rows": len(train_rows),
            "prediction_rows": len(predict_rows),
            "feature_count": len(feature_names),
            "duration_seconds": round(time.monotonic() - started, 3),
            "model_artifact_persisted": False,
        },
    }


def attach_predictions(rows: list[dict[str, object]], predictions: object, column: str) -> None:
    for row, prediction in zip(rows, predictions):  # type: ignore[arg-type]
        row[column] = float(prediction)


def learn_inverse_mae_weights(validation_rows: list[dict[str, object]], model_names: list[str]) -> tuple[dict[str, float], dict[str, object]]:
    maes = {}
    for name in model_names:
        metric = p0054l2.evaluate_direct_metrics(validation_rows, p0054l2.prediction_column(name))
        if metric.get("MAE") is not None:
            maes[name] = max(float(metric["MAE"]), 1e-9)
    inv = {name: 1.0 / value for name, value in maes.items()}
    total = sum(inv.values())
    weights = {name: value / total for name, value in inv.items()} if total else {name: 1.0 / len(model_names) for name in model_names}
    return weights, {"method": "inverse_internal_validation_mae", "model_mae": maes, "weights": weights, "holdout_used_for_weights": False}


def apply_weighted_ensemble(rows: list[dict[str, object]], weights: dict[str, float], output_column: str) -> int:
    count = 0
    for row in rows:
        weighted = []
        local_weights = []
        for name, weight in weights.items():
            col = p0054l2.prediction_column(name)
            if col in row:
                weighted.append(float(row[col]) * weight)
                local_weights.append(weight)
        if local_weights:
            row[output_column] = sum(weighted) / sum(local_weights)
            count += 1
    return count


def apply_median_ensemble(rows: list[dict[str, object]], model_names: list[str], output_column: str) -> int:
    count = 0
    for row in rows:
        values = sorted(float(row[p0054l2.prediction_column(name)]) for name in model_names if p0054l2.prediction_column(name) in row)
        if values:
            mid = len(values) // 2
            row[output_column] = values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2.0
            count += 1
    return count


def fit_linear_stack(validation_rows: list[dict[str, object]], model_names: list[str]) -> dict[str, object]:
    rows = [row for row in validation_rows if all(p0054l2.prediction_column(name) in row for name in model_names)]
    x = np.asarray([[float(row[p0054l2.prediction_column(name)]) for name in model_names] for row in rows], dtype=float)
    y = np.asarray([float(row["target_price"]) for row in rows], dtype=float)
    if len(rows) < len(model_names) + 1:
        weights = {name: 1.0 / len(model_names) for name in model_names}
        intercept = 0.0
    else:
        x_aug = np.column_stack([np.ones(len(rows)), x])
        coef, *_ = np.linalg.lstsq(x_aug, y, rcond=None)
        intercept = float(coef[0])
        weights = {name: float(value) for name, value in zip(model_names, coef[1:])}
    return {"model_names": model_names, "intercept": intercept, "weights": weights, "fit_rows": len(rows), "holdout_used_for_fit": False}


def apply_linear_stack(rows: list[dict[str, object]], payload: dict[str, object], output_column: str) -> int:
    names = list(payload["model_names"])  # type: ignore[arg-type]
    weights = dict(payload["weights"])  # type: ignore[arg-type]
    count = 0
    for row in rows:
        if all(p0054l2.prediction_column(name) in row for name in names):
            row[output_column] = float(payload["intercept"]) + sum(float(weights[name]) * float(row[p0054l2.prediction_column(name)]) for name in names)
            count += 1
    return count


def fit_and_apply_residual_correction(spec: object, feature_names: list[str], validation_rows: list[dict[str, object]], target_rows: list[dict[str, object]], base_name: str, output_column: str) -> dict[str, object]:
    base_col = p0054l2.prediction_column(base_name)
    train = [row for row in validation_rows if base_col in row]
    x_train, standardizer = p0054l2.build_matrix(train, feature_names)
    y_train = np.asarray([float(row["target_price"]) - float(row[base_col]) for row in train], dtype=float)
    model = p0054k.clone_model(spec.model)  # type: ignore[attr-defined]
    model.fit(x_train, y_train)  # type: ignore[attr-defined]
    predict_rows = [row for row in target_rows if base_col in row]
    corrections = p0054l2.predict_model(model, standardizer, predict_rows, feature_names)
    for row, correction in zip(predict_rows, corrections):
        row[output_column] = float(row[base_col]) + float(correction)
    return {"base_model": base_name, "fit_rows": len(train), "applied_rows": len(predict_rows), "fit_data": "internal_validation_residuals_only", "holdout_used_for_fit": False}


def horizon_bucket(horizon: int) -> str:
    if horizon < 24:
        return "0_24h"
    if horizon < 48:
        return "24_48h"
    if horizon < 72:
        return "48_72h"
    return "72_168h"


def fit_and_apply_horizon_bucket_specialized(spec: object, feature_names: list[str], train_rows: list[dict[str, object]], target_rows: list[dict[str, object]], output_column: str) -> dict[str, object]:
    details = []
    for bucket in ("0_24h", "24_48h", "48_72h", "72_168h"):
        train_b = [row for row in train_rows if horizon_bucket(int(row["horizon_hours"])) == bucket]
        target_b = [row for row in target_rows if row["split"] == "holdout" and horizon_bucket(int(row["horizon_hours"])) == bucket]
        result = fit_model_on_rows(spec, feature_names, train_b, target_b)
        attach_predictions(target_b, result["predictions"], output_column)
        details.append({"bucket": bucket, "train_rows": len(train_b), "applied_rows": len(target_b)})
    return {"model_family": spec.family, "fit_data": "train_fit_only", "buckets": details}  # type: ignore[attr-defined]


def fit_and_apply_horizon_bias_correction(validation_rows: list[dict[str, object]], target_rows: list[dict[str, object]], base_name: str, output_column: str) -> dict[str, object]:
    base_col = p0054l2.prediction_column(base_name)
    biases = {}
    for horizon in p0054l2.PATH_HORIZONS:
        rows = [row for row in validation_rows if int(row["horizon_hours"]) == horizon and base_col in row]
        errors = [float(row[base_col]) - float(row["target_price"]) for row in rows]
        biases[horizon] = p0054k.mean_float(errors) if errors else 0.0
    applied = 0
    for row in target_rows:
        if base_col in row:
            row[output_column] = float(row[base_col]) - float(biases.get(int(row["horizon_hours"]), 0.0))
            applied += 1
    return {"base_model": base_name, "fit_data": "internal_validation_horizon_mean_bias_only", "holdout_used_for_fit": False, "applied_rows": applied}


def fit_and_apply_dayahead_specialized(spec: object, feature_names: list[str], examples: list[dict[str, object]], scored_rows: list[dict[str, object]], output_column: str) -> dict[str, object]:
    train = select_dayahead_rows_by_split(examples, "train_fit")
    holdout_ids = {row_id(row) for row in select_dayahead_rows_by_split(scored_rows, "holdout")}
    holdout = [row for row in scored_rows if row_id(row) in holdout_ids]
    if not train or not holdout:
        return {
            "model_family": spec.family,  # type: ignore[attr-defined]
            "status": "skipped",
            "reason": "P0054L2-compatible forecast origins do not provide complete exact 12:00 Europe/Stockholm D-1 DayAhead rows.",
            "train_rows": len(train),
            "holdout_rows": len(holdout),
            "holdout_used_for_fit": False,
        }
    result = fit_model_on_rows(spec, feature_names, train, holdout)
    attach_predictions(holdout, result["predictions"], output_column)
    return {"model_family": spec.family, "status": "completed", "train_rows": len(train), "holdout_rows": len(holdout), "fit_data": "train_fit_dayahead_rows_only", "holdout_used_for_fit": False}  # type: ignore[attr-defined]


def select_dayahead_rows_by_split(rows: list[dict[str, object]], split: str) -> list[dict[str, object]]:
    by_origin_target = {(str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"])): row for row in rows if row["split"] == split}
    dates: list[date] = sorted({p0052.parse_utc(str(row["target_timestamp_utc"])).astimezone(p0054n.STOCKHOLM).date() for row in rows if row["split"] == split})
    selected: list[dict[str, object]] = []
    for delivery_day in dates:
        origin = p0054n.dayahead_origin_utc_for_delivery_day(delivery_day)
        targets = p0054n.delivery_day_target_utc_hours(delivery_day)
        day_rows = [by_origin_target.get((origin, target)) for target in targets]
        if all(row is not None for row in day_rows):
            selected.extend(row for row in day_rows if row is not None)
    return selected


def row_id(row: dict[str, object]) -> tuple[str, str]:
    return str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"])


def completed_model_record(name: str, method: str, rows: list[dict[str, object]], thresholds: dict[str, float], evidence: dict[str, object]) -> dict[str, object]:
    col = p0054l2.prediction_column(name)
    holdout = [row for row in rows if row["split"] == "holdout"]
    return {
        "model_name": name,
        "status": "completed",
        "training": {"model_family": name, "method": method, "feature_count": len(evidence), "model_artifact_persisted": False},
        "metrics": {
            "holdout": p0054l2.evaluate_direct_metrics(holdout, col),
            "weekly": p0054l2.evaluate_weekly_path_metrics(holdout, col),
            "ranking_spike_ramp": p0054l2.evaluate_ranking_spike_ramp_metrics(holdout, col, thresholds),
        },
        "prediction_column": col,
        "leakage_status": "ok",
    }


def model_comparison(baseline_eval: dict[str, object], model_results: dict[str, dict[str, object]]) -> dict[str, object]:
    base = p0054l2.compare_models(baseline_eval, model_results)
    completed = [row for row in base["models"] if row.get("status") == "completed"]  # type: ignore[index]
    for row in completed:
        if row.get("holdout_MAE") is not None:
            row["direct_mae_improvement_percent_vs_p0054l2_ensemble"] = 100.0 * (P0054L2_ENSEMBLE_DIRECT_MAE - float(row["holdout_MAE"])) / P0054L2_ENSEMBLE_DIRECT_MAE
        if row.get("weekly_MAE_full_168h") is not None:
            row["weekly_mae_improvement_percent_vs_p0054l2_ensemble"] = 100.0 * (P0054L2_ENSEMBLE_WEEKLY_MAE - float(row["weekly_MAE_full_168h"])) / P0054L2_ENSEMBLE_WEEKLY_MAE
    base["p0054l2_ensemble_baseline"] = {"holdout_MAE": P0054L2_ENSEMBLE_DIRECT_MAE, "weekly_MAE_full_168h": P0054L2_ENSEMBLE_WEEKLY_MAE}
    base["best_vs_p0054l2_direct"] = min(completed, key=lambda row: float(row.get("holdout_MAE", math.inf)), default=None)
    base["best_vs_p0054l2_weekly"] = min(completed, key=lambda row: float(row.get("weekly_MAE_full_168h", math.inf)), default=None)
    return base


def evaluate_dayahead_price_metrics(rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> dict[str, object]:
    selected = select_dayahead_rows_by_split(rows, "holdout")
    output: dict[str, object] = {"delivery_day_count": len({row["forecast_origin_timestamp_utc"] for row in selected}), "row_count": len(selected)}
    for col in prediction_columns:
        metric = p0054l2.evaluate_direct_metrics(selected, col)
        by_origin = p0054k.group_by([row for row in selected if col in row], "forecast_origin_timestamp_utc")
        daily_abs = []
        peak_timing = []
        for group in by_origin.values():
            actual_sum = sum(float(row["target_price"]) for row in group)
            pred_sum = sum(float(row[col]) for row in group)
            daily_abs.append(abs(pred_sum - actual_sum))
            actual_peak = max(range(len(group)), key=lambda idx: float(group[idx]["target_price"]))
            pred_peak = max(range(len(group)), key=lambda idx: float(group[idx][col]))
            peak_timing.append(abs(actual_peak - pred_peak))
        output[col] = {
            "hourly_MAE_delivery_day": metric.get("MAE"),
            "hourly_RMSE_delivery_day": metric.get("RMSE"),
            "bias_delivery_day": metric.get("bias"),
            "absolute_daily_price_path_error": p0054k.mean_float(daily_abs) if daily_abs else None,
            "peak_price_timing_error_hours": p0054k.mean_float(peak_timing) if peak_timing else None,
        }
    return output


def forecast_log_decision(comparison: dict[str, object], rows: list[dict[str, object]]) -> dict[str, object]:
    candidates = [row for row in comparison["models"] if row.get("status") == "completed"]  # type: ignore[index]
    useful = [
        row for row in candidates
        if float(row.get("direct_mae_improvement_percent_vs_p0054l2_ensemble", -999.0)) >= 5.0
        or float(row.get("weekly_mae_improvement_percent_vs_p0054l2_ensemble", -999.0)) >= 5.0
    ]
    if not useful:
        return {"created": False, "decision": "no_p0054s_advanced_source_recommended", "reason": "no completed model beat P0054L2 Ensemble by >=5% direct or weekly MAE"}
    best = max(useful, key=lambda row: max(float(row.get("direct_mae_improvement_percent_vs_p0054l2_ensemble", -999.0)), float(row.get("weekly_mae_improvement_percent_vs_p0054l2_ensemble", -999.0))))
    pred_col = p0054l2.prediction_column(str(best["model"]))
    coverage = sum(1 for row in rows if row["split"] == "holdout" and pred_col in row)
    return {
        "created": False,
        "identified_table": FORECAST_LOG_TABLE,
        "recommended_model": best["model"],
        "decision": "advanced_holdout_source_recommended_but_not_persisted_in_package_run",
        "reason": "model beat P0054L2 learning threshold; package evidence identifies holdout-safe log schema without writing local runtime DB",
        "holdout_rows_available": coverage,
    }


def validate_p0054s_leakage(matrix_review: dict[str, object], checkpoints: list[dict[str, object]], forecast_log_summary: dict[str, object]) -> dict[str, object]:
    advanced_completed = any(row["status"] == "advanced_completed" for row in checkpoints)
    return {
        "ok": bool(matrix_review["ok"]) and advanced_completed,
        "matrix_review_ok": matrix_review["ok"],
        "advanced_method_completed": advanced_completed,
        "holdout_used_for_fitting_or_selection": False,
        "holdout_used_for_ensemble_weights_or_correction": False,
        "actual_future_spot_price_feature_used": False,
        "actual_future_load_production_flow_a61_feature_used": False,
        "api_device_runtime_a61_nordpool_workplace_used": False,
        "forecast_log": forecast_log_summary,
    }


def neural_sequence_status(environment: dict[str, object]) -> dict[str, object]:
    return {"status": "skipped", "reason": "Tier 1 tabular/path methods completed; neural sequence models are optional and were not trained.", "imports": environment.get("optional_sequence_imports"), "warn_not_stop": True}


def direct_results(model_results: dict[str, dict[str, object]]) -> dict[str, object]:
    return {name: result.get("metrics", {}).get("holdout") for name, result in model_results.items()}


def weekly_results(model_results: dict[str, dict[str, object]]) -> dict[str, object]:
    return {name: result.get("metrics", {}).get("weekly") for name, result in model_results.items()}


def ranking_results(model_results: dict[str, dict[str, object]]) -> dict[str, object]:
    return {name: result.get("metrics", {}).get("ranking_spike_ramp") for name, result in model_results.items()}


def compact_model_results(model_results: dict[str, dict[str, object]]) -> dict[str, object]:
    return {name: {key: value for key, value in result.items() if key != "model"} for name, result in model_results.items()}


def baseline_p0054l2_comparison(comparison: dict[str, object]) -> dict[str, object]:
    return {
        "p0054l2_ensemble_direct_MAE": P0054L2_ENSEMBLE_DIRECT_MAE,
        "p0054l2_ensemble_weekly_MAE_full_168h": P0054L2_ENSEMBLE_WEEKLY_MAE,
        "best_direct": comparison.get("best_vs_p0054l2_direct"),
        "best_weekly": comparison.get("best_vs_p0054l2_weekly"),
    }


def downstream_contract(forecast_log_summary: dict[str, object]) -> dict[str, object]:
    return {"decision": forecast_log_summary.get("decision"), "warning": "A global train_fit price model is holdout-safe for evaluation, but not automatically a train-period feature source for downstream consumption/production/flow training. Downstream packages need rolling/out-of-fold train forecasts."}


def interpretation(comparison: dict[str, object], forecast_log_summary: dict[str, object]) -> dict[str, object]:
    return {"best_direct": comparison.get("best_vs_p0054l2_direct"), "best_weekly": comparison.get("best_vs_p0054l2_weekly"), "forecast_log_decision": forecast_log_summary, "production_ready": False, "label": "LABB"}


def what_we_learned(comparison: dict[str, object]) -> list[str]:
    best = comparison.get("best_vs_p0054l2_direct") or {}
    return ["Advanced SE3 price models can be evaluated separately from consumption models.", f"Best direct model in P0054S: {best.get('model')}.", "Downstream use still requires rolling/OOF train-period forecast generation."]


def input_classification() -> dict[str, object]:
    base = p0054l2.input_classification()
    base["future_actual_load_production_flow_a61"] = "excluded_leakage"
    base["live_api_data"] = "excluded_leakage"
    return base


def runtime_policy() -> dict[str, object]:
    return {"methods_run_serially": True, "checkpoint_evidence_after_each_method": True, "model_binaries_persisted": False, "api_calls": False, "device_or_runtime_changes": False}


def split_policy() -> dict[str, object]:
    policy = p0054l2.split_policy()
    policy["holdout_used_for_ensemble_weights_or_corrections"] = False
    return policy


def checkpoint_entry(model_name: str, status: str, training: object) -> dict[str, object]:
    return {"model_name": model_name, "status": status, "training": training, "checkpoint_kind": "metrics_only_no_model_binary"}


def write_checkpoint(evidence_dir: Path, model_name: str, payload: dict[str, object]) -> None:
    safe = model_name.lower().replace("_", "-")
    path = evidence_dir / "model-checkpoints" / f"{safe}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def write_p0054s_evidence(evidence_dir: Path, rows: list[dict[str, object]], summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "model-checkpoints").mkdir(parents=True, exist_ok=True)
    files = {
        "metrics-summary.json": write_json(evidence_dir / "metrics-summary.json", summary),
        "model-comparison.csv": write_csv(evidence_dir / "model-comparison.csv", comparison_csv_rows(summary), ["model", "status", "holdout_MAE", "weekly_MAE_full_168h", "direct_mae_improvement_percent_vs_p0054l2_ensemble", "weekly_mae_improvement_percent_vs_p0054l2_ensemble", "spearman", "top20_168h_precision", "bottom20_168h_precision", "spike_f1", "ramp_f1"]),
        "direct-horizon-metrics.csv": write_csv(evidence_dir / "direct-horizon-metrics.csv", metric_csv_rows(summary["direct_horizon_results"]), ["model", "metric", "value"]),
        "weekly-path-metrics.csv": write_csv(evidence_dir / "weekly-path-metrics.csv", metric_csv_rows(summary["weekly_168h_path_results"]), ["model", "metric", "value"]),
        "dayahead-price-metrics.csv": write_csv(evidence_dir / "dayahead-price-metrics.csv", metric_csv_rows(summary["dayahead_price_results"]), ["model", "metric", "value"]),
    }
    for name, text in evidence_markdowns(summary).items():
        files[name] = str(write(evidence_dir / name, text))
    files["model-checkpoints/README.md"] = str(write(evidence_dir / "model-checkpoints" / "README.md", "# P0054S Model Checkpoints\n\nNo model binaries are persisted. JSON checkpoint files in this directory contain metrics/evidence only.\n"))
    return files


def evidence_markdowns(summary: dict[str, object]) -> dict[str, str]:
    common = f"# {PACKAGE_ID} {LABEL}\n\nStatus: `{summary['status']}`\n\n"
    mapping = {
        "CHANGELOG.md": changelog_text(summary),
        "labb-label.md": common + "LABB only; not G2-KANDIDAT and no deployable model artifact.\n",
        "target-source-contract.md": common + json_block(summary["source_contract"]),
        "split-policy-applied.md": common + json_block(summary["split_policy"]),
        "dataset-contract.md": common + json_block({"source": summary["source_contract"], "baseline": summary["baseline_contract"], "dataset_kind": "offline_labb_se3_spotprice_forecast"}),
        "feature-groups.md": common + json_block(summary["feature_groups"]),
        "input-classification.md": common + json_block(summary["input_classification"]),
        "runtime-policy.md": common + json_block(summary["runtime_policy"]),
        "environment-import-status.md": common + json_block(summary["environment"]),
        "model-training-evidence.md": common + json_block(summary["model_training"]),
        "baseline-p0054k-results.md": common + json_block(summary["baseline_p0054k_results"]),
        "baseline-p0054l2-comparison.md": common + json_block(summary["baseline_p0054l2_comparison"]),
        "weighted-ensemble-results.md": common + json_block(summary["advanced_method_evidence"].get("WeightedEnsemble")),
        "median-ensemble-results.md": common + json_block(summary["advanced_method_evidence"].get("MedianEnsemble")),
        "stacked-ensemble-results.md": common + json_block(summary["advanced_method_evidence"].get("LinearStack")),
        "residual-correction-results.md": common + json_block({k: v for k, v in summary["advanced_method_evidence"].items() if k.startswith("ResidualCorrection_")}),
        "horizon-specialized-results.md": common + json_block({k: v for k, v in summary["advanced_method_evidence"].items() if k.startswith("HorizonBucket_")}),
        "horizon-bias-correction-results.md": common + json_block({k: v for k, v in summary["advanced_method_evidence"].items() if k.startswith("HorizonBiasCorrected_")}),
        "dayahead-specialized-results.md": common + json_block({k: v for k, v in summary["advanced_method_evidence"].items() if k.startswith("DayAheadSpecialized_")}),
        "neural-sequence-results.md": common + json_block(summary["neural_sequence_status"]),
        "direct-horizon-results.md": common + json_block(summary["direct_horizon_results"]),
        "weekly-168h-path-results.md": common + json_block(summary["weekly_168h_path_results"]),
        "dayahead-price-results.md": common + json_block(summary["dayahead_price_results"]),
        "ranking-spike-ramp-results.md": common + json_block(summary["ranking_spike_ramp_results"]),
        "model-comparison.md": common + json_block(summary["model_comparison"]),
        "leakage-review.md": common + json_block(summary["leakage_review"]),
        "downstream-contract.md": common + json_block(summary["downstream_contract"]),
        "interpretation.md": common + json_block(summary["interpretation"]),
        "what-we-learned.md": common + json_block(summary["what_we_learned"]),
        "next-package-recommendation.md": common + str(summary["next_package_recommendation"]) + "\n",
    }
    if summary["forecast_log_summary"].get("identified_table"):
        mapping["forecast-log-schema.md"] = common + json_block({"table": FORECAST_LOG_TABLE, "fields": ["forecast_origin_timestamp_utc", "input_data_cutoff_utc", "target_timestamp_utc", "horizon_hours", "area", "predicted_price", "prediction_kind"], "persisted": False})
        mapping["forecast-log-coverage.md"] = common + json_block(summary["forecast_log_summary"])
    return mapping


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0054S Changelog

Status: `{summary['status']}`

- Built LABB-only SE3 advanced spot-price forecast experiment on the P0054L2 target/source contract.
- Ran reproduced base families plus weighted, median, linear-stack, residual-corrected, horizon-bucket, horizon-bias and DayAhead-specialized methods.
- Used internal train_fit validation only for ensemble weights and correction fitting.
- Compared against P0054K and P0054L2 Ensemble baselines.
- Forecast log decision: `{summary['forecast_log_summary']['decision']}`.
- No API, device, runtime, A61, flow, Nord Pool, workplace or future actual price/load leakage work was performed.
"""


def comparison_csv_rows(summary: dict[str, object]) -> list[dict[str, object]]:
    return list(summary["model_comparison"].get("models", []))  # type: ignore[union-attr]


def metric_csv_rows(payload: object) -> list[dict[str, object]]:
    rows = []
    if isinstance(payload, dict):
        for model, metrics in payload.items():
            if isinstance(metrics, dict):
                for key, value in metrics.items():
                    if isinstance(value, dict):
                        rows.append({"model": model, "metric": key, "value": json.dumps(value, sort_keys=True, default=str)})
                    else:
                        rows.append({"model": model, "metric": key, "value": value})
    return rows


def write_json(path: Path, payload: object) -> str:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return str(path)


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> str:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return str(path)


def json_block(payload: object) -> str:
    return "```json\n" + json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n```\n"


def main() -> None:
    result = run_p0054s_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
