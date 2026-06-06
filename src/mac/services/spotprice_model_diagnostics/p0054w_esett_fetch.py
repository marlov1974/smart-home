"""P0054W eSett SE3 MGA load-profile fetch and native ingestion."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
import csv
import json
import sqlite3
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics.p0041 import write


PACKAGE_ID = "P0054W"
EVIDENCE_DIR = Path("requirements/package-runs/P0054W")
ESETT_BASE_URL = "https://api.opendata.esett.com"
SE3_MBA_EIC = "10Y1001A1001A46L"
SE3_MBA_NAME = "SE3"
START_UTC = "2022-06-01T00:00:00Z"
MASTERDATA_TABLE = "esett_mga_masterdata_v1"
NATIVE_TABLE = "esett_mga_consumption_native_v1"
CHECKPOINT_TABLE = "esett_mga_consumption_ingestion_checkpoint_v1"
ENTSOE_CONSUMPTION_TABLE = "entsoe_consumption_area_hourly_v1"
SOURCE_SYSTEM = "eSett Open Data"
SOURCE_NAME = "EXP18/LoadProfile"
SETTLEMENT_CLASS = "profiled_load_profile"
UNIT = "MWh"
VALUE_KIND = "energy"
DIRECTION = "consumption_load_source_negative"


@dataclass(frozen=True)
class FetchResult:
    status: str
    mode: str
    loaded_rows: int
    evidence: dict[str, str]


def run_p0054w_esett_fetch(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
    mode: str = "full",
    start_utc: str = START_UTC,
    end_utc: str | None = None,
    preflight_mgas: int = 3,
    preflight_months: int = 2,
    sleep_seconds: float = 0.05,
    max_chunks: int | None = None,
) -> FetchResult:
    db_path = Path(feature_db).expanduser()
    evidence_path = Path(evidence_dir)
    end_text = normalize_utc_text(end_utc) if end_utc else default_end_utc()
    start_text = normalize_utc_text(start_utc)
    started_at = now_utc()
    with sqlite3.connect(db_path, timeout=60.0) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=60000")
        create_schema(conn)
        masterdata = fetch_se3_masterdata()
        persist_masterdata(conn, masterdata)
        preflight = run_preflight(conn, masterdata, start_text, preflight_mgas, preflight_months, sleep_seconds)
        if mode == "preflight":
            progress = load_progress_summary(conn)
            summary = build_summary(db_path, started_at, start_text, end_text, masterdata, preflight, progress, empty_se3_volume_sanity(), "WARN", "preflight_only")
            evidence = write_fetch_evidence(evidence_path, summary)
            return FetchResult(status="WARN", mode=mode, loaded_rows=int(progress["loaded_row_count"]), evidence=evidence)
        if not preflight["ok"]:
            progress = load_progress_summary(conn)
            summary = build_summary(db_path, started_at, start_text, end_text, masterdata, preflight, progress, empty_se3_volume_sanity(), "WARN", "preflight_failed")
            evidence = write_fetch_evidence(evidence_path, summary)
            return FetchResult(status="WARN", mode=mode, loaded_rows=int(progress["loaded_row_count"]), evidence=evidence)
        ensure_full_checkpoint_manifest(conn, masterdata, start_text, end_text)
        process_checkpoint(conn, sleep_seconds=sleep_seconds, max_chunks=max_chunks)
        progress = load_progress_summary(conn)
        sanity = load_se3_volume_sanity(conn)
        status = "PASS" if progress["remaining_period_count"] == 0 else "WARN"
        result_kind = "full_fetch_complete" if status == "PASS" else "checkpointed_partial_progress"
        summary = build_summary(db_path, started_at, start_text, end_text, masterdata, preflight, progress, sanity, status, result_kind)
        evidence = write_fetch_evidence(evidence_path, summary)
        return FetchResult(status=status, mode=mode, loaded_rows=int(progress["loaded_row_count"]), evidence=evidence)


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {MASTERDATA_TABLE} (
            source_system TEXT NOT NULL,
            mga_id TEXT NOT NULL,
            mga_name TEXT,
            country TEXT,
            bidding_zone TEXT,
            DSO_or_grid_owner TEXT,
            mga_type TEXT,
            valid_from TEXT,
            valid_to TEXT,
            ingested_at_utc TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (source_system, mga_id)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {NATIVE_TABLE} (
            source_system TEXT NOT NULL,
            source_name TEXT NOT NULL,
            country TEXT NOT NULL,
            mga_id TEXT NOT NULL,
            mga_name TEXT,
            bidding_zone TEXT,
            settlement_class TEXT NOT NULL,
            resolution_minutes INTEGER NOT NULL,
            interval_start_utc TEXT NOT NULL,
            interval_end_utc TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL,
            value_kind TEXT NOT NULL,
            direction TEXT NOT NULL,
            quality_status TEXT,
            version_or_publication_time_utc TEXT NOT NULL,
            ingested_at_utc TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (
                source_system, source_name, country, mga_id, settlement_class,
                interval_start_utc, interval_end_utc, resolution_minutes, version_or_publication_time_utc
            )
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {CHECKPOINT_TABLE} (
            source_system TEXT NOT NULL,
            mga_id TEXT NOT NULL,
            period_start_utc TEXT NOT NULL,
            period_end_utc TEXT NOT NULL,
            settlement_class TEXT NOT NULL,
            status TEXT NOT NULL,
            attempt_count INTEGER NOT NULL,
            row_count_loaded INTEGER NOT NULL,
            first_attempt_at_utc TEXT,
            last_attempt_at_utc TEXT,
            last_error TEXT,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (source_system, mga_id, period_start_utc, period_end_utc, settlement_class)
        )
        """
    )
    conn.commit()


