"""P0054P2 LABB ENTSO-E actual load ingestion for SE1-SE4."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import csv
import json
import math
import sqlite3
import time
import urllib.error
import xml.etree.ElementTree as ET

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0052a
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile


PACKAGE_ID = "P0054P2"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054P2")
TARGET_TABLE = "entsoe_consumption_area_hourly_v1"
SOURCE_SYSTEM = "ENTSO-E"
SOURCE_MEASURE = "actual_total_load"
AREA_SCOPE = "bidding_zone_internal_consumption_or_load"
START_UTC = datetime(2022, 6, 1, tzinfo=timezone.utc)
HOLDOUT_START_UTC = datetime(2025, 6, 1, tzinfo=timezone.utc)
AREAS = ("SE1", "SE2", "SE3", "SE4")
FLOW_EXPORT_FILENAME = "GUI_NET_CROSS_BORDER_PHYSICAL_FLOWS_202512312300-202612312300.csv"


@dataclass(frozen=True)
class P0054P2Result:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054p2_ingestion(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
    start: datetime = START_UTC,
    end: datetime | None = None,
) -> P0054P2Result:
    started = time.monotonic()
    feature_db = Path(feature_db).expanduser()
    evidence_dir = Path(evidence_dir)
    end_dt = end or latest_request_end_utc()
    token_source = p0052a.load_entsoe_token()
    secret_safety = p0052a.verify_secret_safety(token_source)
    if not secret_safety["secret_safe"]:
        raise RuntimeError("P0054P2 secret safety check failed")

    raw_rows, responses = fetch_actual_load_rows(token_source.token, start, end_dt)
    hourly_rows = aggregate_hourly_load(raw_rows)
    with sqlite3.connect(feature_db) as conn:
        conn.row_factory = sqlite3.Row
        persist_actual_load_rows(conn, hourly_rows)
        coverage = coverage_by_area(conn, start, end_dt)
        volume = volume_sanity_by_area_season(conn)
        se3_check = se3_volume_check(volume)
        comparison = old_source_comparison(conn)
        quality = data_quality_review(conn, coverage, se3_check)

    source_contract = actual_load_source_contract(responses)
    flow_file = classify_cross_border_flow_file()
    status = package_status(source_contract, coverage, se3_check, quality)
    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "request_range": {"start": p0052.format_utc(start), "end": p0052.format_utc(end_dt)},
        "row_counts": {"raw_rows": len(raw_rows), "hourly_rows": len(hourly_rows)},
        "secret_safety": secret_safety_without_path(secret_safety),
        "source_discovery": source_discovery(responses),
        "source_contract": source_contract,
        "area_code_mapping": area_code_mapping(),
        "table_schema": table_schema_contract(),
        "coverage_by_area": coverage,
        "volume_sanity_by_area_season": volume,
        "se3_volume_check": se3_check,
        "old_source_comparison": comparison,
        "cross_border_flow_file_classification": flow_file,
        "data_quality_review": quality,
        "downstream_contract": downstream_contract(),
        "impact_on_p0054k_through_p0054o": downstream_impact(),
        "what_we_learned": what_we_learned(status, comparison),
        "next_package_recommendation": next_package_recommendation(status),
        "no_api_beyond_entsoe_actual_load": True,
        "no_devices": True,
        "no_a61_utilization": True,
        "no_future_actual_price_leakage": True,
        "token_included_in_evidence": False,
        "raw_entsoe_exports_committed": False,
    }
    evidence = write_p0054p2_evidence(evidence_dir, summary)
    return P0054P2Result(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def latest_request_end_utc(now: datetime | None = None) -> datetime:
    current = now or datetime.now(timezone.utc)
    return current.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)


def yearly_chunks(start: datetime, end: datetime) -> list[tuple[datetime, datetime]]:
    chunks = []
    current = start
    while current < end:
        next_year = datetime(current.year + 1, 1, 1, tzinfo=timezone.utc)
        chunk_end = min(next_year, end)
        chunks.append((current, chunk_end))
        current = chunk_end
    return chunks


def build_actual_load_params(area: str, start: datetime, end: datetime) -> tuple[dict[str, str], dict[str, str]]:
    source_area_code = p0052a.DOMAINS[area]
    params = {
        "documentType": "A65",
        "processType": "A16",
        "outBiddingZone_Domain": source_area_code,
        "periodStart": p0052a.format_entsoe_time(start),
        "periodEnd": p0052a.format_entsoe_time(end),
    }
    safe = {
        "document_type": "A65",
        "process_type": "A16",
        "area": area,
        "source_area_code": source_area_code,
        "source_type": SOURCE_MEASURE,
        "area_scope": AREA_SCOPE,
        "usable_for_consumption_target": "true",
        "period_start": p0052.format_utc(start),
        "period_end": p0052.format_utc(end),
    }
    return params, safe


def fetch_actual_load_rows(token: str, start: datetime, end: datetime) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    raw_rows: list[dict[str, object]] = []
    responses: list[dict[str, object]] = []
    for area in AREAS:
        for chunk_start, chunk_end in yearly_chunks(start, end):
            params, safe = build_actual_load_params(area, chunk_start, chunk_end)
            try:
                xml_bytes, status = p0052a.fetch_entsoe_document(token, params, timeout=45.0)
            except urllib.error.URLError as exc:
                responses.append({**safe, "status": "url_error", "root": "", "reason": str(type(exc.reason).__name__)[:180], "timeseries": 0, "points": 0})
                continue
            observations, response = parse_actual_load_document(xml_bytes, safe)
            responses.append({**safe, "status": status, **response})
            raw_rows.extend(observations)
    return raw_rows, responses


def parse_actual_load_document(xml_bytes: bytes, request_meta: dict[str, str]) -> tuple[list[dict[str, object]], dict[str, object]]:
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
    return rows, {"root": root_tag, "reason": "", "timeseries": len(root.findall('.//{*}TimeSeries')), "points": len(root.findall('.//{*}Point'))}


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
        timestamp = period_start + (position - 1) * step
        rows.append(
            {
                "timestamp_utc": p0052.format_utc(timestamp),
                "area": request_meta["area"],
                "consumption_mw": float(quantity),
                "source_system": SOURCE_SYSTEM,
                "source_measure": SOURCE_MEASURE,
                "source_area_code": source_area_code,
                "resolution": resolution,
                "unit": normalize_mw_unit(unit),
                "timezone_handling": "ENTSO-E UTC period timestamps stored as UTC; subhourly values hourly-mean aggregated",
                "package_id": PACKAGE_ID,
                "source_type": SOURCE_MEASURE,
                "area_scope": AREA_SCOPE,
                "usable_for_consumption_target": True,
                "quality_flag": "ok",
            }
        )
    return rows


def aggregate_hourly_load(raw_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str, str, str], list[float]] = defaultdict(list)
    resolutions: dict[tuple[str, str, str, str, str, str], set[str]] = defaultdict(set)
    for row in raw_rows:
        value = float(row["consumption_mw"])
        if not math.isfinite(value):
            continue
        hour = p0052.parse_utc(str(row["timestamp_utc"])).replace(minute=0, second=0, microsecond=0)
        key = (
            p0052.format_utc(hour),
            str(row["area"]),
            str(row["source_system"]),
            str(row["source_measure"]),
            str(row["source_area_code"]),
            str(row["unit"]),
        )
        grouped[key].append(value)
        resolutions[key].add(str(row["resolution"]))
    ingested_at = p0052.format_utc(datetime.now(timezone.utc))
    rows = []
    for key, values in sorted(grouped.items()):
        resolution = "+".join(sorted(resolutions[key]))
        if len(values) > 1:
            resolution = f"{resolution}->hourly_mean"
        rows.append(
            {
                "timestamp_utc": key[0],
                "area": key[1],
                "consumption_mw": sum(values) / len(values),
                "source_system": key[2],
                "source_measure": key[3],
                "source_area_code": key[4],
                "resolution": resolution,
                "unit": key[5],
                "timezone_handling": "ENTSO-E UTC period timestamps stored as UTC; subhourly values hourly-mean aggregated",
                "package_id": PACKAGE_ID,
                "ingested_at_utc": ingested_at,
                "quality_flag": "ok",
            }
        )
    return rows


def persist_actual_load_rows(conn: sqlite3.Connection, rows: list[dict[str, object]]) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {TARGET_TABLE} (
            timestamp_utc TEXT NOT NULL,
            area TEXT NOT NULL,
            consumption_mw REAL NOT NULL,
            source_system TEXT NOT NULL,
            source_measure TEXT NOT NULL,
            source_area_code TEXT,
            resolution TEXT,
            unit TEXT,
            timezone_handling TEXT,
            package_id TEXT NOT NULL,
            ingested_at_utc TEXT,
            quality_flag TEXT,
            PRIMARY KEY (timestamp_utc, area, source_system, source_measure, package_id)
        )
        """
    )
    conn.execute(f"DELETE FROM {TARGET_TABLE} WHERE package_id = ?", (PACKAGE_ID,))
    if rows:
        columns = (
            "timestamp_utc",
            "area",
            "consumption_mw",
            "source_system",
            "source_measure",
            "source_area_code",
            "resolution",
            "unit",
            "timezone_handling",
            "package_id",
            "ingested_at_utc",
            "quality_flag",
        )
        placeholders = ",".join("?" for _ in columns)
        conn.executemany(
            f"INSERT OR REPLACE INTO {TARGET_TABLE} ({','.join(columns)}) VALUES ({placeholders})",
            [[row[col] for col in columns] for row in rows],
        )
    conn.commit()


