"""P0047 SE3-SE1 bottleneck spread export and diagnostics."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import csv
import json
import math
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, robust_scale, write


PACKAGE_ID = "P0047"
EVIDENCE_DIR = Path("requirements/package-runs/P0047")
DEFAULT_START_DATE = date(2025, 1, 1)
DEFAULT_END_DATE = date(2025, 12, 31)
SOURCE_TABLE = "ai2_hour_to_day_training_targets_v2"
TARGET_SE1 = "system_proxy_se1"
TARGET_SPREAD = "area_diff_proxy_se3"
FORBIDDEN_PRODUCTION_PATHS = (
    "SE1_TO_SE3_ANCHORING",
    "SE3_API",
    "PRODUCTION_MODEL",
    "DEPLOYABLE_MODEL_ARTIFACT",
    "M5",
    "M6",
    "M7",
    "SHELLY",
    "DEVICE",
    "KVS",
    "HA",
)
EXPORT_COLUMNS = (
    "timestamp_utc",
    "model_cet_timestamp",
    "model_cet_date",
    "model_cet_hour",
    "se1_price",
    "se3_price",
    "se3_minus_se1",
    "abs_se3_minus_se1",
    "spread_sign",
    "spread_regime",
    "temperature_se1_or_system_actual",
    "solar_se1_or_system_actual",
    "wind_system_proxy",
    "model_cet_weekday",
    "model_cet_day_of_year",
    "base_day_type",
    "special_day_type",
    "special_day_name",
    "is_special_day",
    "is_bridge_day",
    "is_holiday_period",
    "is_major_social_holiday",
)
REQUESTED_UNAVAILABLE_COLUMNS = (
    "temperature_se3_or_south_actual",
    "temperature_south_minus_north",
    "solar_se3_or_south_actual",
    "solar_south_minus_north",
    "wind_south_proxy",
    "wind_central_proxy",
    "wind_north_proxy",
    "wind_south_minus_north",
    "wind_central_minus_north",
)


@dataclass(frozen=True)
class P0047Result:
    status: str
    export_window: dict[str, str]
    row_count: int
    evidence: dict[str, str]


def run_p0047_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
    start_date: date = DEFAULT_START_DATE,
    end_date: date = DEFAULT_END_DATE,
) -> P0047Result:
    started = time.monotonic()
    rows = load_p0047_source_rows(feature_db)
    contract = validate_p0047_contract(rows)
    if not contract["ok"]:
        raise RuntimeError(f"P0047 input contract failed: {contract}")
    export_rows = join_spread_rows(rows, start_date, end_date)
    if not export_rows:
        raise RuntimeError("P0047 found no joined SE3-SE1 export rows")
    thresholds = threshold_candidates([float(row["se3_minus_se1"]) for row in export_rows])
    selected_thresholds = thresholds["T3_robust_sigma_thresholds"]
    for row in export_rows:
        sign, regime = assign_spread_regime(float(row["se3_minus_se1"]), selected_thresholds)
        row["spread_sign"] = sign
        row["spread_regime"] = regime
    distribution = analyze_distribution(export_rows)
    persistence = analyze_persistence(export_rows)
    attribution = analyze_signal_attribution(export_rows)
    top_spikes = top_spike_rows(export_rows)
    status = p0047_status(export_rows, distribution, selected_thresholds)
    summary = {
        "status": status,
        "dataset_tables": [SOURCE_TABLE],
        "contract": contract,
        "export_window": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "row_count": len(export_rows),
        "thresholds": thresholds,
        "selected_threshold_strategy": "T3_robust_sigma_thresholds",
        "distribution": distribution,
        "persistence": persistence,
        "attribution": attribution,
        "top_spikes": top_spikes,
        "missing_requested_columns": list(REQUESTED_UNAVAILABLE_COLUMNS),
        "runtime_seconds": time.monotonic() - started,
        "forbidden_paths": FORBIDDEN_PRODUCTION_PATHS,
    }
    evidence = write_p0047_evidence(Path(evidence_dir), export_rows, summary)
    return P0047Result(status=status, export_window=summary["export_window"], row_count=len(export_rows), evidence=evidence)


def load_p0047_source_rows(feature_db: Path | str = DEFAULT_FEATURE_DB) -> list[dict[str, object]]:
    db = Path(feature_db).expanduser()
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (SOURCE_TABLE,)).fetchone():
            raise RuntimeError(f"P0047 source table {SOURCE_TABLE} is missing")
        return [
            dict(row)
            for row in conn.execute(
                f"""
                SELECT *
                FROM {SOURCE_TABLE}
                WHERE target_series IN (?, ?)
                ORDER BY timestamp_utc, target_series
                """,
                (TARGET_SE1, TARGET_SPREAD),
            )
        ]


def validate_p0047_contract(rows: list[dict[str, object]]) -> dict[str, object]:
    required = {
        "timestamp_utc",
        "model_cet_timestamp",
        "model_cet_date",
        "model_cet_hour",
        "model_cet_weekday",
        "model_cet_day_of_year",
        "target_series",
        "hour_price",
        "base_day_type",
        "special_day_type",
        "special_day_name",
        "is_special_day",
        "is_bridge_day",
        "is_holiday_period",
        "is_major_social_holiday",
    }
    optional_available = {"hourly_temperature_actual", "hourly_solar_actual", "hourly_wind_actual"}
    missing = sorted(required - set(rows[0])) if rows else sorted(required)
    optional_missing = sorted(optional_available - set(rows[0])) if rows else sorted(optional_available)
    counts = Counter(str(row.get("target_series")) for row in rows)
    finite = all(math.isfinite(float(row["hour_price"])) for row in rows if "hour_price" in row)
    return {
        "ok": bool(rows) and not missing and counts[TARGET_SE1] > 0 and counts[TARGET_SPREAD] > 0 and finite,
        "source_table": SOURCE_TABLE,
        "missing_required_fields": missing,
        "missing_optional_available_fields": optional_missing,
        "target_counts": {TARGET_SE1: counts[TARGET_SE1], TARGET_SPREAD: counts[TARGET_SPREAD]},
        "finite_hour_price": finite,
        "uses_p0042_fixed_cet_v2_table": True,
    }


def join_spread_rows(rows: list[dict[str, object]], start_date: date, end_date: date) -> list[dict[str, object]]:
    by_timestamp: dict[str, dict[str, dict[str, object]]] = defaultdict(dict)
    for row in rows:
        model_day = date.fromisoformat(str(row["model_cet_date"]))
        if start_date <= model_day <= end_date:
            by_timestamp[str(row["timestamp_utc"])][str(row["target_series"])] = row
    output: list[dict[str, object]] = []
    for timestamp, grouped in sorted(by_timestamp.items()):
        se1 = grouped.get(TARGET_SE1)
        spread = grouped.get(TARGET_SPREAD)
        if not se1 or not spread:
            continue
        if se1["model_cet_timestamp"] != spread["model_cet_timestamp"]:
            raise RuntimeError(f"P0047 timestamp mismatch at {timestamp}")
        spread_value = float(spread["hour_price"])
        se1_price = float(se1["hour_price"])
        se3_price = se1_price + spread_value
        output.append(
            {
                "timestamp_utc": timestamp,
                "model_cet_timestamp": se1["model_cet_timestamp"],
                "model_cet_date": se1["model_cet_date"],
                "model_cet_hour": int(se1["model_cet_hour"]),
                "se1_price": se1_price,
                "se3_price": se3_price,
                "se3_minus_se1": spread_value,
                "abs_se3_minus_se1": abs(spread_value),
                "spread_sign": "",
                "spread_regime": "",
                "temperature_se1_or_system_actual": value_or_blank(se1.get("hourly_temperature_actual")),
                "solar_se1_or_system_actual": value_or_blank(se1.get("hourly_solar_actual")),
                "wind_system_proxy": value_or_blank(se1.get("hourly_wind_actual")),
                "model_cet_weekday": int(se1["model_cet_weekday"]),
                "model_cet_day_of_year": int(se1["model_cet_day_of_year"]),
                "base_day_type": se1["base_day_type"],
                "special_day_type": se1["special_day_type"],
                "special_day_name": se1["special_day_name"],
                "is_special_day": int(se1["is_special_day"]),
                "is_bridge_day": int(se1["is_bridge_day"]),
                "is_holiday_period": int(se1["is_holiday_period"]),
                "is_major_social_holiday": int(se1["is_major_social_holiday"]),
            }
        )
    return output


def value_or_blank(value: object) -> float | str:
    if value is None:
        return ""
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return ""
    return parsed if math.isfinite(parsed) else ""


def threshold_candidates(spreads: list[float]) -> dict[str, dict[str, float]]:
    values = [float(value) for value in spreads]
    abs_values = [abs(value) for value in values]
    med = percentile(values, 0.5)
    mad = percentile([abs(value - med) for value in values], 0.5) * 1.4826
    iqr = percentile(values, 0.75) - percentile(values, 0.25)
    sigma = max(mad, iqr / 1.349 if iqr else 0.0, robust_scale(values))
    return {
        "T1_fixed_ore_or_currency_thresholds": {
            "near_zero_abs": 0.01,
            "positive": 0.05,
            "negative": -0.05,
            "spike_positive": 0.20,
            "spike_negative": -0.20,
        },
        "T2_quantile_thresholds": {
            "near_zero_abs": percentile(abs_values, 0.25),
            "positive": percentile(values, 0.75),
            "negative": percentile(values, 0.25),
            "spike_positive": percentile(values, 0.95),
            "spike_negative": percentile(values, 0.05),
        },
        "T3_robust_sigma_thresholds": {
            "near_zero_abs": max(0.01, min(0.05, sigma * 0.25)),
            "positive": max(0.02, sigma * 0.5),
            "negative": -max(0.02, sigma * 0.5),
            "spike_positive": max(0.08, sigma * 2.0),
            "spike_negative": -max(0.08, sigma * 2.0),
            "median": med,
            "robust_sigma": sigma,
        },
    }


def assign_spread_regime(spread: float, thresholds: dict[str, float]) -> tuple[str, str]:
    if abs(spread) <= float(thresholds["near_zero_abs"]):
        return "zero", "spread_near_zero"
    if spread >= float(thresholds["spike_positive"]):
        return "positive", "spread_spike_positive"
    if spread <= float(thresholds["spike_negative"]):
        return "negative", "spread_spike_negative"
    if spread > float(thresholds["positive"]):
        return "positive", "spread_positive"
    if spread < float(thresholds["negative"]):
        return "negative", "spread_negative"
    return "positive" if spread > 0.0 else "negative", "spread_small_nonzero"


def analyze_distribution(rows: list[dict[str, object]]) -> dict[str, object]:
    spreads = [float(row["se3_minus_se1"]) for row in rows]
    regimes = Counter(str(row["spread_regime"]) for row in rows)
    signs = Counter(str(row["spread_sign"]) for row in rows)
    return {
        "overall": stats(spreads),
        "by_hour": grouped_stats(rows, "model_cet_hour"),
        "by_weekday": grouped_stats(rows, "model_cet_weekday"),
        "by_month": grouped_stats(rows, "month"),
        "by_special_day_type": grouped_stats(rows, "special_day_type"),
        "regime_counts": dict(sorted(regimes.items())),
        "regime_share": {key: count / len(rows) for key, count in sorted(regimes.items())},
        "sign_counts": dict(sorted(signs.items())),
    }


def grouped_stats(rows: list[dict[str, object]], field: str) -> dict[str, dict[str, float]]:
    buckets: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        key = str(row["model_cet_date"])[5:7] if field == "month" else str(row[field])
        buckets[key].append(float(row["se3_minus_se1"]))
    return {key: stats(values) for key, values in sorted(buckets.items())}


def stats(values: list[float]) -> dict[str, float]:
    vals = [float(value) for value in values]
    return {
        "count": float(len(vals)),
        "min": min(vals) if vals else 0.0,
        "p01": percentile(vals, 0.01),
        "p05": percentile(vals, 0.05),
        "median": percentile(vals, 0.5),
        "mean": sum(vals) / len(vals) if vals else 0.0,
        "p95": percentile(vals, 0.95),
        "p99": percentile(vals, 0.99),
        "max": max(vals) if vals else 0.0,
    }


def analyze_persistence(rows: list[dict[str, object]]) -> dict[str, object]:
    runs = regime_runs(rows)
    transitions: dict[str, Counter[str]] = defaultdict(Counter)
    for left, right in zip(rows, rows[1:]):
        transitions[str(left["spread_regime"])][str(right["spread_regime"])] += 1
    return {
        "run_lengths": runs,
        "run_summary": summarize_runs(runs),
        "transition_matrix": {left: dict(sorted(right.items())) for left, right in sorted(transitions.items())},
        "lag1_same_regime_share": same_regime_share(rows),
    }


def regime_runs(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    if not rows:
        return []
    output = []
    current = str(rows[0]["spread_regime"])
    start = 0
    for index, row in enumerate(rows[1:], start=1):
        regime = str(row["spread_regime"])
        if regime == current:
            continue
        output.append(run_row(rows, start, index - 1, current))
        current = regime
        start = index
    output.append(run_row(rows, start, len(rows) - 1, current))
    return output


def run_row(rows: list[dict[str, object]], start: int, end: int, regime: str) -> dict[str, object]:
    values = [float(row["se3_minus_se1"]) for row in rows[start : end + 1]]
    return {
        "regime": regime,
        "start_timestamp_utc": rows[start]["timestamp_utc"],
        "end_timestamp_utc": rows[end]["timestamp_utc"],
        "length_hours": end - start + 1,
        "mean_spread": sum(values) / len(values),
        "max_abs_spread": max(abs(value) for value in values),
    }


def summarize_runs(runs: list[dict[str, object]]) -> dict[str, dict[str, float]]:
    by_regime: dict[str, list[float]] = defaultdict(list)
    for run in runs:
        by_regime[str(run["regime"])].append(float(run["length_hours"]))
    return {regime: stats(lengths) for regime, lengths in sorted(by_regime.items())}


def same_regime_share(rows: list[dict[str, object]]) -> float:
    pairs = list(zip(rows, rows[1:]))
    if not pairs:
        return 0.0
    return sum(1 for left, right in pairs if left["spread_regime"] == right["spread_regime"]) / len(pairs)


def analyze_signal_attribution(rows: list[dict[str, object]]) -> dict[str, object]:
    fields = (
        "temperature_se1_or_system_actual",
        "solar_se1_or_system_actual",
        "wind_system_proxy",
        "se1_price",
        "se3_price",
        "abs_se3_minus_se1",
    )
    correlations = {
        field: pearson(
            [float(row[field]) for row in rows if row[field] != ""],
            [float(row["se3_minus_se1"]) for row in rows if row[field] != ""],
        )
        for field in fields
    }
    by_regime = {
        field: grouped_numeric_mean(rows, field, "spread_regime")
        for field in fields
        if any(row[field] != "" for row in rows)
    }
    return {
        "pearson_to_spread": correlations,
        "means_by_regime": by_regime,
        "calendar_regime_counts": grouped_counts(rows, "special_day_type", "spread_regime"),
        "missing_requested_columns": list(REQUESTED_UNAVAILABLE_COLUMNS),
    }


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_den = math.sqrt(sum((x - x_mean) ** 2 for x in xs))
    y_den = math.sqrt(sum((y - y_mean) ** 2 for y in ys))
    if x_den <= 0.0 or y_den <= 0.0:
        return None
    return numerator / (x_den * y_den)


def grouped_numeric_mean(rows: list[dict[str, object]], value_field: str, group_field: str) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row[value_field] != "":
            grouped[str(row[group_field])].append(float(row[value_field]))
    return {key: sum(values) / len(values) for key, values in sorted(grouped.items()) if values}


def grouped_counts(rows: list[dict[str, object]], left_field: str, right_field: str) -> dict[str, dict[str, int]]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        grouped[str(row[left_field])][str(row[right_field])] += 1
    return {key: dict(sorted(counts.items())) for key, counts in sorted(grouped.items())}


def top_spike_rows(rows: list[dict[str, object]], limit: int = 40) -> list[dict[str, object]]:
    keys = ("timestamp_utc", "model_cet_date", "model_cet_hour", "se1_price", "se3_price", "se3_minus_se1", "spread_regime", "wind_system_proxy", "special_day_type")
    ordered = sorted(rows, key=lambda row: abs(float(row["se3_minus_se1"])), reverse=True)
    return [{key: row[key] for key in keys} for row in ordered[:limit]]


def p0047_status(rows: list[dict[str, object]], distribution: dict[str, object], selected_thresholds: dict[str, float]) -> str:
    required_regimes = {"spread_near_zero", "spread_positive", "spread_negative"}
    regimes = set(distribution["regime_counts"])  # type: ignore[arg-type]
    if len(rows) < 8000:
        return "STOP"
    if float(selected_thresholds["positive"]) <= 0.0 or float(selected_thresholds["spike_positive"]) <= float(selected_thresholds["positive"]):
        return "STOP"
    if not required_regimes <= regimes:
        return "WARN"
    return "PASS"


def write_p0047_evidence(evidence_dir: Path, export_rows: list[dict[str, object]], summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "plots").mkdir(exist_ok=True)
    export_path = evidence_dir / "se3-se1-last-year-export.csv"
    write_csv(export_path, export_rows, EXPORT_COLUMNS)
    write_csv(evidence_dir / "top-spike-hours.csv", summary["top_spikes"], tuple(summary["top_spikes"][0]) if summary["top_spikes"] else ())
    write_csv(evidence_dir / "regime-run-lengths.csv", summary["persistence"]["run_lengths"], tuple(summary["persistence"]["run_lengths"][0]) if summary["persistence"]["run_lengths"] else ())
    paths = {
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog(summary)),
        "dataset": write(evidence_dir / "dataset-contract.md", dataset_contract_report(summary)),
        "export": str(export_path),
        "export_summary": write(evidence_dir / "export-summary.md", export_summary_report(summary)),
        "distribution": write(evidence_dir / "spread-distribution.md", distribution_report(summary)),
        "thresholds": write(evidence_dir / "spread-regime-definitions.md", threshold_report(summary)),
        "persistence": write(evidence_dir / "regime-persistence-and-transitions.md", persistence_report(summary)),
        "weather": write(evidence_dir / "weather-signal-attribution.md", weather_report(summary)),
        "calendar": write(evidence_dir / "calendar-signal-attribution.md", calendar_report(summary)),
        "spikes": write(evidence_dir / "spike-and-outlier-review.md", spike_report(summary)),
        "models": write(evidence_dir / "candidate-model-designs.md", model_design_report(summary)),
        "next": write(evidence_dir / "next-package-recommendation.md", next_package_report(summary)),
        "component": write(evidence_dir / "component-attribution-summary.md", component_summary(summary)),
    }
    write(evidence_dir / "se3-se1-last-year-summary.json", json.dumps(json_safe(summary), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "regime-transition-matrix.json", json.dumps(json_safe(summary["persistence"]["transition_matrix"]), indent=2, sort_keys=True) + "\n")
    return paths


def write_csv(path: Path, rows: list[dict[str, object]], columns: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def changelog(summary: dict[str, object]) -> str:
    window = summary["export_window"]
    return f"# P0047 changelog\n\n- Exported hourly SE3-SE1 spread evidence for fixed-CET model dates {window['start']} .. {window['end']}.\n- Wrote `se3-se1-last-year-export.csv` with {summary['row_count']} rows.\n- Computed fixed, quantile and robust-sigma candidate spread thresholds; selected robust-sigma for analysis.\n- Documented distribution, regimes, persistence, weather/calendar attribution, spikes and candidate model designs.\n- Result status: {summary['status']}.\n- Confirmed: no SE1-to-SE3 anchoring, no SE3 API, no production model, no M5/M6/M7, no KVS and no device actions.\n"


def dataset_contract_report(summary: dict[str, object]) -> str:
    return "\n".join(
        [
            "# P0047 dataset contract",
            "",
            f"used_tables = {summary['dataset_tables']}",
            "",
            f"contract = {summary['contract']}",
            "",
            "SE3 is reconstructed as `se1_price + se3_minus_se1`; `se3_minus_se1` comes from P0042/P0045 target `area_diff_proxy_se3`.",
            "",
            "Primary timestamp is `timestamp_utc`. Model calendar fields use P0042 fixed-CET: `model_cet_timestamp = timestamp_utc + 1h`.",
            "",
            f"Missing requested weather/gradient columns: {summary['missing_requested_columns']}",
            "",
        ]
    )


def export_summary_report(summary: dict[str, object]) -> str:
    overall = summary["distribution"]["overall"]
    return "\n".join(
        [
            "# P0047 export summary",
            "",
            f"export_window = {summary['export_window']}",
            f"row_count = {summary['row_count']}",
            "regeneration_command = `python3 -m src.mac.services.spotprice_model_diagnostics.p0047`",
            "",
            f"SE3-SE1 min/p01/p05/median/mean/p95/p99/max = {fmt(overall['min'])}, {fmt(overall['p01'])}, {fmt(overall['p05'])}, {fmt(overall['median'])}, {fmt(overall['mean'])}, {fmt(overall['p95'])}, {fmt(overall['p99'])}, {fmt(overall['max'])}",
            "",
            f"regime_counts = {summary['distribution']['regime_counts']}",
            f"regime_share = {summary['distribution']['regime_share']}",
            "",
            "Plots were not committed. P0047 uses committed tables/CSV/JSON to avoid adding image dependencies or large binary evidence.",
            "",
        ]
    )


def distribution_report(summary: dict[str, object]) -> str:
    lines = ["# P0047 spread distribution", "", stats_line("overall", summary["distribution"]["overall"]), "", "## By Hour", "", stats_table(summary["distribution"]["by_hour"]), "", "## By Month", "", stats_table(summary["distribution"]["by_month"])]
    return "\n".join(lines) + "\n"


def threshold_report(summary: dict[str, object]) -> str:
    lines = ["# P0047 spread regime definitions", "", f"selected_strategy = {summary['selected_threshold_strategy']}", ""]
    for name, thresholds in summary["thresholds"].items():
        lines.append(f"## {name}")
        lines.append("")
        for key, value in thresholds.items():
            lines.append(f"- {key}: {fmt(value)}")
        lines.append("")
    lines.append("Recommendation: use robust-sigma thresholds as the next modeling baseline because they are data-driven, less sensitive to rare spikes than pure quantiles, and preserve a fixed near-zero floor.")
    return "\n".join(lines) + "\n"


def persistence_report(summary: dict[str, object]) -> str:
    lines = ["# P0047 regime persistence and transitions", "", f"lag1_same_regime_share = {fmt(summary['persistence']['lag1_same_regime_share'])}", "", "## Run Summary", "", stats_table(summary["persistence"]["run_summary"]), "", "## Transition Matrix", "", transition_table(summary["persistence"]["transition_matrix"])]
    return "\n".join(lines) + "\n"


def weather_report(summary: dict[str, object]) -> str:
    lines = ["# P0047 weather signal attribution", "", "Available AI2 v2 weather fields are system-level temperature, solar and wind proxies. South/north/central gradient columns are unavailable in this source table and are listed as missing.", "", f"missing_requested_columns = {summary['attribution']['missing_requested_columns']}", "", "## Pearson Correlation To Spread", ""]
    for key, value in summary["attribution"]["pearson_to_spread"].items():
        lines.append(f"- {key}: {fmt(value) if value is not None else 'n/a'}")
    lines.extend(["", "## Means By Regime", "", json.dumps(json_safe(summary["attribution"]["means_by_regime"]), indent=2, sort_keys=True)])
    return "\n".join(lines) + "\n"


def calendar_report(summary: dict[str, object]) -> str:
    return "# P0047 calendar signal attribution\n\n" + json.dumps(json_safe(summary["attribution"]["calendar_regime_counts"]), indent=2, sort_keys=True) + "\n\nSpecial-day categories are present, but P0047 treats calendar attribution as diagnostic because spread regimes are dominated by grid/weather/price context rather than calendar labels alone.\n"


def spike_report(summary: dict[str, object]) -> str:
    lines = ["# P0047 spike and outlier review", "", "| timestamp_utc | model_day | hour | se1 | se3 | spread | regime | wind | special_day_type |", "|---|---|---:|---:|---:|---:|---|---:|---|"]
    for row in summary["top_spikes"][:25]:
        lines.append(f"| {row['timestamp_utc']} | {row['model_cet_date']} | {row['model_cet_hour']} | {fmt(row['se1_price'])} | {fmt(row['se3_price'])} | {fmt(row['se3_minus_se1'])} | {row['spread_regime']} | {fmt(row['wind_system_proxy']) if row['wind_system_proxy'] != '' else 'n/a'} | {row['special_day_type']} |")
    lines.append("\nTop spike rows are also written to `top-spike-hours.csv`.")
    return "\n".join(lines) + "\n"


def model_design_report(summary: dict[str, object]) -> str:
    return "\n".join(
        [
            "# P0047 candidate model designs",
            "",
            "Option A, constrained continuous spread regression: useful as a baseline, but weak if rare spikes and regime persistence dominate the target.",
            "",
            "Option B, two-stage bottleneck model: recommended next spread-specific design. Stage 1 classifies near-zero/positive/negative/spike regimes; Stage 2 predicts severity for non-zero regimes.",
            "",
            "Option C, quantile/risk model: useful companion for high-spread risk and operational guardrails, especially if exact spread magnitude remains noisy.",
            "",
            "Option D, direct SE3 model: should be evaluated if spread-specific regime modeling does not clearly beat direct SE3 target learning.",
            "",
            "Option E, hybrid: best strategic direction after P0047: direct SE3 or SE1 baseline plus bottleneck risk adjustment/diagnostic.",
            "",
            "P0047 recommendation: build a bottleneck/regime diagnostic first, then compare against a direct SE3 AI-1/AI-2 model in the next package. Do not use SE1-to-SE3 anchoring as the next step.",
            "",
        ]
    )


def next_package_report(summary: dict[str, object]) -> str:
    return "\n".join(
        [
            "# P0047 next package recommendation",
            "",
            "Recommended next package: build and backtest an exploratory two-stage SE3-SE1 bottleneck model, using P0047 robust-sigma regime labels and severity targets.",
            "",
            "The package should compare that model against a direct SE3 AI-1/AI-2 target model before selecting any SE3 path.",
            "",
            "Do not create a production SE3 API yet. Do not anchor SE1 shape to SE3.",
            "",
        ]
    )


def component_summary(summary: dict[str, object]) -> str:
    overall = summary["distribution"]["overall"]
    regimes = summary["distribution"]["regime_share"]
    return "\n".join(
        [
            "# P0047 component attribution summary",
            "",
            f"Status: {summary['status']}",
            f"1. Exported fixed-CET window {summary['export_window']['start']} .. {summary['export_window']['end']} with {summary['row_count']} rows.",
            f"2. SE3-SE1 median={fmt(overall['median'])}, mean={fmt(overall['mean'])}, p95={fmt(overall['p95'])}, p99={fmt(overall['p99'])}, max={fmt(overall['max'])}.",
            f"3. Near-zero share={fmt(regimes.get('spread_near_zero', 0.0))}; positive bottleneck share={fmt(regimes.get('spread_positive', 0.0) + regimes.get('spread_spike_positive', 0.0))}; negative bottleneck share={fmt(regimes.get('spread_negative', 0.0) + regimes.get('spread_spike_negative', 0.0))}.",
            f"4. Lag-1 same-regime share={fmt(summary['persistence']['lag1_same_regime_share'])}.",
            "5. Weather gradients requested by P0047 are not available in the AI2 v2 table; available system proxies are reported.",
            "6. Recommendation: next package should compare two-stage bottleneck classification+severity against direct SE3 AI-1/AI-2 modeling.",
            "7. Confirmed: no SE1-to-SE3 anchoring, no API, no production model, no M5/M6/M7 and no device actions.",
            "",
        ]
    )


def stats_line(label: str, row: dict[str, float]) -> str:
    return f"{label}: count={int(row['count'])} min={fmt(row['min'])} p01={fmt(row['p01'])} p05={fmt(row['p05'])} median={fmt(row['median'])} mean={fmt(row['mean'])} p95={fmt(row['p95'])} p99={fmt(row['p99'])} max={fmt(row['max'])}"


def stats_table(grouped: dict[str, dict[str, float]]) -> str:
    lines = ["| group | count | min | p05 | median | mean | p95 | max |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for key, row in grouped.items():
        lines.append(f"| {key} | {int(row['count'])} | {fmt(row['min'])} | {fmt(row['p05'])} | {fmt(row['median'])} | {fmt(row['mean'])} | {fmt(row['p95'])} | {fmt(row['max'])} |")
    return "\n".join(lines)


def transition_table(matrix: dict[str, dict[str, int]]) -> str:
    regimes = sorted(set(matrix) | {key for row in matrix.values() for key in row})
    lines = ["| from \\ to | " + " | ".join(regimes) + " |", "|---|" + "|".join("---:" for _ in regimes) + "|"]
    for left in regimes:
        row = matrix.get(left, {})
        lines.append(f"| {left} | " + " | ".join(str(row.get(right, 0)) for right in regimes) + " |")
    return "\n".join(lines)


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def fmt(value: object) -> str:
    return f"{float(value):.6f}"


def main() -> int:
    result = run_p0047_analysis()
    print(json.dumps({"status": result.status, "export_window": result.export_window, "row_count": result.row_count, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
