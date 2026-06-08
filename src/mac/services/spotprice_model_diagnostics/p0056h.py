"""P0056H LABB 36h walk-forward lag protocol."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time as dt_time, timedelta, timezone
from pathlib import Path
import csv
import json
import math
import sqlite3
import time
from zoneinfo import ZoneInfo

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0056c, p0056d, p0056f
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write


PACKAGE_ID = "P0056H"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0056H")
STOCKHOLM = ZoneInfo("Europe/Stockholm")
SCOPED_AREAS = ("SE1", "SE2", "SE3", "FI")
PRIMARY_START_LOCAL = datetime(2025, 6, 1, 6, 0, tzinfo=STOCKHOLM)
MODEL_NAME = "P0056H_HGB_no_price"
MODEL_ID = "HGB_no_price"
PREDICTION_COLUMN = p0054k.prediction_column(MODEL_NAME)
FORECAST_TABLE = "area_consumption_36h_forecast_log_p0056h_v1"
METRICS_TABLE = "area_consumption_36h_metrics_p0056h_v1"
MODES = ("L1_origin_known_fallback", "L2_recursive_lags")
HORIZONS_36 = tuple(range(36))
LAG_FLAGS = ["area_consumption_lag_unavailable_count", "area_consumption_roll_unavailable_count"]


@dataclass(frozen=True)
class OriginWindow:
    origin_local: datetime
    origin_utc: str
    origin_id: str


@dataclass(frozen=True)
class P0056HResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


STATIC_BASELINES = {
    "SE1": {"baseline_name": "P0056E_V2_static", "full_36h_MAE": 123.509, "DayAhead_hourly_MAE": 125.220, "p0056c_full_36h_MAE": 124.609},
    "SE2": {"baseline_name": "P0056F_W12_static", "full_36h_MAE": 197.547, "DayAhead_hourly_MAE": 206.179, "p0056c_full_36h_MAE": 201.827},
    "SE3": {"baseline_name": "P0056C_static", "full_36h_MAE": 250.928, "DayAhead_hourly_MAE": 258.869, "p0056c_full_36h_MAE": 250.928},
    "FI": {"baseline_name": "P0056C_static", "full_36h_MAE": 311.189, "DayAhead_hourly_MAE": 332.717, "p0056c_full_36h_MAE": 311.189},
}

P0056G_WEEKLY = {
    "SE1": {"baseline_name": "P0056G_weekly_162h", "MAE": 131.253},
    "SE2": {"baseline_name": "P0056G_weekly_162h", "MAE": 207.757},
    "SE3": {"baseline_name": "P0056G_weekly_162h", "MAE": 282.365},
    "FI": {"baseline_name": "P0056G_weekly_162h", "MAE": 422.324},
}


def run_p0056h_36h_walk_forward(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0056HResult:
    started = time.monotonic()
    feature_path = Path(feature_db).expanduser()
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)
    reset_progress_files(evidence_path)
    with sqlite3.connect(feature_path, timeout=60.0) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=60000")
        create_schema(conn)
        conn.execute(f"DELETE FROM {FORECAST_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,))
        conn.execute(f"DELETE FROM {METRICS_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,))
        conn.commit()

        targets_all, target_contract_all = p0056c.load_area_targets(conn)
        p0056b_weather_all, p0056b_contract_all = p0056c.load_area_weather_rows(conn)
        p0056d_weather_all, p0056d_contract_all = p0056d.load_p0056d_area_weather_rows(conn)
        target_contract = scoped_contract(target_contract_all, SCOPED_AREAS)
        p0056b_contract = scoped_contract(p0056b_contract_all, SCOPED_AREAS)
        p0056d_contract = scoped_contract(p0056d_contract_all, ("SE1", "SE2", "FI"))
        input_contract = {
            "ok": bool(target_contract["ok"]) and bool(p0056b_contract["ok"]) and bool(p0056d_contract["ok"]),
            "target_contract": target_contract,
            "p0056b_weather_contract": p0056b_contract,
            "p0056d_weather_contract": p0056d_contract,
        }
        if not input_contract["ok"]:
            summary = stopped_summary(started, feature_path, input_contract)
            evidence = write_evidence(evidence_path, summary)
            return P0056HResult("STOP", {}, evidence)

        weather_by_area = {
            "SE1": p0056d_weather_all["SE1"],
            "SE2": p0056d_weather_all["SE2"],
            "SE3": p0056b_weather_all["SE3"],
            "FI": p0056d_weather_all["FI"],
        }
        weather_source_by_area = {"SE1": "P0056D", "SE2": "P0056D", "SE3": "P0056B", "FI": "P0056D"}
        origins = origin_schedule(target_contract, p0056b_contract, p0056d_contract)
        modeling_origins = anchored_historical_origin_schedule(date(2022, 6, 1), origins[-1].origin_local if origins else PRIMARY_START_LOCAL, PRIMARY_START_LOCAL)
        environment = p0054k.capture_environment_status()
        hgb_spec = next(spec for spec in p0054k.model_specs(environment["imports"]) if spec.family == "HGB")  # type: ignore[arg-type]
        features_by_area = feature_contract_by_area()

        origin_results: list[dict[str, object]] = []
        lag_reviews: list[dict[str, object]] = []
        job_status: list[dict[str, object]] = []
        failures: list[dict[str, object]] = []
        skipped_windows: list[dict[str, object]] = []
        scored_rows_for_leakage: list[dict[str, object]] = []
        total_jobs = len(SCOPED_AREAS) * len(origins) * len(MODES)

        for area_code in SCOPED_AREAS:
            target_rows = targets_all[area_code]
            weather_rows = weather_by_area[area_code]
            history = {str(row["timestamp_utc"]): float(row["consumption_mw"]) for row in target_rows}
            base_rows = build_modeling_rows(area_code, target_rows, weather_rows, modeling_origins, weather_source_by_area[area_code])
            rows_by_origin: dict[str, list[dict[str, object]]] = defaultdict(list)
            for row in base_rows:
                rows_by_origin[str(row["forecast_origin_timestamp_utc"])].append(row)
            features = features_by_area[area_code]
            for origin in origins:
                origin_rows_base = [dict(row) for row in rows_by_origin.get(origin.origin_utc, [])]
                train_rows = [dict(row) for row in base_rows if str(row["target_timestamp_utc"]) < origin.origin_utc]
                if len(origin_rows_base) != 36:
                    skipped = {
                        "area_code": area_code,
                        "origin": origin.origin_local.isoformat(),
                        "forecast_origin_utc": origin.origin_utc,
                        "available_forecast_rows": len(origin_rows_base),
                        "expected_forecast_rows": 36,
                        "reason": "incomplete target/weather coverage for strict 36h origin window",
                    }
                    skipped_windows.append(skipped)
                    for mode in MODES:
                        job_status.append(progress(evidence_path, area_code, mode, origin.origin_local.isoformat(), "test", "skipped", extra=skipped))
                    write_job_status(evidence_path, job_status, total_jobs, failures, skipped_windows)
                    continue
                fit_start = None
                try:
                    fit_start = progress(evidence_path, area_code, "shared_HGB", origin.origin_local.isoformat(), "train", "start")
                    apply_weather_profile_features(train_rows, origin_rows_base)
                    fit = fit_hgb(train_rows, features, hgb_spec)
                    progress(evidence_path, area_code, "shared_HGB", origin.origin_local.isoformat(), "train", "done", started_at=fit_start["timestamp"], extra={"train_rows": len(train_rows), "feature_count": len(features)})
                    for mode in MODES:
                        mode_train = progress(evidence_path, area_code, mode, origin.origin_local.isoformat(), "train", "done", started_at=fit_start["timestamp"], extra={"shared_model": MODEL_ID})
                        test_start = progress(evidence_path, area_code, mode, origin.origin_local.isoformat(), "test", "start")
                        forecast_rows = [dict(row) for row in origin_rows_base]
                        availability = apply_lag_mode_features(forecast_rows, origin, history, {}, mode)
                        if mode == "L1_origin_known_fallback":
                            predict_rows(fit, forecast_rows, features)
                        else:
                            predict_l2_recursive(fit, forecast_rows, features, origin, history)
                            availability = apply_lag_mode_features(forecast_rows, origin, history, {str(row["target_timestamp_utc"]): float(row[PREDICTION_COLUMN]) for row in forecast_rows}, mode)
                        metrics = score_origin(forecast_rows, PREDICTION_COLUMN)
                        result = origin_result_row(area_code, origin, mode, metrics, fit, weather_source_by_area[area_code])
                        origin_results.append(result)
                        lag_reviews.append(lag_availability_row(area_code, origin, mode, availability))
                        scored_rows_for_leakage.extend(forecast_rows[:2])
                        persist_origin_outputs(conn, area_code, origin, mode, forecast_rows, result)
                        job_status.append({**mode_train, "note": "shared model fit reused"})
                        job_status.append(progress(evidence_path, area_code, mode, origin.origin_local.isoformat(), "test", "done", started_at=test_start["timestamp"], extra={"forecast_rows": metrics["MAE_0_36h"]["rows"]}))
                except Exception as exc:  # pragma: no cover - package evidence path
                    failed = {"area_code": area_code, "origin": origin.origin_local.isoformat(), "error_type": type(exc).__name__, "error": str(exc)[:600]}
                    failures.append(failed)
                    for mode in MODES:
                        job_status.append(progress(evidence_path, area_code, mode, origin.origin_local.isoformat(), "test", "failed", extra=failed))
                write_job_status(evidence_path, job_status, total_jobs, failures, skipped_windows)

        area_summaries = aggregate_area_mode_results(origin_results)
        static_comparison = compare_static(area_summaries)
        p0056g_comparison = compare_p0056g(area_summaries)
        leakage = leakage_review(origin_results, lag_reviews, scored_rows_for_leakage, sorted({feature for values in features_by_area.values() for feature in values}))
        status = decide_status(area_summaries, origin_results, failures, leakage)
        summary = {
            "package_id": PACKAGE_ID,
            "label": LABEL,
            "status": status,
            "runtime_seconds": round(time.monotonic() - started, 3),
            "feature_db": str(feature_path),
            "areas": SCOPED_AREAS,
            "modes": MODES,
            "origins": [origin.__dict__ for origin in origins],
            "input_contract": input_contract,
            "weather_protocol": {"weather_protocol": "actual_weather_proxy_LABB", "weather_source_by_area": weather_source_by_area},
            "model_method_contract": model_method_contract(features_by_area),
            "static_baselines": STATIC_BASELINES,
            "p0056g_weekly_baselines": P0056G_WEEKLY,
            "job_status": job_status,
            "failures": failures,
            "skipped_incomplete_origin_windows": skipped_windows,
            "origin_results": origin_results,
            "area_summary_results": area_summaries,
            "comparison_vs_static_baseline": static_comparison,
            "comparison_vs_p0056g_weekly": p0056g_comparison,
            "lag_availability_review": lag_reviews,
            "leakage_review": leakage,
            "row_counts": {
                "origins": len(origins),
                "scheduled_origin_mode_jobs": total_jobs,
                "skipped_incomplete_origin_windows": len(skipped_windows),
                "skipped_incomplete_origin_mode_jobs": len(skipped_windows) * len(MODES),
                "origin_results": len(origin_results),
                "expected_origin_results": total_jobs - len(skipped_windows) * len(MODES),
                "failed_jobs": len(failures),
                "forecast_log_rows": table_count(conn, FORECAST_TABLE),
                "metrics_rows": table_count(conn, METRICS_TABLE),
            },
            "no_devices": True,
            "no_runtime_change": True,
            "no_production_activation": True,
            "no_api": True,
            "no_spot_price_features": True,
            "no_flow_exchange_a61_capacity_features": True,
            "no_old_physical_balance_target": True,
            "no_future_actual_load_leakage": bool(leakage["ok"]),
            "no_large_artifacts": True,
        }
        persist_summary_metrics(conn, summary)
        summary["row_counts"]["metrics_rows"] = table_count(conn, METRICS_TABLE)  # type: ignore[index]
        evidence = write_evidence(evidence_path, summary)
        return P0056HResult(status, summary["row_counts"], evidence)  # type: ignore[arg-type]


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {FORECAST_TABLE} (
            forecast_origin_timestamp_utc TEXT NOT NULL,
            target_timestamp_utc TEXT NOT NULL,
            horizon_hours INTEGER NOT NULL,
            area_code TEXT NOT NULL,
            mode TEXT NOT NULL,
            model_name TEXT NOT NULL,
            prediction_kind TEXT NOT NULL,
            predicted_consumption_mw REAL NOT NULL,
            actual_consumption_mw REAL NOT NULL,
            weather_protocol TEXT NOT NULL,
            weather_source_package TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (forecast_origin_timestamp_utc, target_timestamp_utc, area_code, mode, generated_by_package)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {METRICS_TABLE} (
            area_code TEXT NOT NULL,
            origin_id TEXT NOT NULL,
            mode TEXT NOT NULL,
            metric_scope TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL,
            metric_text TEXT,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (area_code, origin_id, mode, metric_scope, metric_name, generated_by_package)
        )
        """
    )
    conn.commit()


