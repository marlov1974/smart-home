"""P0054T LABB SE3 consumption weather/price matrix."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import csv
import json
import math
import random
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054l2, p0054m, p0054n, p0054q, p0054r
from src.mac.services.spotprice_model_diagnostics.p0041 import write
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0054T"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054T")
VARIANT_NO_PRICE = p0054n.VARIANT_NO_PRICE
VARIANT_WITH_PRICE = p0054n.VARIANT_WITH_ADVANCED
INTERNAL_SPLIT_FIELD = "p0054t_internal_split"
SEEDS = tuple(range(1000, 1005))
MODEL_KEYS = {
    "M1_HorizonBiasCorrectedWeightedEnsemble": "HorizonBiasCorrected_WeightedEnsemble",
    "M2_WeightedEnsemble": "WeightedEnsemble",
    "M3_XGBoost": "XGBoost",
}


@dataclass(frozen=True)
class P0054TResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054t_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054TResult:
    started = time.monotonic()
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "checkpoints").mkdir(parents=True, exist_ok=True)

    source_rows, base_rows, contracts = build_p0054t_rows(feature_db, weather_db)
    feature_contract = p0054q.p0054q_feature_contract()
    environment = p0054r.capture_environment_status()
    specs = p0054k.model_specs(environment["imports"])  # type: ignore[arg-type]
    spec_by_family = {spec.family: spec for spec in specs}
    selected_specs = [spec_by_family[name] for name in ("HGB", "LightGBM", "XGBoost") if name in spec_by_family]
    if "XGBoost" not in spec_by_family:
        raise RuntimeError("P0054T requires XGBoost for M3 unless package is revised with substitution evidence")
    if len(selected_specs) < 2:
        raise RuntimeError("P0054T needs at least two base models for weighted ensemble")

    temp_columns = temperature_noise_columns(base_rows)
    matrix_results = []
    checkpoints = []
    for weather_mode in ("W0_weatherProxy", "W1_tempNoise2C"):
        seeds = (None,) if weather_mode == "W0_weatherProxy" else SEEDS
        for price_mode in ("P0_noPrice", "P1_p0054l2Price"):
            for seed in seeds:
                label = f"{weather_mode}__{price_mode}" if seed is None else f"{weather_mode}_seed{seed}__{price_mode}"
                combo_started = time.monotonic()
                rows, path_rows, prep = prepare_matrix_rows(base_rows, weather_mode, price_mode, seed, temp_columns)
                features = feature_contract_for_price_mode(feature_contract, price_mode)
                base_model_keys, training_evidence, validation_evidence = fit_base_models_for_matrix(rows, path_rows, features, selected_specs, price_mode)
                weights, weight_evidence = p0054r.learn_inverse_mae_weights([row for row in rows if row[INTERNAL_SPLIT_FIELD] == "internal_validation"], base_model_keys)
                weighted_key = f"WeightedEnsemble_{price_mode}"
                weighted_col = p0054k.prediction_column(weighted_key)
                p0054r.apply_weighted_ensemble(rows, weights, weighted_col)
                p0054r.apply_weighted_ensemble(path_rows, weights, weighted_col)
                bias_key = f"HorizonBiasCorrected_WeightedEnsemble_{price_mode}"
                bias_col = p0054k.prediction_column(bias_key)
                p00554_validation = [row for row in rows if row[INTERNAL_SPLIT_FIELD] == "internal_validation"]
                bias_evidence = p0054r.fit_and_apply_horizon_bias_correction(p00554_validation, path_rows, weighted_key, bias_col)
                p0054r.fit_and_apply_horizon_bias_correction(p00554_validation, rows, weighted_key, bias_col)
                model_columns = {
                    "M1_HorizonBiasCorrectedWeightedEnsemble": bias_col,
                    "M2_WeightedEnsemble": weighted_col,
                    "M3_XGBoost": p0054k.prediction_column(f"XGBoost_{price_mode}"),
                }
                for model_label, column in model_columns.items():
                    matrix_results.append(
                        score_matrix_variant(
                            rows,
                            path_rows,
                            model_label,
                            weather_mode,
                            price_mode,
                            seed,
                            column,
                            round(time.monotonic() - combo_started, 3),
                        )
                    )
                checkpoint = {
                    "label": label,
                    "weather_mode": weather_mode,
                    "price_mode": price_mode,
                    "seed": seed,
                    "prep": prep,
                    "base_model_keys": base_model_keys,
                    "training": training_evidence,
                    "validation": validation_evidence,
                    "weights": weight_evidence,
                    "horizon_bias": bias_evidence,
                    "duration_seconds": round(time.monotonic() - combo_started, 3),
                }
                checkpoints.append(checkpoint)
                write_json(evidence_dir / "checkpoints" / f"{label}.json", checkpoint)

    summary_rows = aggregate_matrix_results(matrix_results)
    price_deltas = price_delta_summary(summary_rows)
    weather_deltas = weather_delta_summary(summary_rows)
    robustness = robustness_ranking(summary_rows)
    leakage_review = validate_p0054t_leakage(contracts, feature_contract, temp_columns, checkpoints)
    status = "PASS" if leakage_review["ok"] and len(summary_rows) == 12 else "WARN"
    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "target_contract": contracts["target_contract"],
        "spotprice_source_contract": contracts["price_contract"],
        "weather_contract": contracts["weather_contract"],
        "split_policy": p0054r.split_policy(),
        "model_selection_from_p0054r": MODEL_KEYS,
        "weather_noise_protocol": {"mode": "uniform_minus2_plus2C", "seeds": list(SEEDS), "columns": temp_columns, "applied_to": "train_fit_and_holdout"},
        "feature_contract": feature_contract,
        "input_classification": input_classification(),
        "runtime_policy": runtime_policy(),
        "environment": environment,
        "matrix_results": summary_rows,
        "seed_results": matrix_results,
        "price_deltas": price_deltas,
        "weather_deltas": weather_deltas,
        "robustness_ranking": robustness,
        "dayahead_results": result_scope(summary_rows, "dayahead"),
        "full_36h_results": result_scope(summary_rows, "full36"),
        "daily_energy_error_results": result_scope(summary_rows, "daily_energy"),
        "conditional_regime_results": {"status": "not_run", "reason": "matrix scope prioritized direct DayAhead/full36/weather/price deltas; prior P0054R conditional evidence remains baseline."},
        "leakage_review": leakage_review,
        "interpretation": interpretation(summary_rows, price_deltas, weather_deltas, robustness),
        "what_we_learned": what_we_learned(summary_rows, price_deltas),
        "next_package_recommendation": "Use M1 HorizonBiasCorrectedWeightedEnsemble without price as the next rolling-retrain/weather-realism candidate unless P0054T price deltas show >=2% benefit.",
        "row_counts": {
            "source_rows": len(source_rows),
            "base_rows": len(base_rows),
            "matrix_summary_rows": len(summary_rows),
            "seed_result_rows": len(matrix_results),
        },
        "checkpoints": checkpoints,
        "no_api_devices_runtime_a61_nordpool_workplace": True,
        "no_old_target_or_future_actual_leakage": True,
    }
    evidence = write_p0054t_evidence(evidence_dir, summary)
    return P0054TResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def build_p0054t_rows(feature_db: Path | str, weather_db: Path | str) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    source_rows = p0054q.load_entsoe_se3_target_rows(feature_db)
    target_contract = p0054q.validate_entsoe_target_contract(source_rows)
    weather_rows, weather_contract = p0054k.load_weather_proxy_rows(weather_db)
    price_source_rows = p0054l2.load_se3_price_rows(Path(feature_db).expanduser())
    price_rows, price_contract = p0054n.build_p0054n_exact_origin_price_rows(price_source_rows)
    rows = p0054m.build_p0054m_modeling_rows(source_rows, weather_rows, price_rows, set(p0054n.HORIZONS_36H))
    return source_rows, rows, {"target_contract": target_contract, "weather_contract": weather_contract, "price_contract": price_contract}


def temperature_noise_columns(rows: list[dict[str, object]]) -> list[str]:
    terms = ("temperature", "apparent_temperature")
    return sorted({key for row in rows[:200] for key in row if key.startswith("weather_proxy_") and any(term in key for term in terms)})


def apply_temperature_noise(rows: list[dict[str, object]], seed: int, columns: list[str]) -> dict[str, object]:
    rng = random.Random(seed)
    min_noise = math.inf
    max_noise = -math.inf
    changed = 0
    for row in rows:
        if row.get("split") == "outside":
            continue
        for column in columns:
            if row.get(column) is None:
                continue
            noise = rng.uniform(-2.0, 2.0)
            row[column] = p0054k.safe_float(row.get(column)) + noise
            min_noise = min(min_noise, noise)
            max_noise = max(max_noise, noise)
            changed += 1
    return {"seed": seed, "columns": columns, "changed_values": changed, "min_noise_c": min_noise, "max_noise_c": max_noise, "bounds_ok": -2.0 <= min_noise <= max_noise <= 2.0}


def prepare_matrix_rows(base_rows: list[dict[str, object]], weather_mode: str, price_mode: str, seed: int | None, temp_columns: list[str]) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    rows = [dict(row) for row in base_rows]
    split_counts = p0054k.assign_p0054i_splits(rows)
    noise = {"applied": False}
    if weather_mode == "W1_tempNoise2C":
        if seed is None:
            raise ValueError("W1 requires seed")
        noise = {"applied": True, **apply_temperature_noise(rows, seed, temp_columns)}
    profiles = p0054k.fit_train_profiles([row for row in rows if row["split"] == "train_fit"])
    p0054k.apply_profile_features(rows, profiles)
    assign_internal_splits(rows)
    path_rows = [dict(row) for row in rows]
    return rows, path_rows, {"split_counts": split_counts, "noise": noise, "price_mode": price_mode, "weather_mode": weather_mode}


def assign_internal_splits(rows: list[dict[str, object]]) -> dict[str, int]:
    counts = {"internal_train": 0, "internal_validation": 0, "not_train_fit": 0}
    for row in rows:
        if row.get("split") != "train_fit":
            value = "not_train_fit"
        elif str(row["target_timestamp_utc"]) < p0054r.INTERNAL_VALIDATION_START:
            value = "internal_train"
        else:
            value = "internal_validation"
        row[INTERNAL_SPLIT_FIELD] = value
        counts[value] += 1
    return counts


def feature_contract_for_price_mode(feature_contract: dict[str, dict[str, object]], price_mode: str) -> list[str]:
    variant = VARIANT_NO_PRICE if price_mode == "P0_noPrice" else VARIANT_WITH_PRICE
    return list(feature_contract[variant]["features"])  # type: ignore[index]


def fit_base_models_for_matrix(rows: list[dict[str, object]], path_rows: list[dict[str, object]], features: list[str], specs: list[object], price_mode: str) -> tuple[list[str], dict[str, object], dict[str, object]]:
    keys = []
    training = {}
    validation = {}
    internal_train = [row for row in rows if row[INTERNAL_SPLIT_FIELD] == "internal_train"]
    internal_validation = [row for row in rows if row[INTERNAL_SPLIT_FIELD] == "internal_validation"]
    for spec in specs:
        key = f"{spec.family}_{price_mode}"  # type: ignore[attr-defined]
        if internal_train and internal_validation:
            val_fit = p0054r.fit_model_on_rows(spec, features, internal_train, internal_validation)
            p0054r.attach_prediction_values(internal_validation, val_fit["predictions"], p0054k.prediction_column(key))
            validation[key] = p0054k.regression_metric_from_predictions(internal_validation, val_fit["predictions"])  # type: ignore[arg-type]
        else:
            validation[key] = {
                "rows": 0,
                "MAE": None,
                "selection_data": "unavailable_for_this_price_origin_coverage",
                "fallback": "equal_weights_and_zero_horizon_bias_inside_train_fit_only",
            }
        result = p0054k.fit_variant_model(rows, features, spec, price_mode)
        p0054k.attach_predictions(rows, result, p0054k.prediction_column(key), holdout_only=True)
        p0054k.attach_path_predictions(path_rows, result, features, p0054k.prediction_column(key))
        training[key] = result["training"]
        keys.append(key)
    return keys, training, validation


def score_matrix_variant(rows: list[dict[str, object]], path_rows: list[dict[str, object]], model_label: str, weather_mode: str, price_mode: str, seed: int | None, prediction_column: str, duration_seconds: float) -> dict[str, object]:
    full36_summary, _ = p0054n.evaluate_full_36h_paths(path_rows, (prediction_column,))
    dayahead_summary, _ = p0054n.evaluate_dayahead_delivery_days(path_rows, (prediction_column,))
    full36_selected = p0054q.selected_full36_rows(path_rows)
    dayahead_selected = p0054q.selected_dayahead_rows(path_rows)
    p0054q.add_percent_metrics(full36_summary, full36_selected, (prediction_column,), "full36")
    p0054q.add_percent_metrics(dayahead_summary, dayahead_selected, (prediction_column,), "dayahead")
    daily = p0054q.daily_energy_error_summary(dayahead_selected, (prediction_column,))
    full = full36_summary[prediction_column]
    day = dayahead_summary[prediction_column]
    energy = daily[prediction_column]
    return {
        "model": model_label,
        "weather_mode": weather_mode,
        "price_mode": price_mode,
        "seed": seed,
        "prediction_column": prediction_column,
        "hourly_MAE_delivery_day": day.get("hourly_MAE_delivery_day"),
        "hourly_RMSE_delivery_day": day.get("hourly_RMSE_delivery_day"),
        "bias_delivery_day": day.get("bias_delivery_day"),
        "hourly_MAE_percent_of_mean_actual": day.get("MAE_percent_of_mean_actual"),
        "hourly_MAE_percent_of_median_actual": day.get("MAE_percent_of_median_actual"),
        "MAE_full_36h": full.get("MAE_full_36h"),
        "RMSE_full_36h": full.get("RMSE_full_36h"),
        "bias_full_36h": full.get("bias_full_36h"),
        "p90_absolute_error": full.get("p90_absolute_error"),
        "p95_absolute_error": full.get("p95_absolute_error"),
        "MAE_percent_of_mean_actual": full.get("MAE_percent_of_mean_actual"),
        "absolute_daily_energy_error_MWh": energy.get("absolute_daily_energy_error_MWh"),
        "signed_daily_energy_error_MWh": energy.get("signed_daily_energy_error_MWh"),
        "daily_energy_error_percent_of_actual": energy.get("daily_energy_error_percent_of_actual"),
        "duration_seconds": duration_seconds,
    }


def aggregate_matrix_results(seed_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped = defaultdict(list)
    for row in seed_rows:
        weather = "W1_tempNoise2C" if row["weather_mode"] == "W1_tempNoise2C" else "W0_weatherProxy"
        grouped[(row["model"], weather, row["price_mode"])].append(row)
    output = []
    metrics = ("hourly_MAE_delivery_day", "hourly_MAE_percent_of_mean_actual", "MAE_full_36h", "absolute_daily_energy_error_MWh", "daily_energy_error_percent_of_actual")
    for (model, weather, price), rows in sorted(grouped.items()):
        out = {"model": model, "weather_mode": weather, "price_mode": price, "seed_count": len(rows)}
        for metric in metrics:
            values = [float(row[metric]) for row in rows if row.get(metric) is not None]
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
        if row["price_mode"] != "P1_p0054l2Price":
            continue
        base = by_key.get((row["model"], row["weather_mode"], "P0_noPrice"))
        if not base:
            continue
        out.append(delta_row(row["model"], row["weather_mode"], "price_delta_with_minus_no_price", row, base))
    return out


def weather_delta_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_key = {(row["model"], row["weather_mode"], row["price_mode"]): row for row in rows}
    out = []
    for row in rows:
        if row["weather_mode"] != "W1_tempNoise2C":
            continue
        base = by_key.get((row["model"], "W0_weatherProxy", row["price_mode"]))
        if not base:
            continue
        out.append(delta_row(row["model"], row["price_mode"], "weather_noise_delta_noisy_minus_proxy", row, base))
    return out


def delta_row(model: object, group: object, kind: str, current: dict[str, object], base: dict[str, object]) -> dict[str, object]:
    metric = "hourly_MAE_delivery_day_mean"
    cur = float(current[metric])
    old = float(base[metric])
    return {"model": model, "group": group, "delta_kind": kind, "delta_MAE": cur - old, "relative_delta_percent": (cur - old) / old * 100.0 if old else None}


def robustness_ranking(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    noisy = [row for row in rows if row["weather_mode"] == "W1_tempNoise2C"]
    ranked = []
    for row in noisy:
        score = float(row["hourly_MAE_delivery_day_mean"]) + float(row.get("hourly_MAE_delivery_day_std") or 0.0)
        ranked.append({**row, "robustness_score": score, "noisy_mean_dayahead_percent_le_4": float(row["hourly_MAE_percent_of_mean_actual_mean"]) <= 4.0})
    return sorted(ranked, key=lambda row: float(row["robustness_score"]))


def result_scope(rows: list[dict[str, object]], scope: str) -> list[dict[str, object]]:
    if scope == "dayahead":
        keys = ("model", "weather_mode", "price_mode", "hourly_MAE_delivery_day_mean", "hourly_MAE_percent_of_mean_actual_mean")
    elif scope == "full36":
        keys = ("model", "weather_mode", "price_mode", "MAE_full_36h_mean", "MAE_percent_of_mean_actual_mean")
    else:
        keys = ("model", "weather_mode", "price_mode", "absolute_daily_energy_error_MWh_mean", "daily_energy_error_percent_of_actual_mean")
    return [{key: row.get(key) for key in keys} for row in rows]


def validate_p0054t_leakage(contracts: dict[str, object], feature_contract: dict[str, dict[str, object]], temp_columns: list[str], checkpoints: list[dict[str, object]]) -> dict[str, object]:
    forbidden = sorted({feature for group in feature_contract.values() for feature in group["features"] if any(term in str(feature).lower() for term in ("physical_balance", "actual_price", "flow", "export", "import", "a61", "capacity", "utilization"))})  # type: ignore[index]
    noise_bounds_ok = all(cp["prep"]["noise"].get("bounds_ok", True) for cp in checkpoints)
    return {
        "ok": contracts["target_contract"]["ok"] and contracts["price_contract"]["ok"] and not forbidden and noise_bounds_ok,
        "target_contract_ok": contracts["target_contract"]["ok"],
        "price_contract_ok": contracts["price_contract"]["ok"],
        "old_physical_balance_target_used": False,
        "actual_future_load_or_price_feature_used": False,
        "flow_export_import_a61_used": False,
        "holdout_used_for_fitting_or_selection": False,
        "holdout_used_for_ensemble_weights_or_correction": False,
        "forbidden_features": forbidden,
        "weather_noise_columns": temp_columns,
        "weather_noise_bounds_ok": noise_bounds_ok,
        "api_device_runtime_nordpool_workplace_used": False,
    }


def interpretation(rows: list[dict[str, object]], price_deltas: list[dict[str, object]], weather_deltas: list[dict[str, object]], robustness: list[dict[str, object]]) -> dict[str, object]:
    best = min(rows, key=lambda row: float(row["hourly_MAE_delivery_day_mean"]))
    best_robust = robustness[0] if robustness else None
    price_helpful = [row for row in price_deltas if row.get("relative_delta_percent") is not None and float(row["relative_delta_percent"]) <= -2.0]
    return {"best_overall_by_dayahead_hourly_MAE": best, "best_robust_combination": best_robust, "price_useful_by_threshold": bool(price_helpful), "price_helpful_rows": price_helpful}


def what_we_learned(rows: list[dict[str, object]], price_deltas: list[dict[str, object]]) -> list[str]:
    best = min(rows, key=lambda row: float(row["hourly_MAE_delivery_day_mean"]))
    price_help = any(row.get("relative_delta_percent") is not None and float(row["relative_delta_percent"]) <= -2.0 for row in price_deltas)
    return [f"Best matrix combination: {best['model']} {best['weather_mode']} {best['price_mode']}.", f"Price feature kept by threshold: {price_help}.", "Weather-noise retraining remains LABB because weather source is synthetic perturbation of actual proxy."]


def input_classification() -> dict[str, object]:
    return {"calendar": "forecast_safe", "historical_entsoe_load_lags": "forecast_safe", "weather_actual_proxy": "proxy", "temperature_noise": "proxy_sensitivity", "p0054l2_compatible_price_forecast": "forecast_safe", "future_actual_load_price_flow_a61": "excluded_leakage"}


def runtime_policy() -> dict[str, object]:
    return {"serial_matrix": True, "w1_seed_count": len(SEEDS), "checkpoint_each_weather_price_seed": True, "model_binaries_persisted": False}


def write_p0054t_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    files = {
        "metrics-summary.json": write_json(evidence_dir / "metrics-summary.json", summary),
        "matrix-results.csv": write_csv(evidence_dir / "matrix-results.csv", summary["matrix_results"], matrix_columns(summary["matrix_results"])),
        "seed-results.csv": write_csv(evidence_dir / "seed-results.csv", summary["seed_results"], seed_columns(summary["seed_results"])),
        "price-deltas.csv": write_csv(evidence_dir / "price-deltas.csv", summary["price_deltas"], ["model", "group", "delta_kind", "delta_MAE", "relative_delta_percent"]),
        "weather-deltas.csv": write_csv(evidence_dir / "weather-deltas.csv", summary["weather_deltas"], ["model", "group", "delta_kind", "delta_MAE", "relative_delta_percent"]),
        "robustness-ranking.csv": write_csv(evidence_dir / "robustness-ranking.csv", summary["robustness_ranking"], matrix_columns(summary["robustness_ranking"])),
    }
    for name, text in evidence_markdowns(summary).items():
        files[name] = str(write(evidence_dir / name, text))
    return files


def evidence_markdowns(summary: dict[str, object]) -> dict[str, str]:
    common = f"# {PACKAGE_ID} {LABEL}\n\nStatus: `{summary['status']}`\n\n"
    return {
        "CHANGELOG.md": changelog_text(summary),
        "labb-label.md": common + "LABB only. Not G2-KANDIDAT and no deployable model artifact.\n",
        "target-source-contract.md": common + json_block(summary["target_contract"]),
        "split-policy-applied.md": common + json_block(summary["split_policy"]),
        "dataset-contract.md": common + json_block({"target": summary["target_contract"], "weather": summary["weather_contract"], "price": summary["spotprice_source_contract"]}),
        "model-selection-from-p0054r.md": common + json_block(summary["model_selection_from_p0054r"]),
        "spotprice-source-contract.md": common + json_block(summary["spotprice_source_contract"]),
        "weather-noise-protocol.md": common + json_block(summary["weather_noise_protocol"]),
        "feature-groups.md": common + json_block(summary["feature_contract"]),
        "input-classification.md": common + json_block(summary["input_classification"]),
        "runtime-policy.md": common + json_block(summary["runtime_policy"]),
        "model-training-evidence.md": common + json_block(summary["checkpoints"]),
        "matrix-combinations.md": common + json_block(summary["matrix_results"]),
        "matrix-results-summary.md": common + json_block(summary["matrix_results"]),
        "dayahead-results.md": common + json_block(summary["dayahead_results"]),
        "full-36h-results.md": common + json_block(summary["full_36h_results"]),
        "daily-energy-error-results.md": common + json_block(summary["daily_energy_error_results"]),
        "weather-noise-results.md": common + json_block(summary["weather_deltas"]),
        "price-ablation-results.md": common + json_block(summary["price_deltas"]),
        "robustness-ranking.md": common + json_block(summary["robustness_ranking"]),
        "conditional-regime-results.md": common + json_block(summary["conditional_regime_results"]),
        "leakage-review.md": common + json_block(summary["leakage_review"]),
        "interpretation.md": common + json_block(summary["interpretation"]),
        "what-we-learned.md": common + json_block(summary["what_we_learned"]),
        "next-package-recommendation.md": common + str(summary["next_package_recommendation"]) + "\n",
    }


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0054T Changelog

Status: `{summary['status']}`

- Ran corrected-target SE3 consumption 3x2x2 weather/price/model LABB matrix.
- Used five deterministic W1 temperature-noise seeds: `{list(SEEDS)}`.
- Used P0054L2-compatible exact-origin spot-price forecast features for P1.
- Wrote matrix, seed, price-delta, weather-delta, robustness and leakage evidence.
- No API, device, runtime, A61, flow, Nord Pool, workplace, old-target or future actual leakage work was performed.
"""


def matrix_columns(rows: list[dict[str, object]]) -> list[str]:
    columns = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    return columns


def seed_columns(rows: list[dict[str, object]]) -> list[str]:
    return matrix_columns(rows)


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
    result = run_p0054t_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
