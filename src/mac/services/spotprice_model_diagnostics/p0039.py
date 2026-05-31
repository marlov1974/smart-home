"""P0039 holiday-clean M1B and sequential residual diagnostics."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import json
import sqlite3
from statistics import median

from src.mac.services.spotprice_model_diagnostics.p0037 import (
    TARGET_FIELDS,
    count_splits,
    fit_m1_surface,
    fit_m2_signal_normals,
    fit_strict_components,
    fmt,
    load_diagnostic_rows,
    m3b_key,
    predict_m1,
    predict_m2_normal,
)
from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_temperature_normalization.core import (
    DEFAULT_PRICE_DB_PATH,
    DEFAULT_WEATHER_DB_PATH,
    M3_PRIMARY_ANOMALY_SIGNAL,
    TARGETS,
    temperature_bucket,
)


EVIDENCE_DIR = Path("requirements/package-runs/P0039")
PACKAGE_ID = "P0039"
CLEAN_M1B_DAY_TYPES = frozenset({"normal_weekday", "normal_saturday", "normal_sunday"})
M1B_VARIANTS = (
    "M1",
    "M1B_training_base_only",
    "M1_existing_M3A_M3B",
    "M1_M3A_m1b",
    "M1_M3A_m1b_M3B_m1b",
)
TAXONOMY = {
    "A": "temperature",
    "B": "special_days",
    "C": "solar",
    "D": "wind",
}


@dataclass(frozen=True)
class P0039Result:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0039_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    price_db: Path | str = DEFAULT_PRICE_DB_PATH,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0039Result:
    rows = load_diagnostic_rows(feature_db=feature_db, price_db=price_db, weather_db=weather_db)
    fit_strict_components(rows)
    fit_m1b_components(rows)
    matrix = build_p0039_matrix(rows)
    persist_p0039_feature_outputs(rows, feature_db)
    evidence = write_p0039_evidence(Path(evidence_dir), rows, matrix)
    status = "PASS" if _mae(matrix, "M1_M3A_m1b_M3B_m1b", "recomposed_se3") < _mae(matrix, "M1_existing_M3A_M3B", "recomposed_se3") else "WARN"
    return P0039Result(status=status, row_counts=count_splits(rows), evidence=evidence)


def is_m1b_clean_training_row(row: dict[str, object]) -> bool:
    return str(row["special_day_type"]) in CLEAN_M1B_DAY_TYPES and not bool(row["is_special_day"])


def fit_m1b_components(rows: list[dict[str, object]]) -> None:
    train = [row for row in rows if row["split"] == "train"]
    clean_train = [row for row in train if is_m1b_clean_training_row(row)]
    if not clean_train:
        raise RuntimeError("P0039 M1B has no clean train rows")
    for target, short in TARGET_FIELDS.items():
        surface = fit_m1_surface(clean_train, TARGETS[target])
        for row in rows:
            row[f"m1b_{short}"] = predict_m1(surface, row)
    signals = set(M3_PRIMARY_ANOMALY_SIGNAL.values())
    m2_surfaces = {signal: fit_m2_signal_normals(clean_train, signal) for signal in signals}
    for row in rows:
        row["m1b_training_policy"] = "include" if is_m1b_clean_training_row(row) else "exclude_special_contaminated"
        for signal, surface in m2_surfaces.items():
            normal = predict_m2_normal(surface, row)
            row[f"m1b_{signal}_normal"] = normal
            row[f"m1b_{signal}_anomaly"] = float(row[signal]) - normal
            row[f"m1b_{signal}_bucket"] = temperature_bucket(row[f"m1b_{signal}_anomaly"])
    m3a = fit_m3a_m1b_deltas(clean_train)
    for row in rows:
        for target, short in TARGET_FIELDS.items():
            signal = M3_PRIMARY_ANOMALY_SIGNAL[target]
            bucket = str(row[f"m1b_{signal}_bucket"])
            row[f"m3a_m1b_{short}"] = m3a[(target, bucket)]
    m3b, stats = fit_m3b_m1b_deltas(train)
    for row in rows:
        for target, short in TARGET_FIELDS.items():
            key = m3b_key(target, row)
            row[f"m3b_m1b_{short}"] = m3b.get(key, 0.0)
            row[f"m3b_m1b_sample_count_{short}"] = stats.get(key, {}).get("sample_count", 0.0)
            row[f"m3b_m1b_shrinkage_{short}"] = stats.get(key, {}).get("shrinkage_factor", 0.0)
            row[f"m3ab_m1b_normalized_{short}"] = float(row[TARGETS[target]]) - float(row[f"m3a_m1b_{short}"]) - float(row[f"m3b_m1b_{short}"])
    for row in rows:
        row["m3ab_m1b_normalized_se3"] = row["m3ab_m1b_normalized_se1"] + row["m3ab_m1b_normalized_area"]


def fit_m3a_m1b_deltas(clean_train: list[dict[str, object]]) -> dict[tuple[str, str], float]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in clean_train:
        for target, short in TARGET_FIELDS.items():
            signal = M3_PRIMARY_ANOMALY_SIGNAL[target]
            bucket = str(row[f"m1b_{signal}_bucket"])
            residual = float(row[TARGETS[target]]) - float(row[f"m1b_{short}"])
            grouped[(target, bucket)].append(residual)
    output: dict[tuple[str, str], float] = {}
    for target in TARGET_FIELDS:
        normal_values = grouped.get((target, "normal"), [])
        normal_median = float(median(normal_values)) if normal_values else 0.0
        cap = 0.50 if target == "system_proxy_se1" else 0.35
        for bucket in ("extreme_cold", "cold", "normal", "warm", "extreme_warm"):
            values = grouped.get((target, bucket), [])
            med = float(median(values)) if values else normal_median
            raw_delta = 0.0 if bucket == "normal" else 0.50 * (med - normal_median)
            output[(target, bucket)] = max(-cap, min(cap, raw_delta))
    return output


def fit_m3b_m1b_deltas(train: list[dict[str, object]]) -> tuple[dict[tuple[str, str, str, str, str], float], dict[tuple[str, str, str, str, str], dict[str, float]]]:
    grouped: dict[tuple[str, str, str, str, str], list[float]] = defaultdict(list)
    for row in train:
        if not row["is_special_day"]:
            continue
        for target, short in TARGET_FIELDS.items():
            residual = float(row[TARGETS[target]]) - float(row[f"m1b_{short}"]) - float(row[f"m3a_m1b_{short}"])
            grouped[m3b_key(target, row)].append(residual)
    deltas: dict[tuple[str, str, str, str, str], float] = {}
    stats: dict[tuple[str, str, str, str, str], dict[str, float]] = {}
    for key, values in grouped.items():
        target = key[0]
        med = float(median(values))
        shrinkage = len(values) / (len(values) + 24.0)
        cap = 0.50 if target == "system_proxy_se1" else 0.35
        deltas[key] = max(-cap, min(cap, med * shrinkage))
        stats[key] = {"sample_count": float(len(values)), "shrinkage_factor": shrinkage, "median_residual": med}
    return deltas, stats


def build_p0039_matrix(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    holdout = [row for row in rows if row["split"] == "holdout"]
    output: list[dict[str, object]] = []
    baselines: dict[str, float] = {}
    previous: dict[str, float] = {}
    for variant in M1B_VARIANTS:
        for target in ("system_proxy_se1", "area_diff_proxy_se3", "recomposed_se3"):
            actual, predicted = series_for_p0039_variant(holdout, variant, target)
            value = mae(actual, predicted)
            key = target
            if variant == "M1":
                baselines[key] = value
            output.append(
                {
                    "holdout_year": 2025,
                    "variant": variant,
                    "target": target,
                    "MAE": value,
                    "RMSE": rmse(actual, predicted),
                    "signed_error": sum(p - a for a, p in zip(actual, predicted)) / len(actual),
                    "MAE_delta_vs_M1": value - baselines.get(key, value),
                    "MAE_delta_vs_previous_variant": value - previous.get(key, value),
                }
            )
            previous[key] = value
    return output


def series_for_p0039_variant(rows: list[dict[str, object]], variant: str, target: str) -> tuple[list[float], list[float]]:
    if target == "recomposed_se3":
        actual_se1, pred_se1 = series_for_p0039_variant(rows, variant, "system_proxy_se1")
        actual_area, pred_area = series_for_p0039_variant(rows, variant, "area_diff_proxy_se3")
        return [a + b for a, b in zip(actual_se1, actual_area)], [a + b for a, b in zip(pred_se1, pred_area)]
    short = TARGET_FIELDS[target]
    actual_col = "actual_se1" if short == "se1" else "actual_area_diff"
    actual = [float(row[actual_col]) for row in rows]
    if variant == "M1":
        predicted = [float(row[f"m1_raw_{short}"]) for row in rows]
    elif variant == "M1B_training_base_only":
        predicted = [float(row[f"m1b_{short}"]) for row in rows]
    elif variant == "M1_existing_M3A_M3B":
        predicted = [float(row[f"m1_raw_{short}"]) + float(row[f"m3a_{short}"]) + float(row[f"m3b_{short}"]) for row in rows]
    elif variant == "M1_M3A_m1b":
        predicted = [float(row[f"m1_raw_{short}"]) + float(row[f"m3a_m1b_{short}"]) for row in rows]
    elif variant == "M1_M3A_m1b_M3B_m1b":
        predicted = [float(row[f"m1_raw_{short}"]) + float(row[f"m3a_m1b_{short}"]) + float(row[f"m3b_m1b_{short}"]) for row in rows]
    else:
        raise ValueError(f"unknown P0039 variant: {variant}")
    return actual, predicted


def persist_p0039_feature_outputs(rows: list[dict[str, object]], feature_db: Path | str) -> None:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS m1b_holiday_clean_normal_price (
              utc_hour_start TEXT PRIMARY KEY,
              local_date TEXT NOT NULL,
              local_hour INTEGER NOT NULL,
              normal_price_m1b_se1 REAL NOT NULL,
              normal_price_m1b_area_diff REAL NOT NULL,
              normal_price_m1b_se3 REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS m1b_training_row_policy (
              utc_hour_start TEXT PRIMARY KEY,
              local_date TEXT NOT NULL,
              local_hour INTEGER NOT NULL,
              split TEXT NOT NULL,
              special_day_type TEXT NOT NULL,
              special_day_name TEXT NOT NULL,
              policy TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS m3a_temperature_delta_m1b (
              target TEXT NOT NULL,
              utc_hour_start TEXT NOT NULL,
              local_date TEXT NOT NULL,
              local_hour INTEGER NOT NULL,
              temperature_anomaly REAL NOT NULL,
              temperature_bucket TEXT NOT NULL,
              temperature_delta REAL NOT NULL,
              PRIMARY KEY (target, utc_hour_start)
            );
            CREATE TABLE IF NOT EXISTS m3b_special_day_delta_m1b (
              target TEXT NOT NULL,
              utc_hour_start TEXT NOT NULL,
              local_date TEXT NOT NULL,
              local_hour INTEGER NOT NULL,
              special_day_type TEXT NOT NULL,
              special_day_name TEXT NOT NULL,
              special_day_group TEXT NOT NULL,
              bridge_anchor TEXT NOT NULL,
              special_day_delta REAL NOT NULL,
              sample_count REAL NOT NULL,
              shrinkage_factor REAL NOT NULL,
              PRIMARY KEY (target, utc_hour_start)
            );
            CREATE TABLE IF NOT EXISTS m3abcd_normalized_prices_m1b (
              utc_hour_start TEXT PRIMARY KEY,
              local_date TEXT NOT NULL,
              local_hour INTEGER NOT NULL,
              m1b_normal_price_se1 REAL NOT NULL,
              m1b_normal_price_area_diff REAL NOT NULL,
              m3a_temperature_delta_se1 REAL NOT NULL,
              m3a_temperature_delta_area_diff REAL NOT NULL,
              m3b_special_day_delta_se1 REAL NOT NULL,
              m3b_special_day_delta_area_diff REAL NOT NULL,
              m3ab_normalized_price_se1 REAL NOT NULL,
              m3ab_normalized_area_diff REAL NOT NULL,
              m3ab_normalized_se3 REAL NOT NULL
            );
            """
        )
        for table in (
            "m1b_holiday_clean_normal_price",
            "m1b_training_row_policy",
            "m3a_temperature_delta_m1b",
            "m3b_special_day_delta_m1b",
            "m3abcd_normalized_prices_m1b",
        ):
            conn.execute(f"DELETE FROM {table}")
        scoped = [row for row in rows if row["split"] in {"train", "validate", "holdout"}]
        conn.executemany(
            "INSERT INTO m1b_holiday_clean_normal_price VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    row["utc_hour_start"],
                    row["local_date"],
                    row["local_hour"],
                    row["m1b_se1"],
                    row["m1b_area"],
                    row["m1b_se1"] + row["m1b_area"],
                )
                for row in scoped
            ],
        )
        conn.executemany(
            "INSERT INTO m1b_training_row_policy VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    row["utc_hour_start"],
                    row["local_date"],
                    row["local_hour"],
                    row["split"],
                    row["special_day_type"],
                    row["special_day_name"],
                    row["m1b_training_policy"],
                )
                for row in scoped
            ],
        )
        conn.executemany(
            "INSERT INTO m3a_temperature_delta_m1b VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    target,
                    row["utc_hour_start"],
                    row["local_date"],
                    row["local_hour"],
                    row[f"m1b_{M3_PRIMARY_ANOMALY_SIGNAL[target]}_anomaly"],
                    row[f"m1b_{M3_PRIMARY_ANOMALY_SIGNAL[target]}_bucket"],
                    row[f"m3a_m1b_{short}"],
                )
                for row in scoped
                for target, short in TARGET_FIELDS.items()
            ],
        )
        conn.executemany(
            "INSERT INTO m3b_special_day_delta_m1b VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    target,
                    row["utc_hour_start"],
                    row["local_date"],
                    row["local_hour"],
                    row["special_day_type"],
                    row["special_day_name"],
                    row["special_day_group"],
                    row["bridge_anchor"],
                    row[f"m3b_m1b_{short}"],
                    row[f"m3b_m1b_sample_count_{short}"],
                    row[f"m3b_m1b_shrinkage_{short}"],
                )
                for row in scoped
                for target, short in TARGET_FIELDS.items()
            ],
        )
        conn.executemany(
            "INSERT INTO m3abcd_normalized_prices_m1b VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    row["utc_hour_start"],
                    row["local_date"],
                    row["local_hour"],
                    row["m1b_se1"],
                    row["m1b_area"],
                    row["m3a_m1b_se1"],
                    row["m3a_m1b_area"],
                    row["m3b_m1b_se1"],
                    row["m3b_m1b_area"],
                    row["m3ab_m1b_normalized_se1"],
                    row["m3ab_m1b_normalized_area"],
                    row["m3ab_m1b_normalized_se3"],
                )
                for row in scoped
            ],
        )


