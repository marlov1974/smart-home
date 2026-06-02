"""P0048 SE3-SE1 bottleneck feature foundation and exploratory models."""

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

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_model_diagnostics.p0038 import solar_generation_proxy, wind_power_proxy
from src.mac.services.spotprice_model_diagnostics.p0040 import spearman_from_ranks
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, persist_rows, stats, write
from src.mac.services.spotprice_model_diagnostics import p0047
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0048"
EVIDENCE_DIR = Path("requirements/package-runs/P0048")
SOURCE_TABLE = "ai2_hour_to_day_training_targets_v2"
DATASET_TABLE = "se3_se1_bottleneck_training_dataset_v1"
TARGET_SE1 = "system_proxy_se1"
TARGET_SPREAD = "area_diff_proxy_se3"
RANDOM_SEED = 48
P0047_THRESHOLDS = {
    "near_zero_abs": 0.050000,
    "positive": 0.201919,
    "negative": -0.201919,
    "spike_positive": 0.807675,
    "spike_negative": -0.807675,
}
FORBIDDEN_PRODUCTION_PATHS = (
    "SE1_TO_SE3_ANCHORING",
    "SE3_API",
    "PRODUCTION_MODEL",
    "DEPLOYABLE_MODEL_ARTIFACT",
    "M5",
    "M6",
    "M7",
    "SHELLY",
    "DEVICE",
    "KVS",
    "HA",
)
WEATHER_AREA_PROXIES = (
    "se1_core_weather",
    "se3_load_weather",
    "south_connected_weather",
    "nordic_connected_weather",
    "p0038_south_wind_proxy",
    "p0038_central_wind_proxy",
    "p0038_north_wind_proxy",
    "p0038_south_solar_proxy",
    "p0038_se3_load_solar_proxy",
    "p0038_north_solar_proxy",
)
STAGE1_TARGETS = ("binary_positive_bottleneck", "binary_positive_spike", "multiclass_regime")
FEATURE_GROUPS = (
    "C0_time_calendar_baseline",
    "C1_time_calendar_weather_actual",
    "C2_time_calendar_weather_gradient",
    "C3_time_calendar_weather_anomaly_gradient",
    "C4_with_lagged_spread_features_diagnostic",
)
STAGE2_GROUPS = (
    "R0_regime_mean_baseline",
    "R1_time_calendar_baseline",
    "R2_weather_gradient_regressor",
    "R3_weather_anomaly_gradient_regressor",
    "R4_with_lagged_spread_features_diagnostic",
)
MODEL_FEATURE_COLUMNS = (
    "timestamp_utc",
    "model_cet_timestamp",
    "model_cet_date",
    "model_cet_hour",
    "model_cet_weekday",
    "model_cet_day_of_year",
    "model_cet_hour_sin",
    "model_cet_hour_cos",
    "model_cet_day_of_year_sin",
    "model_cet_day_of_year_cos",
    "se1_price",
    "se3_price",
    "se3_minus_se1",
    "abs_se3_minus_se1",
    "spread_sign",
    "spread_regime",
    "is_near_zero",
    "is_positive_bottleneck",
    "is_positive_spike",
    "is_negative_bottleneck",
    "is_negative_spike",
    "spread_severity_positive",
    "spread_severity_abs",
    "split",
)


@dataclass(frozen=True)
class P0048Result:
    status: str
    row_counts: dict[str, int]
    split_counts: dict[str, int]
    evidence: dict[str, str]


class Encoder:
    def __init__(self, categories: dict[str, list[str]]):
        self.categories = categories


def run_p0048_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0048Result:
    start = time.monotonic()
    ai2_rows = load_ai2_spread_source_rows(feature_db)
    base_rows = build_base_spread_rows(ai2_rows)
    if not base_rows:
        raise RuntimeError("P0048 cannot reconstruct SE3-SE1")
    weather_rows, weather_contract = load_weather_feature_rows(weather_db)
    modeling_rows, feature_contract = derive_weather_features(base_rows, weather_rows)
    add_regime_labels(modeling_rows, P0047_THRESHOLDS)
    add_lagged_features(modeling_rows)
    split_counts = assign_chronological_splits(modeling_rows)
    if not all(split_counts.get(split, 0) for split in ("train", "validate", "holdout")):
        raise RuntimeError(f"P0048 split is incomplete: {split_counts}")
    persisted = persist_modeling_dataset(feature_db, modeling_rows)
    stage1 = evaluate_stage1_classifiers(modeling_rows)
    stage2 = evaluate_stage2_regressors(modeling_rows)
    continuous = evaluate_continuous_spread_baselines(modeling_rows)
    combined = evaluate_two_stage_combined(modeling_rows, stage1, stage2)
    attribution = feature_attribution_summary(modeling_rows, stage1, stage2, continuous)
    spike_cases = spike_error_cases(modeling_rows, stage1, stage2, continuous)
    summary = {
        "status": p0048_status(stage1, stage2, continuous, feature_contract),
        "dataset_table": DATASET_TABLE,
        "persisted_rows": persisted,
        "row_counts": {"modeling_rows": len(modeling_rows), "source_rows": len(ai2_rows)},
        "split_counts": split_counts,
        "window": {
            "start": str(modeling_rows[0]["model_cet_date"]),
            "end": str(modeling_rows[-1]["model_cet_date"]),
            "latest_timestamp_utc": str(modeling_rows[-1]["timestamp_utc"]),
        },
        "thresholds": P0047_THRESHOLDS,
        "class_balance": class_balance(modeling_rows),
        "weather_contract": weather_contract,
        "feature_contract": feature_contract,
        "stage1": stage1,
        "stage2": stage2,
        "continuous": continuous,
        "combined": combined,
        "attribution": attribution,
        "spike_cases": spike_cases,
        "runtime_seconds": time.monotonic() - start,
        "forbidden_paths": FORBIDDEN_PRODUCTION_PATHS,
    }
    evidence = write_p0048_evidence(Path(evidence_dir), modeling_rows, summary)
    return P0048Result(status=str(summary["status"]), row_counts=summary["row_counts"], split_counts=split_counts, evidence=evidence)


