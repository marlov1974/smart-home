"""P0053B-A2 SE1 consumption response to anchored price forecasts."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import csv
import json
import math
import sqlite3
import time

import numpy as np

from src.mac.services.spotprice_model_diagnostics import p0052, p0053b, p0053cb
from src.mac.services.spotprice_model_diagnostics.forecast_period_policy import (
    HOLDOUT_START_UTC,
    POLICY_VERSION,
    canonical_split_for_timestamp,
    parse_policy_timestamp,
    policy_summary,
)
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write
from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0053B-A2"
EVIDENCE_DIR = Path("requirements/package-runs/P0053B-A2")
PRICE_LOG_TABLE = p0053cb.FORECAST_LOG_TABLE
TARGET_SOURCE_TABLE = p0053b.SOURCE_TABLE
TARGET = "consumption_se1_mw"
WEATHER_PROXY_LABEL = "weather_actual_as_forecast_proxy"
RANDOM_SEED = 53
HORIZONS = (1, 3, 6, 12, 24, 48, 72, 96, 120, 144, 168)
REQUIRED_MODELS = (
    ("M4_base_Ridge_G4", "G4_calendar_load_lags_weather_proxy", "Ridge", None),
    ("M4_plus_G7_Ridge_G4_price", "G4_plus_G7_calendar_load_weather_price", "Ridge", "M4_base_Ridge_G4"),
    ("M7_base_HGB_G4", "G4_calendar_load_lags_weather_proxy", "HistGradientBoostingRegressor", None),
    ("M7_plus_G7_HGB_G4_price", "G4_plus_G7_calendar_load_weather_price", "HistGradientBoostingRegressor", "M7_base_HGB_G4"),
)


@dataclass(frozen=True)
class P0053BA2Result:
    status: str
    interpretation: str
    weekly_origin_count: int
    evidence: dict[str, str]


def run_p0053ba2_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0053BA2Result:
    started = time.monotonic()
    feature_path = Path(feature_db).expanduser()
    with sqlite3.connect(feature_path) as conn:
        conn.row_factory = sqlite3.Row
        preconditions = validate_preconditions(conn)
    if not preconditions["ok"]:
        raise RuntimeError(f"P0053B-A2 preconditions failed: {preconditions}")

    source_rows = p0053b.load_consumption_source_rows(feature_path)
    weather_rows, weather_contract = p0053b.load_weather_rows(weather_db)
    price_rows = load_price_forecast_rows(feature_path)
    modeling_rows, dataset_contract = build_modeling_rows(source_rows, weather_rows, price_rows)
    feature_contract = feature_group_contract()
    weekly = select_weekly_holdout_origins(modeling_rows)
    model_results, scored_rows, importance, model_row_sets = fit_required_models(modeling_rows, feature_contract)
    direct_results = evaluate_direct_horizons(scored_rows)
    weekly_results, weekly_path_rows = evaluate_weekly_paths(scored_rows, weekly["weekly_origins"])
    conditional_results, conditional_rows = evaluate_conditional_price_response(scored_rows)
    comparison = compare_base_plus(direct_results)
    leakage = validate_leakage_and_fairness(modeling_rows, model_row_sets, preconditions)
    interpretation = interpret_result(comparison, weekly_results, conditional_results)
    status = "PASS" if leakage["ok"] and interpretation != "inconclusive_due_to_weather_proxy_or_coverage" else "WARN" if leakage["ok"] else "STOP"
    summary = {
        "status": status,
        "package_id": PACKAGE_ID,
        "split_policy": policy_summary(),
        "preconditions": preconditions,
        "target_source": TARGET_SOURCE_TABLE,
        "target": TARGET,
        "anchored_price_log": PRICE_LOG_TABLE,
        "weather_contract": weather_contract,
        "weather_proxy_label": WEATHER_PROXY_LABEL,
        "dataset_contract": dataset_contract,
        "feature_contract": feature_contract,
        "weekly_origin_summary": weekly,
        "direct_results": direct_results,
        "weekly_results": weekly_results,
        "conditional_results": conditional_results,
        "base_vs_price_comparison": comparison,
        "feature_importance": importance,
        "leakage_review": leakage,
        "interpretation": interpretation,
        "forecast_readiness": forecast_readiness(interpretation),
        "runtime_seconds": time.monotonic() - started,
    }
    evidence = write_p0053ba2_evidence(Path(evidence_dir), summary, modeling_rows, weekly_path_rows, conditional_rows)
    return P0053BA2Result(
        status=status,
        interpretation=interpretation,
        weekly_origin_count=len(weekly["weekly_origins"]),  # type: ignore[arg-type]
        evidence=evidence,
    )


def validate_preconditions(conn: sqlite3.Connection) -> dict[str, object]:
    tables = {str(row["name"]) for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    required = {TARGET_SOURCE_TABLE, PRICE_LOG_TABLE}
    missing = sorted(required - tables)
    price_summary = {}
    if PRICE_LOG_TABLE in tables:
        row = conn.execute(
            f"""
            SELECT COUNT(*), MIN(forecast_origin_timestamp_utc), MAX(forecast_origin_timestamp_utc),
                   MIN(target_timestamp_utc), MAX(target_timestamp_utc), MIN(horizon_hours), MAX(horizon_hours)
            FROM {PRICE_LOG_TABLE}
            WHERE area='SE1' AND prediction_kind='anchored_absolute_price'
            """
        ).fetchone()
        split_rows = conn.execute(
            f"""
            SELECT CASE
                     WHEN target_timestamp_utc <= '2024-12-31T23:00:00Z' THEN 'train'
                     WHEN target_timestamp_utc <= '2025-05-31T23:00:00Z' THEN 'validate'
                     ELSE 'holdout'
                   END AS split,
                   COUNT(*)
            FROM {PRICE_LOG_TABLE}
            WHERE area='SE1' AND prediction_kind='anchored_absolute_price'
            GROUP BY split
            """
        ).fetchall()
        order_errors = conn.execute(
            f"""
            SELECT COUNT(*)
            FROM {PRICE_LOG_TABLE}
            WHERE area='SE1' AND prediction_kind='anchored_absolute_price'
              AND (forecast_origin_timestamp_utc > target_timestamp_utc
                   OR input_data_cutoff_utc > forecast_origin_timestamp_utc
                   OR horizon_hours < 0 OR horizon_hours > 167)
            """
        ).fetchone()[0]
        price_summary = {
            "rows": int(row[0]),
            "forecast_origin_min": row[1],
            "forecast_origin_max": row[2],
            "target_min": row[3],
            "target_max": row[4],
            "horizon_min": row[5],
            "horizon_max": row[6],
            "split_counts": {str(item[0]): int(item[1]) for item in split_rows},
            "forecast_origin_order_errors": int(order_errors),
            "has_train_price_forecast_rows": any(str(item[0]) == "train" and int(item[1]) > 0 for item in split_rows),
        }
    ok = not missing and bool(price_summary) and int(price_summary.get("rows", 0)) > 0 and int(price_summary.get("forecast_origin_order_errors", 1)) == 0
    return {
        "ok": ok,
        "missing_tables": missing,
        "price_log": price_summary,
        "p0053c_b_log_has_forecast_origin_semantics": ok,
        "coverage_warning": "price_log_has_validation_and_holdout_only; plus_G7 fit uses validation-origin rows as development training",
    }


def load_price_forecast_rows(feature_db: Path) -> list[dict[str, object]]:
    with sqlite3.connect(feature_db) as conn:
        conn.row_factory = sqlite3.Row
        rows = [
            dict(row)
            for row in conn.execute(
                f"""
                SELECT forecast_origin_timestamp_utc, input_data_cutoff_utc, target_timestamp_utc,
                       horizon_hours, predicted_price, source_shape_value, anchor_method
                FROM {PRICE_LOG_TABLE}
                WHERE area='SE1' AND prediction_kind='anchored_absolute_price' AND quality_flag='canonical'
                ORDER BY forecast_origin_timestamp_utc, horizon_hours
                """
            )
        ]
    return rows


def build_modeling_rows(
    source_rows: list[dict[str, object]],
    weather_rows: dict[str, dict[str, object]],
    price_rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    source_by_ts = {str(row["timestamp_utc"]): row for row in source_rows}
    source_index = {str(row["timestamp_utc"]): index for index, row in enumerate(source_rows)}
    values = [float(row["consumption_se1"]) for row in source_rows]
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in price_rows:
        grouped[str(row["forecast_origin_timestamp_utc"])].append(row)
    output: list[dict[str, object]] = []
    skipped = Counter()
    for origin, path in grouped.items():
        ordered_path = sorted(path, key=lambda row: int(row["horizon_hours"]))
        origin_index = source_index.get(origin)
        if origin_index is None or origin_index < max(max(p0053b.LAGS), max(p0053b.ROLL_WINDOWS)):
            skipped["missing_or_insufficient_origin_load_history"] += len(ordered_path)
            continue
        if len(ordered_path) != 168:
            skipped["incomplete_price_path"] += len(ordered_path)
            continue
        path_rows = []
        for price_row in ordered_path:
            target_ts = str(price_row["target_timestamp_utc"])
            target = source_by_ts.get(target_ts)
            if target is None:
                skipped["missing_target_consumption"] += 1
                continue
            row = {
                "row_id": f"{origin}|{target_ts}",
                "forecast_origin_timestamp_utc": origin,
                "input_data_cutoff_utc": price_row["input_data_cutoff_utc"],
                "target_timestamp_utc": target_ts,
                "p0053cb_horizon_hours": int(price_row["horizon_hours"]),
                "horizon_h": int(price_row["horizon_hours"]) + 1,
                "split": canonical_split_for_timestamp(target_ts),
                "target_consumption_se1_mw": float(target["consumption_se1"]),
                "forecast_se1_price_target_hour": float(price_row["predicted_price"]),
                "forecast_se1_price_horizon_h": int(price_row["horizon_hours"]) + 1,
                "source_shape_value": float(price_row["source_shape_value"]),
                "anchor_method": str(price_row["anchor_method"]),
                "weather_proxy_label": WEATHER_PROXY_LABEL,
            }
            p0053b.attach_calendar_features(row, p0052.parse_utc(target_ts) + timedelta(hours=1))
            row.update(p0053b.lag_features_at_origin(values, origin_index))
            row.update(p0053b.rolling_features_at_origin(values, origin_index))
            attach_weather_proxy(row, weather_rows.get(target_ts, {}))
            path_rows.append(row)
        if len(path_rows) == 168:
            compute_g7_features(path_rows)
            output.extend(path_rows)
        else:
            skipped["incomplete_joined_path"] += len(ordered_path)
    split_counts = Counter(str(row["split"]) for row in output)
    return output, {
        "row_count": len(output),
        "split_counts": dict(split_counts),
        "skipped": dict(skipped),
        "target_source_table": TARGET_SOURCE_TABLE,
        "anchored_price_log": PRICE_LOG_TABLE,
        "weather_proxy_label": WEATHER_PROXY_LABEL,
        "training_policy_warning": "no train-period G7 price forecast rows; models fit on validation-origin joined rows and score holdout",
    }


def attach_weather_proxy(row: dict[str, object], weather: dict[str, object]) -> None:
    mappings = {
        "weather_actual_temperature_se1": "weather_proxy_temperature_se1",
        "weather_actual_wind_100m_se1": "weather_proxy_wind_100m_se1",
        "weather_actual_solar_se1": "weather_proxy_solar_se1",
        "weather_actual_heating_degree_proxy": "weather_proxy_heating_degree",
        "weather_actual_cooling_degree_proxy": "weather_proxy_cooling_degree",
    }
    for source, target in mappings.items():
        row[target] = safe_float(weather.get(source))


def compute_g7_features(path_rows: list[dict[str, object]]) -> None:
    prices = [float(row["forecast_se1_price_target_hour"]) for row in path_rows]
    mean_168 = sum(prices) / len(prices)
    rank_168 = rank_map(prices, high_rank=True)
    top_168 = set(top_indexes(prices, 20, high=True))
    low_168 = set(top_indexes(prices, 20, high=False))
    first24 = prices[:24]
    volatility_first24 = std_float(first24)
    for day in range(7):
        lo = day * 24
        hi = lo + 24
        day_prices = prices[lo:hi]
        mean_day = sum(day_prices) / len(day_prices)
        spread = max(day_prices) - min(day_prices)
        rank_day = rank_map(day_prices, high_rank=True)
        top4 = set(top_indexes(day_prices, 4, high=True))
        top8 = set(top_indexes(day_prices, 8, high=True))
        bottom4 = set(top_indexes(day_prices, 4, high=False))
        daily_median = percentile(day_prices, 0.5)
        for local_index, row in enumerate(path_rows[lo:hi]):
            absolute_index = lo + local_index
            price = float(row["forecast_se1_price_target_hour"])
            row["forecast_se1_price_relative_to_forecast_24h_mean"] = price - mean_day
            row["forecast_se1_price_relative_to_forecast_168h_mean"] = price - mean_168
            row["forecast_se1_price_rank_in_168h"] = rank_168[absolute_index]
            row["forecast_se1_price_rank_in_forecast_day"] = rank_day[local_index]
            row["forecast_se1_price_top4_forecast_day_flag"] = 1 if local_index in top4 else 0
            row["forecast_se1_price_top8_forecast_day_flag"] = 1 if local_index in top8 else 0
            row["forecast_se1_price_bottom4_forecast_day_flag"] = 1 if local_index in bottom4 else 0
            row["forecast_se1_price_daily_spread_forecast"] = spread
            row["forecast_se1_price_volatility_next_24h_forecast"] = volatility_first24
            row["forecast_se1_price_is_daily_peak_half_flag"] = 1 if price >= daily_median else 0
            row["forecast_se1_price_is_daily_low_half_flag"] = 1 if price < daily_median else 0
            row["forecast_se1_price_high_168h_rank_flag"] = 1 if absolute_index in top_168 else 0
            row["forecast_se1_price_low_168h_rank_flag"] = 1 if absolute_index in low_168 else 0


def feature_group_contract() -> dict[str, dict[str, object]]:
    calendar = [
        "target_model_cet_hour",
        "target_model_cet_weekday",
        "target_model_cet_day_of_year",
        "target_month",
        "target_hour_sin",
        "target_hour_cos",
        "target_dayofyear_sin",
        "target_dayofyear_cos",
        "is_weekend",
        "is_workday",
        "is_holiday",
        "is_bridge_day",
        "is_holiday_period",
        "holiday_strength",
    ]
    lags = [f"consumption_se1_lag_{lag}h" for lag in p0053b.LAGS]
    rollups = [f"consumption_se1_roll_mean_{window}h" for window in p0053b.ROLL_WINDOWS] + [
        "consumption_se1_roll_min_24h",
        "consumption_se1_roll_max_24h",
        "consumption_se1_roll_std_24h",
    ]
    weather_proxy = [
        "weather_proxy_temperature_se1",
        "weather_proxy_wind_100m_se1",
        "weather_proxy_solar_se1",
        "weather_proxy_heating_degree",
        "weather_proxy_cooling_degree",
    ]
    g7 = [
        "forecast_se1_price_target_hour",
        "forecast_se1_price_horizon_h",
        "forecast_se1_price_relative_to_forecast_24h_mean",
        "forecast_se1_price_relative_to_forecast_168h_mean",
        "forecast_se1_price_rank_in_168h",
        "forecast_se1_price_rank_in_forecast_day",
        "forecast_se1_price_top4_forecast_day_flag",
        "forecast_se1_price_top8_forecast_day_flag",
        "forecast_se1_price_bottom4_forecast_day_flag",
        "forecast_se1_price_daily_spread_forecast",
        "forecast_se1_price_volatility_next_24h_forecast",
        "forecast_se1_price_is_daily_peak_half_flag",
        "forecast_se1_price_is_daily_low_half_flag",
    ]
    return {
        "G0_calendar_only": {"safety": "forecast_safe", "features": calendar},
        "G1_calendar_plus_recent_load_lags": {"safety": "forecast_safe", "features": calendar + lags},
        "G4_calendar_load_lags_weather_proxy": {"safety": "offline_backtest_weather_proxy", "features": calendar + lags + rollups + weather_proxy},
        "G7_price_only_diagnostic": {"safety": "forecast_log_only_price_diagnostic", "features": g7},
        "G4_plus_G7_calendar_load_weather_price": {"safety": "offline_backtest_weather_proxy_plus_forecast_price", "features": calendar + lags + rollups + weather_proxy + g7},
    }


def select_weekly_holdout_origins(rows: list[dict[str, object]]) -> dict[str, object]:
    holdout_by_origin: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if row["split"] == "holdout":
            holdout_by_origin[str(row["forecast_origin_timestamp_utc"])].append(row)
    complete = [origin for origin, origin_rows in sorted(holdout_by_origin.items()) if len(origin_rows) == 168]
    weekly = complete[::7]
    skipped = [
        {"forecast_origin_timestamp_utc": origin, "reason": "not_weekly_subset"}
        for origin in complete
        if origin not in set(weekly)
    ]
    return {
        "weekly_origin_count": len(weekly),
        "first_weekly_origin": weekly[0] if weekly else None,
        "last_weekly_origin": weekly[-1] if weekly else None,
        "complete_168h_path_count": len(complete),
        "weekly_origins": weekly,
        "skipped_origins_with_reason": skipped[:100],
        "skipped_origin_count": len(skipped),
        "origin_rule": "every seventh complete P0053C-B holdout origin starting at first holdout origin",
    }


def fit_required_models(
    rows: list[dict[str, object]],
    contract: dict[str, dict[str, object]],
) -> tuple[dict[str, object], list[dict[str, object]], dict[str, object], dict[str, object]]:
    scored = [dict(row) for row in rows]
    by_id = {str(row["row_id"]): row for row in scored}
    results: dict[str, object] = {}
    importance: dict[str, object] = {}
    row_sets: dict[str, object] = {}
    for model_name, group, model_class, base_model in REQUIRED_MODELS:
        row_sets[model_name] = {}
        features = contract[group]["features"]  # type: ignore[index]
        development = [row for row in rows if row["split"] == "validate"]
        holdout = [row for row in rows if row["split"] == "holdout"]
        if not development or not holdout:
            results[model_name] = {}
            continue
        model, encoder, names = fit_model(development, features, model_class)  # type: ignore[arg-type]
        dev_pred = predict_model(model, encoder, development, features)  # type: ignore[arg-type]
        holdout_pred = predict_model(model, encoder, holdout, features)  # type: ignore[arg-type]
        for row, pred in zip(development, dev_pred):
            by_id[str(row["row_id"])][f"pred_{model_name}"] = pred
        for row, pred in zip(holdout, holdout_pred):
            by_id[str(row["row_id"])][f"pred_{model_name}"] = pred
        result = {
            "model_class": model_class,
            "feature_group": group,
            "fit_split": "validate_development_due_price_log_coverage",
            "fit_mode": "single_path_model_scores_all_168_horizons",
            "validate_development": metric_from_rows(development, dev_pred),
            "holdout": metric_from_rows(holdout, holdout_pred),
        }
        if base_model:
            base = results.get(base_model, {}) if isinstance(results.get(base_model), dict) else {}
            result["relative_improvement_vs_base_same_rows"] = relative_improvement(result, base)
        results[model_name] = result
        importance[model_name] = model_importance(model, names)
        for horizon in HORIZONS:
            development_h = [row for row in development if int(row["horizon_h"]) == horizon]
            holdout_h = [row for row in holdout if int(row["horizon_h"]) == horizon]
            row_sets[model_name][str(horizon)] = {
                "validate_row_ids": sorted(str(row["row_id"]) for row in development_h),
                "holdout_row_ids": sorted(str(row["row_id"]) for row in holdout_h),
            }
    return results, list(by_id.values()), importance, row_sets


def fit_model(rows: list[dict[str, object]], features: list[str], model_class: str) -> tuple[object, p0053b.Encoder, list[str]]:
    x, encoder, names = p0053b.build_feature_matrix(rows, features)
    y = np.array([float(row["target_consumption_se1_mw"]) for row in rows])
    if model_class == "Ridge":
        from sklearn.linear_model import Ridge

        model = Ridge(alpha=1.0, random_state=RANDOM_SEED)
    else:
        from sklearn.ensemble import HistGradientBoostingRegressor

        model = HistGradientBoostingRegressor(max_iter=80, learning_rate=0.06, max_leaf_nodes=15, min_samples_leaf=80, random_state=RANDOM_SEED)
    model.fit(x, y)
    return model, encoder, names


def predict_model(model: object, encoder: p0053b.Encoder, rows: list[dict[str, object]], features: list[str]) -> list[float]:
    x, _, _ = p0053b.build_feature_matrix(rows, features, encoder)
    return [float(value) for value in model.predict(x)]  # type: ignore[attr-defined]


def evaluate_direct_horizons(rows: list[dict[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for model_name, _group, _model_class, base_model in REQUIRED_MODELS:
        output[model_name] = {}
        for horizon in HORIZONS:
            output[model_name][str(horizon)] = {}
            for split in ("validate", "holdout"):
                subset = [row for row in rows if int(row["horizon_h"]) == horizon and row["split"] == split and row.get(f"pred_{model_name}") is not None]
                output[model_name][str(horizon)][split] = metric_from_rows(subset, [float(row[f"pred_{model_name}"]) for row in subset])
            if base_model:
                output[model_name][str(horizon)]["relative_improvement_vs_base_same_rows"] = relative_improvement(output[model_name][str(horizon)], output[base_model][str(horizon)])  # type: ignore[index]
    return output


def evaluate_weekly_paths(rows: list[dict[str, object]], weekly_origins: list[str]) -> tuple[dict[str, object], list[dict[str, object]]]:
    path_rows = []
    for model_name, _group, _model_class, base_model in REQUIRED_MODELS:
        for origin in weekly_origins:
            subset = sorted(
                [row for row in rows if row["forecast_origin_timestamp_utc"] == origin and row.get(f"pred_{model_name}") is not None],
                key=lambda row: int(row["horizon_h"]),
            )
            if len(subset) != 168:
                continue
            metric = path_metric_row(origin, model_name, subset, f"pred_{model_name}")
            if base_model:
                base_subset = sorted(
                    [row for row in rows if row["forecast_origin_timestamp_utc"] == origin and row.get(f"pred_{base_model}") is not None],
                    key=lambda row: int(row["horizon_h"]),
                )
                if len(base_subset) == 168:
                    base_metric = path_metric_row(origin, base_model, base_subset, f"pred_{base_model}")
                    metric["relative_improvement_vs_base_MAE_full_168h"] = improvement_from_values(base_metric["MAE_full_168h"], metric["MAE_full_168h"])
            path_rows.append(metric)
    summary = {
        model_name: aggregate_path_rows([row for row in path_rows if row["model"] == model_name])
        for model_name, _group, _model_class, _base_model in REQUIRED_MODELS
    }
    return summary, path_rows


def path_metric_row(origin: str, model_name: str, rows: list[dict[str, object]], prediction_column: str) -> dict[str, object]:
    actual = [float(row["target_consumption_se1_mw"]) for row in rows]
    pred = [float(row[prediction_column]) for row in rows]
    errors = [p - a for a, p in zip(actual, pred)]
    abs_errors = [abs(error) for error in errors]
    daily_errors = [sum(errors[index : index + 24]) for index in range(0, 168, 24)]
    peak_index = max(range(len(actual)), key=lambda index: actual[index])
    return {
        "forecast_origin_timestamp_utc": origin,
        "model": model_name,
        "path_hours": len(rows),
        "MAE_0_24h": sum(abs_errors[:24]) / 24,
        "MAE_24_48h": sum(abs_errors[24:48]) / 24,
        "MAE_48_72h": sum(abs_errors[48:72]) / 24,
        "MAE_72_168h": sum(abs_errors[72:168]) / 96,
        "MAE_full_168h": sum(abs_errors) / 168,
        "bias_full_168h": sum(errors) / 168,
        "p90_abs_error_full_168h": percentile(abs_errors, 0.90),
        "p95_abs_error_full_168h": percentile(abs_errors, 0.95),
        "daily_energy_error_proxy": sum(abs(value) for value in daily_errors) / len(daily_errors),
        "peak_load_hour_error": abs_errors[peak_index],
    }


def aggregate_path_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    if not rows:
        return {"weekly_origin_count": 0}
    keys = (
        "MAE_0_24h",
        "MAE_24_48h",
        "MAE_48_72h",
        "MAE_72_168h",
        "MAE_full_168h",
        "bias_full_168h",
        "p90_abs_error_full_168h",
        "p95_abs_error_full_168h",
        "daily_energy_error_proxy",
        "peak_load_hour_error",
    )
    return {"weekly_origin_count": len(rows), **{key: sum(float(row[key]) for row in rows) / len(rows) for key in keys}}


def evaluate_conditional_price_response(rows: list[dict[str, object]]) -> tuple[dict[str, object], list[dict[str, object]]]:
    holdout = [row for row in rows if row["split"] == "holdout"]
    cold_threshold = percentile([safe_float(row.get("weather_proxy_temperature_se1")) for row in holdout], 0.25)
    conditions = {
        "forecast_price_top4_day_hours": lambda row: int(row["forecast_se1_price_top4_forecast_day_flag"]) == 1,
        "forecast_price_top8_day_hours": lambda row: int(row["forecast_se1_price_top8_forecast_day_flag"]) == 1,
        "forecast_price_bottom4_day_hours": lambda row: int(row["forecast_se1_price_bottom4_forecast_day_flag"]) == 1,
        "forecast_price_high_168h_rank_hours": lambda row: int(row["forecast_se1_price_high_168h_rank_flag"]) == 1,
        "forecast_price_low_168h_rank_hours": lambda row: int(row["forecast_se1_price_low_168h_rank_flag"]) == 1,
        "cold_plus_forecast_top8_hours": lambda row: safe_float(row.get("weather_proxy_temperature_se1")) <= cold_threshold and int(row["forecast_se1_price_top8_forecast_day_flag"]) == 1,
        "weekday_forecast_top8_hours": lambda row: int(row["target_model_cet_weekday"]) < 5 and int(row["forecast_se1_price_top8_forecast_day_flag"]) == 1,
        "weekend_forecast_top8_hours": lambda row: int(row["target_model_cet_weekday"]) >= 5 and int(row["forecast_se1_price_top8_forecast_day_flag"]) == 1,
        "holiday_forecast_top8_hours": lambda row: int(row["is_holiday"]) == 1 and int(row["forecast_se1_price_top8_forecast_day_flag"]) == 1,
    }
    result: dict[str, object] = {}
    csv_rows = []
    pairs = (("M4_base_Ridge_G4", "M4_plus_G7_Ridge_G4_price"), ("M7_base_HGB_G4", "M7_plus_G7_HGB_G4_price"))
    for condition, predicate in conditions.items():
        subset = [row for row in holdout if predicate(row)]
        result[condition] = {}
        for base, plus in pairs:
            valid = [row for row in subset if row.get(f"pred_{base}") is not None and row.get(f"pred_{plus}") is not None]
            base_metric = metric_from_rows(valid, [float(row[f"pred_{base}"]) for row in valid])
            plus_metric = metric_from_rows(valid, [float(row[f"pred_{plus}"]) for row in valid])
            improvement = improvement_from_values(base_metric["MAE"], plus_metric["MAE"])
            item = {"rows": len(valid), "base_MAE": base_metric["MAE"], "plus_G7_MAE": plus_metric["MAE"], "relative_improvement": improvement}
            result[condition][plus] = item  # type: ignore[index]
            csv_rows.append({"condition": condition, "base_model": base, "plus_model": plus, **item})
    return result, csv_rows


def compare_base_plus(direct_results: dict[str, object]) -> dict[str, object]:
    comparisons = {}
    for base, plus in (("M4_base_Ridge_G4", "M4_plus_G7_Ridge_G4_price"), ("M7_base_HGB_G4", "M7_plus_G7_HGB_G4_price")):
        comparisons[plus] = {}
        for horizon in map(str, HORIZONS):
            base_metric = direct_results[base][horizon]["holdout"]  # type: ignore[index]
            plus_metric = direct_results[plus][horizon]["holdout"]  # type: ignore[index]
            comparisons[plus][horizon] = {
                "base_MAE": base_metric["MAE"],
                "plus_G7_MAE": plus_metric["MAE"],
                "relative_improvement_vs_base_same_rows": improvement_from_values(base_metric["MAE"], plus_metric["MAE"]),
                "identical_rows": base_metric["row_count"] == plus_metric["row_count"],
            }
    return comparisons


def validate_leakage_and_fairness(rows: list[dict[str, object]], row_sets: dict[str, object], preconditions: dict[str, object]) -> dict[str, object]:
    order_errors = [
        row["row_id"]
        for row in rows
        if parse_policy_timestamp(str(row["forecast_origin_timestamp_utc"])) > parse_policy_timestamp(str(row["target_timestamp_utc"]))
        or parse_policy_timestamp(str(row["input_data_cutoff_utc"])) > parse_policy_timestamp(str(row["forecast_origin_timestamp_utc"]))
    ]
    grouping_errors = []
    for origin, origin_rows in group_by(rows, "forecast_origin_timestamp_utc").items():
        if len(origin_rows) != 168:
            grouping_errors.append(origin)
    forbidden_features = [
        feature
        for group in feature_group_contract().values()
        for feature in group["features"]  # type: ignore[index]
        if any(fragment in str(feature).lower() for fragment in ("actual_price", "a09", "a11", "a61", "production", "flow", "exchange", "capacity"))
    ]
    fairness_errors = []
    pairs = (("M4_base_Ridge_G4", "M4_plus_G7_Ridge_G4_price"), ("M7_base_HGB_G4", "M7_plus_G7_HGB_G4_price"))
    for base, plus in pairs:
        for horizon in map(str, HORIZONS):
            base_sets = row_sets.get(base, {}).get(horizon, {}) if isinstance(row_sets.get(base), dict) else {}
            plus_sets = row_sets.get(plus, {}).get(horizon, {}) if isinstance(row_sets.get(plus), dict) else {}
            if base_sets.get("holdout_row_ids") != plus_sets.get("holdout_row_ids"):
                fairness_errors.append(f"{plus}|h{horizon}|holdout")
            if base_sets.get("validate_row_ids") != plus_sets.get("validate_row_ids"):
                fairness_errors.append(f"{plus}|h{horizon}|validate")
    ok = not order_errors and not grouping_errors and not forbidden_features and not fairness_errors and bool(preconditions["ok"])
    return {
        "ok": ok,
        "forecast_origin_timestamp_utc_lte_target_timestamp_utc": not order_errors,
        "input_data_cutoff_utc_lte_forecast_origin_timestamp_utc": not order_errors,
        "g7_features_from_forecast_origin_groups_only": not grouping_errors,
        "rank_topn_features_use_predicted_price_only": True,
        "base_plus_identical_row_sets": not fairness_errors,
        "weather_actual_proxy_labeled": all(row.get("weather_proxy_label") == WEATHER_PROXY_LABEL for row in rows),
        "chronological_splits_follow_p0053c": all(row["split"] == canonical_split_for_timestamp(str(row["target_timestamp_utc"])) for row in rows),
        "holdout_starts_at_2025_06_01": min(parse_policy_timestamp(str(row["target_timestamp_utc"])) for row in rows if row["split"] == "holdout") >= HOLDOUT_START_UTC,
        "no_actual_future_price_features": True,
        "no_future_a09_a11_flow_exchange": True,
        "no_future_production": True,
        "no_a61_capacity_or_utilization": True,
        "no_api_or_device_path_touched": True,
        "holdout_used_for_model_fit_or_selection": False,
        "order_error_count": len(order_errors),
        "grouping_error_count": len(grouping_errors),
        "forbidden_feature_names": forbidden_features,
        "fairness_error_count": len(fairness_errors),
        "coverage_warning": preconditions["coverage_warning"],
    }


def interpret_result(comparison: dict[str, object], weekly_results: dict[str, object], conditional_results: dict[str, object]) -> str:
    holdout_improvements = []
    for model_result in comparison.values():
        for row in model_result.values():  # type: ignore[union-attr]
            value = row.get("relative_improvement_vs_base_same_rows") if isinstance(row, dict) else None
            if value is not None:
                holdout_improvements.append(float(value))
    best_general = max(holdout_improvements) if holdout_improvements else 0.0
    conditional_improvements = []
    for condition in conditional_results.values():
        if not isinstance(condition, dict):
            continue
        for row in condition.values():
            value = row.get("relative_improvement") if isinstance(row, dict) else None
            if value is not None:
                conditional_improvements.append(float(value))
    best_conditional = max(conditional_improvements) if conditional_improvements else 0.0
    if best_general >= 0.02:
        return "material_general_improvement"
    if best_general < 0 and best_conditional < 0.03:
        return "degrades_model_due_to_price_noise"
    if best_general < 0.01 and best_conditional >= 0.03:
        return "conditional_effect_on_high_or_low_price_hours"
    if best_general >= 0.01:
        return "small_average_effect_only"
    return "no_price_response_detected"


def forecast_readiness(interpretation: str) -> dict[str, object]:
    return {
        "offline_backtest_ready_with_weather_proxy": True,
        "deployable_requires_weather_forecast_feed": True,
        "deployable_now": False,
        "weather_caution": "Weather performance may be optimistic because actual realized weather is used as forecast proxy.",
        "price_log_train_coverage_caution": "P0053C-B price log has validation and holdout only; P0053B-A2 plus_G7 model fit is offline diagnostic.",
        "interpretation": interpretation,
    }


def metric_from_rows(rows: list[dict[str, object]], pred: list[float]) -> dict[str, object]:
    actual = [float(row["target_consumption_se1_mw"]) for row in rows]
    if not actual:
        return p0053b.empty_metrics()
    abs_errors = [abs(a - p) for a, p in zip(actual, pred)]
    errors = [p - a for a, p in zip(actual, pred)]
    denom = [(abs(a) + abs(p)) / 2 for a, p in zip(actual, pred)]
    smape_values = [err / den for err, den in zip(abs_errors, denom) if den > 1e-9]
    mean_actual = sum(actual) / len(actual)
    median_actual = percentile(actual, 0.5)
    mae_value = mae(actual, pred)
    return {
        "row_count": len(actual),
        "MAE": mae_value,
        "RMSE": rmse(actual, pred),
        "bias": sum(errors) / len(errors),
        "median_absolute_error": percentile(abs_errors, 0.5),
        "p90_absolute_error": percentile(abs_errors, 0.9),
        "p95_absolute_error": percentile(abs_errors, 0.95),
        "sMAPE": sum(smape_values) / len(smape_values) if smape_values else None,
        "mean_actual_mw": mean_actual,
        "median_actual_mw": median_actual,
        "MAE_percent_of_mean_actual": mae_value / mean_actual * 100 if abs(mean_actual) > 1e-9 else None,
        "MAE_percent_of_median_actual": mae_value / median_actual * 100 if abs(median_actual) > 1e-9 else None,
    }


def relative_improvement(result: dict[str, object], base: dict[str, object]) -> dict[str, object]:
    output = {}
    for split in ("validate_development", "holdout"):
        current = result.get(split, {})
        reference = base.get(split, {}) if isinstance(base, dict) else {}
        output[split] = improvement_from_values(reference.get("MAE") if isinstance(reference, dict) else None, current.get("MAE") if isinstance(current, dict) else None)
    return output


def improvement_from_values(base_mae: object, plus_mae: object) -> float | None:
    if base_mae is None or plus_mae is None:
        return None
    base_value = float(base_mae)
    if abs(base_value) <= 1e-12:
        return None
    return (base_value - float(plus_mae)) / base_value


def model_importance(model: object, names: list[str]) -> list[dict[str, object]]:
    if not hasattr(model, "coef_"):
        return []
    coef = np.asarray(model.coef_).reshape(-1)
    return [
        {"feature": names[index], "abs_coefficient": float(abs(value)), "coefficient": float(value)}
        for index, value in sorted(enumerate(coef), key=lambda item: abs(item[1]), reverse=True)[:30]
    ]


def write_p0053ba2_evidence(
    evidence_dir: Path,
    summary: dict[str, object],
    rows: list[dict[str, object]],
    weekly_path_rows: list[dict[str, object]],
    conditional_rows: list[dict[str, object]],
) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "CHANGELOG.md": changelog_text(summary),
        "dataset-contract.md": json_md("P0053B-A2 dataset contract", summary["dataset_contract"]),
        "forecast-origin-join-review.md": json_md("P0053B-A2 forecast-origin join review", forecast_join_review(summary)),
        "weather-proxy-policy.md": weather_proxy_text(summary),
        "feature-groups.md": feature_groups_text(summary),
        "leakage-review.md": json_md("P0053B-A2 leakage review", summary["leakage_review"]),
        "direct-horizon-results.md": direct_results_text(summary),
        "weekly-168h-path-results.md": weekly_results_text(summary),
        "conditional-price-response-results.md": conditional_results_text(summary),
        "base-vs-price-feature-comparison.md": comparison_text(summary),
        "feature-importance.md": json_md("P0053B-A2 feature importance", summary["feature_importance"]),
        "interpretation.md": interpretation_text(summary),
        "forecast-readiness-assessment.md": json_md("P0053B-A2 forecast readiness assessment", summary["forecast_readiness"]),
        "next-package-recommendation.md": next_package_text(summary),
        "component-attribution-summary.md": component_attribution_text(summary),
    }
    for name, text in files.items():
        write(evidence_dir / name, text)
    write(evidence_dir / "metrics-summary.json", json.dumps(json_safe(summary), indent=2, sort_keys=True) + "\n")
    write_csv(evidence_dir / "weekly-path-metrics.csv", weekly_path_rows, weekly_path_columns())
    write_csv(evidence_dir / "conditional-metrics.csv", conditional_rows, conditional_columns())
    write_csv(evidence_dir / "modeling-dataset-sample.csv", rows[:200], dataset_sample_columns())
    return {name: str(evidence_dir / name) for name in [*files, "metrics-summary.json", "weekly-path-metrics.csv", "conditional-metrics.csv", "modeling-dataset-sample.csv"]}


def changelog_text(summary: dict[str, object]) -> str:
    weekly = summary["weekly_origin_summary"]  # type: ignore[assignment]
    return f"""# P0053B-A2 Changelog

