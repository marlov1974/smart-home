"""P0054R LABB SE3 advanced AI on corrected ENTSO-E target."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import csv
import json
import math
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054m, p0054n, p0054q
from src.mac.services.spotprice_model_diagnostics.p0041 import write
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0054R"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054R")
INTERNAL_VALIDATION_START = "2025-03-01T00:00:00Z"
INTERNAL_SPLIT_FIELD = "p0054r_internal_split"
VARIANT_NO_PRICE = p0054n.VARIANT_NO_PRICE
P0054Q_FULL36_BASELINE_MAE = 644.9873394113744
P0054Q_DAYAHEAD_BASELINE_MAE = 632.7869013389628
P0054Q_DAILY_ENERGY_BASELINE_MWH = 12862.665916660333


@dataclass(frozen=True)
class P0054RResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054r_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054RResult:
    started = time.monotonic()
    evidence_dir = Path(evidence_dir)
    source_rows, direct_rows, path_rows, contracts = build_p0054r_modeling_rows(feature_db, weather_db)
    split_counts = p0054k.assign_p0054i_splits(direct_rows)
    p0054k.assign_p0054i_splits(path_rows)
    internal_counts = assign_internal_validation_splits(direct_rows)
    assign_internal_validation_splits(path_rows)
    profiles = p0054k.fit_train_profiles([row for row in direct_rows if row["split"] == "train_fit"])
    p0054k.apply_profile_features(direct_rows, profiles)
    p0054k.apply_profile_features(path_rows, profiles)

    feature_contract = p0054q.p0054q_feature_contract()
    no_price_features = list(feature_contract[VARIANT_NO_PRICE]["features"])  # type: ignore[index]
    feature_review = p0054m.validate_feature_contract({VARIANT_NO_PRICE: feature_contract[VARIANT_NO_PRICE]})
    matrix_review = validate_no_price_matrix_safety(direct_rows, {VARIANT_NO_PRICE: feature_contract[VARIANT_NO_PRICE]})
    if not contracts["target_contract"]["ok"] or not feature_review["ok"] or not matrix_review["ok"]:  # type: ignore[index]
        raise RuntimeError(f"P0054R contract failed: target={contracts['target_contract']} feature={feature_review} matrix={matrix_review}")

    environment = capture_environment_status()
    specs = p0054k.model_specs(environment["imports"])  # type: ignore[arg-type]
    no_price_specs = [spec for spec in specs if spec.family in {"HGB", "ExtraTrees", "LightGBM", "XGBoost"}]
    if not no_price_specs:
        raise RuntimeError("P0054R no model specs available")

    scored_rows = [dict(row) for row in direct_rows]
    scored_path_rows = [dict(row) for row in path_rows]
    validation_rows = [dict(row) for row in direct_rows if row[INTERNAL_SPLIT_FIELD] == "internal_validation"]
    internal_train_rows = [row for row in direct_rows if row[INTERNAL_SPLIT_FIELD] == "internal_train"]
    train_fit_rows = [row for row in direct_rows if row["split"] == "train_fit"]

    checkpoint_entries: list[dict[str, object]] = []
    model_results: dict[str, dict[str, object]] = {}
    validation_evidence: dict[str, object] = {}

    for spec in no_price_specs:
        key = f"{spec.family}_{VARIANT_NO_PRICE}"
        validation_fit = fit_model_on_rows(spec, no_price_features, internal_train_rows, validation_rows)
        attach_prediction_values(validation_rows, validation_fit["predictions"], p0054k.prediction_column(key))
        validation_evidence[key] = {
            "model_family": spec.family,
            "internal_train_rows": len(internal_train_rows),
            "internal_validation_rows": len(validation_rows),
            "internal_validation": p0054k.regression_metric_from_predictions(validation_rows, validation_fit["predictions"]),  # type: ignore[arg-type]
            "selection_data": "internal_validation_only",
        }

        result = p0054k.fit_variant_model(scored_rows, no_price_features, spec, VARIANT_NO_PRICE)
        model_results[key] = result
        p0054k.attach_predictions(scored_rows, result, p0054k.prediction_column(key), holdout_only=True)
        p0054k.attach_path_predictions(scored_path_rows, result, no_price_features, p0054k.prediction_column(key))
        checkpoint_entries.append(checkpoint_entry(key, "baseline_reproduced", result["training"]))

    baseline_keys = list(model_results)
    weights, weight_evidence = learn_inverse_mae_weights(validation_rows, baseline_keys)
    weighted_key = f"WeightedEnsemble_{VARIANT_NO_PRICE}"
    weighted_col = p0054k.prediction_column(weighted_key)
    apply_weighted_ensemble(validation_rows, weights, weighted_col)
    apply_weighted_ensemble(scored_rows, weights, weighted_col)
    apply_weighted_ensemble(scored_path_rows, weights, weighted_col)
    model_results[weighted_key] = advanced_result_record(weighted_key, "inverse_mae_weighted_ensemble", weight_evidence, len(train_fit_rows), len(scored_path_rows), len(no_price_features))
    checkpoint_entries.append(checkpoint_entry(weighted_key, "advanced_completed", model_results[weighted_key]["training"]))

    median_key = f"MedianEnsemble_{VARIANT_NO_PRICE}"
    median_col = p0054k.prediction_column(median_key)
    apply_median_ensemble(scored_rows, baseline_keys, median_col)
    apply_median_ensemble(scored_path_rows, baseline_keys, median_col)
    model_results[median_key] = advanced_result_record(median_key, "median_ensemble", {"source_models": baseline_keys}, len(train_fit_rows), len(scored_path_rows), len(no_price_features))
    checkpoint_entries.append(checkpoint_entry(median_key, "advanced_completed", model_results[median_key]["training"]))

    best_internal_key = min(baseline_keys, key=lambda key: float(validation_evidence[key]["internal_validation"]["MAE"]))  # type: ignore[index]
    hgb_spec = next((spec for spec in no_price_specs if spec.family == "HGB"), no_price_specs[0])
    residual_key = f"ResidualCorrection_{best_internal_key}"
    residual_col = p0054k.prediction_column(residual_key)
    residual_evidence = fit_and_apply_residual_correction(
        hgb_spec,
        no_price_features,
        validation_rows,
        scored_path_rows,
        best_internal_key,
        residual_col,
    )
    fit_and_apply_residual_correction(hgb_spec, no_price_features, validation_rows, scored_rows, best_internal_key, residual_col)
    model_results[residual_key] = advanced_result_record(residual_key, "residual_correction", residual_evidence, len(validation_rows), len(scored_path_rows), len(no_price_features))
    checkpoint_entries.append(checkpoint_entry(residual_key, "advanced_completed", model_results[residual_key]["training"]))

    horizon_key = f"HorizonSpecialized_{hgb_spec.family}_{VARIANT_NO_PRICE}"
    horizon_col = p0054k.prediction_column(horizon_key)
    horizon_evidence = fit_and_apply_horizon_specialized(hgb_spec, no_price_features, train_fit_rows, scored_path_rows, horizon_col)
    fit_and_apply_horizon_specialized(hgb_spec, no_price_features, train_fit_rows, scored_rows, horizon_col)
    model_results[horizon_key] = advanced_result_record(horizon_key, "horizon_specialized", horizon_evidence, len(train_fit_rows), len(scored_path_rows), len(no_price_features))
    checkpoint_entries.append(checkpoint_entry(horizon_key, "advanced_completed", model_results[horizon_key]["training"]))

    horizon_bias_key = f"HorizonBiasCorrected_{weighted_key}"
    horizon_bias_col = p0054k.prediction_column(horizon_bias_key)
    bias_evidence = fit_and_apply_horizon_bias_correction(validation_rows, scored_path_rows, weighted_key, horizon_bias_col)
    fit_and_apply_horizon_bias_correction(validation_rows, scored_rows, weighted_key, horizon_bias_col)
    model_results[horizon_bias_key] = advanced_result_record(horizon_bias_key, "horizon_bias_correction", bias_evidence, len(validation_rows), len(scored_path_rows), len(no_price_features))
    checkpoint_entries.append(checkpoint_entry(horizon_bias_key, "advanced_completed", model_results[horizon_bias_key]["training"]))

    dayahead_key = f"DayAheadSpecialized_{hgb_spec.family}_{VARIANT_NO_PRICE}"
    dayahead_col = p0054k.prediction_column(dayahead_key)
    dayahead_evidence = fit_and_apply_dayahead_specialized(hgb_spec, no_price_features, scored_path_rows, dayahead_col)
    model_results[dayahead_key] = advanced_result_record(dayahead_key, "dayahead_specialized", dayahead_evidence, int(dayahead_evidence["train_rows"]), int(dayahead_evidence["holdout_rows"]), len(no_price_features))
    checkpoint_entries.append(checkpoint_entry(dayahead_key, "advanced_completed", model_results[dayahead_key]["training"]))

    prediction_columns = tuple(p0054k.prediction_column(key) for key in model_results)
    full36_prediction_columns = tuple(column for column in prediction_columns if not column.startswith(p0054k.prediction_column("DayAheadSpecialized_")))
    fairness = validate_prediction_coverage(scored_rows, baseline_keys)
    full36_summary, full36_rows = p0054n.evaluate_full_36h_paths(scored_path_rows, full36_prediction_columns)
    dayahead_summary, dayahead_rows = p0054n.evaluate_dayahead_delivery_days(scored_path_rows, prediction_columns)
    full36_selected = p0054q.selected_full36_rows(scored_path_rows)
    dayahead_selected = p0054q.selected_dayahead_rows(scored_path_rows)
    p0054q.add_percent_metrics(full36_summary, full36_selected, full36_prediction_columns, "full36")
    p0054q.add_percent_metrics(dayahead_summary, dayahead_selected, prediction_columns, "dayahead")
    daily_energy_summary = p0054q.daily_energy_error_summary(dayahead_selected, prediction_columns)
    conditional_results = p0054k.evaluate_conditional_regimes(scored_path_rows, full36_prediction_columns)
    comparison = model_comparison(model_results, full36_summary, dayahead_summary, daily_energy_summary)
    leakage_review = validate_p0054r_leakage(
        matrix_review,
        fairness,
        contracts["target_contract"],  # type: ignore[arg-type]
        {VARIANT_NO_PRICE: feature_contract[VARIANT_NO_PRICE]},
        checkpoint_entries,
    )
    neural_status = neural_sequence_status()
    status = "PASS" if leakage_review["ok"] and advanced_method_completed(model_results) and bool(full36_selected) and bool(dayahead_selected) else "WARN"

    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "target_contract": contracts["target_contract"],
        "split_policy": split_policy(),
        "split_counts": split_counts,
        "internal_split_counts": internal_counts,
        "dataset_contract": dataset_contract(contracts),
        "feature_contract": {VARIANT_NO_PRICE: feature_contract[VARIANT_NO_PRICE]},
        "input_classification": input_classification(),
        "runtime_policy": runtime_policy(),
        "environment": environment,
        "neural_sequence_status": neural_status,
        "feature_review": feature_review,
        "matrix_safety_review": matrix_review,
        "fairness": fairness,
        "validation_evidence": validation_evidence,
        "ensemble_weight_evidence": weight_evidence,
        "advanced_method_evidence": {
            weighted_key: weight_evidence,
            median_key: {"source_models": baseline_keys},
            residual_key: residual_evidence,
            horizon_key: horizon_evidence,
            horizon_bias_key: bias_evidence,
            dayahead_key: dayahead_evidence,
        },
        "model_training": {key: result["training"] for key, result in model_results.items()},
        "model_results": {key: result.get("metrics", {}) for key, result in model_results.items()},
        "full_36h_results": full36_summary,
        "dayahead_delivery_day_results": dayahead_summary,
        "daily_energy_error_results": daily_energy_summary,
        "percent_error_results": p0054q.percent_error_summary(full36_summary, dayahead_summary),
        "conditional_regime_results": conditional_results,
        "baseline_p0054q_comparison": baseline_p0054q_comparison(comparison),
        "model_comparison": comparison,
        "leakage_review": leakage_review,
        "interpretation": interpretation_summary(comparison),
        "what_we_learned": what_we_learned(comparison),
        "next_package_recommendation": "Recommended next package: P0054S/P0054B-style weather-realism or SE3-SE1 bottleneck-regime advanced AI lab before any G2-KANDIDAT evaluation.",
        "checkpoint_entries": checkpoint_entries,
        "row_counts": {
            "source_rows": len(source_rows),
            "direct_rows": len(direct_rows),
            "path_rows": len(path_rows),
            "train_fit_rows": split_counts.get("train_fit", 0),
            "holdout_rows": split_counts.get("holdout", 0),
            "internal_train_rows": internal_counts.get("internal_train", 0),
            "internal_validation_rows": internal_counts.get("internal_validation", 0),
            "full36_complete_origins": len(full36_rows),
            "dayahead_delivery_days": len(dayahead_rows),
        },
        "no_live_api": True,
        "no_devices_runtime_a61_nordpool_workplace": True,
        "no_old_target_as_target": True,
        "no_future_actual_load_or_price_leakage": True,
        "no_large_model_binaries": True,
    }
    evidence = write_p0054r_evidence(evidence_dir, scored_path_rows, full36_rows, dayahead_rows, summary)
    return P0054RResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def build_p0054r_modeling_rows(feature_db: Path | str, weather_db: Path | str) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    source_rows = p0054q.load_entsoe_se3_target_rows(feature_db)
    target_contract = p0054q.validate_entsoe_target_contract(source_rows)
    weather_rows, weather_contract = p0054k.load_weather_proxy_rows(weather_db)
    no_price_origin_rows = build_no_price_origin_rows(source_rows, set(p0054n.HORIZONS_36H))
    direct_rows = p0054k.build_modeling_rows(source_rows, weather_rows, no_price_origin_rows, set(p0054n.HORIZONS_36H))
    for row in direct_rows:
        row["price_forecast_source"] = "not_used_p0054r_primary_no_price"
        row["price_feature_protocol"] = "excluded_no_price_primary_run"
    path_rows = [dict(row) for row in direct_rows]
    return source_rows, direct_rows, path_rows, {
        "target_contract": target_contract,
        "weather_contract": weather_contract,
        "exact_price_contract": {
            "ok": True,
            "rows": len(no_price_origin_rows),
            "label": "synthetic origin-target skeleton only; price columns excluded from P0054R no-price feature contract",
            "price_used_for_training_or_prediction": False,
        },
    }


def build_no_price_origin_rows(source_rows: list[dict[str, object]], horizons: set[int]) -> list[dict[str, object]]:
    source_timestamps = {str(row["timestamp_utc"]) for row in source_rows}
    if not source_timestamps:
        return []
    start_date = max(p0052.parse_utc(min(source_timestamps)).date(), date(2022, 6, 1))
    end_date = p0052.parse_utc(max(source_timestamps)).date() - timedelta(days=1)
    out = []
    current = start_date
    while current <= end_date:
        origin_ts = p0054n.dayahead_origin_utc_for_delivery_day(current)
        origin_dt = p0052.parse_utc(origin_ts)
        for horizon in sorted(horizons):
            target_ts = p0052.format_utc(origin_dt + timedelta(hours=horizon - 1))
            if target_ts not in source_timestamps:
                continue
            out.append(
                {
                    "forecast_origin_timestamp_utc": origin_ts,
                    "input_data_cutoff_utc": p0052.format_utc(origin_dt - timedelta(hours=1)),
                    "target_timestamp_utc": target_ts,
                    "horizon_hours": horizon - 1,
                    "horizon_h": horizon,
                    "predicted_price": 0.0,
                    "prediction_rule": "P0054R_no_price_origin_skeleton",
                    "price_feature_source_protocol": "not_used_no_price",
                }
            )
        current += timedelta(days=1)
    return out


def assign_internal_validation_splits(rows: list[dict[str, object]]) -> dict[str, int]:
    counts = {"internal_train": 0, "internal_validation": 0, "not_train_fit": 0}
    for row in rows:
        if row.get("split") != "train_fit":
            row[INTERNAL_SPLIT_FIELD] = "not_train_fit"
        elif str(row["target_timestamp_utc"]) < INTERNAL_VALIDATION_START:
            row[INTERNAL_SPLIT_FIELD] = "internal_train"
        else:
            row[INTERNAL_SPLIT_FIELD] = "internal_validation"
        counts[str(row[INTERNAL_SPLIT_FIELD])] += 1
    return counts


def fit_model_on_rows(spec: object, features: list[str], train_rows: list[dict[str, object]], predict_rows_: list[dict[str, object]]) -> dict[str, object]:
    started = time.monotonic()
    x_train, encoder, names = p0054k.build_feature_matrix(train_rows, features)
    y_train = p0054k.np.array([float(row[p0054k.TARGET_FIELD]) for row in train_rows], dtype=float)
    model = p0054k.clone_model(spec.model)  # type: ignore[attr-defined]
    model.fit(x_train, y_train)  # type: ignore[attr-defined]
    predictions = p0054k.predict_rows(model, encoder, predict_rows_, features)
    return {
        "model": model,
        "encoder": encoder,
        "features": names,
        "predictions": predictions,
        "training": {
            "model_family": spec.family,  # type: ignore[attr-defined]
            "model_class": spec.model_class,  # type: ignore[attr-defined]
            "training_rows": len(train_rows),
            "prediction_rows": len(predict_rows_),
            "feature_count": len(names),
            "training_duration_seconds": round(time.monotonic() - started, 3),
            "model_artifact_persisted": False,
        },
    }


def attach_prediction_values(rows: list[dict[str, object]], predictions: object, column: str) -> None:
    for row, prediction in zip(rows, predictions):  # type: ignore[arg-type]
        row[column] = float(prediction)


def learn_inverse_mae_weights(validation_rows: list[dict[str, object]], model_keys: list[str]) -> tuple[dict[str, float], dict[str, object]]:
    maes = {}
    for key in model_keys:
        column = p0054k.prediction_column(key)
        available = [row for row in validation_rows if row.get(column) is not None]
        metric = p0054k.regression_metric_from_predictions(available, [float(row[column]) for row in available])
        if metric["MAE"] is not None:
            maes[key] = max(float(metric["MAE"]), 1e-9)
    inverse = {key: 1.0 / value for key, value in maes.items()}
    total = sum(inverse.values())
    weights = {key: value / total for key, value in inverse.items()} if total else {key: 1.0 / len(model_keys) for key in model_keys}
    return weights, {
        "method": "inverse_internal_validation_mae",
        "selection_data": "internal_validation_only",
        "internal_validation_start": INTERNAL_VALIDATION_START,
        "model_mae": maes,
        "weights": weights,
        "holdout_used_for_weights": False,
    }


def apply_weighted_ensemble(rows: list[dict[str, object]], weights: dict[str, float], output_column: str) -> int:
    count = 0
    for row in rows:
        values = []
        local_weights = []
        for key, weight in weights.items():
            column = p0054k.prediction_column(key)
            if row.get(column) is not None:
                values.append(float(row[column]) * weight)
                local_weights.append(weight)
        if local_weights:
            row[output_column] = sum(values) / sum(local_weights)
            count += 1
    return count


def apply_median_ensemble(rows: list[dict[str, object]], model_keys: list[str], output_column: str) -> int:
    count = 0
    for row in rows:
        values = sorted(float(row[p0054k.prediction_column(key)]) for key in model_keys if row.get(p0054k.prediction_column(key)) is not None)
        if values:
            mid = len(values) // 2
            row[output_column] = values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2.0
            count += 1
    return count


def fit_and_apply_residual_correction(
    spec: object,
    features: list[str],
    validation_rows: list[dict[str, object]],
    target_rows: list[dict[str, object]],
    base_model_key: str,
    output_column: str,
) -> dict[str, object]:
    base_column = p0054k.prediction_column(base_model_key)
    train = [row for row in validation_rows if row.get(base_column) is not None]
    x_train, encoder, names = p0054k.build_feature_matrix(train, features)
    y_train = p0054k.np.array([float(row[p0054k.TARGET_FIELD]) - float(row[base_column]) for row in train], dtype=float)
    model = p0054k.clone_model(spec.model)  # type: ignore[attr-defined]
    model.fit(x_train, y_train)  # type: ignore[attr-defined]
    predict = [row for row in target_rows if row.get(base_column) is not None]
    corrections = p0054k.predict_rows(model, encoder, predict, features)
    for row, correction in zip(predict, corrections):
        row[output_column] = float(row[base_column]) + float(correction)
    return {
        "base_model_key": base_model_key,
        "correction_model_family": spec.family,  # type: ignore[attr-defined]
        "fit_rows": len(train),
        "applied_rows": len(predict),
        "feature_count": len(names),
        "fit_data": "internal_validation_residuals_only",
        "holdout_used_for_fit": False,
    }


def fit_and_apply_horizon_specialized(spec: object, features: list[str], train_rows: list[dict[str, object]], target_rows: list[dict[str, object]], output_column: str) -> dict[str, object]:
    details = []
    total_applied = 0
    for horizon in p0054n.HORIZONS_36H:
        train_h = [row for row in train_rows if int(row["horizon_h"]) == horizon]
        target_h = [row for row in target_rows if int(row["horizon_h"]) == horizon and row.get("split") == "holdout"]
        if not train_h or not target_h:
            continue
        result = fit_model_on_rows(spec, features, train_h, target_h)
        attach_prediction_values(target_h, result["predictions"], output_column)
        total_applied += len(target_h)
        details.append({"horizon_h": horizon, "train_rows": len(train_h), "applied_rows": len(target_h)})
    return {
        "model_family": spec.family,  # type: ignore[attr-defined]
        "horizon_convention": "horizon_h 1..36",
        "horizon_models": len(details),
        "applied_rows": total_applied,
        "details": details,
        "fit_data": "train_fit_only",
    }


def fit_and_apply_horizon_bias_correction(validation_rows: list[dict[str, object]], target_rows: list[dict[str, object]], base_model_key: str, output_column: str) -> dict[str, object]:
    base_column = p0054k.prediction_column(base_model_key)
    biases = {}
    for horizon in p0054n.HORIZONS_36H:
        rows = [row for row in validation_rows if int(row["horizon_h"]) == horizon and row.get(base_column) is not None]
        errors = [float(row[base_column]) - float(row[p0054k.TARGET_FIELD]) for row in rows]
        biases[horizon] = p0054k.mean_float(errors) if errors else 0.0
    applied = 0
    for row in target_rows:
        if row.get(base_column) is not None:
            row[output_column] = float(row[base_column]) - float(biases.get(int(row["horizon_h"]), 0.0))
            applied += 1
    return {
        "base_model_key": base_model_key,
        "fit_data": "internal_validation_horizon_mean_bias_only",
        "holdout_used_for_fit": False,
        "horizon_bias_mw": {str(key): value for key, value in biases.items()},
        "applied_rows": applied,
    }


def fit_and_apply_dayahead_specialized(spec: object, features: list[str], rows: list[dict[str, object]], output_column: str) -> dict[str, object]:
    train_rows = select_dayahead_rows_by_split(rows, "train_fit")
    holdout_rows = select_dayahead_rows_by_split(rows, "holdout")
    result = fit_model_on_rows(spec, features, train_rows, holdout_rows)
    attach_prediction_values(holdout_rows, result["predictions"], output_column)
    return {
        "model_family": spec.family,  # type: ignore[attr-defined]
        "forecast_origin": "12:00 Europe/Stockholm on D-1",
        "delivery_day": "local D 00:00..23:00",
        "train_rows": len(train_rows),
        "holdout_rows": len(holdout_rows),
        "train_delivery_days": len({row["forecast_origin_timestamp_utc"] for row in train_rows}),
        "holdout_delivery_days": len({row["forecast_origin_timestamp_utc"] for row in holdout_rows}),
        "fit_data": "train_fit_dayahead_rows_only",
        "holdout_used_for_fit": False,
    }


def select_dayahead_rows_by_split(rows: list[dict[str, object]], split: str) -> list[dict[str, object]]:
    by_origin_target = {(str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"])): row for row in rows if row["split"] == split}
    target_dates: list[date] = sorted({p0052.parse_utc(str(row["target_timestamp_utc"])).astimezone(p0054n.STOCKHOLM).date() for row in rows if row["split"] == split})
    selected: list[dict[str, object]] = []
    for delivery_day in target_dates:
        origin = p0054n.dayahead_origin_utc_for_delivery_day(delivery_day)
        targets = p0054n.delivery_day_target_utc_hours(delivery_day)
        day_rows = [by_origin_target.get((origin, target)) for target in targets]
        if all(row is not None for row in day_rows):
            selected.extend(row for row in day_rows if row is not None)
    return selected


def validate_p0054r_leakage(
    matrix_review: dict[str, object],
    fairness: dict[str, object],
    target_contract: dict[str, object],
    feature_contract: dict[str, dict[str, object]],
    checkpoint_entries: list[dict[str, object]],
) -> dict[str, object]:
    base = p0054q.validate_p0054q_leakage(matrix_review, fairness, {"ok": True}, target_contract, feature_contract, [{}])
    forbidden_features = sorted({feature for group in feature_contract.values() for feature in group["features"] if any(term in str(feature).lower() for term in ("physical_balance", "actual_price", "flow", "export", "import", "a61", "capacity", "utilization"))})  # type: ignore[index]
    advanced_completed = any(entry["status"] == "advanced_completed" for entry in checkpoint_entries)
    base.update(
        {
            "ok": bool(base["ok"]) and not forbidden_features and advanced_completed,
            "advanced_method_completed": advanced_completed,
            "ensemble_meta_learner_data": "internal_validation_only",
            "holdout_used_for_ensemble_weights_or_correction": False,
            "weather_proxy_label_preserved": True,
            "forbidden_features": forbidden_features,
            "no_api_devices_a61_nordpool_workplace": True,
        }
    )
    return base


def validate_no_price_matrix_safety(rows: list[dict[str, object]], feature_contract: dict[str, dict[str, object]]) -> dict[str, object]:
    forbidden_terms = ("physical_balance", "actual_price", "future_actual_load", "flow", "export", "import", "a61", "capacity", "utilization", "production")
    forbidden_columns = sorted({column for row in rows[:1] for column in row if any(term in column.lower() for term in forbidden_terms)})
    forbidden_features = sorted({feature for group in feature_contract.values() for feature in group["features"] if any(term in str(feature).lower() for term in forbidden_terms)})  # type: ignore[index]
    cutoff_order_ok = all(
        p0052.parse_utc(str(row["input_data_cutoff_utc"])) <= p0052.parse_utc(str(row["forecast_origin_timestamp_utc"])) <= p0052.parse_utc(str(row["target_timestamp_utc"]))
        for row in rows
    )
    source_order_ok = all(
        int(row["horizon_h"]) >= 1
        and p0052.parse_utc(str(row["input_data_cutoff_utc"])) < p0052.parse_utc(str(row["forecast_origin_timestamp_utc"]))
        for row in rows
    )
    return {
        "ok": bool(rows) and not forbidden_columns and not forbidden_features and cutoff_order_ok and source_order_ok,
        "feature_groups": sorted(feature_contract),
        "forbidden_columns": forbidden_columns,
        "forbidden_features": forbidden_features,
        "cutoff_order_ok": cutoff_order_ok,
        "source_order_ok": source_order_ok,
        "price_source_required": False,
        "old_target_used": False,
        "actual_future_load_feature_used": False,
        "production_flow_export_import_a61_used": False,
    }


def validate_prediction_coverage(rows: list[dict[str, object]], model_keys: list[str]) -> dict[str, object]:
    holdout = [row for row in rows if row.get("split") == "holdout"]
    coverage = {}
    ok = bool(holdout)
    for key in model_keys:
        column = p0054k.prediction_column(key)
        predicted = sum(1 for row in holdout if row.get(column) is not None)
        coverage[key] = {"holdout_rows": len(holdout), "predicted_rows": predicted, "ok": predicted == len(holdout)}
        ok = ok and predicted == len(holdout)
    return {"ok": ok, "coverage": coverage, "paired_price_branch_required": False}


def capture_environment_status() -> dict[str, object]:
    status = p0054k.capture_environment_status()
    status["optional_sequence_imports"] = {name: p0054k.import_status(name) for name in ("torch", "tensorflow")}
    return status


def neural_sequence_status() -> dict[str, object]:
    imports = {name: p0054k.import_status(name) for name in ("torch", "tensorflow")}
    return {
        "status": "skipped",
        "reason": "Tier 1 advanced tabular methods completed first; neural sequence models are optional and were not trained in this package run.",
        "imports": imports,
        "warn_not_stop": True,
    }


def advanced_result_record(model_key: str, method: str, evidence: dict[str, object], train_rows: int, prediction_rows: int, feature_count: int) -> dict[str, object]:
    return {
        "metrics": {"model_family": model_key, "variant": VARIANT_NO_PRICE, "method": method, "selection_data": evidence.get("selection_data") or evidence.get("fit_data") or "train_fit_only"},
        "training": {
            "model_family": model_key,
            "variant": VARIANT_NO_PRICE,
            "method": method,
            "training_rows": train_rows,
            "holdout_or_prediction_rows": prediction_rows,
            "feature_count": feature_count,
            "model_artifact_persisted": False,
        },
    }


def checkpoint_entry(model_key: str, status: str, training: object) -> dict[str, object]:
    return {
        "model_key": model_key,
        "status": status,
        "training": training,
        "checkpoint_kind": "metrics_and_evidence_only_no_model_binary",
    }


def advanced_method_completed(model_results: dict[str, dict[str, object]]) -> bool:
    return any(key.startswith(("WeightedEnsemble_", "MedianEnsemble_", "ResidualCorrection_", "HorizonSpecialized_", "DayAheadSpecialized_")) for key in model_results)


def split_policy() -> dict[str, str]:
    return {
        "train_fit": "2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z",
        "holdout": "target_timestamp_utc >= 2025-06-01T00:00:00Z",
        "internal_train": f"train_fit and target_timestamp_utc < {INTERNAL_VALIDATION_START}",
        "internal_validation": f"{INTERNAL_VALIDATION_START} <= target_timestamp_utc < 2025-06-01T00:00:00Z",
        "holdout_tuning_policy": "holdout not used for fitting, early stopping, feature selection, hyperparameter selection, ensemble weights, correction fitting, or model-family selection",
    }


def dataset_contract(contracts: dict[str, object]) -> dict[str, object]:
    return {
        "target": contracts["target_contract"],
        "weather": contracts["weather_contract"],
        "weather_proxy_label": p0054k.WEATHER_PROXY_LABEL,
        "advanced_price": "not_used_in_primary_p0054r_models_no_price_only",
        "dataset_kind": "offline_labb_corrected_entsoe_target_advanced_ai_experiment_not_deployable",
    }


def input_classification() -> dict[str, object]:
    return {
        "calendar": "forecast_safe",
        "historical_entsoe_se3_load_lags_rollups": "forecast_safe",
        "entsoe_se3_target": "historical_observed_only",
        "weather": "proxy",
        "weather_proxy_label": p0054k.WEATHER_PROXY_LABEL,
        "price": "excluded_from_primary_run_after_p0054q_negative_ablation",
        "future_actual_load": "excluded_leakage",
        "actual_future_spot_price": "excluded_leakage",
        "flows_exchanges_net_positions_a61_production": "excluded_leakage",
    }


def runtime_policy() -> dict[str, object]:
    return {
        "methods_run_serially": True,
        "checkpoint_evidence_after_each_method": True,
        "model_binaries_persisted": False,
        "api_calls": False,
        "device_or_runtime_changes": False,
    }


def model_comparison(
    model_results: dict[str, dict[str, object]],
    full36_summary: dict[str, object],
    dayahead_summary: dict[str, object],
    daily_energy_summary: dict[str, object],
) -> dict[str, object]:
    full36 = []
    dayahead_hourly = []
    dayahead_energy = []
    for key in model_results:
        column = p0054k.prediction_column(key)
        if column in full36_summary:
            full36.append({"model": key, "MAE_full_36h": full36_summary[column]["MAE_full_36h"], "MAE_percent_of_mean_actual": full36_summary[column]["MAE_percent_of_mean_actual"]})  # type: ignore[index]
        if column in dayahead_summary:
            dayahead_hourly.append({"model": key, "hourly_MAE_delivery_day": dayahead_summary[column]["hourly_MAE_delivery_day"], "MAE_percent_of_mean_actual": dayahead_summary[column]["MAE_percent_of_mean_actual"]})  # type: ignore[index]
        if column in daily_energy_summary:
            dayahead_energy.append({"model": key, **daily_energy_summary[column]})  # type: ignore[index]
    return {
        "best_full36": min(full36, key=lambda row: float(row["MAE_full_36h"])) if full36 else None,
        "best_dayahead_hourly": min(dayahead_hourly, key=lambda row: float(row["hourly_MAE_delivery_day"])) if dayahead_hourly else None,
        "best_dayahead_daily_energy": min(dayahead_energy, key=lambda row: float(row["absolute_daily_energy_error_MWh"])) if dayahead_energy else None,
        "full36": full36,
        "dayahead_hourly": dayahead_hourly,
        "dayahead_daily_energy": dayahead_energy,
        "workplace_reference_percent_error": "roughly 3-4 percent; P0054R remains LABB because weather is actual_as_forecast_proxy",
    }


def baseline_p0054q_comparison(comparison: dict[str, object]) -> dict[str, object]:
    best_full36 = comparison.get("best_full36") or {}
    best_dayahead = comparison.get("best_dayahead_hourly") or {}
    best_energy = comparison.get("best_dayahead_daily_energy") or {}
    return {
        "p0054q_best_full36_mae_mw": P0054Q_FULL36_BASELINE_MAE,
        "p0054r_best_full36": best_full36,
        "p0054r_full36_relative_improvement_percent": relative_improvement(P0054Q_FULL36_BASELINE_MAE, best_full36.get("MAE_full_36h")),
        "p0054q_best_dayahead_hourly_mae_mw": P0054Q_DAYAHEAD_BASELINE_MAE,
        "p0054r_best_dayahead_hourly": best_dayahead,
        "p0054r_dayahead_relative_improvement_percent": relative_improvement(P0054Q_DAYAHEAD_BASELINE_MAE, best_dayahead.get("hourly_MAE_delivery_day")),
        "p0054q_best_daily_energy_error_mwh": P0054Q_DAILY_ENERGY_BASELINE_MWH,
        "p0054r_best_daily_energy": best_energy,
        "p0054r_daily_energy_relative_improvement_percent": relative_improvement(P0054Q_DAILY_ENERGY_BASELINE_MWH, best_energy.get("absolute_daily_energy_error_MWh")),
    }


def relative_improvement(baseline: float, candidate: object) -> float | None:
    if candidate is None or not math.isfinite(float(candidate)):
        return None
    return (baseline - float(candidate)) / baseline * 100.0


def interpretation_summary(comparison: dict[str, object]) -> dict[str, object]:
    baseline = baseline_p0054q_comparison(comparison)
    best_day = comparison.get("best_dayahead_hourly") or {}
    return {
        "best_full36_model": comparison.get("best_full36"),
        "best_dayahead_hourly_model": best_day,
        "best_dayahead_daily_energy_model": comparison.get("best_dayahead_daily_energy"),
        "relative_improvement_vs_p0054q": baseline,
        "advanced_ai_moves_toward_3_4_percent_reference": bool(best_day.get("MAE_percent_of_mean_actual") is not None and float(best_day["MAE_percent_of_mean_actual"]) < 6.0),
        "production_readiness": "no; LABB only because weather remains weather_actual_as_forecast_proxy and no operator requested G2-KANDIDAT evaluation",
        "price_features": "keep excluded from primary corrected-target consumption run until a separate safe ablation has a stronger hypothesis",
    }


def what_we_learned(comparison: dict[str, object]) -> list[str]:
    best_day = comparison.get("best_dayahead_hourly") or {}
    return [
        "Advanced no-price tabular methods can be evaluated cleanly on the corrected ENTSO-E target without old physical-balance target leakage.",
        f"Best P0054R DayAhead hourly model: {best_day.get('model')}.",
        "Weather remains actual-as-forecast proxy, so even improved metrics are LABB-only and not production-ready.",
    ]


def write_p0054r_evidence(evidence_dir: Path, scored_rows: list[dict[str, object]], full36_rows: list[dict[str, object]], dayahead_rows: list[dict[str, object]], summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "model-checkpoints").mkdir(parents=True, exist_ok=True)
    files = {
        "metrics-summary.json": write_json(evidence_dir / "metrics-summary.json", summary),
        "model-comparison.csv": write_csv(evidence_dir / "model-comparison.csv", comparison_rows(summary), ["scope", "model", "metric_name", "metric_value"]),
        "full-36h-path-metrics.csv": write_csv(evidence_dir / "full-36h-path-metrics.csv", full36_rows, list(full36_rows[0].keys()) if full36_rows else []),
        "dayahead-delivery-day-metrics.csv": write_csv(evidence_dir / "dayahead-delivery-day-metrics.csv", dayahead_rows, list(dayahead_rows[0].keys()) if dayahead_rows else []),
        "modeling-dataset-sample.csv": write_csv(evidence_dir / "modeling-dataset-sample.csv", scored_rows[:500], dataset_sample_columns(summary)),
        "conditional-metrics.csv": write_csv(evidence_dir / "conditional-metrics.csv", p0054n.flatten_conditional_rows(summary), p0054n.conditional_columns()),
    }
    for name, text in evidence_markdowns(summary).items():
        files[name] = str(write(evidence_dir / name, text))
    files["model-checkpoints/README.md"] = str(write(evidence_dir / "model-checkpoints" / "README.md", checkpoint_markdown(summary)))
    return files


def evidence_markdowns(summary: dict[str, object]) -> dict[str, str]:
    common = f"# {PACKAGE_ID} {LABEL}\n\nStatus: `{summary['status']}`\n\n"
    return {
        "CHANGELOG.md": changelog_text(summary),
        "labb-label.md": common + "This package is LABB only. It is not G2-KANDIDAT and creates no deployable model artifact.\n",
        "target-source-contract.md": common + json_block(summary["target_contract"]),
        "split-policy-applied.md": common + json_block(summary["split_policy"]),
        "dataset-contract.md": common + json_block(summary["dataset_contract"]),
        "feature-groups.md": common + json_block(summary["feature_contract"]),
        "input-classification.md": common + json_block(summary["input_classification"]),
        "runtime-policy.md": common + json_block(summary["runtime_policy"]),
        "environment-import-status.md": common + json_block(summary["environment"]),
        "model-training-evidence.md": common + json_block(summary["model_training"]),
        "baseline-p0054q-comparison.md": common + json_block(summary["baseline_p0054q_comparison"]),
        "stacked-ensemble-results.md": common + json_block({"weighted": summary["advanced_method_evidence"][next(key for key in summary["advanced_method_evidence"] if key.startswith("WeightedEnsemble_"))], "median": summary["advanced_method_evidence"][next(key for key in summary["advanced_method_evidence"] if key.startswith("MedianEnsemble_"))]}),
        "residual-correction-results.md": common + json_block({key: value for key, value in summary["advanced_method_evidence"].items() if key.startswith("ResidualCorrection_")}),
        "horizon-specialized-results.md": common + json_block({key: value for key, value in summary["advanced_method_evidence"].items() if key.startswith("HorizonSpecialized_") or key.startswith("HorizonBiasCorrected_")}),
        "dayahead-specialized-results.md": common + json_block({key: value for key, value in summary["advanced_method_evidence"].items() if key.startswith("DayAheadSpecialized_")}),
        "neural-sequence-results.md": common + json_block(summary["neural_sequence_status"]),
        "full-36h-results.md": common + json_block(summary["full_36h_results"]),
        "dayahead-delivery-day-results.md": common + json_block(summary["dayahead_delivery_day_results"]),
        "daily-energy-error-results.md": common + json_block(summary["daily_energy_error_results"]),
        "percent-error-results.md": common + json_block(summary["percent_error_results"]),
        "conditional-regime-results.md": common + json_block(summary["conditional_regime_results"]),
        "model-comparison.md": common + json_block(summary["model_comparison"]),
        "leakage-review.md": common + json_block(summary["leakage_review"]),
        "interpretation.md": common + json_block(summary["interpretation"]),
        "what-we-learned.md": common + json_block(summary["what_we_learned"]),
        "next-package-recommendation.md": common + str(summary["next_package_recommendation"]) + "\n",
    }


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0054R Changelog

Status: `{summary['status']}`

- Built corrected-target SE3 advanced AI LABB experiment on `entsoe_consumption_area_hourly_v1.consumption_mw`.
- Reproduced no-price tabular baselines and ran weighted, median, residual-corrected, horizon-specialized, horizon-bias-corrected, and DayAhead-specialized methods.
- Used internal train_fit validation only for ensemble weights and correction fitting.
- Wrote DayAhead, full_36h, daily-energy, percent-error, conditional-regime, leakage and P0054Q comparison evidence.
- Skipped optional neural sequence models with WARN evidence; no model binaries were persisted.
- No API, device, runtime, A61, flow, Nord Pool, workplace, old-target or future-actual leakage work was performed.
"""


def checkpoint_markdown(summary: dict[str, object]) -> str:
    return "# P0054R Model Checkpoints\n\nNo model binaries are persisted. Checkpoints are compact evidence records only.\n\n```json\n" + json.dumps(summary["checkpoint_entries"], indent=2, sort_keys=True, default=str) + "\n```\n"


def comparison_rows(summary: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    comparison = summary["model_comparison"]
    for scope in ("full36", "dayahead_hourly", "dayahead_daily_energy"):
        for item in comparison.get(scope, []):  # type: ignore[union-attr]
            model = item.get("model")
            for key, value in item.items():
                if key != "model":
                    rows.append({"scope": scope, "model": model, "metric_name": key, "metric_value": value})
    return rows


def dataset_sample_columns(summary: dict[str, object]) -> list[str]:
    columns = [
        "forecast_origin_timestamp_utc",
        "target_timestamp_utc",
        "horizon_h",
        "split",
        INTERNAL_SPLIT_FIELD,
        p0054k.TARGET_FIELD,
        "target_source_table",
        "target_source_column",
        "weather_proxy_label",
    ]
    columns.extend(p0054k.prediction_column(key) for key in summary["model_results"])  # type: ignore[operator]
    return columns


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
    result = run_p0054r_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