def write_p0039_evidence(evidence_dir: Path, rows: list[dict[str, object]], matrix: list[dict[str, object]]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}
    paths["CHANGELOG"] = write(evidence_dir / "CHANGELOG.md", changelog())
    paths["taxonomy"] = write(evidence_dir / "taxonomy.md", taxonomy_report())
    paths["policy"] = write(evidence_dir / "m1b-training-row-policy.md", row_policy_report(rows))
    paths["m1b"] = write(evidence_dir / "m1b-baseline-summary.md", m1b_baseline_report(rows, matrix))
    paths["m3a"] = write(evidence_dir / "m3a-temperature-m1b-summary.md", m3a_report(rows))
    paths["m3b"] = write(evidence_dir / "m3b-special-day-m1b-summary.md", m3b_report(rows))
    paths["contract"] = write(evidence_dir / "sequential-residual-contract.md", residual_contract_report())
    paths["holdout"] = write(evidence_dir / "full-year-holdout-results.md", matrix_markdown(matrix))
    paths["summary"] = write(evidence_dir / "component-attribution-summary.md", summary_report(rows, matrix))
    (evidence_dir / "component-attribution-matrix.json").write_text(json.dumps(matrix, indent=2, sort_keys=True), encoding="utf-8")
    paths["matrix_json"] = str(evidence_dir / "component-attribution-matrix.json")
    return paths


