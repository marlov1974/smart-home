"""P0056I LABB SE2 train-window sensitivity."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import csv
import json
import math
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0056c, p0056d, p0056f, p0056h, p0056h2
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write


PACKAGE_ID = "P0056I"
LABEL = "LABB"
AREA = "SE2"
EVIDENCE_DIR = Path("requirements/package-runs/P0056I")
MODEL_NAME = "P0056I_HGB_no_price_SE2_train_window"
PREDICTION_COLUMN = p0054k.prediction_column(MODEL_NAME)
FORECAST_TABLE = "area_consumption_36h_train_window_forecast_log_p0056i_v1"
METRICS_TABLE = "area_consumption_36h_train_window_metrics_p0056i_v1"
FIXED_EXPANDING_START_UTC = "2022-06-01T00:00:00Z"

TRAIN_WINDOW_VARIANTS = {
    "TW2": {"name": "rolling_2_years", "mode": "rolling_years", "years": 2},
    "TW3": {"name": "rolling_3_years", "mode": "rolling_years", "years": 3},
    "TWX": {"name": "expanding_from_2022_06_01", "mode": "expanding", "years": None},
}

BASELINES = {
    "P0056F_W12_static_full36": 197.547,
    "P0056H_L2_recursive_36h": 242.579,
    "P0056H2_static_style_36h": 228.549,
    "P0056G_weekly": 207.757,
}


@dataclass(frozen=True)
class P0056IResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0056i_train_window_sensitivity(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0056IResult:
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
        target_contract = p0056h.scoped_contract(target_contract_all, (AREA,))
        p0056b_contract = p0056h.scoped_contract(p0056b_contract_all, (AREA,))
        p0056d_contract = p0056h.scoped_contract(p0056d_contract_all, (AREA,))
        input_contract = {
            "ok": bool(target_contract["ok"]) and bool(p0056b_contract["ok"]) and bool(p0056d_contract["ok"]),
            "target_contract": target_contract,
            "p0056b_weather_contract": p0056b_contract,
            "p0056d_weather_contract": p0056d_contract,
        }
        if not input_contract["ok"]:
            summary = stopped_summary(started, feature_path, input_contract)
            evidence = write_evidence(evidence_path, summary)
            return P0056IResult("STOP", {}, evidence)

        origins = p0056h.origin_schedule(target_contract, p0056b_contract, p0056d_contract)
        modeling_origins = p0056i_modeling_origins(origins)
        base_rows = p0056h2.build_static_style_modeling_rows(AREA, targets_all[AREA], p0056d_weather_all[AREA], modeling_origins, "P0056D")
        rows_by_origin: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in base_rows:
            rows_by_origin[str(row["forecast_origin_timestamp_utc"])].append(row)

        environment = p0054k.capture_environment_status()
        hgb_spec = next(spec for spec in p0054k.model_specs(environment["imports"]) if spec.family == "HGB")  # type: ignore[arg-type]
        features = p0056f.feature_names_for_stack("W12")
        origin_results: list[dict[str, object]] = []
        skipped_windows: list[dict[str, object]] = []
        failures: list[dict[str, object]] = []

        for origin in origins:
            origin_rows_source = rows_by_origin.get(origin.origin_utc, [])
            if len(origin_rows_source) != 36:
                skipped_windows.append({
                    "origin_id": origin.origin_id,
                    "forecast_origin_utc": origin.origin_utc,
                    "available_forecast_rows": len(origin_rows_source),
                    "expected_forecast_rows": 36,
                })
                continue
            for variant_id, variant in TRAIN_WINDOW_VARIANTS.items():
                origin_rows = [dict(row) for row in origin_rows_source]
                train_rows = filter_train_rows_for_window(base_rows, origin.origin_utc, variant_id)
                try:
                    p0056h.apply_weather_profile_features(train_rows, origin_rows)
                    fit = p0056h.fit_hgb(train_rows, features, hgb_spec)
                    p0056h.predict_rows(fit, origin_rows, features)
                    for row in origin_rows:
                        row[PREDICTION_COLUMN] = float(row[p0056h.PREDICTION_COLUMN])
                    metrics = p0056h.score_origin(origin_rows, PREDICTION_COLUMN)
                    result = origin_result_row(variant_id, variant, origin, metrics, fit, train_rows)
                    origin_results.append(result)
                    persist_origin_outputs(conn, variant_id, origin, origin_rows, result)
                except Exception as exc:  # pragma: no cover - package evidence path
                    failures.append({"variant_id": variant_id, "origin_id": origin.origin_id, "forecast_origin_utc": origin.origin_utc, "error_type": type(exc).__name__, "error": str(exc)[:600]})

        window_summaries = aggregate_window_results(origin_results)
        comparison = compare_vs_baselines(window_summaries)
        decision = decide_preferred_window(window_summaries)
        summary = {
            "package_id": PACKAGE_ID,
            "label": LABEL,
            "status": decide_status(window_summaries, failures),
            "runtime_seconds": round(time.monotonic() - started, 3),
            "feature_db": str(feature_path),
            "area": AREA,
            "origins": [origin.__dict__ for origin in origins],
            "train_window_variants": TRAIN_WINDOW_VARIANTS,
            "input_contract": input_contract,
            "weather_protocol": {"weather_protocol": "actual_weather_proxy_LABB", "weather_source_by_area": {AREA: "P0056D"}},
            "model_method_contract": model_method_contract(features),
            "static_style_lag_contract": p0056h2.static_style_lag_contract(),
            "lag_feature_check": {"required_features": p0056h2.STATIC_STYLE_FEATURES, "feature_count": len(p0056h2.STATIC_STYLE_FEATURES), "static_features_constant_across_horizon": True},
            "baselines": BASELINES,
            "skipped_incomplete_origin_windows": skipped_windows,
            "failures": failures,
            "origin_results": origin_results,
            "window_summary_results": window_summaries,
            "comparison_vs_baselines": comparison,
            "decision": decision,
            "row_counts": {
                "origins": len(origins),
                "complete_origins": len({row["origin_id"] for row in origin_results}),
                "skipped_incomplete_origin_windows": len(skipped_windows),
                "variant_results": len(origin_results),
                "expected_variant_results": (len(origins) - len(skipped_windows)) * len(TRAIN_WINDOW_VARIANTS),
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
        return P0056IResult(str(summary["status"]), summary["row_counts"], evidence)  # type: ignore[arg-type]


def p0056i_modeling_origins(origins: list[p0056h.OriginWindow]) -> list[p0056h.OriginWindow]:
    latest = origins[-1].origin_local if origins else p0056h.PRIMARY_START_LOCAL
    return p0056h.anchored_historical_origin_schedule(date(2022, 6, 1), latest, p0056h.PRIMARY_START_LOCAL)


def train_window_start_utc(variant_id: str, origin_utc: str) -> str:
    if variant_id == "TWX":
        return FIXED_EXPANDING_START_UTC
    years = int(TRAIN_WINDOW_VARIANTS[variant_id]["years"] or 0)
    origin_dt = p0052.parse_utc(origin_utc)
    try:
        start_dt = origin_dt.replace(year=origin_dt.year - years)
    except ValueError:
        start_dt = origin_dt.replace(year=origin_dt.year - years, day=28)
    return p0056h.format_dt_utc(start_dt)


def filter_train_rows_for_window(rows: list[dict[str, object]], origin_utc: str, variant_id: str) -> list[dict[str, object]]:
    start_utc = train_window_start_utc(variant_id, origin_utc)
    return [dict(row) for row in rows if start_utc <= str(row["target_timestamp_utc"]) < origin_utc]


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {FORECAST_TABLE} (
            forecast_origin_timestamp_utc TEXT NOT NULL,
            target_timestamp_utc TEXT NOT NULL,
            horizon_hours INTEGER NOT NULL,
            area_code TEXT NOT NULL,
            train_window_variant TEXT NOT NULL,
            model_name TEXT NOT NULL,
            prediction_kind TEXT NOT NULL,
            predicted_consumption_mw REAL NOT NULL,
            actual_consumption_mw REAL NOT NULL,
            train_start_utc TEXT NOT NULL,
            train_end_utc TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (forecast_origin_timestamp_utc, target_timestamp_utc, area_code, train_window_variant, model_name, generated_by_package)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {METRICS_TABLE} (
            area_code TEXT NOT NULL,
            train_window_variant TEXT NOT NULL,
            origin_id TEXT NOT NULL,
            metric_scope TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL,
            metric_text TEXT,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (area_code, train_window_variant, origin_id, metric_scope, metric_name, generated_by_package)
        )
        """
    )
    conn.commit()


