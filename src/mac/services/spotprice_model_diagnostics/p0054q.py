"""P0054Q LABB SE3 DayAhead/full_36h rerun with ENTSO-E target."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
import csv
import json
import math
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054l2, p0054m, p0054n
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0054Q"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054Q")
TARGET_TABLE = "entsoe_consumption_area_hourly_v1"
TARGET_AREA = "SE3"
TARGET_COLUMN = "consumption_mw"
SOURCE_MEASURE = "actual_total_load"
AREA_SCOPE = "bidding_zone_internal_consumption_or_load"
VARIANT_NO_PRICE = p0054n.VARIANT_NO_PRICE
VARIANT_WITH_ADVANCED = p0054n.VARIANT_WITH_ADVANCED
MODEL_FAMILIES = p0054n.MODEL_FAMILIES


@dataclass(frozen=True)
class P0054QResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054q_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054QResult:
    started = time.monotonic()
    feature_db = Path(feature_db).expanduser()
    evidence_dir = Path(evidence_dir)

    source_rows = load_entsoe_se3_target_rows(feature_db)
    target_contract = validate_entsoe_target_contract(source_rows)
    if not target_contract["ok"]:
        raise RuntimeError(f"P0054Q target contract failed: {target_contract}")
    weather_rows, weather_contract = p0054k.load_weather_proxy_rows(weather_db)
    price_source_rows = p0054l2.load_se3_price_rows(feature_db)
    exact_price_rows, exact_price_contract = p0054n.build_p0054n_exact_origin_price_rows(price_source_rows)
    if not exact_price_contract["ok"]:
        raise RuntimeError(f"P0054Q exact-origin price contract failed: {exact_price_contract}")

    direct_rows = p0054m.build_p0054m_modeling_rows(source_rows, weather_rows, exact_price_rows, set(p0054n.HORIZONS_36H))
    path_rows = [dict(row) for row in direct_rows]
    split_counts = p0054k.assign_p0054i_splits(direct_rows)
    p0054k.assign_p0054i_splits(path_rows)
    profiles = p0054k.fit_train_profiles([row for row in direct_rows if row["split"] == "train_fit"])
    p0054k.apply_profile_features(direct_rows, profiles)
    p0054k.apply_profile_features(path_rows, profiles)

    feature_contract = p0054q_feature_contract()
    feature_review = p0054m.validate_feature_contract(feature_contract)
    matrix_review = p0054n.validate_p0054n_matrix_safety(direct_rows, feature_contract)
    if not feature_review["ok"] or not matrix_review["ok"]:
        raise RuntimeError(f"P0054Q matrix safety failed: feature={feature_review} matrix={matrix_review}")

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
    fairness = p0054n.validate_paired_row_sets(scored_rows)
    direct_results = p0054k.evaluate_direct_horizons(scored_rows, prediction_columns)
    full36_summary, full36_rows = p0054n.evaluate_full_36h_paths(scored_path_rows, prediction_columns)
    dayahead_summary, dayahead_rows = p0054n.evaluate_dayahead_delivery_days(scored_path_rows, prediction_columns)
    full36_selected = selected_full36_rows(scored_path_rows)
    dayahead_selected = selected_dayahead_rows(scored_path_rows)
    add_percent_metrics(full36_summary, full36_selected, prediction_columns, "full36")
    add_percent_metrics(dayahead_summary, dayahead_selected, prediction_columns, "dayahead")
    daily_energy_summary = daily_energy_error_summary(dayahead_selected, prediction_columns)
    conditional_results = p0054k.evaluate_conditional_regimes(scored_path_rows, prediction_columns)
    ablation = p0054n.compare_advanced_price_ablation_36h(model_results, full36_summary, dayahead_summary)
    comparison = model_comparison(model_results, full36_summary, dayahead_summary, daily_energy_summary)
    target_sanity = target_sanity_metrics(source_rows, dayahead_selected)
    old_target_comparison = old_target_reference_comparison()
    leakage_review = validate_p0054q_leakage(matrix_review, fairness, exact_price_contract, target_contract, feature_contract, scored_path_rows)
    status = "PASS" if leakage_review["ok"] and fairness["ok"] and bool(full36_selected) and bool(dayahead_selected) else "WARN"

    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "target_contract": target_contract,
        "p0054p2_source_review": p0054p2_source_review(),
        "split_policy": p0054n.split_policy(),
        "split_counts": split_counts,
        "dataset_contract": dataset_contract(target_contract, weather_contract, exact_price_contract),
        "feature_contract": feature_contract,
        "input_classification": input_classification(),
        "weather_contract": weather_contract,
        "exact_origin_price_contract": exact_price_contract,
        "feature_review": feature_review,
        "matrix_safety_review": matrix_review,
        "fairness": fairness,
        "environment": environment,
        "model_training": {key: result["training"] for key, result in model_results.items()},
        "model_results": {key: result["metrics"] for key, result in model_results.items()},
        "direct_horizon_results": direct_results,
        "full_36h_results": full36_summary,
        "dayahead_delivery_day_results": dayahead_summary,
        "daily_energy_error_results": daily_energy_summary,
        "percent_error_results": percent_error_summary(full36_summary, dayahead_summary),
        "advanced_price_ablation": ablation,
        "model_comparison": comparison,
        "conditional_regime_results": conditional_results,
        "old_target_comparison": old_target_comparison,
        "target_sanity_metrics": target_sanity,
        "leakage_review": leakage_review,
        "interpretation": interpretation_summary(comparison, target_sanity, old_target_comparison),
        "what_we_learned": what_we_learned(comparison),
        "next_package_recommendation": "P0054R LABB SE3 DayAhead weather realism on ENTSO-E target.",
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
        "no_live_api": True,
        "no_devices_runtime_a61_nordpool_workplace": True,
        "no_old_target_as_target": True,
        "no_future_actual_load_or_price_leakage": True,
    }
    evidence = write_p0054q_evidence(evidence_dir, scored_rows, full36_rows, dayahead_rows, summary)
    return P0054QResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def load_entsoe_se3_target_rows(feature_db: Path | str) -> list[dict[str, object]]:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        if not p0054k.table_exists(conn, TARGET_TABLE):
            raise RuntimeError(f"source table missing: {TARGET_TABLE}")
        rows = [
            normalize_entsoe_target_row(dict(row))
            for row in conn.execute(
                f"""
                SELECT timestamp_utc, area, consumption_mw, source_system, source_measure,
                       source_area_code, resolution, unit, timezone_handling, package_id, quality_flag
                FROM {TARGET_TABLE}
                WHERE package_id='P0054P2' AND area=?
                ORDER BY timestamp_utc
                """,
                (TARGET_AREA,),
            )
        ]
    return rows


def normalize_entsoe_target_row(row: dict[str, object]) -> dict[str, object]:
    ts = p0052.normalize_utc_text(row["timestamp_utc"])
    dt = p0052.parse_utc(ts)
    model = dt + timedelta(hours=1)
    return {
        "timestamp_utc": ts,
        "model_cet_timestamp": p0052.format_utc(model),
        "model_cet_date": model.date().isoformat(),
        "model_cet_hour": model.hour,
        "model_cet_weekday": model.weekday(),
        "model_cet_day_of_year": model.timetuple().tm_yday,
        "consumption_se3": float(row["consumption_mw"]),
        "target_source_table": TARGET_TABLE,
        "target_source_column": TARGET_COLUMN,
        "target_source_measure": str(row["source_measure"]),
        "target_source_area_scope": AREA_SCOPE,
        "target_source_package_id": str(row["package_id"]),
        "target_source_area": str(row["area"]),
        "target_source_system": str(row["source_system"]),
    }


def validate_entsoe_target_contract(rows: list[dict[str, object]]) -> dict[str, object]:
    timestamps = [str(row["timestamp_utc"]) for row in rows]
    values = [float(row["consumption_se3"]) for row in rows if p0054k.is_finite(row.get("consumption_se3"))]
    train_fit = [row for row in rows if p0054k.p0054i_split(str(row["timestamp_utc"])) == "train_fit"]
    holdout = [row for row in rows if p0054k.p0054i_split(str(row["timestamp_utc"])) == "holdout"]
    source_ok = all(
        row.get("target_source_table") == TARGET_TABLE
        and row.get("target_source_column") == TARGET_COLUMN
        and row.get("target_source_measure") == SOURCE_MEASURE
        and row.get("target_source_area") == TARGET_AREA
        and row.get("target_source_package_id") == "P0054P2"
        for row in rows
    )
    return {
        "ok": bool(rows) and source_ok and len(timestamps) == len(set(timestamps)) and len(values) == len(rows) and bool(train_fit) and bool(holdout),
        "source_table": TARGET_TABLE,
        "area": TARGET_AREA,
        "target_column": TARGET_COLUMN,
        "target_field": p0054k.TARGET_FIELD,
        "source_type": SOURCE_MEASURE,
        "area_scope": AREA_SCOPE,
        "unit": "MW hourly mean",
        "rows": len(rows),
        "train_fit_source_rows": len(train_fit),
        "holdout_source_rows": len(holdout),
        "start": min(timestamps) if timestamps else "",
        "end": max(timestamps) if timestamps else "",
        "duplicates": len(timestamps) - len(set(timestamps)),
        "nonfinite_values": len(rows) - len(values),
        "mean_mw": p0054k.mean_float(values),
        "median_mw": percentile(values, 0.5) if values else None,
        "old_physical_balance_target_used": False,
        "usable_for_consumption_target": True,
    }


def p0054q_feature_contract() -> dict[str, dict[str, object]]:
    return p0054n.p0054n_feature_contract()


def selected_full36_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_origin = p0054k.group_by([row for row in rows if row["split"] == "holdout"], "forecast_origin_timestamp_utc")
    complete = [origin for origin, origin_rows in sorted(by_origin.items()) if {int(row["horizon_h"]) for row in origin_rows} >= set(p0054n.HORIZONS_36H)]
    return [row for origin in complete for row in by_origin[origin] if int(row["horizon_h"]) in p0054n.HORIZONS_36H]


def selected_dayahead_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_origin_target = {(str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"])): row for row in rows if row["split"] == "holdout"}
    target_dates = sorted({p0052.parse_utc(str(row["target_timestamp_utc"])).astimezone(p0054n.STOCKHOLM).date() for row in rows if row["split"] == "holdout"})
    selected: list[dict[str, object]] = []
    for delivery_day in target_dates:
        origin = p0054n.dayahead_origin_utc_for_delivery_day(delivery_day)
        targets = p0054n.delivery_day_target_utc_hours(delivery_day)
        day_rows = [by_origin_target.get((origin, target)) for target in targets]
        if all(row is not None for row in day_rows):
            selected.extend(row for row in day_rows if row is not None)
    return selected


def add_percent_metrics(summary: dict[str, object], rows: list[dict[str, object]], prediction_columns: tuple[str, ...], prefix: str) -> None:
    actuals = [float(row[p0054k.TARGET_FIELD]) for row in rows]
    mean_actual = p0054k.mean_float(actuals) if actuals else 0.0
    median_actual = percentile(actuals, 0.5) if actuals else 0.0
    for column in prediction_columns:
        available = [row for row in rows if row.get(column) is not None]
        metric = p0054k.regression_metric_from_predictions(available, [float(row[column]) for row in available])
        if column not in summary:
            summary[column] = {}
        target = summary[column]  # type: ignore[index]
        mae_key = "MAE_full_36h" if prefix == "full36" else "hourly_MAE_delivery_day"
        rmse_key = "RMSE_full_36h" if prefix == "full36" else "hourly_RMSE_delivery_day"
        bias_key = "bias_full_36h" if prefix == "full36" else "bias_delivery_day"
        target[mae_key] = metric["MAE"]
        target[rmse_key] = metric["RMSE"]
        target[bias_key] = metric["bias"]
        target["p90_absolute_error"] = metric["p90_absolute_error"]
        target["p95_absolute_error"] = metric["p95_absolute_error"]
        target["MAE_percent_of_mean_actual"] = percent(metric["MAE"], mean_actual)
        target["MAE_percent_of_median_actual"] = percent(metric["MAE"], median_actual)
        target["mean_actual_mw"] = mean_actual
        target["median_actual_mw"] = median_actual


def daily_energy_error_summary(rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> dict[str, object]:
    by_origin = p0054k.group_by(rows, "forecast_origin_timestamp_utc")
    out: dict[str, object] = {}
    for column in prediction_columns:
        signed_errors = []
        percent_errors = []
        for group in by_origin.values():
            available = [row for row in group if row.get(column) is not None]
            actual = sum(float(row[p0054k.TARGET_FIELD]) for row in available)
            predicted = sum(float(row[column]) for row in available)
            signed = predicted - actual
            signed_errors.append(signed)
            if actual:
                percent_errors.append(abs(signed) / actual * 100.0)
        out[column] = {
            "absolute_daily_energy_error_MWh": p0054k.mean_float([abs(value) for value in signed_errors]) if signed_errors else None,
            "signed_daily_energy_error_MWh": p0054k.mean_float(signed_errors) if signed_errors else None,
            "daily_energy_error_percent_of_actual": p0054k.mean_float(percent_errors) if percent_errors else None,
            "day_count": len(signed_errors),
        }
    return out


def target_sanity_metrics(source_rows: list[dict[str, object]], dayahead_rows: list[dict[str, object]]) -> dict[str, object]:
    holdout_values = [float(row["consumption_se3"]) for row in source_rows if p0054k.p0054i_split(str(row["timestamp_utc"])) == "holdout"]
    day_values = [float(row[p0054k.TARGET_FIELD]) for row in dayahead_rows]
    day_energy = [sum(float(row[p0054k.TARGET_FIELD]) for row in group) / 1000.0 for group in p0054k.group_by(dayahead_rows, "forecast_origin_timestamp_utc").values()]
    return {
        "se3_holdout_mean_actual_mw": p0054k.mean_float(holdout_values),
        "se3_holdout_median_actual_mw": percentile(holdout_values, 0.5) if holdout_values else None,
        "se3_dayahead_delivery_day_mean_actual_mw": p0054k.mean_float(day_values),
        "se3_daily_energy_mean_gwh_day": p0054k.mean_float(day_energy) if day_energy else None,
        "p0054p2_summer_half_year_mean_mw": 8030.544,
        "p0054p2_winter_half_year_mean_mw": 10967.24,
        "order_of_magnitude_ok": bool(holdout_values) and 6000.0 <= p0054k.mean_float(holdout_values) <= 13000.0,
    }


def validate_p0054q_leakage(matrix_review: dict[str, object], fairness: dict[str, object], price_contract: dict[str, object], target_contract: dict[str, object], feature_contract: dict[str, dict[str, object]], rows: list[dict[str, object]]) -> dict[str, object]:
    forbidden_columns = sorted({column for row in rows[:1] for column in row if any(term in column.lower() for term in ("physical_balance", "consumption_se1_se4", "actual_price", "future_actual_load", "flow", "export", "import", "a61", "capacity", "utilization"))})
    feature_terms = sorted({feature for group in feature_contract.values() for feature in group["features"] if any(term in str(feature).lower() for term in ("physical_balance", "actual_price", "flow", "export", "import", "a61", "capacity", "utilization"))})  # type: ignore[index]
    return {
        "ok": matrix_review["ok"] and fairness["ok"] and price_contract["ok"] and target_contract["ok"] and not forbidden_columns and not feature_terms,
        "matrix_review_ok": matrix_review["ok"],
        "fairness_ok": fairness["ok"],
        "price_contract_ok": price_contract["ok"],
        "target_contract_ok": target_contract["ok"],
        "target_source_table": target_contract["source_table"],
        "old_physical_balance_target_used": False,
        "holdout_used_for_model_fitting_or_selection": False,
        "actual_future_load_feature_used": False,
        "actual_future_spot_price_feature_used": False,
        "flow_export_import_a61_used": False,
        "forbidden_columns": forbidden_columns,
        "forbidden_features": feature_terms,
    }


def model_comparison(model_results: dict[str, dict[str, object]], full36_summary: dict[str, object], dayahead_summary: dict[str, object], daily_energy_summary: dict[str, object]) -> dict[str, object]:
    full36 = [{"model": key, "MAE_full_36h": full36_summary[p0054k.prediction_column(key)]["MAE_full_36h"], "MAE_percent_of_mean_actual": full36_summary[p0054k.prediction_column(key)]["MAE_percent_of_mean_actual"]} for key in model_results]  # type: ignore[index]
    dayahead_hourly = [{"model": key, "hourly_MAE_delivery_day": dayahead_summary[p0054k.prediction_column(key)]["hourly_MAE_delivery_day"], "MAE_percent_of_mean_actual": dayahead_summary[p0054k.prediction_column(key)]["MAE_percent_of_mean_actual"]} for key in model_results]  # type: ignore[index]
    dayahead_energy = [{"model": key, **daily_energy_summary[p0054k.prediction_column(key)]} for key in model_results]  # type: ignore[index]
    return {
        "best_no_price_by_full36_MAE": min([row for row in full36 if row["model"].endswith(f"_{VARIANT_NO_PRICE}")], key=lambda row: float(row["MAE_full_36h"])),
        "best_with_advanced_price_by_full36_MAE": min([row for row in full36 if row["model"].endswith(f"_{VARIANT_WITH_ADVANCED}")], key=lambda row: float(row["MAE_full_36h"])),
        "best_by_dayahead_hourly_MAE": min(dayahead_hourly, key=lambda row: float(row["hourly_MAE_delivery_day"])),
        "best_by_dayahead_daily_energy_error": min(dayahead_energy, key=lambda row: float(row["absolute_daily_energy_error_MWh"])),
        "full36": full36,
        "dayahead_hourly": dayahead_hourly,
        "dayahead_daily_energy": dayahead_energy,
        "workplace_reference_percent_error": "roughly 3-4 percent; P0054Q remains LABB because weather is actual_as_forecast_proxy",
    }


def percent(value: object, denom: float) -> float | None:
    if value is None or not denom:
        return None
    return float(value) / denom * 100.0


def percent_error_summary(full36_summary: dict[str, object], dayahead_summary: dict[str, object]) -> dict[str, object]:
    return {
        "full36": {key: value for key, value in full36_summary.items() if str(key).startswith("pred_")},
        "dayahead": {key: value for key, value in dayahead_summary.items() if str(key).startswith("pred_")},
    }


def old_target_reference_comparison() -> dict[str, object]:
    return {
        "p0054n_old_target_best_dayahead_MAE_MW": 149.03724768647368,
        "p0054n_old_target_best_full36_MAE_MW": 150.42261836159255,
        "p0054o_old_target_baseline_percent_of_old_proxy_mean_actual": 6.394256809659218,
        "old_target_label": "proxy-target methodology experiment, not validated total-SE3-load performance",
        "p0054p2_entsoe_over_old_ratio": 2.415764,
        "p0054p2_entsoe_old_correlation": 0.23226,
    }


def p0054p2_source_review() -> dict[str, object]:
    return {
        "source_table": TARGET_TABLE,
        "source_package": "P0054P2",
        "source_contract": "ENTSO-E Actual Total Load A65/A16",
        "p0054p2_status": "PASS",
        "se3_summer_half_year_mean_mw": 8030.544,
        "se3_winter_half_year_mean_mw": 10967.24,
        "old_physical_balance_equivalent": False,
    }


def dataset_contract(target_contract: dict[str, object], weather_contract: dict[str, object], price_contract: dict[str, object]) -> dict[str, object]:
    return {
        "target": target_contract,
        "weather": weather_contract,
        "advanced_price": price_contract,
        "weather_proxy_label": p0054k.WEATHER_PROXY_LABEL,
        "dataset_kind": "offline_labb_corrected_entsoe_target_experiment_not_deployable",
    }


def input_classification() -> dict[str, object]:
    return {
        "calendar": "forecast_safe",
        "historical_entsoe_se3_load_lags_rollups": "forecast_safe",
        "entsoe_se3_target": "historical_observed_only",
        "weather": "proxy",
        "weather_proxy_label": p0054k.WEATHER_PROXY_LABEL,
        "advanced_price_forecast": "forecast_safe_under_p0054n_exact_origin_extension_of_p0054m_protocol",
        "future_actual_load": "excluded_leakage",
        "actual_future_spot_price": "excluded_leakage",
        "production_flow_export_import_a61": "excluded_leakage",
    }


def interpretation_summary(comparison: dict[str, object], target_sanity: dict[str, object], old_target_comparison: dict[str, object]) -> dict[str, object]:
    best = comparison["best_by_dayahead_hourly_MAE"]
    best_percent = best.get("MAE_percent_of_mean_actual")
    return {
        "best_full36_model": comparison["best_no_price_by_full36_MAE"],
        "best_with_advanced_price_full36_model": comparison["best_with_advanced_price_by_full36_MAE"],
        "best_dayahead_hourly_model": best,
        "best_dayahead_daily_energy_model": comparison["best_by_dayahead_daily_energy_error"],
        "corrected_target_percent_vs_workplace_reference": {
            "best_dayahead_hourly_percent_of_mean_actual": best_percent,
            "workplace_reference_percent": "3-4",
            "interpretation": "LABB-only comparison; weather_actual_as_forecast_proxy prevents production claim.",
        },
        "target_sanity": target_sanity,
        "old_target_reference": old_target_comparison,
        "future_method_candidate_basis": bool(best_percent is not None and float(best_percent) <= 6.0),
    }


def what_we_learned(comparison: dict[str, object]) -> list[str]:
    return [
        "Correcting the target source changes absolute MW error scale and makes percent-of-actual the main comparison metric.",
        "P0054K-P0054O should remain labeled as proxy-target methodology experiments.",
        f"Best corrected-target DayAhead hourly model: {comparison['best_by_dayahead_hourly_MAE']['model']}.",
    ]


def write_p0054q_evidence(evidence_dir: Path, scored_rows: list[dict[str, object]], full36_rows: list[dict[str, object]], dayahead_rows: list[dict[str, object]], summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "metrics-summary.json": write_json(evidence_dir / "metrics-summary.json", summary),
        "full-36h-path-metrics.csv": write_csv(evidence_dir / "full-36h-path-metrics.csv", full36_rows, list(full36_rows[0].keys()) if full36_rows else []),
        "dayahead-delivery-day-metrics.csv": write_csv(evidence_dir / "dayahead-delivery-day-metrics.csv", dayahead_rows, list(dayahead_rows[0].keys()) if dayahead_rows else []),
        "modeling-dataset-sample.csv": write_csv(evidence_dir / "modeling-dataset-sample.csv", scored_rows[:500], dataset_sample_columns(summary)),
        "conditional-metrics.csv": write_csv(evidence_dir / "conditional-metrics.csv", p0054n.flatten_conditional_rows(summary), p0054n.conditional_columns()),
    }
    for name, text in evidence_markdowns(summary).items():
        files[name] = str(write(evidence_dir / name, text))
    return files


def evidence_markdowns(summary: dict[str, object]) -> dict[str, str]:
    common = f"# {PACKAGE_ID} {LABEL}\n\nStatus: `{summary['status']}`\n\n"
    return {
        "CHANGELOG.md": changelog_text(summary),
        "labb-label.md": common + "This package is LABB only. It is not G2-KANDIDAT and creates no deployable model artifact.\n",
        "target-source-contract.md": common + json_block(summary["target_contract"]),
        "p0054p2-source-review.md": common + json_block(summary["p0054p2_source_review"]),
        "split-policy-applied.md": common + json_block(summary["split_policy"]),
        "dataset-contract.md": common + json_block(summary["dataset_contract"]),
        "feature-groups.md": common + json_block(summary["feature_contract"]),
        "input-classification.md": common + json_block(summary["input_classification"]),
        "model-training-evidence.md": common + json_block(summary["model_training"]),
        "full-36h-results.md": common + json_block(summary["full_36h_results"]),
        "dayahead-delivery-day-results.md": common + json_block(summary["dayahead_delivery_day_results"]),
        "percent-error-results.md": common + json_block(summary["percent_error_results"]),
        "daily-energy-error-results.md": common + json_block(summary["daily_energy_error_results"]),
        "advanced-price-ablation.md": common + json_block(summary["advanced_price_ablation"]),
        "model-comparison.md": common + json_block(summary["model_comparison"]),
        "conditional-regime-results.md": common + json_block(summary["conditional_regime_results"]),
        "old-target-comparison.md": common + json_block(summary["old_target_comparison"]),
        "leakage-review.md": common + json_block(summary["leakage_review"]),
        "interpretation.md": common + json_block(summary["interpretation"]),
        "what-we-learned.md": common + json_block(summary["what_we_learned"]),
        "next-package-recommendation.md": common + str(summary["next_package_recommendation"]) + "\n",
    }


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0054Q Changelog

Status: `{summary['status']}`

- Reran SE3 DayAhead/full_36h LABB evaluation with ENTSO-E Actual Total Load target from P0054P2.
- Used `entsoe_consumption_area_hourly_v1.consumption_mw` for SE3 target rows.
- Reused P0054N exact 12:00 Europe/Stockholm D-1 origin machinery and P0054M/P0054N advanced-price protocol.
- Wrote corrected-target full_36h, DayAhead, percent-error, daily-energy, conditional, ablation and old-target comparison evidence.
- No live API, device, runtime, A61, future-flow, Nord Pool, workplace or actual future price/load leakage work was performed.
"""


def dataset_sample_columns(summary: dict[str, object]) -> list[str]:
    columns = [
        "forecast_origin_timestamp_utc",
        "target_timestamp_utc",
        "horizon_h",
        "split",
        p0054k.TARGET_FIELD,
        "target_source_table",
        "target_source_column",
        "weather_proxy_label",
        "price_feature_protocol",
        "forecast_se3_price_target_hour",
    ]
    columns.extend(p0054k.prediction_column(key) for key in summary["model_results"])  # type: ignore[operator]
    return columns


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
    result = run_p0054q_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