def coverage_by_area(conn: sqlite3.Connection, start: datetime = START_UTC, end: datetime | None = None) -> dict[str, object]:
    end_dt = end or latest_table_end(conn)
    out: dict[str, object] = {}
    for area in AREAS:
        rows = [
            str(row[0])
            for row in conn.execute(
                f"SELECT timestamp_utc FROM {TARGET_TABLE} WHERE package_id=? AND area=? ORDER BY timestamp_utc",
                (PACKAGE_ID, area),
            )
        ]
        timestamps = set(rows)
        train_expected = expected_hours(start, HOLDOUT_START_UTC)
        holdout_expected = expected_hours(HOLDOUT_START_UTC, end_dt)
        train_missing = [ts for ts in train_expected if ts not in timestamps]
        holdout_missing = [ts for ts in holdout_expected if ts not in timestamps]
        out[area] = {
            "rows": len(rows),
            "first_timestamp_utc": min(rows, default=""),
            "last_timestamp_utc": max(rows, default=""),
            "train_fit_expected_hours": len(train_expected),
            "train_fit_rows": sum(1 for ts in rows if p0052.format_utc(start) <= ts < p0052.format_utc(HOLDOUT_START_UTC)),
            "train_fit_missing_hours": len(train_missing),
            "holdout_expected_hours": len(holdout_expected),
            "holdout_rows": sum(1 for ts in rows if ts >= p0052.format_utc(HOLDOUT_START_UTC)),
            "holdout_missing_hours": len(holdout_missing),
            "missing_examples": (train_missing + holdout_missing)[:12],
        }
    return out


