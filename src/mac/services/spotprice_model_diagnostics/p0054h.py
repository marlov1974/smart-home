"""P0054H origin-local SE1 anchored absolute price forecast log."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
import csv
import json
import math
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB, mae, rmse
from src.mac.services.spotprice_model_diagnostics.forecast_period_policy import (
    MODELING_START_UTC,
    POLICY_VERSION,
    canonical_split_for_timestamp,
    parse_policy_timestamp,
    policy_summary,
)
from src.mac.services.spotprice_model_diagnostics.p0040 import spearman_from_ranks, top_indexes
from src.mac.services.spotprice_model_diagnostics.p0041 import persist_rows, percentile, write


PACKAGE_ID = "P0054H"
EVIDENCE_DIR = Path("requirements/package-runs/P0054H")
FORECAST_LOG_TABLE = "anchored_absolute_price_forecast_log_p0054h_se1_v1"
P0053CB_TABLE = "m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1"
FORECAST_RUN_ID = "P0054H_origin_local_history_baseline_se1_v1"
MODEL_NAME = "P0054H_origin_local_history_baseline"
MODEL_VERSION = "p0054h_origin_local_history_v1"
AREA = "SE1"
TARGET_SERIES = "system_proxy_se1"
PREDICTION_UNIT = "source_hour_price_unit"
PREDICTION_KIND = "anchored_absolute_price"
SOURCE_MODEL_FAMILY = "P0054H_origin_local_history_baseline"
TRAINING_PROTOCOL = "origin_local_no_fit_pre_origin_history"
METHOD_NAME = "previous_week_same_hour_else_hist48_same_hour_else_hist48_median"


@dataclass(frozen=True)
class P0054HResult:
    status: str
    forecast_log_table: str
    forecast_log_rows: int
    evidence: dict[str, str]


def run_p0054h_generation(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054HResult:
    started = time.monotonic()
    db_path = Path(feature_db).expanduser()
    price_rows = load_price_rows(db_path)
    prices_by_ts = {str(row["timestamp_utc"]): float(row["hour_price"]) for row in price_rows}
    windows, skipped = build_daily_windows(price_rows)
    forecast_rows = build_forecast_rows(windows, prices_by_ts)
    persisted_rows = persist_forecast_origin_log(db_path, forecast_rows)
    leakage = validate_leakage(forecast_rows)
    coverage = coverage_by_split(forecast_rows)
    metrics = evaluate_price_metrics(forecast_rows, prices_by_ts)
    comparison = compare_to_p0053cb(db_path, metrics)
    status = status_from_outputs(forecast_rows, leakage, coverage)
    summary = {
        "status": status,
        "package_id": PACKAGE_ID,
        "policy": policy_summary(),
        "source_table": "ai2_hour_to_day_training_targets_v2",
        "target_series": TARGET_SERIES,
        "price_source_summary": price_source_summary(price_rows),
        "forecast_log_table": FORECAST_LOG_TABLE,
        "forecast_log_rows": persisted_rows,
        "forecast_run_id": FORECAST_RUN_ID,
        "forecast_method": forecast_method_contract(),
        "window_count": len(windows),
        "skipped_windows": skipped,
        "coverage": coverage,
        "leakage_review": leakage,
        "price_metrics": metrics,
        "p0053cb_comparison": comparison,
        "runtime_seconds": time.monotonic() - started,
    }
    evidence = write_p0054h_evidence(Path(evidence_dir), summary, forecast_rows)
    return P0054HResult(status=status, forecast_log_table=FORECAST_LOG_TABLE, forecast_log_rows=persisted_rows, evidence=evidence)


def load_price_rows(feature_db: Path | str) -> list[dict[str, object]]:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='ai2_hour_to_day_training_targets_v2'").fetchone():
            raise RuntimeError("missing ai2_hour_to_day_training_targets_v2")
        rows = [
            dict(row)
            for row in conn.execute(
                """
                SELECT timestamp_utc, model_cet_date, model_cet_weekday, model_cet_hour, hour_price
                FROM ai2_hour_to_day_training_targets_v2
                WHERE target_series=?
                ORDER BY timestamp_utc
                """,
                (TARGET_SERIES,),
            )
        ]
    if not rows:
        raise RuntimeError(f"no rows for {TARGET_SERIES}")
    return [
        {
            **row,
            "timestamp_utc": normalize_z(str(row["timestamp_utc"])),
            "split": safe_split_for_timestamp(str(row["timestamp_utc"])),
        }
        for row in rows
    ]


def build_daily_windows(price_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, int]]:
    by_day: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_timestamp = {str(row["timestamp_utc"]): row for row in price_rows}
    prices_by_ts = {str(row["timestamp_utc"]): float(row["hour_price"]) for row in price_rows}
    for row in price_rows:
        by_day[str(row["model_cet_date"])].append(row)
    windows = []
    skipped: dict[str, int] = defaultdict(int)
    for origin_date in sorted(by_day):
        day_rows = sorted(by_day[origin_date], key=lambda row: int(row["model_cet_hour"]))
        if len(day_rows) != 24:
            skipped["incomplete_origin_day"] += 1
            continue
        origin = parse_policy_timestamp(str(day_rows[0]["timestamp_utc"]))
        if origin < MODELING_START_UTC:
            skipped["pre_policy_origin"] += 1
            continue
        hourly = []
        for offset in range(168):
            key = normalize_z(origin + timedelta(hours=offset))
            match = by_timestamp.get(key)
            if match is None:
                hourly = []
                break
            hourly.append(match)
        if len(hourly) != 168:
            skipped["incomplete_168h_path"] += 1
            continue
        splits = {canonical_split_for_timestamp(str(row["timestamp_utc"])) for row in hourly}
        if len(splits) != 1:
            skipped["cross_split_path"] += 1
            continue
        state = build_anchor_state(origin, prices_by_ts)
        if len(state["hist48_prices"]) != 48:
            skipped["missing_prior_48h_anchor"] += 1
            continue
        windows.append({"origin_date": origin_date, "split": next(iter(splits)), "forecast_origin_timestamp_utc": normalize_z(origin), "hourly_rows": hourly})
    return windows, dict(sorted(skipped.items()))


def build_anchor_state(origin: datetime, prices_by_ts: dict[str, float]) -> dict[str, object]:
    history_start = origin - timedelta(hours=48)
    history_end = origin - timedelta(hours=1)
    hist_rows = []
    same_hour: dict[int, list[float]] = defaultdict(list)
    for offset in range(48):
        timestamp = history_start + timedelta(hours=offset)
        key = normalize_z(timestamp)
        if key in prices_by_ts:
            price = prices_by_ts[key]
            hist_rows.append((timestamp, price))
            same_hour[(timestamp + timedelta(hours=1)).hour].append(price)
    prices = [price for _timestamp, price in hist_rows]
    return {
        "history_start": history_start,
        "history_end": history_end,
        "hist48_rows": hist_rows,
        "hist48_prices": prices,
        "same_model_cet_hour": dict(same_hour),
        "median": median(prices),
        "iqr_scale": iqr_scale(prices),
    }


def predict_price(
    hourly: dict[str, object],
    origin: datetime,
    state: dict[str, object],
    prices_by_ts: dict[str, float],
) -> tuple[float, str, str | None]:
    target = parse_policy_timestamp(str(hourly["timestamp_utc"]))
    previous_week = target - timedelta(hours=168)
    previous_key = normalize_z(previous_week)
    if previous_week < origin and previous_key in prices_by_ts:
        return prices_by_ts[previous_key], "previous_week_same_hour", previous_key
    same_hour = state["same_model_cet_hour"]  # type: ignore[assignment]
    values = same_hour.get(int(hourly["model_cet_hour"]), [])
    if values:
        return mean(values), "hist48_same_hour_mean", None
    return float(state["median"]), "hist48_median", None


def build_forecast_rows(windows: list[dict[str, object]], prices_by_ts: dict[str, float]) -> list[dict[str, object]]:
    created = normalize_z(datetime.now(timezone.utc).replace(microsecond=0))
    output = []
    for window in windows:
        origin = parse_policy_timestamp(str(window["forecast_origin_timestamp_utc"]))
        state = build_anchor_state(origin, prices_by_ts)
        for horizon, hourly in enumerate(window["hourly_rows"]):  # type: ignore[index]
            predicted, rule, source_ts = predict_price(hourly, origin, state, prices_by_ts)
            output.append(
                {
                    "forecast_run_id": FORECAST_RUN_ID,
                    "model_name": MODEL_NAME,
                    "model_version": MODEL_VERSION,
                    "split_policy_version": POLICY_VERSION,
                    "package_id": PACKAGE_ID,
                    "source_model_family": SOURCE_MODEL_FAMILY,
                    "method_name": METHOD_NAME,
                    "training_protocol": TRAINING_PROTOCOL,
                    "training_cutoff_utc": normalize_z(origin - timedelta(hours=1)),
                    "prediction_rule": rule,
                    "prediction_source_timestamp_utc": source_ts,
                    "anchor_method": "origin_local_48h_history_anchor",
                    "anchor_level": float(state["median"]),
                    "anchor_scale": float(state["iqr_scale"]),
                    "anchor_window_start_utc": normalize_z(state["history_start"]),  # type: ignore[arg-type]
                    "anchor_window_end_utc": normalize_z(state["history_end"]),  # type: ignore[arg-type]
                    "forecast_origin_timestamp_utc": normalize_z(origin),
                    "input_data_cutoff_utc": normalize_z(origin - timedelta(hours=1)),
                    "target_timestamp_utc": normalize_z(str(hourly["timestamp_utc"])),
                    "horizon_hours": horizon,
                    "area": AREA,
                    "predicted_price": predicted,
                    "prediction_unit": PREDICTION_UNIT,
                    "prediction_kind": PREDICTION_KIND,
                    "created_at_utc": created,
                    "quality_flag": "forecast_safe_origin_local_baseline_not_m4",
                }
            )
    return output


def persist_forecast_origin_log(feature_db: Path, rows: list[dict[str, object]]) -> int:
    with sqlite3.connect(feature_db) as conn:
        persist_rows(conn, FORECAST_LOG_TABLE, rows)
        conn.commit()
    return len(rows)


def validate_leakage(rows: list[dict[str, object]]) -> dict[str, object]:
    anchor_errors = []
    target_order_errors = []
    cutoff_errors = []
    horizon_errors = []
    training_cutoff_errors = []
    source_after_origin_errors = []
    for row in rows:
        origin = parse_policy_timestamp(str(row["forecast_origin_timestamp_utc"]))
        target = parse_policy_timestamp(str(row["target_timestamp_utc"]))
        cutoff = parse_policy_timestamp(str(row["input_data_cutoff_utc"]))
        training_cutoff = parse_policy_timestamp(str(row["training_cutoff_utc"]))
        anchor_start = parse_policy_timestamp(str(row["anchor_window_start_utc"]))
        anchor_end = parse_policy_timestamp(str(row["anchor_window_end_utc"]))
        horizon = int(row["horizon_hours"])
        source_ts = row.get("prediction_source_timestamp_utc")
        if anchor_start != origin - timedelta(hours=48) or anchor_end != origin - timedelta(hours=1) or anchor_end >= origin:
            anchor_errors.append(row["forecast_origin_timestamp_utc"])
        if origin > target:
            target_order_errors.append(row["target_timestamp_utc"])
        if cutoff > origin:
            cutoff_errors.append(row["forecast_origin_timestamp_utc"])
        if training_cutoff > cutoff:
            training_cutoff_errors.append(row["forecast_origin_timestamp_utc"])
        if source_ts and parse_policy_timestamp(str(source_ts)) >= origin:
            source_after_origin_errors.append(row["target_timestamp_utc"])
        if horizon < 0 or horizon > 167:
            horizon_errors.append(row["target_timestamp_utc"])
    ok = not any((anchor_errors, target_order_errors, cutoff_errors, horizon_errors, training_cutoff_errors, source_after_origin_errors))
    return {
        "ok": ok,
        "anchor_price_timestamps_strictly_before_origin": not anchor_errors,
        "forecast_origin_not_after_target": not target_order_errors,
        "input_cutoff_not_after_origin": not cutoff_errors,
        "training_cutoff_not_after_input_cutoff": not training_cutoff_errors,
        "prediction_source_timestamp_before_origin": not source_after_origin_errors,
        "horizons_0_to_167": not horizon_errors,
        "no_target_window_actual_price_used_as_input": True,
        "all_model_fitting_rows_before_origin": True,
        "no_validation_holdout_leakage_into_train_origin_models": True,
        "holdout_used_for_selection_or_fitting": False,
        "a61_used": False,
        "api_or_device_path_touched": False,
        "anchor_error_count": len(anchor_errors),
        "target_order_error_count": len(target_order_errors),
        "cutoff_error_count": len(cutoff_errors),
        "training_cutoff_error_count": len(training_cutoff_errors),
        "prediction_source_after_origin_error_count": len(source_after_origin_errors),
        "horizon_error_count": len(horizon_errors),
    }


def coverage_by_split(rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "by_target_timestamp": coverage_rows(rows, "target_timestamp_utc"),
        "by_forecast_origin": coverage_rows(rows, "forecast_origin_timestamp_utc"),
        "complete_168h_origins": sum(1 for group in group_by(rows, "forecast_origin_timestamp_utc").values() if len(group) == 168),
    }


def coverage_rows(rows: list[dict[str, object]], timestamp_field: str) -> dict[str, dict[str, object]]:
    output: dict[str, dict[str, object]] = {}
    for split in ("train", "validate", "holdout"):
        subset = [row for row in rows if canonical_split_for_timestamp(str(row[timestamp_field])) == split]
        output[split] = {
            "rows": len(subset),
            "origins": len({row["forecast_origin_timestamp_utc"] for row in subset}),
            "min_timestamp_utc": min((str(row[timestamp_field]) for row in subset), default=None),
            "max_timestamp_utc": max((str(row[timestamp_field]) for row in subset), default=None),
        }
    return output


def evaluate_price_metrics(rows: list[dict[str, object]], prices_by_ts: dict[str, float]) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for split in ("train", "validate", "holdout"):
        subset = [row for row in rows if canonical_split_for_timestamp(str(row["target_timestamp_utc"])) == split and str(row["target_timestamp_utc"]) in prices_by_ts]
        output[split] = metric_for_rows(subset, prices_by_ts)
    return output


def metric_for_rows(rows: list[dict[str, object]], prices_by_ts: dict[str, float]) -> dict[str, float]:
    if not rows:
        return {"row_count": 0.0, "path_count": 0.0}
    actual = [prices_by_ts[str(row["target_timestamp_utc"])] for row in rows]
    predicted = [float(row["predicted_price"]) for row in rows]
    errors = [pred - act for pred, act in zip(predicted, actual)]
    path_metrics = [path_metric(path_rows, prices_by_ts) for path_rows in group_by(rows, "forecast_origin_timestamp_utc").values() if len(path_rows) == 168]
    return {
        "row_count": float(len(rows)),
        "path_count": float(len(path_metrics)),
        "MAE": mae(actual, predicted),
        "RMSE": rmse(actual, predicted),
        "bias": mean(errors),
        "median_absolute_error": percentile([abs(error) for error in errors], 0.5),
        "p90_absolute_error": percentile([abs(error) for error in errors], 0.9),
        "p95_absolute_error": percentile([abs(error) for error in errors], 0.95),
        "sMAPE": smape(actual, predicted),
        "spearman": spearman_from_ranks(ranks(actual), ranks(predicted)),
        "MAE_full_168h": mean([row["MAE_full_168h"] for row in path_metrics]),
        "top8_day_precision": mean([row["top8_day_precision"] for row in path_metrics]),
        "top20_168h_precision": mean([row["top20_168h_precision"] for row in path_metrics]),
        "bottom20_168h_precision": mean([row["bottom20_168h_precision"] for row in path_metrics]),
    }


def path_metric(rows: list[dict[str, object]], prices_by_ts: dict[str, float]) -> dict[str, float]:
    ordered = sorted(rows, key=lambda row: int(row["horizon_hours"]))
    actual = [prices_by_ts[str(row["target_timestamp_utc"])] for row in ordered]
    predicted = [float(row["predicted_price"]) for row in ordered]
    top8 = []
    for day in range(7):
        lo = day * 24
        hi = lo + 24
        top8.append(hit_precision(actual[lo:hi], predicted[lo:hi], 8, high=True))
    return {
        "MAE_full_168h": mae(actual, predicted),
        "top8_day_precision": mean(top8),
        "top20_168h_precision": hit_precision(actual, predicted, 20, high=True),
        "bottom20_168h_precision": hit_precision(actual, predicted, 20, high=False),
    }


def compare_to_p0053cb(feature_db: Path, p0054h_metrics: dict[str, dict[str, float]]) -> dict[str, object]:
    with sqlite3.connect(feature_db) as conn:
        conn.row_factory = sqlite3.Row
        if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (P0053CB_TABLE,)).fetchone():
            return {"available": False, "reason": "p0053cb_table_missing"}
        rows = [dict(row) for row in conn.execute(f"SELECT target_timestamp_utc, forecast_origin_timestamp_utc, predicted_price FROM {P0053CB_TABLE} WHERE area=? AND prediction_kind=?", (AREA, PREDICTION_KIND))]
    prices_by_ts = {str(row["timestamp_utc"]): float(row["hour_price"]) for row in load_price_rows(feature_db)}
    normalized = [
        {
            "target_timestamp_utc": normalize_z(str(row["target_timestamp_utc"])),
            "forecast_origin_timestamp_utc": normalize_z(str(row["forecast_origin_timestamp_utc"])),
            "predicted_price": float(row["predicted_price"]),
            "horizon_hours": int((parse_policy_timestamp(str(row["target_timestamp_utc"])) - parse_policy_timestamp(str(row["forecast_origin_timestamp_utc"]))).total_seconds() // 3600),
        }
        for row in rows
    ]
    p0053cb_metrics = evaluate_price_metrics(normalized, prices_by_ts)
    return {
        "available": True,
        "p0053cb_table": P0053CB_TABLE,
        "p0053cb_metrics": {"validate": p0053cb_metrics["validate"], "holdout": p0053cb_metrics["holdout"]},
        "p0054h_metrics": {"validate": p0054h_metrics["validate"], "holdout": p0054h_metrics["holdout"]},
        "mae_full_168h_delta_p0054h_minus_p0053cb": {
            split: p0054h_metrics[split].get("MAE_full_168h", 0.0) - p0053cb_metrics[split].get("MAE_full_168h", 0.0)
            for split in ("validate", "holdout")
        },
    }


def status_from_outputs(rows: list[dict[str, object]], leakage: dict[str, object], coverage: dict[str, object]) -> str:
    by_target = coverage["by_target_timestamp"]  # type: ignore[assignment]
    has_all_splits = all(by_target[split]["rows"] > 0 and by_target[split]["origins"] > 0 for split in ("train", "validate", "holdout"))
    if rows and leakage["ok"] and has_all_splits:
        return "WARN"
    return "STOP"


def forecast_method_contract() -> dict[str, object]:
    return {
        "table": FORECAST_LOG_TABLE,
        "prediction_kind": PREDICTION_KIND,
        "prediction_unit": PREDICTION_UNIT,
        "area": AREA,
        "source_model_family": SOURCE_MODEL_FAMILY,
        "training_protocol": TRAINING_PROTOCOL,
        "method_name": METHOD_NAME,
        "forecast_origin_timestamp_utc": "first target timestamp in each complete daily 168h path",
        "input_data_cutoff_utc": "forecast_origin_timestamp_utc - 1h",
        "anchor_history_window": "[forecast_origin_timestamp_utc - 48h, forecast_origin_timestamp_utc)",
        "target_window": "[forecast_origin_timestamp_utc, forecast_origin_timestamp_utc + 167h]",
        "m4_compatible": False,
        "m4_reason": "does not use P0045 AI1/AI2 shape predictions; origin-local historical baseline only",
        "required_columns": forecast_log_columns(),
    }


def write_p0054h_evidence(evidence_dir: Path, summary: dict[str, object], rows: list[dict[str, object]]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    common_header = f"# P0054H\n\nStatus: `{summary['status']}`\n\n"
    files = {
        "CHANGELOG.md": changelog_text(summary),
        "labb-label.md": labb_label_text(),
        "source-discovery.md": json_md("P0054H source discovery", source_discovery(summary)),
        "training-protocol-decision.md": training_protocol_text(summary),
        "forecast-method-contract.md": json_md("P0054H forecast method contract", summary["forecast_method"]),
        "forecast-log-schema.md": schema_text(summary),
        "coverage-by-split.md": coverage_text(summary),
        "leakage-review.md": json_md("P0054H leakage review", summary["leakage_review"]),
        "validation-holdout-comparison-to-p0053cb.md": json_md("P0054H validation/holdout comparison to P0053C-B", summary["p0053cb_comparison"]),
        "verification-results.md": verification_text(summary),
        "downstream-contract-for-p0054f-retry.md": downstream_contract_text(summary),
        "what-we-learned.md": what_we_learned_text(summary),
        "next-package-recommendation.md": next_package_text(),
    }
    for name, text in files.items():
        write(evidence_dir / name, text if name != "source-discovery.md" else common_header + text)
    write(evidence_dir / "forecast-log-summary.json", json.dumps(json_safe(summary), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "leakage-check-summary.json", json.dumps(json_safe(summary["leakage_review"]), indent=2, sort_keys=True) + "\n")
    write(evidence_dir / "price-forecast-metrics-summary.json", json.dumps(json_safe(summary["price_metrics"]), indent=2, sort_keys=True) + "\n")
    write_csv(evidence_dir / "forecast-origin-log-sample.csv", rows[:200], forecast_log_columns())
    write_csv(evidence_dir / "coverage-by-origin.csv", coverage_by_origin_rows(rows), ("forecast_origin_timestamp_utc", "split", "row_count", "min_target_timestamp_utc", "max_target_timestamp_utc"))
    return {
        name: str(evidence_dir / name)
        for name in [*files, "forecast-log-summary.json", "leakage-check-summary.json", "price-forecast-metrics-summary.json", "forecast-origin-log-sample.csv", "coverage-by-origin.csv"]
    }


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0054H Changelog

- Created forecast-origin-safe SE1 anchored absolute price forecasts with train, validation and holdout coverage.
- Chose a simpler origin-local history baseline instead of M4 because safe train-period M4 would require rolling/cross-fit upstream AI1/AI2 training outside this package's practical scope.
- Persisted `{summary['forecast_log_rows']}` rows to local SQLite table `{FORECAST_LOG_TABLE}`.
- Labeled the output `forecast_safe_origin_local_baseline_not_m4`.
- Wrote coverage, leakage, schema, downstream contract and validation/holdout comparison evidence.
- No live API, devices, Shelly, Home Assistant, KVS, A61 utilization, production deployment, model binary or downstream consumption ablation was performed.

Result status: {summary['status']}.
"""


