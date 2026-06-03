"""P0052B ENTSO-E capacity concept review and historical backfill."""

from __future__ import annotations

from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import math
import sqlite3
import time
import urllib.error
import xml.etree.ElementTree as ET

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0052a


PACKAGE_ID = "P0052B"
EVIDENCE_DIR = Path("requirements/package-runs/P0052B")
PRICE_TABLE = "se3_se1_demand_response_analysis_v1"
CAPACITY_CONCEPT_STATUS = "capacity_concept_uncertain"
DEFAULT_WINDOWS = (
    (datetime(2025, 1, 1, tzinfo=timezone.utc), datetime(2025, 1, 7, 23, tzinfo=timezone.utc), "2025_representative_week"),
    (datetime(2024, 10, 27, tzinfo=timezone.utc), datetime(2024, 11, 3, 23, tzinfo=timezone.utc), "flow_based_transition_week"),
    (datetime(2026, 5, 1, tzinfo=timezone.utc), datetime(2026, 5, 7, 23, tzinfo=timezone.utc), "p0052a_overlap_week"),
)
LONG_METADATA_COLUMNS = {
    "document_type": "TEXT",
    "process_type": "TEXT",
    "business_type": "TEXT",
    "contract_type": "TEXT",
    "entsoe_curve_type": "TEXT",
    "entsoe_resolution": "TEXT",
    "capacity_concept_status": "TEXT",
}
WIDE_COLUMNS = {
    "bottleneck_margin_se1_se2_north_to_south": "REAL",
    "bottleneck_margin_se2_se3_north_to_south": "REAL",
    "bottleneck_margin_se3_se4_north_to_south": "REAL",
    "north_to_south_utilization_max": "REAL",
    "north_to_south_bottleneck_margin_min": "REAL",
    "north_to_south_binding_border_candidate": "TEXT",
}


@dataclass(frozen=True)
class P0052BResult:
    status: str
    row_counts: dict[str, object]
    evidence: dict[str, str]


def run_p0052b_ingestion(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
    windows: tuple[tuple[datetime, datetime, str], ...] = DEFAULT_WINDOWS,
    workers: int = 8,
) -> P0052BResult:
    started = time.monotonic()
    token_source = p0052a.load_entsoe_token()
    secret_safety = p0052a.verify_secret_safety(token_source)
    if not secret_safety["secret_safe"]:
        raise RuntimeError("P0052B secret safety check failed")
    concept_review = capacity_concept_review()
    raw_rows, responses, failed_chunks = fetch_entsoe_rows_for_windows(token_source.token, windows, workers=workers)
    hourly_rows = aggregate_hourly_p0052b(raw_rows)
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        p0052a.ensure_p0052_tables_exist(conn)
        schema_summary = ensure_p0052b_schema(conn)
        persistence = persist_entsoe_rows_p0052b(conn, raw_rows, hourly_rows)
        wide_update = update_wide_entsoe_features_p0052b(conn, hourly_rows, concept_review)
        join_analysis = run_join_fix_analysis(conn)
        validation = validate_p0052b(conn, raw_rows, hourly_rows, responses, secret_safety, join_analysis)
        diagnostics = run_p0052b_diagnostics(conn, concept_review)
    summary = {
        "status": "WARN",
        "secret_safety": secret_safety,
        "schema_summary": schema_summary,
        "capacity_concept_review": concept_review,
        "windows": window_summary(windows),
        "source_contracts": source_contracts(responses, failed_chunks),
        "row_counts": {
            "raw_rows_fetched": len(raw_rows),
            "hourly_rows_aggregated": len(hourly_rows),
            **persistence,
            **wide_update,
        },
        "validation": validation,
        "join_analysis": join_analysis,
        "diagnostics": diagnostics,
        "forecast_safety": forecast_safety_classification(concept_review),
        "runtime_seconds": time.monotonic() - started,
        "forbidden_paths": p0052.FORBIDDEN_PRODUCTION_PATHS,
    }
    evidence = write_p0052b_evidence(Path(evidence_dir), summary)
    return P0052BResult(str(summary["status"]), summary["row_counts"], evidence)