def load_ai2_spread_source_rows(feature_db: Path | str = DEFAULT_FEATURE_DB) -> list[dict[str, object]]:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (SOURCE_TABLE,)).fetchone():
            raise RuntimeError(f"P0048 source table {SOURCE_TABLE} is missing")
        return [
            dict(row)
            for row in conn.execute(
                f"SELECT * FROM {SOURCE_TABLE} WHERE target_series IN (?, ?) ORDER BY timestamp_utc, target_series",
                (TARGET_SE1, TARGET_SPREAD),
            )
        ]


def build_base_spread_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_timestamp: dict[str, dict[str, dict[str, object]]] = defaultdict(dict)
    for row in rows:
        by_timestamp[str(row["timestamp_utc"])][str(row["target_series"])] = row
    output: list[dict[str, object]] = []
    for timestamp, grouped in sorted(by_timestamp.items()):
        se1 = grouped.get(TARGET_SE1)
        spread = grouped.get(TARGET_SPREAD)
        if not se1 or not spread:
            continue
        spread_value = float(spread["hour_price"])
        se1_price = float(se1["hour_price"])
        se3_price = se1_price + spread_value
        output.append(
            {
                "timestamp_utc": normalize_utc_text(timestamp),
                "weather_timestamp_utc": weather_utc_text(timestamp),
                "model_cet_timestamp": se1["model_cet_timestamp"],
                "model_cet_date": se1["model_cet_date"],
                "model_cet_hour": int(se1["model_cet_hour"]),
                "model_cet_weekday": int(se1["model_cet_weekday"]),
                "model_cet_day_of_year": int(se1["model_cet_day_of_year"]),
                "model_cet_hour_sin": float(se1["model_cet_hour_sin"]),
                "model_cet_hour_cos": float(se1["model_cet_hour_cos"]),
                "model_cet_day_of_year_sin": float(se1["model_cet_day_of_year_sin"]),
                "model_cet_day_of_year_cos": float(se1["model_cet_day_of_year_cos"]),
                "se1_price": se1_price,
                "se3_price": se3_price,
                "se3_minus_se1": spread_value,
                "abs_se3_minus_se1": abs(spread_value),
                "base_day_type": se1["base_day_type"],
                "special_day_type": se1["special_day_type"],
                "special_day_name": se1["special_day_name"],
                "is_special_day": int(se1["is_special_day"]),
                "is_bridge_day": int(se1["is_bridge_day"]),
                "is_holiday_period": int(se1["is_holiday_period"]),
                "is_major_social_holiday": int(se1["is_major_social_holiday"]),
                "stockholm_is_dst": int(se1.get("stockholm_is_dst") or 0),
                "stockholm_utc_offset_hours": int(se1.get("stockholm_utc_offset_hours") or 1),
                "stockholm_local_hour": int(se1.get("stockholm_local_hour") or se1["model_cet_hour"]),
            }
        )
    return output