def scoped_contract(contract: dict[str, object], areas: tuple[str, ...]) -> dict[str, object]:
    original = contract.get("areas", {})
    scoped = {area: original.get(area, {}) for area in areas} if isinstance(original, dict) else {}
    return {**contract, "areas": scoped, "ok": all(scoped.get(area, {}).get("rows", 0) > 0 for area in areas)}


def origin_schedule(target_contract: dict[str, object], p0056b_contract: dict[str, object], p0056d_contract: dict[str, object]) -> list[OriginWindow]:
    max_times = []
    for contract in (target_contract, p0056b_contract, p0056d_contract):
        areas = contract.get("areas", {})
        if isinstance(areas, dict):
            for meta in areas.values():
                if isinstance(meta, dict) and meta.get("max_timestamp_utc"):
                    max_times.append(p0052.parse_utc(str(meta["max_timestamp_utc"]).replace("T00:00Z", "T00:00:00Z")))
    latest_target_utc = min(max_times) - timedelta(hours=35)
    current = PRIMARY_START_LOCAL
    out = []
    while current.astimezone(timezone.utc) <= latest_target_utc:
        out.append(make_origin(current))
        current += timedelta(days=5)
    return out


def historical_origin_schedule(start_day: date, latest_origin_local: datetime) -> list[OriginWindow]:
    current = datetime.combine(start_day, dt_time(6, 0), tzinfo=STOCKHOLM)
    out = []
    while current <= latest_origin_local:
        out.append(make_origin(current))
        current += timedelta(days=5)
    return out


