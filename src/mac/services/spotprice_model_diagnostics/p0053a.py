"""P0053A ENTSO-E A09/A11 internal Swedish flow/exchange backfill."""

from __future__ import annotations

from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
import json
import math
import sqlite3
import time
import urllib.error

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0052a, p0052b


PACKAGE_ID = "P0053A"
EVIDENCE_DIR = Path("requirements/package-runs/P0053A")
PRICE_TABLE = "se3_se1_demand_response_analysis_v1"
ANALYSIS_TABLE = "physical_balance_flow_exchange_analysis_v1"
TARGET_START = datetime(2022, 5, 29, 23, tzinfo=timezone.utc)
TARGET_END = datetime(2026, 5, 25, 22, tzinfo=timezone.utc)
WARN_MIN_START = datetime(2024, 1, 1, tzinfo=timezone.utc)
DERIVED_WIDE_COLUMNS = {
    "net_scheduled_exchange_se1_se2_mw": "REAL",
    "net_scheduled_exchange_se2_se3_mw": "REAL",
    "net_scheduled_exchange_se3_se4_mw": "REAL",
    "net_physical_flow_se1_se2_mw": "REAL",
    "net_physical_flow_se2_se3_mw": "REAL",
    "net_physical_flow_se3_se4_mw": "REAL",
    "north_to_south_scheduled_exchange_min": "REAL",
    "north_to_south_scheduled_exchange_mean": "REAL",
    "north_to_south_physical_flow_min": "REAL",
    "north_to_south_physical_flow_mean": "REAL",
    "se3_import_from_se2_scheduled_exchange_mw": "REAL",
    "se4_import_from_se3_scheduled_exchange_mw": "REAL",
    "se3_import_from_se2_physical_flow_mw": "REAL",
    "se4_import_from_se3_physical_flow_mw": "REAL",
    "southward_exchange_pressure": "REAL",
    "southward_physical_flow_pressure": "REAL",
}
ANALYSIS_COLUMNS = (
    ("timestamp_utc", "TEXT PRIMARY KEY"),
    ("model_cet_timestamp", "TEXT"),
    ("model_cet_date", "TEXT"),
    ("model_cet_hour", "INTEGER"),
    ("flow_based_market_coupling_flag", "INTEGER"),
    ("se1_price", "REAL"),
    ("se3_price", "REAL"),
    ("se3_minus_se1", "REAL"),
    ("consumption_se1", "REAL"),
    ("consumption_se2", "REAL"),
    ("consumption_se3", "REAL"),
    ("consumption_se4", "REAL"),
    ("production_se1", "REAL"),
    ("production_se2", "REAL"),
    ("production_se3", "REAL"),
    ("production_se4", "REAL"),
    ("net_load_se1", "REAL"),
    ("net_load_se2", "REAL"),
    ("net_load_se3", "REAL"),
    ("net_load_se4", "REAL"),
    *tuple((column, "REAL") for column in DERIVED_WIDE_COLUMNS),
)


@dataclass(frozen=True)
class P0053AResult:
    status: str
    row_counts: dict[str, object]
    evidence: dict[str, str]