def origin_result_row(
    variant_id: str,
    variant: dict[str, object],
    origin: p0056h.OriginWindow,
    metrics: dict[str, dict[str, object]],
    fit: dict[str, object],
    train_rows: list[dict[str, object]],
) -> dict[str, object]:
    total = metrics["MAE_0_36h"]
    return {
        "area_code": AREA,
        "train_window_variant": variant_id,
        "train_window_name": variant["name"],
        "origin_id": origin.origin_id,
        "forecast_origin_local": origin.origin_local.isoformat(),
        "forecast_origin_utc": origin.origin_utc,
        "train_start": train_window_start_utc(variant_id, origin.origin_utc),
        "train_end": origin.origin_utc,
        "train_rows": fit["train_rows"],
        "raw_train_rows": len(train_rows),
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
    }


def aggregate_window_results(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for variant_id, variant in TRAIN_WINDOW_VARIANTS.items():
        selected = [row for row in rows if row["train_window_variant"] == variant_id]
        maes = [float(row["MAE_0_36h"]) for row in selected if row.get("MAE_0_36h") is not None]
        maes24 = [float(row["MAE_0_24h"]) for row in selected if row.get("MAE_0_24h") is not None]
        maes2436 = [float(row["MAE_24_36h"]) for row in selected if row.get("MAE_24_36h") is not None]
        energy = [float(row["energy_error_percent_36h"]) for row in selected if row.get("energy_error_percent_36h") is not None]
        bias_values = [float(row["bias_0_36h"]) for row in selected if row.get("bias_0_36h") is not None]
        actual_weight = sum(float(row.get("mean_actual_mw") or 0.0) * int(row.get("forecast_rows") or 0) for row in selected)
        abs_weight = sum(float(row.get("MAE_0_36h") or 0.0) * int(row.get("forecast_rows") or 0) for row in selected)
        out.append({
            "train_window_variant": variant_id,
            "train_window_name": variant["name"],
            "origin_count": len(selected),
            "mean_MAE_0_36h": p0054k.mean_float(maes) if maes else None,
            "median_MAE_0_36h": percentile(maes, 0.5) if maes else None,
            "mean_MAE_0_24h": p0054k.mean_float(maes24) if maes24 else None,
            "mean_MAE_24_36h": p0054k.mean_float(maes2436) if maes2436 else None,
            "weighted_MAE_percent_of_mean_load": abs_weight / actual_weight * 100.0 if actual_weight else None,
            "mean_energy_error_percent": p0054k.mean_float(energy) if energy else None,
            "bias_over_period": p0054k.mean_float(bias_values) if bias_values else None,
            "weekday_split": split_summary(selected, "origin_weekday"),
            "monthly_split": split_summary(selected, "origin_month"),
        })
    return out


def split_summary(rows: list[dict[str, object]], key: str) -> dict[str, dict[str, float | int]]:
    out: dict[str, dict[str, float | int]] = {}
    values: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row.get("MAE_0_36h") is not None:
            values[str(row[key])].append(float(row["MAE_0_36h"]))
    for split_key, maes in sorted(values.items()):
        out[split_key] = {"origin_count": len(maes), "mean_MAE_0_36h": p0054k.mean_float(maes)}
    return out


def compare_vs_baselines(summaries: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in summaries:
        mae = float(row["mean_MAE_0_36h"]) if row.get("mean_MAE_0_36h") is not None else math.nan
        for baseline_name, baseline_mae in BASELINES.items():
            out.append({
                "train_window_variant": row["train_window_variant"],
                "baseline_name": baseline_name,
                "baseline_MAE": baseline_mae,
                "p0056i_MAE": mae,
                "delta_MW": mae - baseline_mae,
                "delta_percent": (mae - baseline_mae) / baseline_mae * 100.0,
            })
    return out


def decide_preferred_window(summaries: list[dict[str, object]]) -> dict[str, object]:
    valid = [row for row in summaries if row.get("mean_MAE_0_36h") is not None]
    if not valid:
        return {"preferred_variant": None, "reason": "no_valid_results"}
    ordered = sorted(valid, key=lambda row: float(row["mean_MAE_0_36h"]))
    best = ordered[0]
    second = ordered[1] if len(ordered) > 1 else best
    best_mae = float(best["mean_MAE_0_36h"])
    second_mae = float(second["mean_MAE_0_36h"])
    relative_gain = (second_mae - best_mae) / second_mae * 100.0 if second_mae else 0.0
    if relative_gain >= 1.0:
        return {"preferred_variant": best["train_window_variant"], "reason": "mae_improves_by_at_least_1_percent", "relative_gain_percent": relative_gain}
    if best["train_window_variant"] == "TWX":
        return {"preferred_variant": "TWX", "reason": "twx_raw_best_nearly_equal_and_operationally_simpler", "relative_gain_percent": relative_gain}
    return {"preferred_variant": "TW3", "reason": "differences_below_threshold_prefer_stable_rolling_3_years", "best_raw_variant": best["train_window_variant"], "relative_gain_percent": relative_gain}


def model_method_contract(features: list[str]) -> dict[str, object]:
    return {
        "model_name": MODEL_NAME,
        "model_family": "HGB",
        "area": AREA,
        "feature_stack": "P0056F_W12",
        "feature_count": len(features),
        "method_note": "Same HGB no-price method and SE2 W12 feature set as P0056H2; only train-window filtering varies.",
        "spot_price_features": False,
        "flow_exchange_a61_capacity_features": False,
    }


def decide_status(summaries: list[dict[str, object]], failures: list[dict[str, object]]) -> str:
    if failures or any(int(row.get("origin_count") or 0) == 0 for row in summaries):
        return "STOP"
    return "WARN"


def persist_origin_outputs(conn: sqlite3.Connection, variant_id: str, origin: p0056h.OriginWindow, rows: list[dict[str, object]], result: dict[str, object]) -> None:
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {FORECAST_TABLE}
        (forecast_origin_timestamp_utc, target_timestamp_utc, horizon_hours, area_code,
         train_window_variant, model_name, prediction_kind, predicted_consumption_mw,
         actual_consumption_mw, train_start_utc, train_end_utc, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["forecast_origin_timestamp_utc"],
                row["target_timestamp_utc"],
                int(row["horizon_hours"]),
                AREA,
                variant_id,
                MODEL_NAME,
                row["prediction_kind"],
                float(row[PREDICTION_COLUMN]),
                float(row[p0054k.TARGET_FIELD]),
                result["train_start"],
                result["train_end"],
                PACKAGE_ID,
            )
            for row in rows
        ],
    )
    metric_rows = []
    for name, value in result.items():
        if name in {"area_code", "origin_id", "train_window_variant"}:
            continue
        metric_value = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) else None
        metric_text = None if metric_value is not None else json.dumps(p0056h.json_safe(value), sort_keys=True)
        metric_rows.append((AREA, variant_id, origin.origin_id, "origin", name, metric_value, metric_text, PACKAGE_ID))
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {METRICS_TABLE}
        (area_code, train_window_variant, origin_id, metric_scope, metric_name, metric_value, metric_text, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        metric_rows,
    )
    conn.commit()