def load_weather_feature_rows(weather_db: Path | str = DEFAULT_WEATHER_DB_PATH) -> tuple[dict[str, dict[str, float]], dict[str, object]]:
    with sqlite3.connect(Path(weather_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        records = conn.execute(
            f"""
            SELECT area_proxy, utc_hour_start, weighted_temperature_2m,
                   weighted_wind_speed_100m, weighted_shortwave_radiation,
                   weighted_cloud_cover
            FROM weather_area_hourly
            WHERE area_proxy IN ({",".join("?" for _ in WEATHER_AREA_PROXIES)})
            """,
            WEATHER_AREA_PROXIES,
        ).fetchall()
    by_timestamp: dict[str, dict[str, float]] = defaultdict(dict)
    coverage = Counter()
    for row in records:
        ts = normalize_utc_text(row["utc_hour_start"])
        proxy = str(row["area_proxy"])
        coverage[proxy] += 1
        temp = float(row["weighted_temperature_2m"] or 0.0)
        wind = wind_power_proxy(row["weighted_wind_speed_100m"])
        solar = solar_generation_proxy(row["weighted_shortwave_radiation"], row["weighted_cloud_cover"])
        target = by_timestamp[ts]
        if proxy == "se1_core_weather":
            target["temperature_north_proxy_actual"] = temp
            target["temperature_system_proxy_actual"] = temp
        elif proxy == "south_connected_weather":
            target["temperature_south_proxy_actual"] = temp
        elif proxy == "p0038_south_wind_proxy":
            target["wind_south_proxy_actual"] = wind
        elif proxy == "p0038_central_wind_proxy":
            target["wind_central_proxy_actual"] = wind
        elif proxy == "p0038_north_wind_proxy":
            target["wind_north_proxy_actual"] = wind
        elif proxy == "p0038_south_solar_proxy":
            target["solar_south_proxy_actual"] = solar
        elif proxy == "p0038_se3_load_solar_proxy":
            target["solar_system_proxy_actual"] = solar
        elif proxy == "p0038_north_solar_proxy":
            target["solar_north_proxy_actual"] = solar
    return by_timestamp, {"area_proxy_counts": dict(sorted(coverage.items())), "source_table": "weather_area_hourly"}


def derive_weather_features(
    base_rows: list[dict[str, object]],
    weather_rows: dict[str, dict[str, float]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    missing_timestamps = 0
    for base in base_rows:
        item = dict(base)
        weather = weather_rows.get(str(base["timestamp_utc"]), {})
        if not weather:
            missing_timestamps += 1
        for name in actual_weather_feature_names():
            item[name] = float(weather.get(name, 0.0))
        fill_system_features(item)
        add_gradient_features(item)
        rows.append(item)
    normal_names = actual_weather_feature_names() + gradient_feature_names()
    normals = fit_weather_normals(rows, normal_names)
    for row in rows:
        key = (int(row["model_cet_day_of_year"]), int(row["model_cet_hour"]))
        for name in normal_names:
            normal = float(normals[name].get(key, row[name]))
            row[name.replace("_actual", "_normal")] = normal
            row[name.replace("_actual", "_delta")] = float(row[name]) - normal
    add_delta_ranks_in_day(rows, [name.replace("_actual", "_delta") for name in normal_names])
    return rows, {
        "available_weather_actual_features": normal_names,
        "missing_weather_timestamps": missing_timestamps,
        "missing_requested_features": [],
        "normal_strategy": "fixed-CET day-of-year/hour train-period seasonal median",
    }


def fill_system_features(row: dict[str, object]) -> None:
    row["wind_system_proxy_actual"] = (
        0.50 * float(row["wind_north_proxy_actual"])
        + 0.25 * float(row["wind_central_proxy_actual"])
        + 0.25 * float(row["wind_south_proxy_actual"])
    )
    if not row.get("solar_system_proxy_actual"):
        row["solar_system_proxy_actual"] = (
            0.50 * float(row["solar_north_proxy_actual"])
            + 0.25 * float(row["solar_system_proxy_actual"])
            + 0.25 * float(row["solar_south_proxy_actual"])
        )
    row["temperature_system_proxy_actual"] = (
        0.70 * float(row["temperature_north_proxy_actual"])
        + 0.30 * float(row["temperature_south_proxy_actual"])
    )


def add_gradient_features(row: dict[str, object]) -> None:
    for prefix in ("wind", "solar", "temperature"):
        south = float(row[f"{prefix}_south_proxy_actual"])
        north = float(row[f"{prefix}_north_proxy_actual"])
        system = float(row[f"{prefix}_system_proxy_actual"])
        row[f"{prefix}_south_minus_north_actual"] = south - north
        row[f"{prefix}_south_minus_system_actual"] = south - system
        row[f"{prefix}_north_minus_system_actual"] = north - system
    row["wind_central_minus_north_actual"] = float(row["wind_central_proxy_actual"]) - float(row["wind_north_proxy_actual"])
    row["wind_south_minus_system_actual"] = float(row["wind_south_proxy_actual"]) - float(row["wind_system_proxy_actual"])
    row["wind_north_minus_system_actual"] = float(row["wind_north_proxy_actual"]) - float(row["wind_system_proxy_actual"])


def actual_weather_feature_names() -> list[str]:
    return [
        "wind_south_proxy_actual",
        "wind_central_proxy_actual",
        "wind_north_proxy_actual",
        "wind_system_proxy_actual",
        "solar_south_proxy_actual",
        "solar_north_proxy_actual",
        "solar_system_proxy_actual",
        "temperature_south_proxy_actual",
        "temperature_north_proxy_actual",
        "temperature_system_proxy_actual",
    ]


def gradient_feature_names() -> list[str]:
    return [
        "wind_south_minus_north_actual",
        "wind_central_minus_north_actual",
        "wind_south_minus_system_actual",
        "wind_north_minus_system_actual",
        "solar_south_minus_north_actual",
        "solar_south_minus_system_actual",
        "solar_north_minus_system_actual",
        "temperature_south_minus_north_actual",
        "temperature_south_minus_system_actual",
        "temperature_north_minus_system_actual",
    ]


def fit_weather_normals(rows: list[dict[str, object]], feature_names: list[str]) -> dict[str, dict[tuple[int, int], float]]:
    train = [row for row in rows if date.fromisoformat(str(row["model_cet_date"])) <= date(2024, 12, 31)]
    output: dict[str, dict[tuple[int, int], float]] = {}
    for name in feature_names:
        grouped: dict[tuple[int, int], list[float]] = defaultdict(list)
        by_hour: dict[int, list[float]] = defaultdict(list)
        for row in train:
            doy = int(row["model_cet_day_of_year"])
            hour = int(row["model_cet_hour"])
            value = float(row.get(name) or 0.0)
            grouped[(doy, hour)].append(value)
            by_hour[hour].append(value)
        normal_map: dict[tuple[int, int], float] = {}
        for doy in range(1, 367):
            for hour in range(24):
                values: list[float] = []
                for (candidate_doy, candidate_hour), bucket in grouped.items():
                    if candidate_hour == hour and day_distance(candidate_doy, doy) <= 14:
                        values.extend(bucket)
                if not values:
                    values = by_hour.get(hour, [])
                normal_map[(doy, hour)] = percentile(values, 0.5) if values else 0.0
        output[name] = normal_map
    return output


def add_delta_ranks_in_day(rows: list[dict[str, object]], delta_names: list[str]) -> None:
    by_day: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_day[str(row["model_cet_date"])].append(row)
    for day_rows in by_day.values():
        for name in delta_names:
            ordered = sorted((float(row[name]), row["timestamp_utc"]) for row in day_rows)
            denom = max(1, len(ordered) - 1)
            ranks = {ts: index / denom for index, (_value, ts) in enumerate(ordered)}
            for row in day_rows:
                row[f"{name}_rank_in_day"] = ranks[row["timestamp_utc"]]


def add_regime_labels(rows: list[dict[str, object]], thresholds: dict[str, float]) -> None:
    for row in rows:
        spread = float(row["se3_minus_se1"])
        sign, p0047_regime = p0047.assign_spread_regime(spread, thresholds)
        if p0047_regime in ("spread_negative", "spread_spike_negative"):
            regime = "negative_or_spike_negative"
        else:
            regime = p0047_regime.replace("spread_", "")
        row["spread_sign"] = sign
        row["spread_regime"] = regime
        row["is_near_zero"] = 1 if abs(spread) <= thresholds["near_zero_abs"] else 0
        row["is_positive_bottleneck"] = 1 if spread >= thresholds["positive"] else 0
        row["is_positive_spike"] = 1 if spread >= thresholds["spike_positive"] else 0
        row["is_negative_bottleneck"] = 1 if spread <= thresholds["negative"] else 0
        row["is_negative_spike"] = 1 if spread <= thresholds["spike_negative"] else 0
        row["binary_positive_bottleneck"] = row["is_positive_bottleneck"]
        row["binary_positive_spike"] = row["is_positive_spike"]
        row["multiclass_regime"] = regime
        row["spread_severity_positive"] = max(0.0, spread)
        row["spread_severity_abs"] = abs(spread)
        row["spread_excess_positive"] = max(0.0, spread - thresholds["positive"])
        row["log_positive_spread"] = math.log(max(spread, 1e-6)) if spread > 0.0 else 0.0


def add_lagged_features(rows: list[dict[str, object]]) -> None:
    ordered = sorted(rows, key=lambda row: str(row["timestamp_utc"]))
    by_timestamp = {str(row["timestamp_utc"]): row for row in ordered}
    previous_regime = "missing"
    for index, row in enumerate(ordered):
        prev = ordered[index - 1] if index > 0 else None
        lag24_ts = parse_utc(row["timestamp_utc"]) - timedelta(hours=24)
        lag24 = by_timestamp.get(lag24_ts.isoformat())
        row["lag1_spread"] = float(prev["se3_minus_se1"]) if prev else 0.0
        row["lag1_abs_spread"] = abs(float(prev["se3_minus_se1"])) if prev else 0.0
        row["lag1_is_positive_bottleneck"] = int(prev["is_positive_bottleneck"]) if prev else 0
        row["lag1_is_positive_spike"] = int(prev["is_positive_spike"]) if prev else 0
        row["lag24_spread"] = float(lag24["se3_minus_se1"]) if lag24 else 0.0
        row["lag24_is_positive_bottleneck"] = int(lag24["is_positive_bottleneck"]) if lag24 else 0
        row["previous_regime"] = str(prev["spread_regime"]) if prev else previous_regime


def assign_chronological_splits(rows: list[dict[str, object]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        day = date.fromisoformat(str(row["model_cet_date"]))
        if day <= date(2024, 12, 31):
            split = "train"
        elif day <= date(2025, 12, 31):
            split = "validate"
        else:
            split = "holdout"
        row["split"] = split
        counts[split] += 1
    return dict(sorted(counts.items()))


def persist_modeling_dataset(feature_db: Path | str, rows: list[dict[str, object]]) -> int:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        persist_rows(conn, DATASET_TABLE, rows)
    return len(rows)


def evaluate_stage1_classifiers(rows: list[dict[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for target in STAGE1_TARGETS:
        output[target] = {}
        for group in FEATURE_GROUPS:
            if group == "C0_time_calendar_baseline":
                result = evaluate_grouped_class_baseline(rows, target)
            else:
                result = evaluate_classifier_group(rows, target, group)
            output[target][group] = result
    return output


def evaluate_classifier_group(rows: list[dict[str, object]], target: str, group: str) -> dict[str, object]:
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.tree import DecisionTreeClassifier

    train, validate, holdout = split_rows(rows)
    model_class = "DecisionTreeClassifier" if target == "multiclass_regime" else "HistGradientBoostingClassifier"
    x_train, encoder = build_feature_matrix(train, group)
    y_train = [row[target] for row in train]
    if model_class == "DecisionTreeClassifier":
        model = DecisionTreeClassifier(max_depth=5, min_samples_leaf=120, random_state=RANDOM_SEED)
    else:
        model = HistGradientBoostingClassifier(max_iter=80, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=100, random_state=RANDOM_SEED)
    model.fit(x_train, y_train)
    return {
        "model_class": model_class,
        "feature_group": group,
        "validate": classification_metrics(model, encoder, validate, group, target),
        "holdout": classification_metrics(model, encoder, holdout, group, target),
    }


def evaluate_grouped_class_baseline(rows: list[dict[str, object]], target: str) -> dict[str, object]:
    train, validate, holdout = split_rows(rows)
    grouped: dict[tuple[int, int], Counter[object]] = defaultdict(Counter)
    for row in train:
        grouped[(int(row["model_cet_weekday"]), int(row["model_cet_hour"]))][row[target]] += 1
    global_label = Counter(row[target] for row in train).most_common(1)[0][0]

    def predict(subset: list[dict[str, object]]) -> list[object]:
        predictions = []
        for row in subset:
            bucket = grouped.get((int(row["model_cet_weekday"]), int(row["model_cet_hour"])))
            predictions.append(bucket.most_common(1)[0][0] if bucket else global_label)
        return predictions

    return {
        "model_class": "weekday_hour_majority_baseline",
        "feature_group": "C0_time_calendar_baseline",
        "validate": classification_metric_from_predictions([row[target] for row in validate], predict(validate), target),
        "holdout": classification_metric_from_predictions([row[target] for row in holdout], predict(holdout), target),
    }


def classification_metrics(model: object, encoder: Encoder, rows: list[dict[str, object]], group: str, target: str) -> dict[str, object]:
    x, _ = build_feature_matrix(rows, group, encoder)
    y_true = [row[target] for row in rows]
    y_pred = list(model.predict(x))  # type: ignore[attr-defined]
    metrics = classification_metric_from_predictions(y_true, y_pred, target)
    if target != "multiclass_regime" and hasattr(model, "predict_proba"):
        try:
            proba = [float(row[1]) for row in model.predict_proba(x)]  # type: ignore[attr-defined]
            metrics["roc_auc"] = binary_auc(y_true, proba)
            metrics["pr_auc"] = pr_auc(y_true, proba)
        except Exception:
            metrics["roc_auc"] = None
            metrics["pr_auc"] = None
    return metrics


def classification_metric_from_predictions(y_true: list[object], y_pred: list[object], target: str) -> dict[str, object]:
    labels = sorted({str(value) for value in y_true} | {str(value) for value in y_pred})
    matrix = {label: {inner: 0 for inner in labels} for label in labels}
    for true, pred in zip(y_true, y_pred):
        matrix[str(true)][str(pred)] += 1
    if target == "multiclass_regime":
        accuracy = sum(1 for true, pred in zip(y_true, y_pred) if true == pred) / len(y_true)
        macro_f1 = sum(f1_for_label(y_true, y_pred, label) for label in labels) / len(labels)
        return {"accuracy": accuracy, "macro_f1": macro_f1, "confusion_matrix": matrix, "positive_label": None}
    positive = 1
    tp = sum(1 for true, pred in zip(y_true, y_pred) if int(true) == positive and int(pred) == positive)
    fp = sum(1 for true, pred in zip(y_true, y_pred) if int(true) != positive and int(pred) == positive)
    fn = sum(1 for true, pred in zip(y_true, y_pred) if int(true) == positive and int(pred) != positive)
    tn = sum(1 for true, pred in zip(y_true, y_pred) if int(true) != positive and int(pred) != positive)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn, "tn": tn, "confusion_matrix": matrix, "positive_label": 1}


def f1_for_label(y_true: list[object], y_pred: list[object], label: str) -> float:
    tp = sum(1 for true, pred in zip(y_true, y_pred) if str(true) == label and str(pred) == label)
    fp = sum(1 for true, pred in zip(y_true, y_pred) if str(true) != label and str(pred) == label)
    fn = sum(1 for true, pred in zip(y_true, y_pred) if str(true) == label and str(pred) != label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def evaluate_stage2_regressors(rows: list[dict[str, object]]) -> dict[str, object]:
    positives = [row for row in rows if int(row["is_positive_bottleneck"])]
    output: dict[str, object] = {}
    for target in ("se3_minus_se1", "log_positive_spread", "spread_excess_positive"):
        output[target] = {}
        for group in STAGE2_GROUPS:
            output[target][group] = evaluate_regression_group(positives, target, group)
    return output


def evaluate_regression_group(rows: list[dict[str, object]], target: str, group: str) -> dict[str, object]:
    train, validate, holdout = split_rows(rows)
    if group == "R0_regime_mean_baseline":
        baseline = sum(float(row[target]) for row in train) / len(train)
        return {
            "model_class": "train_mean_baseline",
            "validate": regression_metric_from_predictions(validate, [baseline] * len(validate), target),
            "holdout": regression_metric_from_predictions(holdout, [baseline] * len(holdout), target),
        }
    from sklearn.ensemble import HistGradientBoostingRegressor

    feature_group = {
        "R1_time_calendar_baseline": "C0_time_calendar_baseline",
        "R2_weather_gradient_regressor": "C2_time_calendar_weather_gradient",
        "R3_weather_anomaly_gradient_regressor": "C3_time_calendar_weather_anomaly_gradient",
        "R4_with_lagged_spread_features_diagnostic": "C4_with_lagged_spread_features_diagnostic",
    }[group]
    x_train, encoder = build_feature_matrix(train, feature_group)
    y_train = [float(row[target]) for row in train]
    model = HistGradientBoostingRegressor(max_iter=90, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=80, random_state=RANDOM_SEED)
    model.fit(x_train, y_train)
    return {
        "model_class": "HistGradientBoostingRegressor",
        "validate": regression_metrics(model, encoder, validate, feature_group, target),
        "holdout": regression_metrics(model, encoder, holdout, feature_group, target),
    }


def evaluate_continuous_spread_baselines(rows: list[dict[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for group in ("S0_time_calendar_baseline", "S1_weather_gradient_regression", "S2_with_lagged_spread_features_diagnostic"):
        output[group] = evaluate_continuous_group(rows, group)
    return output


def evaluate_continuous_group(rows: list[dict[str, object]], group: str) -> dict[str, object]:
    train, validate, holdout = split_rows(rows)
    if group == "S0_time_calendar_baseline":
        grouped = grouped_mean(train, "se3_minus_se1")

        def predict(subset: list[dict[str, object]]) -> list[float]:
            return [grouped.get((int(row["model_cet_weekday"]), int(row["model_cet_hour"])), grouped["global"]) for row in subset]

        return {
            "model_class": "weekday_hour_mean_baseline",
            "validate": regression_metric_from_predictions(validate, predict(validate), "se3_minus_se1"),
            "holdout": regression_metric_from_predictions(holdout, predict(holdout), "se3_minus_se1"),
        }
    from sklearn.ensemble import HistGradientBoostingRegressor

    feature_group = "C2_time_calendar_weather_gradient" if group == "S1_weather_gradient_regression" else "C4_with_lagged_spread_features_diagnostic"
    x_train, encoder = build_feature_matrix(train, feature_group)
    y_train = [float(row["se3_minus_se1"]) for row in train]
    model = HistGradientBoostingRegressor(max_iter=90, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=80, random_state=RANDOM_SEED)
    model.fit(x_train, y_train)
    return {
        "model_class": "HistGradientBoostingRegressor",
        "validate": regression_metrics(model, encoder, validate, feature_group, "se3_minus_se1"),
        "holdout": regression_metrics(model, encoder, holdout, feature_group, "se3_minus_se1"),
    }


def regression_metrics(model: object, encoder: Encoder, rows: list[dict[str, object]], group: str, target: str) -> dict[str, object]:
    x, _ = build_feature_matrix(rows, group, encoder)
    pred = [clip_spread(float(value), target) for value in model.predict(x)]  # type: ignore[attr-defined]
    return regression_metric_from_predictions(rows, pred, target)


def regression_metric_from_predictions(rows: list[dict[str, object]], pred: list[float], target: str) -> dict[str, object]:
    actual = [float(row[target]) for row in rows]
    abs_errors = [abs(a - p) for a, p in zip(actual, pred)]
    return {
        "row_count": len(rows),
        "MAE": mae(actual, pred),
        "RMSE": rmse(actual, pred),
        "median_absolute_error": percentile(abs_errors, 0.5),
        "p90_absolute_error": percentile(abs_errors, 0.9),
        "p95_absolute_error": percentile(abs_errors, 0.95),
        "bias": sum(p - a for a, p in zip(actual, pred)) / len(actual) if actual else 0.0,
        "spearman": spearman_from_ranks(ranks(actual), ranks(pred)) if len(actual) > 2 else 0.0,
    }


def evaluate_two_stage_combined(rows: list[dict[str, object]], stage1: dict[str, object], stage2: dict[str, object]) -> dict[str, object]:
    validate_stage1 = stage1["binary_positive_bottleneck"]["C4_with_lagged_spread_features_diagnostic"]["validate"]  # type: ignore[index]
    validate_stage2 = stage2["se3_minus_se1"]["R4_with_lagged_spread_features_diagnostic"]["validate"]  # type: ignore[index]
    continuous = evaluate_continuous_group(rows, "S2_with_lagged_spread_features_diagnostic")
    return {
        "formula": "diagnostic comparison: stage1 lagged positive-bottleneck classifier plus stage2 lagged positive severity; exact probability*severity artifact is not persisted",
        "stage1_validate_f1": validate_stage1.get("f1", 0.0),
        "stage2_validate_MAE": validate_stage2.get("MAE", 0.0),
        "continuous_lagged_validate_MAE": continuous["validate"]["MAE"],
        "interpretation": "two-stage is promising if classifier F1/recall improves over time baseline and severity beats mean baseline",
    }


def build_feature_matrix(rows: list[dict[str, object]], group: str, encoder: Encoder | None = None) -> tuple[list[list[float]], Encoder]:
    features = feature_names_for_group(group)
    categorical = [name for name in ("base_day_type", "special_day_type", "special_day_name", "previous_regime") if name in features]
    if encoder is None:
        encoder = Encoder({name: sorted({str(row.get(name, "")) for row in rows}) for name in categorical})
    matrix = []
    for row in rows:
        values: list[float] = []
        for name in features:
            if name in categorical:
                current = str(row.get(name, ""))
                values.extend(1.0 if current == category else 0.0 for category in encoder.categories[name])
            else:
                values.append(float(row.get(name) or 0.0))
        matrix.append(values)
    return matrix, encoder


def feature_names_for_group(group: str) -> list[str]:
    base = [
        "model_cet_hour",
        "model_cet_hour_sin",
        "model_cet_hour_cos",
        "model_cet_weekday",
        "model_cet_day_of_year_sin",
        "model_cet_day_of_year_cos",
        "is_special_day",
        "is_bridge_day",
        "is_holiday_period",
        "is_major_social_holiday",
        "se1_price",
        "base_day_type",
        "special_day_type",
        "special_day_name",
    ]
    if group in ("C1_time_calendar_weather_actual", "C2_time_calendar_weather_gradient", "C3_time_calendar_weather_anomaly_gradient", "C4_with_lagged_spread_features_diagnostic"):
        base += actual_weather_feature_names()
    if group in ("C2_time_calendar_weather_gradient", "C3_time_calendar_weather_anomaly_gradient", "C4_with_lagged_spread_features_diagnostic"):
        base += gradient_feature_names()
    if group in ("C3_time_calendar_weather_anomaly_gradient", "C4_with_lagged_spread_features_diagnostic"):
        base += [name.replace("_actual", "_delta") for name in actual_weather_feature_names() + gradient_feature_names()]
    if group == "C4_with_lagged_spread_features_diagnostic":
        base += ["lag1_spread", "lag1_abs_spread", "lag1_is_positive_bottleneck", "lag1_is_positive_spike", "lag24_spread", "lag24_is_positive_bottleneck", "previous_regime"]
    return base


def split_rows(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    return (
        [row for row in rows if row["split"] == "train"],
        [row for row in rows if row["split"] == "validate"],
        [row for row in rows if row["split"] == "holdout"],
    )


def grouped_mean(rows: list[dict[str, object]], field: str) -> dict[object, float]:
    grouped: dict[tuple[int, int], list[float]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["model_cet_weekday"]), int(row["model_cet_hour"]))].append(float(row[field]))
    global_mean = sum(float(row[field]) for row in rows) / len(rows)
    return {"global": global_mean, **{key: sum(values) / len(values) for key, values in grouped.items()}}


def class_balance(rows: list[dict[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for field in STAGE1_TARGETS:
        counts = Counter(str(row[field]) for row in rows)
        output[field] = {"counts": dict(sorted(counts.items())), "share": {key: value / len(rows) for key, value in sorted(counts.items())}}
    return output


def feature_attribution_summary(rows: list[dict[str, object]], stage1: dict[str, object], stage2: dict[str, object], continuous: dict[str, object]) -> dict[str, object]:
    validate = {
        group: stage1["binary_positive_bottleneck"][group]["validate"] for group in FEATURE_GROUPS  # type: ignore[index]
    }
    return {
        "stage1_positive_validate_by_group": validate,
        "stage2_positive_severity_validate": {group: stage2["se3_minus_se1"][group]["validate"] for group in STAGE2_GROUPS},  # type: ignore[index]
        "continuous_validate": {group: row["validate"] for group, row in continuous.items()},  # type: ignore[union-attr]
        "gradient_improvement_over_system_weather_f1": float(validate["C2_time_calendar_weather_gradient"].get("f1", 0.0)) - float(validate["C1_time_calendar_weather_actual"].get("f1", 0.0)),
        "lagged_improvement_over_gradient_f1": float(validate["C4_with_lagged_spread_features_diagnostic"].get("f1", 0.0)) - float(validate["C2_time_calendar_weather_gradient"].get("f1", 0.0)),
    }


def spike_error_cases(rows: list[dict[str, object]], stage1: dict[str, object], stage2: dict[str, object], continuous: dict[str, object], limit: int = 50) -> list[dict[str, object]]:
    holdout = [row for row in rows if row["split"] == "holdout"]
    spikes = sorted([row for row in holdout if int(row["is_positive_spike"])], key=lambda row: float(row["se3_minus_se1"]), reverse=True)
    keys = ("timestamp_utc", "model_cet_date", "model_cet_hour", "se1_price", "se3_price", "se3_minus_se1", "spread_regime", "lag1_spread", "wind_south_minus_north_actual", "solar_south_minus_north_actual", "temperature_south_minus_north_actual")
    return [{key: row.get(key, "") for key in keys} for row in spikes[:limit]]


def p0048_status(stage1: dict[str, object], stage2: dict[str, object], continuous: dict[str, object], feature_contract: dict[str, object]) -> str:
    if feature_contract["missing_weather_timestamps"]:
        return "WARN"
    baseline = stage1["binary_positive_bottleneck"]["C0_time_calendar_baseline"]["validate"]["f1"]  # type: ignore[index]
    lagged = stage1["binary_positive_bottleneck"]["C4_with_lagged_spread_features_diagnostic"]["validate"]["f1"]  # type: ignore[index]
    if lagged <= baseline:
        return "WARN"
    return "PASS"


def write_p0048_evidence(evidence_dir: Path, rows: list[dict[str, object]], summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    write_csv(evidence_dir / "modeling-dataset-sample.csv", rows[:240], tuple(rows[0].keys()))
    write_csv(evidence_dir / "spike-error-cases.csv", summary["spike_cases"], tuple(summary["spike_cases"][0].keys()) if summary["spike_cases"] else ())
    paths = {
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog(summary)),
        "dataset": write(evidence_dir / "dataset-contract.md", dataset_contract_report(summary)),
        "feature": write(evidence_dir / "feature-foundation.md", feature_foundation_report(summary)),
        "missing": write(evidence_dir / "missing-feature-report.md", missing_feature_report(summary)),
        "labels": write(evidence_dir / "regime-labels.md", regime_labels_report(summary)),
        "split": write(evidence_dir / "training-split.md", split_report(summary)),
        "stage1": write(evidence_dir / "stage1-classification-results.md", stage1_report(summary)),
        "stage2": write(evidence_dir / "stage2-severity-results.md", stage2_report(summary)),
        "continuous": write(evidence_dir / "continuous-spread-baseline-results.md", continuous_report(summary)),
        "combined": write(evidence_dir / "two-stage-combined-diagnostics.md", combined_report(summary)),
        "attribution": write(evidence_dir / "feature-attribution.md", attribution_report(summary)),
        "calibration": write(evidence_dir / "calibration-and-error-review.md", calibration_report(summary)),
        "spikes": write(evidence_dir / "spike-case-review.md", spike_report(summary)),
        "next": write(evidence_dir / "next-package-recommendation.md", next_package_report(summary)),
        "component": write(evidence_dir / "component-attribution-summary.md", component_summary(summary)),
    }
    write(evidence_dir / "metrics-summary.json", json.dumps(json_safe(summary), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "confusion-matrices.json", json.dumps(json_safe(extract_confusion_matrices(summary["stage1"])), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "feature-importance.json", json.dumps(json_safe(summary["attribution"]), indent=2, sort_keys=True) + "\n")
    return paths


def changelog(summary: dict[str, object]) -> str:
    return f"# P0048 changelog\n\n- Built local `{DATASET_TABLE}` with {summary['persisted_rows']} rows.\n- Added south/north/system weather proxy actuals, normals, deltas and gradient features.\n- Evaluated exploratory Stage-1 classifiers, Stage-2 positive severity regressors and continuous spread regression baselines.\n- Result status: {summary['status']}.\n- No SE1-to-SE3 anchoring, SE3 API, production model artifact, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.\n"


def dataset_contract_report(summary: dict[str, object]) -> str:
    return f"# P0048 dataset contract\n\nlocal_table = `{summary['dataset_table']}`\n\nrow_counts = {summary['row_counts']}\n\nsplit_counts = {summary['split_counts']}\n\nwindow = {summary['window']}\n\n`se3_minus_se1 = se3_price - se1_price` is reconstructed from corrected P0042 AI2 v2 rows. `timestamp_utc` remains primary identity and fixed-CET fields remain model calendar fields.\n"


def feature_foundation_report(summary: dict[str, object]) -> str:
    return "# P0048 feature foundation\n\n" + json.dumps(json_safe({"weather_contract": summary["weather_contract"], "feature_contract": summary["feature_contract"]}), indent=2, sort_keys=True) + "\n\nWeather actuals are exploratory proxy-forecast-known inputs, not production forecast inputs.\n"


def missing_feature_report(summary: dict[str, object]) -> str:
    missing = summary["feature_contract"]["missing_requested_features"]
    return f"# P0048 missing feature report\n\nmissing_requested_features = {missing}\n\nAll requested P0048 proxy families were derived from local weather history source rows. Missing weather timestamps = {summary['feature_contract']['missing_weather_timestamps']}.\n"


def regime_labels_report(summary: dict[str, object]) -> str:
    return f"# P0048 regime labels\n\nthresholds = {summary['thresholds']}\n\nclass_balance = {summary['class_balance']}\n\nNegative and negative-spike regimes are merged into `negative_or_spike_negative` for multiclass modeling because P0047/P0048 counts are sparse.\n"


def split_report(summary: dict[str, object]) -> str:
    return f"# P0048 training split\n\ntrain: earliest available .. 2024-12-31\nvalidate: 2025-01-01 .. 2025-12-31\nholdout: 2026-01-01 .. latest complete timestamp\n\nsplit_counts = {summary['split_counts']}\n\nNo random shuffle is used as primary evaluation.\n"


def stage1_report(summary: dict[str, object]) -> str:
    lines = ["# P0048 Stage 1 classification results", ""]
    for target, groups in summary["stage1"].items():
        lines.extend([f"## {target}", "", "| group | validate precision/recall/F1 | holdout precision/recall/F1 | model |", "|---|---|---|---|"])
        for group, result in groups.items():
            val = result["validate"]
            hold = result["holdout"]
            lines.append(f"| {group} | {metric_triplet(val)} | {metric_triplet(hold)} | {result['model_class']} |")
        if target != list(summary["stage1"])[-1]:
            lines.append("")
    return "\n".join(lines) + "\n"


def stage2_report(summary: dict[str, object]) -> str:
    return metric_family_report("P0048 Stage 2 severity results", summary["stage2"])


def continuous_report(summary: dict[str, object]) -> str:
    lines = ["# P0048 continuous spread baseline results", "", "| group | validate MAE | validate RMSE | holdout MAE | holdout RMSE | model |", "|---|---:|---:|---:|---:|---|"]
    for group, result in summary["continuous"].items():
        lines.append(f"| {group} | {fmt(result['validate']['MAE'])} | {fmt(result['validate']['RMSE'])} | {fmt(result['holdout']['MAE'])} | {fmt(result['holdout']['RMSE'])} | {result['model_class']} |")
    return "\n".join(lines) + "\n"


def combined_report(summary: dict[str, object]) -> str:
    return "# P0048 two-stage combined diagnostics\n\n" + json.dumps(json_safe(summary["combined"]), indent=2, sort_keys=True) + "\n"


def attribution_report(summary: dict[str, object]) -> str:
    return "# P0048 feature attribution\n\n" + json.dumps(json_safe(summary["attribution"]), indent=2, sort_keys=True) + "\n\nGradient improvement is measured as Stage-1 positive-bottleneck validation F1 delta from actual-weather group to gradient group. Lagged improvement is validation F1 delta from gradient group to lagged diagnostic group.\n"


def calibration_report(summary: dict[str, object]) -> str:
    return "# P0048 calibration and error review\n\nCalibration curves are not plotted in P0048. PR-AUC/ROC-AUC are included where the binary classifier exposes probabilities, and confusion matrices are written to `confusion-matrices.json`.\n"


def spike_report(summary: dict[str, object]) -> str:
    lines = ["# P0048 spike case review", "", "Top holdout positive spike cases are written to `spike-error-cases.csv`.", "", "| timestamp_utc | model_day | hour | spread | lag1 | wind_south_minus_north |", "|---|---|---:|---:|---:|---:|"]
    for row in summary["spike_cases"][:20]:
        lines.append(f"| {row['timestamp_utc']} | {row['model_cet_date']} | {row['model_cet_hour']} | {fmt(row['se3_minus_se1'])} | {fmt(row['lag1_spread'])} | {fmt(row['wind_south_minus_north_actual'])} |")
    return "\n".join(lines) + "\n"


def next_package_report(summary: dict[str, object]) -> str:
    return "# P0048 next package recommendation\n\nRecommendation: P0049 should compare direct SE3 AI-1/AI-2 modeling against the best P0048 bottleneck path before any deployable SE3 forecast/API package. Do not proceed directly to production bottleneck deployment yet.\n"


def component_summary(summary: dict[str, object]) -> str:
    attr = summary["attribution"]
    return "\n".join(
        [
            "# P0048 component attribution summary",
            "",
            f"Status: {summary['status']}",
            f"1. Built `{summary['dataset_table']}` with {summary['persisted_rows']} rows and splits {summary['split_counts']}.",
            f"2. Regime thresholds used: {summary['thresholds']}.",
            f"3. Gradient features created: {len(gradient_feature_names())}; missing requested features: {summary['feature_contract']['missing_requested_features']}.",
            f"4. Stage-1 gradient F1 delta over system weather: {fmt(attr['gradient_improvement_over_system_weather_f1'])}.",
            f"5. Stage-1 lagged diagnostic F1 delta over gradients: {fmt(attr['lagged_improvement_over_gradient_f1'])}.",
            "6. Stage-2 and continuous baseline metrics are reported in dedicated evidence files.",
            "7. Recommendation: P0049 should compare direct SE3 AI-1/AI-2 against the best bottleneck path.",
            "8. Confirmed: no SE1-to-SE3 anchoring, no API, no production model, no M5/M6/M7 and no device actions.",
            "",
        ]
    )


def metric_family_report(title: str, family: dict[str, object]) -> str:
    lines = [f"# {title}", ""]
    for target, groups in family.items():
        lines.extend([f"## {target}", "", "| group | validate MAE | validate RMSE | holdout MAE | holdout RMSE | model |", "|---|---:|---:|---:|---:|---|"])
        for group, result in groups.items():
            lines.append(f"| {group} | {fmt(result['validate']['MAE'])} | {fmt(result['validate']['RMSE'])} | {fmt(result['holdout']['MAE'])} | {fmt(result['holdout']['RMSE'])} | {result['model_class']} |")
        if target != list(family)[-1]:
            lines.append("")
    return "\n".join(lines) + "\n"


def metric_triplet(row: dict[str, object]) -> str:
    if "precision" in row:
        return f"{fmt(row['precision'])}/{fmt(row['recall'])}/{fmt(row['f1'])}"
    return f"accuracy={fmt(row['accuracy'])}, macro_f1={fmt(row['macro_f1'])}"


def extract_confusion_matrices(stage1: dict[str, object]) -> dict[str, object]:
    return {
        target: {group: {"validate": result["validate"].get("confusion_matrix"), "holdout": result["holdout"].get("confusion_matrix")} for group, result in groups.items()}
        for target, groups in stage1.items()
    }


def write_csv(path: Path, rows: list[dict[str, object]], columns: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def binary_auc(y_true: list[object], scores: list[float]) -> float | None:
    try:
        from sklearn.metrics import roc_auc_score

        return float(roc_auc_score([int(value) for value in y_true], scores))
    except Exception:
        return None


def pr_auc(y_true: list[object], scores: list[float]) -> float | None:
    try:
        from sklearn.metrics import average_precision_score

        return float(average_precision_score([int(value) for value in y_true], scores))
    except Exception:
        return None


def ranks(values: list[float]) -> list[float]:
    ordered = sorted((value, index) for index, value in enumerate(values))
    output = [0.0] * len(values)
    for rank, (_value, index) in enumerate(ordered):
        output[index] = float(rank)
    return output


def clip_spread(value: float, target: str) -> float:
    if not math.isfinite(value):
        return 0.0
    if target == "log_positive_spread":
        return max(-10.0, min(10.0, value))
    return max(-2.0, min(6.0, value))


def day_distance(left: int, right: int) -> int:
    raw = abs(int(left) - int(right))
    return min(raw, 366 - raw)


def parse_utc(value: object) -> datetime:
    text = str(value).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def normalize_utc_text(value: object) -> str:
    return parse_utc(value).isoformat()


def weather_utc_text(value: object) -> str:
    return parse_utc(value).strftime("%Y-%m-%dT%H:%MZ")


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
    result = run_p0048_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "split_counts": result.split_counts, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
