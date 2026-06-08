"""P0056F LABB weather feature ablation efficiency."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import csv
import json
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054n, p0054q, p0054r, p0056c, p0056d, p0056e
from src.mac.services.spotprice_model_diagnostics.p0041 import write


PACKAGE_ID = "P0056F"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0056F")
SCOPED_AREAS = ("SE1", "SE2")
MODEL_NAME = "HorizonBiasCorrected_WeightedEnsemble_no_price"
FORECAST_TABLE = "area_consumption_forecast_log_p0056f_v1"
METRICS_TABLE = "area_consumption_forecast_metrics_p0056f_v1"


@dataclass(frozen=True)
class WeatherStack:
    stack_id: str
    description: str
    weather_features: tuple[str, ...]


@dataclass(frozen=True)
class P0056FResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0056f_weather_ablation(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0056FResult:
    started = time.monotonic()
    feature_path = Path(feature_db).expanduser()
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)
    reset_progress_log(evidence_path)
    with sqlite3.connect(feature_path, timeout=60.0) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=60000")
        create_schema(conn)
        conn.execute(f"DELETE FROM {FORECAST_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,))
        conn.execute(f"DELETE FROM {METRICS_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,))
        conn.commit()

        targets_all, target_contract_all = p0056c.load_area_targets(conn)
        weather_all, weather_contract_all = p0056d.load_p0056d_area_weather_rows(conn)
        target_contract = scoped_contract(target_contract_all)
        weather_contract = scoped_contract(weather_contract_all)
        input_contract = {"ok": bool(target_contract["ok"]) and bool(weather_contract["ok"]), "target_contract": target_contract, "weather_contract": weather_contract}
        if not input_contract["ok"]:
            summary = stopped_summary(started, feature_path, input_contract)
            evidence = write_evidence(evidence_path, summary)
            return P0056FResult("STOP", {}, evidence)

        environment = p0054r.capture_environment_status()
        specs = p0054k.model_specs(environment["imports"])  # type: ignore[arg-type]
        stacks = weather_stacks()
        results: list[dict[str, object]] = []
        failed: list[dict[str, object]] = []
        job_status: list[dict[str, object]] = []
        total_jobs = len(SCOPED_AREAS) * len(stacks)
        job_index = 0
        for area_code in SCOPED_AREAS:
            base_rows = p0056e.prepare_rows(area_code, targets_all[area_code], weather_all[area_code], "P0056D")
            for stack in stacks:
                job_index += 1
                start = progress(evidence_path, area_code, stack.stack_id, "train", "start")
                rows = [dict(row) for row in base_rows]
                try:
                    features = feature_names_for_stack(stack.stack_id)
                    fit = fit_stack_model(rows, stack, features, specs)
                    job_status.append(progress(evidence_path, area_code, stack.stack_id, "train", "done", started_at=start["timestamp"], extra={"job": f"{job_index}/{total_jobs}", "rows": len(rows), "feature_count": len(features), "weather_feature_count": len(stack.weather_features)}))
                    test = progress(evidence_path, area_code, stack.stack_id, "test", "start")
                    prediction_column = str(fit["prediction_column"])
                    metrics = p0056c.evaluate_area_model(area_code, rows, prediction_column)
                    persist_stack_outputs(conn, area_code, stack, rows, prediction_column, metrics)
                    results.append(stack_result_summary(area_code, stack, fit, metrics, rows, features))
                    job_status.append(progress(evidence_path, area_code, stack.stack_id, "test", "done", started_at=test["timestamp"], extra={"job": f"{job_index}/{total_jobs}", "dayahead_rows": metrics["row_counts"]["dayahead_rows"], "full36_rows": metrics["row_counts"]["full36_rows"]}))
                except Exception as exc:  # pragma: no cover - package evidence path
                    item = {"area_code": area_code, "weather_stack_id": stack.stack_id, "error_type": type(exc).__name__, "error": str(exc)[:500]}
                    failed.append(item)
                    job_status.append(progress(evidence_path, area_code, stack.stack_id, "test", "failed", extra=item))

        marginal = marginal_gain_rows(results)
        comparison = comparison_rows(results)
        decision = peak_efficiency_decision(results, marginal)
        leakage = leakage_review([feature_names_for_stack(stack.stack_id) for stack in stacks])
        status = decide_status(results, failed, leakage)
        summary = {
            "package_id": PACKAGE_ID,
            "label": LABEL,
            "status": status,
            "runtime_seconds": round(time.monotonic() - started, 3),
            "feature_db": str(feature_path),
            "areas": SCOPED_AREAS,
            "input_contract": input_contract,
            "split_policy": p0056c.split_policy(),
            "environment": environment,
            "weather_signal_order": weather_signal_order(),
            "weather_stacks": [stack.__dict__ for stack in stacks],
            "fixed_non_weather_features": fixed_non_weather_features(),
            "job_status": job_status,
            "failed_stacks": failed,
            "feature_ablation_results": results,
            "marginal_gain_rows": marginal,
            "comparison_rows": comparison,
            "peak_efficiency_decision": decision,
            "leakage_review": leakage,
            "row_counts": {"stack_results": len(results), "failed_stacks": len(failed), "forecast_log_rows": table_count(conn, FORECAST_TABLE), "metrics_rows": table_count(conn, METRICS_TABLE)},
            "exploratory_holdout_selection": True,
            "no_devices": True,
            "no_runtime_change": True,
            "no_production_activation": True,
            "no_external_live_data_integration": True,
            "no_spot_price_features": True,
            "no_flow_exchange_a61_capacity_features": True,
            "no_old_physical_balance_target": True,
            "no_future_actual_load_leakage": True,
            "no_large_artifacts": True,
        }
        evidence = write_evidence(evidence_path, summary)
        return P0056FResult(status, summary["row_counts"], evidence)  # type: ignore[arg-type]


def weather_signal_order() -> list[str]:
    return [
        "weather_proxy_temperature_2m_area",
        "weather_proxy_heating_degree_hours_area",
        "weather_proxy_temperature_roll_mean_24h_area",
        "weather_proxy_train_normal_temperature_2m_area",
        "weather_proxy_temperature_delta_from_train_normal_area",
        "weather_proxy_cold_spell_flag_area",
        "weather_proxy_apparent_temperature_area",
        "weather_proxy_wind_speed_area",
        "weather_proxy_snow_depth_area",
        "weather_proxy_precipitation_area",
        "weather_proxy_humidity_area",
        "weather_proxy_cloud_cover_area",
        "weather_proxy_cooling_degree_hours_area",
    ]


def weather_stacks() -> list[WeatherStack]:
    order = weather_signal_order()
    return [
        WeatherStack("W0", "W0 no weather", ()),
        WeatherStack("W1", "W1 temperature only", tuple(order[:1])),
        WeatherStack("W2", "W2 add heating degree", tuple(order[:2])),
        WeatherStack("W3", "W3 add temperature rolling mean", tuple(order[:3])),
        WeatherStack("W4", "W4 add temperature normal and delta", tuple(order[:5])),
        WeatherStack("W5", "W5 add cold spell flag", tuple(order[:6])),
        WeatherStack("W6", "W6 add apparent temperature", tuple(order[:7])),
        WeatherStack("W7", "W7 add wind speed", tuple(order[:8])),
        WeatherStack("W8", "W8 add snow depth", tuple(order[:9])),
        WeatherStack("W9", "W9 add precipitation", tuple(order[:10])),
        WeatherStack("W10", "W10 add humidity", tuple(order[:11])),
        WeatherStack("W11", "W11 add cloud cover", tuple(order[:12])),
        WeatherStack("W12", "W12 add cooling degree", tuple(order[:13])),
    ]


def fixed_non_weather_features() -> list[str]:
    return [feature for feature in p0056c.p0056c_feature_names() if not feature.startswith("weather_proxy_")]


def feature_names_for_stack(stack_id: str) -> list[str]:
    stacks = {stack.stack_id: stack for stack in weather_stacks()}
    return fixed_non_weather_features() + list(stacks[stack_id].weather_features)


def fit_stack_model(rows: list[dict[str, object]], stack: WeatherStack, features: list[str], specs: list[object]) -> dict[str, object]:
    output_column = p0054k.prediction_column(f"P0056F_{stack.stack_id}")
    training = p0056c.fit_horizon_bias_weighted_ensemble(rows, features, specs)
    for row in rows:
        if row.get(p0056c.PREDICTION_COLUMN) is not None:
            row[output_column] = float(row[p0056c.PREDICTION_COLUMN])
    return {"prediction_column": output_column, "training": training}


def stack_result_summary(area_code: str, stack: WeatherStack, fit: dict[str, object], metrics: dict[str, object], rows: list[dict[str, object]], features: list[str]) -> dict[str, object]:
    training = fit["training"] if isinstance(fit.get("training"), dict) else {}
    return {
        "area_code": area_code,
        "method": MODEL_NAME,
        "weather_stack_id": stack.stack_id,
        "weather_feature_count": len(stack.weather_features),
        "weather_features_included": ",".join(stack.weather_features),
        "total_feature_count": len(features),
        "training_rows": training.get("train_fit_rows"),
        "holdout_rows": training.get("holdout_rows"),
        "forecast_origins": len({row["forecast_origin_timestamp_utc"] for row in rows}),
        "DayAhead_hourly_MAE": metrics["dayahead"].get("hourly_MAE_delivery_day"),  # type: ignore[union-attr]
        "DayAhead_RMSE": metrics["dayahead"].get("hourly_RMSE_delivery_day"),  # type: ignore[union-attr]
        "DayAhead_bias": metrics["dayahead"].get("bias_delivery_day"),  # type: ignore[union-attr]
        "MAE_percent_of_mean_actual": metrics["dayahead"].get("MAE_percent_of_mean_actual"),  # type: ignore[union-attr]
        "MAE_percent_of_median_actual": metrics["dayahead"].get("MAE_percent_of_median_actual"),  # type: ignore[union-attr]
        "absolute_daily_energy_error_MWh": metrics["daily_energy"].get("absolute_daily_energy_error_MWh"),  # type: ignore[union-attr]
        "signed_daily_energy_error_MWh": metrics["daily_energy"].get("signed_daily_energy_error_MWh"),  # type: ignore[union-attr]
        "daily_energy_error_percent_of_actual": metrics["daily_energy"].get("daily_energy_error_percent_of_actual"),  # type: ignore[union-attr]
        "full_36h_MAE": metrics["full36"].get("MAE_full_36h"),  # type: ignore[union-attr]
        "full_36h_RMSE": metrics["full36"].get("RMSE_full_36h"),  # type: ignore[union-attr]
        "full_36h_bias": metrics["full36"].get("bias_full_36h"),  # type: ignore[union-attr]
        "p90_absolute_error": metrics["dayahead"].get("p90_absolute_error"),  # type: ignore[union-attr]
        "p95_absolute_error": metrics["dayahead"].get("p95_absolute_error"),  # type: ignore[union-attr]
        "MAE_0_6h": metrics["horizon_slices"].get("MAE_0_6h"),  # type: ignore[union-attr]
        "MAE_0_12h": metrics["horizon_slices"].get("MAE_0_12h"),  # type: ignore[union-attr]
        "MAE_0_24h": metrics["horizon_slices"].get("MAE_0_24h"),  # type: ignore[union-attr]
        "MAE_24_36h": metrics["horizon_slices"].get("MAE_24_36h"),  # type: ignore[union-attr]
        "regimes": metrics.get("regimes"),
    }


def marginal_gain_rows(results: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for area in SCOPED_AREAS:
        rows = sorted([row for row in results if row["area_code"] == area], key=lambda row: int(str(row["weather_stack_id"])[1:]))
        w0 = float(rows[0]["DayAhead_hourly_MAE"]) if rows else 0.0
        current_best = float(current_best_baseline(area)["DayAhead_hourly_MAE"])
        previous = None
        for row in rows:
            current = float(row["DayAhead_hourly_MAE"])
            previous_delta = None if previous is None else current - previous
            previous_percent = None if previous is None else (previous_delta / previous * 100.0)
            out.append({
                "area_code": area,
                "weather_stack_id": row["weather_stack_id"],
                "weather_feature_count": row["weather_feature_count"],
                "DayAhead_hourly_MAE": current,
                "delta_MAE_vs_previous_stack": previous_delta,
                "delta_MAE_percent_vs_previous_stack": previous_percent,
                "delta_MAE_vs_W0": current - w0,
                "delta_MAE_vs_current_best": current - current_best,
                "marginal_gain_per_added_feature": None if previous_delta is None else -previous_delta,
            })
            previous = current
    return out


def comparison_rows(results: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in results:
        area = str(row["area_code"])
        for baseline in (p0056e.P0056C_BASELINES[area] | {"baseline_name": "P0056C"}, p0056e.P0056D_BASELINES[area] | {"baseline_name": "P0056D"}, current_best_baseline(area)):
            out.append({
                "area_code": row["area_code"],
                "weather_stack_id": row["weather_stack_id"],
                "baseline_name": baseline["baseline_name"],
                "baseline_DayAhead_MAE": baseline["DayAhead_hourly_MAE"],
                "stack_DayAhead_MAE": row["DayAhead_hourly_MAE"],
                "delta_vs_baseline_DayAhead_MW": float(row["DayAhead_hourly_MAE"]) - float(baseline["DayAhead_hourly_MAE"]),
                "delta_vs_baseline_DayAhead_percent": (float(row["DayAhead_hourly_MAE"]) - float(baseline["DayAhead_hourly_MAE"])) / float(baseline["DayAhead_hourly_MAE"]) * 100.0,
                "baseline_full36_MAE": baseline["full_36h_MAE"],
                "stack_full36_MAE": row["full_36h_MAE"],
                "delta_vs_baseline_full36_MW": float(row["full_36h_MAE"]) - float(baseline["full_36h_MAE"]),
                "delta_vs_baseline_full36_percent": (float(row["full_36h_MAE"]) - float(baseline["full_36h_MAE"])) / float(baseline["full_36h_MAE"]) * 100.0,
            })
    return out


def current_best_baseline(area: str) -> dict[str, object]:
    if area == "SE1":
        return {"baseline_name": "P0056E_V2", "DayAhead_hourly_MAE": 125.21953299342522, "full_36h_MAE": 123.509}
    return {"baseline_name": "P0056E_V8", "DayAhead_hourly_MAE": 206.52148722664296, "full_36h_MAE": 197.676}


def peak_efficiency_decision(results: list[dict[str, object]], marginal: list[dict[str, object]]) -> dict[str, object]:
    decisions = {}
    for area in SCOPED_AREAS:
        rows = sorted([row for row in results if row["area_code"] == area], key=lambda row: int(str(row["weather_stack_id"])[1:]))
        if not rows:
            decisions[area] = {"decision": "no_results"}
            continue
        best = min(rows, key=lambda row: float(row["DayAhead_hourly_MAE"]))
        best_mae = float(best["DayAhead_hourly_MAE"])
        within = [row for row in rows if (float(row["DayAhead_hourly_MAE"]) - best_mae) / best_mae * 100.0 <= 0.5]
        smallest_within = min(within, key=lambda row: int(row["weather_feature_count"]))
        area_marginal = [row for row in marginal if row["area_code"] == area]
        negative = next((row for row in area_marginal if row.get("delta_MAE_vs_previous_stack") is not None and float(row["delta_MAE_vs_previous_stack"]) > 0.0), None)
        small_gain = next((row for row in area_marginal if row.get("delta_MAE_percent_vs_previous_stack") is not None and abs(float(row["delta_MAE_percent_vs_previous_stack"])) < 0.2), None)
        baseline = current_best_baseline(area)
        improves_baseline = (float(baseline["DayAhead_hourly_MAE"]) - best_mae) / float(baseline["DayAhead_hourly_MAE"]) * 100.0
        feature_reduction = 1.0 - (float(smallest_within["weather_feature_count"]) / 13.0)
        candidate = improves_baseline >= 1.0 or (((float(smallest_within["DayAhead_hourly_MAE"]) - best_mae) / best_mae * 100.0) <= 0.5 and feature_reduction >= 0.5)
        decisions[area] = {
            "best_holdout_weather_stack": best["weather_stack_id"],
            "best_holdout_dayahead_mae": best_mae,
            "best_internal_validation_weather_stack": "not_computed_holdout_exploratory_only",
            "smallest_stack_within_0_5_percent_of_best": smallest_within["weather_stack_id"],
            "first_stack_where_marginal_gain_turns_negative": negative.get("weather_stack_id") if negative else None,
            "first_stack_where_marginal_gain_lt_0_2_percent": small_gain.get("weather_stack_id") if small_gain else None,
            "candidate_default_weather_stack": best["weather_stack_id"] if candidate else None,
            "decision": "candidate_default_weather_stack" if candidate else "keep_current_weather_feature_set",
            "exploratory_holdout_selection": True,
        }
    return decisions


def leakage_review(feature_sets: list[list[str]]) -> dict[str, object]:
    forbidden = ("price", "spot", "flow", "exchange", "net_position", "a61", "capacity", "physical_balance", "future_actual")
    features = sorted({feature for group in feature_sets for feature in group})
    forbidden_features = [feature for feature in features if any(term in feature.lower() for term in forbidden)]
    fixed = fixed_non_weather_features()
    fixed_identical = all([feature for feature in group if not feature.startswith("weather_proxy_")] == fixed for group in feature_sets)
    return {
        "ok": not forbidden_features and fixed_identical,
        "forbidden_features": forbidden_features,
        "fixed_non_weather_features_identical": fixed_identical,
        "holdout_selection_label": "LABB exploratory; no production selection claim",
        "spot_price_feature_used": False,
        "flow_exchange_a61_capacity_feature_used": False,
        "old_physical_balance_target_used": False,
        "future_actual_load_feature_used": False,
    }


def decide_status(results: list[dict[str, object]], failed: list[dict[str, object]], leakage: dict[str, object]) -> str:
    if not leakage["ok"] or any(len([row for row in results if row["area_code"] == area]) < 13 for area in SCOPED_AREAS):
        return "STOP"
    return "WARN" if failed or True else "PASS"


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {FORECAST_TABLE} (
            forecast_origin_timestamp_utc TEXT NOT NULL,
            input_data_cutoff_utc TEXT NOT NULL,
            target_timestamp_utc TEXT NOT NULL,
            horizon_hours INTEGER NOT NULL,
            area_code TEXT NOT NULL,
            weather_stack_id TEXT NOT NULL,
            model_name TEXT NOT NULL,
            prediction_kind TEXT NOT NULL,
            predicted_consumption_mw REAL NOT NULL,
            actual_consumption_mw REAL NOT NULL,
            evaluation_scope TEXT NOT NULL,
            split TEXT NOT NULL,
            weather_proxy_version TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (forecast_origin_timestamp_utc, target_timestamp_utc, area_code, weather_stack_id, generated_by_package)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {METRICS_TABLE} (
            area_code TEXT NOT NULL,
            weather_stack_id TEXT NOT NULL,
            model_name TEXT NOT NULL,
            metric_scope TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL,
            metric_text TEXT,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (area_code, weather_stack_id, metric_scope, metric_name, generated_by_package)
        )
        """
    )
    conn.commit()