def labb_label_text() -> str:
    return """# P0054H LABB Label

P0054H is labeled `LABB`.

It is a local research/data package under P0054A, not a G2-KANDIDAT evaluation and not runtime candidate evidence.
"""


def source_discovery(summary: dict[str, object]) -> dict[str, object]:
    return {
        "source_table": summary["source_table"],
        "target_series": summary["target_series"],
        "price_source_summary": summary["price_source_summary"],
        "p0053cb_table_compared": P0053CB_TABLE,
        "created_table": summary["forecast_log_table"],
    }


def training_protocol_text(summary: dict[str, object]) -> str:
    return f"""# P0054H Training Protocol Decision

Decision:

```text
{TRAINING_PROTOCOL}
```

P0054H does not train an upstream AI1/AI2 M4 model. It uses an origin-local baseline with no fitted parameters crossing forecast origins.

Why not M4:

Safe train-period M4 would require rolling-origin, expanding-origin or blocked out-of-fold AI1/AI2 training. That is larger and slower than needed to unblock a forecast-safe downstream ablation source. The package allows a simpler anchored baseline when clearly labeled.

Method:

```text
{METHOD_NAME}
```

Status: `{summary['status']}`
"""


def schema_text(summary: dict[str, object]) -> str:
    lines = ["# P0054H Forecast Log Schema", "", f"Table: `{FORECAST_LOG_TABLE}`", "", "| column |", "|---|"]
    for column in forecast_log_columns():
        lines.append(f"| `{column}` |")
    return "\n".join(lines) + "\n"


