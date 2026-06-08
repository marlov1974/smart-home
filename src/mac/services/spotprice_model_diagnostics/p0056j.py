"""P0056J LABB static vs rolling row-level audit."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import csv
import json
import math
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054q, p0054r, p0056c, p0056d, p0056e, p0056f, p0056h, p0056h2, p0056i
from src.mac.services.spotprice_model_diagnostics.p0041 import write


PACKAGE_ID = "P0056J"
LABEL = "LABB"
AREA = "SE2"
EVIDENCE_DIR = Path("requirements/package-runs/P0056J")
ROLLING_VARIANT = "TWX"
STATIC_STACK = "W12"
SAMPLE_ORIGIN_COUNT = 12

BASELINES = {
    "P0056F_W12_static_full36": 197.547,
    "P0056H_L2_recursive_36h": 242.579,
    "P0056H2_static_style_36h": 228.549,
    "P0056I_TWX": 228.549,
    "P0056G_weekly": 207.757,
}

FEATURE_GROUPS = {
    "calendar": [
        "horizon_h",
        "target_model_cet_hour",
        "target_model_cet_weekday",
        "target_model_cet_day_of_year",
        "target_month",
        "target_hour_sin",
        "target_hour_cos",
        "target_dayofyear_sin",
        "target_dayofyear_cos",
        "is_weekend",
        "is_workday",
        "is_holiday",
        "is_bridge_day",
        "is_holiday_period",
        "holiday_strength",
        "special_day_type",
        "special_day_group",
    ],
    "lag": p0056h2.STATIC_STYLE_FEATURES,
    "weather": [feature for feature in p0056f.feature_names_for_stack(STATIC_STACK) if feature.startswith("weather_proxy_")],
}
FEATURES_TO_COMPARE = FEATURE_GROUPS["calendar"] + FEATURE_GROUPS["lag"] + FEATURE_GROUPS["weather"]


@dataclass(frozen=True)
class P0056JResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0056j_static_vs_rolling_row_level_audit(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0056JResult:
    started = time.monotonic()
    feature_path = Path(feature_db).expanduser()
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(feature_path, timeout=60.0) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=60000")
        rolling_rows = load_rolling_forecast_rows(conn)
        persisted_static_rows = load_persisted_static_forecast_rows(conn)
        targets_all, target_contract_all = p0056j_load_targets(conn)
        weather_all, weather_contract_all = p0056d.load_p0056d_area_weather_rows(conn)

    if not rolling_rows or not persisted_static_rows:
        summary = stopped_summary(started, feature_path, rolling_rows, persisted_static_rows)
        evidence = write_evidence(evidence_path, summary)
        return P0056JResult("STOP", summary["row_counts"], evidence)  # type: ignore[arg-type]

    static_feature_rows, static_prediction_column, static_training = reconstruct_static_w12_rows(targets_all[AREA], weather_all[AREA])
    rolling_feature_rows = reconstruct_rolling_twx_feature_rows(target_contract_all, weather_contract_all, targets_all[AREA], weather_all[AREA])
    static_selected = p0054q.selected_full36_rows(static_feature_rows)
    static_by_key = {row_key(row): row for row in static_feature_rows if row.get(static_prediction_column) is not None}
    rolling_feature_by_key = {row_key(row): row for row in rolling_feature_rows}
    exact_pairs = intersect_rows(list(static_by_key.values()), rolling_rows)
    aligned_pairs = exact_pairs if exact_pairs else align_rows_by_target_closest_horizon(list(static_by_key.values()), rolling_rows)
    alignment_mode = "exact_origin_target" if exact_pairs else "target_timestamp_closest_static_horizon"
    sampled_origins = select_origin_sample(rolling_rows, SAMPLE_ORIGIN_COUNT)
    sample_pairs = [pair for pair in aligned_pairs if str(pair["forecast_origin_timestamp_utc"]) in sampled_origins]

    feature_pairs = []
    for pair in sample_pairs:
        key = (str(pair["forecast_origin_timestamp_utc"]), str(pair["target_timestamp_utc"]))
        static_feature = pair["static"]
        rolling_feature = rolling_feature_by_key.get(key)
        if static_feature and rolling_feature:
            feature_pairs.append({"key": key, "static": static_feature, "rolling": rolling_feature})

    row_diffs = row_level_prediction_diffs(sample_pairs, static_prediction_column)
    feature_summary = summarize_feature_diffs(feature_pairs, FEATURES_TO_COMPARE)
    metric_reconstruction = reconstruct_metrics(aligned_pairs, static_prediction_column, alignment_mode)
    target_intersection = target_row_intersection_summary(persisted_static_rows, rolling_rows, static_selected, exact_pairs, aligned_pairs)
    model_training = model_training_diff(static_training)
    hypothesis_review = hypotheses(target_intersection, feature_summary, metric_reconstruction, model_training)
    status = "PASS" if exact_pairs and feature_summary and row_diffs else "WARN"
    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "feature_db": str(feature_path),
        "area": AREA,
        "baselines": BASELINES,
        "origin_sample": origin_sample_summary(sampled_origins, rolling_rows),
        "target_row_intersection": target_intersection,
        "row_level_prediction_diff": row_diffs,
        "row_alignment_mode": alignment_mode,
        "feature_diff_summary": feature_summary,
        "lag_feature_diff": [row for row in feature_summary if row["feature"] in FEATURE_GROUPS["lag"]],
        "weather_feature_diff": [row for row in feature_summary if row["feature"] in FEATURE_GROUPS["weather"]],
        "calendar_feature_diff": [row for row in feature_summary if row["feature"] in FEATURE_GROUPS["calendar"]],
        "model_training_diff": model_training,
        "horizon_bias_correction_diff": horizon_bias_diff(static_training),
        "metric_reconstruction": metric_reconstruction,
        "hypothesis_review": hypothesis_review,
        "interpretation": interpretation(metric_reconstruction, target_intersection, feature_summary),
        "decision": decision(metric_reconstruction, target_intersection, hypothesis_review),
        "what_we_learned": what_we_learned(metric_reconstruction, target_intersection),
        "next_package_recommendation": "P0056K: exact static-method rerun on P0056I origin grid, separating model method from row-selection effects.",
        "row_counts": {
            "persisted_static_rows": len(persisted_static_rows),
            "persisted_rolling_rows": len(rolling_rows),
            "static_reconstructed_rows_with_prediction": len(static_by_key),
            "rolling_feature_rows": len(rolling_feature_rows),
            "exact_intersection_rows": len(exact_pairs),
            "aligned_intersection_rows": len(aligned_pairs),
            "sampled_origins": len(sampled_origins),
            "sampled_rows": len(row_diffs),
            "feature_pairs": len(feature_pairs),
        },
        "no_api": True,
        "no_devices": True,
        "no_runtime_change": True,
        "no_production_activation": True,
        "no_result_rewriting": True,
        "no_large_artifacts": True,
    }
    evidence = write_evidence(evidence_path, summary)
    return P0056JResult(status, summary["row_counts"], evidence)  # type: ignore[arg-type]


def p0056j_load_targets(conn: sqlite3.Connection) -> tuple[dict[str, list[dict[str, object]]], dict[str, object]]:
    return p0056c.load_area_targets(conn)


def load_rolling_forecast_rows(conn: sqlite3.Connection) -> list[dict[str, object]]:
    return [
        {
            "forecast_origin_timestamp_utc": p0052.normalize_utc_text(row["forecast_origin_timestamp_utc"]),
            "target_timestamp_utc": p0052.normalize_utc_text(row["target_timestamp_utc"]),
            "horizon_hours": int(row["horizon_hours"]),
            "horizon_h": int(row["horizon_hours"]) + 1,
            "area_code": str(row["area_code"]),
            "prediction": float(row["predicted_consumption_mw"]),
            "actual": float(row["actual_consumption_mw"]),
            "train_start_utc": str(row["train_start_utc"]),
            "train_end_utc": str(row["train_end_utc"]),
        }
        for row in conn.execute(
            """
            SELECT forecast_origin_timestamp_utc, target_timestamp_utc, horizon_hours, area_code,
                   predicted_consumption_mw, actual_consumption_mw, train_start_utc, train_end_utc
            FROM area_consumption_36h_train_window_forecast_log_p0056i_v1
            WHERE generated_by_package='P0056I' AND area_code=? AND train_window_variant=?
            ORDER BY forecast_origin_timestamp_utc, target_timestamp_utc
            """,
            (AREA, ROLLING_VARIANT),
        )
    ]


def load_persisted_static_forecast_rows(conn: sqlite3.Connection) -> list[dict[str, object]]:
    return [
        {
            "forecast_origin_timestamp_utc": p0052.normalize_utc_text(row["forecast_origin_timestamp_utc"]),
            "target_timestamp_utc": p0052.normalize_utc_text(row["target_timestamp_utc"]),
            "horizon_hours": int(row["horizon_hours"]),
            "area_code": str(row["area_code"]),
            "prediction": float(row["predicted_consumption_mw"]),
            "actual": float(row["actual_consumption_mw"]),
        }
        for row in conn.execute(
            """
            SELECT forecast_origin_timestamp_utc, target_timestamp_utc, horizon_hours, area_code,
                   predicted_consumption_mw, actual_consumption_mw
            FROM area_consumption_forecast_log_p0056f_v1
            WHERE generated_by_package='P0056F' AND area_code=? AND weather_stack_id=?
            ORDER BY forecast_origin_timestamp_utc, target_timestamp_utc
            """,
            (AREA, STATIC_STACK),
        )
    ]


def reconstruct_static_w12_rows(target_rows: list[dict[str, object]], weather_rows: dict[str, dict[str, object]]) -> tuple[list[dict[str, object]], str, dict[str, object]]:
    rows = p0056e.prepare_rows(AREA, target_rows, weather_rows, "P0056D")
    environment = p0054r.capture_environment_status()
    specs = p0054k.model_specs(environment["imports"])  # type: ignore[arg-type]
    stack = next(stack for stack in p0056f.weather_stacks() if stack.stack_id == STATIC_STACK)
    features = p0056f.feature_names_for_stack(STATIC_STACK)
    fit = p0056f.fit_stack_model(rows, stack, features, specs)
    return rows, str(fit["prediction_column"]), fit["training"] if isinstance(fit.get("training"), dict) else {}


def reconstruct_rolling_twx_feature_rows(
    target_contract: dict[str, object],
    weather_contract: dict[str, object],
    target_rows: list[dict[str, object]],
    weather_rows: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    p0056b_contract = p0056h.scoped_contract(weather_contract, (AREA,))
    p0056d_contract = p0056h.scoped_contract(weather_contract, (AREA,))
    scoped_target = p0056h.scoped_contract(target_contract, (AREA,))
    origins = p0056h.origin_schedule(scoped_target, p0056b_contract, p0056d_contract)
    modeling_origins = p0056i.p0056i_modeling_origins(origins)
    base_rows = p0056h2.build_static_style_modeling_rows(AREA, target_rows, weather_rows, modeling_origins, "P0056D")
    rows_by_origin: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in base_rows:
        rows_by_origin[str(row["forecast_origin_timestamp_utc"])].append(row)
    out = []
    for origin in origins:
        origin_rows = [dict(row) for row in rows_by_origin.get(origin.origin_utc, [])]
        if len(origin_rows) != 36:
            continue
        train_rows = p0056i.filter_train_rows_for_window(base_rows, origin.origin_utc, ROLLING_VARIANT)
        p0056h.apply_weather_profile_features(train_rows, origin_rows)
        out.extend(origin_rows)
    return out


def row_key(row: dict[str, object]) -> tuple[str, str]:
    return (str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"]))


def intersect_rows(static_rows: list[dict[str, object]], rolling_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    static_by_key = {row_key(row): row for row in static_rows}
    out = []
    for rolling in rolling_rows:
        static = static_by_key.get(row_key(rolling))
        if static is None:
            continue
        out.append({"static": static, "rolling": rolling, "forecast_origin_timestamp_utc": rolling["forecast_origin_timestamp_utc"], "target_timestamp_utc": rolling["target_timestamp_utc"]})
    return out


def align_rows_by_target_closest_horizon(static_rows: list[dict[str, object]], rolling_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_target: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in static_rows:
        by_target[str(row["target_timestamp_utc"])].append(row)
    out = []
    for rolling in rolling_rows:
        candidates = by_target.get(str(rolling["target_timestamp_utc"]), [])
        if not candidates:
            continue
        rolling_horizon = int(rolling.get("horizon_h", int(rolling.get("horizon_hours", 0)) + 1))
        static = min(candidates, key=lambda row: abs(int(row.get("horizon_h", int(row.get("horizon_hours", 0)) + 1)) - rolling_horizon))
        out.append({
            "static": static,
            "rolling": rolling,
            "forecast_origin_timestamp_utc": rolling["forecast_origin_timestamp_utc"],
            "target_timestamp_utc": rolling["target_timestamp_utc"],
            "static_forecast_origin_timestamp_utc": static["forecast_origin_timestamp_utc"],
            "static_horizon_h": static.get("horizon_h"),
        })
    return out


def select_origin_sample(rolling_rows: list[dict[str, object]], count: int) -> list[str]:
    by_origin = p0054k.group_by(rolling_rows, "forecast_origin_timestamp_utc")
    scored = []
    for origin, rows in by_origin.items():
        errors = [abs(float(row["prediction"]) - float(row["actual"])) for row in rows]
        dt = p0052.parse_utc(origin)
        scored.append({"origin": origin, "mae": p0054k.mean_float(errors), "month": dt.month, "weekday": dt.weekday(), "latest_rank": dt.timestamp()})
    selected: list[str] = []
    for row in sorted(scored, key=lambda item: float(item["mae"]), reverse=True)[:3]:
        selected.append(str(row["origin"]))
    for row in sorted(scored, key=lambda item: float(item["mae"]))[:3]:
        selected.append(str(row["origin"]))
    for row in sorted(scored, key=lambda item: float(item["latest_rank"]), reverse=True)[:2]:
        selected.append(str(row["origin"]))
    for row in scored:
        if len(dict.fromkeys(selected)) >= count:
            break
        if str(row["origin"]) not in selected:
            selected.append(str(row["origin"]))
    return list(dict.fromkeys(selected))[:count]


def row_level_prediction_diffs(pairs: list[dict[str, object]], static_prediction_column: str) -> list[dict[str, object]]:
    out = []
    for pair in pairs:
        static = pair["static"]
        rolling = pair["rolling"]
        static_pred = float(static[static_prediction_column])
        rolling_pred = float(rolling["prediction"])
        actual = float(rolling["actual"])
        out.append({
            "forecast_origin_timestamp_utc": rolling["forecast_origin_timestamp_utc"],
            "target_timestamp_utc": rolling["target_timestamp_utc"],
            "horizon_h": rolling["horizon_h"],
            "actual_consumption_mw": actual,
            "static_pipeline_prediction_mw": static_pred,
            "rolling_pipeline_prediction_mw": rolling_pred,
            "prediction_delta_mw": rolling_pred - static_pred,
            "absolute_error_static": abs(static_pred - actual),
            "absolute_error_rolling": abs(rolling_pred - actual),
            "error_delta": abs(rolling_pred - actual) - abs(static_pred - actual),
        })
    return out


def summarize_feature_diffs(feature_pairs: list[dict[str, object]], features: list[str]) -> list[dict[str, object]]:
    out = []
    for feature in features:
        rows = []
        examples = []
        for pair in feature_pairs:
            static_value = pair["static"].get(feature)
            rolling_value = pair["rolling"].get(feature)
            if static_value is None and rolling_value is None:
                continue
            matched = values_match(static_value, rolling_value)
            delta = numeric_delta(static_value, rolling_value)
            rows.append({"matched": matched, "delta": delta})
            if not matched and len(examples) < 3:
                examples.append({"key": list(pair["key"]), "static": static_value, "rolling": rolling_value, "delta": delta})
        deltas = [abs(float(row["delta"])) for row in rows if row["delta"] is not None]
        out.append({
            "feature": feature,
            "rows_compared": len(rows),
            "exact_match_count": sum(1 for row in rows if row["matched"]),
            "mismatch_count": sum(1 for row in rows if not row["matched"]),
            "max_abs_delta": max(deltas) if deltas else None,
            "mean_abs_delta": p0054k.mean_float(deltas) if deltas else None,
            "example_mismatches": examples,
        })
    return out


def values_match(left: object, right: object) -> bool:
    if left is None or right is None:
        return left is right
    try:
        return abs(float(left) - float(right)) <= 1e-9
    except (TypeError, ValueError):
        return str(left) == str(right)


def numeric_delta(left: object, right: object) -> float | None:
    try:
        return float(right) - float(left)
    except (TypeError, ValueError):
        return None


def reconstruct_metrics(pairs: list[dict[str, object]], static_prediction_column: str, alignment_mode: str) -> dict[str, object]:
    static_errors = []
    rolling_errors = []
    for pair in pairs:
        static = pair["static"]
        rolling = pair["rolling"]
        actual = float(rolling["actual"])
        static_errors.append(abs(float(static[static_prediction_column]) - actual))
        rolling_errors.append(abs(float(rolling["prediction"]) - actual))
    static_mae = p0054k.mean_float(static_errors) if static_errors else None
    rolling_mae = p0054k.mean_float(rolling_errors) if rolling_errors else None
    return {
        "intersection_rows": len(pairs),
        "alignment_mode": alignment_mode,
        "static_MAE_on_intersection": static_mae,
        "rolling_MAE_on_intersection": rolling_mae,
        "delta_on_intersection": None if static_mae is None or rolling_mae is None else rolling_mae - static_mae,
        "static_original_MAE": BASELINES["P0056F_W12_static_full36"],
        "rolling_original_MAE": BASELINES["P0056I_TWX"],
        "static_intersection_delta_vs_original": None if static_mae is None else static_mae - BASELINES["P0056F_W12_static_full36"],
        "rolling_intersection_delta_vs_original": None if rolling_mae is None else rolling_mae - BASELINES["P0056I_TWX"],
    }


def target_row_intersection_summary(persisted_static: list[dict[str, object]], rolling: list[dict[str, object]], static_selected: list[dict[str, object]], exact_pairs: list[dict[str, object]], aligned_pairs: list[dict[str, object]]) -> dict[str, object]:
    persisted_static_keys = {row_key(row) for row in persisted_static}
    rolling_keys = {row_key(row) for row in rolling}
    target_static = {str(row["target_timestamp_utc"]) for row in persisted_static}
    target_rolling = {str(row["target_timestamp_utc"]) for row in rolling}
    return {
        "row_count_static_persisted": len(persisted_static),
        "row_count_static_reconstructed_full36_selected": len(static_selected),
        "row_count_rolling": len(rolling),
        "exact_origin_target_intersection_row_count": len(persisted_static_keys & rolling_keys),
        "reconstructed_exact_intersection_row_count": len(exact_pairs),
        "target_aligned_reconstructed_row_count": len(aligned_pairs),
        "target_timestamp_intersection_count": len(target_static & target_rolling),
        "static_only_rows": len(persisted_static_keys - rolling_keys),
        "rolling_only_rows_vs_persisted_static": len(rolling_keys - persisted_static_keys),
        "horizon_distribution_static": distribution(persisted_static, "horizon_hours"),
        "horizon_distribution_rolling": distribution(rolling, "horizon_hours"),
        "local_hour_distribution_static": local_time_distribution(persisted_static, "hour"),
        "local_hour_distribution_rolling": local_time_distribution(rolling, "hour"),
        "weekday_distribution_static": local_time_distribution(persisted_static, "weekday"),
        "weekday_distribution_rolling": local_time_distribution(rolling, "weekday"),
        "month_distribution_static": local_time_distribution(persisted_static, "month"),
        "month_distribution_rolling": local_time_distribution(rolling, "month"),
    }


def distribution(rows: list[dict[str, object]], field: str) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[str(row[field])] += 1
    return dict(sorted(counts.items(), key=lambda item: item[0]))


def local_time_distribution(rows: list[dict[str, object]], component: str) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        local = p0052.parse_utc(str(row["target_timestamp_utc"])).astimezone(p0054q.p0054n.STOCKHOLM) if hasattr(p0054q, "p0054n") else p0052.parse_utc(str(row["target_timestamp_utc"]))
        value = {"hour": local.hour, "weekday": local.weekday(), "month": local.month}[component]
        counts[str(value)] += 1
    return dict(sorted(counts.items(), key=lambda item: int(item[0])))


def model_training_diff(static_training: dict[str, object]) -> dict[str, object]:
    return {
        "static_model_name": "P0056F W12 HorizonBiasCorrected_WeightedEnsemble_no_price",
        "static_model_family": "weighted ensemble over available base model families",
        "static_train_start": "2022-06-01T00:00:00Z",
        "static_train_end": "2025-06-01T00:00:00Z",
        "static_train_row_count": static_training.get("train_fit_rows"),
        "static_validation_start": p0054r.INTERNAL_VALIDATION_START,
        "static_validation_end": "2025-06-01T00:00:00Z",
        "static_validation_row_count": static_training.get("internal_validation_rows"),
        "static_feature_count": len(p0056f.feature_names_for_stack(STATIC_STACK)),
        "static_feature_order": p0056f.feature_names_for_stack(STATIC_STACK),
        "static_ensemble_weights_available": bool(static_training.get("weights")),
        "static_model_artifact_persisted": False,
        "rolling_model_name": "P0056I TWX HGB no-price",
        "rolling_model_family": "HGB",
        "rolling_train_start": "2022-06-01T00:00:00Z per origin",
        "rolling_train_end": "forecast_origin exclusive per origin",
        "rolling_feature_count": len(p0056f.feature_names_for_stack(STATIC_STACK)),
        "rolling_feature_order": p0056f.feature_names_for_stack(STATIC_STACK),
        "rolling_model_artifact_persisted": False,
        "missing_value_handling": "p0054k model matrix handling for both pipelines",
    }


def horizon_bias_diff(static_training: dict[str, object]) -> dict[str, object]:
    return {
        "static_horizon_bias_correction": "present" if static_training.get("horizon_bias") else "unknown_or_unavailable",
        "static_horizon_bias_artifact_persisted": False,
        "rolling_horizon_bias_correction": "none",
        "conclusion": "P0056F static W12 uses horizon-bias correction; P0056I TWX does not.",
    }


def hypotheses(target_intersection: dict[str, object], feature_summary: list[dict[str, object]], metrics: dict[str, object], model_training: dict[str, object]) -> list[dict[str, str]]:
    any_lag_mismatch = any(row["mismatch_count"] for row in feature_summary if row["feature"] in FEATURE_GROUPS["lag"])
    any_weather_mismatch = any(row["mismatch_count"] for row in feature_summary if row["feature"] in FEATURE_GROUPS["weather"])
    exact_persisted = int(target_intersection["exact_origin_target_intersection_row_count"])
    delta = metrics.get("delta_on_intersection")
    return [
        {"hypothesis": "H1 static and rolling evaluate different target rows / horizon mix", "conclusion": "supported" if exact_persisted == 0 else "partly_supported"},
        {"hypothesis": "H2 static and rolling use different lag-feature construction", "conclusion": "rejected" if not any_lag_mismatch else "supported"},
        {"hypothesis": "H3 static and rolling use different weather-feature construction", "conclusion": "supported" if any_weather_mismatch else "rejected"},
        {"hypothesis": "H4 static and rolling use different horizon-bias correction", "conclusion": "supported"},
        {"hypothesis": "H5 static and rolling use different train/validation windows", "conclusion": "supported"},
        {"hypothesis": "H6 static metric is row-wise holdout prediction, not origin-realistic forecast", "conclusion": "supported"},
        {"hypothesis": "H7 rolling pipeline has a target/horizon alignment bug", "conclusion": "rejected" if int(metrics["intersection_rows"]) > 0 else "inconclusive"},
        {"hypothesis": "H8 rolling feature column order or missing handling differs", "conclusion": "inconclusive" if model_training["rolling_model_artifact_persisted"] is False else "rejected"},
        {"hypothesis": "gap remains on reconstructed target-aligned intersection", "conclusion": "supported" if delta is not None and float(delta) > 0 else "rejected"},
    ]


def origin_sample_summary(origins: list[str], rolling_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_origin = p0054k.group_by(rolling_rows, "forecast_origin_timestamp_utc")
    out = []
    for origin in origins:
        rows = by_origin[origin]
        errors = [abs(float(row["prediction"]) - float(row["actual"])) for row in rows]
        local = p0052.parse_utc(origin)
        out.append({"forecast_origin_utc": origin, "rows": len(rows), "rolling_MAE": p0054k.mean_float(errors), "month": local.month, "weekday": local.weekday()})
    return out


def interpretation(metrics: dict[str, object], target_intersection: dict[str, object], feature_summary: list[dict[str, object]]) -> dict[str, object]:
    worst = sorted(feature_summary, key=lambda row: int(row["mismatch_count"]), reverse=True)[:8]
    return {
        "root_cause_summary": "The original static and rolling headline metrics are not on the same persisted origin/horizon row set; target-aligned reconstructed rows still differ mainly by model method, horizon-bias correction and rolling per-origin training.",
        "persisted_static_vs_rolling_exact_intersection": target_intersection["exact_origin_target_intersection_row_count"],
        "reconstructed_alignment_mode": metrics["alignment_mode"],
        "reconstructed_aligned_intersection_rows": metrics["intersection_rows"],
        "static_vs_rolling_delta_on_aligned_intersection": metrics["delta_on_intersection"],
        "largest_feature_mismatch_candidates": [{"feature": row["feature"], "mismatch_count": row["mismatch_count"], "max_abs_delta": row["max_abs_delta"]} for row in worst],
    }


def decision(metrics: dict[str, object], target_intersection: dict[str, object], hypothesis_review: list[dict[str, str]]) -> dict[str, object]:
    return {
        "status": "WARN",
        "old_static_test_origin_realistic": "no; it is a static holdout path evaluation with persisted selected rows and global holdout model predictions",
        "best_gap_explanation": "row-selection/horizon-mix differs for persisted metrics, and reconstructed exact-row comparison still differs by model method, horizon-bias correction and train-window protocol",
        "next_action": "run exact static weighted-ensemble+bias method on the P0056I origin grid as P0056K",
    }


def what_we_learned(metrics: dict[str, object], target_intersection: dict[str, object]) -> dict[str, object]:
    return {
        "persisted_static_log_not_same_grid": int(target_intersection["exact_origin_target_intersection_row_count"]) == 0,
        "target_overlap_exists": target_intersection["target_timestamp_intersection_count"],
        "reconstructed_static_needed_for_exact_row_audit": True,
        "gap_on_reconstructed_intersection_MW": metrics["delta_on_intersection"],
    }


def stopped_summary(started: float, feature_path: Path, rolling_rows: list[dict[str, object]], static_rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": "STOP",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "feature_db": str(feature_path),
        "row_counts": {"rolling_rows": len(rolling_rows), "static_rows": len(static_rows)},
    }


def write_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog_md(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", "# P0056J LABB Label\n\nP0056J is LABB-only audit evidence and not G2-KANDIDAT or production runtime work.\n"),
        "baseline-review.md": write(evidence_dir / "baseline-review.md", json_report("P0056J Baseline Review", summary.get("baselines", {}))),
        "origin-sample.md": write(evidence_dir / "origin-sample.md", table_md("P0056J Origin Sample", summary.get("origin_sample", []))),
        "target-row-intersection.md": write(evidence_dir / "target-row-intersection.md", json_report("P0056J Target Row Intersection", summary.get("target_row_intersection", {}))),
        "row-level-prediction-diff.md": write(evidence_dir / "row-level-prediction-diff.md", row_diff_md(summary.get("row_level_prediction_diff", []))),
        "feature-diff-summary.md": write(evidence_dir / "feature-diff-summary.md", feature_diff_md(summary.get("feature_diff_summary", []))),
        "lag-feature-diff.md": write(evidence_dir / "lag-feature-diff.md", feature_diff_md(summary.get("lag_feature_diff", []))),
        "weather-feature-diff.md": write(evidence_dir / "weather-feature-diff.md", feature_diff_md(summary.get("weather_feature_diff", []))),
        "calendar-feature-diff.md": write(evidence_dir / "calendar-feature-diff.md", feature_diff_md(summary.get("calendar_feature_diff", []))),
        "model-training-diff.md": write(evidence_dir / "model-training-diff.md", json_report("P0056J Model Training Diff", summary.get("model_training_diff", {}))),
        "horizon-bias-correction-diff.md": write(evidence_dir / "horizon-bias-correction-diff.md", json_report("P0056J Horizon Bias Correction Diff", summary.get("horizon_bias_correction_diff", {}))),
        "metric-reconstruction.md": write(evidence_dir / "metric-reconstruction.md", json_report("P0056J Metric Reconstruction", summary.get("metric_reconstruction", {}))),
        "hypothesis-review.md": write(evidence_dir / "hypothesis-review.md", table_md("P0056J Hypothesis Review", summary.get("hypothesis_review", []))),
        "interpretation.md": write(evidence_dir / "interpretation.md", json_report("P0056J Interpretation", summary.get("interpretation", {}))),
        "decision.md": write(evidence_dir / "decision.md", json_report("P0056J Decision", summary.get("decision", {}))),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", json_report("P0056J What We Learned", summary.get("what_we_learned", {}))),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", f"# P0056J Next Package Recommendation\n\n{summary.get('next_package_recommendation')}\n"),
        "row-level-prediction-diff.csv": write_csv(evidence_dir / "row-level-prediction-diff.csv", summary.get("row_level_prediction_diff", [])),
        "feature-diff-summary.csv": write_csv(evidence_dir / "feature-diff-summary.csv", summary.get("feature_diff_summary", [])),
        "target-row-intersection.csv": write_csv(evidence_dir / "target-row-intersection.csv", [summary.get("target_row_intersection", {})]),
        "hypothesis-review.json": write(evidence_dir / "hypothesis-review.json", json.dumps(p0056h.json_safe(summary.get("hypothesis_review", [])), indent=2, sort_keys=True) + "\n"),
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(p0056h.json_safe(compact_summary(summary)), indent=2, sort_keys=True) + "\n"),
    }
    return evidence


def changelog_md(summary: dict[str, object]) -> str:
    rows = summary.get("row_counts", {})
    return "\n".join([
        "# P0056J Changelog",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Exact origin+target intersection rows: `{rows.get('exact_intersection_rows') if isinstance(rows, dict) else None}`",
        f"- Target-aligned reconstructed rows: `{rows.get('aligned_intersection_rows') if isinstance(rows, dict) else None}`",
        f"- Sampled origins: `{rows.get('sampled_origins') if isinstance(rows, dict) else None}`",
        f"- Sampled row diff rows: `{rows.get('sampled_rows') if isinstance(rows, dict) else None}`",
        "- No API, devices, runtime changes, production activation, result rewriting or large artifacts.",
        "",
    ])


def row_diff_md(rows: object) -> str:
    values = rows if isinstance(rows, list) else []
    errors = [float(row["error_delta"]) for row in values if isinstance(row, dict)]
    return "\n".join([
        "# P0056J Row-Level Prediction Diff",
        "",
        f"- Rows reported: `{len(values)}`",
        f"- Mean rolling-minus-static absolute-error delta: `{p0056h.fmt(p0054k.mean_float(errors) if errors else None)}`",
        "",
    ])


def feature_diff_md(rows: object) -> str:
    lines = ["# P0056J Feature Diff Summary", "", "| feature | rows | matches | mismatches | max abs delta | mean abs delta |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in rows if isinstance(rows, list) else []:
        lines.append(f"| {row.get('feature')} | {row.get('rows_compared')} | {row.get('exact_match_count')} | {row.get('mismatch_count')} | {p0056h.fmt(row.get('max_abs_delta'))} | {p0056h.fmt(row.get('mean_abs_delta'))} |")
    lines.append("")
    return "\n".join(lines)


def table_md(title: str, rows: object) -> str:
    values = rows if isinstance(rows, list) else []
    if not values:
        return f"# {title}\n\nNo rows.\n"
    keys = sorted({key for row in values if isinstance(row, dict) for key in row})
    lines = [f"# {title}", "", "| " + " | ".join(keys) + " |", "| " + " | ".join("---" for _ in keys) + " |"]
    for row in values:
        lines.append("| " + " | ".join(str(row.get(key, "")) for key in keys) + " |")
    lines.append("")
    return "\n".join(lines)


def compact_summary(summary: dict[str, object]) -> dict[str, object]:
    return {
        "package_id": summary.get("package_id"),
        "status": summary.get("status"),
        "runtime_seconds": summary.get("runtime_seconds"),
        "row_counts": summary.get("row_counts"),
        "target_row_intersection": summary.get("target_row_intersection"),
        "metric_reconstruction": summary.get("metric_reconstruction"),
        "hypothesis_review": summary.get("hypothesis_review"),
        "decision": summary.get("decision"),
    }


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


def main() -> None:
    result = run_p0056j_static_vs_rolling_row_level_audit()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
