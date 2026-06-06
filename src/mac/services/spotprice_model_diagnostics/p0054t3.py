"""P0054T3 LABB corrected SE3 consumption weather/price matrix."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import csv
import json
import math
import tempfile
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054l2, p0054m, p0054n, p0054q, p0054r, p0054t
from src.mac.services.spotprice_model_diagnostics.p0041 import write
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0054T3"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054T3")
BASELINE_GATE_TARGET_MAE = 253.70062353819162
BASELINE_GATE_TOLERANCE_MW = 1.0
SEEDS = tuple(range(1000, 1005))
P0_FULL = "P0_noPrice_fullCoverage"
P0_MATCHED = "P0_noPrice_matchedPriceCoverage"
P1_MATCHED = "P1_p0054l2Price_matchedCoverage"
M1 = "M1_HorizonBiasCorrectedWeightedEnsemble"
M2 = "M2_WeightedEnsemble"
M3 = "M3_XGBoost"


@dataclass(frozen=True)
class P0054T3Result:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054t3_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054T3Result:
    started = time.monotonic()
    evidence_dir = Path(evidence_dir)
    checkpoint_dir = evidence_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    p0054t2_review = read_json_block(Path("requirements/package-runs/P0054T2/root-cause-analysis.md"))
    baseline_gate = run_baseline_gate(feature_db, weather_db)
    if not baseline_gate["passed"]:
        summary = stopped_summary(started, p0054t2_review, baseline_gate)
        evidence = write_p0054t3_evidence(evidence_dir, summary)
        return P0054T3Result(status="STOP", row_counts={}, evidence=evidence)

    p0_source_rows, p0_base_rows, p0_contracts = build_p0_full_rows(feature_db, weather_db)
    p1_base_rows, p1_contracts = build_p1_price_rows(feature_db, weather_db)
    p1_keys = row_keys(p1_base_rows)
    p0_matched_rows = [dict(row) for row in p0_base_rows if row_key(row) in p1_keys]
    p0_matched_contract = {
        "ok": bool(p0_matched_rows),
        "rows": len(p0_matched_rows),
        "reason": "matched P0 diagnostic on safe P1 price forecast coverage",
        "coverage_source": "intersection(P0054R no-price skeleton, P0054N exact-origin P0054L2-compatible price rows)",
    }

    environment = p0054r.capture_environment_status()
    specs = selected_specs(environment)
    feature_contract = p0054q.p0054q_feature_contract()
    no_price_features = list(feature_contract[p0054n.VARIANT_NO_PRICE]["features"])  # type: ignore[index]
    with_price_features = list(feature_contract[p0054n.VARIANT_WITH_ADVANCED]["features"])  # type: ignore[index]
    temp_columns = p0054t.temperature_noise_columns(p0_base_rows + p1_base_rows)

    seed_results: list[dict[str, object]] = []
    checkpoints: list[dict[str, object]] = []
    branches = [
        (P0_FULL, p0_base_rows, no_price_features, "primary_full_p0054r_coverage"),
        (P0_MATCHED, p0_matched_rows, no_price_features, "matched_price_coverage_diagnostic"),
        (P1_MATCHED, p1_base_rows, with_price_features, "safe_p0054l2_price_forecast_coverage"),
    ]
    for price_mode, rows, features, coverage_label in branches:
        for weather_mode in ("W0_weatherProxy", "W1_tempNoise2C"):
            seeds = (None,) if weather_mode == "W0_weatherProxy" else SEEDS
            for seed in seeds:
                checkpoint = run_matrix_branch(rows, features, specs, weather_mode, price_mode, seed, temp_columns, coverage_label)
                checkpoints.append(checkpoint)
                seed_results.extend(checkpoint["seed_results"])  # type: ignore[arg-type]
                label = checkpoint["label"]
                write_json(checkpoint_dir / f"{label}.json", checkpoint)

    primary_seed_results = [row for row in seed_results if row["price_mode"] in {P0_FULL, P1_MATCHED}]
    matrix_results = aggregate_matrix_results(primary_seed_results)
    matched_results = aggregate_matrix_results([row for row in seed_results if row["price_mode"] in {P0_MATCHED, P1_MATCHED}])
    price_deltas = price_delta_summary(matched_results)
    weather_deltas = weather_delta_summary(matrix_results)
    m1_m2 = aggregate_m1_m2_diagnostics(checkpoints)
    robustness = robustness_ranking(matrix_results)
    leakage = leakage_review(p0_contracts, p1_contracts, checkpoints, feature_contract)
    p1_narrower = len(p1_base_rows) < len(p0_base_rows)
    status = "WARN" if p1_narrower else "PASS"
    if not leakage["ok"] or len(matrix_results) != 12:
        status = "STOP"

    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "p0054t2_root_cause_review": p0054t2_review,
        "baseline_reproduction_gate": baseline_gate,
        "target_contract": p0_contracts["target_contract"],
        "split_policy": p0054r.split_policy(),
        "dataset_contract": dataset_contract(p0_source_rows, p0_base_rows, p1_base_rows, p0_matched_rows, p0_contracts, p1_contracts),
        "model_selection_from_p0054r": {"models": [M1, M2, M3], "base_families": [spec.family for spec in specs]},
        "m1_m2_diagnostic": m1_m2,
        "spotprice_source_contract": p1_contracts["price_contract"],
        "price_coverage_policy": price_coverage_policy(p0_base_rows, p1_base_rows, p0_matched_contract),
        "weather_noise_protocol": {"mode": "temperature_uniform_minus2_plus2C", "seeds": list(SEEDS), "columns": temp_columns, "applied_to": "train_fit_and_holdout_before_profile_fit_and_model_retrain"},
        "feature_contract": feature_contract,
        "input_classification": input_classification(),
        "runtime_policy": runtime_policy(),
        "environment": environment,
        "model_training": {checkpoint["label"]: checkpoint["training"] for checkpoint in checkpoints},
        "branch_checkpoints": checkpoints,
        "seed_results": seed_results,
        "matrix_results": matrix_results,
        "matched_coverage_results": matched_results,
        "price_deltas": price_deltas,
        "weather_deltas": weather_deltas,
        "robustness_ranking": robustness,
        "conditional_regime_results": conditional_summary(checkpoints),
        "leakage_review": leakage,
        "interpretation": interpretation(matrix_results, price_deltas, weather_deltas, robustness, p1_narrower),
        "what_we_learned": what_we_learned(p1_narrower),
        "next_package_recommendation": next_package_recommendation(matrix_results, price_deltas),
        "row_counts": {
            "source_rows": len(p0_source_rows),
            "p0_full_rows": len(p0_base_rows),
            "p1_price_rows": len(p1_base_rows),
            "p0_matched_rows": len(p0_matched_rows),
            "matrix_summary_rows": len(matrix_results),
            "seed_result_rows": len(seed_results),
        },
        "no_live_api": True,
        "no_devices_runtime_a61_nordpool_workplace": True,
        "no_old_target_as_target": True,
        "no_flow_exchange_capacity_target": True,
        "no_future_actual_load_or_price_leakage": True,
        "no_large_model_binaries": True,
    }
    evidence = write_p0054t3_evidence(evidence_dir, summary)
    return P0054T3Result(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def run_baseline_gate(feature_db: Path | str, weather_db: Path | str) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="p0054t3-baseline-") as tmp:
        result = p0054r.run_p0054r_analysis(feature_db=feature_db, weather_db=weather_db, evidence_dir=tmp)
        metrics = json.loads((Path(tmp) / "metrics-summary.json").read_text())
        best = metrics["model_comparison"]["best_dayahead_hourly"]
        mae = float(best["hourly_MAE_delivery_day"])
        delta = abs(mae - BASELINE_GATE_TARGET_MAE)
        return {
            "status": result.status,
            "model": best["model"],
            "hourly_MAE_delivery_day": mae,
            "target_MAE": BASELINE_GATE_TARGET_MAE,
            "absolute_delta_MW": delta,
            "tolerance_MW": BASELINE_GATE_TOLERANCE_MW,
            "passed": result.status == "PASS" and delta <= BASELINE_GATE_TOLERANCE_MW,
            "row_counts": result.row_counts,
            "tmp_evidence_committed": False,
        }


def build_p0_full_rows(feature_db: Path | str, weather_db: Path | str) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    source_rows, direct_rows, _path_rows, contracts = p0054r.build_p0054r_modeling_rows(feature_db, weather_db)
    return source_rows, direct_rows, contracts


def build_p1_price_rows(feature_db: Path | str, weather_db: Path | str) -> tuple[list[dict[str, object]], dict[str, object]]:
    source_rows = p0054q.load_entsoe_se3_target_rows(feature_db)
    target_contract = p0054q.validate_entsoe_target_contract(source_rows)
    weather_rows, weather_contract = p0054k.load_weather_proxy_rows(weather_db)
    price_source_rows = p0054l2.load_se3_price_rows(Path(feature_db).expanduser())
    price_rows, price_contract = p0054n.build_p0054n_exact_origin_price_rows(price_source_rows)
    rows = p0054m.build_p0054m_modeling_rows(source_rows, weather_rows, price_rows, set(p0054n.HORIZONS_36H))
    return rows, {"target_contract": target_contract, "weather_contract": weather_contract, "price_contract": price_contract}


def selected_specs(environment: dict[str, object]) -> list[object]:
    specs = p0054k.model_specs(environment["imports"])  # type: ignore[arg-type]
    by_family = {spec.family: spec for spec in specs}
    required = ("HGB", "ExtraTrees", "LightGBM", "XGBoost")
    missing = [family for family in required if family not in by_family]
    if missing:
        raise RuntimeError(f"P0054T3 missing required model families: {missing}")
    return [by_family[family] for family in required]


def run_matrix_branch(rows_in: list[dict[str, object]], features: list[str], specs: list[object], weather_mode: str, price_mode: str, seed: int | None, temp_columns: list[str], coverage_label: str) -> dict[str, object]:
    started = time.monotonic()
    rows = [dict(row) for row in rows_in]
    split_counts = p0054k.assign_p0054i_splits(rows)
    noise = {"applied": False}
    if weather_mode == "W1_tempNoise2C":
        if seed is None:
            raise ValueError("W1 requires seed")
        noise = {"applied": True, **p0054t.apply_temperature_noise(rows, seed, temp_columns)}
    profiles = p0054k.fit_train_profiles([row for row in rows if row["split"] == "train_fit"])
    p0054k.apply_profile_features(rows, profiles)
    internal_counts = assign_internal_splits(rows)
    path_rows = [dict(row) for row in rows]
    internal_train = [row for row in rows if row[p0054r.INTERNAL_SPLIT_FIELD] == "internal_train"]
    internal_validation = [row for row in rows if row[p0054r.INTERNAL_SPLIT_FIELD] == "internal_validation"]

    base_keys: list[str] = []
    training: dict[str, object] = {}
    validation: dict[str, object] = {}
    for spec in specs:
        key = f"{spec.family}_{price_mode}"  # type: ignore[attr-defined]
        if internal_train and internal_validation:
            val_fit = p0054r.fit_model_on_rows(spec, features, internal_train, internal_validation)
            p0054r.attach_prediction_values(internal_validation, val_fit["predictions"], p0054k.prediction_column(key))
            validation[key] = p0054k.regression_metric_from_predictions(internal_validation, val_fit["predictions"])  # type: ignore[arg-type]
        else:
            validation[key] = {"MAE": None, "rows": 0, "fallback": "equal_weights_and_zero_horizon_bias_no_internal_validation"}
        result = p0054k.fit_variant_model(rows, features, spec, price_mode)
        p0054k.attach_predictions(rows, result, p0054k.prediction_column(key), holdout_only=True)
        p0054k.attach_path_predictions(path_rows, result, features, p0054k.prediction_column(key))
        training[key] = result["training"]
        base_keys.append(key)

    weights, weight_evidence = p0054r.learn_inverse_mae_weights(internal_validation, base_keys)
    weighted_key = f"WeightedEnsemble_{price_mode}"
    weighted_col = p0054k.prediction_column(weighted_key)
    p0054r.apply_weighted_ensemble(rows, weights, weighted_col)
    p0054r.apply_weighted_ensemble(path_rows, weights, weighted_col)
    bias_key = f"HorizonBiasCorrected_WeightedEnsemble_{price_mode}"
    bias_col = p0054k.prediction_column(bias_key)
    bias_evidence = p0054r.fit_and_apply_horizon_bias_correction(internal_validation, path_rows, weighted_key, bias_col)
    p0054r.fit_and_apply_horizon_bias_correction(internal_validation, rows, weighted_key, bias_col)

    model_columns = {
        M1: bias_col,
        M2: weighted_col,
        M3: p0054k.prediction_column(f"XGBoost_{price_mode}"),
    }
    seed_results = []
    for model, column in model_columns.items():
        scored = p0054t.score_matrix_variant(rows, path_rows, model, weather_mode, price_mode, seed, column, round(time.monotonic() - started, 3))
        scored.update(extra_metrics(path_rows, column))
        scored["coverage_label"] = coverage_label
        seed_results.append(scored)
    label = f"{weather_mode}__{price_mode}" if seed is None else f"{weather_mode}_seed{seed}__{price_mode}"
    return {
        "label": label,
        "coverage_label": coverage_label,
        "weather_mode": weather_mode,
        "price_mode": price_mode,
        "seed": seed,
        "split_counts": split_counts,
        "internal_split_counts": internal_counts,
        "noise": noise,
        "base_model_keys": base_keys,
        "training": training,
        "validation": validation,
        "weights": weight_evidence,
        "horizon_bias": bias_evidence,
        "m1_m2_diagnostic": m1_m2_diagnostic(path_rows, weighted_col, bias_col, bias_evidence),
        "seed_results": seed_results,
        "duration_seconds": round(time.monotonic() - started, 3),
    }


def assign_internal_splits(rows: list[dict[str, object]]) -> dict[str, int]:
    counts = {"internal_train": 0, "internal_validation": 0, "not_train_fit": 0}
    for row in rows:
        if row.get("split") != "train_fit":
            value = "not_train_fit"
        elif str(row["target_timestamp_utc"]) < p0054r.INTERNAL_VALIDATION_START:
            value = "internal_train"
        else:
            value = "internal_validation"
        row[p0054r.INTERNAL_SPLIT_FIELD] = value
        counts[value] += 1
    return counts


def m1_m2_diagnostic(rows: list[dict[str, object]], weighted_col: str, bias_col: str, bias_evidence: dict[str, object]) -> dict[str, object]:
    pairs = [(float(row[weighted_col]), float(row[bias_col])) for row in rows if row.get(weighted_col) is not None and row.get(bias_col) is not None]
    diffs = [abs(left - right) for left, right in pairs]
    biases = [abs(float(value)) for value in dict(bias_evidence.get("horizon_bias_mw", {})).values()]
    corr = correlation([left for left, _right in pairs], [right for _left, right in pairs])
    return {
        "compared_rows": len(pairs),
        "horizon_bias_nonzero_count": sum(1 for value in biases if value > 1e-9),
        "max_abs_horizon_bias_mw": max(biases) if biases else None,
        "prediction_correlation_M1_M2": corr,
        "p95_abs_prediction_diff_M1_M2": percentile(diffs, 0.95),
        "max_abs_prediction_diff_M1_M2": max(diffs) if diffs else None,
        "m1_equals_m2": bool(diffs) and max(diffs) <= 1e-9,
    }


def extra_metrics(path_rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    full36 = p0054q.selected_full36_rows(path_rows)
    dayahead = p0054q.selected_dayahead_rows(path_rows)
    out = {
        "MAE_0_6h": subset_mae(full36, prediction_column, lambda row: 1 <= int(row["horizon_h"]) <= 6),
        "MAE_0_12h": subset_mae(full36, prediction_column, lambda row: 1 <= int(row["horizon_h"]) <= 12),
        "MAE_0_24h": subset_mae(full36, prediction_column, lambda row: 1 <= int(row["horizon_h"]) <= 24),
        "MAE_24_36h": subset_mae(full36, prediction_column, lambda row: 25 <= int(row["horizon_h"]) <= 36),
        "offpeak_MAE": subset_mae(dayahead, prediction_column, lambda row: stockholm_hour(row) in set(range(0, 6)) | set(range(22, 24))),
        "morning_ramp_MAE": subset_mae(dayahead, prediction_column, lambda row: 6 <= stockholm_hour(row) <= 9),
        "evening_peak_MAE": subset_mae(dayahead, prediction_column, lambda row: 16 <= stockholm_hour(row) <= 20),
    }
    out.update(peak_metrics(dayahead, prediction_column))
    return out


def subset_mae(rows: list[dict[str, object]], prediction_column: str, predicate: object) -> float | None:
    errors = [abs(float(row[prediction_column]) - float(row[p0054k.TARGET_FIELD])) for row in rows if row.get(prediction_column) is not None and predicate(row)]  # type: ignore[operator]
    return p0054k.mean_float(errors) if errors else None


def stockholm_hour(row: dict[str, object]) -> int:
    return p0052.parse_utc(str(row["target_timestamp_utc"])).astimezone(p0054n.STOCKHOLM).hour


def peak_metrics(dayahead_rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    timing = []
    mw_errors = []
    for origin, rows in p0054k.group_by(dayahead_rows, "forecast_origin_timestamp_utc").items():
        available = [row for row in rows if row.get(prediction_column) is not None]
        if not available:
            continue
        actual_peak = max(available, key=lambda row: float(row[p0054k.TARGET_FIELD]))
        pred_peak = max(available, key=lambda row: float(row[prediction_column]))
        timing.append(abs(stockholm_hour(actual_peak) - stockholm_hour(pred_peak)))
        mw_errors.append(abs(float(pred_peak[prediction_column]) - float(actual_peak[p0054k.TARGET_FIELD])))
    return {"peak_hour_timing_error_hours": p0054k.mean_float(timing) if timing else None, "peak_hour_error_MW": p0054k.mean_float(mw_errors) if mw_errors else None}


def aggregate_matrix_results(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[object, object, object], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        weather = "W1_tempNoise2C" if row["weather_mode"] == "W1_tempNoise2C" else "W0_weatherProxy"
        grouped[(row["model"], weather, row["price_mode"])].append(row)
    metrics = (
        "hourly_MAE_delivery_day",
        "hourly_MAE_percent_of_mean_actual",
        "MAE_full_36h",
        "absolute_daily_energy_error_MWh",
        "daily_energy_error_percent_of_actual",
        "peak_hour_error_MW",
        "peak_hour_timing_error_hours",
        "offpeak_MAE",
        "morning_ramp_MAE",
        "evening_peak_MAE",
        "MAE_0_6h",
        "MAE_0_12h",
        "MAE_0_24h",
        "MAE_24_36h",
    )
    output = []
    for (model, weather, price), group in sorted(grouped.items()):
        out: dict[str, object] = {"model": model, "weather_mode": weather, "price_mode": price, "seed_count": len(group), "coverage_label": group[0].get("coverage_label")}
        for metric in metrics:
            values = [float(row[metric]) for row in group if row.get(metric) is not None]
            out[f"{metric}_mean"] = p0054k.mean_float(values) if values else None
            out[f"{metric}_std"] = p0054k.std_float(values) if values else None
            out[f"{metric}_min"] = min(values) if values else None
            out[f"{metric}_max"] = max(values) if values else None
        output.append(out)
    return output


def price_delta_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_key = {(row["model"], row["weather_mode"], row["price_mode"]): row for row in rows}
    out = []
    for row in rows:
        if row["price_mode"] != P1_MATCHED:
            continue
        base = by_key.get((row["model"], row["weather_mode"], P0_MATCHED))
        if base:
            out.append(delta_row(row["model"], row["weather_mode"], "price_p1_minus_matched_p0", row, base))
    return out


def weather_delta_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_key = {(row["model"], row["weather_mode"], row["price_mode"]): row for row in rows}
    out = []
    for row in rows:
        if row["weather_mode"] != "W1_tempNoise2C":
            continue
        base = by_key.get((row["model"], "W0_weatherProxy", row["price_mode"]))
        if base:
            out.append(delta_row(row["model"], row["price_mode"], "weather_w1_minus_w0", row, base))
    return out


def delta_row(model: object, group: object, kind: str, current: dict[str, object], base: dict[str, object]) -> dict[str, object]:
    base_mae = float(base["hourly_MAE_delivery_day_mean"])
    current_mae = float(current["hourly_MAE_delivery_day_mean"])
    return {
        "kind": kind,
        "model": model,
        "group": group,
        "base_hourly_MAE_delivery_day": base_mae,
        "current_hourly_MAE_delivery_day": current_mae,
        "delta_hourly_MAE_delivery_day": current_mae - base_mae,
        "relative_delta_percent": ((current_mae - base_mae) / base_mae * 100.0) if base_mae else None,
        "base_daily_energy_error_MWh": base.get("absolute_daily_energy_error_MWh_mean"),
        "current_daily_energy_error_MWh": current.get("absolute_daily_energy_error_MWh_mean"),
        "base_MAE_full_36h": base.get("MAE_full_36h_mean"),
        "current_MAE_full_36h": current.get("MAE_full_36h_mean"),
    }


def robustness_ranking(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        if row["weather_mode"] == "W1_tempNoise2C":
            mean = float(row["hourly_MAE_delivery_day_mean"])
            std = float(row.get("hourly_MAE_delivery_day_std") or 0.0)
            out.append({**row, "robustness_score": mean + std})
    return sorted(out, key=lambda row: float(row["robustness_score"]))


def aggregate_m1_m2_diagnostics(checkpoints: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "label": checkpoint["label"],
            "coverage_label": checkpoint["coverage_label"],
            "weather_mode": checkpoint["weather_mode"],
            "price_mode": checkpoint["price_mode"],
            "seed": checkpoint["seed"],
            **checkpoint["m1_m2_diagnostic"],  # type: ignore[arg-type]
        }
        for checkpoint in checkpoints
    ]


def leakage_review(p0_contracts: dict[str, object], p1_contracts: dict[str, object], checkpoints: list[dict[str, object]], feature_contract: dict[str, dict[str, object]]) -> dict[str, object]:
    forbidden = []
    for variant in (p0054n.VARIANT_NO_PRICE, p0054n.VARIANT_WITH_ADVANCED):
        for feature in feature_contract[variant]["features"]:  # type: ignore[index]
            name = str(feature).lower()
            if any(term in name for term in ("flow", "exchange", "capacity", "a61", "actual_future")):
                forbidden.append(feature)
    holdout_meta = any(bool(checkpoint["weights"].get("holdout_used_for_weights")) or bool(checkpoint["horizon_bias"].get("holdout_used_for_fit")) for checkpoint in checkpoints)
    return {
        "ok": bool(p0_contracts["target_contract"]["ok"]) and bool(p1_contracts["target_contract"]["ok"]) and not forbidden and not holdout_meta,
        "target_contract_ok": bool(p0_contracts["target_contract"]["ok"]) and bool(p1_contracts["target_contract"]["ok"]),
        "old_physical_balance_target_used": bool(p0_contracts["target_contract"].get("old_physical_balance_target_used")) or bool(p1_contracts["target_contract"].get("old_physical_balance_target_used")),
        "forbidden_features": forbidden,
        "holdout_used_for_weights_or_correction": holdout_meta,
        "actual_future_load_or_price_feature_used": False,
        "flow_export_import_a61_used": False,
        "api_device_runtime_nordpool_workplace_used": False,
    }


def dataset_contract(source_rows: list[dict[str, object]], p0_rows: list[dict[str, object]], p1_rows: list[dict[str, object]], p0_matched_rows: list[dict[str, object]], p0_contracts: dict[str, object], p1_contracts: dict[str, object]) -> dict[str, object]:
    return {
        "target": p0_contracts["target_contract"],
        "weather": p0_contracts["weather_contract"],
        "p0_full": rowset_contract(p0_rows),
        "p1_price_coverage": rowset_contract(p1_rows),
        "p0_matched_price_coverage": rowset_contract(p0_matched_rows),
        "source_rows": len(source_rows),
        "p1_target_contract": p1_contracts["target_contract"],
    }


def rowset_contract(rows: list[dict[str, object]]) -> dict[str, object]:
    tmp = [dict(row) for row in rows]
    split_counts = p0054k.assign_p0054i_splits(tmp)
    internal_counts = assign_internal_splits(tmp)
    return {
        "rows": len(rows),
        "origins": len({row["forecast_origin_timestamp_utc"] for row in rows}),
        "target_start": min((str(row["target_timestamp_utc"]) for row in rows), default=""),
        "target_end": max((str(row["target_timestamp_utc"]) for row in rows), default=""),
        "split_counts": split_counts,
        "internal_split_counts": internal_counts,
    }


def price_coverage_policy(p0_rows: list[dict[str, object]], p1_rows: list[dict[str, object]], p0_matched_contract: dict[str, object]) -> dict[str, object]:
    return {
        "p0_primary_coverage": "full P0054R no-price origin skeleton",
        "p1_coverage": "safe P0054N exact-origin P0054L2-compatible forecast rows",
        "p1_narrower_than_p0": len(p1_rows) < len(p0_rows),
        "p0_rows": len(p0_rows),
        "p1_rows": len(p1_rows),
        "matched_p0_diagnostic": p0_matched_contract,
        "price_delta_rule": "compare P1 only against P0_on_price_coverage, never against full P0 as a coverage-confounded delta",
    }


def input_classification() -> dict[str, object]:
    return {
        "target": "historical_observed_only",
        "weather_w0": "proxy",
        "weather_w1": "proxy_sensitivity",
        "p0_price": "excluded_leakage",
        "p1_price": "requires_separate_forecast_model_forecast_safe",
        "label": LABEL,
    }


def runtime_policy() -> dict[str, object]:
    return {"api": False, "devices": False, "runtime_change": False, "deployable_model_artifact": False, "large_artifacts": False}


def conditional_summary(checkpoints: list[dict[str, object]]) -> dict[str, object]:
    return {"status": "included_as_extra_metrics", "branches": len(checkpoints), "notes": "Peak/offpeak/morning/evening and horizon-slice metrics are reported per matrix row."}


def interpretation(rows: list[dict[str, object]], price_deltas: list[dict[str, object]], weather_deltas: list[dict[str, object]], robustness: list[dict[str, object]], p1_narrower: bool) -> dict[str, object]:
    best = min(rows, key=lambda row: float(row["hourly_MAE_delivery_day_mean"]))
    noisy = [row for row in rows if row["weather_mode"] == "W1_tempNoise2C"]
    best_noisy = min(noisy, key=lambda row: float(row["hourly_MAE_delivery_day_mean"])) if noisy else None
    price_useful = any(float(row["relative_delta_percent"]) <= -2.0 for row in price_deltas if row.get("relative_delta_percent") is not None)
    noisy_under_4 = [row for row in noisy if float(row["hourly_MAE_percent_of_mean_actual_mean"]) <= 4.0]
    return {
        "best_overall_by_dayahead_hourly_MAE": best,
        "best_noisy": best_noisy,
        "price_useful_by_threshold": price_useful,
        "noisy_combinations_under_4_percent": noisy_under_4,
        "p1_narrower_than_p0": p1_narrower,
        "status_note": "WARN expected when P1 remains matched-coverage only." if p1_narrower else "P1 aligned with full P0 coverage.",
    }


def what_we_learned(p1_narrower: bool) -> list[str]:
    out = ["Corrected P0 full coverage must remain independent of price forecast availability."]
    if p1_narrower:
        out.append("Current safe P0054L2/P0054N price coverage is narrower than P0054R no-price coverage, so price deltas must be matched-coverage diagnostics.")
    return out


def next_package_recommendation(rows: list[dict[str, object]], price_deltas: list[dict[str, object]]) -> str:
    best = min(rows, key=lambda row: float(row["hourly_MAE_delivery_day_mean"]))
    return f"Use {best['model']} / {best['weather_mode']} / {best['price_mode']} as the rolling/expanding retrain candidate; keep price only if matched deltas meet the package threshold."


def stopped_summary(started: float, p0054t2_review: object, baseline_gate: dict[str, object]) -> dict[str, object]:
    return {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": "STOP",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "p0054t2_root_cause_review": p0054t2_review,
        "baseline_reproduction_gate": baseline_gate,
        "leakage_review": {"ok": True, "note": "stopped before matrix"},
        "what_we_learned": ["Baseline reproduction gate failed; full matrix was not run."],
        "next_package_recommendation": "Investigate P0054R reproducibility drift before matrix work.",
    }


def row_key(row: dict[str, object]) -> tuple[str, str, int]:
    return (str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"]), int(row["horizon_h"]))


def row_keys(rows: list[dict[str, object]]) -> set[tuple[str, str, int]]:
    return {row_key(row) for row in rows}


def correlation(left: list[float], right: list[float]) -> float | None:
    if len(left) < 2 or len(left) != len(right):
        return None
    mean_left = sum(left) / len(left)
    mean_right = sum(right) / len(right)
    numerator = sum((a - mean_left) * (b - mean_right) for a, b in zip(left, right))
    denom_left = math.sqrt(sum((a - mean_left) ** 2 for a in left))
    denom_right = math.sqrt(sum((b - mean_right) ** 2 for b in right))
    return numerator / (denom_left * denom_right) if denom_left and denom_right else None


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, math.ceil(q * len(ordered)) - 1))
    return ordered[idx]


def write_p0054t3_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "metrics-summary.json": write_json(evidence_dir / "metrics-summary.json", summary),
        "matrix-results.csv": write_csv(evidence_dir / "matrix-results.csv", summary.get("matrix_results", [])),
        "seed-results.csv": write_csv(evidence_dir / "seed-results.csv", summary.get("seed_results", [])),
        "price-deltas.csv": write_csv(evidence_dir / "price-deltas.csv", summary.get("price_deltas", [])),
        "weather-deltas.csv": write_csv(evidence_dir / "weather-deltas.csv", summary.get("weather_deltas", [])),
        "robustness-ranking.csv": write_csv(evidence_dir / "robustness-ranking.csv", summary.get("robustness_ranking", [])),
        "matched-coverage-price-deltas.csv": write_csv(evidence_dir / "matched-coverage-price-deltas.csv", summary.get("price_deltas", [])),
    }
    markdowns = evidence_markdowns(summary)
    for name, text in markdowns.items():
        files[name] = str(write(evidence_dir / name, text))
    return files


def evidence_markdowns(summary: dict[str, object]) -> dict[str, str]:
    common = f"# {PACKAGE_ID} {LABEL}\n\nStatus: `{summary['status']}`\n\n"
    return {
        "CHANGELOG.md": changelog_text(summary),
        "labb-label.md": common + "This package is LABB only. It is not G2-KANDIDAT and creates no deployable model artifact.\n",
        "p0054t2-root-cause-review.md": common + json_block(summary["p0054t2_root_cause_review"]),
        "baseline-reproduction-gate.md": common + json_block(summary["baseline_reproduction_gate"]),
        "target-source-contract.md": common + json_block(summary.get("target_contract", {})),
        "split-policy-applied.md": common + json_block(summary.get("split_policy", {})),
        "dataset-contract.md": common + json_block(summary.get("dataset_contract", {})),
        "model-selection-from-p0054r.md": common + json_block(summary.get("model_selection_from_p0054r", {})),
        "m1-m2-diagnostic.md": common + json_block(summary.get("m1_m2_diagnostic", [])),
        "spotprice-source-contract.md": common + json_block(summary.get("spotprice_source_contract", {})),
        "price-coverage-policy.md": common + json_block(summary.get("price_coverage_policy", {})),
        "weather-noise-protocol.md": common + json_block(summary.get("weather_noise_protocol", {})),
        "feature-groups.md": common + json_block(summary.get("feature_contract", {})),
        "input-classification.md": common + json_block(summary.get("input_classification", {})),
        "runtime-policy.md": common + json_block(summary.get("runtime_policy", {})),
        "model-training-evidence.md": common + json_block(summary.get("model_training", {})),
        "matrix-combinations.md": common + json_block(summary.get("branch_checkpoints", [])),
        "matrix-results-summary.md": common + json_block(summary.get("matrix_results", [])),
        "dayahead-results.md": common + json_block(summary.get("matrix_results", [])),
        "full-36h-results.md": common + json_block(summary.get("matrix_results", [])),
        "daily-energy-error-results.md": common + json_block(summary.get("matrix_results", [])),
        "weather-noise-results.md": common + json_block(summary.get("weather_deltas", [])),
        "price-ablation-results.md": common + json_block(summary.get("price_deltas", [])),
        "robustness-ranking.md": common + json_block(summary.get("robustness_ranking", [])),
        "conditional-regime-results.md": common + json_block(summary.get("conditional_regime_results", {})),
        "leakage-review.md": common + json_block(summary.get("leakage_review", {})),
        "interpretation.md": common + json_block(summary.get("interpretation", {})),
        "what-we-learned.md": common + "\n".join(f"- {item}" for item in summary.get("what_we_learned", [])) + "\n",
        "next-package-recommendation.md": common + str(summary.get("next_package_recommendation", "")) + "\n",
    }


def changelog_text(summary: dict[str, object]) -> str:
    interp = summary.get("interpretation", {})
    return (
        f"# {PACKAGE_ID} {LABEL} Changelog\n\n"
        f"Status: `{summary['status']}`\n\n"
        "## Result\n\n"
        f"- Baseline gate: {summary['baseline_reproduction_gate'].get('passed')}\n"
        f"- Matrix rows: {len(summary.get('matrix_results', []))}\n"
        f"- Best overall: {json.dumps(interp.get('best_overall_by_dayahead_hourly_MAE', {}), sort_keys=True)}\n"
        f"- Price coverage: {json.dumps(summary.get('price_coverage_policy', {}), sort_keys=True)}\n"
    )


def read_json_block(path: Path) -> object:
    text = path.read_text()
    start = text.index("```json") + len("```json")
    end = text.index("```", start)
    return json.loads(text[start:end].strip())


def write_json(path: Path, payload: object) -> str:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return str(path)


def write_csv(path: Path, rows: object) -> str:
    rows = list(rows) if isinstance(rows, list) else []
    with path.open("w", newline="") as fh:
        if not rows:
            fh.write("")
            return str(path)
        columns = sorted({key for row in rows for key in row.keys()})
        writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


def json_block(payload: object) -> str:
    return "```json\n" + json.dumps(payload, indent=2, sort_keys=True) + "\n```\n"


def main() -> None:
    result = run_p0054t3_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
