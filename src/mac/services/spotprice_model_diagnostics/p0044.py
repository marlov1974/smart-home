"""P0044 AI-1 day-to-local-week shape/scale model diagnostics."""

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
from src.mac.services.spotprice_model_diagnostics.p0040 import spearman_from_ranks, top_indexes
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write


PACKAGE_ID = "P0044"
EVIDENCE_DIR = Path("requirements/package-runs/P0044")
RANDOM_SEED = 44
TARGET_SERIES = ("system_proxy_se1", "area_diff_proxy_se3")
TARGET_NAMES = ("day_level_shape", "log_day_scale_index", "log_local_7d_scale")
FEATURE_GROUPS = (
    "F0_time_only",
    "F1_time_plus_calendar",
    "F2_time_calendar_weather_actual",
    "F3_time_calendar_weather_delta",
    "F4_full",
    "F5_area_diff_wind_gradient_optional",
)
FORBIDDEN_PRODUCTION_PATHS = ("AI2_RETRAIN", "COMBINED_168H", "M5", "M6", "M7", "API", "SHELLY", "DEVICE", "KVS", "HA")


@dataclass(frozen=True)
class P0044Result:
    status: str
    split_counts: dict[str, object]
    selected_feature_groups: dict[str, dict[str, str]]
    evidence: dict[str, str]


class Encoder:
    def __init__(self, categories: dict[str, list[str]]):
        self.categories = categories


