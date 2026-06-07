"""P0056A LABB northern Europe area consumption measurements."""

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


PACKAGE_ID = "P0056A"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0056A")
SOURCE_SYSTEM = "ENTSO-E"
SOURCE_MEASURE = "actual_total_load"
AREA_SCOPE = "bidding_zone_internal_consumption_or_load"
START_UTC = datetime(2022, 6, 1, tzinfo=timezone.utc)
NATIVE_TABLE = "area_consumption_native_v1"
HOURLY_TABLE = "area_consumption_hourly_v1"
CATALOG_TABLE = "area_consumption_area_catalog_v1"
SE3_REFERENCE_TABLE = "entsoe_consumption_area_hourly_v1"
SE3_REFERENCE_PACKAGE = "P0054P2"

AREA_EIC = {
    "SE1": "10Y1001A1001A44P",
    "SE2": "10Y1001A1001A45N",
    "SE3": "10Y1001A1001A46L",
    "SE4": "10Y1001A1001A47J",
    "NO1": "10YNO-1--------2",
    "NO2": "10YNO-2--------T",
    "NO3": "10YNO-3--------J",
    "NO4": "10YNO-4--------9",
    "NO5": "10Y1001A1001A48H",
    "DK1": "10YDK-1--------W",
    "DK2": "10YDK-2--------M",
    "FI": "10YFI-1--------U",
    "EE": "10Y1001A1001A39I",
    "LV": "10YLV-1001A00074",
    "LT": "10YLT-1001A0008Q",
    "DE_LU": "10Y1001A1001A82H",
    "PL": "10YPL-AREA-----S",
    "NL": "10YNL----------L",
}
PRIMARY_AREAS = tuple(AREA_EIC)


@dataclass(frozen=True)
class P0056AResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0056a_ingestion(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
    start: datetime = START_UTC,
    end: datetime | None = None,
) -> P0056AResult:
    started = time.monotonic()
    feature_db = Path(feature_db).expanduser()
    evidence_dir = Path(evidence_dir)
    end_dt = end or latest_request_end_utc()
    token_source = p0052a.load_entsoe_token()
    secret_safety = p0052a.verify_secret_safety(token_source)
    if not secret_safety["secret_safe"]:
        raise RuntimeError("P0056A secret safety check failed")

    catalog_rows = area_catalog()
    native_rows, responses = fetch_actual_load_native_rows(token_source.token, start, end_dt)
    hourly_rows = aggregate_native_to_hourly(native_rows)
    with sqlite3.connect(feature_db) as conn:
        conn.row_factory = sqlite3.Row
        db_counts = persist_p0056a_tables(conn, catalog_rows, native_rows, hourly_rows)
        validation = validation_summary(conn, start, end_dt, responses)
    status = package_status(validation)
    summary = {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "request_range": {"start": p0052.format_utc(start), "end": p0052.format_utc(end_dt)},
        "area_scope": area_scope_summary(catalog_rows),
        "source_access_review": source_access_review(responses, secret_safety),
        "area_code_mapping": area_code_mapping(catalog_rows),
        "native_resolution_review": validation["native_resolution_review"],
        "database_schema_contract": database_schema_contract(),
        "ingestion_progress": ingestion_progress(responses, db_counts),
        "database_load_evidence": db_counts,
        "hourly_aggregation_contract": hourly_aggregation_contract(),
        "coverage_and_missingness": validation["coverage_and_missingness"],
        "volume_sanity_check": validation["volume_sanity_check"],
        "se3_target_consistency_check": validation["se3_target_consistency_check"],
        "data_quality_review": validation["data_quality_review"],
        "modeling_readiness_review": modeling_readiness_review(status, validation),
        "what_we_learned": what_we_learned(status, validation),
        "next_package_recommendation": next_package_recommendation(status, validation),
        "row_counts": {
            "area_catalog_rows": len(catalog_rows),
            "native_rows": len(native_rows),
            "hourly_rows": len(hourly_rows),
            **db_counts,
        },
        "no_devices": True,
        "no_runtime_change": True,
        "no_model_training": True,
        "no_spot_price_features": True,
        "no_flow_exchange_a61_capacity_features": True,
        "no_old_physical_balance_target": True,
        "raw_exports_committed": False,
        "token_included_in_evidence": False,
    }
    evidence = write_p0056a_evidence(evidence_dir, summary)
    return P0056AResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def latest_request_end_utc(now: datetime | None = None) -> datetime:
    current = now or datetime.now(timezone.utc)
    return current.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)