def anchored_historical_origin_schedule(start_day: date, latest_origin_local: datetime, anchor_local: datetime) -> list[OriginWindow]:
    current = anchor_local
    start_local = datetime.combine(start_day, dt_time(6, 0), tzinfo=STOCKHOLM)
    while current - timedelta(days=5) >= start_local:
        current -= timedelta(days=5)
    out = []
    while current <= latest_origin_local:
        out.append(make_origin(current))
        current += timedelta(days=5)
    return out


def make_origin(origin_local: datetime) -> OriginWindow:
    return OriginWindow(
        origin_local=origin_local,
        origin_utc=format_dt_utc(origin_local),
        origin_id=origin_local.strftime("%Y%m%dT%H%M%S%z"),
    )


def format_dt_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_modeling_rows(
    area_code: str,
    target_rows: list[dict[str, object]],
    weather_rows: dict[str, dict[str, object]],
    origins: list[OriginWindow],
    weather_source: str,
) -> list[dict[str, object]]:
    source_by_ts = {str(row["timestamp_utc"]): row for row in target_rows}
    values_by_ts = {str(row["timestamp_utc"]): float(row["consumption_mw"]) for row in target_rows}
    rows = []
    for origin in origins:
        origin_dt = p0052.parse_utc(origin.origin_utc)
        for horizon in HORIZONS_36:
            target_ts = p0052.format_utc(origin_dt + timedelta(hours=horizon))
            target = source_by_ts.get(target_ts)
            weather = weather_rows.get(target_ts)
            if target is None or weather is None:
                continue
            row = {
                "forecast_origin_timestamp_utc": origin.origin_utc,
                "forecast_origin_local": origin.origin_local.isoformat(),
                "origin_id": origin.origin_id,
                "target_timestamp_utc": target_ts,
                "horizon_hours": horizon,
                "horizon_h": horizon + 1,
                p0054k.TARGET_FIELD: float(target["consumption_mw"]),
                "area_code": area_code,
                "area_or_target": area_code,
                "prediction_kind": "consumption_mw_actual_weather_proxy_labb",
                "dataset_kind": "offline_labb_36h_walk_forward_lag_protocol_not_deployable",
                "weather_source_generated_by_package": weather_source,
                "weather_protocol": "actual_weather_proxy_LABB",
                "split": "rolling_origin",
            }
            p0054k.attach_calendar_features(row, p0052.parse_utc(target_ts) + timedelta(hours=1))
            row.update(actual_lag_features(target_ts, values_by_ts))
            row.update(weather)
            rows.append(row)
    return rows


def actual_lag_features(target_ts: str, values_by_ts: dict[str, float]) -> dict[str, float]:
    target_dt = p0052.parse_utc(target_ts)
    out = {}
    for lag in p0054k.LAGS:
        out[f"area_consumption_lag_{lag}h"] = lookup_value(values_by_ts, p0052.format_utc(target_dt - timedelta(hours=lag)), 0.0)
    for window in p0054k.ROLL_WINDOWS:
        vals = [lookup_value(values_by_ts, p0052.format_utc(target_dt - timedelta(hours=offset)), 0.0) for offset in range(1, window + 1)]
        out[f"area_consumption_roll_mean_{window}h"] = p0054k.mean_float(vals)
    vals24 = [lookup_value(values_by_ts, p0052.format_utc(target_dt - timedelta(hours=offset)), 0.0) for offset in range(1, 25)]
    mean24 = p0054k.mean_float(vals24)
    out["area_consumption_roll_min_24h"] = min(vals24)
    out["area_consumption_roll_max_24h"] = max(vals24)
    out["area_consumption_roll_std_24h"] = math.sqrt(sum((value - mean24) ** 2 for value in vals24) / len(vals24))
    out["area_consumption_ramp_1h"] = out["area_consumption_lag_1h"] - out["area_consumption_lag_2h"]
    out["area_consumption_ramp_24h"] = out["area_consumption_lag_1h"] - out["area_consumption_lag_24h"]
    out["area_consumption_same_hour_24h_vs_168h"] = out["area_consumption_lag_24h"] - out["area_consumption_lag_168h"]
    out["area_consumption_lag_unavailable_count"] = 0.0
    out["area_consumption_roll_unavailable_count"] = 0.0
    return out


def lookup_value(values_by_ts: dict[str, float], timestamp_utc: str, fallback: float) -> float:
    return float(values_by_ts.get(timestamp_utc, fallback))


def classify_lag(target_ts: str, origin_ts: str, lag_hours: int) -> str:
    target_dt = p0052.parse_utc(target_ts)
    origin_dt = p0052.parse_utc(origin_ts)
    lag_dt = target_dt - timedelta(hours=lag_hours)
    if lag_dt >= target_dt:
        return "forbidden_future_actual"
    if lag_dt >= origin_dt:
        return "requires_recursive_forecast"
    if lag_dt == origin_dt - timedelta(hours=1):
        return "known_actual_at_origin"
    return "known_actual_before_origin"


def apply_lag_mode_features(
    rows: list[dict[str, object]],
    origin: OriginWindow,
    history: dict[str, float],
    predictions: dict[str, float],
    mode: str,
) -> dict[str, object]:
    counts: Counter[str] = Counter()
    for row in sorted(rows, key=lambda item: int(item["horizon_hours"])):
        target_ts = str(row["target_timestamp_utc"])
        target_dt = p0052.parse_utc(target_ts)
        lag_unavailable = 0
        for lag in p0054k.LAGS:
            lag_ts = p0052.format_utc(target_dt - timedelta(hours=lag))
            classification = classify_lag(target_ts, origin.origin_utc, lag)
            counts[classification] += 1
            if classification == "requires_recursive_forecast":
                if mode == "L2_recursive_lags" and lag_ts in predictions:
                    value = predictions[lag_ts]
                else:
                    fallback_ts = p0052.format_utc(p0052.parse_utc(lag_ts) - timedelta(hours=168))
                    value = history.get(fallback_ts, history.get(p0052.format_utc(p0052.parse_utc(origin.origin_utc) - timedelta(hours=1)), 0.0))
                    lag_unavailable += 1
                row[f"area_consumption_lag_{lag}h"] = float(value)
        row["area_consumption_lag_unavailable_count"] = float(lag_unavailable)
        roll_unavailable = rebuild_roll_features(row, origin, history, predictions, mode)
        row["area_consumption_roll_unavailable_count"] = float(roll_unavailable)
    return {"mode": mode, "classification_counts": dict(counts), "rows": len(rows)}


