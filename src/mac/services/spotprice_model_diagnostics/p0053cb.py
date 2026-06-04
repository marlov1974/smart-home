"""P0053C-B 48h anchored absolute SE1 price forecast log."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
import csv
import json
import math
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_model_diagnostics import p0045, p0053ca
from src.mac.services.spotprice_model_diagnostics.forecast_period_policy import (
    POLICY_VERSION,
    TRAIN_END_UTC,
    canonical_split_for_timestamp,
    parse_policy_timestamp,
    policy_summary,
)
from src.mac.services.spotprice_model_diagnostics.p0040 import spearman_from_ranks, top_indexes
from src.mac.services.spotprice_model_diagnostics.p0041 import persist_rows, percentile, write


PACKAGE_ID = "P0053C-B"
EVIDENCE_DIR = Path("requirements/package-runs/P0053C-B")
FORECAST_LOG_TABLE = "m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1"
SOURCE_SHAPE_TABLE = p0053ca.FORECAST_LOG_TABLE
MODEL_NAME = "M4_P0045_48h_anchored_absolute_price"
MODEL_VERSION = "p0053cb_48h_anchor_v1"
FORECAST_RUN_ID = "P0053C-B_m4_48h_anchored_absolute_se1_v1"
SOURCE_SHAPE_RUN_ID = "P0053C-A_m4_shape_regenerated_validation_holdout"
AREA = "SE1"
TARGET_SERIES = "system_proxy_se1"
PREDICTION_UNIT = "source_hour_price_unit"
PREDICTION_KIND = "anchored_absolute_price"
ANCHOR_METHODS = ("A0_mean_std", "A1_median_iqr", "A2_last24_last48_blend_iqr", "A3_same_hour_48h_iqr")
BASELINE_METHODS = ("B0_last48_mean_flat", "B1_same_hour_hist48_flat", "B2_same_hour_previous_week", "B3_train_profile")


@dataclass(frozen=True)
class P0053CBResult:
    status: str
    selected_anchor: str
    forecast_log_rows: int
    evidence: dict[str, str]


def run_p0053cb_anchoring(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0053CBResult:
    started = time.monotonic()
    db_path = Path(feature_db).expanduser()
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        preconditions = validate_preconditions(conn)
    if not preconditions["ok"]:
        raise RuntimeError(f"P0053C-B preconditions failed: {preconditions}")

    windows, shape_predictions, selected_shape_formula, input_contract, window_counts = prepare_shape_windows(db_path)
    prices_by_ts, train_profile, actual_summary = load_actual_prices(db_path)
    evaluated_rows, anchor_evidence = evaluate_anchor_methods(windows, shape_predictions, prices_by_ts, train_profile)
    metrics = aggregate_metrics(evaluated_rows)
    selected_anchor = select_anchor_method(metrics)
    forecast_rows = build_forecast_origin_rows(evaluated_rows, selected_anchor)
    persisted_rows = persist_forecast_origin_log(db_path, forecast_rows)
    leakage = leakage_review(forecast_rows, anchor_evidence)
    baseline = baseline_comparison(metrics, selected_anchor)
    summary = {
        "status": status_from_summary(forecast_rows, leakage, metrics, selected_anchor),
        "package_id": PACKAGE_ID,
        "policy": policy_summary(),
        "preconditions": preconditions,
        "input_contract": input_contract,
        "actual_price_summary": actual_summary,
        "window_counts": window_counts,
        "source_shape_table": SOURCE_SHAPE_TABLE,
        "forecast_log_table": FORECAST_LOG_TABLE,
        "forecast_log_rows": persisted_rows,
        "selected_shape_formula": selected_shape_formula,
        "anchor_methods": anchor_method_definitions(),
        "selected_anchor": selected_anchor,
        "metrics": metrics,
        "baseline_comparison": baseline,
        "leakage_review": leakage,
        "anchor_evidence": anchor_evidence,
        "forecast_origin_contract": forecast_origin_contract(),
        "runtime_seconds": time.monotonic() - started,
    }
    evidence = write_p0053cb_evidence(Path(evidence_dir), summary, forecast_rows)
    return P0053CBResult(
        status=str(summary["status"]),
        selected_anchor=selected_anchor,
        forecast_log_rows=persisted_rows,
        evidence=evidence,
    )


def validate_preconditions(conn: sqlite3.Connection) -> dict[str, object]:
    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    shape_exists = SOURCE_SHAPE_TABLE in tables
    actual_exists = "ai2_hour_to_day_training_targets_v2" in tables
    shape_rows = 0
    shape_kinds: list[str] = []
    shape_units: list[str] = []
    if shape_exists:
        shape_rows = int(conn.execute(f"SELECT COUNT(*) FROM {SOURCE_SHAPE_TABLE}").fetchone()[0])
        shape_kinds = [str(row[0]) for row in conn.execute(f"SELECT DISTINCT prediction_kind FROM {SOURCE_SHAPE_TABLE} ORDER BY 1").fetchall()]
        shape_units = [str(row[0]) for row in conn.execute(f"SELECT DISTINCT prediction_unit FROM {SOURCE_SHAPE_TABLE} ORDER BY 1").fetchall()]
    actual_rows = 0
    actual_min = None
    actual_max = None
    if actual_exists:
        row = conn.execute(
            "SELECT COUNT(*), MIN(timestamp_utc), MAX(timestamp_utc) FROM ai2_hour_to_day_training_targets_v2 WHERE target_series=?",
            (TARGET_SERIES,),
        ).fetchone()
        actual_rows = int(row[0])
        actual_min = normalize_z(str(row[1])) if row[1] else None
        actual_max = normalize_z(str(row[2])) if row[2] else None
    ok = (
        shape_exists
        and actual_exists
        and shape_rows > 0
        and actual_rows > 0
        and shape_kinds == ["shape_index"]
        and shape_units == ["centered_shape_index"]
    )
    return {
        "ok": ok,
        "source_shape_table_exists": shape_exists,
        "source_shape_rows": shape_rows,
        "source_shape_prediction_kinds": shape_kinds,
        "source_shape_prediction_units": shape_units,
        "actual_price_table_exists": actual_exists,
        "actual_price_rows": actual_rows,
        "actual_price_min_timestamp_utc": actual_min,
        "actual_price_max_timestamp_utc": actual_max,
    }


def prepare_shape_windows(feature_db: Path) -> tuple[list[dict[str, object]], dict[str, list[float]], str, dict[str, object], dict[str, object]]:
    ai1_rows, ai2_rows = p0045.load_corrected_inputs(feature_db)
    input_contract = p0045.validate_input_contract(ai1_rows, ai2_rows)
    if not input_contract["ok"]:
        raise RuntimeError(f"P0053C-B input contract failed: {input_contract}")
    ai2_rows = p0053ca.filter_ai2_policy_rows(ai2_rows)
    p0053ca.assign_policy_splits(ai2_rows, "timestamp_utc")
    p0053ca.assign_ai1_policy_splits(ai1_rows)
    ai1_rows = [row for row in ai1_rows if row["split"] in {"train", "validate", "holdout"}]
    ai1_predictions = p0045.regenerate_ai1_predictions(ai1_rows)
    ai2_predictions = p0045.regenerate_ai2_predictions(ai2_rows)
    windows = [
        window
        for window in p0053ca.build_policy_forecast_windows(ai1_rows, ai2_rows)
        if window["target_series"] == TARGET_SERIES and window["split"] in {"validate", "holdout"}
    ]
    time_profiles = p0045.fit_time_profile_baselines(ai2_rows)
    window_results = p0045.evaluate_all_windows(windows, ai1_predictions, ai2_predictions, time_profiles)
    shape_metrics = p0045.summarize_metrics(window_results)
    shape_candidates = ("combined_scaled", "combined_dimensionless")
    selected_shape_formula = min(
        shape_candidates,
        key=lambda name: shape_metrics[TARGET_SERIES]["validate"][name]["shape_MAE_scaled"],
    )
    formula = "scaled" if selected_shape_formula == "combined_scaled" else "dimensionless"
    shape_predictions = {window_id(window): p0045.combine_window(window, ai1_predictions, ai2_predictions, formula) for window in windows}
    return windows, shape_predictions, selected_shape_formula, input_contract, p0045.window_counts(windows)


def load_actual_prices(feature_db: Path) -> tuple[dict[str, float], dict[tuple[int, int], float], dict[str, object]]:
    prices: dict[str, float] = {}
    train_profile_values: dict[tuple[int, int], list[float]] = defaultdict(list)
    with sqlite3.connect(feature_db) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT timestamp_utc, model_cet_weekday, model_cet_hour, hour_price FROM ai2_hour_to_day_training_targets_v2 WHERE target_series=? ORDER BY timestamp_utc",
            (TARGET_SERIES,),
        ).fetchall()
    for row in rows:
        timestamp = normalize_z(str(row["timestamp_utc"]))
        price = float(row["hour_price"])
        prices[timestamp] = price
        if parse_policy_timestamp(timestamp) <= TRAIN_END_UTC:
            train_profile_values[(int(row["model_cet_weekday"]), int(row["model_cet_hour"]))].append(price)
    train_profile = {key: sum(values) / len(values) for key, values in train_profile_values.items()}
    return prices, train_profile, {
        "rows": len(prices),
        "min_timestamp_utc": min(prices) if prices else None,
        "max_timestamp_utc": max(prices) if prices else None,
        "train_profile_cells": len(train_profile),
    }


def evaluate_anchor_methods(
    windows: list[dict[str, object]],
    shape_predictions: dict[str, list[float]],
    prices_by_ts: dict[str, float],
    train_profile: dict[tuple[int, int], float],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    anchor_samples = []
    skipped_windows = []
    for window in windows:
        origin = parse_policy_timestamp(normalize_z(str(window["hourly_rows"][0]["timestamp_utc"])))  # type: ignore[index]
        state = build_anchor_state(origin, prices_by_ts)
        actual = [prices_by_ts.get(normalize_z(str(row["timestamp_utc"]))) for row in window["hourly_rows"]]  # type: ignore[index]
        if len(state["hist48_prices"]) != 48 or any(value is None for value in actual):
            skipped_windows.append({"window_id": window_id(window), "hist48_count": len(state["hist48_prices"]), "actual_count": len([v for v in actual if v is not None])})
            continue
        shape = shape_predictions[window_id(window)]
        for method in ANCHOR_METHODS + BASELINE_METHODS:
            path_predictions = []
            for horizon, (hourly, shape_value, actual_price) in enumerate(zip(window["hourly_rows"], shape, actual)):  # type: ignore[index]
                target_ts = normalize_z(str(hourly["timestamp_utc"]))
                predicted, level, scale = predict_method(method, float(shape_value), hourly, horizon, origin, state, prices_by_ts, train_profile)
                path_predictions.append(predicted)
                rows.append(
                    {
                        "split": str(window["split"]),
                        "window_id": window_id(window),
                        "origin_date": str(window["origin_date"]),
                        "forecast_origin_timestamp_utc": normalize_z(origin),
                        "input_data_cutoff_utc": normalize_z(origin - timedelta(hours=1)),
                        "target_timestamp_utc": target_ts,
                        "horizon_hours": horizon,
                        "anchor_method": method,
                        "anchor_level": level,
                        "anchor_scale": scale,
                        "anchor_history_start_utc": normalize_z(state["history_start"]),
                        "anchor_history_end_utc": normalize_z(state["history_end"]),
                        "source_shape_value": float(shape_value),
                        "predicted_price": predicted,
                        "actual_price": float(actual_price),  # type: ignore[arg-type]
                        "quality_flag": "canonical" if method in ANCHOR_METHODS else "baseline_forecast_safe",
                    }
                )
            if len(anchor_samples) < 20 and method in ANCHOR_METHODS:
                anchor_samples.append(
                    {
                        "split": str(window["split"]),
                        "window_id": window_id(window),
                        "method": method,
                        "origin": normalize_z(origin),
                        "history_start": normalize_z(state["history_start"]),
                        "history_end": normalize_z(state["history_end"]),
                        "history_price_count": len(state["hist48_prices"]),
                        "first_target": normalize_z(str(window["hourly_rows"][0]["timestamp_utc"])),  # type: ignore[index]
                        "last_target": normalize_z(str(window["hourly_rows"][-1]["timestamp_utc"])),  # type: ignore[index]
                        "first_prediction": path_predictions[0],
                    }
                )
    return rows, {
        "skipped_windows": skipped_windows,
        "sample_anchor_windows": anchor_samples,
        "evaluated_rows": len(rows),
        "methods": list(ANCHOR_METHODS),
        "baselines": list(BASELINE_METHODS),
    }


def build_anchor_state(origin: datetime, prices_by_ts: dict[str, float]) -> dict[str, object]:
    history_start = origin - timedelta(hours=48)
    history_end = origin - timedelta(hours=1)
    hist_rows = []
    for offset in range(48):
        timestamp = history_start + timedelta(hours=offset)
        key = normalize_z(timestamp)
        if key in prices_by_ts:
            hist_rows.append((timestamp, prices_by_ts[key]))
    prices = [price for _timestamp, price in hist_rows]
    same_hour: dict[int, list[float]] = defaultdict(list)
    for timestamp, price in hist_rows:
        same_hour[(timestamp + timedelta(hours=1)).hour].append(price)
    last24 = prices[-24:]
    return {
        "history_start": history_start,
        "history_end": history_end,
        "hist48_rows": hist_rows,
        "hist48_prices": prices,
        "last24_prices": last24,
        "same_model_cet_hour": dict(same_hour),
        "mean": mean(prices),
        "std": population_std(prices),
        "median": median(prices),
        "iqr_scale": iqr_scale(prices),
        "last24_last48_level": 0.5 * mean(last24) + 0.5 * mean(prices),
    }


def predict_method(
    method: str,
    shape_value: float,
    hourly: dict[str, object],
    horizon: int,
    origin: datetime,
    state: dict[str, object],
    prices_by_ts: dict[str, float],
    train_profile: dict[tuple[int, int], float],
) -> tuple[float, float, float]:
    hist = state["hist48_prices"]  # type: ignore[assignment]
    if method == "A0_mean_std":
        level = float(state["mean"])
        scale = float(state["std"])
        return level + shape_value * scale, level, scale
    if method == "A1_median_iqr":
        level = float(state["median"])
        scale = float(state["iqr_scale"])
        return level + shape_value * scale, level, scale
    if method == "A2_last24_last48_blend_iqr":
        level = float(state["last24_last48_level"])
        scale = float(state["iqr_scale"])
        return level + shape_value * scale, level, scale
    if method == "A3_same_hour_48h_iqr":
        same_hour = state["same_model_cet_hour"]  # type: ignore[assignment]
        values = same_hour.get(int(hourly["model_cet_hour"]), hist)
        level = mean(values)
        scale = float(state["iqr_scale"])
        return level + shape_value * scale, level, scale
    if method == "B0_last48_mean_flat":
        level = float(state["mean"])
        return level, level, 0.0
    if method == "B1_same_hour_hist48_flat":
        same_hour = state["same_model_cet_hour"]  # type: ignore[assignment]
        values = same_hour.get(int(hourly["model_cet_hour"]), hist)
        level = mean(values)
        return level, level, 0.0
    if method == "B2_same_hour_previous_week":
        target = parse_policy_timestamp(normalize_z(str(hourly["timestamp_utc"])))
        previous = target - timedelta(hours=168)
        if previous >= origin:
            raise RuntimeError("previous-week baseline would leak future data")
        level = prices_by_ts[normalize_z(previous)]
        return level, level, 0.0
    if method == "B3_train_profile":
        key = (int(hourly["model_cet_weekday"]), int(hourly["model_cet_hour"]))
        level = float(train_profile[key])
        return level, level, 0.0
    raise ValueError(f"unknown method: {method}")


def aggregate_metrics(rows: list[dict[str, object]]) -> dict[str, dict[str, dict[str, float]]]:
    output: dict[str, dict[str, dict[str, float]]] = {}
    for split in ("validate", "holdout"):
        output[split] = {}
        for method in ANCHOR_METHODS + BASELINE_METHODS:
            method_rows = [row for row in rows if row["split"] == split and row["anchor_method"] == method]
            output[split][method] = aggregate_method_metrics(method_rows)
    return output


def aggregate_method_metrics(rows: list[dict[str, object]]) -> dict[str, float]:
    if not rows:
        return {"row_count": 0.0, "path_count": 0.0}
    actual = [float(row["actual_price"]) for row in rows]
    predicted = [float(row["predicted_price"]) for row in rows]
    errors = [pred - act for pred, act in zip(predicted, actual)]
    abs_errors = [abs(error) for error in errors]
    paths = group_by_window(rows)
    path_metrics = [path_metric(path_rows) for path_rows in paths.values() if len(path_rows) == 168]
    return {
        "row_count": float(len(rows)),
        "path_count": float(len(path_metrics)),
        "MAE": mae(actual, predicted),
        "RMSE": rmse(actual, predicted),
        "bias": sum(errors) / len(errors),
        "median_absolute_error": percentile(abs_errors, 0.50),
        "p90_absolute_error": percentile(abs_errors, 0.90),
        "p95_absolute_error": percentile(abs_errors, 0.95),
        "sMAPE": smape(actual, predicted),
        "correlation": pearson(actual, predicted),
        "spearman": spearman_from_ranks(p0045.ranks(actual), p0045.ranks(predicted)),
        "MAE_full_168h": mean([row["MAE_full_168h"] for row in path_metrics]),
        "RMSE_full_168h": mean([row["RMSE_full_168h"] for row in path_metrics]),
        "bias_full_168h": mean([row["bias_full_168h"] for row in path_metrics]),
        "top4_day_precision": mean([row["top4_day_precision"] for row in path_metrics]),
        "top8_day_precision": mean([row["top8_day_precision"] for row in path_metrics]),
        "bottom4_day_precision": mean([row["bottom4_day_precision"] for row in path_metrics]),
        "top20_168h_precision": mean([row["top20_168h_precision"] for row in path_metrics]),
        "bottom20_168h_precision": mean([row["bottom20_168h_precision"] for row in path_metrics]),
        "best8_168h_precision": mean([row["best8_168h_precision"] for row in path_metrics]),
        "worst8_168h_precision": mean([row["worst8_168h_precision"] for row in path_metrics]),
    }


def path_metric(rows: list[dict[str, object]]) -> dict[str, float]:
    ordered = sorted(rows, key=lambda row: int(row["horizon_hours"]))
    actual = [float(row["actual_price"]) for row in ordered]
    predicted = [float(row["predicted_price"]) for row in ordered]
    errors = [pred - act for pred, act in zip(predicted, actual)]
    top4 = []
    top8 = []
    bottom4 = []
    for day in range(7):
        lo = day * 24
        hi = lo + 24
        top4.append(hit_precision(actual[lo:hi], predicted[lo:hi], 4, high=True))
        top8.append(hit_precision(actual[lo:hi], predicted[lo:hi], 8, high=True))
        bottom4.append(hit_precision(actual[lo:hi], predicted[lo:hi], 4, high=False))
    return {
        "MAE_full_168h": mae(actual, predicted),
        "RMSE_full_168h": rmse(actual, predicted),
        "bias_full_168h": sum(errors) / len(errors),
        "top4_day_precision": mean(top4),
        "top8_day_precision": mean(top8),
        "bottom4_day_precision": mean(bottom4),
        "top20_168h_precision": hit_precision(actual, predicted, 20, high=True),
        "bottom20_168h_precision": hit_precision(actual, predicted, 20, high=False),
        "best8_168h_precision": hit_precision(actual, predicted, 8, high=True),
        "worst8_168h_precision": hit_precision(actual, predicted, 8, high=False),
    }


def select_anchor_method(metrics: dict[str, dict[str, dict[str, float]]]) -> str:
    return min(
        ANCHOR_METHODS,
        key=lambda method: (
            metrics["validate"][method]["MAE_full_168h"],
            -metrics["validate"][method]["top8_day_precision"],
            -metrics["validate"][method]["top20_168h_precision"],
            method,
        ),
    )


def build_forecast_origin_rows(rows: list[dict[str, object]], selected_anchor: str) -> list[dict[str, object]]:
    created = datetime.now(timezone.utc).replace(microsecond=0)
    output = []
    for row in rows:
        if row["anchor_method"] != selected_anchor:
            continue
        output.append(
            {
                "forecast_run_id": FORECAST_RUN_ID,
                "source_shape_run_id": SOURCE_SHAPE_RUN_ID,
                "model_name": MODEL_NAME,
                "model_version": MODEL_VERSION,
                "split_policy_version": POLICY_VERSION,
                "anchor_method": row["anchor_method"],
                "anchor_level": row["anchor_level"],
                "anchor_scale": row["anchor_scale"],
                "anchor_history_start_utc": row["anchor_history_start_utc"],
                "anchor_history_end_utc": row["anchor_history_end_utc"],
                "forecast_origin_timestamp_utc": row["forecast_origin_timestamp_utc"],
                "input_data_cutoff_utc": row["input_data_cutoff_utc"],
                "target_timestamp_utc": row["target_timestamp_utc"],
                "horizon_hours": row["horizon_hours"],
                "area": AREA,
                "predicted_price": row["predicted_price"],
                "prediction_unit": PREDICTION_UNIT,
                "prediction_kind": PREDICTION_KIND,
                "source_shape_value": row["source_shape_value"],
                "created_at_utc": normalize_z(created),
                "quality_flag": row["quality_flag"],
            }
        )
    return output


def persist_forecast_origin_log(feature_db: Path, rows: list[dict[str, object]]) -> int:
    with sqlite3.connect(feature_db) as conn:
        persist_rows(conn, FORECAST_LOG_TABLE, rows)
        conn.commit()
    return len(rows)


def leakage_review(rows: list[dict[str, object]], anchor_evidence: dict[str, object]) -> dict[str, object]:
    anchor_order_errors = []
    target_order_errors = []
    cutoff_order_errors = []
    horizon_errors = []
    for row in rows:
        origin = parse_policy_timestamp(str(row["forecast_origin_timestamp_utc"]))
        target = parse_policy_timestamp(str(row["target_timestamp_utc"]))
        cutoff = parse_policy_timestamp(str(row["input_data_cutoff_utc"]))
        history_start = parse_policy_timestamp(str(row["anchor_history_start_utc"]))
        history_end = parse_policy_timestamp(str(row["anchor_history_end_utc"]))
        horizon = int(row["horizon_hours"])
        if not (history_start == origin - timedelta(hours=48) and history_end == origin - timedelta(hours=1) and history_end < origin):
            anchor_order_errors.append(row["forecast_origin_timestamp_utc"])
        if origin > target:
            target_order_errors.append(row["target_timestamp_utc"])
        if cutoff > origin:
            cutoff_order_errors.append(row["forecast_origin_timestamp_utc"])
        if horizon < 0 or horizon > 167:
            horizon_errors.append(row["target_timestamp_utc"])
    ok = not anchor_order_errors and not target_order_errors and not cutoff_order_errors and not horizon_errors
    return {
        "ok": ok,
        "anchor_price_timestamps_strictly_before_origin": not anchor_order_errors,
        "forecast_origin_not_after_target": not target_order_errors,
        "input_cutoff_not_after_origin": not cutoff_order_errors,
        "horizons_0_to_167": not horizon_errors,
        "anchor_order_error_count": len(anchor_order_errors),
        "target_order_error_count": len(target_order_errors),
        "cutoff_order_error_count": len(cutoff_order_errors),
        "horizon_error_count": len(horizon_errors),
        "no_target_window_actual_price_used_for_anchor": ok,
        "holdout_used_for_selection": False,
        "a61_used": False,
        "api_or_device_path_touched": False,
        "sample_anchor_windows": anchor_evidence.get("sample_anchor_windows", []),
    }


def baseline_comparison(metrics: dict[str, dict[str, dict[str, float]]], selected_anchor: str) -> dict[str, object]:
    output: dict[str, object] = {"selected_anchor": selected_anchor}
    for split in ("validate", "holdout"):
        selected = metrics[split][selected_anchor]
        output[split] = {
            baseline: {
                "baseline_MAE_full_168h": metrics[split][baseline].get("MAE_full_168h"),
                "selected_minus_baseline_MAE_full_168h": selected.get("MAE_full_168h", 0.0) - metrics[split][baseline].get("MAE_full_168h", 0.0),
                "baseline_top8_day_precision": metrics[split][baseline].get("top8_day_precision"),
                "selected_minus_baseline_top8_day_precision": selected.get("top8_day_precision", 0.0) - metrics[split][baseline].get("top8_day_precision", 0.0),
            }
            for baseline in BASELINE_METHODS
        }
    return output


def status_from_summary(
    forecast_rows: list[dict[str, object]],
    leakage: dict[str, object],
    metrics: dict[str, dict[str, dict[str, float]]],
    selected_anchor: str,
) -> str:
    selected_metrics = metrics.get("validate", {}).get(selected_anchor, {})
    if not forecast_rows or not leakage["ok"] or not selected_metrics.get("path_count"):
        return "STOP"
    return "PASS"


def anchor_method_definitions() -> dict[str, str]:
    return {
        "A0_mean_std": "level=mean(hist48), scale=population_std(hist48), pred=level+shape*scale",
        "A1_median_iqr": "level=median(hist48), scale=(q75-q25)/1.349, pred=level+shape*scale",
        "A2_last24_last48_blend_iqr": "level=0.5*mean(last24)+0.5*mean(hist48), scale=(q75-q25)/1.349, pred=level+shape*scale",
        "A3_same_hour_48h_iqr": "level=mean(previous 48h prices with same fixed-CET hour), scale=(q75-q25)/1.349, pred=level+shape*scale",
    }


def forecast_origin_contract() -> dict[str, object]:
    return {
        "table": FORECAST_LOG_TABLE,
        "forecast_origin_timestamp_utc": "first target timestamp in each 168h rolling path",
        "input_data_cutoff_utc": "forecast_origin_timestamp_utc - 1h",
        "anchor_history_window": "[forecast_origin_timestamp_utc - 48h, forecast_origin_timestamp_utc)",
        "target_window": "[forecast_origin_timestamp_utc, forecast_origin_timestamp_utc + 167h]",
        "prediction_kind": PREDICTION_KIND,
        "prediction_unit": PREDICTION_UNIT,
        "selection_policy": "A0-A3 selected on validation MAE_full_168h only; holdout report-only",
        "required_columns": forecast_log_columns(),
    }


def write_p0053cb_evidence(evidence_dir: Path, summary: dict[str, object], log_rows: list[dict[str, object]]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "CHANGELOG.md": changelog_text(summary),
        "prior-48h-anchor-evidence.md": prior_anchor_text(),
        "anchor-method-definitions.md": json_md("P0053C-B anchor method definitions", summary["anchor_methods"]),
        "forecast-origin-contract.md": json_md("P0053C-B forecast-origin contract", summary["forecast_origin_contract"]),
        "leakage-review.md": json_md("P0053C-B leakage review", summary["leakage_review"]),
        "anchor-validation-results.md": metrics_text(summary, "validate"),
        "anchor-holdout-results.md": metrics_text(summary, "holdout"),
        "baseline-comparison.md": json_md("P0053C-B baseline comparison", summary["baseline_comparison"]),
        "selected-anchor.md": selected_anchor_text(summary),
        "forecast-origin-log-output.md": forecast_log_output_text(summary),
        "g7-readiness-for-consumption-response.md": g7_readiness_text(summary),
        "next-package-recommendation.md": next_package_text(summary),
        "component-attribution-summary.md": component_attribution_text(summary),
    }
    for name, text in files.items():
        write(evidence_dir / name, text)
    write(evidence_dir / "anchor-metrics.json", json.dumps(json_safe(summary["metrics"]), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "g7-feature-readiness.json", json.dumps(json_safe(g7_feature_readiness()), indent=2, sort_keys=True) + "\n")
    write_csv(evidence_dir / "forecast-origin-log-sample.csv", log_rows[:200], forecast_log_columns())
    return {name: str(evidence_dir / name) for name in [*files, "anchor-metrics.json", "g7-feature-readiness.json", "forecast-origin-log-sample.csv"]}


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0053C-B Changelog

- Created 48h anchored absolute SE1 price forecasts from regenerated P0053C-A/P0045 M4 shape paths.
- Evaluated A0-A3 anchor methods on validation and holdout under P0053C global split policy.
- Selected `{summary['selected_anchor']}` using validation `MAE_full_168h`; holdout was report-only.
- Persisted `{summary['forecast_log_rows']}` rows to local table `{FORECAST_LOG_TABLE}`.
- Result status: {summary['status']}.
- No API, devices, Shelly, Home Assistant, KVS, A61 utilization, production activation or future target price anchoring was performed.
"""