def persist_stack_outputs(conn: sqlite3.Connection, area_code: str, stack: WeatherStack, rows: list[dict[str, object]], prediction_column: str, metrics: dict[str, object]) -> None:
    selected_ids = {(str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"])) for row in p0054q.selected_full36_rows(rows) + p0054q.selected_dayahead_rows(rows)}
    forecast_rows = []
    for row in rows:
        key = (str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"]))
        if row.get("split") == "holdout" and row.get(prediction_column) is not None and key in selected_ids:
            forecast_rows.append((row["forecast_origin_timestamp_utc"], row["input_data_cutoff_utc"], row["target_timestamp_utc"], int(row["horizon_hours"]), area_code, stack.stack_id, MODEL_NAME, "consumption_mw", float(row[prediction_column]), float(row[p0054k.TARGET_FIELD]), "dayahead_or_full36", row["split"], "P0056D", PACKAGE_ID))
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {FORECAST_TABLE}
        (forecast_origin_timestamp_utc, input_data_cutoff_utc, target_timestamp_utc, horizon_hours,
         area_code, weather_stack_id, model_name, prediction_kind, predicted_consumption_mw,
         actual_consumption_mw, evaluation_scope, split, weather_proxy_version, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        forecast_rows,
    )
    metric_rows = []
    for scope in ("dayahead", "full36", "daily_energy", "horizon_slices", "regimes"):
        for name, value in p0056c.flatten_metrics(metrics.get(scope, {})).items():  # type: ignore[arg-type]
            metric_value = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None
            metric_text = None if metric_value is not None else json.dumps(json_safe(value), sort_keys=True)
            metric_rows.append((area_code, stack.stack_id, MODEL_NAME, scope, name, metric_value, metric_text, PACKAGE_ID))
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {METRICS_TABLE}
        (area_code, weather_stack_id, model_name, metric_scope, metric_name, metric_value, metric_text, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        metric_rows,
    )
    conn.commit()


def scoped_contract(contract: dict[str, object]) -> dict[str, object]:
    areas = contract.get("areas", {})
    scoped = {area: areas.get(area, {}) for area in SCOPED_AREAS} if isinstance(areas, dict) else {}
    return {**contract, "areas": scoped, "ok": all(scoped.get(area, {}).get("rows", 0) > 0 for area in SCOPED_AREAS)}


def stopped_summary(started: float, feature_path: Path, input_contract: dict[str, object]) -> dict[str, object]:
    return {"package_id": PACKAGE_ID, "label": LABEL, "status": "STOP", "runtime_seconds": round(time.monotonic() - started, 3), "feature_db": str(feature_path), "input_contract": input_contract, "row_counts": {}}


def reset_progress_log(evidence_dir: Path) -> None:
    write(evidence_dir / "progress-log.md", "# P0056F Progress Log\n\n")


def progress(evidence_dir: Path, area_code: str, stack_id: str, phase: str, status: str, *, started_at: str | None = None, extra: dict[str, object] | None = None) -> dict[str, object]:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    elapsed = None if not started_at else (p0052.parse_utc(now) - p0052.parse_utc(started_at)).total_seconds()
    parts = [f"[P0056F progress] area={area_code}", f"stack={stack_id}", f"phase={phase}", f"status={status}"]
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
    return {"area_code": area_code, "weather_stack_id": stack_id, "phase": phase, "status": status, "timestamp": now, "elapsed_seconds": elapsed, **(extra or {})}


def write_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    results = summary.get("feature_ablation_results", [])
    marginal = summary.get("marginal_gain_rows", [])
    comparison = summary.get("comparison_rows", [])
    evidence = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog_md(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", "# P0056F LABB Label\n\nP0056F is LABB-only exploratory weather feature ablation, not G2-KANDIDAT or production selection.\n"),
        "baseline-review.md": write(evidence_dir / "baseline-review.md", json_report("P0056F Baseline Review", {"P0056C": p0056e.P0056C_BASELINES, "P0056D": p0056e.P0056D_BASELINES, "P0056E_current_best": {area: current_best_baseline(area) for area in SCOPED_AREAS}})),
        "input-source-contract.md": write(evidence_dir / "input-source-contract.md", json_report("P0056F Input Source Contract", summary.get("input_contract", {}))),
        "split-policy-applied.md": write(evidence_dir / "split-policy-applied.md", json_report("P0056F Split Policy Applied", summary.get("split_policy", {}))),
        "weather-signal-order.md": write(evidence_dir / "weather-signal-order.md", json_report("P0056F Weather Signal Order", summary.get("weather_signal_order", []))),
        "weather-stack-contract.md": write(evidence_dir / "weather-stack-contract.md", json_report("P0056F Weather Stack Contract", summary.get("weather_stacks", []))),
        "feature-ablation-results.md": write(evidence_dir / "feature-ablation-results.md", results_md(results)),
        "area-results.md": write(evidence_dir / "area-results.md", area_results_md(results)),
        "marginal-gain-analysis.md": write(evidence_dir / "marginal-gain-analysis.md", marginal_md(marginal)),
        "peak-efficiency-decision.md": write(evidence_dir / "peak-efficiency-decision.md", json_report("P0056F Peak Efficiency Decision", summary.get("peak_efficiency_decision", {}))),
        "comparison-vs-baseline.md": write(evidence_dir / "comparison-vs-baseline.md", comparison_md(comparison)),
        "leakage-review.md": write(evidence_dir / "leakage-review.md", json_report("P0056F Leakage Review", summary.get("leakage_review", {}))),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", what_we_learned_md(summary)),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", "# P0056F Next Package Recommendation\n\nRecommended next package: validate promising compact weather stacks with nested validation or rolling-origin selection before any candidate-default claim.\n"),
        "feature-ablation-results.csv": write_csv(evidence_dir / "feature-ablation-results.csv", results),
        "marginal-gain-analysis.csv": write_csv(evidence_dir / "marginal-gain-analysis.csv", marginal),
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(json_safe(compact_summary(summary)), indent=2, sort_keys=True) + "\n"),
    }
    return evidence


def changelog_md(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0056F Changelog",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Stack results: `{len(summary.get('feature_ablation_results', []))}`",
        f"- Failed stacks: `{len(summary.get('failed_stacks', []))}`",
        f"- Forecast log rows: `{summary.get('row_counts', {}).get('forecast_log_rows', 0)}`",
        f"- Metrics rows: `{summary.get('row_counts', {}).get('metrics_rows', 0)}`",
        "- Scope: SE1 and SE2 only.",
        "- Result is LABB exploratory holdout ablation, not production selection.",
        "- No devices, runtime changes, production activation, external live data, spot price, flow/exchange/A61/capacity or future actual load leakage.",
        "",
    ])