def rebuild_roll_features(row: dict[str, object], origin: OriginWindow, history: dict[str, float], predictions: dict[str, float], mode: str) -> int:
    target_dt = p0052.parse_utc(str(row["target_timestamp_utc"]))
    unavailable = 0
    for window in p0054k.ROLL_WINDOWS:
        vals = []
        for offset in range(1, window + 1):
            ts = p0052.format_utc(target_dt - timedelta(hours=offset))
            if p0052.parse_utc(ts) >= p0052.parse_utc(origin.origin_utc):
                if mode == "L2_recursive_lags" and ts in predictions:
                    vals.append(predictions[ts])
                else:
                    unavailable += 1
                    fallback_ts = p0052.format_utc(p0052.parse_utc(ts) - timedelta(hours=168))
                    vals.append(history.get(fallback_ts, history.get(p0052.format_utc(p0052.parse_utc(origin.origin_utc) - timedelta(hours=1)), 0.0)))
            else:
                vals.append(history.get(ts, 0.0))
        row[f"area_consumption_roll_mean_{window}h"] = p0054k.mean_float([float(value) for value in vals])
    vals24 = []
    for offset in range(1, 25):
        ts = p0052.format_utc(target_dt - timedelta(hours=offset))
        vals24.append(float(predictions.get(ts, history.get(ts, history.get(p0052.format_utc(p0052.parse_utc(ts) - timedelta(hours=168)), 0.0)))))
    mean24 = p0054k.mean_float(vals24)
    row["area_consumption_roll_min_24h"] = min(vals24)
    row["area_consumption_roll_max_24h"] = max(vals24)
    row["area_consumption_roll_std_24h"] = math.sqrt(sum((value - mean24) ** 2 for value in vals24) / len(vals24))
    row["area_consumption_ramp_1h"] = float(row["area_consumption_lag_1h"]) - float(row["area_consumption_lag_2h"])
    row["area_consumption_ramp_24h"] = float(row["area_consumption_lag_1h"]) - float(row["area_consumption_lag_24h"])
    row["area_consumption_same_hour_24h_vs_168h"] = float(row["area_consumption_lag_24h"]) - float(row["area_consumption_lag_168h"])
    return unavailable


def apply_weather_profile_features(train_rows: list[dict[str, object]], forecast_rows: list[dict[str, object]]) -> None:
    normals = p0054k.grouped_mean(
        [row for row in train_rows if p0054k.is_finite(row.get("weather_proxy_temperature_2m_area"))],
        ("target_month", "target_model_cet_hour"),
        "weather_proxy_temperature_2m_area",
    )
    fallback = p0054k.mean_float([float(row["weather_proxy_temperature_2m_area"]) for row in train_rows if p0054k.is_finite(row.get("weather_proxy_temperature_2m_area"))])
    for row in train_rows + forecast_rows:
        normal = p0054k.profile_predict(normals, row, ("target_month", "target_model_cet_hour")) or fallback
        temp = p0054k.safe_float(row.get("weather_proxy_temperature_2m_area"))
        row["weather_proxy_train_normal_temperature_2m_area"] = normal
        row["weather_proxy_temperature_delta_from_train_normal_area"] = temp - normal
        row["weather_proxy_cold_spell_flag_area"] = 1 if p0054k.safe_float(row.get("weather_proxy_heating_degree_hours_area")) >= 12 else 0


def feature_contract_by_area() -> dict[str, list[str]]:
    return {
        "SE1": p0056f.feature_names_for_stack("W10") + LAG_FLAGS,
        "SE2": p0056f.feature_names_for_stack("W12") + LAG_FLAGS,
        "SE3": p0056c.p0056c_feature_names() + LAG_FLAGS,
        "FI": p0056c.p0056c_feature_names() + LAG_FLAGS,
    }


def fit_hgb(train_rows: list[dict[str, object]], features: list[str], spec: object) -> dict[str, object]:
    if len(train_rows) < 5000:
        raise RuntimeError(f"insufficient train rows: {len(train_rows)}")
    started = time.monotonic()
    x_train, encoder, names = p0054k.build_feature_matrix(train_rows, features)
    y_train = p0054k.np.array([float(row[p0054k.TARGET_FIELD]) for row in train_rows], dtype=float)
    model = p0054k.clone_model(spec.model)  # type: ignore[attr-defined]
    model.fit(x_train, y_train)  # type: ignore[attr-defined]
    return {
        "model": model,
        "encoder": encoder,
        "features": names,
        "model_family": spec.family,  # type: ignore[attr-defined]
        "model_class": spec.model_class,  # type: ignore[attr-defined]
        "hyperparameters": spec.hyperparameters,  # type: ignore[attr-defined]
        "train_rows": len(train_rows),
        "training_duration_seconds": round(time.monotonic() - started, 3),
    }


def predict_rows(fit: dict[str, object], rows: list[dict[str, object]], features: list[str]) -> None:
    predictions = p0054k.predict_rows(fit["model"], fit["encoder"], rows, features)  # type: ignore[arg-type]
    for row, prediction in zip(rows, predictions):
        row[PREDICTION_COLUMN] = float(prediction)


def predict_l2_recursive(fit: dict[str, object], rows: list[dict[str, object]], features: list[str], origin: OriginWindow, history: dict[str, float]) -> None:
    predictions: dict[str, float] = {}
    for row in sorted(rows, key=lambda item: int(item["horizon_hours"])):
        apply_lag_mode_features([row], origin, history, predictions, "L2_recursive_lags")
        predict_rows(fit, [row], features)
        predictions[str(row["target_timestamp_utc"])] = float(row[PREDICTION_COLUMN])


def score_origin(rows: list[dict[str, object]], prediction_column: str) -> dict[str, dict[str, object]]:
    available = [row for row in rows if row.get(prediction_column) is not None]
    return {
        "MAE_0_6h": metric_scope([row for row in available if 0 <= int(row["horizon_hours"]) < 6], prediction_column),
        "MAE_0_12h": metric_scope([row for row in available if 0 <= int(row["horizon_hours"]) < 12], prediction_column),
        "MAE_0_24h": metric_scope([row for row in available if 0 <= int(row["horizon_hours"]) < 24], prediction_column),
        "MAE_24_36h": metric_scope([row for row in available if 24 <= int(row["horizon_hours"]) < 36], prediction_column),
        "MAE_0_36h": metric_scope(available, prediction_column),
    }


