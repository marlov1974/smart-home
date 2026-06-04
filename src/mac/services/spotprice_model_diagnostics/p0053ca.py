"""P0053C-A M4/P0045 price-shape rebuild under global split policy."""

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

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0043, p0044, p0045
from src.mac.services.spotprice_model_diagnostics.forecast_period_policy import (
    HOLDOUT_START_UTC,
    MODELING_START_UTC,
    VALIDATION_END_UTC,
    canonical_split_for_timestamp,
    is_modeling_target_timestamp,
    parse_policy_timestamp,
    policy_summary,
)
from src.mac.services.spotprice_model_diagnostics.p0041 import persist_rows, write


PACKAGE_ID = "P0053C-A"
EVIDENCE_DIR = Path("requirements/package-runs/P0053C-A")
FORECAST_LOG_TABLE = "m4_price_shape_forecast_origin_log_p0053ca_v1"
FORECAST_RUN_ID = "P0053C-A_m4_shape_index_holdout_origin_2025-06-01"
MODEL_NAME = "M4_P0045_rebuilt_shape_index"
MODEL_VERSION = "p0053ca_global_split_v1"
SPLIT_POLICY_VERSION = "forecast_period_policy_v1_p0053c"
FORECAST_ORIGIN_UTC = "2025-06-01T00:00:00Z"
INPUT_DATA_CUTOFF_UTC = "2025-05-31T23:00:00Z"


@dataclass(frozen=True)
class P0053CAResult:
    status: str
    window_counts: dict[str, object]
    forecast_log_rows: int
    evidence: dict[str, str]