def persist_summary_metrics(conn: sqlite3.Connection, summary: dict[str, object]) -> None:
    rows = []
    for window in summary.get("window_summary_results", []):
        if not isinstance(window, dict):
            continue
        variant_id = str(window["train_window_variant"])
        for name, value in window.items():
            if name == "train_window_variant":
                continue
            metric_value = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) else None
            metric_text = None if metric_value is not None else json.dumps(p0056h.json_safe(value), sort_keys=True)
            rows.append((AREA, variant_id, "ALL", "window_summary", name, metric_value, metric_text, PACKAGE_ID))
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {METRICS_TABLE}
        (area_code, train_window_variant, origin_id, metric_scope, metric_name, metric_value, metric_text, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()


def write_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog_md(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", labb_label_md(summary)),
        "baseline-review.md": write(evidence_dir / "baseline-review.md", baseline_review_md()),
        "origin-schedule.md": write(evidence_dir / "origin-schedule.md", origin_schedule_md(summary)),
        "train-window-contract.md": write(evidence_dir / "train-window-contract.md", train_window_contract_md()),
        "lag-feature-list.md": write(evidence_dir / "lag-feature-list.md", p0056h2.lag_feature_list_md(summary.get("lag_feature_check", {}))),
        "input-source-contract.md": write(evidence_dir / "input-source-contract.md", json_report("P0056I Input Source Contract", summary.get("input_contract", {}))),
        "weather-protocol.md": write(evidence_dir / "weather-protocol.md", json_report("P0056I Weather Protocol", summary.get("weather_protocol", {}))),
        "model-method-contract.md": write(evidence_dir / "model-method-contract.md", json_report("P0056I Model Method Contract", summary.get("model_method_contract", {}))),
        "origin-results.md": write(evidence_dir / "origin-results.md", origin_results_md(summary.get("origin_results", []))),
        "window-summary-results.md": write(evidence_dir / "window-summary-results.md", window_summary_md(summary.get("window_summary_results", []))),
        "comparison-vs-baselines.md": write(evidence_dir / "comparison-vs-baselines.md", comparison_md(summary.get("comparison_vs_baselines", []))),
        "interpretation.md": write(evidence_dir / "interpretation.md", interpretation_md(summary)),
        "decision.md": write(evidence_dir / "decision.md", decision_md(summary)),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", what_we_learned_md(summary)),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", next_package_recommendation_md(summary)),
        "origin-results.csv": write_csv(evidence_dir / "origin-results.csv", summary.get("origin_results", [])),
        "window-summary-results.csv": write_csv(evidence_dir / "window-summary-results.csv", summary.get("window_summary_results", [])),
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(p0056h.json_safe(compact_summary(summary)), indent=2, sort_keys=True) + "\n"),
    }
    return evidence


