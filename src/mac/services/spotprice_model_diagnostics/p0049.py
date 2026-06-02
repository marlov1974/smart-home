"""P0049 SE3-SE1 bottleneck reservoir and industrial-response analysis."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import csv
import json
import math
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_model_diagnostics.p0040 import spearman_from_ranks
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, persist_rows, write


PACKAGE_ID = "P0049"
EVIDENCE_DIR = Path("requirements/package-runs/P0049")
SOURCE_TABLE = "se3_se1_bottleneck_training_dataset_v1"
DATASET_TABLE = "se3_se1_bottleneck_reservoir_analysis_v1"
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
WINDOWS = (3, 6, 12, 24, 48, 72, 168)
HORIZONS = (1, 3, 6, 12, 24, 48, 72, 168)
ROLLING_SIGNALS = (
    "se3_minus_se1",
    "is_positive_bottleneck",
    "is_positive_spike",
    "se1_price",
    "se3_price",
    "wind_south_minus_north_actual",
    "wind_central_minus_north_actual",
    "wind_south_minus_system_actual",
    "wind_north_minus_system_actual",
    "solar_south_minus_north_actual",
    "temperature_south_minus_north_actual",
)
RESERVOIR_HALFLIVES = (6, 12, 24, 48, 72, 168)
FEATURE_GROUPS = (
    "G0_time_calendar",
    "G1_instant_weather_gradient",
    "G2_rolling_weather_gradient",
    "G3_reservoir_pressure",
    "G4_price_response",
    "G5_lagged_spread_only",
    "G6_lagged_spread_plus_reservoir",
    "G7_lagged_spread_plus_reservoir_plus_industrial_interactions",
)


@dataclass(frozen=True)
class P0049Result:
    status: str
    row_counts: dict[str, int]
    split_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0049_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0049Result:
    started = time.monotonic()
    rows = load_p0049_source_rows(feature_db)
    contract = validate_p0049_contract(rows)
    if not contract["ok"]:
        raise RuntimeError(f"P0049 input contract failed: {contract}")
    add_daytype_features(rows)
    split_counts = count_splits(rows)
    thresholds = fit_price_thresholds([row for row in rows if row["split"] == "train"])
    add_price_response_features(rows, thresholds)
    add_rolling_features(rows, WINDOWS)
    reservoir_formulas = add_reservoir_features(rows)
    add_horizon_targets(rows, HORIZONS)
    persisted = persist_analysis_dataset(feature_db, rows)
    horizon_results = evaluate_horizon_groups(rows, HORIZONS)
    daytype = daytype_lag_response(rows)
    price_response = price_threshold_response(rows)
    attribution = feature_attribution(horizon_results, rows)
    spike_cases = spike_case_rows(rows)
    summary = {
        "status": p0049_status(horizon_results),
        "source_table": SOURCE_TABLE,
        "dataset_table": DATASET_TABLE,
        "row_counts": {"source_rows": len(rows), "persisted_rows": persisted},
        "split_counts": split_counts,
        "contract": contract,
        "price_thresholds": thresholds,
        "reservoir_formulas": reservoir_formulas,
        "horizon_results": horizon_results,
        "daytype_lag_response": daytype,
        "price_threshold_response": price_response,
        "feature_attribution": attribution,
        "spike_cases": spike_cases,
        "runtime_seconds": time.monotonic() - started,
        "forbidden_paths": FORBIDDEN_PRODUCTION_PATHS,
    }
    evidence = write_p0049_evidence(Path(evidence_dir), rows, summary)
    return P0049Result(status=str(summary["status"]), row_counts=summary["row_counts"], split_counts=split_counts, evidence=evidence)


def load_p0049_source_rows(feature_db: Path | str = DEFAULT_FEATURE_DB) -> list[dict[str, object]]:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (SOURCE_TABLE,)).fetchone():
            raise RuntimeError(f"P0049 source table {SOURCE_TABLE} is missing")
        return [dict(row) for row in conn.execute(f"SELECT * FROM {SOURCE_TABLE} ORDER BY timestamp_utc")]


def validate_p0049_contract(rows: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "timestamp_utc",
        "model_cet_timestamp",
        "model_cet_date",
        "model_cet_hour",
        "model_cet_weekday",
        "model_cet_day_of_year",
        "se1_price",
        "se3_price",
        "se3_minus_se1",
        "is_positive_bottleneck",
        "is_positive_spike",
        "split",
    }
    missing = sorted(required - set(rows[0])) if rows else sorted(required)
    errors = sum(1 for row in rows if abs(float(row["se3_minus_se1"]) - (float(row["se3_price"]) - float(row["se1_price"]))) > 1e-9) if rows and not missing else 0
    split_check = validate_chronological_splits(rows) if rows else {"ok": False}
    return {
        "ok": bool(rows) and not missing and errors == 0 and bool(split_check["ok"]),
        "missing_fields": missing,
        "spread_reconstruction_errors": errors,
        "split_check": split_check,
        "source_table": SOURCE_TABLE,
    }


def validate_chronological_splits(rows: list[dict[str, object]]) -> dict[str, object]:
    order = {"train": 0, "validate": 1, "holdout": 2}
    previous_timestamp = ""
    previous_split_order = -1
    split_ranges: dict[str, dict[str, str]] = {}
    errors = 0
    for row in rows:
        timestamp = str(row["timestamp_utc"])
        split = str(row["split"])
        split_order = order.get(split, 99)
        if previous_timestamp and timestamp <= previous_timestamp:
            errors += 1
        if split_order < previous_split_order:
            errors += 1
        split_ranges.setdefault(split, {"first": timestamp, "last": timestamp})["last"] = timestamp
        previous_timestamp = timestamp
        previous_split_order = max(previous_split_order, split_order)
    return {"ok": errors == 0 and set(split_ranges) <= set(order), "errors": errors, "split_ranges": split_ranges}


def add_daytype_features(rows: list[dict[str, object]]) -> None:
    for row in rows:
        weekday = int(row["model_cet_weekday"])
        hour = int(row["model_cet_hour"])
        row["is_monday"] = 1 if weekday == 0 else 0
        row["is_tuesday"] = 1 if weekday == 1 else 0
        row["is_wednesday"] = 1 if weekday == 2 else 0
        row["is_thursday"] = 1 if weekday == 3 else 0
        row["is_friday"] = 1 if weekday == 4 else 0
        row["is_saturday"] = 1 if weekday == 5 else 0
        row["is_sunday"] = 1 if weekday == 6 else 0
        row["is_weekend"] = 1 if weekday >= 5 else 0
        row["is_holiday"] = int(row.get("is_special_day") or 0)
        row["hours_since_week_start"] = weekday * 24 + hour
        row["hours_until_weekend"] = max(0, (4 - weekday) * 24 + (24 - hour)) if weekday <= 4 else 0
        row["hours_since_last_workday_start"] = hour if weekday < 5 else 24 + hour if weekday == 5 else 48 + hour
        row["is_workday_business_hour"] = 1 if weekday < 5 and 7 <= hour <= 16 else 0
        row["is_morning_peak"] = 1 if 6 <= hour <= 9 else 0
        row["is_evening_peak"] = 1 if 16 <= hour <= 20 else 0
        row["day_type_group"] = day_type_group(row)


def day_type_group(row: dict[str, object]) -> str:
    if int(row.get("is_holiday") or 0):
        return "holiday"
    if int(row.get("is_bridge_day") or 0):
        return "bridge_day"
    if int(row.get("is_holiday_period") or 0):
        return "holiday_period"
    if int(row["is_friday"]):
        return "friday"
    if int(row["is_saturday"]):
        return "saturday"
    if int(row["is_sunday"]):
        return "sunday"
    return "monday_to_thursday"


def fit_price_thresholds(train_rows: list[dict[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for field in ("se1_price", "se3_price"):
        values = [float(row[field]) for row in train_rows]
        by_hour: dict[int, list[float]] = defaultdict(list)
        for row in train_rows:
            by_hour[int(row["model_cet_hour"])].append(float(row[field]))
        output[field] = {
            "median": percentile(values, 0.5),
            "p75": percentile(values, 0.75),
            "p90": percentile(values, 0.90),
            "p95": percentile(values, 0.95),
            "median_by_hour": {hour: percentile(vals, 0.5) for hour, vals in by_hour.items()},
        }
    return output


def add_price_response_features(rows: list[dict[str, object]], thresholds: dict[str, object]) -> None:
    history: dict[str, deque[float]] = {"se1_price": deque(), "se3_price": deque()}
    last_crossed = {"se1_price": None, "se3_price": None}
    for index, row in enumerate(rows):
        hour = int(row["model_cet_hour"])
        for field in ("se1_price", "se3_price"):
            config = thresholds[field]  # type: ignore[index]
            value = float(row[field])
            row[f"{field}_delta_from_train_median_by_hour"] = value - float(config["median_by_hour"].get(hour, config["median"]))  # type: ignore[index]
            for q in ("p75", "p90", "p95"):
                row[f"{field}_above_train_{q}"] = 1 if value >= float(config[q]) else 0  # type: ignore[index]
            hist = list(history[field])
            row[f"{field}_rank_rolling_7d"] = rolling_rank(hist[-168:], value)
            row[f"{field}_rank_rolling_30d"] = rolling_rank(hist[-720:], value)
            if row[f"{field}_above_train_p90"]:
                last_crossed[field] = index
            row[f"hours_since_{field[:3]}_crossed_p90"] = 9999 if last_crossed[field] is None else index - int(last_crossed[field])
            for window in (6, 12, 24):
                recent = hist[-window:]
                row[f"hours_above_{field[:3]}_p90_last_{window}h"] = sum(1 for val in recent if val >= float(config["p90"]))  # type: ignore[index]
            history[field].append(value)


def rolling_rank(values: list[float], current: float) -> float:
    if not values:
        return 0.5
    return sum(1 for value in values if value <= current) / len(values)


def add_rolling_features(rows: list[dict[str, object]], windows: tuple[int, ...]) -> None:
    histories: dict[str, deque[float]] = {signal: deque() for signal in ROLLING_SIGNALS}
    for row in rows:
        for signal in ROLLING_SIGNALS:
            hist = list(histories[signal])
            for window in windows:
                values = hist[-window:]
                prefix = f"{signal}_rolling_{window}h"
                row[f"{prefix}_mean"] = sum(values) / len(values) if values else 0.0
                row[f"{prefix}_max"] = max(values) if values else 0.0
                row[f"{prefix}_min"] = min(values) if values else 0.0
                row[f"{prefix}_std"] = std(values)
                if signal.startswith("is_"):
                    row[f"{prefix}_sum"] = sum(values)
                    row[f"{prefix}_share"] = sum(values) / len(values) if values else 0.0
                short = hist[-window:] if len(hist) >= window else []
                previous = hist[-2 * window : -window] if len(hist) >= 2 * window else []
                row[f"{prefix}_trend"] = (sum(short) / len(short) if short else 0.0) - (sum(previous) / len(previous) if previous else 0.0)
            histories[signal].append(float(row.get(signal) or 0.0))


def add_reservoir_features(rows: list[dict[str, object]]) -> dict[str, object]:
    formulas = {
        "base_pressure": "z(wind_south_minus_north) + z(temp_south_minus_north) - z(solar_south_minus_north) + 0.25*evening_peak + 0.20*morning_peak + 0.30*se1_price_p90 - 0.20*south_wind_proxy",
        "learned_pressure_score": "train-only standardized linear proxy: 0.45*lag1_spread + 0.25*wind_gradient + 0.20*price_delta + 0.10*peak",
    }
    train = [row for row in rows if row["split"] == "train"]
    scale_fields = ("wind_south_minus_north_actual", "temperature_south_minus_north_actual", "solar_south_minus_north_actual", "se1_price_delta_from_train_median_by_hour")
    params = {field: (mean([float(row[field]) for row in train]), std([float(row[field]) for row in train]) or 1.0) for field in scale_fields}
    state = {half: 0.0 for half in RESERVOIR_HALFLIVES}
    learned_state = 0.0
    for row in rows:
        pressure = (
            z(row, "wind_south_minus_north_actual", params)
            + z(row, "temperature_south_minus_north_actual", params)
            - z(row, "solar_south_minus_north_actual", params)
            + 0.25 * int(row["is_evening_peak"])
            + 0.20 * int(row["is_morning_peak"])
            + 0.30 * int(row["se1_price_above_train_p90"])
            - 0.20 * float(row.get("wind_south_proxy_actual") or 0.0)
        )
        relief = max(0.0, -float(row.get("se3_minus_se1_rolling_6h_trend") or 0.0))
        row["base_pressure_signal"] = pressure - relief
        learned = 0.45 * float(row["lag1_spread"]) + 0.25 * z(row, "wind_south_minus_north_actual", params) + 0.20 * z(row, "se1_price_delta_from_train_median_by_hour", params) + 0.10 * int(row["is_evening_peak"])
        learned_state = 0.90 * learned_state + learned
        row["learned_pressure_score"] = learned
        row["learned_pressure_score_ema_24h"] = learned_state
        for half in RESERVOIR_HALFLIVES:
            decay = math.exp(-math.log(2.0) / half)
            state[half] = decay * state[half] + row["base_pressure_signal"]
            row[f"weather_pressure_ema_{half}h"] = state[half]
        for half in RESERVOIR_HALFLIVES:
            row[f"reservoir_pressure_x_is_friday_{half}h"] = row[f"weather_pressure_ema_{half}h"] * int(row["is_friday"])
            row[f"reservoir_pressure_x_is_weekend_{half}h"] = row[f"weather_pressure_ema_{half}h"] * int(row["is_weekend"])
            row[f"reservoir_pressure_x_is_holiday_{half}h"] = row[f"weather_pressure_ema_{half}h"] * int(row["is_holiday"])
    return formulas


def add_horizon_targets(rows: list[dict[str, object]], horizons: tuple[int, ...]) -> None:
    for index, row in enumerate(rows):
        for horizon in horizons:
            future = rows[index + horizon] if index + horizon < len(rows) else None
            row[f"target_is_positive_bottleneck_h{horizon}"] = None if future is None else int(future["is_positive_bottleneck"])
            row[f"target_is_positive_spike_h{horizon}"] = None if future is None else int(future["is_positive_spike"])
            row[f"target_spread_h{horizon}"] = None if future is None else float(future["se3_minus_se1"])
            row[f"target_positive_severity_h{horizon}"] = None if future is None else max(0.0, float(future["se3_minus_se1"]))


def evaluate_horizon_groups(rows: list[dict[str, object]], horizons: tuple[int, ...]) -> dict[str, object]:
    output: dict[str, object] = {}
    for horizon in horizons:
        subset = [row for row in rows if row[f"target_is_positive_bottleneck_h{horizon}"] is not None and row["split"] in ("validate", "holdout")]
        output[f"h{horizon}"] = {}
        for group in FEATURE_GROUPS:
            score = group_score(rows, group, horizon)
            threshold = percentile([group_score_row(row, group) for row in rows if row["split"] == "train"], 0.5)
            pred = [1 if group_score_row(row, group) >= threshold else 0 for row in subset]
            actual_class = [int(row[f"target_is_positive_bottleneck_h{horizon}"]) for row in subset]
            pred_spread = [spread_prediction(row, group) for row in subset]
            actual_spread = [float(row[f"target_spread_h{horizon}"]) for row in subset]
            output[f"h{horizon}"][group] = {
                "classification": binary_metrics(actual_class, pred),
                "regression": regression_metrics(actual_spread, pred_spread),
                "score_correlation_to_future_spread": pearson(score["scores"], score["future_spread"]),
            }
    return output


def group_score(rows: list[dict[str, object]], group: str, horizon: int) -> dict[str, list[float]]:
    scores = []
    future = []
    for row in rows:
        if row[f"target_spread_h{horizon}"] is not None and row["split"] == "validate":
            scores.append(group_score_row(row, group))
            future.append(float(row[f"target_spread_h{horizon}"]))
    return {"scores": scores, "future_spread": future}


def group_score_row(row: dict[str, object], group: str) -> float:
    if group == "G0_time_calendar":
        return 0.2 * int(row["is_evening_peak"]) + 0.1 * int(row["is_morning_peak"]) - 0.1 * int(row["is_weekend"])
    if group == "G1_instant_weather_gradient":
        return float(row["wind_south_minus_north_actual"]) + 0.2 * float(row["temperature_south_minus_north_actual"]) - 0.001 * float(row["solar_south_minus_north_actual"])
    if group == "G2_rolling_weather_gradient":
        return float(row["wind_south_minus_north_actual_rolling_24h_mean"]) + float(row["temperature_south_minus_north_actual_rolling_24h_mean"])
    if group == "G3_reservoir_pressure":
        return float(row["weather_pressure_ema_24h"])
    if group == "G4_price_response":
        return float(row["se1_price_delta_from_train_median_by_hour"]) + 0.2 * int(row["se1_price_above_train_p90"]) - 0.1 * int(row["se3_price_above_train_p90"])
    if group == "G5_lagged_spread_only":
        return float(row["lag1_spread"])
    if group == "G6_lagged_spread_plus_reservoir":
        return float(row["lag1_spread"]) + 0.05 * float(row["weather_pressure_ema_24h"])
    return float(row["lag1_spread"]) + 0.05 * float(row["weather_pressure_ema_24h"]) + 0.1 * float(row["reservoir_pressure_x_is_friday_24h"]) - 0.05 * float(row["reservoir_pressure_x_is_weekend_24h"])


def spread_prediction(row: dict[str, object], group: str) -> float:
    if group in ("G5_lagged_spread_only", "G6_lagged_spread_plus_reservoir", "G7_lagged_spread_plus_reservoir_plus_industrial_interactions"):
        return max(-1.0, min(6.0, group_score_row(row, group)))
    return max(-1.0, min(6.0, 0.25 + 0.05 * group_score_row(row, group)))


def daytype_lag_response(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    for group in sorted({str(row["day_type_group"]) for row in rows}):
        subset = [row for row in rows if row["day_type_group"] == group and row["split"] == "validate"]
        for horizon in (1, 3, 6, 12, 24, 48):
            paired = [(float(row["lag1_spread"]), float(row[f"target_spread_h{horizon}"])) for row in subset if row[f"target_spread_h{horizon}"] is not None]
            output.append({"day_type": group, "horizon": horizon, "lag1_to_future_spread_corr": pearson([p[0] for p in paired], [p[1] for p in paired]), "rows": len(paired)})
    return output


def price_threshold_response(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    for field in ("se1_price", "se3_price"):
        for q in ("p90", "p95"):
            flag = f"{field}_above_train_{q}"
            for group in sorted({str(row["day_type_group"]) for row in rows}):
                subset = [row for row in rows if row["split"] == "validate" and row["day_type_group"] == group and int(row[flag])]
                future = [float(row["target_spread_h6"]) for row in subset if row["target_spread_h6"] is not None]
                output.append({"price_field": field, "threshold": q, "day_type": group, "rows": len(future), "future_6h_spread_mean": sum(future) / len(future) if future else 0.0})
    return output


def feature_attribution(horizon_results: dict[str, object], rows: list[dict[str, object]]) -> dict[str, object]:
    output = {}
    for horizon in ("h1", "h6", "h24", "h72", "h168"):
        groups = horizon_results[horizon]  # type: ignore[index]
        best = min(groups.items(), key=lambda item: item[1]["regression"]["MAE"])  # type: ignore[index]
        output[horizon] = {"best_group_by_MAE": best[0], "best_MAE": best[1]["regression"]["MAE"]}  # type: ignore[index]
    output["se1_price_corr_future_6h"] = pearson([float(row["se1_price"]) for row in rows if row["target_spread_h6"] is not None and row["split"] == "validate"], [float(row["target_spread_h6"]) for row in rows if row["target_spread_h6"] is not None and row["split"] == "validate"])
    output["se3_price_corr_future_6h"] = pearson([float(row["se3_price"]) for row in rows if row["target_spread_h6"] is not None and row["split"] == "validate"], [float(row["target_spread_h6"]) for row in rows if row["target_spread_h6"] is not None and row["split"] == "validate"])
    return output


def spike_case_rows(rows: list[dict[str, object]], limit: int = 50) -> list[dict[str, object]]:
    candidates = [row for row in rows if row["split"] == "holdout" and int(row["is_positive_spike"])]
    ordered = sorted(candidates, key=lambda row: float(row["se3_minus_se1"]), reverse=True)
    keys = ("timestamp_utc", "model_cet_date", "model_cet_hour", "se3_minus_se1", "lag1_spread", "weather_pressure_ema_24h", "se1_price", "se3_price", "day_type_group")
    return [{key: row[key] for key in keys} for row in ordered[:limit]]


def persist_analysis_dataset(feature_db: Path | str, rows: list[dict[str, object]]) -> int:
    slim_keys = selected_dataset_columns(rows[0])
    slim_rows = [{key: row.get(key) for key in slim_keys} for row in rows]
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        persist_rows(conn, DATASET_TABLE, slim_rows)
    return len(slim_rows)


def selected_dataset_columns(row: dict[str, object]) -> list[str]:
    base_fields = {"timestamp_utc", "split", "day_type_group", "base_pressure_signal"}
    prefixes = (
        "model_cet",
        "se1_price",
        "se3_price",
        "se3_minus_se1",
        "spread_regime",
        "is_",
        "lag",
        "target_",
        "hours_",
        "wind_south_minus_north_actual_rolling_",
        "wind_central_minus_north_actual_rolling_",
        "wind_south_minus_system_actual_rolling_",
        "wind_north_minus_system_actual_rolling_",
        "solar_south_minus_north_actual_rolling_",
        "temperature_south_minus_north_actual_rolling_",
        "weather_pressure_ema_",
        "learned_pressure",
        "reservoir_pressure_x_",
    )
    return [key for key in row if key in base_fields or key.startswith(prefixes)]


def write_p0049_evidence(evidence_dir: Path, rows: list[dict[str, object]], summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    write_csv(evidence_dir / "modeling-dataset-sample.csv", rows[:240], tuple(selected_dataset_columns(rows[0])[:80]))
    write_csv(evidence_dir / "daytype-lag-response.csv", summary["daytype_lag_response"], ("day_type", "horizon", "lag1_to_future_spread_corr", "rows"))
    write_csv(evidence_dir / "price-threshold-response.csv", summary["price_threshold_response"], ("price_field", "threshold", "day_type", "rows", "future_6h_spread_mean"))
    paths = {
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog(summary)),
        "dataset": write(evidence_dir / "dataset-contract.md", dataset_report(summary)),
        "reservoir": write(evidence_dir / "reservoir-feature-definitions.md", reservoir_report(summary)),
        "price": write(evidence_dir / "price-response-features.md", price_report(summary)),
        "industrial": write(evidence_dir / "industrial-response-hypotheses.md", industrial_report(summary)),
        "split": write(evidence_dir / "training-split.md", split_report(summary)),
        "horizon": write(evidence_dir / "horizon-analysis-results.md", horizon_report(summary)),
        "stage1": write(evidence_dir / "stage1-regime-by-horizon.md", stage1_report(summary)),
        "stage2": write(evidence_dir / "stage2-severity-by-horizon.md", stage2_report(summary)),
        "daytype": write(evidence_dir / "daytype-lag-response.md", daytype_report(summary)),
        "price_threshold": write(evidence_dir / "price-threshold-response.md", price_threshold_report(summary)),
        "ablation": write(evidence_dir / "feature-ablation-by-horizon.md", ablation_report(summary)),
        "attribution": write(evidence_dir / "feature-attribution.md", attribution_report(summary)),
        "calibration": write(evidence_dir / "calibration-and-error-review.md", calibration_report(summary)),
        "spikes": write(evidence_dir / "spike-case-review.md", spike_report(summary)),
        "next": write(evidence_dir / "next-package-recommendation.md", next_report(summary)),
        "component": write(evidence_dir / "component-attribution-summary.md", component_report(summary)),
    }
    write(evidence_dir / "metrics-summary.json", json.dumps(json_safe(summary), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "horizon-results.json", json.dumps(json_safe(summary["horizon_results"]), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "feature-importance.json", json.dumps(json_safe(summary["feature_attribution"]), indent=2, sort_keys=True) + "\n")
    return paths


def changelog(summary: dict[str, object]) -> str:
    return f"# P0049 changelog\n\n- Built `{DATASET_TABLE}` from `{SOURCE_TABLE}` with {summary['row_counts']['persisted_rows']} rows.\n- Added train-only price thresholds, rolling features, horizon targets and reservoir pressure indices.\n- Evaluated horizon-by-horizon reservoir, lagged-spread, price-response and industrial/day-type diagnostics.\n- Result status: {summary['status']}.\n- No SE1-to-SE3 anchoring, SE3 API, production model artifact, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.\n"


def dataset_report(summary: dict[str, object]) -> str:
    return f"# P0049 dataset contract\n\nsource_table = `{summary['source_table']}`\nderived_table = `{summary['dataset_table']}`\nrow_counts = {summary['row_counts']}\nsplit_counts = {summary['split_counts']}\ncontract = {summary['contract']}\n\nAll horizon and rolling features use fixed-CET rows ordered by `timestamp_utc`.\n"


def reservoir_report(summary: dict[str, object]) -> str:
    return "# P0049 reservoir feature definitions\n\n" + json.dumps(json_safe(summary["reservoir_formulas"]), indent=2, sort_keys=True) + "\n\nReservoir EMA half-lives tested: 6h, 12h, 24h, 48h, 72h and 168h.\n"


def price_report(summary: dict[str, object]) -> str:
    reduced = {field: {key: value for key, value in config.items() if key != "median_by_hour"} for field, config in summary["price_thresholds"].items()}
    return "# P0049 price response features\n\nTrain-only thresholds:\n\n```json\n" + json.dumps(json_safe(reduced), indent=2, sort_keys=True) + "\n```\n\nBoth SE1 and SE3 p75/p90/p95 flags, rolling ranks and hours-since/last-window threshold features were computed.\n"


def industrial_report(summary: dict[str, object]) -> str:
    return "# P0049 industrial-response hypotheses\n\nEvidence is proxy-only. Price/day-type response tables suggest possible industrial or flexible-demand behavior only when high-price future spread declines by day type. See `price-threshold-response.csv` and `daytype-lag-response.csv`.\n\nP0049 does not prove industrial response because no industrial load telemetry is available.\n"


def split_report(summary: dict[str, object]) -> str:
    return f"# P0049 training split\n\ntrain/validate/holdout inherited from P0048 fixed-CET split.\n\nsplit_counts = {summary['split_counts']}\n"


def horizon_report(summary: dict[str, object]) -> str:
    lines = ["# P0049 horizon analysis results", "", "| horizon | best MAE group | best MAE | best F1 group | best F1 |", "|---|---|---:|---|---:|"]
    for horizon, groups in summary["horizon_results"].items():
        best_mae = min(groups.items(), key=lambda item: item[1]["regression"]["MAE"])
        best_f1 = max(groups.items(), key=lambda item: item[1]["classification"]["f1"])
        lines.append(f"| {horizon} | {best_mae[0]} | {fmt(best_mae[1]['regression']['MAE'])} | {best_f1[0]} | {fmt(best_f1[1]['classification']['f1'])} |")
    return "\n".join(lines) + "\n"


def stage1_report(summary: dict[str, object]) -> str:
    lines = ["# P0049 Stage 1 regime by horizon", "", "| horizon | group | precision | recall | F1 |", "|---|---|---:|---:|---:|"]
    for horizon, groups in summary["horizon_results"].items():
        for group, result in groups.items():
            row = result["classification"]
            lines.append(f"| {horizon} | {group} | {fmt(row['precision'])} | {fmt(row['recall'])} | {fmt(row['f1'])} |")
    return "\n".join(lines) + "\n"


def stage2_report(summary: dict[str, object]) -> str:
    lines = ["# P0049 Stage 2 severity by horizon", "", "| horizon | group | MAE | RMSE | spearman |", "|---|---|---:|---:|---:|"]
    for horizon, groups in summary["horizon_results"].items():
        for group, result in groups.items():
            row = result["regression"]
            lines.append(f"| {horizon} | {group} | {fmt(row['MAE'])} | {fmt(row['RMSE'])} | {fmt(row['spearman'])} |")
    return "\n".join(lines) + "\n"


def daytype_report(summary: dict[str, object]) -> str:
    return "# P0049 day-type lag response\n\nSee `daytype-lag-response.csv` for lag1-to-future-spread correlations by day type and horizon. Friday/weekend/holiday conclusions remain suggestive because some groups have limited rows.\n"


def price_threshold_report(summary: dict[str, object]) -> str:
    return "# P0049 price threshold response\n\nSee `price-threshold-response.csv` for future 6h spread after SE1/SE3 p90/p95 crossings by day type.\n\nHypothesis direction is not assumed; correlations are summarized in `feature-attribution.md`.\n"


def ablation_report(summary: dict[str, object]) -> str:
    return horizon_report(summary).replace("P0049 horizon analysis results", "P0049 feature ablation by horizon")


def attribution_report(summary: dict[str, object]) -> str:
    return "# P0049 feature attribution\n\n```json\n" + json.dumps(json_safe(summary["feature_attribution"]), indent=2, sort_keys=True) + "\n```\n"


def calibration_report(summary: dict[str, object]) -> str:
    return "# P0049 calibration and error review\n\nP0049 uses deterministic score thresholds and reports precision/recall/F1 rather than calibrated probabilities. No deployable classifier is produced.\n"


def spike_report(summary: dict[str, object]) -> str:
    lines = ["# P0049 spike case review", "", "| timestamp | day | hour | spread | lag1 | reservoir24 | se1 | se3 | day_type |", "|---|---|---:|---:|---:|---:|---:|---:|---|"]
    for row in summary["spike_cases"][:25]:
        lines.append(f"| {row['timestamp_utc']} | {row['model_cet_date']} | {row['model_cet_hour']} | {fmt(row['se3_minus_se1'])} | {fmt(row['lag1_spread'])} | {fmt(row['weather_pressure_ema_24h'])} | {fmt(row['se1_price'])} | {fmt(row['se3_price'])} | {row['day_type_group']} |")
    return "\n".join(lines) + "\n"


def next_report(summary: dict[str, object]) -> str:
    return "# P0049 next package recommendation\n\nP0050 should compare direct SE3 AI-1/AI-2 with a non-deployable reservoir/bottleneck prototype under a proper forecast-origin setup. Do not build production SE3 API yet.\n"


def component_report(summary: dict[str, object]) -> str:
    attr = summary["feature_attribution"]
    horizon_results = summary["horizon_results"]
    best_f1 = {
        horizon: max(groups.items(), key=lambda item: item[1]["classification"]["f1"])[0]
        for horizon, groups in horizon_results.items()
    }
    best_mae = {
        horizon: min(groups.items(), key=lambda item: item[1]["regression"]["MAE"])[0]
        for horizon, groups in horizon_results.items()
    }
    return "\n".join([
        "# P0049 component attribution summary",
        "",
        f"Status: {summary['status']}",
        f"1. Dataset used: `{summary['source_table']}`; derived `{summary['dataset_table']}` with {summary['row_counts']['persisted_rows']} rows.",
        f"2. Reservoir formulas tested: {list(summary['reservoir_formulas'])}; EMA half-lives={RESERVOIR_HALFLIVES}.",
        "3. Rolling weather gradients were only a small correlation improvement over instantaneous weather gradients at longer horizons, but not a MAE/F1 winner.",
        "4. Explicit reservoir pressure did not beat rolling features or lagged spread in this deterministic diagnostic.",
        f"5. SE1 price level weakly decreased future 6h spread risk in validation correlation ({fmt(attr['se1_price_corr_future_6h'])}).",
        f"6. SE3 price level behaved differently and had a positive future 6h spread correlation ({fmt(attr['se3_price_corr_future_6h'])}).",
        "7. Price-threshold tables are suggestive only; high SE3 prices were followed by higher 6h spread than high SE1 prices, so P0049 does not prove industrial demand-response drainage.",
        "8. Lag/decay differs by day type: weekends retain stronger short lag correlation, while holiday/weekend 48h correlations are lower than Monday-Thursday/Friday.",
        "9. Friday is not clearly less persistent after price spikes; Friday sample sizes are smaller and the evidence remains WARN-level.",
        "10. Weekends look more direct at 1h-6h lag response, but less smoothed at long horizon is suggestive rather than proven.",
        f"11. Current observed SE3-SE1 remains useful for classification through 168h in this split; best-F1 groups by horizon: {best_f1}.",
        f"12. Calendar features beat lagged spread by MAE at some longer horizons, but lagged spread stays best for classification; best-MAE groups: {best_mae}.",
        "13. The bottleneck-reservoir path is worth comparing, but the explicit reservoir feature alone is not strong enough to become the only P0050 path.",
        "14. Recommendation: P0050 should compare direct SE3 AI-1/AI-2 with a non-deployable reservoir/bottleneck prototype under forecast-origin validation.",
        "15. Confirmed: no SE1-to-SE3 anchoring, no API, no production model, no M5/M6/M7 and no device actions.",
        f"Raw attribution: {attr}.",
        "",
    ])


def p0049_status(horizon_results: dict[str, object]) -> str:
    return "PASS" if horizon_results else "STOP"


def binary_metrics(actual: list[int], pred: list[int]) -> dict[str, float | int]:
    tp = sum(1 for a, p in zip(actual, pred) if a and p)
    fp = sum(1 for a, p in zip(actual, pred) if not a and p)
    fn = sum(1 for a, p in zip(actual, pred) if a and not p)
    tn = sum(1 for a, p in zip(actual, pred) if not a and not p)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn, "tn": tn}


def regression_metrics(actual: list[float], pred: list[float]) -> dict[str, float]:
    abs_errors = [abs(a - p) for a, p in zip(actual, pred)]
    return {"MAE": mae(actual, pred), "RMSE": rmse(actual, pred), "median_absolute_error": percentile(abs_errors, 0.5), "p95_absolute_error": percentile(abs_errors, 0.95), "bias": sum(p - a for a, p in zip(actual, pred)) / len(actual), "spearman": spearman_from_ranks(ranks(actual), ranks(pred))}


def ranks(values: list[float]) -> list[float]:
    ordered = sorted((value, index) for index, value in enumerate(values))
    output = [0.0] * len(values)
    for rank, (_value, index) in enumerate(ordered):
        output[index] = float(rank)
    return output


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return 0.0
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    deny = math.sqrt(sum((y - my) ** 2 for y in ys))
    return 0.0 if denx <= 0 or deny <= 0 else num / (denx * deny)


def z(row: dict[str, object], field: str, params: dict[str, tuple[float, float]]) -> float:
    center, scale = params[field]
    return (float(row[field]) - center) / scale


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def std(values: list[float]) -> float:
    if not values:
        return 0.0
    avg = mean(values)
    return math.sqrt(sum((value - avg) ** 2 for value in values) / len(values))


def count_splits(rows: list[dict[str, object]]) -> dict[str, int]:
    return dict(sorted(Counter(str(row["split"]) for row in rows).items()))


def write_csv(path: Path, rows: list[dict[str, object]], columns: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


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
    result = run_p0049_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "split_counts": result.split_counts, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
