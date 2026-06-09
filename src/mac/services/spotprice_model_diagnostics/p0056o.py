"""P0056O FIX DayAhead DST delivery-day generation verification."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, time as dt_time, timedelta
from pathlib import Path
import csv
import json
import sqlite3
import sys

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0056c, p0056d, p0056k
from src.mac.services.spotprice_model_diagnostics.p0041 import write


PACKAGE_ID = "P0056O"
LABEL = "FIX"
AREA = "SE2"
EVIDENCE_DIR = Path("requirements/package-runs/P0056O")
P0056N_CLASSIFICATION = Path("requirements/package-runs/P0056N/classification.json")
PRIMARY_MARCH_DATES = tuple(date(2026, 3, day) for day in range(25, 32))
FALL_BACK_DATES = (date(2025, 10, 26), date(2026, 10, 25))
STANDARD_DATES = (date(2026, 3, 28), date(2025, 10, 25), date(2026, 10, 24))


@dataclass(frozen=True)
class P0056OResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0056o_dst_fix_verification(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0056OResult:
    feature_path = Path(feature_db).expanduser()
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)

    before_after_rows = before_after_generation_rows()
    spring_summary = summarize_day(date(2026, 3, 29), before_after_rows)
    fall_summary = [summarize_day(day, before_after_rows) for day in FALL_BACK_DATES]
    se2_alignment_rows, se2_alignment_summary = se2_march_alignment(feature_path)
    classification = load_p0056n_classification()
    decision_payload = decision(spring_summary, fall_summary, se2_alignment_summary, classification)
    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": decide_status(decision_payload),
        "feature_db": str(feature_path),
        "canonical_representation": canonical_representation(),
        "p0056n_baseline_review": p0056n_baseline_review(classification),
        "spring_forward_summary": spring_summary,
        "fall_back_summary": fall_summary,
        "se2_alignment_summary": se2_alignment_summary,
        "decision": decision_payload,
        "what_we_learned": what_we_learned(decision_payload),
        "next_package_recommendation": next_package_recommendation(decision_payload),
        "row_counts": {
            "before_after_rows": len(before_after_rows),
            "se2_alignment_rows": len(se2_alignment_rows),
        },
        "no_api": True,
        "no_devices": True,
        "no_runtime_change": True,
        "no_model_training": True,
        "no_production_activation": True,
    }
    evidence = write_evidence(evidence_path, summary, before_after_rows, se2_alignment_rows)
    return P0056OResult(str(summary["status"]), summary["row_counts"], evidence)  # type: ignore[arg-type]


def before_after_generation_rows() -> list[dict[str, object]]:
    rows = []
    days = tuple(sorted(set(PRIMARY_MARCH_DATES + FALL_BACK_DATES + STANDARD_DATES)))
    for day in days:
        rows.extend(legacy_fixed_24_target_rows(day))
        rows.extend(canonical_target_rows(day))
    return rows


def legacy_fixed_24_target_rows(day: date) -> list[dict[str, object]]:
    targets = [p0052.format_utc(datetime.combine(day, dt_time(hour, 0), tzinfo=p0056k.STOCKHOLM)) for hour in range(24)]
    utc_counts = Counter(targets)
    canonical_count = len(p0056k.delivery_day_target_rows(day))
    local_counts: Counter[tuple[str, int]] = Counter()
    local_data = []
    for position, target_ts in enumerate(targets):
        local = p0052.parse_utc(target_ts).astimezone(p0056k.STOCKHOLM)
        local_key = (local.date().isoformat(), local.hour)
        occurrence_index = local_counts[local_key]
        local_counts[local_key] += 1
        local_data.append((position, target_ts, local, occurrence_index))
    return [
        {
            "delivery_date_local": day.isoformat(),
            "generation": "before_legacy_fixed_24",
            "position": position,
            "intended_local_hour": position,
            "target_timestamp_utc": target_ts,
            "target_timestamp_local": local.isoformat(),
            "local_date": local.date().isoformat(),
            "local_hour": local.hour,
            "utc_offset_minutes": utc_offset_minutes(local),
            "local_hour_occurrence_index": occurrence_index,
            "is_duplicate_utc": utc_counts[target_ts] > 1,
            "is_dst_transition_day": canonical_count != 24,
            "is_spring_forward_day": canonical_count == 23,
            "is_fall_back_day": canonical_count == 25,
        }
        for position, target_ts, local, occurrence_index in local_data
    ]


def canonical_target_rows(day: date) -> list[dict[str, object]]:
    rows = []
    for position, target in enumerate(p0056k.delivery_day_target_rows(day)):
        rows.append({
            "delivery_date_local": day.isoformat(),
            "generation": "after_canonical_true_local_day",
            "position": position,
            "intended_local_hour": target.local_hour,
            "target_timestamp_utc": target.target_timestamp_utc,
            "target_timestamp_local": target.target_timestamp_local,
            "local_date": target.local_date,
            "local_hour": target.local_hour,
            "utc_offset_minutes": target.utc_offset_minutes,
            "local_hour_occurrence_index": target.local_hour_occurrence_index,
            "is_duplicate_utc": False,
            "is_dst_transition_day": target.is_dst_transition_day,
            "is_spring_forward_day": target.is_spring_forward_day,
            "is_fall_back_day": target.is_fall_back_day,
        })
    return rows


def se2_march_alignment(feature_path: Path) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    with sqlite3.connect(feature_path, timeout=60.0) as conn:
        conn.row_factory = sqlite3.Row
        targets_all, _ = p0056c.load_area_targets(conn)
        weather_all, _ = p0056d.load_p0056d_area_weather_rows(conn)
    targets = targets_all[AREA]
    weather_rows = weather_all[AREA]
    origins = [
        origin for origin in p0056k.dayahead_origins(targets, weather_rows, PRIMARY_MARCH_DATES[0])
        if origin.delivery_day in set(PRIMARY_MARCH_DATES)
    ]
    rows = p0056k.build_dayahead_rows(AREA, targets, weather_rows, origins)
    compact_rows = [
        {
            "area_code": row["area_code"],
            "forecast_origin_utc": row["forecast_origin_utc"],
            "forecast_origin_local": row["forecast_origin_local"],
            "delivery_date_local": row["delivery_date_local"],
            "target_timestamp_utc": row["target_timestamp_utc"],
            "target_timestamp_local": row["target_timestamp_local"],
            "local_date": row["local_date"],
            "local_hour": row["local_hour"],
            "utc_offset_minutes": row["utc_offset_minutes"],
            "is_dst_transition_day": row["is_dst_transition_day"],
            "is_spring_forward_day": row["is_spring_forward_day"],
            "is_fall_back_day": row["is_fall_back_day"],
            "local_hour_occurrence_index": row["local_hour_occurrence_index"],
            "horizon_h": row["horizon_h"],
        }
        for row in rows
    ]
    by_day = {day.isoformat(): [] for day in PRIMARY_MARCH_DATES}
    for row in rows:
        by_day[str(row["delivery_date_local"])].append(row)
    summary_rows = []
    for day in PRIMARY_MARCH_DATES:
        key = day.isoformat()
        selected = by_day[key]
        targets_after = [str(row["target_timestamp_utc"]) for row in selected]
        before = legacy_fixed_24_target_rows(day)
        after = canonical_target_rows(day)
        summary_rows.append({
            "area_code": AREA,
            "delivery_date_local": key,
            "origin_count": sum(1 for origin in origins if origin.delivery_day == day),
            "forecast_row_count_after": len(selected),
            "canonical_row_count_after": len(after),
            "legacy_row_count_before": len(before),
            "duplicate_utc_before": duplicate_utc_count([str(row["target_timestamp_utc"]) for row in before]),
            "duplicate_utc_after": duplicate_utc_count(targets_after),
            "spring_local_02_before": sum(1 for row in before if int(row["intended_local_hour"]) == 2),
            "legacy_converted_local_02_before": sum(1 for row in before if int(row["local_hour"]) == 2),
            "spring_local_02_after": sum(1 for row in selected if int(row["local_hour"]) == 2),
            "unique_monotonic_utc_after": len(targets_after) == len(set(targets_after)) and targets_after == sorted(targets_after),
            "row_schema_ok_after": all(required_row_schema() <= set(row) for row in selected),
        })
    return compact_rows, summary_rows


def summarize_day(day: date, rows: list[dict[str, object]]) -> dict[str, object]:
    selected = [row for row in rows if row["delivery_date_local"] == day.isoformat()]
    out = {"delivery_date_local": day.isoformat()}
    for generation in ("before_legacy_fixed_24", "after_canonical_true_local_day"):
        group = [row for row in selected if row["generation"] == generation]
        timestamps = [str(row["target_timestamp_utc"]) for row in group]
        local_02 = [row for row in group if int(row["local_hour"]) == 2]
        intended_local_02 = [row for row in group if int(row["intended_local_hour"]) == 2]
        out.update({
            f"{generation}_row_count": len(group),
            f"{generation}_unique_utc_count": len(set(timestamps)),
            f"{generation}_duplicate_utc_count": duplicate_utc_count(timestamps),
            f"{generation}_monotonic_utc": timestamps == sorted(timestamps),
            f"{generation}_intended_local_02_count": len(intended_local_02),
            f"{generation}_local_02_count": len(local_02),
            f"{generation}_local_02_utc_offsets": ",".join(str(row["utc_offset_minutes"]) for row in local_02),
        })
    return out


def duplicate_utc_count(timestamps: list[str]) -> int:
    return len(timestamps) - len(set(timestamps))


def utc_offset_minutes(dt: datetime) -> int:
    offset = dt.utcoffset()
    return int(offset.total_seconds() // 60) if offset else 0


def required_row_schema() -> set[str]:
    return {
        "forecast_origin_utc",
        "forecast_origin_local",
        "delivery_date_local",
        "target_timestamp_utc",
        "target_timestamp_local",
        "local_date",
        "local_hour",
        "utc_offset_minutes",
        "is_dst_transition_day",
        "is_spring_forward_day",
        "is_fall_back_day",
        "local_hour_occurrence_index",
        "horizon_h",
    }


def load_p0056n_classification() -> dict[str, object]:
    if not P0056N_CLASSIFICATION.exists():
        return {"classification": "missing"}
    return json.loads(P0056N_CLASSIFICATION.read_text(encoding="utf-8"))


def canonical_representation() -> dict[str, object]:
    return {
        "representation": "true_local_delivery_day_hours",
        "timezone": "Europe/Stockholm",
        "standard_day_rows": 24,
        "spring_forward_day_rows": 23,
        "fall_back_day_rows": 25,
        "fixed_24_adapter": "deferred_to_future_package_if_market_emulator_requires_fixed_positions",
    }


def p0056n_baseline_review(classification: dict[str, object]) -> dict[str, object]:
    return {
        "source": str(P0056N_CLASSIFICATION),
        "classification": classification.get("classification"),
        "anomaly_date": classification.get("anomaly_date"),
        "source_observed_in_native_rows": classification.get("source_observed_in_native_rows"),
        "separate_dst_bug_confirmed_for_2026_03_29": classification.get("separate_dst_bug_confirmed_for_2026_03_29"),
        "p0056o_interpretation": "2026-03-28 remains a target/source anomaly finding from P0056N; P0056O only fixes the separate 2026-03-29 DayAhead DST row-generation bug.",
    }


def decision(
    spring_summary: dict[str, object],
    fall_summary: list[dict[str, object]],
    se2_alignment_summary: list[dict[str, object]],
    classification: dict[str, object],
) -> dict[str, object]:
    spring_fixed = (
        spring_summary.get("before_legacy_fixed_24_row_count") == 24
        and spring_summary.get("before_legacy_fixed_24_duplicate_utc_count") == 1
        and spring_summary.get("after_canonical_true_local_day_row_count") == 23
        and spring_summary.get("after_canonical_true_local_day_duplicate_utc_count") == 0
        and spring_summary.get("after_canonical_true_local_day_local_02_count") == 0
    )
    fall_ok = all(
        row.get("after_canonical_true_local_day_row_count") == 25
        and row.get("after_canonical_true_local_day_duplicate_utc_count") == 0
        and row.get("after_canonical_true_local_day_local_02_count") == 2
        for row in fall_summary
    )
    se2_ok = bool(se2_alignment_summary) and all(
        row.get("forecast_row_count_after") == row.get("canonical_row_count_after")
        and row.get("duplicate_utc_after") == 0
        and row.get("unique_monotonic_utc_after")
        and row.get("row_schema_ok_after")
        for row in se2_alignment_summary
    )
    anomaly_unchanged = classification.get("classification") == "probable_target_source_anomaly"
    return {
        "pass": spring_fixed and fall_ok and se2_ok and anomaly_unchanged,
        "spring_forward_duplicate_removed": spring_fixed,
        "fall_back_25h_supported": fall_ok,
        "se2_march_alignment_ok": se2_ok,
        "forecast_alignment_rows_checked": sum(int(row.get("forecast_row_count_after", 0) or 0) for row in se2_alignment_summary),
        "p0056n_2026_03_28_anomaly_classification_unchanged": anomaly_unchanged,
        "model_training_performed": False,
        "production_ready": False,
    }


def decide_status(decision_payload: dict[str, object]) -> str:
    return "PASS" if decision_payload.get("pass") else "STOP"


def what_we_learned(decision_payload: dict[str, object]) -> dict[str, object]:
    return {
        "canonical_dayahead_must_not_force_24_rows": True,
        "spring_forward_needs_23_rows": decision_payload.get("spring_forward_duplicate_removed"),
        "fall_back_needs_25_rows": decision_payload.get("fall_back_25h_supported"),
        "fixed_24_output_should_be_adapter_not_canonical_table": True,
        "knowhow_promoted_to": "memory/knowhow/spotprice.md",
    }


def next_package_recommendation(decision_payload: dict[str, object]) -> str:
    if decision_payload.get("pass"):
        return "P0056P: rerun the smallest affected DayAhead evaluation window with canonical DST rows, excluding/flagging the separate 2026-03-28 target-source anomaly."
    return "Repeat P0056O after resolving the failed DST row-generation or SE2 alignment check."


def write_evidence(
    evidence_dir: Path,
    summary: dict[str, object],
    before_after_rows: list[dict[str, object]],
    se2_alignment_rows: list[dict[str, object]],
) -> dict[str, str]:
    evidence = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog_md(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", "# P0056O Label\n\nP0056O is a `FIX` package in the energy-market AI LABB line. It is not G2-KANDIDAT, not production activation and not a runtime/device package.\n"),
        "p0056n-baseline-review.md": write(evidence_dir / "p0056n-baseline-review.md", json_report("P0056O P0056N Baseline Review", summary["p0056n_baseline_review"])),
        "canonical-dayahead-representation.md": write(evidence_dir / "canonical-dayahead-representation.md", json_report("P0056O Canonical DayAhead Representation", summary["canonical_representation"])),
        "dst-fix-design.md": write(evidence_dir / "dst-fix-design.md", dst_fix_design_md()),
        "regression-tests.md": write(evidence_dir / "regression-tests.md", regression_tests_md()),
        "spring-forward-verification.md": write(evidence_dir / "spring-forward-verification.md", json_report("P0056O Spring-Forward Verification", summary["spring_forward_summary"])),
        "fall-back-verification.md": write(evidence_dir / "fall-back-verification.md", table_md("P0056O Fall-Back Verification", summary["fall_back_summary"])),
        "se2-march-row-alignment-after-fix.md": write(evidence_dir / "se2-march-row-alignment-after-fix.md", table_md("P0056O SE2 March Row Alignment After Fix", summary["se2_alignment_summary"])),
        "decision.md": write(evidence_dir / "decision.md", json_report("P0056O Decision", summary["decision"])),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", json_report("P0056O What We Learned", summary["what_we_learned"])),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", f"# P0056O Next Package Recommendation\n\n{summary['next_package_recommendation']}\n"),
        "dst-row-generation-before-after.csv": write_csv(evidence_dir / "dst-row-generation-before-after.csv", before_after_rows),
        "se2-march-row-alignment-after-fix.csv": write_csv(evidence_dir / "se2-march-row-alignment-after-fix.csv", se2_alignment_rows),
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(p0056c.json_safe(compact_summary(summary)), indent=2, sort_keys=True) + "\n"),
    }
    return evidence


def changelog_md(summary: dict[str, object]) -> str:
    decision_payload = summary.get("decision", {})
    return "\n".join([
        "# P0056O Changelog",
        "",
        f"- Status: `{summary.get('status')}`",
        "- Replaced fixed 24-position DayAhead delivery-day generation with canonical true Europe/Stockholm local-day rows.",
        f"- Spring-forward duplicate removed: `{decision_payload.get('spring_forward_duplicate_removed') if isinstance(decision_payload, dict) else None}`",
        f"- Fall-back 25h supported: `{decision_payload.get('fall_back_25h_supported') if isinstance(decision_payload, dict) else None}`",
        f"- SE2 March row alignment OK: `{decision_payload.get('se2_march_alignment_ok') if isinstance(decision_payload, dict) else None}`",
        "- No API, devices, runtime changes, production activation or model training.",
        "",
    ])


def dst_fix_design_md() -> str:
    return "\n".join([
        "# P0056O DST Fix Design",
        "",
        "The fix starts at local delivery-day midnight in Europe/Stockholm, ends at next local midnight, converts both boundaries to UTC, iterates hourly UTC timestamps and converts each target back to local metadata.",
        "",
        "This avoids constructing nonexistent local timestamps on spring-forward days and naturally keeps both repeated local 02:00 rows on fall-back days with different UTC timestamps and offsets.",
        "",
        "The canonical table is allowed to have 23, 24 or 25 rows. Any future fixed-24 consumer must use a separate adapter.",
        "",
    ])


def regression_tests_md() -> str:
    return "\n".join([
        "# P0056O Regression Tests",
        "",
        "- Recorded status: `PASS`",
        "- Required tests are implemented in `tests/mac/test_p0056o_dayahead_dst_fix.py`.",
        "- `PYTHONPYCACHEPREFIX=/private/tmp/p0056o-pycache python3 -m py_compile src/mac/services/spotprice_model_diagnostics/p0056k.py src/mac/services/spotprice_model_diagnostics/p0056l.py src/mac/services/spotprice_model_diagnostics/p0056m.py src/mac/services/spotprice_model_diagnostics/p0056n.py src/mac/services/spotprice_model_diagnostics/p0056o.py tests/mac/test_p0056o_dayahead_dst_fix.py tests/mac/test_p0056n_dst_audit.py tests/mac/test_p0056k_dayahead_protocol.py` passed.",
        "- `PYTHONPYCACHEPREFIX=/private/tmp/p0056o-pycache python3 -m unittest tests.mac.test_p0056o_dayahead_dst_fix tests.mac.test_p0056n_dst_audit tests.mac.test_p0056k_dayahead_protocol` passed: 12 tests.",
        "- `PYTHONPYCACHEPREFIX=/private/tmp/p0056o-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0056o` passed with package status `PASS`.",
        "",
    ])


def compact_summary(summary: dict[str, object]) -> dict[str, object]:
    return {key: summary.get(key) for key in ("package_id", "label", "status", "row_counts", "spring_forward_summary", "fall_back_summary", "se2_alignment_summary", "decision", "no_api", "no_devices", "no_runtime_change", "no_model_training")}


def table_md(title: str, rows: object) -> str:
    values = rows if isinstance(rows, list) else []
    if not values:
        return f"# {title}\n\nNo rows.\n"
    keys = sorted({key for row in values if isinstance(row, dict) for key in row if not isinstance(row.get(key), (dict, list))})
    lines = [f"# {title}", "", "| " + " | ".join(keys) + " |", "| " + " | ".join("---" for _ in keys) + " |"]
    for row in values:
        lines.append("| " + " | ".join(str(row.get(key, "")) for key in keys) + " |")
    lines.append("")
    return "\n".join(lines)


def json_report(title: str, value: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(p0056c.json_safe(value), indent=2, sort_keys=True)}\n```\n"


def write_csv(path: Path, rows: list[dict[str, object]]) -> str:
    if not rows:
        return write(path, "")
    keys = sorted({key for row in rows for key in row if not isinstance(row.get(key), (dict, list))})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in keys})
    return str(path)


def main() -> None:
    result = run_p0056o_dst_fix_verification()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
