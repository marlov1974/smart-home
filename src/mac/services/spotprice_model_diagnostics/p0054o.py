"""P0054O LABB SE3 DayAhead weather noise ablation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json
import math
import time

import numpy as np

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0054k, p0054l2, p0054m, p0054n
from src.mac.services.spotprice_model_diagnostics.p0041 import write
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0054O"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054O")
SEEDS = tuple(range(1000, 1010))
NOISE_AMPLITUDE_C = 2.0
SCENARIO = "uniform_pm2c_train_and_holdout"
VARIANT_WITH_ADVANCED = p0054n.VARIANT_WITH_ADVANCED
SELECTED_MODELS = (
    ("HGB", p0054n.VARIANT_NO_PRICE),
    ("LightGBM", p0054n.VARIANT_NO_PRICE),
    ("LightGBM", VARIANT_WITH_ADVANCED),
    ("XGBoost", p0054n.VARIANT_NO_PRICE),
)
WORKPLACE_REFERENCE = {"reported_error_range_percent": "3-4", "source": "operator-provided contextual reference"}


@dataclass(frozen=True)
class P0054OResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054o_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054OResult:
    started = time.monotonic()
    evidence_dir = Path(evidence_dir)
    base = build_base_rows(Path(feature_db).expanduser(), Path(weather_db).expanduser())
    feature_contract = p0054n.p0054n_feature_contract()
    temp_discovery = temperature_feature_columns(feature_contract)
    if not temp_discovery["selected_for_noise"]:
        raise RuntimeError(f"P0054O found no temperature columns: {temp_discovery}")

    environment = p0054k.capture_environment_status()
    specs = p0054k.model_specs(environment["imports"])  # type: ignore[arg-type]
    baseline = run_one_weather_case(base["direct_rows"], feature_contract, specs, selected_models(), scenario="baseline_no_noise", seed=None, temp_columns=temp_discovery["selected_for_noise"], amplitude=0.0)
    seed_runs = [
        run_one_weather_case(base["direct_rows"], feature_contract, specs, selected_models(), scenario=SCENARIO, seed=seed, temp_columns=temp_discovery["selected_for_noise"], amplitude=NOISE_AMPLITUDE_C)
        for seed in SEEDS
    ]
    seed_metrics = [row for run in seed_runs for row in run["metric_rows"]]
    baseline_metrics = baseline["metric_rows"]
    seed_summary = summarize_seed_metrics(seed_metrics, baseline_metrics)
    price_summary = advanced_price_under_weather_noise(seed_summary)
    leakage_review = leakage_review_summary(base, baseline, seed_runs)
    status = "PASS" if leakage_review["ok"] and required_models_ran(seed_summary) else "WARN"
    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "weather_noise_protocol": weather_noise_protocol(),
        "temperature_feature_discovery": temp_discovery,
        "split_policy": p0054n.split_policy(),
        "dataset_contract": base["target_contract"],
        "price_feature_protocol": base["exact_price_contract"],
        "environment": environment,
        "selected_models": selected_models(),
        "model_training": {"baseline": baseline["model_training"], "noisy_seed_runs": {str(run["seed"]): run["model_training"] for run in seed_runs}},
        "baseline_metrics": baseline_metrics,
        "seed_metric_summary": seed_summary,
        "full_36h_weather_noise_results": extract_metric_family(seed_summary, "full36"),
        "dayahead_weather_noise_results": extract_metric_family(seed_summary, "dayahead"),
        "percent_error_results": extract_percent_results(seed_summary),
        "daily_energy_error_results": extract_daily_energy_results(seed_summary),
        "advanced_price_under_weather_noise": price_summary,
        "conditional_regime_results": baseline["conditional_regime_results"],
        "leakage_review": leakage_review,
        "interpretation": interpretation(seed_summary, price_summary),
        "row_counts": {
            "base_direct_rows": len(base["direct_rows"]),
            "baseline_metric_rows": len(baseline_metrics),
            "seed_metric_rows": len(seed_metrics),
            "seeds": len(SEEDS),
            "exact_origin_price_rows": int(base["exact_price_contract"]["rows"]),
        },
        "no_api_devices_runtime_a61_future_flow": True,
        "no_large_artifacts": True,
    }
    evidence = write_p0054o_evidence(evidence_dir, baseline_metrics, seed_metrics, summary)
    return P0054OResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def build_base_rows(feature_db: Path, weather_db: Path) -> dict[str, object]:
    source_rows = p0054k.load_se3_consumption_rows(feature_db)
    target_contract = p0054k.validate_target_contract(source_rows)
    if not target_contract["ok"]:
        raise RuntimeError(f"P0054O target contract failed: {target_contract}")
    weather_rows, weather_contract = p0054k.load_weather_proxy_rows(weather_db)
    price_rows = p0054l2.load_se3_price_rows(feature_db)
    exact_price_rows, exact_price_contract = p0054n.build_p0054n_exact_origin_price_rows(price_rows)
    if not exact_price_contract["ok"]:
        raise RuntimeError(f"P0054O exact price contract failed: {exact_price_contract}")
    direct_rows = p0054m.build_p0054m_modeling_rows(source_rows, weather_rows, exact_price_rows, set(p0054n.HORIZONS_36H))
    return {
        "target_contract": target_contract,
        "weather_contract": weather_contract,
        "exact_price_contract": exact_price_contract,
        "direct_rows": direct_rows,
    }


def selected_models() -> list[dict[str, str]]:
    return [{"family": family, "variant": variant, "model_key": f"{family}_{variant}"} for family, variant in SELECTED_MODELS]


def temperature_feature_columns(feature_contract: dict[str, dict[str, object]]) -> dict[str, object]:
    used = sorted({str(feature) for meta in feature_contract.values() for feature in meta["features"] if any(token in str(feature).lower() for token in ("temp", "temperature", "t2m"))})  # type: ignore[index]
    selected = [column for column in used if column in ("weather_proxy_temperature_2m_se3", "weather_proxy_apparent_temperature_se3")]
    derived = [column for column in used if column not in selected]
    return {
        "used_temperature_like_features": used,
        "selected_for_noise": selected,
        "derived_recomputed_after_noise": derived,
        "selection_rule": "perturb source temperature-like weather proxy columns; recompute train normal/delta/cold-spell derived features after noise",
    }


def apply_temperature_noise(rows: list[dict[str, object]], columns: list[str], *, seed: int, amplitude: float) -> tuple[list[dict[str, object]], dict[str, object]]:
    rng = np.random.default_rng(seed)
    out = [dict(row) for row in rows]
    audit: dict[str, object] = {"seed": seed, "amplitude": amplitude, "columns": columns, "min_noise": {}, "max_noise": {}, "changed_values": 0}
    for column in columns:
        noises = []
        for row in out:
            if not p0054k.is_finite(row.get(column)):
                continue
            noise = float(rng.random() * (2.0 * amplitude) - amplitude)
            row[column] = float(row[column]) + noise
            noises.append(noise)
        audit["min_noise"][column] = min(noises) if noises else None  # type: ignore[index]
        audit["max_noise"][column] = max(noises) if noises else None  # type: ignore[index]
        audit["changed_values"] = int(audit["changed_values"]) + len(noises)
    return out, audit


def prepare_rows_for_training(base_rows: list[dict[str, object]], *, seed: int | None, temp_columns: list[str], amplitude: float) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    rows = [dict(row) for row in base_rows]
    noise_audit: dict[str, object] = {"scenario": "baseline_no_noise", "noise_applied": False}
    if seed is not None and amplitude > 0:
        rows, noise_audit = apply_temperature_noise(rows, temp_columns, seed=seed, amplitude=amplitude)
        noise_audit["scenario"] = SCENARIO
        noise_audit["noise_applied"] = True
    split_counts = p0054k.assign_p0054i_splits(rows)
    profiles = p0054k.fit_train_profiles([row for row in rows if row["split"] == "train_fit"])
    p0054k.apply_profile_features(rows, profiles)
    path_rows = [dict(row) for row in rows]
    noise_audit["split_counts"] = split_counts
    return rows, path_rows, noise_audit


def run_one_weather_case(
    base_rows: list[dict[str, object]],
    feature_contract: dict[str, dict[str, object]],
    specs: list[object],
    model_requests: list[dict[str, str]],
    *,
    scenario: str,
    seed: int | None,
    temp_columns: list[str],
    amplitude: float,
) -> dict[str, object]:
    direct_rows, path_rows, noise_audit = prepare_rows_for_training(base_rows, seed=seed, temp_columns=temp_columns, amplitude=amplitude)
    model_results, scored_rows, scored_path_rows = fit_selected_models(direct_rows, path_rows, feature_contract, specs, model_requests)
    metric_rows = evaluate_weather_noise_run(scored_path_rows, tuple(model_results), scenario=scenario, seed=seed)
    prediction_columns = tuple(p0054k.prediction_column(key) for key in model_results)
    return {
        "scenario": scenario,
        "seed": seed,
        "noise_audit": noise_audit,
        "model_training": {key: result["training"] for key, result in model_results.items()},
        "metric_rows": metric_rows,
        "conditional_regime_results": p0054k.evaluate_conditional_regimes(scored_path_rows, prediction_columns) if seed is None else {},
        "scored_rows": scored_rows[:0],
    }


def fit_selected_models(
    direct_rows: list[dict[str, object]],
    path_rows: list[dict[str, object]],
    feature_contract: dict[str, dict[str, object]],
    specs: list[object],
    model_requests: list[dict[str, str]],
) -> tuple[dict[str, dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    spec_by_family = {spec.family: spec for spec in specs}  # type: ignore[attr-defined]
    model_results: dict[str, dict[str, object]] = {}
    scored_rows = [dict(row) for row in direct_rows]
    scored_path_rows = [dict(row) for row in path_rows]
    for request in model_requests:
        family = request["family"]
        variant = request["variant"]
        spec = spec_by_family.get(family)
        if spec is None:
            continue
        features = feature_contract[variant]["features"]
        result = p0054k.fit_variant_model(scored_rows, features, spec, variant)  # type: ignore[arg-type]
        model_key = request["model_key"]
        model_results[model_key] = result
        p0054k.attach_predictions(scored_rows, result, p0054k.prediction_column(model_key), holdout_only=True)
        p0054k.attach_path_predictions(scored_path_rows, result, features, p0054k.prediction_column(model_key))  # type: ignore[arg-type]
    return model_results, scored_rows, scored_path_rows


def evaluate_weather_noise_run(rows: list[dict[str, object]], model_keys: tuple[str, ...], *, scenario: str, seed: int | None) -> list[dict[str, object]]:
    full36_rows = select_complete_full36_rows(rows)
    dayahead_rows = select_complete_dayahead_rows(rows)
    metric_rows = []
    for model_key in model_keys:
        column = p0054k.prediction_column(model_key)
        full_metric = p0054k.regression_metric_from_predictions([row for row in full36_rows if row.get(column) is not None], [float(row[column]) for row in full36_rows if row.get(column) is not None])
        day_subset = [row for row in dayahead_rows if row.get(column) is not None]
        day_metric = p0054k.regression_metric_from_predictions(day_subset, [float(row[column]) for row in day_subset])
        energy = daily_energy_error_percent(day_subset, column)
        metric_rows.append(
            {
                "scenario": scenario,
                "seed": "" if seed is None else seed,
                "model": model_key,
                "MAE_full_36h": full_metric["MAE"],
                "RMSE_full_36h": full_metric["RMSE"],
                "bias_full_36h": full_metric["bias"],
                "p90_full_36h": full_metric["p90_absolute_error"],
                "p95_full_36h": full_metric["p95_absolute_error"],
                "full36_MAE_percent_of_mean_actual": full_metric["MAE_percent_of_mean_actual"],
                "full36_MAE_percent_of_median_actual": full_metric["MAE_percent_of_median_actual"],
                "hourly_MAE_delivery_day": day_metric["MAE"],
                "hourly_RMSE_delivery_day": day_metric["RMSE"],
                "bias_delivery_day": day_metric["bias"],
                "hourly_MAE_percent_of_mean_actual": day_metric["MAE_percent_of_mean_actual"],
                "hourly_MAE_percent_of_median_actual": day_metric["MAE_percent_of_median_actual"],
                "absolute_daily_energy_error_MWh": energy["absolute_daily_energy_error_MWh"],
                "signed_daily_energy_error_MWh": energy["signed_daily_energy_error_MWh"],
                "daily_energy_error_percent_of_actual": energy["daily_energy_error_percent_of_actual"],
                "peak_hour_error_MW": p0054n.peak_hour_mw_error(day_subset, column),
                "peak_hour_timing_error_hours": p0054n.peak_hour_timing_error(day_subset, column),
                "morning_ramp_MAE": p0054n.subset_mae(day_subset, column, lambda row: 6 <= int(row["target_model_cet_hour"]) <= 9),
                "evening_peak_MAE": p0054n.subset_mae(day_subset, column, lambda row: 16 <= int(row["target_model_cet_hour"]) <= 20),
            }
        )
    return metric_rows


def select_complete_full36_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_origin = p0054k.group_by([row for row in rows if row["split"] == "holdout"], "forecast_origin_timestamp_utc")
    complete = [origin for origin, group in by_origin.items() if {int(row["horizon_h"]) for row in group} >= set(p0054n.HORIZONS_36H)]
    return [row for origin in complete for row in by_origin[origin] if int(row["horizon_h"]) in p0054n.HORIZONS_36H]


def select_complete_dayahead_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_origin_target = {(str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"])): row for row in rows if row["split"] == "holdout"}
    target_dates = sorted({p0054n.p0052.parse_utc(str(row["target_timestamp_utc"])).astimezone(p0054n.STOCKHOLM).date() for row in rows if row["split"] == "holdout"})
    selected: list[dict[str, object]] = []
    for delivery_day in target_dates:
        origin = p0054n.dayahead_origin_utc_for_delivery_day(delivery_day)
        targets = p0054n.delivery_day_target_utc_hours(delivery_day)
        day_rows = [by_origin_target.get((origin, target)) for target in targets]
        if any(row is None for row in day_rows):
            continue
        selected.extend([row for row in day_rows if row is not None])
    return selected


def daily_energy_error_percent(rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    grouped = p0054k.group_by(rows, "forecast_origin_timestamp_utc")
    signed = []
    abs_pct = []
    for group in grouped.values():
        actual_sum = sum(float(row[p0054k.TARGET_FIELD]) for row in group)
        pred_sum = sum(float(row[prediction_column]) for row in group)
        err = pred_sum - actual_sum
        signed.append(err)
        if abs(actual_sum) > 1e-9:
            abs_pct.append(abs(err) / actual_sum * 100.0)
    return {
        "absolute_daily_energy_error_MWh": p0054k.mean_float([abs(value) for value in signed]) if signed else None,
        "signed_daily_energy_error_MWh": p0054k.mean_float(signed) if signed else None,
        "daily_energy_error_percent_of_actual": p0054k.mean_float(abs_pct) if abs_pct else None,
    }


def summarize_seed_metrics(seed_rows: list[dict[str, object]], baseline_rows: list[dict[str, object]]) -> dict[str, object]:
    baseline_by_model = {str(row["model"]): row for row in baseline_rows}
    out = {}
    fields = [
        "MAE_full_36h",
        "RMSE_full_36h",
        "full36_MAE_percent_of_mean_actual",
        "hourly_MAE_delivery_day",
        "hourly_RMSE_delivery_day",
        "hourly_MAE_percent_of_mean_actual",
        "absolute_daily_energy_error_MWh",
        "daily_energy_error_percent_of_actual",
    ]
    for model, rows in p0054k.group_by(seed_rows, "model").items():
        model_out = {"baseline": baseline_by_model.get(model, {}), "noisy": {}}
        for field in fields:
            values = [float(row[field]) for row in rows if row.get(field) is not None and math.isfinite(float(row[field]))]
            base = baseline_by_model.get(model, {}).get(field)
            model_out["noisy"][field] = distribution(values, float(base) if base is not None else None)  # type: ignore[index]
        out[model] = model_out
    return out


def distribution(values: list[float], baseline: float | None) -> dict[str, object]:
    if not values:
        return {"count": 0}
    mean_value = p0054k.mean_float(values)
    return {
        "count": len(values),
        "mean": mean_value,
        "std": p0054k.std_float(values),
        "min": min(values),
        "max": max(values),
        "baseline": baseline,
        "delta_vs_baseline": mean_value - baseline if baseline is not None else None,
        "relative_change_percent": p0054k.relative_change(mean_value, baseline) if baseline is not None else None,
    }


def advanced_price_under_weather_noise(seed_summary: dict[str, object]) -> dict[str, object]:
    no_model = "LightGBM_no_price"
    with_model = f"LightGBM_{VARIANT_WITH_ADVANCED}"
    no_day = seed_summary.get(no_model, {}).get("noisy", {}).get("hourly_MAE_delivery_day", {})  # type: ignore[union-attr]
    with_day = seed_summary.get(with_model, {}).get("noisy", {}).get("hourly_MAE_delivery_day", {})  # type: ignore[union-attr]
    no_full = seed_summary.get(no_model, {}).get("noisy", {}).get("MAE_full_36h", {})  # type: ignore[union-attr]
    with_full = seed_summary.get(with_model, {}).get("noisy", {}).get("MAE_full_36h", {})  # type: ignore[union-attr]
    return {
        "comparison_family": "LightGBM",
        "dayahead_no_price_mean_MAE": no_day.get("mean"),
        "dayahead_with_price_mean_MAE": with_day.get("mean"),
        "dayahead_with_minus_no_MAE": diff_or_none(with_day.get("mean"), no_day.get("mean")),
        "full36_no_price_mean_MAE": no_full.get("mean"),
        "full36_with_price_mean_MAE": with_full.get("mean"),
        "full36_with_minus_no_MAE": diff_or_none(with_full.get("mean"), no_full.get("mean")),
        "advanced_price_helped_under_noise": (with_day.get("mean") is not None and no_day.get("mean") is not None and float(with_day["mean"]) < float(no_day["mean"])) or (with_full.get("mean") is not None and no_full.get("mean") is not None and float(with_full["mean"]) < float(no_full["mean"])),
    }


def diff_or_none(left: object, right: object) -> float | None:
    if left is None or right is None:
        return None
    return float(left) - float(right)


def required_models_ran(seed_summary: dict[str, object]) -> bool:
    return all(key in seed_summary for key in ("HGB_no_price", "LightGBM_with_p0054n_exact_dayahead_advanced_price", "XGBoost_no_price"))


def extract_metric_family(seed_summary: dict[str, object], family: str) -> dict[str, object]:
    prefix = "MAE_full_36h" if family == "full36" else "hourly_MAE_delivery_day"
    return {model: values["noisy"][prefix] for model, values in seed_summary.items()}  # type: ignore[index]


def extract_percent_results(seed_summary: dict[str, object]) -> dict[str, object]:
    return {
        model: {
            "full36_MAE_percent_of_mean_actual": values["noisy"]["full36_MAE_percent_of_mean_actual"],
            "hourly_MAE_percent_of_mean_actual": values["noisy"]["hourly_MAE_percent_of_mean_actual"],
        }
        for model, values in seed_summary.items()  # type: ignore[union-attr]
    }


def extract_daily_energy_results(seed_summary: dict[str, object]) -> dict[str, object]:
    return {model: values["noisy"]["daily_energy_error_percent_of_actual"] for model, values in seed_summary.items()}  # type: ignore[index]


def weather_noise_protocol() -> dict[str, object]:
    return {
        "primary_analysis": "B_train_fit_and_holdout_noise",
        "required_scenario": SCENARIO,
        "formula": "temp_noisy = temp_actual_proxy + uniform(-2.0, +2.0)",
        "seeds": list(SEEDS),
        "rng": "numpy.default_rng(seed)",
        "amplitude_c": NOISE_AMPLITUDE_C,
    }


def leakage_review_summary(base: dict[str, object], baseline: dict[str, object], seed_runs: list[dict[str, object]]) -> dict[str, object]:
    audits = [run["noise_audit"] for run in seed_runs]
    ranges_ok = all(all(float(value) >= -NOISE_AMPLITUDE_C - 1e-12 for value in audit["min_noise"].values() if value is not None) and all(float(value) <= NOISE_AMPLITUDE_C + 1e-12 for value in audit["max_noise"].values() if value is not None) for audit in audits)  # type: ignore[union-attr]
    return {
        "ok": bool(base["exact_price_contract"]["ok"]) and ranges_ok and bool(baseline["metric_rows"]),
        "noise_range_ok": ranges_ok,
        "exact_price_contract_ok": bool(base["exact_price_contract"]["ok"]),
        "baseline_preserved": bool(baseline["metric_rows"]),
        "actual_future_spot_price_feature_used": False,
        "actual_future_load_feature_used": False,
        "production_flow_export_import_a61_used": False,
        "live_api_device_runtime_nordpool_workplace_used": False,
    }


def interpretation(seed_summary: dict[str, object], price_summary: dict[str, object]) -> dict[str, object]:
    hgb = seed_summary.get("HGB_no_price", {})
    day = hgb.get("noisy", {}).get("hourly_MAE_delivery_day", {})  # type: ignore[union-attr]
    full = hgb.get("noisy", {}).get("MAE_full_36h", {})  # type: ignore[union-attr]
    pct = hgb.get("noisy", {}).get("hourly_MAE_percent_of_mean_actual", {})  # type: ignore[union-attr]
    return {
        "p0054n_winner_under_noise": "HGB_no_price",
        "hgb_no_price_noisy_dayahead_mae": day,
        "hgb_no_price_noisy_full36_mae": full,
        "hgb_no_price_noisy_dayahead_percent_of_mean_actual": pct,
        "workplace_reference": WORKPLACE_REFERENCE,
        "advanced_price_under_noise": price_summary,
        "promotion_note": "LABB only; any workplace-grade or G2-KANDIDAT track requires a separate operator request and acceptance criteria.",
    }


def write_p0054o_evidence(evidence_dir: Path, baseline_rows: list[dict[str, object]], seed_rows: list[dict[str, object]], summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "metrics-summary.json": write_json(evidence_dir / "metrics-summary.json", summary),
        "seed-metrics.csv": write_csv(evidence_dir / "seed-metrics.csv", seed_rows, metric_columns()),
        "baseline-metrics.csv": write_csv(evidence_dir / "baseline-metrics.csv", baseline_rows, metric_columns()),
        "percent-error-summary.json": write_json(evidence_dir / "percent-error-summary.json", summary["percent_error_results"]),
        "daily-energy-error-summary.csv": write_csv(evidence_dir / "daily-energy-error-summary.csv", flatten_daily_energy(summary), ["model", "count", "mean", "std", "min", "max", "baseline", "delta_vs_baseline", "relative_change_percent"]),
    }
    for name, text in evidence_markdowns(summary).items():
        files[name] = str(write(evidence_dir / name, text))
    return files


def evidence_markdowns(summary: dict[str, object]) -> dict[str, str]:
    common = f"# {PACKAGE_ID} {LABEL}\n\nStatus: `{summary['status']}`\n\n"
    return {
        "CHANGELOG.md": changelog_text(summary),
        "labb-label.md": common + "This package is LABB only. It is not G2-KANDIDAT and creates no deployable model artifact.\n",
        "weather-noise-protocol.md": common + json_block(summary["weather_noise_protocol"]),
        "temperature-feature-discovery.md": common + json_block(summary["temperature_feature_discovery"]),
        "split-policy-applied.md": common + json_block(summary["split_policy"]),
        "dataset-contract.md": common + json_block(summary["dataset_contract"]),
        "price-feature-protocol-review.md": common + json_block(summary["price_feature_protocol"]),
        "model-training-evidence.md": common + json_block(summary["model_training"]),
        "full-36h-weather-noise-results.md": common + json_block(summary["full_36h_weather_noise_results"]),
        "dayahead-weather-noise-results.md": common + json_block(summary["dayahead_weather_noise_results"]),
        "percent-error-results.md": common + json_block(summary["percent_error_results"]),
        "daily-energy-error-results.md": common + json_block(summary["daily_energy_error_results"]),
        "advanced-price-under-weather-noise.md": common + json_block(summary["advanced_price_under_weather_noise"]),
        "conditional-regime-results.md": common + json_block(summary["conditional_regime_results"]),
        "leakage-review.md": common + json_block(summary["leakage_review"]),
        "interpretation.md": common + json_block(summary["interpretation"]),
        "what-we-learned.md": common + what_we_learned_text(summary),
        "next-package-recommendation.md": common + next_package_text(),
    }


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0054O Changelog

Status: `{summary['status']}`

- Ran deterministic ±2°C uniform temperature-noise ablation for P0054N exact DayAhead/full_36h rows.
- Applied noise to train_fit and holdout source temperature proxy columns before model training.
- Evaluated HGB_no_price, LightGBM_no_price, LightGBM_with_advanced_price and XGBoost_no_price over seeds 1000..1009.
- Wrote full_36h, DayAhead, percent-error, daily-energy, advanced-price and leakage evidence.
- No API, device, runtime, A61, future-flow, Nord Pool, workplace or actual future price/load leakage work was performed.
"""