def changelog() -> str:
    return "\n".join(
        [
            "# P0039 changelog",
            "",
            "- Added holiday-clean M1B diagnostics and strict train-only M1B-trained M3A/M3B chain.",
            "- Corrected P0039 follow-up: M1B is a training/normalization base only; holdout chains apply M1B-trained deltas on the M1 baseplate.",
            "- Added P0039 taxonomy and sequential residual evidence.",
            "- Added local feature DB output tables with M1B-suffixed names.",
            "- Deferred M3C_m1b, M3D_m1b and M4_m1b implementation to future packages; P0039 documents their target contract.",
            "- No M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.",
            "",
        ]
    )


def taxonomy_report() -> str:
    return "\n".join(
        [
            "# P0039 taxonomy",
            "",
            "| Symbol | Domain | Existing name | Normal model | Delta model |",
            "|---|---|---|---|---|",
            "| A | temperature | M3A | M2A climate normal | M3A temperature delta |",
            "| B | special days | M3B | no M2B required | M3B special-day delta |",
            "| C | solar | M3C | M2C solar generation potential normal | M3C solar delta |",
            "| D | wind | M3D | M2D wind generation potential normal | M3D wind delta |",
            "",
            "No required M2B exists because special days are deterministic calendar features, not weather-normalized signals.",
            "",
        ]
    )