def run_p0053a_backfill(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
    start: datetime = TARGET_START,
    end: datetime = TARGET_END,
    workers: int = 8,
    fetch: bool = True,
) -> P0053AResult:
    started = time.monotonic()
    token_source = p0052a.load_entsoe_token()
    secret_safety = p0052a.verify_secret_safety(token_source)
    if not secret_safety["secret_safe"]:
        raise RuntimeError("P0053A secret safety check failed")
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        p0052a.ensure_p0052_tables_exist(conn)
        schema_summary = ensure_p0053a_schema(conn)
        tasks, plan = plan_missing_fetch_tasks(conn, start, end) if fetch else ([], {"fetch_skipped": True, "reason": "operator_requested_evidence_refresh_without_network_fetch", "documents": [config["document_type"] for config in a09_a11_configs()], "a61_requested": False})
        raw_rows, responses, failed_chunks = fetch_missing_entsoe_rows(token_source.token, tasks, workers=workers) if fetch else ([], [], [])
        hourly_rows = p0052b.aggregate_hourly_p0052b(raw_rows)
        persistence = p0052b.persist_entsoe_rows_p0052b(conn, raw_rows, hourly_rows)
        canonical_rows = load_a09_a11_hourly_rows(conn, start, end)
        wide_update = update_wide_flow_exchange_features(conn, canonical_rows)
        joined = create_joined_analysis_dataset(conn, start, end)
        validation = validate_p0053a(conn, start, end, secret_safety, tasks, raw_rows, hourly_rows, failed_chunks, joined)
        diagnostics = run_p0053a_diagnostics(conn, start, end)
    status = "PASS" if validation["full_target_net_complete"] and validation["ok"] else "WARN" if validation["warn_minimum_net_substantial"] and validation["ok"] else "STOP"
    summary = {
        "status": status,
        "secret_safety": secret_safety,
        "schema_summary": schema_summary,
        "ranges": {"requested_start": p0052a.format_utc(start), "requested_end": p0052a.format_utc(end), "warn_minimum_start": p0052a.format_utc(WARN_MIN_START)},
        "backfill_plan": plan,
        "source_contracts": source_contracts(responses, failed_chunks),
        "row_counts": {
            "fetch_tasks_planned": len(tasks),
        "raw_rows_fetched": len(raw_rows),
        "hourly_rows_fetched": len(hourly_rows),
            "canonical_a09_a11_rows_in_range": len(canonical_rows),
            **persistence,
            **wide_update,
            **joined,
        },
        "validation": validation,
        "diagnostics": diagnostics,
        "forecast_safety": forecast_safety_classification(),
        "runtime_seconds": time.monotonic() - started,
        "forbidden_paths": p0052.FORBIDDEN_PRODUCTION_PATHS,
    }
    evidence = write_p0053a_evidence(Path(evidence_dir), summary)
    return P0053AResult(status=status, row_counts=summary["row_counts"], evidence=evidence)


def a09_a11_configs() -> tuple[dict[str, str], ...]:
    return tuple(config for config in p0052a.DOCUMENT_CONFIGS if config["document_type"] in {"A09", "A11"})


def monthly_chunks(start: datetime, end: datetime) -> list[tuple[datetime, datetime]]:
    start = p0052a.parse_utc(start).replace(minute=0, second=0, microsecond=0)
    end = p0052a.parse_utc(end).replace(minute=0, second=0, microsecond=0)
    chunks: list[tuple[datetime, datetime]] = []
    current = start
    while current <= end:
        if current.month == 12:
            next_month = current.replace(year=current.year + 1, month=1, day=1, hour=0)
        else:
            next_month = current.replace(month=current.month + 1, day=1, hour=0)
        chunk_end = min(end, next_month - timedelta(hours=1))
        chunks.append((current, chunk_end))
        current = chunk_end + timedelta(hours=1)
    return chunks