def area_catalog() -> list[dict[str, object]]:
    return [
        {
            "area_code": area,
            "bidding_zone_code": area,
            "entsoe_eic": eic,
            "source_system": SOURCE_SYSTEM,
            "source_measure": SOURCE_MEASURE,
            "area_scope": AREA_SCOPE,
            "is_primary_scope": True,
            "generated_by_package": PACKAGE_ID,
        }
        for area, eic in AREA_EIC.items()
    ]


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
    source_area_code = AREA_EIC[area]
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
        "area_code": area,
        "bidding_zone_code": area,
        "source_area_code": source_area_code,
        "source_type": SOURCE_MEASURE,
        "area_scope": AREA_SCOPE,
        "period_start": p0052.format_utc(start),
        "period_end": p0052.format_utc(end),
    }
    return params, safe


def fetch_actual_load_native_rows(token: str, start: datetime, end: datetime) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    native_rows: list[dict[str, object]] = []
    responses: list[dict[str, object]] = []
    for area in PRIMARY_AREAS:
        for chunk_start, chunk_end in yearly_chunks(start, end):
            params, safe = build_actual_load_params(area, chunk_start, chunk_end)
            try:
                xml_bytes, status = p0052a.fetch_entsoe_document(token, params, timeout=45.0)
            except urllib.error.URLError as exc:
                responses.append({**safe, "status": "url_error", "root": "", "reason": str(type(exc.reason).__name__)[:180], "timeseries": 0, "points": 0})
                continue
            observations, response = parse_actual_load_document(xml_bytes, safe)
            responses.append({**safe, "status": status, **response})
            native_rows.extend(observations)
    return native_rows, responses


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
        interval_start = period_start + (position - 1) * step
        interval_end = interval_start + step
        rows.append(
            {
                "area_code": request_meta["area_code"],
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
            }
        )
    return rows