def expected_hours(start: datetime, end: datetime) -> list[str]:
    hours = []
    current = start
    while current < end:
        hours.append(p0052.format_utc(current))
        current += timedelta(hours=1)
    return hours


def latest_table_end(conn: sqlite3.Connection) -> datetime:
    row = conn.execute(f"SELECT MAX(timestamp_utc) FROM {TARGET_TABLE} WHERE package_id=?", (PACKAGE_ID,)).fetchone()
    if row and row[0]:
        return p0052.parse_utc(str(row[0])) + timedelta(hours=1)
    return latest_request_end_utc()


def volume_sanity_by_area_season(conn: sqlite3.Connection) -> dict[str, object]:
    rows = [dict(row) for row in conn.execute(f"SELECT timestamp_utc, area, consumption_mw FROM {TARGET_TABLE} WHERE package_id=?", (PACKAGE_ID,))]
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        ts = p0052.parse_utc(str(row["timestamp_utc"]))
        month = ts.month
        season = half_year_for_month(month)
        grouped[(str(row["area"]), season)].append(float(row["consumption_mw"]))
    out: dict[str, object] = {}
    for area in AREAS:
        out[area] = {}
        for season in ("winter_half_year", "summer_half_year"):
            values = grouped.get((area, season), [])
            out[area][season] = describe_values(values, daily_energy_values(rows, area, season))
    return out


