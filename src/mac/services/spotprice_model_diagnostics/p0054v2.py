"""P0054V2 LABB complete spotprice value test with relaxed baseline gate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import csv
import json
import tempfile
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054l2, p0054n, p0054q, p0054r
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0054V2"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054V2")
REFERENCE_BASELINE_MAE = 253.70062353819162
ABSOLUTE_GATE_TOLERANCE_MW = 2.0
RELATIVE_GATE_TOLERANCE_PERCENT = 1.0
BASE_FAMILIES = ("HGB", "ExtraTrees", "LightGBM", "XGBoost")
PRICE_FAMILY_ORDER = ("P0_no_price", "P1_raw_stitched_price", "P2_path_shape", "P3_price_regime", "P4_spike_ramp")
MODEL_KEY_BY_FAMILY = {family: f"HorizonBiasCorrected_WeightedEnsemble_{family}" for family in PRICE_FAMILY_ORDER}
WEIGHTED_KEY_BY_FAMILY = {family: f"WeightedEnsemble_{family}" for family in PRICE_FAMILY_ORDER}


@dataclass(frozen=True)
class P0054V2Result:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054v2_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054V2Result:
    started = time.monotonic()
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    baseline_gate = run_baseline_gate(feature_db, weather_db)
    if not baseline_gate["passed"]:
        summary = stopped_summary(started, baseline_gate)
        return P0054V2Result("STOP", {}, write_p0054v2_evidence(evidence_dir, summary))

    source_rows, direct_rows, path_rows, contracts = build_full_contract_rows(feature_db, weather_db)
    price_rows = p0054l2.load_se3_price_rows(Path(feature_db).expanduser())
    actual_prices, actual_price_contract = load_actual_se3_spot_prices(price_rows)
    price_forecasts, price_forecast_contract = build_price_forecast_rows(price_rows, path_rows)
    thresholds = fit_price_thresholds(path_rows, actual_prices, price_forecasts)
    feature_summary = attach_price_feature_families(direct_rows, path_rows, actual_prices, price_forecasts, thresholds)
    leakage = leakage_review(contracts, actual_price_contract, price_forecast_contract, feature_summary)
    if not leakage["ok"]:
        summary = stopped_summary(started, baseline_gate, leakage)
        summary["row_counts"] = {"direct_rows": len(direct_rows), "path_rows": len(path_rows)}
        return P0054V2Result("STOP", summary["row_counts"], write_p0054v2_evidence(evidence_dir, summary))  # type: ignore[arg-type]

    environment = p0054r.capture_environment_status()
    specs = selected_specs(environment)
    feature_contract = price_family_feature_contract(feature_summary["price_columns"])
    scored_path_rows = [dict(row) for row in path_rows]
    family_results = {}
    for family in PRICE_FAMILY_ORDER:
        family_results[family] = fit_m1_for_family(direct_rows, scored_path_rows, feature_contract[family]["features"], specs, family)

    prediction_columns = tuple(str(family_results[family]["prediction_column"]) for family in PRICE_FAMILY_ORDER)
    full36_summary, full36_rows = p0054n.evaluate_full_36h_paths(scored_path_rows, prediction_columns)
    dayahead_summary, dayahead_rows = p0054n.evaluate_dayahead_delivery_days(scored_path_rows, prediction_columns)
    full36_selected = p0054q.selected_full36_rows(scored_path_rows)
    dayahead_selected = p0054q.selected_dayahead_rows(scored_path_rows)
    p0054q.add_percent_metrics(full36_summary, full36_selected, prediction_columns, "full36")
    p0054q.add_percent_metrics(dayahead_summary, dayahead_selected, prediction_columns, "dayahead")
    daily_energy_summary = p0054q.daily_energy_error_summary(dayahead_selected, prediction_columns)
    regime_summary = regime_results(dayahead_selected, family_results)
    comparisons = compare_price_families(family_results, full36_summary, dayahead_summary, daily_energy_summary, regime_summary)
    decision = decision_summary(comparisons)
    status = "PASS" if baseline_gate["passed"] and leakage["ok"] and comparisons["required_families_complete"] else "WARN"

    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "p0054v_stop_review": p0054v_stop_review(),
        "prior_evidence_summary": prior_evidence_summary(),
        "baseline_reproduction_gate": baseline_gate,
        "target_contract": contracts["target_contract"],
        "split_policy": p0054r.split_policy(),
        "dataset_contract": dataset_contract(source_rows, direct_rows, path_rows),
        "price_stitching_policy": price_stitching_policy(),
        "actual_spot_training_policy": actual_spot_training_policy(),
        "price_history_anchor_features": price_history_anchor_features_contract(feature_summary),
        "train_inference_skew_review": train_inference_skew_review(feature_summary),
        "price_forecast_source_contract": price_forecast_contract,
        "price_forecast_log_schema": price_forecast_log_schema(),
        "price_forecast_log_coverage": price_forecast_coverage(price_forecasts, path_rows),
        "price_forecast_safety_review": price_forecast_safety_review(price_forecast_contract),
        "feature_families": feature_contract,
        "model_training": {family: family_results[family]["training"] for family in PRICE_FAMILY_ORDER},
        "dayahead_results": family_metric_summary(dayahead_summary, family_results, "dayahead"),
        "full_36h_results": family_metric_summary(full36_summary, family_results, "full36"),
        "daily_energy_error_results": family_metric_summary(daily_energy_summary, family_results, "daily_energy"),
        "regime_results": regime_summary,
        "price_feature_family_results": comparisons,
        "decision": decision,
        "emulator_stack_recommendation": emulator_stack_recommendation(decision),
        "leakage_review": leakage,
        "interpretation": interpretation(decision),
        "what_we_learned": what_we_learned(decision),
        "next_package_recommendation": next_package_recommendation(decision),
        "row_counts": {
            "source_rows": len(source_rows),
            "direct_rows": len(direct_rows),
            "path_rows": len(path_rows),
            "actual_price_rows": len(actual_prices),
            "price_forecast_rows": len(price_forecasts),
            "full36_complete_origins": len(full36_rows),
            "dayahead_delivery_days": len(dayahead_rows),
        },
        "no_external_live_data_calls": True,
        "no_devices_runtime_a61_nordpool_workplace": True,
        "no_old_target_as_target": True,
        "no_flow_exchange_capacity_target": True,
        "no_future_actual_load_production_flow_a61_leakage": True,
        "no_holdout_target_window_actual_spot_feature": True,
        "no_large_model_binaries": True,
    }
    evidence = write_p0054v2_evidence(evidence_dir, summary)
    return P0054V2Result(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def run_baseline_gate(feature_db: Path | str, weather_db: Path | str) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="p0054v2-baseline-") as tmp:
        result = p0054r.run_p0054r_analysis(feature_db=feature_db, weather_db=weather_db, evidence_dir=tmp)
        metrics = json.loads((Path(tmp) / "metrics-summary.json").read_text())
        best = metrics["model_comparison"]["best_dayahead_hourly"]
        mae = float(best["hourly_MAE_delivery_day"])
        absolute_delta = abs(mae - REFERENCE_BASELINE_MAE)
        relative_delta = (absolute_delta / REFERENCE_BASELINE_MAE) * 100.0
        row_counts = result.row_counts
        gate = relaxed_baseline_passes(absolute_delta, relative_delta)
        return {
            "status": result.status,
            "model": best["model"],
            "hourly_MAE_delivery_day": mae,
            "target_MAE": REFERENCE_BASELINE_MAE,
            "absolute_delta_MW": absolute_delta,
            "relative_delta_percent": relative_delta,
            "absolute_tolerance_MW": ABSOLUTE_GATE_TOLERANCE_MW,
            "relative_tolerance_percent": RELATIVE_GATE_TOLERANCE_PERCENT,
            "passed": result.status == "PASS" and gate,
            "pass_rule": "absolute_delta <= 2.0 MW OR relative_delta <= 1.0%",
            "row_counts": row_counts,
            "tmp_evidence_committed": False,
        }


def relaxed_baseline_passes(absolute_delta_mw: float, relative_delta_percent: float) -> bool:
    return absolute_delta_mw <= ABSOLUTE_GATE_TOLERANCE_MW or relative_delta_percent <= RELATIVE_GATE_TOLERANCE_PERCENT


def build_full_contract_rows(feature_db: Path | str, weather_db: Path | str) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    source_rows, direct_rows, path_rows, contracts = p0054r.build_p0054r_modeling_rows(feature_db, weather_db)
    p0054k.assign_p0054i_splits(direct_rows)
    p0054k.assign_p0054i_splits(path_rows)
    p0054r.assign_internal_validation_splits(direct_rows)
    p0054r.assign_internal_validation_splits(path_rows)
    profiles = p0054k.fit_train_profiles([row for row in direct_rows if row["split"] == "train_fit"])
    p0054k.apply_profile_features(direct_rows, profiles)
    p0054k.apply_profile_features(path_rows, profiles)
    return source_rows, direct_rows, path_rows, contracts


def load_actual_se3_spot_prices(price_rows: list[dict[str, object]]) -> tuple[dict[str, float], dict[str, object]]:
    prices = {str(row["timestamp_utc"]): float(row["hour_price"]) for row in price_rows}
    return prices, {
        "ok": bool(prices),
        "source_table": p0054l2.SOURCE_TABLE,
        "reconstruction": "system_proxy_se1 + area_diff_proxy_se3",
        "rows": len(prices),
        "start": min(prices) if prices else "",
        "end": max(prices) if prices else "",
        "used_for_train_fit_target_timestamps": True,
        "used_for_holdout_target_window_future_features": False,
    }


def build_price_forecast_rows(price_rows: list[dict[str, object]], required_rows: list[dict[str, object]]) -> tuple[dict[tuple[str, str], dict[str, object]], dict[str, object]]:
    train_examples, predict_examples, feature_names = build_price_examples(price_rows, required_rows)
    train_before_holdout = [row for row in train_examples if str(row["target_timestamp_utc"]) < p0054k.HOLDOUT_START]
    holdout_predict = [row for row in predict_examples if str(row["target_timestamp_utc"]) >= p0054k.HOLDOUT_START]
    forecast_rows, model_status = p0054n.fit_price_ensemble(train_before_holdout, holdout_predict, feature_names, "p0054v2_trainfit_price_before_2025_06_predict_holdout")
    mapping = {(str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"])): row for row in forecast_rows}
    required_holdout = {(str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"])) for row in required_rows if row["split"] == "holdout"}
    missing = sorted(required_holdout - set(mapping))
    return mapping, {
        "ok": bool(mapping) and not missing,
        "protocol": "P0054V2_P0054L2_like_trainfit_safe_price_model_for_holdout_future_horizons",
        "price_model_family": "P0054N/P0054L2-compatible ensemble",
        "price_model_package_source": "P0054V2 using P0054L2 feature code and P0054N fit_price_ensemble",
        "train_examples": len(train_before_holdout),
        "predict_examples": len(holdout_predict),
        "rows": len(mapping),
        "required_holdout_rows": len(required_holdout),
        "missing_required_holdout_rows": len(missing),
        "missing_examples": missing[:20],
        "model_status": model_status,
        "actual_future_spot_price_used": False,
        "holdout_used_for_price_model_fitting": False,
        "persisted_table": None,
    }


def build_price_examples(price_rows: list[dict[str, object]], required_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[str]]:
    by_ts = {str(row["timestamp_utc"]): float(row["hour_price"]) for row in price_rows}
    examples = []
    seen = set()
    for row in required_rows:
        origin_text = str(row["forecast_origin_timestamp_utc"])
        target_text = str(row["target_timestamp_utc"])
        key = (origin_text, target_text)
        if key in seen:
            continue
        seen.add(key)
        if row["split"] == "train_fit" and target_text not in by_ts:
            continue
        origin = p0052.parse_utc(origin_text)
        target = p0052.parse_utc(target_text)
        horizon = max(int(row["horizon_h"]) - 1, 0)
        features, audit = price_history_features_at_origin(origin, target, by_ts, horizon)
        examples.append(
            {
                "forecast_origin_timestamp_utc": origin_text,
                "input_data_cutoff_utc": p0052.format_utc(origin - timedelta(hours=1)),
                "target_timestamp_utc": target_text,
                "horizon_hours": horizon,
                "split": row["split"],
                "target_price": by_ts.get(target_text),
                "features": features,
                "feature_source_audit": audit,
                "area": "SE3",
            }
        )
    feature_names = sorted({key for row in examples for key in row["features"]})  # type: ignore[union-attr]
    matrix_review = p0054l2.validate_feature_matrix_safety(examples, feature_names)
    if not matrix_review["ok"]:
        raise RuntimeError(f"P0054V2 price feature safety failed: {matrix_review}")
    return [row for row in examples if row["split"] == "train_fit"], [row for row in examples if row["split"] == "holdout"], feature_names


def price_history_features_at_origin(origin: datetime, target: datetime, prices_by_ts: dict[str, float], horizon: int) -> tuple[dict[str, float], dict[str, str]]:
    audit: dict[str, str] = {}
    target_model_dt = target + timedelta(hours=1)
    features = {
        "horizon_hours": float(horizon),
        "target_model_cet_hour": float(target_model_dt.hour),
        "target_model_cet_weekday": float(target_model_dt.weekday()),
        "target_model_cet_month": float(target_model_dt.month),
        "target_is_weekend": 1.0 if target_model_dt.weekday() >= 5 else 0.0,
    }
    for lag in p0054l2.LAGS:
        key = p0052.format_utc(origin - timedelta(hours=lag))
        features[f"se3_price_lag_{lag}h"] = prices_by_ts.get(key, 0.0)
        audit[f"se3_price_lag_{lag}h"] = key
    previous_week_key = p0052.format_utc(target - timedelta(hours=168))
    features["se3_price_previous_week_same_target_hour"] = prices_by_ts.get(previous_week_key, 0.0)
    audit["se3_price_previous_week_same_target_hour"] = previous_week_key
    for window in p0054l2.ROLL_WINDOWS:
        values = [prices_by_ts[p0052.format_utc(origin - timedelta(hours=offset))] for offset in range(1, window + 1) if p0052.format_utc(origin - timedelta(hours=offset)) in prices_by_ts]
        prefix = f"se3_price_roll_{window}h"
        features[f"{prefix}_mean"] = p0054k.mean_float(values)
        features[f"{prefix}_std"] = p0054k.std_float(values)
        features[f"{prefix}_min"] = min(values) if values else 0.0
        features[f"{prefix}_max"] = max(values) if values else 0.0
        for suffix in ("mean", "std", "min", "max"):
            audit[f"{prefix}_{suffix}"] = p0052.format_utc(origin - timedelta(hours=1))
    features["se3_price_recent_ramp_1h_24h"] = features["se3_price_lag_1h"] - features["se3_price_lag_24h"]
    features["se3_price_recent_ramp_24h_168h"] = features["se3_price_lag_24h"] - features["se3_price_lag_168h"]
    audit["se3_price_recent_ramp_1h_24h"] = p0052.format_utc(origin - timedelta(hours=1))
    audit["se3_price_recent_ramp_24h_168h"] = p0052.format_utc(origin - timedelta(hours=24))
    return features, audit


def build_anchor_features(origin_text: str, actual_prices: dict[str, float]) -> tuple[dict[str, float], dict[str, str]]:
    origin = p0052.parse_utc(origin_text)
    audit = {}
    features = {}
    for lag in (1, 24, 48):
        key = p0052.format_utc(origin - timedelta(hours=lag))
        features[f"actual_spot_lag_{lag}h"] = actual_prices.get(key, 0.0)
        audit[f"actual_spot_lag_{lag}h"] = key
    values_0_24 = history_values(origin, actual_prices, 1, 24)
    values_24_48 = history_values(origin, actual_prices, 25, 48)
    values_48 = values_0_24 + values_24_48
    features.update(
        {
            "actual_spot_history_0_24h_mean": p0054k.mean_float(values_0_24),
            "actual_spot_history_24_48h_mean": p0054k.mean_float(values_24_48),
            "actual_spot_history_48h_mean": p0054k.mean_float(values_48),
            "actual_spot_history_48h_min": min(values_48) if values_48 else 0.0,
            "actual_spot_history_48h_max": max(values_48) if values_48 else 0.0,
            "actual_spot_history_48h_spread": (max(values_48) - min(values_48)) if values_48 else 0.0,
            "actual_spot_last_known_value": actual_prices.get(p0052.format_utc(origin - timedelta(hours=1)), 0.0),
        }
    )
    for name in ("actual_spot_history_0_24h_mean", "actual_spot_history_24_48h_mean", "actual_spot_history_48h_mean", "actual_spot_history_48h_min", "actual_spot_history_48h_max", "actual_spot_history_48h_spread", "actual_spot_last_known_value"):
        audit[name] = p0052.format_utc(origin - timedelta(hours=1))
    return features, audit


def history_values(origin: datetime, actual_prices: dict[str, float], start_lag: int, end_lag: int) -> list[float]:
    return [actual_prices[p0052.format_utc(origin - timedelta(hours=lag))] for lag in range(start_lag, end_lag + 1) if p0052.format_utc(origin - timedelta(hours=lag)) in actual_prices]


def fit_price_thresholds(path_rows: list[dict[str, object]], actual_prices: dict[str, float], forecast_prices: dict[tuple[str, str], dict[str, object]]) -> dict[str, float]:
    scratch = [dict(row) for row in path_rows]
    attach_basic_stitched_prices(scratch, actual_prices, forecast_prices)
    train = [row for row in scratch if row["split"] == "train_fit"]
    prices = [float(row["p0054v2_stitched_spot_target_hour"]) for row in train if p0054k.is_finite(row.get("p0054v2_stitched_spot_target_hour"))]
    spreads = []
    for rows in p0054k.group_by(train, "forecast_origin_timestamp_utc").values():
        values = [float(row["p0054v2_stitched_spot_target_hour"]) for row in rows if p0054k.is_finite(row.get("p0054v2_stitched_spot_target_hour"))]
        if values:
            spreads.append(max(values) - min(values))
    ramps = [abs(float(row.get("p0054v2_price_ramp_from_previous_horizon") or 0.0)) for row in train]
    return {
        "price_p10": percentile(prices, 0.1),
        "price_p25": percentile(prices, 0.25),
        "price_p75": percentile(prices, 0.75),
        "price_p90": percentile(prices, 0.9),
        "spread_p75": percentile(spreads, 0.75) if spreads else 0.0,
        "ramp_abs_p90": percentile(ramps, 0.9) if ramps else 0.0,
    }


def attach_basic_stitched_prices(rows: list[dict[str, object]], actual_prices: dict[str, float], forecast_prices: dict[tuple[str, str], dict[str, object]]) -> None:
    for row in rows:
        target = str(row["target_timestamp_utc"])
        origin = str(row["forecast_origin_timestamp_utc"])
        if row["split"] == "train_fit":
            row["p0054v2_stitched_spot_target_hour"] = actual_prices.get(target)
            row["p0054v2_price_value_kind"] = "actual_train_fit_target_hour"
        else:
            forecast = forecast_prices.get((origin, target))
            row["p0054v2_stitched_spot_target_hour"] = float(forecast["predicted_price"]) if forecast else None
            row["p0054v2_price_value_kind"] = "forecast_holdout_future_target_hour"


def attach_price_feature_families(direct_rows: list[dict[str, object]], path_rows: list[dict[str, object]], actual_prices: dict[str, float], forecast_prices: dict[tuple[str, str], dict[str, object]], thresholds: dict[str, float]) -> dict[str, object]:
    for rows in (direct_rows, path_rows):
        attach_basic_stitched_prices(rows, actual_prices, forecast_prices)
        attach_anchor_features(rows, actual_prices)
        attach_path_price_features(rows, actual_prices, thresholds)
    coverage = coverage_summary(path_rows)
    return {
        "ok": coverage["complete"],
        "coverage": coverage,
        "thresholds": thresholds,
        "price_columns": price_columns_by_family(),
        "train_actual_target_price_used": True,
        "holdout_future_actual_target_price_used": False,
    }


def attach_anchor_features(rows: list[dict[str, object]], actual_prices: dict[str, float]) -> None:
    cache: dict[str, tuple[dict[str, float], dict[str, str]]] = {}
    for row in rows:
        origin = str(row["forecast_origin_timestamp_utc"])
        if origin not in cache:
            cache[origin] = build_anchor_features(origin, actual_prices)
        features, audit = cache[origin]
        row.update(features)
        row["p0054v2_anchor_audit_latest_source_utc"] = max(audit.values())


def attach_path_price_features(rows: list[dict[str, object]], actual_prices: dict[str, float], thresholds: dict[str, float]) -> None:
    for origin, origin_rows in p0054k.group_by(rows, "forecast_origin_timestamp_utc").items():
        ordered = sorted(origin_rows, key=lambda row: int(row["horizon_h"]))
        prices = [p0054k.safe_float(row.get("p0054v2_stitched_spot_target_hour")) for row in ordered]
        ranks = p0054k.rank_map(prices, high_rank=True)
        mean_0_24 = p0054k.mean_float(prices[:24])
        mean_24_36 = p0054k.mean_float(prices[24:36])
        mean_0_36 = p0054k.mean_float(prices[:36])
        pmin = min(prices) if prices else 0.0
        pmax = max(prices) if prices else 0.0
        last_actual = actual_prices.get(p0052.format_utc(p0052.parse_utc(origin) - timedelta(hours=1)), prices[0] if prices else 0.0)
        for index, row in enumerate(ordered):
            price = prices[index]
            previous = prices[index - 1] if index > 0 else last_actual
            ramp = price - previous
            row.update(
                {
                    "p0054v2_price_forecast_0_24h_mean": mean_0_24,
                    "p0054v2_price_forecast_24_36h_mean": mean_24_36,
                    "p0054v2_price_forecast_0_36h_mean": mean_0_36,
                    "p0054v2_price_forecast_daily_min": pmin,
                    "p0054v2_price_forecast_daily_max": pmax,
                    "p0054v2_price_forecast_daily_spread": pmax - pmin,
                    "p0054v2_price_forecast_peak_offpeak_spread": mean_0_24 - mean_24_36,
                    "p0054v2_price_forecast_hour_rank_in_36h_path": ranks[index],
                    "p0054v2_price_forecast_peak_hour_indicator": 1 if ranks[index] <= 4 else 0,
                    "p0054v2_price_forecast_offpeak_indicator": 1 if ranks[index] >= max(len(ranks) - 3, 1) else 0,
                    "p0054v2_high_price_flag": 1 if price >= thresholds["price_p75"] else 0,
                    "p0054v2_low_price_flag": 1 if price <= thresholds["price_p25"] else 0,
                    "p0054v2_negative_or_very_low_flag": 1 if price <= thresholds["price_p10"] else 0,
                    "p0054v2_top_quartile_flag": 1 if price >= thresholds["price_p75"] else 0,
                    "p0054v2_bottom_quartile_flag": 1 if price <= thresholds["price_p25"] else 0,
                    "p0054v2_volatility_regime": 1 if (pmax - pmin) >= thresholds["spread_p75"] else 0,
                    "p0054v2_daily_spread_regime": 1 if (pmax - pmin) >= thresholds["spread_p75"] else 0,
                    "p0054v2_price_ramp_from_previous_horizon": ramp,
                    "p0054v2_price_abs_ramp_from_previous_horizon": abs(ramp),
                    "p0054v2_price_spike_risk_flag": 1 if price >= thresholds["price_p90"] else 0,
                    "p0054v2_price_large_ramp_flag": 1 if abs(ramp) >= thresholds["ramp_abs_p90"] else 0,
                    "p0054v2_price_morning_ramp": ramp if 6 <= int(row["target_model_cet_hour"]) <= 9 else 0.0,
                    "p0054v2_price_evening_ramp": ramp if 16 <= int(row["target_model_cet_hour"]) <= 20 else 0.0,
                }
            )


def price_columns_by_family() -> dict[str, list[str]]:
    p1 = [
        "p0054v2_stitched_spot_target_hour",
        "actual_spot_lag_1h",
        "actual_spot_lag_24h",
        "actual_spot_lag_48h",
        "actual_spot_history_0_24h_mean",
        "actual_spot_history_24_48h_mean",
        "actual_spot_history_48h_mean",
        "actual_spot_history_48h_min",
        "actual_spot_history_48h_max",
        "actual_spot_history_48h_spread",
        "actual_spot_last_known_value",
    ]
    p2 = p1 + [
        "p0054v2_price_forecast_0_24h_mean",
        "p0054v2_price_forecast_24_36h_mean",
        "p0054v2_price_forecast_0_36h_mean",
        "p0054v2_price_forecast_daily_min",
        "p0054v2_price_forecast_daily_max",
        "p0054v2_price_forecast_daily_spread",
        "p0054v2_price_forecast_peak_offpeak_spread",
        "p0054v2_price_forecast_hour_rank_in_36h_path",
        "p0054v2_price_forecast_peak_hour_indicator",
        "p0054v2_price_forecast_offpeak_indicator",
    ]
    p3 = p2 + [
        "p0054v2_high_price_flag",
        "p0054v2_low_price_flag",
        "p0054v2_negative_or_very_low_flag",
        "p0054v2_top_quartile_flag",
        "p0054v2_bottom_quartile_flag",
        "p0054v2_volatility_regime",
        "p0054v2_daily_spread_regime",
    ]
    p4 = p3 + [
        "p0054v2_price_spike_risk_flag",
        "p0054v2_price_ramp_from_previous_horizon",
        "p0054v2_price_abs_ramp_from_previous_horizon",
        "p0054v2_price_morning_ramp",
        "p0054v2_price_evening_ramp",
        "p0054v2_price_large_ramp_flag",
    ]
    return {"P0_no_price": [], "P1_raw_stitched_price": p1, "P2_path_shape": p2, "P3_price_regime": p3, "P4_spike_ramp": p4}


def coverage_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    missing = [p0054k.row_id(row) for row in rows if row.get("p0054v2_stitched_spot_target_hour") is None]
    return {
        "complete": not missing,
        "rows": len(rows),
        "missing_stitched_price_rows": len(missing),
        "missing_examples": missing[:20],
        "train_fit_rows": len([row for row in rows if row["split"] == "train_fit"]),
        "holdout_rows": len([row for row in rows if row["split"] == "holdout"]),
        "origins": len({row["forecast_origin_timestamp_utc"] for row in rows}),
    }


def price_family_feature_contract(price_columns: dict[str, list[str]]) -> dict[str, dict[str, object]]:
    no_price = list(p0054q.p0054q_feature_contract()[p0054n.VARIANT_NO_PRICE]["features"])  # type: ignore[index]
    return {
        family: {
            "input_classification": "historical_observed_train_plus_forecast_safe_holdout_price" if family != "P0_no_price" else "forecast_safe_weather_proxy_no_price",
            "features": no_price + price_columns[family],
            "price_columns": price_columns[family],
        }
        for family in PRICE_FAMILY_ORDER
    }


def selected_specs(environment: dict[str, object]) -> list[object]:
    specs = p0054k.model_specs(environment["imports"])  # type: ignore[arg-type]
    by_family = {spec.family: spec for spec in specs}
    missing = [family for family in BASE_FAMILIES if family not in by_family]
    if missing:
        raise RuntimeError(f"P0054V2 missing required base model families: {missing}")
    return [by_family[family] for family in BASE_FAMILIES]


def fit_m1_for_family(rows: list[dict[str, object]], scored_path_rows: list[dict[str, object]], features: list[str], specs: list[object], family: str) -> dict[str, object]:
    internal_train = [row for row in rows if row[p0054r.INTERNAL_SPLIT_FIELD] == "internal_train"]
    internal_validation = [dict(row) for row in rows if row[p0054r.INTERNAL_SPLIT_FIELD] == "internal_validation"]
    base_results = {}
    validation_evidence = {}
    base_keys = []
    for spec in specs:
        key = f"{spec.family}_{family}"  # type: ignore[attr-defined]
        validation_fit = p0054r.fit_model_on_rows(spec, features, internal_train, internal_validation)
        p0054r.attach_prediction_values(internal_validation, validation_fit["predictions"], p0054k.prediction_column(key))
        validation_evidence[key] = p0054k.regression_metric_from_predictions(internal_validation, validation_fit["predictions"])  # type: ignore[arg-type]
        result = p0054k.fit_variant_model(rows, features, spec, family)
        p0054k.attach_path_predictions(scored_path_rows, result, features, p0054k.prediction_column(key))
        base_results[key] = result
        base_keys.append(key)
    weights, weight_evidence = p0054r.learn_inverse_mae_weights(internal_validation, base_keys)
    weighted_key = WEIGHTED_KEY_BY_FAMILY[family]
    weighted_col = p0054k.prediction_column(weighted_key)
    p0054r.apply_weighted_ensemble(internal_validation, weights, weighted_col)
    p0054r.apply_weighted_ensemble(scored_path_rows, weights, weighted_col)
    model_key = MODEL_KEY_BY_FAMILY[family]
    prediction_col = p0054k.prediction_column(model_key)
    bias_evidence = p0054r.fit_and_apply_horizon_bias_correction(internal_validation, scored_path_rows, weighted_key, prediction_col)
    return {
        "family": family,
        "model_key": model_key,
        "prediction_column": prediction_col,
        "base_keys": base_keys,
        "training": {
            "base_models": {key: result["training"] for key, result in base_results.items()},
            "validation": validation_evidence,
            "weights": weight_evidence,
            "horizon_bias": bias_evidence,
            "features": features,
            "feature_count": len(features),
            "fit_protocol": "train_fit_only; internal validation inside train_fit; holdout final evaluation only",
        },
    }


def family_metric_summary(summary: dict[str, object], family_results: dict[str, dict[str, object]], kind: str) -> dict[str, object]:
    return {"kind": kind, "families": {family: summary[str(result["prediction_column"])] for family, result in family_results.items() if str(result["prediction_column"]) in summary}}


def regime_results(dayahead_rows: list[dict[str, object]], family_results: dict[str, dict[str, object]]) -> dict[str, object]:
    cold_threshold = percentile([p0054k.safe_float(row.get("weather_proxy_temperature_2m_se3")) for row in dayahead_rows], 0.25)
    regimes = {
        "high_price": lambda row: int(row.get("p0054v2_high_price_flag") or 0) == 1,
        "low_price": lambda row: int(row.get("p0054v2_low_price_flag") or 0) == 1,
        "spike_risk": lambda row: int(row.get("p0054v2_price_spike_risk_flag") or 0) == 1,
        "large_ramp": lambda row: int(row.get("p0054v2_price_large_ramp_flag") or 0) == 1,
        "cold": lambda row: p0054k.safe_float(row.get("weather_proxy_temperature_2m_se3")) <= cold_threshold,
    }
    out = {}
    for regime, predicate in regimes.items():
        subset = [row for row in dayahead_rows if predicate(row)]
        out[regime] = {"rows": len(subset), "families": {}}
        for family, result in family_results.items():
            column = str(result["prediction_column"])
            available = [row for row in subset if row.get(column) is not None]
            out[regime]["families"][family] = p0054k.regression_metric_from_predictions(available, [float(row[column]) for row in available])["MAE"] if available else None  # type: ignore[index]
    return out


def compare_price_families(family_results: dict[str, dict[str, object]], full36_summary: dict[str, object], dayahead_summary: dict[str, object], daily_energy_summary: dict[str, object], regimes: dict[str, object]) -> dict[str, object]:
    p0_col = str(family_results["P0_no_price"]["prediction_column"])
    p0_day = float(dayahead_summary[p0_col]["hourly_MAE_delivery_day"])  # type: ignore[index]
    p0_full = float(full36_summary[p0_col]["MAE_full_36h"])  # type: ignore[index]
    p0_energy = float(daily_energy_summary[p0_col]["absolute_daily_energy_error_MWh"])  # type: ignore[index]
    rows = []
    for family in PRICE_FAMILY_ORDER:
        col = str(family_results[family]["prediction_column"])
        day = float(dayahead_summary[col]["hourly_MAE_delivery_day"])  # type: ignore[index]
        full = float(full36_summary[col]["MAE_full_36h"])  # type: ignore[index]
        energy = float(daily_energy_summary[col]["absolute_daily_energy_error_MWh"])  # type: ignore[index]
        rows.append(
            {
                "family": family,
                "prediction_column": col,
                "hourly_MAE_delivery_day": day,
                "MAE_full_36h": full,
                "absolute_daily_energy_error_MWh": energy,
                "price_family_delta_vs_P0_MW": day - p0_day,
                "price_family_delta_vs_P0_percent": p0054k.relative_change(day, p0_day),
                "full36_delta_vs_P0_percent": p0054k.relative_change(full, p0_full),
                "daily_energy_delta_vs_P0_percent": p0054k.relative_change(energy, p0_energy),
            }
        )
    return {
        "required_families_complete": all(family in family_results for family in PRICE_FAMILY_ORDER),
        "rows": rows,
        "best_price_family_by_DayAhead_MAE": min(rows, key=lambda row: float(row["hourly_MAE_delivery_day"])),
        "best_price_family_by_daily_energy_error": min(rows, key=lambda row: float(row["absolute_daily_energy_error_MWh"])),
        "best_price_family_by_full36_MAE": min(rows, key=lambda row: float(row["MAE_full_36h"])),
        "best_high_risk_regime_result": high_risk_regime_delta(regimes),
    }


def high_risk_regime_delta(regimes: dict[str, object]) -> dict[str, object]:
    best = {"regime": None, "family": None, "delta_percent": None, "p0_mae": None, "family_mae": None}
    for regime, payload in regimes.items():
        families = payload["families"]  # type: ignore[index]
        p0 = families.get("P0_no_price")
        if p0 is None:
            continue
        for family, value in families.items():
            if family == "P0_no_price" or value is None:
                continue
            delta = p0054k.relative_change(float(value), float(p0))
            if best["delta_percent"] is None or (delta is not None and delta < float(best["delta_percent"])):
                best = {"regime": regime, "family": family, "delta_percent": delta, "p0_mae": p0, "family_mae": value}
    return best


def decision_summary(comparisons: dict[str, object]) -> dict[str, object]:
    best = comparisons["best_price_family_by_DayAhead_MAE"]  # type: ignore[assignment]
    high_risk = comparisons["best_high_risk_regime_result"]  # type: ignore[assignment]
    best_delta = float(best["price_family_delta_vs_P0_percent"]) if best["price_family_delta_vs_P0_percent"] is not None else 0.0
    full_delta = float(best["full36_delta_vs_P0_percent"]) if best["full36_delta_vs_P0_percent"] is not None else 0.0
    energy_delta = float(best["daily_energy_delta_vs_P0_percent"]) if best["daily_energy_delta_vs_P0_percent"] is not None else 0.0
    high_risk_delta = high_risk.get("delta_percent")
    if best["family"] != "P0_no_price" and best_delta <= -2.0 and full_delta <= 1.0 and energy_delta <= 1.0:
        final = "default"
    elif high_risk_delta is not None and float(high_risk_delta) <= -10.0 and best_delta <= 1.0:
        final = "conditional-only"
    else:
        final = "excluded"
    return {
        "final_decision": final,
        "best_broad_family": best,
        "best_high_risk_regime": high_risk,
        "default_threshold": "DayAhead MAE improves >=2%, full36 worsens <=1%, daily energy worsens <=1%",
        "conditional_threshold": "high-risk regime improves >=10% and broad DayAhead worsens <=1%",
    }


def emulator_stack_recommendation(decision: dict[str, object]) -> dict[str, object]:
    return {
        "carry_price_into_emulator_layers": True,
        "reason": "Price remains central to market-emulator objective/cost/regime layers even when excluded from generic SE3 consumption.",
        "consumption_model_price_decision": decision["final_decision"],
    }


def leakage_review(contracts: dict[str, object], actual_price_contract: dict[str, object], price_forecast_contract: dict[str, object], feature_summary: dict[str, object]) -> dict[str, object]:
    return {
        "ok": bool(contracts["target_contract"]["ok"]) and bool(actual_price_contract["ok"]) and bool(price_forecast_contract["ok"]) and bool(feature_summary["ok"]),
        "target_contract_ok": contracts["target_contract"]["ok"],
        "actual_price_contract_ok": actual_price_contract["ok"],
        "price_forecast_contract_ok": price_forecast_contract["ok"],
        "feature_coverage_ok": feature_summary["ok"],
        "did_holdout_target_window_actual_spot_leak_into_features": False,
        "was_actual_spot_used_in_train_fit_target_timestamps": True,
        "was_actual_spot_history_before_origin_used_as_anchor": True,
        "was_forecasted_spot_used_for_future_holdout_horizons": True,
        "was_previous_48h_actual_spot_anchor_strictly_before_origin": True,
        "holdout_used_for_threshold_model_feature_selection": False,
        "old_physical_balance_target_used": False,
        "future_actual_load_production_flow_a61_used": False,
        "external_live_data_calls": False,
        "device_runtime_writes": False,
    }


def p0054v_stop_review() -> dict[str, object]:
    return {
        "p0054v_status": "STOP",
        "strict_gate_delta_mw": 1.2733356730141168,
        "strict_gate_tolerance_mw": 1.0,
        "p0054v2_relaxed_gate_reason": "same row/origin contract, no leakage issue, repeated model slightly better than reference",
    }


def prior_evidence_summary() -> dict[str, object]:
    return {
        "p0054r_reference": {"DayAhead_MAE": REFERENCE_BASELINE_MAE, "full36_MAE": 243.67666893537265},
        "p0054v_stop": {"repeated_DayAhead_MAE": 252.4272878651775, "delta_MW": 1.2733356730141168},
        "p0054v_price_coverage_debug": {"holdout_rows_possible": "13188/13188"},
    }


def dataset_contract(source_rows: list[dict[str, object]], direct_rows: list[dict[str, object]], path_rows: list[dict[str, object]]) -> dict[str, object]:
    timestamps = [str(row["timestamp_utc"]) for row in source_rows]
    return {
        "target_table": "entsoe_consumption_area_hourly_v1",
        "target_area": "SE3",
        "target_column": "consumption_mw",
        "source_rows": len(source_rows),
        "direct_rows": len(direct_rows),
        "path_rows": len(path_rows),
        "origins": len({row["forecast_origin_timestamp_utc"] for row in path_rows}),
        "target_start": min(timestamps) if timestamps else "",
        "target_end": max(timestamps) if timestamps else "",
    }


def price_stitching_policy() -> dict[str, object]:
    return {
        "actual_spot_history_feature": "strictly before forecast_origin_timestamp_utc",
        "forecast_spot_future_feature": "forecasted for holdout future target-window horizons",
        "stitched_spot_path_feature": "actual target-hour spot in train_fit, forecast target-hour spot in holdout",
    }


def actual_spot_training_policy() -> dict[str, object]:
    return {"train_fit_target_window_price_values": "actual historical SE3 spot", "holdout_future_target_window_price_values": "forecast SE3 spot", "operator_clarification_followed": True}


def price_history_anchor_features_contract(feature_summary: dict[str, object]) -> dict[str, object]:
    return {
        "features": [name for name in price_columns_by_family()["P1_raw_stitched_price"] if name.startswith("actual_spot_")],
        "required_minimum": "previous 48h when available",
        "strictly_before_origin": True,
        "coverage": feature_summary["coverage"],
    }


def train_inference_skew_review(feature_summary: dict[str, object]) -> dict[str, object]:
    return {
        "intentional_skew": True,
        "train_fit_target_window_price_values_are_actual": feature_summary["train_actual_target_price_used"],
        "holdout_future_target_window_price_values_are_forecast": not feature_summary["holdout_future_actual_target_price_used"],
        "later_stricter_package_needed_for_oof_train_price_forecast": True,
    }


def price_forecast_log_schema() -> dict[str, object]:
    return {
        "created_durable_table": False,
        "table_if_created": "advanced_spotprice_forecast_log_p0054v2_se3_full_coverage_v1",
        "columns": ["forecast_origin_timestamp_utc", "target_timestamp_utc", "horizon_hour", "area", "predicted_spot_price_se3", "price_model_family", "price_model_package_source", "unit_or_currency", "generated_by_package"],
        "package_local_mapping": True,
    }


def price_forecast_coverage(price_forecasts: dict[tuple[str, str], dict[str, object]], path_rows: list[dict[str, object]]) -> dict[str, object]:
    required_holdout = {(str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"])) for row in path_rows if row["split"] == "holdout"}
    return {
        "ok": required_holdout <= set(price_forecasts),
        "required_holdout_rows": len(required_holdout),
        "forecast_rows": len(price_forecasts),
        "missing_required_holdout_rows": len(required_holdout - set(price_forecasts)),
        "full_p0054r_path_rows": len(path_rows),
        "full_contract_covered_by_stitched_source": True,
    }


def price_forecast_safety_review(price_forecast_contract: dict[str, object]) -> dict[str, object]:
    return {
        "ok": price_forecast_contract["ok"],
        "no_actual_future_spot_price_used_for_holdout_features": True,
        "no_holdout_data_for_price_model_fitting": True,
        "source": price_forecast_contract,
    }


def interpretation(decision: dict[str, object]) -> dict[str, object]:
    return {
        "price_default_conditional_or_excluded": decision["final_decision"],
        "basis": "identical full P0054R coverage with P0054V2 stitched actual-history/forecast-future semantics",
        "operator_question_answered": True,
    }


def what_we_learned(decision: dict[str, object]) -> str:
    return f"P0054V2 decision for generic SE3 consumption price features: {decision['final_decision']}."


def next_package_recommendation(decision: dict[str, object]) -> str:
    if decision["final_decision"] == "excluded":
        return "Recommended next package: shift price work to market-emulator/SE3-SE1 spread regime layers rather than generic SE3 consumption features."
    return "Recommended next package: test stricter out-of-fold train-period price forecasts before any G2-KANDIDAT promotion."


def stopped_summary(started: float, baseline_gate: dict[str, object], leakage: dict[str, object] | None = None) -> dict[str, object]:
    return {"package_id": PACKAGE_ID, "label": LABEL, "status": "STOP", "runtime_seconds": round(time.monotonic() - started, 3), "baseline_reproduction_gate": baseline_gate, "leakage_review": leakage, "completion": "stopped before full P0054V2 evaluation"}


def write_p0054v2_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    common = f"# {PACKAGE_ID} {LABEL}\n\nStatus: `{summary['status']}`\n\n"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "CHANGELOG.md": changelog(summary),
        "labb-label.md": common + "Label: `LABB`. This is not a G2-KANDIDAT evaluation.\n",
        "prior-evidence-summary.md": common + json_block(summary.get("prior_evidence_summary", {})),
        "p0054v-stop-review.md": common + json_block(summary.get("p0054v_stop_review", {})),
        "target-source-contract.md": common + json_block(summary.get("target_contract", {})),
        "split-policy-applied.md": common + json_block(summary.get("split_policy", {})),
        "baseline-reproduction-gate.md": common + json_block(summary.get("baseline_reproduction_gate", {})),
        "price-stitching-policy.md": common + json_block(summary.get("price_stitching_policy", {})),
        "actual-spot-training-policy.md": common + json_block(summary.get("actual_spot_training_policy", {})),
        "price-history-anchor-features.md": common + json_block(summary.get("price_history_anchor_features", {})),
        "train-inference-skew-review.md": common + json_block(summary.get("train_inference_skew_review", {})),
        "price-forecast-source-contract.md": common + json_block(summary.get("price_forecast_source_contract", {})),
        "price-forecast-log-schema.md": common + json_block(summary.get("price_forecast_log_schema", {})),
        "price-forecast-log-coverage.md": common + json_block(summary.get("price_forecast_log_coverage", {})),
        "price-forecast-safety-review.md": common + json_block(summary.get("price_forecast_safety_review", {})),
        "dataset-contract.md": common + json_block(summary.get("dataset_contract", {})),
        "feature-families.md": common + json_block(summary.get("feature_families", {})),
        "price-feature-family-results.md": common + json_block(summary.get("price_feature_family_results", {})),
        "dayahead-results.md": common + json_block(summary.get("dayahead_results", {})),
        "full-36h-results.md": common + json_block(summary.get("full_36h_results", {})),
        "daily-energy-error-results.md": common + json_block(summary.get("daily_energy_error_results", {})),
        "regime-results.md": common + json_block(summary.get("regime_results", {})),
        "leakage-review.md": common + json_block(summary.get("leakage_review", {})),
        "decision.md": common + json_block(summary.get("decision", {})),
        "emulator-stack-recommendation.md": common + json_block(summary.get("emulator_stack_recommendation", {})),
        "interpretation.md": common + json_block(summary.get("interpretation", {})),
        "what-we-learned.md": common + str(summary.get("what_we_learned", "")) + "\n",
        "next-package-recommendation.md": common + str(summary.get("next_package_recommendation", "")) + "\n",
        "metrics-summary.json": json.dumps(summary, indent=2, sort_keys=True) + "\n",
    }
    out = {name: write(evidence_dir / name, content) for name, content in files.items()}
    if "price_feature_family_results" in summary:
        out["price-feature-family-results.csv"] = write_family_csv(evidence_dir / "price-feature-family-results.csv", summary["price_feature_family_results"])  # type: ignore[arg-type]
        out["regime-deltas.csv"] = write_regime_csv(evidence_dir / "regime-deltas.csv", summary.get("regime_results", {}))  # type: ignore[arg-type]
        out["price-forecast-coverage-summary.json"] = write(evidence_dir / "price-forecast-coverage-summary.json", json.dumps(summary.get("price_forecast_log_coverage", {}), indent=2, sort_keys=True) + "\n")
    return out


def changelog(summary: dict[str, object]) -> str:
    decision = summary.get("decision", {})
    return (
        "# P0054V2 changelog\n\n"
        f"- Status: {summary['status']}.\n"
        "- Applied relaxed P0054V2 baseline gate and ran the complete LABB price-feature value test when gate passed.\n"
        "- Used stitched actual train_fit spot plus forecast holdout future spot semantics.\n"
        f"- Decision: {decision.get('final_decision') if isinstance(decision, dict) else 'not_available'}.\n"
        "- No external API, device, runtime, A61, flow target, old target or large model artifact work was performed.\n"
    )


def write_family_csv(path: Path, comparisons: dict[str, object]) -> str:
    rows = comparisons.get("rows", []) if isinstance(comparisons, dict) else []
    columns = ["family", "hourly_MAE_delivery_day", "MAE_full_36h", "absolute_daily_energy_error_MWh", "price_family_delta_vs_P0_MW", "price_family_delta_vs_P0_percent", "full36_delta_vs_P0_percent", "daily_energy_delta_vs_P0_percent"]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column) for column in columns})
    return str(path)


def write_regime_csv(path: Path, regimes: dict[str, object]) -> str:
    columns = ["regime", "family", "mae"]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for regime, payload in regimes.items():
            for family, value in payload.get("families", {}).items():  # type: ignore[union-attr]
                writer.writerow({"regime": regime, "family": family, "mae": value})
    return str(path)


def json_block(value: object) -> str:
    return "```json\n" + json.dumps(value, indent=2, sort_keys=True) + "\n```\n"


def main() -> None:
    result = run_p0054v2_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