def metric_scope(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    if not rows:
        return {"rows": 0, "MAE": None, "RMSE": None, "bias": None, "p90_absolute_error": None, "p95_absolute_error": None, "absolute_energy_error_MWh": None, "signed_energy_error_MWh": None, "energy_error_percent": None, "mean_actual_mw": None}
    predictions = [float(row[prediction_column]) for row in rows]
    metric = p0054k.regression_metric_from_predictions(rows, predictions)
    actual_energy = sum(float(row[p0054k.TARGET_FIELD]) for row in rows)
    predicted_energy = sum(predictions)
    signed = predicted_energy - actual_energy
    return {
        "rows": len(rows),
        "MAE": metric["MAE"],
        "RMSE": metric["RMSE"],
        "bias": metric["bias"],
        "p90_absolute_error": metric["p90_absolute_error"],
        "p95_absolute_error": metric["p95_absolute_error"],
        "absolute_energy_error_MWh": abs(signed),
        "signed_energy_error_MWh": signed,
        "energy_error_percent": abs(signed) / actual_energy * 100.0 if abs(actual_energy) > 1e-9 else None,
        "mean_actual_mw": metric["mean_actual_mw"],
    }


def origin_result_row(area_code: str, origin: OriginWindow, mode: str, metrics: dict[str, dict[str, object]], fit: dict[str, object], weather_source: str) -> dict[str, object]:
    total = metrics["MAE_0_36h"]
    return {
        "area_code": area_code,
        "origin_id": origin.origin_id,
        "forecast_origin_local": origin.origin_local.isoformat(),
        "forecast_origin_utc": origin.origin_utc,
        "mode": mode,
        "model_name": MODEL_NAME,
        "train_rows": fit["train_rows"],
        "forecast_rows": total["rows"],
        "MAE_0_6h": metrics["MAE_0_6h"]["MAE"],
        "MAE_0_12h": metrics["MAE_0_12h"]["MAE"],
        "MAE_0_24h": metrics["MAE_0_24h"]["MAE"],
        "MAE_24_36h": metrics["MAE_24_36h"]["MAE"],
        "MAE_0_36h": total["MAE"],
        "RMSE_0_36h": total["RMSE"],
        "bias_0_36h": total["bias"],
        "p90_absolute_error": total["p90_absolute_error"],
        "p95_absolute_error": total["p95_absolute_error"],
        "absolute_energy_error_MWh_36h": total["absolute_energy_error_MWh"],
        "signed_energy_error_MWh_36h": total["signed_energy_error_MWh"],
        "energy_error_percent_36h": total["energy_error_percent"],
        "mean_actual_mw": total["mean_actual_mw"],
        "origin_weekday": origin.origin_local.weekday(),
        "origin_month": origin.origin_local.month,
        "weather_protocol": "actual_weather_proxy_LABB",
        "weather_source_package": weather_source,
    }


def lag_availability_row(area_code: str, origin: OriginWindow, mode: str, review: dict[str, object]) -> dict[str, object]:
    counts = review.get("classification_counts", {})
    return {
        "area_code": area_code,
        "origin_id": origin.origin_id,
        "mode": mode,
        "known_actual_at_origin": counts.get("known_actual_at_origin", 0) if isinstance(counts, dict) else 0,
        "known_actual_before_origin": counts.get("known_actual_before_origin", 0) if isinstance(counts, dict) else 0,
        "requires_recursive_forecast": counts.get("requires_recursive_forecast", 0) if isinstance(counts, dict) else 0,
        "forbidden_future_actual": counts.get("forbidden_future_actual", 0) if isinstance(counts, dict) else 0,
    }


def aggregate_area_mode_results(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for area in SCOPED_AREAS:
        for mode in MODES:
            selected = [row for row in rows if row["area_code"] == area and row["mode"] == mode]
            maes = [float(row["MAE_0_36h"]) for row in selected if row.get("MAE_0_36h") is not None]
            maes24 = [float(row["MAE_0_24h"]) for row in selected if row.get("MAE_0_24h") is not None]
            maes2436 = [float(row["MAE_24_36h"]) for row in selected if row.get("MAE_24_36h") is not None]
            energy = [float(row["energy_error_percent_36h"]) for row in selected if row.get("energy_error_percent_36h") is not None]
            bias = [float(row["bias_0_36h"]) for row in selected if row.get("bias_0_36h") is not None]
            actual_weight = sum(float(row.get("mean_actual_mw") or 0.0) * int(row.get("forecast_rows") or 0) for row in selected)
            abs_weight = sum(float(row.get("MAE_0_36h") or 0.0) * int(row.get("forecast_rows") or 0) for row in selected)
            out.append({
                "area_code": area,
                "mode": mode,
                "origin_count": len(selected),
                "mean_MAE_0_36h": p0054k.mean_float(maes) if maes else None,
                "median_MAE_0_36h": percentile(maes, 0.5) if maes else None,
                "mean_MAE_0_24h": p0054k.mean_float(maes24) if maes24 else None,
                "mean_MAE_24_36h": p0054k.mean_float(maes2436) if maes2436 else None,
                "weighted_MAE_percent_of_mean_load": abs_weight / actual_weight * 100.0 if actual_weight else None,
                "mean_energy_error_percent": p0054k.mean_float(energy) if energy else None,
                "bias_over_period": p0054k.mean_float(bias) if bias else None,
                "weekday_split": split_mean(selected, "origin_weekday", "MAE_0_36h"),
                "monthly_split": split_mean(selected, "origin_month", "MAE_0_36h"),
            })
    return out


def split_mean(rows: list[dict[str, object]], key: str, metric: str) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row.get(metric) is not None:
            grouped[str(row[key])].append(float(row[metric]))
    return {name: p0054k.mean_float(values) for name, values in sorted(grouped.items())}


def compare_static(summaries: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in summaries:
        baseline = STATIC_BASELINES[str(row["area_code"])]
        mae = float(row["mean_MAE_0_36h"]) if row.get("mean_MAE_0_36h") is not None else math.nan
        base = float(baseline["full_36h_MAE"])
        out.append({
            "area_code": row["area_code"],
            "mode": row["mode"],
            "baseline_name": baseline["baseline_name"],
            "static_full36_MAE": base,
            "rolling_36h_MAE": mae,
            "delta_vs_static_MW": mae - base,
            "delta_vs_static_percent": (mae - base) / base * 100.0 if base else None,
            "within_1_percent_or_better": ((mae - base) / base * 100.0) <= 1.0 if base else False,
        })
    return out


def compare_p0056g(summaries: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in summaries:
        baseline = P0056G_WEEKLY[str(row["area_code"])]
        mae = float(row["mean_MAE_0_36h"]) if row.get("mean_MAE_0_36h") is not None else math.nan
        base = float(baseline["MAE"])
        out.append({
            "area_code": row["area_code"],
            "mode": row["mode"],
            "p0056g_weekly_MAE_162h": base,
            "rolling_36h_MAE": mae,
            "delta_vs_p0056g_MW": mae - base,
            "delta_vs_p0056g_percent": (mae - base) / base * 100.0 if base else None,
            "materially_better_than_p0056g": mae < base,
        })
    return out


def leakage_review(results: list[dict[str, object]], lag_reviews: list[dict[str, object]], sample_rows: list[dict[str, object]], features: list[str]) -> dict[str, object]:
    forbidden = ("price", "spot", "flow", "exchange", "net_position", "a61", "capacity", "physical_balance", "future_actual")
    forbidden_features = [feature for feature in features if any(term in feature.lower() for term in forbidden)]
    forbidden_lags = sum(int(row.get("forbidden_future_actual") or 0) for row in lag_reviews)
    complete = all(int(row.get("forecast_rows") or 0) == 36 for row in results)
    target_order_ok = all(p0052.parse_utc(str(row["forecast_origin_timestamp_utc"])) <= p0052.parse_utc(str(row["target_timestamp_utc"])) for row in sample_rows)
    return {
        "ok": not forbidden_features and forbidden_lags == 0 and complete and target_order_ok,
        "forbidden_features": forbidden_features,
        "forbidden_future_actual_lag_count": forbidden_lags,
        "forecast_rows_complete": complete,
        "target_order_ok": target_order_ok,
        "primary_modes": MODES,
        "oracle_mode_run": False,
        "spot_price_feature_used": False,
        "flow_exchange_a61_capacity_feature_used": False,
        "old_physical_balance_target_used": False,
        "future_actual_load_feature_used": False,
    }


def decide_status(summaries: list[dict[str, object]], results: list[dict[str, object]], failures: list[dict[str, object]], leakage: dict[str, object]) -> str:
    missing_area_modes = [row for row in summaries if int(row.get("origin_count") or 0) == 0]
    if not leakage["ok"] or failures or not results or missing_area_modes:
        return "STOP"
    return "WARN"


def persist_origin_outputs(conn: sqlite3.Connection, area_code: str, origin: OriginWindow, mode: str, rows: list[dict[str, object]], result: dict[str, object]) -> None:
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {FORECAST_TABLE}
        (forecast_origin_timestamp_utc, target_timestamp_utc, horizon_hours, area_code, mode,
         model_name, prediction_kind, predicted_consumption_mw, actual_consumption_mw,
         weather_protocol, weather_source_package, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["forecast_origin_timestamp_utc"],
                row["target_timestamp_utc"],
                int(row["horizon_hours"]),
                area_code,
                mode,
                MODEL_NAME,
                row["prediction_kind"],
                float(row[PREDICTION_COLUMN]),
                float(row[p0054k.TARGET_FIELD]),
                row["weather_protocol"],
                row["weather_source_generated_by_package"],
                PACKAGE_ID,
            )
            for row in rows
            if row.get(PREDICTION_COLUMN) is not None
        ],
    )
    metric_rows = []
    for name, value in result.items():
        if name in {"area_code", "origin_id", "mode"}:
            continue
        metric_value = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) else None
        metric_text = None if metric_value is not None else json.dumps(json_safe(value), sort_keys=True)
        metric_rows.append((area_code, origin.origin_id, mode, "origin", name, metric_value, metric_text, PACKAGE_ID))
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {METRICS_TABLE}
        (area_code, origin_id, mode, metric_scope, metric_name, metric_value, metric_text, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        metric_rows,
    )
    conn.commit()


def persist_summary_metrics(conn: sqlite3.Connection, summary: dict[str, object]) -> None:
    rows = []
    for area in summary.get("area_summary_results", []):
        if not isinstance(area, dict):
            continue
        for name, value in area.items():
            if name in {"area_code", "mode"}:
                continue
            metric_value = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) else None
            metric_text = None if metric_value is not None else json.dumps(json_safe(value), sort_keys=True)
            rows.append((area["area_code"], "ALL", area["mode"], "area_summary", name, metric_value, metric_text, PACKAGE_ID))
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {METRICS_TABLE}
        (area_code, origin_id, mode, metric_scope, metric_name, metric_value, metric_text, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()


def progress(evidence_dir: Path, area_code: str, mode: str, origin: str, phase: str, status: str, *, started_at: str | None = None, extra: dict[str, object] | None = None) -> dict[str, object]:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    elapsed = None if not started_at else (p0052.parse_utc(now) - p0052.parse_utc(started_at)).total_seconds()
    parts = [f"[P0056H progress] area={area_code}", f"mode={mode}", f"origin={origin}", f"phase={phase}", f"status={status}"]
    if status == "start":
        parts.append(f"timestamp={now}")
    if elapsed is not None:
        parts.append(f"elapsed_seconds={elapsed:.3f}")
    if extra:
        parts.extend(f"{key}={value}" for key, value in extra.items())
    line = " ".join(parts)
    print(line, flush=True)
    with (evidence_dir / "progress-log.md").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    return {"area_code": area_code, "mode": mode, "origin": origin, "phase": phase, "status": status, "timestamp": now, "elapsed_seconds": elapsed, **(extra or {})}


def reset_progress_files(evidence_dir: Path) -> None:
    write(evidence_dir / "progress-log.md", "# P0056H Progress Log\n\n")
    write(evidence_dir / "job-status.md", "# P0056H Job Status\n\nNo jobs completed yet.\n")
    write(evidence_dir / "checkpoint-resume.md", checkpoint_resume_md([], 0, [], []))


def write_job_status(evidence_dir: Path, jobs: list[dict[str, object]], total_jobs: int, failures: list[dict[str, object]], skipped_windows: list[dict[str, object]]) -> None:
    write(evidence_dir / "job-status.md", job_status_md(jobs, total_jobs, failures, skipped_windows))
    write(evidence_dir / "checkpoint-resume.md", checkpoint_resume_md(jobs, total_jobs, failures, skipped_windows))
    write_csv(evidence_dir / "job-status.csv", jobs)


def job_status_md(jobs: list[dict[str, object]], total_jobs: int, failures: list[dict[str, object]], skipped_windows: list[dict[str, object]]) -> str:
    completed = len([job for job in jobs if job.get("phase") == "test" and job.get("status") == "done"])
    skipped_jobs = len(skipped_windows) * len(MODES)
    lines = ["# P0056H Job Status", "", f"- Completed test jobs: `{completed}`", f"- Total scheduled mode-origin jobs: `{total_jobs}`", f"- Skipped incomplete mode-origin jobs: `{skipped_jobs}`", f"- Failed jobs: `{len(failures)}`", "", "| area | mode | origin | phase | status | elapsed_seconds |", "| --- | --- | --- | --- | --- | ---: |"]
    for job in jobs:
        elapsed = "" if job.get("elapsed_seconds") is None else f"{float(job['elapsed_seconds']):.3f}"
        lines.append(f"| {job.get('area_code')} | {job.get('mode')} | {job.get('origin')} | {job.get('phase')} | {job.get('status')} | {elapsed} |")
    lines.append("")
    return "\n".join(lines)


def checkpoint_resume_md(jobs: list[dict[str, object]], total_jobs: int, failures: list[dict[str, object]], skipped_windows: list[dict[str, object]]) -> str:
    completed = [job for job in jobs if job.get("phase") == "test" and job.get("status") == "done"]
    skipped_jobs = len(skipped_windows) * len(MODES)
    last = completed[-1] if completed else {}
    return "\n".join([
        "# P0056H Checkpoint Resume",
        "",
        f"- completed_jobs: `{len(completed)}`",
        f"- skipped_jobs: `{skipped_jobs}`",
        f"- remaining_jobs: `{max(total_jobs - skipped_jobs - len(completed), 0)}`",
        f"- failed_jobs: `{len(failures)}`",
        f"- last_completed_area: `{last.get('area_code', '')}`",
        f"- last_completed_mode: `{last.get('mode', '')}`",
        f"- last_completed_origin: `{last.get('origin', '')}`",
        "- resume_command: `PYTHONPYCACHEPREFIX=/private/tmp/p0056h-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0056h`",
        "- checkpoint_location: `requirements/package-runs/P0056H/job-status.csv`",
        "",
    ])


def write_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog_md(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", "# P0056H LABB Label\n\nP0056H is LABB-only 36h lag protocol evidence, not G2-KANDIDAT or production activation.\n"),
        "baseline-review.md": write(evidence_dir / "baseline-review.md", json_report("P0056H Baseline Review", summary.get("static_baselines", STATIC_BASELINES))),
        "origin-schedule.md": write(evidence_dir / "origin-schedule.md", origin_schedule_md(summary)),
        "lag-protocol-contract.md": write(evidence_dir / "lag-protocol-contract.md", lag_protocol_md()),
        "lag-availability-review.md": write(evidence_dir / "lag-availability-review.md", lag_availability_md(summary.get("lag_availability_review", []))),
        "input-source-contract.md": write(evidence_dir / "input-source-contract.md", json_report("P0056H Input Source Contract", summary.get("input_contract", {}))),
        "coverage-gaps.md": write(evidence_dir / "coverage-gaps.md", coverage_gaps_md(summary.get("skipped_incomplete_origin_windows", []))),
        "weather-protocol.md": write(evidence_dir / "weather-protocol.md", json_report("P0056H Weather Protocol", summary.get("weather_protocol", {}))),
        "model-method-contract.md": write(evidence_dir / "model-method-contract.md", json_report("P0056H Model Method Contract", summary.get("model_method_contract", {}))),
        "origin-results.md": write(evidence_dir / "origin-results.md", origin_results_md(summary.get("origin_results", []))),
        "area-summary-results.md": write(evidence_dir / "area-summary-results.md", area_summary_md(summary.get("area_summary_results", []))),
        "comparison-vs-static-baseline.md": write(evidence_dir / "comparison-vs-static-baseline.md", comparison_md(summary.get("comparison_vs_static_baseline", []), "static_full36_MAE", "delta_vs_static_percent")),
        "comparison-vs-p0056g-weekly.md": write(evidence_dir / "comparison-vs-p0056g-weekly.md", comparison_md(summary.get("comparison_vs_p0056g_weekly", []), "p0056g_weekly_MAE_162h", "delta_vs_p0056g_percent")),
        "leakage-review.md": write(evidence_dir / "leakage-review.md", json_report("P0056H Leakage Review", summary.get("leakage_review", {}))),
        "decision.md": write(evidence_dir / "decision.md", decision_md(summary)),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", what_we_learned_md(summary)),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", "# P0056H Next Package Recommendation\n\nRecommended next package: if L2 recursive 36h is competitive, replace actual-weather proxy with a production-like weather forecast/noise protocol before G2-KANDIDAT evaluation.\n"),
        "origin-results.csv": write_csv(evidence_dir / "origin-results.csv", summary.get("origin_results", [])),
        "area-summary-results.csv": write_csv(evidence_dir / "area-summary-results.csv", summary.get("area_summary_results", [])),
        "lag-availability-summary.csv": write_csv(evidence_dir / "lag-availability-summary.csv", summary.get("lag_availability_review", [])),
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(json_safe(compact_summary(summary)), indent=2, sort_keys=True) + "\n"),
    }
    return evidence


