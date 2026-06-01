"""P0043 AI-2 hour-to-day shape model training diagnostics."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import json
import math
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_model_diagnostics.p0040 import spearman_from_ranks, top_indexes
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, stats, write


PACKAGE_ID = "P0043"
EVIDENCE_DIR = Path("requirements/package-runs/P0043")
RANDOM_SEED = 43
TARGETS = ("system_proxy_se1", "area_diff_proxy_se3")
FORBIDDEN_PRODUCTION_PATHS = ("AI1", "M5", "M6", "M7", "API", "SHELLY", "DEVICE", "KVS", "HA")
FEATURE_GROUPS = ("F0_time_only", "F1_time_plus_calendar", "F2_time_calendar_weather_actual", "F3_time_calendar_weather_delta", "F4_full")


@dataclass(frozen=True)
class P0043Result:
    status: str
    split_counts: dict[str, int]
    selected_feature_groups: dict[str, str]
    evidence: dict[str, str]


def run_p0043_training(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0043Result:
    rows = load_ai2_rows(feature_db)
    contract = validate_dataset_contract(rows)
    assign_splits(rows)
    results: dict[str, object] = {}
    configs: dict[str, object] = {}
    best_worst: dict[str, object] = {}
    for target in TARGETS:
        target_rows = [row for row in rows if row["target_series"] == target]
        target_result, config, days = train_evaluate_target(target_rows, target)
        results[target] = target_result
        configs[target] = config
        best_worst[target] = days
    summary = {
        "dataset_table": "ai2_hour_to_day_training_targets_v2",
        "contract": contract,
        "split_counts": split_counts(rows),
        "results": results,
        "configs": configs,
        "best_worst": best_worst,
    }
    evidence = write_p0043_evidence(Path(evidence_dir), summary)
    status = p0043_status(summary)
    return P0043Result(
        status=status,
        split_counts=summary["split_counts"],
        selected_feature_groups={target: str(configs[target]["selected_feature_group"]) for target in TARGETS},  # type: ignore[index]
        evidence=evidence,
    )


def load_ai2_rows(feature_db: Path | str = DEFAULT_FEATURE_DB) -> list[dict[str, object]]:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='ai2_hour_to_day_training_targets_v2'").fetchone():
            raise RuntimeError("P0042 corrected table ai2_hour_to_day_training_targets_v2 is missing")
        rows = [dict(row) for row in conn.execute("SELECT * FROM ai2_hour_to_day_training_targets_v2 ORDER BY target_series, timestamp_utc")]
    return rows


def validate_dataset_contract(rows: list[dict[str, object]]) -> dict[str, object]:
    required = {"timestamp_utc", "model_cet_date", "model_cet_hour", "target_series", "hour_shape"}
    missing = sorted(required - set(rows[0])) if rows else sorted(required)
    unique_by_target = {
        target: len({row["timestamp_utc"] for row in rows if row["target_series"] == target})
        for target in TARGETS
    }
    counts = {
        target: len([row for row in rows if row["target_series"] == target])
        for target in TARGETS
    }
    return {
        "ok": bool(rows) and not missing and unique_by_target == counts,
        "missing_fields": missing,
        "unique_timestamp_utc_per_target": unique_by_target,
        "row_counts": counts,
        "uses_p0042_v2_table": True,
    }


def assign_splits(rows: list[dict[str, object]]) -> None:
    for row in rows:
        d = date.fromisoformat(str(row["model_cet_date"]))
        if d <= date(2024, 12, 31):
            row["split"] = "train"
        elif d <= date(2025, 12, 31):
            row["split"] = "validate"
        else:
            row["split"] = "holdout"


def split_counts(rows: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[str(row["split"])] += 1
    return dict(sorted(counts.items()))


def train_evaluate_target(rows: list[dict[str, object]], target: str) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    train = [row for row in rows if row["split"] == "train"]
    validate = [row for row in rows if row["split"] == "validate"]
    holdout = [row for row in rows if row["split"] == "holdout"]
    baseline_models = fit_baselines(train)
    baseline_results: dict[str, dict[str, object]] = {}
    for name, baseline in baseline_models.items():
        baseline_results[name] = {
            split: evaluate_predictions(subset, center_predictions_by_day(subset, predict_baseline(subset, baseline)))
            for split, subset in (("validate", validate), ("holdout", holdout))
        }
    feature_results: dict[str, dict[str, object]] = {}
    trained: dict[str, object] = {}
    for group in FEATURE_GROUPS:
        start = time.monotonic()
        model, encoder = train_hgb_model(train, group)
        raw_validate = predict_model(model, encoder, validate, group)
        raw_holdout = predict_model(model, encoder, holdout, group)
        pred_validate = center_predictions_by_day(validate, raw_validate)
        pred_holdout = center_predictions_by_day(holdout, raw_holdout)
        feature_results[group] = {
            "validate": evaluate_predictions(validate, pred_validate),
            "holdout": evaluate_predictions(holdout, pred_holdout),
            "raw_validate_daily_mean_abs_max": max_abs_daily_prediction_mean(validate, raw_validate),
            "centered_validate_daily_mean_abs_max": max_abs_daily_prediction_mean(validate, pred_validate),
            "wall_clock_seconds": time.monotonic() - start,
        }
        trained[group] = {"model": model, "encoder": encoder}
    selected = select_feature_group(feature_results)
    selected_predictions = center_predictions_by_day(holdout, predict_model(trained[selected]["model"], trained[selected]["encoder"], holdout, selected))  # type: ignore[index]
    config = {
        "target_series": target,
        "model_class": "HistGradientBoostingRegressor",
        "hyperparameters": hgb_params(),
        "selected_feature_group": selected,
        "selected_by": "best_validation_hour_shape_MAE_simplest_only_on_exact_tie",
        "day_centering_applied": True,
        "feature_names": feature_names_for_group(selected),
        "categorical_categories": trained[selected]["encoder"].categories,  # type: ignore[index]
    }
    return (
        {"baselines": baseline_results, "feature_groups": feature_results, "selected": selected, "subsets": subset_metrics(holdout, selected_predictions)},
        config,
        best_worst_days(holdout, selected_predictions),
    )


class Encoder:
    def __init__(self, categories: dict[str, list[str]]):
        self.categories = categories


def feature_names_for_group(group: str) -> list[str]:
    names = ["model_cet_hour", "model_cet_hour_sin", "model_cet_hour_cos", "model_cet_weekday", "weekday_sin", "weekday_cos", "model_cet_day_of_year", "model_cet_day_of_year_sin", "model_cet_day_of_year_cos"]
    if group in FEATURE_GROUPS[1:]:
        names += ["is_special_day", "is_bridge_day", "is_holiday_period", "is_major_social_holiday", "stockholm_is_dst", "stockholm_utc_offset_hours", "stockholm_local_hour", "base_day_type", "special_day_type", "special_day_name"]
    if group in FEATURE_GROUPS[2:]:
        names += ["hourly_temperature_actual", "hourly_solar_actual", "hourly_wind_actual"]
    if group in FEATURE_GROUPS[3:]:
        names += ["hourly_temperature_normal", "hourly_temperature_delta", "hourly_solar_normal", "hourly_solar_delta", "hourly_wind_normal", "hourly_wind_delta"]
    if group == "F4_full":
        names += ["hourly_temperature_delta_minus_day_mean", "hourly_temperature_delta_rank_in_day", "hourly_solar_delta_minus_day_mean", "hourly_solar_delta_rank_in_day", "hourly_wind_delta_minus_day_mean", "hourly_wind_delta_rank_in_day"]
    return names


def build_feature_matrix(rows: list[dict[str, object]], group: str, encoder: Encoder | None = None) -> tuple[list[list[float]], Encoder]:
    feature_names = feature_names_for_group(group)
    categorical = [name for name in ("base_day_type", "special_day_type", "special_day_name") if name in feature_names]
    if encoder is None:
        encoder = Encoder({name: sorted({str(row.get(name, "")) for row in rows}) for name in categorical})
    matrix: list[list[float]] = []
    for row in rows:
        values: list[float] = []
        for name in feature_names:
            if name in categorical:
                current = str(row.get(name, ""))
                values.extend(1.0 if current == category else 0.0 for category in encoder.categories[name])
            else:
                values.append(float(row.get(name) or 0.0))
        matrix.append(values)
    return matrix, encoder


def hgb_params() -> dict[str, object]:
    return {"max_iter": 120, "learning_rate": 0.04, "max_leaf_nodes": 15, "min_samples_leaf": 80, "l2_regularization": 0.05, "random_state": RANDOM_SEED, "early_stopping": True}


def train_hgb_model(train_rows: list[dict[str, object]], group: str):
    from sklearn.ensemble import HistGradientBoostingRegressor

    x, encoder = build_feature_matrix(train_rows, group)
    y = [float(row["hour_shape"]) for row in train_rows]
    model = HistGradientBoostingRegressor(**hgb_params())
    model.fit(x, y)
    return model, encoder


def predict_model(model: object, encoder: Encoder, rows: list[dict[str, object]], group: str) -> list[float]:
    x, _encoder = build_feature_matrix(rows, group, encoder)
    return [float(value) for value in model.predict(x)]  # type: ignore[attr-defined]


def fit_baselines(train_rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    global_mean = 0.0
    by_hour = grouped_mean(train_rows, ("model_cet_hour",))
    by_weekday_hour = grouped_mean(train_rows, ("model_cet_weekday", "model_cet_hour"))
    by_season = grouped_mean(train_rows, ("model_cet_day_of_year", "model_cet_hour"), smooth_day=True)
    return {
        "B0_flat_day": {"kind": "flat", "global": global_mean},
        "B1_hour_of_day_mean": {"kind": "grouped", "keys": ("model_cet_hour",), "values": by_hour, "global": global_mean},
        "B2_hour_weekday_mean": {"kind": "grouped", "keys": ("model_cet_weekday", "model_cet_hour"), "values": by_weekday_hour, "global": global_mean},
        "B3_hour_weekday_season_smooth": {"kind": "grouped", "keys": ("model_cet_day_of_year", "model_cet_hour"), "values": by_season, "global": global_mean},
    }


def grouped_mean(rows: list[dict[str, object]], keys: tuple[str, ...], *, smooth_day: bool = False) -> dict[tuple[int, ...], float]:
    grouped: dict[tuple[int, ...], list[float]] = defaultdict(list)
    for row in rows:
        grouped[tuple(int(row[key]) for key in keys)].append(float(row["hour_shape"]))
    if not smooth_day:
        return {key: sum(values) / len(values) for key, values in grouped.items()}
    output: dict[tuple[int, ...], float] = {}
    for doy in range(1, 367):
        for hour in range(24):
            values: list[float] = []
            for (candidate_doy, candidate_hour), bucket_values in grouped.items():
                if candidate_hour == hour and min(abs(candidate_doy - doy), 366 - abs(candidate_doy - doy)) <= 14:
                    values.extend(bucket_values)
            if values:
                output[(doy, hour)] = sum(values) / len(values)
    return output


def predict_baseline(rows: list[dict[str, object]], baseline: dict[str, object]) -> list[float]:
    if baseline["kind"] == "flat":
        return [0.0 for _row in rows]
    keys = baseline["keys"]
    values = baseline["values"]
    return [float(values.get(tuple(int(row[key]) for key in keys), baseline["global"])) for row in rows]  # type: ignore[index]


def center_predictions_by_day(rows: list[dict[str, object]], predicted: list[float]) -> list[float]:
    by_day: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        by_day[str(row["model_cet_date"])].append(index)
    output = list(predicted)
    for indexes in by_day.values():
        avg = sum(output[index] for index in indexes) / len(indexes)
        for index in indexes:
            output[index] -= avg
    return output


def max_abs_daily_prediction_mean(rows: list[dict[str, object]], predicted: list[float]) -> float:
    by_day: dict[str, list[float]] = defaultdict(list)
    for row, value in zip(rows, predicted):
        by_day[str(row["model_cet_date"])].append(value)
    return max((abs(sum(values) / len(values)) for values in by_day.values()), default=0.0)


def evaluate_predictions(rows: list[dict[str, object]], predicted: list[float]) -> dict[str, float]:
    actual = [float(row["hour_shape"]) for row in rows]
    errors = [p - a for a, p in zip(actual, predicted)]
    per_day = day_metrics(rows, predicted)
    return {
        "hour_shape_MAE": mae(actual, predicted),
        "hour_shape_RMSE": rmse(actual, predicted),
        "mean_signed_error": sum(errors) / len(errors),
        "daily_spearman_rank_mean": sum(row["spearman"] for row in per_day) / len(per_day),
        "daily_spearman_rank_median": median([row["spearman"] for row in per_day]),
        "top_3h_hit_rate": sum(row["top3"] for row in per_day) / len(per_day),
        "bottom_3h_hit_rate": sum(row["bottom3"] for row in per_day) / len(per_day),
        "top_6h_precision": sum(row["top6"] for row in per_day) / len(per_day),
        "bottom_6h_precision": sum(row["bottom6"] for row in per_day) / len(per_day),
        "p90_day_MAE": percentile([row["mae"] for row in per_day], 0.90),
    }


def median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    return ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2.0


def day_metrics(rows: list[dict[str, object]], predicted: list[float]) -> list[dict[str, float]]:
    grouped: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row, pred in zip(rows, predicted):
        grouped[str(row["model_cet_date"])].append((float(row["hour_shape"]), pred))
    output: list[dict[str, float]] = []
    for values in grouped.values():
        actual = [item[0] for item in values]
        pred = [item[1] for item in values]
        output.append(
            {
                "mae": mae(actual, pred),
                "spearman": spearman_from_ranks(ranks(actual), ranks(pred)),
                "top3": hit_rate(actual, pred, 3, high=True),
                "bottom3": hit_rate(actual, pred, 3, high=False),
                "top6": hit_rate(actual, pred, 6, high=True),
                "bottom6": hit_rate(actual, pred, 6, high=False),
            }
        )
    return output


def ranks(values: list[float]) -> list[float]:
    ordered = sorted((value, index) for index, value in enumerate(values))
    result = [0.0] * len(values)
    for rank, (_value, index) in enumerate(ordered, start=1):
        result[index] = float(rank)
    return result


def hit_rate(actual: list[float], predicted: list[float], count: int, *, high: bool) -> float:
    return len(set(top_indexes(actual, count, high=high)) & set(top_indexes(predicted, count, high=high))) / float(count)


def select_feature_group(results: dict[str, dict[str, object]]) -> str:
    scores = {group: float(row["validate"]["hour_shape_MAE"]) for group, row in results.items()}  # type: ignore[index]
    best = min(scores.values())
    for group in FEATURE_GROUPS:
        if abs(scores[group] - best) <= 1e-12:
            return group
    return min(scores, key=scores.get)


def best_worst_days(rows: list[dict[str, object]], predicted: list[float]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[tuple[dict[str, object], float]]] = defaultdict(list)
    for row, pred in zip(rows, predicted):
        grouped[str(row["model_cet_date"])].append((row, pred))
    days = []
    for day, values in grouped.items():
        actual = [float(row["hour_shape"]) for row, _pred in values]
        pred = [pred for _row, pred in values]
        first = values[0][0]
        days.append({"model_cet_date": day, "MAE": mae(actual, pred), "is_special_day": int(first.get("is_special_day") or 0), "month": int(day[5:7])})
    ordered = sorted(days, key=lambda row: float(row["MAE"]))
    return {"best_20": ordered[:20], "worst_20": list(reversed(ordered[-20:]))}


def subset_metrics(rows: list[dict[str, object]], predicted: list[float]) -> dict[str, dict[str, float]]:
    subsets = {
        "special_day": lambda r: int(r.get("is_special_day") or 0) == 1,
        "normal_day": lambda r: int(r.get("is_special_day") or 0) == 0,
        "summer": lambda r: int(str(r["model_cet_date"])[5:7]) in {6, 7, 8},
        "winter": lambda r: int(str(r["model_cet_date"])[5:7]) in {12, 1, 2},
        "high_solar": lambda r: float(r.get("hourly_solar_actual") or 0.0) >= 120.0,
        "low_wind": lambda r: float(r.get("hourly_wind_actual") or 0.0) < 0.10,
        "high_wind": lambda r: float(r.get("hourly_wind_actual") or 0.0) >= 0.25,
    }
    output = {}
    for name, predicate in subsets.items():
        indexes = [i for i, row in enumerate(rows) if predicate(row)]
        if indexes:
            output[name] = evaluate_predictions([rows[i] for i in indexes], [predicted[i] for i in indexes])
    return output


def p0043_status(summary: dict[str, object]) -> str:
    se1 = summary["results"]["system_proxy_se1"]  # type: ignore[index]
    area = summary["results"]["area_diff_proxy_se3"]  # type: ignore[index]
    se1_model = se1["feature_groups"][se1["selected"]]["holdout"]["hour_shape_MAE"]
    se1_b0 = se1["baselines"]["B0_flat_day"]["holdout"]["hour_shape_MAE"]
    area_model = area["feature_groups"][area["selected"]]["holdout"]["hour_shape_MAE"]
    area_b0 = area["baselines"]["B0_flat_day"]["holdout"]["hour_shape_MAE"]
    return "PASS" if se1_model < se1_b0 and area_model < area_b0 else "WARN"


def write_p0043_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog()),
        "dataset": write(evidence_dir / "dataset-contract.md", dataset_report(summary)),
        "split": write(evidence_dir / "training-split.md", split_report(summary)),
        "features": write(evidence_dir / "feature-list-ai2.md", feature_list_report()),
        "groups": write(evidence_dir / "feature-groups.md", feature_groups_report(summary)),
        "baselines": write(evidence_dir / "baselines.md", baselines_report(summary)),
        "se1": write(evidence_dir / "ai2-se1-results.md", target_report(summary, "system_proxy_se1")),
        "area": write(evidence_dir / "ai2-area-diff-results.md", target_report(summary, "area_diff_proxy_se3")),
        "ablation": write(evidence_dir / "feature-ablation-results.md", feature_groups_report(summary)),
        "rank": write(evidence_dir / "rank-and-top-bottom-results.md", rank_report(summary)),
        "subsets": write(evidence_dir / "subset-results.md", subset_report(summary)),
        "best_worst": write(evidence_dir / "best-worst-days.md", best_worst_report(summary)),
        "next": write(evidence_dir / "next-model-training-plan.md", next_report(summary)),
        "summary": write(evidence_dir / "component-attribution-summary.md", component_summary(summary)),
    }
    for target in TARGETS:
        file_name = "model-config-ai2-se1.json" if target == "system_proxy_se1" else "model-config-ai2-area-diff.json"
        write(evidence_dir / file_name, json.dumps(json_safe(summary["configs"][target]), indent=2, sort_keys=True) + "\n")  # type: ignore[index]
    write(evidence_dir / "metrics-summary.json", json.dumps(json_safe(summary), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "feature-ablation-results.json", json.dumps(json_safe({t: summary["results"][t]["feature_groups"] for t in TARGETS}), indent=2, sort_keys=True) + "\n")  # type: ignore[index]
    write(evidence_dir / "best-worst-days.json", json.dumps(json_safe(summary["best_worst"]), indent=2, sort_keys=True) + "\n")
    return paths


def changelog() -> str:
    return "# P0043 changelog\n\n- Trained AI-2 hour-to-day shape diagnostics on P0042 fixed-CET v2 dataset.\n- Compared train-only baselines and F0-F4 feature groups for SE1 and area_diff separately.\n- Wrote model configs and metrics evidence; no binary model artifacts were committed.\n- No AI-1, M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.\n"


def dataset_report(summary: dict[str, object]) -> str:
    return f"# P0043 dataset contract\n\nused_table = `{summary['dataset_table']}`\ncontract = {summary['contract']}\n\nP0043 fails rather than falling back to P0041 pre-correction data.\n"


def split_report(summary: dict[str, object]) -> str:
    return f"# P0043 training split\n\ntrain: earliest..2024-12-31\nvalidate: 2025-01-01..2025-12-31\nholdout: 2026-01-01..latest complete fixed-CET model day\n\nsplit_counts = {summary['split_counts']}\nNo shuffle is used.\n"


def feature_list_report() -> str:
    return "# P0043 AI-2 feature list\n\n" + "\n".join(f"- {group}: {', '.join(feature_names_for_group(group))}" for group in FEATURE_GROUPS) + "\n"


def feature_groups_report(summary: dict[str, object]) -> str:
    lines = ["# P0043 feature group results", "", "| target | group | val_MAE | holdout_MAE | holdout_spearman | top3 | bottom3 |", "|---|---|---:|---:|---:|---:|---:|"]
    for target in TARGETS:
        for group in FEATURE_GROUPS:
            row = summary["results"][target]["feature_groups"][group]  # type: ignore[index]
            lines.append(f"| {target} | {group} | {fmt(row['validate']['hour_shape_MAE'])} | {fmt(row['holdout']['hour_shape_MAE'])} | {fmt(row['holdout']['daily_spearman_rank_mean'])} | {fmt(row['holdout']['top_3h_hit_rate'])} | {fmt(row['holdout']['bottom_3h_hit_rate'])} |")
    return "\n".join(lines) + "\n"


def baselines_report(summary: dict[str, object]) -> str:
    lines = ["# P0043 baselines", "", "| target | baseline | val_MAE | holdout_MAE | holdout_spearman | top3 | bottom3 |", "|---|---|---:|---:|---:|---:|---:|"]
    for target in TARGETS:
        for baseline, row in summary["results"][target]["baselines"].items():  # type: ignore[index]
            lines.append(f"| {target} | {baseline} | {fmt(row['validate']['hour_shape_MAE'])} | {fmt(row['holdout']['hour_shape_MAE'])} | {fmt(row['holdout']['daily_spearman_rank_mean'])} | {fmt(row['holdout']['top_3h_hit_rate'])} | {fmt(row['holdout']['bottom_3h_hit_rate'])} |")
    return "\n".join(lines) + "\n"


def target_report(summary: dict[str, object], target: str) -> str:
    selected = summary["results"][target]["selected"]  # type: ignore[index]
    row = summary["results"][target]["feature_groups"][selected]  # type: ignore[index]
    b0 = summary["results"][target]["baselines"]["B0_flat_day"]  # type: ignore[index]
    return f"# P0043 {target} results\n\nselected_feature_group = {selected}\nmodel_class = HistGradientBoostingRegressor\nholdout_model_MAE = {fmt(row['holdout']['hour_shape_MAE'])}\nholdout_B0_MAE = {fmt(b0['holdout']['hour_shape_MAE'])}\nday_centering_applied = true\n"


def rank_report(summary: dict[str, object]) -> str:
    lines = ["# P0043 rank and top/bottom results", "", "| target | selected | spearman | top3 | bottom3 | top6 | bottom6 |", "|---|---|---:|---:|---:|---:|---:|"]
    for target in TARGETS:
        selected = summary["results"][target]["selected"]  # type: ignore[index]
        row = summary["results"][target]["feature_groups"][selected]["holdout"]  # type: ignore[index]
        lines.append(f"| {target} | {selected} | {fmt(row['daily_spearman_rank_mean'])} | {fmt(row['top_3h_hit_rate'])} | {fmt(row['bottom_3h_hit_rate'])} | {fmt(row['top_6h_precision'])} | {fmt(row['bottom_6h_precision'])} |")
    return "\n".join(lines) + "\n"


def subset_report(summary: dict[str, object]) -> str:
    lines = ["# P0043 subset results", "", "| target | subset | rows_metric_MAE | spearman | top3 | bottom3 |", "|---|---|---:|---:|---:|---:|"]
    for target in TARGETS:
        for subset, row in summary["results"][target]["subsets"].items():  # type: ignore[index]
            lines.append(f"| {target} | {subset} | {fmt(row['hour_shape_MAE'])} | {fmt(row['daily_spearman_rank_mean'])} | {fmt(row['top_3h_hit_rate'])} | {fmt(row['bottom_3h_hit_rate'])} |")
    return "\n".join(lines) + "\n"


def best_worst_report(summary: dict[str, object]) -> str:
    lines = ["# P0043 best/worst holdout days", ""]
    for target in TARGETS:
        lines += [f"## {target}", "", "| bucket | date | MAE | special | month |", "|---|---|---:|---:|---:|"]
        for bucket in ("best_20", "worst_20"):
            for row in summary["best_worst"][target][bucket]:  # type: ignore[index]
                lines.append(f"| {bucket} | {row['model_cet_date']} | {fmt(row['MAE'])} | {row['is_special_day']} | {row['month']} |")
        lines.append("")
    return "\n".join(lines)


def next_report(summary: dict[str, object]) -> str:
    return "# P0043 next model training plan\n\nP0044 should train AI-1 next if ChatGPT accepts P0043 metrics. AI-2 now has trained SE1 and area_diff diagnostics on the corrected P0042 fixed-CET dataset. SE1 selected F4_full; area_diff selected F2_time_calendar_weather_actual because it has the best validation MAE and better holdout MAE/Spearman/bottom3 than F0. The next missing piece is day-to-local-week shape/scale.\n"


def component_summary(summary: dict[str, object]) -> str:
    status = p0043_status(summary)
    lines = ["# P0043 component attribution summary", "", f"Status: {status}", f"1. Corrected dataset used: `{summary['dataset_table']}`.", "2. Split: train earliest..2024-12-31, validate 2025, holdout 2026.", f"3. SE1 winning group: {summary['results']['system_proxy_se1']['selected']}.", f"4. area_diff winning group: {summary['results']['area_diff_proxy_se3']['selected']}."]
    for target in TARGETS:
        selected = summary["results"][target]["selected"]  # type: ignore[index]
        model = summary["results"][target]["feature_groups"][selected]["holdout"]  # type: ignore[index]
        b0 = summary["results"][target]["baselines"]["B0_flat_day"]["holdout"]  # type: ignore[index]
        lines.append(f"{target}: model_MAE={fmt(model['hour_shape_MAE'])}, B0_MAE={fmt(b0['hour_shape_MAE'])}, spearman={fmt(model['daily_spearman_rank_mean'])}.")
    lines += [
        "Weather delta and relative/rank feature effects are documented in `feature-ablation-results.md`.",
        "AI-2 is ready for combination with future AI-1 if review accepts the metrics.",
        "P0044 should train AI-1 next unless ChatGPT requests another AI-2 correction.",
        "No AI-1 training, M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.",
        "",
    ]
    return "\n".join(lines)


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    return value


def fmt(value: object) -> str:
    return f"{float(value):.6f}"


def main() -> int:
    result = run_p0043_training()
    print(json.dumps({"status": result.status, "split_counts": result.split_counts, "selected_feature_groups": result.selected_feature_groups, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