def changelog_md(summary: dict[str, object]) -> str:
    rows = summary.get("row_counts", {})
    return "\n".join([
        "# P0056I Changelog",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- SE2 complete origins: `{rows.get('complete_origins', 0) if isinstance(rows, dict) else 0}`",
        f"- Variant results: `{rows.get('variant_results', 0) if isinstance(rows, dict) else 0}`",
        f"- Failed jobs: `{rows.get('failed_jobs', 0) if isinstance(rows, dict) else 0}`",
        "- Compared TW2, TW3 and TWX with P0056H2 static-style lag construction.",
        "- No API, devices, runtime changes, spot price, flow/exchange/A61/capacity or old physical_balance features.",
        "",
    ])


def labb_label_md(summary: dict[str, object]) -> str:
    return "# P0056I LABB Label\n\nP0056I is `LABB` evidence only. It uses actual weather as a forecast proxy and is not deployable or a G2-KANDIDAT evaluation.\n"


def baseline_review_md() -> str:
    lines = ["# P0056I Baseline Review", "", "| baseline | SE2 MAE |", "| --- | ---: |"]
    for name, value in BASELINES.items():
        lines.append(f"| {name} | {p0056h.fmt(value)} |")
    lines.append("")
    return "\n".join(lines)


def origin_schedule_md(summary: dict[str, object]) -> str:
    origins = summary.get("origins", [])
    return "\n".join([
        "# P0056I Origin Schedule",
        "",
        "- Area: `SE2`",
        "- Origin time: `06:00 Europe/Stockholm`",
        "- Origin step: every fifth day",
        "- Horizon: `36h`",
        f"- Scheduled origins: `{len(origins) if isinstance(origins, list) else 0}`",
        f"- Complete origins: `{summary.get('row_counts', {}).get('complete_origins') if isinstance(summary.get('row_counts'), dict) else None}`",
        "",
    ])


