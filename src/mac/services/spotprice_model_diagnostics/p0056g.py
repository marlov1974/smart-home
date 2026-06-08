"""P0056G LABB weekly walk-forward consumption emulator."""

from __future__ import annotations

from collections import defaultdict
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


PACKAGE_ID = "P0056G"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0056G")
STOCKHOLM = ZoneInfo("Europe/Stockholm")
SCOPED_AREAS = ("SE1", "SE2", "SE3", "FI")
PRIMARY_START_LOCAL = date(2025, 6, 1)
MIN_TRAIN_DAYS = 365
MODEL_ID = "B_weekly_HGB_no_price"
MODEL_NAME = "Weekly_HGB_no_price"
PREDICTION_COLUMN = p0054k.prediction_column(MODEL_NAME)
FORECAST_TABLE = "area_consumption_weekly_forecast_log_p0056g_v1"
METRICS_TABLE = "area_consumption_weekly_metrics_p0056g_v1"


@dataclass(frozen=True)
class WeeklyWindow:
    week_start_local: date
    week_end_local: date
    forecast_origin_local: datetime
    training_cutoff_local: datetime
    forecast_origin_utc: str
    training_cutoff_utc: str
    week_id: str


@dataclass(frozen=True)
class P0056GResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


STATIC_BASELINES = {
    "SE1": {"baseline_name": "P0056E_V2_static", "DayAhead_hourly_MAE": 125.21953299342522, "full_36h_MAE": 123.509, "source": "P0056E area-variant-results"},
    "SE2": {"baseline_name": "P0056F_W12_static", "DayAhead_hourly_MAE": 206.179, "full_36h_MAE": 197.547, "source": "P0056F area-results"},
    "SE3": {"baseline_name": "P0056C_static", "DayAhead_hourly_MAE": 258.869, "full_36h_MAE": 250.928, "source": "P0056C area-results"},
    "FI": {"baseline_name": "P0056C_static", "DayAhead_hourly_MAE": 332.717, "full_36h_MAE": 311.189, "source": "P0056C area-results"},
}