def row_policy_report(rows: list[dict[str, object]]) -> str:
    by_split: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    by_type: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in rows:
        policy = str(row["m1b_training_policy"])
        by_split[str(row["split"])][policy] += 1
        by_type[str(row["special_day_type"])][policy] += 1
    lines = [
        "# P0039 M1B training row policy",
        "",
        "Policy: exclude all rows whose `special_day_type` is not `normal_weekday`, `normal_saturday`, or `normal_sunday`, and exclude any row flagged `is_special_day`.",
        "",
        "Midsummer Day is excluded because the Swedish calendar classifies it as `major_social_holiday`.",
        "",
        "| split | included | excluded |",
        "|---|---:|---:|",
    ]
    for split in ("train", "validate", "holdout"):
        lines.append(f"| {split} | {by_split[split].get('include', 0)} | {by_split[split].get('exclude_special_contaminated', 0)} |")
    lines.extend(["", "| special_day_type | included | excluded |", "|---|---:|---:|"])
    for day_type in sorted(by_type):
        lines.append(f"| {day_type} | {by_type[day_type].get('include', 0)} | {by_type[day_type].get('exclude_special_contaminated', 0)} |")
    return "\n".join(lines) + "\n"


def m1b_baseline_report(rows: list[dict[str, object]], matrix: list[dict[str, object]]) -> str:
    clean_train = [row for row in rows if row["split"] == "train" and is_m1b_clean_training_row(row)]
    all_train = [row for row in rows if row["split"] == "train"]
    lines = [
        "# P0039 M1B baseline summary",
        "",
        f"train_rows_total = {len(all_train)}",
        f"train_rows_included_for_M1B = {len(clean_train)}",
        f"train_rows_excluded_for_M1B = {len(all_train) - len(clean_train)}",
        "",
        "M1B uses the same week/weekday/hour robust median surface style as M1, fitted only on holiday-clean train rows.",
        "",
        matrix_markdown([row for row in matrix if row["variant"] in {"M1", "M1B"}]),
    ]
    return "\n".join(lines)