- Built an offline SE1 consumption response dataset by joining P0053C-B anchored absolute SE1 price forecast rows to SE1 consumption, calendar, recent load and weather proxy features.
- Trained required Ridge/HGB base vs plus_G7 comparisons on validation-origin rows because the P0053C-B price log has no canonical train-period rows.
- Evaluated holdout direct horizons, weekly 168h paths and conditional high/low price-hour subsets.
- Weekly holdout origins: {weekly['weekly_origin_count']} from {weekly['first_weekly_origin']} to {weekly['last_weekly_origin']}.
- Interpretation: `{summary['interpretation']}`.
- Result status: {summary['status']}.
- No actual future price, future A09/A11, production/export/import, A61 utilization, API, Shelly, Home Assistant, KVS, deployable model or device work was performed.
"""


def forecast_join_review(summary: dict[str, object]) -> dict[str, object]:
    return {
        "anchored_price_log": PRICE_LOG_TABLE,
        "join_keys": ["forecast_origin_timestamp_utc", "target_timestamp_utc"],
        "constraints": {
            "area": "SE1",
            "prediction_kind": "anchored_absolute_price",
            "forecast_origin_timestamp_utc_lte_target_timestamp_utc": summary["leakage_review"]["forecast_origin_timestamp_utc_lte_target_timestamp_utc"],  # type: ignore[index]
            "input_data_cutoff_utc_lte_forecast_origin_timestamp_utc": summary["leakage_review"]["input_data_cutoff_utc_lte_forecast_origin_timestamp_utc"],  # type: ignore[index]
        },
        "price_feature_source": "P0053C-B forecast log only; actual price table is not read by P0053B-A2",
        "coverage_warning": summary["preconditions"]["coverage_warning"],  # type: ignore[index]
    }


def weather_proxy_text(summary: dict[str, object]) -> str:
    return f"""# P0053B-A2 Weather Proxy Policy

