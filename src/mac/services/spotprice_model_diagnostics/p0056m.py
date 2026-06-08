"""P0056M LABB SE2 M6 DayAhead error slice analysis."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import csv
import json
import math
import sqlite3
import sys
import time
import warnings

import numpy as np

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0056c, p0056d, p0056k
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write


PACKAGE_ID = "P0056M"
LABEL = "LABB"
AREA = "SE2"
MODEL_ID = "M6"
EVIDENCE_DIR = Path("requirements/package-runs/P0056M")
BASELINE_EVIDENCE = Path("requirements/package-runs/P0056K/area-model-results.csv")
P0056K_SE2_M6_BASELINE_MAE = 232.69280738198043
BASELINE_TOLERANCE_MW = 0.001
TARGET = p0056k.TARGET
TEMP_FIELD = "weather_proxy_temperature_2m_area"
HDH_FIELD = "weather_proxy_heating_degree_hours_area"
SAFE_RAMP_FIELD = "safe_same_hour_delta_168_336h"
WEEKDAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


@dataclass(frozen=True)
class P0056MResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0056m_error_slice_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0056MResult:
    started = time.monotonic()
    warnings.filterwarnings("ignore", message="X does not have valid feature names.*")
    feature_path = Path(feature_db).expanduser()
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)
    initialize_progress(evidence_path)

    with sqlite3.connect(feature_path, timeout=60.0) as conn:
        conn.row_factory = sqlite3.Row
        targets_all, target_contract = p0056c.load_area_targets(conn)
        weather_all, weather_contract = load_p0056d_weather(conn)

    input_contract = input_source_contract(target_contract, weather_contract)
    if not input_contract["ok"]:
        summary = stopped_summary(started, feature_path, input_contract, [{"error": "input contract failed"}])
        return P0056MResult("STOP", summary["row_counts"], write_evidence(evidence_path, summary, [], [], {}, {}, [], []))  # type: ignore[arg-type]

    targets = targets_all[AREA]
    weather_rows = weather_all[AREA]
    origins = p0056k.dayahead_origins(targets, weather_rows, p0056k.FIRST_EVAL_DELIVERY_DAY)
    reconstruction = reconstruct_se2_m6_predictions(targets, weather_rows, origins, evidence_path)
    day_rows = reconstruction["day_rows"]
    hour_rows = reconstruction["hour_rows"]
    failures = reconstruction["failures"]
    aggregate = aggregate_day_rows(day_rows)
    baseline = baseline_review(aggregate)
    slices = build_all_slices(day_rows, hour_rows)
    best_tests, worst_tests = top_bottom_tests(day_rows)
    patterns = interpret_patterns(slices, best_tests, worst_tests, aggregate)
    decision_payload = decision(patterns, baseline, failures)
    status = decide_status(day_rows, hour_rows, baseline, failures)
    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "feature_db": str(feature_path),
        "area": AREA,
        "model_id": MODEL_ID,
        "input_contract": input_contract,
        "dayahead_protocol": p0056k.dayahead_protocol(),
        "reconstruction_contract": reconstruction_contract(),
        "leakage_review": leakage_review(),
        "p0056k_baseline_review": baseline,
        "aggregate_metrics": aggregate,
        "pattern_review": patterns,
        "decision": decision_payload,
        "next_package_recommendation": next_package_recommendation(patterns),
        "failures": failures,
        "row_counts": {
            "origins": len(origins),
            "delivery_days": len(day_rows),
            "hour_rows": len(hour_rows),
            "failures": len(failures),
        },
        "no_api": True,
        "no_devices": True,
        "no_runtime_change": True,
        "no_production_activation": True,
        "no_spot_price_features": True,
        "no_flow_exchange_a61_capacity_features": True,
        "no_old_physical_balance_target": True,
        "no_future_actual_load_features": True,
        "no_large_artifacts": True,
    }
    evidence = write_evidence(evidence_path, summary, day_rows, hour_rows, slices, patterns, best_tests, worst_tests)
    return P0056MResult(status, summary["row_counts"], evidence)  # type: ignore[arg-type]


def load_p0056d_weather(conn: sqlite3.Connection) -> tuple[dict[str, dict[str, dict[str, object]]], dict[str, object]]:
    return p0056d.load_p0056d_area_weather_rows(conn)


def reconstruct_se2_m6_predictions(
    targets: list[dict[str, object]],
    weather_rows: dict[str, dict[str, object]],
    origins: list[p0056k.Origin],
    evidence_dir: Path | None = None,
) -> dict[str, object]:
    environment = p0054k.capture_environment_status()
    specs = p0056k.model_specs_for_p0056k(environment)
    model_order = ["M1"] + [f"M{index}" for index in range(2, 6) if f"M{index}" in specs]
    modeling_origins = p0056k.dayahead_origins(targets, weather_rows, p0056k.FIRST_MODELING_DELIVERY_DAY)
    base_rows = p0056k.build_dayahead_rows(AREA, targets, weather_rows, modeling_origins)
    rows_by_origin = rows_by_origin_utc(base_rows)
    prior_model_mae: dict[str, list[float]] = defaultdict(list)
    day_rows: list[dict[str, object]] = []
    hour_rows: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    completed = 0

    for origin_index, origin in enumerate(origins, start=1):
        started = time.monotonic()
        forecast_rows = [dict(row) for row in rows_by_origin.get(origin.origin_utc, [])]
        if len(forecast_rows) != 24:
            failures.append({"origin_utc": origin.origin_utc, "delivery_day": origin.delivery_day.isoformat(), "error": f"incomplete forecast rows {len(forecast_rows)}"})
            continue
        train_rows = [dict(row) for row in base_rows if p0056k.EXPANDING_TRAIN_START_UTC <= str(row["target_timestamp_utc"]) < origin.origin_utc]
        if len(train_rows) < 1000:
            failures.append({"origin_utc": origin.origin_utc, "delivery_day": origin.delivery_day.isoformat(), "error": f"insufficient train rows {len(train_rows)}"})
            continue
        try:
            base_predictions: dict[str, list[float]] = {}
            for model_id in model_order:
                if model_id == "M1":
                    predictions, _training = p0056k.fit_predict_ridge(train_rows, forecast_rows)
                else:
                    predictions, _training = p0056k.fit_predict_spec(train_rows, forecast_rows, specs[model_id])
                base_predictions[model_id] = predictions
                base_result = p0056k.score_origin(AREA, origin, model_id, forecast_rows, predictions, {"train_rows": len(train_rows), "feature_count": len(p0056k.FEATURES), "model_family": "base_for_M6"}, 0.0)
                prior_model_mae[model_id].append(float(base_result["DayAhead_hourly_MAE"]))
            m6_predictions, m6_training = p0056k.weighted_ensemble_predictions(base_predictions, prior_model_mae, forecast_rows)
            current_hour_rows = build_hour_rows(origin, forecast_rows, m6_predictions)
            day_rows.append(build_day_metrics(origin, current_hour_rows))
            hour_rows.extend(current_hour_rows)
            completed += 1
            if evidence_dir and should_write_progress(completed, len(origins)):
                append_progress(evidence_dir, origin, origin_index, len(origins), "done", completed, {"MAE": day_rows[-1]["hourly_MAE"], "seconds": round(time.monotonic() - started, 3), "weights": m6_training.get("weights", {})})
        except Exception as exc:  # pragma: no cover - long-running evidence path
            failures.append({"origin_utc": origin.origin_utc, "delivery_day": origin.delivery_day.isoformat(), "error_type": type(exc).__name__, "error": str(exc)[:600]})
            if evidence_dir:
                append_progress(evidence_dir, origin, origin_index, len(origins), "failed", completed, {"error_type": type(exc).__name__, "error": str(exc)[:160]})
    return {"day_rows": day_rows, "hour_rows": hour_rows, "failures": failures}


def rows_by_origin_utc(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    out: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        out[str(row["forecast_origin_timestamp_utc"])].append(row)
    return out


def build_hour_rows(origin: p0056k.Origin, forecast_rows: list[dict[str, object]], predictions: list[float]) -> list[dict[str, object]]:
    rows = []
    for row, prediction in zip(forecast_rows, predictions):
        actual = float(row[TARGET])
        forecast = float(prediction)
        error = forecast - actual
        target_dt = p0052.parse_utc(str(row["target_timestamp_utc"]))
        local_dt = target_dt.astimezone(p0056k.STOCKHOLM)
        temp = value_or_none(row, TEMP_FIELD)
        hdh = value_or_none(row, HDH_FIELD)
        rows.append({
            "forecast_origin": origin.origin_utc,
            "delivery_date": origin.delivery_day.isoformat(),
            "target_timestamp": row["target_timestamp_utc"],
            "target_timestamp_utc": row["target_timestamp_utc"],
            "local_hour": local_dt.hour,
            "horizon_h": int(row["horizon_h"]),
            "actual_mw": actual,
            "forecast_mw": forecast,
            "error_mw": error,
            "absolute_error_mw": abs(error),
            "weekday": WEEKDAY_NAMES[origin.delivery_day.weekday()],
            "month": int(origin.delivery_day.month),
            "season": season_for_month(origin.delivery_day.month),
            "temperature_2m": temp,
            "heating_degree_hours": hdh,
            "ramp_24h_or_safe_proxy": value_or_none(row, SAFE_RAMP_FIELD),
            "is_holiday": int(float(row.get("is_holiday", 0.0))),
            "is_workday": int(float(row.get("is_workday", 0.0))),
            "is_weekend": int(float(row.get("is_weekend", 0.0))),
        })
    return rows


def build_day_metrics(origin: p0056k.Origin, rows: list[dict[str, object]]) -> dict[str, object]:
    actuals = [float(row["actual_mw"]) for row in rows]
    forecasts = [float(row["forecast_mw"]) for row in rows]
    errors = [float(row["error_mw"]) for row in rows]
    abs_errors = [float(row["absolute_error_mw"]) for row in rows]
    temps = [float(row["temperature_2m"]) for row in rows if row.get("temperature_2m") is not None]
    hdhs = [float(row["heating_degree_hours"]) for row in rows if row.get("heating_degree_hours") is not None]
    largest = max(rows, key=lambda row: float(row["absolute_error_mw"]))
    signed_energy = sum(errors)
    actual_energy = sum(actuals)
    mean_actual = mean(actuals)
    ramp_score = max([abs(actuals[index] - actuals[index - 1]) for index in range(1, len(actuals))] or [0.0])
    return {
        "delivery_date": origin.delivery_day.isoformat(),
        "forecast_origin": origin.origin_utc,
        "weekday": WEEKDAY_NAMES[origin.delivery_day.weekday()],
        "weekday_index": origin.delivery_day.weekday(),
        "month": origin.delivery_day.month,
        "month_name": MONTH_NAMES[origin.delivery_day.month],
        "season": season_for_month(origin.delivery_day.month),
        "half_year": half_year_for_month(origin.delivery_day.month),
        "day_type": day_type(rows),
        "mean_actual_load_mw": mean_actual,
        "mean_forecast_load_mw": mean(forecasts),
        "hourly_MAE": mean(abs_errors),
        "hourly_RMSE": math.sqrt(mean([error * error for error in errors])),
        "bias_mw": mean(errors),
        "signed_daily_energy_error_MWh": signed_energy,
        "absolute_daily_energy_error_MWh": abs(signed_energy),
        "daily_energy_error_percent": abs(signed_energy) / actual_energy * 100.0 if actual_energy else 0.0,
        "max_absolute_hourly_error_mw": max(abs_errors),
        "p90_absolute_hourly_error_mw": percentile(abs_errors, 0.9),
        "mean_temperature_2m": mean(temps) if temps else None,
        "min_temperature_2m": min(temps) if temps else None,
        "max_temperature_2m": max(temps) if temps else None,
        "heating_degree_hours_sum": sum(hdhs),
        "cold_spell_flag_any": bool(temps and min(temps) <= -10.0),
        "load_ramp_score": ramp_score,
        "temperature_bin": temperature_bin(mean(temps) if temps else None),
        "heating_degree_bin": heating_degree_bin(sum(hdhs)),
        "largest_error_hour": largest["local_hour"],
        "largest_error_mw": largest["error_mw"],
        "largest_absolute_error_mw": largest["absolute_error_mw"],
        "short_explanation_candidate": explanation_candidate(mean(temps) if temps else None, mean_actual, ramp_score, mean(errors), max(abs_errors)),
    }


def build_all_slices(day_rows: list[dict[str, object]], hour_rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    load_bins = quantile_bins(day_rows, "mean_actual_load_mw", "load")
    ramp_bins = quantile_bins(day_rows, "load_ramp_score", "ramp")
    day_enriched = []
    for row in day_rows:
        current = dict(row)
        current["load_quantile"] = load_bins[str(row["delivery_date"])]
        current["ramp_quantile"] = ramp_bins[str(row["delivery_date"])]
        day_enriched.append(current)
    return {
        "weekday": slice_summary(day_enriched, "weekday"),
        "month": slice_summary(day_enriched, "month_name"),
        "season": slice_summary(day_enriched, "season"),
        "half_year": slice_summary(day_enriched, "half_year"),
        "temperature": slice_summary(day_enriched, "temperature_bin"),
        "heating_degree": slice_summary(day_enriched, "heating_degree_bin"),
        "load": slice_summary(day_enriched, "load_quantile"),
        "ramp": slice_summary(day_enriched, "ramp_quantile"),
        "holiday_workday_weekend": slice_summary(day_enriched, "day_type"),
        "horizon_hour": hour_slice_summary(hour_rows, lambda row: horizon_bin(int(row["horizon_h"]))),
        "local_hour": hour_slice_summary(hour_rows, lambda row: f"{int(row['local_hour']):02d}"),
    }


def slice_summary(rows: list[dict[str, object]], key: str) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key, "unknown"))].append(row)
    out = []
    for name, selected in groups.items():
        out.append({
            "slice": name,
            "count": len(selected),
            "MAE": mean([float(row["hourly_MAE"]) for row in selected]),
            "bias_mw": mean([float(row["bias_mw"]) for row in selected]),
            "absolute_daily_energy_error_MWh": mean([float(row["absolute_daily_energy_error_MWh"]) for row in selected]),
            "daily_energy_error_percent": mean([float(row["daily_energy_error_percent"]) for row in selected]),
            "mean_actual_load_mw": mean([float(row["mean_actual_load_mw"]) for row in selected]),
            "mean_temperature_2m": mean([float(row["mean_temperature_2m"]) for row in selected if row.get("mean_temperature_2m") is not None]) if any(row.get("mean_temperature_2m") is not None for row in selected) else None,
        })
    return sorted(out, key=lambda row: str(row["slice"]))


def hour_slice_summary(rows: list[dict[str, object]], key_func: object) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[str(key_func(row))].append(row)  # type: ignore[operator]
    out = []
    for name, selected in groups.items():
        out.append({
            "slice": name,
            "count": len(selected),
            "MAE": mean([float(row["absolute_error_mw"]) for row in selected]),
            "bias_mw": mean([float(row["error_mw"]) for row in selected]),
            "p90_absolute_error_mw": percentile([float(row["absolute_error_mw"]) for row in selected], 0.9),
        })
    return sorted(out, key=lambda row: str(row["slice"]))


def top_bottom_tests(day_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    best = sorted(day_rows, key=lambda row: (float(row["hourly_MAE"]), float(row["absolute_daily_energy_error_MWh"])))[:5]
    worst = sorted(day_rows, key=lambda row: (float(row["hourly_MAE"]), float(row["absolute_daily_energy_error_MWh"])), reverse=True)[:5]
    return ranked_tests(best), ranked_tests(worst)


def ranked_tests(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    fields = [
        "delivery_date",
        "forecast_origin",
        "weekday",
        "month",
        "season",
        "hourly_MAE",
        "hourly_RMSE",
        "bias_mw",
        "absolute_daily_energy_error_MWh",
        "daily_energy_error_percent",
        "mean_actual_load_mw",
        "mean_forecast_load_mw",
        "mean_temperature_2m",
        "min_temperature_2m",
        "max_temperature_2m",
        "heating_degree_hours_sum",
        "cold_spell_flag_any",
        "largest_error_hour",
        "largest_error_mw",
        "short_explanation_candidate",
    ]
    out = []
    for rank, row in enumerate(rows, start=1):
        current = {"rank": rank}
        current.update({field: row.get(field) for field in fields})
        out.append(current)
    return out


def interpret_patterns(
    slices: dict[str, list[dict[str, object]]],
    best_tests: list[dict[str, object]],
    worst_tests: list[dict[str, object]],
    aggregate: dict[str, object],
) -> dict[str, object]:
    weekday_worst = extreme_slice(slices["weekday"], True)
    weekday_best = extreme_slice(slices["weekday"], False)
    month_worst = extreme_slice(slices["month"], True)
    month_best = extreme_slice(slices["month"], False)
    season_worst = extreme_slice(slices["season"], True)
    season_best = extreme_slice(slices["season"], False)
    temp_by_name = {str(row["slice"]): row for row in slices["temperature"]}
    cold_mae = combined_mae(temp_by_name, ["very_cold", "cold"])
    mild_mae = float(temp_by_name.get("mild", {}).get("MAE", 0.0) or 0.0)
    warm_mae = combined_mae(temp_by_name, ["warm", "hot"])
    half = {str(row["slice"]): row for row in slices["half_year"]}
    load_worst = extreme_slice(slices["load"], True)
    load_best = extreme_slice(slices["load"], False)
    ramp_worst = extreme_slice(slices["ramp"], True)
    ramp_best = extreme_slice(slices["ramp"], False)
    spike_ratio = float(aggregate.get("mean_max_abs_error_to_mae_ratio", 0.0))
    bias_abs = abs(float(aggregate.get("DayAhead_bias", 0.0)))
    mae = float(aggregate.get("DayAhead_hourly_MAE", 0.0))
    mode = "bias" if mae and bias_abs / mae > 0.5 else "isolated hourly spikes" if spike_ratio > 2.0 else "volatility"
    answers = {
        "1_worst_weekday": weekday_worst,
        "2_best_weekday": weekday_best,
        "3_worst_month": month_worst,
        "4_worst_season": season_worst,
        "5_cold_weather_increases_error": compare_statement(cold_mae, warm_mae, "cold", "warm/hot"),
        "6_mild_weather_increases_error": compare_statement(mild_mae, mean([cold_mae, warm_mae]), "mild", "cold/warm average"),
        "7_winter_vs_summer": compare_statement(float(half.get("winter_half", {}).get("MAE", 0.0) or 0.0), float(half.get("summer_half", {}).get("MAE", 0.0) or 0.0), "winter_half", "summer_half"),
        "8_high_load_days_worse": compare_statement(float(load_worst.get("MAE", 0.0)), float(load_best.get("MAE", 0.0)), str(load_worst.get("slice")), str(load_best.get("slice"))),
        "9_high_ramp_days_worse": compare_statement(float(ramp_worst.get("MAE", 0.0)), float(ramp_best.get("MAE", 0.0)), str(ramp_worst.get("slice")), str(ramp_best.get("slice"))),
        "10_error_mode": mode,
        "11_worst_test_patterns": common_patterns(worst_tests),
        "12_best_test_patterns": common_patterns(best_tests),
        "best_month": month_best,
        "best_season": season_best,
        "worst_load_slice": load_worst,
        "worst_ramp_slice": ramp_worst,
    }
    return answers


def aggregate_day_rows(day_rows: list[dict[str, object]]) -> dict[str, object]:
    if not day_rows:
        return {}
    return {
        "area_code": AREA,
        "model_id": MODEL_ID,
        "origin_count": len(day_rows),
        "delivery_day_count": len(day_rows),
        "DayAhead_hourly_MAE": mean([float(row["hourly_MAE"]) for row in day_rows]),
        "DayAhead_RMSE": mean([float(row["hourly_RMSE"]) for row in day_rows]),
        "DayAhead_bias": mean([float(row["bias_mw"]) for row in day_rows]),
        "absolute_daily_energy_error_MWh": mean([float(row["absolute_daily_energy_error_MWh"]) for row in day_rows]),
        "daily_energy_error_percent_of_actual": mean([float(row["daily_energy_error_percent"]) for row in day_rows]),
        "mean_max_abs_error_to_mae_ratio": mean([float(row["max_absolute_hourly_error_mw"]) / max(float(row["hourly_MAE"]), 1e-9) for row in day_rows]),
    }


def baseline_review(aggregate: dict[str, object]) -> dict[str, object]:
    evidence_row = load_p0056k_baseline_row()
    expected = float(evidence_row.get("DayAhead_hourly_MAE", P0056K_SE2_M6_BASELINE_MAE))
    reconstructed = float(aggregate.get("DayAhead_hourly_MAE", math.nan))
    delta = reconstructed - expected
    return {
        "source": str(BASELINE_EVIDENCE),
        "area": AREA,
        "model_id": MODEL_ID,
        "expected_DayAhead_hourly_MAE": expected,
        "reconstructed_DayAhead_hourly_MAE": reconstructed,
        "delta_MW": delta,
        "matches_within_tolerance": math.isfinite(delta) and abs(delta) <= BASELINE_TOLERANCE_MW,
        "origin_count_expected": int(float(evidence_row.get("origin_count", 0) or 0)),
        "origin_count_reconstructed": int(aggregate.get("origin_count", 0) or 0),
        "warning": "P0056K hour-level predictions were reconstructed, not loaded from a saved prediction dump.",
    }


def load_p0056k_baseline_row() -> dict[str, object]:
    if not BASELINE_EVIDENCE.exists():
        return {"DayAhead_hourly_MAE": P0056K_SE2_M6_BASELINE_MAE}
    with BASELINE_EVIDENCE.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("area_code") == AREA and row.get("model_id") == MODEL_ID:
                return row
    return {"DayAhead_hourly_MAE": P0056K_SE2_M6_BASELINE_MAE}


def decision(patterns: dict[str, object], baseline: dict[str, object], failures: list[dict[str, object]]) -> dict[str, object]:
    return {
        "status_basis": "PASS" if baseline.get("matches_within_tolerance") and not failures else "WARN",
        "production_ready": False,
        "baseline_matched": baseline.get("matches_within_tolerance"),
        "primary_failure_pattern": patterns.get("10_error_mode"),
        "next_package": next_package_recommendation(patterns),
    }


def next_package_recommendation(patterns: dict[str, object]) -> str:
    worst = patterns.get("1_worst_weekday", {})
    season = patterns.get("4_worst_season", {})
    return f"P0056N: targeted SE2 DayAhead feature/error fix for worst slices ({slice_name(worst)} and {slice_name(season)}) without forbidden price/flow/A61 inputs."


def decide_status(day_rows: list[dict[str, object]], hour_rows: list[dict[str, object]], baseline: dict[str, object], failures: list[dict[str, object]]) -> str:
    if not day_rows or not hour_rows:
        return "STOP"
    if len(day_rows) != int(baseline.get("origin_count_expected", len(day_rows)) or len(day_rows)):
        return "WARN"
    return "WARN" if failures or not baseline.get("matches_within_tolerance") else "PASS"


def input_source_contract(target_contract: dict[str, object], weather_contract: dict[str, object]) -> dict[str, object]:
    target_areas = target_contract.get("areas", {}) if isinstance(target_contract.get("areas"), dict) else {}
    weather_areas = weather_contract.get("areas", {}) if isinstance(weather_contract.get("areas"), dict) else {}
    return {
        "ok": AREA in target_areas and AREA in weather_areas,
        "target_source": "area_consumption_hourly_v1/P0056A",
        "weather_source": "P0056D actual-weather proxy LABB",
        "area": AREA,
    }


def reconstruction_contract() -> dict[str, object]:
    return {
        "baseline": "P0056K SE2 M6 WeightedEnsemble_no_price",
        "prediction_source": "reconstructed_from_committed_P0056K_logic",
        "base_models": "M1 plus available M2-M5 exactly as P0056K environment allows",
        "forecast_origin": "D-1 12:00 Europe/Stockholm",
        "delivery_day": "D 00:00..23:00 Europe/Stockholm",
        "train_end": "strictly before forecast_origin",
    }


def leakage_review() -> dict[str, object]:
    p0056k_review = p0056k.leakage_review()
    return {
        "ok": bool(p0056k_review.get("ok")),
        "inherits_p0056k_features": True,
        "posthoc_actuals_only_for_error_analysis": True,
        "forbidden_features": p0056k_review.get("forbidden_features", []),
        "future_actual_load_feature_used_for_prediction": False,
        "spot_price_feature_used": False,
        "flow_exchange_a61_capacity_feature_used": False,
        "old_physical_balance_target_used": False,
    }


def stopped_summary(started: float, feature_path: Path, input_contract: dict[str, object], failures: list[dict[str, object]]) -> dict[str, object]:
    return {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": "STOP",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "feature_db": str(feature_path),
        "input_contract": input_contract,
        "failures": failures,
        "row_counts": {"delivery_days": 0, "hour_rows": 0, "failures": len(failures)},
    }


def season_for_month(month: int) -> str:
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "autumn"


def half_year_for_month(month: int) -> str:
    return "winter_half" if month in (10, 11, 12, 1, 2, 3) else "summer_half"


def temperature_bin(value: float | None) -> str:
    if value is None:
        return "unknown"
    if value <= -10.0:
        return "very_cold"
    if value <= 0.0:
        return "cold"
    if value <= 10.0:
        return "mild"
    if value <= 20.0:
        return "warm"
    return "hot"


def heating_degree_bin(value: float) -> str:
    if value <= 0.0:
        return "none"
    if value <= 72.0:
        return "low"
    if value <= 168.0:
        return "medium"
    return "high"


def horizon_bin(horizon: int) -> str:
    if horizon <= 5:
        return "00-05"
    if horizon <= 11:
        return "06-11"
    if horizon <= 17:
        return "12-17"
    if horizon <= 23:
        return "18-23"
    if horizon <= 29:
        return "24-29"
    if horizon <= 35:
        return "30-35"
    return "36+"


def quantile_bins(rows: list[dict[str, object]], field: str, prefix: str) -> dict[str, str]:
    if not rows:
        return {}
    values = sorted(float(row[field]) for row in rows)
    q25 = percentile(values, 0.25)
    q50 = percentile(values, 0.50)
    q75 = percentile(values, 0.75)
    out = {}
    for row in rows:
        value = float(row[field])
        if value <= q25:
            label = f"{prefix}_q1_low"
        elif value <= q50:
            label = f"{prefix}_q2"
        elif value <= q75:
            label = f"{prefix}_q3"
        else:
            label = f"{prefix}_q4_high"
        out[str(row["delivery_date"])] = label
    return out


def day_type(rows: list[dict[str, object]]) -> str:
    if any(int(row.get("is_holiday", 0)) for row in rows):
        return "holiday"
    if any(int(row.get("is_weekend", 0)) for row in rows):
        return "weekend"
    return "workday"


def explanation_candidate(temp: float | None, load: float, ramp: float, bias: float, max_abs: float) -> str:
    parts = []
    parts.append(temperature_bin(temp))
    parts.append("high_load" if load > 2000.0 else "low_load")
    parts.append("high_ramp" if ramp > 250.0 else "low_ramp")
    parts.append("overforecast_bias" if bias > 0 else "underforecast_bias")
    parts.append("hourly_spike" if max_abs > 500.0 else "distributed_error")
    return ", ".join(parts)


def extreme_slice(rows: list[dict[str, object]], worst: bool) -> dict[str, object]:
    if not rows:
        return {}
    return dict(max(rows, key=lambda row: float(row["MAE"])) if worst else min(rows, key=lambda row: float(row["MAE"])))


def compare_statement(left: float, right: float, left_name: str, right_name: str) -> str:
    if not left or not right:
        return f"insufficient data for {left_name} vs {right_name}"
    delta = left - right
    relation = "higher" if delta > 0 else "lower"
    return f"{left_name} MAE is {abs(delta):.3f} MW {relation} than {right_name} ({left:.3f} vs {right:.3f} MW)."


def combined_mae(rows_by_name: dict[str, dict[str, object]], names: list[str]) -> float:
    selected = [rows_by_name[name] for name in names if name in rows_by_name]
    if not selected:
        return 0.0
    total = sum(int(row["count"]) for row in selected)
    return sum(float(row["MAE"]) * int(row["count"]) for row in selected) / total if total else 0.0


def common_patterns(rows: list[dict[str, object]]) -> str:
    if not rows:
        return "No rows."
    seasons = most_common([str(row.get("season")) for row in rows])
    weekdays = most_common([str(row.get("weekday")) for row in rows])
    explanations = most_common([str(row.get("short_explanation_candidate")) for row in rows])
    return f"Most common season: {seasons}; weekday: {weekdays}; explanation tags: {explanations}."


def most_common(values: list[str]) -> str:
    counts: dict[str, int] = defaultdict(int)
    for value in values:
        counts[value] += 1
    best = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
    return f"{best[0]} ({best[1]}/{len(values)})"


def slice_name(value: object) -> str:
    return str(value.get("slice", "unknown")) if isinstance(value, dict) else "unknown"


def value_or_none(row: dict[str, object], field: str) -> float | None:
    value = row.get(field)
    if value is None:
        return None
    return float(value)


def mean(values: list[float]) -> float:
    return p0054k.mean_float(values) if values else 0.0


def initialize_progress(evidence_dir: Path) -> None:
    write(evidence_dir / "progress-log.md", "")
    write(evidence_dir / "job-status.md", "# P0056M Job Status\n\nNo jobs yet.\n")


def should_write_progress(completed: int, total: int) -> bool:
    return completed == 1 or completed == total or completed % 25 == 0


def append_progress(evidence_dir: Path, origin: p0056k.Origin, origin_index: int, origin_count: int, status: str, completed: int, extra: dict[str, object]) -> None:
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "area": AREA,
        "model_id": MODEL_ID,
        "origin_utc": origin.origin_utc,
        "delivery_day": origin.delivery_day.isoformat(),
        "origin_index": origin_index,
        "origin_count": origin_count,
        "status": status,
        "completed_origins": completed,
        **extra,
    }
    line = json.dumps(p0056c.json_safe(payload), sort_keys=True)
    with (evidence_dir / "progress-log.md").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    write(evidence_dir / "job-status.md", "\n".join(["# P0056M Job Status", "", f"- Last status: `{status}`", f"- Origin: `{origin_index}/{origin_count}`", f"- Completed origins: `{completed}`", f"- Delivery day: `{origin.delivery_day.isoformat()}`", f"- Timestamp UTC: `{payload['timestamp_utc']}`", ""]))
    print(line, flush=True)


def write_evidence(
    evidence_dir: Path,
    summary: dict[str, object],
    day_rows: list[dict[str, object]],
    hour_rows: list[dict[str, object]],
    slices: dict[str, list[dict[str, object]]],
    patterns: dict[str, object],
    best_tests: list[dict[str, object]],
    worst_tests: list[dict[str, object]],
) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog_md(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", "# P0056M LABB Label\n\nP0056M is LABB-only SE2 M6 DayAhead error analysis. It is not G2-KANDIDAT or production activation.\n"),
        "p0056k-baseline-review.md": write(evidence_dir / "p0056k-baseline-review.md", json_report("P0056M P0056K Baseline Review", summary.get("p0056k_baseline_review", {}))),
        "dayahead-protocol.md": write(evidence_dir / "dayahead-protocol.md", json_report("P0056M DayAhead Protocol", summary.get("dayahead_protocol", {}))),
        "input-source-contract.md": write(evidence_dir / "input-source-contract.md", json_report("P0056M Input Source Contract", summary.get("input_contract", {}))),
        "leakage-review.md": write(evidence_dir / "leakage-review.md", json_report("P0056M Leakage Review", summary.get("leakage_review", {}))),
        "day-level-results.md": write(evidence_dir / "day-level-results.md", table_md("P0056M Day-Level Results", day_rows)),
        "hour-level-summary.md": write(evidence_dir / "hour-level-summary.md", hour_level_summary_md(hour_rows, slices)),
        "weekday-slice.md": write(evidence_dir / "weekday-slice.md", table_md("P0056M Weekday Slice", slices.get("weekday", []))),
        "month-slice.md": write(evidence_dir / "month-slice.md", table_md("P0056M Month Slice", slices.get("month", []))),
        "season-slice.md": write(evidence_dir / "season-slice.md", table_md("P0056M Season Slice", slices.get("season", []) + slices.get("half_year", []))),
        "temperature-slice.md": write(evidence_dir / "temperature-slice.md", table_md("P0056M Temperature Slice", slices.get("temperature", []) + slices.get("heating_degree", []))),
        "load-slice.md": write(evidence_dir / "load-slice.md", table_md("P0056M Load Slice", slices.get("load", []) + slices.get("holiday_workday_weekend", []))),
        "ramp-slice.md": write(evidence_dir / "ramp-slice.md", table_md("P0056M Ramp Slice", slices.get("ramp", []))),
        "horizon-hour-slice.md": write(evidence_dir / "horizon-hour-slice.md", table_md("P0056M Horizon And Local-Hour Slice", slices.get("horizon_hour", []) + slices.get("local_hour", []))),
        "top-5-best-tests.md": write(evidence_dir / "top-5-best-tests.md", table_md("P0056M Top 5 Best Tests", best_tests)),
        "top-5-worst-tests.md": write(evidence_dir / "top-5-worst-tests.md", table_md("P0056M Top 5 Worst Tests", worst_tests)),
        "pattern-review.md": write(evidence_dir / "pattern-review.md", pattern_review_md(patterns)),
        "decision.md": write(evidence_dir / "decision.md", json_report("P0056M Decision", summary.get("decision", {}))),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", what_we_learned_md(summary, patterns)),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", f"# P0056M Next Package Recommendation\n\n{summary.get('next_package_recommendation')}\n"),
        "day-level-results.csv": write_csv(evidence_dir / "day-level-results.csv", day_rows),
        "hour-level-summary.csv": write_csv(evidence_dir / "hour-level-summary.csv", hour_rows),
        "slice-summary.csv": write_csv(evidence_dir / "slice-summary.csv", flatten_slices(slices)),
        "top-bottom-tests.json": write(evidence_dir / "top-bottom-tests.json", json.dumps(p0056c.json_safe({"best": best_tests, "worst": worst_tests}), indent=2, sort_keys=True) + "\n"),
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(p0056c.json_safe(compact_summary(summary)), indent=2, sort_keys=True) + "\n"),
    }
    return evidence


def changelog_md(summary: dict[str, object]) -> str:
    rows = summary.get("row_counts", {})
    baseline = summary.get("p0056k_baseline_review", {})
    return "\n".join([
        "# P0056M Changelog",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Area/model: `{AREA}/{MODEL_ID}`",
        f"- Delivery days analyzed: `{rows.get('delivery_days') if isinstance(rows, dict) else None}`",
        f"- Hour rows analyzed: `{rows.get('hour_rows') if isinstance(rows, dict) else None}`",
        f"- Reconstructed MAE: `{baseline.get('reconstructed_DayAhead_hourly_MAE') if isinstance(baseline, dict) else None}` MW",
        f"- P0056K baseline match: `{baseline.get('matches_within_tolerance') if isinstance(baseline, dict) else None}`",
        "- No API, devices, runtime changes, production activation, spot price, flow/exchange/A61/capacity or old physical_balance features.",
        "",
    ])


def hour_level_summary_md(hour_rows: list[dict[str, object]], slices: dict[str, list[dict[str, object]]]) -> str:
    return "\n".join([
        "# P0056M Hour-Level Summary",
        "",
        f"- Compact hour rows persisted: `{len(hour_rows)}`",
        "- Full scope is SE2 only, so `hour-level-summary.csv` is intentionally compact enough to commit.",
        "",
        table_md("Horizon Bins", slices.get("horizon_hour", [])),
        table_md("Local-Hour Bins", slices.get("local_hour", [])),
    ])


def pattern_review_md(patterns: dict[str, object]) -> str:
    lines = ["# P0056M Pattern Review", ""]
    for key in sorted(patterns):
        value = patterns[key]
        if isinstance(value, dict):
            lines.append(f"- `{key}`: `{value.get('slice', value)}` MAE `{value.get('MAE')}` count `{value.get('count')}`")
        else:
            lines.append(f"- `{key}`: {value}")
    lines.append("")
    return "\n".join(lines)


def what_we_learned_md(summary: dict[str, object], patterns: dict[str, object]) -> str:
    return "\n".join([
        "# P0056M What We Learned",
        "",
        f"- SE2 M6 realistic DayAhead error is not uniform; worst weekday is `{slice_name(patterns.get('1_worst_weekday'))}` and worst season is `{slice_name(patterns.get('4_worst_season'))}`.",
        f"- Error mode classification: `{patterns.get('10_error_mode')}`.",
        "- The analysis used reconstructed P0056K M6 predictions because P0056K did not persist hour-level forecast rows.",
        "- This remains LABB-only and does not change runtime behavior.",
        "",
    ])


def compact_summary(summary: dict[str, object]) -> dict[str, object]:
    return {key: summary.get(key) for key in ("package_id", "status", "runtime_seconds", "row_counts", "area", "model_id", "p0056k_baseline_review", "aggregate_metrics", "pattern_review", "decision", "leakage_review", "failures")}


def flatten_slices(slices: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    out = []
    for name, rows in slices.items():
        for row in rows:
            current = {"slice_type": name}
            current.update(row)
            out.append(current)
    return out


def table_md(title: str, rows: object) -> str:
    values = rows if isinstance(rows, list) else []
    if not values:
        return f"# {title}\n\nNo rows.\n"
    keys = sorted({key for row in values if isinstance(row, dict) for key in row if not isinstance(row.get(key), (dict, list))})
    lines = [f"# {title}", "", "| " + " | ".join(keys) + " |", "| " + " | ".join("---" for _ in keys) + " |"]
    for row in values:
        lines.append("| " + " | ".join(format_cell(row.get(key)) for key in keys) + " |")
    lines.append("")
    return "\n".join(lines)


def format_cell(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def json_report(title: str, value: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(p0056c.json_safe(value), indent=2, sort_keys=True)}\n```\n"


def write_csv(path: Path, rows: list[dict[str, object]]) -> str:
    if not rows:
        return write(path, "")
    keys = sorted({key for row in rows for key in row if not isinstance(row.get(key), (dict, list))})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in keys})
    return str(path)


def main() -> None:
    result = run_p0056m_error_slice_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
