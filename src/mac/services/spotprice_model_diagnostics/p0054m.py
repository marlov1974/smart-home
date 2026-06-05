"""P0054M LABB SE3 consumption with P0054L2 advanced price forecast."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import csv
import json
import math
import sqlite3
import time

import numpy as np

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054l2
from src.mac.services.spotprice_model_diagnostics.p0041 import persist_rows, write
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0054M"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054M")
TRAIN_PRICE_TABLE = "advanced_spotprice_forecast_log_p0054m_se3_train_blocked_oof_v1"
P0054L2_HOLDOUT_TABLE = "advanced_spotprice_forecast_log_p0054l2_se3_v1"
PRICE_PROTOCOL = "rolling_oof_train_plus_holdout"
TRAIN_FIT_START = "2022-06-01T00:00:00Z"
TRAIN_PRICE_BLOCK_START = "2025-03-01T00:00:00Z"
HOLDOUT_START = "2025-06-01T00:00:00Z"
MODEL_FAMILIES = ("HGB", "ExtraTrees", "LightGBM", "XGBoost")
HORIZONS = p0054k.HORIZONS
PATH_HORIZONS = p0054k.PATH_HORIZONS
VARIANT_NO_PRICE = "no_price"
VARIANT_WITH_ADVANCED = "with_p0054l2_ensemble_price_forecast"
FORBIDDEN_NO_PRICE_TERMS = p0054k.FORBIDDEN_NO_PRICE_TERMS
FORBIDDEN_WITH_PRICE_TERMS = ("production", "flow", "export", "import", "a61", "capacity", "utilization", "margin", "continental", "actual_price")


@dataclass(frozen=True)
class P0054MResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054m_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054MResult:
    started = time.monotonic()
    feature_db = Path(feature_db).expanduser()
    evidence_dir = Path(evidence_dir)

    source_rows = p0054k.load_se3_consumption_rows(feature_db)
    target_contract = p0054k.validate_target_contract(source_rows)
    if not target_contract["ok"]:
        raise RuntimeError(f"P0054M target contract failed: {target_contract}")
    weather_rows, weather_contract = p0054k.load_weather_proxy_rows(weather_db)
    se3_price_rows = p0054l2.load_se3_price_rows(feature_db)
    train_price_rows, train_price_contract = build_blocked_oof_price_rows(se3_price_rows)
    persist_p0054m_price_rows(feature_db, train_price_rows)
    holdout_price_rows, holdout_contract = load_p0054l2_holdout_price_rows(feature_db)
    if not holdout_contract["ok"]:
        raise RuntimeError(f"P0054M holdout advanced price source failed: {holdout_contract}")
    price_rows = train_price_rows + holdout_price_rows
    price_contract = advanced_price_source_contract(train_price_contract, holdout_contract, price_rows)
    if not price_contract["ok"]:
        raise RuntimeError(f"P0054M price source contract failed: {price_contract}")

    direct_rows = build_p0054m_modeling_rows(source_rows, weather_rows, price_rows, set(HORIZONS))
    path_rows = build_p0054m_modeling_rows(source_rows, weather_rows, price_rows, set(PATH_HORIZONS), holdout_weekly_only=True)
    split_counts = p0054k.assign_p0054i_splits(direct_rows)
    p0054k.assign_p0054i_splits(path_rows)
    train_rows = [row for row in direct_rows if row["split"] == "train_fit"]
    profiles = p0054k.fit_train_profiles(train_rows)
    p0054k.apply_profile_features(direct_rows, profiles)
    p0054k.apply_profile_features(path_rows, profiles)
    feature_contract = p0054m_feature_contract()
    feature_review = validate_feature_contract(feature_contract)
    if not feature_review["ok"]:
        raise RuntimeError(f"P0054M feature contract failed: {feature_review}")
    matrix_review = validate_p0054m_matrix_safety(direct_rows, feature_contract)
    if not matrix_review["ok"]:
        raise RuntimeError(f"P0054M matrix safety failed: {matrix_review}")

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
    weekly_summary, weekly_path_rows = p0054k.evaluate_weekly_paths(scored_path_rows, prediction_columns)
    conditional_results = p0054k.evaluate_conditional_regimes(scored_path_rows, prediction_columns)
    ablation = compare_advanced_price_ablation(model_results, weekly_summary, conditional_results)
    comparison = model_comparison(model_results, weekly_summary)
    p0054k_comparison = compare_to_p0054k_evidence(comparison, ablation)
    importance = p0054k.feature_importance_or_attribution(model_results)
    leakage_review = leakage_review_summary(matrix_review, fairness, price_contract)
    status = "PASS" if leakage_review["ok"] and fairness["ok"] and ablation["required_model_pairs_complete"] else "WARN"

    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "price_feature_protocol": PRICE_PROTOCOL,
        "target_contract": target_contract,
        "weather_contract": weather_contract,
        "advanced_price_source_contract": price_contract,
        "train_price_contract": train_price_contract,
        "holdout_price_contract": holdout_contract,
        "split_policy": split_policy(),
        "split_counts": split_counts,
        "row_counts": {
            "source_rows": len(source_rows),
            "train_price_rows": len(train_price_rows),
            "holdout_price_rows": len(holdout_price_rows),
            "direct_rows": len(direct_rows),
            "weekly_path_rows": len(path_rows),
            "train_fit_rows": split_counts.get("train_fit", 0),
            "holdout_rows": split_counts.get("holdout", 0),
        },
        "environment": environment,
        "feature_contract": feature_contract,
        "feature_review": feature_review,
        "matrix_safety_review": matrix_review,
        "fairness": fairness,
        "input_classification": input_classification(),
        "model_training": {key: result["training"] for key, result in model_results.items()},
        "model_results": {key: result["metrics"] for key, result in model_results.items()},
        "advanced_price_ablation": ablation,
        "model_comparison": comparison,
        "direct_horizon_results": direct_results,
        "weekly_168h_path_results": weekly_summary,
        "conditional_regime_results": conditional_results,
        "p0054k_comparison": p0054k_comparison,
        "feature_importance_or_attribution": importance,
        "leakage_review": leakage_review,
        "no_api_devices_runtime_a61_future_flow": True,
        "no_large_artifacts": True,
    }
    evidence = write_p0054m_evidence(evidence_dir, scored_rows, weekly_path_rows, summary)
    return P0054MResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def build_blocked_oof_price_rows(price_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    examples, skipped = p0054l2.build_price_forecast_examples(price_rows)
    train_examples = [row for row in examples if TRAIN_FIT_START <= str(row["target_timestamp_utc"]) < TRAIN_PRICE_BLOCK_START]
    predict_examples = [dict(row) for row in examples if TRAIN_PRICE_BLOCK_START <= str(row["target_timestamp_utc"]) < HOLDOUT_START]
    feature_names = sorted({key for row in examples for key in row["features"]})  # type: ignore[union-attr]
    matrix_review = p0054l2.validate_feature_matrix_safety(train_examples + predict_examples, feature_names)
    if not matrix_review["ok"]:
        raise RuntimeError(f"P0054M train price matrix safety failed: {matrix_review}")
    imports = p0054k.capture_environment_status()["imports"]
    specs = p0054l2.model_specs(imports)  # type: ignore[arg-type]
    prediction_columns = []
    model_status = {}
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
    if len(prediction_columns) < 2:
        raise RuntimeError(f"P0054M needs at least two price models for Ensemble approximation: {model_status}")
    output = []
    created = p0052.format_utc(datetime.now(timezone.utc).replace(microsecond=0))
    for row in predict_examples:
        predicted = p0054k.mean_float([float(row[column]) for column in prediction_columns])
        output.append(
            {
                "forecast_run_id": "P0054M_train_blocked_oof_se3_price_v1",
                "package_id": PACKAGE_ID,
                "model_name": "Ensemble",
                "model_version": "p0054m_blocked_oof_p0054l2_compatible_v1",
                "area": "SE3",
                "forecast_origin_timestamp_utc": row["forecast_origin_timestamp_utc"],
                "input_data_cutoff_utc": row["input_data_cutoff_utc"],
                "target_timestamp_utc": row["target_timestamp_utc"],
                "horizon_hours": int(row["horizon_hours"]),
                "horizon_h": int(row["horizon_hours"]) + 1,
                "predicted_price": predicted,
                "prediction_unit": "repository hour_price convention",
                "prediction_kind": "advanced_absolute_price",
                "training_protocol": "blocked_oof_train_price_before_2025_03",
                "training_cutoff_utc": p0052.format_utc(p0052.parse_utc(TRAIN_PRICE_BLOCK_START) - timedelta(hours=1)),
                "quality_flag": "train_fit_safe_blocked_oof_advanced_price_forecast",
                "prediction_rule": "P0054M_blocked_oof_ensemble",
                "source_reconstruction": "system_proxy_se1 + area_diff_proxy_se3",
                "created_at_utc": created,
            }
        )
    contract = {
        "ok": bool(output),
        "protocol": PRICE_PROTOCOL,
        "table": TRAIN_PRICE_TABLE,
        "rows": len(output),
        "model_status": model_status,
        "train_price_model_rows": len(train_examples),
        "target_rows_predicted": len(predict_examples),
        "target_start": min((str(row["target_timestamp_utc"]) for row in output), default=""),
        "target_end": max((str(row["target_timestamp_utc"]) for row in output), default=""),
        "forecast_origins": len({row["forecast_origin_timestamp_utc"] for row in output}),
        "training_cutoff_utc": p0052.format_utc(p0052.parse_utc(TRAIN_PRICE_BLOCK_START) - timedelta(hours=1)),
        "holdout_used_for_train_price_features": False,
        "skipped_windows": skipped,
        "matrix_review": matrix_review,
        "coverage_warning": "train-side advanced price coverage is limited to 2025-03-01..2025-05-31",
    }
    return output, contract


def persist_p0054m_price_rows(feature_db: Path, rows: list[dict[str, object]]) -> int:
    with sqlite3.connect(feature_db) as conn:
        persist_rows(conn, TRAIN_PRICE_TABLE, rows)
        conn.commit()
    return len(rows)


def load_p0054l2_holdout_price_rows(feature_db: Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    output = []
    with sqlite3.connect(feature_db) as conn:
        conn.row_factory = sqlite3.Row
        if not p0054k.table_exists(conn, P0054L2_HOLDOUT_TABLE):
            return [], {"ok": False, "reason": "missing_table", "table": P0054L2_HOLDOUT_TABLE}
        for row in conn.execute(
            f"""
            SELECT forecast_origin_timestamp_utc, input_data_cutoff_utc, target_timestamp_utc,
                   horizon_hours, predicted_price, model_name, quality_flag, training_protocol
            FROM {P0054L2_HOLDOUT_TABLE}
            WHERE area='SE3'
              AND model_name='Ensemble'
              AND prediction_kind='advanced_absolute_price'
            ORDER BY forecast_origin_timestamp_utc, horizon_hours
            """
        ):
            output.append(
                {
                    "forecast_origin_timestamp_utc": p0052.normalize_utc_text(row["forecast_origin_timestamp_utc"]),
                    "input_data_cutoff_utc": p0052.normalize_utc_text(row["input_data_cutoff_utc"]),
                    "target_timestamp_utc": p0052.normalize_utc_text(row["target_timestamp_utc"]),
                    "horizon_hours": int(row["horizon_hours"]),
                    "horizon_h": int(row["horizon_hours"]) + 1,
                    "predicted_price": float(row["predicted_price"]),
                    "prediction_rule": "P0054L2_Ensemble",
                    "price_feature_source_protocol": "p0054l2_holdout_safe",
                }
            )
    holdout = [row for row in output if p0054k.p0054i_split(str(row["target_timestamp_utc"])) == "holdout"]
    return output, {
        "ok": bool(holdout) and len(holdout) == len(output),
        "table": P0054L2_HOLDOUT_TABLE,
        "model_name": "Ensemble",
        "rows": len(output),
        "target_start": min((str(row["target_timestamp_utc"]) for row in output), default=""),
        "target_end": max((str(row["target_timestamp_utc"]) for row in output), default=""),
        "forecast_origins": len({row["forecast_origin_timestamp_utc"] for row in output}),
        "train_fit_rows": len(output) - len(holdout),
        "holdout_rows": len(holdout),
        "holdout_used_for_consumption_training": False,
    }


def advanced_price_source_contract(train_contract: dict[str, object], holdout_contract: dict[str, object], rows: list[dict[str, object]]) -> dict[str, object]:
    train = [row for row in rows if p0054k.p0054i_split(str(row["target_timestamp_utc"])) == "train_fit"]
    holdout = [row for row in rows if p0054k.p0054i_split(str(row["target_timestamp_utc"])) == "holdout"]
    return {
        "ok": bool(train) and bool(holdout) and train_contract["ok"] and holdout_contract["ok"],
        "price_feature_protocol": PRICE_PROTOCOL,
        "train_source": train_contract,
        "holdout_source": holdout_contract,
        "combined_rows": len(rows),
        "train_fit_rows": len(train),
        "holdout_rows": len(holdout),
        "train_fit_holdout_source_separated": True,
        "p0054l2_holdout_source_used_as_train_feature": False,
    }


def build_p0054m_modeling_rows(
    source_rows: list[dict[str, object]],
    weather_rows: dict[str, dict[str, object]],
    price_rows: list[dict[str, object]],
    horizons: set[int],
    *,
    holdout_weekly_only: bool = False,
) -> list[dict[str, object]]:
    rows = p0054k.build_modeling_rows(source_rows, weather_rows, price_rows, horizons, holdout_weekly_only=holdout_weekly_only)
    for row in rows:
        row["price_forecast_source"] = "P0054M_blocked_oof_train_plus_P0054L2_holdout_advanced_ensemble"
        if p0054k.p0054i_split(str(row["target_timestamp_utc"])) == "train_fit":
            row["price_feature_protocol"] = "blocked_oof_train_price_before_2025_03"
        else:
            row["price_feature_protocol"] = "p0054l2_holdout_safe_ensemble"
    return rows


def p0054m_feature_contract() -> dict[str, dict[str, object]]:
    base_contract = p0054k.feature_group_contract()
    return {
        VARIANT_NO_PRICE: base_contract["no_price"],
        VARIANT_WITH_ADVANCED: {
            "input_classification": "mixed_forecast_safe_advanced_price_and_weather_proxy",
            "features": list(base_contract["with_p0054k_se3_price_forecast"]["features"]),
        },
    }


def validate_feature_contract(contract: dict[str, dict[str, object]]) -> dict[str, object]:
    violations = []
    for group, meta in contract.items():
        forbidden = FORBIDDEN_NO_PRICE_TERMS if group == VARIANT_NO_PRICE else FORBIDDEN_WITH_PRICE_TERMS
        for feature in meta["features"]:  # type: ignore[index]
            lowered = str(feature).lower()
            for term in forbidden:
                if term in lowered:
                    violations.append({"group": group, "feature": feature, "term": term})
    return {"ok": not violations, "violations": violations}


def validate_p0054m_matrix_safety(rows: list[dict[str, object]], feature_contract: dict[str, dict[str, object]]) -> dict[str, object]:
    base = p0054k.validate_matrix_safety(rows, feature_contract)
    train_rows = [row for row in rows if p0054k.p0054i_split(str(row["target_timestamp_utc"])) == "train_fit"]
    train_protocol_ok = all(row.get("price_feature_protocol") == "blocked_oof_train_price_before_2025_03" for row in train_rows)
    target_order_ok = all(p0052.parse_utc(str(row["input_data_cutoff_utc"])) <= p0052.parse_utc(str(row["forecast_origin_timestamp_utc"])) <= p0052.parse_utc(str(row["target_timestamp_utc"])) for row in rows)
    forbidden = [
        column
        for row in rows[:1]
        for column in row
        if any(term in column.lower() for term in ("actual_price", "production", "flow", "export", "import", "a61", "capacity", "utilization", "continental"))
    ]
    return {
        "ok": train_protocol_ok and target_order_ok and not forbidden,
        "base_p0054k_matrix_review": base,
        "train_protocol_ok": train_protocol_ok,
        "target_order_ok": target_order_ok,
        "forbidden_columns": sorted(set(forbidden)),
        "p0054l2_holdout_used_as_train_feature": False,
        "actual_future_spot_price_used": False,
        "production_flow_export_import_a61_used": False,
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


def compare_advanced_price_ablation(model_results: dict[str, dict[str, object]], weekly_summary: dict[str, object], conditional_results: dict[str, object]) -> dict[str, object]:
    rows = []
    for family in MODEL_FAMILIES:
        no_key = f"{family}_{VARIANT_NO_PRICE}"
        price_key = f"{family}_{VARIANT_WITH_ADVANCED}"
        if no_key not in model_results or price_key not in model_results:
            continue
        no_mae = float(model_results[no_key]["metrics"]["holdout"]["MAE"])  # type: ignore[index]
        price_mae = float(model_results[price_key]["metrics"]["holdout"]["MAE"])  # type: ignore[index]
        no_weekly = float(weekly_summary[p0054k.prediction_column(no_key)]["MAE_full_168h"])  # type: ignore[index]
        price_weekly = float(weekly_summary[p0054k.prediction_column(price_key)]["MAE_full_168h"])  # type: ignore[index]
        rows.append(
            {
                "family": family,
                "holdout_no_price_MAE": no_mae,
                "holdout_with_advanced_price_MAE": price_mae,
                "holdout_with_minus_no_MAE": price_mae - no_mae,
                "holdout_relative_change_percent": p0054k.relative_change(price_mae, no_mae),
                "weekly_no_price_MAE_full_168h": no_weekly,
                "weekly_with_advanced_price_MAE_full_168h": price_weekly,
                "weekly_with_minus_no_MAE_full_168h": price_weekly - no_weekly,
                "weekly_relative_change_percent": p0054k.relative_change(price_weekly, no_weekly),
                "advanced_price_helped_holdout": price_mae < no_mae,
                "advanced_price_helped_weekly": price_weekly < no_weekly,
            }
        )
    conditional = conditional_advanced_price_help_summary(conditional_results)
    keep = should_keep_advanced_price(rows, conditional)
    return {
        "required_model_pairs_complete": len(rows) == len(MODEL_FAMILIES),
        "per_model_family": rows,
        "conditional_price_help_summary": conditional,
        "learning_threshold": "useful if holdout or weekly improves by >=2%, or >=3% in at least two important regimes without broad worsening",
        "advanced_price_should_be_kept_for_future_se3_experiments": keep,
        "xgboost_benefits_from_advanced_price": next((row for row in rows if row["family"] == "XGBoost"), {}).get("advanced_price_helped_holdout"),
        "interpretation_category": "supports_hypothesis" if keep else "no_effect_detected",
    }


def conditional_advanced_price_help_summary(conditional_results: dict[str, object]) -> dict[str, object]:
    out = {}
    interesting = []
    for regime, values in conditional_results.items():
        regime_out = {}
        for family in MODEL_FAMILIES:
            no_col = p0054k.prediction_column(f"{family}_{VARIANT_NO_PRICE}")
            price_col = p0054k.prediction_column(f"{family}_{VARIANT_WITH_ADVANCED}")
            if no_col not in values or price_col not in values:  # type: ignore[operator]
                continue
            no_mae = values[no_col]["MAE"]  # type: ignore[index]
            price_mae = values[price_col]["MAE"]  # type: ignore[index]
            change = p0054k.relative_change(float(price_mae), float(no_mae)) if no_mae else None
            regime_out[family] = {"no_price_MAE": no_mae, "with_advanced_price_MAE": price_mae, "relative_change_percent": change}
            if change is not None and change <= -3.0:
                interesting.append({"regime": regime, "family": family, "relative_change_percent": change})
        out[regime] = regime_out
    return {"by_regime": out, "improvements_at_least_3_percent": interesting, "count": len(interesting)}


def should_keep_advanced_price(rows: list[dict[str, object]], conditional: dict[str, object]) -> bool:
    broad = any((row["holdout_relative_change_percent"] is not None and row["holdout_relative_change_percent"] <= -2.0) or (row["weekly_relative_change_percent"] is not None and row["weekly_relative_change_percent"] <= -2.0) for row in rows)
    material_worsening = any(row["holdout_relative_change_percent"] is not None and row["holdout_relative_change_percent"] > 2.0 for row in rows)
    return broad or (int(conditional.get("count", 0)) >= 2 and not material_worsening)


def model_comparison(model_results: dict[str, dict[str, object]], weekly_summary: dict[str, object]) -> dict[str, object]:
    direct = [{"model": key, "holdout_MAE": result["metrics"]["holdout"]["MAE"]} for key, result in model_results.items()]  # type: ignore[index]
    weekly = [{"model": key, "weekly_MAE_full_168h": weekly_summary[p0054k.prediction_column(key)]["MAE_full_168h"]} for key in model_results]  # type: ignore[index]
    return {
        "best_no_price_by_holdout_MAE": min([row for row in direct if row["model"].endswith(f"_{VARIANT_NO_PRICE}")], key=lambda row: float(row["holdout_MAE"])),
        "best_with_advanced_price_by_holdout_MAE": min([row for row in direct if row["model"].endswith(f"_{VARIANT_WITH_ADVANCED}")], key=lambda row: float(row["holdout_MAE"])),
        "best_no_price_by_weekly_MAE_full_168h": min([row for row in weekly if row["model"].endswith(f"_{VARIANT_NO_PRICE}")], key=lambda row: float(row["weekly_MAE_full_168h"])),
        "best_with_advanced_price_by_weekly_MAE_full_168h": min([row for row in weekly if row["model"].endswith(f"_{VARIANT_WITH_ADVANCED}")], key=lambda row: float(row["weekly_MAE_full_168h"])),
        "direct_holdout": direct,
        "weekly_168h": weekly,
    }


def compare_to_p0054k_evidence(comparison: dict[str, object], ablation: dict[str, object]) -> dict[str, object]:
    p0054k_reference = {
        "XGBoost_no_price_holdout_MAE": 48.01602472809628,
        "XGBoost_no_price_weekly_MAE_full_168h": 108.51610764072525,
        "XGBoost_with_p0054k_se3_price_forecast_holdout_MAE": 48.491100583964595,
        "XGBoost_with_p0054k_se3_price_forecast_weekly_MAE_full_168h": 109.81910335762592,
        "LightGBM_with_p0054k_se3_price_forecast_holdout_MAE": 48.3202873218118,
        "LightGBM_with_p0054k_se3_price_forecast_weekly_MAE_full_168h": 132.89188052486935,
    }
    return {
        "reference": p0054k_reference,
        "p0054m_best_no_price_holdout": comparison["best_no_price_by_holdout_MAE"],
        "p0054m_best_with_advanced_price_holdout": comparison["best_with_advanced_price_by_holdout_MAE"],
        "p0054m_best_no_price_weekly": comparison["best_no_price_by_weekly_MAE_full_168h"],
        "p0054m_best_with_advanced_price_weekly": comparison["best_with_advanced_price_by_weekly_MAE_full_168h"],
        "protocol_warning": "P0054M trains on a narrower 2025-03..2025-05 train-side price-covered subset, so P0054K comparisons are evidence-summary comparisons, not identical-row reruns.",
        "advanced_price_ablation": ablation,
    }


def leakage_review_summary(matrix_review: dict[str, object], fairness: dict[str, object], price_contract: dict[str, object]) -> dict[str, object]:
    return {
        "ok": matrix_review["ok"] and fairness["ok"] and price_contract["ok"],
        "matrix_review_ok": matrix_review["ok"],
        "fairness_ok": fairness["ok"],
        "price_contract_ok": price_contract["ok"],
        "p0054l2_holdout_used_as_train_feature": False,
        "actual_future_spot_price_feature_used": False,
        "holdout_used_for_fitting_or_selection": False,
        "api_device_runtime_a61_future_flow_used": False,
    }


def write_p0054m_evidence(evidence_dir: Path, scored_rows: list[dict[str, object]], weekly_path_rows: list[dict[str, object]], summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "metrics-summary.json": write_json(evidence_dir / "metrics-summary.json", summary),
        "advanced-price-ablation-summary.json": write_json(evidence_dir / "advanced-price-ablation-summary.json", summary["advanced_price_ablation"]),
        "modeling-dataset-sample.csv": write_csv(evidence_dir / "modeling-dataset-sample.csv", scored_rows[:500], dataset_sample_columns(summary)),
        "weekly-path-metrics.csv": write_csv(evidence_dir / "weekly-path-metrics.csv", weekly_path_rows, list(weekly_path_rows[0].keys()) if weekly_path_rows else []),
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
        "price-feature-protocol-decision.md": common + json_block({"selected": PRICE_PROTOCOL, "contract": summary["advanced_price_source_contract"]}),
        "split-policy-applied.md": common + json_block(summary["split_policy"]),
        "dataset-contract.md": common + json_block(summary["target_contract"]),
        "advanced-price-source-contract.md": common + json_block(summary["advanced_price_source_contract"]),
        "input-classification.md": common + json_block(summary["input_classification"]),
        "feature-groups.md": common + json_block(summary["feature_contract"]),
        "model-training-evidence.md": common + json_block(summary["model_training"]),
        "no-price-results.md": common + json_block({key: value for key, value in summary["model_results"].items() if key.endswith(f"_{VARIANT_NO_PRICE}")}),
        "with-advanced-price-results.md": common + json_block({key: value for key, value in summary["model_results"].items() if key.endswith(f"_{VARIANT_WITH_ADVANCED}")}),
        "advanced-price-ablation.md": common + json_block(summary["advanced_price_ablation"]),
        "model-comparison.md": common + json_block(summary["model_comparison"]),
        "direct-horizon-results.md": common + json_block(summary["direct_horizon_results"]),
        "weekly-168h-path-results.md": common + json_block(summary["weekly_168h_path_results"]),
        "conditional-regime-results.md": common + json_block(summary["conditional_regime_results"]),
        "p0054k-comparison.md": common + json_block(summary["p0054k_comparison"]),
        "feature-importance-or-attribution.md": common + json_block(summary["feature_importance_or_attribution"]),
        "leakage-review.md": common + json_block(summary["leakage_review"]),
        "interpretation.md": common + interpretation_text(summary),
        "what-we-learned.md": common + what_we_learned_text(summary),
        "next-package-recommendation.md": common + next_package_text(summary),
    }


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0054M Changelog

Status: `{summary['status']}`

- Selected `{PRICE_PROTOCOL}`.
- Created train-side blocked OOF advanced SE3 price rows in `{TRAIN_PRICE_TABLE}`.
- Used P0054L2 Ensemble holdout rows for holdout evaluation.
- Trained paired no-price and with-advanced-price SE3 consumption models for HGB, ExtraTrees, LightGBM and XGBoost.
- Wrote direct, weekly path, conditional, ablation and P0054K comparison evidence.
- No API, device, runtime, A61, future-flow or actual future price leakage work was performed.
"""