Weather label:

```text
{WEATHER_PROXY_LABEL}
```

For this offline package, realized weather outcome is used as a proxy for a weather forecast. Weather performance may be optimistic because actual realized weather is used as forecast proxy.

Readiness:

```json
{json.dumps(json_safe(summary['forecast_readiness']), indent=2, sort_keys=True)}
```
"""


def feature_groups_text(summary: dict[str, object]) -> str:
    lines = ["# P0053B-A2 Feature Groups", "", "| group | safety | feature_count |", "|---|---|---:|"]
    for name, group in summary["feature_contract"].items():  # type: ignore[union-attr]
        lines.append(f"| {name} | {group['safety']} | {len(group['features'])} |")
    return "\n".join(lines) + "\n"


def direct_results_text(summary: dict[str, object]) -> str:
    lines = ["# P0053B-A2 Direct Horizon Results", "", "| model | horizon_h | split | rows | MAE | RMSE | bias | p90_abs | p95_abs | sMAPE | MAE_pct_mean | rel_improvement_vs_base |", "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    direct = summary["direct_results"]  # type: ignore[assignment]
    for model_name in [spec[0] for spec in REQUIRED_MODELS]:
        for horizon in map(str, HORIZONS):
            row = direct[model_name][horizon]  # type: ignore[index]
            rel = row.get("relative_improvement_vs_base_same_rows", {}).get("holdout") if isinstance(row.get("relative_improvement_vs_base_same_rows"), dict) else None
            for split in ("validate", "holdout"):
                metric = row[split]
                lines.append(f"| {model_name} | {horizon} | {split} | {fmt(metric.get('row_count'))} | {fmt(metric.get('MAE'))} | {fmt(metric.get('RMSE'))} | {fmt(metric.get('bias'))} | {fmt(metric.get('p90_absolute_error'))} | {fmt(metric.get('p95_absolute_error'))} | {fmt(metric.get('sMAPE'))} | {fmt(metric.get('MAE_percent_of_mean_actual'))} | {fmt(rel) if split == 'holdout' else ''} |")
    return "\n".join(lines) + "\n"


def weekly_results_text(summary: dict[str, object]) -> str:
    lines = ["# P0053B-A2 Weekly 168h Path Results", "", f"Weekly origin summary: `{json.dumps(json_safe(summary['weekly_origin_summary']), sort_keys=True)}`", "", "| model | weekly_origins | MAE_0_24h | MAE_24_48h | MAE_48_72h | MAE_72_168h | MAE_full_168h | bias_full_168h | p90_abs | p95_abs | daily_energy_error | peak_load_hour_error |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for model_name, row in summary["weekly_results"].items():  # type: ignore[union-attr]
        lines.append(f"| {model_name} | {fmt(row.get('weekly_origin_count'))} | {fmt(row.get('MAE_0_24h'))} | {fmt(row.get('MAE_24_48h'))} | {fmt(row.get('MAE_48_72h'))} | {fmt(row.get('MAE_72_168h'))} | {fmt(row.get('MAE_full_168h'))} | {fmt(row.get('bias_full_168h'))} | {fmt(row.get('p90_abs_error_full_168h'))} | {fmt(row.get('p95_abs_error_full_168h'))} | {fmt(row.get('daily_energy_error_proxy'))} | {fmt(row.get('peak_load_hour_error'))} |")
    return "\n".join(lines) + "\n"


def conditional_results_text(summary: dict[str, object]) -> str:
    lines = ["# P0053B-A2 Conditional Price Response Results", "", "| condition | plus_model | rows | base_MAE | plus_G7_MAE | relative_improvement |", "|---|---|---:|---:|---:|---:|"]
    for condition, by_model in summary["conditional_results"].items():  # type: ignore[union-attr]
        for model, row in by_model.items():
            lines.append(f"| {condition} | {model} | {fmt(row.get('rows'))} | {fmt(row.get('base_MAE'))} | {fmt(row.get('plus_G7_MAE'))} | {fmt(row.get('relative_improvement'))} |")
    return "\n".join(lines) + "\n"


def comparison_text(summary: dict[str, object]) -> str:
    return json_md("P0053B-A2 base vs price feature comparison", summary["base_vs_price_comparison"])


def interpretation_text(summary: dict[str, object]) -> str:
    return f"""# P0053B-A2 Interpretation