def run_p0044_training(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0044Result:
    rows = load_ai1_rows(feature_db)
    contract = validate_dataset_contract(rows)
    if not contract["ok"]:
        raise RuntimeError(f"P0044 dataset contract failed: {contract}")
    assign_splits(rows)
    results: dict[str, dict[str, object]] = {}
    configs: dict[str, dict[str, object]] = {}
    best_worst: dict[str, dict[str, object]] = {}
    for series in TARGET_SERIES:
        results[series] = {}
        configs[series] = {}
        best_worst[series] = {}
        series_rows = [row for row in rows if row["target_series"] == series]
        for target_name in TARGET_NAMES:
            target_result, config, days = train_evaluate_target(series_rows, series, target_name)
            results[series][target_name] = target_result
            configs[series][target_name] = config
            best_worst[series][target_name] = days
    summary = {
        "dataset_table": "ai1_day_to_local_week_training_targets_v2",
        "contract": contract,
        "split_counts": split_counts(rows),
        "results": results,
        "configs": configs,
        "best_worst": best_worst,
        "hgb_params": hgb_params(),
    }
    evidence = write_p0044_evidence(Path(evidence_dir), summary)
    status = p0044_status(summary)
    return P0044Result(
        status=status,
        split_counts=summary["split_counts"],
        selected_feature_groups={
            series: {target: str(configs[series][target]["selected_feature_group"]) for target in TARGET_NAMES}
            for series in TARGET_SERIES
        },
        evidence=evidence,
    )


def load_ai1_rows(feature_db: Path | str = DEFAULT_FEATURE_DB) -> list[dict[str, object]]:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='ai1_day_to_local_week_training_targets_v2'").fetchone():
            raise RuntimeError("P0042 corrected table ai1_day_to_local_week_training_targets_v2 is missing")
        rows = [dict(row) for row in conn.execute("SELECT * FROM ai1_day_to_local_week_training_targets_v2 ORDER BY target_series, model_cet_date")]
    return rows


def validate_dataset_contract(rows: list[dict[str, object]]) -> dict[str, object]:
    required = {"model_cet_date", "target_series", "local_7d_start", "local_7d_end", *TARGET_NAMES}
    missing = sorted(required - set(rows[0])) if rows else sorted(required)
    forbidden_target_columns_present = [name for name in ("day_mean_price", "day_ratio_index_diagnostic") if rows and name in rows[0]]
    counts = {series: len([row for row in rows if row.get("target_series") == series]) for series in TARGET_SERIES}
    unique_dates = {
        series: len({row["model_cet_date"] for row in rows if row.get("target_series") == series})
        for series in TARGET_SERIES
    }
    complete_local_windows = all(int(row.get("local_7d_row_count") or 0) == 168 for row in rows)
    finite_targets = all(math.isfinite(float(row[name])) for row in rows for name in TARGET_NAMES)
    return {
        "ok": bool(rows) and not missing and counts == unique_dates and complete_local_windows and finite_targets,
        "missing_fields": missing,
        "row_counts": counts,
        "unique_model_cet_dates_per_target": unique_dates,
        "local_7d_row_count_all_168_hours": complete_local_windows,
        "targets_are_finite": finite_targets,
        "uses_p0042_v2_table": True,
        "absolute_or_ratio_columns_present_but_not_targets": forbidden_target_columns_present,
        "target_columns_used": list(TARGET_NAMES),
    }


def assign_splits(rows: list[dict[str, object]]) -> None:
    for row in rows:
        d = date.fromisoformat(str(row["model_cet_date"]))
        if d <= date(2024, 12, 31):
            row["split"] = "train"
        elif d <= date(2025, 12, 31):
            row["split"] = "validate"
        else:
            row["split"] = "holdout"


def split_counts(rows: list[dict[str, object]]) -> dict[str, object]:
    global_counts: dict[str, int] = defaultdict(int)
    per_series: dict[str, dict[str, int]] = {series: defaultdict(int) for series in TARGET_SERIES}  # type: ignore[assignment]
    for row in rows:
        split = str(row["split"])
        global_counts[split] += 1
        per_series[str(row["target_series"])][split] += 1
    return {
        "global": dict(sorted(global_counts.items())),
        "per_target_series": {series: dict(sorted(counts.items())) for series, counts in per_series.items()},
        "split_definition": {
            "train": "earliest..2024-12-31",
            "validate": "2025-01-01..2025-12-31",
            "holdout": "2026-01-01..latest",
        },
    }


def train_evaluate_target(rows: list[dict[str, object]], series: str, target_name: str) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    train = [row for row in rows if row["split"] == "train"]
    validate = [row for row in rows if row["split"] == "validate"]
    holdout = [row for row in rows if row["split"] == "holdout"]
    baselines = fit_baselines(train, target_name)
    baseline_results = {
        name: {
            split: evaluate_predictions(subset, predict_baseline(subset, baseline), target_name)
            for split, subset in (("validate", validate), ("holdout", holdout))
        }
        for name, baseline in baselines.items()
    }
    feature_results: dict[str, dict[str, object]] = {}
    trained: dict[str, dict[str, object]] = {}
    for group in FEATURE_GROUPS:
        start = time.monotonic()
        model, encoder = train_hgb_model(train, group, target_name)
        validate_pred = predict_model(model, encoder, validate, group)
        holdout_pred = predict_model(model, encoder, holdout, group)
        feature_results[group] = {
            "validate": evaluate_predictions(validate, validate_pred, target_name),
            "holdout": evaluate_predictions(holdout, holdout_pred, target_name),
            "wall_clock_seconds": time.monotonic() - start,
        }
        trained[group] = {"model": model, "encoder": encoder}
    selected = select_feature_group(feature_results)
    selected_pred = predict_model(trained[selected]["model"], trained[selected]["encoder"], holdout, selected)  # type: ignore[arg-type]
    config = {
        "target_series": series,
        "target_name": target_name,
        "model_class": "HistGradientBoostingRegressor",
        "hyperparameters": hgb_params(),
        "selected_feature_group": selected,
        "selected_by": "best_validation_MAE_simplest_within_0.5_percent_of_best",
        "feature_names": feature_names_for_group(selected),
        "categorical_categories": trained[selected]["encoder"].categories,  # type: ignore[index]
        "trained_on_split": "train",
        "binary_artifact_committed": False,
    }
    return (
        {
            "baselines": baseline_results,
            "feature_groups": feature_results,
            "selected": selected,
            "subsets": subset_metrics(holdout, selected_pred, target_name),
            "diagnostic_window_centering": centered_diagnostic(rows=holdout, predicted=selected_pred, target_name=target_name),
        },
        config,
        best_worst_days(holdout, selected_pred, target_name),
    )


def feature_names_for_group(group: str) -> list[str]:
    names = ["weekday", "weekday_sin", "weekday_cos", "day_of_year", "day_of_year_sin", "day_of_year_cos"]
    if group in FEATURE_GROUPS[1:]:
        names += ["base_day_type", "special_day_type", "special_day_name", "is_special_day", "is_bridge_day", "is_holiday_period", "is_major_social_holiday"]
    if group in FEATURE_GROUPS[2:]:
        names += ["daily_temperature_actual", "daily_solar_actual", "daily_wind_actual"]
    if group in FEATURE_GROUPS[3:]:
        names += ["daily_temperature_normal", "daily_temperature_delta", "daily_solar_normal", "daily_solar_delta", "daily_wind_normal", "daily_wind_delta"]
    if group in FEATURE_GROUPS[4:]:
        names += [
            "daily_temperature_delta_minus_local_7d_mean",
            "daily_temperature_delta_rank_in_local_7d",
            "daily_solar_delta_minus_local_7d_mean",
            "daily_solar_delta_rank_in_local_7d",
            "daily_wind_delta_minus_local_7d_mean",
            "daily_wind_delta_rank_in_local_7d",
        ]
    if group == "F5_area_diff_wind_gradient_optional":
        names += [
            "daily_wind_system_proxy",
            "daily_wind_south_proxy",
            "daily_wind_central_proxy",
            "daily_wind_north_proxy",
            "daily_wind_south_minus_north",
            "daily_wind_central_minus_north",
        ]
    return names


def build_feature_matrix(rows: list[dict[str, object]], group: str, encoder: Encoder | None = None) -> tuple[list[list[float]], Encoder]:
    feature_names = feature_names_for_group(group)
    categorical = [name for name in ("base_day_type", "special_day_type", "special_day_name") if name in feature_names]
    if encoder is None:
        encoder = Encoder({name: sorted({str(row.get(name, "")) for row in rows}) for name in categorical})
    matrix: list[list[float]] = []
    for row in rows:
        values: list[float] = []
        for name in feature_names:
            if name in categorical:
                current = str(row.get(name, ""))
                values.extend(1.0 if current == category else 0.0 for category in encoder.categories[name])
            else:
                values.append(float(row.get(name) or 0.0))
        matrix.append(values)
    return matrix, encoder


def hgb_params() -> dict[str, object]:
    return {
        "max_iter": 80,
        "learning_rate": 0.04,
        "max_leaf_nodes": 7,
        "min_samples_leaf": 40,
        "l2_regularization": 0.10,
        "random_state": RANDOM_SEED,
        "early_stopping": True,
    }


def train_hgb_model(train_rows: list[dict[str, object]], group: str, target_name: str):
    from sklearn.ensemble import HistGradientBoostingRegressor

    x, encoder = build_feature_matrix(train_rows, group)
    y = [float(row[target_name]) for row in train_rows]
    model = HistGradientBoostingRegressor(**hgb_params())
    model.fit(x, y)
    return model, encoder


def predict_model(model: object, encoder: Encoder, rows: list[dict[str, object]], group: str) -> list[float]:
    x, _encoder = build_feature_matrix(rows, group, encoder)
    output = [float(value) for value in model.predict(x)]  # type: ignore[attr-defined]
    if not all(math.isfinite(value) for value in output):
        raise RuntimeError("P0044 model produced non-finite predictions")
    return output


def fit_baselines(train_rows: list[dict[str, object]], target_name: str) -> dict[str, dict[str, object]]:
    global_mean = mean_value(train_rows, target_name)
    if target_name == "day_level_shape":
        return {
            "B0_zero": {"kind": "constant", "value": 0.0},
            "B1_weekday_mean": grouped_baseline(train_rows, target_name, ("weekday",), 0.0),
            "B2_weekday_season_smooth": season_baseline(train_rows, target_name, include_weekday=True, global_value=0.0),
            "B3_special_day_mean": grouped_baseline(train_rows, target_name, ("base_day_type", "special_day_type"), 0.0),
        }
    if target_name == "log_day_scale_index":
        return {
            "B0_zero": {"kind": "constant", "value": 0.0},
            "B1_weekday_mean": grouped_baseline(train_rows, target_name, ("weekday",), 0.0),
            "B2_special_day_mean": grouped_baseline(train_rows, target_name, ("base_day_type", "special_day_type"), 0.0),
        }
    return {
        "B0_train_mean": {"kind": "constant", "value": global_mean},
        "B1_season_smooth": season_baseline(train_rows, target_name, include_weekday=False, global_value=global_mean),
        "B2_weather_actual_or_delta_simple": weather_bucket_baseline(train_rows, target_name, global_mean),
    }


def mean_value(rows: list[dict[str, object]], target_name: str) -> float:
    return sum(float(row[target_name]) for row in rows) / len(rows) if rows else 0.0


def grouped_baseline(rows: list[dict[str, object]], target_name: str, keys: tuple[str, ...], global_value: float) -> dict[str, object]:
    grouped: dict[tuple[str, ...], list[float]] = defaultdict(list)
    for row in rows:
        grouped[tuple(str(row.get(key, "")) for key in keys)].append(float(row[target_name]))
    return {
        "kind": "grouped",
        "keys": keys,
        "values": {key: sum(values) / len(values) for key, values in grouped.items()},
        "global": global_value,
        "fit_rows": len(rows),
    }


def season_baseline(rows: list[dict[str, object]], target_name: str, *, include_weekday: bool, global_value: float) -> dict[str, object]:
    grouped: dict[tuple[int, int], list[float]] = defaultdict(list)
    for row in rows:
        weekday = int(row["weekday"]) if include_weekday else -1
        grouped[(int(row["day_of_year"]), weekday)].append(float(row[target_name]))
    values: dict[tuple[int, int], float] = {}
    for doy in range(1, 367):
        weekdays = range(7) if include_weekday else [-1]
        for weekday in weekdays:
            bucket: list[float] = []
            for (candidate_doy, candidate_weekday), candidate_values in grouped.items():
                if candidate_weekday == weekday and day_distance(candidate_doy, doy) <= 21:
                    bucket.extend(candidate_values)
            if bucket:
                values[(doy, weekday)] = sum(bucket) / len(bucket)
    return {"kind": "season", "values": values, "include_weekday": include_weekday, "global": global_value, "smoothing_window_days": 21, "fit_rows": len(rows)}


def weather_bucket_baseline(rows: list[dict[str, object]], target_name: str, global_value: float) -> dict[str, object]:
    grouped: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        key = (
            bucket(float(row.get("daily_temperature_delta") or 0.0), (-3.0, 3.0)),
            bucket(float(row.get("daily_solar_delta") or 0.0), (-20.0, 20.0)),
            bucket(float(row.get("daily_wind_delta") or 0.0), (-0.05, 0.05)),
        )
        grouped[key].append(float(row[target_name]))
    return {
        "kind": "weather_bucket",
        "values": {key: sum(values) / len(values) for key, values in grouped.items()},
        "global": global_value,
        "fit_rows": len(rows),
    }


def bucket(value: float, limits: tuple[float, float]) -> str:
    if value < limits[0]:
        return "low"
    if value > limits[1]:
        return "high"
    return "normal"


def predict_baseline(rows: list[dict[str, object]], baseline: dict[str, object]) -> list[float]:
    if baseline["kind"] == "constant":
        return [float(baseline["value"]) for _row in rows]
    if baseline["kind"] == "grouped":
        keys = baseline["keys"]
        values = baseline["values"]
        return [float(values.get(tuple(str(row.get(key, "")) for key in keys), baseline["global"])) for row in rows]  # type: ignore[index]
    if baseline["kind"] == "season":
        values = baseline["values"]
        include_weekday = bool(baseline["include_weekday"])
        return [
            float(values.get((int(row["day_of_year"]), int(row["weekday"]) if include_weekday else -1), baseline["global"]))  # type: ignore[index]
            for row in rows
        ]
    values = baseline["values"]
    return [
        float(
            values.get(
                (
                    bucket(float(row.get("daily_temperature_delta") or 0.0), (-3.0, 3.0)),
                    bucket(float(row.get("daily_solar_delta") or 0.0), (-20.0, 20.0)),
                    bucket(float(row.get("daily_wind_delta") or 0.0), (-0.05, 0.05)),
                ),
                baseline["global"],
            )
        )
        for row in rows
    ]


def evaluate_predictions(rows: list[dict[str, object]], predicted: list[float], target_name: str) -> dict[str, float]:
    actual = [float(row[target_name]) for row in rows]
    errors = [p - a for a, p in zip(actual, predicted)]
    output = {
        "MAE": mae(actual, predicted) if actual else 0.0,
        "RMSE": rmse(actual, predicted) if actual else 0.0,
        "mean_signed_error": sum(errors) / len(errors) if errors else 0.0,
    }
    if target_name == "day_level_shape":
        output.update(local_window_rank_metrics(rows, predicted, target_name))
    elif target_name == "log_day_scale_index":
        rank = local_window_rank_metrics(rows, predicted, target_name)
        output.update(
            {
                "local_window_count": rank["local_window_count"],
                "spearman_rank_within_local_7d_mean": rank["spearman_rank_within_local_7d_mean"],
                "spearman_rank_within_local_7d_median": rank["spearman_rank_within_local_7d_median"],
                "highest_volatility_day_hit_rate": rank["highest_day_hit_rate"],
                "lowest_volatility_day_hit_rate": rank["lowest_day_hit_rate"],
                "top_2_volatility_days_precision": rank["top_2_days_precision"],
            }
        )
    else:
        output["correlation"] = pearson(actual, predicted)
    if target_name in ("log_day_scale_index", "log_local_7d_scale"):
        output["exponentiated_predictions_positive"] = 1.0 if all(math.isfinite(math.exp(value)) and math.exp(value) > 0.0 for value in predicted) else 0.0
    return output


def local_window_rank_metrics(rows: list[dict[str, object]], predicted: list[float], target_name: str) -> dict[str, float]:
    by_day = {date.fromisoformat(str(row["model_cet_date"])): (row, predicted[index]) for index, row in enumerate(rows)}
    spearman_values: list[float] = []
    high_hits: list[float] = []
    low_hits: list[float] = []
    top2: list[float] = []
    bottom2: list[float] = []
    for center in sorted(by_day):
        window_days = [center + timedelta(days=offset) for offset in range(-2, 5)]
        if any(day not in by_day for day in window_days):
            continue
        actual = [float(by_day[day][0][target_name]) for day in window_days]
        pred = [float(by_day[day][1]) for day in window_days]
        spearman_values.append(spearman_from_ranks(ranks(actual), ranks(pred)))
        high_hits.append(1.0 if top_indexes(actual, 1, high=True)[0] == top_indexes(pred, 1, high=True)[0] else 0.0)
        low_hits.append(1.0 if top_indexes(actual, 1, high=False)[0] == top_indexes(pred, 1, high=False)[0] else 0.0)
        top2.append(hit_precision(actual, pred, 2, high=True))
        bottom2.append(hit_precision(actual, pred, 2, high=False))
    return {
        "local_window_count": float(len(spearman_values)),
        "spearman_rank_within_local_7d_mean": sum(spearman_values) / len(spearman_values) if spearman_values else 0.0,
        "spearman_rank_within_local_7d_median": median(spearman_values),
        "highest_day_hit_rate": sum(high_hits) / len(high_hits) if high_hits else 0.0,
        "lowest_day_hit_rate": sum(low_hits) / len(low_hits) if low_hits else 0.0,
        "top_2_days_precision": sum(top2) / len(top2) if top2 else 0.0,
        "bottom_2_days_precision": sum(bottom2) / len(bottom2) if bottom2 else 0.0,
    }


def ranks(values: list[float]) -> list[float]:
    ordered = sorted((value, index) for index, value in enumerate(values))
    output = [0.0] * len(values)
    for rank, (_value, index) in enumerate(ordered, start=1):
        output[index] = float(rank)
    return output


def median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    middle = len(ordered) // 2
    return ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2.0


def hit_precision(actual: list[float], predicted: list[float], count: int, *, high: bool) -> float:
    return len(set(top_indexes(actual, count, high=high)) & set(top_indexes(predicted, count, high=high))) / float(count)


def pearson(left: list[float], right: list[float]) -> float:
    if len(left) < 2 or len(right) < 2:
        return 0.0
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((l - left_mean) * (r - right_mean) for l, r in zip(left, right))
    left_den = math.sqrt(sum((l - left_mean) ** 2 for l in left))
    right_den = math.sqrt(sum((r - right_mean) ** 2 for r in right))
    return numerator / (left_den * right_den) if left_den and right_den else 0.0


def day_distance(left: int, right: int) -> int:
    raw = abs(int(left) - int(right))
    return min(raw, 366 - raw)


def select_feature_group(results: dict[str, dict[str, object]]) -> str:
    scores = {group: float(row["validate"]["MAE"]) for group, row in results.items()}  # type: ignore[index]
    best = min(scores.values())
    threshold = best * 1.005
    for group in FEATURE_GROUPS:
        if scores[group] <= threshold:
            return group
    return min(scores, key=scores.get)


def subset_metrics(rows: list[dict[str, object]], predicted: list[float], target_name: str) -> dict[str, dict[str, float]]:
    temps = [float(row.get("daily_temperature_delta") or 0.0) for row in rows]
    high_temp = percentile(temps, 0.75) if temps else 0.0
    low_temp = percentile(temps, 0.25) if temps else 0.0
    subsets = {
        "special_day": lambda r: int(r.get("is_special_day") or 0) == 1,
        "normal_day": lambda r: int(r.get("is_special_day") or 0) == 0,
        "bridge_day": lambda r: int(r.get("is_bridge_day") or 0) == 1,
        "holiday_period": lambda r: int(r.get("is_holiday_period") or 0) == 1,
        "summer": lambda r: int(str(r["model_cet_date"])[5:7]) in {6, 7, 8},
        "winter": lambda r: int(str(r["model_cet_date"])[5:7]) in {12, 1, 2},
        "high_temp_delta": lambda r: float(r.get("daily_temperature_delta") or 0.0) >= high_temp,
        "low_temp_delta": lambda r: float(r.get("daily_temperature_delta") or 0.0) <= low_temp,
        "high_solar": lambda r: float(r.get("daily_solar_actual") or 0.0) >= 120.0,
        "low_wind": lambda r: float(r.get("daily_wind_actual") or 0.0) < 0.10,
        "high_wind": lambda r: float(r.get("daily_wind_actual") or 0.0) >= 0.25,
    }
    output = {}
    for name, predicate in subsets.items():
        indexes = [index for index, row in enumerate(rows) if predicate(row)]
        if indexes:
            output[name] = evaluate_predictions([rows[i] for i in indexes], [predicted[i] for i in indexes], target_name)
    return output


def centered_diagnostic(rows: list[dict[str, object]], predicted: list[float], target_name: str) -> dict[str, object]:
    if target_name != "day_level_shape":
        return {"applied_to_future_default": False, "tested": False}
    by_day = {date.fromisoformat(str(row["model_cet_date"])): index for index, row in enumerate(rows)}
    centered = list(predicted)
    touched: set[int] = set()
    for center in sorted(by_day):
        window = [center + timedelta(days=offset) for offset in range(-2, 5)]
        if any(day not in by_day for day in window):
            continue
        indexes = [by_day[day] for day in window]
        avg = sum(predicted[index] for index in indexes) / len(indexes)
        for index in indexes:
            centered[index] = predicted[index] - avg
            touched.add(index)
    return {
        "applied_to_future_default": False,
        "tested": True,
        "centered_rows": len(touched),
        "raw_holdout": evaluate_predictions(rows, predicted, target_name),
        "centered_holdout": evaluate_predictions(rows, centered, target_name),
    }


def best_worst_days(rows: list[dict[str, object]], predicted: list[float], target_name: str) -> dict[str, list[dict[str, object]]]:
    days = []
    for row, pred in zip(rows, predicted):
        actual = float(row[target_name])
        days.append(
            {
                "model_cet_date": row["model_cet_date"],
                "absolute_error": abs(pred - actual),
                "actual": actual,
                "predicted": pred,
                "special_day_type": row.get("special_day_type", ""),
                "is_special_day": int(row.get("is_special_day") or 0),
                "month": int(str(row["model_cet_date"])[5:7]),
            }
        )
    ordered = sorted(days, key=lambda row: float(row["absolute_error"]))
    return {"best_20": ordered[:20], "worst_20": list(reversed(ordered[-20:]))}


def p0044_status(summary: dict[str, object]) -> str:
    results = summary["results"]  # type: ignore[assignment]
    se1 = results["system_proxy_se1"]  # type: ignore[index]
    se1_day = se1["day_level_shape"]
    selected = se1_day["selected"]
    model = se1_day["feature_groups"][selected]["holdout"]
    b0 = se1_day["baselines"]["B0_zero"]["holdout"]
    rank_improved = model["spearman_rank_within_local_7d_mean"] >= b0["spearman_rank_within_local_7d_mean"] or model["top_2_days_precision"] >= b0["top_2_days_precision"]
    if model["MAE"] >= b0["MAE"] or not rank_improved:
        return "STOP"
    all_six = all(results[series][target]["selected"] in FEATURE_GROUPS for series in TARGET_SERIES for target in TARGET_NAMES)  # type: ignore[index]
    if not all_six:
        return "STOP"
    weak = []
    for series in TARGET_SERIES:
        for target in TARGET_NAMES:
            target_result = results[series][target]  # type: ignore[index]
            selected_group = target_result["selected"]
            model_mae = target_result["feature_groups"][selected_group]["holdout"]["MAE"]
            b0_name = "B0_train_mean" if target == "log_local_7d_scale" else "B0_zero"
            b0_mae = target_result["baselines"][b0_name]["holdout"]["MAE"]
            if model_mae >= b0_mae:
                weak.append((series, target))
    return "PASS" if not weak else "WARN"


def write_p0044_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog()),
        "dataset": write(evidence_dir / "dataset-contract.md", dataset_report(summary)),
        "split": write(evidence_dir / "training-split.md", split_report(summary)),
        "feature_list": write(evidence_dir / "feature-list-ai1.md", feature_list_report()),
        "feature_groups": write(evidence_dir / "feature-groups.md", feature_groups_report(summary)),
        "baselines": write(evidence_dir / "baselines.md", baselines_report(summary)),
        "ablation": write(evidence_dir / "feature-ablation-results.md", feature_groups_report(summary)),
        "rank": write(evidence_dir / "rank-and-top-bottom-day-results.md", rank_report(summary)),
        "subsets": write(evidence_dir / "subset-results.md", subset_report(summary)),
        "best_worst": write(evidence_dir / "best-worst-days.md", best_worst_report(summary)),
        "overlap": write(evidence_dir / "overlap-and-leakage-notes.md", overlap_report()),
        "next": write(evidence_dir / "next-combination-plan.md", next_report(summary)),
        "summary": write(evidence_dir / "component-attribution-summary.md", component_summary(summary)),
    }
    for series in TARGET_SERIES:
        for target in TARGET_NAMES:
            paths[f"{series}_{target}"] = write(evidence_dir / result_file_name(series, target), target_report(summary, series, target))
            write(evidence_dir / config_file_name(series, target), json.dumps(json_safe(summary["configs"][series][target]), indent=2, sort_keys=True) + "\n")  # type: ignore[index]
    write(evidence_dir / "metrics-summary.json", json.dumps(json_safe(summary), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "feature-ablation-results.json", json.dumps(json_safe({series: {target: summary["results"][series][target]["feature_groups"] for target in TARGET_NAMES} for series in TARGET_SERIES}), indent=2, sort_keys=True) + "\n")  # type: ignore[index]
    write(evidence_dir / "best-worst-days.json", json.dumps(json_safe(summary["best_worst"]), indent=2, sort_keys=True) + "\n")
    return paths


def result_file_name(series: str, target: str) -> str:
    prefix = "ai1-se1" if series == "system_proxy_se1" else "ai1-area-diff"
    suffix = {
        "day_level_shape": "day-level-results.md",
        "log_day_scale_index": "day-scale-results.md",
        "log_local_7d_scale": "local-7d-scale-results.md",
    }[target]
    return f"{prefix}-{suffix}"


def config_file_name(series: str, target: str) -> str:
    series_slug = "system-proxy-se1" if series == "system_proxy_se1" else "area-diff"
    target_slug = target.replace("_", "-")
    return f"model-config-ai1-{series_slug}-{target_slug}.json"


def changelog() -> str:
    return "# P0044 changelog\n\n- Trained AI-1 day-to-local-week diagnostics on the P0042 corrected fixed-CET AI-1 v2 table.\n- Evaluated six target-specific bounded HGB models against train-only baselines and F0-F5 feature groups.\n- Wrote model configuration JSON and metrics evidence; no binary model artifacts were committed.\n- No AI-2 retraining, combined forecast, M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.\n"


def dataset_report(summary: dict[str, object]) -> str:
    return f"# P0044 dataset contract\n\nused_table = `{summary['dataset_table']}`\n\ncontract = {summary['contract']}\n\nP0044 fails rather than falling back to P0041 pre-correction data. Absolute price and ratio diagnostic columns may exist in the input table for traceability, but the target list used for model training is exactly `{', '.join(TARGET_NAMES)}`.\n"


def split_report(summary: dict[str, object]) -> str:
    return f"# P0044 training split\n\ntrain: earliest..2024-12-31\nvalidate: 2025-01-01..2025-12-31\nholdout: 2026-01-01..latest complete fixed-CET model day\n\nsplit_counts = {summary['split_counts']}\n\nNo shuffle is used. Baselines and HGB models are fit on train rows only.\n"


def feature_list_report() -> str:
    return "# P0044 AI-1 feature list\n\n" + "\n".join(f"- {group}: {', '.join(feature_names_for_group(group))}" for group in FEATURE_GROUPS) + "\n"


def feature_groups_report(summary: dict[str, object]) -> str:
    lines = ["# P0044 feature group results", "", "| series | target | group | val_MAE | holdout_MAE | rank_or_corr | top/high | bottom/low |", "|---|---|---|---:|---:|---:|---:|---:|"]
    for series in TARGET_SERIES:
        for target in TARGET_NAMES:
            for group in FEATURE_GROUPS:
                row = summary["results"][series][target]["feature_groups"][group]  # type: ignore[index]
                metric = rank_metric(row["holdout"], target)
                high = row["holdout"].get("highest_day_hit_rate", row["holdout"].get("highest_volatility_day_hit_rate", 0.0))
                low = row["holdout"].get("lowest_day_hit_rate", row["holdout"].get("lowest_volatility_day_hit_rate", 0.0))
                lines.append(f"| {series} | {target} | {group} | {fmt(row['validate']['MAE'])} | {fmt(row['holdout']['MAE'])} | {fmt(metric)} | {fmt(high)} | {fmt(low)} |")
    return "\n".join(lines) + "\n"


def baselines_report(summary: dict[str, object]) -> str:
    lines = ["# P0044 baselines", "", "| series | target | baseline | val_MAE | holdout_MAE | rank_or_corr |", "|---|---|---|---:|---:|---:|"]
    for series in TARGET_SERIES:
        for target in TARGET_NAMES:
            for baseline, row in summary["results"][series][target]["baselines"].items():  # type: ignore[index]
                lines.append(f"| {series} | {target} | {baseline} | {fmt(row['validate']['MAE'])} | {fmt(row['holdout']['MAE'])} | {fmt(rank_metric(row['holdout'], target))} |")
    return "\n".join(lines) + "\n"


def target_report(summary: dict[str, object], series: str, target: str) -> str:
    target_result = summary["results"][series][target]  # type: ignore[index]
    selected = target_result["selected"]
    model = target_result["feature_groups"][selected]["holdout"]
    b0_name = "B0_train_mean" if target == "log_local_7d_scale" else "B0_zero"
    b0 = target_result["baselines"][b0_name]["holdout"]
    return "\n".join(
        [
            f"# P0044 {series} {target}",
            "",
            f"selected_feature_group = {selected}",
            "model_class = HistGradientBoostingRegressor",
            f"holdout_model_MAE = {fmt(model['MAE'])}",
            f"holdout_{b0_name}_MAE = {fmt(b0['MAE'])}",
            f"holdout_model_rank_or_corr = {fmt(rank_metric(model, target))}",
            f"diagnostic_centering = {target_result['diagnostic_window_centering']}",
            "",
        ]
    )


def rank_report(summary: dict[str, object]) -> str:
    lines = ["# P0044 rank and top/bottom day results", "", "| series | target | selected | windows | spearman | highest/hivol | lowest/lovol | top2 | bottom2 |", "|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for series in TARGET_SERIES:
        for target in ("day_level_shape", "log_day_scale_index"):
            selected = summary["results"][series][target]["selected"]  # type: ignore[index]
            row = summary["results"][series][target]["feature_groups"][selected]["holdout"]  # type: ignore[index]
            lines.append(
                f"| {series} | {target} | {selected} | {fmt(row['local_window_count'])} | {fmt(row['spearman_rank_within_local_7d_mean'])} | {fmt(row.get('highest_day_hit_rate', row.get('highest_volatility_day_hit_rate', 0.0)))} | {fmt(row.get('lowest_day_hit_rate', row.get('lowest_volatility_day_hit_rate', 0.0)))} | {fmt(row.get('top_2_days_precision', row.get('top_2_volatility_days_precision', 0.0)))} | {fmt(row.get('bottom_2_days_precision', 0.0))} |"
            )
    return "\n".join(lines) + "\n"


def subset_report(summary: dict[str, object]) -> str:
    lines = ["# P0044 subset results", "", "| series | target | subset | MAE | RMSE | rank_or_corr |", "|---|---|---|---:|---:|---:|"]
    for series in TARGET_SERIES:
        for target in TARGET_NAMES:
            for subset, row in summary["results"][series][target]["subsets"].items():  # type: ignore[index]
                lines.append(f"| {series} | {target} | {subset} | {fmt(row['MAE'])} | {fmt(row['RMSE'])} | {fmt(rank_metric(row, target))} |")
    return "\n".join(lines) + "\n"


def best_worst_report(summary: dict[str, object]) -> str:
    lines = ["# P0044 best/worst holdout center dates", ""]
    for series in TARGET_SERIES:
        for target in TARGET_NAMES:
            lines += [f"## {series} {target}", "", "| bucket | date | abs_error | actual | predicted | special_day_type | special | month |", "|---|---|---:|---:|---:|---|---:|---:|"]
            for bucket_name in ("best_20", "worst_20"):
                for row in summary["best_worst"][series][target][bucket_name]:  # type: ignore[index]
                    lines.append(f"| {bucket_name} | {row['model_cet_date']} | {fmt(row['absolute_error'])} | {fmt(row['actual'])} | {fmt(row['predicted'])} | {row['special_day_type']} | {row['is_special_day']} | {row['month']} |")
            lines.append("")
    return "\n".join(lines)


def overlap_report() -> str:
    return "# P0044 overlap and leakage notes\n\nAI-1 target rows use local windows D-2..D+4 over continuous `model_cet_date`, so adjacent rows overlap heavily and are not iid samples. Chronological validation and holdout are still used, but metrics should be read as model-selection diagnostics rather than independent-sample confidence estimates.\n\nLocal-window rank metrics use continuous date arithmetic and may cross calendar years. They require all seven window center dates to be present in the evaluated split, so windows adjacent to train/validate/holdout boundaries are skipped to avoid cross-split evaluation leakage. They are not skipped merely because they cross a calendar-year boundary.\n\nTraining features are time, Swedish calendar and weather-derived fields from the P0042 AI-1 dataset. P0044 does not use actual future spot prices, absolute day price, day ratio diagnostics, AI-2 predictions, combined forecast outputs or anchored absolute forecast errors as model features or targets.\n\nWeather features are intended as forecast-time-known/proxy forecast-known inputs for the future AI-1 combination track. P0044 records this assumption but does not implement forecast ingestion.\n"


def next_report(summary: dict[str, object]) -> str:
    lines = ["# P0044 next combination plan", ""]
    lines.append("P0045 can combine AI-1 with P0043 AI-2 only after reviewing which P0044 targets beat train-only baselines. Recommended target usage:")
    for series in TARGET_SERIES:
        for target in TARGET_NAMES:
            result = summary["results"][series][target]  # type: ignore[index]
            selected = result["selected"]
            model_mae = float(result["feature_groups"][selected]["holdout"]["MAE"])
            b0_name = "B0_train_mean" if target == "log_local_7d_scale" else "B0_zero"
            b0_mae = float(result["baselines"][b0_name]["holdout"]["MAE"])
            recommendation = "use AI-1 target" if model_mae < b0_mae else "prefer baseline/API-anchor fallback until improved"
            lines.append(f"- {series} {target}: selected={selected}, model_MAE={fmt(model_mae)}, {b0_name}_MAE={fmt(b0_mae)}, recommendation={recommendation}.")
    lines.append("")
    lines.append("No combined 168h forecast or anchored absolute API was built in P0044.")
    return "\n".join(lines) + "\n"


def component_summary(summary: dict[str, object]) -> str:
    status = p0044_status(summary)
    lines = ["# P0044 component attribution summary", "", f"Status: {status}", f"1. Corrected P0042 dataset/table used: `{summary['dataset_table']}`.", "2. Split: train earliest..2024-12-31, validate 2025, holdout 2026.", "3. Model class: bounded HistGradientBoostingRegressor.", "4. Feature groups tested: F0-F5."]
    for series in TARGET_SERIES:
        for target in TARGET_NAMES:
            result = summary["results"][series][target]  # type: ignore[index]
            selected = result["selected"]
            model = result["feature_groups"][selected]["holdout"]
            b0_name = "B0_train_mean" if target == "log_local_7d_scale" else "B0_zero"
            b0 = result["baselines"][b0_name]["holdout"]
            lines.append(f"{series} {target}: selected={selected}, model_MAE={fmt(model['MAE'])}, {b0_name}_MAE={fmt(b0['MAE'])}, rank_or_corr={fmt(rank_metric(model, target))}.")
    lines += [
        "Weather delta and relative-to-local-7d/rank effects are visible in `feature-ablation-results.md`.",
        "Targets weaker than their baseline should use baseline/API-anchor fallback in P0045 rather than being forced into the combined model.",
        "No AI-2 retraining, combined 168h forecast, M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.",
        "",
    ]
    return "\n".join(lines)


def rank_metric(row: dict[str, object], target: str) -> float:
    if target == "log_local_7d_scale":
        return float(row.get("correlation", 0.0))
    return float(row.get("spearman_rank_within_local_7d_mean", 0.0))


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def fmt(value: object) -> str:
    return f"{float(value):.6f}"


def main() -> int:
    result = run_p0044_training()
    print(json.dumps({"status": result.status, "split_counts": result.split_counts, "selected_feature_groups": result.selected_feature_groups, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