def m3a_report(rows: list[dict[str, object]]) -> str:
    holdout = [row for row in rows if row["split"] == "holdout"]
    lines = ["# P0039 M3A M1B temperature summary", "", "| target | bucket | rows | delta_median | avg_model_delta |", "|---|---|---:|---:|---:|"]
    for target, short in TARGET_FIELDS.items():
        signal = M3_PRIMARY_ANOMALY_SIGNAL[target]
        for bucket in ("extreme_cold", "cold", "normal", "warm", "extreme_warm"):
            subset = [row for row in holdout if row[f"m1b_{signal}_bucket"] == bucket]
            if not subset:
                lines.append(f"| {target} | {bucket} | 0 |  |  |")
                continue
            residuals = [float(row[TARGETS[target]]) - float(row[f"m1b_{short}"]) for row in subset]
            deltas = [float(row[f"m3a_m1b_{short}"]) for row in subset]
            lines.append(f"| {target} | {bucket} | {len(subset)} | {fmt(median(residuals))} | {fmt(sum(deltas) / len(deltas))} |")
    lines.extend(["", "M3A_m1b target formula: `actual - M1B`, fitted on holiday-clean train rows only.", ""])
    return "\n".join(lines)


def m3b_report(rows: list[dict[str, object]]) -> str:
    holdout = [row for row in rows if row["split"] == "holdout"]
    lines = ["# P0039 M3B M1B special-day summary", "", "| subset | rows | M1+M3A_m1b MAE | M1+M3A_m1b+M3B_m1b MAE | delta |", "|---|---:|---:|---:|---:|"]
    for name, subset in (
        ("special_day_hours", [row for row in holdout if row["is_special_day"]]),
        ("non_special_day_hours", [row for row in holdout if not row["is_special_day"]]),
        ("holiday_weekday_hours", [row for row in holdout if row["is_special_day"] and int(row["weekday"]) < 5]),
    ):
        if not subset:
            lines.append(f"| {name} | 0 |  |  |  |")
            continue
        actual, before = series_for_p0039_variant(subset, "M1_M3A_m1b", "recomposed_se3")
        _actual, after = series_for_p0039_variant(subset, "M1_M3A_m1b_M3B_m1b", "recomposed_se3")
        b = mae(actual, before)
        a = mae(actual, after)
        lines.append(f"| {name} | {len(subset)} | {fmt(b)} | {fmt(a)} | {fmt(a - b)} |")
    lines.extend(["", "M3B_m1b target formula: `actual - M1B - M3A_m1b`, fitted on train special-day rows only.", ""])
    return "\n".join(lines)