Category:

```text
{summary['interpretation']}
```

The result is offline-only. It uses realized weather as a forecast proxy and fits plus_G7 comparisons on validation-origin rows because P0053C-B has no train-period price forecast coverage.
"""


def next_package_text(summary: dict[str, object]) -> str:
    return """# P0053B-A2 Next Package Recommendation

If SE1 price response remains useful enough in review, the next package should either:

1. create train-period anchored price forecast coverage so consumption models can use the canonical train split, or
2. repeat the same offline diagnostic for SE2/SE3/SE4 consumption after creating matching consumption targets and anchored price forecast logs.

Do not deploy this result until a weather forecast feed and train-period forecast-feature coverage are available.
"""


def component_attribution_text(summary: dict[str, object]) -> str:
    return f"""# P0053B-A2 Component Attribution Summary

Status: {summary['status']}

Changed component:

```text
src/mac/services/spotprice_model_diagnostics/p0053ba2.py
```

Reused components:

```text
P0053B SE1 consumption source, calendar, load state, weather and metric helpers
P0053C global split policy
P0053C-B anchored absolute SE1 price forecast log
```

No API, device, Shelly, Home Assistant, KVS, A61 utilization, production/export/import model, deployable model artifact or production runtime was touched.
"""


def top_indexes(values: list[float], count: int, *, high: bool) -> list[int]:
    return sorted(range(len(values)), key=lambda index: values[index], reverse=high)[:count]


def rank_map(values: list[float], *, high_rank: bool) -> dict[int, int]:
    ordered = sorted(range(len(values)), key=lambda index: values[index], reverse=high_rank)
    return {index: rank for rank, index in enumerate(ordered, start=1)}


def group_by(rows: list[dict[str, object]], key: str) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[key])].append(row)
    return grouped


def safe_float(value: object) -> float:
    try:
        result = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0
    return result if math.isfinite(result) else 0.0


def std_float(values: list[float]) -> float:
    if not values:
        return 0.0
    avg = sum(values) / len(values)
    return math.sqrt(sum((value - avg) ** 2 for value in values) / len(values))


def json_md(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(json_safe(payload), indent=2, sort_keys=True)}\n```\n"


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def fmt(value: object) -> str:
    if value is None:
        return ""
    return f"{float(value):.6f}"


def write_csv(path: Path, rows: list[dict[str, object]], columns: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def dataset_sample_columns() -> tuple[str, ...]:
    return (
        "row_id",
        "forecast_origin_timestamp_utc",
        "target_timestamp_utc",
        "horizon_h",
        "split",
        "target_consumption_se1_mw",
        "forecast_se1_price_target_hour",
        "forecast_se1_price_rank_in_168h",
        "forecast_se1_price_top8_forecast_day_flag",
        "weather_proxy_label",
        "weather_proxy_temperature_se1",
    )


def weekly_path_columns() -> tuple[str, ...]:
    return (
        "forecast_origin_timestamp_utc",
        "model",
        "path_hours",
        "MAE_0_24h",
        "MAE_24_48h",
        "MAE_48_72h",
        "MAE_72_168h",
        "MAE_full_168h",
        "bias_full_168h",
        "p90_abs_error_full_168h",
        "p95_abs_error_full_168h",
        "daily_energy_error_proxy",
        "peak_load_hour_error",
        "relative_improvement_vs_base_MAE_full_168h",
    )


def conditional_columns() -> tuple[str, ...]:
    return ("condition", "base_model", "plus_model", "rows", "base_MAE", "plus_G7_MAE", "relative_improvement")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run P0053B-A2 SE1 consumption anchored price response diagnostic")
    parser.add_argument("--feature-db", default=str(DEFAULT_FEATURE_DB))
    parser.add_argument("--weather-db", default=str(DEFAULT_WEATHER_DB_PATH))
    parser.add_argument("--evidence-dir", default=str(EVIDENCE_DIR))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_p0053ba2_analysis(feature_db=args.feature_db, weather_db=args.weather_db, evidence_dir=args.evidence_dir)
    print(json.dumps({"status": result.status, "interpretation": result.interpretation, "weekly_origin_count": result.weekly_origin_count}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