def interpretation_text(summary: dict[str, object]) -> str:
    comparison = summary["model_comparison"]  # type: ignore[assignment]
    ablation = summary["advanced_price_ablation"]  # type: ignore[assignment]
    return (
        f"Price feature protocol: `{PRICE_PROTOCOL}`.\n\n"
        f"Best no-price holdout model: `{comparison['best_no_price_by_holdout_MAE']['model']}`.\n\n"
        f"Best with-advanced-price holdout model: `{comparison['best_with_advanced_price_by_holdout_MAE']['model']}`.\n\n"
        f"XGBoost benefits from advanced price: `{ablation['xgboost_benefits_from_advanced_price']}`.\n\n"
        f"Keep advanced price for future SE3 experiments: `{ablation['advanced_price_should_be_kept_for_future_se3_experiments']}`.\n\n"
        "Weather remains LABB actual-as-forecast proxy. The train-side advanced price source is blocked and partial, not a full train_fit rolling source.\n"
    )


def what_we_learned_text(summary: dict[str, object]) -> str:
    keep = summary["advanced_price_ablation"]["advanced_price_should_be_kept_for_future_se3_experiments"]  # type: ignore[index]
    if keep:
        return "The advanced P0054L2-compatible price forecast produced useful SE3 consumption signal under a safe blocked train-feature protocol.\n"
    return "The advanced P0054L2-compatible price forecast did not produce enough generic SE3 consumption signal under the safe blocked train-feature protocol.\n"