def prior_anchor_text() -> str:
    return """# P0053C-B Prior 48h Anchor Evidence

Found prior anchoring evidence, but not an exact durable predecessor for the P0053C-B global split 48h formula set.

- `requirements/package-runs/P0040/level-shape-separation.md` documents level/shape separation where known spot prices set level through additive anchoring.
- `requirements/package-runs/P0046/anchor-scenario-comparison.json` contains anchored absolute scenario comparisons.
- P0053C-B therefore defines A0-A3 explicitly and proves the 48h prior-origin anchor contract under the P0053C global split policy.
"""


def metrics_text(summary: dict[str, object], split: str) -> str:
    lines = [
        f"# P0053C-B {split.title()} Anchor Results",
        "",
        "| method | rows | paths | MAE_full_168h | RMSE_full_168h | bias_full_168h | MAE | RMSE | p90_abs | p95_abs | sMAPE | corr | spearman | top8_day | top20_168h | bottom20_168h |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    metrics = summary["metrics"][split]  # type: ignore[index]
    for method in ANCHOR_METHODS + BASELINE_METHODS:
        row = metrics[method]
        selected = " selected" if method == summary["selected_anchor"] else ""
        lines.append(
            f"| {method}{selected} | {fmt(row.get('row_count'))} | {fmt(row.get('path_count'))} | {fmt(row.get('MAE_full_168h'))} | {fmt(row.get('RMSE_full_168h'))} | {fmt(row.get('bias_full_168h'))} | {fmt(row.get('MAE'))} | {fmt(row.get('RMSE'))} | {fmt(row.get('p90_absolute_error'))} | {fmt(row.get('p95_absolute_error'))} | {fmt(row.get('sMAPE'))} | {fmt(row.get('correlation'))} | {fmt(row.get('spearman'))} | {fmt(row.get('top8_day_precision'))} | {fmt(row.get('top20_168h_precision'))} | {fmt(row.get('bottom20_168h_precision'))} |"
        )
    return "\n".join(lines) + "\n"


def selected_anchor_text(summary: dict[str, object]) -> str:
    selected = summary["selected_anchor"]
    validation = summary["metrics"]["validate"][selected]  # type: ignore[index]
    holdout = summary["metrics"]["holdout"][selected]  # type: ignore[index]
    return f"""# P0053C-B Selected Anchor

Selected anchor: `{selected}`

Selection rule:

```text
min validation MAE_full_168h over A0-A3, tie-break validation top8_day_precision and top20_168h_precision
```

Validation selected metrics:

```json
{json.dumps(json_safe(validation), indent=2, sort_keys=True)}
```

Holdout selected metrics, report-only:

```json
{json.dumps(json_safe(holdout), indent=2, sort_keys=True)}
```
"""


def forecast_log_output_text(summary: dict[str, object]) -> str:
    return f"""# P0053C-B Forecast-Origin Log Output

Local table:

```text
{FORECAST_LOG_TABLE}
```

Rows persisted:

```text
{summary['forecast_log_rows']}
```

The log contains `prediction_kind=anchored_absolute_price`, `area=SE1`, and `prediction_unit={PREDICTION_UNIT}`. It stores the selected validation-only anchor for validation and holdout forecast origins.

Sample:

```text
requirements/package-runs/P0053C-B/forecast-origin-log-sample.csv
```
"""


def g7_readiness_text(summary: dict[str, object]) -> str:
    readiness = g7_feature_readiness()
    return f"""# P0053C-B G7 Readiness For Consumption Response

Status: ready_for_offline_consumption_response_backtest

The anchored log can support forecast-path-only G7 features because every rank, top/bottom flag, relative value, spread and volatility can be computed from predictions available at each forecast origin.

```json
{json.dumps(json_safe(readiness), indent=2, sort_keys=True)}
```
"""


def next_package_text(summary: dict[str, object]) -> str:
    return """# P0053C-B Next Package Recommendation

Recommended next package:

```text
P0053B-A2: retry SE1 consumption price-response using P0053C-B anchored absolute forecast paths for forecast-safe price features.
```

Use only the forecast-origin log path. Do not use target-window actual prices for feature construction.
"""


def component_attribution_text(summary: dict[str, object]) -> str:
    return f"""# P0053C-B Component Attribution Summary

Status: {summary['status']}

Changed component:

```text
src/mac/services/spotprice_model_diagnostics/p0053cb.py
```

Reused components:

```text
P0043/P0044/P0045 deterministic M4 regeneration
P0053C forecast period policy
P0053C-A global split window construction
P0041 local SQLite persistence helpers
```

Created local table:

```text
{FORECAST_LOG_TABLE}
```

No API, device, Shelly, Home Assistant, KVS, A61 utilization, deployable runtime or production activation was touched.
"""


def g7_feature_readiness() -> dict[str, object]:
    return {
        "forecast_se1_price_target_hour": "ready_from_predicted_price",
        "forecast_se1_price_rank_in_forecast_day": "ready_compute_within_origin_day_path",
        "forecast_se1_price_rank_in_168h": "ready_compute_within_origin_168h_path",
        "forecast_se1_price_top4_forecast_day_flag": "ready_compute_within_origin_day_path",
        "forecast_se1_price_top8_forecast_day_flag": "ready_compute_within_origin_day_path",
        "forecast_se1_price_bottom4_forecast_day_flag": "ready_compute_within_origin_day_path",
        "forecast_se1_price_relative_to_forecast_24h_mean": "ready_compute_from_first_24h_path_or_day_path",
        "forecast_se1_price_relative_to_forecast_168h_mean": "ready_compute_from_origin_168h_path",
        "forecast_se1_price_daily_spread_forecast": "ready_compute_by_forecast_day",
        "forecast_se1_price_volatility_next_24h_forecast": "ready_compute_from_first_24h_path",
        "feature_construction_rule": "derive only from rows sharing the same forecast_origin_timestamp_utc",
    }


def group_by_window(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["window_id"])].append(row)
    return grouped


