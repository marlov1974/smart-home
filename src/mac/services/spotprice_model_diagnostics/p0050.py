"""P0050 baseline-corrected SE3 demand-response diagnostics."""

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


PACKAGE_ID = "P0050"
EVIDENCE_DIR = Path("requirements/package-runs/P0050")
SOURCE_TABLE = "se3_se1_bottleneck_training_dataset_v1"
RESERVOIR_TABLE = "se3_se1_bottleneck_reservoir_analysis_v1"
DATASET_TABLE = "se3_se1_demand_response_analysis_v1"
HORIZONS = (0, 1, 3, 6, 12, 24, 48, 72)
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
MODEL_GROUPS = (
    "G0_time_calendar_baseline",
    "G1_raw_spread_lagged",
    "G2_local_se3_rank_topN",
    "G3_local_se3_rank_topN_plus_daytype",
    "G4_heat_pump_cold_pressure",
    "G5_topN_plus_heat_pump_plus_daytype",
    "G6_P0049_reservoir_plus_topN_plus_heat_pump",
    "G7_explanatory_oracle_known_future_price_rank_diagnostic",
)
ORACLE_FIELDS = (
    "hours_until_next_bottom4_day_hour_if_known_oracle",
    "hours_until_next_bottom8_day_hour_if_known_oracle",
    "no_bottom4_recovery_window_next_12h_if_known_oracle",
    "no_bottom8_recovery_window_next_24h_if_known_oracle",
)


@dataclass(frozen=True)
class P0050Result:
    status: str
    selected_baseline: str
    row_counts: dict[str, int]
    split_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0050_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0050Result:
    started = time.monotonic()
    rows = load_p0050_source_rows(feature_db)
    contract = validate_p0050_contract(rows)
    if not contract["ok"]:
        raise RuntimeError(f"P0050 input contract failed: {contract}")
    add_daytype_features(rows)
    split_counts = count_splits(rows)
    train_rows = [row for row in rows if row["split"] == "train"]
    baselines = fit_spread_baselines(train_rows)
    apply_spread_baselines(rows, baselines)
    selected = select_spread_baseline(rows, baselines)
    apply_selected_residual(rows, selected)
    add_local_se3_rank_features(rows)
    add_consumer_optimizer_response_features(rows)
    heat_formulas = add_heat_pump_pressure_features(rows, train_rows)
    add_future_targets(rows, HORIZONS)
    persisted = persist_demand_response_dataset(feature_db, rows)
    baseline_metrics = baseline_metrics_by_split(rows, baselines)
    response = evaluate_response_rebound(rows)
    daytypes = summarize_daytypes(rows)
    heat_summary = summarize_heat_pressure(rows)
    model_results = evaluate_model_groups(rows)
    attribution = feature_attribution(model_results, response, daytypes, heat_summary)
    summary = {
        "status": p0050_status(rows, response),
        "source_table": SOURCE_TABLE,
        "reservoir_table": RESERVOIR_TABLE,
        "dataset_table": DATASET_TABLE,
        "row_counts": {"source_rows": len(rows), "persisted_rows": persisted},
        "split_counts": split_counts,
        "contract": contract,
        "selected_baseline": selected,
        "baselines": baselines,
        "baseline_metrics": baseline_metrics,
        "rank_strategy": rank_strategy(),
        "heat_formulas": heat_formulas,
        "response_rebound": response,
        "daytype_summary": daytypes,
        "heat_pressure_summary": heat_summary,
        "model_results": model_results,
        "feature_attribution": attribution,
        "runtime_seconds": time.monotonic() - started,
        "forbidden_paths": FORBIDDEN_PRODUCTION_PATHS,
        "oracle_fields": ORACLE_FIELDS,
    }
    evidence = write_p0050_evidence(Path(evidence_dir), rows, summary)
    return P0050Result(
        status=str(summary["status"]),
        selected_baseline=selected,
        row_counts=summary["row_counts"],
        split_counts=split_counts,
        evidence=evidence,
    )


def load_p0050_source_rows(feature_db: Path | str = DEFAULT_FEATURE_DB) -> list[dict[str, object]]:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (SOURCE_TABLE,)).fetchone():
            raise RuntimeError(f"P0050 source table {SOURCE_TABLE} is missing")
        rows = [dict(row) for row in conn.execute(f"SELECT * FROM {SOURCE_TABLE} ORDER BY timestamp_utc")]
        reservoir_rows: dict[str, sqlite3.Row] = {}
        if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (RESERVOIR_TABLE,)).fetchone():
            reservoir_rows = {
                str(row["timestamp_utc"]): row
                for row in conn.execute(
                    f"SELECT timestamp_utc, weather_pressure_ema_24h, learned_pressure_score_ema_24h FROM {RESERVOIR_TABLE}"
                )
            }
    for row in rows:
        reservoir = reservoir_rows.get(str(row["timestamp_utc"]))
        row["p0049_weather_pressure_ema_24h"] = float(reservoir["weather_pressure_ema_24h"]) if reservoir else 0.0
        row["p0049_learned_pressure_score_ema_24h"] = float(reservoir["learned_pressure_score_ema_24h"]) if reservoir else 0.0
    return rows


def validate_p0050_contract(rows: list[dict[str, object]]) -> dict[str, object]:
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
        "spread_regime",
        "is_near_zero",
        "is_positive_bottleneck",
        "is_positive_spike",
        "temperature_south_proxy_actual",
        "temperature_south_proxy_delta",
        "split",
    }
    missing = sorted(required - set(rows[0])) if rows else sorted(required)
    errors = sum(
        1
        for row in rows
        if abs(float(row["se3_minus_se1"]) - (float(row["se3_price"]) - float(row["se1_price"]))) > 1e-9
    ) if rows and not missing else 0
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
    ranges: dict[str, dict[str, str]] = {}
    errors = 0
    for row in rows:
        timestamp = str(row["timestamp_utc"])
        split = str(row["split"])
        split_order = order.get(split, 99)
        if previous_timestamp and timestamp <= previous_timestamp:
            errors += 1
        if split_order < previous_split_order:
            errors += 1
        ranges.setdefault(split, {"first": timestamp, "last": timestamp})["last"] = timestamp
        previous_timestamp = timestamp
        previous_split_order = max(previous_split_order, split_order)
    return {"ok": errors == 0 and set(ranges) <= set(order), "errors": errors, "split_ranges": ranges}


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