def results_md(rows: object) -> str:
    lines = ["# P0056F Feature Ablation Results", "", "| area | stack | weather_count | DayAhead MAE | full36 MAE | daily energy % |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('area_code')} | {row.get('weather_stack_id')} | {row.get('weather_feature_count')} | {fmt(row.get('DayAhead_hourly_MAE'))} | {fmt(row.get('full_36h_MAE'))} | {fmt(row.get('daily_energy_error_percent_of_actual'))} |")
    lines.append("")
    return "\n".join(lines)


def area_results_md(rows: object) -> str:
    lines = ["# P0056F Area Results", "", "| area | best stack | best DayAhead MAE | best full36 MAE |", "| --- | --- | ---: | ---: |"]
    for area in SCOPED_AREAS:
        area_rows = [row for row in rows if isinstance(rows, list) and row.get("area_code") == area]
        if area_rows:
            best = min(area_rows, key=lambda row: float(row["DayAhead_hourly_MAE"]))
            lines.append(f"| {area} | {best.get('weather_stack_id')} | {fmt(best.get('DayAhead_hourly_MAE'))} | {fmt(best.get('full_36h_MAE'))} |")
    lines.append("")
    return "\n".join(lines)


def marginal_md(rows: object) -> str:
    lines = ["# P0056F Marginal Gain Analysis", "", "| area | stack | delta vs previous | delta % previous | delta vs W0 | delta vs current best |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('area_code')} | {row.get('weather_stack_id')} | {fmt(row.get('delta_MAE_vs_previous_stack'))} | {fmt(row.get('delta_MAE_percent_vs_previous_stack'))} | {fmt(row.get('delta_MAE_vs_W0'))} | {fmt(row.get('delta_MAE_vs_current_best'))} |")
    lines.append("")
    return "\n".join(lines)