def plan_missing_fetch_tasks(conn: sqlite3.Connection, start: datetime, end: datetime) -> tuple[list[dict[str, object]], dict[str, object]]:
    tasks: list[dict[str, object]] = []
    skipped = 0
    for chunk_start, chunk_end in monthly_chunks(start, end):
        expected_hours = int((chunk_end - chunk_start).total_seconds() // 3600) + 1
        for config in a09_a11_configs():
            for border in p0052a.INTERNAL_BORDERS:
                left, right = border.split("_", 1)
                for from_area, to_area in ((left, right), (right, left)):
                    count = existing_hour_count(conn, config, from_area, to_area, chunk_start, chunk_end)
                    if count >= expected_hours:
                        skipped += 1
                        continue
                    params, safe = p0052a.build_entsoe_params(config, from_area, to_area, chunk_start, chunk_end)
                    tasks.append({"params": params, "safe": safe, "config": config, "start": chunk_start, "end": chunk_end, "existing_hours": count, "expected_hours": expected_hours})
    return tasks, {
        "requested_chunks": len(monthly_chunks(start, end)),
        "tasks_to_fetch": len(tasks),
        "tasks_skipped_complete": skipped,
        "documents": [config["document_type"] for config in a09_a11_configs()],
        "a61_requested": False,
    }


def existing_hour_count(conn: sqlite3.Connection, config: dict[str, str], from_area: str, to_area: str, start: datetime, end: datetime) -> int:
    return int(conn.execute(
        f"""
        SELECT COUNT(DISTINCT timestamp_utc)
        FROM {p0052.CANONICAL_TABLE}
        WHERE timestamp_utc BETWEEN ? AND ?
          AND source_dataset=?
          AND from_area=?
          AND to_area=?
          AND measure=?
        """,
        (p0052a.format_utc(start), p0052a.format_utc(end), config["source_dataset"], from_area, to_area, config["measure"]),
    ).fetchone()[0])


def fetch_missing_entsoe_rows(token: str, tasks: list[dict[str, object]], *, workers: int) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    raw_rows: list[dict[str, object]] = []
    responses: list[dict[str, object]] = []
    failed_chunks: list[dict[str, object]] = []
    if not tasks:
        return raw_rows, responses, failed_chunks
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        future_map = {pool.submit(fetch_task, token, task): task for task in tasks}
        for completed, future in enumerate(as_completed(future_map), start=1):
            rows, response, failure = future.result()
            if failure:
                failed_chunks.append(failure)
            else:
                raw_rows.extend(rows)
                responses.append(response)
            if completed % 10 == 0 or completed == len(tasks):
                print(f"P0053A fetch progress {completed}/{len(tasks)}", flush=True)
    return raw_rows, responses, failed_chunks


def fetch_task(token: str, task: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, object], dict[str, object] | None]:
    safe = dict(task["safe"])
    config = dict(task["config"])
    chunk_start = p0052a.parse_utc(task["start"])
    chunk_end = p0052a.parse_utc(task["end"])
    try:
        xml_bytes, status = p0052a.fetch_entsoe_document(token, dict(task["params"]), timeout=15.0)
        observations, response = p0052b.parse_entsoe_document_clipped(xml_bytes, safe, chunk_start, chunk_end)
    except (urllib.error.URLError, ValueError, sqlite3.Error) as exc:
        return [], {}, {**safe, "error_type": type(exc).__name__, "token_masked": True}
    rows = [
        p0052b.enrich_row(row, config, safe)
        for row in observations
        if chunk_start <= p0052a.parse_utc(str(row["timestamp_utc"])) <= chunk_end
    ]
    return rows, {**safe, "status": status, **response}, None


def ensure_p0053a_schema(conn: sqlite3.Connection) -> dict[str, object]:
    summary = p0052b.ensure_p0052b_schema(conn)
    added = summary.setdefault("added_columns", {}).setdefault(p0052.WIDE_TABLE, [])
    existing = p0052.table_columns(conn, p0052.WIDE_TABLE)
    for column, column_type in DERIVED_WIDE_COLUMNS.items():
        if column not in existing:
            conn.execute(f"ALTER TABLE {p0052.WIDE_TABLE} ADD COLUMN {column} {column_type}")
            added.append(column)
    conn.commit()
    return summary


def load_a09_a11_hourly_rows(conn: sqlite3.Connection, start: datetime, end: datetime) -> list[dict[str, object]]:
    datasets = [config["source_dataset"] for config in a09_a11_configs()]
    placeholders = ", ".join("?" for _ in datasets)
    return [dict(row) for row in conn.execute(
        f"""
        SELECT *
        FROM {p0052.CANONICAL_TABLE}
        WHERE timestamp_utc BETWEEN ? AND ?
          AND source_dataset IN ({placeholders})
        ORDER BY timestamp_utc, source_dataset, from_area, to_area
        """,
        [p0052a.format_utc(start), p0052a.format_utc(end), *datasets],
    )]