def train_window_contract_md() -> str:
    return "\n".join([
        "# P0056I Train-Window Contract",
        "",
        "| variant | train_start | train_end |",
        "| --- | --- | --- |",
        "| TW2 | forecast_origin minus 2 calendar years | forecast_origin exclusive |",
        "| TW3 | forecast_origin minus 3 calendar years | forecast_origin exclusive |",
        "| TWX | 2022-06-01T00:00:00Z | forecast_origin exclusive |",
        "",
        "Everything except `train_start` is held fixed across variants.",
        "",
    ])


def origin_results_md(rows: object) -> str:
    values = rows if isinstance(rows, list) else []
    lines = ["# P0056I Origin Results", "", f"- Origin/variant rows: `{len(values)}`", "", "| variant | origins | mean MAE 0-36h |", "| --- | ---: | ---: |"]
    for variant_id in TRAIN_WINDOW_VARIANTS:
        selected = [row for row in values if isinstance(row, dict) and row.get("train_window_variant") == variant_id]
        maes = [float(row["MAE_0_36h"]) for row in selected if row.get("MAE_0_36h") is not None]
        lines.append(f"| {variant_id} | {len(selected)} | {p0056h.fmt(p0054k.mean_float(maes) if maes else None)} |")
    lines.append("")
    return "\n".join(lines)