def half_year_for_month(month: int) -> str:
    if month in (10, 11, 12, 1, 2, 3):
        return "winter_half_year"
    return "summer_half_year"


def daily_energy_values(rows: list[dict[str, object]], area: str, season: str) -> list[float]:
    grouped: dict[str, float] = defaultdict(float)
    for row in rows:
        if str(row["area"]) != area:
            continue
        ts = p0052.parse_utc(str(row["timestamp_utc"]))
        if half_year_for_month(ts.month) != season:
            continue
        grouped[ts.date().isoformat()] += float(row["consumption_mw"]) / 1000.0
    return list(grouped.values())


def describe_values(values: list[float], daily_gwh: list[float]) -> dict[str, object]:
    if not values:
        return {"rows": 0}
    ordered = sorted(values)
    daily_ordered = sorted(daily_gwh)
    return {
        "rows": len(values),
        "mean_mw": round(sum(values) / len(values), 3),
        "median_mw": round(percentile(ordered, 0.50), 3),
        "p05_mw": round(percentile(ordered, 0.05), 3),
        "p25_mw": round(percentile(ordered, 0.25), 3),
        "p75_mw": round(percentile(ordered, 0.75), 3),
        "p95_mw": round(percentile(ordered, 0.95), 3),
        "min_mw": round(ordered[0], 3),
        "max_mw": round(ordered[-1], 3),
        "daily_energy_gwh_mean": round(sum(daily_ordered) / len(daily_ordered), 3) if daily_ordered else 0.0,
        "daily_energy_gwh_median": round(percentile(daily_ordered, 0.50), 3) if daily_ordered else 0.0,
    }


def se3_volume_check(volume: dict[str, object]) -> dict[str, object]:
    se3 = volume.get("SE3", {})
    summer = se3.get("summer_half_year", {}) if isinstance(se3, dict) else {}
    winter = se3.get("winter_half_year", {}) if isinstance(se3, dict) else {}
    summer_mean = float(summer.get("mean_mw", 0.0)) if isinstance(summer, dict) else 0.0
    winter_mean = float(winter.get("mean_mw", 0.0)) if isinstance(winter, dict) else 0.0
    plausible = 3000.0 <= summer_mean <= 20000.0 and 3000.0 <= winter_mean <= 25000.0
    return {
        "ok": plausible,
        "source_type": SOURCE_MEASURE,
        "area_scope": AREA_SCOPE,
        "usable_for_consumption_target": True,
        "summer_mean_mw": round(summer_mean, 3),
        "winter_mean_mw": round(winter_mean, 3),
        "interpretation": "SE3 actual-load magnitude is compatible with internal consumption/load, not line flow.",
    }


def old_source_comparison(conn: sqlite3.Connection) -> dict[str, object]:
    old_table = "physical_balance_se1_se4_hourly_v1"
    if not p0052.table_exists(conn, old_table):
        return {"old_table": old_table, "available": False, "reason": "table_missing"}
    old_cols = p0052.table_columns(conn, old_table)
    out: dict[str, object] = {"old_table": old_table, "available": True, "areas": {}}
    for area in AREAS:
        column = f"consumption_{area.lower()}"
        if column not in old_cols:
            out["areas"][area] = {"overlap_rows": 0, "reason": f"missing_column_{column}"}
            continue
        rows = [
            dict(row)
            for row in conn.execute(
                f"""
                SELECT n.timestamp_utc, n.consumption_mw AS entsoe_mw, o.{column} AS old_mw
                FROM {TARGET_TABLE} n
                JOIN {old_table} o ON o.timestamp_utc = n.timestamp_utc
                WHERE n.package_id=? AND n.area=? AND o.{column} IS NOT NULL
                """,
                (PACKAGE_ID, area),
            )
        ]
        out["areas"][area] = compare_value_rows(rows)
    return out