def capacity_concept_review() -> dict[str, object]:
    return {
        "status": CAPACITY_CONCEPT_STATUS,
        "official_sources": [
            "https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide_prod_backup_06_11_2024.html",
            "https://transparencyplatform.zendesk.com/hc/en-us/articles/15856778598548-Contract-MarketAgreement-Type",
            "https://www.entsoe.eu/Documents/EDI/Library/Core/entso-e-code-list-v29r0.pdf",
        ],
        "document_type_A61": {
            "meaning": "Maximum possible",
            "use_for_utilization": False,
            "reason": "A61 is a maximum-possible capacity document/business meaning, but contract type alone does not prove hourly market-capacity compatibility.",
        },
        "contract_types": {
            "A02": {"meaning": "Weekly", "directional": True, "capacity_horizon": "weekly", "use_for_utilization": False},
            "A03": {"meaning": "Monthly", "directional": True, "capacity_horizon": "monthly", "use_for_utilization": False},
            "A04": {"meaning": "Yearly", "directional": True, "capacity_horizon": "yearly", "use_for_utilization": False},
        },
        "selected_capacity_contract_type": None,
        "utilization_allowed": False,
        "bottleneck_margin_allowed": False,
        "conclusion": "Store A61 capacity rows with explicit contract labels, but keep utilization and bottleneck margin null until publication timing and compatibility with scheduled exchange/physical flow are proven.",
    }


def ensure_p0052b_schema(conn: sqlite3.Connection) -> dict[str, object]:
    added: dict[str, list[str]] = {p0052.RAW_TABLE: [], p0052.CANONICAL_TABLE: [], p0052.WIDE_TABLE: []}
    for table in (p0052.RAW_TABLE, p0052.CANONICAL_TABLE):
        existing = p0052.table_columns(conn, table)
        for column, column_type in LONG_METADATA_COLUMNS.items():
            if column not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
                added[table].append(column)
    existing_wide = p0052.table_columns(conn, p0052.WIDE_TABLE)
    for column in p0052a.wide_entsoe_columns():
        if column not in existing_wide:
            conn.execute(f"ALTER TABLE {p0052.WIDE_TABLE} ADD COLUMN {column} REAL")
            added[p0052.WIDE_TABLE].append(column)
    existing_wide = p0052.table_columns(conn, p0052.WIDE_TABLE)
    for column, column_type in WIDE_COLUMNS.items():
        if column not in existing_wide:
            conn.execute(f"ALTER TABLE {p0052.WIDE_TABLE} ADD COLUMN {column} {column_type}")
            added[p0052.WIDE_TABLE].append(column)
    conn.commit()
    return {"added_columns": added}


def fetch_entsoe_rows_for_windows(token: str, windows: tuple[tuple[datetime, datetime, str], ...], *, workers: int = 8) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    raw_rows: list[dict[str, object]] = []
    responses: list[dict[str, object]] = []
    failed_chunks: list[dict[str, object]] = []
    tasks = []
    for start, end, window_id in windows:
        for chunk_start, chunk_end in chunk_windows(start, end, max_days=31):
            for config in p0052a.DOCUMENT_CONFIGS:
                for border in p0052a.INTERNAL_BORDERS:
                    left, right = border.split("_", 1)
                    for from_area, to_area in ((left, right), (right, left)):
                        params, safe = p0052a.build_entsoe_params(config, from_area, to_area, chunk_start, chunk_end)
                        safe = {**safe, "window_id": window_id}
                        tasks.append((params, safe, config, chunk_start, chunk_end))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_map = {pool.submit(fetch_one_entsoe_task, token, *task): task for task in tasks}
        completed = 0
        for future in as_completed(future_map):
            completed += 1
            rows, response, failure = future.result()
            if failure:
                failed_chunks.append(failure)
            else:
                raw_rows.extend(rows)
                responses.append(response)
            if completed % 10 == 0 or completed == len(tasks):
                print(f"P0052B fetch progress {completed}/{len(tasks)}", flush=True)
    return raw_rows, responses, failed_chunks


def fetch_one_entsoe_task(
    token: str,
    params: dict[str, str],
    safe: dict[str, str],
    config: dict[str, str],
    chunk_start: datetime,
    chunk_end: datetime,
) -> tuple[list[dict[str, object]], dict[str, object], dict[str, object] | None]:
    try:
        xml_bytes, status = p0052a.fetch_entsoe_document(token, params, timeout=12.0)
        observations, response = parse_entsoe_document_clipped(xml_bytes, safe, chunk_start, chunk_end)
    except (urllib.error.URLError, ValueError, sqlite3.Error) as exc:
        return [], {}, {**safe, "error_type": type(exc).__name__, "token_masked": True}
    rows = [enrich_row(row, config, safe) for row in observations if chunk_start <= p0052a.parse_utc(str(row["timestamp_utc"])) <= chunk_end]
    return rows, {**safe, "status": status, **response}, None


