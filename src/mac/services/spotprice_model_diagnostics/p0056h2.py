"""P0056H2 LABB 36h static-style lag comparison."""

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

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0056c, p0056d, p0056f, p0056h
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write


PACKAGE_ID = "P0056H2"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0056H2")
MODEL_NAME = "P0056H2_HGB_no_price_static_style_lags"
PREDICTION_COLUMN = p0054k.prediction_column(MODEL_NAME)
FORECAST_TABLE = "area_consumption_36h_static_style_forecast_log_p0056h2_v1"
METRICS_TABLE = "area_consumption_36h_static_style_metrics_p0056h2_v1"
SCOPED_AREAS = p0056h.SCOPED_AREAS
LAG_FEATURES = [f"area_consumption_lag_{lag}h" for lag in p0054k.LAGS]
ROLLING_FEATURES = [f"area_consumption_roll_mean_{window}h" for window in p0054k.ROLL_WINDOWS] + [
    "area_consumption_roll_min_24h",
    "area_consumption_roll_max_24h",
    "area_consumption_roll_std_24h",
    "area_consumption_ramp_1h",
    "area_consumption_ramp_24h",
    "area_consumption_same_hour_24h_vs_168h",
]
STATIC_STYLE_FEATURES = LAG_FEATURES + ROLLING_FEATURES

STATIC_BASELINES = p0056h.STATIC_BASELINES
P0056G_WEEKLY = p0056h.P0056G_WEEKLY
P0056H_L2 = {
    "SE1": {"baseline_name": "P0056H_L2_recursive_lags", "MAE": 138.317},
    "SE2": {"baseline_name": "P0056H_L2_recursive_lags", "MAE": 242.579},
    "SE3": {"baseline_name": "P0056H_L2_recursive_lags", "MAE": 361.881},
    "FI": {"baseline_name": "P0056H_L2_recursive_lags", "MAE": 367.057},
}