def compare_value_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    pairs = [(float(row["entsoe_mw"]), float(row["old_mw"])) for row in rows if is_finite(row["entsoe_mw"]) and is_finite(row["old_mw"])]
    if not pairs:
        return {"overlap_rows": 0}
    entsoe_values, old_values = zip(*pairs)
    mean_entsoe = sum(entsoe_values) / len(entsoe_values)
    mean_old = sum(old_values) / len(old_values)
    return {
        "overlap_rows": len(pairs),
        "entsoe_mean_mw": round(mean_entsoe, 3),
        "old_mean_mw": round(mean_old, 3),
        "entsoe_div_old_ratio": round(mean_entsoe / mean_old, 6) if mean_old else None,
        "mean_difference_mw": round(mean_entsoe - mean_old, 3),
        "correlation": round(correlation_pairs(pairs), 6) if len(pairs) > 1 else None,
    }


def correlation_pairs(pairs: list[tuple[float, float]]) -> float:
    xs, ys = zip(*pairs)
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
    denom_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    denom_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if denom_x == 0 or denom_y == 0:
        return 0.0
    return numerator / (denom_x * denom_y)


def data_quality_review(conn: sqlite3.Connection, coverage: dict[str, object], se3_check: dict[str, object]) -> dict[str, object]:
    rows = [dict(row) for row in conn.execute(f"SELECT timestamp_utc, area, consumption_mw FROM {TARGET_TABLE} WHERE package_id=?", (PACKAGE_ID,))]
    duplicate_count = len(rows) - len({(row["timestamp_utc"], row["area"]) for row in rows})
    nonfinite = sum(1 for row in rows if not is_finite(row["consumption_mw"]))
    negative = sum(1 for row in rows if is_finite(row["consumption_mw"]) and float(row["consumption_mw"]) < 0)
    all_train_holdout = all(
        isinstance(data, dict)
        and int(data.get("train_fit_rows", 0)) > 0
        and int(data.get("holdout_rows", 0)) > 0
        for data in coverage.values()
    )
    return {
        "ok": bool(rows) and duplicate_count == 0 and nonfinite == 0 and negative == 0 and all_train_holdout and bool(se3_check["ok"]),
        "rows": len(rows),
        "duplicates_by_timestamp_area": duplicate_count,
        "nonfinite_values": nonfinite,
        "negative_values": negative,
        "all_areas_have_train_fit_and_holdout": all_train_holdout,
        "token_leak_scan_required": True,
    }


def actual_load_source_contract(responses: list[dict[str, object]]) -> dict[str, object]:
    points_by_area = Counter()
    for response in responses:
        points_by_area[str(response["area"])] += int(response.get("points", 0) or 0)
    return {
        "ok": all(points_by_area[area] > 0 for area in AREAS),
        "source_system": SOURCE_SYSTEM,
        "document_type": "A65",
        "process_type": "A16",
        "source_type": SOURCE_MEASURE,
        "area_scope": AREA_SCOPE,
        "usable_for_consumption_target": True,
        "forbidden_sources_used": False,
        "forbidden_source_classes": ["net_cross_border_physical_flows", "A09", "A11", "A61", "production", "price"],
        "points_by_area": dict(points_by_area),
    }