def residual_contract_report() -> str:
    return "\n".join(
        [
            "# P0039 sequential residual contract",
            "",
            "```text",
            "M1B = holiday-clean baseline",
            "M3A target = actual - M1B",
            "M3B target = actual - M1B - M3A",
            "M3C target = actual - M1B - M3A - M3B",
            "M3D target = actual - M1B - M3A - M3B - M3C",
            "M4 target = actual - M1B - M3A - M3B - M3C - M3D",
            "```",
            "",
            "P0039 implements M1B, M3A_m1b and M3B_m1b. M1B is a training/normalization base; prediction chains keep M1 as the baseplate and apply M1B-trained deltas on top. M3C_m1b, M3D_m1b and M4_m1b are documented contracts for future packages and are not promoted here.",
            "",
        ]
    )


def matrix_markdown(matrix: list[dict[str, object]]) -> str:
    lines = ["# P0039 full-year holdout results", "", "| holdout_year | variant | target | MAE | RMSE | signed_error | MAE_delta_vs_M1 | MAE_delta_vs_previous_variant |", "|---:|---|---|---:|---:|---:|---:|---:|"]
    for row in matrix:
        lines.append(f"| {row['holdout_year']} | {row['variant']} | {row['target']} | {fmt(row['MAE'])} | {fmt(row['RMSE'])} | {fmt(row['signed_error'])} | {fmt(row['MAE_delta_vs_M1'])} | {fmt(row['MAE_delta_vs_previous_variant'])} |")
    return "\n".join(lines) + "\n"