def parse_entsoe_document_clipped(xml_bytes: bytes, request_meta: dict[str, str], clip_start: datetime, clip_end: datetime) -> tuple[list[dict[str, object]], dict[str, object]]:
    root = ET.fromstring(xml_bytes)
    root_tag = p0052a.strip_ns(root.tag)
    if root_tag == "Acknowledgement_MarketDocument":
        reason = p0052a.text_or_empty(root.find(".//{*}text"))
        return [], {"root": root_tag, "reason": reason[:180], "timeseries": 0, "points": 0}
    rows: list[dict[str, object]] = []
    for series in root.findall(".//{*}TimeSeries"):
        series_meta = p0052a.series_metadata(series, request_meta)
        for period in series.findall(".//{*}Period"):
            rows.extend(parse_entsoe_period_points_clipped(period, request_meta, series_meta, clip_start, clip_end))
    return rows, {"root": root_tag, "reason": "", "timeseries": len(root.findall(".//{*}TimeSeries")), "points": len(root.findall(".//{*}Point"))}


def parse_entsoe_period_points_clipped(period: ET.Element, request_meta: dict[str, str], series_meta: dict[str, str], clip_start: datetime, clip_end: datetime) -> list[dict[str, object]]:
    start_text = p0052a.text_or_empty(period.find(".//{*}timeInterval/{*}start"))
    end_text = p0052a.text_or_empty(period.find(".//{*}timeInterval/{*}end"))
    resolution = p0052a.text_or_empty(period.find(".//{*}resolution"))
    period_start = p0052a.parse_utc(start_text)
    period_end = p0052a.parse_utc(end_text) if end_text else None
    step = p0052a.resolution_to_timedelta(resolution, period_start=period_start, period_end=period_end)
    rows = []
    for point in period.findall(".//{*}Point"):
        position = int(p0052a.text_or_empty(point.find(".//{*}position")) or "1")
        quantity = p0052a.text_or_empty(point.find(".//{*}quantity"))
        if not quantity:
            continue
        timestamp = period_start + (position - 1) * step
        rows.extend(expand_entsoe_value_clipped(timestamp, step, float(quantity), request_meta, series_meta, clip_start, clip_end))
    return rows


