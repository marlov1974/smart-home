"""P0055B LABB SE3 settlement-migration normalized decomposition."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import csv
import json
import math
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054r, p0055a
from src.mac.services.spotprice_model_diagnostics.p0041 import write


PACKAGE_ID = "P0055B"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0055B")
MONTHLY_TABLE = "se3_component_monthly_allocation_v1"
NORMALIZED_CLUSTER_TABLE = "se3_profiled_cluster_normalized_hourly_v1"
NORMALIZED_RESIDUAL_TABLE = "se3_residual_normalized_hourly_v1"
NORMALIZED_DECOMPOSITION_TABLE = "se3_normalized_decomposition_hourly_v1"
RAW_REFERENCE = Path("requirements/package-runs/P0055A/metrics-summary.json")
EPS = 1e-9


@dataclass(frozen=True)
class P0055BResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0055b_analysis(*, feature_db: Path | str = DEFAULT_FEATURE_DB, evidence_dir: Path | str = EVIDENCE_DIR) -> P0055BResult:
    started = time.monotonic()
    feature_db = Path(feature_db).expanduser()
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    aligned_rows = load_aligned_decomposition_rows(feature_db)
    monthly_observed = monthly_allocation_rows(aligned_rows)
    monotonicity = monotonicity_metrics(monthly_observed)
    allocation_model = fit_train_share_models(monthly_observed)
    normalized_rows, normalization_validation = normalize_hourly_components(aligned_rows, allocation_model)
    db_counts = persist_p0055b_tables(feature_db, allocation_model["monthly_rows"], normalized_rows, normalization_validation["rows"])  # type: ignore[arg-type]

    normalized_components, component_meta = build_normalized_component_targets(normalized_rows)
    weather_rows, weather_contract = p0055a.load_climate_zone_weather_rows(feature_db)
    environment = p0054r.capture_environment_status()
    specs = [spec for spec in p0054k.model_specs(environment["imports"]) if spec.family in p0054k.MODEL_FAMILIES]  # type: ignore[arg-type]
    forecast = forecast_normalized_components(feature_db, normalized_components, component_meta, weather_rows, specs)
    raw_reference = load_raw_reference()
    comparison = comparison_summary(raw_reference, forecast["metrics"])
    leakage = validate_p0055b_leakage(allocation_model, forecast, normalization_validation)
    status = "PASS" if leakage["ok"] and normalization_validation["ok"] and forecast["metrics"]["normalized_decomposition_total"]["dayahead"] else "WARN"
    if not monotonicity["aggregate"]["hypothesis_direction_ok"]:  # type: ignore[index]
        status = "WARN"

    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "input_contract": input_contract(aligned_rows, weather_contract),
        "settlement_migration_hypothesis": settlement_migration_hypothesis(),
        "monthly_share_analysis": monthly_share_analysis(monthly_observed),
        "monotonicity": monotonicity,
        "allocation_model": allocation_model,
        "normalization_validation": normalization_validation,
        "database_output": db_counts,
        "split_policy": p0055a.split_policy(),
        "model_method_contract": p0055a.feature_contract(),
        "component_training": forecast["component_training"],
        "component_results": forecast["component_results"],
        "direct_se3_results": forecast["metrics"]["direct_se3"],
        "raw_decomposition_reference": raw_reference,
        "normalized_decomposition_total_results": forecast["metrics"]["normalized_decomposition_total"],
        "reconciled_results": {"metrics": forecast["metrics"]["reconciled_total"], "reconciliation": forecast["reconciliation"]},
        "comparison_vs_direct": comparison,
        "error_contribution": forecast["error_contribution"],
        "leakage_review": leakage,
        "interpretation": interpretation(comparison, monotonicity, normalization_validation),
        "what_we_learned": what_we_learned(comparison, monotonicity),
        "next_package_recommendation": next_package_recommendation(comparison, monotonicity),
        "row_counts": {
            "aligned_hours": len(aligned_rows),
            "monthly_allocation_rows": len(monthly_observed),
            "normalized_component_rows": len(normalized_rows),
            "forecast_component_count": len(forecast["component_results"]),
            "normalized_decomposition_rows": len(forecast["decomposition_rows"]),
        },
        "no_api": True,
        "no_devices": True,
        "no_runtime_change": True,
        "no_spot_price_features": True,
        "no_old_physical_balance_target": True,
        "no_flow_exchange_a61_capacity_features": True,
        "no_holdout_migration_reference_or_reconciliation_fit": True,
        "no_large_artifacts": True,
    }
    evidence = write_p0055b_evidence(evidence_dir, summary)
    return P0055BResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def load_aligned_decomposition_rows(feature_db: Path | str) -> list[dict[str, object]]:
    direct = {str(row["timestamp_utc"]): float(row["consumption_se3"]) for row in p0055a.load_direct_target_rows(feature_db)}
    components, _meta = p0055a.load_component_target_rows(feature_db)
    timestamps = set(direct)
    for component_id in list(p0055a.ZERO_COMPONENT_IDS) + [p0055a.RESIDUAL_COMPONENT]:
        timestamps &= {str(row["timestamp_utc"]) for row in components[component_id]}
    by_component = {
        component_id: {str(row["timestamp_utc"]): float(row["consumption_se3"]) for row in rows}
        for component_id, rows in components.items()
        if component_id in set(p0055a.ZERO_COMPONENT_IDS) | {p0055a.RESIDUAL_COMPONENT}
    }
    output = []
    for ts in sorted(timestamps):
        values = {component_id: by_component[component_id][ts] for component_id in list(p0055a.ZERO_COMPONENT_IDS) + [p0055a.RESIDUAL_COMPONENT]}
        output.append(
            {
                "timestamp_utc": ts,
                "month_start_utc": month_start(ts),
                "split": p0054k.p0054i_split(ts),
                "total_mw": direct[ts],
                "components": values,
                "component_sum_mw": sum(values.values()),
            }
        )
    return output


def monthly_allocation_rows(aligned_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: {"component_mwh": 0.0, "total_mwh": 0.0, "hours": 0.0})
    for row in aligned_rows:
        total = float(row["total_mw"])
        for component_id, value in row["components"].items():  # type: ignore[union-attr]
            target = grouped[(str(row["month_start_utc"]), str(component_id))]
            target["component_mwh"] += float(value)
            target["total_mwh"] += total
            target["hours"] += 1.0
    output = []
    for (month, component_id), values in sorted(grouped.items()):
        observed_share = values["component_mwh"] / values["total_mwh"] if values["total_mwh"] else 0.0
        output.append(
            {
                "month_start_utc": month,
                "component_id": component_id,
                "component_type": component_type(component_id),
                "observed_share": observed_share,
                "component_mwh": values["component_mwh"],
                "total_mwh": values["total_mwh"],
                "hours": int(values["hours"]),
                "split": p0054k.p0054i_split(month),
            }
        )
    return output


def monotonicity_metrics(monthly_rows: list[dict[str, object]]) -> dict[str, object]:
    by_component = group_rows(monthly_rows, "component_id")
    components = {component_id: monotonicity_for_series(rows) for component_id, rows in by_component.items()}
    profiled_by_month: dict[str, float] = defaultdict(float)
    residual_by_month: dict[str, float] = defaultdict(float)
    for row in monthly_rows:
        if str(row["component_id"]).startswith("C"):
            profiled_by_month[str(row["month_start_utc"])] += float(row["observed_share"])
        elif row["component_id"] == p0055a.RESIDUAL_COMPONENT:
            residual_by_month[str(row["month_start_utc"])] += float(row["observed_share"])
    aggregate = {
        "profiled_total": monotonicity_for_pairs(sorted(profiled_by_month.items())),
        "residual": monotonicity_for_pairs(sorted(residual_by_month.items())),
    }
    aggregate["hypothesis_direction_ok"] = (
        aggregate["profiled_total"]["monthly_share_slope"] > 0.0
        and aggregate["residual"]["monthly_share_slope"] < 0.0
        and aggregate["profiled_total"]["is_one_way_readable"]
        and aggregate["residual"]["is_one_way_readable"]
    )
    return {"components": components, "aggregate": aggregate}


def monotonicity_for_series(rows: list[dict[str, object]]) -> dict[str, object]:
    pairs = [(str(row["month_start_utc"]), float(row["observed_share"])) for row in sorted(rows, key=lambda row: str(row["month_start_utc"]))]
    return monotonicity_for_pairs(pairs)


def monotonicity_for_pairs(pairs: list[tuple[str, float]]) -> dict[str, object]:
    if not pairs:
        return {"monthly_share_start": None, "monthly_share_end": None, "monthly_share_slope": 0.0, "number_of_direction_reversals": 0, "max_backtrack": 0.0, "monotonicity_score": 0.0, "is_one_way_readable": False}
    values = [value for _month, value in pairs]
    slope = linear_slope(values)
    direction = 1 if slope >= 0 else -1
    reversals = 0
    max_backtrack = 0.0
    last_sign = 0
    forward = 0
    backward = 0
    for prev, cur in zip(values, values[1:]):
        delta = cur - prev
        sign = 1 if delta > EPS else -1 if delta < -EPS else 0
        if sign:
            if last_sign and sign != last_sign:
                reversals += 1
            last_sign = sign
        if direction * delta >= -EPS:
            forward += 1
        else:
            backward += 1
            max_backtrack = max(max_backtrack, abs(delta))
    steps = max(len(values) - 1, 1)
    score = forward / steps
    return {
        "monthly_share_start": values[0],
        "monthly_share_end": values[-1],
        "monthly_share_slope": slope,
        "number_of_direction_reversals": reversals,
        "max_backtrack": max_backtrack,
        "monotonicity_score": score,
        "is_one_way_readable": score >= 0.70 and max_backtrack <= max(0.01, abs(values[-1] - values[0]) * 0.75),
    }


def fit_train_share_models(monthly_rows: list[dict[str, object]]) -> dict[str, object]:
    months = sorted({str(row["month_start_utc"]) for row in monthly_rows})
    train_months = [month for month in months if p0054k.p0054i_split(month) == "train_fit"]
    month_index = {month: index for index, month in enumerate(months)}
    reference_month = max(train_months)
    by_component = group_rows(monthly_rows, "component_id")
    fitted: dict[tuple[str, str], float] = {}
    model_rows = []
    model_params = {}
    for component_id, rows in by_component.items():
        train = [row for row in rows if p0054k.p0054i_split(str(row["month_start_utc"])) == "train_fit"]
        xs = [month_index[str(row["month_start_utc"])] for row in train]
        ys = [float(row["observed_share"]) for row in train]
        intercept, slope = linear_fit(xs, ys)
        model_params[component_id] = {"intercept": intercept, "slope": slope, "fit_months": len(train), "fit_data": "train_fit_only"}
        for month in months:
            fitted[(month, component_id)] = max(0.0, intercept + slope * month_index[month])
    for month in months:
        total = sum(fitted[(month, component_id)] for component_id in by_component) or 1.0
        for component_id in by_component:
            fitted[(month, component_id)] = fitted[(month, component_id)] / total
    reference = {component_id: fitted[(reference_month, component_id)] for component_id in by_component}
    for row in monthly_rows:
        component_id = str(row["component_id"])
        month = str(row["month_start_utc"])
        model_rows.append(
            {
                **row,
                "smoothed_share": fitted[(month, component_id)],
                "reference_share": reference[component_id],
                "reference_month_or_window": reference_month,
                "share_slope": model_params[component_id]["slope"],
                "monotonicity_flags": json.dumps(monotonicity_for_series(by_component[component_id]), sort_keys=True),
                "is_forecast_safe_reference": True,
                "generated_by_package": PACKAGE_ID,
            }
        )
    return {
        "method": "train_fit_linear_monthly_share_model_reference_latest_train_fit_month",
        "reference_month": reference_month,
        "reference_shares": reference,
        "model_params": model_params,
        "monthly_rows": model_rows,
        "holdout_months_fit": 0,
        "holdout_used_for_reference": False,
        "holdout_used_for_share_model": False,
    }


def normalize_hourly_components(aligned_rows: list[dict[str, object]], allocation_model: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, object]]:
    smooth = {(str(row["month_start_utc"]), str(row["component_id"])): float(row["smoothed_share"]) for row in allocation_model["monthly_rows"]}  # type: ignore[index]
    reference = {str(key): float(value) for key, value in allocation_model["reference_shares"].items()}  # type: ignore[union-attr]
    output = []
    validation_rows = []
    max_abs_delta = 0.0
    for row in aligned_rows:
        total = float(row["total_mw"])
        month = str(row["month_start_utc"])
        prelim = {}
        for component_id, observed in row["components"].items():  # type: ignore[union-attr]
            observed_share = float(observed) / total if total else 0.0
            denom = smooth.get((month, str(component_id)), 0.0)
            prelim[str(component_id)] = 0.0 if denom <= EPS else observed_share * reference.get(str(component_id), 0.0) / denom
        prelim_sum = sum(prelim.values()) or 1.0
        normalized_sum = 0.0
        observed_sum = 0.0
        for component_id, observed in row["components"].items():  # type: ignore[union-attr]
            normalized_share = prelim[str(component_id)] / prelim_sum
            normalized = total * normalized_share
            observed_sum += float(observed)
            normalized_sum += normalized
            output.append(
                {
                    "timestamp_utc": row["timestamp_utc"],
                    "component_id": component_id,
                    "component_type": component_type(str(component_id)),
                    "observed_consumption_mw": float(observed),
                    "normalized_consumption_mw": normalized,
                    "normalization_method": allocation_model["method"],
                    "reference_month_or_window": allocation_model["reference_month"],
                    "share_used": reference.get(str(component_id), 0.0),
                    "is_forecast_safe_reference": True,
                    "generated_by_package": PACKAGE_ID,
                }
            )
        delta = normalized_sum - total
        max_abs_delta = max(max_abs_delta, abs(delta))
        validation_rows.append(
            {
                "timestamp_utc": row["timestamp_utc"],
                "observed_component_sum_mw": observed_sum,
                "normalized_component_sum_mw": normalized_sum,
                "entsoe_total_consumption_mw": total,
                "normalization_sum_delta_mw": delta,
                "generated_by_package": PACKAGE_ID,
            }
        )
    return output, {"ok": max_abs_delta <= 1e-6, "max_abs_sum_delta_mw": max_abs_delta, "rows": validation_rows}


def persist_p0055b_tables(feature_db: Path, monthly_rows: list[dict[str, object]], normalized_rows: list[dict[str, object]], decomposition_rows: list[dict[str, object]]) -> dict[str, int]:
    clusters = [row for row in normalized_rows if str(row["component_id"]).startswith("C")]
    residual = [row for row in normalized_rows if row["component_id"] == p0055a.RESIDUAL_COMPONENT]
    with sqlite3.connect(feature_db) as conn:
        conn.execute(f"DROP TABLE IF EXISTS {MONTHLY_TABLE}")
        conn.execute(f"DROP TABLE IF EXISTS {NORMALIZED_CLUSTER_TABLE}")
        conn.execute(f"DROP TABLE IF EXISTS {NORMALIZED_RESIDUAL_TABLE}")
        conn.execute(f"DROP TABLE IF EXISTS {NORMALIZED_DECOMPOSITION_TABLE}")
        create_and_insert(conn, MONTHLY_TABLE, monthly_rows)
        create_and_insert(conn, NORMALIZED_CLUSTER_TABLE, clusters)
        create_and_insert(conn, NORMALIZED_RESIDUAL_TABLE, residual)
        create_and_insert(conn, NORMALIZED_DECOMPOSITION_TABLE, decomposition_rows)
        conn.commit()
    return {
        MONTHLY_TABLE: len(monthly_rows),
        NORMALIZED_CLUSTER_TABLE: len(clusters),
        NORMALIZED_RESIDUAL_TABLE: len(residual),
        NORMALIZED_DECOMPOSITION_TABLE: len(decomposition_rows),
    }


def create_and_insert(conn: sqlite3.Connection, table: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    columns = list(rows[0].keys())
    defs = ", ".join(f"{column} {sqlite_type(rows[0].get(column))}" for column in columns)
    conn.execute(f"CREATE TABLE {table} ({defs})")
    placeholders = ", ".join("?" for _ in columns)
    conn.executemany(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", [[row.get(column) for column in columns] for row in rows])


def sqlite_type(value: object) -> str:
    if isinstance(value, int):
        return "INTEGER"
    if isinstance(value, float):
        return "REAL"
    return "TEXT"


def build_normalized_component_targets(normalized_rows: list[dict[str, object]]) -> tuple[dict[str, list[dict[str, object]]], dict[str, dict[str, object]]]:
    components: dict[str, list[dict[str, object]]] = defaultdict(list)
    meta: dict[str, dict[str, object]] = {}
    for row in normalized_rows:
        component_id = str(row["component_id"])
        key = p0055a.RESIDUAL_COMPONENT if component_id == p0055a.RESIDUAL_COMPONENT else component_id
        components[key].append({"timestamp_utc": row["timestamp_utc"], "consumption_se3": float(row["normalized_consumption_mw"])})
        meta.setdefault(key, {"component_type": component_type(key), "total_mwh": 0.0})
        meta[key]["total_mwh"] = float(meta[key]["total_mwh"]) + float(row["normalized_consumption_mw"])
    return dict(components), meta


def forecast_normalized_components(feature_db: Path, normalized_components: dict[str, list[dict[str, object]]], component_meta: dict[str, dict[str, object]], weather_rows: dict[str, dict[str, dict[str, object]]], specs: list[object]) -> dict[str, object]:
    feature_names = p0055a.p0055a_feature_names()
    direct_targets = p0055a.load_direct_target_rows(feature_db)
    direct_rows = p0055a.build_component_modeling_rows(direct_targets, p0055a.DIRECT_COMPONENT, "SE3_BROAD_PROXY", weather_rows, set(p0055a.p0054n.HORIZONS_36H))
    component_results: dict[str, dict[str, object]] = {}
    component_results[p0055a.DIRECT_COMPONENT] = p0055a.fit_component_forecast(p0055a.DIRECT_COMPONENT, "direct_se3_total", direct_rows, feature_names, specs, zero_history=False)
    for cluster_id in p0055a.ZERO_COMPONENT_IDS:
        rows = p0055a.build_component_modeling_rows(normalized_components.get(cluster_id, []), f"forecast_cluster_{cluster_id}", p0055a.CLUSTER_WEATHER_ZONE[cluster_id], weather_rows, set(p0055a.p0054n.HORIZONS_36H))
        zero_history = float(component_meta.get(cluster_id, {}).get("total_mwh", 0.0)) == 0.0
        component_results[cluster_id] = p0055a.fit_component_forecast(cluster_id, "normalized_profiled_load_profile_cluster", rows, feature_names, specs, zero_history=zero_history)
    residual_rows = p0055a.build_component_modeling_rows(normalized_components[p0055a.RESIDUAL_COMPONENT], p0055a.RESIDUAL_COMPONENT, "SE3_BROAD_PROXY", weather_rows, set(p0055a.p0054n.HORIZONS_36H))
    component_results[p0055a.RESIDUAL_COMPONENT] = p0055a.fit_component_forecast(p0055a.RESIDUAL_COMPONENT, "normalized_metered_non_profiled_residual", residual_rows, feature_names, specs, zero_history=False)
    direct_scored = component_results[p0055a.DIRECT_COMPONENT]["rows"]  # type: ignore[assignment]
    decomposition_rows = p0055a.aggregate_decomposition_rows(component_results, direct_scored)
    reconciliation = p0055a.learn_reconciliation_weights(decomposition_rows)
    p0055a.apply_reconciled_forecast(decomposition_rows, reconciliation["weights"])  # type: ignore[arg-type]
    metrics = p0055a.compute_all_metrics(direct_scored, decomposition_rows)
    metrics["normalized_decomposition_total"] = metrics.pop("decomposition_total")
    component_results_rows = p0055a.component_metrics(component_results)
    return {
        "component_results": component_results,
        "component_training": {key: value["training"] for key, value in component_results.items()},
        "component_results_rows": component_results_rows,
        "component_results": component_results_rows,
        "decomposition_rows": decomposition_rows,
        "metrics": metrics,
        "reconciliation": reconciliation,
        "error_contribution": p0055a.error_contribution_analysis(decomposition_rows, component_results),
    }


def load_raw_reference() -> dict[str, object]:
    if not RAW_REFERENCE.exists():
        return {"available": False}
    payload = json.loads(RAW_REFERENCE.read_text())
    return {
        "available": True,
        "p0055a_comparison_vs_direct": payload.get("comparison_vs_direct"),
        "p0055a_decomposition_total": payload.get("total_metrics", {}).get("decomposition_total"),
        "p0055a_direct_se3": payload.get("total_metrics", {}).get("direct_se3"),
    }


def comparison_summary(raw_reference: dict[str, object], metrics: dict[str, object]) -> dict[str, object]:
    direct = metrics["direct_se3"]
    normalized = metrics["normalized_decomposition_total"]
    reconciled = metrics["reconciled_total"]
    direct_mae = metric_value(direct, "dayahead", "hourly_MAE_delivery_day")
    normalized_mae = metric_value(normalized, "dayahead", "hourly_MAE_delivery_day")
    raw_mae = metric_value(raw_reference.get("p0055a_decomposition_total", {}), "dayahead", "hourly_MAE_delivery_day")
    direct_full = metric_value(direct, "full36", "MAE_full_36h")
    normalized_full = metric_value(normalized, "full36", "MAE_full_36h")
    direct_energy = metric_value(direct, "daily_energy", "absolute_daily_energy_error_MWh")
    normalized_energy = metric_value(normalized, "daily_energy", "absolute_daily_energy_error_MWh")
    rec_mae = metric_value(reconciled, "dayahead", "hourly_MAE_delivery_day")
    return {
        "normalized_delta_vs_direct_MW": none_delta(normalized_mae, direct_mae),
        "normalized_delta_vs_direct_percent": relative_delta(normalized_mae, direct_mae),
        "normalized_delta_vs_raw_decomposition_MW": none_delta(normalized_mae, raw_mae),
        "normalized_delta_vs_raw_decomposition_percent": relative_delta(normalized_mae, raw_mae),
        "full36_delta_vs_direct_percent": relative_delta(normalized_full, direct_full),
        "daily_energy_delta_vs_direct_percent": relative_delta(normalized_energy, direct_energy),
        "reconciled_delta_vs_direct_percent": relative_delta(rec_mae, direct_mae),
        "normalized_beats_direct_threshold": p0055a.threshold_decomposition(direct_mae, normalized_mae, direct_energy, normalized_energy, direct_full, normalized_full),
        "normalization_improves_raw_decomposition": bool(raw_mae and normalized_mae and normalized_mae < raw_mae),
    }


def validate_p0055b_leakage(allocation_model: dict[str, object], forecast: dict[str, object], normalization_validation: dict[str, object]) -> dict[str, object]:
    return {
        "ok": normalization_validation["ok"] and not allocation_model["holdout_used_for_reference"] and not allocation_model["holdout_used_for_share_model"] and not forecast["reconciliation"].get("holdout_used_for_weights_or_bias"),
        "normalization_sum_ok": normalization_validation["ok"],
        "holdout_used_for_reference": allocation_model["holdout_used_for_reference"],
        "holdout_used_for_share_model": allocation_model["holdout_used_for_share_model"],
        "reconciliation_holdout_used": bool(forecast["reconciliation"].get("holdout_used_for_weights_or_bias")),
        "spot_price_features_used": False,
        "old_physical_balance_target_used": False,
        "flow_exchange_a61_capacity_used": False,
        "future_actual_target_feature_used": False,
        "residual_treated_as_observed_per_mga": False,
    }


def input_contract(aligned_rows: list[dict[str, object]], weather_contract: dict[str, object]) -> dict[str, object]:
    timestamps = [str(row["timestamp_utc"]) for row in aligned_rows]
    return {
        "ok": bool(aligned_rows) and bool(weather_contract.get("zones")),
        "aligned_hours": len(aligned_rows),
        "start": min(timestamps) if timestamps else "",
        "end": max(timestamps) if timestamps else "",
        "direct_table": p0055a.p0054q.TARGET_TABLE,
        "cluster_table": p0055a.CLUSTER_TABLE,
        "residual_table": p0055a.RESIDUAL_TABLE,
        "weather_contract": weather_contract,
    }


def settlement_migration_hypothesis() -> dict[str, object]:
    return {
        "hypothesis": "profiled/load-profile and residual shares include administrative settlement/product migration",
        "expected_direction": "profiled share trends one way and residual trends opposite",
        "primary_model": "train-fit-only monthly linear share normalization",
        "label": LABEL,
    }


def monthly_share_analysis(monthly_rows: list[dict[str, object]]) -> dict[str, object]:
    profiled = defaultdict(float)
    residual = defaultdict(float)
    for row in monthly_rows:
        if str(row["component_id"]).startswith("C"):
            profiled[str(row["month_start_utc"])] += float(row["observed_share"])
        elif row["component_id"] == p0055a.RESIDUAL_COMPONENT:
            residual[str(row["month_start_utc"])] += float(row["observed_share"])
    return {
        "months": len({row["month_start_utc"] for row in monthly_rows}),
        "component_rows": len(monthly_rows),
        "profiled_total_start_end": first_last(profiled),
        "residual_start_end": first_last(residual),
    }


def interpretation(comparison: dict[str, object], monotonicity: dict[str, object], normalization_validation: dict[str, object]) -> dict[str, object]:
    if not monotonicity["aggregate"]["hypothesis_direction_ok"]:  # type: ignore[index]
        primary = "settlement_migration_not_safely_readable"
    elif comparison["normalized_beats_direct_threshold"]:
        primary = "normalized_decomposition_beats_direct"
    elif comparison["normalization_improves_raw_decomposition"]:
        primary = "normalization_helps_but_direct_remains_default"
    else:
        primary = "normalization_does_not_help_direct_remains_default"
    return {
        "primary_answer": primary,
        "normalization_sum_ok": normalization_validation["ok"],
        "labb_not_g2_candidate": True,
        "weather_proxy_limitation": "P0054Z actual weather is used as actual-as-forecast proxy.",
    }


def what_we_learned(comparison: dict[str, object], monotonicity: dict[str, object]) -> list[str]:
    return [
        f"Aggregate migration direction ok: {monotonicity['aggregate']['hypothesis_direction_ok']}.",
        f"Normalized decomposition delta vs direct: {comparison.get('normalized_delta_vs_direct_percent')} percent.",
        f"Normalized decomposition delta vs raw decomposition: {comparison.get('normalized_delta_vs_raw_decomposition_percent')} percent.",
        "The residual remains calculated, not observed measured MGA data.",
    ]


def next_package_recommendation(comparison: dict[str, object], monotonicity: dict[str, object]) -> str:
    if comparison.get("normalized_beats_direct_threshold"):
        return "P0055C should stress-test normalized decomposition under stricter weather realism and seasonal regimes."
    if monotonicity["aggregate"]["hypothesis_direction_ok"]:  # type: ignore[index]
        return "P0055C should inspect residual substructure or improve cluster taxonomy; direct SE3 remains default."
    return "P0055C should avoid deeper decomposition until a better settlement/product migration signal is available."


def write_p0055b_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", "# P0055B LABB label\n\nLabel: `LABB`. This is not a G2-KANDIDAT evaluation.\n"),
        "input-source-contract.md": write(evidence_dir / "input-source-contract.md", json_report("P0055B input source contract", summary["input_contract"])),
        "settlement-migration-hypothesis.md": write(evidence_dir / "settlement-migration-hypothesis.md", json_report("P0055B settlement migration hypothesis", summary["settlement_migration_hypothesis"])),
        "monthly-share-analysis.md": write(evidence_dir / "monthly-share-analysis.md", json_report("P0055B monthly share analysis", summary["monthly_share_analysis"])),
        "monotonicity-review.md": write(evidence_dir / "monotonicity-review.md", json_report("P0055B monotonicity review", summary["monotonicity"])),
        "allocation-normalization-method.md": write(evidence_dir / "allocation-normalization-method.md", json_report("P0055B allocation normalization method", summary["allocation_model"])),
        "normalized-series-contract.md": write(evidence_dir / "normalized-series-contract.md", json_report("P0055B normalized series contract", summary["normalization_validation"])),
        "database-output-evidence.md": write(evidence_dir / "database-output-evidence.md", json_report("P0055B database output evidence", summary["database_output"])),
        "split-policy-applied.md": write(evidence_dir / "split-policy-applied.md", json_report("P0055B split policy", summary["split_policy"])),
        "model-method-contract.md": write(evidence_dir / "model-method-contract.md", json_report("P0055B model method contract", summary["model_method_contract"])),
        "component-training-evidence.md": write(evidence_dir / "component-training-evidence.md", json_report("P0055B component training evidence", summary["component_training"])),
        "component-results.md": write(evidence_dir / "component-results.md", markdown_table("P0055B component results", summary["component_results"])),
        "direct-se3-results.md": write(evidence_dir / "direct-se3-results.md", json_report("P0055B direct SE3 results", summary["direct_se3_results"])),
        "raw-decomposition-reference.md": write(evidence_dir / "raw-decomposition-reference.md", json_report("P0055B raw decomposition reference", summary["raw_decomposition_reference"])),
        "normalized-decomposition-total-results.md": write(evidence_dir / "normalized-decomposition-total-results.md", json_report("P0055B normalized decomposition total results", summary["normalized_decomposition_total_results"])),
        "reconciled-results.md": write(evidence_dir / "reconciled-results.md", json_report("P0055B reconciled results", summary["reconciled_results"])),
        "comparison-vs-direct.md": write(evidence_dir / "comparison-vs-direct.md", json_report("P0055B comparison vs direct", summary["comparison_vs_direct"])),
        "error-contribution-analysis.md": write(evidence_dir / "error-contribution-analysis.md", json_report("P0055B error contribution analysis", summary["error_contribution"])),
        "leakage-review.md": write(evidence_dir / "leakage-review.md", json_report("P0055B leakage review", summary["leakage_review"])),
        "interpretation.md": write(evidence_dir / "interpretation.md", json_report("P0055B interpretation", summary["interpretation"])),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", "# P0055B what we learned\n\n" + "\n".join(f"- {line}" for line in summary["what_we_learned"]) + "\n"),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", "# P0055B next package recommendation\n\n" + str(summary["next_package_recommendation"]) + "\n"),
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(json_safe(summary), indent=2, sort_keys=True) + "\n"),
    }
    files["monthly-shares.csv"] = write_csv(evidence_dir / "monthly-shares.csv", compact_rows(summary["allocation_model"]["monthly_rows"], 200))  # type: ignore[index]
    files["monotonicity-summary.csv"] = write_csv(evidence_dir / "monotonicity-summary.csv", monotonicity_csv_rows(summary["monotonicity"]))
    files["component-results.csv"] = write_csv(evidence_dir / "component-results.csv", summary["component_results"])
    files["total-comparison.csv"] = write_csv(evidence_dir / "total-comparison.csv", [summary["comparison_vs_direct"]])
    return files


def changelog(summary: dict[str, object]) -> str:
    comparison = summary["comparison_vs_direct"]
    return f"""# P0055B changelog