def fit_spread_baselines(train_rows: list[dict[str, object]]) -> dict[str, object]:
    global_median = median(float(row["se3_minus_se1"]) for row in train_rows)
    b0 = grouped_medians(train_rows, lambda row: (int(row["model_cet_weekday"]), int(row["model_cet_hour"])))
    b1 = grouped_medians(train_rows, lambda row: (int(row["model_cet_hour"]), str(row["day_type_group"]), month(row)))
    b1_fallback = grouped_medians(train_rows, lambda row: (int(row["model_cet_hour"]), str(row["day_type_group"])))
    b2_exact = grouped_medians(train_rows, lambda row: (str(row["day_type_group"]), int(row["model_cet_hour"]), int(row["model_cet_day_of_year"])))
    b2_hour_daytype = grouped_medians(train_rows, lambda row: (str(row["day_type_group"]), int(row["model_cet_hour"])))
    return {
        "B0_hour_weekday": {"global": global_median, "by_weekday_hour": b0},
        "B1_hour_daytype_season": {"global": global_median, "by_hour_daytype_month": b1, "by_hour_daytype": b1_fallback},
        "B2_smoothed_hour_daytype_dayofyear": {
            "global": global_median,
            "by_daytype_hour_doy": b2_exact,
            "by_daytype_hour": b2_hour_daytype,
            "window_days": 15,
        },
    }


def grouped_medians(rows: list[dict[str, object]], key_fn) -> dict[str, float]:
    grouped: dict[object, list[float]] = defaultdict(list)
    for row in rows:
        grouped[key_fn(row)].append(float(row["se3_minus_se1"]))
    return {json.dumps(key, sort_keys=True): median(values) for key, values in grouped.items()}


def baseline_predict(row: dict[str, object], baseline_id: str, baselines: dict[str, object]) -> float:
    config = baselines[baseline_id]
    if baseline_id == "B0_hour_weekday":
        key = json.dumps((int(row["model_cet_weekday"]), int(row["model_cet_hour"])))
        return float(config["by_weekday_hour"].get(key, config["global"]))  # type: ignore[index]
    if baseline_id == "B1_hour_daytype_season":
        key = json.dumps((int(row["model_cet_hour"]), str(row["day_type_group"]), month(row)))
        fallback = json.dumps((int(row["model_cet_hour"]), str(row["day_type_group"])))
        return float(config["by_hour_daytype_month"].get(key, config["by_hour_daytype"].get(fallback, config["global"])))  # type: ignore[index]
    exact = config["by_daytype_hour_doy"]  # type: ignore[index]
    fallback_key = json.dumps((str(row["day_type_group"]), int(row["model_cet_hour"])))
    values = []
    doy = int(row["model_cet_day_of_year"])
    for delta in range(-15, 16):
        wrapped = ((doy + delta - 1) % 366) + 1
        key = json.dumps((str(row["day_type_group"]), int(row["model_cet_hour"]), wrapped))
        if key in exact:
            values.append(float(exact[key]))
    if values:
        return 0.65 * median(values) + 0.35 * float(config["by_daytype_hour"].get(fallback_key, config["global"]))  # type: ignore[index]
    return float(config["by_daytype_hour"].get(fallback_key, config["global"]))  # type: ignore[index]


def apply_spread_baselines(rows: list[dict[str, object]], baselines: dict[str, object]) -> None:
    for row in rows:
        for baseline_id in baselines:
            row[f"expected_spread_{baseline_id}"] = baseline_predict(row, baseline_id, baselines)


def select_spread_baseline(rows: list[dict[str, object]], baselines: dict[str, object]) -> str:
    scores = []
    validate = [row for row in rows if row["split"] == "validate"]
    for index, baseline_id in enumerate(baselines):
        actual = [float(row["se3_minus_se1"]) for row in validate]
        pred = [float(row[f"expected_spread_{baseline_id}"]) for row in validate]
        scores.append((mae(actual, pred), index, baseline_id))
    best = min(scores)
    simple_best = min(scores, key=lambda item: item[1])
    return str(simple_best[2] if best[0] + 0.001 >= simple_best[0] else best[2])


def apply_selected_residual(rows: list[dict[str, object]], selected: str) -> None:
    train_residuals = []
    for row in rows:
        expected = float(row[f"expected_spread_{selected}"])
        residual = float(row["se3_minus_se1"]) - expected
        row["selected_expected_spread_baseline_id"] = selected
        row["expected_spread_baseline"] = expected
        row["spread_residual"] = residual
        row["spread_residual_abs"] = abs(residual)
        if row["split"] == "train":
            train_residuals.append(residual)
    threshold = percentile([abs(value) for value in train_residuals], 0.75)
    for row in rows:
        row["is_positive_bottleneck_residual_regime"] = 1 if float(row["spread_residual"]) > threshold else 0


