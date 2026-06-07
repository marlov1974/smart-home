"""P0055B2 LABB SE3 nonlinear monotone settlement-migration redo."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0054k, p0054r, p0055a, p0055b
from src.mac.services.spotprice_model_diagnostics.p0041 import write


PACKAGE_ID = "P0055B2"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0055B2")
NON_ZERO_CLUSTERS = ("C11", "C12", "C13", "C21", "C22", "C31", "C32", "C33", "C42", "C43", "C44")
REFERENCE_WINDOW_MONTHS = 3
EPS = 1e-9


@dataclass(frozen=True)
class P0055B2Result:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0055b2_analysis(*, feature_db: Path | str = DEFAULT_FEATURE_DB, evidence_dir: Path | str = EVIDENCE_DIR) -> P0055B2Result:
    started = time.monotonic()
    feature_db = Path(feature_db).expanduser()
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    aligned_rows = p0055b.load_aligned_decomposition_rows(feature_db)
    monthly_observed = p0055b.monthly_allocation_rows(aligned_rows)
    monotonicity = p0055b.monotonicity_metrics(monthly_observed)
    allocation_model = fit_cluster_specific_monotone_model(monthly_observed)
    normalized_rows, normalization_validation = p0055b.normalize_hourly_components(aligned_rows, allocation_model)
    restamp_generated_package(normalized_rows)
    restamp_generated_package(normalization_validation["rows"])  # type: ignore[index]
    db_counts = p0055b.persist_p0055b_tables(feature_db, allocation_model["monthly_rows"], normalized_rows, normalization_validation["rows"])  # type: ignore[arg-type]

    normalized_components, component_meta = p0055b.build_normalized_component_targets(normalized_rows)
    weather_rows, weather_contract = p0055a.load_climate_zone_weather_rows(feature_db)
    environment = p0054r.capture_environment_status()
    specs = [spec for spec in p0054k.model_specs(environment["imports"]) if spec.family in p0054k.MODEL_FAMILIES]  # type: ignore[arg-type]
    forecast = p0055b.forecast_normalized_components(feature_db, normalized_components, component_meta, weather_rows, specs)
    raw_reference = p0055b.load_raw_reference()
    comparison = p0055b.comparison_summary(raw_reference, forecast["metrics"])
    leakage = validate_p0055b2_leakage(allocation_model, forecast, normalization_validation)
    cluster_review = cluster_specific_review(allocation_model)
    status = classify_status(leakage, normalization_validation, comparison, cluster_review)

    summary = {
        "package_id": PACKAGE_ID,
        "redo_for": "P0055B",
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "input_contract": p0055b.input_contract(aligned_rows, weather_contract),
        "split_policy": p0055a.split_policy(),
        "model_method_contract": p0055a.feature_contract(),
        "settlement_migration_hypothesis": settlement_migration_hypothesis(),
        "monthly_share_analysis": p0055b.monthly_share_analysis(monthly_observed),
        "monotonicity": monotonicity,
        "cluster_specific_review": cluster_review,
        "monthly_delta_analysis": monthly_delta_analysis(allocation_model),
        "nonlinear_monotone_fit_review": nonlinear_monotone_fit_review(allocation_model, cluster_review),
        "reference_allocation_review": reference_allocation_review(allocation_model),
        "allocation_model": allocation_model,
        "normalization_validation": normalization_validation,
        "database_output": db_counts,
        "component_training": forecast["component_training"],
        "component_results": forecast["component_results"],
        "direct_se3_results": forecast["metrics"]["direct_se3"],
        "raw_decomposition_reference": raw_reference,
        "normalized_decomposition_total_results": forecast["metrics"]["normalized_decomposition_total"],
        "reconciled_results": {"metrics": forecast["metrics"]["reconciled_total"], "reconciliation": forecast["reconciliation"]},
        "comparison_vs_direct": comparison,
        "error_contribution": forecast["error_contribution"],
        "leakage_review": leakage,
        "interpretation": interpretation(comparison, cluster_review, normalization_validation),
        "what_we_learned": what_we_learned(comparison, cluster_review),
        "next_package_recommendation": next_package_recommendation(comparison, cluster_review),
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
    evidence = write_p0055b2_evidence(evidence_dir, summary)
    return P0055B2Result(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def fit_cluster_specific_monotone_model(monthly_rows: list[dict[str, object]]) -> dict[str, object]:
    months = sorted({str(row["month_start_utc"]) for row in monthly_rows})
    train_months = [month for month in months if p0054k.p0054i_split(month) == "train_fit"]
    if not train_months:
        raise RuntimeError("P0055B2 requires train_fit monthly allocation rows")
    reference_months = train_months[-REFERENCE_WINDOW_MONTHS:]
    reference_label = f"{reference_months[0]}..{reference_months[-1]}"
    by_component = p0055b.group_rows(monthly_rows, "component_id")
    observed_by_month_component = {
        (str(row["month_start_utc"]), str(row["component_id"])): float(row["observed_share"])
        for row in monthly_rows
    }
    fitted: dict[tuple[str, str], float] = {}
    component_metrics: dict[str, dict[str, object]] = {}
    fit_params: dict[str, dict[str, object]] = {}

    for cluster_id in p0055a.ZERO_COMPONENT_IDS:
        train_pairs = [
            (str(row["month_start_utc"]), float(row["observed_share"]), float(row.get("total_mwh", 1.0) or 1.0))
            for row in sorted(by_component.get(cluster_id, []), key=lambda item: str(item["month_start_utc"]))
            if p0054k.p0054i_split(str(row["month_start_utc"])) == "train_fit"
        ]
        observed_pairs = [(month, share) for month, share, _weight in train_pairs]
        if cluster_id not in NON_ZERO_CLUSTERS:
            fit_values = [0.0 for _row in train_pairs]
            fit_method = "zero_cluster_forced_zero"
        else:
            fit_values = pava_non_decreasing([share for _month, share, _weight in train_pairs], [weight for _month, _share, weight in train_pairs])
            fit_method = "cluster_specific_weighted_pava_non_decreasing_train_fit_only"
        for month, fit_share in zip([month for month, _share, _weight in train_pairs], fit_values):
            fitted[(month, cluster_id)] = max(0.0, fit_share)
        reference = average_month_values(reference_months, cluster_id, observed_by_month_component)
        component_metrics[cluster_id] = {
            **cluster_delta_metrics(observed_pairs),
            "component_id": cluster_id,
            "component_type": "profiled_load_profile_cluster",
            "fit_method": fit_method,
            "fitted_delta_metrics": cluster_delta_metrics([(month, value) for (month, _share, _weight), value in zip(train_pairs, fit_values)]),
            "reference_share_raw": reference,
            "reference_window": reference_label,
            "fit_months": len(train_pairs),
        }
        fit_params[cluster_id] = {"fit_method": fit_method, "fit_data": "train_fit_only", "fit_months": len(train_pairs)}

    reference_shares = {cluster_id: average_month_values(reference_months, cluster_id, observed_by_month_component) for cluster_id in p0055a.ZERO_COMPONENT_IDS}
    for cluster_id in p0055a.ZERO_COMPONENT_IDS:
        if cluster_id not in NON_ZERO_CLUSTERS:
            reference_shares[cluster_id] = 0.0
    reference_total = sum(reference_shares.values())
    if reference_total >= 1.0:
        scale = 0.999999 / reference_total
        reference_shares = {key: value * scale for key, value in reference_shares.items()}
    reference_shares[p0055a.RESIDUAL_COMPONENT] = max(0.0, 1.0 - sum(reference_shares.values()))

    for month in months:
        if p0054k.p0054i_split(month) != "train_fit":
            for cluster_id in p0055a.ZERO_COMPONENT_IDS:
                fitted[(month, cluster_id)] = reference_shares[cluster_id]
            fitted[(month, p0055a.RESIDUAL_COMPONENT)] = reference_shares[p0055a.RESIDUAL_COMPONENT]
            continue
        cluster_sum = 0.0
        for cluster_id in p0055a.ZERO_COMPONENT_IDS:
            value = fitted.get((month, cluster_id), 0.0)
            fitted[(month, cluster_id)] = value
            cluster_sum += value
        if cluster_sum >= 1.0:
            scale = 0.999999 / cluster_sum
            for cluster_id in p0055a.ZERO_COMPONENT_IDS:
                fitted[(month, cluster_id)] *= scale
            cluster_sum = sum(fitted[(month, cluster_id)] for cluster_id in p0055a.ZERO_COMPONENT_IDS)
        fitted[(month, p0055a.RESIDUAL_COMPONENT)] = max(0.0, 1.0 - cluster_sum)

    monthly_model_rows = []
    for row in monthly_rows:
        month = str(row["month_start_utc"])
        component_id = str(row["component_id"])
        monthly_model_rows.append(
            {
                **row,
                "smoothed_share": fitted.get((month, component_id), 0.0),
                "reference_share": reference_shares.get(component_id, 0.0),
                "reference_month_or_window": reference_label,
                "share_slope": None,
                "monotonicity_flags": json.dumps(compact_metric_flags(component_metrics.get(component_id, {})), sort_keys=True),
                "is_forecast_safe_reference": True,
                "generated_by_package": PACKAGE_ID,
            }
        )

    return {
        "method": "cluster_specific_weighted_pava_non_decreasing_reference_latest_stable_train_fit_window",
        "reference_month": reference_label,
        "reference_months": reference_months,
        "reference_window_months": len(reference_months),
        "reference_shares": reference_shares,
        "model_params": fit_params,
        "cluster_metrics": component_metrics,
        "monthly_rows": monthly_model_rows,
        "holdout_months_fit": 0,
        "holdout_used_for_reference": False,
        "holdout_used_for_share_model": False,
        "zero_clusters_forced_zero": [cluster_id for cluster_id in p0055a.ZERO_COMPONENT_IDS if cluster_id not in NON_ZERO_CLUSTERS],
    }


def pava_non_decreasing(values: list[float], weights: list[float] | None = None) -> list[float]:
    if not values:
        return []
    if weights is None:
        weights = [1.0] * len(values)
    blocks = []
    for index, value in enumerate(values):
        block = {"start": index, "end": index, "weight": float(weights[index] or 1.0), "value": float(value)}
        blocks.append(block)
        while len(blocks) >= 2 and blocks[-2]["value"] > blocks[-1]["value"] + EPS:
            right = blocks.pop()
            left = blocks.pop()
            weight = left["weight"] + right["weight"]
            merged = {
                "start": left["start"],
                "end": right["end"],
                "weight": weight,
                "value": (left["value"] * left["weight"] + right["value"] * right["weight"]) / weight,
            }
            blocks.append(merged)
    fitted = [0.0] * len(values)
    for block in blocks:
        for index in range(int(block["start"]), int(block["end"]) + 1):
            fitted[index] = float(block["value"])
    return fitted


def restamp_generated_package(rows: object) -> None:
    for row in rows if isinstance(rows, list) else []:
        if isinstance(row, dict) and "generated_by_package" in row:
            row["generated_by_package"] = PACKAGE_ID


def cluster_delta_metrics(pairs: list[tuple[str, float]]) -> dict[str, object]:
    values = [float(value) for _month, value in pairs]
    deltas = []
    positive = 0.0
    negative = 0.0
    flat = 0
    for (prev_month, prev), (month, cur) in zip(pairs, pairs[1:]):
        delta = cur - prev
        deltas.append({"from_month": prev_month, "to_month": month, "delta": delta})
        if delta > EPS:
            positive += delta
        elif delta < -EPS:
            negative += delta
        else:
            flat += 1
    denom = positive + abs(negative)
    one_way_score = 1.0 if denom <= EPS else positive / denom
    return {
        "monthly_share_start": values[0] if values else None,
        "monthly_share_end": values[-1] if values else None,
        "monthly_delta_series": deltas,
        "positive_delta_sum": positive,
        "negative_delta_sum": negative,
        "max_monthly_positive_delta": max([row["delta"] for row in deltas if row["delta"] > EPS], default=0.0),
        "max_monthly_negative_delta": min([row["delta"] for row in deltas if row["delta"] < -EPS], default=0.0),
        "number_of_negative_delta_months": sum(1 for row in deltas if row["delta"] < -EPS),
        "number_of_zero_or_flat_months": flat,
        "one_way_score": one_way_score,
        "is_monotone_enough": one_way_score >= 0.70 and abs(negative) <= max(positive * 0.50, 0.001),
    }


def average_month_values(months: list[str], component_id: str, values: dict[tuple[str, str], float]) -> float:
    selected = [values.get((month, component_id), 0.0) for month in months]
    return sum(selected) / len(selected) if selected else 0.0


def compact_metric_flags(metrics: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in metrics.items()
        if key not in {"monthly_delta_series", "fitted_delta_metrics"}
    }


def validate_p0055b2_leakage(allocation_model: dict[str, object], forecast: dict[str, object], normalization_validation: dict[str, object]) -> dict[str, object]:
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


def cluster_specific_review(allocation_model: dict[str, object]) -> dict[str, object]:
    metrics = allocation_model["cluster_metrics"]  # type: ignore[index]
    rows = [metrics[cluster_id] for cluster_id in NON_ZERO_CLUSTERS]  # type: ignore[index]
    readable = [row for row in rows if row["is_monotone_enough"]]
    return {
        "required_clusters": list(NON_ZERO_CLUSTERS),
        "required_clusters_evaluated": len(rows),
        "observed_monotone_enough_clusters": [row["component_id"] for row in readable],
        "observed_not_monotone_enough_clusters": [row["component_id"] for row in rows if not row["is_monotone_enough"]],
        "all_required_clusters_evaluated": len(rows) == len(NON_ZERO_CLUSTERS),
        "all_zero_clusters_forced_zero": allocation_model.get("zero_clusters_forced_zero", []),
        "primary_signal_readable": len(readable) == len(rows),
        "cluster_rows": rows,
    }


def monthly_delta_analysis(allocation_model: dict[str, object]) -> dict[str, object]:
    metrics = allocation_model["cluster_metrics"]  # type: ignore[index]
    return {
        "scope": "observed train_fit monthly deltas with fitted monotone deltas attached per cluster",
        "clusters": [metrics[cluster_id] for cluster_id in NON_ZERO_CLUSTERS],  # type: ignore[index]
    }


def nonlinear_monotone_fit_review(allocation_model: dict[str, object], cluster_review: dict[str, object]) -> dict[str, object]:
    return {
        "method": allocation_model["method"],
        "fit_data": "train_fit_only",
        "holdout_used_for_fit": allocation_model["holdout_used_for_share_model"],
        "fit_is_cluster_specific": True,
        "fit_is_nonlinear": True,
        "fit_allows_jumps_and_flats": True,
        "fit_constraint": "non_zero_profiled_clusters fitted non-decreasing by weighted PAVA; zero clusters forced zero; residual is remaining share",
        "observed_primary_signal_readable": cluster_review["primary_signal_readable"],
        "observed_not_monotone_enough_clusters": cluster_review["observed_not_monotone_enough_clusters"],
        "interpretation": "PAVA enforces a diagnostic monotone allocation curve; observed deltas remain the authority for readability.",
    }


def reference_allocation_review(allocation_model: dict[str, object]) -> dict[str, object]:
    reference_shares = allocation_model["reference_shares"]  # type: ignore[index]
    cluster_reference_sum = sum(float(reference_shares[cluster_id]) for cluster_id in p0055a.ZERO_COMPONENT_IDS)  # type: ignore[index]
    return {
        "reference_month_or_window": allocation_model["reference_month"],
        "reference_months": allocation_model["reference_months"],
        "reference_window_months": allocation_model["reference_window_months"],
        "reference_source": "latest stable allocation window inside train_fit",
        "holdout_used_for_reference": allocation_model["holdout_used_for_reference"],
        "holdout_used_for_share_model": allocation_model["holdout_used_for_share_model"],
        "reference_cluster_share_sum": cluster_reference_sum,
        "reference_residual_share": reference_shares[p0055a.RESIDUAL_COMPONENT],  # type: ignore[index]
        "reference_total_share_sum": cluster_reference_sum + float(reference_shares[p0055a.RESIDUAL_COMPONENT]),  # type: ignore[index]
        "is_forecast_safe_reference": True,
    }


def classify_status(leakage: dict[str, object], normalization_validation: dict[str, object], comparison: dict[str, object], cluster_review: dict[str, object]) -> str:
    if not leakage["ok"] or not normalization_validation["ok"] or not cluster_review["all_required_clusters_evaluated"]:
        return "STOP"
    if not cluster_review["primary_signal_readable"]:
        return "WARN"
    if comparison.get("normalized_beats_direct_threshold"):
        return "PASS"
    return "WARN"


def settlement_migration_hypothesis() -> dict[str, object]:
    return {
        "hypothesis": "profiled/load-profile cluster and calculated residual shares include administrative settlement/product migration",
        "expected_direction": "non-zero profiled clusters mostly non-decreasing; residual absorbs remaining share",
        "primary_model": "cluster-specific train-fit-only weighted PAVA monotone share normalization",
        "label": LABEL,
    }


def interpretation(comparison: dict[str, object], cluster_review: dict[str, object], normalization_validation: dict[str, object]) -> dict[str, object]:
    if not normalization_validation["ok"]:
        primary = "normalization_invalid"
    elif not cluster_review["primary_signal_readable"]:
        primary = "cluster_specific_migration_not_safely_readable"
    elif comparison.get("normalized_beats_direct_threshold"):
        primary = "normalized_decomposition_beats_direct"
    elif comparison.get("normalization_improves_raw_decomposition"):
        primary = "normalization_helps_but_direct_remains_default"
    else:
        primary = "normalization_does_not_help_direct_remains_default"
    return {
        "primary_answer": primary,
        "normalization_sum_ok": normalization_validation["ok"],
        "labb_not_g2_candidate": True,
        "weather_proxy_limitation": "P0054Z actual weather is used as actual-as-forecast proxy.",
    }


def what_we_learned(comparison: dict[str, object], cluster_review: dict[str, object]) -> list[str]:
    return [
        f"Required clusters evaluated: {cluster_review['required_clusters_evaluated']}.",
        f"Observed monotone-enough clusters: {cluster_review['observed_monotone_enough_clusters']}.",
        f"Observed not monotone-enough clusters: {cluster_review['observed_not_monotone_enough_clusters']}.",
        f"Normalized decomposition delta vs direct: {comparison.get('normalized_delta_vs_direct_percent')} percent.",
        f"Normalized decomposition delta vs raw decomposition: {comparison.get('normalized_delta_vs_raw_decomposition_percent')} percent.",
    ]


def next_package_recommendation(comparison: dict[str, object], cluster_review: dict[str, object]) -> str:
    if not cluster_review["primary_signal_readable"]:
        return "Do not promote decomposition. Next work should identify better settlement/product metadata or residual substructure before more forecasting."
    if comparison.get("normalized_beats_direct_threshold"):
        return "Stress-test normalized decomposition under stricter forecast-weather realism before any G2-KANDIDAT evaluation."
    return "Keep direct SE3 as default and treat decomposition as LABB diagnostics."


def write_p0055b2_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", "# P0055B2 LABB label\n\nLabel: `LABB`. This is not a G2-KANDIDAT evaluation.\n"),
        "input-source-contract.md": write(evidence_dir / "input-source-contract.md", p0055b.json_report("P0055B2 input source contract", summary["input_contract"])),
        "settlement-migration-hypothesis.md": write(evidence_dir / "settlement-migration-hypothesis.md", p0055b.json_report("P0055B2 settlement migration hypothesis", summary["settlement_migration_hypothesis"])),
        "monthly-share-analysis.md": write(evidence_dir / "monthly-share-analysis.md", p0055b.json_report("P0055B2 monthly share analysis", summary["monthly_share_analysis"])),
        "cluster-specific-migration-rates.md": write(evidence_dir / "cluster-specific-migration-rates.md", p0055b.json_report("P0055B2 cluster-specific migration rates", summary["cluster_specific_review"])),
        "monthly-delta-analysis.md": write(evidence_dir / "monthly-delta-analysis.md", p0055b.json_report("P0055B2 monthly delta analysis", summary["monthly_delta_analysis"])),
        "nonlinear-monotone-fit-review.md": write(evidence_dir / "nonlinear-monotone-fit-review.md", p0055b.json_report("P0055B2 nonlinear monotone fit review", summary["nonlinear_monotone_fit_review"])),
        "reference-allocation-review.md": write(evidence_dir / "reference-allocation-review.md", p0055b.json_report("P0055B2 reference allocation review", summary["reference_allocation_review"])),
        "monotonicity-review.md": write(evidence_dir / "monotonicity-review.md", p0055b.json_report("P0055B2 monotonicity review", summary["monotonicity"])),
        "allocation-normalization-method.md": write(evidence_dir / "allocation-normalization-method.md", p0055b.json_report("P0055B2 allocation normalization method", compact_allocation_model(summary["allocation_model"]))),
        "normalized-series-contract.md": write(evidence_dir / "normalized-series-contract.md", p0055b.json_report("P0055B2 normalized series contract", summary["normalization_validation"])),
        "database-output-evidence.md": write(evidence_dir / "database-output-evidence.md", p0055b.json_report("P0055B2 database output evidence", summary["database_output"])),
        "split-policy-applied.md": write(evidence_dir / "split-policy-applied.md", p0055b.json_report("P0055B2 split policy", summary["split_policy"])),
        "model-method-contract.md": write(evidence_dir / "model-method-contract.md", p0055b.json_report("P0055B2 model method contract", summary["model_method_contract"])),
        "component-training-evidence.md": write(evidence_dir / "component-training-evidence.md", p0055b.json_report("P0055B2 component training evidence", summary["component_training"])),
        "component-results.md": write(evidence_dir / "component-results.md", p0055b.markdown_table("P0055B2 component results", summary["component_results"])),
        "direct-se3-results.md": write(evidence_dir / "direct-se3-results.md", p0055b.json_report("P0055B2 direct SE3 results", summary["direct_se3_results"])),
        "raw-decomposition-reference.md": write(evidence_dir / "raw-decomposition-reference.md", p0055b.json_report("P0055B2 raw decomposition reference", summary["raw_decomposition_reference"])),
        "normalized-decomposition-total-results.md": write(evidence_dir / "normalized-decomposition-total-results.md", p0055b.json_report("P0055B2 normalized decomposition total results", summary["normalized_decomposition_total_results"])),
        "reconciled-results.md": write(evidence_dir / "reconciled-results.md", p0055b.json_report("P0055B2 reconciled results", summary["reconciled_results"])),
        "comparison-vs-direct.md": write(evidence_dir / "comparison-vs-direct.md", p0055b.json_report("P0055B2 comparison vs direct", summary["comparison_vs_direct"])),
        "error-contribution-analysis.md": write(evidence_dir / "error-contribution-analysis.md", p0055b.json_report("P0055B2 error contribution analysis", summary["error_contribution"])),
        "leakage-review.md": write(evidence_dir / "leakage-review.md", p0055b.json_report("P0055B2 leakage review", summary["leakage_review"])),
        "interpretation.md": write(evidence_dir / "interpretation.md", p0055b.json_report("P0055B2 interpretation", summary["interpretation"])),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", "# P0055B2 what we learned\n\n" + "\n".join(f"- {line}" for line in summary["what_we_learned"]) + "\n"),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", "# P0055B2 next package recommendation\n\n" + str(summary["next_package_recommendation"]) + "\n"),
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(p0055b.json_safe(compact_summary(summary)), indent=2, sort_keys=True) + "\n"),
    }
    files["monthly-shares.csv"] = p0055b.write_csv(evidence_dir / "monthly-shares.csv", p0055b.compact_rows(summary["allocation_model"]["monthly_rows"], 250))  # type: ignore[index]
    files["cluster-migration-rates.csv"] = p0055b.write_csv(evidence_dir / "cluster-migration-rates.csv", summary["cluster_specific_review"]["cluster_rows"])  # type: ignore[index]
    files["component-results.csv"] = p0055b.write_csv(evidence_dir / "component-results.csv", summary["component_results"])
    files["total-comparison.csv"] = p0055b.write_csv(evidence_dir / "total-comparison.csv", [summary["comparison_vs_direct"]])
    return files


def compact_allocation_model(model: object) -> dict[str, object]:
    model_dict = dict(model) if isinstance(model, dict) else {}
    monthly_rows = list(model_dict.pop("monthly_rows", [])) if isinstance(model_dict.get("monthly_rows"), list) else []
    model_dict["monthly_row_count"] = len(monthly_rows)
    model_dict["monthly_rows_sample"] = monthly_rows[:20]
    return model_dict


def compact_summary(summary: dict[str, object]) -> dict[str, object]:
    output = dict(summary)
    output["allocation_model"] = compact_allocation_model(summary.get("allocation_model", {}))
    output["monthly_delta_analysis"] = {
        "scope": summary.get("monthly_delta_analysis", {}).get("scope") if isinstance(summary.get("monthly_delta_analysis"), dict) else None,
        "cluster_count": len(summary.get("monthly_delta_analysis", {}).get("clusters", [])) if isinstance(summary.get("monthly_delta_analysis"), dict) else 0,
    }
    return output


def changelog(summary: dict[str, object]) -> str:
    comparison = summary["comparison_vs_direct"]
    return f"""# P0055B2 changelog

Status: `{summary['status']}`

- Rebuilt P0055B as a forward-moving redo under the operator nonlinear monotone clarification.
- Used cluster-specific weighted PAVA monotone train-fit allocation curves and latest stable train-fit reference window.
- Wrote local DB tables for monthly allocation and normalized component series with `generated_by_package = P0055B2`.
- Normalized decomposition delta vs direct DayAhead MAE: `{comparison.get('normalized_delta_vs_direct_percent')}` percent.
- Normalized decomposition delta vs raw decomposition DayAhead MAE: `{comparison.get('normalized_delta_vs_raw_decomposition_percent')}` percent.
- No API, devices, runtime writes, spot-price features, old physical_balance target, flow/A61/capacity features, model binaries or large raw prediction dumps.
"""


def main() -> None:
    result = run_p0055b2_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