def window_summary_md(rows: object) -> str:
    lines = ["# P0056I Window Summary Results", "", "| variant | origins | mean MAE 0-36h | median MAE | MAE 0-24h | MAE 24-36h | weighted MAE % load | mean energy error % | bias |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('train_window_variant')} | {row.get('origin_count')} | {p0056h.fmt(row.get('mean_MAE_0_36h'))} | {p0056h.fmt(row.get('median_MAE_0_36h'))} | {p0056h.fmt(row.get('mean_MAE_0_24h'))} | {p0056h.fmt(row.get('mean_MAE_24_36h'))} | {p0056h.fmt(row.get('weighted_MAE_percent_of_mean_load'))} | {p0056h.fmt(row.get('mean_energy_error_percent'))} | {p0056h.fmt(row.get('bias_over_period'))} |")
    lines.append("")
    return "\n".join(lines)


def comparison_md(rows: object) -> str:
    lines = ["# P0056I Comparison Vs Baselines", "", "| variant | baseline | baseline MAE | P0056I MAE | delta MW | delta % |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('train_window_variant')} | {row.get('baseline_name')} | {p0056h.fmt(row.get('baseline_MAE'))} | {p0056h.fmt(row.get('p0056i_MAE'))} | {p0056h.fmt(row.get('delta_MW'))} | {p0056h.fmt(row.get('delta_percent'))} |")
    lines.append("")
    return "\n".join(lines)


def interpretation_md(summary: dict[str, object]) -> str:
    windows = {str(row["train_window_variant"]): row for row in summary.get("window_summary_results", []) if isinstance(row, dict)}
    tw2 = windows.get("TW2", {})
    tw3 = windows.get("TW3", {})
    twx = windows.get("TWX", {})
    tw2_vs_tw3 = delta_percent(tw2.get("mean_MAE_0_36h"), tw3.get("mean_MAE_0_36h"))
    twx_vs_tw3 = delta_percent(twx.get("mean_MAE_0_36h"), tw3.get("mean_MAE_0_36h"))
    return "\n".join([
        "# P0056I Interpretation",
        "",
        f"- TW2 vs TW3 MAE delta: `{p0056h.fmt(tw2_vs_tw3)}%`.",
        f"- TWX vs TW3 MAE delta: `{p0056h.fmt(twx_vs_tw3)}%`.",
        f"- Preferred window: `{summary.get('decision', {}).get('preferred_variant') if isinstance(summary.get('decision'), dict) else None}`.",
        "- The experiment isolates training-window length; actual-weather proxy remains LABB-only.",
        "",
    ])


def decision_md(summary: dict[str, object]) -> str:
    decision = summary.get("decision", {}) if isinstance(summary.get("decision"), dict) else {}
    return "\n".join([
        "# P0056I Decision",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Preferred train-window variant: `{decision.get('preferred_variant')}`",
        f"- Reason: `{decision.get('reason')}`",
        "- Production readiness: not ready; LABB-only diagnostic.",
        "",
    ])


def what_we_learned_md(summary: dict[str, object]) -> str:
    return "# P0056I What We Learned\n\nTraining-window length can now be compared independently from lag construction for SE2 on the P0056H/P0056H2 36h origin grid. Use the preferred variant only as LABB guidance until forecast-safe weather and runtime contracts are evaluated separately.\n"


def next_package_recommendation_md(summary: dict[str, object]) -> str:
    decision = summary.get("decision", {}) if isinstance(summary.get("decision"), dict) else {}
    preferred = decision.get("preferred_variant")
    return f"# P0056I Next Package Recommendation\n\nUse `{preferred}` as the train-window assumption in the next SE2 emulator consumption protocol test, then test whether the remaining static-baseline gap is caused by model method or evaluation split rather than training-window length.\n"


def compact_summary(summary: dict[str, object]) -> dict[str, object]:
    return {
        "package_id": summary.get("package_id"),
        "status": summary.get("status"),
        "runtime_seconds": summary.get("runtime_seconds"),
        "row_counts": summary.get("row_counts"),
        "window_summary_results": summary.get("window_summary_results"),
        "comparison_vs_baselines": summary.get("comparison_vs_baselines"),
        "decision": summary.get("decision"),
        "lag_feature_check": summary.get("lag_feature_check"),
    }


def stopped_summary(started: float, feature_path: Path, input_contract: dict[str, object]) -> dict[str, object]:
    return {"package_id": PACKAGE_ID, "label": LABEL, "status": "STOP", "runtime_seconds": round(time.monotonic() - started, 3), "feature_db": str(feature_path), "input_contract": input_contract, "row_counts": {}}


def delta_percent(value: object, baseline: object) -> float | None:
    if value is None or baseline is None:
        return None
    base = float(baseline)
    return (float(value) - base) / base * 100.0 if base else None


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
    result = run_p0056i_train_window_sensitivity()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