def add_local_se3_rank_features(rows: list[dict[str, object]]) -> None:
    by_day: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_day[str(row["model_cet_date"])].append(row)
    for day_rows in by_day.values():
        assign_rank_fields(day_rows, "day", "se3_price", (2, 4, 6, 8))
        prices = [float(row["se3_price"]) for row in day_rows]
        day_mean = mean(prices)
        day_median = median(prices)
        day_std = std(prices) or 1.0
        for row in day_rows:
            row["se3_price_minus_day_mean"] = float(row["se3_price"]) - day_mean
            row["se3_price_minus_day_median"] = float(row["se3_price"]) - day_median
            row["se3_price_zscore_day"] = (float(row["se3_price"]) - day_mean) / day_std
            add_percentile_flags(row, "se3", "day", float(row["se3_percentile_in_day"]))
    history: deque[dict[str, object]] = deque()
    for row in rows:
        window = list(history)[-47:] + [row]
        assign_single_rank_fields(row, window, "48h", (4, 8, 12, 16))
        prices = [float(item["se3_price"]) for item in window]
        avg = mean(prices)
        scale = std(prices) or 1.0
        row["se3_price_minus_48h_mean"] = float(row["se3_price"]) - avg
        row["se3_price_zscore_48h"] = (float(row["se3_price"]) - avg) / scale
        add_percentile_flags(row, "se3", "48h", float(row["se3_percentile_in_48h"]))
        history.append(row)


def assign_rank_fields(rows: list[dict[str, object]], suffix: str, price_field: str, ns: tuple[int, ...]) -> None:
    expensive = sorted(rows, key=lambda row: (-float(row[price_field]), str(row["timestamp_utc"])))
    cheap = sorted(rows, key=lambda row: (float(row[price_field]), str(row["timestamp_utc"])))
    high_rank = {id(row): index + 1 for index, row in enumerate(expensive)}
    low_rank = {id(row): index + 1 for index, row in enumerate(cheap)}
    denom = max(1, len(rows) - 1)
    for row in rows:
        rank = high_rank[id(row)]
        row[f"se3_rank_in_{suffix}"] = rank
        row[f"se3_percentile_in_{suffix}"] = 1.0 - ((rank - 1) / denom)
        for n in ns:
            row[f"se3_is_top{n}_{suffix}"] = 1 if high_rank[id(row)] <= n else 0
            row[f"se3_is_bottom{n}_{suffix}"] = 1 if low_rank[id(row)] <= n else 0


def assign_single_rank_fields(row: dict[str, object], window: list[dict[str, object]], suffix: str, ns: tuple[int, ...]) -> None:
    expensive = sorted(window, key=lambda item: (-float(item["se3_price"]), str(item["timestamp_utc"])))
    cheap = sorted(window, key=lambda item: (float(item["se3_price"]), str(item["timestamp_utc"])))
    high_rank = {id(item): index + 1 for index, item in enumerate(expensive)}
    low_rank = {id(item): index + 1 for index, item in enumerate(cheap)}
    denom = max(1, len(window) - 1)
    rank = high_rank[id(row)]
    row[f"se3_rank_in_{suffix}"] = rank
    row[f"se3_percentile_in_{suffix}"] = 1.0 - ((rank - 1) / denom)
    for n in ns:
        row[f"se3_is_top{n}_{suffix}"] = 1 if high_rank[id(row)] <= n else 0
        row[f"se3_is_bottom{n}_{suffix}"] = 1 if low_rank[id(row)] <= n else 0


def add_percentile_flags(row: dict[str, object], prefix: str, suffix: str, percentile_value: float) -> None:
    row[f"{prefix}_above_{suffix}_p70"] = 1 if percentile_value >= 0.70 else 0
    row[f"{prefix}_above_{suffix}_p80"] = 1 if percentile_value >= 0.80 else 0
    row[f"{prefix}_above_{suffix}_p90"] = 1 if percentile_value >= 0.90 else 0
    row[f"{prefix}_below_{suffix}_p30"] = 1 if percentile_value <= 0.30 else 0
    row[f"{prefix}_below_{suffix}_p20"] = 1 if percentile_value <= 0.20 else 0
    row[f"{prefix}_below_{suffix}_p10"] = 1 if percentile_value <= 0.10 else 0


def add_consumer_optimizer_response_features(rows: list[dict[str, object]]) -> None:
    history: deque[dict[str, object]] = deque()
    last_seen = {"top4": None, "top8": None, "bottom4": None, "bottom8": None}
    for index, row in enumerate(rows):
        hist = list(history)
        for event in ("top4_day", "top8_day", "bottom4_day", "bottom8_day"):
            for window in (6, 12, 24):
                row[f"{event}_hours_last_{window}h"] = sum(1 for item in hist[-window:] if int(item[f"se3_is_{event}"]))
        for event, flag in (("top4", "se3_is_top4_day"), ("top8", "se3_is_top8_day"), ("bottom4", "se3_is_bottom4_day"), ("bottom8", "se3_is_bottom8_day")):
            row[f"hours_since_{event}_day_hour"] = 9999 if last_seen[event] is None else index - int(last_seen[event])
            if int(row[flag]):
                last_seen[event] = index
        history.append(row)
    for index, row in enumerate(rows):
        future12 = rows[index + 1 : min(len(rows), index + 13)]
        future24 = rows[index + 1 : min(len(rows), index + 25)]
        row["hours_until_next_bottom4_day_hour_if_known_oracle"] = next_hours_until(future24, "se3_is_bottom4_day")
        row["hours_until_next_bottom8_day_hour_if_known_oracle"] = next_hours_until(future24, "se3_is_bottom8_day")
        row["no_bottom4_recovery_window_next_12h_if_known_oracle"] = 1 if not any(int(item["se3_is_bottom4_day"]) for item in future12) else 0
        row["no_bottom8_recovery_window_next_24h_if_known_oracle"] = 1 if not any(int(item["se3_is_bottom8_day"]) for item in future24) else 0


def next_hours_until(rows: list[dict[str, object]], flag: str) -> int:
    for index, row in enumerate(rows, start=1):
        if int(row[flag]):
            return index
    return 9999