def derive_flow_exchange_features(values: dict[str, object]) -> dict[str, object]:
    out: dict[str, object] = {}
    scheduled_nets: list[float] = []
    physical_nets: list[float] = []
    for border in p0052a.INTERNAL_BORDERS:
        a, b = border.lower().split("_", 1)
        scheduled = net(values.get(f"scheduled_exchange_{a}_to_{b}_mw"), values.get(f"scheduled_exchange_{b}_to_{a}_mw"))
        physical = net(values.get(f"physical_flow_{a}_to_{b}_mw"), values.get(f"physical_flow_{b}_to_{a}_mw"))
        if scheduled is not None:
            out[f"net_scheduled_exchange_{a}_{b}_mw"] = scheduled
            scheduled_nets.append(scheduled)
        if physical is not None:
            out[f"net_physical_flow_{a}_{b}_mw"] = physical
            physical_nets.append(physical)
    if scheduled_nets:
        out["north_to_south_scheduled_exchange_min"] = min(scheduled_nets)
        out["north_to_south_scheduled_exchange_mean"] = sum(scheduled_nets) / len(scheduled_nets)
    if physical_nets:
        out["north_to_south_physical_flow_min"] = min(physical_nets)
        out["north_to_south_physical_flow_mean"] = sum(physical_nets) / len(physical_nets)
    for prefix in ("scheduled_exchange", "physical_flow"):
        se2_se3 = out.get(f"net_{prefix}_se2_se3_mw")
        se3_se4 = out.get(f"net_{prefix}_se3_se4_mw")
        if se2_se3 is not None:
            out[f"se3_import_from_se2_{prefix}_mw"] = max(0.0, float(se2_se3))
        if se3_se4 is not None:
            out[f"se4_import_from_se3_{prefix}_mw"] = max(0.0, float(se3_se4))
        if se2_se3 is not None or se3_se4 is not None:
            out[f"southward_{'exchange' if prefix == 'scheduled_exchange' else 'physical_flow'}_pressure"] = max(0.0, float(se2_se3 or 0.0)) + max(0.0, float(se3_se4 or 0.0))
    return out


def net(forward: object, reverse: object) -> float | None:
    if forward is None and reverse is None:
        return None
    return float(forward or 0.0) - float(reverse or 0.0)


def update_wide_flow_exchange_features(conn: sqlite3.Connection, hourly_rows: list[dict[str, object]]) -> dict[str, int]:
    by_hour: dict[str, dict[str, object]] = defaultdict(dict)
    for row in hourly_rows:
        column = p0052a.wide_column_for_row(row)
        if column:
            by_hour[str(row["timestamp_utc"])][column] = float(row["value"])
    inserted = 0
    updated = 0
    for timestamp, values in sorted(by_hour.items()):
        if p0052b.ensure_wide_row(conn, timestamp):
            inserted += 1
        values.update(derive_flow_exchange_features(values))
        assignments = ", ".join(f"{column}=?" for column in values)
        cur = conn.execute(f"UPDATE {p0052.WIDE_TABLE} SET {assignments} WHERE timestamp_utc=?", [*values.values(), timestamp])
        updated += cur.rowcount
    conn.commit()
    return {"wide_rows_inserted": inserted, "wide_rows_updated": updated}


def create_joined_analysis_dataset(conn: sqlite3.Connection, start: datetime, end: datetime) -> dict[str, object]:
    conn.execute(f"DROP TABLE IF EXISTS {ANALYSIS_TABLE}")
    columns_sql = ", ".join(f"{name} {kind}" for name, kind in ANALYSIS_COLUMNS)
    conn.execute(f"CREATE TABLE {ANALYSIS_TABLE} ({columns_sql})")
    price_rows = load_price_rows(conn)
    physical_rows = load_physical_rows(conn)
    wide_columns = [name for name, _ in ANALYSIS_COLUMNS if name in p0052.table_columns(conn, p0052.WIDE_TABLE)]
    rows: list[dict[str, object]] = []
    for wide in conn.execute(
        f"SELECT {', '.join(wide_columns)} FROM {p0052.WIDE_TABLE} WHERE timestamp_utc BETWEEN ? AND ? ORDER BY timestamp_utc",
        (p0052a.format_utc(start), p0052a.format_utc(end)),
    ):
        row = dict(wide)
        ts = p0052.normalize_utc_text(row["timestamp_utc"])
        price = price_rows.get(ts)
        physical = physical_rows.get(ts)
        if not price or not physical:
            continue
        row.update(price)
        row.update(physical)
        rows.append({name: row.get(name) for name, _ in ANALYSIS_COLUMNS})
    p0052.insert_rows(conn, ANALYSIS_TABLE, rows)
    conn.commit()
    return {
        "analysis_rows": len(rows),
        "analysis_table": ANALYSIS_TABLE,
        "analysis_start": min((str(row["timestamp_utc"]) for row in rows), default=""),
        "analysis_end": max((str(row["timestamp_utc"]) for row in rows), default=""),
    }