def source_discovery(responses: list[dict[str, object]]) -> dict[str, object]:
    attempts = [
        {key: response.get(key) for key in ("document_type", "process_type", "area", "source_area_code", "status", "root", "reason", "timeseries", "points")}
        for response in responses
    ]
    return {
        "selected_contract": "ENTSO-E Actual Total Load / Total Load - Actual by Swedish bidding zone",
        "selected_document_type": "A65",
        "selected_process_type": "A16",
        "attempts": attempts,
        "token_included_in_evidence": False,
    }


def area_code_mapping() -> dict[str, object]:
    return {area: {"eic": p0052a.DOMAINS[area], "scope": AREA_SCOPE} for area in AREAS}


def table_schema_contract() -> dict[str, object]:
    return {
        "table": TARGET_TABLE,
        "primary_key": ["timestamp_utc", "area", "source_system", "source_measure", "package_id"],
        "columns": {
            "timestamp_utc": "UTC hourly target timestamp",
            "area": "SE1-SE4 bidding zone",
            "consumption_mw": "hourly mean MW",
            "source_system": SOURCE_SYSTEM,
            "source_measure": SOURCE_MEASURE,
            "source_area_code": "ENTSO-E EIC bidding zone code",
            "resolution": "source resolution, with ->hourly_mean for aggregated subhourly data",
            "unit": "MW",
            "timezone_handling": "source period timestamps normalized to UTC",
            "package_id": PACKAGE_ID,
        },
    }


def classify_cross_border_flow_file() -> dict[str, object]:
    candidates = []
    for root in (Path.cwd(), Path.home() / ".smart-home"):
        if root.exists():
            candidates.extend(root.rglob(FLOW_EXPORT_FILENAME))
    return {
        "filename": FLOW_EXPORT_FILENAME,
        "present": bool(candidates),
        "paths_checked": ["repository", "~/.smart-home"],
        "classification": "net_cross_border_physical_flows",
        "usable_for_consumption_target": False,
        "reason": "Physical cross-border flow/exchange files describe border transfer, not internal area load or consumption.",
    }


def downstream_contract() -> dict[str, object]:
    return {
        "table": TARGET_TABLE,
        "target_column": "consumption_mw",
        "join_key": ["timestamp_utc", "area"],
        "source_type": SOURCE_MEASURE,
        "forecast_safety_class": "historical_observed_only_target",
        "usage": "Use as historical target only; any future use requires a separate forecast model.",
    }


def downstream_impact() -> dict[str, object]:
    return {
        "p0054k": "May replace old SE3 physical-balance consumption target after a follow-up package updates loaders and metrics.",
        "p0054l2": "No direct change; price-origin logic remains separate.",
        "p0054m": "No retraining in P0054P2; future LABB packages can use this table as target source.",
        "p0054n": "Full 36h SE3 target should be rerun only in a later package.",
        "p0054o": "No model rerun in P0054P2; downstream metrics remain stale until rerun.",
    }


def what_we_learned(status: str, comparison: dict[str, object]) -> list[str]:
    lessons = [
        "P0054P2 must distinguish actual total load from A09/A11 physical exchange and A61 capacity.",
        f"The package status is {status}; downstream model metrics should not be interpreted as refreshed by this ingestion package.",
    ]
    if comparison.get("available"):
        lessons.append("Old physical-balance consumption and ENTSO-E actual total load are compared by overlap to quantify target-source differences.")
    return lessons


def next_package_recommendation(status: str) -> str:
    if status == "PASS":
        return "P0054Q should rerun SE3 LABB consumption modeling against entsoe_consumption_area_hourly_v1 and compare against P0054K-P0054O stale metrics."
    return "Resolve source coverage or source-contract gaps before downstream modeling."


def package_status(source_contract: dict[str, object], coverage: dict[str, object], se3_check: dict[str, object], quality: dict[str, object]) -> str:
    all_areas_ok = all(
        isinstance(data, dict)
        and int(data.get("train_fit_rows", 0)) > 0
        and int(data.get("holdout_rows", 0)) > 0
        for data in coverage.values()
    )
    if source_contract["ok"] and all_areas_ok and se3_check["ok"] and quality["ok"]:
        return "PASS"
    if source_contract["ok"] and se3_check["ok"] and quality["rows"]:
        return "WARN"
    return "STOP"