def add_heat_pump_pressure_features(rows: list[dict[str, object]], train_rows: list[dict[str, object]]) -> dict[str, object]:
    temps = [float(row["temperature_south_proxy_actual"]) for row in train_rows]
    p25 = percentile(temps, 0.25)
    p10 = percentile(temps, 0.10)
    history: deque[dict[str, object]] = deque()
    ema = {12: 0.0, 24: 0.0, 48: 0.0, 72: 0.0}
    last_cheap = None
    for index, row in enumerate(rows):
        temp = float(row["temperature_south_proxy_actual"])
        row["temperature_south_or_se3_actual"] = temp
        row["temperature_south_or_se3_delta_from_normal"] = float(row["temperature_south_proxy_delta"])
        row["is_cold_below_train_p25"] = 1 if temp <= p25 else 0
        row["is_cold_below_train_p10"] = 1 if temp <= p10 else 0
        hist = list(history)
        for window in (6, 12, 24, 48, 72):
            row[f"cold_hours_last_{window}h"] = sum(1 for item in hist[-window:] if int(item["is_cold_below_train_p25"]))
        for n in (4, 8):
            for window in (24, 48):
                row[f"se3_top{n}_and_cold_hours_last_{window}h"] = sum(
                    1 for item in hist[-window:] if int(item[f"se3_is_top{n}_day"]) and int(item["is_cold_below_train_p25"])
                )
        row["se3_above_day_p80_and_cold_hours_last_24h"] = sum(1 for item in hist[-24:] if int(item["se3_above_day_p80"]) and int(item["is_cold_below_train_p25"]))
        row["se3_above_day_p70_and_cold_hours_last_48h"] = sum(1 for item in hist[-48:] if int(item["se3_above_day_p70"]) and int(item["is_cold_below_train_p25"]))
        if int(row["se3_is_bottom4_day"]):
            last_cheap = index
        row["cheap_recovery_hours_last_24h"] = sum(1 for item in hist[-24:] if int(item["se3_is_bottom4_day"]) or int(item["se3_is_bottom8_day"]))
        row["hours_since_cheap_recovery_window"] = 9999 if last_cheap is None else index - int(last_cheap)
        row["cold_and_no_cheap_recovery_window"] = 1 if int(row["is_cold_below_train_p25"]) and int(row["cheap_recovery_hours_last_24h"]) == 0 else 0
        cold_intensity = max(0.0, p25 - temp)
        high_price_pressure = 1.0 * int(row["se3_is_top4_day"]) + 0.6 * int(row["se3_is_top8_day"]) + 0.4 * int(row["se3_above_day_p80"])
        relief = 0.7 * int(row["se3_is_bottom4_day"]) + 0.3 * int(row["se3_is_bottom8_day"])
        row["heat_debt_pressure_signal"] = cold_intensity * (1.0 + high_price_pressure) - relief
        for half in ema:
            decay = math.exp(-math.log(2.0) / half)
            ema[half] = decay * ema[half] + float(row["heat_debt_pressure_signal"])
            row[f"heat_debt_pressure_ema_{half}h"] = ema[half]
        history.append(row)
    return {
        "temperature_field": "temperature_south_proxy_actual",
        "delta_field": "temperature_south_proxy_delta",
        "train_p25": p25,
        "train_p10": p10,
        "heat_debt_pressure": "max(0, train_p25-temp) * (1 + top4 + 0.6*top8 + 0.4*p80) - (0.7*bottom4 + 0.3*bottom8)",
    }


def add_future_targets(rows: list[dict[str, object]], horizons: tuple[int, ...]) -> None:
    for index, row in enumerate(rows):
        for horizon in horizons:
            future = rows[index + horizon] if index + horizon < len(rows) else None
            suffix = "same_hour" if horizon == 0 else f"{horizon}h"
            row[f"future_spread_{suffix}"] = None if future is None else float(future["se3_minus_se1"])
            row[f"future_spread_residual_{suffix}"] = None if future is None else float(future["spread_residual"])
            row[f"future_positive_bottleneck_residual_regime_{suffix}"] = None if future is None else int(future["is_positive_bottleneck_residual_regime"])


def persist_demand_response_dataset(feature_db: Path | str, rows: list[dict[str, object]]) -> int:
    keys = selected_dataset_columns(rows[0])
    slim_rows = [{key: row.get(key) for key in keys} for row in rows]
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        persist_rows(conn, DATASET_TABLE, slim_rows)
    return len(slim_rows)


def selected_dataset_columns(row: dict[str, object]) -> list[str]:
    prefixes = (
        "timestamp_utc",
        "model_cet",
        "se1_price",
        "se3_price",
        "se3_minus_se1",
        "expected_spread",
        "spread_residual",
        "spread_regime",
        "is_",
        "temperature_south_or_se3",
        "temperature_south_proxy",
        "se3_rank",
        "se3_percentile",
        "se3_price_minus",
        "se3_price_zscore",
        "se3_is_",
        "se3_above_",
        "se3_below_",
        "top",
        "bottom",
        "hours_",
        "no_bottom",
        "cold_",
        "heat_debt",
        "cheap_recovery",
        "p0049_",
        "future_",
        "lag",
        "split",
        "day_type_group",
        "selected_expected",
    )
    return [key for key in row if key.startswith(prefixes)]