def load_price_rows(conn: sqlite3.Connection) -> dict[str, dict[str, object]]:
    if not p0052.table_exists(conn, PRICE_TABLE):
        return {}
    columns = p0052.table_columns(conn, PRICE_TABLE)
    se3_price = "se3_price_eur_mwh" if "se3_price_eur_mwh" in columns else "se3_price"
    spread = "se3_minus_se1_eur_mwh" if "se3_minus_se1_eur_mwh" in columns else "se3_minus_se1"
    se1_price = "se1_price_eur_mwh" if "se1_price_eur_mwh" in columns else "se1_price"
    return {
        p0052.normalize_utc_text(row[0]): {"se1_price": row[1], "se3_price": row[2], "se3_minus_se1": row[3]}
        for row in conn.execute(f"SELECT timestamp_utc, {se1_price}, {se3_price}, {spread} FROM {PRICE_TABLE}")
    }


def load_physical_rows(conn: sqlite3.Connection) -> dict[str, dict[str, object]]:
    if not p0052.table_exists(conn, p0052.PHYSICAL_TABLE):
        return {}
    columns = [name for name, _ in ANALYSIS_COLUMNS if name in p0052.table_columns(conn, p0052.PHYSICAL_TABLE)]
    return {
        p0052.normalize_utc_text(row["timestamp_utc"]): dict(row)
        for row in conn.execute(f"SELECT {', '.join(columns)} FROM {p0052.PHYSICAL_TABLE}")
    }


def validate_p0053a(
    conn: sqlite3.Connection,
    start: datetime,
    end: datetime,
    secret_safety: dict[str, object],
    tasks: list[dict[str, object]],
    raw_rows: list[dict[str, object]],
    hourly_rows: list[dict[str, object]],
    failed_chunks: list[dict[str, object]],
    joined: dict[str, object],
) -> dict[str, object]:
    forbidden_task_docs = sorted({str(task["safe"]["document_type"]) for task in tasks if str(task["safe"]["document_type"]) != "A09" and str(task["safe"]["document_type"]) != "A11"})
    forbidden_row_docs = sorted({str(row.get("document_type", "")) for row in raw_rows + hourly_rows if str(row.get("document_type", "")) not in {"A09", "A11"}})
    duplicates = len(hourly_rows) - len({(r["timestamp_utc"], r["source_name"], r["source_dataset"], r["from_area"], r["to_area"], r["border_id"], r["measure"], r.get("document_type", "")) for r in hourly_rows})
    nonfinite = sum(1 for row in hourly_rows if not p0052a.is_finite(row["value"]))
    full = directional_coverage_summary(conn, start, end)
    warn = directional_coverage_summary(conn, max(start, WARN_MIN_START), end)
    full_net = net_feature_coverage_summary(conn, start, end)
    warn_net = net_feature_coverage_summary(conn, max(start, WARN_MIN_START), end)
    one_row_per_wide = bool(conn.execute(f"SELECT COUNT(*) = COUNT(DISTINCT timestamp_utc) FROM {p0052.WIDE_TABLE}").fetchone()[0])
    ok = bool(secret_safety["secret_safe"]) and not forbidden_task_docs and not forbidden_row_docs and duplicates == 0 and nonfinite == 0 and one_row_per_wide and int(joined.get("analysis_rows", 0)) > 0
    return {
        "ok": ok,
        "secret_checked": secret_safety["secret_checked"],
        "secret_safe": secret_safety["secret_safe"],
        "forbidden_task_documents": forbidden_task_docs,
        "forbidden_row_documents": forbidden_row_docs,
        "a61_requested": False,
        "duplicates_in_fetched_hourly_rows": duplicates,
        "nonfinite_fetched_hourly_values": nonfinite,
        "failed_chunks": len(failed_chunks),
        "one_row_per_wide_timestamp": one_row_per_wide,
        "full_target_directional_complete": full["complete"],
        "warn_minimum_directional_complete": warn["complete"],
        "full_target_net_complete": full_net["complete"],
        "warn_minimum_net_complete": warn_net["complete"],
        "warn_minimum_net_substantial": warn_net["min_completion_percent"] >= 95.0 and int(joined.get("analysis_rows", 0)) >= warn_net["expected_hours"],
        "full_target_directional_coverage": full,
        "warn_minimum_directional_coverage": warn,
        "full_target_net_feature_coverage": full_net,
        "warn_minimum_net_feature_coverage": warn_net,
        "analysis_rows": joined.get("analysis_rows", 0),
        "utilization_or_margin_derived_by_p0053a": False,
        "token_leak_scan_required": True,
    }