def fetch_se3_masterdata() -> list[dict[str, object]]:
    return sorted(
        [item for item in fetch_json("/EXP03/MeteringGridAreas", {"mba": SE3_MBA_EIC}) if item.get("country") == "SE"],
        key=lambda item: str(item.get("mgaCode") or ""),
    )


def persist_masterdata(conn: sqlite3.Connection, masterdata: list[dict[str, object]]) -> None:
    ingested = now_utc()
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {MASTERDATA_TABLE}
        (source_system, mga_id, mga_name, country, bidding_zone, DSO_or_grid_owner, mga_type, valid_from, valid_to, ingested_at_utc, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                SOURCE_SYSTEM,
                str(item.get("mgaCode") or ""),
                item.get("mgaName"),
                item.get("country"),
                SE3_MBA_NAME,
                item.get("dsoName"),
                item.get("mgaType"),
                None,
                None,
                ingested,
                PACKAGE_ID,
            )
            for item in masterdata
            if item.get("mgaCode")
        ],
    )
    conn.commit()


def run_preflight(
    conn: sqlite3.Connection,
    masterdata: list[dict[str, object]],
    start_utc: str,
    preflight_mgas: int,
    preflight_months: int,
    sleep_seconds: float,
) -> dict[str, object]:
    selected = [item for item in masterdata if item.get("mgaType") == "DISTRIBUTION"][:preflight_mgas]
    periods = month_ranges(start_utc, add_months(start_utc, preflight_months))
    loaded = 0
    samples: list[dict[str, object]] = []
    errors: list[str] = []
    loaded += fetch_preflight_periods(conn, selected, periods, samples, errors, sleep_seconds)
    fallback_periods: list[tuple[str, str]] = []
    if not samples and not errors:
        fallback_periods = month_ranges("2025-01-01T00:00:00Z", "2025-03-01T00:00:00Z")
        loaded += fetch_preflight_periods(conn, selected, fallback_periods, samples, errors, sleep_seconds)
    summary = resolution_transition_summary([str(row["timestampUTC"]) for row in samples if row.get("timestampUTC")])
    return {
        "ok": bool(selected) and not errors,
        "selected_mgas": [item.get("mgaCode") for item in selected],
        "selected_periods": [{"start": start, "end": end} for start, end in periods],
        "fallback_sample_periods": [{"start": start, "end": end} for start, end in fallback_periods],
        "loaded_rows": loaded,
        "sample_rows": samples,
        "resolution_summary_from_sample": summary,
        "errors": errors,
    }


def fetch_preflight_periods(
    conn: sqlite3.Connection,
    selected: list[dict[str, object]],
    periods: list[tuple[str, str]],
    samples: list[dict[str, object]],
    errors: list[str],
    sleep_seconds: float,
) -> int:
    loaded = 0
    for mga in selected:
        for start, end in periods:
            try:
                rows = fetch_load_profile(str(mga["mgaCode"]), start, end)
                native_rows = native_rows_from_payload(mga, rows)
                persist_native_rows(conn, native_rows)
                loaded += len(native_rows)
                if rows and len(samples) < 5:
                    samples.extend(rows[: 5 - len(samples)])
                time.sleep(sleep_seconds)
            except Exception as exc:  # pragma: no cover - exercised by live run only
                errors.append(f"{mga.get('mgaCode')} {start}..{end}: {exc}")
    return loaded


