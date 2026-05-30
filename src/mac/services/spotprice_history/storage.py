"""SQLite storage for P0030 spot price history."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import sqlite3
from typing import Sequence
from zoneinfo import ZoneInfo

from .models import HourlySpotPrice, ValidationReport


SCHEMA_VERSION = "1"
DEFAULT_DB_PATH = Path.home() / ".smart-home" / "data" / "spotprice_history.sqlite3"
STOCKHOLM = ZoneInfo("Europe/Stockholm")


def default_db_path() -> Path:
    return DEFAULT_DB_PATH


def connect_db(path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(Path(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path: Path | str) -> None:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect_db(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_meta (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS spot_prices (
              area TEXT NOT NULL,
              utc_hour_start TEXT NOT NULL,
              local_hour_start TEXT NOT NULL,
              local_date TEXT NOT NULL,
              local_hour INTEGER NOT NULL,
              utc_offset TEXT NOT NULL,
              fold INTEGER NOT NULL,
              price_sek_per_kwh REAL NOT NULL,
              price_eur_per_kwh REAL,
              exchange_rate REAL,
              source TEXT NOT NULL,
              source_resolution TEXT NOT NULL,
              samples INTEGER NOT NULL,
              ingested_at TEXT NOT NULL,
              PRIMARY KEY (area, utc_hour_start)
            );
            CREATE INDEX IF NOT EXISTS idx_spot_prices_area_local_date
              ON spot_prices(area, local_date);
            CREATE TABLE IF NOT EXISTS ingest_runs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              area TEXT NOT NULL,
              command TEXT NOT NULL,
              started_at TEXT NOT NULL,
              finished_at TEXT NOT NULL,
              start_date TEXT NOT NULL,
              end_date TEXT NOT NULL,
              fetched_days INTEGER NOT NULL,
              upserted_rows INTEGER NOT NULL,
              ok INTEGER NOT NULL,
              message TEXT NOT NULL
            );
            """
        )
        conn.execute(
            "INSERT OR REPLACE INTO schema_meta(key, value) VALUES('schema_version', ?)",
            (SCHEMA_VERSION,),
        )


def expected_utc_hours_for_local_date(local_date: date) -> tuple[datetime, ...]:
    start_local = datetime.combine(local_date, datetime.min.time(), tzinfo=STOCKHOLM)
    end_local = datetime.combine(local_date + timedelta(days=1), datetime.min.time(), tzinfo=STOCKHOLM)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)
    hours: list[datetime] = []
    current = start_utc
    while current < end_utc:
        hours.append(current)
        current += timedelta(hours=1)
    return tuple(hours)


def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:00Z")


def upsert_prices(conn: sqlite3.Connection, rows: Sequence[HourlySpotPrice]) -> int:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    conn.executemany(
        """
        INSERT INTO spot_prices (
          area, utc_hour_start, local_hour_start, local_date, local_hour,
          utc_offset, fold, price_sek_per_kwh, price_eur_per_kwh, exchange_rate,
          source, source_resolution, samples, ingested_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(area, utc_hour_start) DO UPDATE SET
          local_hour_start=excluded.local_hour_start,
          local_date=excluded.local_date,
          local_hour=excluded.local_hour,
          utc_offset=excluded.utc_offset,
          fold=excluded.fold,
          price_sek_per_kwh=excluded.price_sek_per_kwh,
          price_eur_per_kwh=excluded.price_eur_per_kwh,
          exchange_rate=excluded.exchange_rate,
          source=excluded.source,
          source_resolution=excluded.source_resolution,
          samples=excluded.samples,
          ingested_at=excluded.ingested_at
        """,
        [
            (
                row.area,
                row.utc_hour_start,
                row.local_hour_start,
                row.local_date,
                row.local_hour,
                row.utc_offset,
                row.fold,
                row.price_sek_per_kwh,
                row.price_eur_per_kwh,
                row.exchange_rate,
                row.source,
                row.source_resolution,
                row.samples,
                now,
            )
            for row in rows
        ],
    )
    return len(rows)


def latest_complete_local_date(conn: sqlite3.Connection, area: str) -> date | None:
    rows = conn.execute(
        "SELECT DISTINCT local_date FROM spot_prices WHERE area=? ORDER BY local_date DESC",
        (area,),
    ).fetchall()
    for row in rows:
        candidate = date.fromisoformat(row["local_date"])
        report = validate_range(conn, area, candidate, candidate, db_path="")
        if report.ok:
            return candidate
    return None


def validate_range(
    conn: sqlite3.Connection,
    area: str,
    start_date: date,
    end_date: date | None = None,
    db_path: str = "",
) -> ValidationReport:
    if end_date is None:
        row = conn.execute(
            "SELECT MAX(local_date) AS local_date FROM spot_prices WHERE area=?",
            (area,),
        ).fetchone()
        if row is None or row["local_date"] is None:
            end_date = start_date
        else:
            end_date = date.fromisoformat(row["local_date"])
    if end_date < start_date:
        end_date = start_date

    expected: list[str] = []
    current_date = start_date
    while current_date <= end_date:
        expected.extend(iso_z(hour) for hour in expected_utc_hours_for_local_date(current_date))
        current_date += timedelta(days=1)

    rows = conn.execute(
        """
        SELECT utc_hour_start, local_date, price_sek_per_kwh
        FROM spot_prices
        WHERE area=? AND local_date BETWEEN ? AND ?
        ORDER BY utc_hour_start
        """,
        (area, start_date.isoformat(), end_date.isoformat()),
    ).fetchall()
    actual = [row["utc_hour_start"] for row in rows]
    actual_set = set(actual)
    duplicate_count = len(actual) - len(actual_set)
    missing = [hour for hour in expected if hour not in actual_set]
    extra = [hour for hour in actual if hour not in set(expected)]
    prices = [float(row["price_sek_per_kwh"]) for row in rows]
    per_year: dict[str, int] = {}
    for row in rows:
        year = row["local_date"][:4]
        per_year[year] = per_year.get(year, 0) + 1

    errors: list[str] = []
    if missing:
        errors.append(f"missing_hours={len(missing)}")
    if extra:
        errors.append(f"unexpected_hours={len(extra)}")
    if duplicate_count:
        errors.append(f"duplicate_hours={duplicate_count}")

    return ValidationReport(
        area=area,
        db_path=db_path,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        ok=not errors,
        row_count=len(rows),
        expected_count=len(expected),
        first_utc_hour_start=actual[0] if actual else None,
        last_utc_hour_start=actual[-1] if actual else None,
        duplicate_count=duplicate_count,
        gap_count=len(missing),
        negative_price_count=sum(1 for price in prices if price < 0),
        min_price_sek_per_kwh=min(prices) if prices else None,
        max_price_sek_per_kwh=max(prices) if prices else None,
        mean_price_sek_per_kwh=(sum(prices) / len(prices)) if prices else None,
        per_year_counts=per_year,
        errors=tuple(errors),
    )


def record_ingest_run(
    conn: sqlite3.Connection,
    *,
    area: str,
    command: str,
    started_at: str,
    finished_at: str,
    start_date: date,
    end_date: date,
    fetched_days: int,
    upserted_rows: int,
    ok: bool,
    message: str,
) -> None:
    conn.execute(
        """
        INSERT INTO ingest_runs (
          area, command, started_at, finished_at, start_date, end_date,
          fetched_days, upserted_rows, ok, message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            area,
            command,
            started_at,
            finished_at,
            start_date.isoformat(),
            end_date.isoformat(),
            fetched_days,
            upserted_rows,
            1 if ok else 0,
            message,
        ),
    )