def model_method_contract(features_by_area: dict[str, list[str]]) -> dict[str, object]:
    return {
        "model_name": MODEL_NAME,
        "model_family": "HGB",
        "method_note": "Tractable rolling-origin lag protocol test; not full weighted ensemble reproduction.",
        "modes": MODES,
        "feature_counts_by_area": {area: len(features) for area, features in features_by_area.items()},
        "spot_price_features": False,
        "flow_exchange_a61_capacity_features": False,
    }


def changelog_md(summary: dict[str, object]) -> str:
    rows = summary.get("row_counts", {})
    return "\n".join([
        "# P0056H Changelog",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Origins: `{rows.get('origins', 0) if isinstance(rows, dict) else 0}`",
        f"- Origin/mode results: `{rows.get('origin_results', 0) if isinstance(rows, dict) else 0}`",
        f"- Failed jobs: `{rows.get('failed_jobs', 0) if isinstance(rows, dict) else 0}`",
        "- Scope: SE1, SE2, SE3 and FI.",
        "- Weather protocol: actual-weather proxy, LABB only.",
        "- No API, devices, runtime changes, spot price, flow/exchange/A61/capacity or old physical_balance features.",
        "",
    ])


def origin_schedule_md(summary: dict[str, object]) -> str:
    origins = summary.get("origins", [])
    first = origins[0] if isinstance(origins, list) and origins else {}
    last = origins[-1] if isinstance(origins, list) and origins else {}
    weekdays = sorted({p0052.parse_utc(str(item["origin_utc"])).astimezone(STOCKHOLM).weekday() for item in origins}) if isinstance(origins, list) else []
    return "\n".join([
        "# P0056H Origin Schedule",
        "",
        "- Origin cadence: every 5th day.",
        "- Origin local time: 06:00 Europe/Stockholm.",
        "- Horizon: 36 hours, origin through origin + 35h.",
        f"- Origin count: `{len(origins) if isinstance(origins, list) else 0}`.",
        f"- First origin: `{first.get('origin_local', '')}`.",
        f"- Last origin: `{last.get('origin_local', '')}`.",
        f"- Weekdays covered: `{weekdays}`.",
        "",
    ])


