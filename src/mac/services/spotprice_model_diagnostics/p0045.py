"""P0045 AI-1 + AI-2 168h shape combination diagnostics."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import json
import math
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_model_diagnostics import p0043, p0044
from src.mac.services.spotprice_model_diagnostics.p0040 import spearman_from_ranks, top_indexes
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, robust_scale, write


PACKAGE_ID = "P0045"
EVIDENCE_DIR = Path("requirements/package-runs/P0045")
TARGET_SERIES = ("system_proxy_se1", "area_diff_proxy_se3")
FORMULAS = ("scaled", "dimensionless")
DEPLOYABLE_PREDICTORS = ("combined_scaled", "combined_dimensionless", "B0_flat_168h", "B1_AI2_only", "B2_AI1_day_only", "B3_time_profile_168h")
ORACLE_PREDICTORS = ("B4_AI2_actual_day_scale_oracle", "B5_AI1_actual_hour_shape_oracle")
FORBIDDEN_PRODUCTION_PATHS = ("NEW_AI_TRAINING", "ABSOLUTE_API", "M5", "M6", "M7", "API", "SHELLY", "DEVICE", "KVS", "HA")
AI2_SELECTED_GROUPS = {"system_proxy_se1": "F4_full", "area_diff_proxy_se3": "F2_time_calendar_weather_actual"}
AI1_SELECTED_GROUPS = {
    "system_proxy_se1": {
        "day_level_shape": "F5_area_diff_wind_gradient_optional",
        "log_day_scale_index": "F5_area_diff_wind_gradient_optional",
        "log_local_7d_scale": "F5_area_diff_wind_gradient_optional",
    },
    "area_diff_proxy_se3": {
        "day_level_shape": "F5_area_diff_wind_gradient_optional",
        "log_day_scale_index": "fallback_zero",
        "log_local_7d_scale": "fallback_train_mean",
    },
}


@dataclass(frozen=True)
class P0045Result:
    status: str
    selected_formulas: dict[str, str]
    window_counts: dict[str, object]
    evidence: dict[str, str]


def run_p0045_combination(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0045Result:
    start = time.monotonic()
    ai1_rows, ai2_rows = load_corrected_inputs(feature_db)
    contract = validate_input_contract(ai1_rows, ai2_rows)
    if not contract["ok"]:
        raise RuntimeError(f"P0045 input contract failed: {contract}")
    p0044.assign_splits(ai1_rows)
    p0043.assign_splits(ai2_rows)
    ai1_predictions = regenerate_ai1_predictions(ai1_rows)
    ai2_predictions = regenerate_ai2_predictions(ai2_rows)
    windows = build_forecast_windows(ai1_rows, ai2_rows)
    time_profiles = fit_time_profile_baselines(ai2_rows)
    window_results = evaluate_all_windows(windows, ai1_predictions, ai2_predictions, time_profiles)
    metrics = summarize_metrics(window_results)
    selected = select_formulas(metrics)
    summary = {
        "dataset_tables": ["ai1_day_to_local_week_training_targets_v2", "ai2_hour_to_day_training_targets_v2"],
        "contract": contract,
        "target_usage_policy": target_usage_policy(),
        "window_counts": window_counts(windows),
        "metrics": metrics,
        "selected_formulas": selected,
        "window_results": window_results,
        "runtime_seconds": time.monotonic() - start,
    }
    evidence = write_p0045_evidence(Path(evidence_dir), summary)
    return P0045Result(status=p0045_status(summary), selected_formulas=selected, window_counts=summary["window_counts"], evidence=evidence)


def load_corrected_inputs(feature_db: Path | str = DEFAULT_FEATURE_DB) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    db = Path(feature_db).expanduser()
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        for table in ("ai1_day_to_local_week_training_targets_v2", "ai2_hour_to_day_training_targets_v2"):
            if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone():
                raise RuntimeError(f"P0042 corrected table {table} is missing")
        ai1 = [dict(row) for row in conn.execute("SELECT * FROM ai1_day_to_local_week_training_targets_v2 ORDER BY target_series, model_cet_date")]
        ai2 = [dict(row) for row in conn.execute("SELECT * FROM ai2_hour_to_day_training_targets_v2 ORDER BY target_series, timestamp_utc")]
    return ai1, ai2


def validate_input_contract(ai1_rows: list[dict[str, object]], ai2_rows: list[dict[str, object]]) -> dict[str, object]:
    ai1_required = {"model_cet_date", "target_series", "day_level_shape", "log_day_scale_index", "log_local_7d_scale"}
    ai2_required = {"timestamp_utc", "model_cet_date", "model_cet_hour", "target_series", "hour_price", "hour_shape"}
    ai1_missing = sorted(ai1_required - set(ai1_rows[0])) if ai1_rows else sorted(ai1_required)
    ai2_missing = sorted(ai2_required - set(ai2_rows[0])) if ai2_rows else sorted(ai2_required)
    ai1_counts = {series: len([row for row in ai1_rows if row.get("target_series") == series]) for series in TARGET_SERIES}
    ai2_counts = {series: len([row for row in ai2_rows if row.get("target_series") == series]) for series in TARGET_SERIES}
    finite_ai1 = all(math.isfinite(float(row[target])) for row in ai1_rows for target in p0044.TARGET_NAMES)
    finite_ai2 = all(math.isfinite(float(row["hour_shape"])) and math.isfinite(float(row["hour_price"])) for row in ai2_rows)
    return {
        "ok": bool(ai1_rows) and bool(ai2_rows) and not ai1_missing and not ai2_missing and all(ai1_counts.values()) and all(ai2_counts.values()) and finite_ai1 and finite_ai2,
        "ai1_missing_fields": ai1_missing,
        "ai2_missing_fields": ai2_missing,
        "ai1_counts": ai1_counts,
        "ai2_counts": ai2_counts,
        "finite_ai1_targets": finite_ai1,
        "finite_ai2_targets": finite_ai2,
        "uses_p0042_v2_tables": True,
    }


def regenerate_ai2_predictions(ai2_rows: list[dict[str, object]]) -> dict[str, dict[str, float]]:
    predictions: dict[str, dict[str, float]] = {}
    for series, group in AI2_SELECTED_GROUPS.items():
        rows = [row for row in ai2_rows if row["target_series"] == series]
        train = [row for row in rows if row["split"] == "train"]
        model, encoder = p0043.train_hgb_model(train, group)
        raw = p0043.predict_model(model, encoder, rows, group)
        centered = p0043.center_predictions_by_day(rows, raw)
        predictions[series] = {hour_key(row): pred for row, pred in zip(rows, centered)}
    return predictions


def regenerate_ai1_predictions(ai1_rows: list[dict[str, object]]) -> dict[str, dict[str, dict[str, float]]]:
    predictions: dict[str, dict[str, dict[str, float]]] = {series: {} for series in TARGET_SERIES}
    for series in TARGET_SERIES:
        rows = [row for row in ai1_rows if row["target_series"] == series]
        train = [row for row in rows if row["split"] == "train"]
        predictions[series] = {str(row["model_cet_date"]): {} for row in rows}
        for target, group in AI1_SELECTED_GROUPS[series].items():
            if group == "fallback_zero":
                values = [0.0 for _row in rows]
            elif group == "fallback_train_mean":
                train_mean = sum(float(row[target]) for row in train) / len(train)
                values = [train_mean for _row in rows]
            else:
                model, encoder = p0044.train_hgb_model(train, group, target)
                values = p0044.predict_model(model, encoder, rows, group)
            for row, value in zip(rows, values):
                predictions[series][str(row["model_cet_date"])][target] = float(value)
    return predictions


def build_forecast_windows(ai1_rows: list[dict[str, object]], ai2_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    ai1_dates = {series: {date.fromisoformat(str(row["model_cet_date"])) for row in ai1_rows if row["target_series"] == series} for series in TARGET_SERIES}
    by_series_day: dict[str, dict[date, list[dict[str, object]]]] = {series: defaultdict(list) for series in TARGET_SERIES}  # type: ignore[assignment]
    for row in ai2_rows:
        by_series_day[str(row["target_series"])][date.fromisoformat(str(row["model_cet_date"]))].append(row)
    windows = []
    for series in TARGET_SERIES:
        start_candidates = sorted(set(by_series_day[series]) & ai1_dates[series])
        for origin in start_candidates:
            days = [origin + timedelta(days=offset) for offset in range(7)]
            hourly = []
            if any(day not in ai1_dates[series] for day in days):
                continue
            for day in days:
                day_rows = sorted(by_series_day[series].get(day, []), key=lambda row: int(row["model_cet_hour"]))
                if len(day_rows) != 24:
                    hourly = []
                    break
                hourly.extend(day_rows)
            if len(hourly) != 168:
                continue
            split = split_for_date(origin)
            if split == "train":
                continue
            windows.append({"target_series": series, "origin_date": origin.isoformat(), "split": split, "hourly_rows": hourly})
    return windows


def split_for_date(day: date) -> str:
    if day <= date(2024, 12, 31):
        return "train"
    if day <= date(2025, 12, 31):
        return "validate"
    return "holdout"


def fit_time_profile_baselines(ai2_rows: list[dict[str, object]]) -> dict[str, dict[tuple[int, int], float]]:
    profiles: dict[str, dict[tuple[int, int], list[float]]] = {series: defaultdict(list) for series in TARGET_SERIES}  # type: ignore[assignment]
    for row in ai2_rows:
        if row["split"] != "train":
            continue
        profiles[str(row["target_series"])][(int(row["model_cet_weekday"]), int(row["model_cet_hour"]))].append(float(row["hour_price"]))
    return {
        series: {key: sum(values) / len(values) for key, values in grouped.items()}
        for series, grouped in profiles.items()
    }


def evaluate_all_windows(
    windows: list[dict[str, object]],
    ai1_predictions: dict[str, dict[str, dict[str, float]]],
    ai2_predictions: dict[str, dict[str, float]],
    time_profiles: dict[str, dict[tuple[int, int], float]],
) -> list[dict[str, object]]:
    results = []
    for window in windows:
        series = str(window["target_series"])
        actual = actual_shape(window)
        predictors = {
            "combined_scaled": combine_window(window, ai1_predictions, ai2_predictions, "scaled"),
            "combined_dimensionless": combine_window(window, ai1_predictions, ai2_predictions, "dimensionless"),
            "B0_flat_168h": [0.0] * 168,
            "B1_AI2_only": center([ai2_predictions[series][hour_key(row)] for row in window["hourly_rows"]]),  # type: ignore[index]
            "B2_AI1_day_only": ai1_day_only(window, ai1_predictions),
            "B3_time_profile_168h": time_profile_prediction(window, time_profiles),
            "B4_AI2_actual_day_scale_oracle": oracle_ai2_actual_day_scale(window, ai2_predictions),
            "B5_AI1_actual_hour_shape_oracle": oracle_ai1_actual_hour_shape(window, ai1_predictions),
        }
        for predictor, pred in predictors.items():
            metrics = evaluate_window(window, actual, pred)
            results.append(
                {
                    "target_series": series,
                    "origin_date": window["origin_date"],
                    "split": window["split"],
                    "predictor": predictor,
                    "is_oracle": predictor in ORACLE_PREDICTORS,
                    **metrics,
                    **window_context(window),
                }
            )
    return results


def combine_window(
    window: dict[str, object],
    ai1_predictions: dict[str, dict[str, dict[str, float]]],
    ai2_predictions: dict[str, dict[str, float]],
    formula: str,
) -> list[float]:
    series = str(window["target_series"])
    values = []
    for row in window["hourly_rows"]:  # type: ignore[index]
        day = str(row["model_cet_date"])
        daily = ai1_predictions[series][day]
        day_level = daily["day_level_shape"]
        day_scale_index = math.exp(daily["log_day_scale_index"])
        local_scale = math.exp(daily["log_local_7d_scale"])
        if not math.isfinite(day_scale_index) or not math.isfinite(local_scale) or day_scale_index <= 0.0 or local_scale <= 0.0:
            raise RuntimeError("P0045 produced non-finite or non-positive scale prediction")
        hour_shape = ai2_predictions[series][hour_key(row)]
        if formula == "scaled":
            values.append(day_level * local_scale + hour_shape * local_scale * day_scale_index)
        else:
            values.append(day_level + hour_shape * day_scale_index)
    return center(values)


def ai1_day_only(window: dict[str, object], ai1_predictions: dict[str, dict[str, dict[str, float]]]) -> list[float]:
    series = str(window["target_series"])
    values = []
    for row in window["hourly_rows"]:  # type: ignore[index]
        daily = ai1_predictions[series][str(row["model_cet_date"])]
        values.append(daily["day_level_shape"] * math.exp(daily["log_local_7d_scale"]))
    return center(values)


def time_profile_prediction(window: dict[str, object], time_profiles: dict[str, dict[tuple[int, int], float]]) -> list[float]:
    series = str(window["target_series"])
    values = []
    profile = time_profiles[series]
    fallback = sum(profile.values()) / len(profile)
    for row in window["hourly_rows"]:  # type: ignore[index]
        values.append(float(profile.get((int(row["model_cet_weekday"]), int(row["model_cet_hour"])), fallback)))
    return center(values)


def oracle_ai2_actual_day_scale(window: dict[str, object], ai2_predictions: dict[str, dict[str, float]]) -> list[float]:
    series = str(window["target_series"])
    values = [ai2_predictions[series][hour_key(row)] * float(row["day_intraday_scale"]) for row in window["hourly_rows"]]  # type: ignore[index]
    return center(values)


def oracle_ai1_actual_hour_shape(window: dict[str, object], ai1_predictions: dict[str, dict[str, dict[str, float]]]) -> list[float]:
    series = str(window["target_series"])
    values = []
    for row in window["hourly_rows"]:  # type: ignore[index]
        daily = ai1_predictions[series][str(row["model_cet_date"])]
        values.append(daily["day_level_shape"] * math.exp(daily["log_local_7d_scale"]) + float(row["hour_shape"]) * math.exp(daily["log_local_7d_scale"]) * math.exp(daily["log_day_scale_index"]))
    return center(values)


def actual_shape(window: dict[str, object]) -> dict[str, list[float] | float]:
    prices = [float(row["hour_price"]) for row in window["hourly_rows"]]  # type: ignore[index]
    centered = center(prices)
    scale = robust_scale(prices)
    return {"centered": centered, "scaled": [value / scale for value in centered], "scale": scale}


def evaluate_window(window: dict[str, object], actual: dict[str, list[float] | float], predicted: list[float]) -> dict[str, float]:
    actual_centered = actual["centered"]  # type: ignore[assignment]
    scale = float(actual["scale"])
    predicted_scaled = [value / scale for value in predicted]
    daily = daily_allocation_metrics(window, actual_centered, predicted)  # type: ignore[arg-type]
    intraday = intraday_metrics(window, actual_centered, predicted)  # type: ignore[arg-type]
    return {
        "shape_MAE_centered": mae(actual_centered, predicted),  # type: ignore[arg-type]
        "shape_RMSE_centered": rmse(actual_centered, predicted),  # type: ignore[arg-type]
        "shape_MAE_scaled": mae(actual["scaled"], predicted_scaled),  # type: ignore[arg-type]
        "shape_RMSE_scaled": rmse(actual["scaled"], predicted_scaled),  # type: ignore[arg-type]
        "signed_bias_after_centering": sum(predicted) / len(predicted),
        "spearman_168h": spearman_from_ranks(ranks(actual_centered), ranks(predicted)),  # type: ignore[arg-type]
        "top_10_percent_hit_rate": hit_precision(actual_centered, predicted, 17, high=True),  # type: ignore[arg-type]
        "bottom_10_percent_hit_rate": hit_precision(actual_centered, predicted, 17, high=False),  # type: ignore[arg-type]
        "top_20h_precision": hit_precision(actual_centered, predicted, 20, high=True),  # type: ignore[arg-type]
        "bottom_20h_precision": hit_precision(actual_centered, predicted, 20, high=False),  # type: ignore[arg-type]
        "best_8h_hit_rate": hit_precision(actual_centered, predicted, 8, high=True),  # type: ignore[arg-type]
        "worst_8h_hit_rate": hit_precision(actual_centered, predicted, 8, high=False),  # type: ignore[arg-type]
        **daily,
        **intraday,
    }


def daily_allocation_metrics(window: dict[str, object], actual: list[float], predicted: list[float]) -> dict[str, float]:
    actual_daily = []
    predicted_daily = []
    for day_index in range(7):
        lo = day_index * 24
        hi = lo + 24
        actual_daily.append(sum(actual[lo:hi]) / 24.0)
        predicted_daily.append(sum(predicted[lo:hi]) / 24.0)
    return {
        "day_mean_shape_MAE": mae(actual_daily, predicted_daily),
        "day_rank_spearman": spearman_from_ranks(ranks(actual_daily), ranks(predicted_daily)),
        "highest_day_hit_rate": 1.0 if top_indexes(actual_daily, 1, high=True)[0] == top_indexes(predicted_daily, 1, high=True)[0] else 0.0,
        "lowest_day_hit_rate": 1.0 if top_indexes(actual_daily, 1, high=False)[0] == top_indexes(predicted_daily, 1, high=False)[0] else 0.0,
    }


def intraday_metrics(window: dict[str, object], actual: list[float], predicted: list[float]) -> dict[str, float]:
    spearman = []
    top3 = []
    bottom3 = []
    for day_index in range(7):
        lo = day_index * 24
        hi = lo + 24
        day_actual = actual[lo:hi]
        day_pred = predicted[lo:hi]
        spearman.append(spearman_from_ranks(ranks(day_actual), ranks(day_pred)))
        top3.append(hit_precision(day_actual, day_pred, 3, high=True))
        bottom3.append(hit_precision(day_actual, day_pred, 3, high=False))
    return {
        "hour_within_day_spearman_mean": sum(spearman) / len(spearman),
        "top_3h_daily_hit_rate": sum(top3) / len(top3),
        "bottom_3h_daily_hit_rate": sum(bottom3) / len(bottom3),
    }


def window_context(window: dict[str, object]) -> dict[str, object]:
    rows = window["hourly_rows"]  # type: ignore[assignment]
    return {
        "has_special_day": any(int(row.get("is_special_day") or 0) for row in rows),
        "has_bridge_day": any(int(row.get("is_bridge_day") or 0) for row in rows),
        "has_holiday_period": any(int(row.get("is_holiday_period") or 0) for row in rows),
        "month": int(str(window["origin_date"])[5:7]),
        "mean_temp_delta": sum(float(row.get("hourly_temperature_delta") or 0.0) for row in rows) / len(rows),
        "mean_solar": sum(float(row.get("hourly_solar_actual") or 0.0) for row in rows) / len(rows),
        "mean_wind": sum(float(row.get("hourly_wind_actual") or 0.0) for row in rows) / len(rows),
    }


def summarize_metrics(window_results: list[dict[str, object]]) -> dict[str, dict[str, dict[str, dict[str, float]]]]:
    output: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
    for series in TARGET_SERIES:
        output[series] = {}
        for split in ("validate", "holdout"):
            output[series][split] = {}
            for predictor in DEPLOYABLE_PREDICTORS + ORACLE_PREDICTORS:
                rows = [row for row in window_results if row["target_series"] == series and row["split"] == split and row["predictor"] == predictor]
                output[series][split][predictor] = aggregate_metric_rows(rows)
    return output


def aggregate_metric_rows(rows: list[dict[str, object]]) -> dict[str, float]:
    metrics = [
        "shape_MAE_centered",
        "shape_RMSE_centered",
        "shape_MAE_scaled",
        "shape_RMSE_scaled",
        "signed_bias_after_centering",
        "spearman_168h",
        "top_10_percent_hit_rate",
        "bottom_10_percent_hit_rate",
        "top_20h_precision",
        "bottom_20h_precision",
        "best_8h_hit_rate",
        "worst_8h_hit_rate",
        "day_mean_shape_MAE",
        "day_rank_spearman",
        "highest_day_hit_rate",
        "lowest_day_hit_rate",
        "hour_within_day_spearman_mean",
        "top_3h_daily_hit_rate",
        "bottom_3h_daily_hit_rate",
    ]
    if not rows:
        return {"window_count": 0.0}
    return {"window_count": float(len(rows)), **{metric: sum(float(row[metric]) for row in rows) / len(rows) for metric in metrics}}


def select_formulas(metrics: dict[str, dict[str, dict[str, dict[str, float]]]]) -> dict[str, str]:
    selected = {}
    for series in TARGET_SERIES:
        candidates = ("combined_scaled", "combined_dimensionless")
        selected[series] = min(candidates, key=lambda name: metrics[series]["validate"][name]["shape_MAE_scaled"])
    return selected


def p0045_status(summary: dict[str, object]) -> str:
    metrics = summary["metrics"]  # type: ignore[assignment]
    selected = summary["selected_formulas"]  # type: ignore[assignment]
    se1 = metrics["system_proxy_se1"]["holdout"]  # type: ignore[index]
    se1_selected = se1[selected["system_proxy_se1"]]  # type: ignore[index]
    b0 = se1["B0_flat_168h"]
    if se1_selected["shape_MAE_scaled"] >= b0["shape_MAE_scaled"] or se1_selected["spearman_168h"] <= b0["spearman_168h"]:
        return "STOP"
    if se1_selected["shape_MAE_scaled"] < se1["B1_AI2_only"]["shape_MAE_scaled"] or se1_selected["shape_MAE_scaled"] < se1["B2_AI1_day_only"]["shape_MAE_scaled"]:
        return "PASS"
    return "WARN"


def window_counts(windows: list[dict[str, object]]) -> dict[str, object]:
    counts: dict[str, dict[str, int]] = {series: defaultdict(int) for series in TARGET_SERIES}  # type: ignore[assignment]
    for window in windows:
        counts[str(window["target_series"])][str(window["split"])] += 1
    return {series: dict(sorted(values.items())) for series, values in counts.items()}


def target_usage_policy() -> dict[str, object]:
    return {
        "system_proxy_se1": {
            "day_level_shape": "AI-1 P0044 F5",
            "log_day_scale_index": "AI-1 P0044 F5",
            "log_local_7d_scale": "AI-1 P0044 F5",
        },
        "area_diff_proxy_se3": {
            "day_level_shape": "AI-1 P0044 F5 weak-confidence",
            "log_day_scale_index": "fallback 0.0",
            "log_local_7d_scale": "fallback train mean from train rows",
        },
    }


def subset_summary(window_results: list[dict[str, object]], selected: dict[str, str]) -> dict[str, dict[str, dict[str, float]]]:
    output: dict[str, dict[str, dict[str, float]]] = {}
    for series in TARGET_SERIES:
        predictor = selected[series]
        rows = [row for row in window_results if row["target_series"] == series and row["split"] == "holdout" and row["predictor"] == predictor]
        subsets = {
            "normal_week": lambda r: not r["has_special_day"] and not r["has_bridge_day"] and not r["has_holiday_period"],
            "holiday_week": lambda r: r["has_special_day"] or r["has_holiday_period"],
            "bridge_day_week": lambda r: r["has_bridge_day"],
            "summer": lambda r: int(r["month"]) in {6, 7, 8},
            "winter": lambda r: int(r["month"]) in {12, 1, 2},
            "high_solar_week": lambda r: float(r["mean_solar"]) >= percentile([float(row["mean_solar"]) for row in rows], 0.75),
            "low_wind_week": lambda r: float(r["mean_wind"]) <= percentile([float(row["mean_wind"]) for row in rows], 0.25),
            "high_wind_week": lambda r: float(r["mean_wind"]) >= percentile([float(row["mean_wind"]) for row in rows], 0.75),
            "high_temp_delta_week": lambda r: float(r["mean_temp_delta"]) >= percentile([float(row["mean_temp_delta"]) for row in rows], 0.75),
        }
        output[series] = {name: aggregate_metric_rows([row for row in rows if predicate(row)]) for name, predicate in subsets.items()}
    return output


def best_worst_windows(window_results: list[dict[str, object]], selected: dict[str, str]) -> dict[str, object]:
    output = {}
    for series in TARGET_SERIES:
        predictor = selected[series]
        rows = [row for row in window_results if row["target_series"] == series and row["split"] == "holdout" and row["predictor"] == predictor]
        ordered = sorted(rows, key=lambda row: float(row["shape_MAE_scaled"]))
        output[series] = {
            "best_20": slim_window_rows(ordered[:20]),
            "worst_20": slim_window_rows(list(reversed(ordered[-20:]))),
        }
    return output


def slim_window_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    keys = ("origin_date", "predictor", "shape_MAE_scaled", "shape_MAE_centered", "spearman_168h", "day_rank_spearman", "hour_within_day_spearman_mean", "has_special_day", "month")
    return [{key: row[key] for key in keys} for row in rows]


def center(values: list[float]) -> list[float]:
    avg = sum(values) / len(values) if values else 0.0
    return [value - avg for value in values]


def ranks(values: list[float]) -> list[float]:
    ordered = sorted((value, index) for index, value in enumerate(values))
    output = [0.0] * len(values)
    for rank, (_value, index) in enumerate(ordered, start=1):
        output[index] = float(rank)
    return output


def hit_precision(actual: list[float], predicted: list[float], count: int, *, high: bool) -> float:
    return len(set(top_indexes(actual, count, high=high)) & set(top_indexes(predicted, count, high=high))) / float(count)


def hour_key(row: dict[str, object]) -> str:
    return f"{row['target_series']}|{row['timestamp_utc']}"


def write_p0045_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    subset = subset_summary(summary["window_results"], summary["selected_formulas"])  # type: ignore[arg-type]
    best_worst = best_worst_windows(summary["window_results"], summary["selected_formulas"])  # type: ignore[arg-type]
    paths = {
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog(summary)),
        "dataset": write(evidence_dir / "dataset-contract.md", dataset_report(summary)),
        "inputs": write(evidence_dir / "model-input-contract.md", model_input_report()),
        "policy": write(evidence_dir / "target-usage-policy.md", target_policy_report(summary)),
        "formulas": write(evidence_dir / "combination-formulas.md", formulas_report(summary)),
        "windows": write(evidence_dir / "forecast-window-policy.md", windows_report(summary)),
        "baselines": write(evidence_dir / "baselines.md", baselines_report(summary)),
        "shape": write(evidence_dir / "shape-metrics-summary.md", shape_report(summary)),
        "rank": write(evidence_dir / "rank-and-top-bottom-results.md", rank_report(summary)),
        "daily": write(evidence_dir / "daily-allocation-results.md", daily_report(summary)),
        "intraday": write(evidence_dir / "intraday-results.md", intraday_report(summary)),
        "subsets": write(evidence_dir / "subset-results.md", subset_report(subset)),
        "best_worst": write(evidence_dir / "best-worst-windows.md", best_worst_report(best_worst)),
        "oracle": write(evidence_dir / "oracle-diagnostics.md", oracle_report(summary)),
        "next": write(evidence_dir / "next-anchoring-plan.md", next_report(summary)),
        "summary": write(evidence_dir / "component-attribution-summary.md", component_summary(summary)),
    }
    write(evidence_dir / "metrics-summary.json", json.dumps(json_safe({k: v for k, v in summary.items() if k != "window_results"}), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "best-worst-windows.json", json.dumps(json_safe(best_worst), indent=2, sort_keys=True) + "\n")
    return paths


def changelog(summary: dict[str, object]) -> str:
    return f"# P0045 changelog\n\n- Combined regenerated P0043 AI-2 and P0044 AI-1 predictions into fixed-CET rolling 168h shape diagnostics.\n- Applied P0044 fallback policy for weak area_diff scale targets.\n- Evaluated scaled and dimensionless combination formulas against B0-B5 baselines.\n- Result status: {p0045_status(summary)}.\n- Wrote summary metrics and best/worst JSON; full per-window raw JSON is intentionally not committed because it is large and reproducible.\n- No new AI model search, production API, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.\n"


def dataset_report(summary: dict[str, object]) -> str:
    return f"# P0045 dataset contract\n\nused_tables = {summary['dataset_tables']}\n\ncontract = {summary['contract']}\n\nP0045 fails rather than falling back to P0041/pre-P0042 datasets.\n"


def model_input_report() -> str:
    return "# P0045 model input contract\n\nP0043/P0044 binary models were not committed. P0045 regenerates evaluation predictions deterministically from corrected P0042 train rows and the stored selected feature groups.\n\nAI-2 source: P0043 selected groups `system_proxy_se1=F4_full`, `area_diff_proxy_se3=F2_time_calendar_weather_actual`; target is `hour_shape`.\n\nAI-1 source: P0044 selected groups/fallbacks; targets are `day_level_shape`, `log_day_scale_index`, `log_local_7d_scale`.\n\nThis is artifact regeneration for historical evaluation, not new AI model development or hyperparameter selection.\n"


def target_policy_report(summary: dict[str, object]) -> str:
    return "# P0045 target usage policy\n\n" + json.dumps(summary["target_usage_policy"], indent=2, sort_keys=True) + "\n"


def formulas_report(summary: dict[str, object]) -> str:
    return f"# P0045 combination formulas\n\nSelected formulas by validation scaled MAE: {summary['selected_formulas']}\n\nScaled formula: `day_level_shape * exp(log_local_7d_scale) + hour_shape * exp(log_local_7d_scale) * exp(log_day_scale_index)`, centered over 168h.\n\nDimensionless formula: `day_level_shape + hour_shape * exp(log_day_scale_index)`, centered over 168h.\n"


def windows_report(summary: dict[str, object]) -> str:
    return f"# P0045 forecast window policy\n\nPrimary origins are fixed-CET model days at hour 00. Each window covers D 00:00 through D+6 23:00 and is accepted only with exactly 168 hourly rows for the target series.\n\nwindow_counts = {summary['window_counts']}\n\nRolling windows overlap heavily; metrics are model-selection diagnostics rather than iid confidence estimates.\n"


def baselines_report(summary: dict[str, object]) -> str:
    return metrics_table(summary, "P0045 baselines", DEPLOYABLE_PREDICTORS + ORACLE_PREDICTORS)


def shape_report(summary: dict[str, object]) -> str:
    return metrics_table(summary, "P0045 shape metrics summary", DEPLOYABLE_PREDICTORS)


def rank_report(summary: dict[str, object]) -> str:
    return metric_columns_table(summary, "P0045 rank and top/bottom results", ("spearman_168h", "top_10_percent_hit_rate", "bottom_10_percent_hit_rate", "top_20h_precision", "bottom_20h_precision", "best_8h_hit_rate", "worst_8h_hit_rate"))


def daily_report(summary: dict[str, object]) -> str:
    return metric_columns_table(summary, "P0045 daily allocation results", ("day_mean_shape_MAE", "day_rank_spearman", "highest_day_hit_rate", "lowest_day_hit_rate"))


def intraday_report(summary: dict[str, object]) -> str:
    return metric_columns_table(summary, "P0045 intraday results", ("hour_within_day_spearman_mean", "top_3h_daily_hit_rate", "bottom_3h_daily_hit_rate"))


def metrics_table(summary: dict[str, object], title: str, predictors: tuple[str, ...]) -> str:
    lines = [f"# {title}", "", "| series | split | predictor | windows | scaled_MAE | centered_MAE | spearman | day_spearman | intraday_spearman | oracle |", "|---|---|---|---:|---:|---:|---:|---:|---:|---|"]
    metrics = summary["metrics"]  # type: ignore[assignment]
    for series in TARGET_SERIES:
        for split in ("validate", "holdout"):
            for predictor in predictors:
                row = metrics[series][split][predictor]  # type: ignore[index]
                lines.append(f"| {series} | {split} | {predictor} | {fmt(row.get('window_count', 0.0))} | {fmt(row.get('shape_MAE_scaled', 0.0))} | {fmt(row.get('shape_MAE_centered', 0.0))} | {fmt(row.get('spearman_168h', 0.0))} | {fmt(row.get('day_rank_spearman', 0.0))} | {fmt(row.get('hour_within_day_spearman_mean', 0.0))} | {predictor in ORACLE_PREDICTORS} |")
    return "\n".join(lines) + "\n"


def metric_columns_table(summary: dict[str, object], title: str, columns: tuple[str, ...]) -> str:
    lines = [f"# {title}", "", "| series | split | predictor | " + " | ".join(columns) + " |", "|---|---|---|" + "|".join("---:" for _ in columns) + "|"]
    metrics = summary["metrics"]  # type: ignore[assignment]
    for series in TARGET_SERIES:
        for split in ("validate", "holdout"):
            for predictor in DEPLOYABLE_PREDICTORS:
                row = metrics[series][split][predictor]  # type: ignore[index]
                lines.append(f"| {series} | {split} | {predictor} | " + " | ".join(fmt(row.get(col, 0.0)) for col in columns) + " |")
    return "\n".join(lines) + "\n"


def subset_report(subset: dict[str, dict[str, dict[str, float]]]) -> str:
    lines = ["# P0045 subset results", "", "| series | subset | windows | scaled_MAE | spearman | day_spearman | intraday_spearman |", "|---|---|---:|---:|---:|---:|---:|"]
    for series, rows in subset.items():
        for name, row in rows.items():
            lines.append(f"| {series} | {name} | {fmt(row.get('window_count', 0.0))} | {fmt(row.get('shape_MAE_scaled', 0.0))} | {fmt(row.get('spearman_168h', 0.0))} | {fmt(row.get('day_rank_spearman', 0.0))} | {fmt(row.get('hour_within_day_spearman_mean', 0.0))} |")
    return "\n".join(lines) + "\n"


def best_worst_report(best_worst: dict[str, object]) -> str:
    lines = ["# P0045 best/worst holdout windows", ""]
    for series in TARGET_SERIES:
        lines += [f"## {series}", "", "| bucket | origin | predictor | scaled_MAE | centered_MAE | spearman | day_spearman | intraday_spearman | special | month |", "|---|---|---|---:|---:|---:|---:|---:|---|---:|"]
        for bucket_name in ("best_20", "worst_20"):
            for row in best_worst[series][bucket_name]:  # type: ignore[index]
                lines.append(f"| {bucket_name} | {row['origin_date']} | {row['predictor']} | {fmt(row['shape_MAE_scaled'])} | {fmt(row['shape_MAE_centered'])} | {fmt(row['spearman_168h'])} | {fmt(row['day_rank_spearman'])} | {fmt(row['hour_within_day_spearman_mean'])} | {row['has_special_day']} | {row['month']} |")
        lines.append("")
    return "\n".join(lines)


def oracle_report(summary: dict[str, object]) -> str:
    return metrics_table(summary, "P0045 oracle diagnostics", ORACLE_PREDICTORS) + "\nOracle diagnostics use actual historical target structure and are excluded from deployable model selection.\n"


def next_report(summary: dict[str, object]) -> str:
    status = p0045_status(summary)
    selected = summary["selected_formulas"]
    return f"# P0045 next anchoring plan\n\nStatus: {status}\n\nSelected deployable formulas: {selected}\n\nP0046 may proceed only as an anchored absolute-price backtest, not production API, if it accepts the P0045 shape/rank tradeoffs. SE1 should be the first anchoring target. area_diff should remain diagnostic or fallback-constrained unless reviewed.\n"


def component_summary(summary: dict[str, object]) -> str:
    status = p0045_status(summary)
    lines = ["# P0045 component attribution summary", "", f"Status: {status}", f"1. Corrected datasets used: {summary['dataset_tables']}.", "2. AI-2 predictions regenerated from P0043 selected groups; AI-1 predictions regenerated/applied from P0044 target policy.", f"3. Selected formulas: {summary['selected_formulas']}.", f"4. Window counts: {summary['window_counts']}."]
    metrics = summary["metrics"]  # type: ignore[assignment]
    for series in TARGET_SERIES:
        selected = summary["selected_formulas"][series]  # type: ignore[index]
        row = metrics[series]["holdout"][selected]  # type: ignore[index]
        b0 = metrics[series]["holdout"]["B0_flat_168h"]  # type: ignore[index]
        ai2 = metrics[series]["holdout"]["B1_AI2_only"]  # type: ignore[index]
        ai1 = metrics[series]["holdout"]["B2_AI1_day_only"]  # type: ignore[index]
        lines.append(f"{series}: selected={selected}, scaled_MAE={fmt(row['shape_MAE_scaled'])}, B0={fmt(b0['shape_MAE_scaled'])}, AI2_only={fmt(ai2['shape_MAE_scaled'])}, AI1_only={fmt(ai1['shape_MAE_scaled'])}, spearman={fmt(row['spearman_168h'])}.")
    lines += [
        "Oracle diagnostics are labeled and excluded from deployable selection.",
        "No new AI hyperparameter search/training, anchored absolute API, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.",
        "",
    ]
    return "\n".join(lines)


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def fmt(value: object) -> str:
    return f"{float(value):.6f}"


def main() -> int:
    result = run_p0045_combination()
    print(json.dumps({"status": result.status, "selected_formulas": result.selected_formulas, "window_counts": result.window_counts, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