Status: `{summary['status']}`

- Built LABB settlement-migration normalized SE3 decomposition test.
- Wrote local DB tables for monthly allocation and normalized component series.
- Normalized decomposition delta vs direct DayAhead MAE: `{comparison.get('normalized_delta_vs_direct_percent')}` percent.
- Normalized decomposition delta vs raw decomposition DayAhead MAE: `{comparison.get('normalized_delta_vs_raw_decomposition_percent')}` percent.
- No API, devices, runtime writes, spot-price features, old physical_balance target, flow/A61/capacity features, model binaries or large raw prediction dumps.
"""


def metric_value(container: object, section: str, key: str) -> float | None:
    try:
        value = container[section][key]  # type: ignore[index]
    except (KeyError, TypeError):
        return None
    return None if value is None else float(value)


def none_delta(value: float | None, baseline: float | None) -> float | None:
    if value is None or baseline is None:
        return None
    return value - baseline


def relative_delta(value: float | None, baseline: float | None) -> float | None:
    if value is None or baseline in (None, 0.0):
        return None
    return (value - baseline) / baseline * 100.0


def linear_fit(xs: list[int], ys: list[float]) -> tuple[float, float]:
    if not xs or not ys:
        return 0.0, 0.0
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denom = sum((x - mean_x) ** 2 for x in xs)
    slope = 0.0 if not denom else sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denom
    return mean_y - slope * mean_x, slope


def linear_slope(values: list[float]) -> float:
    _intercept, slope = linear_fit(list(range(len(values))), values)
    return slope


def month_start(timestamp_utc: str) -> str:
    dt = p0052.parse_utc(timestamp_utc)
    return f"{dt.year:04d}-{dt.month:02d}-01T00:00:00Z"


def component_type(component_id: str) -> str:
    if component_id.startswith("C"):
        return "profiled_load_profile_cluster"
    if component_id == p0055a.RESIDUAL_COMPONENT:
        return "metered_non_profiled_residual_calculated"
    return "unknown"


def group_rows(rows: list[dict[str, object]], key: str) -> dict[str, list[dict[str, object]]]:
    out: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        out[str(row[key])].append(row)
    return dict(out)


def first_last(values: dict[str, float]) -> dict[str, object]:
    if not values:
        return {"start": None, "end": None}
    months = sorted(values)
    return {"start_month": months[0], "start": values[months[0]], "end_month": months[-1], "end": values[months[-1]]}


def compact_rows(rows: list[dict[str, object]], limit: int) -> list[dict[str, object]]:
    return rows[:limit]


def monotonicity_csv_rows(monotonicity: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for component_id, metrics in monotonicity["components"].items():  # type: ignore[union-attr]
        rows.append({"component_id": component_id, **metrics})
    for component_id, metrics in monotonicity["aggregate"].items():  # type: ignore[union-attr]
        if isinstance(metrics, dict):
            rows.append({"component_id": component_id, **metrics})
    return rows


def json_report(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(json_safe(payload), indent=2, sort_keys=True)}\n```\n"


def markdown_table(title: str, rows: object) -> str:
    rows = list(rows) if isinstance(rows, list) else []
    if not rows:
        return f"# {title}\n\nNo rows.\n"
    headers = list(rows[0].keys())
    lines = [f"# {title}", "", "| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(fmt_cell(row.get(header)) for header in headers) + " |")
    return "\n".join(lines) + "\n"


def write_csv(path: Path, rows: object) -> str:
    rows = list(rows) if isinstance(rows, list) else []
    if not rows:
        path.write_text("")
        return str(path)
    headers = list(rows[0].keys())
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({header: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value for header, value in row.items()})
    return str(path)


def fmt_cell(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return ""
    return str(value)


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items() if key != "rows"}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def main() -> None:
    result = run_p0055b_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
