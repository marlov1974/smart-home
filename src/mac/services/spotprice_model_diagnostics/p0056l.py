"""P0056L LABB SE2 neural DayAhead smoke test."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import csv
import importlib.util
import json
import math
import sqlite3
import sys
import time
import warnings

import numpy as np

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0056c, p0056d, p0056k
from src.mac.services.spotprice_model_diagnostics.p0041 import write


PACKAGE_ID = "P0056L"
LABEL = "LABB"
AREA = "SE2"
EVIDENCE_DIR = Path("requirements/package-runs/P0056L")
SUBSET_STEP = 4
SEQUENCE_LOOKBACK_HOURS = 168
SEQUENCE_FEATURES = [f"origin_load_window_lag_{hour:03d}h" for hour in range(1, SEQUENCE_LOOKBACK_HOURS + 1)]

P0056K_BASELINES = {
    "M6": {"DayAhead_hourly_MAE": 232.69280738198043, "MAE_percent_of_mean_actual": 12.832408927934823},
    "M7": {"DayAhead_hourly_MAE": 233.9480432393704, "MAE_percent_of_mean_actual": 12.957669101084063},
    "M4": {"DayAhead_hourly_MAE": 233.75305382282218, "MAE_percent_of_mean_actual": 12.886913882353019},
    "M3": {"DayAhead_hourly_MAE": 233.09245936856348, "MAE_percent_of_mean_actual": 12.87590966065606},
}


@dataclass(frozen=True)
class P0056LResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0056l_neural_dayahead_smoke(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0056LResult:
    started = time.monotonic()
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    evidence_path = Path(evidence_dir)
    initialize_progress(evidence_path)
    feature_path = Path(feature_db).expanduser()
    with sqlite3.connect(feature_path, timeout=60.0) as conn:
        conn.row_factory = sqlite3.Row
        targets_all, target_contract = p0056c.load_area_targets(conn)
        weather_all, weather_contract = p0056d.load_p0056d_area_weather_rows(conn)

    dependency_review = neural_dependency_review()
    input_contract = input_source_contract(target_contract, weather_contract)
    if not input_contract["ok"]:
        summary = stopped_summary(started, feature_path, input_contract, dependency_review)
        return P0056LResult("STOP", summary["row_counts"], write_evidence(evidence_path, summary, []))  # type: ignore[arg-type]

    targets = targets_all[AREA]
    weather_rows = weather_all[AREA]
    origins = p0056k.dayahead_origins(targets, weather_rows, p0056k.FIRST_EVAL_DELIVERY_DAY)
    selected_origins = select_representative_origins(origins, SUBSET_STEP)
    modeling_origins = p0056k.dayahead_origins(targets, weather_rows, p0056k.FIRST_MODELING_DELIVERY_DAY)
    base_rows = p0056k.build_dayahead_rows(AREA, targets, weather_rows, modeling_origins)
    values_by_ts = {str(row["timestamp_utc"]): float(row["consumption_mw"]) for row in targets}
    sequence_rows = add_sequence_window_features(base_rows, values_by_ts)
    base_by_origin = rows_by_origin(base_rows)
    sequence_by_origin = rows_by_origin(sequence_rows)

    model_specs = model_contract()
    origin_results: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    stability: dict[str, dict[str, object]] = {model_id: {"failed_origins": 0, "nan_predictions": 0, "negative_predictions": 0, "iterations": []} for model_id in model_specs}
    total_jobs = len(selected_origins) * len(model_specs)
    completed_jobs = 0

    for origin_index, origin in enumerate(selected_origins, start=1):
        for model_id, spec in model_specs.items():
            job_started = time.monotonic()
            progress(evidence_path, origin, model_id, origin_index, len(selected_origins), "start", completed_jobs, total_jobs)
            source_rows = sequence_rows if spec["kind"] == "sequence" else base_rows
            source_by_origin = sequence_by_origin if spec["kind"] == "sequence" else base_by_origin
            forecast_rows = [dict(row) for row in source_by_origin.get(origin.origin_utc, [])]
            train_rows = [dict(row) for row in source_rows if p0056k.EXPANDING_TRAIN_START_UTC <= str(row["target_timestamp_utc"]) < origin.origin_utc]
            try:
                if len(forecast_rows) != 24:
                    raise RuntimeError(f"incomplete forecast rows: {len(forecast_rows)}")
                predictions, training = fit_predict_mlp(model_id, train_rows, forecast_rows, list(spec["features"]))
                stability[model_id]["nan_predictions"] = int(stability[model_id]["nan_predictions"]) + sum(1 for value in predictions if not math.isfinite(value))
                stability[model_id]["negative_predictions"] = int(stability[model_id]["negative_predictions"]) + sum(1 for value in predictions if value < 0.0)
                if training.get("n_iter") is not None:
                    stability[model_id]["iterations"].append(training["n_iter"])  # type: ignore[index, union-attr]
                result = p0056k.score_origin(AREA, origin, model_id, forecast_rows, predictions, training, time.monotonic() - job_started)
                origin_results.append(result)
                completed_jobs += 1
                progress(evidence_path, origin, model_id, origin_index, len(selected_origins), "done", completed_jobs, total_jobs, {"MAE": result["DayAhead_hourly_MAE"], "seconds": round(time.monotonic() - job_started, 3)})
            except Exception as exc:  # pragma: no cover - long-run evidence path
                failures.append({"area": AREA, "origin_utc": origin.origin_utc, "model_id": model_id, "error_type": type(exc).__name__, "error": str(exc)[:600]})
                stability[model_id]["failed_origins"] = int(stability[model_id]["failed_origins"]) + 1
                completed_jobs += 1
                progress(evidence_path, origin, model_id, origin_index, len(selected_origins), "failed", completed_jobs, total_jobs, {"error_type": type(exc).__name__, "error": str(exc)[:160]})

    area_model_results = aggregate_neural_results(origin_results)
    comparison = comparison_vs_p0056k(area_model_results)
    decision = decision_summary(comparison, failures)
    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": decide_status(area_model_results, failures),
        "runtime_seconds": round(time.monotonic() - started, 3),
        "feature_db": str(feature_path),
        "area": AREA,
        "subset_policy": subset_policy(len(origins), len(selected_origins)),
        "input_contract": input_contract,
        "dependency_review": dependency_review,
        "dayahead_protocol": p0056k.dayahead_protocol(),
        "feature_protocol": feature_protocol(),
        "training_policy": training_policy(),
        "model_contract": compact_model_contract(model_specs),
        "area_model_results": area_model_results,
        "comparison_vs_p0056k": comparison,
        "stability_review": stability_review(stability, failures),
        "leakage_review": leakage_review(model_specs),
        "decision": decision,
        "what_we_learned": what_we_learned(decision),
        "next_package_recommendation": next_package_recommendation(decision),
        "failures": failures,
        "row_counts": {
            "available_origins": len(origins),
            "selected_origins": len(selected_origins),
            "origin_results": len(origin_results),
            "area_model_results": len(area_model_results),
            "failures": len(failures),
            "completed_jobs": completed_jobs,
            "planned_jobs": total_jobs,
        },
        "no_api": True,
        "no_devices": True,
        "no_runtime_change": True,
        "no_production_activation": True,
        "no_large_artifacts": True,
    }
    return P0056LResult(str(summary["status"]), summary["row_counts"], write_evidence(evidence_path, summary, origin_results))  # type: ignore[arg-type]


def select_representative_origins(origins: list[p0056k.Origin], step: int = SUBSET_STEP) -> list[p0056k.Origin]:
    if step <= 1:
        return list(origins)
    return list(origins[::step])


def rows_by_origin(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    out: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        out[str(row["forecast_origin_timestamp_utc"])].append(row)
    return out


def add_sequence_window_features(rows: list[dict[str, object]], values_by_ts: dict[str, float]) -> list[dict[str, object]]:
    enriched = []
    for row in rows:
        origin_dt = p0052.parse_utc(str(row["forecast_origin_timestamp_utc"]))
        current = dict(row)
        for hour, feature in enumerate(SEQUENCE_FEATURES, start=1):
            current[feature] = values_by_ts[p0052.format_utc(origin_dt - timedelta(hours=hour))]
        enriched.append(current)
    return enriched


def fit_predict_mlp(model_id: str, train_rows: list[dict[str, object]], forecast_rows: list[dict[str, object]], features: list[str]) -> tuple[list[float], dict[str, object]]:
    from sklearn.exceptions import ConvergenceWarning
    from sklearn.neural_network import MLPRegressor

    started = time.monotonic()
    x_train, encoder, names = p0054k.build_feature_matrix(train_rows, features)
    y_train = np.array([float(row[p0056k.TARGET]) for row in train_rows], dtype=float)
    y_mean = float(np.mean(y_train))
    y_std = float(np.std(y_train)) or 1.0
    y_scaled = (y_train - y_mean) / y_std
    hidden = (48, 24) if model_id == "N1_TabularMLP" else (32,)
    model = MLPRegressor(
        hidden_layer_sizes=hidden,
        activation="relu",
        solver="adam",
        alpha=0.002,
        batch_size=256,
        learning_rate_init=0.001,
        max_iter=70,
        early_stopping=True,
        validation_fraction=0.12,
        n_iter_no_change=8,
        random_state=p0054k.RANDOM_SEED,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(x_train, y_scaled)
    x_forecast, _, _ = p0054k.build_feature_matrix(forecast_rows, features, encoder)
    predictions = [float(value * y_std + y_mean) for value in model.predict(x_forecast)]
    return predictions, {
        "model_family": "scikit-learn MLPRegressor",
        "model_class": "MLPRegressor",
        "train_rows": len(train_rows),
        "feature_count": len(names),
        "train_seconds": round(time.monotonic() - started, 3),
        "n_iter": int(getattr(model, "n_iter_", 0)),
        "loss": float(getattr(model, "loss_", 0.0)),
        "early_stopping": True,
        "convergence_warnings": sum(1 for warning in caught if issubclass(warning.category, ConvergenceWarning)),
    }


def model_contract() -> dict[str, dict[str, object]]:
    return {
        "N1_TabularMLP": {"kind": "tabular", "features": list(p0056k.FEATURES), "framework": "scikit-learn", "architecture": "MLPRegressor hidden=(48,24)"},
        "N2_SequenceMLP_168h": {"kind": "sequence", "features": list(p0056k.FEATURES) + SEQUENCE_FEATURES, "framework": "scikit-learn", "architecture": "MLPRegressor hidden=(32,), 168h flattened known-at-origin load window"},
    }


def compact_model_contract(specs: dict[str, dict[str, object]]) -> dict[str, object]:
    return {model_id: {key: value for key, value in spec.items() if key != "features"} | {"feature_count": len(spec["features"])} for model_id, spec in specs.items()}


def aggregate_neural_results(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for model_id in sorted({str(row["model_id"]) for row in rows}):
        selected = [row for row in rows if row["model_id"] == model_id]
        if not selected:
            continue
        out.append({
            "area_code": AREA,
            "model_id": model_id,
            "origin_count": len(selected),
            "delivery_day_count": len(selected),
            "DayAhead_hourly_MAE": p0054k.mean_float([float(row["DayAhead_hourly_MAE"]) for row in selected]),
            "DayAhead_RMSE": p0054k.mean_float([float(row["DayAhead_RMSE"]) for row in selected]),
            "DayAhead_bias": p0054k.mean_float([float(row["DayAhead_bias"]) for row in selected]),
            "MAE_percent_of_mean_actual": p0054k.mean_float([float(row["MAE_percent_of_mean_actual"]) for row in selected]),
            "MAE_percent_of_median_actual": p0054k.mean_float([float(row["MAE_percent_of_median_actual"]) for row in selected]),
            "absolute_daily_energy_error_MWh": p0054k.mean_float([float(row["absolute_daily_energy_error_MWh"]) for row in selected]),
            "signed_daily_energy_error_MWh": p0054k.mean_float([float(row["signed_daily_energy_error_MWh"]) for row in selected]),
            "daily_energy_error_percent_of_actual": p0054k.mean_float([float(row["daily_energy_error_percent_of_actual"]) for row in selected]),
            "p90_absolute_error": p0054k.mean_float([float(row["p90_absolute_error"]) for row in selected]),
            "p95_absolute_error": p0054k.mean_float([float(row["p95_absolute_error"]) for row in selected]),
            "mean_seconds_per_origin": p0054k.mean_float([float(row["seconds"]) for row in selected]),
            "weekday_weekend_split": p0056k.split_metric(selected, lambda row: "weekend" if int(row["weekday"]) >= 5 else "weekday"),
            "monthly_split": p0056k.split_metric(selected, lambda row: str(row["month"])),
        })
    return out


def comparison_vs_p0056k(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        for baseline_id, baseline in P0056K_BASELINES.items():
            neural_mae = float(row["DayAhead_hourly_MAE"])
            baseline_mae = float(baseline["DayAhead_hourly_MAE"])
            out.append({
                "area_code": AREA,
                "model_id": row["model_id"],
                "baseline_model": f"P0056K_{baseline_id}",
                "baseline_DayAhead_hourly_MAE": baseline_mae,
                "neural_subset_DayAhead_hourly_MAE": neural_mae,
                "delta_MW": neural_mae - baseline_mae,
                "relative_improvement_percent": (baseline_mae - neural_mae) / baseline_mae * 100.0,
                "comparison_scope": "P0056K full SE2 aggregate baseline vs P0056L reduced representative subset",
            })
    return out


def decision_summary(comparison: list[dict[str, object]], failures: list[dict[str, object]]) -> dict[str, object]:
    vs_m6 = [row for row in comparison if row["baseline_model"] == "P0056K_M6"]
    best = max(vs_m6, key=lambda row: float(row["relative_improvement_percent"])) if vs_m6 else {}
    clears = bool(best) and float(best["relative_improvement_percent"]) >= 2.0
    return {
        "worth_expanding": clears,
        "best_neural_model": best.get("model_id"),
        "best_neural_MAE": best.get("neural_subset_DayAhead_hourly_MAE"),
        "baseline_M6_MAE": P0056K_BASELINES["M6"]["DayAhead_hourly_MAE"],
        "relative_improvement_vs_M6_percent": best.get("relative_improvement_percent"),
        "threshold_met": clears,
        "production_ready": False,
        "reason": "Reduced-subset neural smoke comparison; expand only if >=2 percent improvement vs P0056K M6.",
        "failure_count": len(failures),
    }


def decide_status(rows: list[dict[str, object]], failures: list[dict[str, object]]) -> str:
    if not rows:
        return "STOP"
    if failures and len(rows) < len(model_contract()):
        return "STOP"
    return "WARN"


def neural_dependency_review() -> dict[str, object]:
    return {
        "torch": bool(importlib.util.find_spec("torch")),
        "sklearn": bool(importlib.util.find_spec("sklearn")),
        "numpy": bool(importlib.util.find_spec("numpy")),
        "selected_framework": "scikit-learn MLPRegressor",
        "skipped": [
            {"model_id": "N3_TCN_1D_CNN", "reason": "torch unavailable; no local TCN dependency"},
            {"model_id": "N4_NBEATS_NHITS", "reason": "no supported local dependency and heavy dependency install is out of scope"},
        ],
    }


def input_source_contract(target_contract: dict[str, object], weather_contract: dict[str, object]) -> dict[str, object]:
    target_areas = target_contract.get("areas", {}) if isinstance(target_contract.get("areas"), dict) else {}
    weather_areas = weather_contract.get("areas", {}) if isinstance(weather_contract.get("areas"), dict) else {}
    return {"ok": AREA in target_areas and AREA in weather_areas, "area": AREA, "target_source": "area_consumption_hourly_v1/P0056A", "weather_source": "P0056D", "weather_protocol": "actual_weather_proxy_LABB"}


def subset_policy(available: int, selected: int) -> dict[str, object]:
    return {"status": "reduced_representative_WARN", "available_origins": available, "selected_origins": selected, "selection": f"every {SUBSET_STEP}th P0056K-valid SE2 origin"}


def feature_protocol() -> dict[str, object]:
    return {"base_protocol": p0056k.lag_protocol(), "sequence_features": {"N2_SequenceMLP_168h": f"{SEQUENCE_LOOKBACK_HOURS} known-at-origin historical load values"}, "future_actual_load_used": False}


def training_policy() -> dict[str, object]:
    return {"window": "expanding from 2022-06-01", "train_end": "strictly before forecast_origin", "target_scaling": "per-origin train y mean/std", "early_stopping": True, "random_seed": p0054k.RANDOM_SEED}


def leakage_review(specs: dict[str, dict[str, object]]) -> dict[str, object]:
    features = sorted({feature for spec in specs.values() for feature in spec["features"]})  # type: ignore[union-attr]
    forbidden = [feature for feature in features if any(term in feature.lower() for term in ("price", "spot", "flow", "exchange", "a61", "capacity", "physical_balance", "future_actual"))]
    return {"ok": not forbidden, "forbidden_features": forbidden, "future_actual_load_feature_used": False, "spot_price_feature_used": False, "flow_exchange_a61_capacity_feature_used": False, "old_physical_balance_target_used": False}


def stability_review(stability: dict[str, dict[str, object]], failures: list[dict[str, object]]) -> dict[str, object]:
    out = {}
    for model_id, row in stability.items():
        iterations = [int(value) for value in row.get("iterations", [])]
        out[model_id] = {
            "failed_origins": row["failed_origins"],
            "nan_predictions": row["nan_predictions"],
            "negative_predictions": row["negative_predictions"],
            "mean_iterations": p0054k.mean_float(iterations) if iterations else 0.0,
            "max_iterations": max(iterations) if iterations else 0,
        }
    return {"models": out, "failure_count": len(failures), "random_seed": p0054k.RANDOM_SEED}


def what_we_learned(decision: dict[str, object]) -> dict[str, object]:
    return {"neural_expansion_recommended": decision.get("worth_expanding"), "subset_warning": True, "p0056k_m6_still_primary_full_origin_se2_baseline": not bool(decision.get("worth_expanding"))}


def next_package_recommendation(decision: dict[str, object]) -> str:
    if decision.get("worth_expanding"):
        return "P0056M: run a full-origin multi-area neural comparison with a proper sequence model stack."
    return "Keep P0056K M6/M7 as the SE2 realistic DayAhead baseline; revisit neural only with a larger global/multi-area neural package."


def stopped_summary(started: float, feature_path: Path, input_contract: dict[str, object], dependency_review: dict[str, object]) -> dict[str, object]:
    return {"package_id": PACKAGE_ID, "label": LABEL, "status": "STOP", "runtime_seconds": round(time.monotonic() - started, 3), "feature_db": str(feature_path), "input_contract": input_contract, "dependency_review": dependency_review, "row_counts": {}}


def progress(evidence_dir: Path, origin: p0056k.Origin, model_id: str, origin_index: int, origin_count: int, status: str, completed: int, total: int, extra: dict[str, object] | None = None) -> None:
    payload = {"timestamp_utc": p0052.format_utc(datetime.now(timezone.utc)), "area": AREA, "model_id": model_id, "origin_utc": origin.origin_utc, "delivery_day": origin.delivery_day.isoformat(), "origin_index": origin_index, "origin_count": origin_count, "status": status, "completed_jobs": completed, "planned_jobs": total, **(extra or {})}
    line = json.dumps(payload, sort_keys=True)
    with (evidence_dir / "progress-log.md").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    write(evidence_dir / "job-status.md", "\n".join(["# P0056L Job Status", "", f"- Last status: `{status}`", f"- Area: `{AREA}`", f"- Model: `{model_id}`", f"- Origin: `{origin_index}/{origin_count}`", f"- Completed jobs: `{completed}/{total}`", f"- Timestamp UTC: `{payload['timestamp_utc']}`", ""]))
    if status == "failed" or completed == 0 or completed == total or (status == "done" and completed % 20 == 0):
        print(line, flush=True)


def initialize_progress(evidence_dir: Path) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    write(evidence_dir / "progress-log.md", "")
    write(evidence_dir / "job-status.md", "# P0056L Job Status\n\nNo jobs yet.\n")


def write_evidence(evidence_dir: Path, summary: dict[str, object], origin_results: list[dict[str, object]]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog_md(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", "# P0056L LABB Label\n\nP0056L is LABB-only neural DayAhead smoke testing. It is not G2-KANDIDAT or production activation.\n"),
        "p0056k-baseline-review.md": write(evidence_dir / "p0056k-baseline-review.md", p0056k_baseline_review_md()),
        "dayahead-protocol.md": write(evidence_dir / "dayahead-protocol.md", json_report("P0056L DayAhead Protocol", summary.get("dayahead_protocol", {}))),
        "input-source-contract.md": write(evidence_dir / "input-source-contract.md", json_report("P0056L Input Source Contract", summary.get("input_contract", {}))),
        "feature-protocol.md": write(evidence_dir / "feature-protocol.md", json_report("P0056L Feature Protocol", summary.get("feature_protocol", {}))),
        "neural-dependency-review.md": write(evidence_dir / "neural-dependency-review.md", json_report("P0056L Neural Dependency Review", summary.get("dependency_review", {}))),
        "model-contract.md": write(evidence_dir / "model-contract.md", json_report("P0056L Model Contract", summary.get("model_contract", {}))),
        "training-policy.md": write(evidence_dir / "training-policy.md", json_report("P0056L Training Policy", summary.get("training_policy", {}))),
        "area-model-results.md": write(evidence_dir / "area-model-results.md", table_md("P0056L Area Model Results", summary.get("area_model_results", []))),
        "comparison-vs-p0056k.md": write(evidence_dir / "comparison-vs-p0056k.md", table_md("P0056L Comparison Vs P0056K", summary.get("comparison_vs_p0056k", []))),
        "stability-review.md": write(evidence_dir / "stability-review.md", json_report("P0056L Stability Review", summary.get("stability_review", {}))),
        "leakage-review.md": write(evidence_dir / "leakage-review.md", json_report("P0056L Leakage Review", summary.get("leakage_review", {}))),
        "decision.md": write(evidence_dir / "decision.md", json_report("P0056L Decision", summary.get("decision", {}))),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", json_report("P0056L What We Learned", summary.get("what_we_learned", {}))),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", f"# P0056L Next Package Recommendation\n\n{summary.get('next_package_recommendation')}\n"),
        "area-model-results.csv": write_csv(evidence_dir / "area-model-results.csv", summary.get("area_model_results", [])),
        "comparison-vs-p0056k.csv": write_csv(evidence_dir / "comparison-vs-p0056k.csv", summary.get("comparison_vs_p0056k", [])),
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(p0056c.json_safe(compact_summary(summary)), indent=2, sort_keys=True) + "\n"),
    }
    return evidence


def p0056k_baseline_review_md() -> str:
    rows = ["# P0056L P0056K Baseline Review", "", "| baseline | DayAhead hourly MAE | MAE percent of mean actual |", "| --- | ---: | ---: |"]
    for model_id, values in P0056K_BASELINES.items():
        rows.append(f"| P0056K {model_id} | {values['DayAhead_hourly_MAE']:.6f} | {values['MAE_percent_of_mean_actual']:.6f} |")
    rows.append("")
    return "\n".join(rows)


def changelog_md(summary: dict[str, object]) -> str:
    rows = summary.get("row_counts", {})
    decision = summary.get("decision", {}) if isinstance(summary.get("decision"), dict) else {}
    return "\n".join(["# P0056L Changelog", "", f"- Status: `{summary.get('status')}`", f"- Selected origins: `{rows.get('selected_origins') if isinstance(rows, dict) else None}`", f"- Models: `N1_TabularMLP`, `N2_SequenceMLP_168h`", f"- Best neural model: `{decision.get('best_neural_model')}`", f"- Threshold met: `{decision.get('threshold_met')}`", "- No API, devices, runtime changes, production activation, forbidden features or large artifacts.", ""])


def compact_summary(summary: dict[str, object]) -> dict[str, object]:
    return {key: summary.get(key) for key in ("package_id", "status", "runtime_seconds", "row_counts", "dependency_review", "subset_policy", "area_model_results", "comparison_vs_p0056k", "stability_review", "leakage_review", "decision", "failures")}


def table_md(title: str, rows: object) -> str:
    values = rows if isinstance(rows, list) else []
    if not values:
        return f"# {title}\n\nNo rows.\n"
    keys = sorted({key for row in values if isinstance(row, dict) for key in row if not isinstance(row.get(key), (dict, list))})
    lines = [f"# {title}", "", "| " + " | ".join(keys) + " |", "| " + " | ".join("---" for _ in keys) + " |"]
    for row in values:
        lines.append("| " + " | ".join(str(row.get(key, "")) for key in keys) + " |")
    lines.append("")
    return "\n".join(lines)


def json_report(title: str, value: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(p0056c.json_safe(value), indent=2, sort_keys=True)}\n```\n"


def write_csv(path: Path, rows: object) -> str:
    values = rows if isinstance(rows, list) else []
    if not values:
        return write(path, "")
    keys = sorted({key for row in values if isinstance(row, dict) for key in row if not isinstance(row.get(key), (dict, list))})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        for row in values:
            writer.writerow({key: row.get(key) for key in keys})
    return str(path)


def main() -> None:
    result = run_p0056l_neural_dayahead_smoke()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