@dataclass(frozen=True)
class P0056H2Result:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0056h2_static_style_lag_comparison(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0056H2Result:
    started = time.monotonic()
    feature_path = Path(feature_db).expanduser()
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)
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
        target_contract = p0056h.scoped_contract(target_contract_all, SCOPED_AREAS)
        p0056b_contract = p0056h.scoped_contract(p0056b_contract_all, SCOPED_AREAS)
        p0056d_contract = p0056h.scoped_contract(p0056d_contract_all, ("SE1", "SE2", "FI"))
        input_contract = {
            "ok": bool(target_contract["ok"]) and bool(p0056b_contract["ok"]) and bool(p0056d_contract["ok"]),
            "target_contract": target_contract,
            "p0056b_weather_contract": p0056b_contract,
            "p0056d_weather_contract": p0056d_contract,
        }
        if not input_contract["ok"]:
            summary = stopped_summary(started, feature_path, input_contract)
            evidence = write_evidence(evidence_path, summary)
            return P0056H2Result("STOP", {}, evidence)

        weather_by_area = {
            "SE1": p0056d_weather_all["SE1"],
            "SE2": p0056d_weather_all["SE2"],
            "SE3": p0056b_weather_all["SE3"],
            "FI": p0056d_weather_all["FI"],
        }
        weather_source_by_area = {"SE1": "P0056D", "SE2": "P0056D", "SE3": "P0056B", "FI": "P0056D"}
        origins = p0056h_origins(target_contract, p0056b_contract, p0056d_contract)
        modeling_origins = p0056h.anchored_historical_origin_schedule(date(2022, 6, 1), origins[-1].origin_local if origins else p0056h.PRIMARY_START_LOCAL, p0056h.PRIMARY_START_LOCAL)
        environment = p0054k.capture_environment_status()
        hgb_spec = next(spec for spec in p0054k.model_specs(environment["imports"]) if spec.family == "HGB")  # type: ignore[arg-type]
        features_by_area = feature_contract_by_area()

        origin_results: list[dict[str, object]] = []
        skipped_windows: list[dict[str, object]] = []
        failures: list[dict[str, object]] = []
        lag_checks: list[dict[str, object]] = []
        total_jobs = len(SCOPED_AREAS) * len(origins)

        for area_code in SCOPED_AREAS:
            target_rows = targets_all[area_code]
            weather_rows = weather_by_area[area_code]
            base_rows = build_static_style_modeling_rows(area_code, target_rows, weather_rows, modeling_origins, weather_source_by_area[area_code])
            rows_by_origin: dict[str, list[dict[str, object]]] = defaultdict(list)
            for row in base_rows:
                rows_by_origin[str(row["forecast_origin_timestamp_utc"])].append(row)
            features = features_by_area[area_code]
            for origin in origins:
                origin_rows = [dict(row) for row in rows_by_origin.get(origin.origin_utc, [])]
                train_rows = [dict(row) for row in base_rows if str(row["target_timestamp_utc"]) < origin.origin_utc]
                if len(origin_rows) != 36:
                    skipped_windows.append({
                        "area_code": area_code,
                        "origin": origin.origin_local.isoformat(),
                        "forecast_origin_utc": origin.origin_utc,
                        "available_forecast_rows": len(origin_rows),
                        "expected_forecast_rows": 36,
                    })
                    continue
                try:
                    p0056h.apply_weather_profile_features(train_rows, origin_rows)
                    fit = p0056h.fit_hgb(train_rows, features, hgb_spec)
                    p0056h.predict_rows(fit, origin_rows, features)
                    for row in origin_rows:
                        row[P0056H2_prediction_column_alias()] = float(row[p0056h.PREDICTION_COLUMN])
                        row[PREDICTION_COLUMN] = float(row[p0056h.PREDICTION_COLUMN])
                    metrics = p0056h.score_origin(origin_rows, PREDICTION_COLUMN)
                    result = origin_result_row(area_code, origin, metrics, fit, weather_source_by_area[area_code])
                    origin_results.append(result)
                    lag_checks.append(static_lag_check_row(area_code, origin, origin_rows))
                    persist_origin_outputs(conn, area_code, origin, origin_rows, result)
                except Exception as exc:  # pragma: no cover - package evidence path
                    failures.append({"area_code": area_code, "origin": origin.origin_local.isoformat(), "error_type": type(exc).__name__, "error": str(exc)[:600]})

        area_summaries = aggregate_area_results(origin_results)
        summary = {
            "package_id": PACKAGE_ID,
            "label": LABEL,
            "status": decide_status(area_summaries, failures),
            "runtime_seconds": round(time.monotonic() - started, 3),
            "feature_db": str(feature_path),
            "areas": SCOPED_AREAS,
            "origins": [origin.__dict__ for origin in origins],
            "input_contract": input_contract,
            "weather_protocol": {"weather_protocol": "actual_weather_proxy_LABB", "weather_source_by_area": weather_source_by_area},
            "model_method_contract": model_method_contract(features_by_area),
            "static_style_lag_contract": static_style_lag_contract(),
            "static_baselines": STATIC_BASELINES,
            "p0056h_l2_baselines": P0056H_L2,
            "p0056g_weekly_baselines": P0056G_WEEKLY,
            "skipped_incomplete_origin_windows": skipped_windows,
            "failures": failures,
            "origin_results": origin_results,
            "area_summary_results": area_summaries,
            "comparison_vs_static_baseline": compare_baseline(area_summaries, STATIC_BASELINES, "full_36h_MAE", "static_full36_MAE", "delta_vs_static_percent"),
            "comparison_vs_p0056h": compare_baseline(area_summaries, P0056H_L2, "MAE", "p0056h_l2_MAE", "delta_vs_p0056h_percent"),
            "comparison_vs_p0056g_weekly": compare_baseline(area_summaries, P0056G_WEEKLY, "MAE", "p0056g_weekly_MAE_162h", "delta_vs_p0056g_percent"),
            "lag_feature_check": lag_feature_check(lag_checks),
            "row_counts": {
                "origins": len(origins),
                "scheduled_origin_jobs": total_jobs,
                "skipped_incomplete_origin_windows": len(skipped_windows),
                "origin_results": len(origin_results),
                "expected_origin_results": total_jobs - len(skipped_windows),
                "failed_jobs": len(failures),
                "forecast_log_rows": table_count(conn, FORECAST_TABLE),
                "metrics_rows": table_count(conn, METRICS_TABLE),
            },
            "no_api": True,
            "no_devices": True,
            "no_runtime_change": True,
            "no_production_activation": True,
            "no_spot_price_features": True,
            "no_flow_exchange_a61_capacity_features": True,
            "no_old_physical_balance_target": True,
            "no_large_artifacts": True,
        }
        persist_summary_metrics(conn, summary)
        summary["row_counts"]["metrics_rows"] = table_count(conn, METRICS_TABLE)  # type: ignore[index]
        evidence = write_evidence(evidence_path, summary)
        return P0056H2Result(str(summary["status"]), summary["row_counts"], evidence)  # type: ignore[arg-type]


