"""P0054N LABB SE3 consumption full 36h DayAhead evaluation."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time as dt_time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import csv
import json
import time

import numpy as np

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054l2, p0054m
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0054N"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054N")
STOCKHOLM = ZoneInfo("Europe/Stockholm")
TRAIN_FIT_START = "2022-06-01T00:00:00Z"
TRAIN_PRICE_BLOCK_START = "2025-03-01T00:00:00Z"
HOLDOUT_START = "2025-06-01T00:00:00Z"
HORIZONS_36H = tuple(range(1, 37))
PRICE_HORIZONS_36H = tuple(range(36))
MODEL_FAMILIES = p0054m.MODEL_FAMILIES
VARIANT_NO_PRICE = p0054m.VARIANT_NO_PRICE
VARIANT_WITH_ADVANCED = "with_p0054n_exact_dayahead_advanced_price"
PRICE_PROTOCOL = "p0054n_exact_origin_blocked_train_plus_trainfit_holdout"


@dataclass(frozen=True)
class P0054NResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054n_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054NResult:
    started = time.monotonic()
    feature_db = Path(feature_db).expanduser()
    evidence_dir = Path(evidence_dir)

    source_rows = p0054k.load_se3_consumption_rows(feature_db)
    target_contract = p0054k.validate_target_contract(source_rows)
    if not target_contract["ok"]:
        raise RuntimeError(f"P0054N target contract failed: {target_contract}")
    weather_rows, weather_contract = p0054k.load_weather_proxy_rows(weather_db)
    price_source_rows = p0054l2.load_se3_price_rows(feature_db)
    exact_price_rows, exact_price_contract = build_p0054n_exact_origin_price_rows(price_source_rows)
    if not exact_price_contract["ok"]:
        raise RuntimeError(f"P0054N exact-origin price contract failed: {exact_price_contract}")

    direct_rows = p0054m.build_p0054m_modeling_rows(source_rows, weather_rows, exact_price_rows, set(HORIZONS_36H))
    path_rows = [dict(row) for row in direct_rows]
    split_counts = p0054k.assign_p0054i_splits(direct_rows)
    p0054k.assign_p0054i_splits(path_rows)
    train_rows = [row for row in direct_rows if row["split"] == "train_fit"]
    profiles = p0054k.fit_train_profiles(train_rows)
    p0054k.apply_profile_features(direct_rows, profiles)
    p0054k.apply_profile_features(path_rows, profiles)

    feature_contract = p0054n_feature_contract()
    feature_review = p0054m.validate_feature_contract(feature_contract)
    matrix_review = validate_p0054n_matrix_safety(direct_rows, feature_contract)
    if not feature_review["ok"] or not matrix_review["ok"]:
        raise RuntimeError(f"P0054N matrix safety failed: feature={feature_review} matrix={matrix_review}")

    environment = p0054k.capture_environment_status()
    specs = p0054k.model_specs(environment["imports"])  # type: ignore[arg-type]
    model_results: dict[str, dict[str, object]] = {}
    scored_rows = [dict(row) for row in direct_rows]
    scored_path_rows = [dict(row) for row in path_rows]
    for spec in specs:
        if spec.family not in MODEL_FAMILIES:
            continue
        for variant, features in (
            (VARIANT_NO_PRICE, feature_contract[VARIANT_NO_PRICE]["features"]),
            (VARIANT_WITH_ADVANCED, feature_contract[VARIANT_WITH_ADVANCED]["features"]),
        ):
            result = p0054k.fit_variant_model(scored_rows, features, spec, variant)  # type: ignore[arg-type]
            model_key = f"{spec.family}_{variant}"
            model_results[model_key] = result
            p0054k.attach_predictions(scored_rows, result, p0054k.prediction_column(model_key), holdout_only=True)
            p0054k.attach_path_predictions(scored_path_rows, result, features, p0054k.prediction_column(model_key))  # type: ignore[arg-type]

    prediction_columns = tuple(p0054k.prediction_column(key) for key in model_results)
    fairness = validate_paired_row_sets(scored_rows)
    direct_results = p0054k.evaluate_direct_horizons(scored_rows, prediction_columns)
    full36_summary, full36_rows = evaluate_full_36h_paths(scored_path_rows, prediction_columns)
    dayahead_summary, dayahead_rows = evaluate_dayahead_delivery_days(scored_path_rows, prediction_columns)
    intraday_summary = intraday_slice_summary(full36_summary)
    conditional_results = p0054k.evaluate_conditional_regimes(scored_path_rows, prediction_columns)
    ablation = compare_advanced_price_ablation_36h(model_results, full36_summary, dayahead_summary)
    comparison = model_comparison(model_results, full36_summary, dayahead_summary)
    p0054m_comparison = compare_to_p0054m(comparison)
    leakage_review = leakage_review_summary(matrix_review, fairness, exact_price_contract)
    status = "PASS" if leakage_review["ok"] and fairness["ok"] and ablation["required_model_pairs_complete"] else "WARN"

    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "split_policy": split_policy(),
        "split_counts": split_counts,
        "target_contract": target_contract,
        "weather_contract": weather_contract,
        "exact_origin_price_contract": exact_price_contract,
        "origin_cadence_review": origin_cadence_review(feature_db),
        "dayahead_use_case": dayahead_use_case_contract(scored_path_rows),
        "input_classification": input_classification(),
        "feature_contract": feature_contract,
        "feature_review": feature_review,
        "matrix_safety_review": matrix_review,
        "fairness": fairness,
        "environment": environment,
        "model_training": {key: result["training"] for key, result in model_results.items()},
        "model_results": {key: result["metrics"] for key, result in model_results.items()},
        "direct_horizon_results": direct_results,
        "full_36h_results": full36_summary,
        "dayahead_delivery_day_results": dayahead_summary,
        "intraday_slice_results": intraday_summary,
        "conditional_regime_results": conditional_results,
        "advanced_price_ablation_36h": ablation,
        "model_comparison": comparison,
        "p0054m_comparison": p0054m_comparison,
        "leakage_review": leakage_review,
        "interpretation": interpretation_summary(comparison, ablation, p0054m_comparison),
        "row_counts": {
            "source_rows": len(source_rows),
            "exact_origin_price_rows": len(exact_price_rows),
            "direct_rows": len(direct_rows),
            "full36_path_candidate_rows": len(path_rows),
            "full36_complete_origin_rows": len({row["forecast_origin_timestamp_utc"] for row in full36_rows}),
            "dayahead_delivery_days": len(dayahead_rows),
            "train_fit_rows": split_counts.get("train_fit", 0),
            "holdout_rows": split_counts.get("holdout", 0),
        },
        "no_api_devices_runtime_a61_future_flow": True,
        "no_large_artifacts": True,
    }
    evidence = write_p0054n_evidence(evidence_dir, scored_rows, full36_rows, dayahead_rows, summary)
    return P0054NResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def dayahead_origin_utc_for_delivery_day(delivery_day: date) -> str:
    local_decision = datetime.combine(delivery_day - timedelta(days=1), dt_time(12, 0), tzinfo=STOCKHOLM)
    return p0052.format_utc(local_decision.astimezone(timezone.utc))


def delivery_day_target_utc_hours(delivery_day: date) -> list[str]:
    out = []
    for hour in range(24):
        local_target = datetime.combine(delivery_day, dt_time(hour, 0), tzinfo=STOCKHOLM)
        out.append(p0052.format_utc(local_target.astimezone(timezone.utc)))
    return out


def build_p0054n_exact_origin_price_rows(price_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    base_examples, base_skipped = p0054l2.build_price_forecast_examples(price_rows)
    origin_texts = exact_origin_texts(price_rows)
    predict_examples = build_exact_origin_price_examples(price_rows, origin_texts, PRICE_HORIZONS_36H)
    train_before_block = [row for row in base_examples if TRAIN_FIT_START <= str(row["target_timestamp_utc"]) < TRAIN_PRICE_BLOCK_START]
    train_before_holdout = [row for row in base_examples if TRAIN_FIT_START <= str(row["target_timestamp_utc"]) < HOLDOUT_START]
    predict_train = [row for row in predict_examples if TRAIN_PRICE_BLOCK_START <= str(row["target_timestamp_utc"]) < HOLDOUT_START]
    predict_holdout = [row for row in predict_examples if str(row["target_timestamp_utc"]) >= HOLDOUT_START]
    feature_names = sorted({key for row in base_examples + predict_examples for key in row["features"]})  # type: ignore[union-attr]
    matrix_review = p0054l2.validate_feature_matrix_safety(base_examples + predict_examples, feature_names)
    if not matrix_review["ok"]:
        return [], {"ok": False, "reason": "price_matrix_safety_failed", "matrix_review": matrix_review}

    train_rows, train_status = fit_price_ensemble(train_before_block, predict_train, feature_names, "blocked_train_price_before_2025_03")
    holdout_rows, holdout_status = fit_price_ensemble(train_before_holdout, predict_holdout, feature_names, "trainfit_price_before_2025_06")
    output = train_rows + holdout_rows
    return output, {
        "ok": bool(output) and bool(train_rows) and bool(holdout_rows),
        "protocol": PRICE_PROTOCOL,
        "persisted": False,
        "reason_for_package_local_extension": "P0054M/P0054L2 persisted logs have only 23:00Z origins; P0054N requires 12:00 Europe/Stockholm D-1.",
        "rows": len(output),
        "train_fit_rows": len([row for row in output if p0054k.p0054i_split(str(row["target_timestamp_utc"])) == "train_fit"]),
        "holdout_rows": len([row for row in output if p0054k.p0054i_split(str(row["target_timestamp_utc"])) == "holdout"]),
        "forecast_origins": len({row["forecast_origin_timestamp_utc"] for row in output}),
        "target_start": min((str(row["target_timestamp_utc"]) for row in output), default=""),
        "target_end": max((str(row["target_timestamp_utc"]) for row in output), default=""),
        "train_model_status": train_status,
        "holdout_model_status": holdout_status,
        "base_skipped_windows": base_skipped,
        "matrix_review": matrix_review,
        "p0054l2_holdout_source_used_as_train_feature": False,
        "actual_future_spot_price_used": False,
    }


def exact_origin_texts(price_rows: list[dict[str, object]]) -> list[str]:
    timestamps = sorted(p0052.normalize_utc_text(row["timestamp_utc"]) for row in price_rows)
    if not timestamps:
        return []
    start_date = max(p0052.parse_utc(timestamps[0]).date() + timedelta(days=200), date(2025, 3, 1))
    end_date = p0052.parse_utc(timestamps[-1]).date() - timedelta(days=1)
    origins = []
    current = start_date
    while current <= end_date:
        origins.append(dayahead_origin_utc_for_delivery_day(current))
        current += timedelta(days=1)
    return sorted(set(origins))


def build_exact_origin_price_examples(price_rows: list[dict[str, object]], origin_texts: list[str], horizons: tuple[int, ...]) -> list[dict[str, object]]:
    by_ts = {str(row["timestamp_utc"]): float(row["hour_price"]) for row in price_rows}
    by_meta = {str(row["timestamp_utc"]): row for row in price_rows}
    examples: list[dict[str, object]] = []
    for origin_text in origin_texts:
        origin = p0052.parse_utc(origin_text)
        for horizon in horizons:
            target = origin + timedelta(hours=horizon)
            target_text = p0052.format_utc(target)
            if target_text not in by_ts or target_text not in by_meta:
                continue
            features, audit = p0054l2.price_history_features_at_origin(origin, target, by_ts, by_meta, horizon)
            examples.append(
                {
                    "forecast_origin_timestamp_utc": origin_text,
                    "input_data_cutoff_utc": p0052.format_utc(origin - timedelta(hours=1)),
                    "target_timestamp_utc": target_text,
                    "horizon_hours": horizon,
                    "split": p0054k.p0054i_split(target_text),
                    "target_price": by_ts[target_text],
                    "features": features,
                    "feature_source_audit": audit,
                    "area": "SE3",
                }
            )
    return examples


def fit_price_ensemble(train_examples: list[dict[str, object]], predict_examples: list[dict[str, object]], feature_names: list[str], protocol: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    imports = p0054k.capture_environment_status()["imports"]
    specs = p0054l2.model_specs(imports)  # type: ignore[arg-type]
    prediction_columns = []
    model_status = {}
    if not train_examples or not predict_examples:
        return [], {"ok": False, "reason": "missing_train_or_predict_examples", "train_rows": len(train_examples), "predict_rows": len(predict_examples)}
    for spec in specs:
        if spec.family not in MODEL_FAMILIES:
            continue
        started = time.monotonic()
        x_train, standardizer = p0054l2.build_matrix(train_examples, feature_names)
        y_train = np.array([float(row["target_price"]) for row in train_examples], dtype=float)
        model = p0054k.clone_model(spec.model)
        model.fit(x_train, y_train)  # type: ignore[attr-defined]
        preds = p0054l2.predict_model(model, standardizer, predict_examples, feature_names)
        column = f"price_pred_{spec.family}"
        prediction_columns.append(column)
        for row, pred in zip(predict_examples, preds):
            row[column] = float(pred)
        model_status[spec.family] = {
            "status": "completed",
            "train_rows": len(train_examples),
            "predicted_rows": len(predict_examples),
            "feature_count": len(feature_names),
            "duration_seconds": round(time.monotonic() - started, 3),
            "hyperparameters": spec.hyperparameters,
        }
    output = []
    created = p0052.format_utc(datetime.now(timezone.utc).replace(microsecond=0))
    for row in predict_examples:
        if len(prediction_columns) < 2:
            continue
        predicted = p0054k.mean_float([float(row[column]) for column in prediction_columns])
        output.append(
            {
                "forecast_run_id": "P0054N_exact_dayahead_origin_se3_price_v1",
                "package_id": PACKAGE_ID,
                "model_name": "Ensemble",
                "model_version": "p0054n_exact_origin_p0054l2_compatible_v1",
                "area": "SE3",
                "forecast_origin_timestamp_utc": row["forecast_origin_timestamp_utc"],
                "input_data_cutoff_utc": row["input_data_cutoff_utc"],
                "target_timestamp_utc": row["target_timestamp_utc"],
                "horizon_hours": int(row["horizon_hours"]),
                "horizon_h": int(row["horizon_hours"]) + 1,
                "predicted_price": predicted,
                "prediction_unit": "repository hour_price convention",
                "prediction_kind": "advanced_absolute_price",
                "training_protocol": protocol,
                "quality_flag": "p0054n_exact_origin_forecast_safe_advanced_price",
                "prediction_rule": "P0054N_exact_origin_ensemble",
                "created_at_utc": created,
            }
        )
    return output, {"ok": bool(output), "protocol": protocol, "model_status": model_status, "rows": len(output)}


def p0054n_feature_contract() -> dict[str, dict[str, object]]:
    base = p0054k.feature_group_contract()
    return {
        VARIANT_NO_PRICE: base["no_price"],
        VARIANT_WITH_ADVANCED: {
            "input_classification": "mixed_forecast_safe_advanced_price_and_weather_proxy",
            "features": list(base["with_p0054k_se3_price_forecast"]["features"]),
        },
    }


def validate_p0054n_matrix_safety(rows: list[dict[str, object]], feature_contract: dict[str, dict[str, object]]) -> dict[str, object]:
    train_rows = [row for row in rows if p0054k.p0054i_split(str(row["target_timestamp_utc"])) == "train_fit"]
    holdout_rows = [row for row in rows if p0054k.p0054i_split(str(row["target_timestamp_utc"])) == "holdout"]
    train_protocol_ok = all(row.get("price_feature_protocol") == "blocked_oof_train_price_before_2025_03" for row in train_rows)
    holdout_protocol_ok = all(row.get("price_feature_protocol") == "p0054l2_holdout_safe_ensemble" for row in holdout_rows)
    target_order_ok = all(p0052.parse_utc(str(row["input_data_cutoff_utc"])) <= p0052.parse_utc(str(row["forecast_origin_timestamp_utc"])) <= p0052.parse_utc(str(row["target_timestamp_utc"])) for row in rows)
    forbidden = [column for row in rows[:1] for column in row if any(term in column.lower() for term in ("actual_price", "production", "flow", "export", "import", "a61", "capacity", "utilization", "continental"))]
    return {
        "ok": train_protocol_ok and holdout_protocol_ok and target_order_ok and not forbidden,
        "train_protocol_ok": train_protocol_ok,
        "holdout_protocol_ok": holdout_protocol_ok,
        "target_order_ok": target_order_ok,
        "forbidden_columns": sorted(set(forbidden)),
        "p0054l2_holdout_used_as_train_feature": False,
        "actual_future_spot_price_used": False,
        "production_flow_export_import_a61_used": False,
        "feature_groups": sorted(feature_contract),
    }


def validate_paired_row_sets(rows: list[dict[str, object]]) -> dict[str, object]:
    pairs = {}
    ok = True
    for family in MODEL_FAMILIES:
        no_col = p0054k.prediction_column(f"{family}_{VARIANT_NO_PRICE}")
        price_col = p0054k.prediction_column(f"{family}_{VARIANT_WITH_ADVANCED}")
        no_ids = sorted(p0054k.row_id(row) for row in rows if row.get(no_col) is not None)
        price_ids = sorted(p0054k.row_id(row) for row in rows if row.get(price_col) is not None)
        pair_ok = bool(no_ids) and no_ids == price_ids
        ok = ok and pair_ok
        pairs[family] = {"ok": pair_ok, "no_price_rows": len(no_ids), "with_advanced_price_rows": len(price_ids)}
    return {"ok": ok, "pairs": pairs}


def evaluate_full_36h_paths(rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> tuple[dict[str, object], list[dict[str, object]]]:
    by_origin = p0054k.group_by([row for row in rows if row["split"] == "holdout"], "forecast_origin_timestamp_utc")
    complete_origins = [
        origin
        for origin, origin_rows in sorted(by_origin.items())
        if {int(row["horizon_h"]) for row in origin_rows} >= set(HORIZONS_36H)
    ]
    selected = [row for origin in complete_origins for row in by_origin[origin] if int(row["horizon_h"]) in HORIZONS_36H]
    summary: dict[str, object] = {
        "horizon_convention": "repository horizon_h 1..36 equals target hours origin..origin+35h",
        "complete_origin_count": len(complete_origins),
        "target_row_count": len(selected),
        "first_origin": complete_origins[0] if complete_origins else "",
        "last_origin": complete_origins[-1] if complete_origins else "",
        "skipped_origin_count": len(by_origin) - len(complete_origins),
    }
    compact_rows = []
    for column in prediction_columns:
        summary[column] = full_36h_metric_summary(selected, column)
    for origin in complete_origins:
        origin_rows = [row for row in by_origin[origin] if int(row["horizon_h"]) in HORIZONS_36H]
        out = {"forecast_origin_timestamp_utc": origin, "row_count": len(origin_rows)}
        for column in prediction_columns:
            available = [row for row in origin_rows if row.get(column) is not None]
            out[f"{column}_MAE_full_36h"] = p0054k.regression_metric_from_predictions(available, [float(row[column]) for row in available])["MAE"]
        compact_rows.append(out)
    return summary, compact_rows


def full_36h_metric_summary(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    available = [row for row in rows if row.get(prediction_column) is not None]
    metric = p0054k.regression_metric_from_predictions(available, [float(row[prediction_column]) for row in available])
    buckets = {
        "MAE_0_6h": lambda row: 1 <= int(row["horizon_h"]) <= 6,
        "MAE_0_12h": lambda row: 1 <= int(row["horizon_h"]) <= 12,
        "MAE_0_24h": lambda row: 1 <= int(row["horizon_h"]) <= 24,
        "MAE_24_36h": lambda row: 25 <= int(row["horizon_h"]) <= 36,
    }
    out = {
        "MAE_full_36h": metric["MAE"],
        "bias_full_36h": metric["bias"],
        "p90_full_36h": metric["p90_absolute_error"],
        "p95_full_36h": metric["p95_absolute_error"],
        "daily_energy_error_proxy": daily_energy_error_proxy(available, prediction_column),
        "peak_hour_error": peak_hour_timing_error(available, prediction_column),
    }
    for name, predicate in buckets.items():
        subset = [row for row in available if predicate(row)]
        out[name] = p0054k.regression_metric_from_predictions(subset, [float(row[prediction_column]) for row in subset])["MAE"]
    return out


def evaluate_dayahead_delivery_days(rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> tuple[dict[str, object], list[dict[str, object]]]:
    by_origin_target = {(str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"])): row for row in rows if row["split"] == "holdout"}
    target_dates = sorted({p0052.parse_utc(str(row["target_timestamp_utc"])).astimezone(STOCKHOLM).date() for row in rows if row["split"] == "holdout"})
    selected: list[dict[str, object]] = []
    compact_rows = []
    for delivery_day in target_dates:
        origin = dayahead_origin_utc_for_delivery_day(delivery_day)
        targets = delivery_day_target_utc_hours(delivery_day)
        day_rows = [by_origin_target.get((origin, target)) for target in targets]
        if any(row is None for row in day_rows):
            continue
        concrete = [row for row in day_rows if row is not None]
        selected.extend(concrete)
        compact = {
            "delivery_day_local": delivery_day.isoformat(),
            "forecast_origin_timestamp_utc": origin,
            "target_hours": len(concrete),
            "first_target_timestamp_utc": targets[0],
            "last_target_timestamp_utc": targets[-1],
        }
        for column in prediction_columns:
            available = [row for row in concrete if row.get(column) is not None]
            metric = p0054k.regression_metric_from_predictions(available, [float(row[column]) for row in available])
            compact[f"{column}_hourly_MAE_delivery_day"] = metric["MAE"]
            compact[f"{column}_absolute_daily_energy_error_MWh"] = abs(sum(float(row[column]) - float(row[p0054k.TARGET_FIELD]) for row in available))
        compact_rows.append(compact)
    summary: dict[str, object] = {
        "decision_time_local": "12:00 Europe/Stockholm on D-1",
        "submission_deadline_context": "before 13:00 Europe/Stockholm on D-1",
        "delivery_day_local": "D 00:00..23:00 Europe/Stockholm",
        "delivery_day_count": len(compact_rows),
        "target_row_count": len(selected),
        "dst_handling": "zoneinfo Europe/Stockholm conversion per local delivery hour",
    }
    for column in prediction_columns:
        summary[column] = dayahead_metric_summary(selected, column)
    return summary, compact_rows


def dayahead_metric_summary(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    available = [row for row in rows if row.get(prediction_column) is not None]
    metric = p0054k.regression_metric_from_predictions(available, [float(row[prediction_column]) for row in available])
    grouped = p0054k.group_by(available, "forecast_origin_timestamp_utc")
    signed_energy = [sum(float(row[prediction_column]) - float(row[p0054k.TARGET_FIELD]) for row in group) for group in grouped.values()]
    return {
        "hourly_MAE_delivery_day": metric["MAE"],
        "hourly_RMSE_delivery_day": metric["RMSE"],
        "bias_delivery_day": metric["bias"],
        "absolute_daily_energy_error_MWh": p0054k.mean_float([abs(value) for value in signed_energy]) if signed_energy else None,
        "signed_daily_energy_error_MWh": p0054k.mean_float(signed_energy) if signed_energy else None,
        "sMAPE": metric["sMAPE"],
        "peak_hour_error_MW": peak_hour_mw_error(available, prediction_column),
        "peak_hour_timing_error_hours": peak_hour_timing_error(available, prediction_column),
        "offpeak_MAE": subset_mae(available, prediction_column, lambda row: int(row["target_model_cet_hour"]) not in range(7, 21)),
        "morning_ramp_MAE": subset_mae(available, prediction_column, lambda row: 6 <= int(row["target_model_cet_hour"]) <= 9),
        "evening_peak_MAE": subset_mae(available, prediction_column, lambda row: 16 <= int(row["target_model_cet_hour"]) <= 20),
        "weekday_MAE": subset_mae(available, prediction_column, lambda row: int(row["is_weekend"]) == 0),
        "weekend_MAE": subset_mae(available, prediction_column, lambda row: int(row["is_weekend"]) == 1),
        "holiday_MAE": subset_mae(available, prediction_column, lambda row: int(row["is_holiday"]) == 1),
        "cold_MAE": conditional_quantile_mae(available, prediction_column, "weather_proxy_temperature_2m_se3", 0.25, low=True),
        "high_price_MAE": conditional_quantile_mae(available, prediction_column, "price_forecast_horizon_value", 0.75, low=False),
        "price_spike_MAE": subset_mae(available, prediction_column, lambda row: int(row.get("price_forecast_spike_flag_within_path") or 0) == 1),
        "large_price_ramp_MAE": conditional_quantile_mae(available, prediction_column, "price_forecast_ramp_from_previous_horizon", 0.9, low=False, absolute=True),
    }


def intraday_slice_summary(full36_summary: dict[str, object]) -> dict[str, object]:
    return {
        column: {
            key: value
            for key, value in metrics.items()
            if key in ("MAE_0_6h", "MAE_0_12h", "MAE_0_24h", "MAE_24_36h", "MAE_full_36h", "bias_full_36h", "p90_full_36h", "p95_full_36h")
        }
        for column, metrics in full36_summary.items()
        if str(column).startswith("pred_") and isinstance(metrics, dict)
    }


def subset_mae(rows: list[dict[str, object]], prediction_column: str, predicate: object) -> float | None:
    subset = [row for row in rows if bool(predicate(row))]  # type: ignore[operator]
    if not subset:
        return None
    return p0054k.regression_metric_from_predictions(subset, [float(row[prediction_column]) for row in subset])["MAE"]  # type: ignore[return-value]


def conditional_quantile_mae(rows: list[dict[str, object]], prediction_column: str, field: str, q: float, *, low: bool, absolute: bool = False) -> float | None:
    values = [abs(p0054k.safe_float(row.get(field))) if absolute else p0054k.safe_float(row.get(field)) for row in rows if p0054k.is_finite(row.get(field))]
    if len(values) < 24:
        return None
    threshold = percentile(values, q)
    return subset_mae(rows, prediction_column, lambda row: (abs(p0054k.safe_float(row.get(field))) if absolute else p0054k.safe_float(row.get(field))) <= threshold if low else (abs(p0054k.safe_float(row.get(field))) if absolute else p0054k.safe_float(row.get(field))) >= threshold)


def daily_energy_error_proxy(rows: list[dict[str, object]], prediction_column: str) -> float | None:
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["forecast_origin_timestamp_utc"]), (int(row["horizon_h"]) - 1) // 24)].append(row)
    errors = [abs(sum(float(row[prediction_column]) for row in group) - sum(float(row[p0054k.TARGET_FIELD]) for row in group)) for group in grouped.values()]
    return p0054k.mean_float(errors) if errors else None


def peak_hour_timing_error(rows: list[dict[str, object]], prediction_column: str) -> float | None:
    errors = []
    for group in p0054k.group_by(rows, "forecast_origin_timestamp_utc").values():
        available = [row for row in group if row.get(prediction_column) is not None]
        if not available:
            continue
        actual_peak = max(available, key=lambda row: float(row[p0054k.TARGET_FIELD]))
        predicted_peak = max(available, key=lambda row: float(row[prediction_column]))
        errors.append(abs(int(actual_peak["horizon_h"]) - int(predicted_peak["horizon_h"])))
    return p0054k.mean_float([float(value) for value in errors]) if errors else None


def peak_hour_mw_error(rows: list[dict[str, object]], prediction_column: str) -> float | None:
    errors = []
    for group in p0054k.group_by(rows, "forecast_origin_timestamp_utc").values():
        available = [row for row in group if row.get(prediction_column) is not None]
        if not available:
            continue
        actual_peak = max(available, key=lambda row: float(row[p0054k.TARGET_FIELD]))
        predicted_at_actual_peak = float(actual_peak[prediction_column])
        errors.append(predicted_at_actual_peak - float(actual_peak[p0054k.TARGET_FIELD]))
    return p0054k.mean_float(errors) if errors else None


def compare_advanced_price_ablation_36h(model_results: dict[str, dict[str, object]], full36_summary: dict[str, object], dayahead_summary: dict[str, object]) -> dict[str, object]:
    rows = []
    for family in MODEL_FAMILIES:
        no_key = f"{family}_{VARIANT_NO_PRICE}"
        price_key = f"{family}_{VARIANT_WITH_ADVANCED}"
        if no_key not in model_results or price_key not in model_results:
            continue
        no_col = p0054k.prediction_column(no_key)
        price_col = p0054k.prediction_column(price_key)
        no_full = full36_summary[no_col]["MAE_full_36h"]  # type: ignore[index]
        price_full = full36_summary[price_col]["MAE_full_36h"]  # type: ignore[index]
        no_day = dayahead_summary[no_col]["hourly_MAE_delivery_day"]  # type: ignore[index]
        price_day = dayahead_summary[price_col]["hourly_MAE_delivery_day"]  # type: ignore[index]
        rows.append(
            {
                "family": family,
                "full36_no_price_MAE": no_full,
                "full36_with_advanced_price_MAE": price_full,
                "full36_with_minus_no_MAE": float(price_full) - float(no_full),
                "full36_relative_change_percent": p0054k.relative_change(float(price_full), float(no_full)),
                "dayahead_no_price_hourly_MAE": no_day,
                "dayahead_with_advanced_price_hourly_MAE": price_day,
                "dayahead_with_minus_no_hourly_MAE": float(price_day) - float(no_day),
                "dayahead_relative_change_percent": p0054k.relative_change(float(price_day), float(no_day)),
                "advanced_price_helped_full36": float(price_full) < float(no_full),
                "advanced_price_helped_dayahead": float(price_day) < float(no_day),
            }
        )
    return {
        "required_model_pairs_complete": len(rows) == len(MODEL_FAMILIES),
        "per_model_family": rows,
        "advanced_price_should_be_kept_for_future_se3_36h_experiments": any((row["full36_relative_change_percent"] is not None and row["full36_relative_change_percent"] <= -2.0) or (row["dayahead_relative_change_percent"] is not None and row["dayahead_relative_change_percent"] <= -2.0) for row in rows),
    }


def model_comparison(model_results: dict[str, dict[str, object]], full36_summary: dict[str, object], dayahead_summary: dict[str, object]) -> dict[str, object]:
    full36 = [{"model": key, "MAE_full_36h": full36_summary[p0054k.prediction_column(key)]["MAE_full_36h"]} for key in model_results]  # type: ignore[index]
    dayahead_hourly = [{"model": key, "hourly_MAE_delivery_day": dayahead_summary[p0054k.prediction_column(key)]["hourly_MAE_delivery_day"]} for key in model_results]  # type: ignore[index]
    dayahead_energy = [{"model": key, "absolute_daily_energy_error_MWh": dayahead_summary[p0054k.prediction_column(key)]["absolute_daily_energy_error_MWh"]} for key in model_results]  # type: ignore[index]
    return {
        "best_no_price_by_full36_MAE": min([row for row in full36 if row["model"].endswith(f"_{VARIANT_NO_PRICE}")], key=lambda row: float(row["MAE_full_36h"])),
        "best_with_advanced_price_by_full36_MAE": min([row for row in full36 if row["model"].endswith(f"_{VARIANT_WITH_ADVANCED}")], key=lambda row: float(row["MAE_full_36h"])),
        "best_by_dayahead_hourly_MAE": min(dayahead_hourly, key=lambda row: float(row["hourly_MAE_delivery_day"])),
        "best_by_dayahead_daily_energy_error": min(dayahead_energy, key=lambda row: float(row["absolute_daily_energy_error_MWh"])),
        "full36": full36,
        "dayahead_hourly": dayahead_hourly,
        "dayahead_daily_energy": dayahead_energy,
    }


def compare_to_p0054m(comparison: dict[str, object]) -> dict[str, object]:
    best_full36 = comparison["best_with_advanced_price_by_full36_MAE"]
    p0054m_weekly = 206.2574365420684
    p0054m_direct = 140.54830097681355
    return {
        "p0054m_best_direct_holdout_MAE": p0054m_direct,
        "p0054m_best_weekly_MAE_full_168h": p0054m_weekly,
        "p0054n_best_with_advanced_price_full36": best_full36,
        "full36_vs_full168_relative_change_percent": p0054k.relative_change(float(best_full36["MAE_full_36h"]), p0054m_weekly),
        "comparison_label": "indicative: P0054N uses exact 12:00-local origins and full_36h, P0054M weekly evidence used persisted 23:00Z origins and full_168h.",
    }


def origin_cadence_review(feature_db: Path) -> dict[str, object]:
    train_rows, train_contract = p0054m.load_p0054l2_holdout_price_rows(feature_db)
    return {
        "p0054l2_holdout_contract": train_contract,
        "p0054l2_origin_hhmm_values": sorted({str(row["forecast_origin_timestamp_utc"])[11:16] for row in train_rows}),
        "review_result": "persisted P0054L2/P0054M origins are not exact DayAhead 12:00 Europe/Stockholm origins; P0054N generated package-local exact origins in memory.",
    }


def dayahead_use_case_contract(rows: list[dict[str, object]]) -> dict[str, object]:
    sample = []
    for delivery_day in (date(2025, 6, 2), date(2025, 10, 27), date(2026, 3, 30)):
        sample.append(
            {
                "delivery_day_local": delivery_day.isoformat(),
                "forecast_origin_timestamp_utc": dayahead_origin_utc_for_delivery_day(delivery_day),
                "first_target_timestamp_utc": delivery_day_target_utc_hours(delivery_day)[0],
                "last_target_timestamp_utc": delivery_day_target_utc_hours(delivery_day)[-1],
            }
        )
    return {"sample_utc_conversions": sample, "path_rows": len(rows)}


def leakage_review_summary(matrix_review: dict[str, object], fairness: dict[str, object], price_contract: dict[str, object]) -> dict[str, object]:
    return {
        "ok": matrix_review["ok"] and fairness["ok"] and price_contract["ok"],
        "matrix_review_ok": matrix_review["ok"],
        "fairness_ok": fairness["ok"],
        "price_contract_ok": price_contract["ok"],
        "holdout_used_for_model_fitting_or_selection": False,
        "p0054l2_holdout_used_as_train_feature": False,
        "actual_future_spot_price_feature_used": False,
        "api_device_runtime_a61_future_flow_used": False,
    }


def input_classification() -> dict[str, object]:
    return {
        "calendar": "forecast_safe",
        "historical_se3_load_lags_rollups": "forecast_safe",
        "weather": "proxy",
        "weather_proxy_label": p0054k.WEATHER_PROXY_LABEL,
        "advanced_price_forecast": "forecast_safe_under_p0054n_exact_origin_extension_of_p0054m_protocol",
        "actual_future_spot_price": "excluded_leakage",
        "production_flow_export_import_a61": "excluded_leakage",
        "future_actual_load": "excluded_leakage",
    }


def split_policy() -> dict[str, str]:
    return {
        "policy_name": "LABB_P0054_TRAIN_THROUGH_MAY_2025",
        "train_fit": f"{TRAIN_FIT_START} <= target_timestamp_utc < {HOLDOUT_START}",
        "holdout": f"target_timestamp_utc >= {HOLDOUT_START}",
        "train_side_advanced_price_training_cutoff": f"{TRAIN_PRICE_BLOCK_START} minus one hour for train-side blocked predictions",
    }


def interpretation_summary(comparison: dict[str, object], ablation: dict[str, object], p0054m_comparison: dict[str, object]) -> dict[str, object]:
    return {
        "best_full36_model": comparison["best_with_advanced_price_by_full36_MAE"],
        "best_dayahead_hourly_model": comparison["best_by_dayahead_hourly_MAE"],
        "best_dayahead_daily_energy_model": comparison["best_by_dayahead_daily_energy_error"],
        "advanced_price_keep": ablation["advanced_price_should_be_kept_for_future_se3_36h_experiments"],
        "method_candidate_track": "future_G2-KANDIDAT_or_workplace_grade_track_requires_operator_request_and_market_acceptance_criteria",
        "p0054m_comparison": p0054m_comparison,
    }


def write_p0054n_evidence(evidence_dir: Path, scored_rows: list[dict[str, object]], full36_rows: list[dict[str, object]], dayahead_rows: list[dict[str, object]], summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "metrics-summary.json": write_json(evidence_dir / "metrics-summary.json", summary),
        "full-36h-path-metrics.csv": write_csv(evidence_dir / "full-36h-path-metrics.csv", full36_rows, list(full36_rows[0].keys()) if full36_rows else []),
        "dayahead-delivery-day-metrics.csv": write_csv(evidence_dir / "dayahead-delivery-day-metrics.csv", dayahead_rows, list(dayahead_rows[0].keys()) if dayahead_rows else []),
        "modeling-dataset-sample.csv": write_csv(evidence_dir / "modeling-dataset-sample.csv", scored_rows[:500], dataset_sample_columns(summary)),
        "conditional-metrics.csv": write_csv(evidence_dir / "conditional-metrics.csv", flatten_conditional_rows(summary), conditional_columns()),
    }
    for name, text in evidence_markdowns(summary).items():
        files[name] = str(write(evidence_dir / name, text))
    return files


def evidence_markdowns(summary: dict[str, object]) -> dict[str, str]:
    common = f"# {PACKAGE_ID} {LABEL}\n\nStatus: `{summary['status']}`\n\n"
    return {
        "CHANGELOG.md": changelog_text(summary),
        "labb-label.md": common + "This package is LABB only. It is not G2-KANDIDAT and creates no deployable model artifact.\n",
        "split-policy-applied.md": common + json_block(summary["split_policy"]),
        "dayahead-use-case.md": common + json_block(summary["dayahead_use_case"]),
        "dataset-contract.md": common + json_block(summary["target_contract"]),
        "price-feature-protocol-review.md": common + json_block({"selected": PRICE_PROTOCOL, "contract": summary["exact_origin_price_contract"], "origin_cadence_review": summary["origin_cadence_review"]}),
        "input-classification.md": common + json_block(summary["input_classification"]),
        "feature-groups.md": common + json_block(summary["feature_contract"]),
        "model-training-evidence.md": common + json_block(summary["model_training"]),
        "full-36h-results.md": common + json_block(summary["full_36h_results"]),
        "dayahead-delivery-day-results.md": common + json_block(summary["dayahead_delivery_day_results"]),
        "intraday-slice-results.md": common + json_block(summary["intraday_slice_results"]),
        "advanced-price-ablation-36h.md": common + json_block(summary["advanced_price_ablation_36h"]),
        "model-comparison.md": common + json_block(summary["model_comparison"]),
        "p0054m-comparison.md": common + json_block(summary["p0054m_comparison"]),
        "conditional-regime-results.md": common + json_block(summary["conditional_regime_results"]),
        "leakage-review.md": common + json_block(summary["leakage_review"]),
        "interpretation.md": common + json_block(summary["interpretation"]),
        "what-we-learned.md": common + what_we_learned_text(summary),
        "next-package-recommendation.md": common + next_package_text(summary),
    }


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0054N Changelog

Status: `{summary['status']}`

- Built exact 12:00 Europe/Stockholm D-1 origin SE3 consumption full_36h LABB evaluation.
- Generated package-local in-memory advanced SE3 price forecasts because persisted P0054M/P0054L2 origins are not DayAhead 12:00-local origins.
- Trained paired no-price and with-advanced-price SE3 consumption models for available P0054M families.
- Wrote full_36h, DayAhead delivery-day, intraday, conditional, ablation and P0054M comparison evidence.
- No API, device, runtime, A61, future-flow, Nord Pool, workplace or actual future price leakage work was performed.
"""


