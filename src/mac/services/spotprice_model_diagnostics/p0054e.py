"""P0054E LABB SE4 LightGBM/XGBoost comparison."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import csv
import importlib
import importlib.metadata as importlib_metadata
import json
import platform
import subprocess
import sys
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054d
from src.mac.services.spotprice_model_diagnostics.forecast_period_policy import policy_summary
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0054E"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054E")
FEATURE_GROUP = "G4_calendar_load_lags_rollups_weather_proxy"
P0054D_SUMMARY_PATH = Path("requirements/package-runs/P0054D/summary.json")
INTERESTING_DIRECT_OR_WEEKLY_THRESHOLD_PERCENT = -2.0
INTERESTING_CONDITIONAL_THRESHOLD_PERCENT = -3.0
LIGHTGBM_MODEL_NAME = "LightGBM_G4_se4_load_weather"
XGBOOST_MODEL_NAME = "XGBoost_G4_se4_load_weather"
EXTRATREES_MODEL_NAME = "ExtraTrees_G4_se4_load_weather"
MODEL_TO_COLUMN = {
    EXTRATREES_MODEL_NAME: "pred_ExtraTrees_G4_calendar_load_lags_rollups_weather_proxy",
    LIGHTGBM_MODEL_NAME: "pred_LightGBM_G4_calendar_load_lags_rollups_weather_proxy",
    XGBOOST_MODEL_NAME: "pred_XGBoost_G4_calendar_load_lags_rollups_weather_proxy",
}
MODEL_ORDER = (EXTRATREES_MODEL_NAME, LIGHTGBM_MODEL_NAME, XGBOOST_MODEL_NAME)


@dataclass(frozen=True)
class ModelSpec:
    name: str
    model_class: str
    model: object
    package: str
    hyperparameters: dict[str, object]


@dataclass(frozen=True)
class P0054EResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054e_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054EResult:
    started = time.monotonic()
    environment = capture_environment_status()
    source_rows = p0054d.load_se4_consumption_rows(feature_db)
    target_contract = p0054d.validate_target_contract(source_rows)
    if not target_contract["ok"]:
        raise RuntimeError(f"P0054E target contract failed: {target_contract}")

    weather_rows, weather_contract = p0054d.load_weather_proxy_rows(weather_db)
    rows = p0054d.build_direct_horizon_rows(source_rows, weather_rows, p0054d.HORIZONS)
    path_candidate_rows = p0054d.build_weekly_path_candidate_rows(source_rows, weather_rows)
    split_counts = p0054d.assign_global_splits(rows)
    p0054d.assign_global_splits(path_candidate_rows)
    profiles = p0054d.fit_train_profiles([row for row in rows if row["split"] == "train"])
    p0054d.apply_profile_features(rows, profiles)
    p0054d.apply_profile_features(path_candidate_rows, profiles)

    feature_contract = p0054d.feature_group_contract()
    feature_review = p0054d.validate_feature_contract(feature_contract)
    if not feature_review["ok"]:
        raise RuntimeError(f"P0054E forbidden feature contract failed: {feature_review}")
    features = feature_contract[FEATURE_GROUP]["features"]  # type: ignore[index]

    specs = optional_model_specs(environment["imports"])  # type: ignore[arg-type]
    if len(specs) <= 1:
        raise RuntimeError(f"P0054E requires LightGBM or XGBoost beyond ExtraTrees: {environment['imports']}")

    model_results: dict[str, dict[str, object]] = {}
    for spec in specs:
        model_results[spec.name] = fit_p0054e_model(rows, features, spec)  # type: ignore[arg-type]

    scored_rows = attach_named_predictions(rows, model_results)
    scored_path_rows = attach_weekly_predictions(path_candidate_rows, model_results, features)  # type: ignore[arg-type]
    prediction_columns = tuple(MODEL_TO_COLUMN[spec.name] for spec in specs)
    direct_results = evaluate_direct_horizons(scored_rows, prediction_columns)
    weekly_summary, weekly_path_rows = evaluate_weekly_168h_paths(scored_path_rows, prediction_columns)
    conditional_results = evaluate_conditional_regimes(scored_rows, prediction_columns)
    fairness = validate_identical_row_sets(scored_rows, prediction_columns)
    p0054d_summary = load_p0054d_summary()
    comparison = compare_p0054e_models(model_results, weekly_summary, conditional_results, p0054d_summary)
    importances = feature_importance_or_attribution(model_results, features)
    status = "PASS" if fairness["ok"] and feature_review["ok"] and comparison["at_least_one_boosted_model_ran"] else "WARN"
    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "dataset_kind": p0054d.DATASET_KIND,
        "split_policy": policy_summary(),
        "source_table": p0054d.SOURCE_TABLE,
        "target": "consumption_se4_mw",
        "weather_table": p0054d.WEATHER_TABLE,
        "weather_area_proxy": p0054d.WEATHER_AREA_PROXY,
        "weather_proxy_label": p0054d.WEATHER_PROXY_LABEL,
        "environment": environment,
        "install_scope": "Mac-local LABB user-site Python packages plus Homebrew libomp runtime; not a G2 runtime dependency",
        "target_contract": target_contract,
        "weather_contract": weather_contract,
        "weather_proxy_definition": p0054d.weather_proxy_definition(),
        "feature_contract": feature_contract,
        "feature_review": feature_review,
        "split_counts": split_counts,
        "row_counts": {
            "source_rows": len(source_rows),
            "direct_horizon_rows": len(rows),
            "path_candidate_rows": len(path_candidate_rows),
            "weekly_path_origins": int(weekly_summary["weekly_origin_count"]),
        },
        "model_training": {name: result["training"] for name, result in model_results.items()},
        "model_results": {name: result["metrics"] for name, result in model_results.items()},
        "model_comparison": comparison,
        "direct_horizon_results": direct_results,
        "weekly_168h_path_results": weekly_summary,
        "conditional_regime_results": conditional_results,
        "feature_importance_or_attribution": importances,
        "fairness": fairness,
        "runtime_seconds": round(time.monotonic() - started, 3),
    }
    evidence = write_p0054e_evidence(Path(evidence_dir), scored_rows, weekly_path_rows, summary)
    return P0054EResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def capture_environment_status() -> dict[str, object]:
    return {
        "python": {
            "executable": sys.executable,
            "version": sys.version.replace("\n", " "),
            "prefix": sys.prefix,
            "base_prefix": sys.base_prefix,
            "venv": sys.prefix != sys.base_prefix or bool(getattr(sys, "real_prefix", "")),
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "pip": pip_version(),
        "packages": {name: package_version(name) for name in ("numpy", "scipy", "scikit-learn", "lightgbm", "xgboost")},
        "libomp": brew_libomp_version(),
        "imports": {name: import_status(name) for name in ("lightgbm", "xgboost")},
    }


def pip_version() -> str:
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], check=False, capture_output=True, text=True)
    except OSError as exc:
        return f"unavailable: {exc}"
    return result.stdout.strip() or result.stderr.strip()


def brew_libomp_version() -> str:
    try:
        result = subprocess.run(["brew", "list", "--versions", "libomp"], check=False, capture_output=True, text=True)
    except OSError as exc:
        return f"unavailable: {exc}"
    return result.stdout.strip() or result.stderr.strip() or "not_installed"


def package_version(package_name: str) -> str:
    try:
        return importlib_metadata.version(package_name)
    except importlib_metadata.PackageNotFoundError:
        return "not_installed"


def import_status(module_name: str) -> dict[str, object]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # noqa: BLE001 - evidence should capture exact optional import failure.
        return {"ok": False, "error_type": type(exc).__name__, "error": str(exc)}
    return {"ok": True, "version": str(getattr(module, "__version__", package_version(module_name)))}


def optional_model_specs(imports: dict[str, dict[str, object]]) -> list[ModelSpec]:
    from sklearn.ensemble import ExtraTreesRegressor

    specs = [
        ModelSpec(
            name=EXTRATREES_MODEL_NAME,
            model_class="ExtraTreesRegressor",
            package="scikit-learn",
            model=ExtraTreesRegressor(
                n_estimators=180,
                max_features=0.75,
                min_samples_leaf=4,
                max_samples=0.80,
                bootstrap=True,
                n_jobs=-1,
                random_state=p0054d.RANDOM_SEED,
            ),
            hyperparameters={
                "n_estimators": 180,
                "max_features": 0.75,
                "min_samples_leaf": 4,
                "max_samples": 0.80,
                "bootstrap": True,
                "n_jobs": -1,
                "random_state": p0054d.RANDOM_SEED,
            },
        )
    ]
    if imports.get("lightgbm", {}).get("ok"):
        from lightgbm import LGBMRegressor

        specs.append(
            ModelSpec(
                name=LIGHTGBM_MODEL_NAME,
                model_class="LGBMRegressor",
                package="lightgbm",
                model=LGBMRegressor(
                    objective="regression_l1",
                    metric="mae",
                    n_estimators=650,
                    learning_rate=0.045,
                    num_leaves=63,
                    min_child_samples=80,
                    subsample=0.85,
                    subsample_freq=1,
                    colsample_bytree=0.85,
                    reg_lambda=0.2,
                    random_state=p0054d.RANDOM_SEED,
                    n_jobs=-1,
                    verbose=-1,
                ),
                hyperparameters={
                    "objective": "regression_l1",
                    "metric": "mae",
                    "n_estimators": 650,
                    "learning_rate": 0.045,
                    "num_leaves": 63,
                    "min_child_samples": 80,
                    "subsample": 0.85,
                    "subsample_freq": 1,
                    "colsample_bytree": 0.85,
                    "reg_lambda": 0.2,
                    "random_state": p0054d.RANDOM_SEED,
                    "n_jobs": -1,
                },
            )
        )
    if imports.get("xgboost", {}).get("ok"):
        from xgboost import XGBRegressor

        specs.append(
            ModelSpec(
                name=XGBOOST_MODEL_NAME,
                model_class="XGBRegressor",
                package="xgboost",
                model=XGBRegressor(
                    objective="reg:squarederror",
                    eval_metric="mae",
                    n_estimators=650,
                    learning_rate=0.045,
                    max_depth=7,
                    min_child_weight=8,
                    subsample=0.85,
                    colsample_bytree=0.85,
                    reg_lambda=1.0,
                    random_state=p0054d.RANDOM_SEED,
                    n_jobs=-1,
                    tree_method="hist",
                ),
                hyperparameters={
                    "objective": "reg:squarederror",
                    "eval_metric": "mae",
                    "n_estimators": 650,
                    "learning_rate": 0.045,
                    "max_depth": 7,
                    "min_child_weight": 8,
                    "subsample": 0.85,
                    "colsample_bytree": 0.85,
                    "reg_lambda": 1.0,
                    "random_state": p0054d.RANDOM_SEED,
                    "n_jobs": -1,
                    "tree_method": "hist",
                },
            )
        )
    return specs


def fit_p0054e_model(rows: list[dict[str, object]], features: list[str], spec: ModelSpec) -> dict[str, object]:
    started = time.monotonic()
    result = p0054d.fit_model(rows, features, spec.model, spec.model_class)
    result["training"] = {
        "model_name": spec.name,
        "model_class": spec.model_class,
        "package": spec.package,
        "feature_group": FEATURE_GROUP,
        "weather_proxy_name": p0054d.WEATHER_AREA_PROXY,
        "random_seed": p0054d.RANDOM_SEED,
        "hyperparameters": spec.hyperparameters,
        "training_duration_seconds": round(time.monotonic() - started, 3),
        "training_rows": sum(1 for row in rows if row["split"] == "train"),
        "validation_rows": sum(1 for row in rows if row["split"] == "validate"),
        "holdout_rows": sum(1 for row in rows if row["split"] == "holdout"),
        "model_artifact_persisted": False,
    }
    return result


def attach_named_predictions(rows: list[dict[str, object]], model_results: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    split_rows = {
        "validate": [row for row in rows if row["split"] == "validate"],
        "holdout": [row for row in rows if row["split"] == "holdout"],
    }
    for model_name, result in model_results.items():
        column = MODEL_TO_COLUMN[model_name]
        predictions = result["predictions"]  # type: ignore[assignment]
        for split, rows_for_split in split_rows.items():
            for row, prediction in zip(rows_for_split, predictions.get(split, [])):  # type: ignore[union-attr]
                row[column] = float(prediction)
    return rows


def attach_weekly_predictions(
    path_rows: list[dict[str, object]],
    model_results: dict[str, dict[str, object]],
    features: list[str],
) -> list[dict[str, object]]:
    for model_name, result in model_results.items():
        column = MODEL_TO_COLUMN[model_name]
        predictions = p0054d.predict_rows(result["model"], result["encoder"], path_rows, features)  # type: ignore[arg-type]
        for row, prediction in zip(path_rows, predictions):
            row[column] = float(prediction)
    return path_rows


def evaluate_direct_horizons(rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> dict[str, object]:
    return {
        column: {
            str(horizon): p0054d.metrics_by_split([row for row in rows if int(row["horizon_h"]) == horizon], column)
            for horizon in p0054d.HORIZONS
        }
        for column in prediction_columns
    }


def select_weekly_holdout_origins(scored_rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> dict[str, object]:
    complete = []
    skipped = []
    by_origin: dict[str, list[dict[str, object]]] = {}
    for row in scored_rows:
        if row.get("split") != "holdout":
            continue
        if p0052.parse_utc(str(row["forecast_origin_timestamp_utc"])) < p0052.parse_utc(p0054d.HOLDOUT_START):
            continue
        by_origin.setdefault(str(row["forecast_origin_timestamp_utc"]), []).append(row)
    for origin, rows in sorted(by_origin.items()):
        horizons = {int(row["horizon_h"]) for row in rows if all(row.get(column) is not None for column in prediction_columns)}
        if all(horizon in horizons for horizon in p0054d.PATH_HORIZONS):
            complete.append(origin)
        else:
            skipped.append({"forecast_origin_timestamp_utc": origin, "reason": "incomplete_168h_prediction_path", "available_horizons": len(horizons)})
    return {
        "complete_168h_path_count": len(complete),
        "weekly_origin_count": len(complete),
        "weekly_origins": complete,
        "first_weekly_origin": complete[0] if complete else "",
        "last_weekly_origin": complete[-1] if complete else "",
        "skipped_origins_with_reason": skipped,
    }


def evaluate_weekly_168h_paths(
    scored_rows: list[dict[str, object]],
    prediction_columns: tuple[str, ...],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    selection = select_weekly_holdout_origins(scored_rows, prediction_columns)
    weekly_set = set(selection["weekly_origins"])  # type: ignore[arg-type]
    rows = [
        row
        for row in scored_rows
        if str(row["forecast_origin_timestamp_utc"]) in weekly_set and 1 <= int(row["horizon_h"]) <= 168
    ]
    summary: dict[str, object] = dict(selection)
    path_rows = []
    for column in prediction_columns:
        summary[column] = p0054d.weekly_path_metric_summary(rows, column)
    for origin in selection["weekly_origins"]:  # type: ignore[union-attr]
        origin_rows = [row for row in rows if row["forecast_origin_timestamp_utc"] == origin]
        out = {"forecast_origin_timestamp_utc": origin, "row_count": len(origin_rows)}
        for column in prediction_columns:
            available = [row for row in origin_rows if row.get(column) is not None]
            out[f"{column}_MAE"] = p0054d.regression_metric_from_predictions(available, [float(row[column]) for row in available])["MAE"]
        path_rows.append(out)
    return summary, path_rows


def evaluate_conditional_regimes(rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> dict[str, object]:
    scored = [row for row in rows if all(row.get(column) is not None for column in prediction_columns)]
    temps = [p0054d.safe_float(row.get("weather_proxy_temperature_2m_se4")) for row in scored if p0054d.is_finite(row.get("weather_proxy_temperature_2m_se4"))]
    deltas = [
        p0054d.safe_float(row.get("weather_proxy_temperature_delta_from_train_normal_se4"))
        for row in scored
        if p0054d.is_finite(row.get("weather_proxy_temperature_delta_from_train_normal_se4"))
    ]
    temp_p25 = percentile(temps, 0.25) if temps else 0.0
    temp_p10 = percentile(temps, 0.1) if temps else 0.0
    delta_p10 = percentile(deltas, 0.1) if deltas else 0.0
    regimes = {
        "cold_hours_temperature_p25_or_lower": lambda row: p0054d.safe_float(row.get("weather_proxy_temperature_2m_se4")) <= temp_p25,
        "very_cold_hours_temperature_p10_or_lower": lambda row: p0054d.safe_float(row.get("weather_proxy_temperature_2m_se4")) <= temp_p10,
        "rapid_temperature_drop_proxy_p10_or_lower": lambda row: p0054d.safe_float(row.get("weather_proxy_temperature_delta_from_train_normal_se4")) <= delta_p10,
        "weekday": lambda row: int(row["is_weekend"]) == 0,
        "weekend": lambda row: int(row["is_weekend"]) == 1,
        "holiday": lambda row: int(row["is_holiday"]) == 1,
        "morning_ramp_06_09": lambda row: 6 <= int(row["target_model_cet_hour"]) <= 9,
        "evening_peak_16_20": lambda row: 16 <= int(row["target_model_cet_hour"]) <= 20,
        "summer_low_load_months": lambda row: int(row["target_month"]) in (6, 7, 8),
        "winter_high_load_months": lambda row: int(row["target_month"]) in (12, 1, 2),
    }
    return {
        name: {column: p0054d.metrics_by_split([row for row in scored if predicate(row)], column) for column in prediction_columns}
        for name, predicate in regimes.items()
    }


def validate_identical_row_sets(rows: list[dict[str, object]], prediction_columns: tuple[str, ...]) -> dict[str, object]:
    row_sets = {
        column: sorted(
            f"{row['forecast_origin_timestamp_utc']}|{row['target_timestamp_utc']}|{row['horizon_h']}"
            for row in rows
            if row.get(column) is not None
        )
        for column in prediction_columns
    }
    values = list(row_sets.values())
    return {
        "ok": bool(values) and all(value == values[0] for value in values),
        "row_counts": {column: len(ids) for column, ids in row_sets.items()},
        "weather_actual_proxy_labeled": all(row.get("weather_proxy_label") in (p0054d.WEATHER_PROXY_LABEL, "weather_proxy_missing") for row in rows),
    }


def load_p0054d_summary(path: Path = P0054D_SUMMARY_PATH) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def compare_p0054e_models(
    model_results: dict[str, dict[str, object]],
    weekly_summary: dict[str, object],
    conditional_results: dict[str, object],
    p0054d_summary: dict[str, object],
) -> dict[str, object]:
    direct = []
    weekly = []
    for model_name in MODEL_ORDER:
        if model_name not in model_results:
            continue
        holdout = model_results[model_name]["metrics"]["holdout"]  # type: ignore[index]
        direct.append({"model_name": model_name, "holdout_MAE": holdout["MAE"], "holdout_R2": holdout["R2"]})
        column = MODEL_TO_COLUMN[model_name]
        if column in weekly_summary:
            weekly.append({"model_name": model_name, "weekly_MAE_full_168h": weekly_summary[column]["MAE_full_168h"]})  # type: ignore[index]
    best_direct = min(direct, key=lambda row: float(row["holdout_MAE"])) if direct else {}
    best_weekly = min(weekly, key=lambda row: float(row["weekly_MAE_full_168h"])) if weekly else {}
    p0054d_extra = p0054d_summary.get("additional_advanced_model_results", {}).get("holdout", {}) if p0054d_summary else {}
    p0054d_weekly = p0054d_summary.get("weekly_168h_path_results", {}).get(p0054d.EXTRATREES_PREDICTION_COLUMN, {}) if p0054d_summary else {}
    same_run_extra_holdout = next((row for row in direct if row["model_name"] == EXTRATREES_MODEL_NAME), {})
    same_run_extra_weekly = next((row for row in weekly if row["model_name"] == EXTRATREES_MODEL_NAME), {})
    boosted_names = [name for name in (LIGHTGBM_MODEL_NAME, XGBOOST_MODEL_NAME) if name in model_results]
    comparisons = {}
    for model_name in boosted_names:
        model_direct = next(row for row in direct if row["model_name"] == model_name)
        model_weekly = next(row for row in weekly if row["model_name"] == model_name)
        comparisons[model_name] = {
            "same_run_minus_extratrees_holdout_MAE": float(model_direct["holdout_MAE"]) - float(same_run_extra_holdout["holdout_MAE"]),
            "same_run_relative_to_extratrees_holdout_MAE_percent": relative_change(float(model_direct["holdout_MAE"]), float(same_run_extra_holdout["holdout_MAE"])),
            "same_run_minus_extratrees_weekly_MAE_full_168h": float(model_weekly["weekly_MAE_full_168h"]) - float(same_run_extra_weekly["weekly_MAE_full_168h"]),
            "same_run_relative_to_extratrees_weekly_MAE_full_168h_percent": relative_change(
                float(model_weekly["weekly_MAE_full_168h"]), float(same_run_extra_weekly["weekly_MAE_full_168h"])
            ),
            "p0054d_extratrees_relative_holdout_MAE_percent": relative_change(float(model_direct["holdout_MAE"]), float(p0054d_extra.get("MAE", same_run_extra_holdout["holdout_MAE"]))),
            "p0054d_extratrees_relative_weekly_MAE_full_168h_percent": relative_change(
                float(model_weekly["weekly_MAE_full_168h"]),
                float(p0054d_weekly.get("MAE_full_168h", same_run_extra_weekly["weekly_MAE_full_168h"])),
            ),
        }
    conditional_improvements = conditional_improvement_summary(conditional_results)
    beats_p0054d_by_threshold = [
        name
        for name, comparison in comparisons.items()
        if comparison["p0054d_extratrees_relative_holdout_MAE_percent"] <= INTERESTING_DIRECT_OR_WEEKLY_THRESHOLD_PERCENT
        or comparison["p0054d_extratrees_relative_weekly_MAE_full_168h_percent"] <= INTERESTING_DIRECT_OR_WEEKLY_THRESHOLD_PERCENT
    ]
    return {
        "comparison_type": "same-run for ExtraTrees/LightGBM/XGBoost; P0054D ExtraTrees included as evidence-summary baseline",
        "direct_holdout": direct,
        "weekly_168h": weekly,
        "best_model_by_direct_holdout_MAE": best_direct,
        "best_model_by_weekly_MAE_full_168h": best_weekly,
        "p0054d_extratrees_baseline": {
            "holdout_MAE": p0054d_extra.get("MAE"),
            "weekly_MAE_full_168h": p0054d_weekly.get("MAE_full_168h"),
        },
        "boosted_vs_extratrees": comparisons,
        "conditional_improvement_summary": conditional_improvements,
        "models_beating_p0054d_extratrees_by_at_least_2_percent_holdout_or_weekly": beats_p0054d_by_threshold,
        "at_least_one_boosted_model_ran": bool(boosted_names),
        "learning_threshold": {
            "direct_or_weekly_percent": INTERESTING_DIRECT_OR_WEEKLY_THRESHOLD_PERCENT,
            "conditional_percent": INTERESTING_CONDITIONAL_THRESHOLD_PERCENT,
        },
        "interpretation_category": interpretation_category(beats_p0054d_by_threshold, conditional_improvements),
    }


def conditional_improvement_summary(conditional_results: dict[str, object]) -> dict[str, object]:
    output: dict[str, object] = {}
    extra_column = MODEL_TO_COLUMN[EXTRATREES_MODEL_NAME]
    for regime_name, regime_values in conditional_results.items():
        regime_out = {}
        extra_holdout = regime_values[extra_column]["holdout"]["MAE"]  # type: ignore[index]
        for model_name in (LIGHTGBM_MODEL_NAME, XGBOOST_MODEL_NAME):
            column = MODEL_TO_COLUMN[model_name]
            if column not in regime_values:
                continue
            model_holdout = regime_values[column]["holdout"]["MAE"]  # type: ignore[index]
            regime_out[model_name] = {
                "holdout_MAE": model_holdout,
                "relative_to_extratrees_holdout_MAE_percent": relative_change(float(model_holdout), float(extra_holdout)) if extra_holdout else None,
            }
        output[regime_name] = regime_out
    interesting = {}
    for model_name in (LIGHTGBM_MODEL_NAME, XGBOOST_MODEL_NAME):
        wins = [
            regime_name
            for regime_name, regime_values in output.items()
            if model_name in regime_values
            and regime_values[model_name]["relative_to_extratrees_holdout_MAE_percent"] is not None  # type: ignore[index]
            and regime_values[model_name]["relative_to_extratrees_holdout_MAE_percent"] <= INTERESTING_CONDITIONAL_THRESHOLD_PERCENT  # type: ignore[index]
        ]
        interesting[model_name] = {"regimes_improved_by_at_least_3_percent": wins, "count": len(wins)}
    return {"by_regime": output, "interesting": interesting}


def interpretation_category(beats_threshold: list[str], conditional_summary: dict[str, object]) -> str:
    if beats_threshold:
        return "candidate_for_followup"
    interesting = conditional_summary.get("interesting", {})
    for item in interesting.values():  # type: ignore[union-attr]
        if int(item.get("count", 0)) >= 2:
            return "candidate_for_followup"
    return "no_effect_detected"


def feature_importance_or_attribution(model_results: dict[str, dict[str, object]], features: list[str]) -> dict[str, object]:
    output = {}
    for model_name, result in model_results.items():
        model = result["model"]
        names = result["features"]
        importances = getattr(model, "feature_importances_", None)
        if importances is None:
            output[model_name] = {"available": False, "reason": "model_has_no_feature_importances_attribute"}
            continue
        ranked = sorted(
            [{"feature": feature, "importance": float(importance)} for feature, importance in zip(names, importances)],
            key=lambda row: abs(float(row["importance"])),
            reverse=True,
        )
        output[model_name] = {"available": True, "method": "model_feature_importances_", "top": ranked[:25]}
    output["feature_group"] = features
    return output


def relative_change(value: float, baseline: float) -> float | None:
    if abs(baseline) < 1e-9:
        return None
    return (value - baseline) / baseline * 100


def write_p0054e_evidence(
    evidence_dir: Path,
    scored_rows: list[dict[str, object]],
    weekly_path_rows: list[dict[str, object]],
    summary: dict[str, object],
) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}
    files["metrics_summary_json"] = write_json(evidence_dir / "metrics-summary.json", summary)
    files["modeling_dataset_sample_csv"] = write_csv(
        evidence_dir / "modeling-dataset-sample.csv",
        scored_rows[:5000],
        direct_output_columns(summary),
    )
    files["weekly_path_metrics_csv"] = write_csv(
        evidence_dir / "weekly-path-metrics.csv",
        weekly_path_rows,
        list(weekly_path_rows[0].keys()) if weekly_path_rows else [],
    )
    files["conditional_metrics_csv"] = write_csv(evidence_dir / "conditional-metrics.csv", flatten_conditional_rows(summary), conditional_columns())
    for filename, content in evidence_markdowns(summary).items():
        files[filename] = str(write(evidence_dir / filename, content))
    return files


def evidence_markdowns(summary: dict[str, object]) -> dict[str, str]:
    comparison = summary["model_comparison"]  # type: ignore[index]
    common = f"# {PACKAGE_ID} {LABEL}\n\n"
    return {
        "CHANGELOG.md": common
        + "Installed/imported LightGBM and XGBoost LABB dependencies, reran the corrected SE4 no-price consumption experiment with `se4_load_weather`, and compared ExtraTrees, LightGBM and XGBoost. No runtime, device, price, production, flow/export/import or A61 inputs were used.\n",
        "labb-label.md": common + "This package is LABB only. It is not G2-KANDIDAT and creates no deployable model artifact.\n",
        "dataset-contract.md": common + json_block(summary["target_contract"]),
        "input-classification.md": common
        + json_block(
            {
                "calendar": "forecast_safe",
                "historical_se4_load_lags_rollups": "forecast_safe",
                "weather": "proxy",
                "weather_proxy_label": p0054d.WEATHER_PROXY_LABEL,
                "spot_price": "excluded_leakage",
                "production_flow_export_import_a61": "excluded_leakage",
            }
        ),
        "feature-groups.md": common + json_block(summary["feature_contract"]),
        "model-training-evidence.md": common + json_block({"environment": summary["environment"], "training": summary["model_training"]}),
        "lightgbm-results.md": common + model_result_block(summary, LIGHTGBM_MODEL_NAME),
        "xgboost-results.md": common + model_result_block(summary, XGBOOST_MODEL_NAME),
        "model-comparison.md": common + json_block(comparison),
        "direct-horizon-results.md": common + json_block(summary["direct_horizon_results"]),
        "weekly-168h-path-results.md": common + json_block(summary["weekly_168h_path_results"]),
        "conditional-regime-results.md": common + json_block(summary["conditional_regime_results"]),
        "feature-importance-or-attribution.md": common + json_block(summary["feature_importance_or_attribution"]),
        "interpretation.md": common + interpretation_text(summary),
        "what-we-learned.md": common + what_we_learned_text(summary),
        "next-package-recommendation.md": common + next_package_text(summary),
    }


def model_result_block(summary: dict[str, object], model_name: str) -> str:
    if model_name not in summary["model_results"]:  # type: ignore[operator]
        return json_block({"ran": False, "reason": "model_not_importable_or_not_selected"})
    return json_block({"training": summary["model_training"][model_name], "metrics": summary["model_results"][model_name]})  # type: ignore[index]


def interpretation_text(summary: dict[str, object]) -> str:
    comparison = summary["model_comparison"]  # type: ignore[index]
    best_direct = comparison["best_model_by_direct_holdout_MAE"]  # type: ignore[index]
    best_weekly = comparison["best_model_by_weekly_MAE_full_168h"]  # type: ignore[index]
    boosted = comparison["boosted_vs_extratrees"]  # type: ignore[index]
    return (
        f"Best direct holdout model: `{best_direct.get('model_name')}` with MAE `{best_direct.get('holdout_MAE')}`.\n\n"
        f"Best weekly 168h model: `{best_weekly.get('model_name')}` with MAE `{best_weekly.get('weekly_MAE_full_168h')}`.\n\n"
        "LightGBM/XGBoost versus ExtraTrees:\n\n"
        + json_block(boosted)
        + "\nThis is LABB evidence with realized weather used as `weather_actual_as_forecast_proxy`; it is not deployable candidate evidence.\n"
    )


def what_we_learned_text(summary: dict[str, object]) -> str:
    comparison = summary["model_comparison"]  # type: ignore[index]
    category = comparison["interpretation_category"]  # type: ignore[index]
    if category == "candidate_for_followup":
        return "At least one boosted model passed the LABB learning threshold versus P0054D ExtraTrees. Further bounded tuning or stricter forecast-safe reruns are justified before any candidate discussion.\n"
    return "LightGBM/XGBoost did not clear the P0054E LABB learning threshold versus the corrected P0054D ExtraTrees baseline. The result argues against broad SE4 consumption model work unless a later package tests a more specific hypothesis.\n"


def next_package_text(summary: dict[str, object]) -> str:
    category = summary["model_comparison"]["interpretation_category"]  # type: ignore[index]
    if category == "candidate_for_followup":
        return "Recommended next package: P0054F bounded tuned boosting on validation only, still LABB, with no runtime promotion.\n"
    return "Recommended next package: return to the P0054A recommendation and open an advanced AI LABB for SE3-SE1 spread/flaskhalsregimer rather than continuing generic SE4 consumption modeling.\n"


def direct_output_columns(summary: dict[str, object]) -> list[str]:
    columns = [
        "forecast_origin_timestamp_utc",
        "input_data_cutoff_utc",
        "target_timestamp_utc",
        "horizon_h",
        "split",
        p0054d.TARGET_FIELD,
        "weather_proxy_label",
    ]
    columns.extend(MODEL_TO_COLUMN[name] for name in MODEL_ORDER if name in summary["model_results"])  # type: ignore[operator]
    return columns


def flatten_conditional_rows(summary: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for regime, regime_values in summary["conditional_regime_results"].items():  # type: ignore[union-attr]
        for column, split_values in regime_values.items():
            model_name = next((name for name, model_column in MODEL_TO_COLUMN.items() if model_column == column), column)
            holdout = split_values["holdout"]
            rows.append(
                {
                    "regime": regime,
                    "model_name": model_name,
                    "holdout_row_count": holdout["row_count"],
                    "holdout_MAE": holdout["MAE"],
                    "holdout_RMSE": holdout["RMSE"],
                    "holdout_bias": holdout["bias"],
                    "holdout_R2": holdout["R2"],
                }
            )
    return rows


def conditional_columns() -> list[str]:
    return ["regime", "model_name", "holdout_row_count", "holdout_MAE", "holdout_RMSE", "holdout_bias", "holdout_R2"]


def write_json(path: Path, payload: object) -> str:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return str(path)


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> str:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column) for column in columns})
    return str(path)


def json_block(value: object) -> str:
    return "```json\n" + json.dumps(value, indent=2, sort_keys=True, default=str) + "\n```\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feature-db", type=Path, default=DEFAULT_FEATURE_DB)
    parser.add_argument("--weather-db", type=Path, default=DEFAULT_WEATHER_DB_PATH)
    parser.add_argument("--evidence-dir", type=Path, default=EVIDENCE_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_p0054e_analysis(feature_db=args.feature_db, weather_db=args.weather_db, evidence_dir=args.evidence_dir)
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