def hit_precision(actual: list[float], predicted: list[float], count: int, *, high: bool) -> float:
    return len(set(top_indexes(actual, count, high=high)) & set(top_indexes(predicted, count, high=high))) / float(count)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def population_std(values: list[float]) -> float:
    if not values:
        return 0.0
    avg = mean(values)
    return math.sqrt(sum((value - avg) ** 2 for value in values) / len(values))


def iqr_scale(values: list[float]) -> float:
    if not values:
        return 0.0
    scale = (percentile(values, 0.75) - percentile(values, 0.25)) / 1.349
    if scale <= 0.0 or not math.isfinite(scale):
        return population_std(values)
    return scale


def smape(actual: list[float], predicted: list[float]) -> float:
    values = []
    for act, pred in zip(actual, predicted):
        denom = (abs(act) + abs(pred)) / 2.0
        if denom > 1e-12:
            values.append(abs(pred - act) / denom)
    return mean(values)


def pearson(actual: list[float], predicted: list[float]) -> float:
    if len(actual) < 2:
        return 0.0
    mean_actual = mean(actual)
    mean_pred = mean(predicted)
    num = sum((a - mean_actual) * (p - mean_pred) for a, p in zip(actual, predicted))
    den_actual = math.sqrt(sum((a - mean_actual) ** 2 for a in actual))
    den_pred = math.sqrt(sum((p - mean_pred) ** 2 for p in predicted))
    den = den_actual * den_pred
    return num / den if den > 0.0 else 0.0


