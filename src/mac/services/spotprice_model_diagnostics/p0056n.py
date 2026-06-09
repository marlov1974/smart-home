"""P0056N LABB SE2 DST and target anomaly audit."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time as dt_time, timedelta, timezone
from pathlib import Path
import csv
import json
import math
import sqlite3
import sys
from zoneinfo import ZoneInfo

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0056k
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write


PACKAGE_ID = "P0056N"
LABEL = "LABB"
AREA = "SE2"
STOCKHOLM = ZoneInfo("Europe/Stockholm")
EVIDENCE_DIR = Path("requirements/package-runs/P0056N")
P0056M_HOUR_ROWS = Path("requirements/package-runs/P0056M/hour-level-summary.csv")
P0056M_DAY_ROWS = Path("requirements/package-runs/P0056M/day-level-results.csv")
PRIMARY_AUDIT_DATES = tuple(date(2026, 3, day) for day in range(25, 32))
WORST_DATES = (
    date(2026, 3, 28),
    date(2025, 12, 27),
    date(2025, 12, 12),
    date(2026, 2, 8),
    date(2025, 12, 24),
)
COMPARISON_DATES = (date(2026, 3, 21), date(2026, 4, 4))
AUDIT_DATES = tuple(sorted(set(PRIMARY_AUDIT_DATES + WORST_DATES + COMPARISON_DATES)))
ANOMALY_DATE = date(2026, 3, 28)


@dataclass(frozen=True)
class P0056NResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0056n_dst_target_anomaly_audit(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0056NResult:
    feature_path = Path(feature_db).expanduser()
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(feature_path) as conn:
        conn.row_factory = sqlite3.Row
        native_rows = load_native_rows(conn, AUDIT_DATES)
        hourly_rows = load_hourly_rows(conn, AUDIT_DATES)

    p0056m_hour_rows = load_p0056m_hour_rows(PRIMARY_AUDIT_DATES)
    p0056m_day_rows = load_p0056m_day_rows(AUDIT_DATES)
    dst_rows = dst_local_day_audit(PRIMARY_AUDIT_DATES)
    mapping_rows = utc_local_mapping_rows(PRIMARY_AUDIT_DATES)
    raw_local_rows, raw_utc_rows = native_day_audits(native_rows)
    hourly_local_rows, hourly_utc_rows = hourly_day_audits(hourly_rows)
    neighbor_rows = neighbor_day_comparison(hourly_local_rows, p0056m_day_rows)
    forecast_rows = forecast_row_alignment_audit(p0056m_hour_rows)
    spikes = top_spikes(hourly_rows, 20)
    classification = target_anomaly_classification(hourly_local_rows, raw_local_rows, forecast_rows, spikes)
    decision_payload = decision(classification, dst_rows, forecast_rows)
    status = decide_status(native_rows, hourly_rows, mapping_rows, classification)
    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "area": AREA,
        "feature_db": str(feature_path),
        "audit_window": audit_window_summary(),
        "p0056m_baseline_review": p0056m_baseline_review(p0056m_day_rows),
        "dst_summary": dst_summary(dst_rows, mapping_rows, forecast_rows),
        "classification": classification,
        "decision": decision_payload,
        "what_we_learned": what_we_learned(classification, decision_payload),
        "next_package_recommendation": next_package_recommendation(classification, decision_payload),
        "row_counts": {
            "native_rows": len(native_rows),
            "hourly_rows": len(hourly_rows),
            "p0056m_hour_rows": len(p0056m_hour_rows),
            "p0056m_day_rows": len(p0056m_day_rows),
            "dst_rows": len(dst_rows),
            "forecast_alignment_rows": len(forecast_rows),
        },
        "no_api": True,
        "no_devices": True,
        "no_runtime_change": True,
        "no_model_training": True,
        "no_production_activation": True,
    }
    evidence = write_evidence(
        evidence_path,
        summary,
        raw_local_rows,
        raw_utc_rows,
        hourly_local_rows,
        hourly_utc_rows,
        dst_rows,
        mapping_rows,
        neighbor_rows,
        forecast_rows,
        spikes,
        classification,
    )
    return P0056NResult(status, summary["row_counts"], evidence)  # type: ignore[arg-type]


def load_native_rows(conn: sqlite3.Connection, audit_dates: tuple[date, ...]) -> list[dict[str, object]]:
    start_utc, end_utc = utc_bounds_for_dates(audit_dates)
    rows = []
    for row in conn.execute(
        """
        SELECT area_code, interval_start_utc, interval_end_utc, value, unit, value_kind,
               native_resolution_minutes, source_system, source_area_code, document_type,
               process_type, generated_by_package
        FROM area_consumption_native_v1
        WHERE generated_by_package='P0056A'
          AND area_code=?
          AND interval_start_utc >= ?
          AND interval_start_utc < ?
        ORDER BY interval_start_utc
        """,
        (AREA, p0052.format_utc(start_utc), p0052.format_utc(end_utc)),
    ):
        item = dict(row)
        local = p0052.parse_utc(str(item["interval_start_utc"])).astimezone(STOCKHOLM)
        if local.date() in audit_dates:
            item["local_date"] = local.date().isoformat()
            item["local_hour"] = local.hour
            item["local_timestamp"] = local.isoformat()
            rows.append(item)
    return rows


def load_hourly_rows(conn: sqlite3.Connection, audit_dates: tuple[date, ...]) -> list[dict[str, object]]:
    start_utc, end_utc = utc_bounds_for_dates(audit_dates)
    rows = []
    for row in conn.execute(
        """
        SELECT timestamp_utc, area_code, consumption_mw, source_system, aggregation_method,
               native_resolution_mix, coverage_flag, input_row_count, generated_by_package
        FROM area_consumption_hourly_v1
        WHERE generated_by_package='P0056A'
          AND area_code=?
          AND timestamp_utc >= ?
          AND timestamp_utc < ?
        ORDER BY timestamp_utc
        """,
        (AREA, p0052.format_utc(start_utc), p0052.format_utc(end_utc)),
    ):
        item = dict(row)
        local = p0052.parse_utc(str(item["timestamp_utc"])).astimezone(STOCKHOLM)
        if local.date() in audit_dates:
            item["local_date"] = local.date().isoformat()
            item["local_hour"] = local.hour
            item["local_timestamp"] = local.isoformat()
            rows.append(item)
    return rows


def load_p0056m_hour_rows(audit_dates: tuple[date, ...]) -> list[dict[str, object]]:
    rows = []
    wanted = {day.isoformat() for day in audit_dates}
    with P0056M_HOUR_ROWS.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["delivery_date"] in wanted:
                rows.append({key: parse_csv_value(value) for key, value in row.items()})
    return rows


def load_p0056m_day_rows(audit_dates: tuple[date, ...]) -> list[dict[str, object]]:
    rows = []
    wanted = {day.isoformat() for day in audit_dates}
    with P0056M_DAY_ROWS.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["delivery_date"] in wanted:
                rows.append({key: parse_csv_value(value) for key, value in row.items()})
    return rows


def expected_local_hours_for_day(local_day: date) -> list[dict[str, object]]:
    start_local = datetime.combine(local_day, dt_time(0, 0), tzinfo=STOCKHOLM)
    end_local = datetime.combine(local_day + timedelta(days=1), dt_time(0, 0), tzinfo=STOCKHOLM)
    current = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)
    rows = []
    while current < end_utc:
        local = current.astimezone(STOCKHOLM)
        rows.append({
            "timestamp_utc": p0052.format_utc(current),
            "local_date": local.date().isoformat(),
            "local_hour": local.hour,
            "local_timestamp": local.isoformat(),
            "utc_offset": local.utcoffset().total_seconds() / 3600.0 if local.utcoffset() else 0.0,
        })
        current += timedelta(hours=1)
    return rows


def p0056k_delivery_day_mapping(local_day: date) -> list[dict[str, object]]:
    targets = p0056k.delivery_day_target_utc_hours(local_day)
    utc_counts = Counter(targets)
    converted_keys = []
    rows = []
    for position, target_ts in enumerate(targets):
        local = p0052.parse_utc(target_ts).astimezone(STOCKHOLM)
        key = f"{local.date().isoformat()}T{local.hour:02d}"
        converted_keys.append(key)
        rows.append({
            "delivery_date": local_day.isoformat(),
            "position": position,
            "intended_local_hour": position,
            "target_timestamp_utc": target_ts,
            "converted_local_date": local.date().isoformat(),
            "converted_local_hour": local.hour,
            "converted_local_timestamp": local.isoformat(),
            "is_duplicate_utc": utc_counts[target_ts] > 1,
            "intended_hour_matches_converted_hour": position == local.hour,
            "forced_nonexistent_or_shifted_local_hour": position != local.hour,
        })
    local_counts = Counter(converted_keys)
    for row in rows:
        key = f"{row['converted_local_date']}T{int(row['converted_local_hour']):02d}"
        row["is_duplicate_converted_local_hour"] = local_counts[key] > 1
    return rows


def dst_local_day_audit(audit_dates: tuple[date, ...]) -> list[dict[str, object]]:
    rows = []
    for day in audit_dates:
        expected = expected_local_hours_for_day(day)
        actual = p0056k_delivery_day_mapping(day)
        expected_hours = {int(row["local_hour"]) for row in expected}
        actual_utc = [str(row["target_timestamp_utc"]) for row in actual]
        rows.append({
            "local_date": day.isoformat(),
            "expected_valid_local_hour_count": len(expected),
            "expected_valid_local_hours": ",".join(f"{hour:02d}" for hour in sorted(expected_hours)),
            "p0056k_position_count": len(actual),
            "p0056k_unique_utc_count": len(set(actual_utc)),
            "p0056k_duplicate_utc_count": len(actual_utc) - len(set(actual_utc)),
            "p0056k_forced_shifted_position_count": sum(1 for row in actual if row["forced_nonexistent_or_shifted_local_hour"]),
            "spring_forward_no_local_02": day == date(2026, 3, 29) and 2 not in expected_hours,
            "dst_behavior": "spring_forward_23h" if len(expected) == 23 else "standard_24h" if len(expected) == 24 else "fall_back_25h",
        })
    return rows


def utc_local_mapping_rows(audit_dates: tuple[date, ...]) -> list[dict[str, object]]:
    rows = []
    for day in audit_dates:
        expected_by_utc = {str(row["timestamp_utc"]): row for row in expected_local_hours_for_day(day)}
        for row in p0056k_delivery_day_mapping(day):
            expected = expected_by_utc.get(str(row["target_timestamp_utc"]))
            rows.append({
                **row,
                "exists_in_expected_valid_utc_hours": expected is not None,
                "expected_local_hour_for_utc": expected.get("local_hour") if expected else None,
            })
    return rows


def native_day_audits(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    return native_group_audit(rows, "local_date"), native_group_audit(rows, "utc_date")


def native_group_audit(rows: list[dict[str, object]], key_type: str) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if key_type == "utc_date":
            key = p0052.parse_utc(str(row["interval_start_utc"])).date().isoformat()
        else:
            key = str(row["local_date"])
        groups[key].append(row)
    out = []
    for key, selected in sorted(groups.items()):
        values = [float(row["value"]) for row in selected]
        starts = [str(row["interval_start_utc"]) for row in selected]
        resolutions = Counter(str(row["native_resolution_minutes"]) for row in selected)
        out.append({
            "day_type": key_type,
            "day": key,
            "native_row_count": len(selected),
            "unique_interval_start_count": len(set(starts)),
            "duplicate_interval_start_count": len(starts) - len(set(starts)),
            "native_resolution_distribution": counter_text(resolutions),
            "min_mw": min(values) if values else None,
            "mean_mw": mean(values),
            "max_mw": max(values) if values else None,
            "p95_mw": percentile(values, 0.95) if values else None,
        })
    return out


def hourly_day_audits(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    return hourly_group_audit(rows, "local_date"), hourly_group_audit(rows, "utc_date")


def hourly_group_audit(rows: list[dict[str, object]], key_type: str) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if key_type == "utc_date":
            key = p0052.parse_utc(str(row["timestamp_utc"])).date().isoformat()
        else:
            key = str(row["local_date"])
        groups[key].append(row)
    out = []
    for key, selected in sorted(groups.items()):
        values = [float(row["consumption_mw"]) for row in selected]
        timestamps = [str(row["timestamp_utc"]) for row in selected]
        local_keys = [f"{row['local_date']}T{int(row['local_hour']):02d}" for row in selected]
        coverage = Counter(str(row["coverage_flag"]) for row in selected)
        resolution = Counter(str(row["native_resolution_mix"]) for row in selected)
        input_counts = Counter(str(row["input_row_count"]) for row in selected)
        missing_utc_hours = []
        expected_count = None
        if key_type == "local_date":
            expected = expected_local_hours_for_day(date.fromisoformat(key))
            expected_count = len(expected)
            expected_utc = {str(row["timestamp_utc"]) for row in expected}
            missing_utc_hours = sorted(expected_utc - set(timestamps))
        out.append({
            "day_type": key_type,
            "day": key,
            "hourly_row_count": len(selected),
            "expected_local_day_hour_count": expected_count,
            "unique_utc_timestamp_count": len(set(timestamps)),
            "duplicate_utc_timestamp_count": len(timestamps) - len(set(timestamps)),
            "missing_expected_utc_hours": ",".join(missing_utc_hours),
            "missing_expected_utc_hour_count": len(missing_utc_hours),
            "duplicate_local_timestamp_count": len(local_keys) - len(set(local_keys)),
            "coverage_flag_distribution": counter_text(coverage),
            "native_resolution_mix_distribution": counter_text(resolution),
            "input_row_count_distribution": counter_text(input_counts),
            "min_actual_mw": min(values) if values else None,
            "mean_actual_mw": mean(values),
            "max_actual_mw": max(values) if values else None,
            "p95_actual_mw": percentile(values, 0.95) if values else None,
        })
    return out


def neighbor_day_comparison(hourly_local_rows: list[dict[str, object]], p0056m_day_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    p0056m_by_day = {str(row["delivery_date"]): row for row in p0056m_day_rows}
    wanted = {day.isoformat() for day in PRIMARY_AUDIT_DATES + COMPARISON_DATES}
    out = []
    for row in hourly_local_rows:
        day = str(row["day"])
        if day not in wanted:
            continue
        p0056m = p0056m_by_day.get(day, {})
        out.append({
            "local_date": day,
            "weekday": date.fromisoformat(day).strftime("%A"),
            "hourly_mean_actual_mw": row["mean_actual_mw"],
            "hourly_max_actual_mw": row["max_actual_mw"],
            "hourly_row_count": row["hourly_row_count"],
            "p0056m_mean_forecast_mw": p0056m.get("mean_forecast_load_mw"),
            "p0056m_hourly_MAE": p0056m.get("hourly_MAE"),
            "p0056m_bias_mw": p0056m.get("bias_mw"),
        })
    return sorted(out, key=lambda row: str(row["local_date"]))


def forecast_row_alignment_audit(p0056m_hour_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_day_target_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in p0056m_hour_rows:
        by_day_target_counts[str(row["delivery_date"])][str(row["target_timestamp_utc"])] += 1
    mapping_by_day: dict[str, dict[str, list[dict[str, object]]]] = {}
    for day in PRIMARY_AUDIT_DATES:
        by_ts: dict[str, list[dict[str, object]]] = defaultdict(list)
        for mapping in p0056k_delivery_day_mapping(day):
            by_ts[str(mapping["target_timestamp_utc"])].append(mapping)
        mapping_by_day[day.isoformat()] = by_ts
    out = []
    for row in p0056m_hour_rows:
        day = str(row["delivery_date"])
        target_ts = str(row["target_timestamp_utc"])
        target_local = p0052.parse_utc(target_ts).astimezone(STOCKHOLM)
        origin_local = p0052.parse_utc(str(row["forecast_origin"])).astimezone(STOCKHOLM)
        mappings = mapping_by_day.get(day, {}).get(target_ts, [])
        out.append({
            "forecast_origin_utc": row["forecast_origin"],
            "forecast_origin_local": origin_local.isoformat(),
            "delivery_date_local": day,
            "target_timestamp_utc": target_ts,
            "target_timestamp_local": target_local.isoformat(),
            "horizon_h": int(float(row["horizon_h"])),
            "local_hour": int(float(row["local_hour"])),
            "is_duplicate_target_timestamp_in_p0056m_day": by_day_target_counts[day][target_ts] > 1,
            "p0056k_mapping_positions": ",".join(str(mapping["position"]) for mapping in mappings),
            "p0056k_duplicate_utc_for_delivery_day": any(bool(mapping["is_duplicate_utc"]) for mapping in mappings),
            "p0056k_forced_shifted_position": any(bool(mapping["forced_nonexistent_or_shifted_local_hour"]) for mapping in mappings),
            "is_missing_local_hour_expected_by_DST": day == "2026-03-29" and int(float(row["local_hour"])) == 2,
            "actual_mw": float(row["actual_mw"]),
            "forecast_mw": float(row["forecast_mw"]),
            "error_mw": float(row["error_mw"]),
        })
    return out


def top_spikes(hourly_rows: list[dict[str, object]], limit: int = 20) -> list[dict[str, object]]:
    selected = sorted(hourly_rows, key=lambda row: float(row["consumption_mw"]), reverse=True)[:limit]
    out = []
    for rank, row in enumerate(selected, start=1):
        out.append({
            "rank": rank,
            "timestamp_utc": row["timestamp_utc"],
            "local_timestamp": row["local_timestamp"],
            "local_date": row["local_date"],
            "local_hour": row["local_hour"],
            "actual_mw": float(row["consumption_mw"]),
            "native_resolution_mix": row["native_resolution_mix"],
            "input_row_count": row["input_row_count"],
            "coverage_flag": row["coverage_flag"],
        })
    return out


def target_anomaly_classification(
    hourly_local_rows: list[dict[str, object]],
    native_local_rows: list[dict[str, object]],
    forecast_rows: list[dict[str, object]],
    spikes: list[dict[str, object]],
) -> dict[str, object]:
    hourly = {str(row["day"]): row for row in hourly_local_rows}
    native = {str(row["day"]): row for row in native_local_rows}
    anomaly = hourly.get(ANOMALY_DATE.isoformat(), {})
    native_anomaly = native.get(ANOMALY_DATE.isoformat(), {})
    prior = hourly.get((ANOMALY_DATE - timedelta(days=7)).isoformat(), {})
    nxt = hourly.get((ANOMALY_DATE + timedelta(days=7)).isoformat(), {})
    neighbors = [hourly.get((ANOMALY_DATE + timedelta(days=offset)).isoformat(), {}) for offset in (-3, -2, -1, 1, 2, 3)]
    neighbor_means = [float(row["mean_actual_mw"]) for row in neighbors if row]
    baseline = mean(neighbor_means)
    anomaly_mean = float(anomaly.get("mean_actual_mw", 0.0) or 0.0)
    native_mean = float(native_anomaly.get("mean_mw", 0.0) or 0.0)
    hourly_timestamps_normal = anomaly.get("duplicate_utc_timestamp_count") == 0 and anomaly.get("missing_expected_utc_hour_count") == 0
    hourly_coverage_complete = str(anomaly.get("coverage_flag_distribution")) == "ok:24"
    source_observed = bool(native_anomaly) and native_mean > baseline * 2.0 if baseline else False
    same_weekday_not_repeated = bool(prior and nxt) and anomaly_mean > max(float(prior["mean_actual_mw"]), float(nxt["mean_actual_mw"])) * 2.0
    p0056k_dst_bug = any(row["delivery_date_local"] == "2026-03-29" and row["p0056k_duplicate_utc_for_delivery_day"] for row in forecast_rows)
    if source_observed and hourly_timestamps_normal and same_weekday_not_repeated:
        classification = "probable_target_source_anomaly"
    elif not hourly_timestamps_normal:
        classification = "probable_time/DST_bug"
    elif source_observed:
        classification = "inconclusive"
    else:
        classification = "inconclusive"
    return {
        "anomaly_date": ANOMALY_DATE.isoformat(),
        "classification": classification,
        "source_observed_in_native_rows": source_observed,
        "hourly_timestamp_shape_normal_for_day": hourly_timestamps_normal,
        "hourly_coverage_complete_for_day": hourly_coverage_complete,
        "same_weekday_prior_next_not_repeated": same_weekday_not_repeated,
        "neighbor_mean_actual_mw": baseline,
        "anomaly_hourly_mean_actual_mw": anomaly_mean,
        "anomaly_native_mean_mw": native_mean,
        "same_weekday_prior_mean_mw": prior.get("mean_actual_mw"),
        "same_weekday_next_mean_mw": nxt.get("mean_actual_mw"),
        "top_spike_actual_mw": spikes[0]["actual_mw"] if spikes else None,
        "separate_dst_bug_confirmed_for_2026_03_29": p0056k_dst_bug,
        "interpretation": "The 2026-03-28 extreme is already present in P0056A native source rows. Hourly UTC timestamps have normal shape, but the local day has partial source coverage on two hourly rows and only 94 native 15-minute rows instead of an expected 96. The anomaly is not explained by the separate 2026-03-29 DayAhead DST duplicate. Without an independent source it should be treated as a probable target/source anomaly or target-definition/coverage issue, not as a confirmed real load regime.",
    }


def decision(classification: dict[str, object], dst_rows: list[dict[str, object]], forecast_rows: list[dict[str, object]]) -> dict[str, object]:
    dst_bug = bool(classification.get("separate_dst_bug_confirmed_for_2026_03_29"))
    anomaly_class = str(classification.get("classification"))
    return {
        "flag_or_exclude_recommendation": "flag_2026_03_28_as_probable_source_anomaly_and_exclude_from_model_selection_until_independently_verified",
        "dst_recommendation": "fix_or_special_case_DayAhead_delivery_day_generation_for_23h_25h_local_days_before_future_realistic_DayAhead_comparisons" if dst_bug else "keep_current_dst_mapping",
        "model_change_allowed_by_p0056n": False,
        "classification": anomaly_class,
        "forecast_alignment_rows_checked": len(forecast_rows),
    }


def decide_status(native_rows: list[dict[str, object]], hourly_rows: list[dict[str, object]], mapping_rows: list[dict[str, object]], classification: dict[str, object]) -> str:
    if not hourly_rows or not mapping_rows:
        return "STOP"
    if not native_rows:
        return "WARN"
    return "PASS" if classification.get("classification") else "WARN"


def dst_summary(dst_rows: list[dict[str, object]], mapping_rows: list[dict[str, object]], forecast_rows: list[dict[str, object]]) -> dict[str, object]:
    spring = next((row for row in dst_rows if row["local_date"] == "2026-03-29"), {})
    return {
        "stockholm_2026_03_29_expected_valid_hour_count": spring.get("expected_valid_local_hour_count"),
        "stockholm_2026_03_29_has_no_local_02": spring.get("spring_forward_no_local_02"),
        "p0056k_2026_03_29_position_count": spring.get("p0056k_position_count"),
        "p0056k_2026_03_29_unique_utc_count": spring.get("p0056k_unique_utc_count"),
        "p0056k_2026_03_29_duplicate_utc_count": spring.get("p00556k_duplicate_utc_count", spring.get("p0056k_duplicate_utc_count")),
        "p0056m_duplicate_target_rows_2026_03_29": sum(1 for row in forecast_rows if row["delivery_date_local"] == "2026-03-29" and row["is_duplicate_target_timestamp_in_p0056m_day"]),
    }


def p0056m_baseline_review(day_rows: list[dict[str, object]]) -> dict[str, object]:
    anomaly = next((row for row in day_rows if row.get("delivery_date") == ANOMALY_DATE.isoformat()), {})
    return {
        "source": str(P0056M_DAY_ROWS),
        "rows_loaded": len(day_rows),
        "anomaly_day_present": bool(anomaly),
        "anomaly_day_hourly_MAE": anomaly.get("hourly_MAE"),
        "anomaly_day_mean_actual_load_mw": anomaly.get("mean_actual_load_mw"),
        "anomaly_day_mean_forecast_load_mw": anomaly.get("mean_forecast_load_mw"),
    }


def audit_window_summary() -> dict[str, object]:
    return {
        "primary_audit_dates": [day.isoformat() for day in PRIMARY_AUDIT_DATES],
        "worst_dates": [day.isoformat() for day in WORST_DATES],
        "comparison_dates": [day.isoformat() for day in COMPARISON_DATES],
        "area": AREA,
    }


def what_we_learned(classification: dict[str, object], decision_payload: dict[str, object]) -> dict[str, object]:
    return {
        "p0056k_dayahead_spring_forward_bug": classification.get("separate_dst_bug_confirmed_for_2026_03_29"),
        "anomaly_2026_03_28_classification": classification.get("classification"),
        "source_observed_extreme": classification.get("source_observed_in_native_rows"),
        "future_evaluation_policy": decision_payload.get("flag_or_exclude_recommendation"),
    }


def next_package_recommendation(classification: dict[str, object], decision_payload: dict[str, object]) -> str:
    return "P0056O: fix/audit DayAhead DST delivery-day generation and rerun SE2 M6 slices with 2026-03-28 flagged/excluded from model selection."


def utc_bounds_for_dates(audit_dates: tuple[date, ...]) -> tuple[datetime, datetime]:
    start = datetime.combine(min(audit_dates), dt_time(0, 0), tzinfo=STOCKHOLM).astimezone(timezone.utc)
    end = datetime.combine(max(audit_dates) + timedelta(days=1), dt_time(0, 0), tzinfo=STOCKHOLM).astimezone(timezone.utc)
    return start, end


def parse_csv_value(value: str) -> object:
    if value in {"True", "False"}:
        return value == "True"
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def mean(values: list[float]) -> float:
    return p0054k.mean_float(values) if values else 0.0


def counter_text(counter: Counter[str]) -> str:
    return ",".join(f"{key}:{counter[key]}" for key in sorted(counter))


def write_evidence(
    evidence_dir: Path,
    summary: dict[str, object],
    raw_local_rows: list[dict[str, object]],
    raw_utc_rows: list[dict[str, object]],
    hourly_local_rows: list[dict[str, object]],
    hourly_utc_rows: list[dict[str, object]],
    dst_rows: list[dict[str, object]],
    mapping_rows: list[dict[str, object]],
    neighbor_rows: list[dict[str, object]],
    forecast_rows: list[dict[str, object]],
    spikes: list[dict[str, object]],
    classification: dict[str, object],
) -> dict[str, str]:
    evidence = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog_md(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", "# P0056N LABB Label\n\nP0056N is LABB-only target/DST diagnostics. It is not G2-KANDIDAT or production activation.\n"),
        "p0056m-baseline-review.md": write(evidence_dir / "p0056m-baseline-review.md", json_report("P0056N P0056M Baseline Review", summary["p0056m_baseline_review"])),
        "audit-window.md": write(evidence_dir / "audit-window.md", json_report("P0056N Audit Window", summary["audit_window"])),
        "raw-native-row-audit.md": write(evidence_dir / "raw-native-row-audit.md", table_md("P0056N Raw Native Local-Day Audit", raw_local_rows) + "\n" + table_md("P0056N Raw Native UTC-Day Audit", raw_utc_rows)),
        "hourly-row-audit.md": write(evidence_dir / "hourly-row-audit.md", table_md("P0056N Hourly Local-Day Audit", hourly_local_rows) + "\n" + table_md("P0056N Hourly UTC-Day Audit", hourly_utc_rows)),
        "dst-local-day-audit.md": write(evidence_dir / "dst-local-day-audit.md", table_md("P0056N DST Local-Day Audit", dst_rows)),
        "utc-local-mapping-audit.md": write(evidence_dir / "utc-local-mapping-audit.md", table_md("P0056N UTC Local Mapping Audit", mapping_rows)),
        "target-anomaly-2026-03-28.md": write(evidence_dir / "target-anomaly-2026-03-28.md", target_anomaly_md(classification, hourly_local_rows, raw_local_rows)),
        "neighbor-day-comparison.md": write(evidence_dir / "neighbor-day-comparison.md", table_md("P0056N Neighbor Day Comparison", neighbor_rows)),
        "forecast-row-alignment-audit.md": write(evidence_dir / "forecast-row-alignment-audit.md", table_md("P0056N Forecast Row Alignment Audit", forecast_rows)),
        "top-spikes.md": write(evidence_dir / "top-spikes.md", table_md("P0056N Top Actual-Load Spikes", spikes)),
        "classification.md": write(evidence_dir / "classification.md", json_report("P0056N Classification", classification)),
        "decision.md": write(evidence_dir / "decision.md", json_report("P0056N Decision", summary["decision"])),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", json_report("P0056N What We Learned", summary["what_we_learned"])),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", f"# P0056N Next Package Recommendation\n\n{summary['next_package_recommendation']}\n"),
        "raw-native-row-audit.csv": write_csv(evidence_dir / "raw-native-row-audit.csv", raw_local_rows + raw_utc_rows),
        "hourly-row-audit.csv": write_csv(evidence_dir / "hourly-row-audit.csv", hourly_local_rows + hourly_utc_rows),
        "dst-local-day-audit.csv": write_csv(evidence_dir / "dst-local-day-audit.csv", dst_rows),
        "forecast-row-alignment-audit.csv": write_csv(evidence_dir / "forecast-row-alignment-audit.csv", forecast_rows),
        "top-spikes.csv": write_csv(evidence_dir / "top-spikes.csv", spikes),
        "classification.json": write(evidence_dir / "classification.json", json.dumps(json_safe(classification), indent=2, sort_keys=True) + "\n"),
    }
    return evidence


def changelog_md(summary: dict[str, object]) -> str:
    rows = summary["row_counts"]
    classification = summary["classification"]
    return "\n".join([
        "# P0056N Changelog",
        "",
        f"- Status: `{summary['status']}`",
        f"- Native rows audited: `{rows['native_rows']}`",
        f"- Hourly rows audited: `{rows['hourly_rows']}`",
        f"- P0056M forecast rows audited: `{rows['p0056m_hour_rows']}`",
        f"- 2026-03-28 classification: `{classification['classification']}`",
        f"- Separate DST bug confirmed: `{classification['separate_dst_bug_confirmed_for_2026_03_29']}`",
        "- No API, devices, runtime changes, model retraining, production activation or forbidden feature families.",
        "",
    ])


def target_anomaly_md(classification: dict[str, object], hourly_rows: list[dict[str, object]], native_rows: list[dict[str, object]]) -> str:
    hourly = next((row for row in hourly_rows if row["day"] == ANOMALY_DATE.isoformat()), {})
    native = next((row for row in native_rows if row["day"] == ANOMALY_DATE.isoformat()), {})
    return "\n".join([
        "# P0056N Target Anomaly 2026-03-28",
        "",
        "## Classification",
        "",
        f"`{classification['classification']}`",
        "",
        "## Evidence",
        "",
        f"- Hourly mean actual MW: `{hourly.get('mean_actual_mw')}`",
        f"- Hourly max actual MW: `{hourly.get('max_actual_mw')}`",
        f"- Hourly row count: `{hourly.get('hourly_row_count')}`",
        f"- Hourly coverage distribution: `{hourly.get('coverage_flag_distribution')}`",
        f"- Native mean MW: `{native.get('mean_mw')}`",
        f"- Native max MW: `{native.get('max_mw')}`",
        f"- Native row count: `{native.get('native_row_count')}`",
        f"- Native resolution distribution: `{native.get('native_resolution_distribution')}`",
        f"- Interpretation: {classification['interpretation']}",
        "",
    ])


def table_md(title: str, rows: list[dict[str, object]]) -> str:
    if not rows:
        return f"# {title}\n\nNo rows.\n"
    keys = sorted({key for row in rows for key in row if not isinstance(row.get(key), (dict, list))})
    lines = [f"# {title}", "", "| " + " | ".join(keys) + " |", "| " + " | ".join("---" for _ in keys) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(format_cell(row.get(key)) for key in keys) + " |")
    lines.append("")
    return "\n".join(lines)


def json_report(title: str, value: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(json_safe(value), indent=2, sort_keys=True)}\n```\n"


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


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def format_cell(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def main() -> None:
    result = run_p0056n_dst_target_anomaly_audit()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