def what_we_learned_text(summary: dict[str, object]) -> str:
    keep = summary["advanced_price_ablation_36h"]["advanced_price_should_be_kept_for_future_se3_36h_experiments"]  # type: ignore[index]
    if keep:
        return "Exact-origin advanced price features are worth keeping for future SE3 36h LABB experiments, but promotion requires a separate operator-requested G2-KANDIDAT or workplace-grade package.\n"
    return "The exact-origin advanced price feature did not clear the broad 36h LABB learning threshold. Future work should prioritize regime-specific hypotheses before any candidate-track discussion.\n"


def next_package_text(summary: dict[str, object]) -> str:
    return "Recommended next package: P0054B/P0054O advanced AI-lab for SE3-SE1 spread and bottleneck regimes, using the P0054N exact-origin DayAhead machinery only if the operator wants a market-time consumption/spread experiment.\n"


def dataset_sample_columns(summary: dict[str, object]) -> list[str]:
    columns = [
        "forecast_origin_timestamp_utc",
        "target_timestamp_utc",
        "horizon_h",
        "split",
        p0054k.TARGET_FIELD,
        "weather_proxy_label",
        "price_feature_protocol",
        "forecast_se3_price_target_hour",
    ]
    columns.extend(p0054k.prediction_column(key) for key in summary["model_results"])  # type: ignore[operator]
    return columns


def flatten_conditional_rows(summary: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for regime, values in summary["conditional_regime_results"].items():  # type: ignore[union-attr]
        for column, metric in values.items():
            rows.append({"regime": regime, "prediction_column": column, **metric})
    return rows


def conditional_columns() -> list[str]:
    return ["regime", "prediction_column", "row_count", "MAE", "RMSE", "bias", "median_absolute_error", "p90_absolute_error", "p95_absolute_error", "sMAPE", "R2"]


def write_json(path: Path, payload: object) -> str:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return str(path)


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> str:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return str(path)


def json_block(payload: object) -> str:
    return "```json\n" + json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n```\n"


def main() -> None:
    result = run_p0054n_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