def normalize_z(timestamp: str | datetime) -> str:
    return parse_policy_timestamp(timestamp).isoformat().replace("+00:00", "Z")


def window_id(window: dict[str, object]) -> str:
    return f"{window['target_series']}|{window['split']}|{window['origin_date']}"


def forecast_log_columns() -> tuple[str, ...]:
    return (
        "forecast_run_id",
        "source_shape_run_id",
        "model_name",
        "model_version",
        "split_policy_version",
        "anchor_method",
        "anchor_level",
        "anchor_scale",
        "anchor_history_start_utc",
        "anchor_history_end_utc",
        "forecast_origin_timestamp_utc",
        "input_data_cutoff_utc",
        "target_timestamp_utc",
        "horizon_hours",
        "area",
        "predicted_price",
        "prediction_unit",
        "prediction_kind",
        "source_shape_value",
        "created_at_utc",
        "quality_flag",
    )


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
    return value


def fmt(value: object) -> str:
    if value is None:
        return ""
    return f"{float(value):.6f}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run P0053C-B 48h anchored absolute price forecast log")
    parser.add_argument("--feature-db", default=str(DEFAULT_FEATURE_DB))
    parser.add_argument("--evidence-dir", default=str(EVIDENCE_DIR))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_p0053cb_anchoring(feature_db=args.feature_db, evidence_dir=args.evidence_dir)
    print(json.dumps({"status": result.status, "selected_anchor": result.selected_anchor, "forecast_log_rows": result.forecast_log_rows}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
