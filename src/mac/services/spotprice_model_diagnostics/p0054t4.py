"""P0054T4 LABB inference-only weather noise realism for SE3 consumption."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json
import math
import random
import tempfile
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0054k, p0054n, p0054q, p0054r, p0054t, p0054t3
from src.mac.services.spotprice_model_diagnostics.p0041 import write
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0054T4"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054T4")
BASELINE_GATE_TARGET_MAE = 253.70062353819162
BASELINE_GATE_TOLERANCE_MW = 1.0
SEEDS = tuple(range(1000, 1010))
MODEL_KEY = "HorizonBiasCorrected_WeightedEnsemble_no_price"
WEIGHTED_KEY = "WeightedEnsemble_no_price"
MODEL_LABEL = "M1_HorizonBiasCorrectedWeightedEnsemble"


@dataclass(frozen=True)
class P0054T4Result:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054t4_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054T4Result:
    started = time.monotonic()
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    t3_weather = read_json_block(Path("requirements/package-runs/P0054T3/weather-noise-results.md"))
    baseline_gate = run_baseline_gate(feature_db, weather_db)
    if not baseline_gate["passed"]:
        summary = stopped_summary(started, baseline_gate, t3_weather)
        return P0054T4Result("STOP", {}, write_p0054t4_evidence(evidence_dir, summary))

    source_rows, rows, path_rows, contracts = p0054r.build_p0054r_modeling_rows(feature_db, weather_db)
    p0054k.assign_p0054i_splits(rows)
    p0054k.assign_p0054i_splits(path_rows)
    p0054r.assign_internal_validation_splits(rows)
    p0054r.assign_internal_validation_splits(path_rows)
    profiles = p0054k.fit_train_profiles([row for row in rows if row["split"] == "train_fit"])
    p0054k.apply_profile_features(rows, profiles)
    p0054k.apply_profile_features(path_rows, profiles)
    feature_contract = p0054q.p0054q_feature_contract()
    features = list(feature_contract[p0054n.VARIANT_NO_PRICE]["features"])  # type: ignore[index]
    environment = p0054r.capture_environment_status()
    specs = selected_specs(environment)
    temperature_columns = temperature_feature_columns(path_rows, features)
    clean_fit = fit_clean_m1(rows, path_rows, features, specs)

    seed_results = []
    clean_result = score_prediction_branch(clean_fit["clean_path_rows"], clean_fit["bias_col"], "W0_clean", None, 0.0)
    seed_results.append(clean_result)
    for seed in SEEDS:
        seed_started = time.monotonic()
        noisy_path = [dict(row) for row in path_rows]
        noise = apply_inference_temperature_noise(noisy_path, seed, temperature_columns, 2.0)
        for key, result in clean_fit["base_results"].items():  # type: ignore[union-attr]
            p0054k.attach_path_predictions(noisy_path, result, features, p0054k.prediction_column(key))
        p0054r.apply_weighted_ensemble(noisy_path, clean_fit["weights"], clean_fit["weighted_col"])  # type: ignore[arg-type]
        apply_fixed_horizon_bias(noisy_path, clean_fit["biases"], clean_fit["weighted_col"], clean_fit["bias_col"])  # type: ignore[arg-type]
        scored = score_prediction_branch(noisy_path, clean_fit["bias_col"], "W1_inferenceTempNoise2C", seed, round(time.monotonic() - seed_started, 3))
        scored["noise"] = noise
        seed_results.append(scored)

    aggregate = summarize_seed_results(seed_results)
    deltas = inference_noise_delta(aggregate)
    leakage = leakage_review(contracts, features, clean_fit)
    status = "WARN"
    if not leakage["ok"] or not baseline_gate["passed"]:
        status = "STOP"
    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "p0054t3_weather_interpretation_review": t3_weather,
        "baseline_reproduction_gate": baseline_gate,
        "target_contract": contracts["target_contract"],
        "split_policy": p0054r.split_policy(),
        "dataset_contract": dataset_contract(source_rows, rows, path_rows),
        "model_contract": model_contract(clean_fit, specs),
        "weather_noise_protocol": {
            "w0": "clean train_fit and clean holdout actual-weather proxy",
            "w1": "clean train_fit; holdout/inference final temperature model-input columns plus deterministic uniform noise",
            "seeds": list(SEEDS),
            "magnitude_c": 2.0,
            "temperature_columns": temperature_columns,
            "limitation": "noise is applied to final model-input temperature columns, not raw weather followed by derived-feature recomputation",
        },
        "temperature_feature_selection": {"columns": temperature_columns, "selection_rule": "weather_proxy temperature/apparent_temperature columns excluding train normals, deltas and degree-hour transforms"},
        "model_training": clean_fit["training"],
        "seed_results": seed_results,
        "inference_noise_results": aggregate,
        "weather_deltas": deltas,
        "leakage_review": leakage,
        "interpretation": interpretation(aggregate, deltas),
        "what_we_learned": what_we_learned(aggregate, deltas),
        "next_package_recommendation": next_package_recommendation(aggregate),
        "row_counts": {
            "source_rows": len(source_rows),
            "modeling_rows": len(rows),
            "path_rows": len(path_rows),
            "seed_result_rows": len(seed_results),
            "w1_seed_count": len(SEEDS),
        },
        "no_live_api": True,
        "no_devices_runtime_a61_nordpool_workplace": True,
        "no_old_target_as_target": True,
        "no_flow_exchange_capacity_target": True,
        "no_future_actual_load_or_price_leakage": True,
        "no_large_model_binaries": True,
    }
    evidence = write_p0054t4_evidence(evidence_dir, summary)
    return P0054T4Result(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def run_baseline_gate(feature_db: Path | str, weather_db: Path | str) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="p0054t4-baseline-") as tmp:
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


def selected_specs(environment: dict[str, object]) -> list[object]:
    specs = p0054k.model_specs(environment["imports"])  # type: ignore[arg-type]
    by_family = {spec.family: spec for spec in specs}
    required = ("HGB", "ExtraTrees", "LightGBM", "XGBoost")
    missing = [family for family in required if family not in by_family]
    if missing:
        raise RuntimeError(f"P0054T4 missing required base model families: {missing}")
    return [by_family[family] for family in required]


def temperature_feature_columns(rows: list[dict[str, object]], features: list[str]) -> list[str]:
    candidates = sorted({column for column in features if column.startswith("weather_proxy_") and ("temperature" in column or "apparent_temperature" in column)})
    excluded_terms = ("train_normal", "delta", "degree")
    return [column for column in candidates if not any(term in column for term in excluded_terms) and any(column in row for row in rows[:200])]


def fit_clean_m1(rows: list[dict[str, object]], path_rows: list[dict[str, object]], features: list[str], specs: list[object]) -> dict[str, object]:
    internal_train = [row for row in rows if row[p0054r.INTERNAL_SPLIT_FIELD] == "internal_train"]
    internal_validation = [row for row in rows if row[p0054r.INTERNAL_SPLIT_FIELD] == "internal_validation"]
    validation_evidence = {}
    base_results = {}
    base_keys = []
    for spec in specs:
        key = f"{spec.family}_no_price"  # type: ignore[attr-defined]
        validation_fit = p0054r.fit_model_on_rows(spec, features, internal_train, internal_validation)
        p0054r.attach_prediction_values(internal_validation, validation_fit["predictions"], p0054k.prediction_column(key))
        validation_evidence[key] = p0054k.regression_metric_from_predictions(internal_validation, validation_fit["predictions"])  # type: ignore[arg-type]
        result = p0054k.fit_variant_model(rows, features, spec, p0054n.VARIANT_NO_PRICE)
        p0054k.attach_path_predictions(path_rows, result, features, p0054k.prediction_column(key))
        base_results[key] = result
        base_keys.append(key)
    weights, weight_evidence = p0054r.learn_inverse_mae_weights(internal_validation, base_keys)
    weighted_col = p0054k.prediction_column(WEIGHTED_KEY)
    p0054r.apply_weighted_ensemble(internal_validation, weights, weighted_col)
    p0054r.apply_weighted_ensemble(path_rows, weights, weighted_col)
    bias_col = p0054k.prediction_column(MODEL_KEY)
    bias_evidence = p0054r.fit_and_apply_horizon_bias_correction(internal_validation, path_rows, WEIGHTED_KEY, bias_col)
    biases = {int(key): float(value) for key, value in dict(bias_evidence["horizon_bias_mw"]).items()}
    return {
        "base_keys": base_keys,
        "base_results": base_results,
        "weights": weights,
        "weighted_col": weighted_col,
        "bias_col": bias_col,
        "biases": biases,
        "clean_path_rows": [dict(row) for row in path_rows],
        "training": {
            "base_models": {key: result["training"] for key, result in base_results.items()},
            "validation": validation_evidence,
            "weights": weight_evidence,
            "horizon_bias": bias_evidence,
            "fit_protocol": "clean_train_fit_weather_only",
            "model_reused_for_all_inference_noise_seeds": True,
        },
    }


def apply_inference_temperature_noise(rows: list[dict[str, object]], seed: int, columns: list[str], magnitude: float) -> dict[str, object]:
    rng = random.Random(seed)
    changed = 0
    min_noise = math.inf
    max_noise = -math.inf
    touched_splits = set()
    for row in rows:
        if row.get("split") != "holdout":
            continue
        for column in columns:
            if row.get(column) is None:
                continue
            noise = rng.uniform(-magnitude, magnitude)
            row[column] = p0054k.safe_float(row.get(column)) + noise
            changed += 1
            min_noise = min(min_noise, noise)
            max_noise = max(max_noise, noise)
            touched_splits.add(str(row.get("split")))
    return {
        "seed": seed,
        "columns": columns,
        "changed_values": changed,
        "min_noise_c": min_noise,
        "max_noise_c": max_noise,
        "bounds_ok": -magnitude <= min_noise <= max_noise <= magnitude if changed else False,
        "touched_splits": sorted(touched_splits),
        "train_fit_changed": "train_fit" in touched_splits,
    }


def apply_fixed_horizon_bias(rows: list[dict[str, object]], biases: dict[int, float], weighted_col: str, bias_col: str) -> int:
    applied = 0
    for row in rows:
        if row.get(weighted_col) is not None:
            row[bias_col] = float(row[weighted_col]) - float(biases.get(int(row["horizon_h"]), 0.0))
            applied += 1
    return applied


def score_prediction_branch(path_rows: list[dict[str, object]], prediction_column: str, weather_mode: str, seed: int | None, duration_seconds: float) -> dict[str, object]:
    scored = p0054t.score_matrix_variant(path_rows, path_rows, MODEL_LABEL, weather_mode, "P0_noPrice_fullCoverage", seed, prediction_column, duration_seconds)
    scored.update(p0054t3.extra_metrics(path_rows, prediction_column))
    return scored


def summarize_seed_results(seed_results: list[dict[str, object]]) -> dict[str, object]:
    by_mode: dict[str, list[dict[str, object]]] = {}
    for row in seed_results:
        by_mode.setdefault(str(row["weather_mode"]), []).append(row)
    return {mode: aggregate_rows(rows) for mode, rows in sorted(by_mode.items())}


def aggregate_rows(rows: list[dict[str, object]]) -> dict[str, object]:
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
    out: dict[str, object] = {"weather_mode": rows[0]["weather_mode"], "seed_count": len(rows), "model": MODEL_LABEL}
    for metric in metrics:
        values = [float(row[metric]) for row in rows if row.get(metric) is not None]
        out[f"{metric}_mean"] = p0054k.mean_float(values) if values else None
        out[f"{metric}_std"] = p0054k.std_float(values) if values else None
        out[f"{metric}_min"] = min(values) if values else None
        out[f"{metric}_max"] = max(values) if values else None
        if values:
            best = min(rows, key=lambda row: float(row[metric]) if row.get(metric) is not None else math.inf)
            worst = max(rows, key=lambda row: float(row[metric]) if row.get(metric) is not None else -math.inf)
            out[f"{metric}_best_seed"] = best.get("seed")
            out[f"{metric}_worst_seed"] = worst.get("seed")
    return out


def inference_noise_delta(aggregate: dict[str, object]) -> dict[str, object]:
    w0 = aggregate["W0_clean"]
    w1 = aggregate["W1_inferenceTempNoise2C"]
    base = float(w0["hourly_MAE_delivery_day_mean"])
    current = float(w1["hourly_MAE_delivery_day_mean"])
    return {
        "inference_noise_delta_W1_minus_W0_MW": current - base,
        "inference_noise_delta_W1_minus_W0_percent": ((current - base) / base * 100.0) if base else None,
        "w0": w0,
        "w1": w1,
    }


def leakage_review(contracts: dict[str, object], features: list[str], clean_fit: dict[str, object]) -> dict[str, object]:
    forbidden = [feature for feature in features if any(term in feature.lower() for term in ("flow", "exchange", "capacity", "a61", "actual_future", "price"))]
    training = clean_fit["training"]
    return {
        "ok": bool(contracts["target_contract"]["ok"]) and not forbidden and not training["weights"]["holdout_used_for_weights"] and not training["horizon_bias"]["holdout_used_for_fit"],  # type: ignore[index]
        "target_contract_ok": bool(contracts["target_contract"]["ok"]),
        "old_physical_balance_target_used": bool(contracts["target_contract"].get("old_physical_balance_target_used")),
        "forbidden_features": forbidden,
        "holdout_used_for_weights_or_correction": bool(training["weights"]["holdout_used_for_weights"]) or bool(training["horizon_bias"]["holdout_used_for_fit"]),  # type: ignore[index]
        "actual_future_load_or_price_feature_used": False,
        "flow_export_import_a61_used": False,
        "api_device_runtime_nordpool_workplace_used": False,
        "spot_price_features_used": False,
    }


def dataset_contract(source_rows: list[dict[str, object]], rows: list[dict[str, object]], path_rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "source_rows": len(source_rows),
        "modeling_rows": len(rows),
        "path_rows": len(path_rows),
        "origins": len({row["forecast_origin_timestamp_utc"] for row in path_rows}),
        "target_start": min(str(row["target_timestamp_utc"]) for row in path_rows),
        "target_end": max(str(row["target_timestamp_utc"]) for row in path_rows),
        "split_counts": p0054k.assign_p0054i_splits([dict(row) for row in rows]),
        "internal_validation_start": p0054r.INTERNAL_VALIDATION_START,
    }


def model_contract(clean_fit: dict[str, object], specs: list[object]) -> dict[str, object]:
    return {
        "model": MODEL_LABEL,
        "base_families": [spec.family for spec in specs],
        "weights": clean_fit["training"]["weights"],  # type: ignore[index]
        "horizon_bias": clean_fit["training"]["horizon_bias"],  # type: ignore[index]
        "model_reused_for_all_inference_noise_seeds": True,
    }


def interpretation(aggregate: dict[str, object], deltas: dict[str, object]) -> dict[str, object]:
    w0 = aggregate["W0_clean"]
    w1 = aggregate["W1_inferenceTempNoise2C"]
    return {
        "w0_dayahead_percent": w0["hourly_MAE_percent_of_mean_actual_mean"],
        "w1_dayahead_percent_mean": w1["hourly_MAE_percent_of_mean_actual_mean"],
        "w1_remains_under_3_percent": float(w1["hourly_MAE_percent_of_mean_actual_mean"]) <= 3.0,
        "w1_remains_under_4_percent": float(w1["hourly_MAE_percent_of_mean_actual_mean"]) <= 4.0,
        "inference_noise_delta": deltas,
        "p0054t3_regularization_note": "P0054T3 W1 retrained on noisy train+holdout weather; P0054T4 W1 keeps clean training and perturbs inference only.",
    }


def what_we_learned(aggregate: dict[str, object], deltas: dict[str, object]) -> list[str]:
    return [
        "Inference-only temperature noise is the correct weather-error realism test; train+holdout noise is a regularization-style sensitivity test.",
        f"W1 inference-only DayAhead MAE delta was {deltas['inference_noise_delta_W1_minus_W0_MW']} MW.",
    ]


def next_package_recommendation(aggregate: dict[str, object]) -> str:
    w1 = aggregate["W1_inferenceTempNoise2C"]
    if float(w1["hourly_MAE_percent_of_mean_actual_mean"]) <= 3.0:
        return "Proceed to rolling/expanding retrain for the no-price M1 path, and separately add real historical weather forecast ingestion."
    return "Prioritize real historical weather forecast ingestion before rolling retrain."


def stopped_summary(started: float, baseline_gate: dict[str, object], t3_weather: object) -> dict[str, object]:
    return {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": "STOP",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "baseline_reproduction_gate": baseline_gate,
        "p0054t3_weather_interpretation_review": t3_weather,
        "leakage_review": {"ok": True, "note": "stopped before inference noise"},
    }


def write_p0054t4_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "inference-noise-summary.json": write_json(evidence_dir / "inference-noise-summary.json", summary),
        "seed-results.csv": write_csv(evidence_dir / "seed-results.csv", summary.get("seed_results", [])),
        "weather-deltas.csv": write_csv(evidence_dir / "weather-deltas.csv", [summary.get("weather_deltas", {})]),
    }
    for name, text in evidence_markdowns(summary).items():
        files[name] = str(write(evidence_dir / name, text))
    return files


def evidence_markdowns(summary: dict[str, object]) -> dict[str, str]:
    common = f"# {PACKAGE_ID} {LABEL}\n\nStatus: `{summary['status']}`\n\n"
    return {
        "CHANGELOG.md": changelog_text(summary),
        "labb-label.md": common + "This package is LABB only. It is not G2-KANDIDAT and creates no deployable model artifact.\n",
        "p0054t3-weather-interpretation-review.md": common + json_block(summary.get("p0054t3_weather_interpretation_review", {})),
        "baseline-reproduction-gate.md": common + json_block(summary.get("baseline_reproduction_gate", {})),
        "target-source-contract.md": common + json_block(summary.get("target_contract", {})),
        "split-policy-applied.md": common + json_block(summary.get("split_policy", {})),
        "dataset-contract.md": common + json_block(summary.get("dataset_contract", {})),
        "model-contract.md": common + json_block(summary.get("model_contract", {})),
        "weather-noise-protocol.md": common + json_block(summary.get("weather_noise_protocol", {})),
        "temperature-feature-selection.md": common + json_block(summary.get("temperature_feature_selection", {})),
        "model-training-evidence.md": common + json_block(summary.get("model_training", {})),
        "inference-noise-results.md": common + json_block(summary.get("inference_noise_results", {})),
        "dayahead-results.md": common + json_block(summary.get("inference_noise_results", {})),
        "full-36h-results.md": common + json_block(summary.get("inference_noise_results", {})),
        "daily-energy-error-results.md": common + json_block(summary.get("inference_noise_results", {})),
        "seed-stability-results.md": common + json_block(summary.get("inference_noise_results", {})),
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
        f"- Baseline gate: {summary.get('baseline_reproduction_gate', {}).get('passed')}\n"
        f"- W1 <=3%: {interp.get('w1_remains_under_3_percent')}\n"
        f"- W1 <=4%: {interp.get('w1_remains_under_4_percent')}\n"
        f"- Delta: {json.dumps(summary.get('weather_deltas', {}), sort_keys=True)}\n"
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
    result = run_p0054t4_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