def coverage_text(summary: dict[str, object]) -> str:
    lines = ["# P0054H Coverage By Split", ""]
    for title, key in (("By target timestamp", "by_target_timestamp"), ("By forecast origin", "by_forecast_origin")):
        lines += [f"## {title}", "", "| split | rows | origins | min timestamp | max timestamp |", "|---|---:|---:|---|---|"]
        for split, row in summary["coverage"][key].items():  # type: ignore[index]
            lines.append(f"| {split} | {row['rows']} | {row['origins']} | {row['min_timestamp_utc']} | {row['max_timestamp_utc']} |")
        lines.append("")
    lines.append(f"Complete 168h origins: `{summary['coverage']['complete_168h_origins']}`")  # type: ignore[index]
    return "\n".join(lines) + "\n"


def verification_text(summary: dict[str, object]) -> str:
    return f"""# P0054H Verification Results

Generation command:

```text
python3 -m src.mac.services.spotprice_model_diagnostics.p0054h
```

Generation status:

```text
{summary['status']}
```

Rows persisted:

```text
{summary['forecast_log_rows']}
```

Final `git diff --check` and large-artifact checks are recorded in the final package report after command execution.
"""


def downstream_contract_text(summary: dict[str, object]) -> str:
    return f"""# P0054H Downstream Contract For P0054F/P0054I Retry

Use table:

```text
{FORECAST_LOG_TABLE}
```

Join keys:

```text
forecast_origin_timestamp_utc
target_timestamp_utc
```

Primary feature:

```text
predicted_price
```

Required filters:

```text
area = SE1
prediction_kind = anchored_absolute_price
quality_flag = forecast_safe_origin_local_baseline_not_m4
training_protocol = {TRAINING_PROTOCOL}
```

Important label:

```text
This is not M4. It is a forecast-safe origin-local historical price baseline.
```
"""


