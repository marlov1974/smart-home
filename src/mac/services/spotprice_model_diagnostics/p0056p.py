"""P0056P LABB SE2 ENTSO-E source verification for 2026-03-28."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time as dt_time, timedelta, timezone
import json
import math
from pathlib import Path
import sqlite3
import time
import urllib.error
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0052a


PACKAGE_ID = "P0056P"
LABEL = "LABB"
SOURCE_SYSTEM = "ENTSO-E"
SOURCE_MEASURE = "actual_total_load"
AREA_SCOPE = "bidding_zone_internal_consumption_or_load"
NATIVE_TABLE = "area_consumption_native_v1"
HOURLY_TABLE = "area_consumption_hourly_v1"
REFERENCE_HOURLY_TABLE = "entsoe_consumption_area_hourly_v1"
DEFAULT_EVIDENCE_DIR = Path("requirements/package-runs/P0056P")
DEFAULT_AREA = "SE2"
DEFAULT_START_LOCAL_DATE = date(2026, 3, 27)
DEFAULT_END_LOCAL_DATE = date(2026, 3, 30)
ANOMALY_DATE = date(2026, 3, 28)
STOCKHOLM = ZoneInfo("Europe/Stockholm")
HOURLY_TOLERANCE_MW = 0.001
SPIKE_THRESHOLD_MW = 7000.0

AREA_EIC = {
    "SE1": "10Y1001A1001A44P",
    "SE2": "10Y1001A1001A45N",
    "SE3": "10Y1001A1001A46L",
    "SE4": "10Y1001A1001A47J",
    "FI": "10YFI-1--------U",
    "DK1": "10YDK-1--------W",
    "DK2": "10YDK-2--------M",
    "NO1": "10YNO-1--------2",
    "NO2": "10YNO-2--------T",
    "NO3": "10YNO-3--------J",
    "NO4": "10YNO-4--------9",
    "LT": "10YLT-1001A0008Q",
    "PL": "10YPL-AREA-----S",
    "DE_LU": "10Y1001A1001A82H",
}


@dataclass(frozen=True)
class P0056PResult:
    status: str
    classification: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0056p_source_verification(
    *,
    area: str = DEFAULT_AREA,
    start_local_date: date = DEFAULT_START_LOCAL_DATE,
    end_local_date: date = DEFAULT_END_LOCAL_DATE,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = DEFAULT_EVIDENCE_DIR,
    fresh_fetch: bool = True,
) -> P0056PResult:
    started = time.monotonic()
    area = area.upper()
    if area not in AREA_EIC:
        raise ValueError(f"Unsupported area: {area}")
    local_dates = local_dates_inclusive(start_local_date, end_local_date)
    start_utc, end_utc = utc_bounds_for_local_dates(start_local_date, end_local_date)
    fresh_rows: list[dict[str, object]] = []
    fetch_meta: dict[str, object]
    token_meta: dict[str, object] = {"token_source": "not_used", "secret_checked": False, "secret_safe": False}

    if fresh_fetch:
        try:
            token_source = p0052a.load_entsoe_token()
            secret_safety = p0052a.verify_secret_safety(token_source)
            token_meta = sanitized_secret_safety(token_source.source_label, secret_safety)
            if not secret_safety["secret_safe"]:
                raise RuntimeError("ENTSO-E secret safety check failed")
            fresh_rows, fetch_meta = load_fresh_entsoe_actual_load_rows(token_source.token, area, start_utc, end_utc, local_dates)
        except (RuntimeError, urllib.error.URLError, ET.ParseError) as exc:
            fetch_meta = {
                "status": "fetch_failed",
                "reason": str(type(exc).__name__)[:120],
                "row_count": 0,
                "native_resolution_minutes": [],
            }
    else:
        fetch_meta = {
            "status": "skipped",
            "reason": "fresh_fetch_disabled",
            "row_count": 0,
            "native_resolution_minutes": [],
        }

    feature_path = Path(feature_db).expanduser()
    with sqlite3.connect(feature_path) as conn:
        conn.row_factory = sqlite3.Row
        local_native_rows = load_local_native_area_rows(conn, area, start_utc, end_utc, local_dates)
        local_hourly_rows = load_local_hourly_area_rows(conn, area, start_utc, end_utc, local_dates)
        reference_hourly_rows = load_reference_hourly_area_rows(conn, area, start_utc, end_utc, local_dates)

    fresh_hourly_rows = aggregate_native_to_hourly_for_audit(fresh_rows)
    fresh_summary, fresh_native_comparison = summarize_native_rows(fresh_rows, local_dates, "fresh_entsoe")
    local_native_summary, local_native_day_rows = summarize_native_rows(local_native_rows, local_dates, "local_native")
    native_comparison_rows = compare_native_rows(fresh_native_comparison, local_native_day_rows, ANOMALY_DATE)
    hourly_summary, hourly_comparison_rows = compare_hourly_rows(fresh_hourly_rows, local_hourly_rows, local_dates)
    reference_summary, _reference_comparison_rows = compare_hourly_rows(fresh_hourly_rows, reference_hourly_rows, local_dates)
    decision_payload = classify_2026_03_28_anomaly(area, fresh_summary, local_native_summary, hourly_summary)
    status = "PASS" if decision_payload["classification"] in {"source_observed_anomaly", "verified_local_bug"} else "WARN"

    summary: dict[str, object] = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "area": area,
        "eic": AREA_EIC[area],
        "source_window": {
            "start_local_date": start_local_date.isoformat(),
            "end_local_date": end_local_date.isoformat(),
            "start_utc": p0052.format_utc(start_utc),
            "end_utc": p0052.format_utc(end_utc),
        },
        "request_contract": source_contract(area, start_utc, end_utc),
        "token_safety": token_meta,
        "fresh_fetch": fetch_meta,
        "fresh_native_summary": fresh_summary,
        "local_native_summary": local_native_summary,
        "hourly_aggregation_summary": hourly_summary,
        "reference_hourly_summary": reference_summary,
        "decision": decision_payload,
        "row_counts": {
            "fresh_native_rows": len(fresh_rows),
            "fresh_hourly_rows": len(fresh_hourly_rows),
            "local_native_rows": len(local_native_rows),
            "local_hourly_rows": len(local_hourly_rows),
            "reference_hourly_rows": len(reference_hourly_rows),
            "native_comparison_rows": len(native_comparison_rows),
            "hourly_comparison_rows": len(hourly_comparison_rows),
        },
        "no_model_training": True,
        "no_runtime_change": True,
        "no_devices": True,
        "no_home_assistant": True,
        "no_flow_exchange_a61_capacity_features": True,
        "no_price_features": True,
        "raw_xml_committed": False,
        "token_included_in_evidence": False,
    }
    evidence = write_p0056p_evidence(Path(evidence_dir), summary, native_comparison_rows, hourly_comparison_rows)
    return P0056PResult(status, str(decision_payload["classification"]), summary["row_counts"], evidence)  # type: ignore[arg-type]


def build_p0056p_entsoe_request(area: str, start_utc: datetime, end_utc: datetime) -> tuple[dict[str, str], dict[str, str]]:
    area = area.upper()
    if area not in AREA_EIC:
        raise ValueError(f"Unsupported area: {area}")
    eic = AREA_EIC[area]
    params = {
        "documentType": "A65",
        "processType": "A16",
        "outBiddingZone_Domain": eic,
        "periodStart": p0052a.format_entsoe_time(start_utc),
        "periodEnd": p0052a.format_entsoe_time(end_utc),
    }
    safe = {
        "document_type": "A65",
        "process_type": "A16",
        "area": area,
        "source_area_code": eic,
        "out_bidding_zone_domain": eic,
        "source_system": SOURCE_SYSTEM,
        "source_measure": SOURCE_MEASURE,
        "area_scope": AREA_SCOPE,
        "period_start": p0052.format_utc(start_utc),
        "period_end": p0052.format_utc(end_utc),
    }
    return params, safe


def load_fresh_entsoe_actual_load_rows(
    token: str,
    area: str,
    start_utc: datetime,
    end_utc: datetime,
    local_dates: list[date],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    params, safe = build_p0056p_entsoe_request(area, start_utc, end_utc)
    xml_bytes, status = p0052a.fetch_entsoe_document(token, params, timeout=45.0)
    rows, response = parse_entsoe_actual_load_xml(xml_bytes, safe)
    local_set = {item.isoformat() for item in local_dates}
    filtered = [row for row in rows if str(row.get("local_date", "")) in local_set]
    resolutions = sorted({int(row["native_resolution_minutes"]) for row in filtered})
    return filtered, {
        **safe,
        "status": status,
        **response,
        "row_count": len(filtered),
        "native_resolution_minutes": resolutions,
    }


def parse_entsoe_actual_load_xml(xml_bytes: bytes, request_meta: dict[str, str]) -> tuple[list[dict[str, object]], dict[str, object]]:
    root = ET.fromstring(xml_bytes)
    root_tag = p0052a.strip_ns(root.tag)
    if root_tag == "Acknowledgement_MarketDocument":
        reason = p0052a.text_or_empty(root.find(".//{*}text"))
        return [], {"root": root_tag, "reason": reason[:180], "timeseries": 0, "points": 0}
    rows: list[dict[str, object]] = []
    for series in root.findall(".//{*}TimeSeries"):
        unit = p0052a.text_or_empty(series.find(".//{*}quantity_Measure_Unit.name")) or "MAW"
        source_area_code = (
            p0052a.text_or_empty(series.find(".//{*}outBiddingZone_Domain.mRID"))
            or p0052a.text_or_empty(series.find(".//{*}out_Domain.mRID"))
            or request_meta["source_area_code"]
        )
        for period in series.findall(".//{*}Period"):
            rows.extend(parse_actual_load_period(period, request_meta, source_area_code, unit))
    return rows, {"root": root_tag, "reason": "", "timeseries": len(root.findall(".//{*}TimeSeries")), "points": len(root.findall(".//{*}Point"))}


def parse_actual_load_period(period: ET.Element, request_meta: dict[str, str], source_area_code: str, unit: str) -> list[dict[str, object]]:
    start_text = p0052a.text_or_empty(period.find(".//{*}timeInterval/{*}start"))
    end_text = p0052a.text_or_empty(period.find(".//{*}timeInterval/{*}end"))
    resolution = p0052a.text_or_empty(period.find(".//{*}resolution"))
    period_start = p0052.parse_utc(start_text)
    period_end = p0052.parse_utc(end_text) if end_text else None
    step = p0052a.resolution_to_timedelta(resolution, period_start=period_start, period_end=period_end)
    rows = []
    for point in period.findall(".//{*}Point"):
        position = int(p0052a.text_or_empty(point.find(".//{*}position")) or "1")
        quantity = p0052a.text_or_empty(point.find(".//{*}quantity"))
        if not quantity:
            continue
        interval_start = period_start + (position - 1) * step
        interval_end = interval_start + step
        local = interval_start.astimezone(STOCKHOLM)
        rows.append({
            "area_code": request_meta["area"],
            "interval_start_utc": p0052.format_utc(interval_start),
            "interval_end_utc": p0052.format_utc(interval_end),
            "value": float(quantity),
            "unit": normalize_mw_unit(unit),
            "value_kind": SOURCE_MEASURE,
            "native_resolution_minutes": int(step.total_seconds() // 60),
            "source_system": SOURCE_SYSTEM,
            "source_area_code": source_area_code,
            "document_type": request_meta["document_type"],
            "process_type": request_meta["process_type"],
            "generated_by_package": PACKAGE_ID,
            "local_date": local.date().isoformat(),
            "local_hour": local.hour,
            "local_timestamp": local.isoformat(),
        })
    return rows


def load_local_native_area_rows(
    conn: sqlite3.Connection,
    area: str,
    start_utc: datetime,
    end_utc: datetime,
    local_dates: list[date],
) -> list[dict[str, object]]:
    local_set = {item.isoformat() for item in local_dates}
    rows = []
    for row in conn.execute(
        f"""
        SELECT area_code, interval_start_utc, interval_end_utc, value, unit, value_kind,
               native_resolution_minutes, source_system, source_area_code, document_type,
               process_type, generated_by_package
        FROM {NATIVE_TABLE}
        WHERE generated_by_package='P0056A'
          AND area_code=?
          AND interval_start_utc >= ?
          AND interval_start_utc < ?
        ORDER BY interval_start_utc
        """,
        (area, p0052.format_utc(start_utc), p0052.format_utc(end_utc)),
    ):
        item = dict(row)
        local = p0052.parse_utc(str(item["interval_start_utc"])).astimezone(STOCKHOLM)
        if local.date().isoformat() in local_set:
            item["local_date"] = local.date().isoformat()
            item["local_hour"] = local.hour
            item["local_timestamp"] = local.isoformat()
            rows.append(item)
    return rows


def load_local_hourly_area_rows(
    conn: sqlite3.Connection,
    area: str,
    start_utc: datetime,
    end_utc: datetime,
    local_dates: list[date],
) -> list[dict[str, object]]:
    local_set = {item.isoformat() for item in local_dates}
    rows = []
    for row in conn.execute(
        f"""
        SELECT timestamp_utc, area_code, consumption_mw, source_system, aggregation_method,
               native_resolution_mix, coverage_flag, input_row_count, generated_by_package
        FROM {HOURLY_TABLE}
        WHERE generated_by_package='P0056A'
          AND area_code=?
          AND timestamp_utc >= ?
          AND timestamp_utc < ?
        ORDER BY timestamp_utc
        """,
        (area, p0052.format_utc(start_utc), p0052.format_utc(end_utc)),
    ):
        item = dict(row)
        local = p0052.parse_utc(str(item["timestamp_utc"])).astimezone(STOCKHOLM)
        if local.date().isoformat() in local_set:
            item["local_date"] = local.date().isoformat()
            item["local_hour"] = local.hour
            item["local_timestamp"] = local.isoformat()
            rows.append(item)
    return rows


def load_reference_hourly_area_rows(
    conn: sqlite3.Connection,
    area: str,
    start_utc: datetime,
    end_utc: datetime,
    local_dates: list[date],
) -> list[dict[str, object]]:
    if not p0052.table_exists(conn, REFERENCE_HOURLY_TABLE):
        return []
    local_set = {item.isoformat() for item in local_dates}
    rows = []
    for row in conn.execute(
        f"""
        SELECT timestamp_utc, area AS area_code, consumption_mw, source_system,
               resolution AS native_resolution_mix, quality_flag AS coverage_flag,
               0 AS input_row_count, package_id AS generated_by_package
        FROM {REFERENCE_HOURLY_TABLE}
        WHERE area=?
          AND timestamp_utc >= ?
          AND timestamp_utc < ?
        ORDER BY timestamp_utc
        """,
        (area, p0052.format_utc(start_utc), p0052.format_utc(end_utc)),
    ):
        item = dict(row)
        local = p0052.parse_utc(str(item["timestamp_utc"])).astimezone(STOCKHOLM)
        if local.date().isoformat() in local_set:
            item["local_date"] = local.date().isoformat()
            item["local_hour"] = local.hour
            item["local_timestamp"] = local.isoformat()
            rows.append(item)
    return rows


def aggregate_native_to_hourly_for_audit(native_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for row in native_rows:
        value = float(row["value"])
        if not math.isfinite(value):
            continue
        start = p0052.parse_utc(str(row["interval_start_utc"]))
        end = p0052.parse_utc(str(row["interval_end_utc"]))
        current = start.replace(minute=0, second=0, microsecond=0)
        while current < end:
            hour_end = current + timedelta(hours=1)
            overlap_start = max(start, current)
            overlap_end = min(end, hour_end)
            seconds = max(0.0, (overlap_end - overlap_start).total_seconds())
            if seconds > 0:
                key = (p0052.format_utc(current), str(row["area_code"]))
                target = grouped.setdefault(key, {"timestamp_utc": key[0], "area_code": key[1], "weighted_mw_seconds": 0.0, "covered_seconds": 0.0, "input_row_count": 0})
                target["weighted_mw_seconds"] = float(target["weighted_mw_seconds"]) + value * seconds
                target["covered_seconds"] = float(target["covered_seconds"]) + seconds
                target["input_row_count"] = int(target["input_row_count"]) + 1
            current = hour_end
    out = []
    for _key, data in sorted(grouped.items()):
        covered = float(data["covered_seconds"])
        local = p0052.parse_utc(str(data["timestamp_utc"])).astimezone(STOCKHOLM)
        out.append({
            "timestamp_utc": data["timestamp_utc"],
            "area_code": data["area_code"],
            "consumption_mw": float(data["weighted_mw_seconds"]) / covered if covered else None,
            "input_row_count": data["input_row_count"],
            "coverage_flag": "ok" if abs(covered - 3600.0) <= 1.0 else "partial_hour",
            "covered_seconds": covered,
            "local_date": local.date().isoformat(),
            "local_hour": local.hour,
            "local_timestamp": local.isoformat(),
        })
    return out


def summarize_native_rows(rows: list[dict[str, object]], local_dates: list[date], source_label: str) -> tuple[dict[str, object], list[dict[str, object]]]:
    by_date: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_date[str(row.get("local_date", ""))].append(row)
    values = [float(row["value"]) for row in rows if is_finite(row.get("value"))]
    all_starts = [str(row["interval_start_utc"]) for row in rows]
    by_date_summary = {}
    compact_rows: list[dict[str, object]] = []
    for local_day in local_dates:
        day_key = local_day.isoformat()
        day_rows = by_date.get(day_key, [])
        resolutions = [int(row["native_resolution_minutes"]) for row in day_rows if row.get("native_resolution_minutes") is not None]
        resolution = most_common_int(resolutions) or 15
        expected = expected_interval_starts(local_day, resolution)
        observed = [str(row["interval_start_utc"]) for row in day_rows]
        observed_set = set(observed)
        duplicates = sorted(timestamp for timestamp, count in Counter(observed).items() if count > 1)
        missing = [timestamp for timestamp in expected if timestamp not in observed_set]
        day_values = [float(row["value"]) for row in day_rows if is_finite(row.get("value"))]
        by_date_summary[day_key] = {
            "expected_rows": len(expected),
            "observed_rows": len(day_rows),
            "missing_rows": len(missing),
            "missing_timestamps": missing[:24],
            "duplicate_rows": len(duplicates),
            "duplicate_timestamps": duplicates[:24],
            "native_resolution_minutes": resolution,
            **value_stats(day_values),
        }
        for row in day_rows:
            if day_key == ANOMALY_DATE.isoformat():
                compact_rows.append({
                    "source": source_label,
                    "interval_start_utc": row["interval_start_utc"],
                    "interval_end_utc": row["interval_end_utc"],
                    "local_timestamp": row.get("local_timestamp", ""),
                    "value_mw": row["value"],
                    "native_resolution_minutes": row["native_resolution_minutes"],
                })
    return {
        "source": source_label,
        "row_count": len(rows),
        "unique_interval_start_count": len(set(all_starts)),
        "duplicate_interval_start_count": len(all_starts) - len(set(all_starts)),
        "native_resolution_minutes": sorted(set(int(row["native_resolution_minutes"]) for row in rows)) if rows else [],
        "has_7279_or_equivalent_spike": bool(values and max(values) >= SPIKE_THRESHOLD_MW),
        **value_stats(values),
        "by_local_date": by_date_summary,
    }, compact_rows


def compare_native_rows(fresh_rows: list[dict[str, object]], local_rows: list[dict[str, object]], local_day: date) -> list[dict[str, object]]:
    day_key = local_day.isoformat()
    fresh = {str(row["interval_start_utc"]): row for row in fresh_rows if str(row.get("source")) == "fresh_entsoe"}
    local = {str(row["interval_start_utc"]): row for row in local_rows if str(row.get("source")) == "local_native"}
    keys = sorted(set(fresh) | set(local))
    out = []
    for key in keys:
        f_row = fresh.get(key)
        l_row = local.get(key)
        local_ts = (f_row or l_row or {}).get("local_timestamp", "")
        if local_ts and not str(local_ts).startswith(day_key):
            continue
        fresh_value = float(f_row["value_mw"]) if f_row else None
        local_value = float(l_row["value_mw"]) if l_row else None
        out.append({
            "interval_start_utc": key,
            "local_timestamp": local_ts,
            "fresh_mw": fresh_value,
            "local_native_mw": local_value,
            "delta_mw": round(local_value - fresh_value, 6) if fresh_value is not None and local_value is not None else None,
            "fresh_present": f_row is not None,
            "local_present": l_row is not None,
        })
    return out


def compare_hourly_rows(fresh_hourly: list[dict[str, object]], local_hourly: list[dict[str, object]], local_dates: list[date]) -> tuple[dict[str, object], list[dict[str, object]]]:
    local_date_set = {item.isoformat() for item in local_dates}
    fresh = {str(row["timestamp_utc"]): row for row in fresh_hourly if str(row.get("local_date")) in local_date_set}
    local = {str(row["timestamp_utc"]): row for row in local_hourly if str(row.get("local_date")) in local_date_set}
    rows = []
    diffs = []
    partial_hours = []
    fresh_values = []
    local_values = []
    for timestamp in sorted(set(fresh) | set(local)):
        f_row = fresh.get(timestamp)
        l_row = local.get(timestamp)
        local_ts = (f_row or l_row or {}).get("local_timestamp", "")
        fresh_value = float(f_row["consumption_mw"]) if f_row and f_row.get("consumption_mw") is not None else None
        local_value = float(l_row["consumption_mw"]) if l_row and l_row.get("consumption_mw") is not None else None
        delta = None
        beyond = False
        if fresh_value is not None and local_value is not None:
            delta = local_value - fresh_value
            diffs.append(abs(delta))
            beyond = abs(delta) > HOURLY_TOLERANCE_MW
        if fresh_value is not None:
            fresh_values.append(fresh_value)
        if local_value is not None:
            local_values.append(local_value)
        if l_row and str(l_row.get("coverage_flag", "")) != "ok":
            partial_hours.append(timestamp)
        rows.append({
            "timestamp_utc": timestamp,
            "local_timestamp": local_ts,
            "fresh_aggregated_mw": fresh_value,
            "local_hourly_mw": local_value,
            "delta_mw": round(delta, 6) if delta is not None else None,
            "beyond_tolerance": beyond,
            "fresh_input_row_count": f_row.get("input_row_count") if f_row else None,
            "local_input_row_count": l_row.get("input_row_count") if l_row else None,
            "local_coverage_flag": l_row.get("coverage_flag") if l_row else None,
        })
    return {
        "fresh_hourly_rows": len(fresh),
        "local_hourly_rows": len(local),
        "fresh_max_mw": max(fresh_values) if fresh_values else None,
        "local_max_mw": max(local_values) if local_values else None,
        "fresh_has_7279_or_equivalent_spike": bool(fresh_values and max(fresh_values) >= SPIKE_THRESHOLD_MW),
        "local_has_7279_or_equivalent_spike": bool(local_values and max(local_values) >= SPIKE_THRESHOLD_MW),
        "comparable_rows": len(diffs),
        "max_abs_diff_mw": max(diffs) if diffs else None,
        "mean_abs_diff_mw": sum(diffs) / len(diffs) if diffs else None,
        "rows_beyond_tolerance": sum(1 for row in rows if row["beyond_tolerance"]),
        "hourly_aggregation_ok": bool(diffs) and max(diffs) <= HOURLY_TOLERANCE_MW,
        "partial_hour_rows": len(partial_hours),
        "partial_hour_timestamps": partial_hours[:24],
    }, rows


def classify_2026_03_28_anomaly(
    area: str,
    fresh_summary: dict[str, object],
    local_native_summary: dict[str, object],
    hourly_summary: dict[str, object],
) -> dict[str, object]:
    fresh_available = int(fresh_summary.get("row_count", 0)) > 0
    fresh_has_spike = bool(fresh_summary.get("has_7279_or_equivalent_spike"))
    local_native_has_spike = bool(local_native_summary.get("has_7279_or_equivalent_spike"))
    local_hourly_has_spike = local_day_hourly_has_spike(hourly_summary)
    hourly_ok = bool(hourly_summary.get("hourly_aggregation_ok"))
    if not fresh_available:
        classification = "unresolved_exclude_from_selection"
        action = "exclude_until_source_verified"
    elif not fresh_has_spike and (local_native_has_spike or local_hourly_has_spike):
        classification = "verified_local_bug"
        action = "fix_local_ingestion_before_modeling"
    elif fresh_has_spike and local_native_has_spike:
        classification = "source_observed_anomaly"
        action = "exclude_until_independently_verified"
    elif fresh_has_spike and not local_native_has_spike:
        classification = "verified_local_bug"
        action = "fix_local_ingestion_before_modeling"
    else:
        classification = "unresolved_exclude_from_selection"
        action = "exclude_until_source_verified"
    return {
        "area": area,
        "delivery_date_local": ANOMALY_DATE.isoformat(),
        "classification": classification,
        "fresh_entsoe_has_spike": fresh_has_spike,
        "local_native_has_spike": local_native_has_spike,
        "local_hourly_has_spike": local_hourly_has_spike,
        "native_rows_expected": native_expected_for_anomaly(local_native_summary),
        "native_rows_observed": native_observed_for_anomaly(local_native_summary),
        "hourly_aggregation_ok": hourly_ok,
        "model_selection_action": action,
        "recommended_next_package": next_package_recommendation_for_classification(classification),
    }


def local_day_hourly_has_spike(hourly_summary: dict[str, object]) -> bool:
    return bool(hourly_summary.get("local_has_7279_or_equivalent_spike"))


def native_expected_for_anomaly(summary: dict[str, object]) -> int | None:
    by_date = summary.get("by_local_date", {})
    if isinstance(by_date, dict):
        day = by_date.get(ANOMALY_DATE.isoformat(), {})
        if isinstance(day, dict):
            return int(day.get("expected_rows", 0))
    return None


def native_observed_for_anomaly(summary: dict[str, object]) -> int | None:
    by_date = summary.get("by_local_date", {})
    if isinstance(by_date, dict):
        day = by_date.get(ANOMALY_DATE.isoformat(), {})
        if isinstance(day, dict):
            return int(day.get("observed_rows", 0))
    return None


def next_package_recommendation_for_classification(classification: str) -> str:
    if classification == "verified_local_bug":
        return "P0056Q: fix or quarantine the SE2 local consumption ingestion/aggregation issue before model-selection reruns."
    if classification == "source_observed_anomaly":
        return "P0056Q: independently verify the 2026-03-28 SE2 ENTSO-E source-observed anomaly or exclude it from model selection."
    return "P0056Q: obtain an independent/original source path for SE2 2026-03-28 before model-selection use."


def write_p0056p_evidence(
    evidence_dir: Path,
    summary: dict[str, object],
    native_rows: list[dict[str, object]],
    hourly_rows: list[dict[str, object]],
) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}
    paths["source-contract.md"] = write_text(evidence_dir / "source-contract.md", source_contract_md(summary))
    paths["fresh-entsoe-fetch.md"] = write_text(evidence_dir / "fresh-entsoe-fetch.md", fresh_fetch_md(summary))
    paths["local-native-comparison.md"] = write_text(evidence_dir / "local-native-comparison.md", local_native_md(summary))
    paths["hourly-aggregation-comparison.md"] = write_text(evidence_dir / "hourly-aggregation-comparison.md", hourly_md(summary))
    paths["decision.md"] = write_text(evidence_dir / "decision.md", "# P0056P Decision\n\n```json\n" + json.dumps(summary["decision"], indent=2, sort_keys=True) + "\n```\n")
    paths["what-we-learned.md"] = write_text(evidence_dir / "what-we-learned.md", what_we_learned_md(summary))
    paths["next-package-recommendation.md"] = write_text(evidence_dir / "next-package-recommendation.md", next_package_md(summary))
    paths["metrics-summary.json"] = write_text(evidence_dir / "metrics-summary.json", json.dumps(summary, indent=2, sort_keys=True) + "\n")
    paths["se2-2026-03-28-native-comparison.csv"] = write_csv(evidence_dir / "se2-2026-03-28-native-comparison.csv", native_rows)
    paths["se2-2026-03-28-hourly-comparison.csv"] = write_csv(evidence_dir / "se2-2026-03-28-hourly-comparison.csv", hourly_rows_for_day(hourly_rows, ANOMALY_DATE))
    paths["labb-label.md"] = write_text(evidence_dir / "labb-label.md", "# P0056P LABB Label\n\nP0056P is LABB-only source verification. It is not G2-KANDIDAT and performs no production/runtime/model action.\n")
    paths["CHANGELOG.md"] = write_text(evidence_dir / "CHANGELOG.md", changelog_md(summary))
    return {name: str(path) for name, path in paths.items()}


def source_contract(area: str, start_utc: datetime, end_utc: datetime) -> dict[str, object]:
    _params, safe = build_p0056p_entsoe_request(area, start_utc, end_utc)
    return {
        **safe,
        "selected_contract": "ENTSO-E Actual Total Load / Total Load - Actual by bidding zone",
        "forbidden_documents_used": [],
        "no_a09_a11_a61_flow_exchange_capacity": True,
    }


def source_contract_md(summary: dict[str, object]) -> str:
    return "# P0056P Source Contract\n\n```json\n" + json.dumps(summary["request_contract"], indent=2, sort_keys=True) + "\n```\n"


def fresh_fetch_md(summary: dict[str, object]) -> str:
    data = {
        "fresh_fetch": summary["fresh_fetch"],
        "token_safety": summary["token_safety"],
        "fresh_native_summary": summary["fresh_native_summary"],
        "no_token_leak_confirmation": not contains_token_like_text(json.dumps(summary, sort_keys=True)),
    }
    return "# P0056P Fresh ENTSO-E Fetch\n\n```json\n" + json.dumps(data, indent=2, sort_keys=True) + "\n```\n"


def local_native_md(summary: dict[str, object]) -> str:
    data = {
        "local_native_table": NATIVE_TABLE,
        "local_native_summary": summary["local_native_summary"],
    }
    return "# P0056P Local Native Comparison\n\n```json\n" + json.dumps(data, indent=2, sort_keys=True) + "\n```\n"


def hourly_md(summary: dict[str, object]) -> str:
    data = {
        "local_hourly_table": HOURLY_TABLE,
        "reference_hourly_table": REFERENCE_HOURLY_TABLE,
        "hourly_aggregation_summary": summary["hourly_aggregation_summary"],
        "reference_hourly_summary": summary["reference_hourly_summary"],
    }
    return "# P0056P Hourly Aggregation Comparison\n\n```json\n" + json.dumps(data, indent=2, sort_keys=True) + "\n```\n"


def what_we_learned_md(summary: dict[str, object]) -> str:
    decision = summary["decision"]
    return (
        "# P0056P What We Learned\n\n"
        f"- Classification: `{decision['classification']}`.\n"
        f"- Fresh ENTSO-E has spike: `{decision['fresh_entsoe_has_spike']}`.\n"
        f"- Local native has spike: `{decision['local_native_has_spike']}`.\n"
        f"- Hourly aggregation OK: `{decision['hourly_aggregation_ok']}`.\n"
        f"- Model-selection action: `{decision['model_selection_action']}`.\n"
        "- This package does not independently confirm physical reality; it only compares ENTSO-E source and local ingestion layers.\n"
    )


def next_package_md(summary: dict[str, object]) -> str:
    decision = summary["decision"]
    return f"# P0056P Next Package Recommendation\n\n{decision['recommended_next_package']}\n"


def changelog_md(summary: dict[str, object]) -> str:
    decision = summary["decision"]
    return (
        "# P0056P Changelog\n\n"
        f"- Status: `{summary['status']}`.\n"
        f"- Classification: `{decision['classification']}`.\n"
        f"- Model-selection action: `{decision['model_selection_action']}`.\n"
        f"- Fresh ENTSO-E has spike: `{decision['fresh_entsoe_has_spike']}`.\n"
        f"- Local native rows for 2026-03-28: `{decision['native_rows_observed']}` observed / `{decision['native_rows_expected']}` expected.\n"
        f"- Hourly aggregation OK: `{decision['hourly_aggregation_ok']}`.\n"
        "- No model training, runtime changes, devices, Shelly, Home Assistant, price/flow/A61/capacity features, raw XML dump or token leak.\n"
    )


def local_dates_inclusive(start_local_date: date, end_local_date: date) -> list[date]:
    if end_local_date < start_local_date:
        raise ValueError("end_local_date must be >= start_local_date")
    out = []
    current = start_local_date
    while current <= end_local_date:
        out.append(current)
        current += timedelta(days=1)
    return out


def utc_bounds_for_local_dates(start_local_date: date, end_local_date: date) -> tuple[datetime, datetime]:
    start_local = datetime.combine(start_local_date, dt_time(0, 0), tzinfo=STOCKHOLM)
    end_local = datetime.combine(end_local_date + timedelta(days=1), dt_time(0, 0), tzinfo=STOCKHOLM)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def expected_interval_starts(local_day: date, resolution_minutes: int) -> list[str]:
    start_local = datetime.combine(local_day, dt_time(0, 0), tzinfo=STOCKHOLM)
    end_local = datetime.combine(local_day + timedelta(days=1), dt_time(0, 0), tzinfo=STOCKHOLM)
    current = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)
    step = timedelta(minutes=resolution_minutes)
    out = []
    while current < end_utc:
        out.append(p0052.format_utc(current))
        current += step
    return out


def most_common_int(values: list[int]) -> int | None:
    if not values:
        return None
    return Counter(values).most_common(1)[0][0]


def value_stats(values: list[float]) -> dict[str, object]:
    if not values:
        return {"min_mw": None, "max_mw": None, "mean_mw": None}
    return {
        "min_mw": min(values),
        "max_mw": max(values),
        "mean_mw": sum(values) / len(values),
    }


def normalize_mw_unit(unit: str) -> str:
    return "MW" if unit in {"MAW", "MW"} else unit


def is_finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def sanitized_secret_safety(source_label: str, secret_safety: dict[str, object]) -> dict[str, object]:
    return {
        "token_source": source_label,
        "secret_checked": bool(secret_safety.get("secret_checked")),
        "secret_safe": bool(secret_safety.get("secret_safe")),
        "secret_gitignored": secret_safety.get("secret_gitignored"),
        "secret_location_class": secret_safety.get("secret_location_class", "environment"),
    }


def contains_token_like_text(text: str) -> bool:
    lowered = text.lower()
    return "securitytoken" in lowered or "entsoe_security_token" in lowered


def hourly_rows_for_day(rows: list[dict[str, object]], local_day: date) -> list[dict[str, object]]:
    prefix = local_day.isoformat()
    return [row for row in rows if str(row.get("local_timestamp", "")).startswith(prefix)]


def write_text(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def write_csv(path: Path, rows: list[dict[str, object]]) -> Path:
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    columns = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="P0056P SE2 ENTSO-E source verification")
    parser.add_argument("--area", default=DEFAULT_AREA)
    parser.add_argument("--start-local-date", default=DEFAULT_START_LOCAL_DATE.isoformat())
    parser.add_argument("--end-local-date", default=DEFAULT_END_LOCAL_DATE.isoformat())
    parser.add_argument("--feature-db", default=str(DEFAULT_FEATURE_DB))
    parser.add_argument("--write-evidence", default=str(DEFAULT_EVIDENCE_DIR))
    parser.add_argument("--skip-fresh-fetch", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_p0056p_source_verification(
        area=args.area,
        start_local_date=date.fromisoformat(args.start_local_date),
        end_local_date=date.fromisoformat(args.end_local_date),
        feature_db=Path(args.feature_db),
        evidence_dir=Path(args.write_evidence),
        fresh_fetch=not args.skip_fresh_fetch,
    )
    print(json.dumps({"status": result.status, "classification": result.classification, "row_counts": result.row_counts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