def aggregate_native_to_hourly(native_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    ingested_at = p0052.format_utc(datetime.now(timezone.utc))
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
                target = grouped.setdefault(
                    key,
                    {
                        "timestamp_utc": key[0],
                        "area_code": key[1],
                        "weighted_mw_seconds": 0.0,
                        "covered_seconds": 0.0,
                        "native_resolutions": set(),
                        "input_row_count": 0,
                    },
                )
                target["weighted_mw_seconds"] = float(target["weighted_mw_seconds"]) + value * seconds
                target["covered_seconds"] = float(target["covered_seconds"]) + seconds
                target["native_resolutions"].add(int(row["native_resolution_minutes"]))  # type: ignore[union-attr]
                target["input_row_count"] = int(target["input_row_count"]) + 1
            current = hour_end
    rows = []
    for key, data in sorted(grouped.items()):
        covered = float(data["covered_seconds"])
        resolution_mix = "+".join(str(item) for item in sorted(data["native_resolutions"]))  # type: ignore[arg-type]
        rows.append(
            {
                "timestamp_utc": data["timestamp_utc"],
                "area_code": data["area_code"],
                "bidding_zone_code": data["area_code"],
                "consumption_mw": float(data["weighted_mw_seconds"]) / covered if covered else None,
                "source_system": SOURCE_SYSTEM,
                "aggregation_method": "time_weighted_hourly_average_mw",
                "native_resolution_mix": resolution_mix,
                "coverage_flag": "ok" if abs(covered - 3600.0) <= 1.0 else "partial_hour",
                "input_row_count": data["input_row_count"],
                "ingested_at_utc": ingested_at,
                "generated_by_package": PACKAGE_ID,
            }
        )
    return rows


def persist_p0056a_tables(conn: sqlite3.Connection, catalog_rows: list[dict[str, object]], native_rows: list[dict[str, object]], hourly_rows: list[dict[str, object]]) -> dict[str, int]:
    ensure_tables(conn)
    for table in (CATALOG_TABLE, NATIVE_TABLE, HOURLY_TABLE):
        conn.execute(f"DELETE FROM {table} WHERE generated_by_package=?", (PACKAGE_ID,))
    insert_rows(conn, CATALOG_TABLE, catalog_rows)
    insert_rows(conn, NATIVE_TABLE, native_rows)
    insert_rows(conn, HOURLY_TABLE, hourly_rows)
    conn.commit()
    return {CATALOG_TABLE: len(catalog_rows), NATIVE_TABLE: len(native_rows), HOURLY_TABLE: len(hourly_rows)}


def ensure_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {CATALOG_TABLE} (
            area_code TEXT NOT NULL,
            bidding_zone_code TEXT NOT NULL,
            entsoe_eic TEXT NOT NULL,
            source_system TEXT NOT NULL,
            source_measure TEXT NOT NULL,
            area_scope TEXT NOT NULL,
            is_primary_scope INTEGER NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (area_code, source_system, source_measure, generated_by_package)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {NATIVE_TABLE} (
            area_code TEXT NOT NULL,
            interval_start_utc TEXT NOT NULL,
            interval_end_utc TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL,
            value_kind TEXT NOT NULL,
            native_resolution_minutes INTEGER NOT NULL,
            source_system TEXT NOT NULL,
            source_area_code TEXT,
            document_type TEXT,
            process_type TEXT,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (area_code, interval_start_utc, interval_end_utc, value_kind, source_system, generated_by_package)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {HOURLY_TABLE} (
            timestamp_utc TEXT NOT NULL,
            area_code TEXT NOT NULL,
            bidding_zone_code TEXT NOT NULL,
            consumption_mw REAL NOT NULL,
            source_system TEXT NOT NULL,
            aggregation_method TEXT NOT NULL,
            native_resolution_mix TEXT,
            coverage_flag TEXT,
            input_row_count INTEGER NOT NULL,
            ingested_at_utc TEXT,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (timestamp_utc, area_code, source_system, generated_by_package)
        )
        """
    )


def insert_rows(conn: sqlite3.Connection, table: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    columns = list(rows[0].keys())
    placeholders = ",".join("?" for _ in columns)
    conn.executemany(
        f"INSERT OR REPLACE INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
        [[row.get(column) for column in columns] for row in rows],
    )


def validation_summary(conn: sqlite3.Connection, start: datetime, end: datetime, responses: list[dict[str, object]]) -> dict[str, object]:
    hourly = [dict(row) for row in conn.execute(f"SELECT * FROM {HOURLY_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,))]
    native = [dict(row) for row in conn.execute(f"SELECT * FROM {NATIVE_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,))]
    coverage = coverage_and_missingness(hourly, start, end)
    volume = volume_sanity(hourly)
    se3 = se3_target_consistency(conn)
    quality = data_quality(hourly, native, coverage, se3)
    return {
        "native_resolution_review": native_resolution_review(native),
        "coverage_and_missingness": coverage,
        "volume_sanity_check": volume,
        "se3_target_consistency_check": se3,
        "data_quality_review": quality,
        "responses": responses,
    }


def coverage_and_missingness(rows: list[dict[str, object]], start: datetime, end: datetime) -> dict[str, object]:
    by_area = group_by(rows, "area_code")
    out: dict[str, object] = {}
    expected = expected_hours(start, end)
    for area in PRIMARY_AREAS:
        area_rows = by_area.get(area, [])
        timestamps = {str(row["timestamp_utc"]) for row in area_rows}
        missing = [timestamp for timestamp in expected if timestamp not in timestamps]
        out[area] = {
            "row_count": len(area_rows),
            "min_timestamp_utc": min(timestamps, default=""),
            "max_timestamp_utc": max(timestamps, default=""),
            "coverage_ratio_since_2022_06_01": len(timestamps) / len(expected) if expected else 0.0,
            "missing_intervals": len(missing),
            "missing_examples": missing[:12],
            "duplicate_intervals": len(area_rows) - len(timestamps),
        }
    return out


def expected_hours(start: datetime, end: datetime) -> list[str]:
    out = []
    current = start
    while current < end:
        out.append(p0052.format_utc(current))
        current += timedelta(hours=1)
    return out


def native_resolution_review(native_rows: list[dict[str, object]]) -> dict[str, object]:
    by_area = group_by(native_rows, "area_code")
    out = {}
    for area in PRIMARY_AREAS:
        resolutions = sorted({int(row["native_resolution_minutes"]) for row in by_area.get(area, [])})
        out[area] = {"native_resolution": resolution_label(resolutions), "native_resolution_minutes": resolutions, "native_rows": len(by_area.get(area, []))}
    return out


def resolution_label(resolutions: list[int]) -> str:
    if not resolutions:
        return "unknown"
    if resolutions == [15]:
        return "15m"
    if resolutions == [30]:
        return "30m"
    if resolutions == [60]:
        return "60m"
    return "mixed"


def volume_sanity(rows: list[dict[str, object]]) -> dict[str, object]:
    by_area = group_by(rows, "area_code")
    out = {}
    for area in PRIMARY_AREAS:
        values = [float(row["consumption_mw"]) for row in by_area.get(area, []) if is_finite(row.get("consumption_mw"))]
        out[area] = describe_values(values)
    return out


def describe_values(values: list[float]) -> dict[str, object]:
    if not values:
        return {"row_count": 0}
    ordered = sorted(values)
    return {
        "row_count": len(values),
        "mean_mw": round(sum(values) / len(values), 3),
        "median_mw": round(percentile(ordered, 0.50), 3),
        "p05_mw": round(percentile(ordered, 0.05), 3),
        "p95_mw": round(percentile(ordered, 0.95), 3),
        "min_mw": round(ordered[0], 3),
        "max_mw": round(ordered[-1], 3),
        "negative_hours_count": sum(1 for value in values if value < 0.0),
        "zero_hours_count": sum(1 for value in values if value == 0.0),
    }


def se3_target_consistency(conn: sqlite3.Connection) -> dict[str, object]:
    if not p0052.table_exists(conn, SE3_REFERENCE_TABLE):
        return {"ok": False, "reference_table": SE3_REFERENCE_TABLE, "reason": "reference_table_missing"}
    rows = [
        dict(row)
        for row in conn.execute(
            f"""
            SELECT n.timestamp_utc, n.consumption_mw AS p0056a_mw, r.consumption_mw AS reference_mw
            FROM {HOURLY_TABLE} n
            JOIN {SE3_REFERENCE_TABLE} r ON r.timestamp_utc = n.timestamp_utc AND r.area = 'SE3'
            WHERE n.generated_by_package=? AND n.area_code='SE3' AND r.package_id=?
            ORDER BY n.timestamp_utc
            """,
            (PACKAGE_ID, SE3_REFERENCE_PACKAGE),
        )
    ]
    diffs = [abs(float(row["p0056a_mw"]) - float(row["reference_mw"])) for row in rows]
    return {
        "ok": bool(rows) and (max(diffs) if diffs else 0.0) <= 1e-6,
        "reference_table": SE3_REFERENCE_TABLE,
        "reference_package": SE3_REFERENCE_PACKAGE,
        "overlap_rows": len(rows),
        "max_abs_delta_mw": max(diffs) if diffs else None,
        "mean_abs_delta_mw": sum(diffs) / len(diffs) if diffs else None,
    }


def data_quality(hourly_rows: list[dict[str, object]], native_rows: list[dict[str, object]], coverage: dict[str, object], se3: dict[str, object]) -> dict[str, object]:
    hourly_keys = [(row["timestamp_utc"], row["area_code"]) for row in hourly_rows]
    native_keys = [(row["area_code"], row["interval_start_utc"], row["interval_end_utc"]) for row in native_rows]
    nonfinite = sum(1 for row in hourly_rows if not is_finite(row.get("consumption_mw")))
    negative = sum(1 for row in hourly_rows if is_finite(row.get("consumption_mw")) and float(row["consumption_mw"]) < 0)
    areas_with_rows = [area for area, item in coverage.items() if isinstance(item, dict) and int(item.get("row_count", 0)) > 0]
    return {
        "ok": len(areas_with_rows) == len(PRIMARY_AREAS) and len(hourly_keys) == len(set(hourly_keys)) and len(native_keys) == len(set(native_keys)) and nonfinite == 0 and negative == 0 and bool(se3.get("ok")),
        "hourly_rows": len(hourly_rows),
        "native_rows": len(native_rows),
        "areas_with_rows": areas_with_rows,
        "missing_primary_areas": [area for area in PRIMARY_AREAS if area not in areas_with_rows],
        "duplicate_hourly_intervals": len(hourly_keys) - len(set(hourly_keys)),
        "duplicate_native_intervals": len(native_keys) - len(set(native_keys)),
        "nonfinite_hourly_values": nonfinite,
        "negative_hours_count": negative,
        "se3_consistency_ok": bool(se3.get("ok")),
    }


def package_status(validation: dict[str, object]) -> str:
    quality = validation["data_quality_review"]
    coverage = validation["coverage_and_missingness"]
    if quality["ok"] and all(isinstance(item, dict) and float(item.get("coverage_ratio_since_2022_06_01", 0.0)) >= 0.95 for item in coverage.values()):  # type: ignore[union-attr]
        return "PASS"
    if quality["areas_with_rows"] and quality["se3_consistency_ok"]:  # type: ignore[index]
        return "WARN"
    return "STOP"


def group_by(rows: list[dict[str, object]], key: str) -> dict[str, list[dict[str, object]]]:
    out: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        out[str(row[key])].append(row)
    return dict(out)


def is_finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def normalize_mw_unit(unit: str) -> str:
    return "MW" if unit in {"MAW", "MW"} else unit


def source_access_review(responses: list[dict[str, object]], secret_safety: dict[str, object]) -> dict[str, object]:
    points_by_area = Counter()
    attempts = []
    for response in responses:
        area = str(response["area_code"])
        points_by_area[area] += int(response.get("points", 0) or 0)
        attempts.append({key: response.get(key) for key in ("area_code", "source_area_code", "period_start", "period_end", "status", "root", "reason", "timeseries", "points")})
    return {
        "ok": all(points_by_area[area] > 0 for area in PRIMARY_AREAS),
        "source_system": SOURCE_SYSTEM,
        "document_type": "A65",
        "process_type": "A16",
        "token_source": secret_safety.get("token_source"),
        "token_included_in_evidence": False,
        "points_by_area": dict(points_by_area),
        "attempts": attempts,
    }


def area_scope_summary(catalog_rows: list[dict[str, object]]) -> dict[str, object]:
    return {"primary_areas": [row["area_code"] for row in catalog_rows], "area_count": len(catalog_rows), "label": LABEL}


def area_code_mapping(catalog_rows: list[dict[str, object]]) -> dict[str, object]:
    return {str(row["area_code"]): {"eic": row["entsoe_eic"], "scope": row["area_scope"]} for row in catalog_rows}


def ingestion_progress(responses: list[dict[str, object]], db_counts: dict[str, int]) -> dict[str, object]:
    completed = sorted({str(response["area_code"]) for response in responses if int(response.get("points", 0) or 0) > 0})
    return {"completed_areas": completed, "missing_areas": [area for area in PRIMARY_AREAS if area not in completed], "db_counts": db_counts}


def database_schema_contract() -> dict[str, object]:
    return {
        "native_table": NATIVE_TABLE,
        "hourly_table": HOURLY_TABLE,
        "catalog_table": CATALOG_TABLE,
        "generated_by_package": PACKAGE_ID,
        "hourly_primary_key": ["timestamp_utc", "area_code", "source_system", "generated_by_package"],
        "native_primary_key": ["area_code", "interval_start_utc", "interval_end_utc", "value_kind", "source_system", "generated_by_package"],
    }


def hourly_aggregation_contract() -> dict[str, object]:
    return {
        "value_kind": SOURCE_MEASURE,
        "native_value_semantics": "average MW over native interval",
        "aggregation_method": "time-weighted hourly average MW",
        "unit_policy": "MAW and MW normalized to MW; unknown units preserved and visible",
        "mixed_resolution_policy": "native_resolution_mix records all contributing native interval lengths",
    }


def modeling_readiness_review(status: str, validation: dict[str, object]) -> dict[str, object]:
    quality = validation["data_quality_review"]
    return {
        "ready_for_next_labb_forecast_package": status in {"PASS", "WARN"} and bool(quality.get("areas_with_rows")),
        "status": status,
        "label": LABEL,
        "not_g2_candidate": True,
        "forecast_model_trained": False,
        "target_usage": "historical_observed_only target rows; future use requires separate forecast model",
    }


def what_we_learned(status: str, validation: dict[str, object]) -> list[str]:
    quality = validation["data_quality_review"]
    return [
        f"P0056A status is {status}.",
        f"Areas with rows: {quality.get('areas_with_rows')}.",
        f"Missing primary areas: {quality.get('missing_primary_areas')}.",
        f"SE3 consistency ok: {quality.get('se3_consistency_ok')}.",
    ]


def next_package_recommendation(status: str, validation: dict[str, object]) -> str:
    missing = validation["data_quality_review"].get("missing_primary_areas", [])  # type: ignore[union-attr]
    if status == "PASS":
        return "Build P0056B as multi-area consumption forecast lab using these measured targets and forecast-safe features."
    if missing:
        return "Resolve missing primary area ENTSO-E access/mapping before multi-area consumption forecasting."
    return "Use P0056B to build forecast models, while documenting any partial latest-data coverage."


def write_p0056a_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "CHANGELOG.md": changelog(summary),
        "labb-label.md": json_md("P0056A LABB label", {"label": LABEL, "g2_candidate": False}),
        "area-scope.md": json_md("P0056A area scope", summary["area_scope"]),
        "source-access-review.md": json_md("P0056A source access review", summary["source_access_review"]),
        "area-code-mapping.md": json_md("P0056A area code mapping", summary["area_code_mapping"]),
        "native-resolution-review.md": json_md("P0056A native resolution review", summary["native_resolution_review"]),
        "database-schema-contract.md": json_md("P0056A database schema contract", summary["database_schema_contract"]),
        "ingestion-progress.md": json_md("P0056A ingestion progress", summary["ingestion_progress"]),
        "database-load-evidence.md": json_md("P0056A database load evidence", summary["database_load_evidence"]),
        "hourly-aggregation-contract.md": json_md("P0056A hourly aggregation contract", summary["hourly_aggregation_contract"]),
        "coverage-and-missingness.md": json_md("P0056A coverage and missingness", summary["coverage_and_missingness"]),
        "volume-sanity-check.md": json_md("P0056A volume sanity check", summary["volume_sanity_check"]),
        "se3-target-consistency-check.md": json_md("P0056A SE3 target consistency check", summary["se3_target_consistency_check"]),
        "data-quality-review.md": json_md("P0056A data quality review", summary["data_quality_review"]),
        "modeling-readiness-review.md": json_md("P0056A modeling readiness review", summary["modeling_readiness_review"]),
        "what-we-learned.md": "# P0056A what we learned\n\n" + "\n".join(f"- {line}" for line in summary["what_we_learned"]) + "\n",
        "next-package-recommendation.md": "# P0056A next package recommendation\n\n" + str(summary["next_package_recommendation"]) + "\n",
        "ingestion-summary.json": json.dumps(json_safe(summary), indent=2, sort_keys=True) + "\n",
    }
    paths = {}
    for filename, content in files.items():
        path = evidence_dir / filename
        path.write_text(content, encoding="utf-8")
        paths[filename] = str(path)
    paths["area-scope.csv"] = write_csv(evidence_dir / "area-scope.csv", [{"area_code": area} for area in PRIMARY_AREAS])
    paths["area-code-mapping.csv"] = write_csv(evidence_dir / "area-code-mapping.csv", [{"area_code": area, "eic": AREA_EIC[area]} for area in PRIMARY_AREAS])
    paths["coverage-summary.csv"] = write_summary_csv(evidence_dir / "coverage-summary.csv", summary["coverage_and_missingness"])
    paths["volume-sanity-summary.csv"] = write_summary_csv(evidence_dir / "volume-sanity-summary.csv", summary["volume_sanity_check"])
    return paths


def changelog(summary: dict[str, object]) -> str:
    return f"""# P0056A changelog

Status: `{summary['status']}`

- Loaded northern Europe ENTSO-E A65/A16 actual total load measurements into P0056A native/hourly/catalog tables.
- Primary area count: `{summary['area_scope']['area_count']}`.
- Hourly rows: `{summary['row_counts']['hourly_rows']}`.
- Native rows: `{summary['row_counts']['native_rows']}`.
- SE3 consistency ok: `{summary['se3_target_consistency_check']['ok']}`.
- No forecast models, devices, runtime writes, spot-price features, flow/exchange/A61/capacity features, old physical_balance target or large raw committed exports.
"""


def json_md(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(json_safe(payload), indent=2, sort_keys=True)}\n```\n"


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, (datetime,)):
        return p0052.format_utc(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def write_csv(path: Path, rows: list[dict[str, object]]) -> str:
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(rows[0].keys()) if rows else ["empty"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return str(path)


def write_summary_csv(path: Path, payload: object) -> str:
    rows = []
    if isinstance(payload, dict):
        for area, data in payload.items():
            row = {"area_code": area}
            if isinstance(data, dict):
                row.update({key: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value for key, value in data.items()})
            rows.append(row)
    return write_csv(path, rows)


def main() -> None:
    result = run_p0056a_ingestion()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