def p0056h_origins(target_contract: dict[str, object], p0056b_contract: dict[str, object], p0056d_contract: dict[str, object]) -> list[p0056h.OriginWindow]:
    return p0056h.origin_schedule(target_contract, p0056b_contract, p0056d_contract)


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {FORECAST_TABLE} (
            forecast_origin_timestamp_utc TEXT NOT NULL,
            target_timestamp_utc TEXT NOT NULL,
            horizon_hours INTEGER NOT NULL,
            area_code TEXT NOT NULL,
            model_name TEXT NOT NULL,
            prediction_kind TEXT NOT NULL,
            predicted_consumption_mw REAL NOT NULL,
            actual_consumption_mw REAL NOT NULL,
            weather_protocol TEXT NOT NULL,
            weather_source_package TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (forecast_origin_timestamp_utc, target_timestamp_utc, area_code, model_name, generated_by_package)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {METRICS_TABLE} (
            area_code TEXT NOT NULL,
            origin_id TEXT NOT NULL,
            metric_scope TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL,
            metric_text TEXT,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (area_code, origin_id, metric_scope, metric_name, generated_by_package)
        )
        """
    )
    conn.commit()


def build_static_style_modeling_rows(
    area_code: str,
    target_rows: list[dict[str, object]],
    weather_rows: dict[str, dict[str, object]],
    origins: list[p0056h.OriginWindow],
    weather_source: str,
) -> list[dict[str, object]]:
    source_by_ts = {str(row["timestamp_utc"]): row for row in target_rows}
    source_index = {str(row["timestamp_utc"]): index for index, row in enumerate(target_rows)}
    values = [float(row["consumption_mw"]) for row in target_rows]
    required_history = max(max(p0054k.LAGS), max(p0054k.ROLL_WINDOWS))
    rows = []
    for origin in origins:
        origin_index = source_index.get(origin.origin_utc)
        if origin_index is None or origin_index < required_history:
            continue
        lag_features = static_style_lag_features_at_origin(values, origin_index)
        origin_dt = p0052.parse_utc(origin.origin_utc)
        for horizon in p0056h.HORIZONS_36:
            target_ts = p0056h.format_dt_utc(origin_dt + timedelta(hours=horizon))
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
                "prediction_kind": "consumption_mw_static_style_origin_lags_actual_weather_proxy_labb",
                "dataset_kind": "offline_labb_36h_static_style_lag_comparison_not_deployable",
                "weather_source_generated_by_package": weather_source,
                "weather_protocol": "actual_weather_proxy_LABB",
                "split": "rolling_origin",
            }
            p0054k.attach_calendar_features(row, p0052.parse_utc(target_ts) + timedelta(hours=1))
            row.update(lag_features)
            row.update(weather)
            rows.append(row)
    return rows


def static_style_lag_features_at_origin(values: list[float], origin_index: int) -> dict[str, float]:
    return {**p0056c.area_lag_features_at_origin(values, origin_index), **p0056c.area_rolling_features_at_origin(values, origin_index)}


def feature_contract_by_area() -> dict[str, list[str]]:
    return {
        "SE1": p0056f.feature_names_for_stack("W10"),
        "SE2": p0056f.feature_names_for_stack("W12"),
        "SE3": p0056c.p0056c_feature_names(),
        "FI": p0056c.p0056c_feature_names(),
    }


def P0056H2_prediction_column_alias() -> str:
    return p0056h.PREDICTION_COLUMN


def origin_result_row(area_code: str, origin: p0056h.OriginWindow, metrics: dict[str, dict[str, object]], fit: dict[str, object], weather_source: str) -> dict[str, object]:
    total = metrics["MAE_0_36h"]
    return {
        "area_code": area_code,
        "origin_id": origin.origin_id,
        "forecast_origin_local": origin.origin_local.isoformat(),
        "forecast_origin_utc": origin.origin_utc,
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


def aggregate_area_results(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for area in SCOPED_AREAS:
        selected = [row for row in rows if row["area_code"] == area]
        maes = [float(row["MAE_0_36h"]) for row in selected if row.get("MAE_0_36h") is not None]
        maes24 = [float(row["MAE_0_24h"]) for row in selected if row.get("MAE_0_24h") is not None]
        maes2436 = [float(row["MAE_24_36h"]) for row in selected if row.get("MAE_24_36h") is not None]
        actual_weight = sum(float(row.get("mean_actual_mw") or 0.0) * int(row.get("forecast_rows") or 0) for row in selected)
        abs_weight = sum(float(row.get("MAE_0_36h") or 0.0) * int(row.get("forecast_rows") or 0) for row in selected)
        out.append({
            "area_code": area,
            "origin_count": len(selected),
            "mean_MAE_0_36h": p0054k.mean_float(maes) if maes else None,
            "median_MAE_0_36h": percentile(maes, 0.5) if maes else None,
            "mean_MAE_0_24h": p0054k.mean_float(maes24) if maes24 else None,
            "mean_MAE_24_36h": p0054k.mean_float(maes2436) if maes2436 else None,
            "weighted_MAE_percent_of_mean_load": abs_weight / actual_weight * 100.0 if actual_weight else None,
        })
    return out


def compare_baseline(summaries: list[dict[str, object]], baselines: dict[str, dict[str, float | str]], source_key: str, baseline_label: str, delta_label: str) -> list[dict[str, object]]:
    out = []
    for row in summaries:
        area = str(row["area_code"])
        mae = float(row["mean_MAE_0_36h"]) if row.get("mean_MAE_0_36h") is not None else math.nan
        base = float(baselines[area][source_key])
        out.append({
            "area_code": area,
            baseline_label: base,
            "p0056h2_static_style_MAE": mae,
            "delta_MW": mae - base,
            delta_label: (mae - base) / base * 100.0 if base else None,
            "baseline_name": baselines[area].get("baseline_name", "baseline"),
        })
    return out


def static_lag_check_row(area_code: str, origin: p0056h.OriginWindow, rows: list[dict[str, object]]) -> dict[str, object]:
    stable = True
    first = rows[0] if rows else {}
    for feature in STATIC_STYLE_FEATURES:
        values = {row.get(feature) for row in rows}
        stable = stable and len(values) == 1
    return {"area_code": area_code, "origin_id": origin.origin_id, "rows": len(rows), "static_features_constant_across_horizon": stable, "sample_lag_1h": first.get("area_consumption_lag_1h")}


def lag_feature_check(rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "required_features": STATIC_STYLE_FEATURES,
        "feature_count": len(STATIC_STYLE_FEATURES),
        "static_features_constant_across_horizon": all(bool(row.get("static_features_constant_across_horizon")) for row in rows),
        "origin_windows_checked": len(rows),
    }


def static_style_lag_contract() -> dict[str, object]:
    return {
        "contract": "P0056C_static_style_origin_anchored_lags",
        "origin_lag_source": "known historical load before forecast origin",
        "same_feature_values_across_36h_horizon": True,
        "target_hour_actual_lags_used": False,
        "feature_names": STATIC_STYLE_FEATURES,
    }


def model_method_contract(features_by_area: dict[str, list[str]]) -> dict[str, object]:
    return {
        "model_name": MODEL_NAME,
        "model_family": "HGB",
        "method_note": "P0056H2 uses the tractable P0056H HGB no-price fit to isolate static-style lag feature construction.",
        "feature_counts_by_area": {area: len(features) for area, features in features_by_area.items()},
        "spot_price_features": False,
        "flow_exchange_a61_capacity_features": False,
    }


def decide_status(summaries: list[dict[str, object]], failures: list[dict[str, object]]) -> str:
    if failures or any(int(row.get("origin_count") or 0) == 0 for row in summaries):
        return "STOP"
    return "WARN"


def persist_origin_outputs(conn: sqlite3.Connection, area_code: str, origin: p0056h.OriginWindow, rows: list[dict[str, object]], result: dict[str, object]) -> None:
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {FORECAST_TABLE}
        (forecast_origin_timestamp_utc, target_timestamp_utc, horizon_hours, area_code,
         model_name, prediction_kind, predicted_consumption_mw, actual_consumption_mw,
         weather_protocol, weather_source_package, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["forecast_origin_timestamp_utc"],
                row["target_timestamp_utc"],
                int(row["horizon_hours"]),
                area_code,
                MODEL_NAME,
                row["prediction_kind"],
                float(row[PREDICTION_COLUMN]),
                float(row[p0054k.TARGET_FIELD]),
                row["weather_protocol"],
                row["weather_source_generated_by_package"],
                PACKAGE_ID,
            )
            for row in rows
        ],
    )
    metric_rows = []
    for name, value in result.items():
        if name in {"area_code", "origin_id"}:
            continue
        metric_value = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) else None
        metric_text = None if metric_value is not None else json.dumps(p0056h.json_safe(value), sort_keys=True)
        metric_rows.append((area_code, origin.origin_id, "origin", name, metric_value, metric_text, PACKAGE_ID))
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {METRICS_TABLE}
        (area_code, origin_id, metric_scope, metric_name, metric_value, metric_text, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?)
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
            if name == "area_code":
                continue
            metric_value = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) else None
            metric_text = None if metric_value is not None else json.dumps(p0056h.json_safe(value), sort_keys=True)
            rows.append((area["area_code"], "ALL", "area_summary", name, metric_value, metric_text, PACKAGE_ID))
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {METRICS_TABLE}
        (area_code, origin_id, metric_scope, metric_name, metric_value, metric_text, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()


def write_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog_md(summary)),
        "static-style-lag-contract.md": write(evidence_dir / "static-style-lag-contract.md", json_report("P0056H2 Static-Style Lag Contract", summary.get("static_style_lag_contract", {}))),
        "lag-feature-list.md": write(evidence_dir / "lag-feature-list.md", lag_feature_list_md(summary.get("lag_feature_check", {}))),
        "area-summary-results.md": write(evidence_dir / "area-summary-results.md", area_summary_md(summary.get("area_summary_results", []))),
        "comparison-vs-static-baseline.md": write(evidence_dir / "comparison-vs-static-baseline.md", comparison_md(summary.get("comparison_vs_static_baseline", []), "static_full36_MAE", "delta_vs_static_percent")),
        "comparison-vs-p0056h.md": write(evidence_dir / "comparison-vs-p0056h.md", comparison_md(summary.get("comparison_vs_p0056h", []), "p0056h_l2_MAE", "delta_vs_p0056h_percent")),
        "comparison-vs-p0056g-weekly.md": write(evidence_dir / "comparison-vs-p0056g-weekly.md", comparison_md(summary.get("comparison_vs_p0056g_weekly", []), "p0056g_weekly_MAE_162h", "delta_vs_p0056g_percent")),
        "interpretation.md": write(evidence_dir / "interpretation.md", interpretation_md(summary)),
        "decision.md": write(evidence_dir / "decision.md", decision_md(summary)),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", next_package_recommendation_md(summary)),
        "origin-results.csv": write_csv(evidence_dir / "origin-results.csv", summary.get("origin_results", [])),
        "area-summary-results.csv": write_csv(evidence_dir / "area-summary-results.csv", summary.get("area_summary_results", [])),
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(p0056h.json_safe(compact_summary(summary)), indent=2, sort_keys=True) + "\n"),
    }
    return evidence


def changelog_md(summary: dict[str, object]) -> str:
    rows = summary.get("row_counts", {})
    return "\n".join([
        "# P0056H2 Changelog",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Origin results: `{rows.get('origin_results', 0) if isinstance(rows, dict) else 0}`",
        f"- Failed jobs: `{rows.get('failed_jobs', 0) if isinstance(rows, dict) else 0}`",
        "- Scope: SE1, SE2, SE3 and FI.",
        "- Static-style origin-anchored lag features implemented.",
        "- No API, devices, runtime changes, spot price, flow/exchange/A61/capacity or old physical_balance features.",
        "",
    ])


def lag_feature_list_md(check: object) -> str:
    data = check if isinstance(check, dict) else {}
    lines = ["# P0056H2 Lag Feature List", "", f"- Feature count: `{data.get('feature_count', len(STATIC_STYLE_FEATURES))}`", f"- Constant across 36h horizon check: `{data.get('static_features_constant_across_horizon')}`", ""]
    lines.extend(f"- `{feature}`" for feature in STATIC_STYLE_FEATURES)
    lines.append("")
    return "\n".join(lines)


def area_summary_md(rows: object) -> str:
    lines = ["# P0056H2 Area Summary Results", "", "| area | origins | mean MAE 0-36h | median MAE | MAE 0-24h | MAE 24-36h | weighted MAE % load |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('area_code')} | {row.get('origin_count')} | {p0056h.fmt(row.get('mean_MAE_0_36h'))} | {p0056h.fmt(row.get('median_MAE_0_36h'))} | {p0056h.fmt(row.get('mean_MAE_0_24h'))} | {p0056h.fmt(row.get('mean_MAE_24_36h'))} | {p0056h.fmt(row.get('weighted_MAE_percent_of_mean_load'))} |")
    lines.append("")
    return "\n".join(lines)


def comparison_md(rows: object, baseline_key: str, delta_key: str) -> str:
    lines = ["# P0056H2 Comparison", "", "| area | baseline | P0056H2 static-style MAE | delta MW | delta % |", "| --- | ---: | ---: | ---: | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('area_code')} | {p0056h.fmt(row.get(baseline_key))} | {p0056h.fmt(row.get('p0056h2_static_style_MAE'))} | {p0056h.fmt(row.get('delta_MW'))} | {p0056h.fmt(row.get(delta_key))} |")
    lines.append("")
    return "\n".join(lines)


def interpretation_md(summary: dict[str, object]) -> str:
    comparisons = summary.get("comparison_vs_static_baseline", [])
    recovered = [row for row in comparisons if isinstance(row, dict) and row.get("delta_vs_static_percent") is not None and float(row["delta_vs_static_percent"]) <= 1.0]
    return "\n".join([
        "# P0056H2 Interpretation",
        "",
        f"- Old static performance recovered within 1 percent for `{len(recovered)}` of `{len(comparisons) if isinstance(comparisons, list) else 0}` areas.",
        "- This isolates static-style origin-anchored lag construction against P0056H's rolling 36h protocol.",
        "- Actual-weather proxy remains LABB-only and is not production forecast weather.",
        "",
    ])


def decision_md(summary: dict[str, object]) -> str:
    lines = ["# P0056H2 Decision", "", f"- Status: `{summary.get('status')}`", "- Production readiness: not ready; LABB-only diagnostic.", ""]
    for row in summary.get("comparison_vs_static_baseline", []) if isinstance(summary.get("comparison_vs_static_baseline"), list) else []:
        verdict = "static_recovered" if row.get("delta_vs_static_percent") is not None and float(row["delta_vs_static_percent"]) <= 1.0 else "static_not_recovered"
        lines.append(f"- {row.get('area_code')}: {verdict}; delta `{p0056h.fmt(row.get('delta_vs_static_percent'))}%` vs static baseline.")
    lines.append("")
    return "\n".join(lines)


def next_package_recommendation_md(summary: dict[str, object]) -> str:
    return "# P0056H2 Next Package Recommendation\n\nIf static-style lags recover performance, run an exact P0056C weighted-ensemble rerun on the P0056H origin grid. If not, investigate split/evaluation definition differences and weather protocol before more lag engineering.\n"


def compact_summary(summary: dict[str, object]) -> dict[str, object]:
    return {
        "package_id": summary.get("package_id"),
        "status": summary.get("status"),
        "runtime_seconds": summary.get("runtime_seconds"),
        "row_counts": summary.get("row_counts"),
        "area_summary_results": summary.get("area_summary_results"),
        "comparison_vs_static_baseline": summary.get("comparison_vs_static_baseline"),
        "comparison_vs_p0056h": summary.get("comparison_vs_p0056h"),
        "comparison_vs_p0056g_weekly": summary.get("comparison_vs_p0056g_weekly"),
        "lag_feature_check": summary.get("lag_feature_check"),
    }


def stopped_summary(started: float, feature_path: Path, input_contract: dict[str, object]) -> dict[str, object]:
    return {"package_id": PACKAGE_ID, "label": LABEL, "status": "STOP", "runtime_seconds": round(time.monotonic() - started, 3), "feature_db": str(feature_path), "input_contract": input_contract, "row_counts": {}}


def json_report(title: str, value: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(p0056h.json_safe(value), indent=2, sort_keys=True)}\n```\n"


def write_csv(path: Path, rows: object) -> str:
    values = rows if isinstance(rows, list) else []
    if not values:
        return write(path, "")
    keys = sorted({key for row in values if isinstance(row, dict) for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        for row in values:
            writer.writerow({key: json.dumps(p0056h.json_safe(row.get(key)), sort_keys=True) if isinstance(row.get(key), (dict, list)) else row.get(key) for key in keys})
    return str(path)


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {table} WHERE generated_by_package=?", (PACKAGE_ID,)).fetchone()[0])


def main() -> None:
    result = run_p0056h2_static_style_lag_comparison()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
