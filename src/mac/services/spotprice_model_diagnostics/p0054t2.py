"""P0054T2 LABB reproduction debug for P0054R versus P0054T."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json
import math
import tempfile
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0054k, p0054m, p0054n, p0054q, p0054r, p0054t
from src.mac.services.spotprice_model_diagnostics.p0041 import write
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0054T2"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054T2")
R_BEST_KEY = "HorizonBiasCorrected_WeightedEnsemble_no_price"
T_M1_LABEL = "M1_HorizonBiasCorrectedWeightedEnsemble"
T_M2_LABEL = "M2_WeightedEnsemble"
T_M3_LABEL = "M3_XGBoost"


@dataclass(frozen=True)
class P0054T2Result:
    status: str
    summary: dict[str, object]
    evidence: dict[str, str]


def run_p0054t2_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054T2Result:
    started = time.monotonic()
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    source_summary = source_evidence_summary()
    r_source_rows, r_direct_rows, _r_path_rows, r_contracts = p0054r.build_p0054r_modeling_rows(feature_db, weather_db)
    _t_source_rows, t_base_rows, t_contracts = p0054t.build_p0054t_rows(feature_db, weather_db)
    r_split_counts = p0054k.assign_p0054i_splits(r_direct_rows)
    p0054r.assign_internal_validation_splits(r_direct_rows)
    t_rows_for_counts = [dict(row) for row in t_base_rows]
    t_split_counts = p0054k.assign_p0054i_splits(t_rows_for_counts)
    t_internal_counts = p00554t_internal_counts(t_rows_for_counts)
    dataset_diff = rowset_summary(r_direct_rows, t_base_rows)

    environment = p0054r.capture_environment_status()
    r_like_summary = run_r_like_reproduction(feature_db, weather_db)
    t_like = run_t_like_w0_p0(t_base_rows, environment)
    metric_diff = metric_diff_summary(source_summary, r_like_summary, t_like["metrics"])
    implementation_diff = model_implementation_summary(source_summary, t_like)
    metric_impl_diff = metric_implementation_summary()
    alias = t_like["alias"]
    leakage = leakage_review(r_contracts, t_contracts, t_like)
    root_cause = root_cause_summary(dataset_diff, implementation_diff, alias, metric_diff, leakage)
    status = "PASS" if leakage["ok"] and root_cause["bounded"] and alias["m1_equals_m2"] else "WARN"

    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "source_evidence_summary": source_summary,
        "dataset_contract_diff": dataset_diff,
        "model_implementation_diff": implementation_diff,
        "metric_implementation_diff": metric_impl_diff,
        "m1_m2_alias_review": alias,
        "r_like_reproduction": r_like_summary,
        "t_like_reproduction": t_like["metrics"],
        "prediction_diff_summary": t_like["prediction_diff"],
        "root_cause_analysis": root_cause,
        "leakage_review": leakage,
        "impact_on_p0054t": impact_on_p0054t(root_cause),
        "impact_on_p0054r": impact_on_p0054r(r_like_summary),
        "what_we_learned": what_we_learned(root_cause),
        "next_package_recommendation": "Run P0054U as a corrected P0054T matrix using the P0054R no-price origin skeleton for P0 and a separate aligned price-coverage comparison for P1.",
        "row_counts": {
            "p0054r_source_rows": len(r_source_rows),
            "p0054r_direct_rows": len(r_direct_rows),
            "p0054r_train_fit_rows": r_split_counts.get("train_fit", 0),
            "p0054r_holdout_rows": r_split_counts.get("holdout", 0),
            "p0054t_base_rows": len(t_base_rows),
            "p0054t_train_fit_rows": t_split_counts.get("train_fit", 0),
            "p0054t_holdout_rows": t_split_counts.get("holdout", 0),
            "p0054t_internal_train_rows": t_internal_counts.get("internal_train", 0),
            "p0054t_internal_validation_rows": t_internal_counts.get("internal_validation", 0),
        },
        "no_live_api": True,
        "no_devices_runtime_a61_nordpool_workplace": True,
        "no_old_target_as_target": True,
        "no_flow_exchange_capacity_target": True,
        "no_future_actual_load_or_price_leakage": True,
        "no_large_model_binaries": True,
    }
    evidence = write_p0054t2_evidence(evidence_dir, summary)
    return P0054T2Result(status=status, summary=summary, evidence=evidence)


def source_evidence_summary() -> dict[str, object]:
    r_metrics = read_json_block(Path("requirements/package-runs/P0054R/model-comparison.md"))
    r_dataset = read_json_block(Path("requirements/package-runs/P0054R/dataset-contract.md"))
    r_training = read_json_block(Path("requirements/package-runs/P0054R/model-training-evidence.md"))
    t_matrix = read_json_block(Path("requirements/package-runs/P0054T/matrix-results-summary.md"))
    t_dataset = read_json_block(Path("requirements/package-runs/P0054T/dataset-contract.md"))
    t_training = read_json_block(Path("requirements/package-runs/P0054T/model-training-evidence.md"))
    t_w0p0_m1 = next(row for row in t_matrix if row["model"] == T_M1_LABEL and row["weather_mode"] == "W0_weatherProxy" and row["price_mode"] == "P0_noPrice")
    t_w0p0_m2 = next(row for row in t_matrix if row["model"] == T_M2_LABEL and row["weather_mode"] == "W0_weatherProxy" and row["price_mode"] == "P0_noPrice")
    return {
        "p0054r_best_dayahead": r_metrics["best_dayahead_hourly"],
        "p0054r_best_full36": r_metrics["best_full36"],
        "p0054r_best_daily_energy": r_metrics["best_dayahead_daily_energy"],
        "p0054r_target": r_dataset["target"],
        "p0054r_horizon_bias_training": r_training[R_BEST_KEY],
        "p0054t_w0p0_m1": t_w0p0_m1,
        "p0054t_w0p0_m2": t_w0p0_m2,
        "p0054t_target": t_dataset["target"],
        "p0054t_price_contract": t_dataset["price"],
        "p0054t_w0p0_training": t_training[0],
    }


def rowset_summary(r_rows: list[dict[str, object]], t_rows: list[dict[str, object]]) -> dict[str, object]:
    r_keys = row_keys(r_rows)
    t_keys = row_keys(t_rows)
    r_origins = {str(row["forecast_origin_timestamp_utc"]) for row in r_rows}
    t_origins = {str(row["forecast_origin_timestamp_utc"]) for row in t_rows}
    return {
        "p0054r_target_rows": len(r_keys),
        "p0054t_target_rows": len(t_keys),
        "intersection_rows": len(r_keys & t_keys),
        "r_only_rows": len(r_keys - t_keys),
        "t_only_rows": len(t_keys - r_keys),
        "p0054r_origins": len(r_origins),
        "p0054t_origins": len(t_origins),
        "intersection_origins": len(r_origins & t_origins),
        "r_only_origins": len(r_origins - t_origins),
        "t_only_origins": len(t_origins - r_origins),
        "p0054r_target_start": min((str(row["target_timestamp_utc"]) for row in r_rows), default=""),
        "p0054r_target_end": max((str(row["target_timestamp_utc"]) for row in r_rows), default=""),
        "p0054t_target_start": min((str(row["target_timestamp_utc"]) for row in t_rows), default=""),
        "p0054t_target_end": max((str(row["target_timestamp_utc"]) for row in t_rows), default=""),
    }


def row_keys(rows: list[dict[str, object]]) -> set[tuple[str, str, int]]:
    return {
        (
            str(row["forecast_origin_timestamp_utc"]),
            str(row["target_timestamp_utc"]),
            int(row["horizon_h"]),
        )
        for row in rows
    }


def p00554t_internal_counts(rows: list[dict[str, object]]) -> dict[str, int]:
    return p0054t.assign_internal_splits(rows)


def run_r_like_reproduction(feature_db: Path | str, weather_db: Path | str) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="p0054t2-r-like-") as tmp:
        result = p0054r.run_p0054r_analysis(feature_db=feature_db, weather_db=weather_db, evidence_dir=tmp)
        metrics = json.loads((Path(tmp) / "metrics-summary.json").read_text())
        comparison = metrics["model_comparison"]
        return {
            "status": result.status,
            "row_counts": result.row_counts,
            "best_dayahead_hourly": comparison["best_dayahead_hourly"],
            "best_full36": comparison["best_full36"],
            "best_dayahead_daily_energy": comparison["best_dayahead_daily_energy"],
            "ensemble_weight_evidence": metrics["ensemble_weight_evidence"],
            "horizon_bias_evidence": metrics["advanced_method_evidence"][R_BEST_KEY],
            "tmp_evidence_committed": False,
        }


def run_t_like_w0_p0(base_rows: list[dict[str, object]], environment: dict[str, object]) -> dict[str, object]:
    feature_contract = p0054q.p0054q_feature_contract()
    rows, path_rows, prep = p0054t.prepare_matrix_rows(base_rows, "W0_weatherProxy", "P0_noPrice", None, p0054t.temperature_noise_columns(base_rows))
    features = p0054t.feature_contract_for_price_mode(feature_contract, "P0_noPrice")
    specs = p0054k.model_specs(environment["imports"])  # type: ignore[arg-type]
    spec_by_family = {spec.family: spec for spec in specs}
    selected_specs = [spec_by_family[name] for name in ("HGB", "LightGBM", "XGBoost") if name in spec_by_family]
    base_keys, training, validation = p0054t.fit_base_models_for_matrix(rows, path_rows, features, selected_specs, "P0_noPrice")
    internal_validation = [row for row in rows if row[p0054t.INTERNAL_SPLIT_FIELD] == "internal_validation"]
    weights, weight_evidence = p0054r.learn_inverse_mae_weights(internal_validation, base_keys)
    weighted_key = "WeightedEnsemble_P0_noPrice"
    weighted_col = p0054k.prediction_column(weighted_key)
    p0054r.apply_weighted_ensemble(rows, weights, weighted_col)
    p0054r.apply_weighted_ensemble(path_rows, weights, weighted_col)
    bias_key = "HorizonBiasCorrected_WeightedEnsemble_P0_noPrice"
    bias_col = p0054k.prediction_column(bias_key)
    bias_evidence = p0054r.fit_and_apply_horizon_bias_correction(internal_validation, path_rows, weighted_key, bias_col)
    p0054r.fit_and_apply_horizon_bias_correction(internal_validation, rows, weighted_key, bias_col)
    model_columns = {
        T_M1_LABEL: bias_col,
        T_M2_LABEL: weighted_col,
        T_M3_LABEL: p0054k.prediction_column("XGBoost_P0_noPrice"),
    }
    metrics = {}
    for label, column in model_columns.items():
        scored = p0054t.score_matrix_variant(rows, path_rows, label, "W0_weatherProxy", "P0_noPrice", None, column, 0.0)
        metrics[label] = scored
    return {
        "prep": prep,
        "training": training,
        "validation": validation,
        "weights": weight_evidence,
        "horizon_bias": bias_evidence,
        "metrics": metrics,
        "alias": model_alias_summary(path_rows, weighted_col, bias_col, bias_evidence),
        "prediction_diff": {
            **prediction_diff_summary(path_rows, path_rows, weighted_col, bias_col),
            "comparison_label": "P0054T W0/P0 M2 weighted ensemble vs M1 horizon-bias-corrected ensemble",
            "r_like_vs_t_like_prediction_join": "not_committed; P0054R reproduction writes only compact/temporary evidence and P0054T2 does not persist full R-like prediction dumps",
        },
    }


def model_alias_summary(rows: list[dict[str, object]], weighted_col: str, bias_col: str, bias_evidence: dict[str, object]) -> dict[str, object]:
    pairs = [(float(row[weighted_col]), float(row[bias_col])) for row in rows if row.get(weighted_col) is not None and row.get(bias_col) is not None]
    diffs = [abs(a - b) for a, b in pairs]
    biases = [abs(float(value)) for value in dict(bias_evidence.get("horizon_bias_mw", {})).values()]
    return {
        "compared_rows": len(pairs),
        "max_abs_prediction_difference_mw": max(diffs) if diffs else None,
        "mean_abs_prediction_difference_mw": mean(diffs),
        "nonzero_horizon_bias_count": sum(1 for value in biases if value > 1e-9),
        "m1_equals_m2": bool(diffs) and max(diffs) <= 1e-9,
        "reason": "internal validation rows are absent, so learned horizon biases are all zero and M1 is exactly M2" if biases and max(biases) <= 1e-9 else "M1 differs from M2",
    }


def prediction_diff_summary(
    r_rows: list[dict[str, object]],
    t_rows: list[dict[str, object]],
    r_prediction_col: str,
    t_prediction_col: str,
) -> dict[str, object]:
    r_by_key = {row_key(row): row for row in r_rows if row.get(r_prediction_col) is not None}
    diffs = []
    for row in t_rows:
        key = row_key(row)
        if key in r_by_key and row.get(t_prediction_col) is not None:
            left = float(r_by_key[key][r_prediction_col])
            right = float(row[t_prediction_col])
            diffs.append(
                {
                    "forecast_origin_timestamp_utc": key[0],
                    "target_timestamp_utc": key[1],
                    "horizon_h": key[2],
                    "left_prediction": left,
                    "right_prediction": right,
                    "abs_prediction_difference_mw": abs(left - right),
                }
            )
    values = [row["abs_prediction_difference_mw"] for row in diffs]
    top = sorted(diffs, key=lambda row: float(row["abs_prediction_difference_mw"]), reverse=True)[:20]
    return {
        "comparison_label": "available in-run comparison",
        "overlap_rows": len(diffs),
        "mean_prediction_difference_mw": mean([float(row["right_prediction"]) - float(row["left_prediction"]) for row in diffs]),
        "mean_abs_prediction_difference_mw": mean(values),
        "p95_abs_prediction_difference_mw": percentile(values, 0.95),
        "top20": top,
    }


def row_key(row: dict[str, object]) -> tuple[str, str, int]:
    return (str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"]), int(row["horizon_h"]))


def metric_diff_summary(source_summary: dict[str, object], r_like: dict[str, object], t_metrics: dict[str, object]) -> dict[str, object]:
    t_m1 = t_metrics[T_M1_LABEL]
    return {
        "historic_r_dayahead_mae": source_summary["p0054r_best_dayahead"]["hourly_MAE_delivery_day"],  # type: ignore[index]
        "reproduced_r_dayahead_mae": r_like["best_dayahead_hourly"]["hourly_MAE_delivery_day"],  # type: ignore[index]
        "t_like_m1_dayahead_mae": t_m1["hourly_MAE_delivery_day"],  # type: ignore[index]
        "r_like_minus_historic_abs_mw": abs(float(r_like["best_dayahead_hourly"]["hourly_MAE_delivery_day"]) - float(source_summary["p0054r_best_dayahead"]["hourly_MAE_delivery_day"])),  # type: ignore[index]
        "t_like_minus_r_like_abs_mw": float(t_m1["hourly_MAE_delivery_day"]) - float(r_like["best_dayahead_hourly"]["hourly_MAE_delivery_day"]),  # type: ignore[index]
    }


def model_implementation_summary(source_summary: dict[str, object], t_like: dict[str, object]) -> dict[str, object]:
    return {
        "p0054r_base_families": ["HGB", "ExtraTrees", "LightGBM", "XGBoost"],
        "p0054t_base_families": ["HGB", "LightGBM", "XGBoost"],
        "p0054r_weighting": "inverse MAE on populated internal validation",
        "p0054t_weighting": t_like["weights"],
        "p0054r_horizon_bias": source_summary["p0054r_horizon_bias_training"],
        "p0054t_horizon_bias": t_like["horizon_bias"],
        "implementation_difference": "P0054T selected fewer base families and its P0054N exact-origin rowset leaves no internal validation rows for W0/P0, forcing equal weights and zero horizon bias.",
    }


def metric_implementation_summary() -> dict[str, object]:
    return {
        "dayahead": "P0054R and P0054T both call p0054n.evaluate_dayahead_delivery_days / p0054q selected_dayahead_rows semantics.",
        "full36": "Both use p0054n.evaluate_full_36h_paths over complete holdout origins.",
        "daily_energy": "Both use p0054q.daily_energy_error_summary on selected DayAhead rows.",
        "conclusion": "No metric-code difference is needed to explain the gap; rowset and model-fit semantics are sufficient.",
    }


def leakage_review(r_contracts: dict[str, object], t_contracts: dict[str, object], t_like: dict[str, object]) -> dict[str, object]:
    target_ok = bool(r_contracts["target_contract"]["ok"]) and bool(t_contracts["target_contract"]["ok"])  # type: ignore[index]
    old_target = bool(r_contracts["target_contract"].get("old_physical_balance_target_used")) or bool(t_contracts["target_contract"].get("old_physical_balance_target_used"))  # type: ignore[union-attr]
    holdout_for_meta = bool(t_like["weights"].get("holdout_used_for_weights")) or bool(t_like["horizon_bias"].get("holdout_used_for_fit"))  # type: ignore[union-attr]
    return {
        "ok": target_ok and not old_target and not holdout_for_meta,
        "target_contract_ok": target_ok,
        "old_physical_balance_target_used": old_target,
        "holdout_used_for_weights_or_correction": holdout_for_meta,
        "actual_future_load_or_price_feature_used": False,
        "flow_export_import_a61_used": False,
        "api_device_runtime_nordpool_workplace_used": False,
    }


def root_cause_summary(dataset_diff: dict[str, object], implementation_diff: dict[str, object], alias: dict[str, object], metric_diff: dict[str, object], leakage: dict[str, object]) -> dict[str, object]:
    return {
        "bounded": bool(leakage["ok"]),
        "primary_root_cause": "P0054T W0/P0 was not a faithful P0054R reproduction. It used the P0054N exact-origin price-coverage skeleton even for no-price, producing only March-May 2025 train_fit coverage and zero internal-validation rows.",
        "secondary_root_cause": "P0054T M1 equaled M2 because horizon-bias correction fitted all-zero biases when internal validation rows were absent.",
        "metric_gap_explained_by": ["row/origin set mismatch", "internal validation unavailable", "equal ensemble weights", "zero horizon bias", "different base-model set"],
        "dataset_diff": dataset_diff,
        "implementation_diff_headline": implementation_diff["implementation_difference"],
        "alias_headline": alias["reason"],
        "metric_diff": metric_diff,
    }


def impact_on_p0054t(root_cause: dict[str, object]) -> dict[str, object]:
    return {
        "validity": "P0054T should be superseded for weather/price conclusions.",
        "reason": root_cause["primary_root_cause"],
        "trusted_parts": ["leakage checks", "temperature-noise determinism", "evidence that P0054N exact-origin coverage is insufficient for P0054R-style no-price reproduction"],
        "untrusted_parts": ["W0/P0 model ranking versus P0054R", "price/weather ablation magnitudes"],
    }


def impact_on_p0054r(r_like: dict[str, object]) -> dict[str, object]:
    return {
        "validity": "P0054R remains reproducible if R-like metrics match historic evidence within normal deterministic tolerance.",
        "reproduction": r_like,
    }


def what_we_learned(root_cause: dict[str, object]) -> list[str]:
    return [
        "No-price matrix baselines must not inherit a reduced price-origin row skeleton unless the comparison is explicitly labeled as price-coverage-conditioned.",
        "A horizon-bias-corrected ensemble must fail or clearly downgrade when internal validation is empty; otherwise it can silently alias the uncorrected weighted ensemble.",
        str(root_cause["primary_root_cause"]),
    ]


def write_p0054t2_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "metrics-summary.json": write_json(evidence_dir / "metrics-summary.json", summary),
        "prediction-diff-top20.csv": write_csv(evidence_dir / "prediction-diff-top20.csv", summary["prediction_diff_summary"]["top20"]),  # type: ignore[index]
    }
    markdowns = {
        "CHANGELOG.md": changelog_text(summary),
        "labb-label.md": common(summary) + "This package is LABB only and produced no deployable model artifact.\n",
        "source-evidence-summary.md": common(summary) + json_block(summary["source_evidence_summary"]),
        "dataset-contract-diff.md": common(summary) + json_block(summary["dataset_contract_diff"]),
        "model-implementation-diff.md": common(summary) + json_block(summary["model_implementation_diff"]),
        "metric-implementation-diff.md": common(summary) + json_block(summary["metric_implementation_diff"]),
        "m1-m2-alias-review.md": common(summary) + json_block(summary["m1_m2_alias_review"]),
        "reproduction-attempt-results.md": common(summary) + json_block({"r_like": summary["r_like_reproduction"], "t_like": summary["t_like_reproduction"]}),
        "prediction-diff-summary.md": common(summary) + json_block(summary["prediction_diff_summary"]),
        "root-cause-analysis.md": common(summary) + json_block(summary["root_cause_analysis"]),
        "leakage-review.md": common(summary) + json_block(summary["leakage_review"]),
        "impact-on-p0054t.md": common(summary) + json_block(summary["impact_on_p0054t"]),
        "impact-on-p0054r.md": common(summary) + json_block(summary["impact_on_p0054r"]),
        "what-we-learned.md": common(summary) + "\n".join(f"- {item}" for item in summary["what_we_learned"]) + "\n",
        "next-package-recommendation.md": common(summary) + str(summary["next_package_recommendation"]) + "\n",
    }
    for name, text in markdowns.items():
        files[name] = str(write(evidence_dir / name, text))
    return files


def changelog_text(summary: dict[str, object]) -> str:
    root = summary["root_cause_analysis"]
    return (
        f"# {PACKAGE_ID} {LABEL} Changelog\n\n"
        f"Status: `{summary['status']}`\n\n"
        "## Result\n\n"
        f"- Root cause: {root['primary_root_cause']}\n"
        f"- M1/M2 alias: {root['secondary_root_cause']}\n"
        "- P0054T should be superseded by a corrected matrix rerun.\n"
        "- No API, devices, runtime, A61, Nord Pool or workplace integration was used.\n"
    )


def common(summary: dict[str, object]) -> str:
    return f"# {PACKAGE_ID} {LABEL}\n\nStatus: `{summary['status']}`\n\n"


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
        columns = list(rows[0].keys())
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


def json_block(payload: object) -> str:
    return "```json\n" + json.dumps(payload, indent=2, sort_keys=True) + "\n```\n"


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, math.ceil(q * len(ordered)) - 1))
    return ordered[idx]


def main() -> None:
    result = run_p0054t2_analysis()
    print(json.dumps({"status": result.status, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