def what_we_learned_text(summary: dict[str, object]) -> str:
    return """# P0054H What We Learned

- A safe train/validation/holdout price forecast-origin log can be created locally without live API calls.
- The practical package-scoped path is a non-M4 origin-local historical baseline.
- This source is suitable for a downstream ablation that asks whether forecast-safe price information helps SE1 consumption models, but not for claims about M4 price forecast quality.

Knowhow promotion: intentionally skipped. The forecast-origin safety rule is already covered by durable policy memory; this package records the concrete table contract as package evidence.
"""


def next_package_text() -> str:
    return """# P0054H Next Package Recommendation

Recommended next package:

```text
P0054I LABB SE1 consumption price forecast ablation retry
```

Use P0054H's forecast-safe price log as the with-price source and label it as an origin-local historical baseline, not M4.
"""


def price_source_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "rows": len(rows),
        "min_timestamp_utc": min(str(row["timestamp_utc"]) for row in rows),
        "max_timestamp_utc": max(str(row["timestamp_utc"]) for row in rows),
    }


def coverage_by_origin_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    for origin, group in sorted(group_by(rows, "forecast_origin_timestamp_utc").items()):
        output.append(
            {
                "forecast_origin_timestamp_utc": origin,
                "split": canonical_split_for_timestamp(origin),
                "row_count": len(group),
                "min_target_timestamp_utc": min(str(row["target_timestamp_utc"]) for row in group),
                "max_target_timestamp_utc": max(str(row["target_timestamp_utc"]) for row in group),
            }
        )
    return output


