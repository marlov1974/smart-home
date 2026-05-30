"""Backfill and daily ingest orchestration for P0031 weather history."""

from __future__ import annotations

from datetime import date, datetime, timedelta
import sqlite3
from typing import Callable

from .models import IngestSummary, WeatherLocation
from .source import (
    fetch_open_meteo_range_with_retry,
    parse_open_meteo_response,
    utc_request_dates_for_local_range,
)
from .storage import (
    AREA_PROXY,
    all_area_proxies,
    compute_all_area_proxy_hourly,
    configured_locations,
    create_ingest_run,
    expected_utc_hours_for_range,
    finish_ingest_run,
    latest_complete_local_date,
    upsert_weather_observations,
    validate_weather_continuity,
)


Fetcher = Callable[[WeatherLocation, date, date], bytes]


def latest_safe_complete_day(today: date | None = None) -> date:
    return (today or date.today()) - timedelta(days=6)


def backfill(
    conn: sqlite3.Connection,
    *,
    start_date: date,
    end_date: date,
    db_path: str,
    fetcher: Fetcher | None = None,
    run_type: str = "backfill",
) -> IngestSummary:
    if end_date < start_date:
        report = validate_weather_continuity(conn, start_date, start_date, db_path=db_path)
        return IngestSummary(db_path, start_date.isoformat(), end_date.isoformat(), 0, 0, 0, 0, "no_new_complete_day_available", report)
    locations = [location for area_proxy in all_area_proxies(conn) for location in configured_locations(conn, area_proxy)]
    fetch = fetcher or (
        lambda location, start_utc_date, end_utc_date: fetch_open_meteo_range_with_retry(
            location, start_utc_date, end_utc_date
        )
    )
    run_id = create_ingest_run(
        conn,
        run_type=run_type,
        start_date=start_date,
        end_date=end_date,
        locations_requested=len(locations),
    )
    expected_hours = expected_utc_hours_for_range(start_date, end_date)
    start_utc_date, end_utc_date = utc_request_dates_for_local_range(start_date, end_date)
    observations_upserted = 0
    fetched_ranges = 0
    try:
        for location in locations:
            if _location_complete(conn, location.location_id, start_date, end_date, len(expected_hours)):
                continue
            payload = fetch(location, start_utc_date, end_utc_date)
            observations = parse_open_meteo_response(payload, location, expected_hours)
            observations_upserted += upsert_weather_observations(conn, observations, run_id)
            fetched_ranges += 1
            conn.commit()
        area_rows = compute_all_area_proxy_hourly(
            conn,
            start_date=start_date,
            end_date=end_date,
            ingest_run_id=run_id,
        )
        conn.commit()
        report = validate_weather_continuity(conn, start_date, end_date, db_path=db_path)
        status = "ok" if report.complete else "incomplete"
        finish_ingest_run(
            conn,
            run_id,
            status=status,
            records_inserted=observations_upserted + area_rows,
            records_updated=0,
            gaps_detected=report.location_gap_count + report.area_gap_count,
            error_summary=",".join(report.errors),
        )
        return IngestSummary(
            db_path,
            start_date.isoformat(),
            end_date.isoformat(),
            len(locations),
            fetched_ranges,
            observations_upserted,
            area_rows,
            status,
            report,
        )
    except Exception as exc:
        finish_ingest_run(
            conn,
            run_id,
            status="error",
            records_inserted=observations_upserted,
            records_updated=0,
            gaps_detected=0,
            error_summary=str(exc),
        )
        raise


def ingest_daily(
    conn: sqlite3.Connection,
    *,
    db_path: str,
    today: date | None = None,
    fetcher: Fetcher | None = None,
) -> IngestSummary:
    safe_day = latest_safe_complete_day(today)
    latest_dates = [
        latest
        for latest in (latest_complete_local_date(conn, area_proxy) for area_proxy in all_area_proxies(conn))
        if latest is not None
    ]
    latest = min(latest_dates) if latest_dates else None
    start = (latest + timedelta(days=1)) if latest else safe_day
    if start > safe_day:
        validation_day = latest or safe_day
        report = validate_weather_continuity(conn, validation_day, validation_day, area_proxy=AREA_PROXY, db_path=db_path)
        run_id = create_ingest_run(
            conn,
            run_type="daily",
            start_date=validation_day,
            end_date=validation_day,
            locations_requested=sum(len(configured_locations(conn, area_proxy)) for area_proxy in all_area_proxies(conn)),
            status="no_new_complete_day_available",
        )
        finish_ingest_run(
            conn,
            run_id,
            status="no_new_complete_day_available",
            records_inserted=0,
            records_updated=0,
            gaps_detected=0,
        )
        return IngestSummary(
            db_path,
            validation_day.isoformat(),
            validation_day.isoformat(),
            sum(len(configured_locations(conn, area_proxy)) for area_proxy in all_area_proxies(conn)),
            0,
            0,
            0,
            "no_new_complete_day_available",
            report,
        )
    return backfill(conn, start_date=start, end_date=safe_day, db_path=db_path, fetcher=fetcher, run_type="daily")


def _location_complete(
    conn: sqlite3.Connection,
    location_id: str,
    start_date: date,
    end_date: date,
    expected_count: int,
) -> bool:
    row = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM weather_observations
        WHERE location_id=? AND local_date BETWEEN ? AND ?
        """,
        (location_id, start_date.isoformat(), end_date.isoformat()),
    ).fetchone()
    if row is None or int(row["count"]) != expected_count:
        return False
    null_checks = [
        "temperature_2m IS NULL",
        "apparent_temperature IS NULL",
        "wind_speed_10m IS NULL",
        "wind_speed_100m IS NULL",
        "wind_gusts_10m IS NULL",
        "cloud_cover IS NULL",
        "shortwave_radiation IS NULL",
        "precipitation IS NULL",
        "snowfall IS NULL",
        "relative_humidity_2m IS NULL",
        "pressure_msl IS NULL",
    ]
    null_row = conn.execute(
        f"""
        SELECT COUNT(*) AS count
        FROM weather_observations
        WHERE location_id=? AND local_date BETWEEN ? AND ? AND ({" OR ".join(null_checks)})
        """,
        (location_id, start_date.isoformat(), end_date.isoformat()),
    ).fetchone()
    return null_row is not None and int(null_row["count"]) == 0