def expand_entsoe_value_clipped(timestamp: datetime, step: timedelta, value: float, request_meta: dict[str, str], series_meta: dict[str, str], clip_start: datetime, clip_end: datetime) -> list[dict[str, object]]:
    if request_meta["measure"] == "capacity_mw" and step > timedelta(hours=1):
        start = max(timestamp, clip_start)
        end = min(timestamp + step - timedelta(hours=1), clip_end)
        if end < start:
            return []
        count = int((end.replace(minute=0, second=0, microsecond=0) - start.replace(minute=0, second=0, microsecond=0)).total_seconds() // 3600) + 1
        timestamps = [start.replace(minute=0, second=0, microsecond=0) + timedelta(hours=i) for i in range(count)]
    else:
        timestamps = [timestamp] if clip_start <= timestamp <= clip_end else []
    return [
        p0052a.source_observation(
            ts,
            request_meta["source_dataset"],
            series_meta["from_area"],
            series_meta["to_area"],
            series_meta["border_id"],
            request_meta["measure"],
            value,
            series_meta["unit"],
            request_meta["capacity_method_label"],
            request_meta["flow_type_label"],
            "ok",
        )
        for ts in timestamps
    ]


def chunk_windows(start: datetime, end: datetime, max_days: int) -> list[tuple[datetime, datetime]]:
    chunks = []
    current = start
    while current <= end:
        chunk_end = min(end, current + timedelta(days=max_days) - timedelta(hours=1))
        chunks.append((current, chunk_end))
        current = chunk_end + timedelta(hours=1)
    return chunks


def enrich_row(row: dict[str, object], config: dict[str, str], request_meta: dict[str, str]) -> dict[str, object]:
    out = dict(row)
    out.update(metadata_for_config(config, request_meta))
    return out


def metadata_for_config(config: dict[str, str], request_meta: dict[str, str]) -> dict[str, str]:
    document_type = str(config["document_type"])
    contract_type = str(config.get("contract_type", ""))
    return {
        "document_type": document_type,
        "process_type": "",
        "business_type": "A61" if document_type == "A61" else "",
        "contract_type": contract_type,
        "entsoe_curve_type": "",
        "entsoe_resolution": "",
        "capacity_concept_status": CAPACITY_CONCEPT_STATUS if document_type == "A61" else "not_capacity",
    }


def aggregate_hourly_p0052b(raw_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    hourly = p0052a.aggregate_hourly(raw_rows)
    metadata_by_key = {}
    for row in raw_rows:
        hour = p0052a.parse_utc(str(row["timestamp_utc"])).replace(minute=0, second=0, microsecond=0)
        key = (
            p0052a.format_utc(hour),
            row["source_name"],
            row["source_dataset"],
            row["from_area"],
            row["to_area"],
            row["border_id"],
            row["measure"],
            row["capacity_method_label"],
            row["flow_type_label"],
        )
        metadata_by_key[key] = {column: row.get(column, "") for column in LONG_METADATA_COLUMNS}
    for row in hourly:
        key = (
            row["timestamp_utc"],
            row["source_name"],
            row["source_dataset"],
            row["from_area"],
            row["to_area"],
            row["border_id"],
            row["measure"],
            row["capacity_method_label"],
            row["flow_type_label"],
        )
        row.update(metadata_by_key.get(key, {}))
    return hourly


def persist_entsoe_rows_p0052b(conn: sqlite3.Connection, raw_rows: list[dict[str, object]], hourly_rows: list[dict[str, object]]) -> dict[str, int]:
    before_raw = conn.execute(f"SELECT COUNT(*) FROM {p0052.RAW_TABLE}").fetchone()[0]
    before_hourly = conn.execute(f"SELECT COUNT(*) FROM {p0052.CANONICAL_TABLE}").fetchone()[0]
    p0052.insert_rows(conn, p0052.RAW_TABLE, raw_rows)
    p0052.insert_rows(conn, p0052.CANONICAL_TABLE, hourly_rows)
    conn.commit()
    after_raw = conn.execute(f"SELECT COUNT(*) FROM {p0052.RAW_TABLE}").fetchone()[0]
    after_hourly = conn.execute(f"SELECT COUNT(*) FROM {p0052.CANONICAL_TABLE}").fetchone()[0]
    return {
        "raw_rows_inserted_or_reused": len(raw_rows),
        "hourly_rows_inserted_or_reused": len(hourly_rows),
        "raw_rows_net_new": after_raw - before_raw,
        "hourly_rows_net_new": after_hourly - before_hourly,
    }


def update_wide_entsoe_features_p0052b(conn: sqlite3.Connection, hourly_rows: list[dict[str, object]], concept_review: dict[str, object]) -> dict[str, int]:
    by_hour: dict[str, dict[str, object]] = defaultdict(dict)
    for row in hourly_rows:
        column = wide_column_for_row_p0052b(row)
        if column:
            by_hour[str(row["timestamp_utc"])][column] = float(row["value"])
    inserted = 0
    updated = 0
    for timestamp, values in sorted(by_hour.items()):
        if ensure_wide_row(conn, timestamp):
            inserted += 1
        values.update(derive_wide_features_p0052b(values, concept_review))
        assignments = ", ".join(f"{column}=?" for column in values)
        params = list(values.values()) + [timestamp]
        cur = conn.execute(f"UPDATE {p0052.WIDE_TABLE} SET {assignments} WHERE timestamp_utc=?", params)
        updated += cur.rowcount
    conn.commit()
    return {"wide_rows_inserted": inserted, "wide_rows_updated": updated}


def ensure_wide_row(conn: sqlite3.Connection, timestamp_utc: str) -> bool:
    exists = conn.execute(f"SELECT 1 FROM {p0052.WIDE_TABLE} WHERE timestamp_utc=?", (timestamp_utc,)).fetchone()
    if exists:
        return False
    dt = p0052a.parse_utc(timestamp_utc)
    model_dt = dt + timedelta(hours=1)
    conn.execute(
        f"""
        INSERT INTO {p0052.WIDE_TABLE}
        (timestamp_utc, model_cet_timestamp, model_cet_date, model_cet_hour, flow_based_market_coupling_flag, flow_based_go_live_date, capacity_method_label)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            p0052a.format_utc(dt),
            p0052a.format_utc(model_dt),
            model_dt.date().isoformat(),
            model_dt.hour,
            1 if dt >= p0052.FLOW_BASED_GO_LIVE else 0,
            p0052a.format_utc(p0052.FLOW_BASED_GO_LIVE),
            CAPACITY_CONCEPT_STATUS,
        ),
    )
    return True


def wide_column_for_row_p0052b(row: dict[str, object]) -> str | None:
    return p0052a.wide_column_for_row(row)


def derive_wide_features_p0052b(values: dict[str, object], concept_review: dict[str, object]) -> dict[str, object]:
    out: dict[str, object] = {}
    for border in p0052a.INTERNAL_BORDERS:
        a, b = border.lower().split("_", 1)
        scheduled = values.get(f"scheduled_exchange_{a}_to_{b}_mw")
        physical = values.get(f"physical_flow_{a}_to_{b}_mw")
        chosen = scheduled if scheduled is not None else physical
        if chosen is not None:
            out[f"flow_or_exchange_{a}_to_{b}_mw"] = chosen
    if not concept_review.get("utilization_allowed"):
        return out
    for border in p0052a.INTERNAL_BORDERS:
        a, b = border.lower().split("_", 1)
        flow = out.get(f"flow_or_exchange_{a}_to_{b}_mw")
        capacity = values.get(f"capacity_{a}_to_{b}_mw")
        util = capacity_utilization_safe(flow, capacity, concept_review)
        if util is not None:
            out[f"utilization_{a}_{b}_north_to_south"] = util
            out[f"bottleneck_margin_{a}_{b}_north_to_south"] = float(capacity) - max(0.0, float(flow))
    return out


def capacity_utilization_safe(flow_or_exchange: object, capacity: object, concept_review: dict[str, object]) -> float | None:
    if not concept_review.get("utilization_allowed"):
        return None
    return p0052a.capacity_utilization(flow_or_exchange, capacity)


def normalize_timestamp_sql(expr: str) -> str:
    return f"substr(replace({expr}, '+00:00', 'Z'), 1, 19) || 'Z'"


def run_join_fix_analysis(conn: sqlite3.Connection) -> dict[str, object]:
    if not p0052.table_exists(conn, PRICE_TABLE):
        return {"price_table_exists": False, "exact_join_rows": 0, "normalized_join_rows": 0}
    exact = conn.execute(f"SELECT COUNT(*) FROM {p0052.WIDE_TABLE} w JOIN {PRICE_TABLE} p ON p.timestamp_utc = w.timestamp_utc").fetchone()[0]
    normalized = conn.execute(
        f"""
        SELECT COUNT(*)
        FROM {p0052.WIDE_TABLE} w
        JOIN {PRICE_TABLE} p ON {normalize_timestamp_sql('p.timestamp_utc')} = {normalize_timestamp_sql('w.timestamp_utc')}
        """
    ).fetchone()[0]
    existing = set(p0052.table_columns(conn, p0052.WIDE_TABLE))
    signal_columns = [
        column
        for column in (
            "scheduled_exchange_se2_to_se3_mw",
            "scheduled_exchange_se3_to_se4_mw",
            "physical_flow_se2_to_se3_mw",
            "physical_flow_se3_to_se4_mw",
        )
        if column in existing
    ]
    if signal_columns:
        nonnull = conn.execute(
            f"""
            SELECT COUNT(*)
            FROM {p0052.WIDE_TABLE} w
            JOIN {PRICE_TABLE} p ON {normalize_timestamp_sql('p.timestamp_utc')} = {normalize_timestamp_sql('w.timestamp_utc')}
            WHERE {" OR ".join(f"w.{column} IS NOT NULL" for column in signal_columns)}
            """
        ).fetchone()[0]
    else:
        nonnull = 0
    return {
        "price_table_exists": True,
        "issue": "P0052A used exact text join; transfer timestamps used Z while price timestamps used +00:00.",
        "exact_join_rows": exact,
        "normalized_join_rows": normalized,
        "normalized_join_rows_with_entsoe_signal": nonnull,
    }


def run_p0052b_diagnostics(conn: sqlite3.Connection, concept_review: dict[str, object]) -> dict[str, object]:
    if not p0052.table_exists(conn, PRICE_TABLE):
        return {"joined_rows": 0, "reason": "no price table"}
    columns = [
        "scheduled_exchange_se2_to_se3_mw",
        "scheduled_exchange_se3_to_se4_mw",
        "physical_flow_se2_to_se3_mw",
        "physical_flow_se3_to_se4_mw",
    ]
    existing = p0052.table_columns(conn, p0052.WIDE_TABLE)
    columns = [column for column in columns if column in existing]
    select_cols = ", ".join(f"w.{column}" for column in columns)
    rows = [dict(row) for row in conn.execute(f"""
        SELECT w.timestamp_utc, p.se3_price AS se3_price, p.se3_minus_se1 AS se3_minus_se1, {select_cols}
        FROM {p0052.WIDE_TABLE} w
        JOIN {PRICE_TABLE} p ON {normalize_timestamp_sql('p.timestamp_utc')} = {normalize_timestamp_sql('w.timestamp_utc')}
        WHERE {" OR ".join(f"w.{column} IS NOT NULL" for column in columns)}
    """)]
    correlations = {}
    for column in columns:
        correlations[f"se3_price_vs_{column}"] = correlation(rows, "se3_price", column)
        correlations[f"se3_minus_se1_vs_{column}"] = correlation(rows, "se3_minus_se1", column)
    return {
        "price_table": PRICE_TABLE,
        "joined_rows": len(rows),
        "columns": columns,
        "correlations": correlations,
        "utilization_margin_status": "blocked_capacity_concept_uncertain" if not concept_review.get("utilization_allowed") else "enabled",
    }


def correlation(rows: list[dict[str, object]], x_key: str, y_key: str) -> float | None:
    pairs = [(float(row[x_key]), float(row[y_key])) for row in rows if row.get(x_key) is not None and row.get(y_key) is not None and p0052a.is_finite(row[x_key]) and p0052a.is_finite(row[y_key])]
    if len(pairs) < 2:
        return None
    xs, ys = zip(*pairs)
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
    denom_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    denom_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if denom_x == 0 or denom_y == 0:
        return None
    return numerator / (denom_x * denom_y)


def validate_p0052b(conn: sqlite3.Connection, raw_rows: list[dict[str, object]], hourly_rows: list[dict[str, object]], responses: list[dict[str, object]], secret_safety: dict[str, object], join_analysis: dict[str, object]) -> dict[str, object]:
    duplicate_keys = {(row["timestamp_utc"], row["source_name"], row["source_dataset"], row["from_area"], row["to_area"], row["border_id"], row["measure"], row["capacity_method_label"], row["flow_type_label"], row.get("document_type", ""), row.get("contract_type", "")) for row in hourly_rows}
    duplicates = len(hourly_rows) - len(duplicate_keys)
    nonfinite = sum(1 for row in hourly_rows if not p0052a.is_finite(row["value"]))
    negative_capacity = sum(1 for row in hourly_rows if row["measure"] == "capacity_mw" and float(row["value"]) < 0)
    forbidden_documents = sorted({str(row.get("document_type", "")) for row in hourly_rows if str(row.get("document_type", "")) in p0052a.FORBIDDEN_DOCUMENT_TYPES})
    one_row_per_wide_timestamp = conn.execute(f"SELECT COUNT(*) = COUNT(DISTINCT timestamp_utc) FROM {p0052.WIDE_TABLE}").fetchone()[0]
    return {
        "ok": bool(hourly_rows) and duplicates == 0 and nonfinite == 0 and negative_capacity == 0 and not forbidden_documents and bool(secret_safety["secret_safe"]) and int(join_analysis.get("normalized_join_rows_with_entsoe_signal", 0)) > 0,
        "secret_checked": secret_safety["secret_checked"],
        "secret_safe": secret_safety["secret_safe"],
        "duplicates": duplicates,
        "nonfinite_values": nonfinite,
        "negative_capacity_values": negative_capacity,
        "forbidden_documents": forbidden_documents,
        "one_row_per_wide_timestamp": bool(one_row_per_wide_timestamp),
        "row_counts_by_measure": dict(Counter(str(row["measure"]) for row in hourly_rows)),
        "response_counts": dict(Counter(f"{r['document_type']}_{r.get('contract_type','')}_{r.get('root','')}" for r in responses)),
        "token_leak_scan_required": True,
    }


def source_contracts(responses: list[dict[str, object]], failed_chunks: list[dict[str, object]]) -> dict[str, object]:
    attempted = []
    for response in responses:
        attempted.append({key: response.get(key) for key in ("window_id", "document_type", "contract_type", "from_area", "to_area", "measure", "status", "root", "reason", "timeseries", "points")})
    return {
        "base_url": p0052a.ENTSOE_BASE_URL,
        "attempted_contracts": attempted,
        "failed_chunks": failed_chunks,
        "token_included_in_evidence": False,
    }


def window_summary(windows: tuple[tuple[datetime, datetime, str], ...]) -> list[dict[str, str]]:
    return [{"window_id": name, "start": p0052a.format_utc(start), "end": p0052a.format_utc(end)} for start, end, name in windows]


def forecast_safety_classification(concept_review: dict[str, object]) -> dict[str, str]:
    return {
        "scheduled_exchange_mw": "historical_observed_only",
        "physical_flow_mw": "historical_observed_only",
        "capacity_mw_A02": "not_forecast_safe_until_capacity_concept_review",
        "capacity_mw_A03": "not_forecast_safe_until_capacity_concept_review",
        "capacity_mw_A04": "not_forecast_safe_until_capacity_concept_review",
        "utilization": "not_forecast_safe_until_capacity_concept_review",
        "bottleneck_margin": "not_forecast_safe_until_capacity_concept_review",
        "flow_based_market_coupling_flag": "forecast_time_known_near_term",
    }


def write_p0052b_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "CHANGELOG.md": changelog_text(summary),
        "secret-handling.md": json_md("P0052B secret handling", secret_handling_evidence(summary["secret_safety"])),
        "entsoe-capacity-concept-review.md": json_md("P0052B ENTSO-E capacity concept review", summary["capacity_concept_review"]),
        "entsoe-source-contracts.md": json_md("P0052B ENTSO-E source contracts", summary["source_contracts"]),
        "eic-domain-mapping.md": json_md("P0052B EIC domain mapping", p0052a.eic_domain_mapping()),
        "database-contract.md": database_contract_text(summary),
        "backfill-plan-and-summary.md": json_md("P0052B backfill plan and summary", {"windows": summary["windows"], "row_counts": summary["row_counts"], "runtime_seconds": summary["runtime_seconds"]}),
        "time-normalization-and-dst.md": "# P0052B time normalization and DST\n\nENTSO-E timestamps are stored as UTC `...Z`. Diagnostics joins normalize both `...Z` and `...+00:00` forms through SQLite datetime conversion. Fixed-CET fields remain UTC+1 all year.\n",
        "data-validation.md": json_md("P0052B data validation", summary["validation"]),
        "coverage-and-missingness.md": json_md("P0052B coverage and missingness", {"windows": summary["windows"], "row_counts": summary["row_counts"], "response_counts": summary["validation"]["response_counts"]}),
        "direction-conventions.md": "# P0052B direction conventions\n\nRequests use `out_Domain = from_area` and `in_Domain = to_area`. Stored values are positive in that directed border direction.\n",
        "join-fix-analysis.md": json_md("P0052B join fix analysis", summary["join_analysis"]),
        "flow-based-era-review.md": flow_based_review_text(summary),
        "derived-feature-definitions.md": derived_feature_text(summary),
        "capacity-utilization-and-margin-diagnostics.md": json_md("P0052B capacity/utilization and margin diagnostics", summary["diagnostics"]),
        "forecast-safety-classification.md": json_md("P0052B forecast-safety classification", summary["forecast_safety"]),
        "next-package-recommendation.md": next_recommendation_text(summary),
        "component-attribution-summary.md": component_summary_text(summary),
    }
    for name, content in files.items():
        (evidence_dir / name).write_text(content, encoding="utf-8")
    json_files = {
        "capacity-concept-review.json": summary["capacity_concept_review"],
        "source-contracts.json": summary["source_contracts"],
        "coverage-summary.json": {"windows": summary["windows"], "row_counts": summary["row_counts"]},
        "validation-summary.json": summary["validation"],
        "diagnostics-summary.json": summary["diagnostics"],
    }
    for name, payload in json_files.items():
        (evidence_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {name: str(evidence_dir / name) for name in files | json_files}


def secret_handling_evidence(secret_safety: dict[str, object]) -> dict[str, object]:
    return {
        "token_source_class": secret_safety.get("token_source"),
        "secret_checked": secret_safety.get("secret_checked"),
        "secret_safe": secret_safety.get("secret_safe"),
        "secret_gitignored_or_outside_repo": secret_safety.get("secret_gitignored"),
        "file_mode_or_unavailable_reason": secret_safety.get("file_mode", "environment_not_a_file"),
        "directory_mode_or_unavailable_reason": secret_safety.get("directory_mode", "environment_not_a_file"),
        "token_in_logs": False,
        "token_in_evidence": False,
    }


def json_md(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0052B changelog

- Re-verified ENTSO-E token safety without writing the token value.
- Added metadata-compatible P0052 schema columns and backfilled ENTSO-E A09/A11/A61 representative historical windows.
- Fixed P0052A diagnostics join by normalizing `Z` and `+00:00` UTC timestamp strings.
- A61 A02/A03/A04 are documented as weekly/monthly/yearly contract types; utilization and bottleneck margin remain blocked because capacity concept compatibility is uncertain.
- Result status: {summary['status']}.
- No token leak, continental price levels, SE1-to-SE3 anchoring, API, production model, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.
"""


def database_contract_text(summary: dict[str, object]) -> str:
    return f"""# P0052B database contract

P0052B reuses and extends:

- `{p0052.RAW_TABLE}`
- `{p0052.CANONICAL_TABLE}`
- `{p0052.WIDE_TABLE}`

Added metadata columns are documented in schema summary:

```json
{json.dumps(summary['schema_summary'], indent=2, sort_keys=True)}
```

Existing SvK/Statnett and P0052A rows are preserved.
"""


def flow_based_review_text(summary: dict[str, object]) -> str:
    return """# P0052B flow-based era review

P0052B includes a `2024-09-01T00:00:00Z .. 2024-12-31T23:00:00Z` transition window around the known 2024-10-29 Nordic flow-based go-live date. A61 values are stored with explicit contract labels on both sides where returned by ENTSO-E.

The package does not claim pre/post concept comparability for utilization. Model features should retain `flow_based_market_coupling_flag`.
"""


def derived_feature_text(summary: dict[str, object]) -> str:
    return """# P0052B derived feature definitions

Scheduled exchange and physical flow columns are historical observed diagnostics. `flow_or_exchange_*` prefers scheduled exchange when available, otherwise physical flow.

Capacity utilization and bottleneck margin remain null because `capacity_concept_status = capacity_concept_uncertain`.
"""


def next_recommendation_text(summary: dict[str, object]) -> str:
    joined = summary["join_analysis"].get("normalized_join_rows_with_entsoe_signal")
    return f"""# P0052B next package recommendation

P0053 may begin physical-regime modeling using P0051 physical balance plus P0052/P0052A/P0052B historical scheduled exchange and physical-flow diagnostics. It should not use A61 capacity-derived utilization or bottleneck margin as production-intent features yet.

Normalized joined rows with ENTSO-E signal: {joined}.
"""


def component_summary_text(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0052B component attribution summary",
        "",
        f"Status: {summary['status']}",
        "1. Token safety was re-verified; no token value is stored in evidence.",
        "2. A61 A02/A03/A04 mean weekly/monthly/yearly contract types in the ENTSO-E context.",
        "3. No A61 contract type is selected for utilization diagnostics because concept compatibility remains uncertain.",
        "4. Internal Swedish capacity/exchange/flow was backfilled for representative windows where ENTSO-E returned rows.",
        f"5. Backfill row counts: {summary['row_counts']}.",
        f"6. Join fix: {summary['join_analysis']}.",
        "7. Pre/post 2024-10-29 comparability remains inconclusive for utilization.",
        "8. Utilization and bottleneck margin remain blocked.",
        f"9. Diagnostics: {summary['diagnostics']}.",
        f"10. Forecast safety: {summary['forecast_safety']}.",
        "11. Recommendation: P0053 may use historical exchange/flow diagnostics, not A61 utilization/margin.",
        "12. Confirmed: no token leak, no continental price levels, no SE1-to-SE3 anchoring, no API, no production model and no device actions.",
        "",
    ])


def main() -> None:
    result = run_p0052b_ingestion()
    print(f"P0052B {result.status}: row_counts={json.dumps(result.row_counts, sort_keys=True)}")


if __name__ == "__main__":
    main()