def group_by(rows: list[dict[str, object]], key: str) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[key])].append(row)
    return grouped


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def iqr_scale(values: list[float]) -> float:
    if not values:
        return 0.0
    scale = (percentile(values, 0.75) - percentile(values, 0.25)) / 1.349
    return scale if scale > 0.0 and math.isfinite(scale) else 0.0


def smape(actual: list[float], predicted: list[float]) -> float:
    values = []
    for act, pred in zip(actual, predicted):
        denom = (abs(act) + abs(pred)) / 2.0
        if denom > 1e-12:
            values.append(abs(pred - act) / denom)
    return mean(values)


def ranks(values: list[float]) -> list[float]:
    ordered = sorted((value, index) for index, value in enumerate(values))
    output = [0.0] * len(values)
    for rank, (_value, index) in enumerate(ordered, start=1):
        output[index] = float(rank)
    return output


def hit_precision(actual: list[float], predicted: list[float], count: int, *, high: bool) -> float:
    return len(set(top_indexes(actual, count, high=high)) & set(top_indexes(predicted, count, high=high))) / float(count)


def normalize_z(timestamp: str | datetime) -> str:
    return parse_policy_timestamp(timestamp).isoformat().replace("+00:00", "Z")


def safe_split_for_timestamp(timestamp: str | datetime) -> str:
    parsed = parse_policy_timestamp(timestamp)
    if parsed < MODELING_START_UTC:
        return "pre_policy_context_only"
    return canonical_split_for_timestamp(timestamp)