def run_p0056g_weekly_walk_forward(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0056GResult:
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
        weather_by_area = {
            "SE1": p0056d_weather_all["SE1"],
            "SE2": p0056d_weather_all["SE2"],
            "SE3": p0056b_weather_all["SE3"],
            "FI": p0056d_weather_all["FI"],
        }
        weather_source_by_area = {"SE1": "P0056D", "SE2": "P0056D", "SE3": "P0056B", "FI": "P0056D"}
        weather_label_by_area = {
            area: (p0056d.P0056D_WEATHER_LABEL if weather_source_by_area[area] == "P0056D" else p0054k.WEATHER_PROXY_LABEL)
            for area in SCOPED_AREAS
        }
        input_contract = {
            "ok": bool(target_contract["ok"]) and bool(p0056b_contract["ok"]) and bool(p0056d_contract["ok"]),
            "target_contract": target_contract,
            "p0056b_weather_contract": p0056b_contract,
            "p0056d_weather_contract": p0056d_contract,
            "weather_source_by_area": weather_source_by_area,
        }
        if not input_contract["ok"]:
            summary = stopped_summary(started, feature_path, input_contract)
            evidence = write_evidence(evidence_path, summary)
            return P0056GResult("STOP", {}, evidence)

        weeks = weekly_windows(target_contract, p0056b_contract, p0056d_contract)
        modeling_weeks = all_weekly_windows(date(2022, 6, 1), weeks[-1].week_end_local if weeks else PRIMARY_START_LOCAL)
        environment = p0054k.capture_environment_status()
        hgb_spec = next(spec for spec in p0054k.model_specs(environment["imports"]) if spec.family == "HGB")  # type: ignore[arg-type]
        base_features_by_area = feature_contract_by_area()
        weekly_results: list[dict[str, object]] = []
        job_status: list[dict[str, object]] = []
        scored_rows_for_leakage: list[dict[str, object]] = []
        failures: list[dict[str, object]] = []
        total_jobs = len(SCOPED_AREAS) * len(weeks)

        for area_code in SCOPED_AREAS:
            all_rows = build_all_weekly_rows(
                area_code,
                targets_all[area_code],
                weather_by_area[area_code],
                modeling_weeks,
                weather_source_by_area[area_code],
                weather_label_by_area[area_code],
            )
            rows_by_week = defaultdict(list)
            for row in all_rows:
                rows_by_week[str(row["week_id"])].append(row)
            features = base_features_by_area[area_code]
            for week in weeks:
                started_train = progress(evidence_path, area_code, week.week_id, MODEL_ID, "train", "start")
                try:
                    train_rows = [
                        dict(row)
                        for row in all_rows
                        if str(row["target_timestamp_utc"]) < week.training_cutoff_utc
                        and p0052.parse_utc(str(row["target_timestamp_utc"])) <= p0052.parse_utc(week.training_cutoff_utc) - timedelta(hours=1)
                    ]
                    forecast_rows = [dict(row) for row in rows_by_week[week.week_id]]
                    apply_weekly_weather_profile_features(train_rows, forecast_rows)
                    fit = fit_weekly_hgb(train_rows, forecast_rows, features, hgb_spec)
                    job_status.append(progress(evidence_path, area_code, week.week_id, MODEL_ID, "train", "done", started_at=started_train["timestamp"], extra={"train_rows": len(train_rows), "forecast_rows": len(forecast_rows), "feature_count": len(features)}))
                    started_test = progress(evidence_path, area_code, week.week_id, MODEL_ID, "test", "start")
                    metrics = score_week(forecast_rows, PREDICTION_COLUMN)
                    result = weekly_result_row(area_code, week, fit, metrics, forecast_rows, weather_source_by_area[area_code], features)
                    weekly_results.append(result)
                    persist_week_outputs(conn, area_code, week, forecast_rows, result)
                    scored_rows_for_leakage.extend(forecast_rows[:4])
                    job_status.append(progress(evidence_path, area_code, week.week_id, MODEL_ID, "test", "done", started_at=started_test["timestamp"], extra={"forecast_rows_168h": metrics["full_week_168h"]["rows"], "forecast_rows_162h": metrics["forward_162h"]["rows"]}))
                except Exception as exc:  # pragma: no cover - package evidence path
                    failed = {"area_code": area_code, "week_id": week.week_id, "model_id": MODEL_ID, "error_type": type(exc).__name__, "error": str(exc)[:600]}
                    failures.append(failed)
                    job_status.append(progress(evidence_path, area_code, week.week_id, MODEL_ID, "test", "failed", extra=failed))
                write_job_status(evidence_path, job_status, total_jobs, failures)

        area_summaries = aggregate_area_results(weekly_results)
        comparisons = compare_to_static_baseline(area_summaries)
        structural = structural_diagnostics(weekly_results)
        leakage = leakage_review(weekly_results, scored_rows_for_leakage, sorted({feature for values in base_features_by_area.values() for feature in values}))
        status = decide_status(weeks, weekly_results, failures, leakage)
        summary = {
            "package_id": PACKAGE_ID,
            "label": LABEL,
            "status": status,
            "runtime_seconds": round(time.monotonic() - started, 3),
            "feature_db": str(feature_path),
            "areas": SCOPED_AREAS,
            "weeks": [week.__dict__ for week in weeks],
            "modeling_weeks": [week.__dict__ for week in modeling_weeks],
            "input_contract": input_contract,
            "weather_protocol": {
                "weather_protocol": "actual_weather_proxy",
                "label": "LABB sensitivity only; not production weather forecast",
                "weather_source_by_area": weather_source_by_area,
            },
            "model_variant_contract": model_variant_contract(base_features_by_area),
            "static_baselines": STATIC_BASELINES,
            "job_status": job_status,
            "failures": failures,
            "weekly_results": weekly_results,
            "area_summary_results": area_summaries,
            "comparison_vs_static_baseline": comparisons,
            "structural_change_diagnostics": structural,
            "leakage_review": leakage,
            "row_counts": {
                "weeks": len(weeks),
                "weekly_results": len(weekly_results),
                "expected_weekly_results": total_jobs,
                "forecast_log_rows": table_count(conn, FORECAST_TABLE),
                "metrics_rows": table_count(conn, METRICS_TABLE),
                "failed_jobs": len(failures),
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
        return P0056GResult(status, summary["row_counts"], evidence)  # type: ignore[arg-type]


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {FORECAST_TABLE} (
            forecast_origin_timestamp_utc TEXT NOT NULL,
            input_data_cutoff_utc TEXT NOT NULL,
            target_timestamp_utc TEXT NOT NULL,
            horizon_hours INTEGER NOT NULL,
            area_code TEXT NOT NULL,
            model_id TEXT NOT NULL,
            model_name TEXT NOT NULL,
            prediction_kind TEXT NOT NULL,
            predicted_consumption_mw REAL NOT NULL,
            actual_consumption_mw REAL NOT NULL,
            evaluation_scope TEXT NOT NULL,
            weather_protocol TEXT NOT NULL,
            weather_source_package TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (forecast_origin_timestamp_utc, target_timestamp_utc, area_code, model_id, generated_by_package)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {METRICS_TABLE} (
            area_code TEXT NOT NULL,
            week_id TEXT NOT NULL,
            model_id TEXT NOT NULL,
            metric_scope TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL,
            metric_text TEXT,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (area_code, week_id, model_id, metric_scope, metric_name, generated_by_package)
        )
        """
    )
    conn.commit()


def scoped_contract(contract: dict[str, object], areas: tuple[str, ...]) -> dict[str, object]:
    original = contract.get("areas", {})
    scoped = {area: original.get(area, {}) for area in areas} if isinstance(original, dict) else {}
    return {**contract, "areas": scoped, "ok": all(scoped.get(area, {}).get("rows", 0) > 0 for area in areas)}


def weekly_windows(target_contract: dict[str, object], p0056b_contract: dict[str, object], p0056d_contract: dict[str, object]) -> list[WeeklyWindow]:
    max_dates = []
    for contract in (target_contract, p0056b_contract, p0056d_contract):
        areas = contract.get("areas", {})
        if isinstance(areas, dict):
            for meta in areas.values():
                if isinstance(meta, dict) and meta.get("max_timestamp_utc"):
                    max_dates.append(p0052.parse_utc(str(meta["max_timestamp_utc"]).replace("T00:00Z", "T00:00:00Z")).astimezone(STOCKHOLM).date())
    latest = min(max_dates)
    latest_complete_sunday = latest - timedelta(days=(latest.weekday() - 6) % 7)
    if latest.weekday() != 6:
        latest_complete_sunday -= timedelta(days=7)
    return all_weekly_windows(PRIMARY_START_LOCAL, latest_complete_sunday)


def all_weekly_windows(start_date: date, latest_complete_sunday: date) -> list[WeeklyWindow]:
    current = next_monday(start_date)
    out = []
    while current + timedelta(days=6) <= latest_complete_sunday:
        origin_local = datetime.combine(current, dt_time(6, 0), tzinfo=STOCKHOLM)
        cutoff_local = datetime.combine(current, dt_time(0, 0), tzinfo=STOCKHOLM)
        iso = current.isocalendar()
        out.append(
            WeeklyWindow(
                week_start_local=current,
                week_end_local=current + timedelta(days=6),
                forecast_origin_local=origin_local,
                training_cutoff_local=cutoff_local,
                forecast_origin_utc=format_dt_utc(origin_local),
                training_cutoff_utc=format_dt_utc(cutoff_local),
                week_id=f"{iso.year}-W{iso.week:02d}",
            )
        )
        current += timedelta(days=7)
    return out


def next_monday(day: date) -> date:
    return day if day.weekday() == 0 else day + timedelta(days=(7 - day.weekday()) % 7)


def format_dt_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_all_weekly_rows(
    area_code: str,
    target_rows: list[dict[str, object]],
    weather_rows: dict[str, dict[str, object]],
    weeks: list[WeeklyWindow],
    weather_source: str,
    weather_label: str,
) -> list[dict[str, object]]:
    source_by_ts = {str(row["timestamp_utc"]): row for row in target_rows}
    source_index = {str(row["timestamp_utc"]): index for index, row in enumerate(target_rows)}
    values = [float(row["consumption_mw"]) for row in target_rows]
    rows = []
    required_history = max(max(p0054k.LAGS), max(p0054k.ROLL_WINDOWS))
    for week in weeks:
        origin_index = source_index.get(week.forecast_origin_utc)
        if origin_index is None or origin_index < required_history:
            continue
        for offset in range(168):
            target_local = datetime.combine(week.week_start_local, dt_time(0, 0), tzinfo=STOCKHOLM) + timedelta(hours=offset)
            target_ts = format_dt_utc(target_local)
            target = source_by_ts.get(target_ts)
            weather = weather_rows.get(target_ts)
            if target is None or weather is None:
                continue
            row = {
                "forecast_origin_timestamp_utc": week.forecast_origin_utc,
                "input_data_cutoff_utc": week.training_cutoff_utc,
                "target_timestamp_utc": target_ts,
                "horizon_h": offset + 1,
                "horizon_hours": int((p0052.parse_utc(target_ts) - p0052.parse_utc(week.forecast_origin_utc)).total_seconds() // 3600),
                p0054k.TARGET_FIELD: float(target["consumption_mw"]),
                "area_code": area_code,
                "area_or_target": area_code,
                "week_id": week.week_id,
                "week_start_local": week.week_start_local.isoformat(),
                "forecast_origin_local": week.forecast_origin_local.isoformat(),
                "training_cutoff_local": week.training_cutoff_local.isoformat(),
                "prediction_kind": "consumption_mw_actual_weather_proxy_labb",
                "dataset_kind": "offline_labb_weekly_walk_forward_consumption_emulator_not_deployable",
                "weather_proxy_label": weather_label,
                "weather_source_generated_by_package": weather_source,
                "target_source_generated_by_package": "P0056A",
                "split": "weekly_candidate",
            }
            p0054k.attach_calendar_features(row, p0052.parse_utc(target_ts) + timedelta(hours=1))
            row.update(p0056c.area_lag_features_at_origin(values, origin_index))
            row.update(p0056c.area_rolling_features_at_origin(values, origin_index))
            row.update(weather)
            rows.append(row)
    return rows


def apply_weekly_weather_profile_features(train_rows: list[dict[str, object]], forecast_rows: list[dict[str, object]]) -> None:
    normals = p0054k.grouped_mean(
        [row for row in train_rows if p0054k.is_finite(row.get("weather_proxy_temperature_2m_area"))],
        ("target_month", "target_model_cet_hour"),
        "weather_proxy_temperature_2m_area",
    )
    fallback_normal = p0054k.mean_float([float(row["weather_proxy_temperature_2m_area"]) for row in train_rows if p0054k.is_finite(row.get("weather_proxy_temperature_2m_area"))])
    for row in train_rows + forecast_rows:
        normal = p0054k.profile_predict(normals, row, ("target_month", "target_model_cet_hour"))
        if normal == 0.0:
            normal = fallback_normal
        temp = p0054k.safe_float(row.get("weather_proxy_temperature_2m_area"))
        row["weather_proxy_train_normal_temperature_2m_area"] = normal
        row["weather_proxy_temperature_delta_from_train_normal_area"] = temp - normal
        row["weather_proxy_cold_spell_flag_area"] = 1 if p0054k.safe_float(row.get("weather_proxy_heating_degree_hours_area")) >= 12 else 0


def feature_contract_by_area() -> dict[str, list[str]]:
    return {
        "SE1": p0056f.feature_names_for_stack("W10"),
        "SE2": p0056f.feature_names_for_stack("W12"),
        "SE3": p0056c.p0056c_feature_names(),
        "FI": p0056c.p0056c_feature_names(),
    }


def fit_weekly_hgb(train_rows: list[dict[str, object]], forecast_rows: list[dict[str, object]], features: list[str], spec: object) -> dict[str, object]:
    if len(train_rows) < 8000 or len(forecast_rows) < 120:
        raise RuntimeError(f"insufficient weekly rows: train={len(train_rows)} forecast={len(forecast_rows)}")
    x_train, encoder, names = p0054k.build_feature_matrix(train_rows, features)
    y_train = p0054k.np.array([float(row[p0054k.TARGET_FIELD]) for row in train_rows], dtype=float)
    model = p0054k.clone_model(spec.model)  # type: ignore[attr-defined]
    started = time.monotonic()
    model.fit(x_train, y_train)  # type: ignore[attr-defined]
    predictions = p0054k.predict_rows(model, encoder, forecast_rows, features)
    for row, prediction in zip(forecast_rows, predictions):
        row[PREDICTION_COLUMN] = float(prediction)
    return {
        "model_family": spec.family,  # type: ignore[attr-defined]
        "model_class": spec.model_class,  # type: ignore[attr-defined]
        "hyperparameters": spec.hyperparameters,  # type: ignore[attr-defined]
        "train_rows": len(train_rows),
        "forecast_rows": len(forecast_rows),
        "feature_count": len(names),
        "training_duration_seconds": round(time.monotonic() - started, 3),
        "model_artifact_persisted": False,
    }


def score_week(rows: list[dict[str, object]], prediction_column: str) -> dict[str, dict[str, object]]:
    full = [row for row in rows if row.get(prediction_column) is not None]
    forward = [row for row in full if int(row["horizon_hours"]) >= 0]
    return {
        "full_week_168h": metric_scope(full, prediction_column),
        "forward_162h": metric_scope(forward, prediction_column),
        "weekday": metric_scope([row for row in forward if int(row.get("is_weekend", 0)) == 0], prediction_column),
        "weekend": metric_scope([row for row in forward if int(row.get("is_weekend", 0)) == 1], prediction_column),
        "cold": metric_scope([row for row in forward if float(row.get("weather_proxy_temperature_2m_area", 99.0)) <= 0.0], prediction_column),
        "high_load": metric_scope(high_load_rows(forward), prediction_column),
        "ramp": metric_scope(ramp_rows(forward), prediction_column),
    }


def metric_scope(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    if not rows:
        return {"rows": 0, "MAE": None, "RMSE": None, "bias": None, "energy_abs_error_MWh": None, "energy_signed_error_MWh": None, "energy_error_percent": None, "p90_absolute_error": None, "p95_absolute_error": None, "mean_actual_mw": None}
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
        "energy_abs_error_MWh": abs(signed),
        "energy_signed_error_MWh": signed,
        "energy_error_percent": abs(signed) / actual_energy * 100.0 if abs(actual_energy) > 1e-9 else None,
        "p90_absolute_error": metric["p90_absolute_error"],
        "p95_absolute_error": metric["p95_absolute_error"],
        "mean_actual_mw": metric["mean_actual_mw"],
    }


def high_load_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    if not rows:
        return []
    threshold = percentile([float(row[p0054k.TARGET_FIELD]) for row in rows], 0.9)
    return [row for row in rows if float(row[p0054k.TARGET_FIELD]) >= threshold]


def ramp_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    if not rows:
        return []
    threshold = percentile([abs(float(row.get("area_consumption_ramp_24h", 0.0))) for row in rows], 0.9)
    return [row for row in rows if abs(float(row.get("area_consumption_ramp_24h", 0.0))) >= threshold]


def weekly_result_row(area_code: str, week: WeeklyWindow, fit: dict[str, object], metrics: dict[str, dict[str, object]], forecast_rows: list[dict[str, object]], weather_source: str, features: list[str]) -> dict[str, object]:
    full = metrics["full_week_168h"]
    forward = metrics["forward_162h"]
    return {
        "area_code": area_code,
        "week_id": week.week_id,
        "week_start_local": week.week_start_local.isoformat(),
        "forecast_origin_local": week.forecast_origin_local.isoformat(),
        "training_cutoff_local": week.training_cutoff_local.isoformat(),
        "forecast_origin_timestamp_utc": week.forecast_origin_utc,
        "input_data_cutoff_utc": week.training_cutoff_utc,
        "model_id": MODEL_ID,
        "model_name": MODEL_NAME,
        "weather_protocol": "actual_weather_proxy",
        "weather_source_package": weather_source,
        "train_rows": fit["train_rows"],
        "feature_count": len(features),
        "forecast_rows_168h": full["rows"],
        "forecast_rows_162h": forward["rows"],
        "weekly_MAE_168h": full["MAE"],
        "weekly_RMSE_168h": full["RMSE"],
        "weekly_bias_168h": full["bias"],
        "weekly_MAE_162h": forward["MAE"],
        "weekly_RMSE_162h": forward["RMSE"],
        "weekly_bias_162h": forward["bias"],
        "weekly_energy_abs_error_MWh": full["energy_abs_error_MWh"],
        "weekly_energy_signed_error_MWh": full["energy_signed_error_MWh"],
        "weekly_energy_error_percent": full["energy_error_percent"],
        "p90_absolute_error": forward["p90_absolute_error"],
        "p95_absolute_error": forward["p95_absolute_error"],
        "weekday_MAE_162h": metrics["weekday"]["MAE"],
        "weekend_MAE_162h": metrics["weekend"]["MAE"],
        "cold_MAE_162h": metrics["cold"]["MAE"],
        "high_load_MAE_162h": metrics["high_load"]["MAE"],
        "ramp_MAE_162h": metrics["ramp"]["MAE"],
        "mean_actual_mw_162h": forward["mean_actual_mw"],
        "mean_actual_mw_168h": full["mean_actual_mw"],
        "target_min_utc": min(str(row["target_timestamp_utc"]) for row in forecast_rows),
        "target_max_utc": max(str(row["target_timestamp_utc"]) for row in forecast_rows),
    }


def aggregate_area_results(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for area in SCOPED_AREAS:
        area_rows = [row for row in rows if row["area_code"] == area]
        maes = [float(row["weekly_MAE_162h"]) for row in area_rows if row.get("weekly_MAE_162h") is not None]
        full_maes = [float(row["weekly_MAE_168h"]) for row in area_rows if row.get("weekly_MAE_168h") is not None]
        energy = [float(row["weekly_energy_error_percent"]) for row in area_rows if row.get("weekly_energy_error_percent") is not None]
        biases = [float(row["weekly_bias_162h"]) for row in area_rows if row.get("weekly_bias_162h") is not None]
        actual_weight = sum(float(row.get("mean_actual_mw_162h") or 0.0) * int(row.get("forecast_rows_162h") or 0) for row in area_rows)
        abs_error_weight = sum(float(row.get("weekly_MAE_162h") or 0.0) * int(row.get("forecast_rows_162h") or 0) for row in area_rows)
        worst = max(area_rows, key=lambda row: float(row.get("weekly_MAE_162h") or -1.0), default={})
        best = min(area_rows, key=lambda row: float(row.get("weekly_MAE_162h") or math.inf), default={})
        first_half = area_rows[: len(area_rows) // 2]
        second_half = area_rows[len(area_rows) // 2 :]
        out.append({
            "area_code": area,
            "model_id": MODEL_ID,
            "weeks": len(area_rows),
            "mean_weekly_MAE_162h": p0054k.mean_float(maes) if maes else None,
            "median_weekly_MAE_162h": percentile(maes, 0.5) if maes else None,
            "p90_weekly_MAE_162h": percentile(maes, 0.9) if maes else None,
            "mean_weekly_MAE_168h": p0054k.mean_float(full_maes) if full_maes else None,
            "weighted_MAE_percent_of_mean_load": abs_error_weight / actual_weight * 100.0 if actual_weight else None,
            "mean_weekly_energy_error_percent": p0054k.mean_float(energy) if energy else None,
            "bias_over_period_162h": p0054k.mean_float(biases) if biases else None,
            "worst_week": worst.get("week_id"),
            "worst_week_MAE_162h": worst.get("weekly_MAE_162h"),
            "best_week": best.get("week_id"),
            "best_week_MAE_162h": best.get("weekly_MAE_162h"),
            "trend_in_error_over_time": (p0054k.mean_float([float(row["weekly_MAE_162h"]) for row in second_half]) - p0054k.mean_float([float(row["weekly_MAE_162h"]) for row in first_half])) if first_half and second_half else None,
        })
    return out


def compare_to_static_baseline(area_summaries: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for summary in area_summaries:
        area = str(summary["area_code"])
        baseline = STATIC_BASELINES[area]
        weekly = float(summary["mean_weekly_MAE_162h"]) if summary.get("mean_weekly_MAE_162h") is not None else math.nan
        baseline_mae = float(baseline["DayAhead_hourly_MAE"])
        delta = weekly - baseline_mae
        out.append({
            "area_code": area,
            "baseline_name": baseline["baseline_name"],
            "baseline_static_DayAhead_MAE": baseline_mae,
            "weekly_retrain_mean_MAE_162h": weekly,
            "delta_vs_static_MW": delta,
            "delta_vs_static_percent": delta / baseline_mae * 100.0 if baseline_mae else None,
            "weekly_retrain_improves_by_2_percent": delta / baseline_mae * 100.0 <= -2.0 if baseline_mae else False,
            "source": baseline["source"],
        })
    return out


def structural_diagnostics(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    by_area_week = {(str(row["area_code"]), str(row["week_id"])): row for row in rows}
    for area in SCOPED_AREAS:
        area_rows = [row for row in rows if row["area_code"] == area]
        previous_actual = None
        for row in area_rows:
            actual = float(row.get("mean_actual_mw_168h") or 0.0)
            prior_year = by_area_week.get((area, previous_year_week(str(row["week_id"]))))
            yoy = None if prior_year is None else actual - float(prior_year.get("mean_actual_mw_168h") or 0.0)
            out.append({
                "area_code": area,
                "week_id": row["week_id"],
                "week_start_local": row["week_start_local"],
                "rolling_mean_actual_load_mw": actual,
                "rolling_model_bias_mw_162h": row.get("weekly_bias_162h"),
                "week_over_week_load_level_change_mw": None if previous_actual is None else actual - previous_actual,
                "year_over_year_same_week_load_change_mw": yoy,
                "late_period": str(row["week_start_local"]) >= "2026-01-01",
            })
            previous_actual = actual
    return out


def previous_year_week(week_id: str) -> str:
    year, week = week_id.split("-W")
    return f"{int(year) - 1}-W{week}"


def leakage_review(results: list[dict[str, object]], sample_rows: list[dict[str, object]], features: list[str]) -> dict[str, object]:
    forbidden = ("price", "spot", "flow", "exchange", "net_position", "a61", "capacity", "physical_balance", "future_actual")
    forbidden_features = [feature for feature in features if any(term in feature.lower() for term in forbidden)]
    target_order_ok = all(
        p0052.parse_utc(str(row["input_data_cutoff_utc"])) < p0052.parse_utc(str(row["forecast_origin_timestamp_utc"]))
        for row in sample_rows
    )
    forecast_coverage_ok = all(int(row.get("forecast_rows_168h") or 0) >= 120 and int(row.get("forecast_rows_162h") or 0) >= 114 for row in results)
    return {
        "ok": not forbidden_features and target_order_ok and forecast_coverage_ok,
        "forbidden_features": forbidden_features,
        "target_order_ok": target_order_ok,
        "forecast_rows_complete": False,
        "forecast_coverage_ok": forecast_coverage_ok,
        "forecast_coverage_note": "Metrics use available area-week rows; local source gaps are reported through forecast_rows_168h/162h.",
        "training_cutoff_rule": "weekly train rows target_timestamp_utc < training_cutoff_utc",
        "weather_protocol": "actual_weather_proxy LABB sensitivity",
        "spot_price_feature_used": False,
        "flow_exchange_a61_capacity_feature_used": False,
        "old_physical_balance_target_used": False,
        "future_actual_load_feature_used": False,
        "holdout_or_future_weeks_used_for_fit_or_selection": False,
    }


def decide_status(weeks: list[WeeklyWindow], results: list[dict[str, object]], failures: list[dict[str, object]], leakage: dict[str, object]) -> str:
    if not leakage["ok"] or len(results) < len(weeks) * len(SCOPED_AREAS) or failures:
        return "STOP"
    return "WARN"


def persist_week_outputs(conn: sqlite3.Connection, area_code: str, week: WeeklyWindow, rows: list[dict[str, object]], result: dict[str, object]) -> None:
    forecast_rows = [
        (
            row["forecast_origin_timestamp_utc"],
            row["input_data_cutoff_utc"],
            row["target_timestamp_utc"],
            int(row["horizon_hours"]),
            area_code,
            MODEL_ID,
            MODEL_NAME,
            row["prediction_kind"],
            float(row[PREDICTION_COLUMN]),
            float(row[p0054k.TARGET_FIELD]),
            "full_week_168h" if int(row["horizon_hours"]) < 0 else "full_week_168h_and_forward_162h",
            "actual_weather_proxy",
            row["weather_source_generated_by_package"],
            PACKAGE_ID,
        )
        for row in rows
        if row.get(PREDICTION_COLUMN) is not None
    ]
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {FORECAST_TABLE}
        (forecast_origin_timestamp_utc, input_data_cutoff_utc, target_timestamp_utc, horizon_hours,
         area_code, model_id, model_name, prediction_kind, predicted_consumption_mw,
         actual_consumption_mw, evaluation_scope, weather_protocol, weather_source_package, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        forecast_rows,
    )
    metric_rows = []
    for name, value in result.items():
        if name in {"area_code", "week_id", "model_id", "model_name"}:
            continue
        metric_value = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) else None
        metric_text = None if metric_value is not None else json.dumps(json_safe(value), sort_keys=True)
        metric_rows.append((area_code, week.week_id, MODEL_ID, "weekly", name, metric_value, metric_text, PACKAGE_ID))
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {METRICS_TABLE}
        (area_code, week_id, model_id, metric_scope, metric_name, metric_value, metric_text, generated_by_package)
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
        area_code = str(area["area_code"])
        for name, value in area.items():
            if name == "area_code":
                continue
            metric_value = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) else None
            metric_text = None if metric_value is not None else json.dumps(json_safe(value), sort_keys=True)
            rows.append((area_code, "ALL", MODEL_ID, "area_summary", name, metric_value, metric_text, PACKAGE_ID))
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {METRICS_TABLE}
        (area_code, week_id, model_id, metric_scope, metric_name, metric_value, metric_text, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()


def reset_progress_files(evidence_dir: Path) -> None:
    write(evidence_dir / "progress-log.md", "# P0056G Progress Log\n\n")
    write(evidence_dir / "job-status.md", "# P0056G Job Status\n\nNo jobs completed yet.\n")
    write(evidence_dir / "checkpoint-resume.md", checkpoint_resume_md([], 0, []))


def progress(evidence_dir: Path, area_code: str, week_id: str, model_id: str, phase: str, status: str, *, started_at: str | None = None, extra: dict[str, object] | None = None) -> dict[str, object]:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    elapsed = None if not started_at else (p0052.parse_utc(now) - p0052.parse_utc(started_at)).total_seconds()
    parts = [f"[P0056G progress] area={area_code}", f"week={week_id}", f"model={model_id}", f"phase={phase}", f"status={status}"]
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
    return {"area_code": area_code, "week_id": week_id, "model_id": model_id, "phase": phase, "status": status, "timestamp": now, "elapsed_seconds": elapsed, **(extra or {})}


def write_job_status(evidence_dir: Path, jobs: list[dict[str, object]], total_jobs: int, failures: list[dict[str, object]]) -> None:
    write(evidence_dir / "job-status.md", job_status_md(jobs, total_jobs, failures))
    write(evidence_dir / "checkpoint-resume.md", checkpoint_resume_md(jobs, total_jobs, failures))
    write_csv(evidence_dir / "job-status.csv", jobs)


def job_status_md(jobs: list[dict[str, object]], total_jobs: int, failures: list[dict[str, object]]) -> str:
    completed_tests = len([job for job in jobs if job.get("phase") == "test" and job.get("status") == "done"])
    lines = ["# P0056G Job Status", "", f"- Completed test jobs: `{completed_tests}`", f"- Total expected area-week jobs: `{total_jobs}`", f"- Failed jobs: `{len(failures)}`", "", "| area | week | model | phase | status | elapsed_seconds |", "| --- | --- | --- | --- | --- | ---: |"]
    for job in jobs:
        elapsed = "" if job.get("elapsed_seconds") is None else f"{float(job['elapsed_seconds']):.3f}"
        lines.append(f"| {job.get('area_code')} | {job.get('week_id')} | {job.get('model_id')} | {job.get('phase')} | {job.get('status')} | {elapsed} |")
    lines.append("")
    return "\n".join(lines)


def checkpoint_resume_md(jobs: list[dict[str, object]], total_jobs: int, failures: list[dict[str, object]]) -> str:
    completed = [job for job in jobs if job.get("phase") == "test" and job.get("status") == "done"]
    last = completed[-1] if completed else {}
    remaining = max(total_jobs - len(completed), 0)
    return "\n".join([
        "# P0056G Checkpoint Resume",
        "",
        f"- completed_jobs: `{len(completed)}`",
        f"- remaining_jobs: `{remaining}`",
        f"- failed_jobs: `{len(failures)}`",
        f"- last_completed_area: `{last.get('area_code', '')}`",
        f"- last_completed_week: `{last.get('week_id', '')}`",
        f"- last_completed_model: `{last.get('model_id', '')}`",
        "- resume_command: `PYTHONPYCACHEPREFIX=/private/tmp/p0056g-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0056g`",
        "- checkpoint_location: `requirements/package-runs/P0056G/job-status.csv`",
        "",
    ])


def write_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog_md(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", "# P0056G LABB Label\n\nP0056G is LABB-only weekly walk-forward emulator evidence. It is not G2-KANDIDAT, not production weather, and not production activation.\n"),
        "baseline-review.md": write(evidence_dir / "baseline-review.md", json_report("P0056G Baseline Review", summary.get("static_baselines", STATIC_BASELINES))),
        "weekly-emulation-protocol.md": write(evidence_dir / "weekly-emulation-protocol.md", weekly_protocol_md(summary)),
        "input-source-contract.md": write(evidence_dir / "input-source-contract.md", json_report("P0056G Input Source Contract", summary.get("input_contract", {}))),
        "weather-protocol.md": write(evidence_dir / "weather-protocol.md", json_report("P0056G Weather Protocol", summary.get("weather_protocol", {}))),
        "model-variant-contract.md": write(evidence_dir / "model-variant-contract.md", json_report("P0056G Model Variant Contract", summary.get("model_variant_contract", {}))),
        "weekly-results.md": write(evidence_dir / "weekly-results.md", weekly_results_md(summary.get("weekly_results", []))),
        "area-summary-results.md": write(evidence_dir / "area-summary-results.md", area_summary_md(summary.get("area_summary_results", []))),
        "comparison-vs-static-baseline.md": write(evidence_dir / "comparison-vs-static-baseline.md", comparison_md(summary.get("comparison_vs_static_baseline", []))),
        "structural-change-diagnostics.md": write(evidence_dir / "structural-change-diagnostics.md", structural_md(summary.get("structural_change_diagnostics", []))),
        "leakage-review.md": write(evidence_dir / "leakage-review.md", json_report("P0056G Leakage Review", summary.get("leakage_review", {}))),
        "decision.md": write(evidence_dir / "decision.md", decision_md(summary)),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", what_we_learned_md(summary)),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", "# P0056G Next Package Recommendation\n\nRecommended next package: P0056H should replace actual-weather proxy with a production-like weather forecast/noise protocol and decide whether the weekly retrain cadence remains beneficial without future weather actuals.\n"),
        "weekly-results.csv": write_csv(evidence_dir / "weekly-results.csv", summary.get("weekly_results", [])),
        "area-summary-results.csv": write_csv(evidence_dir / "area-summary-results.csv", summary.get("area_summary_results", [])),
        "comparison-vs-static-baseline.csv": write_csv(evidence_dir / "comparison-vs-static-baseline.csv", summary.get("comparison_vs_static_baseline", [])),
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(json_safe(compact_summary(summary)), indent=2, sort_keys=True) + "\n"),
    }
    return evidence


def changelog_md(summary: dict[str, object]) -> str:
    rows = summary.get("row_counts", {})
    return "\n".join([
        "# P0056G Changelog",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Weeks: `{rows.get('weeks', 0) if isinstance(rows, dict) else 0}`",
        f"- Weekly area-results: `{rows.get('weekly_results', 0) if isinstance(rows, dict) else 0}`",
        f"- Failed jobs: `{rows.get('failed_jobs', 0) if isinstance(rows, dict) else 0}`",
        "- Scope: SE1, SE2, SE3 and FI.",
        "- Weather protocol: actual-weather proxy, LABB only.",
        "- No API, devices, runtime changes, spot price, flow/exchange/A61/capacity or old physical_balance features.",
        "",
    ])


def weekly_protocol_md(summary: dict[str, object]) -> str:
    weeks = summary.get("weeks", [])
    first = weeks[0] if isinstance(weeks, list) and weeks else {}
    last = weeks[-1] if isinstance(weeks, list) and weeks else {}
    return "\n".join([
        "# P0056G Weekly Emulation Protocol",
        "",
        "- Time zone: Europe/Stockholm.",
        "- Training cutoff: Monday 00:00 local boundary after prior Sunday, applied as `target_timestamp_utc < training_cutoff_utc`.",
        "- Forecast origin: Monday 06:00 local.",
        "- Delivery window: Monday 00:00 through Sunday 23:00 local.",
        "- `full_week_168h` includes Monday 00:00-05:00 as nowcast/backcast hours.",
        "- `forward_162h` includes Monday 06:00 through Sunday 23:00.",
        f"- First week: `{first.get('week_start_local', '')}`.",
        f"- Last week: `{last.get('week_start_local', '')}`.",
        "",
    ])


def model_variant_contract(features_by_area: dict[str, list[str]]) -> dict[str, object]:
    return {
        "A_static_baseline": STATIC_BASELINES,
        "B_weekly_HGB_no_price": {
            "model_name": MODEL_NAME,
            "model_family": "HGB",
            "feature_source": "P0056C/P0056F no-price feature family",
            "feature_counts_by_area": {area: len(features) for area, features in features_by_area.items()},
            "spot_price_features": False,
            "flow_exchange_a61_capacity_features": False,
            "model_artifacts_persisted": False,
        },
    }


def weekly_results_md(rows: object) -> str:
    lines = ["# P0056G Weekly Results", "", "| area | week | train rows | MAE 168h | MAE 162h | bias 162h | energy % |", "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('area_code')} | {row.get('week_id')} | {row.get('train_rows')} | {fmt(row.get('weekly_MAE_168h'))} | {fmt(row.get('weekly_MAE_162h'))} | {fmt(row.get('weekly_bias_162h'))} | {fmt(row.get('weekly_energy_error_percent'))} |")
    lines.append("")
    return "\n".join(lines)


def area_summary_md(rows: object) -> str:
    lines = ["# P0056G Area Summary Results", "", "| area | weeks | mean MAE 162h | median MAE 162h | p90 MAE 162h | mean MAE 168h | weighted MAE % load | bias 162h |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('area_code')} | {row.get('weeks')} | {fmt(row.get('mean_weekly_MAE_162h'))} | {fmt(row.get('median_weekly_MAE_162h'))} | {fmt(row.get('p90_weekly_MAE_162h'))} | {fmt(row.get('mean_weekly_MAE_168h'))} | {fmt(row.get('weighted_MAE_percent_of_mean_load'))} | {fmt(row.get('bias_over_period_162h'))} |")
    lines.append("")
    return "\n".join(lines)


def comparison_md(rows: object) -> str:
    lines = ["# P0056G Comparison Vs Static Baseline", "", "| area | baseline | static MAE | weekly MAE 162h | delta MW | delta % | improves >=2% |", "| --- | --- | ---: | ---: | ---: | ---: | --- |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('area_code')} | {row.get('baseline_name')} | {fmt(row.get('baseline_static_DayAhead_MAE'))} | {fmt(row.get('weekly_retrain_mean_MAE_162h'))} | {fmt(row.get('delta_vs_static_MW'))} | {fmt(row.get('delta_vs_static_percent'))} | {row.get('weekly_retrain_improves_by_2_percent')} |")
    lines.append("")
    return "\n".join(lines)


def structural_md(rows: object) -> str:
    lines = ["# P0056G Structural Change Diagnostics", "", "| area | week | actual mean MW | bias MW | WoW load change | YoY load change | late period |", "| --- | --- | ---: | ---: | ---: | ---: | --- |"]
    selected = []
    for area in SCOPED_AREAS:
        area_rows = [row for row in rows if isinstance(rows, list) and row.get("area_code") == area]
        selected.extend(area_rows[:3] + area_rows[-6:])
    for row in selected:
        lines.append(f"| {row.get('area_code')} | {row.get('week_id')} | {fmt(row.get('rolling_mean_actual_load_mw'))} | {fmt(row.get('rolling_model_bias_mw_162h'))} | {fmt(row.get('week_over_week_load_level_change_mw'))} | {fmt(row.get('year_over_year_same_week_load_change_mw'))} | {row.get('late_period')} |")
    lines.append("")
    lines.append("Compact table shows first three and latest six weeks per area; full diagnostics are in `metrics-summary.json`.")
    lines.append("")
    return "\n".join(lines)


def decision_md(summary: dict[str, object]) -> str:
    lines = ["# P0056G Decision", ""]
    lines.append(f"- Status: `{summary.get('status')}`")
    lines.append("- Recommendation: keep weekly retrain as LABB emulator protocol candidate only if comparison rows show >=2% MAE improvement or material late-period bias improvement.")
    lines.append("- Production readiness: not ready; actual-weather proxy must be replaced before G2-KANDIDAT evaluation.")
    lines.append("")
    for row in summary.get("comparison_vs_static_baseline", []):
        if isinstance(row, dict):
            verdict = "improves" if row.get("weekly_retrain_improves_by_2_percent") else "does_not_meet_default_threshold"
            lines.append(f"- {row.get('area_code')}: {verdict}; delta `{fmt(row.get('delta_vs_static_percent'))}%` vs `{row.get('baseline_name')}`.")
    lines.append("")
    return "\n".join(lines)


def what_we_learned_md(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0056G What We Learned",
        "",
        "- Weekly walk-forward evaluation can be run with explicit origin/cutoff/delivery-week semantics and checkpointed per area-week.",
        "- Results are LABB because future actual weather proxy is still used.",
        "- Static evidence comparison is useful for direction, but production promotion requires production-like weather forecasts and a closer model-method match.",
        "",
    ])


def compact_summary(summary: dict[str, object]) -> dict[str, object]:
    return {
        "package_id": summary.get("package_id"),
        "status": summary.get("status"),
        "runtime_seconds": summary.get("runtime_seconds"),
        "areas": summary.get("areas"),
        "row_counts": summary.get("row_counts"),
        "area_summary_results": summary.get("area_summary_results"),
        "comparison_vs_static_baseline": summary.get("comparison_vs_static_baseline"),
        "leakage_review": summary.get("leakage_review"),
    }


def stopped_summary(started: float, feature_path: Path, input_contract: dict[str, object]) -> dict[str, object]:
    return {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": "STOP",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "feature_db": str(feature_path),
        "input_contract": input_contract,
        "row_counts": {},
    }


def json_report(title: str, value: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(json_safe(value), indent=2, sort_keys=True)}\n```\n"


def write_csv(path: Path, rows: object) -> str:
    values = rows if isinstance(rows, list) else []
    if not values:
        return write(path, "")
    keys = sorted({key for row in values if isinstance(row, dict) for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
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
    result = run_p0056g_weekly_walk_forward()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