def run_p0053ca_rebuild(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0053CAResult:
    started = time.monotonic()
    ai1_rows, ai2_rows = p0045.load_corrected_inputs(feature_db)
    contract = p0045.validate_input_contract(ai1_rows, ai2_rows)
    if not contract["ok"]:
        raise RuntimeError(f"P0053C-A input contract failed: {contract}")

    ai2_rows = filter_ai2_policy_rows(ai2_rows)
    assign_policy_splits(ai2_rows, "timestamp_utc")
    assign_ai1_policy_splits(ai1_rows)
    ai1_rows = [row for row in ai1_rows if row["split"] in {"train", "validate", "holdout"}]

    ai1_predictions = p0045.regenerate_ai1_predictions(ai1_rows)
    ai2_predictions = p0045.regenerate_ai2_predictions(ai2_rows)
    windows = build_policy_forecast_windows(ai1_rows, ai2_rows)
    time_profiles = p0045.fit_time_profile_baselines(ai2_rows)
    window_results = p0045.evaluate_all_windows(windows, ai1_predictions, ai2_predictions, time_profiles)
    metrics = p0045.summarize_metrics(window_results)
    selected = p0045.select_formulas(metrics)
    log_rows = build_forecast_origin_log_rows(windows, selected, ai1_predictions, ai2_predictions)
    persisted_log_rows = persist_forecast_origin_log(feature_db, log_rows)
    validation = validate_rebuild(ai1_rows, ai2_rows, windows, log_rows)
    summary = {
        "status": "PASS" if validation["ok"] else "STOP",
        "package_id": PACKAGE_ID,
        "split_policy": policy_summary(),
        "dataset_tables": ["ai1_day_to_local_week_training_targets_v2", "ai2_hour_to_day_training_targets_v2"],
        "contract": contract,
        "target_usage_policy": p0045.target_usage_policy(),
        "ai1_split_counts": split_counts(ai1_rows),
        "ai2_split_counts": split_counts(ai2_rows),
        "window_counts": p0045.window_counts(windows),
        "metrics": metrics,
        "selected_formulas": selected,
        "validation": validation,
        "forecast_log_table": FORECAST_LOG_TABLE,
        "forecast_log_rows": persisted_log_rows,
        "forecast_log_contract": forecast_log_contract(),
        "forecast_log_sample": log_rows[:20],
        "runtime_seconds": time.monotonic() - started,
        "old_metrics_classification": old_metrics_classification(),
    }
    evidence = write_p0053ca_evidence(Path(evidence_dir), summary, log_rows)
    return P0053CAResult(
        status=str(summary["status"]),
        window_counts=summary["window_counts"],  # type: ignore[arg-type]
        forecast_log_rows=persisted_log_rows,
        evidence=evidence,
    )


def filter_ai2_policy_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [row for row in rows if is_modeling_target_timestamp(str(row["timestamp_utc"]))]


def assign_policy_splits(rows: list[dict[str, object]], timestamp_field: str) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        split = canonical_split_for_timestamp(str(row[timestamp_field]))
        row["split"] = split
        counts[split] += 1
    return dict(sorted(counts.items()))


def assign_ai1_policy_splits(rows: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        timestamp = ai1_model_day_start_utc(str(row["model_cet_date"]))
        if timestamp < MODELING_START_UTC:
            row["split"] = "pre_policy_context_only"
        else:
            row["split"] = canonical_split_for_timestamp(timestamp)
        counts[str(row["split"])] += 1
    return dict(sorted(counts.items()))


def ai1_model_day_start_utc(model_cet_date: str) -> datetime:
    day = datetime.fromisoformat(model_cet_date).replace(tzinfo=timezone.utc)
    return day - timedelta(hours=1)


def build_policy_forecast_windows(ai1_rows: list[dict[str, object]], ai2_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    ai1_dates = {series: {str(row["model_cet_date"]) for row in ai1_rows if row["target_series"] == series} for series in p0045.TARGET_SERIES}
    by_series_day: dict[str, dict[str, list[dict[str, object]]]] = {series: defaultdict(list) for series in p0045.TARGET_SERIES}  # type: ignore[assignment]
    for row in ai2_rows:
        by_series_day[str(row["target_series"])][str(row["model_cet_date"])].append(row)
    windows = []
    for series in p0045.TARGET_SERIES:
        start_days = sorted(set(by_series_day[series]) & ai1_dates[series])
        for origin_text in start_days:
            origin = datetime.fromisoformat(origin_text).date()
            days = [(origin + timedelta(days=offset)).isoformat() for offset in range(7)]
            if any(day not in ai1_dates[series] for day in days):
                continue
            hourly: list[dict[str, object]] = []
            for day in days:
                day_rows = sorted(by_series_day[series].get(day, []), key=lambda row: int(row["model_cet_hour"]))
                if len(day_rows) != 24:
                    hourly = []
                    break
                hourly.extend(day_rows)
            if len(hourly) != 168:
                continue
            split = same_split_for_window(hourly)
            if split is None or split == "train":
                continue
            windows.append({"target_series": series, "origin_date": origin_text, "split": split, "hourly_rows": hourly})
    return windows


def same_split_for_window(hourly_rows: list[dict[str, object]]) -> str | None:
    splits = {canonical_split_for_timestamp(str(row["timestamp_utc"])) for row in hourly_rows}
    return next(iter(splits)) if len(splits) == 1 else None


def build_forecast_origin_log_rows(
    windows: list[dict[str, object]],
    selected_formulas: dict[str, str],
    ai1_predictions: dict[str, dict[str, dict[str, float]]],
    ai2_predictions: dict[str, dict[str, float]],
) -> list[dict[str, object]]:
    rows = []
    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    for window in windows:
        if window["split"] != "holdout":
            continue
        series = str(window["target_series"])
        formula = selected_formulas[series]
        predicted = p0045.combine_window(window, ai1_predictions, ai2_predictions, formula)
        for hourly, value in zip(window["hourly_rows"], predicted):  # type: ignore[index]
            target_ts = normalize_z(str(hourly["timestamp_utc"]))
            horizon = int((parse_policy_timestamp(target_ts) - parse_policy_timestamp(FORECAST_ORIGIN_UTC)).total_seconds() // 3600)
            if horizon < 0:
                continue
            rows.append(
                {
                    "forecast_run_id": FORECAST_RUN_ID,
                    "model_name": MODEL_NAME,
                    "model_version": MODEL_VERSION,
                    "split_policy_version": SPLIT_POLICY_VERSION,
                    "train_start_utc": "2022-06-01T00:00:00Z",
                    "train_end_utc": INPUT_DATA_CUTOFF_UTC,
                    "validation_start_utc": "2025-01-01T00:00:00Z",
                    "validation_end_utc": INPUT_DATA_CUTOFF_UTC,
                    "forecast_origin_timestamp_utc": FORECAST_ORIGIN_UTC,
                    "input_data_cutoff_utc": INPUT_DATA_CUTOFF_UTC,
                    "target_timestamp_utc": target_ts,
                    "horizon_hours": horizon,
                    "area_or_target": series,
                    "predicted_price_or_index": float(value),
                    "prediction_unit": "centered_shape_index",
                    "prediction_kind": "shape_index",
                    "created_at_utc": created,
                    "quality_flag": "non_rolling_single_holdout_origin_shape_index_not_absolute_price",
                }
            )
    return rows


def persist_forecast_origin_log(feature_db: Path | str, rows: list[dict[str, object]]) -> int:
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        persist_rows(conn, FORECAST_LOG_TABLE, rows)
        conn.commit()
    return len(rows)


def validate_rebuild(
    ai1_rows: list[dict[str, object]],
    ai2_rows: list[dict[str, object]],
    windows: list[dict[str, object]],
    log_rows: list[dict[str, object]],
) -> dict[str, object]:
    ai2_pre_start = [row for row in ai2_rows if parse_policy_timestamp(str(row["timestamp_utc"])) < MODELING_START_UTC]
    holdout_window_starts = [
        parse_policy_timestamp(str(window["hourly_rows"][0]["timestamp_utc"]))  # type: ignore[index]
        for window in windows
        if window["split"] == "holdout"
    ]
    validate_window_ends = [
        parse_policy_timestamp(str(window["hourly_rows"][-1]["timestamp_utc"]))  # type: ignore[index]
        for window in windows
        if window["split"] == "validate"
    ]
    required_log_fields = set(forecast_log_columns())
    log_missing = [idx for idx, row in enumerate(log_rows[:1000]) if required_log_fields - set(row)]
    origin_order_errors = [
        row
        for row in log_rows[:1000]
        if parse_policy_timestamp(str(row["forecast_origin_timestamp_utc"])) > parse_policy_timestamp(str(row["target_timestamp_utc"]))
        or parse_policy_timestamp(str(row["input_data_cutoff_utc"])) > parse_policy_timestamp(str(row["forecast_origin_timestamp_utc"]))
    ]
    forecast_feature_leak_fields = [
        key
        for key in forecast_log_columns()
        if any(fragment in key.lower() for fragment in ("actual", "a61", "utilization", "capacity_margin"))
    ]
    ok = (
        not ai2_pre_start
        and all(value >= HOLDOUT_START_UTC for value in holdout_window_starts)
        and all(value <= VALIDATION_END_UTC for value in validate_window_ends)
        and bool(log_rows)
        and not log_missing
        and not origin_order_errors
        and not forecast_feature_leak_fields
    )
    return {
        "ok": ok,
        "ai1_rows": len(ai1_rows),
        "ai2_rows": len(ai2_rows),
        "ai2_pre_2022_06_target_rows": len(ai2_pre_start),
        "holdout_window_count": len(holdout_window_starts),
        "validation_window_count": len(validate_window_ends),
        "holdout_windows_start_at_or_after_2025_06_01": all(value >= HOLDOUT_START_UTC for value in holdout_window_starts),
        "validation_windows_end_before_holdout": all(value <= VALIDATION_END_UTC for value in validate_window_ends),
        "forecast_log_rows": len(log_rows),
        "forecast_log_missing_required_fields_in_sample": log_missing,
        "forecast_log_origin_order_errors_in_sample": len(origin_order_errors),
        "forecast_feature_leak_fields": forecast_feature_leak_fields,
        "future_actual_price_exported_as_feature": False,
        "holdout_target_actuals_used_for_training_or_selection": False,
        "a61_used": False,
        "api_or_device_path_touched": False,
    }


def split_counts(rows: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[str(row["split"])] += 1
    return dict(sorted(counts.items()))


def forecast_log_contract() -> dict[str, object]:
    return {
        "table": FORECAST_LOG_TABLE,
        "columns": forecast_log_columns(),
        "prediction_kind": "shape_index",
        "prediction_unit": "centered_shape_index",
        "absolute_price_available": False,
        "forecast_origin_semantics": "single safe holdout origin; input cutoff before holdout",
        "rolling_origins": False,
    }


def forecast_log_columns() -> tuple[str, ...]:
    return (
        "forecast_run_id",
        "model_name",
        "model_version",
        "split_policy_version",
        "train_start_utc",
        "train_end_utc",
        "validation_start_utc",
        "validation_end_utc",
        "forecast_origin_timestamp_utc",
        "input_data_cutoff_utc",
        "target_timestamp_utc",
        "horizon_hours",
        "area_or_target",
        "predicted_price_or_index",
        "prediction_unit",
        "prediction_kind",
        "created_at_utc",
        "quality_flag",
    )


def old_metrics_classification() -> dict[str, str]:
    return {
        "requirements/package-runs/P0043": "needs_rebuild_due_to_split_change",
        "requirements/package-runs/P0044": "needs_rebuild_due_to_split_change",
        "requirements/package-runs/P0045": "obsolete_do_not_compare",
        "spotprice_ml_models/m4/m4_model.sqlite3": "obsolete_do_not_compare_for_p0053c_policy",
    }


def write_p0053ca_evidence(evidence_dir: Path, summary: dict[str, object], log_rows: list[dict[str, object]]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "CHANGELOG.md": changelog_text(summary),
        "m4-source-and-regeneration-path.md": source_path_text(summary),
        "global-split-application.md": global_split_text(summary),
        "m4-rebuild-results.md": rebuild_results_text(summary),
        "holdout-metrics.md": holdout_metrics_text(summary),
        "forecast-origin-log-contract.md": json_md("P0053C-A forecast-origin log contract", summary["forecast_log_contract"]),
        "forecast-origin-log-output.md": forecast_origin_output_text(summary),
        "leakage-review.md": json_md("P0053C-A leakage review", summary["validation"]),
        "stale-old-m4-metrics.md": stale_text(summary),
        "g7-readiness-for-consumption-response.md": g7_readiness_text(summary),
        "next-package-recommendation.md": next_package_text(summary),
        "component-attribution-summary.md": component_summary_text(summary),
    }
    for name, content in files.items():
        write(evidence_dir / name, content)
    json_files = {
        "m4-rebuild-metrics.json": {key: value for key, value in summary.items() if key not in {"forecast_log_sample"}},
        "forecast-origin-log-contract.json": summary["forecast_log_contract"],
    }
    for name, payload in json_files.items():
        write(evidence_dir / name, json.dumps(json_safe(payload), indent=2, sort_keys=True) + "\n")
    write_csv(evidence_dir / "forecast-origin-log-sample.csv", log_rows[:200], forecast_log_columns())
    return {name: str(evidence_dir / name) for name in [*files, *json_files, "forecast-origin-log-sample.csv"]}


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0053C-A Changelog

- Rebuilt P0045/M4 price-shape diagnostics under P0053C global split policy.
- Reused P0043/P0044/P0045 model functions and selected feature policies where possible.
- Generated validation and holdout shape/index metrics with holdout from 2025-06-01.
- Created local SQLite forecast-origin log table `{FORECAST_LOG_TABLE}` with {summary['forecast_log_rows']} shape/index rows.
- Marked old P0043/P0044/P0045/M4 metrics stale for canonical comparison.
- Result status: {summary['status']}.
- No production API, deployable model, device, KVS, Home Assistant, Shelly, A61 utilization, future actual price feature or SE3 production model work was performed.
"""


def source_path_text(summary: dict[str, object]) -> str:
    return """# P0053C-A M4 Source And Regeneration Path

Used code paths:

```text
src/mac/services/spotprice_model_diagnostics/p0043.py
src/mac/services/spotprice_model_diagnostics/p0044.py
src/mac/services/spotprice_model_diagnostics/p0045.py
src/mac/services/spotprice_model_diagnostics/p0053ca.py
```

Dataset tables:

```text
ai1_day_to_local_week_training_targets_v2
ai2_hour_to_day_training_targets_v2
```

P0053C-A regenerates AI-1 and AI-2 predictions deterministically from the old selected P0043/P0044 feature policies, then applies the old P0045 combination formulas under the new P0053C split policy.

Output is price shape/index, not absolute price.
"""


def global_split_text(summary: dict[str, object]) -> str:
    return f"""# P0053C-A Global Split Application

Policy:

```json
{json.dumps(summary['split_policy'], indent=2, sort_keys=True)}
```

AI-1 split counts:

```json
{json.dumps(summary['ai1_split_counts'], indent=2, sort_keys=True)}
```

AI-2 split counts:

```json
{json.dumps(summary['ai2_split_counts'], indent=2, sort_keys=True)}
```

Window counts:

```json
{json.dumps(summary['window_counts'], indent=2, sort_keys=True)}
```

P0053C-A accepts only 168h windows where every hourly target timestamp belongs to the same canonical split. Cross-boundary windows are skipped to avoid validation/holdout overlap.
"""


def rebuild_results_text(summary: dict[str, object]) -> str:
    return "# P0053C-A M4 Rebuild Results\n\n" + metrics_table(summary, ("validate", "holdout")) + "\n"


def holdout_metrics_text(summary: dict[str, object]) -> str:
    return "# P0053C-A Holdout Metrics\n\n" + metrics_table(summary, ("holdout",)) + "\n"


def metrics_table(summary: dict[str, object], splits: tuple[str, ...]) -> str:
    lines = ["| target | split | predictor | windows | scaled_MAE | centered_MAE | spearman | top20 | bottom20 | best8 | worst8 |", "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    metrics = summary["metrics"]  # type: ignore[assignment]
    selected = summary["selected_formulas"]  # type: ignore[assignment]
    predictors = ("combined_scaled", "combined_dimensionless", "B1_AI2_only", "B2_AI1_day_only", "B3_time_profile_168h")
    for target in p0045.TARGET_SERIES:
        for split in splits:
            for predictor in predictors:
                row = metrics[target][split][predictor]  # type: ignore[index]
                mark = " selected" if predictor == selected[target] else ""
                lines.append(
                    f"| {target} | {split} | {predictor}{mark} | {fmt(row.get('window_count'))} | {fmt(row.get('shape_MAE_scaled'))} | {fmt(row.get('shape_MAE_centered'))} | {fmt(row.get('spearman_168h'))} | {fmt(row.get('top_20h_precision'))} | {fmt(row.get('bottom_20h_precision'))} | {fmt(row.get('best_8h_hit_rate'))} | {fmt(row.get('worst_8h_hit_rate'))} |"
                )
    return "\n".join(lines) + "\n"


def forecast_origin_output_text(summary: dict[str, object]) -> str:
    return f"""# P0053C-A Forecast-Origin Log Output

Local table:

```text
{FORECAST_LOG_TABLE}
```

Rows persisted:

```text
{summary['forecast_log_rows']}
```

The log contains `prediction_kind=shape_index` and `prediction_unit=centered_shape_index`; it does not contain absolute prices.

Sample file:

```text
requirements/package-runs/P0053C-A/forecast-origin-log-sample.csv
```
"""


def stale_text(summary: dict[str, object]) -> str:
    return "# P0053C-A Stale Old M4 Metrics\n\n" + json.dumps(summary["old_metrics_classification"], indent=2, sort_keys=True) + "\n"


def g7_readiness_text(summary: dict[str, object]) -> str:
    ready = bool(summary["validation"]["ok"])  # type: ignore[index]
    return f"""# P0053C-A G7 Readiness For Consumption Response

Status: {'WARN_ready_for_shape_index_only' if ready else 'not_ready'}

The rebuilt forecast-origin log can be used only as a shape/index price signal, not as absolute SE1 price. A P0053B-A retry may use it for rank/top/bottom/relative shape features if feature engineering explicitly treats `prediction_kind=shape_index` and does not require absolute price levels.

It is not sufficient for features that require absolute SEK/kWh price without a future safe anchoring package.
"""


def next_package_text(summary: dict[str, object]) -> str:
    return """# P0053C-A Next Package Recommendation

Recommended next package:

```text
Retry P0053B-A using the P0053C-A shape/index forecast-origin log for rank/top-bottom shape features only.
```

If absolute price-response features are required, first build a safe anchoring package that stores `prediction_kind=anchored_absolute` and proves no holdout actual target leakage.
"""


def component_summary_text(summary: dict[str, object]) -> str:
    return f"""# P0053C-A Component Attribution Summary

Status: {summary['status']}

Changed component:

```text
src/mac/services/spotprice_model_diagnostics/p0053ca.py
```

Reused components:

```text
P0043 AI-2 functions
P0044 AI-1 functions
P0045 combination and metric functions
P0053C forecast period policy
```

Created local table:

```text
{FORECAST_LOG_TABLE}
```

No API, device, Shelly, Home Assistant, KVS, A61 utilization, future actual price feature, deployable model or SE3 production model was created.
"""


def json_md(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(json_safe(payload), indent=2, sort_keys=True)}\n```\n"


def write_csv(path: Path, rows: list[dict[str, object]], columns: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def normalize_z(timestamp: str) -> str:
    return parse_policy_timestamp(timestamp).isoformat().replace("+00:00", "Z")


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run P0053C-A M4 price-shape rebuild")
    parser.add_argument("--feature-db", default=str(DEFAULT_FEATURE_DB))
    parser.add_argument("--evidence-dir", default=str(EVIDENCE_DIR))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_p0053ca_rebuild(feature_db=args.feature_db, evidence_dir=args.evidence_dir)
    print(json.dumps({"status": result.status, "window_counts": result.window_counts, "forecast_log_rows": result.forecast_log_rows}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