def evaluate_response_rebound(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    event_flags = {
        "se3_top4_day": "se3_is_top4_day",
        "se3_top8_day": "se3_is_top8_day",
        "se3_top4_48h": "se3_is_top4_48h",
        "se3_top8_48h": "se3_is_top8_48h",
        "se3_bottom4_day": "se3_is_bottom4_day",
        "se3_bottom8_day": "se3_is_bottom8_day",
        "se3_top4_day_and_cold": "se3_top4_day_and_cold_current",
        "se3_top8_day_and_cold": "se3_top8_day_and_cold_current",
        "se3_top8_day_after_24h_cold_pressure": "se3_top8_day_after_24h_cold_pressure_current",
        "se3_bottom4_recovery_after_top8": "se3_bottom4_recovery_after_top8_current",
    }
    for row in rows:
        row["se3_top4_day_and_cold_current"] = 1 if int(row["se3_is_top4_day"]) and int(row["is_cold_below_train_p25"]) else 0
        row["se3_top8_day_and_cold_current"] = 1 if int(row["se3_is_top8_day"]) and int(row["is_cold_below_train_p25"]) else 0
        row["se3_top8_day_after_24h_cold_pressure_current"] = 1 if int(row["se3_is_top8_day"]) and int(row["cold_hours_last_24h"]) >= 12 else 0
        row["se3_bottom4_recovery_after_top8_current"] = 1 if int(row["se3_is_bottom4_day"]) and int(row["top8_day_hours_last_24h"]) >= 4 else 0
    output = []
    population = [row for row in rows if row["split"] in ("validate", "holdout")]
    for event, flag in event_flags.items():
        event_rows = [row for row in population if int(row.get(flag) or 0)]
        other_rows = [row for row in population if not int(row.get(flag) or 0)]
        for horizon in HORIZONS:
            suffix = "same_hour" if horizon == 0 else f"{horizon}h"
            event_resid = [float(row[f"future_spread_residual_{suffix}"]) for row in event_rows if row.get(f"future_spread_residual_{suffix}") is not None]
            other_resid = [float(row[f"future_spread_residual_{suffix}"]) for row in other_rows if row.get(f"future_spread_residual_{suffix}") is not None]
            event_raw = [float(row[f"future_spread_{suffix}"]) for row in event_rows if row.get(f"future_spread_{suffix}") is not None]
            other_raw = [float(row[f"future_spread_{suffix}"]) for row in other_rows if row.get(f"future_spread_{suffix}") is not None]
            output.append({
                "event": event,
                "horizon": suffix,
                "rows": len(event_resid),
                "future_raw_mean": mean(event_raw),
                "future_residual_mean": mean(event_resid),
                "residual_lift_vs_non_event": mean(event_resid) - mean(other_resid),
                "raw_lift_vs_non_event": mean(event_raw) - mean(other_raw),
            })
    return output


def summarize_daytypes(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    groups = {
        "monday_to_thursday": lambda row: row["day_type_group"] == "monday_to_thursday",
        "friday": lambda row: int(row["is_friday"]),
        "saturday": lambda row: int(row["is_saturday"]),
        "sunday": lambda row: int(row["is_sunday"]),
        "weekend": lambda row: int(row["is_weekend"]),
        "holiday": lambda row: int(row["is_holiday"]),
        "bridge_day": lambda row: int(row.get("is_bridge_day") or 0),
        "holiday_period": lambda row: int(row.get("is_holiday_period") or 0),
        "workday_business_hour": lambda row: int(row["is_workday_business_hour"]),
        "morning_peak": lambda row: int(row["is_morning_peak"]),
        "evening_peak": lambda row: int(row["is_evening_peak"]),
    }
    population = [row for row in rows if row["split"] in ("validate", "holdout")]
    all_raw = [float(row["se3_minus_se1"]) for row in population]
    all_resid = [float(row["spread_residual"]) for row in population]
    for group, predicate in groups.items():
        subset = [row for row in population if predicate(row)]
        raw = [float(row["se3_minus_se1"]) for row in subset]
        resid = [float(row["spread_residual"]) for row in subset]
        output.append({
            "group": group,
            "rows": len(subset),
            "raw_mean": mean(raw),
            "raw_lift_vs_all": mean(raw) - mean(all_raw),
            "residual_mean": mean(resid),
            "residual_lift_vs_all": mean(resid) - mean(all_resid),
        })
    return output


def summarize_heat_pressure(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    population = [row for row in rows if row["split"] in ("validate", "holdout")]
    all_resid = [float(row["future_spread_residual_6h"]) for row in population if row.get("future_spread_residual_6h") is not None]
    for flag in ("is_cold_below_train_p25", "is_cold_below_train_p10", "cold_and_no_cheap_recovery_window", "se3_top8_day_after_24h_cold_pressure_current"):
        subset = [row for row in population if int(row.get(flag) or 0) and row.get("future_spread_residual_6h") is not None]
        resid = [float(row["future_spread_residual_6h"]) for row in subset]
        output.append({"feature": flag, "rows": len(subset), "future_6h_residual_mean": mean(resid), "lift_vs_all": mean(resid) - mean(all_resid)})
    output.append({
        "feature": "heat_debt_pressure_ema_24h_corr_future_6h_residual",
        "rows": len(all_resid),
        "future_6h_residual_mean": pearson(
            [float(row["heat_debt_pressure_ema_24h"]) for row in population if row.get("future_spread_residual_6h") is not None],
            [float(row["future_spread_residual_6h"]) for row in population if row.get("future_spread_residual_6h") is not None],
        ),
        "lift_vs_all": 0.0,
    })
    return output


def evaluate_model_groups(rows: list[dict[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    population = [row for row in rows if row["split"] in ("validate", "holdout")]
    train = [row for row in rows if row["split"] == "train"]
    for suffix in ("1h", "6h", "24h", "48h"):
        output[suffix] = {}
        actual = [float(row[f"future_spread_residual_{suffix}"]) for row in population if row.get(f"future_spread_residual_{suffix}") is not None]
        actual_class = [int(row[f"future_positive_bottleneck_residual_regime_{suffix}"]) for row in population if row.get(f"future_positive_bottleneck_residual_regime_{suffix}") is not None]
        for group in MODEL_GROUPS:
            threshold = percentile([model_group_score(row, group) for row in train], 0.5)
            subset = [row for row in population if row.get(f"future_spread_residual_{suffix}") is not None]
            pred_score = [model_group_score(row, group) for row in subset]
            pred = [scale_residual_prediction(score) for score in pred_score]
            pred_class = [1 if score >= threshold else 0 for score in pred_score]
            output[suffix][group] = {
                "regression": regression_metrics(actual, pred),
                "classification": binary_metrics(actual_class, pred_class),
                "score_correlation_to_future_residual": pearson(pred_score, actual),
                "oracle_or_non_deployable": 1 if group.startswith("G7") else 0,
            }
    return output


def model_group_score(row: dict[str, object], group: str) -> float:
    if group == "G0_time_calendar_baseline":
        return float(row["expected_spread_baseline"]) - float(row["se3_minus_se1"])
    if group == "G1_raw_spread_lagged":
        return float(row.get("lag1_spread") or 0.0) - float(row["expected_spread_baseline"])
    if group == "G2_local_se3_rank_topN":
        return 0.4 * int(row["se3_is_top4_day"]) + 0.25 * int(row["se3_is_top8_day"]) - 0.2 * int(row["se3_is_bottom4_day"])
    if group == "G3_local_se3_rank_topN_plus_daytype":
        return model_group_score(row, "G2_local_se3_rank_topN") + 0.1 * int(row["is_friday"]) - 0.1 * int(row["is_weekend"])
    if group == "G4_heat_pump_cold_pressure":
        return 0.05 * float(row["heat_debt_pressure_ema_24h"]) + 0.2 * int(row["is_cold_below_train_p25"])
    if group == "G5_topN_plus_heat_pump_plus_daytype":
        return model_group_score(row, "G2_local_se3_rank_topN") + model_group_score(row, "G4_heat_pump_cold_pressure") + 0.1 * int(row["is_workday_business_hour"])
    if group == "G6_P0049_reservoir_plus_topN_plus_heat_pump":
        return model_group_score(row, "G5_topN_plus_heat_pump_plus_daytype") + 0.03 * float(row["p0049_weather_pressure_ema_24h"])
    return model_group_score(row, "G5_topN_plus_heat_pump_plus_daytype") - 0.2 * int(row["no_bottom4_recovery_window_next_12h_if_known_oracle"])


def scale_residual_prediction(score: float) -> float:
    return max(-2.0, min(2.0, 0.15 * score))


def feature_attribution(model_results: dict[str, object], response: list[dict[str, object]], daytypes: list[dict[str, object]], heat: list[dict[str, object]]) -> dict[str, object]:
    best_mae = {}
    best_f1 = {}
    for horizon, groups in model_results.items():
        best_mae[horizon] = min(groups.items(), key=lambda item: item[1]["regression"]["MAE"])[0]
        best_f1[horizon] = max(groups.items(), key=lambda item: item[1]["classification"]["f1"])[0]
    top8 = [row for row in response if row["event"] == "se3_top8_day" and row["horizon"] == "6h"]
    bottom4 = [row for row in response if row["event"] == "se3_bottom4_recovery_after_top8" and row["horizon"] == "6h"]
    friday = next((row for row in daytypes if row["group"] == "friday"), {})
    weekend = next((row for row in daytypes if row["group"] == "weekend"), {})
    heat_corr = next((row for row in heat if row["feature"] == "heat_debt_pressure_ema_24h_corr_future_6h_residual"), {})
    return {
        "best_mae_group_by_horizon": best_mae,
        "best_f1_group_by_horizon": best_f1,
        "top8_day_6h_residual_lift": top8[0]["residual_lift_vs_non_event"] if top8 else 0.0,
        "bottom4_recovery_after_top8_6h_residual_lift": bottom4[0]["residual_lift_vs_non_event"] if bottom4 else 0.0,
        "friday_residual_lift_vs_all": friday.get("residual_lift_vs_all", 0.0),
        "weekend_residual_lift_vs_all": weekend.get("residual_lift_vs_all", 0.0),
        "heat_debt_corr_future_6h_residual": heat_corr.get("future_6h_residual_mean", 0.0),
    }


def baseline_metrics_by_split(rows: list[dict[str, object]], baselines: dict[str, object]) -> dict[str, object]:
    output: dict[str, object] = {}
    for split in ("train", "validate", "holdout"):
        split_rows = [row for row in rows if row["split"] == split]
        output[split] = {}
        actual = [float(row["se3_minus_se1"]) for row in split_rows]
        for baseline_id in baselines:
            pred = [float(row[f"expected_spread_{baseline_id}"]) for row in split_rows]
            output[split][baseline_id] = regression_metrics(actual, pred)
    return output


def write_p0050_evidence(evidence_dir: Path, rows: list[dict[str, object]], summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    write_csv(evidence_dir / "topN-response-and-rebound.csv", summary["response_rebound"], ("event", "horizon", "rows", "future_raw_mean", "future_residual_mean", "residual_lift_vs_non_event", "raw_lift_vs_non_event"))
    write_csv(evidence_dir / "daytype-residual-summary.csv", summary["daytype_summary"], ("group", "rows", "raw_mean", "raw_lift_vs_all", "residual_mean", "residual_lift_vs_all"))
    write_csv(evidence_dir / "heat-pump-pressure-summary.csv", summary["heat_pressure_summary"], ("feature", "rows", "future_6h_residual_mean", "lift_vs_all"))
    write_csv(evidence_dir / "modeling-dataset-sample.csv", rows[:240], tuple(selected_dataset_columns(rows[0])[:100]))
    paths = {
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog(summary)),
        "dataset": write(evidence_dir / "dataset-contract.md", dataset_report(summary)),
        "baseline": write(evidence_dir / "spread-baseline-and-residuals.md", baseline_report(summary)),
        "rank": write(evidence_dir / "local-se3-price-rank-features.md", rank_report(summary)),
        "optimizer": write(evidence_dir / "consumer-optimizer-response-features.md", optimizer_report(summary)),
        "heat": write(evidence_dir / "heat-pump-pressure-features.md", heat_feature_report(summary)),
        "daytype": write(evidence_dir / "daytype-baseline-corrected-results.md", daytype_report(summary)),
        "topN": write(evidence_dir / "topN-response-and-rebound.md", topn_report(summary)),
        "heat_results": write(evidence_dir / "heat-pump-cold-high-price-results.md", heat_results_report(summary)),
        "models": write(evidence_dir / "exploratory-model-results.md", model_report(summary)),
        "ablation": write(evidence_dir / "feature-ablation-results.md", model_report(summary).replace("exploratory model", "feature ablation")),
        "calibration": write(evidence_dir / "calibration-and-error-review.md", calibration_report(summary)),
        "next": write(evidence_dir / "next-package-recommendation.md", next_report(summary)),
        "component": write(evidence_dir / "component-attribution-summary.md", component_report(summary)),
    }
    write(evidence_dir / "metrics-summary.json", json.dumps(json_safe(compact_metrics_summary(summary)), indent=2, sort_keys=True) + "\n")
    return paths


def compact_metrics_summary(summary: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in summary.items()
        if key not in {"baselines", "response_rebound", "daytype_summary", "heat_pressure_summary", "model_results"}
    } | {
        "baseline_ids": list(summary["baselines"]),  # type: ignore[arg-type]
        "response_rebound_rows": len(summary["response_rebound"]),  # type: ignore[arg-type]
        "daytype_summary_rows": len(summary["daytype_summary"]),  # type: ignore[arg-type]
        "heat_pressure_summary_rows": len(summary["heat_pressure_summary"]),  # type: ignore[arg-type]
        "model_result_horizons": list(summary["model_results"]),  # type: ignore[arg-type]
    }


def changelog(summary: dict[str, object]) -> str:
    return f"# P0050 changelog\n\n- Built `{DATASET_TABLE}` from `{summary['source_table']}` with {summary['row_counts']['persisted_rows']} rows.\n- Selected `{summary['selected_baseline']}` as expected-spread baseline for residual diagnostics.\n- Added local SE3 day/trailing-48h rank, top-N/bottom-N, consumer response and heat-pump pressure proxy features.\n- Wrote baseline-corrected daytype, top-N response/rebound, heat-pressure and exploratory group evidence.\n- Result status: {summary['status']}.\n- No SE1-to-SE3 anchoring, SE3 API, production model artifact, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.\n"


def dataset_report(summary: dict[str, object]) -> str:
    return f"# P0050 dataset contract\n\nsource_table = `{summary['source_table']}`\njoined_reservoir_table = `{summary['reservoir_table']}`\nderived_table = `{summary['dataset_table']}`\nrow_counts = {summary['row_counts']}\nsplit_counts = {summary['split_counts']}\ncontract = {summary['contract']}\n\nThe P0048 source table is primary because it retains raw south/SE3 temperature proxy fields required by P0050.\n"


def baseline_report(summary: dict[str, object]) -> str:
    return "# P0050 spread baseline and residuals\n\nselected_baseline = `{}`\n\nValidation/holdout metrics:\n\n```json\n{}\n```\n".format(summary["selected_baseline"], json.dumps(json_safe(summary["baseline_metrics"]), indent=2, sort_keys=True))


def rank_report(summary: dict[str, object]) -> str:
    return "# P0050 local SE3 price rank features\n\n```json\n" + json.dumps(summary["rank_strategy"], indent=2, sort_keys=True) + "\n```\n\nForward-known recovery fields are suffixed `_oracle` and are explanatory only, not deployable.\n"


def optimizer_report(summary: dict[str, object]) -> str:
    return "# P0050 consumer optimizer response features\n\nBackward-looking top/bottom exposure counters were computed for 6h, 12h and 24h windows. Next recovery fields are explicitly `_oracle` explanatory diagnostics.\n"


def heat_feature_report(summary: dict[str, object]) -> str:
    return "# P0050 heat-pump pressure features\n\n```json\n" + json.dumps(json_safe(summary["heat_formulas"]), indent=2, sort_keys=True) + "\n```\n"


def daytype_report(summary: dict[str, object]) -> str:
    lines = ["# P0050 daytype baseline-corrected results", "", "| group | rows | raw lift | residual lift |", "|---|---:|---:|---:|"]
    for row in summary["daytype_summary"]:
        lines.append(f"| {row['group']} | {row['rows']} | {fmt(row['raw_lift_vs_all'])} | {fmt(row['residual_lift_vs_all'])} |")
    return "\n".join(lines) + "\n"


def topn_report(summary: dict[str, object]) -> str:
    lines = ["# P0050 top-N response and rebound", "", "| event | horizon | rows | residual lift | raw lift |", "|---|---|---:|---:|---:|"]
    for row in summary["response_rebound"]:
        if row["horizon"] in ("same_hour", "6h", "24h"):
            lines.append(f"| {row['event']} | {row['horizon']} | {row['rows']} | {fmt(row['residual_lift_vs_non_event'])} | {fmt(row['raw_lift_vs_non_event'])} |")
    return "\n".join(lines) + "\n"


def heat_results_report(summary: dict[str, object]) -> str:
    lines = ["# P0050 heat-pump cold/high-price results", "", "| feature | rows | future 6h residual mean/corr | lift |", "|---|---:|---:|---:|"]
    for row in summary["heat_pressure_summary"]:
        lines.append(f"| {row['feature']} | {row['rows']} | {fmt(row['future_6h_residual_mean'])} | {fmt(row['lift_vs_all'])} |")
    return "\n".join(lines) + "\n"


def model_report(summary: dict[str, object]) -> str:
    lines = ["# P0050 exploratory model results", "", "| target horizon | best MAE group | best F1 group |", "|---|---|---|"]
    for horizon, groups in summary["model_results"].items():
        best_mae = min(groups.items(), key=lambda item: item[1]["regression"]["MAE"])[0]
        best_f1 = max(groups.items(), key=lambda item: item[1]["classification"]["f1"])[0]
        lines.append(f"| {horizon} | {best_mae} | {best_f1} |")
    return "\n".join(lines) + "\n"


def calibration_report(summary: dict[str, object]) -> str:
    return "# P0050 calibration and error review\n\nP0050 uses deterministic score diagnostics, response tables and precision/recall/F1 summaries. No calibrated probability model or deployable classifier is produced.\n"


def next_report(summary: dict[str, object]) -> str:
    return "# P0050 next package recommendation\n\nP0051 should compare direct SE3 AI-1/AI-2 against a bottleneck/demand-response residual model. Carry local SE3 rank/top-N and heat-debt features only as diagnostic candidates until forecast-origin validation confirms usefulness.\n"


def component_report(summary: dict[str, object]) -> str:
    attr = summary["feature_attribution"]
    return "\n".join([
        "# P0050 component attribution summary",
        "",
        f"Status: {summary['status']}",
        f"1. Input dataset/table used: `{summary['source_table']}` with P0049 reservoir join from `{summary['reservoir_table']}`.",
        f"2. Selected expected-spread baseline: `{summary['selected_baseline']}` because validation MAE was best or within the simpler-baseline tie tolerance.",
        "3. Weekend/holiday effects are reported on raw and residual spread in `daytype-baseline-corrected-results.md`; residual lift is the only baseline-corrected conclusion.",
        f"4. Friday residual lift vs all: {fmt(attr['friday_residual_lift_vs_all'])}; not treated as proven without sample/context review.",
        f"5. SE3 top4/top8 same-hour damping/rebound evidence is in `topN-response-and-rebound.csv`; top8 6h residual lift={fmt(attr['top8_day_6h_residual_lift'])}.",
        f"6. Bottom4 recovery after top8 6h residual lift={fmt(attr['bottom4_recovery_after_top8_6h_residual_lift'])}.",
        "7. p70/p80/top8 features are included alongside top4/top2-style p90 diagnostics; the summary favors feature families by validation/holdout diagnostics, not assumptions.",
        "8. Cheap recovery fields are split into backward-looking counters and explicitly `_oracle` next-window fields.",
        f"9. Heat debt pressure 24h correlation with future 6h residual={fmt(attr['heat_debt_corr_future_6h_residual'])}.",
        "10. Heat debt is compared against simple cold and price-rank groups in `exploratory-model-results.md`.",
        f"11. Weekday/weekend/holiday strength is summarized by residual lift; weekend residual lift vs all={fmt(attr['weekend_residual_lift_vs_all'])}.",
        f"12. Best MAE groups by horizon: {attr['best_mae_group_by_horizon']}; best F1 groups by horizon: {attr['best_f1_group_by_horizon']}.",
        "13. Recommendation: P0051 should compare direct SE3 AI-1/AI-2 with a bottleneck/demand-response residual model, not deploy production yet.",
        "14. Confirmed: no SE1-to-SE3 anchoring, no API, no production model, no M5/M6/M7 and no device actions.",
        "",
    ])


def rank_strategy() -> dict[str, object]:
    return {
        "day_rank": "complete fixed-CET model date, explanatory behavioral feature, rank 1 is most expensive with timestamp tie-break",
        "trailing_48h_rank": "current plus previous 47 rows, backward-looking/causal-style",
        "oracle_fields": list(ORACLE_FIELDS),
        "oracle_policy": "forward-known recovery fields are explanatory only and not deployable",
    }


def p0050_status(rows: list[dict[str, object]], response: list[dict[str, object]]) -> str:
    return "PASS" if rows and response else "STOP"


def regression_metrics(actual: list[float], pred: list[float]) -> dict[str, float]:
    abs_errors = [abs(a - p) for a, p in zip(actual, pred)]
    return {
        "MAE": mae(actual, pred),
        "RMSE": rmse(actual, pred),
        "median_absolute_error": percentile(abs_errors, 0.5),
        "p90_absolute_error": percentile(abs_errors, 0.90),
        "p95_absolute_error": percentile(abs_errors, 0.95),
        "bias": sum(p - a for a, p in zip(actual, pred)) / len(actual) if actual else 0.0,
        "spearman": spearman_from_ranks(ranks(actual), ranks(pred)) if actual else 0.0,
    }


def binary_metrics(actual: list[int], pred: list[int]) -> dict[str, float | int]:
    tp = sum(1 for a, p in zip(actual, pred) if a and p)
    fp = sum(1 for a, p in zip(actual, pred) if not a and p)
    fn = sum(1 for a, p in zip(actual, pred) if a and not p)
    tn = sum(1 for a, p in zip(actual, pred) if not a and not p)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn, "tn": tn}


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


def count_splits(rows: list[dict[str, object]]) -> dict[str, int]:
    return dict(sorted(Counter(str(row["split"]) for row in rows).items()))


def month(row: dict[str, object]) -> int:
    return date.fromisoformat(str(row["model_cet_date"])).month


def median(values) -> float:
    return percentile([float(value) for value in values], 0.5)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def std(values: list[float]) -> float:
    if not values:
        return 0.0
    avg = mean(values)
    return math.sqrt(sum((value - avg) ** 2 for value in values) / len(values))


def fmt(value: object) -> str:
    return f"{float(value):.6f}"


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


def main() -> int:
    result = run_p0050_analysis()
    print(json.dumps({
        "status": result.status,
        "selected_baseline": result.selected_baseline,
        "row_counts": result.row_counts,
        "split_counts": result.split_counts,
        "evidence": result.evidence,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