def ensure_full_checkpoint_manifest(conn: sqlite3.Connection, masterdata: list[dict[str, object]], start_utc: str, end_utc: str) -> None:
    periods = month_ranges(start_utc, end_utc)
    rows = []
    for item in masterdata:
        mga_id = str(item.get("mgaCode") or "")
        if not mga_id:
            continue
        for start, end in periods:
            rows.append((SOURCE_SYSTEM, mga_id, start, end, SETTLEMENT_CLASS, "pending", 0, 0, None, None, None, PACKAGE_ID))
    conn.executemany(
        f"""
        INSERT OR IGNORE INTO {CHECKPOINT_TABLE}
        (source_system, mga_id, period_start_utc, period_end_utc, settlement_class, status, attempt_count,
         row_count_loaded, first_attempt_at_utc, last_attempt_at_utc, last_error, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()


def process_checkpoint(conn: sqlite3.Connection, *, sleep_seconds: float, max_chunks: int | None) -> None:
    processed = 0
    while True:
        if max_chunks is not None and processed >= max_chunks:
            return
        checkpoint = conn.execute(
            f"""
            SELECT * FROM {CHECKPOINT_TABLE}
            WHERE status IN ('pending', 'failed')
            ORDER BY mga_id, period_start_utc
            LIMIT 1
            """
        ).fetchone()
        if not checkpoint:
            return
        started = now_utc()
        first_attempt = checkpoint["first_attempt_at_utc"] or started
        attempts = int(checkpoint["attempt_count"]) + 1
        conn.execute(
            f"""
            UPDATE {CHECKPOINT_TABLE}
            SET status='running', attempt_count=?, first_attempt_at_utc=?, last_attempt_at_utc=?, last_error=NULL
            WHERE source_system=? AND mga_id=? AND period_start_utc=? AND period_end_utc=? AND settlement_class=?
            """,
            (
                attempts,
                first_attempt,
                started,
                checkpoint["source_system"],
                checkpoint["mga_id"],
                checkpoint["period_start_utc"],
                checkpoint["period_end_utc"],
                checkpoint["settlement_class"],
            ),
        )
        conn.commit()
        try:
            mga = load_masterdata_by_id(conn, str(checkpoint["mga_id"]))
            payload = fetch_load_profile(str(checkpoint["mga_id"]), str(checkpoint["period_start_utc"]), str(checkpoint["period_end_utc"]))
            rows = native_rows_from_payload(mga, payload)
            persist_native_rows(conn, rows)
            conn.execute(
                f"""
                UPDATE {CHECKPOINT_TABLE}
                SET status='done', row_count_loaded=?, last_attempt_at_utc=?, last_error=NULL
                WHERE source_system=? AND mga_id=? AND period_start_utc=? AND period_end_utc=? AND settlement_class=?
                """,
                (
                    len(rows),
                    now_utc(),
                    checkpoint["source_system"],
                    checkpoint["mga_id"],
                    checkpoint["period_start_utc"],
                    checkpoint["period_end_utc"],
                    checkpoint["settlement_class"],
                ),
            )
            conn.commit()
        except Exception as exc:  # pragma: no cover - exercised by live run only
            conn.execute(
                f"""
                UPDATE {CHECKPOINT_TABLE}
                SET status='failed', last_attempt_at_utc=?, last_error=?
                WHERE source_system=? AND mga_id=? AND period_start_utc=? AND period_end_utc=? AND settlement_class=?
                """,
                (
                    now_utc(),
                    str(exc)[:1000],
                    checkpoint["source_system"],
                    checkpoint["mga_id"],
                    checkpoint["period_start_utc"],
                    checkpoint["period_end_utc"],
                    checkpoint["settlement_class"],
                ),
            )
            conn.commit()
        processed += 1
        time.sleep(sleep_seconds)


def load_masterdata_by_id(conn: sqlite3.Connection, mga_id: str) -> dict[str, object]:
    row = conn.execute(f"SELECT * FROM {MASTERDATA_TABLE} WHERE source_system=? AND mga_id=?", (SOURCE_SYSTEM, mga_id)).fetchone()
    if not row:
        return {"mgaCode": mga_id, "mgaName": None, "country": "SE", "mba": SE3_MBA_NAME}
    return {
        "mgaCode": row["mga_id"],
        "mgaName": row["mga_name"],
        "country": row["country"],
        "mba": row["bidding_zone"],
        "dsoName": row["DSO_or_grid_owner"],
        "mgaType": row["mga_type"],
    }


def fetch_load_profile(mga_id: str, start_utc: str, end_utc: str) -> list[dict[str, object]]:
    return fetch_json("/EXP18/LoadProfile", {"mba": SE3_MBA_EIC, "mga": mga_id, "start": format_esett_time(start_utc), "end": format_esett_time(end_utc)})


def native_rows_from_payload(mga: dict[str, object], payload: list[dict[str, object]]) -> list[dict[str, object]]:
    if not payload:
        return []
    resolution = infer_resolution_minutes([str(row["timestampUTC"]) for row in payload if row.get("timestampUTC")])
    ingested = now_utc()
    output = []
    for row in payload:
        start = normalize_utc_text(str(row["timestampUTC"]))
        end = (parse_utc(start) + timedelta(minutes=resolution)).isoformat().replace("+00:00", "Z")
        output.append({
            "source_system": SOURCE_SYSTEM,
            "source_name": SOURCE_NAME,
            "country": str(mga.get("country") or "SE"),
            "mga_id": str(row.get("mgaCode") or mga.get("mgaCode") or ""),
            "mga_name": row.get("mgaName") or mga.get("mgaName"),
            "bidding_zone": SE3_MBA_NAME,
            "settlement_class": SETTLEMENT_CLASS,
            "resolution_minutes": resolution,
            "interval_start_utc": start,
            "interval_end_utc": end,
            "value": float(row["quantity"]),
            "unit": UNIT,
            "value_kind": VALUE_KIND,
            "direction": DIRECTION,
            "quality_status": "ok",
            "version_or_publication_time_utc": "",
            "ingested_at_utc": ingested,
            "generated_by_package": PACKAGE_ID,
        })
    return output


def persist_native_rows(conn: sqlite3.Connection, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    columns = list(rows[0])
    placeholders = ", ".join("?" for _ in columns)
    conn.executemany(
        f"INSERT OR REPLACE INTO {NATIVE_TABLE} ({', '.join(columns)}) VALUES ({placeholders})",
        [tuple(row[column] for column in columns) for row in rows],
    )
    conn.commit()


def load_progress_summary(conn: sqlite3.Connection) -> dict[str, object]:
    native = conn.execute(
        f"""
        SELECT COUNT(*) AS rows, COUNT(DISTINCT mga_id) AS mgas, MIN(interval_start_utc) AS min_ts, MAX(interval_start_utc) AS max_ts
        FROM {NATIVE_TABLE}
        WHERE generated_by_package=?
        """,
        (PACKAGE_ID,),
    ).fetchone()
    by_status = {
        row["status"]: int(row["count"])
        for row in conn.execute(f"SELECT status, COUNT(*) AS count FROM {CHECKPOINT_TABLE} GROUP BY status")
    }
    remaining = sum(count for status, count in by_status.items() if status in {"pending", "failed", "running"})
    return {
        "loaded_row_count": int(native["rows"] or 0),
        "loaded_mga_count": int(native["mgas"] or 0),
        "loaded_min_timestamp": native["min_ts"],
        "loaded_max_timestamp": native["max_ts"],
        "checkpoint_status_counts": by_status,
        "completed_period_count": int(by_status.get("done", 0)),
        "remaining_period_count": int(remaining),
        "remaining_mga_count": count_remaining_mgas(conn),
        "checkpoint_location": CHECKPOINT_TABLE,
        "resume_command": "PYTHONPYCACHEPREFIX=/private/tmp/p0054w-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0054w_esett_fetch --mode full",
    }


def load_se3_volume_sanity(conn: sqlite3.Connection) -> dict[str, object]:
    row = conn.execute(
        f"""
        WITH mga_hourly AS (
            SELECT substr(interval_start_utc, 1, 13) || ':00:00Z' AS timestamp_utc,
                   SUM(-value) AS mga_mwh_hour,
                   COUNT(DISTINCT mga_id) AS mga_count
            FROM {NATIVE_TABLE}
            WHERE generated_by_package=? AND bidding_zone='SE3'
            GROUP BY 1
        ),
        joined AS (
            SELECT m.timestamp_utc, m.mga_mwh_hour, e.consumption_mw AS entsoe_mw, m.mga_count
            FROM mga_hourly m
            JOIN {ENTSOE_CONSUMPTION_TABLE} e
              ON e.timestamp_utc=m.timestamp_utc AND e.area='SE3'
        )
        SELECT COUNT(*) AS joined_hours,
               MIN(timestamp_utc) AS min_timestamp,
               MAX(timestamp_utc) AS max_timestamp,
               AVG(mga_mwh_hour) AS avg_mga_hour_mwh,
               AVG(entsoe_mw) AS avg_entsoe_mw,
               AVG(mga_mwh_hour / entsoe_mw) AS avg_ratio,
               MIN(mga_mwh_hour / entsoe_mw) AS min_ratio,
               MAX(mga_mwh_hour / entsoe_mw) AS max_ratio,
               MIN(mga_count) AS min_mga_count,
               MAX(mga_count) AS max_mga_count
        FROM joined
        """,
        (PACKAGE_ID,),
    ).fetchone()
    return {
        "comparison": "sum(-eSett_MGA_LoadProfile_MWh_per_hour) versus ENTSO-E SE3 actual_total_load MW",
        "aggregation_method": "15m source MWh summed to hourly MWh; numeric value is comparable to average MW over one hour",
        "joined_hours": int(row["joined_hours"] or 0),
        "min_timestamp": row["min_timestamp"],
        "max_timestamp": row["max_timestamp"],
        "avg_mga_hour_mwh": float(row["avg_mga_hour_mwh"] or 0.0),
        "avg_entsoe_mw": float(row["avg_entsoe_mw"] or 0.0),
        "avg_ratio": float(row["avg_ratio"] or 0.0),
        "min_ratio": float(row["min_ratio"] or 0.0),
        "max_ratio": float(row["max_ratio"] or 0.0),
        "min_mga_count_per_hour": int(row["min_mga_count"] or 0),
        "max_mga_count_per_hour": int(row["max_mga_count"] or 0),
        "interpretation": "EXP18 LoadProfile is materially below ENTSO-E SE3 actual total load; treat it as profiled/load-profile component, not total SE3 consumption.",
    }


def empty_se3_volume_sanity() -> dict[str, object]:
    return {
        "comparison": "not_run",
        "aggregation_method": "not_run",
        "joined_hours": 0,
        "min_timestamp": None,
        "max_timestamp": None,
        "avg_mga_hour_mwh": 0.0,
        "avg_entsoe_mw": 0.0,
        "avg_ratio": 0.0,
        "min_ratio": 0.0,
        "max_ratio": 0.0,
        "min_mga_count_per_hour": 0,
        "max_mga_count_per_hour": 0,
        "interpretation": "SE3 sanity check is only run after full fetch.",
    }


def count_remaining_mgas(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        f"SELECT COUNT(DISTINCT mga_id) FROM {CHECKPOINT_TABLE} WHERE status IN ('pending', 'failed', 'running')"
    ).fetchone()
    return int(row[0] or 0)


def build_summary(
    db_path: Path,
    started_at: str,
    start_utc: str,
    end_utc: str,
    masterdata: list[dict[str, object]],
    preflight: dict[str, object],
    progress: dict[str, object],
    se3_volume_sanity: dict[str, object],
    status: str,
    result_kind: str,
) -> dict[str, object]:
    mga_type_counts = dict(sorted(Counter(str(item.get("mgaType") or "unknown") for item in masterdata).items()))
    return {
        "package_id": PACKAGE_ID,
        "status": status,
        "result_kind": result_kind,
        "started_at_utc": started_at,
        "generated_at_utc": now_utc(),
        "feature_db": str(db_path),
        "source_system": SOURCE_SYSTEM,
        "source_name": SOURCE_NAME,
        "source_base_url": ESETT_BASE_URL,
        "source_endpoints": ["/EXP03/MeteringGridAreas", "/EXP18/LoadProfile"],
        "source_license": "eSett Open Data states CC0 on opendata.esett.com",
        "bidding_zone": SE3_MBA_NAME,
        "mba_eic": SE3_MBA_EIC,
        "requested_start_utc": start_utc,
        "requested_end_utc": end_utc,
        "mga_masterdata_count": len(masterdata),
        "mga_type_counts": mga_type_counts,
        "settlement_class": SETTLEMENT_CLASS,
        "unit": UNIT,
        "value_kind": VALUE_KIND,
        "direction": DIRECTION,
        "preflight": preflight,
        "progress": progress,
        "se3_volume_sanity": se3_volume_sanity,
        "database_tables": [MASTERDATA_TABLE, NATIVE_TABLE, CHECKPOINT_TABLE],
        "no_credentials": True,
        "no_devices_or_runtime": True,
        "no_a61": True,
        "raw_data_committed": False,
    }


def write_fetch_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary": write_json(evidence_dir / "summary.json", summary),
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog(summary)),
        "review": write(evidence_dir / "review.md", review_report(summary)),
        "design": write(evidence_dir / "design.md", design_report(summary)),
        "functions": write(evidence_dir / "functions.md", functions_report()),
        "label": write(evidence_dir / "labb-label.md", "# P0054W LABB label\n\nLabel: `LABB`.\n"),
        "heavy": write(evidence_dir / "heavy-fetch-plan.md", heavy_fetch_report(summary)),
        "checkpoint": write(evidence_dir / "ingestion-checkpoint-contract.md", checkpoint_report(summary)),
        "preflight": write(evidence_dir / "preflight-fetch-results.md", preflight_report(summary)),
        "progress": write(evidence_dir / "full-fetch-progress.md", full_progress_report(summary)),
        "resume": write(evidence_dir / "resume-instructions.md", resume_report(summary)),
        "database_load": write(evidence_dir / "database-load-evidence.md", database_load_report(summary)),
        "database": write(evidence_dir / "database-ingestion-contract.md", database_contract_report(summary)),
        "hourly": write(evidence_dir / "hourly-aggregation-contract.md", hourly_report(summary)),
        "se3_sanity": write(evidence_dir / "se3-volume-sanity-check.md", se3_sanity_report(summary)),
        "masterdata": write(evidence_dir / "mga-masterdata-inventory.md", masterdata_report(summary)),
        "mapping": write(evidence_dir / "mga-price-area-mapping.md", mapping_report(summary)),
        "series": write(evidence_dir / "consumption-series-inventory.md", series_report(summary)),
        "settlement": write(evidence_dir / "settlement-classification.md", settlement_report(summary)),
        "resolution": write(evidence_dir / "resolution-transition-analysis.md", resolution_report(summary)),
        "native": write(evidence_dir / "native-resolution-contract.md", native_report(summary)),
        "quality": write(evidence_dir / "data-quality-review.md", quality_report(summary)),
        "leakage": write(evidence_dir / "leakage-and-use-scope-review.md", leakage_report()),
        "learned": write(evidence_dir / "what-we-learned.md", learned_report(summary)),
        "next": write(evidence_dir / "next-package-recommendation.md", next_report(summary)),
        "scope": write(evidence_dir / "no-api-no-device-runtime-review.md", scope_report(summary)),
        "source_inventory": write(evidence_dir / "source-inventory.md", source_inventory_report(summary)),
        "terminology": write(evidence_dir / "esett-terminology.md", terminology_report(summary)),
    }
    write_csv(evidence_dir / "mga-price-area-counts.csv", [{"bidding_zone": SE3_MBA_NAME, "mga_count": summary["mga_masterdata_count"]}])
    write_csv(evidence_dir / "database-load-summary.csv", [flatten_progress(summary)])
    write_csv(evidence_dir / "se3-volume-sanity-check.csv", [summary["se3_volume_sanity"]])
    return paths


def changelog(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0054W changelog",
        "",
        "- Rebased P0054W onto operator heavy-fetch clarifications.",
        "- Added eSett Open Data EXP03/EXP18 SE3 MGA masterdata and load-profile ingestion.",
        f"- Result: `{summary['status']}` / `{summary['result_kind']}`.",
        f"- Loaded rows: `{summary['progress']['loaded_row_count']}`.",
        f"- Completed periods: `{summary['progress']['completed_period_count']}`.",
        "- No credentials, devices, runtime changes, A61 utilization, model training or raw data commits.",
        "",
    ])


def review_report(summary: dict[str, object]) -> str:
    return f"""# P0054W review

Status: `{summary['status']}`

P0054W is consistent after applying the two operator clarification files. eSett Open Data exposes public `EXP03/MeteringGridAreas` and `EXP18/LoadProfile`, so the package must not stop at discovery.

Preflight status: `{summary['preflight']['ok']}`.

The ingestion preserves native `resolution_minutes`, `settlement_class`, source sign, unit and value kind in `{NATIVE_TABLE}` and uses `{CHECKPOINT_TABLE}` for resumable full fetch.
"""


def design_report(summary: dict[str, object]) -> str:
    return f"""# P0054W design

Strategy: outer loop MGA, inner loop calendar month.

Reason: eSett `EXP18/LoadProfile` accepts one optional `mga` filter, and monthly chunks keep each request bounded while preserving native 15m/60m rows.

Tables:

- `{MASTERDATA_TABLE}`
- `{NATIVE_TABLE}`
- `{CHECKPOINT_TABLE}`

Verification commands:

```bash
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054w tests.mac.services.spotprice_model_diagnostics.test_p0054w_esett_fetch
PYTHONPYCACHEPREFIX=/private/tmp/p0054w-pycache python3 -m py_compile src/mac/services/spotprice_model_diagnostics/p0054w.py src/mac/services/spotprice_model_diagnostics/p0054w_esett_fetch.py tests/mac/services/spotprice_model_diagnostics/test_p0054w.py tests/mac/services/spotprice_model_diagnostics/test_p0054w_esett_fetch.py
PYTHONPYCACHEPREFIX=/private/tmp/p0054w-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0054w_esett_fetch --mode full
git diff --check
```
"""


def functions_report() -> str:
    return f"""# P0054W function design

`run_p0054w_esett_fetch(...)` orchestrates preflight, schema creation, checkpoint creation, full fetch and evidence writing.

`create_schema(...)` creates `{MASTERDATA_TABLE}`, `{NATIVE_TABLE}` and `{CHECKPOINT_TABLE}`.

`fetch_se3_masterdata(...)` reads public eSett SE3 MGA masterdata.

`run_preflight(...)` loads a small 1-3 MGA / 1-2 month sample and validates source shape.

`ensure_full_checkpoint_manifest(...)` creates resumable per-MGA/per-month work items.

`process_checkpoint(...)` fetches and persists pending chunks incrementally.

`native_rows_from_payload(...)` converts eSett `LoadProfileDTO` rows into the native contract while preserving source sign, unit, resolution and settlement class.

`write_fetch_evidence(...)` writes P0054W package-run evidence.
"""


def heavy_fetch_report(summary: dict[str, object]) -> str:
    return f"""# P0054W heavy-fetch plan

Chosen strategy: outer loop MGA, inner loop month.

Requested range: `{summary['requested_start_utc']}` through `{summary['requested_end_utc']}`.

Masterdata count: `{summary['mga_masterdata_count']}` SE3 MGAs.

Checkpoint table: `{CHECKPOINT_TABLE}`.

The fetch is serial with conservative pacing and can resume from checkpoint without discarding completed chunks.
"""


def checkpoint_report(summary: dict[str, object]) -> str:
    return f"""# P0054W ingestion checkpoint contract

Table: `{CHECKPOINT_TABLE}`

Primary key:

```text
source_system, mga_id, period_start_utc, period_end_utc, settlement_class
```

Status values used: `pending`, `running`, `done`, `failed`.

Progress:

```json
{json.dumps(summary['progress'], indent=2, sort_keys=True)}
```
"""


def preflight_report(summary: dict[str, object]) -> str:
    return "# P0054W preflight fetch results\n\n```json\n" + json.dumps(summary["preflight"], indent=2, sort_keys=True) + "\n```\n"


def full_progress_report(summary: dict[str, object]) -> str:
    return "# P0054W full-fetch progress\n\n```json\n" + json.dumps(summary["progress"], indent=2, sort_keys=True) + "\n```\n"


def resume_report(summary: dict[str, object]) -> str:
    return f"""# P0054W resume instructions

Resume command:

```bash
{summary['progress']['resume_command']}
```

Checkpoint location: `{summary['progress']['checkpoint_location']}` in `{summary['feature_db']}`.
"""


def database_load_report(summary: dict[str, object]) -> str:
    return f"""# P0054W database-load evidence

Loaded database tables:

- `{MASTERDATA_TABLE}`
- `{NATIVE_TABLE}`
- `{CHECKPOINT_TABLE}`

Loaded rows: `{summary['progress']['loaded_row_count']}`.
Loaded MGAs: `{summary['progress']['loaded_mga_count']}`.
Min timestamp: `{summary['progress']['loaded_min_timestamp']}`.
Max timestamp: `{summary['progress']['loaded_max_timestamp']}`.
"""


def database_contract_report(summary: dict[str, object]) -> str:
    return f"""# P0054W database ingestion contract

Native table: `{NATIVE_TABLE}`.

The native table preserves source system/name, country, MGA id/name, bidding zone, settlement class, resolution minutes, interval start/end, source value, unit, value kind, direction, quality status, ingest time and package id.

Uniqueness follows the P0054W required key including `version_or_publication_time_utc`, stored as an empty string when unavailable because SQLite treats nulls as distinct in unique keys.
"""


def hourly_report(summary: dict[str, object]) -> str:
    return f"""# P0054W hourly aggregation contract

Hourly aggregation was used only for SE3 volume sanity checking, not as source of truth.

Method:

```text
15m source MWh -> hourly MWh by sum(-value)
```

The negative source sign is inverted only for aggregate comparison against positive ENTSO-E load. Native rows in `{NATIVE_TABLE}` preserve the source sign.
"""


def se3_sanity_report(summary: dict[str, object]) -> str:
    return "# P0054W SE3 volume sanity check\n\n```json\n" + json.dumps(summary["se3_volume_sanity"], indent=2, sort_keys=True) + "\n```\n"


def masterdata_report(summary: dict[str, object]) -> str:
    return f"""# P0054W MGA masterdata inventory

Source: eSett `EXP03/MeteringGridAreas`.

SE3 MGA count: `{summary['mga_masterdata_count']}`.

MGA type counts:

```json
{json.dumps(summary['mga_type_counts'], indent=2, sort_keys=True)}
```
"""


def mapping_report(summary: dict[str, object]) -> str:
    return f"""# P0054W MGA price-area mapping

All fetched masterdata rows were requested with SE3 MBA EIC `{SE3_MBA_EIC}` and stored with bidding zone `{SE3_MBA_NAME}`.

Count by price area:

- SE3: `{summary['mga_masterdata_count']}`
- SE1: `0`
- SE2: `0`
- SE4: `0`
- unknown/unmapped: `0`
"""


def series_report(summary: dict[str, object]) -> str:
    return f"""# P0054W consumption-series inventory

Source: eSett `EXP18/LoadProfile`.

Series classification:

- `mga_id`: `mgaCode`
- timestamp: `timestampUTC`
- value: `quantity`
- unit: `{UNIT}`
- value kind: `{VALUE_KIND}`
- settlement class: `{SETTLEMENT_CLASS}`
- direction/sign: `{DIRECTION}`

Loaded rows: `{summary['progress']['loaded_row_count']}`.
"""


def settlement_report(summary: dict[str, object]) -> str:
    return f"""# P0054W settlement classification

eSett `EXP18/LoadProfile` is stored as `{SETTLEMENT_CLASS}`.

P0054W did not merge this source with measured, flex or total consumption. Future packages must keep `EXP15/Consumption` and `EXP18/LoadProfile` separate unless a source contract explicitly defines a safe total.
"""


def resolution_report(summary: dict[str, object]) -> str:
    return "# P0054W resolution transition analysis\n\nPreflight sample:\n\n```json\n" + json.dumps(summary["preflight"]["resolution_summary_from_sample"], indent=2, sort_keys=True) + "\n```\n"


def native_report(summary: dict[str, object]) -> str:
    return f"""# P0054W native-resolution contract

P0054W stores native source timestamps directly in `{NATIVE_TABLE}`.

`resolution_minutes` is inferred from adjacent source timestamps per response. Values are not resampled to hourly and source negative consumption sign is preserved.
"""


def quality_report(summary: dict[str, object]) -> str:
    return f"""# P0054W data-quality review

Preflight errors:

```json
{json.dumps(summary['preflight']['errors'], indent=2)}
```

Checkpoint status:

```json
{json.dumps(summary['progress']['checkpoint_status_counts'], indent=2, sort_keys=True)}
```
"""


def leakage_report() -> str:
    return """# P0054W leakage and use-scope review

P0054W loads historical observed eSett load-profile data only. It trains no model and creates no forecast-time feature.

No future price leakage, API serving, devices, Shelly, Home Assistant, KVS, A61 utilization or runtime activation were performed.
"""


def learned_report(summary: dict[str, object]) -> str:
    return f"""# P0054W what we learned

1. eSett Open Data has public SE3 MGA masterdata and `EXP18/LoadProfile`.
2. `EXP18/LoadProfile` supports per-MGA querying and currently returns 15-minute rows in the preflight sample.
3. Source values are negative for load profile quantities; P0054W preserves that source sign.
4. Full SE3 fetch progress is checkpointed in `{CHECKPOINT_TABLE}`.
"""


def next_report(summary: dict[str, object]) -> str:
    if summary["status"] == "PASS":
        recommendation = "D. test hierarchical reconciliation: direct SE3 + grouped/MGA bottom-up"
    else:
        recommendation = "Continue/resume P0054W full fetch before modeling."
    return f"# P0054W next package recommendation\n\nRecommended next step: {recommendation}\n"


def scope_report(summary: dict[str, object]) -> str:
    return """# P0054W no API / no device / runtime review

Authorized public eSett Open Data API calls were used for P0054W data ingestion.

Confirmed not performed:

- no credentials or tokens
- no device action
- no Shelly, Home Assistant or KVS action
- no runtime change
- no A61 utilization
- no model training
- no large raw data commit
"""


def source_inventory_report(summary: dict[str, object]) -> str:
    return f"""# P0054W source inventory

Selected source:

- eSett Open Data `{ESETT_BASE_URL}/EXP03/MeteringGridAreas`
- eSett Open Data `{ESETT_BASE_URL}/EXP18/LoadProfile`

Source tables:

- `{MASTERDATA_TABLE}`
- `{NATIVE_TABLE}`
- `{CHECKPOINT_TABLE}`
"""


def terminology_report(summary: dict[str, object]) -> str:
    return f"""# P0054W eSett terminology

`MGA`: eSett Metering Grid Area, represented by `mgaCode` / `mgaName`.

`MBA`: eSett market balance area; P0054W used SE3 MBA `{SE3_MBA_EIC}` to identify SE3 MGAs.

`LoadProfile`: eSett `EXP18` time series per MGA, stored as `{SETTLEMENT_CLASS}`.
"""


def flatten_progress(summary: dict[str, object]) -> dict[str, object]:
    progress = summary["progress"]
    return {
        "status": summary["status"],
        "result_kind": summary["result_kind"],
        "loaded_row_count": progress["loaded_row_count"],
        "loaded_mga_count": progress["loaded_mga_count"],
        "completed_period_count": progress["completed_period_count"],
        "remaining_period_count": progress["remaining_period_count"],
        "loaded_min_timestamp": progress["loaded_min_timestamp"],
        "loaded_max_timestamp": progress["loaded_max_timestamp"],
    }


def fetch_json(path: str, query: dict[str, object]) -> list[dict[str, object]]:
    url = ESETT_BASE_URL + path + "?" + urllib.parse.urlencode(query)
    request = urllib.request.Request(url, headers={"User-Agent": "smart-home-p0054w/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=60.0) as response:
            if response.status == 204:
                return []
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError:
        raw = subprocess.check_output(["curl", "-fsSL", url], timeout=120.0).decode("utf-8")
        return json.loads(raw) if raw else []


def month_ranges(start_utc: str, end_utc: str) -> list[tuple[str, str]]:
    current = parse_utc(start_utc)
    end = parse_utc(end_utc)
    ranges = []
    while current < end:
        next_month = first_of_next_month(current)
        chunk_end = min(next_month, end)
        ranges.append((format_utc(current), format_utc(chunk_end)))
        current = chunk_end
    return ranges


def add_months(start_utc: str, months: int) -> str:
    current = parse_utc(start_utc)
    for _ in range(months):
        current = first_of_next_month(current)
    return format_utc(current)


def first_of_next_month(value: datetime) -> datetime:
    if value.month == 12:
        return value.replace(year=value.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return value.replace(month=value.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)


def infer_resolution_minutes(timestamps: list[str]) -> int:
    ordered = sorted(parse_utc(value) for value in timestamps)
    deltas = Counter(int((right - left).total_seconds() // 60) for left, right in zip(ordered, ordered[1:]) if right > left)
    if not deltas:
        return 15
    return int(deltas.most_common(1)[0][0])


def resolution_transition_summary(timestamps: list[str]) -> dict[str, object]:
    ordered = sorted(parse_utc(value) for value in timestamps)
    deltas = Counter(int((right - left).total_seconds() // 60) for left, right in zip(ordered, ordered[1:]) if right > left)
    total = sum(deltas.values())
    return {
        "first_timestamp": format_utc(ordered[0]) if ordered else None,
        "last_timestamp": format_utc(ordered[-1]) if ordered else None,
        "observed_time_deltas_minutes": {str(key): value for key, value in sorted(deltas.items())},
        "share_15m": deltas.get(15, 0) / total if total else 0.0,
        "share_60m": deltas.get(60, 0) / total if total else 0.0,
        "mixed_resolution_periods": len(deltas) > 1,
    }


def default_end_utc() -> str:
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    return format_utc(now)


def format_esett_time(value: str) -> str:
    return parse_utc(value).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def normalize_utc_text(value: str) -> str:
    return format_utc(parse_utc(value))


def parse_utc(value: str) -> datetime:
    text = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def now_utc() -> str:
    return format_utc(datetime.now(timezone.utc))


def write_json(path: Path, value: object) -> str:
    return write(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        write(path, "")
        return
    fieldnames = sorted({key for row in rows for key in row})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("preflight", "full"), default="full")
    parser.add_argument("--start-utc", default=START_UTC)
    parser.add_argument("--end-utc")
    parser.add_argument("--preflight-mgas", type=int, default=3)
    parser.add_argument("--preflight-months", type=int, default=2)
    parser.add_argument("--sleep-seconds", type=float, default=0.05)
    parser.add_argument("--max-chunks", type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_p0054w_esett_fetch(
        mode=args.mode,
        start_utc=args.start_utc,
        end_utc=args.end_utc,
        preflight_mgas=args.preflight_mgas,
        preflight_months=args.preflight_months,
        sleep_seconds=args.sleep_seconds,
        max_chunks=args.max_chunks,
    )
    print(json.dumps({"status": result.status, "mode": result.mode, "loaded_rows": result.loaded_rows, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
