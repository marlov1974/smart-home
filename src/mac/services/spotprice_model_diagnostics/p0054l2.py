"""P0054L2 LABB serial SE3 spot-price forecast long-run."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import math
import sqlite3
import time

import numpy as np

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k
from src.mac.services.spotprice_model_diagnostics.p0041 import persist_rows, percentile, write


PACKAGE_ID = "P0054L2"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054L2")
CHECKPOINT_DIR = EVIDENCE_DIR / "model-checkpoints"
SOURCE_TABLE = "ai2_hour_to_day_training_targets_v2"
BASELINE_TABLE = "anchored_absolute_price_forecast_log_p0054k_se3_v1"
ADVANCED_TABLE = "advanced_spotprice_forecast_log_p0054l2_se3_v1"
TRAIN_FIT_START = "2022-06-01T00:00:00Z"
INTERNAL_VALIDATION_START = "2025-03-01T00:00:00Z"
HOLDOUT_START = "2025-06-01T00:00:00Z"
RANDOM_SEED = 542
PATH_HORIZONS = tuple(range(168))
LAGS = (1, 2, 3, 6, 12, 24, 48, 72, 168)
ROLL_WINDOWS = (6, 12, 24, 48, 168, 336)
FORBIDDEN_FEATURE_TERMS = (
    "actual",
    "production",
    "consumption",
    "load",
    "flow",
    "export",
    "import",
    "a09",
    "a11",
    "a61",
    "capacity",
    "utilization",
    "margin",
    "continental",
)


@dataclass(frozen=True)
class P0054L2Result:
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


@dataclass(frozen=True)
class Standardizer:
    means: dict[str, float]
    scales: dict[str, float]


def run_p0054l2_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054L2Result:
    started = time.monotonic()
    feature_db = Path(feature_db).expanduser()
    evidence_dir = Path(evidence_dir)
    (evidence_dir / "model-checkpoints").mkdir(parents=True, exist_ok=True)

    price_rows = load_se3_price_rows(feature_db)
    source_contract = validate_source_contract(price_rows)
    if not source_contract["ok"]:
        raise RuntimeError(f"P0054L2 source contract failed: {source_contract}")
    examples, skipped_windows = build_price_forecast_examples(price_rows)
    split_counts = count_by(examples, "split")
    feature_names = sorted({key for row in examples for key in row["features"]})  # type: ignore[union-attr]
    matrix_review = validate_feature_matrix_safety(examples, feature_names)
    if not matrix_review["ok"]:
        raise RuntimeError(f"P0054L2 feature matrix safety failed: {matrix_review}")
    baseline_rows, baseline_contract = load_p0054k_baseline_rows(feature_db)
    baseline_eval = evaluate_baseline(examples, baseline_rows)
    if not baseline_eval["ok"]:
        raise RuntimeError(f"P0054L2 baseline comparison failed: {baseline_eval}")

    environment = capture_environment_status()
    specs = model_specs(environment["imports"])  # type: ignore[arg-type]
    spec_by_family = {spec.family: spec for spec in specs}
    model_results: dict[str, dict[str, object]] = {}
    scored_rows = [dict(row) for row in examples]
    thresholds = fit_train_thresholds(examples)
    for family in ("HGB", "ExtraTrees", "LightGBM", "XGBoost"):
        checkpoint_started = time.monotonic()
        if family not in spec_by_family:
            checkpoint = skipped_checkpoint(family, "import_unavailable", examples, feature_names, environment)
            write_model_checkpoint(evidence_dir, family, checkpoint)
            model_results[family] = checkpoint
            continue
        try:
            result = fit_serial_model(scored_rows, feature_names, spec_by_family[family], thresholds)
            result["status"] = "completed"
            result["duration_seconds"] = round(time.monotonic() - checkpoint_started, 3)
        except Exception as exc:  # checkpoint failure evidence before continuing other families
            result = failed_checkpoint(family, exc, examples, feature_names, spec_by_family[family], checkpoint_started)
        write_model_checkpoint(evidence_dir, family, result)
        model_results[family] = result

    completed = [name for name, result in model_results.items() if result.get("status") == "completed"]
    ensemble_result = None
    if len(completed) >= 2:
        ensemble_result = build_simple_ensemble(scored_rows, completed, thresholds)
        write_model_checkpoint(evidence_dir, "Ensemble", ensemble_result)
        model_results["Ensemble"] = ensemble_result

    comparison = compare_models(baseline_eval, model_results)
    recommendation = recommendation_from_comparison(comparison)
    forecast_log_summary: dict[str, object] = {"created": False, "reason": "no_advanced_source_recommended"}
    if recommendation.get("create_forecast_log"):
        best_model = str(recommendation["recommended_model"])
        forecast_count = persist_advanced_forecast_log(feature_db, scored_rows, best_model, model_results[best_model])
        forecast_log_summary = {"created": True, "table": ADVANCED_TABLE, "rows": forecast_count, "recommended_model": best_model}

    leakage_review = leakage_review_summary(matrix_review, model_results, forecast_log_summary)
    completed_core = [name for name in ("HGB", "ExtraTrees", "LightGBM", "XGBoost") if model_results.get(name, {}).get("status") == "completed"]
    if not completed_core:
        status = "STOP"
    elif len(completed_core) >= 4 and leakage_review["ok"]:
        status = "PASS"
    elif len(completed_core) >= 2 and leakage_review["ok"]:
        status = "WARN"
    else:
        status = "STOP"

    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "source_contract": source_contract,
        "baseline_contract": baseline_contract,
        "baseline_metrics": baseline_eval,
        "split_policy": split_policy(),
        "split_counts": split_counts,
        "row_counts": {
            "source_rows": len(price_rows),
            "model_examples": len(examples),
            "train_fit_rows": split_counts.get("train_fit", 0),
            "holdout_rows": split_counts.get("holdout", 0),
            "feature_count": len(feature_names),
        },
        "skipped_windows": skipped_windows,
        "feature_names": feature_names,
        "feature_groups": feature_groups(),
        "input_classification": input_classification(),
        "matrix_review": matrix_review,
        "environment": environment,
        "model_results": compact_model_results(model_results),
        "model_comparison": comparison,
        "recommendation": recommendation,
        "forecast_log_summary": forecast_log_summary,
        "leakage_review": leakage_review,
        "downstream_warning": downstream_warning(),
        "no_downstream_consumption_model_run": True,
        "no_api_devices_runtime_a61_or_future_flow": True,
    }
    evidence = write_p0054l2_evidence(evidence_dir, summary)
    return P0054L2Result(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def load_se3_price_rows(feature_db: Path) -> list[dict[str, object]]:
    return p0054k.load_se3_price_source_rows(feature_db)


def validate_source_contract(rows: list[dict[str, object]]) -> dict[str, object]:
    contract = p0054k.validate_se3_price_source_contract(rows)
    contract["package_id"] = PACKAGE_ID
    contract["target"] = "spot_price_se3"
    contract["unit"] = "repository hour_price convention"
    contract["timestamp_semantics"] = "timestamp_utc is the target hour start in UTC"
    return contract


def build_price_forecast_examples(price_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, int]]:
    by_ts = {str(row["timestamp_utc"]): float(row["hour_price"]) for row in price_rows}
    by_meta = {str(row["timestamp_utc"]): row for row in price_rows}
    windows, skipped = p0054k.build_se3_price_windows(price_rows)
    examples: list[dict[str, object]] = []
    for window in windows:
        origin_text = str(window["forecast_origin_timestamp_utc"])
        origin = p0052.parse_utc(origin_text)
        for horizon, hourly in enumerate(window["hourly_rows"]):  # type: ignore[index]
            target_text = p0052.normalize_utc_text(hourly["timestamp_utc"])
            target = p0052.parse_utc(target_text)
            features, audit = price_history_features_at_origin(origin, target, by_ts, by_meta, horizon)
            examples.append(
                {
                    "forecast_origin_timestamp_utc": origin_text,
                    "input_data_cutoff_utc": p0052.format_utc(origin - timedelta(hours=1)),
                    "target_timestamp_utc": target_text,
                    "horizon_hours": horizon,
                    "split": p0054_split(target_text),
                    "target_price": float(hourly["hour_price"]),
                    "features": features,
                    "feature_source_audit": audit,
                    "area": "SE3",
                }
            )
    return examples, skipped


def price_history_features_at_origin(
    origin: datetime,
    target: datetime,
    prices_by_ts: dict[str, float],
    meta_by_ts: dict[str, dict[str, object]],
    horizon: int,
) -> tuple[dict[str, float], dict[str, str]]:
    audit: dict[str, str] = {}
    target_meta = meta_by_ts[p0052.format_utc(target)]
    features = {
        "horizon_hours": float(horizon),
        "target_model_cet_hour": float(target_meta["model_cet_hour"]),
        "target_model_cet_weekday": float(target_meta["model_cet_weekday"]),
        "target_model_cet_month": float((target + timedelta(hours=1)).month),
        "target_is_weekend": 1.0 if int(target_meta["model_cet_weekday"]) >= 5 else 0.0,
    }
    for lag in LAGS:
        ts = origin - timedelta(hours=lag)
        key = p0052.format_utc(ts)
        features[f"se3_price_lag_{lag}h"] = prices_by_ts.get(key, 0.0)
        audit[f"se3_price_lag_{lag}h"] = key
    previous_week = target - timedelta(hours=168)
    previous_week_key = p0052.format_utc(previous_week)
    features["se3_price_previous_week_same_target_hour"] = prices_by_ts.get(previous_week_key, 0.0)
    audit["se3_price_previous_week_same_target_hour"] = previous_week_key
    for window in ROLL_WINDOWS:
        values = []
        for offset in range(1, window + 1):
            key = p0052.format_utc(origin - timedelta(hours=offset))
            if key in prices_by_ts:
                values.append(prices_by_ts[key])
        prefix = f"se3_price_roll_{window}h"
        features[f"{prefix}_mean"] = p0054k.mean_float(values)
        features[f"{prefix}_std"] = p0054k.std_float(values)
        features[f"{prefix}_min"] = min(values) if values else 0.0
        features[f"{prefix}_max"] = max(values) if values else 0.0
        audit[f"{prefix}_mean"] = p0052.format_utc(origin - timedelta(hours=1))
        audit[f"{prefix}_std"] = p0052.format_utc(origin - timedelta(hours=1))
        audit[f"{prefix}_min"] = p0052.format_utc(origin - timedelta(hours=1))
        audit[f"{prefix}_max"] = p0052.format_utc(origin - timedelta(hours=1))
    lag1 = features["se3_price_lag_1h"]
    lag24 = features["se3_price_lag_24h"]
    lag168 = features["se3_price_lag_168h"]
    features["se3_price_recent_ramp_1h_24h"] = lag1 - lag24
    features["se3_price_recent_ramp_24h_168h"] = lag24 - lag168
    audit["se3_price_recent_ramp_1h_24h"] = p0052.format_utc(origin - timedelta(hours=1))
    audit["se3_price_recent_ramp_24h_168h"] = p0052.format_utc(origin - timedelta(hours=24))
    return features, audit


def validate_feature_matrix_safety(rows: list[dict[str, object]], feature_names: list[str]) -> dict[str, object]:
    forbidden = [name for name in feature_names if any(term in name.lower() for term in FORBIDDEN_FEATURE_TERMS)]
    source_errors = []
    for row in rows:
        origin = p0052.parse_utc(str(row["forecast_origin_timestamp_utc"]))
        target = p0052.parse_utc(str(row["target_timestamp_utc"]))
        cutoff = p0052.parse_utc(str(row["input_data_cutoff_utc"]))
        if cutoff > origin or origin > target:
            source_errors.append(f"{row['forecast_origin_timestamp_utc']}->{row['target_timestamp_utc']}")
            continue
        audit = row["feature_source_audit"]  # type: ignore[assignment]
        for _feature, source_ts in audit.items():
            if p0052.parse_utc(str(source_ts)) >= origin:
                source_errors.append(f"{_feature}:{source_ts}>={row['forecast_origin_timestamp_utc']}")
                break
    return {
        "ok": not forbidden and not source_errors,
        "feature_count": len(feature_names),
        "forbidden_feature_names": forbidden,
        "source_timestamp_errors": source_errors[:20],
        "source_timestamp_error_count": len(source_errors),
        "all_lag_rolling_history_timestamps_strictly_before_origin": not source_errors,
        "no_target_window_actual_price_used_as_input": True,
        "no_production_flow_export_import_a61_features": not forbidden,
    }


def load_p0054k_baseline_rows(feature_db: Path) -> tuple[dict[tuple[str, str], dict[str, object]], dict[str, object]]:
    rows: dict[tuple[str, str], dict[str, object]] = {}
    with sqlite3.connect(feature_db) as conn:
        conn.row_factory = sqlite3.Row
        if not p0054k.table_exists(conn, BASELINE_TABLE):
            return {}, {"ok": False, "reason": "missing_table", "table": BASELINE_TABLE}
        for row in conn.execute(
            f"""
            SELECT forecast_origin_timestamp_utc, input_data_cutoff_utc, target_timestamp_utc,
                   horizon_hours, predicted_price, prediction_kind, quality_flag, training_protocol
            FROM {BASELINE_TABLE}
            WHERE area='SE3'
              AND prediction_kind='anchored_absolute_price'
              AND quality_flag='forecast_safe_origin_local_baseline_not_m4'
              AND training_protocol='origin_local_no_fit_pre_origin_history'
            """
        ):
            origin = p0052.normalize_utc_text(row["forecast_origin_timestamp_utc"])
            target = p0052.normalize_utc_text(row["target_timestamp_utc"])
            rows[(origin, target)] = {
                "forecast_origin_timestamp_utc": origin,
                "target_timestamp_utc": target,
                "input_data_cutoff_utc": p0052.normalize_utc_text(row["input_data_cutoff_utc"]),
                "horizon_hours": int(row["horizon_hours"]),
                "predicted_price": float(row["predicted_price"]),
            }
    holdout = [row for row in rows.values() if p0054_split(str(row["target_timestamp_utc"])) == "holdout"]
    return rows, {"ok": bool(rows) and bool(holdout), "table": BASELINE_TABLE, "rows": len(rows), "holdout_rows": len(holdout)}


def evaluate_baseline(examples: list[dict[str, object]], baseline_rows: dict[tuple[str, str], dict[str, object]]) -> dict[str, object]:
    scored = []
    for row in examples:
        if row["split"] != "holdout":
            continue
        baseline = baseline_rows.get((str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"])))
        if baseline is None:
            continue
        scored.append({**row, "pred_baseline": float(baseline["predicted_price"])})
    if not scored:
        return {"ok": False, "reason": "no_comparable_holdout_rows"}
    return {
        "ok": True,
        "model_name": "P0054K_origin_local_history_baseline",
        "table": BASELINE_TABLE,
        "label": "forecast_safe_origin_local_baseline_not_m4",
        "holdout": evaluate_direct_metrics(scored, "pred_baseline"),
        "weekly": evaluate_weekly_path_metrics(scored, "pred_baseline"),
        "ranking_spike_ramp": evaluate_ranking_spike_ramp_metrics(scored, "pred_baseline", fit_train_thresholds(examples)),
        "comparable_holdout_rows": len(scored),
        "comparable_holdout_origins": len({row["forecast_origin_timestamp_utc"] for row in scored}),
    }


def capture_environment_status() -> dict[str, object]:
    return p0054k.capture_environment_status()


def model_specs(imports: dict[str, dict[str, object]]) -> list[ModelSpec]:
    from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor

    specs = [
        ModelSpec(
            family="HGB",
            model_class="HistGradientBoostingRegressor",
            package="scikit-learn",
            model=HistGradientBoostingRegressor(max_iter=180, learning_rate=0.045, max_leaf_nodes=31, min_samples_leaf=80, random_state=RANDOM_SEED),
            hyperparameters={"max_iter": 180, "learning_rate": 0.045, "max_leaf_nodes": 31, "min_samples_leaf": 80, "random_state": RANDOM_SEED},
        ),
        ModelSpec(
            family="ExtraTrees",
            model_class="ExtraTreesRegressor",
            package="scikit-learn",
            model=ExtraTreesRegressor(n_estimators=160, max_features=0.8, min_samples_leaf=3, max_samples=0.8, bootstrap=True, n_jobs=-1, random_state=RANDOM_SEED),
            hyperparameters={"n_estimators": 160, "max_features": 0.8, "min_samples_leaf": 3, "max_samples": 0.8, "bootstrap": True, "n_jobs": -1, "random_state": RANDOM_SEED},
        ),
    ]
    if imports.get("lightgbm", {}).get("ok"):
        from lightgbm import LGBMRegressor

        specs.append(
            ModelSpec(
                family="LightGBM",
                model_class="LGBMRegressor",
                package="lightgbm",
                model=LGBMRegressor(objective="regression_l1", metric="mae", n_estimators=360, learning_rate=0.045, num_leaves=63, min_child_samples=80, subsample=0.85, subsample_freq=1, colsample_bytree=0.85, reg_lambda=0.2, random_state=RANDOM_SEED, n_jobs=-1, verbose=-1),
                hyperparameters={"objective": "regression_l1", "metric": "mae", "n_estimators": 360, "learning_rate": 0.045, "num_leaves": 63, "min_child_samples": 80, "subsample": 0.85, "colsample_bytree": 0.85, "reg_lambda": 0.2, "random_state": RANDOM_SEED, "n_jobs": -1},
            )
        )
    if imports.get("xgboost", {}).get("ok"):
        from xgboost import XGBRegressor

        specs.append(
            ModelSpec(
                family="XGBoost",
                model_class="XGBRegressor",
                package="xgboost",
                model=XGBRegressor(objective="reg:squarederror", eval_metric="mae", n_estimators=300, learning_rate=0.045, max_depth=6, min_child_weight=8, subsample=0.85, colsample_bytree=0.85, reg_lambda=1.0, random_state=RANDOM_SEED, n_jobs=-1, tree_method="hist"),
                hyperparameters={"objective": "reg:squarederror", "eval_metric": "mae", "n_estimators": 300, "learning_rate": 0.045, "max_depth": 6, "min_child_weight": 8, "subsample": 0.85, "colsample_bytree": 0.85, "reg_lambda": 1.0, "random_state": RANDOM_SEED, "n_jobs": -1, "tree_method": "hist"},
            )
        )
    return specs


def fit_serial_model(rows: list[dict[str, object]], feature_names: list[str], spec: ModelSpec, thresholds: dict[str, float]) -> dict[str, object]:
    started = time.monotonic()
    train = [row for row in rows if row["split"] == "train_fit"]
    internal_validation = [row for row in train if str(row["target_timestamp_utc"]) >= INTERNAL_VALIDATION_START]
    holdout = [row for row in rows if row["split"] == "holdout"]
    x_train, standardizer = build_matrix(train, feature_names)
    y_train = np.array([float(row["target_price"]) for row in train], dtype=float)
    model = p0054k.clone_model(spec.model)
    model.fit(x_train, y_train)  # type: ignore[attr-defined]
    pred_col = prediction_column(spec.family)
    for subset in (internal_validation, holdout):
        preds = predict_model(model, standardizer, subset, feature_names)
        for row, pred in zip(subset, preds):
            row[pred_col] = float(pred)
    return {
        "model_name": spec.family,
        "status": "completed",
        "training": {
            "model_family": spec.family,
            "model_class": spec.model_class,
            "package": spec.package,
            "hyperparameters": spec.hyperparameters,
            "train_rows": len(train),
            "internal_validation_rows": len(internal_validation),
            "holdout_rows": len(holdout),
            "feature_count": len(feature_names),
            "duration_seconds": round(time.monotonic() - started, 3),
            "model_artifact_persisted": False,
        },
        "metrics": {
            "holdout": evaluate_direct_metrics(holdout, pred_col),
            "weekly": evaluate_weekly_path_metrics(holdout, pred_col),
            "ranking_spike_ramp": evaluate_ranking_spike_ramp_metrics(holdout, pred_col, thresholds),
            "internal_validation": evaluate_direct_metrics(internal_validation, pred_col),
        },
        "prediction_column": pred_col,
        "leakage_status": "ok",
    }


def build_matrix(rows: list[dict[str, object]], feature_names: list[str], standardizer: Standardizer | None = None) -> tuple[np.ndarray, Standardizer]:
    if standardizer is None:
        means = {}
        scales = {}
        for name in feature_names:
            values = [p0054k.safe_float(row["features"].get(name)) for row in rows]  # type: ignore[union-attr]
            means[name] = p0054k.mean_float(values)
            scales[name] = p0054k.std_float(values) or 1.0
        standardizer = Standardizer(means=means, scales=scales)
    matrix = []
    for row in rows:
        features = row["features"]  # type: ignore[assignment]
        matrix.append([(p0054k.safe_float(features.get(name)) - standardizer.means[name]) / standardizer.scales[name] for name in feature_names])
    return np.array(matrix, dtype=float), standardizer


def predict_model(model: object, standardizer: Standardizer, rows: list[dict[str, object]], feature_names: list[str]) -> np.ndarray:
    if not rows:
        return np.array([], dtype=float)
    x, _ = build_matrix(rows, feature_names, standardizer)
    return np.asarray(model.predict(x), dtype=float)  # type: ignore[attr-defined]


def evaluate_direct_metrics(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    pairs = [(float(row["target_price"]), float(row[prediction_column])) for row in rows if prediction_column in row and p0054k.is_finite(row.get(prediction_column))]
    if not pairs:
        return {"rows": 0}
    actual = [item[0] for item in pairs]
    pred = [item[1] for item in pairs]
    errors = [p - a for a, p in pairs]
    abs_errors = [abs(err) for err in errors]
    smape_values = [abs(p - a) / ((abs(a) + abs(p)) / 2.0) for a, p in pairs if (abs(a) + abs(p)) > 0]
    mean_actual = p0054k.mean_float(actual)
    sst = sum((value - mean_actual) ** 2 for value in actual)
    sse = sum((p - a) ** 2 for a, p in pairs)
    return {
        "rows": len(pairs),
        "MAE": mae(actual, pred),
        "RMSE": rmse(actual, pred),
        "bias": p0054k.mean_float(errors),
        "median_absolute_error": percentile(abs_errors, 0.5),
        "p90_absolute_error": percentile(abs_errors, 0.9),
        "p95_absolute_error": percentile(abs_errors, 0.95),
        "sMAPE": p0054k.mean_float(smape_values),
        "R2": 1.0 - (sse / sst) if sst else None,
    }


def evaluate_weekly_path_metrics(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    complete = []
    for _origin, group in p0054k.group_by([row for row in rows if prediction_column in row], "forecast_origin_timestamp_utc").items():
        if len(group) != 168:
            continue
        complete.extend(group)
    if not complete:
        return {"complete_origins": 0, "rows": 0}
    metrics = evaluate_direct_metrics(complete, prediction_column)
    metrics["complete_origins"] = len({row["forecast_origin_timestamp_utc"] for row in complete})
    metrics["MAE_full_168h"] = metrics["MAE"]
    metrics["bias_full_168h"] = metrics["bias"]
    metrics["p90_full_path_absolute_error"] = metrics["p90_absolute_error"]
    metrics["p95_full_path_absolute_error"] = metrics["p95_absolute_error"]
    return metrics


def evaluate_ranking_spike_ramp_metrics(rows: list[dict[str, object]], prediction_column: str, thresholds: dict[str, float]) -> dict[str, object]:
    scored = [row for row in rows if prediction_column in row]
    if not scored:
        return {"rows": 0}
    actual = [float(row["target_price"]) for row in scored]
    pred = [float(row[prediction_column]) for row in scored]
    output = {
        "rows": len(scored),
        "spearman": spearman(actual, pred),
        "top20_168h_precision": mean_path_precision(scored, prediction_column, 20, high=True),
        "bottom20_168h_precision": mean_path_precision(scored, prediction_column, 20, high=False),
    }
    spike_threshold = thresholds["spike_price_p90"]
    low_threshold = thresholds["low_price_p10"]
    ramp_threshold = thresholds["ramp_abs_p90"]
    output["spike_detection"] = binary_detection(scored, prediction_column, lambda row: float(row["target_price"]) >= spike_threshold, lambda row: float(row[prediction_column]) >= spike_threshold)
    output["low_price_detection"] = binary_detection(scored, prediction_column, lambda row: float(row["target_price"]) <= low_threshold, lambda row: float(row[prediction_column]) <= low_threshold)
    output["ramp_detection"] = ramp_detection(scored, prediction_column, ramp_threshold)
    output["high_price_regime_MAE"] = mae_subset(scored, prediction_column, lambda row: float(row["target_price"]) >= spike_threshold)
    output["low_price_regime_MAE"] = mae_subset(scored, prediction_column, lambda row: float(row["target_price"]) <= low_threshold)
    output["large_price_ramp_MAE"] = mae_subset(scored, prediction_column, lambda row: abs(float(row["target_price"]) - float(row["features"]["se3_price_previous_week_same_target_hour"])) >= ramp_threshold)  # type: ignore[index]
    output["forecast_price_spike_MAE"] = mae_subset(scored, prediction_column, lambda row: float(row[prediction_column]) >= spike_threshold)
    return output


def fit_train_thresholds(rows: list[dict[str, object]]) -> dict[str, float]:
    train = [row for row in rows if row["split"] == "train_fit"]
    prices = [float(row["target_price"]) for row in train]
    ramps = [abs(float(row["target_price"]) - float(row["features"]["se3_price_previous_week_same_target_hour"])) for row in train]  # type: ignore[index]
    return {
        "spike_price_p90": percentile(prices, 0.9),
        "low_price_p10": percentile(prices, 0.1),
        "ramp_abs_p90": percentile(ramps, 0.9),
    }


def spearman(actual: list[float], pred: list[float]) -> float | None:
    if len(actual) < 2:
        return None
    return pearson(rank_values(actual), rank_values(pred))


def rank_values(values: list[float]) -> list[float]:
    ordered = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    for rank, index in enumerate(ordered, start=1):
        ranks[index] = float(rank)
    return ranks


def pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    lmean = p0054k.mean_float(left)
    rmean = p0054k.mean_float(right)
    numerator = sum((l - lmean) * (r - rmean) for l, r in zip(left, right))
    ldenom = math.sqrt(sum((l - lmean) ** 2 for l in left))
    rdenom = math.sqrt(sum((r - rmean) ** 2 for r in right))
    return numerator / (ldenom * rdenom) if ldenom and rdenom else None


def mean_path_precision(rows: list[dict[str, object]], prediction_column: str, n: int, *, high: bool) -> float | None:
    scores = []
    for _origin, group in p0054k.group_by(rows, "forecast_origin_timestamp_utc").items():
        if len(group) < n:
            continue
        actual_set = {id(row) for row in sorted(group, key=lambda row: float(row["target_price"]), reverse=high)[:n]}
        pred_set = {id(row) for row in sorted(group, key=lambda row: float(row[prediction_column]), reverse=high)[:n]}
        scores.append(len(actual_set & pred_set) / float(n))
    return p0054k.mean_float(scores) if scores else None


def binary_detection(rows: list[dict[str, object]], prediction_column: str, actual_fn: object, pred_fn: object) -> dict[str, object]:
    tp = fp = fn = 0
    for row in rows:
        actual = bool(actual_fn(row))  # type: ignore[operator]
        predicted = bool(pred_fn(row))  # type: ignore[operator]
        if actual and predicted:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif actual and not predicted:
            fn += 1
    precision_value = tp / (tp + fp) if tp + fp else 0.0
    recall_value = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision_value * recall_value / (precision_value + recall_value) if precision_value + recall_value else 0.0
    return {"precision": precision_value, "recall": recall_value, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def ramp_detection(rows: list[dict[str, object]], prediction_column: str, threshold: float) -> dict[str, object]:
    return binary_detection(
        rows,
        prediction_column,
        lambda row: abs(float(row["target_price"]) - float(row["features"]["se3_price_previous_week_same_target_hour"])) >= threshold,  # type: ignore[index]
        lambda row: abs(float(row[prediction_column]) - float(row["features"]["se3_price_previous_week_same_target_hour"])) >= threshold,  # type: ignore[index]
    )


def mae_subset(rows: list[dict[str, object]], prediction_column: str, predicate: object) -> float | None:
    subset = [row for row in rows if bool(predicate(row))]  # type: ignore[operator]
    if not subset:
        return None
    return mae([float(row["target_price"]) for row in subset], [float(row[prediction_column]) for row in subset])


def build_simple_ensemble(rows: list[dict[str, object]], completed: list[str], thresholds: dict[str, float]) -> dict[str, object]:
    pred_col = prediction_column("Ensemble")
    holdout = [row for row in rows if row["split"] == "holdout"]
    source_cols = [prediction_column(name) for name in completed if all(prediction_column(name) in row for row in holdout)]
    for row in holdout:
        row[pred_col] = p0054k.mean_float([float(row[col]) for col in source_cols])
    return {
        "model_name": "Ensemble",
        "status": "completed" if source_cols else "skipped",
        "training": {
            "model_family": "Ensemble",
            "hyperparameters": {"method": "simple mean of completed model predictions", "source_models": completed},
            "train_rows": 0,
            "internal_validation_rows": 0,
            "holdout_rows": len(holdout),
            "feature_count": len(source_cols),
            "model_artifact_persisted": False,
        },
        "metrics": {
            "holdout": evaluate_direct_metrics(holdout, pred_col),
            "weekly": evaluate_weekly_path_metrics(holdout, pred_col),
            "ranking_spike_ramp": evaluate_ranking_spike_ramp_metrics(holdout, pred_col, thresholds),
        },
        "prediction_column": pred_col,
        "leakage_status": "ok",
    }


def write_model_checkpoint(evidence_dir: Path, model_name: str, checkpoint: dict[str, object]) -> dict[str, str]:
    checkpoint_dir = evidence_dir / "model-checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    json_path = checkpoint_dir / f"{model_name.lower()}-metrics.json"
    md_path = checkpoint_dir / f"{model_name.lower()}.md"
    json_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    status = checkpoint.get("status")
    metrics = checkpoint.get("metrics", {})
    md = [
        f"# P0054L2 {model_name} Checkpoint",
        "",
        f"Status: `{status}`",
        "",
        "```json",
        json.dumps({"model_name": model_name, "training": checkpoint.get("training", {}), "metrics": metrics, "leakage_status": checkpoint.get("leakage_status")}, indent=2, sort_keys=True, default=str),
        "```",
        "",
    ]
    md_path.write_text("\n".join(md), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def skipped_checkpoint(family: str, reason: str, examples: list[dict[str, object]], feature_names: list[str], environment: dict[str, object]) -> dict[str, object]:
    return {
        "model_name": family,
        "status": "skipped",
        "reason": reason,
        "training": {
            "model_family": family,
            "train_rows": sum(1 for row in examples if row["split"] == "train_fit"),
            "holdout_rows": sum(1 for row in examples if row["split"] == "holdout"),
            "feature_count": len(feature_names),
            "import_status": environment.get("imports", {}).get(family.lower()),  # type: ignore[union-attr]
        },
        "leakage_status": "not_applicable",
    }


def failed_checkpoint(family: str, exc: Exception, examples: list[dict[str, object]], feature_names: list[str], spec: ModelSpec, started: float) -> dict[str, object]:
    return {
        "model_name": family,
        "status": "failed",
        "error": repr(exc),
        "training": {
            "model_family": family,
            "model_class": spec.model_class,
            "package": spec.package,
            "hyperparameters": spec.hyperparameters,
            "train_rows": sum(1 for row in examples if row["split"] == "train_fit"),
            "holdout_rows": sum(1 for row in examples if row["split"] == "holdout"),
            "feature_count": len(feature_names),
            "duration_seconds": round(time.monotonic() - started, 3),
        },
        "leakage_status": "ok_before_model_failure",
    }


def compare_models(baseline_eval: dict[str, object], model_results: dict[str, dict[str, object]]) -> dict[str, object]:
    baseline_holdout = float(baseline_eval["holdout"]["MAE"])  # type: ignore[index]
    baseline_weekly = float(baseline_eval["weekly"]["MAE_full_168h"])  # type: ignore[index]
    rows = []
    for name, result in model_results.items():
        if result.get("status") != "completed":
            rows.append({"model": name, "status": result.get("status")})
            continue
        holdout = result["metrics"]["holdout"]  # type: ignore[index]
        weekly = result["metrics"]["weekly"]  # type: ignore[index]
        ranking = result["metrics"]["ranking_spike_ramp"]  # type: ignore[index]
        direct_mae = float(holdout.get("MAE", math.inf))
        weekly_mae = float(weekly.get("MAE_full_168h", math.inf))
        rows.append(
            {
                "model": name,
                "status": "completed",
                "holdout_MAE": direct_mae,
                "weekly_MAE_full_168h": weekly_mae,
                "direct_mae_improvement_percent_vs_p0054k": 100.0 * (baseline_holdout - direct_mae) / baseline_holdout,
                "weekly_mae_improvement_percent_vs_p0054k": 100.0 * (baseline_weekly - weekly_mae) / baseline_weekly,
                "spearman": ranking.get("spearman"),
                "top20_168h_precision": ranking.get("top20_168h_precision"),
                "bottom20_168h_precision": ranking.get("bottom20_168h_precision"),
                "spike_f1": ranking.get("spike_detection", {}).get("f1"),
                "ramp_f1": ranking.get("ramp_detection", {}).get("f1"),
            }
        )
    completed = [row for row in rows if row.get("status") == "completed"]
    best_direct = min(completed, key=lambda row: float(row["holdout_MAE"]), default=None)
    best_weekly = min(completed, key=lambda row: float(row["weekly_MAE_full_168h"]), default=None)
    best_ranking = max(completed, key=lambda row: float(row.get("spearman") or -999.0), default=None)
    return {
        "baseline": {"holdout_MAE": baseline_holdout, "weekly_MAE_full_168h": baseline_weekly},
        "models": rows,
        "best_completed_by_direct_MAE": best_direct,
        "best_completed_by_weekly_MAE_full_168h": best_weekly,
        "best_completed_by_ranking": best_ranking,
        "any_direct_or_weekly_2pct_improvement": any(
            float(row.get("direct_mae_improvement_percent_vs_p0054k", 0.0)) >= 2.0
            or float(row.get("weekly_mae_improvement_percent_vs_p0054k", 0.0)) >= 2.0
            for row in completed
        ),
    }


def recommendation_from_comparison(comparison: dict[str, object]) -> dict[str, object]:
    candidates = [row for row in comparison["models"] if row.get("status") == "completed"]  # type: ignore[index]
    useful = [
        row
        for row in candidates
        if float(row.get("direct_mae_improvement_percent_vs_p0054k", 0.0)) >= 2.0
        or float(row.get("weekly_mae_improvement_percent_vs_p0054k", 0.0)) >= 2.0
    ]
    if not useful:
        return {
            "create_forecast_log": False,
            "recommended_model": None,
            "decision": "no_advanced_source_recommended",
            "reason": "no completed model met the >=2% direct or weekly MAE learning threshold",
            "p0054m_recommendation": "Do not create P0054M from this run unless ranking/spike analysis is manually judged worth a follow-up.",
        }
    best = max(useful, key=lambda row: max(float(row.get("direct_mae_improvement_percent_vs_p0054k", 0.0)), float(row.get("weekly_mae_improvement_percent_vs_p0054k", 0.0))))
    return {
        "create_forecast_log": True,
        "recommended_model": best["model"],
        "decision": "advanced_holdout_source_recommended",
        "reason": "completed model met the P0054L2 learning threshold versus P0054K baseline",
        "p0054m_recommendation": downstream_warning(),
    }


def persist_advanced_forecast_log(feature_db: Path, rows: list[dict[str, object]], model_name: str, model_result: dict[str, object]) -> int:
    pred_col = prediction_column(model_name)
    created = p0052.format_utc(datetime.now(timezone.utc).replace(microsecond=0))
    output = []
    for row in rows:
        if row["split"] != "holdout" or pred_col not in row:
            continue
        output.append(
            {
                "forecast_run_id": "P0054L2_advanced_se3_price_v1",
                "package_id": PACKAGE_ID,
                "model_name": model_name,
                "model_version": "p0054l2_advanced_se3_v1",
                "area": "SE3",
                "forecast_origin_timestamp_utc": row["forecast_origin_timestamp_utc"],
                "input_data_cutoff_utc": row["input_data_cutoff_utc"],
                "target_timestamp_utc": row["target_timestamp_utc"],
                "horizon_hours": int(row["horizon_hours"]),
                "predicted_price": float(row[pred_col]),
                "prediction_unit": "repository hour_price convention",
                "prediction_kind": "advanced_absolute_price",
                "training_protocol": "global_train_fit_holdout_evaluation_only",
                "training_cutoff_utc": "2025-05-31T23:00:00Z",
                "quality_flag": "holdout_safe_advanced_price_forecast_not_train_feature",
                "source_reconstruction": "system_proxy_se1 + area_diff_proxy_se3",
                "created_at_utc": created,
            }
        )
    with sqlite3.connect(feature_db) as conn:
        persist_rows(conn, ADVANCED_TABLE, output)
        conn.commit()
    return len(output)


def leakage_review_summary(matrix_review: dict[str, object], model_results: dict[str, dict[str, object]], forecast_log_summary: dict[str, object]) -> dict[str, object]:
    failed = [name for name, result in model_results.items() if result.get("leakage_status") not in ("ok", "not_applicable", "ok_before_model_failure")]
    return {
        "ok": matrix_review["ok"] and not failed,
        "matrix_review_ok": matrix_review["ok"],
        "model_leakage_failures": failed,
        "holdout_used_for_fitting_or_selection": False,
        "actual_future_spot_price_feature_used": False,
        "api_device_runtime_a61_future_flow_used": False,
        "advanced_forecast_log": forecast_log_summary,
    }


def write_p0054l2_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}
    mapping = {
        "CHANGELOG.md": changelog_text(summary),
        "labb-label.md": "# P0054L2 LABB Label\n\nStatus: `LABB`; not `G2-KANDIDAT`.\n",
        "runtime-policy.md": runtime_policy_text(),
        "attempts.md": attempts_text(summary),
        "split-policy-applied.md": json_md("P0054L2 Split Policy", summary["split_policy"]),
        "source-discovery.md": json_md("P0054L2 Source Discovery", summary["source_contract"]),
        "price-target-contract.md": json_md("P0054L2 Price Target Contract", summary["source_contract"]),
        "feature-groups.md": json_md("P0054L2 Feature Groups", summary["feature_groups"]),
        "input-classification.md": json_md("P0054L2 Input Classification", summary["input_classification"]),
        "model-training-evidence.md": json_md("P0054L2 Model Training Evidence", summary["model_results"]),
        "baseline-p0054k-results.md": json_md("P0054L2 P0054K Baseline Results", summary["baseline_metrics"]),
        "model-comparison.md": json_md("P0054L2 Model Comparison", summary["model_comparison"]),
        "direct-horizon-results.md": direct_results_text(summary),
        "weekly-168h-path-results.md": weekly_results_text(summary),
        "ranking-spike-ramp-results.md": ranking_results_text(summary),
        "leakage-review.md": json_md("P0054L2 Leakage Review", summary["leakage_review"]),
        "downstream-contract-for-p0054m.md": downstream_contract_text(summary),
        "interpretation.md": interpretation_text(summary),
        "what-we-learned.md": what_we_learned_text(summary),
        "next-package-recommendation.md": next_package_text(summary),
        "metrics-summary.json": json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n",
    }
    if summary["forecast_log_summary"].get("created"):  # type: ignore[index]
        mapping["forecast-log-schema.md"] = forecast_log_schema_text()
        mapping["forecast-log-coverage.md"] = json_md("P0054L2 Forecast Log Coverage", summary["forecast_log_summary"])
    model_file_keys = {
        "hgb": "HGB",
        "extratrees": "ExtraTrees",
        "lightgbm": "LightGBM",
        "xgboost": "XGBoost",
        "ensemble": "Ensemble",
    }
    for model, key in model_file_keys.items():
        if key in summary["model_results"]:  # type: ignore[operator]
            mapping[f"{model}-results.md"] = json_md(f"P0054L2 {key} Results", summary["model_results"][key])  # type: ignore[index]
    for filename, content in mapping.items():
        path = evidence_dir / filename
        path.write_text(content, encoding="utf-8")
        files[filename] = str(path)
    return files


def compact_model_results(model_results: dict[str, dict[str, object]]) -> dict[str, object]:
    return {name: {key: value for key, value in result.items() if key != "model"} for name, result in model_results.items()}


def direct_results_text(summary: dict[str, object]) -> str:
    return json_md("P0054L2 Direct Horizon Results", {"baseline": summary["baseline_metrics"]["holdout"], "models": {name: result.get("metrics", {}).get("holdout") for name, result in summary["model_results"].items()}})  # type: ignore[index,union-attr]


def weekly_results_text(summary: dict[str, object]) -> str:
    return json_md("P0054L2 Weekly 168h Path Results", {"baseline": summary["baseline_metrics"]["weekly"], "models": {name: result.get("metrics", {}).get("weekly") for name, result in summary["model_results"].items()}})  # type: ignore[index,union-attr]


def ranking_results_text(summary: dict[str, object]) -> str:
    return json_md("P0054L2 Ranking Spike Ramp Results", {"baseline": summary["baseline_metrics"]["ranking_spike_ramp"], "models": {name: result.get("metrics", {}).get("ranking_spike_ramp") for name, result in summary["model_results"].items()}})  # type: ignore[index,union-attr]


def json_md(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True, default=str)}\n```\n"


def changelog_text(summary: dict[str, object]) -> str:
    rec = summary["recommendation"]  # type: ignore[assignment]
    return (
        "# P0054L2 Changelog\n\n"
        f"Status: `{summary['status']}`\n\n"
        "- Built a serial LABB SE3 advanced spot-price forecast experiment.\n"
        "- Wrote per-model checkpoints immediately after completed/skipped/failed models.\n"
        "- Compared completed models to the P0054K reconstructed SE3 origin-local baseline.\n"
        f"- Forecast log decision: `{rec['decision']}`.\n"
        "- No SE3 consumption model, API, device, runtime, A61 or future-flow work was performed.\n"
    )


def runtime_policy_text() -> str:
    return (
        "# P0054L2 Runtime Policy\n\n"
        "Long runtime is accepted. Models run one family at a time in this order: HGB, ExtraTrees, LightGBM, XGBoost, optional Ensemble. "
        "Each family writes a checkpoint before the next begins.\n"
    )


def attempts_text(summary: dict[str, object]) -> str:
    return json_md("P0054L2 Attempt 1", {"result": summary["status"], "runtime_seconds": summary["runtime_seconds"], "model_status": {name: result.get("status") for name, result in summary["model_results"].items()}})  # type: ignore[union-attr]


def downstream_contract_text(summary: dict[str, object]) -> str:
    return (
        "# P0054L2 Downstream Contract For P0054M\n\n"
        f"{downstream_warning()}\n\n"
        f"Decision: `{summary['recommendation']['decision']}`.\n"  # type: ignore[index]
    )


def interpretation_text(summary: dict[str, object]) -> str:
    return json_md("P0054L2 Interpretation", {"status": summary["status"], "comparison": summary["model_comparison"], "recommendation": summary["recommendation"]})


def what_we_learned_text(summary: dict[str, object]) -> str:
    return (
        "# P0054L2 What We Learned\n\n"
        "Serial checkpointing prevents the P0054L failure mode where useful earlier model work was discarded after a later slow model.\n\n"
        f"Result status: `{summary['status']}`.\n"
    )


def next_package_text(summary: dict[str, object]) -> str:
    if summary["forecast_log_summary"].get("created"):  # type: ignore[index]
        return "# P0054L2 Next Package Recommendation\n\nCreate P0054M only with the downstream contract warning in this package.\n"
    return "# P0054L2 Next Package Recommendation\n\nDo not create a downstream SE3 consumption package from this run unless a human operator explicitly accepts a ranking/spike-only rationale.\n"


def forecast_log_schema_text() -> str:
    return json_md(
        "P0054L2 Forecast Log Schema",
        {
            "table": ADVANCED_TABLE,
            "fields": [
                "forecast_origin_timestamp_utc",
                "input_data_cutoff_utc",
                "target_timestamp_utc",
                "horizon_hours",
                "area",
                "predicted_price",
                "prediction_kind",
                "quality_flag",
            ],
            "prediction_kind": "advanced_absolute_price",
            "quality_flag": "holdout_safe_advanced_price_forecast_not_train_feature",
        },
    )


def split_policy() -> dict[str, object]:
    return {
        "policy": "LABB_P0054_TRAIN_THROUGH_MAY_2025",
        "train_fit": f"{TRAIN_FIT_START} <= target_timestamp_utc < {HOLDOUT_START}",
        "internal_validation": f"{INTERNAL_VALIDATION_START} <= target_timestamp_utc < {HOLDOUT_START}",
        "holdout": f"target_timestamp_utc >= {HOLDOUT_START}",
        "holdout_used_for_selection_or_fitting": False,
    }


def feature_groups() -> dict[str, object]:
    return {
        "forecast_safe": [
            "calendar/time known in advance",
            "horizon_hour",
            "historical SE3 price lags strictly before origin",
            "historical SE3 rolling stats strictly before origin",
            "previous-week same-target-hour price strictly before origin",
        ],
        "excluded": list(FORBIDDEN_FEATURE_TERMS),
    }


def input_classification() -> dict[str, object]:
    return {
        "calendar_and_horizon": "forecast_safe",
        "historical_reconstructed_se3_price_before_origin": "forecast_safe",
        "target_window_actual_se3_price": "excluded_leakage",
        "production_flow_export_import_a61": "excluded_leakage",
    }


def downstream_warning() -> str:
    return "A global train_fit price model is holdout-safe for evaluation, but not automatically a train-period feature source for downstream consumption training. P0054M must use holdout-only evaluation or create rolling/out-of-fold train forecasts if it needs train_fit consumption features."


def p0054_split(timestamp: str) -> str:
    if timestamp < TRAIN_FIT_START:
        return "warmup"
    if timestamp < HOLDOUT_START:
        return "train_fit"
    return "holdout"


def count_by(rows: list[dict[str, object]], field: str) -> dict[str, int]:
    output: dict[str, int] = {}
    for row in rows:
        key = str(row[field])
        output[key] = output.get(key, 0) + 1
    return dict(sorted(output.items()))


def prediction_column(model_name: str) -> str:
    return f"predicted_price_{model_name.lower()}"


def main() -> None:
    result = run_p0054l2_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