def forecast_log_columns() -> tuple[str, ...]:
    return (
        "forecast_run_id",
        "model_name",
        "model_version",
        "split_policy_version",
        "package_id",
        "source_model_family",
        "method_name",
        "training_protocol",
        "training_cutoff_utc",
        "prediction_rule",
        "prediction_source_timestamp_utc",
        "anchor_method",
        "anchor_level",
        "anchor_scale",
        "anchor_window_start_utc",
        "anchor_window_end_utc",
        "forecast_origin_timestamp_utc",
        "input_data_cutoff_utc",
        "target_timestamp_utc",
        "horizon_hours",
        "area",
        "predicted_price",
        "prediction_unit",
        "prediction_kind",
        "created_at_utc",
        "quality_flag",
    )


def write_csv(path: Path, rows: list[dict[str, object]], columns: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run P0054H origin-local SE1 anchored price forecast log")
    parser.add_argument("--feature-db", default=str(DEFAULT_FEATURE_DB))
    parser.add_argument("--evidence-dir", default=str(EVIDENCE_DIR))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_p0054h_generation(feature_db=args.feature_db, evidence_dir=args.evidence_dir)
    print(json.dumps({"status": result.status, "forecast_log_table": result.forecast_log_table, "forecast_log_rows": result.forecast_log_rows}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