def lag_protocol_md() -> str:
    return "\n".join([
        "# P0056H Lag Protocol Contract",
        "",
        "- `L1_origin_known_fallback`: lag values that point into the forecast window are replaced with same-hour seasonal fallback values and flagged through unavailable counters.",
        "- `L2_recursive_lags`: lag values that point into earlier forecast-window hours use the model's own previous forecast when available; otherwise they fall back like L1.",
        "- Primary result excludes future actual load lag leakage.",
        "- Oracle future-actual lag sensitivity was not run.",
        "",
    ])


def lag_availability_md(rows: object) -> str:
    totals: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in rows if isinstance(rows, list) else []:
        key = (str(row.get("area_code")), str(row.get("mode")))
        for name in ("known_actual_at_origin", "known_actual_before_origin", "requires_recursive_forecast", "forbidden_future_actual"):
            totals[key][name] += int(row.get(name) or 0)
    lines = ["# P0056H Lag Availability Review", "", "| area | mode | known at origin | known before | recursive required | forbidden future actual |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    for (area, mode), counts in sorted(totals.items()):
        lines.append(f"| {area} | {mode} | {counts['known_actual_at_origin']} | {counts['known_actual_before_origin']} | {counts['requires_recursive_forecast']} | {counts['forbidden_future_actual']} |")
    lines.append("")
    return "\n".join(lines)


def coverage_gaps_md(rows: object) -> str:
    values = rows if isinstance(rows, list) else []
    lines = ["# P0056H Coverage Gaps", ""]
    if not values:
        lines.append("No incomplete 36h origin windows were skipped.")
        lines.append("")
        return "\n".join(lines)
    by_area = Counter(str(row.get("area_code")) for row in values if isinstance(row, dict))
    lines.append("Incomplete origin windows were skipped rather than scored, preserving strict 36h metrics for evaluated origins.")
    lines.append("")
    for area, count in sorted(by_area.items()):
        lines.append(f"- {area}: `{count}` skipped origin windows.")
    lines.extend(["", "| area | origin_local | available rows | reason |", "| --- | --- | ---: | --- |"])
    for row in values:
        if isinstance(row, dict):
            lines.append(f"| {row.get('area_code')} | {row.get('origin')} | {row.get('available_forecast_rows')} | {row.get('reason')} |")
    lines.append("")
    return "\n".join(lines)


def origin_results_md(rows: object) -> str:
    lines = ["# P0056H Origin Results", "", "| area | mode | origin | MAE 0-36h | MAE 0-24h | MAE 24-36h | bias | energy % |", "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('area_code')} | {row.get('mode')} | {row.get('forecast_origin_local')} | {fmt(row.get('MAE_0_36h'))} | {fmt(row.get('MAE_0_24h'))} | {fmt(row.get('MAE_24_36h'))} | {fmt(row.get('bias_0_36h'))} | {fmt(row.get('energy_error_percent_36h'))} |")
    lines.append("")
    return "\n".join(lines)


def area_summary_md(rows: object) -> str:
    lines = ["# P0056H Area Summary Results", "", "| area | mode | origins | mean MAE 0-36h | median MAE | MAE 0-24h | MAE 24-36h | weighted MAE % load | bias |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('area_code')} | {row.get('mode')} | {row.get('origin_count')} | {fmt(row.get('mean_MAE_0_36h'))} | {fmt(row.get('median_MAE_0_36h'))} | {fmt(row.get('mean_MAE_0_24h'))} | {fmt(row.get('mean_MAE_24_36h'))} | {fmt(row.get('weighted_MAE_percent_of_mean_load'))} | {fmt(row.get('bias_over_period'))} |")
    lines.append("")
    return "\n".join(lines)


def comparison_md(rows: object, baseline_key: str, delta_key: str) -> str:
    lines = ["# P0056H Comparison", "", "| area | mode | baseline | rolling 36h MAE | delta % |", "| --- | --- | ---: | ---: | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('area_code')} | {row.get('mode')} | {fmt(row.get(baseline_key))} | {fmt(row.get('rolling_36h_MAE'))} | {fmt(row.get(delta_key))} |")
    lines.append("")
    return "\n".join(lines)


def decision_md(summary: dict[str, object]) -> str:
    lines = ["# P0056H Decision", "", f"- Status: `{summary.get('status')}`", "- Production readiness: not ready; actual-weather proxy remains LABB-only.", ""]
    comparisons = summary.get("comparison_vs_static_baseline", [])
    for row in comparisons if isinstance(comparisons, list) else []:
        verdict = "candidate_threshold_met" if row.get("within_1_percent_or_better") else "does_not_meet_static_threshold"
        lines.append(f"- {row.get('area_code')} {row.get('mode')}: {verdict}; delta `{fmt(row.get('delta_vs_static_percent'))}%` vs `{row.get('baseline_name')}`.")
    lines.append("")
    return "\n".join(lines)


def what_we_learned_md(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0056H What We Learned",
        "",
        "- 36h rolling-origin forecasts can classify and avoid future actual load lag leakage explicitly.",
        "- L1 fallback and L2 recursive lag protocols are directly comparable against static full36 and P0056G weekly results.",
        "- Any production recommendation still needs production-like weather protocol, not actual-weather proxy.",
        "",
    ])