def directional_coverage_summary(conn: sqlite3.Connection, start: datetime, end: datetime) -> dict[str, object]:
    expected_hours = int((end - start).total_seconds() // 3600) + 1
    coverage: dict[str, int] = {}
    for config in a09_a11_configs():
        for border in p0052a.INTERNAL_BORDERS:
            left, right = border.split("_", 1)
            for from_area, to_area in ((left, right), (right, left)):
                key = f"{config['document_type']}:{from_area}->{to_area}"
                coverage[key] = existing_hour_count(conn, config, from_area, to_area, start, end)
    missing = {key: max(0, expected_hours - count) for key, count in coverage.items()}
    return {
        "start": p0052a.format_utc(start),
        "end": p0052a.format_utc(end),
        "expected_hours_per_direction": expected_hours,
        "complete": all(count >= expected_hours for count in coverage.values()),
        "min_hours": min(coverage.values(), default=0),
        "max_missing_hours": max(missing.values(), default=expected_hours),
        "missing_hours_by_contract": missing,
    }


def net_feature_coverage_summary(conn: sqlite3.Connection, start: datetime, end: datetime) -> dict[str, object]:
    expected_hours = int((end - start).total_seconds() // 3600) + 1
    columns = (
        "net_scheduled_exchange_se1_se2_mw",
        "net_scheduled_exchange_se2_se3_mw",
        "net_scheduled_exchange_se3_se4_mw",
        "net_physical_flow_se1_se2_mw",
        "net_physical_flow_se2_se3_mw",
        "net_physical_flow_se3_se4_mw",
    )
    existing = p0052.table_columns(conn, p0052.WIDE_TABLE)
    counts: dict[str, int] = {}
    for column in columns:
        if column not in existing:
            counts[column] = 0
            continue
        counts[column] = int(conn.execute(
            f"SELECT COUNT(*) FROM {p0052.WIDE_TABLE} WHERE timestamp_utc BETWEEN ? AND ? AND {column} IS NOT NULL",
            (p0052a.format_utc(start), p0052a.format_utc(end)),
        ).fetchone()[0])
    percents = {column: round((count / expected_hours) * 100.0, 3) if expected_hours else 0.0 for column, count in counts.items()}
    return {
        "start": p0052a.format_utc(start),
        "end": p0052a.format_utc(end),
        "expected_hours": expected_hours,
        "counts": counts,
        "completion_percent_by_feature": percents,
        "min_completion_percent": min(percents.values(), default=0.0),
        "complete": all(count >= expected_hours for count in counts.values()),
    }


def run_p0053a_diagnostics(conn: sqlite3.Connection, start: datetime, end: datetime) -> dict[str, object]:
    if not p0052.table_exists(conn, ANALYSIS_TABLE):
        return {"joined_rows": 0}
    rows = [dict(row) for row in conn.execute(f"SELECT * FROM {ANALYSIS_TABLE} WHERE timestamp_utc BETWEEN ? AND ?", (p0052a.format_utc(start), p0052a.format_utc(end)))]
    columns = [
        "net_scheduled_exchange_se2_se3_mw",
        "net_scheduled_exchange_se3_se4_mw",
        "net_physical_flow_se2_se3_mw",
        "net_physical_flow_se3_se4_mw",
        "southward_exchange_pressure",
        "southward_physical_flow_pressure",
    ]
    correlations = {}
    for column in columns:
        correlations[f"se3_price_vs_{column}"] = p0052.correlation(rows, "se3_price", column)
        correlations[f"se3_minus_se1_vs_{column}"] = p0052.correlation(rows, "se3_minus_se1", column)
    return {
        "joined_rows": len(rows),
        "analysis_table": ANALYSIS_TABLE,
        "correlations": correlations,
        "pre_post_flow_based": split_summary(rows, columns),
    }


def split_summary(rows: list[dict[str, object]], columns: list[str]) -> dict[str, object]:
    out: dict[str, object] = {}
    for split_name, split_rows in (("pre_flow_based", [r for r in rows if not r.get("flow_based_market_coupling_flag")]), ("post_flow_based", [r for r in rows if r.get("flow_based_market_coupling_flag")])):
        out[split_name] = {"rows": len(split_rows), "means": {column: mean(split_rows, column) for column in columns}}
    return out


def mean(rows: list[dict[str, object]], column: str) -> float | None:
    values = [float(row[column]) for row in rows if row.get(column) is not None and p0052a.is_finite(row[column])]
    return sum(values) / len(values) if values else None


def source_contracts(responses: list[dict[str, object]], failed_chunks: list[dict[str, object]]) -> dict[str, object]:
    attempted = [
        {key: response.get(key) for key in ("document_type", "from_area", "to_area", "measure", "status", "root", "reason", "timeseries", "points", "period_start", "period_end")}
        for response in responses
    ]
    response_counts = dict(Counter(f"{row.get('document_type')}:{row.get('root')}:{row.get('reason', '')[:80]}" for row in attempted))
    return {
        "base_url": p0052a.ENTSOE_BASE_URL,
        "attempted_contract_count": len(attempted),
        "attempted_contract_samples": attempted[:24],
        "response_counts": response_counts,
        "failed_chunk_count": len(failed_chunks),
        "failed_chunk_samples": failed_chunks[:24],
        "token_included_in_evidence": False,
        "documents_allowed": ["A09", "A11"],
        "a61_requested": False,
    }


def forecast_safety_classification() -> dict[str, str]:
    return {
        "scheduled_exchange_mw": "historical_observed_only_not_forecast_safe",
        "physical_flow_mw": "historical_observed_only_not_forecast_safe",
        "net_exchange_and_flow_features": "historical_observed_only_not_forecast_safe",
        "utilization": "not_created_by_p0053a",
        "bottleneck_margin": "not_created_by_p0053a",
    }


def write_p0053a_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "CHANGELOG.md": changelog_text(summary),
        "secret-handling.md": json_md("P0053A secret handling", secret_handling(summary["secret_safety"])),
        "entsoe-a09-a11-source-contracts.md": json_md("P0053A ENTSO-E A09/A11 source contracts", summary["source_contracts"]),
        "eic-domain-mapping.md": json_md("P0053A EIC domain mapping", {area: p0052a.DOMAINS[area] for area in ("SE1", "SE2", "SE3", "SE4")}),
        "database-contract.md": database_contract_text(),
        "backfill-plan-and-summary.md": json_md("P0053A backfill plan and summary", {"ranges": summary["ranges"], "plan": summary["backfill_plan"], "row_counts": summary["row_counts"], "runtime_seconds": summary["runtime_seconds"]}),
        "time-normalization-and-dst.md": "# P0053A time normalization and DST\n\nENTSO-E timestamps are stored as UTC `...Z`. Joins normalize both `...Z` and `...+00:00` text forms before matching. Fixed-CET fields remain UTC+1 all year for continuity with prior model datasets.\n",
        "data-validation.md": json_md("P0053A data validation", summary["validation"]),
        "coverage-and-missingness.md": json_md("P0053A coverage and missingness", {"full_directional": summary["validation"]["full_target_directional_coverage"], "warn_minimum_directional": summary["validation"]["warn_minimum_directional_coverage"], "full_net_features": summary["validation"]["full_target_net_feature_coverage"], "warn_minimum_net_features": summary["validation"]["warn_minimum_net_feature_coverage"], "failed_chunks": summary["validation"]["failed_chunks"]}),
        "direction-conventions.md": "# P0053A direction conventions\n\nRequests use `out_Domain = from_area` and `in_Domain = to_area`. Directed values are positive in that direction. Net north-to-south values are computed as north-to-south directed MW minus south-to-north directed MW for each internal Swedish border.\n",
        "derived-feature-definitions.md": derived_feature_text(),
        "joined-analysis-dataset.md": json_md("P0053A joined analysis dataset", {key: summary["row_counts"][key] for key in ("analysis_table", "analysis_rows", "analysis_start", "analysis_end")}),
        "initial-flow-exchange-diagnostics.md": json_md("P0053A initial flow/exchange diagnostics", summary["diagnostics"].get("correlations", {})),
        "pre-post-flow-based-diagnostics.md": json_md("P0053A pre/post flow-based diagnostics", summary["diagnostics"].get("pre_post_flow_based", {})),
        "forecast-safety-classification.md": json_md("P0053A forecast safety classification", summary["forecast_safety"]),
        "next-package-recommendation.md": next_package_text(summary),
        "component-attribution-summary.md": component_summary_text(summary),
    }
    for name, content in files.items():
        (evidence_dir / name).write_text(content, encoding="utf-8")
    json_files = {
        "source-contracts.json": summary["source_contracts"],
        "coverage-summary.json": {"full_directional": summary["validation"]["full_target_directional_coverage"], "warn_minimum_directional": summary["validation"]["warn_minimum_directional_coverage"], "full_net_features": summary["validation"]["full_target_net_feature_coverage"], "warn_minimum_net_features": summary["validation"]["warn_minimum_net_feature_coverage"]},
        "validation-summary.json": summary["validation"],
        "diagnostics-summary.json": summary["diagnostics"],
    }
    for name, payload in json_files.items():
        (evidence_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {name: str(evidence_dir / name) for name in files | json_files}


def secret_handling(secret_safety: dict[str, object]) -> dict[str, object]:
    return {"token_source_class": secret_safety.get("token_source"), "secret_checked": secret_safety.get("secret_checked"), "secret_safe": secret_safety.get("secret_safe"), "file_mode_or_reason": secret_safety.get("file_mode", "environment_not_a_file"), "directory_mode_or_reason": secret_safety.get("directory_mode", "environment_not_a_file"), "token_in_logs": False, "token_in_evidence": False}


def database_contract_text() -> str:
    return f"""# P0053A database contract

P0053A reuses `{p0052.RAW_TABLE}`, `{p0052.CANONICAL_TABLE}` and `{p0052.WIDE_TABLE}`.

P0053A creates or replaces `{ANALYSIS_TABLE}` as an offline analysis table joined from observed A09/A11 wide features, P0051 physical balance and P0048/P0049 price/spread columns.

No utilization or bottleneck-margin features are created or populated by P0053A.
"""


def derived_feature_text() -> str:
    return "# P0053A derived feature definitions\n\n- `net_scheduled_exchange_<border>_mw = north_to_south_scheduled_exchange - south_to_north_scheduled_exchange`.\n- `net_physical_flow_<border>_mw = north_to_south_physical_flow - south_to_north_physical_flow`.\n- `southward_exchange_pressure = max(0, net_scheduled_exchange_se2_se3_mw) + max(0, net_scheduled_exchange_se3_se4_mw)`.\n- `southward_physical_flow_pressure = max(0, net_physical_flow_se2_se3_mw) + max(0, net_physical_flow_se3_se4_mw)`.\n- Capacity utilization and bottleneck margin are intentionally absent from P0053A derivations.\n"


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0053A changelog

- Re-verified ENTSO-E token safety without writing the token value.
- Backfilled only ENTSO-E A09 scheduled exchange and A11 physical flow for internal Swedish borders.
- Updated directional net and southward pressure features in the transfer wide table.
- Created `{ANALYSIS_TABLE}` for observed physical balance, flow/exchange and SE3/SE1 price diagnostics.
- Result status: {summary['status']}.
- No A61 request, utilization/margin derivation, continental price feature, SE3 forecast/API/model, Shelly, Home Assistant, KVS or device action was performed.
"""


def next_package_text(summary: dict[str, object]) -> str:
    return f"# P0053A next package recommendation\n\nUse `{ANALYSIS_TABLE}` for offline feature attribution before deciding whether observed A09/A11 signals should become training features. They are historical observed signals and are not forecast-safe without a separate future-availability package.\n"


def component_summary_text(summary: dict[str, object]) -> str:
    return f"# P0053A component attribution summary\n\nStatus: {summary['status']}\n\nRows: {summary['row_counts']}\n\nA09/A11 observed flow/exchange may explain historical SE3 price and SE3-SE1 spread variation; P0053A does not make it a deployable forecast component.\n"


def json_md(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run P0053A ENTSO-E A09/A11 backfill")
    parser.add_argument("--feature-db", default=str(DEFAULT_FEATURE_DB))
    parser.add_argument("--evidence-dir", default=str(EVIDENCE_DIR))
    parser.add_argument("--start", default=p0052a.format_utc(TARGET_START))
    parser.add_argument("--end", default=p0052a.format_utc(TARGET_END))
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--skip-fetch", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_p0053a_backfill(
        feature_db=args.feature_db,
        evidence_dir=args.evidence_dir,
        start=p0052a.parse_utc(args.start),
        end=p0052a.parse_utc(args.end),
        workers=args.workers,
        fetch=not args.skip_fetch,
    )
    print(json.dumps({"status": result.status, "row_counts": result.row_counts}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