def secret_safety_without_path(secret_safety: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in secret_safety.items() if key != "path"}


def normalize_mw_unit(unit: str) -> str:
    return "MW" if unit in {"MAW", "MW"} else unit


def is_finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def write_p0054p2_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    writes = {
        "CHANGELOG.md": changelog_markdown(summary),
        "labb-label.md": evidence_markdown("LABB Label", {"label": LABEL, "package_id": PACKAGE_ID, "production_candidate": False}),
        "source-discovery.md": evidence_markdown("Source Discovery", summary["source_discovery"]),
        "entsoe-actual-load-source-contract.md": evidence_markdown("ENTSO-E Actual Load Source Contract", summary["source_contract"]),
        "area-code-mapping.md": evidence_markdown("Area Code Mapping", summary["area_code_mapping"]),
        "table-schema.md": evidence_markdown("Table Schema", summary["table_schema"]),
        "coverage-by-area.md": evidence_markdown("Coverage By Area", summary["coverage_by_area"]),
        "volume-sanity-by-area-season.md": evidence_markdown("Volume Sanity By Area Season", summary["volume_sanity_by_area_season"]),
        "se3-volume-check.md": evidence_markdown("SE3 Volume Check", summary["se3_volume_check"]),
        "old-source-comparison.md": evidence_markdown("Old Source Comparison", summary["old_source_comparison"]),
        "cross-border-flow-file-classification.md": evidence_markdown("Cross-Border Flow File Classification", summary["cross_border_flow_file_classification"]),
        "data-quality-review.md": evidence_markdown("Data Quality Review", summary["data_quality_review"]),
        "downstream-contract-for-p0054q.md": evidence_markdown("Downstream Contract For P0054Q", summary["downstream_contract"]),
        "impact-on-p0054k-through-p0054o.md": evidence_markdown("Impact On P0054K Through P0054O", summary["impact_on_p0054k_through_p0054o"]),
        "what-we-learned.md": evidence_markdown("What We Learned", summary["what_we_learned"]),
        "next-package-recommendation.md": evidence_markdown("Next Package Recommendation", summary["next_package_recommendation"]),
        "summary.json": json.dumps(summary, indent=2, sort_keys=True) + "\n",
    }
    paths: dict[str, str] = {}
    for filename, content in writes.items():
        path = evidence_dir / filename
        path.write_text(content, encoding="utf-8")
        paths[filename] = str(path)
    write_coverage_csv(evidence_dir / "coverage-by-area.csv", summary["coverage_by_area"])  # type: ignore[arg-type]
    paths["coverage-by-area.csv"] = str(evidence_dir / "coverage-by-area.csv")
    return paths


def evidence_markdown(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"


def changelog_markdown(summary: dict[str, object]) -> str:
    return (
        "# CHANGELOG\n\n"
        f"- Package: {PACKAGE_ID}\n"
        f"- Label: {LABEL}\n"
        f"- Status: {summary['status']}\n"
        f"- Built table `{TARGET_TABLE}` from ENTSO-E A65/A16 actual total load by SE1-SE4 bidding zone.\n"
        "- Classified cross-border physical flow exports as not usable for consumption targets.\n"
        "- No device, runtime, A61 utilization, price API or future actual price leakage changes.\n"
    )


def write_coverage_csv(path: Path, coverage: dict[str, object]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            lineterminator="\n",
            fieldnames=[
                "area",
                "rows",
                "first_timestamp_utc",
                "last_timestamp_utc",
                "train_fit_rows",
                "train_fit_missing_hours",
                "holdout_rows",
                "holdout_missing_hours",
            ],
        )
        writer.writeheader()
        for area, payload in coverage.items():
            row = {"area": area}
            if isinstance(payload, dict):
                row.update({key: payload.get(key, "") for key in writer.fieldnames if key != "area"})
            writer.writerow(row)


def main() -> None:
    result = run_p0054p2_ingestion()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
