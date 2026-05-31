"""P0037 full-year holdout component attribution."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import json
import math
import sqlite3
import time
from statistics import median
from typing import Iterable

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, FEATURE_NAMES, TrainingRow, build_calendar_features, mae, rmse
from src.mac.services.spotprice_temperature_normalization.core import (
    DEFAULT_CALENDAR_CSV_PATH,
    DEFAULT_PRICE_DB_PATH,
    DEFAULT_WEATHER_DB_PATH,
    M3_PRIMARY_ANOMALY_SIGNAL,
    TARGETS,
    _load_joined_rows,
    load_special_day_calendar,
    open_feature_database,
    temperature_bucket,
)


PACKAGE_ID = "P0037"
EVIDENCE_DIR = Path("requirements/package-runs/P0037")
TARGET_FIELDS = {
    "system_proxy_se1": "se1",
    "area_diff_proxy_se3": "area",
}
OBSERVED_VARIANTS = (
    "M1",
    "M1+M3A",
    "M1+M3B",
    "M1+M3A+M3B",
    "M1+M4",
    "M1+M3A+M4",
    "M1+M3B+M4",
    "M1+M3A+M3B+M4",
)


@dataclass(frozen=True)
class AnalysisResult:
    status: str
    row_counts: dict[str, int]
    matrix: list[dict[str, object]]
    evidence: dict[str, str]
    summary_answers: dict[str, str]


def run_p0037_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    price_db: Path | str = DEFAULT_PRICE_DB_PATH,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    calendar_csv: Path | str = DEFAULT_CALENDAR_CSV_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> AnalysisResult:
    rows = load_diagnostic_rows(feature_db=feature_db, price_db=price_db, weather_db=weather_db, calendar_csv=calendar_csv)
    fit_strict_components(rows)
    timings: list[dict[str, object]] = []
    models = train_m4_models(rows, timings)
    apply_m4_predictions(rows, models)
    matrix = build_component_matrix(rows)
    subsets = build_subset_metrics(rows)
    summaries = build_diagnostics(rows, matrix, subsets)
    evidence = write_evidence(
        evidence_dir=Path(evidence_dir),
        rows=rows,
        matrix=matrix,
        subsets=subsets,
        diagnostics=summaries,
        timings=timings,
    )
    return AnalysisResult(
        status=summaries["status"],
        row_counts=count_splits(rows),
        matrix=matrix,
        evidence=evidence,
        summary_answers=summaries["answers"],
    )


def load_diagnostic_rows(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    price_db: Path | str = DEFAULT_PRICE_DB_PATH,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    calendar_csv: Path | str = DEFAULT_CALENDAR_CSV_PATH,
) -> list[dict[str, object]]:
    with open_feature_database(feature_db) as conn:
        rows = _load_joined_rows(conn, price_db, weather_db, date(2022, 5, 30), None)
        full_period = load_full_period_m1(conn)
    calendar = load_special_day_calendar(calendar_csv)
    for row in rows:
        d = date.fromisoformat(str(row["local_date"]))
        row["split"] = split_for_p0037(d)
        row["year"] = d.year
        row["month"] = d.month
        row["is_2025_holdout"] = 1 if row["split"] == "holdout" else 0
        cal = calendar.get(str(row["local_date"]), normal_calendar())
        row.update(
            {
                "special_day_type": cal["special_day_type"],
                "special_day_name": cal["special_day_name"],
                "special_day_group": cal["special_day_group"],
                "bridge_anchor": cal["bridge_anchor"],
                "bridge_strength": cal["bridge_strength"],
                "is_special_day": 1 if is_special_calendar_day(cal) else 0,
                "is_holiday_period_day": int(cal["is_holiday_period_day"]),
            }
        )
        fp = full_period.get(str(row["utc_hour_start"]), {})
        row["full_period_m1_se1"] = float(fp.get("normal_price_v1_se1", 0.0))
        row["full_period_m1_area"] = float(fp.get("normal_price_v1_area_diff", 0.0))
    return rows


def load_full_period_m1(conn: sqlite3.Connection) -> dict[str, dict[str, float]]:
    if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='m3ab_normalized_prices'").fetchone():
        return {}
    return {
        str(row["utc_hour_start"]): {
            "normal_price_v1_se1": float(row["normal_price_v1_se1"]),
            "normal_price_v1_area_diff": float(row["normal_price_v1_area_diff"]),
        }
        for row in conn.execute(
            "SELECT utc_hour_start, normal_price_v1_se1, normal_price_v1_area_diff FROM m3ab_normalized_prices"
        )
    }


def fit_strict_components(rows: list[dict[str, object]]) -> None:
    train = [row for row in rows if row["split"] == "train"]
    for target, short in TARGET_FIELDS.items():
        actual_field = TARGETS[target]
        raw_surface = fit_m1_surface(train, actual_field)
        for row in rows:
            row[f"m1_raw_{short}"] = predict_m1(raw_surface, row)
    m2_surfaces = {signal: fit_m2_signal_normals(train, signal) for signal in set(M3_PRIMARY_ANOMALY_SIGNAL.values())}
    for row in rows:
        for signal, surface in m2_surfaces.items():
            normal = predict_m2_normal(surface, row)
            row[f"{signal}_normal"] = normal
            row[f"{signal}_anomaly"] = float(row[signal]) - normal
            row[f"{signal}_bucket"] = temperature_bucket(row[f"{signal}_anomaly"])
    m3a = fit_m3a_deltas(train)
    for row in rows:
        for target, short in TARGET_FIELDS.items():
            signal = M3_PRIMARY_ANOMALY_SIGNAL[target]
            bucket = str(row[f"{signal}_bucket"])
            row[f"m3a_{short}"] = m3a[(target, bucket)]
    m3b, m3b_stats = fit_m3b_deltas(train)
    for row in rows:
        for target, short in TARGET_FIELDS.items():
            row[f"m3b_{short}"] = m3b.get(m3b_key(target, row), 0.0)
            row[f"m3b_sample_count_{short}"] = m3b_stats.get(m3b_key(target, row), {}).get("sample_count", 0)
            row[f"m3b_shrinkage_{short}"] = m3b_stats.get(m3b_key(target, row), {}).get("shrinkage_factor", 0.0)
    for row in rows:
        row["structural_se1"] = float(row["actual_se1"]) - row["m3a_se1"] - row["m3b_se1"]
        row["structural_area"] = float(row["actual_area_diff"]) - row["m3a_area"] - row["m3b_area"]
    for target, short in TARGET_FIELDS.items():
        structural_field = f"structural_{short}"
        structural_surface = fit_m1_surface(train, structural_field)
        for row in rows:
            row[f"m1_structural_{short}"] = predict_m1(structural_surface, row)
            row[f"m4_target_{short}"] = float(row[structural_field]) - row[f"m1_structural_{short}"]


def fit_m1_surface(rows: list[dict[str, object]], value_field: str) -> dict[str, object]:
    by_bucket: dict[tuple[int, int, int], list[float]] = defaultdict(list)
    by_hour: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        key = (int(row["iso_week"]), int(row["weekday"]), int(row["local_hour"]))
        value = float(row[value_field])
        by_bucket[key].append(value)
        by_hour[int(row["local_hour"])].append(value)
    bucket_medians: dict[tuple[int, int, int], float] = {}
    for iso_week in range(1, 54):
        for weekday in range(7):
            for hour in range(24):
                values: list[float] = []
                for (candidate_week, candidate_weekday, candidate_hour), bucket_values in by_bucket.items():
                    if candidate_weekday == weekday and candidate_hour == hour and week_distance(candidate_week, iso_week) <= 2:
                        values.extend(bucket_values)
                if not values:
                    values = by_hour.get(hour, [])
                if values:
                    bucket_medians[(iso_week, weekday, hour)] = float(median(values))
    hour_medians = {hour: float(median(values)) for hour, values in by_hour.items() if values}
    global_median = float(median([float(row[value_field]) for row in rows]))
    return {"bucket_medians": bucket_medians, "hour_medians": hour_medians, "global_median": global_median}


def predict_m1(surface: dict[str, object], row: dict[str, object]) -> float:
    key = (int(row["iso_week"]), int(row["weekday"]), int(row["local_hour"]))
    bucket_medians = surface["bucket_medians"]
    if key in bucket_medians:
        return float(bucket_medians[key])
    return float(surface["hour_medians"].get(int(row["local_hour"]), surface["global_median"]))


def fit_m2_signal_normals(rows: list[dict[str, object]], signal: str) -> dict[str, object]:
    by_bucket: dict[tuple[int, int], list[float]] = defaultdict(list)
    by_hour: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        by_bucket[(int(row["day_of_year"]), int(row["local_hour"]))].append(float(row[signal]))
        by_hour[int(row["local_hour"])].append(float(row[signal]))
    medians: dict[tuple[int, int], float] = {}
    for doy in range(1, 367):
        for hour in range(24):
            values: list[float] = []
            for (candidate_doy, candidate_hour), bucket_values in by_bucket.items():
                if candidate_hour == hour and day_distance(candidate_doy, doy) <= 14:
                    values.extend(bucket_values)
            if not values:
                values = by_hour.get(hour, [])
            if values:
                medians[(doy, hour)] = float(median(values))
    hour_medians = {hour: float(median(values)) for hour, values in by_hour.items()}
    global_median = float(median([float(row[signal]) for row in rows]))
    return {"medians": medians, "hour_medians": hour_medians, "global_median": global_median}


def predict_m2_normal(surface: dict[str, object], row: dict[str, object]) -> float:
    key = (int(row["day_of_year"]), int(row["local_hour"]))
    if key in surface["medians"]:
        return float(surface["medians"][key])
    return float(surface["hour_medians"].get(int(row["local_hour"]), surface["global_median"]))


def fit_m3a_deltas(train: list[dict[str, object]]) -> dict[tuple[str, str], float]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in train:
        for target, short in TARGET_FIELDS.items():
            signal = M3_PRIMARY_ANOMALY_SIGNAL[target]
            bucket = str(row[f"{signal}_bucket"])
            actual = float(row[TARGETS[target]])
            grouped[(target, bucket)].append(actual - float(row[f"m1_raw_{short}"]))
    output: dict[tuple[str, str], float] = {}
    for target in TARGET_FIELDS:
        normal_values = grouped.get((target, "normal"), [])
        normal_median = float(median(normal_values)) if normal_values else 0.0
        cap = 0.50 if target == "system_proxy_se1" else 0.35
        for bucket in ("extreme_cold", "cold", "normal", "warm", "extreme_warm"):
            values = grouped.get((target, bucket), [])
            med = float(median(values)) if values else normal_median
            raw_delta = 0.0 if bucket == "normal" else 0.50 * (med - normal_median)
            output[(target, bucket)] = max(-cap, min(cap, raw_delta))
    return output


def fit_m3b_deltas(train: list[dict[str, object]]) -> tuple[dict[tuple[str, str, str, str, str], float], dict[tuple[str, str, str, str, str], dict[str, float]]]:
    grouped: dict[tuple[str, str, str, str, str], list[float]] = defaultdict(list)
    for row in train:
        if not row["is_special_day"]:
            continue
        for target, short in TARGET_FIELDS.items():
            residual = float(row[TARGETS[target]]) - float(row[f"m1_raw_{short}"]) - float(row[f"m3a_{short}"])
            grouped[m3b_key(target, row)].append(residual)
    deltas: dict[tuple[str, str, str, str, str], float] = {}
    stats: dict[tuple[str, str, str, str, str], dict[str, float]] = {}
    for key, values in grouped.items():
        target = key[0]
        med = float(median(values))
        shrinkage = len(values) / (len(values) + 24.0)
        cap = 0.50 if target == "system_proxy_se1" else 0.35
        delta = max(-cap, min(cap, med * shrinkage))
        deltas[key] = delta
        stats[key] = {"sample_count": float(len(values)), "shrinkage_factor": shrinkage, "median_residual": med}
    return deltas, stats


def train_m4_models(rows: list[dict[str, object]], timings: list[dict[str, object]]) -> dict[str, object]:
    train_rows = [row for row in rows if row["split"] == "train"]
    validate_rows = [row for row in rows if row["split"] == "validate"]
    features = build_features(rows)
    models: dict[str, object] = {}
    for target, short in TARGET_FIELDS.items():
        train_x = [features[str(row["utc_hour_start"])] for row in train_rows]
        train_y = [float(row[f"m4_target_{short}"]) for row in train_rows]
        validate_x = [features[str(row["utc_hour_start"])] for row in validate_rows]
        validate_y = [float(row[f"m4_target_{short}"]) for row in validate_rows]
        models[short] = train_hgb_grid(target, train_x, train_y, validate_x, validate_y, timings)
    for row in rows:
        row["features"] = features[str(row["utc_hour_start"])]
    return models


def build_features(rows: list[dict[str, object]]) -> dict[str, list[float]]:
    training_rows = [
        TrainingRow(
            utc_hour_start=str(row["utc_hour_start"]),
            local_date=str(row["local_date"]),
            local_hour=int(row["local_hour"]),
            target_se1=0.0,
            target_area_diff=0.0,
            target_se3=0.0,
            baseline_se1=0.0,
            baseline_area_diff=0.0,
            baseline_se3=0.0,
        )
        for row in rows
    ]
    return build_calendar_features(training_rows)


def train_hgb_grid(
    target: str,
    train_x: list[list[float]],
    train_y: list[float],
    validate_x: list[list[float]],
    validate_y: list[float],
    timings: list[dict[str, object]],
) -> object:
    from sklearn.ensemble import HistGradientBoostingRegressor

    best: tuple[float, object] | None = None
    local_timings: list[dict[str, object]] = []
    for index, params in enumerate(hgb_grid(), start=1):
        start = time.monotonic()
        estimator = HistGradientBoostingRegressor(**params)
        estimator.fit(train_x, train_y)
        elapsed = time.monotonic() - start
        predicted = [float(v) for v in estimator.predict(validate_x)]
        score = mae(validate_y, predicted)
        timing = {
            "candidate_id": f"p0037_{target}_{index:03d}",
            "target": target,
            "parameters": params,
            "train_rows": len(train_x),
            "feature_count": len(train_x[0]) if train_x else 0,
            "elapsed_seconds": elapsed,
            "validate_mae": score,
            "validate_rmse": rmse(validate_y, predicted),
            "status": "ok",
        }
        local_timings.append(timing)
        if best is None or score < best[0]:
            best = (score, estimator)
    if best is None:
        raise RuntimeError(f"no HGB candidate trained for {target}")
    best_score = best[0]
    selected_marked = False
    for timing in local_timings:
        timing["selected"] = False
        if not selected_marked and abs(float(timing["validate_mae"]) - best_score) < 1e-12:
            timing["selected"] = True
            selected_marked = True
    timings.extend(local_timings)
    return best[1]


def hgb_grid() -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for max_iter in (50, 100):
        for learning_rate in (0.03, 0.05):
            for max_leaf_nodes in (7, 15):
                output.append(
                    {
                        "max_iter": max_iter,
                        "learning_rate": learning_rate,
                        "max_leaf_nodes": max_leaf_nodes,
                        "min_samples_leaf": 100,
                        "l2_regularization": 0.1,
                        "early_stopping": True,
                        "random_state": 37,
                    }
                )
    return output


def apply_m4_predictions(rows: list[dict[str, object]], models: dict[str, object]) -> None:
    for row in rows:
        row["m4_se1"] = float(models["se1"].predict([row["features"]])[0])
        row["m4_area"] = float(models["area"].predict([row["features"]])[0])


def build_component_matrix(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    holdout = [row for row in rows if row["split"] == "holdout"]
    output: list[dict[str, object]] = []
    for target_mode in ("structural", "observed"):
        variants = ("M1", "M1+M4") if target_mode == "structural" else OBSERVED_VARIANTS
        previous: dict[str, float] = {}
        m1_metrics: dict[str, float] = {}
        m1_rmse: dict[str, float] = {}
        for variant in variants:
            for target in ("system_proxy_se1", "area_diff_proxy_se3", "recomposed_se3"):
                actual, predicted = series_for_variant(holdout, target_mode, variant, target)
                metric_mae = mae(actual, predicted)
                metric_rmse = rmse(actual, predicted)
                key = f"{target_mode}:{target}"
                if variant == "M1":
                    m1_metrics[key] = metric_mae
                    m1_rmse[key] = metric_rmse
                output.append(
                    {
                        "holdout_year": 2025,
                        "target_mode": target_mode,
                        "variant": variant,
                        "target": target,
                        "MAE": metric_mae,
                        "RMSE": metric_rmse,
                        "MAE_delta_vs_M1": metric_mae - m1_metrics.get(key, metric_mae),
                        "RMSE_delta_vs_M1": metric_rmse - m1_rmse.get(key, metric_rmse),
                        "MAE_delta_vs_previous_variant": metric_mae - previous.get(key, metric_mae),
                        "winner_or_status": "improves_M1" if metric_mae < m1_metrics.get(key, metric_mae) else "not_better_than_M1",
                    }
                )
                previous[key] = metric_mae
    return output


def series_for_variant(rows: list[dict[str, object]], target_mode: str, variant: str, target: str) -> tuple[list[float], list[float]]:
    if target == "recomposed_se3":
        se1_actual, se1_pred = series_for_variant(rows, target_mode, variant, "system_proxy_se1")
        area_actual, area_pred = series_for_variant(rows, target_mode, variant, "area_diff_proxy_se3")
        return [a + b for a, b in zip(se1_actual, area_actual)], [a + b for a, b in zip(se1_pred, area_pred)]
    short = TARGET_FIELDS[target]
    actual_col = "actual_se1" if short == "se1" else "actual_area_diff"
    actual = [float(row[actual_col]) for row in rows]
    if target_mode == "structural":
        actual = [float(row[f"structural_{short}"]) for row in rows]
        pred = [float(row[f"m1_structural_{short}"]) + (float(row[f"m4_{short}"]) if variant == "M1+M4" else 0.0) for row in rows]
        return actual, pred
    pred = [float(row[f"m1_structural_{short}"]) for row in rows]
    if "M3A" in variant:
        pred = [value + float(row[f"m3a_{short}"]) for value, row in zip(pred, rows)]
    if "M3B" in variant:
        pred = [value + float(row[f"m3b_{short}"]) for value, row in zip(pred, rows)]
    if "M4" in variant:
        pred = [value + float(row[f"m4_{short}"]) for value, row in zip(pred, rows)]
    return actual, pred


def build_subset_metrics(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    holdout = [row for row in rows if row["split"] == "holdout"]
    subsets = {
        "all_hours": holdout,
        "special_day_hours": [row for row in holdout if row["is_special_day"]],
        "non_special_day_hours": [row for row in holdout if not row["is_special_day"]],
        "fixed_public_holiday": [row for row in holdout if row["special_day_type"] == "fixed_public_holiday"],
        "movable_public_holiday": [row for row in holdout if row["special_day_type"] == "movable_public_holiday"],
        "major_social_holiday": [row for row in holdout if row["special_day_group"] == "major_social_holiday"],
        "bridge_day_strong": [row for row in holdout if row["bridge_strength"] == "strong"],
        "bridge_day_weak": [row for row in holdout if row["bridge_strength"] == "weak"],
        "holiday_period_day": [row for row in holdout if row["is_holiday_period_day"]],
        "normal_weekday": [row for row in holdout if row["special_day_type"] == "normal_weekday"],
        "normal_saturday": [row for row in holdout if row["special_day_type"] == "normal_saturday"],
        "normal_sunday": [row for row in holdout if row["special_day_type"] == "normal_sunday"],
    }
    for bucket in ("extreme_cold", "cold", "normal", "warm", "extreme_warm"):
        subsets[bucket if bucket != "normal" else "normal_temperature"] = [
            row for row in holdout if row[f"{M3_PRIMARY_ANOMALY_SIGNAL['system_proxy_se1']}_bucket"] == bucket
        ]
    subsets["special_day_AND_extreme_cold_cold"] = [
        row for row in holdout if row["is_special_day"] and row[f"{M3_PRIMARY_ANOMALY_SIGNAL['system_proxy_se1']}_bucket"] in {"extreme_cold", "cold"}
    ]
    subsets["non_special_day_AND_extreme_cold_cold"] = [
        row for row in holdout if not row["is_special_day"] and row[f"{M3_PRIMARY_ANOMALY_SIGNAL['system_proxy_se1']}_bucket"] in {"extreme_cold", "cold"}
    ]
    subsets["normal_weekday_AND_extreme_cold_cold"] = [
        row for row in holdout if row["special_day_type"] == "normal_weekday" and row[f"{M3_PRIMARY_ANOMALY_SIGNAL['system_proxy_se1']}_bucket"] in {"extreme_cold", "cold"}
    ]
    output: dict[str, list[dict[str, object]]] = {}
    for name, subset_rows in subsets.items():
        if not subset_rows:
            output[name] = []
            continue
        output[name] = []
        for variant in ("M1", "M1+M3A", "M1+M3B", "M1+M3A+M3B", "M1+M3A+M3B+M4"):
            actual, pred = series_for_variant(subset_rows, "observed", variant, "recomposed_se3")
            output[name].append({"subset": name, "rows": len(subset_rows), "variant": variant, "target": "recomposed_se3", "MAE": mae(actual, pred), "RMSE": rmse(actual, pred), "signed_error": sum(p - a for a, p in zip(actual, pred)) / len(actual)})
    return output


def build_diagnostics(rows: list[dict[str, object]], matrix: list[dict[str, object]], subsets: dict[str, list[dict[str, object]]]) -> dict[str, object]:
    def metric(mode: str, variant: str, target: str) -> float:
        return float(next(row["MAE"] for row in matrix if row["target_mode"] == mode and row["variant"] == variant and row["target"] == target))

    special_rows = subset_source(subsets, "special_day_hours")
    non_special_rows = subset_source(subsets, "non_special_day_hours")
    special_m1 = next(row for row in special_rows if row["variant"] == "M1") if special_rows else None
    special_m3b = next(row for row in special_rows if row["variant"] == "M1+M3B") if special_rows else None
    non_special_m1 = next(row for row in non_special_rows if row["variant"] == "M1") if non_special_rows else None
    non_special_m3b = next(row for row in non_special_rows if row["variant"] == "M1+M3B") if non_special_rows else None
    answers = {
        "m3a_improves_observed": verdict(metric("observed", "M1+M3A", "recomposed_se3"), metric("observed", "M1", "recomposed_se3")),
        "m3b_improves_special": verdict(float(special_m3b["MAE"]), float(special_m1["MAE"])) if special_m1 and special_m3b else "no special-day rows",
        "m3b_hurts_non_special": verdict(float(non_special_m3b["MAE"]), float(non_special_m1["MAE"])) if non_special_m1 and non_special_m3b else "no non-special rows",
        "m4_improves_structural": verdict(metric("structural", "M1+M4", "recomposed_se3"), metric("structural", "M1", "recomposed_se3")),
        "m4_area_diff": verdict(metric("structural", "M1+M4", "area_diff_proxy_se3"), metric("structural", "M1", "area_diff_proxy_se3")),
        "m4_se1": verdict(metric("structural", "M1+M4", "system_proxy_se1"), metric("structural", "M1", "system_proxy_se1")),
        "p0036_pass_full_year": "yes" if metric("structural", "M1+M4", "recomposed_se3") < metric("structural", "M1", "recomposed_se3") else "no",
        "most_suspect": most_suspect(matrix),
    }
    status = "PASS" if answers["p0036_pass_full_year"] == "yes" else "WARN"
    return {"status": status, "answers": answers}


def write_evidence(
    *,
    evidence_dir: Path,
    rows: list[dict[str, object]],
    matrix: list[dict[str, object]],
    subsets: dict[str, list[dict[str, object]]],
    diagnostics: dict[str, object],
    timings: list[dict[str, object]],
) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}
    row_counts = count_splits(rows)
    paths["CHANGELOG"] = write_text(evidence_dir / "CHANGELOG.md", "# P0037 changelog\n\n- Added full-year 2025 component attribution diagnostics.\n- No production model, M5/M6/M7/API, Shelly, HA, KVS or device changes.\n")
    paths["full_year"] = write_text(
        evidence_dir / "full-year-holdout-summary.md",
        "\n".join(
            [
                "# P0037 full-year holdout summary",
                "",
                f"Status: {diagnostics['status']}",
                "",
                "```text",
                "train = 2022-05-30..2023-12-31",
                "validate = 2024-01-01..2024-12-31",
                "holdout = 2025-01-01..2025-12-31",
                f"train_rows = {row_counts.get('train', 0)}",
                f"validate_rows = {row_counts.get('validate', 0)}",
                f"holdout_rows = {row_counts.get('holdout', 0)}",
                "strict_no_leakage = M1/M2/M3A/M3B/M4 fit without 2025 holdout rows",
                "m3a_weather_mode = observed-weather diagnostic attribution only; no M5 forecast claim",
                "```",
                "",
                matrix_markdown(matrix, target_mode="structural"),
                "",
                matrix_markdown(matrix, target_mode="observed"),
                "",
            ]
        ),
    )
    paths["matrix"] = write_text(evidence_dir / "component-attribution-matrix.md", matrix_markdown(matrix))
    (evidence_dir / "component-attribution-matrix.json").write_text(json.dumps(matrix, indent=2, sort_keys=True), encoding="utf-8")
    paths["matrix_json"] = str(evidence_dir / "component-attribution-matrix.json")
    paths["m1"] = write_text(evidence_dir / "m1-leakage-report.md", m1_report(rows))
    paths["m3a"] = write_text(evidence_dir / "m3a-temperature-attribution.md", m3a_report(rows, subsets))
    paths["m3b"] = write_text(evidence_dir / "m3b-special-day-attribution.md", m3b_report(rows, subsets))
    paths["m4"] = write_text(evidence_dir / "m4-residual-attribution.md", m4_report(rows, matrix, timings))
    paths["summary"] = write_text(evidence_dir / "component-attribution-summary.md", summary_report(diagnostics, matrix))
    return paths


def matrix_markdown(matrix: list[dict[str, object]], target_mode: str | None = None) -> str:
    rows = [row for row in matrix if target_mode is None or row["target_mode"] == target_mode]
    title = "# P0037 component attribution matrix" if target_mode is None else f"## {target_mode} target mode"
    lines = [
        title,
        "",
        "| holdout_year | target_mode | variant | target | MAE | RMSE | MAE_delta_vs_M1 | RMSE_delta_vs_M1 | MAE_delta_vs_previous_variant | winner_or_status |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['holdout_year']} | {row['target_mode']} | {row['variant']} | {row['target']} | {fmt(row['MAE'])} | {fmt(row['RMSE'])} | {fmt(row['MAE_delta_vs_M1'])} | {fmt(row['RMSE_delta_vs_M1'])} | {fmt(row['MAE_delta_vs_previous_variant'])} | {row['winner_or_status']} |"
        )
    return "\n".join(lines)


def m1_report(rows: list[dict[str, object]]) -> str:
    holdout = [row for row in rows if row["split"] == "holdout"]
    lines = [
        "# P0037 M1 leakage report",
        "",
        "| variant | target | MAE | RMSE |",
        "|---|---|---:|---:|",
    ]
    variants = {
        "full_period_M1_existing": ("full_period_m1_se1", "full_period_m1_area"),
        "train_only_M1_for_2025_holdout": ("m1_raw_se1", "m1_raw_area"),
        "train_only_M1_m3ab_normalized_for_2025_holdout": ("m1_structural_se1", "m1_structural_area"),
    }
    for name, (se1_col, area_col) in variants.items():
        for target, actual, pred in (
            ("system_proxy_se1", [float(r["actual_se1"]) for r in holdout], [float(r[se1_col]) for r in holdout]),
            ("area_diff_proxy_se3", [float(r["actual_area_diff"]) for r in holdout], [float(r[area_col]) for r in holdout]),
            ("recomposed_se3", [float(r["actual_se3"]) for r in holdout], [float(r[se1_col]) + float(r[area_col]) for r in holdout]),
        ):
            lines.append(f"| {name} | {target} | {fmt(mae(actual, pred))} | {fmt(rmse(actual, pred))} |")
    lines.extend(["", "Full-period M1 includes the 2025 holdout and is leakage-advantaged. It is a production-reference diagnostic, not a strict holdout baseline.", ""])
    return "\n".join(lines)


def m3a_report(rows: list[dict[str, object]], subsets: dict[str, list[dict[str, object]]]) -> str:
    holdout = [row for row in rows if row["split"] == "holdout"]
    lines = [
        "# P0037 M3A temperature attribution",
        "",
        "| bucket/subset | rows | M1 MAE | M1+M3A MAE | delta | signed_error_after |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name in ("extreme_cold", "cold", "normal_temperature", "warm", "extreme_warm"):
        subset_rows = [row for row in holdout if row in {id_row for id_row in rows}] if False else None
        metric_rows = subset_source(subsets, name)
        if not metric_rows:
            lines.append(f"| {name} | 0 |  |  |  |  |")
            continue
        before = next(row for row in metric_rows if row["variant"] == "M1")
        after = next(row for row in metric_rows if row["variant"] == "M1+M3A")
        lines.append(f"| {name} | {before['rows']} | {fmt(before['MAE'])} | {fmt(after['MAE'])} | {fmt(after['MAE'] - before['MAE'])} | {fmt(after['signed_error'])} |")
    corr_before = correlation(
        [float(row[f"{M3_PRIMARY_ANOMALY_SIGNAL['system_proxy_se1']}_anomaly"]) for row in holdout],
        [float(row["m1_structural_se1"]) - float(row["actual_se1"]) for row in holdout],
    )
    corr_after = correlation(
        [float(row[f"{M3_PRIMARY_ANOMALY_SIGNAL['system_proxy_se1']}_anomaly"]) for row in holdout],
        [float(row["m1_structural_se1"]) + float(row["m3a_se1"]) - float(row["actual_se1"]) for row in holdout],
    )
    lines.extend(["", f"before_M3A_residual_vs_temperature_anomaly_corr = {fmt(corr_before)}", f"after_M3A_residual_vs_temperature_anomaly_corr = {fmt(corr_after)}", ""])
    return "\n".join(lines)


def m3b_report(rows: list[dict[str, object]], subsets: dict[str, list[dict[str, object]]]) -> str:
    lines = [
        "# P0037 M3B special-day attribution",
        "",
        "| subset | rows | M1 MAE | M1+M3B MAE | delta | signed_error_after |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name in ("special_day_hours", "non_special_day_hours", "fixed_public_holiday", "movable_public_holiday", "major_social_holiday", "bridge_day_strong", "bridge_day_weak", "holiday_period_day"):
        metric_rows = subset_source(subsets, name)
        if not metric_rows:
            lines.append(f"| {name} | 0 |  |  |  |  |")
            continue
        before = next(row for row in metric_rows if row["variant"] == "M1")
        after = next(row for row in metric_rows if row["variant"] == "M1+M3B")
        lines.append(f"| {name} | {before['rows']} | {fmt(before['MAE'])} | {fmt(after['MAE'])} | {fmt(after['MAE'] - before['MAE'])} | {fmt(after['signed_error'])} |")
    lines.append("")
    return "\n".join(lines)


def m4_report(rows: list[dict[str, object]], matrix: list[dict[str, object]], timings: list[dict[str, object]]) -> str:
    holdout = [row for row in rows if row["split"] == "holdout"]
    selected = [row for row in timings if row.get("selected")]
    lines = [
        "# P0037 M4 residual attribution",
        "",
        matrix_markdown([row for row in matrix if row["target_mode"] == "structural"]),
        "",
        "## Selected HGB candidates",
        "",
        "| target | candidate_id | validate_mae | elapsed_seconds | parameters |",
        "|---|---|---:|---:|---|",
    ]
    for row in selected:
        lines.append(f"| {row['target']} | {row['candidate_id']} | {fmt(row['validate_mae'])} | {fmt(row['elapsed_seconds'])} | `{json.dumps(row['parameters'], sort_keys=True)}` |")
    lines.extend(["", "## Largest M4-worsened recomposed SE3 rows", "", largest_m4_rows(holdout, worsened=True), "", "## Largest M4-improved recomposed SE3 rows", "", largest_m4_rows(holdout, worsened=False), ""])
    return "\n".join(lines)


def summary_report(diagnostics: dict[str, object], matrix: list[dict[str, object]]) -> str:
    answers = diagnostics["answers"]
    lines = [
        "# P0037 component attribution summary",
        "",
        f"Status: {diagnostics['status']}",
        "",
        "## Required answers",
        "",
        f"1. M3A improves full-year observed reconstruction versus M1: {answers['m3a_improves_observed']}.",
        "2. M3A temperature-correlation details are in `m3a-temperature-attribution.md`.",
        "3. M3A extreme bucket over/under-correction is shown by bucket signed error in `m3a-temperature-attribution.md`.",
        f"4. M3B improves special-day hours versus M1: {answers['m3b_improves_special']}.",
        f"5. M3B hurts non-special-day hours: {answers['m3b_hurts_non_special']}.",
        f"6. M4 improves M3AB-normalized structural target versus train-only M1: {answers['m4_improves_structural']}. Area_diff: {answers['m4_area_diff']}. SE1: {answers['m4_se1']}.",
        f"7. P0036 PASS remains valid under full-year holdout: {answers['p0036_pass_full_year']}.",
        f"8. Most suspect remaining component/error source: {answers['most_suspect']}.",
        "9. Concentration by temperature/special-day subsets is in the attribution files.",
        "10. P0036 is diagnostic-PASS for full-year structural M4 if item 7 is yes; otherwise treat as WARN.",
        "",
        "No M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.",
        "",
    ]
    return "\n".join(lines)


def largest_m4_rows(rows: list[dict[str, object]], *, worsened: bool) -> str:
    ranked = []
    for row in rows:
        actual, m1 = series_for_variant([row], "structural", "M1", "recomposed_se3")
        _actual, m4 = series_for_variant([row], "structural", "M1+M4", "recomposed_se3")
        delta = abs(actual[0] - m4[0]) - abs(actual[0] - m1[0])
        ranked.append((delta, row, actual[0], m1[0], m4[0]))
    ranked.sort(key=lambda item: item[0], reverse=worsened)
    lines = [
        "| local_date | hour | special_day_type | actual_structural_se3 | M1 | M1+M4 | MAE_delta |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for delta, row, actual, m1, m4 in ranked[:20]:
        lines.append(f"| {row['local_date']} | {row['local_hour']} | {row['special_day_type']} | {fmt(actual)} | {fmt(m1)} | {fmt(m4)} | {fmt(delta)} |")
    return "\n".join(lines)


def split_for_p0037(d: date) -> str:
    if d <= date(2023, 12, 31):
        return "train"
    if d <= date(2024, 12, 31):
        return "validate"
    if d <= date(2025, 12, 31):
        return "holdout"
    return "future"


def count_splits(rows: Iterable[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[str(row["split"])] += 1
    return dict(counts)


def week_distance(left: int, right: int) -> int:
    direct = abs(left - right)
    return min(direct, 53 - direct)


def day_distance(left: int, right: int) -> int:
    direct = abs(left - right)
    return min(direct, 366 - direct)


def m3b_key(target: str, row: dict[str, object]) -> tuple[str, str, str, str, str]:
    return (
        target,
        str(row["special_day_type"]),
        str(row["special_day_name"]),
        str(row["special_day_group"]),
        str(row["bridge_anchor"]),
    )


def normal_calendar() -> dict[str, object]:
    return {
        "special_day_type": "normal_weekday",
        "special_day_name": "normal",
        "special_day_group": "normal",
        "bridge_anchor": "none",
        "bridge_strength": "none",
        "holiday_strength": 0.0,
        "is_public_holiday": 0,
        "is_major_social_holiday": 0,
        "is_holiday_eve": 0,
        "is_bridge_day": 0,
        "is_holiday_period_day": 0,
    }


def is_special_calendar_day(calendar: dict[str, object]) -> bool:
    return bool(
        int(calendar.get("is_public_holiday", 0))
        or int(calendar.get("is_major_social_holiday", 0))
        or int(calendar.get("is_holiday_eve", 0))
        or int(calendar.get("is_bridge_day", 0))
        or int(calendar.get("is_holiday_period_day", 0))
    )


def verdict(candidate: float, baseline: float) -> str:
    if candidate < baseline - 1e-9:
        return f"helps ({fmt(candidate)} vs {fmt(baseline)})"
    if candidate > baseline + 1e-9:
        return f"hurts/no improvement ({fmt(candidate)} vs {fmt(baseline)})"
    return f"no material change ({fmt(candidate)} vs {fmt(baseline)})"


def most_suspect(matrix: list[dict[str, object]]) -> str:
    observed = [row for row in matrix if row["target_mode"] == "observed" and row["target"] == "recomposed_se3"]
    full = next(row for row in observed if row["variant"] == "M1+M3A+M3B+M4")
    return f"remaining recomposed SE3 observed MAE {fmt(full['MAE'])}; inspect largest SE1/area spikes and M4-worsened rows"


def subset_source(subsets: dict[str, list[dict[str, object]]], name: str) -> list[dict[str, object]]:
    return subsets.get(name, [])


def correlation(xs: list[float], ys: list[float]) -> float:
    if not xs or len(xs) != len(ys):
        return 0.0
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_var = sum((x - x_mean) ** 2 for x in xs)
    y_var = sum((y - y_mean) ** 2 for y in ys)
    if x_var <= 0 or y_var <= 0:
        return 0.0
    return numerator / math.sqrt(x_var * y_var)


def fmt(value: object) -> str:
    return f"{float(value):.6f}"


def write_text(path: Path, text: str) -> str:
    path.write_text(text, encoding="utf-8")
    return str(path)


def main() -> int:
    result = run_p0037_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