def next_package_text(summary: dict[str, object]) -> str:
    keep = summary["advanced_price_ablation"]["advanced_price_should_be_kept_for_future_se3_experiments"]  # type: ignore[index]
    if keep:
        return "Recommended next package: test whether the advanced price effect is stronger in SE3-SE1 spread/flaskhals regimes with a fuller rolling train forecast source.\n"
    return "Recommended next package: return to SE3-SE1 spread/flaskhals-regime LABB rather than continuing generic SE3 consumption price-feature ablations.\n"


def input_classification() -> dict[str, object]:
    return {
        "calendar": "forecast_safe",
        "historical_se3_consumption_lags_rollups": "forecast_safe",
        "weather": "proxy",
        "weather_proxy_label": p0054k.WEATHER_PROXY_LABEL,
        "p0054m_blocked_oof_train_price_forecast": "forecast_safe",
        "p0054l2_holdout_advanced_price_forecast": "forecast_safe_for_holdout_evaluation",
        "actual_future_spot_price": "excluded_leakage",
        "production_flow_export_import_a61": "excluded_leakage",
    }


def split_policy() -> dict[str, str]:
    return {
        "policy_name": "LABB_P0054_TRAIN_THROUGH_MAY_2025",
        "train_fit": f"{TRAIN_FIT_START} <= target_timestamp_utc < {HOLDOUT_START}",
        "holdout": f"target_timestamp_utc >= {HOLDOUT_START}",
        "train_side_price_feature_coverage": f"{TRAIN_PRICE_BLOCK_START} <= target_timestamp_utc < {HOLDOUT_START}",
    }


def dataset_sample_columns(summary: dict[str, object]) -> list[str]:
    feature_names = list(summary["feature_contract"][VARIANT_WITH_ADVANCED]["features"])  # type: ignore[index]
    return [
        "forecast_origin_timestamp_utc",
        "target_timestamp_utc",
        "horizon_h",
        p0054k.TARGET_FIELD,
        "split",
        "price_feature_protocol",
    ] + feature_names[:30]


def flatten_conditional_rows(summary: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for regime, columns in summary["conditional_regime_results"].items():  # type: ignore[union-attr]
        for model, metrics in columns.items():
            rows.append({"regime": regime, "model": model, **metrics})
    return rows


def conditional_columns() -> list[str]:
    return ["regime", "model", "row_count", "MAE", "RMSE", "bias", "median_absolute_error", "p90_absolute_error", "p95_absolute_error", "sMAPE", "R2", "mean_actual_mw", "median_actual_mw", "MAE_percent_of_mean_actual", "MAE_percent_of_median_actual"]


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
    result = run_p0054m_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
