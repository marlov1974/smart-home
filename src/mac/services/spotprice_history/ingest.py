"""Backfill and daily ingest orchestration for P0030 spot history."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import sqlite3
from typing import Callable

from .models import IngestSummary
from .source import fetch_source_day_with_retry, source_url, parse_price_day
from .storage import record_ingest_run, upsert_prices, validate_range, latest_complete_local_date


Fetcher = Callable[[str, date], bytes]


def backfill(
    conn: sqlite3.Connection,
    *,
    area: str,
    start_date: date,
    end_date: date,
    db_path: str,
    fetcher: Fetcher | None = None,
    command: str = "backfill",
) -> IngestSummary:
    fetch = fetcher or (lambda fetch_area, fetch_date: fetch_source_day_with_retry(fetch_area, fetch_date))
    started = _now()
    fetched_days = 0
    upserted_rows = 0
    current = start_date
    while current <= end_date:
        try:
            payload = fetch(area, current)
        except Exception as exc:
            raise RuntimeError(f"fetch failed for {area} {current}: {exc}") from exc
        rows = parse_price_day(payload, area, source_url(area, current))
        upserted_rows += upsert_prices(conn, rows)
        conn.commit()
        fetched_days += 1
        current += timedelta(days=1)
    validation = validate_range(conn, area, start_date, end_date, db_path=db_path)
    finished = _now()
    record_ingest_run(
        conn,
        area=area,
        command=command,
        started_at=started,
        finished_at=finished,
        start_date=start_date,
        end_date=end_date,
        fetched_days=fetched_days,
        upserted_rows=upserted_rows,
        ok=validation.ok,
        message="ok" if validation.ok else ",".join(validation.errors),
    )
    if not validation.ok:
        raise ValueError(f"spot history validation failed: {validation.errors}")
    return IngestSummary(
        area=area,
        db_path=db_path,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        fetched_days=fetched_days,
        upserted_rows=upserted_rows,
        validation=validation,
    )


def ingest_daily(
    conn: sqlite3.Connection,
    *,
    area: str,
    db_path: str,
    today: date | None = None,
    fetcher: Fetcher | None = None,
) -> IngestSummary:
    local_today = today or datetime.now().date()
    newest_complete = local_today - timedelta(days=1)
    latest = latest_complete_local_date(conn, area)
    start = (latest + timedelta(days=1)) if latest else newest_complete
    if start > newest_complete:
        validation_start = latest or newest_complete
        validation = validate_range(conn, area, validation_start, latest, db_path=db_path)
        now = _now()
        record_ingest_run(
            conn,
            area=area,
            command="ingest-daily",
            started_at=now,
            finished_at=now,
            start_date=validation_start,
            end_date=latest or validation_start,
            fetched_days=0,
            upserted_rows=0,
            ok=validation.ok,
            message="no-op" if validation.ok else ",".join(validation.errors),
        )
        return IngestSummary(
            area=area,
            db_path=db_path,
            start_date=validation.start_date,
            end_date=validation.end_date,
            fetched_days=0,
            upserted_rows=0,
            validation=validation,
        )
    return backfill(
        conn,
        area=area,
        start_date=start,
        end_date=newest_complete,
        db_path=db_path,
        fetcher=fetcher,
        command="ingest-daily",
    )


def ingest_daily_for_areas(
    conn: sqlite3.Connection,
    *,
    areas: list[str],
    db_path: str,
    today: date | None = None,
    fetcher: Fetcher | None = None,
) -> list[IngestSummary]:
    return [
        ingest_daily(conn, area=area, db_path=db_path, today=today, fetcher=fetcher)
        for area in areas
    ]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