def summary_report(rows: list[dict[str, object]], matrix: list[dict[str, object]]) -> str:
    m1 = _mae(matrix, "M1", "recomposed_se3")
    m1b = _mae(matrix, "M1B_training_base_only", "recomposed_se3")
    existing = _mae(matrix, "M1_existing_M3A_M3B", "recomposed_se3")
    m1b_m3a = _mae(matrix, "M1_M3A_m1b", "recomposed_se3")
    m1b_m3b = _mae(matrix, "M1_M3A_m1b_M3B_m1b", "recomposed_se3")
    clean_train = len([row for row in rows if row["split"] == "train" and is_m1b_clean_training_row(row)])
    all_train = len([row for row in rows if row["split"] == "train"])
    recommendation = "M1 remains the baseplate; M1B-trained deltas are promising enough for downstream experiments" if m1b_m3b <= existing else "M1 remains the baseplate; do not replace existing deltas until the M1B-trained chain beats the current chain"
    return "\n".join(
        [
            "# P0039 component attribution summary",
            "",
            f"Status: {'PASS' if m1b_m3b < existing else 'WARN'}",
            "",
            "## Required Answers",
            "",
            f"1. M1B improves training cleanliness versus M1 by excluding {all_train - clean_train} of {all_train} train rows from baseline fitting.",
            f"2. M1B as a standalone prediction base is diagnostic-only and {'improves' if m1b < m1 else 'worsens or does not improve'} full-year holdout recomposed SE3 MAE: M1={fmt(m1)}, M1B_training_base_only={fmt(m1b)}.",
            f"3. M3A trained on holiday-clean data and applied on M1 changes recomposed SE3 MAE from M1={fmt(m1)} to M1+M3A_m1b={fmt(m1b_m3a)}.",
            f"4. M3B trained after M3A and applied on M1 changes recomposed SE3 MAE from M1+M3A_m1b={fmt(m1b_m3a)} to M1+M3A_m1b+M3B_m1b={fmt(m1b_m3b)}.",
            f"5. M1 baseplate plus M1B-trained deltas {'beats' if m1b_m3b < existing else 'does not beat'} previous M1-based chain: corrected chain={fmt(m1b_m3b)}, existing chain={fmt(existing)}.",
            f"6. Recommendation: {recommendation}.",
            "",
            "## Local Diagnostic Tables",
            "",
            "`m1b_holiday_clean_normal_price`, `m1b_training_row_policy`, and `m3abcd_normalized_prices_m1b` are written for train/validate/holdout rows.",
            "`m3a_temperature_delta_m1b` and `m3b_special_day_delta_m1b` are written per target and train/validate/holdout hour.",
            "`m3c_solar_delta_m1b`, `m3d_wind_delta_m1b`, and M4_m1b outputs are deferred; their sequential target formulas are in `sequential-residual-contract.md`.",
            "",
            "No M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.",
            "",
        ]
    )


def _mae(matrix: list[dict[str, object]], variant: str, target: str) -> float:
    return float(next(row["MAE"] for row in matrix if row["variant"] == variant and row["target"] == target))


def write(path: Path, text: str) -> str:
    path.write_text(text, encoding="utf-8")
    return str(path)


def main() -> int:
    result = run_p0039_analysis()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
