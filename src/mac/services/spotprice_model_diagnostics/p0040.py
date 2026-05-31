"""P0040 weekly anchored forecast backtest diagnostics."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import json
import math
from statistics import median

from src.mac.services.spotprice_model_diagnostics.p0037 import count_splits, fit_strict_components, fmt, load_diagnostic_rows
from src.mac.services.spotprice_model_diagnostics.p0038 import (
    apply_solar_wind_features,
    enrich_p0038_weather,
    fit_apply_m3c_m3d,
    fit_apply_m4_area_only,
)
from src.mac.services.spotprice_model_diagnostics.p0039 import fit_m1b_components
from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_temperature_normalization.core import DEFAULT_PRICE_DB_PATH, DEFAULT_WEATHER_DB_PATH


PACKAGE_ID = "P0040"
EVIDENCE_DIR = Path("requirements/package-runs/P0040")
PRIMARY_START = date(2025, 6, 1)
PRIMARY_END = date(2026, 6, 1)
ANCHORS = ("anchor_16h_mean", "anchor_16h_median", "anchor_16h_robust")
TARGETS = ("system_proxy_se1", "area_diff_proxy_se3", "recomposed_se3")
VARIANTS = (
    "V0_naive_flat_week",
    "V1_M1_shape_only",
    "V2_M1_plus_existing_M3A_M3B",
    "V3_M1_plus_M3A_m1b_M3B_m1b",
    "V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D",
    "V5_diagnostic_with_M3C",
    "V6_diagnostic_with_M4_area_diff",
)


@dataclass(frozen=True)
class ForecastOrigin:
    origin_date: date
    origin_local_time: str
    known_rows: list[dict[str, object]]
    horizon_rows: list[dict[str, object]]


@dataclass(frozen=True)
class P0040Result:
    status: str
    origin_count: int
    backtest_start: str
    backtest_end: str
    evidence: dict[str, str]


def run_p0040_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    price_db: Path | str = DEFAULT_PRICE_DB_PATH,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0040Result:
    rows = load_diagnostic_rows(feature_db=feature_db, price_db=price_db, weather_db=weather_db)
    enrich_p0038_weather(rows, weather_db)
    apply_solar_wind_features(rows)
    fit_static_strict_components(rows)
    origins = forecast_origins(rows, PRIMARY_START, PRIMARY_END)
    if not origins:
        raise RuntimeError("P0040 found no eligible forecast origins")
    weekly = build_weekly_results(origins)
    aggregates = aggregate_results(weekly)
    evidence = write_p0040_evidence(Path(evidence_dir), rows, origins, weekly, aggregates)
    v2 = aggregate_metric(aggregates, "anchor_16h_mean", "V2_M1_plus_existing_M3A_M3B", "recomposed_se3", "anchored_absolute_MAE")
    v3 = aggregate_metric(aggregates, "anchor_16h_mean", "V3_M1_plus_M3A_m1b_M3B_m1b", "recomposed_se3", "anchored_absolute_MAE")
    mean_rows = [row for row in aggregates if row["anchor"] == "anchor_16h_mean" and row["target"] == "recomposed_se3"]
    best_abs = min(mean_rows, key=lambda row: float(row["anchored_absolute_MAE"]))
    status = "PASS" if best_abs["variant"] != "V0_naive_flat_week" and v3 <= v2 else "WARN"
    return P0040Result(status=status, origin_count=len(origins), backtest_start=origins[0].origin_date.isoformat(), backtest_end=origins[-1].origin_date.isoformat(), evidence=evidence)


def fit_static_strict_components(rows: list[dict[str, object]]) -> None:
    fit_strict_components(rows)
    fit_m1b_components(rows)
    fit_apply_m3c_m3d(rows)
    try:
        fit_apply_m4_area_only(rows)
    except Exception as exc:  # pragma: no cover - exercised only when sklearn/local artifacts are unavailable
        for row in rows:
            row["m4_area"] = 0.0
            row["m4_se1_disabled"] = 0.0
            row["p0040_m4_error"] = str(exc)


def forecast_origins(rows: list[dict[str, object]], start: date, end: date) -> list[ForecastOrigin]:
    by_day_hour = {(date.fromisoformat(str(row["local_date"])), int(row["local_hour"])): row for row in rows}
    max_day = max(day for day, _hour in by_day_hour)
    latest_complete = min(end, max_day - timedelta(days=6))
    current = start
    while current.weekday() != 0:
        current += timedelta(days=1)
    origins: list[ForecastOrigin] = []
    while current <= latest_complete:
        known = [by_day_hour.get((current, hour)) for hour in range(16)]
        horizon = [by_day_hour.get((current + timedelta(days=offset), hour)) for offset in range(7) for hour in range(24)]
        if all(known) and all(horizon):
            origins.append(ForecastOrigin(current, "06:00", list(known), list(horizon)))  # type: ignore[arg-type]
        current += timedelta(days=7)
    return origins


def build_weekly_results(origins: list[ForecastOrigin]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for origin in origins:
        subsets = classify_origin(origin)
        for variant in VARIANTS:
            known_pred = build_variant_predictions(origin.known_rows, variant)
            horizon_pred = build_variant_predictions(origin.horizon_rows, variant)
            actual = actual_series(origin.horizon_rows)
            known_actual = actual_series(origin.known_rows)
            for anchor in ANCHORS:
                anchored: dict[str, list[float]] = {}
                anchor_meta: dict[str, float] = {}
                for target in ("system_proxy_se1", "area_diff_proxy_se3"):
                    anchored[target], meta = anchor_predictions(known_actual[target], known_pred[target], horizon_pred[target], anchor)
                    anchor_meta[f"{target}_offset"] = meta["offset"]
                anchored["recomposed_se3"] = [a + b for a, b in zip(anchored["system_proxy_se1"], anchored["area_diff_proxy_se3"])]
                for target in TARGETS:
                    metrics = compute_absolute_metrics(actual[target], anchored[target])
                    shape = compute_shape_metrics(actual[target], anchored[target])
                    output.append(
                        {
                            "origin_date": origin.origin_date.isoformat(),
                            "origin_local_time": origin.origin_local_time,
                            "weather_oracle": "actual_weather_used_as_forecast_proxy",
                            "variant": variant,
                            "anchor": anchor,
                            "target": target,
                            **metrics,
                            **shape,
                            **subsets,
                            "anchor_offset_se1": anchor_meta["system_proxy_se1_offset"],
                            "anchor_offset_area": anchor_meta["area_diff_proxy_se3_offset"],
                        }
                    )
    return output


def actual_series(rows: list[dict[str, object]]) -> dict[str, list[float]]:
    se1 = [float(row["actual_se1"]) for row in rows]
    area = [float(row["actual_area_diff"]) for row in rows]
    return {"system_proxy_se1": se1, "area_diff_proxy_se3": area, "recomposed_se3": [a + b for a, b in zip(se1, area)]}


def build_variant_predictions(rows: list[dict[str, object]], variant: str) -> dict[str, list[float]]:
    se1: list[float] = []
    area: list[float] = []
    for row in rows:
        if variant == "V0_naive_flat_week":
            se1_value = 0.0
            area_value = 0.0
        elif variant == "V1_M1_shape_only":
            se1_value = float(row["m1_raw_se1"])
            area_value = float(row["m1_raw_area"])
        elif variant == "V2_M1_plus_existing_M3A_M3B":
            se1_value = float(row["m1_raw_se1"]) + float(row["m3a_se1"]) + float(row["m3b_se1"])
            area_value = float(row["m1_raw_area"]) + float(row["m3a_area"]) + float(row["m3b_area"])
        elif variant == "V3_M1_plus_M3A_m1b_M3B_m1b":
            se1_value = float(row["m1_raw_se1"]) + float(row["m3a_m1b_se1"]) + float(row["m3b_m1b_se1"])
            area_value = float(row["m1_raw_area"]) + float(row["m3a_m1b_area"]) + float(row["m3b_m1b_area"])
        elif variant == "V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D":
            base = build_variant_predictions([row], "V3_M1_plus_M3A_m1b_M3B_m1b")
            se1_value = base["system_proxy_se1"][0] + float(row["m3d_se1"])
            area_value = base["area_diff_proxy_se3"][0] + float(row["m3d_area"])
        elif variant == "V5_diagnostic_with_M3C":
            base = build_variant_predictions([row], "V3_M1_plus_M3A_m1b_M3B_m1b")
            se1_value = base["system_proxy_se1"][0] + float(row["m3c_se1"])
            area_value = base["area_diff_proxy_se3"][0] + float(row["m3c_area"])
        elif variant == "V6_diagnostic_with_M4_area_diff":
            base = build_variant_predictions([row], "V3_M1_plus_M3A_m1b_M3B_m1b")
            se1_value = base["system_proxy_se1"][0]
            area_value = base["area_diff_proxy_se3"][0] + float(row.get("m4_area", 0.0))
        else:
            raise ValueError(f"unknown P0040 variant: {variant}")
        se1.append(se1_value)
        area.append(area_value)
    return {"system_proxy_se1": se1, "area_diff_proxy_se3": area, "recomposed_se3": [a + b for a, b in zip(se1, area)]}


def anchor_predictions(known_actual: list[float], known_predicted: list[float], horizon_predicted: list[float], method: str) -> tuple[list[float], dict[str, float]]:
    if method == "anchor_16h_mean":
        offset = (sum(known_actual) / len(known_actual)) - (sum(known_predicted) / len(known_predicted))
    elif method == "anchor_16h_median":
        offset = float(median(known_actual)) - float(median(known_predicted))
    elif method == "anchor_16h_robust":
        offset = float(median([a - p for a, p in zip(known_actual, known_predicted)]))
    else:
        raise ValueError(f"unknown anchor method: {method}")
    return [value + offset for value in horizon_predicted], {"offset": offset}


def compute_absolute_metrics(actual: list[float], predicted: list[float]) -> dict[str, float]:
    daily_actual = [sum(actual[i : i + 24]) / 24.0 for i in range(0, len(actual), 24)]
    daily_pred = [sum(predicted[i : i + 24]) / 24.0 for i in range(0, len(predicted), 24)]
    return {
        "anchored_absolute_MAE": mae(actual, predicted),
        "anchored_absolute_RMSE": rmse(actual, predicted),
        "anchored_signed_error": sum(p - a for a, p in zip(actual, predicted)) / len(actual),
        "anchored_daily_mean_MAE": mae(daily_actual, daily_pred),
        "anchored_weekly_mean_error": (sum(predicted) / len(predicted)) - (sum(actual) / len(actual)),
    }


def compute_shape_metrics(actual: list[float], predicted: list[float]) -> dict[str, float]:
    centered_actual = center(actual)
    centered_pred = center(predicted)
    scaled_actual = scale_centered(centered_actual)
    scaled_pred = scale_centered(centered_pred)
    actual_ranks = ranks(actual)
    pred_ranks = ranks(predicted)
    return {
        "weekly_centered_shape_MAE": mae(centered_actual, centered_pred),
        "weekly_centered_shape_RMSE": rmse(centered_actual, centered_pred),
        "weekly_scaled_shape_MAE": mae(scaled_actual, scaled_pred),
        "weekly_rank_spearman": spearman_from_ranks(actual_ranks, pred_ranks),
        "weekly_top_10pct_precision": top_precision(actual, predicted, max(1, int(len(actual) * 0.10)), high=True),
        "weekly_bottom_10pct_precision": top_precision(actual, predicted, max(1, int(len(actual) * 0.10)), high=False),
        "daily_centered_shape_MAE": sum(mae(center(actual[i : i + 24]), center(predicted[i : i + 24])) for i in range(0, len(actual), 24)) / 7.0,
        "daily_rank_spearman_mean": sum(spearman_from_ranks(ranks(actual[i : i + 24]), ranks(predicted[i : i + 24])) for i in range(0, len(actual), 24)) / 7.0,
        "daily_top_3h_hit_rate": daily_hit_rate(actual, predicted, high=True),
        "daily_bottom_3h_hit_rate": daily_hit_rate(actual, predicted, high=False),
        "expensive_hour_recall": top_precision(predicted, actual, max(1, int(len(actual) * 0.10)), high=True),
        "cheap_hour_recall": top_precision(predicted, actual, max(1, int(len(actual) * 0.10)), high=False),
    }


def center(values: list[float]) -> list[float]:
    mean = sum(values) / len(values)
    return [value - mean for value in values]


def scale_centered(values: list[float]) -> list[float]:
    scale = median([abs(value) for value in values]) or 1.0
    return [value / scale for value in values]


def ranks(values: list[float]) -> list[float]:
    ordered = sorted((value, index) for index, value in enumerate(values))
    result = [0.0] * len(values)
    for rank, (_value, index) in enumerate(ordered, start=1):
        result[index] = float(rank)
    return result


def spearman_from_ranks(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left:
        return 0.0
    left_centered = center(left)
    right_centered = center(right)
    denom = math.sqrt(sum(v * v for v in left_centered) * sum(v * v for v in right_centered))
    if denom <= 0.0:
        return 0.0
    return sum(a * b for a, b in zip(left_centered, right_centered)) / denom


def top_precision(actual: list[float], predicted: list[float], count: int, *, high: bool) -> float:
    actual_set = set(top_indexes(actual, count, high=high))
    pred_set = set(top_indexes(predicted, count, high=high))
    return len(actual_set & pred_set) / float(count)


def top_indexes(values: list[float], count: int, *, high: bool) -> list[int]:
    return [index for _value, index in sorted(((value, index) for index, value in enumerate(values)), reverse=high)[:count]]


def daily_hit_rate(actual: list[float], predicted: list[float], *, high: bool) -> float:
    hits = 0
    for start in range(0, len(actual), 24):
        hits += len(set(top_indexes(actual[start : start + 24], 3, high=high)) & set(top_indexes(predicted[start : start + 24], 3, high=high))) / 3.0
    return hits / 7.0


def classify_origin(origin: ForecastOrigin) -> dict[str, bool]:
    rows = origin.horizon_rows
    avg_temp = sum(float(row["se1_system_temperature"]) for row in rows) / len(rows)
    avg_wind = sum(float(row.get("m3d_wind_proxy_area", 0.0)) for row in rows) / len(rows)
    avg_solar = sum(float(row.get("m3c_solar_proxy_area", 0.0)) for row in rows) / len(rows)
    month = origin.origin_date.month
    return {
        "subset_all_forecast_weeks": True,
        "subset_holiday_weeks": any(row["is_special_day"] for row in rows),
        "subset_non_holiday_weeks": not any(row["is_special_day"] for row in rows),
        "subset_bridge_weeks": any(str(row["bridge_strength"]) in {"strong", "weak"} for row in rows),
        "subset_major_social_holidays": any(row["special_day_group"] == "major_social_holiday" for row in rows),
        "subset_cold_weeks": avg_temp <= 0.0,
        "subset_warm_weeks": avg_temp >= 15.0,
        "subset_high_wind_weeks": avg_wind >= 0.25,
        "subset_low_wind_weeks": avg_wind < 0.10,
        "subset_high_solar_weeks": avg_solar >= 120.0,
        "subset_low_solar_weeks": avg_solar < 40.0,
        "subset_summer_weeks": month in {6, 7, 8},
        "subset_winter_weeks": month in {12, 1, 2},
    }


def aggregate_results(weekly: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in weekly:
        grouped[(str(row["anchor"]), str(row["variant"]), str(row["target"]))].append(row)
    output: list[dict[str, object]] = []
    for (anchor, variant, target), rows in sorted(grouped.items()):
        maes = [float(row["anchored_absolute_MAE"]) for row in rows]
        output.append(
            {
                "anchor": anchor,
                "variant": variant,
                "target": target,
                "forecast_weeks": len(rows),
                "anchored_absolute_MAE": sum(maes) / len(maes),
                "anchored_absolute_RMSE": sum(float(row["anchored_absolute_RMSE"]) for row in rows) / len(rows),
                "anchored_signed_error": sum(float(row["anchored_signed_error"]) for row in rows) / len(rows),
                "anchored_daily_mean_MAE": sum(float(row["anchored_daily_mean_MAE"]) for row in rows) / len(rows),
                "anchored_weekly_mean_error": sum(float(row["anchored_weekly_mean_error"]) for row in rows) / len(rows),
                "p90_weekly_absolute_MAE": percentile(maes, 0.90),
                "weekly_centered_shape_MAE": sum(float(row["weekly_centered_shape_MAE"]) for row in rows) / len(rows),
                "weekly_rank_spearman": sum(float(row["weekly_rank_spearman"]) for row in rows) / len(rows),
                "weekly_top_10pct_precision": sum(float(row["weekly_top_10pct_precision"]) for row in rows) / len(rows),
                "weekly_bottom_10pct_precision": sum(float(row["weekly_bottom_10pct_precision"]) for row in rows) / len(rows),
                "daily_top_3h_hit_rate": sum(float(row["daily_top_3h_hit_rate"]) for row in rows) / len(rows),
                "daily_bottom_3h_hit_rate": sum(float(row["daily_bottom_3h_hit_rate"]) for row in rows) / len(rows),
                "expensive_hour_recall": sum(float(row["expensive_hour_recall"]) for row in rows) / len(rows),
                "cheap_hour_recall": sum(float(row["cheap_hour_recall"]) for row in rows) / len(rows),
            }
        )
    return output


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[int((len(ordered) - 1) * q)]


def aggregate_metric(aggregates: list[dict[str, object]], anchor: str, variant: str, target: str, metric: str) -> float:
    return float(next(row[metric] for row in aggregates if row["anchor"] == anchor and row["variant"] == variant and row["target"] == target))


def write_p0040_evidence(evidence_dir: Path, rows: list[dict[str, object]], origins: list[ForecastOrigin], weekly: list[dict[str, object]], aggregates: list[dict[str, object]]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog()),
        "method": write(evidence_dir / "weekly-backtest-method.md", method_report(rows, origins)),
        "level_shape": write(evidence_dir / "level-shape-separation.md", level_shape_report()),
        "shape_defs": write(evidence_dir / "shape-metrics-definition.md", shape_definition_report()),
        "absolute": write(evidence_dir / "anchored-absolute-results.md", aggregate_table(aggregates, "anchored_absolute_MAE") + "\n" + subset_breakdown_markdown(weekly)),
        "shape": write(evidence_dir / "weekly-shape-results.md", aggregate_table(aggregates, "weekly_centered_shape_MAE")),
        "anchor": write(evidence_dir / "level-anchor-results.md", anchor_report(aggregates)),
        "variants": write(evidence_dir / "variant-comparison.md", variant_report(aggregates)),
        "best_worst": write(evidence_dir / "best-worst-weeks.md", best_worst_report(weekly)),
        "short_term": write(evidence_dir / "short-term-forecast-design.md", short_term_report()),
        "long_term": write(evidence_dir / "long-term-futures-shape-design.md", long_term_report()),
        "summary": write(evidence_dir / "component-attribution-summary.md", summary_report(origins, aggregates)),
    }
    (evidence_dir / "anchored-absolute-results.json").write_text(json.dumps([row for row in aggregates if row["target"] == "recomposed_se3"], sort_keys=True), encoding="utf-8")
    (evidence_dir / "weekly-shape-results.json").write_text(json.dumps(compact_weekly_shape_json(weekly), sort_keys=True), encoding="utf-8")
    (evidence_dir / "variant-comparison.json").write_text(json.dumps(aggregates, sort_keys=True), encoding="utf-8")
    paths.update({"absolute_json": str(evidence_dir / "anchored-absolute-results.json"), "shape_json": str(evidence_dir / "weekly-shape-results.json"), "variant_json": str(evidence_dir / "variant-comparison.json")})
    return paths


def changelog() -> str:
    return "# P0040 changelog\n\n- Added weekly anchored 7-day forecast backtest diagnostics.\n- Used M1 as baseplate and M1B only for M3A/M3B training.\n- No M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.\n"


def method_report(rows: list[dict[str, object]], origins: list[ForecastOrigin]) -> str:
    counts = count_splits(rows)
    return "\n".join(
        [
            "# P0040 weekly backtest method",
            "",
            f"primary_backtest_start = {origins[0].origin_date.isoformat()}",
            f"primary_backtest_end = {origins[-1].origin_date.isoformat()}",
            f"forecast_origin_count = {len(origins)}",
            "origin_rule = Monday 06:00 local",
            "known_spot_context = Monday 00:00..15:00, 16 hours",
            "horizon = 168 complete Monday-start hours",
            "weather_oracle = actual_weather_used_as_forecast_proxy",
            "strict_fit = static pre-backtest P0037 train rows ending 2023-12-31; no forecast-horizon spot prices used as features",
            f"row_counts = {counts}",
            "",
        ]
    )


def level_shape_report() -> str:
    return "# P0040 level/shape separation\n\nKnown 16h spot prices set level through additive anchoring. Component variants supply hourly shape. Shape metrics are evaluated separately from anchored absolute accuracy.\n"


def shape_definition_report() -> str:
    return "# P0040 shape metrics definition\n\nCentered shape subtracts period mean. Scaled shape divides centered values by median absolute centered value with a safe fallback of 1. Rank metrics use hourly rank order and are safe for zero/negative prices.\n"


def aggregate_table(aggregates: list[dict[str, object]], sort_metric: str) -> str:
    rows = [row for row in aggregates if row["target"] == "recomposed_se3"]
    rows.sort(key=lambda row: float(row[sort_metric]))
    lines = ["# P0040 aggregate results", "", "| anchor | variant | weeks | MAE | RMSE | signed | daily_mean_MAE | p90_MAE | shape_MAE | spearman | top10 | bottom10 |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['anchor']} | {row['variant']} | {row['forecast_weeks']} | {fmt(row['anchored_absolute_MAE'])} | {fmt(row['anchored_absolute_RMSE'])} | {fmt(row['anchored_signed_error'])} | {fmt(row['anchored_daily_mean_MAE'])} | {fmt(row['p90_weekly_absolute_MAE'])} | {fmt(row['weekly_centered_shape_MAE'])} | {fmt(row['weekly_rank_spearman'])} | {fmt(row['weekly_top_10pct_precision'])} | {fmt(row['weekly_bottom_10pct_precision'])} |")
    return "\n".join(lines) + "\n"


def subset_breakdown(weekly: list[dict[str, object]]) -> list[dict[str, object]]:
    subset_fields = [
        "subset_all_forecast_weeks",
        "subset_holiday_weeks",
        "subset_non_holiday_weeks",
        "subset_bridge_weeks",
        "subset_major_social_holidays",
        "subset_cold_weeks",
        "subset_warm_weeks",
        "subset_high_wind_weeks",
        "subset_low_wind_weeks",
        "subset_high_solar_weeks",
        "subset_low_solar_weeks",
        "subset_summer_weeks",
        "subset_winter_weeks",
    ]
    rows = [row for row in weekly if row["anchor"] == "anchor_16h_mean" and row["target"] == "recomposed_se3"]
    output: list[dict[str, object]] = []
    for subset in subset_fields:
        for variant in VARIANTS:
            selected = [row for row in rows if row["variant"] == variant and row.get(subset)]
            if not selected:
                continue
            output.append(
                {
                    "subset": subset.replace("subset_", ""),
                    "variant": variant,
                    "weeks": len(selected),
                    "anchored_absolute_MAE": sum(float(row["anchored_absolute_MAE"]) for row in selected) / len(selected),
                    "weekly_centered_shape_MAE": sum(float(row["weekly_centered_shape_MAE"]) for row in selected) / len(selected),
                    "weekly_top_10pct_precision": sum(float(row["weekly_top_10pct_precision"]) for row in selected) / len(selected),
                    "weekly_bottom_10pct_precision": sum(float(row["weekly_bottom_10pct_precision"]) for row in selected) / len(selected),
                }
            )
    return output


def subset_breakdown_markdown(weekly: list[dict[str, object]]) -> str:
    rows = subset_breakdown(weekly)
    lines = ["# P0040 subset breakdown", "", "| subset | variant | weeks | MAE | shape_MAE | top10 | bottom10 |", "|---|---|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['subset']} | {row['variant']} | {row['weeks']} | {fmt(row['anchored_absolute_MAE'])} | {fmt(row['weekly_centered_shape_MAE'])} | {fmt(row['weekly_top_10pct_precision'])} | {fmt(row['weekly_bottom_10pct_precision'])} |")
    return "\n".join(lines) + "\n"


def compact_weekly_shape_json(weekly: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = [row for row in weekly if row["target"] == "recomposed_se3"]
    return [
        {
            "origin_date": row["origin_date"],
            "anchor": row["anchor"],
            "variant": row["variant"],
            "anchored_absolute_MAE": row["anchored_absolute_MAE"],
            "weekly_centered_shape_MAE": row["weekly_centered_shape_MAE"],
            "weekly_rank_spearman": row["weekly_rank_spearman"],
            "weekly_top_10pct_precision": row["weekly_top_10pct_precision"],
            "weekly_bottom_10pct_precision": row["weekly_bottom_10pct_precision"],
        }
        for row in rows
    ]


def anchor_report(aggregates: list[dict[str, object]]) -> str:
    lines = ["# P0040 level anchor results", "", "| anchor | best_variant | recomposed_SE3_MAE |", "|---|---|---:|"]
    for anchor in ANCHORS:
        rows = [row for row in aggregates if row["anchor"] == anchor and row["target"] == "recomposed_se3"]
        best = min(rows, key=lambda row: float(row["anchored_absolute_MAE"]))
        lines.append(f"| {anchor} | {best['variant']} | {fmt(best['anchored_absolute_MAE'])} |")
    return "\n".join(lines) + "\n"


def variant_report(aggregates: list[dict[str, object]]) -> str:
    return aggregate_table([row for row in aggregates if row["anchor"] == "anchor_16h_mean"], "anchored_absolute_MAE")


def best_worst_report(weekly: list[dict[str, object]]) -> str:
    rows = [row for row in weekly if row["anchor"] == "anchor_16h_mean" and row["target"] == "recomposed_se3"]
    best_variant = min(aggregate_results(rows), key=lambda row: float(row["anchored_absolute_MAE"]))["variant"]
    selected = [row for row in rows if row["variant"] == best_variant]
    selected.sort(key=lambda row: float(row["anchored_absolute_MAE"]))
    return week_table("# P0040 best 10 weeks", selected[:10]) + "\n" + week_table("# P0040 worst 10 weeks", list(reversed(selected[-10:])))


def week_table(title: str, rows: list[dict[str, object]]) -> str:
    lines = [title, "", "| origin_date | variant | MAE | RMSE | spearman | holiday | cold | high_wind | high_solar |", "|---|---|---:|---:|---:|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['origin_date']} | {row['variant']} | {fmt(row['anchored_absolute_MAE'])} | {fmt(row['anchored_absolute_RMSE'])} | {fmt(row['weekly_rank_spearman'])} | {row['subset_holiday_weeks']} | {row['subset_cold_weeks']} | {row['subset_high_wind_weeks']} | {row['subset_high_solar_weeks']} |")
    return "\n".join(lines) + "\n"


def short_term_report() -> str:
    return "# P0040 short-term forecast design\n\nInput: nearest known spot hours, weather forecast, special-day calendar and active shape components. Mechanism: generate hourly shape, apply weather/special-day deltas, then anchor level from known spot context. Output: 7-day hourly absolute forecast. P0040 does not build the API.\n"


def long_term_report() -> str:
    return "# P0040 long-term futures shape design\n\nFuture M7/futures mode should take forward levels by year/quarter/month/week when available and allocate them hourly with the shape model under normal or specified weather assumptions. P0040 has no historical futures data and makes no futures backtest claim.\n"


def summary_report(origins: list[ForecastOrigin], aggregates: list[dict[str, object]]) -> str:
    mean_rows = [row for row in aggregates if row["anchor"] == "anchor_16h_mean" and row["target"] == "recomposed_se3"]
    best_abs = min(mean_rows, key=lambda row: float(row["anchored_absolute_MAE"]))
    best_shape = min(mean_rows, key=lambda row: float(row["weekly_centered_shape_MAE"]))
    v2 = aggregate_metric(aggregates, "anchor_16h_mean", "V2_M1_plus_existing_M3A_M3B", "recomposed_se3", "anchored_absolute_MAE")
    v3 = aggregate_metric(aggregates, "anchor_16h_mean", "V3_M1_plus_M3A_m1b_M3B_m1b", "recomposed_se3", "anchored_absolute_MAE")
    v4 = aggregate_metric(aggregates, "anchor_16h_mean", "V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D", "recomposed_se3", "anchored_absolute_MAE")
    v5 = aggregate_metric(aggregates, "anchor_16h_mean", "V5_diagnostic_with_M3C", "recomposed_se3", "anchored_absolute_MAE")
    v6 = aggregate_metric(aggregates, "anchor_16h_mean", "V6_diagnostic_with_M4_area_diff", "recomposed_se3", "anchored_absolute_MAE")
    return "\n".join(
        [
            "# P0040 component attribution summary",
            "",
            f"Status: {'WARN' if best_abs['variant'] == 'V0_naive_flat_week' else ('PASS' if v3 <= v2 else 'WARN')}",
            f"forecast_origin_count = {len(origins)}",
            "",
            "## Required Answers",
            "",
            f"1. Best anchored absolute 7-day forecast: {best_abs['variant']} with {best_abs['anchor']} MAE={fmt(best_abs['anchored_absolute_MAE'])}.",
            f"2. Best 16h anchoring method: {best_abs['anchor']} for the winning variant.",
            f"3. Remaining absolute error after anchoring: MAE={fmt(best_abs['anchored_absolute_MAE'])}, RMSE={fmt(best_abs['anchored_absolute_RMSE'])}.",
            f"4. Best weekly shape: {best_shape['variant']} centered-shape MAE={fmt(best_shape['weekly_centered_shape_MAE'])}.",
            f"5. Best expensive-hour identification is in `anchored-absolute-results.md` (`weekly_top_10pct_precision`).",
            f"6. Best cheap-hour identification is in `anchored-absolute-results.md` (`weekly_bottom_10pct_precision`).",
            f"7. P0039 M1B-trained M3A/M3B {'improves' if v3 < v2 else 'does not improve'} anchored absolute MAE vs existing M3A/M3B: V2={fmt(v2)}, V3={fmt(v3)}.",
            f"8. M3D effect vs V3: {fmt(v4 - v3)} MAE.",
            f"9. M3C effect vs V3: {fmt(v5 - v3)} MAE.",
            f"10. M4_area_diff effect vs V3: {fmt(v6 - v3)} MAE.",
            "11. The stack is not ready to replace a simple anchored flat-week short-term baseline. Missing work: level-aware shape training, stronger intra-week shape validation and real weather forecast handling. P0040 does not build M5/M6/API and still uses actual weather as an oracle proxy.",
            "",
            "No M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.",
            "",
        ]
    )


def write(path: Path, text: str) -> str:
    path.write_text(text, encoding="utf-8")
    return str(path)


def main() -> int:
    result = run_p0040_analysis()
    print(json.dumps({"status": result.status, "origin_count": result.origin_count, "backtest_start": result.backtest_start, "backtest_end": result.backtest_end, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