def comparison_md(rows: object) -> str:
    lines = ["# P0056F Comparison Vs Baseline", "", "| area | stack | baseline | delta DayAhead MW | delta DayAhead % | delta full36 MW | delta full36 % |", "| --- | --- | --- | ---: | ---: | ---: | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('area_code')} | {row.get('weather_stack_id')} | {row.get('baseline_name')} | {fmt(row.get('delta_vs_baseline_DayAhead_MW'))} | {fmt(row.get('delta_vs_baseline_DayAhead_percent'))} | {fmt(row.get('delta_vs_baseline_full36_MW'))} | {fmt(row.get('delta_vs_baseline_full36_percent'))} |")
    lines.append("")
    return "\n".join(lines)


def what_we_learned_md(summary: dict[str, object]) -> str:
    decision = summary.get("peak_efficiency_decision", {})
    return "\n".join([
        "# P0056F What We Learned",
        "",
        f"- SE1 best stack: `{decision.get('SE1', {}).get('best_holdout_weather_stack') if isinstance(decision, dict) else ''}`.",
        f"- SE2 best stack: `{decision.get('SE2', {}).get('best_holdout_weather_stack') if isinstance(decision, dict) else ''}`.",
        "- Holdout stack choice is exploratory and requires nested validation before promotion.",
        "",
    ])


def compact_summary(summary: dict[str, object]) -> dict[str, object]:
    return {key: summary.get(key) for key in ("status", "row_counts", "failed_stacks", "peak_efficiency_decision", "leakage_review", "feature_ablation_results", "marginal_gain_rows", "comparison_rows")}


def write_csv(path: Path, rows: object) -> str:
    typed_rows = list(rows) if isinstance(rows, list) else []
    keys: list[str] = []
    for row in typed_rows:
        if isinstance(row, dict):
            for key in row:
                if key not in keys and key not in {"regimes"}:
                    keys.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        for row in typed_rows:
            writer.writerow({key: json_safe(row.get(key)) if isinstance(row, dict) else "" for key in keys})
    return str(path)


def json_report(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(json_safe(payload), indent=2, sort_keys=True)}\n```\n"


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {table} WHERE generated_by_package=?", (PACKAGE_ID,)).fetchone()[0] or 0)


def fmt(value: object) -> str:
    if value is None:
        return ""
    return f"{float(value):.3f}"


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if isinstance(value, float):
        return value if value == value else None
    return str(value)


def main() -> int:
    result = run_p0056f_weather_ablation()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