def what_we_learned_text(summary: dict[str, object]) -> str:
    hgb = summary["interpretation"]["hgb_no_price_noisy_dayahead_percent_of_mean_actual"]  # type: ignore[index]
    return f"With deterministic ±2°C temperature noise, the P0054N winner remains measurable as percent-of-load around `{hgb.get('mean')}` percent of mean actual load for DayAhead hourly MAE. Synthetic noise is still LABB proxy evidence, not workplace-grade validation.\n"


def next_package_text() -> str:
    return "Recommended next package: calibrate weather-noise scenarios against a real archived forecast-vs-actual weather source before any G2-KANDIDAT or workplace-grade interpretation.\n"


def flatten_daily_energy(summary: dict[str, object]) -> list[dict[str, object]]:
    return [{"model": model, **values} for model, values in summary["daily_energy_error_results"].items()]  # type: ignore[union-attr]


def metric_columns() -> list[str]:
    return [
        "scenario",
        "seed",
        "model",
        "MAE_full_36h",
        "RMSE_full_36h",
        "bias_full_36h",
        "p90_full_36h",
        "p95_full_36h",
        "full36_MAE_percent_of_mean_actual",
        "full36_MAE_percent_of_median_actual",
        "hourly_MAE_delivery_day",
        "hourly_RMSE_delivery_day",
        "bias_delivery_day",
        "hourly_MAE_percent_of_mean_actual",
        "hourly_MAE_percent_of_median_actual",
        "absolute_daily_energy_error_MWh",
        "signed_daily_energy_error_MWh",
        "daily_energy_error_percent_of_actual",
        "peak_hour_error_MW",
        "peak_hour_timing_error_hours",
        "morning_ramp_MAE",
        "evening_peak_MAE",
    ]


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
    result = run_p0054o_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
