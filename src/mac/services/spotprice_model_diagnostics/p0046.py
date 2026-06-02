"""P0046 SE1 anchored absolute-price backtest diagnostics."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import json
import math
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_model_diagnostics import p0043, p0044, p0045
from src.mac.services.spotprice_model_diagnostics.p0040 import spearman_from_ranks, top_indexes
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, robust_scale, write


PACKAGE_ID = "P0046"
EVIDENCE_DIR = Path("requirements/package-runs/P0046")
PRIMARY_TARGET = "system_proxy_se1"
TARGET_SERIES = ("system_proxy_se1", "area_diff_proxy_se3")
ANCHOR_SCENARIOS = (11, 16, 24, 35)
ANCHOR_METHODS = ("L1_level", "L2_level_scale", "L3_shrink_scale")
SHAPE_PREDICTORS = ("P0045_combined_scaled", "B2_anchor_time_profile", "B3_P0045_AI1_only_anchor", "B4_P0045_AI2_only_anchor")
ORACLE_PREDICTORS = ("B5_oracle_anchor_upper_bound",)
DIRECT_BASELINES = ("B0_anchor_flat", "B1_anchor_last_known")
FORBIDDEN_PRODUCTION_PATHS = ("AI1_RETRAIN", "AI2_RETRAIN", "PRODUCTION_API", "M5", "M6", "M7", "SHELLY", "DEVICE", "KVS", "HA")
SCALE_CLIP = (0.05, 20.0)


@dataclass(frozen=True)
class P0046Result:
    status: str
    selected: dict[str, object]
    window_counts: dict[str, object]
    evidence: dict[str, str]


def run_p0046_backtest(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0046Result:
    start = time.monotonic()
    ai1_rows, ai2_rows = p0045.load_corrected_inputs(feature_db)
    contract = p0045.validate_input_contract(ai1_rows, ai2_rows)
    if not contract["ok"]:
        raise RuntimeError(f"P0046 input contract failed: {contract}")
    p0044.assign_splits(ai1_rows)
    p0043.assign_splits(ai2_rows)
    ai1_predictions = p0045.regenerate_ai1_predictions(ai1_rows)
    ai2_predictions = p0045.regenerate_ai2_predictions(ai2_rows)
    windows = build_origin_windows(ai1_rows, ai2_rows)
    if not windows:
        raise RuntimeError("P0046 found no complete Monday 06:00 168h forecast windows")
    time_profiles = p0045.fit_time_profile_baselines(ai2_rows)
    window_results = evaluate_all_windows(windows, ai1_predictions, ai2_predictions, time_profiles)
    metrics = summarize_metrics(window_results)
    selected = select_se1_configuration(metrics)
    summary = {
        "dataset_tables": ["ai1_day_to_local_week_training_targets_v2", "ai2_hour_to_day_training_targets_v2"],
        "contract": contract,
        "forecast_origin_policy": "Monday 06:00 fixed-CET model time; 168 consecutive fixed-CET hours; validation=2025 origins, holdout=2026 origins",
        "anchor_scenarios": ANCHOR_SCENARIOS,
        "anchor_methods": ANCHOR_METHODS,
        "scale_clip": SCALE_CLIP,
        "shape_source": "P0045 system_proxy_se1 selected formula combined_scaled",
        "window_counts": window_counts(windows),
        "metrics": metrics,
        "selected": selected,
        "window_results": window_results,
        "status": p0046_status(metrics, selected),
        "runtime_seconds": time.monotonic() - start,
    }
    evidence = write_p0046_evidence(Path(evidence_dir), summary)
    return P0046Result(status=str(summary["status"]), selected=selected, window_counts=summary["window_counts"], evidence=evidence)


def build_origin_windows(ai1_rows: list[dict[str, object]], ai2_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    ai1_dates = {series: {date.fromisoformat(str(row["model_cet_date"])) for row in ai1_rows if row["target_series"] == series} for series in TARGET_SERIES}
    by_series_hour: dict[str, dict[tuple[date, int], dict[str, object]]] = {series: {} for series in TARGET_SERIES}
    for row in ai2_rows:
        by_series_hour[str(row["target_series"])][(date.fromisoformat(str(row["model_cet_date"])), int(row["model_cet_hour"]))] = row
    windows = []
    for series in TARGET_SERIES:
        dates = sorted({day for day, _hour in by_series_hour[series]})
        for origin_day in dates:
            if origin_day.weekday() != 0:
                continue
            hourly = []
            for offset in range(168):
                absolute_hour = 6 + offset
                day = origin_day + timedelta(days=absolute_hour // 24)
                hour = absolute_hour % 24
                if day not in ai1_dates[series] or (day, hour) not in by_series_hour[series]:
                    hourly = []
                    break
                hourly.append(by_series_hour[series][(day, hour)])
            if len(hourly) != 168:
                continue
            split = p0045.split_for_date(origin_day)
            if split == "train":
                continue
            windows.append(
                {
                    "target_series": series,
                    "origin_date": origin_day.isoformat(),
                    "origin_hour": 6,
                    "split": split,
                    "hourly_rows": hourly,
                }
            )
    return windows


def window_shape_predictions(
    window: dict[str, object],
    ai1_predictions: dict[str, dict[str, dict[str, float]]],
    ai2_predictions: dict[str, dict[str, float]],
    time_profiles: dict[str, dict[tuple[int, int], float]],
) -> dict[str, list[float]]:
    series = str(window["target_series"])
    actual = [float(row["hour_price"]) for row in window["hourly_rows"]]  # type: ignore[index]
    return {
        "P0045_combined_scaled": p0045.combine_window(window, ai1_predictions, ai2_predictions, "scaled"),
        "B2_anchor_time_profile": p0045.time_profile_prediction(window, time_profiles),
        "B3_P0045_AI1_only_anchor": p0045.ai1_day_only(window, ai1_predictions),
        "B4_P0045_AI2_only_anchor": p0045.center([ai2_predictions[series][p0045.hour_key(row)] for row in window["hourly_rows"]]),  # type: ignore[index]
        "B5_oracle_anchor_upper_bound": p0045.center(actual),
    }


def evaluate_all_windows(
    windows: list[dict[str, object]],
    ai1_predictions: dict[str, dict[str, dict[str, float]]],
    ai2_predictions: dict[str, dict[str, float]],
    time_profiles: dict[str, dict[tuple[int, int], float]],
) -> list[dict[str, object]]:
    rows = []
    for window in windows:
        actual = [float(row["hour_price"]) for row in window["hourly_rows"]]  # type: ignore[index]
        shape_predictions = window_shape_predictions(window, ai1_predictions, ai2_predictions, time_profiles)
        for anchor_count in ANCHOR_SCENARIOS:
            direct_forecasts = {
                "B0_anchor_flat": [sum(actual[:anchor_count]) / anchor_count] * 168,
                "B1_anchor_last_known": [actual[anchor_count - 1]] * 168,
            }
            for predictor, forecast in direct_forecasts.items():
                rows.append(evaluate_anchored_window(window, predictor, "direct", anchor_count, forecast))
            for predictor, shape in shape_predictions.items():
                for method in ANCHOR_METHODS:
                    params = fit_anchor(method, actual[:anchor_count], shape[:anchor_count], anchor_count)
                    forecast = apply_anchor(params, shape)
                    rows.append(evaluate_anchored_window(window, predictor, method, anchor_count, forecast))
    return rows


def fit_anchor(method: str, actual_anchor: list[float], shape_anchor: list[float], anchor_count: int) -> dict[str, float | str]:
    if len(actual_anchor) != anchor_count or len(shape_anchor) != anchor_count:
        raise ValueError("anchor arrays must match anchor_count")
    if method == "L1_level":
        level = sum(actual - shape for actual, shape in zip(actual_anchor, shape_anchor)) / anchor_count
        return {"method": method, "level": level, "scale": 1.0}
    mean_actual = sum(actual_anchor) / anchor_count
    mean_shape = sum(shape_anchor) / anchor_count
    centered_actual = [value - mean_actual for value in actual_anchor]
    centered_shape = [value - mean_shape for value in shape_anchor]
    denominator = sum(value * value for value in centered_shape)
    raw_scale = 1.0 if denominator <= 1e-12 else sum(a * s for a, s in zip(centered_actual, centered_shape)) / denominator
    if not math.isfinite(raw_scale) or raw_scale <= 0.0:
        raw_scale = 1.0
    clipped = min(max(raw_scale, SCALE_CLIP[0]), SCALE_CLIP[1])
    if method == "L3_shrink_scale":
        weight = anchor_count / (anchor_count + 24.0)
        clipped = weight * clipped + (1.0 - weight) * 1.0
    if method not in ANCHOR_METHODS:
        raise ValueError(f"unknown anchor method: {method}")
    level = mean_actual - clipped * mean_shape
    return {"method": method, "level": level, "scale": clipped}


def apply_anchor(params: dict[str, float | str], shape: list[float]) -> list[float]:
    level = float(params["level"])
    scale = float(params["scale"])
    forecast = [level + scale * value for value in shape]
    if not all(math.isfinite(value) for value in forecast):
        raise RuntimeError("anchoring produced non-finite forecast")
    return forecast


def evaluate_anchored_window(
    window: dict[str, object],
    predictor: str,
    method: str,
    anchor_count: int,
    forecast: list[float],
) -> dict[str, object]:
    actual = [float(row["hour_price"]) for row in window["hourly_rows"]]  # type: ignore[index]
    if len(actual) != 168 or len(forecast) != 168:
        raise ValueError("P0046 forecast windows must be exactly 168 hours")
    eval_actual = actual[anchor_count:]
    eval_forecast = forecast[anchor_count:]
    abs_errors = [abs(a - p) for a, p in zip(eval_actual, eval_forecast)]
    signed = [p - a for a, p in zip(eval_actual, eval_forecast)]
    daily = daily_metrics(actual, forecast, anchor_count)
    opt = optimization_metrics(eval_actual, eval_forecast)
    return {
        "target_series": window["target_series"],
        "origin_date": window["origin_date"],
        "origin_hour": window["origin_hour"],
        "split": window["split"],
        "predictor": predictor,
        "anchor_method": method,
        "anchor_count": anchor_count,
        "is_oracle": predictor in ORACLE_PREDICTORS,
        "evaluation_hours": len(eval_actual),
        "MAE": mae(eval_actual, eval_forecast),
        "RMSE": rmse(eval_actual, eval_forecast),
        "median_absolute_error": percentile(abs_errors, 0.5),
        "mean_signed_error": sum(signed) / len(signed),
        "p90_absolute_error": percentile(abs_errors, 0.9),
        "p95_absolute_error": percentile(abs_errors, 0.95),
        "spearman_rank": spearman_from_ranks(p0045.ranks(eval_actual), p0045.ranks(eval_forecast)),
        "kendall_tau": kendall_tau(eval_actual, eval_forecast),
        "top_10_percent_hit_rate": hit_precision(eval_actual, eval_forecast, max(1, round(len(eval_actual) * 0.10)), high=True),
        "bottom_10_percent_hit_rate": hit_precision(eval_actual, eval_forecast, max(1, round(len(eval_actual) * 0.10)), high=False),
        "top_20h_precision": hit_precision(eval_actual, eval_forecast, min(20, len(eval_actual)), high=True),
        "bottom_20h_precision": hit_precision(eval_actual, eval_forecast, min(20, len(eval_actual)), high=False),
        "best_8h_hit_rate": hit_precision(eval_actual, eval_forecast, min(8, len(eval_actual)), high=False),
        "worst_8h_hit_rate": hit_precision(eval_actual, eval_forecast, min(8, len(eval_actual)), high=True),
        **opt,
        **daily,
        **window_context(window),
    }


def optimization_metrics(actual: list[float], predicted: list[float]) -> dict[str, float]:
    count = min(20, len(actual))
    cheap_actual = set(top_indexes(actual, count, high=False))
    cheap_pred = set(top_indexes(predicted, count, high=False))
    expensive_actual = set(top_indexes(actual, count, high=True))
    expensive_pred = set(top_indexes(predicted, count, high=True))
    perfect_cost = sum(actual[index] for index in cheap_actual)
    selected_cost = sum(actual[index] for index in cheap_pred)
    flat_indexes = set(range(count))
    flat_cost = sum(actual[index] for index in flat_indexes)
    return {
        "cheap_hour_capture_rate": len(cheap_actual & cheap_pred) / count,
        "expensive_hour_avoidance_rate": 1.0 - (len(expensive_actual & cheap_pred) / count),
        "regret_vs_perfect_top_N_selection": selected_cost - perfect_cost,
        "regret_vs_anchor_flat_top_N_selection": selected_cost - flat_cost,
        "expensive_hour_capture_rate": len(expensive_actual & expensive_pred) / count,
    }


def daily_metrics(actual: list[float], forecast: list[float], anchor_count: int) -> dict[str, float]:
    day_mae = []
    peak_errors = []
    low_errors = []
    actual_means = []
    forecast_means = []
    for day_index in range(7):
        lo = day_index * 24
        hi = lo + 24
        pairs = [(actual[index], forecast[index]) for index in range(lo, hi) if index >= anchor_count]
        if not pairs:
            continue
        day_actual = [pair[0] for pair in pairs]
        day_forecast = [pair[1] for pair in pairs]
        day_mae.append(mae(day_actual, day_forecast))
        peak_idx = top_indexes(day_actual, 1, high=True)[0]
        low_idx = top_indexes(day_actual, 1, high=False)[0]
        peak_errors.append(abs(day_actual[peak_idx] - day_forecast[peak_idx]))
        low_errors.append(abs(day_actual[low_idx] - day_forecast[low_idx]))
        actual_means.append(sum(day_actual) / len(day_actual))
        forecast_means.append(sum(day_forecast) / len(day_forecast))
    return {
        "daily_mean_MAE": sum(day_mae) / len(day_mae),
        "daily_peak_hour_error": sum(peak_errors) / len(peak_errors),
        "daily_low_hour_error": sum(low_errors) / len(low_errors),
        "day_rank_spearman": spearman_from_ranks(p0045.ranks(actual_means), p0045.ranks(forecast_means)),
    }


def summarize_metrics(rows: list[dict[str, object]]) -> dict[str, dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]]]:
    output: dict[str, dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]]] = {}
    for series in TARGET_SERIES:
        output[series] = {}
        for split in ("validate", "holdout"):
            output[series][split] = {}
            predictors = sorted({str(row["predictor"]) for row in rows if row["target_series"] == series and row["split"] == split})
            for predictor in predictors:
                output[series][split][predictor] = {}
                methods = sorted({str(row["anchor_method"]) for row in rows if row["target_series"] == series and row["split"] == split and row["predictor"] == predictor})
                for method in methods:
                    output[series][split][predictor][method] = {}
                    for anchor_count in ANCHOR_SCENARIOS:
                        subset = [row for row in rows if row["target_series"] == series and row["split"] == split and row["predictor"] == predictor and row["anchor_method"] == method and row["anchor_count"] == anchor_count]
                        output[series][split][predictor][method][f"A{anchor_count}"] = aggregate_metric_rows(subset)
    return output


def aggregate_metric_rows(rows: list[dict[str, object]]) -> dict[str, float]:
    metrics = (
        "MAE",
        "RMSE",
        "median_absolute_error",
        "mean_signed_error",
        "p90_absolute_error",
        "p95_absolute_error",
        "spearman_rank",
        "kendall_tau",
        "top_10_percent_hit_rate",
        "bottom_10_percent_hit_rate",
        "top_20h_precision",
        "bottom_20h_precision",
        "best_8h_hit_rate",
        "worst_8h_hit_rate",
        "cheap_hour_capture_rate",
        "expensive_hour_avoidance_rate",
        "regret_vs_perfect_top_N_selection",
        "regret_vs_anchor_flat_top_N_selection",
        "daily_mean_MAE",
        "daily_peak_hour_error",
        "daily_low_hour_error",
        "day_rank_spearman",
    )
    if not rows:
        return {"window_count": 0.0}
    return {"window_count": float(len(rows)), **{metric: sum(float(row[metric]) for row in rows) / len(rows) for metric in metrics}}


def select_se1_configuration(metrics: dict[str, object]) -> dict[str, object]:
    validate = metrics[PRIMARY_TARGET]["validate"]  # type: ignore[index]
    candidates = []
    for predictor in ("P0045_combined_scaled", "B2_anchor_time_profile", "B3_P0045_AI1_only_anchor", "B4_P0045_AI2_only_anchor"):
        for method in ANCHOR_METHODS:
            for anchor_count in ANCHOR_SCENARIOS:
                row = validate[predictor][method][f"A{anchor_count}"]  # type: ignore[index]
                if row.get("window_count", 0.0) <= 0.0:
                    continue
                candidates.append((float(row["MAE"]), -float(row["spearman_rank"]), predictor, method, anchor_count))
    if not candidates:
        raise RuntimeError("P0046 could not select SE1 anchoring configuration")
    _mae, _rank, predictor, method, anchor_count = min(candidates)
    return {"target_series": PRIMARY_TARGET, "predictor": predictor, "anchor_method": method, "anchor_count": anchor_count, "selection_split": "validate"}


def p0046_status(metrics: dict[str, object], selected: dict[str, object]) -> str:
    predictor = str(selected["predictor"])
    method = str(selected["anchor_method"])
    anchor = f"A{selected['anchor_count']}"
    validate = metrics[PRIMARY_TARGET]["validate"]  # type: ignore[index]
    holdout = metrics[PRIMARY_TARGET]["holdout"]  # type: ignore[index]
    selected_validate = validate[predictor][method][anchor]
    selected_holdout = holdout[predictor][method][anchor]
    flat_validate = validate["B0_anchor_flat"]["direct"][anchor]
    flat_holdout = holdout["B0_anchor_flat"]["direct"][anchor]
    if selected_validate["MAE"] >= flat_validate["MAE"] or selected_holdout["MAE"] > flat_holdout["MAE"] * 1.02:
        return "STOP"
    if selected_validate["spearman_rank"] <= flat_validate["spearman_rank"]:
        return "WARN"
    return "PASS"


def window_counts(windows: list[dict[str, object]]) -> dict[str, object]:
    counts: dict[str, dict[str, int]] = {series: defaultdict(int) for series in TARGET_SERIES}  # type: ignore[assignment]
    for window in windows:
        counts[str(window["target_series"])][str(window["split"])] += 1
    return {series: dict(sorted(values.items())) for series, values in counts.items()}


def subset_summary(rows: list[dict[str, object]], selected: dict[str, object]) -> dict[str, dict[str, float]]:
    chosen = [
        row
        for row in rows
        if row["target_series"] == PRIMARY_TARGET
        and row["split"] == "holdout"
        and row["predictor"] == selected["predictor"]
        and row["anchor_method"] == selected["anchor_method"]
        and row["anchor_count"] == selected["anchor_count"]
    ]
    solar_p75 = percentile([float(row["mean_solar"]) for row in chosen], 0.75)
    wind_p25 = percentile([float(row["mean_wind"]) for row in chosen], 0.25)
    wind_p75 = percentile([float(row["mean_wind"]) for row in chosen], 0.75)
    temp_p75 = percentile([float(row["mean_temp_delta"]) for row in chosen], 0.75)
    volatility_p75 = percentile([float(row["actual_scale"]) for row in chosen], 0.75)
    subsets = {
        "normal_week_subset": lambda r: not r["has_special_day"] and not r["has_bridge_day"] and not r["has_holiday_period"],
        "holiday_week_subset": lambda r: r["has_special_day"] or r["has_holiday_period"],
        "bridge_day_week_subset": lambda r: r["has_bridge_day"],
        "summer_subset": lambda r: int(r["month"]) in {6, 7, 8},
        "winter_subset": lambda r: int(r["month"]) in {12, 1, 2},
        "high_solar_week_subset": lambda r: float(r["mean_solar"]) >= solar_p75,
        "low_wind_week_subset": lambda r: float(r["mean_wind"]) <= wind_p25,
        "high_wind_week_subset": lambda r: float(r["mean_wind"]) >= wind_p75,
        "high_temp_delta_week_subset": lambda r: float(r["mean_temp_delta"]) >= temp_p75,
        "low_temp_delta_week_subset": lambda r: float(r["mean_temp_delta"]) < temp_p75,
        "negative_price_windows": lambda r: bool(r["has_negative_price"]),
        "near_zero_price_windows": lambda r: bool(r["has_near_zero_price"]),
        "high_volatility_windows": lambda r: float(r["actual_scale"]) >= volatility_p75,
    }
    return {name: aggregate_metric_rows([row for row in chosen if predicate(row)]) for name, predicate in subsets.items()}


def best_worst_windows(rows: list[dict[str, object]], selected: dict[str, object]) -> dict[str, object]:
    chosen = [
        row
        for row in rows
        if row["target_series"] == PRIMARY_TARGET
        and row["split"] == "holdout"
        and row["predictor"] == selected["predictor"]
        and row["anchor_method"] == selected["anchor_method"]
        and row["anchor_count"] == selected["anchor_count"]
    ]
    ordered = sorted(chosen, key=lambda row: float(row["MAE"]))
    return {"best_20": slim_window_rows(ordered[:20]), "worst_20": slim_window_rows(list(reversed(ordered[-20:])))}


def slim_window_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    keys = ("origin_date", "predictor", "anchor_method", "anchor_count", "MAE", "RMSE", "spearman_rank", "cheap_hour_capture_rate", "has_special_day", "month")
    return [{key: row[key] for key in keys} for row in rows]


def window_context(window: dict[str, object]) -> dict[str, object]:
    rows = window["hourly_rows"]  # type: ignore[assignment]
    prices = [float(row["hour_price"]) for row in rows]
    return {
        "has_special_day": any(int(row.get("is_special_day") or 0) for row in rows),
        "has_bridge_day": any(int(row.get("is_bridge_day") or 0) for row in rows),
        "has_holiday_period": any(int(row.get("is_holiday_period") or 0) for row in rows),
        "month": int(str(window["origin_date"])[5:7]),
        "mean_temp_delta": sum(float(row.get("hourly_temperature_delta") or 0.0) for row in rows) / len(rows),
        "mean_solar": sum(float(row.get("hourly_solar_actual") or 0.0) for row in rows) / len(rows),
        "mean_wind": sum(float(row.get("hourly_wind_actual") or 0.0) for row in rows) / len(rows),
        "actual_scale": robust_scale(prices),
        "has_negative_price": any(value < 0.0 for value in prices),
        "has_near_zero_price": any(abs(value) <= 0.01 for value in prices),
    }


def hit_precision(actual: list[float], predicted: list[float], count: int, *, high: bool) -> float:
    return len(set(top_indexes(actual, count, high=high)) & set(top_indexes(predicted, count, high=high))) / float(count)


def kendall_tau(actual: list[float], predicted: list[float]) -> float:
    concordant = 0
    discordant = 0
    for i in range(len(actual)):
        for j in range(i + 1, len(actual)):
            left = actual[i] - actual[j]
            right = predicted[i] - predicted[j]
            product = left * right
            if product > 0.0:
                concordant += 1
            elif product < 0.0:
                discordant += 1
    total = concordant + discordant
    return 0.0 if total == 0 else (concordant - discordant) / total


def write_p0046_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    subset = subset_summary(summary["window_results"], summary["selected"])  # type: ignore[arg-type]
    best_worst = best_worst_windows(summary["window_results"], summary["selected"])  # type: ignore[arg-type]
    paths = {
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog(summary)),
        "dataset": write(evidence_dir / "dataset-contract.md", dataset_report(summary)),
        "origin": write(evidence_dir / "forecast-origin-policy.md", origin_report(summary)),
        "anchor_policy": write(evidence_dir / "anchor-hour-policy.md", anchor_policy_report(summary)),
        "formulas": write(evidence_dir / "anchoring-formulas.md", formulas_report(summary)),
        "baselines": write(evidence_dir / "baselines.md", baselines_report(summary)),
        "validation": write(evidence_dir / "se1-validation-results.md", metrics_table(summary, "P0046 SE1 validation results", PRIMARY_TARGET, "validate")),
        "holdout": write(evidence_dir / "se1-holdout-results.md", metrics_table(summary, "P0046 SE1 holdout results", PRIMARY_TARGET, "holdout")),
        "anchor_compare": write(evidence_dir / "anchor-scenario-comparison.md", anchor_comparison_report(summary)),
        "rank": write(evidence_dir / "rank-and-top-bottom-results.md", metric_columns_report(summary, "P0046 rank and top/bottom results", ("spearman_rank", "kendall_tau", "top_10_percent_hit_rate", "bottom_10_percent_hit_rate", "top_20h_precision", "bottom_20h_precision", "best_8h_hit_rate", "worst_8h_hit_rate"))),
        "optimization": write(evidence_dir / "optimization-oriented-results.md", metric_columns_report(summary, "P0046 optimization-oriented results", ("cheap_hour_capture_rate", "expensive_hour_avoidance_rate", "regret_vs_perfect_top_N_selection", "regret_vs_anchor_flat_top_N_selection"))),
        "daily": write(evidence_dir / "daily-results.md", metric_columns_report(summary, "P0046 daily results", ("daily_mean_MAE", "daily_peak_hour_error", "daily_low_hour_error", "day_rank_spearman"))),
        "subsets": write(evidence_dir / "subset-results.md", subset_report(subset)),
        "best_worst": write(evidence_dir / "best-worst-windows.md", best_worst_report(best_worst)),
        "area_diff": write(evidence_dir / "area-diff-diagnostics.md", metrics_table(summary, "P0046 area_diff diagnostics", "area_diff_proxy_se3", "holdout")),
        "recomposed": write(evidence_dir / "recomposed-se3-diagnostics.md", recomposed_report(summary)),
        "oracle": write(evidence_dir / "oracle-diagnostics.md", oracle_report(summary)),
        "next": write(evidence_dir / "next-api-prototype-plan.md", next_api_report(summary)),
        "component": write(evidence_dir / "component-attribution-summary.md", component_summary(summary)),
    }
    write(evidence_dir / "metrics-summary.json", json.dumps(json_safe({key: value for key, value in summary.items() if key != "window_results"}), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "anchor-scenario-comparison.json", json.dumps(json_safe(summary["metrics"][PRIMARY_TARGET]), indent=2, sort_keys=True) + "\n")  # type: ignore[index]
    write(evidence_dir / "best-worst-windows.json", json.dumps(json_safe(best_worst), indent=2, sort_keys=True) + "\n")
    return paths


def changelog(summary: dict[str, object]) -> str:
    return f"# P0046 changelog\n\n- Built SE1-first anchored absolute-price backtest for P0045 `combined_scaled` 168h shape.\n- Tested Monday 06:00 fixed-CET origins with A11/A16/A24/A35 anchors and L1/L2/L3 deterministic anchoring.\n- Compared flat, last-known, time-profile, AI1-only, AI2-only and oracle diagnostics.\n- Result status: {summary['status']}.\n- Selected SE1 configuration: {summary['selected']}.\n- Wrote aggregate JSON and best/worst JSON; full per-window raw JSON is intentionally not committed because it is large and reproducible.\n- No AI retraining, production API, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.\n"


def dataset_report(summary: dict[str, object]) -> str:
    return f"# P0046 dataset contract\n\nused_tables = {summary['dataset_tables']}\n\ncontract = {summary['contract']}\n\nP0046 uses corrected P0042 fixed-CET v2 tables through P0045 loaders and fails rather than falling back to older datasets.\n"


def origin_report(summary: dict[str, object]) -> str:
    return f"# P0046 forecast-origin policy\n\nPrimary policy: {summary['forecast_origin_policy']}.\n\nwindow_counts = {summary['window_counts']}\n\nEach accepted window has exactly 168 hourly rows from Monday 06:00 through the following Monday 05:00 fixed-CET model time.\n"


def anchor_policy_report(summary: dict[str, object]) -> str:
    return "# P0046 anchor-hour policy\n\nAnchor scenarios: A11, A16, A24 and A35.\n\nFor each scenario, only the first N hours from forecast origin are used to fit anchoring parameters. All absolute-price error, rank and optimization metrics exclude those anchor hours.\n"


def formulas_report(summary: dict[str, object]) -> str:
    return f"# P0046 anchoring formulas\n\nScale clip range: {summary['scale_clip']}.\n\nL1 level-only: `forecast[h] = shape[h] + mean(actual_anchor - shape_anchor)`.\n\nL2 level + robust scale: ordinary least-squares slope on centered anchor values, forced finite/positive and clipped, then `level = mean(actual_anchor) - scale * mean(shape_anchor)`.\n\nL3 shrink scale: same clipped L2 scale shrunk toward `1.0` with `weight = anchor_count / (anchor_count + 24)`.\n"


def baselines_report(summary: dict[str, object]) -> str:
    return "# P0046 baselines\n\nB0_anchor_flat: future hours equal mean anchor price.\n\nB1_anchor_last_known: future hours equal last anchor price.\n\nB2_anchor_time_profile: train-only fixed-CET weekday/hour profile, centered as shape and anchored with L1/L2/L3.\n\nB3_P0045_AI1_only_anchor: P0045 AI1-only shape anchored with L1/L2/L3.\n\nB4_P0045_AI2_only_anchor: P0045 AI2-only shape anchored with L1/L2/L3.\n\nB5_oracle_anchor_upper_bound: actual future centered shape anchored with L1/L2/L3; diagnostic only and excluded from deployable selection.\n"


def metrics_table(summary: dict[str, object], title: str, series: str, split: str) -> str:
    lines = [f"# {title}", "", "| predictor | method | anchor | windows | MAE | RMSE | p95_abs | spearman | cheap_capture | oracle |", "|---|---|---|---:|---:|---:|---:|---:|---:|---|"]
    metrics = summary["metrics"][series][split]  # type: ignore[index]
    for predictor, methods in metrics.items():
        for method, anchors in methods.items():
            for anchor, row in anchors.items():
                lines.append(f"| {predictor} | {method} | {anchor} | {fmt(row.get('window_count', 0.0))} | {fmt(row.get('MAE', 0.0))} | {fmt(row.get('RMSE', 0.0))} | {fmt(row.get('p95_absolute_error', 0.0))} | {fmt(row.get('spearman_rank', 0.0))} | {fmt(row.get('cheap_hour_capture_rate', 0.0))} | {predictor in ORACLE_PREDICTORS} |")
    return "\n".join(lines) + "\n"


def anchor_comparison_report(summary: dict[str, object]) -> str:
    selected = summary["selected"]
    return "# P0046 anchor scenario comparison\n\nSelected from validation only: " + json.dumps(json_safe(selected), sort_keys=True) + "\n\n" + metrics_table(summary, "SE1 validation by anchor scenario", PRIMARY_TARGET, "validate")


def metric_columns_report(summary: dict[str, object], title: str, columns: tuple[str, ...]) -> str:
    lines = [f"# {title}", "", "| split | predictor | method | anchor | " + " | ".join(columns) + " |", "|---|---|---|---|" + "|".join("---:" for _ in columns) + "|"]
    metrics = summary["metrics"][PRIMARY_TARGET]  # type: ignore[index]
    for split in ("validate", "holdout"):
        for predictor, methods in metrics[split].items():
            for method, anchors in methods.items():
                for anchor, row in anchors.items():
                    if predictor in ORACLE_PREDICTORS:
                        continue
                    lines.append(f"| {split} | {predictor} | {method} | {anchor} | " + " | ".join(fmt(row.get(col, 0.0)) for col in columns) + " |")
    return "\n".join(lines) + "\n"


def subset_report(subset: dict[str, dict[str, float]]) -> str:
    lines = ["# P0046 subset results", "", "| subset | windows | MAE | RMSE | spearman | cheap_capture | p95_abs |", "|---|---:|---:|---:|---:|---:|---:|"]
    for name, row in subset.items():
        lines.append(f"| {name} | {fmt(row.get('window_count', 0.0))} | {fmt(row.get('MAE', 0.0))} | {fmt(row.get('RMSE', 0.0))} | {fmt(row.get('spearman_rank', 0.0))} | {fmt(row.get('cheap_hour_capture_rate', 0.0))} | {fmt(row.get('p95_absolute_error', 0.0))} |")
    return "\n".join(lines) + "\n"


def best_worst_report(best_worst: dict[str, object]) -> str:
    lines = ["# P0046 best/worst holdout windows", "", "| bucket | origin | predictor | method | anchor | MAE | RMSE | spearman | cheap_capture | special | month |", "|---|---|---|---|---:|---:|---:|---:|---:|---|---:|"]
    for bucket in ("best_20", "worst_20"):
        for row in best_worst[bucket]:  # type: ignore[index]
            lines.append(f"| {bucket} | {row['origin_date']} | {row['predictor']} | {row['anchor_method']} | {row['anchor_count']} | {fmt(row['MAE'])} | {fmt(row['RMSE'])} | {fmt(row['spearman_rank'])} | {fmt(row['cheap_hour_capture_rate'])} | {row['has_special_day']} | {row['month']} |")
    return "\n".join(lines) + "\n"


def recomposed_report(summary: dict[str, object]) -> str:
    return "# P0046 recomposed SE3 diagnostics\n\nRecomposed SE3 remains diagnostic only in P0046. This package did not select or promote an SE3 forecast path. SE3 recomposition should wait until area_diff absolute anchoring is reviewed separately.\n"


def oracle_report(summary: dict[str, object]) -> str:
    return metrics_table(summary, "P0046 oracle diagnostics", PRIMARY_TARGET, "holdout") + "\nOracle diagnostics use actual historical target structure and are excluded from deployable model selection.\n"


def next_api_report(summary: dict[str, object]) -> str:
    status = summary["status"]
    selected = summary["selected"]
    return f"# P0046 next API prototype plan\n\nStatus: {status}\n\nP0047 recommendation: build an SE1-only forecast-service/API prototype only if P0046 status is PASS or WARN and keep it feature-flagged/non-production.\n\nSelected SE1 anchoring configuration: {selected}.\n\nArea_diff and recomposed SE3 should remain diagnostic/fallback-constrained.\n"


def component_summary(summary: dict[str, object]) -> str:
    selected = summary["selected"]
    metrics = summary["metrics"][PRIMARY_TARGET]  # type: ignore[index]
    anchor = f"A{selected['anchor_count']}"
    pred = str(selected["predictor"])
    method = str(selected["anchor_method"])
    val = metrics["validate"][pred][method][anchor]
    hold = metrics["holdout"][pred][method][anchor]
    b0v = metrics["validate"]["B0_anchor_flat"]["direct"][anchor]
    b0h = metrics["holdout"]["B0_anchor_flat"]["direct"][anchor]
    lines = [
        "# P0046 component attribution summary",
        "",
        f"Status: {summary['status']}",
        f"1. P0045 SE1 shape source used: {summary['shape_source']}.",
        f"2. Forecast-origin policy: {summary['forecast_origin_policy']}.",
        f"3. Anchor scenarios tested: {summary['anchor_scenarios']}.",
        f"4. Selected anchoring formula: {selected}.",
        f"5. Validation selected MAE={fmt(val['MAE'])}, B0_anchor_flat MAE={fmt(b0v['MAE'])}.",
        f"6. Holdout selected MAE={fmt(hold['MAE'])}, B0_anchor_flat MAE={fmt(b0h['MAE'])}.",
        "7. Rank/top-bottom and optimization metrics are reported in dedicated evidence files.",
        "8. Worst windows are reported in `best-worst-windows.md`.",
        "9. P0047 should be SE1-only and non-production if it proceeds.",
        "10. area_diff/recomposed SE3 remains diagnostic only.",
        "11. Confirmed: no production API, no AI retraining, no M5/M6/M7 and no device actions.",
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
    result = run_p0046_backtest()
    print(json.dumps({"status": result.status, "selected": result.selected, "window_counts": result.window_counts, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