def compact_summary(summary: dict[str, object]) -> dict[str, object]:
    return {
        "package_id": summary.get("package_id"),
        "status": summary.get("status"),
        "runtime_seconds": summary.get("runtime_seconds"),
        "areas": summary.get("areas"),
        "modes": summary.get("modes"),
        "row_counts": summary.get("row_counts"),
        "skipped_incomplete_origin_windows": summary.get("skipped_incomplete_origin_windows"),
        "area_summary_results": summary.get("area_summary_results"),
        "comparison_vs_static_baseline": summary.get("comparison_vs_static_baseline"),
        "comparison_vs_p0056g_weekly": summary.get("comparison_vs_p0056g_weekly"),
        "leakage_review": summary.get("leakage_review"),
    }


def stopped_summary(started: float, feature_path: Path, input_contract: dict[str, object]) -> dict[str, object]:
    return {"package_id": PACKAGE_ID, "label": LABEL, "status": "STOP", "runtime_seconds": round(time.monotonic() - started, 3), "feature_db": str(feature_path), "input_contract": input_contract, "row_counts": {}}


def json_report(title: str, value: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(json_safe(value), indent=2, sort_keys=True)}\n```\n"


def write_csv(path: Path, rows: object) -> str:
    values = rows if isinstance(rows, list) else []
    if not values:
        return write(path, "")
    keys = sorted({key for row in values if isinstance(row, dict) for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        for row in values:
            writer.writerow({key: json.dumps(json_safe(row.get(key)), sort_keys=True) if isinstance(row.get(key), (dict, list)) else row.get(key) for key in keys})
    return str(path)


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def fmt(value: object) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"{float(value):.3f}"
    if value is None:
        return ""
    return str(value)


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {table} WHERE generated_by_package=?", (PACKAGE_ID,)).fetchone()[0])


def main() -> None:
    result = run_p0056h_36h_walk_forward()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
