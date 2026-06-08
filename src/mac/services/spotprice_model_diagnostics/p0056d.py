"""P0056D LABB SE1/SE2/FI Open-Meteo weather proxy retune."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import csv
import json
import math
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0054k, p0054n, p0054q, p0054r, p0056c
from src.mac.services.spotprice_model_diagnostics.p0041 import write
from src.mac.services.weather_history.models import WEATHER_VARIABLES, WeatherLocation, WeatherObservation
from src.mac.services.weather_history.source import ARCHIVE_URL, fetch_open_meteo_range, parse_open_meteo_response


PACKAGE_ID = "P0056D"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0056D")
SCOPED_AREAS = ("SE1", "SE2", "FI")
START_DATE = date(2022, 6, 1)
END_DATE = date(2026, 5, 31)
REQUEST_SPACING_SECONDS = 5.0
FETCH_CHUNK_MONTHS = 3

ZONE_TABLE = "area_weather_zone_openmeteo_hourly_p0056d_v1"
PROXY_TABLE = "area_weather_proxy_hourly_p0056d_v1"
FEATURE_TABLE = "area_weather_features_hourly_p0056d_v1"
WEIGHT_TABLE = "area_weather_proxy_weights_p0056d_v1"
FORECAST_TABLE = "area_consumption_forecast_log_p0056d_v1"
METRICS_TABLE = "area_consumption_forecast_metrics_p0056d_v1"

P0056C_BASELINE_CSV = Path("requirements/package-runs/P0056C/area-results.csv")
P0056D_WEATHER_LABEL = "weather_actual_as_forecast_proxy_p0056d_openmeteo_zone_weighted"


@dataclass(frozen=True)
class WeatherZone:
    area_code: str
    zone_id: str
    description: str
    weight: float
    confidence: str
    rationale: str


@dataclass(frozen=True)
class RepresentativeLocation:
    area_code: str
    zone_id: str
    location_id: str
    name: str
    latitude: float
    longitude: float
    location_weight_in_zone: float


@dataclass(frozen=True)
class P0056DResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def weather_zones() -> list[WeatherZone]:
    return [
        WeatherZone("SE1", "SE1_LULEA_PITEA_BODEN", "Lulea, Pitea and Boden coastal/load-centre zone.", 0.45, "medium", "Largest SE1 coastal population and industrial/electrification load centre."),
        WeatherZone("SE1", "SE1_KIRUNA_GALLIVARE", "Kiruna and Gallivare mining/inland zone.", 0.20, "medium", "Important mining and inland cold-weather demand."),
        WeatherZone("SE1", "SE1_SKELLEFTEA", "Skelleftea coastal industrial zone.", 0.25, "medium", "Large coastal municipality and industrial load growth."),
        WeatherZone("SE1", "SE1_HAPARANDA", "Haparanda eastern border coastal zone.", 0.10, "low", "Small but distinct far-eastern coastal climate."),
        WeatherZone("SE2", "SE2_SUNDSVALL_HARNOSAND_ORNSKOLDSVIK", "Sundsvall, Harnosand and Ornskoldsvik coastal corridor.", 0.30, "medium", "Large SE2 coastal population and industry corridor."),
        WeatherZone("SE2", "SE2_UMEA", "Umea northern coastal university/load centre.", 0.25, "medium", "Large municipality and important northern coastal load centre."),
        WeatherZone("SE2", "SE2_HUDIKSVALL", "Hudiksvall southern coastal zone.", 0.12, "low", "Southern coastal climate and load representation."),
        WeatherZone("SE2", "SE2_SOLLEFTEA_KRAMFORS", "Solleftea and Kramfors inland/coastal transition.", 0.13, "low", "Middle-Angermanland load and inland/coastal transition."),
        WeatherZone("SE2", "SE2_OSTERSUND_ARE", "Ostersund and Are inland/mountain zone.", 0.20, "medium", "Large inland centre plus mountain/tourism cold-load regime."),
        WeatherZone("FI", "FI_HELSINKI_ESPOO_VANTAA_RING", "Helsinki, Espoo, Vantaa, Kerava and Kirkkonummi metropolitan ring.", 0.45, "medium", "Dominant Finnish population and load concentration."),
        WeatherZone("FI", "FI_TURKU_PORI", "Turku and Pori southwest/west coast zone.", 0.15, "medium", "Major southwest and west-coast load centres."),
        WeatherZone("FI", "FI_TAMPERE_LAHTI_HAMEENLINNA_KOUVOLA", "Tampere, Lahti, Hameenlinna and Kouvola southern inland zone.", 0.20, "medium", "Large southern inland population/load belt."),
        WeatherZone("FI", "FI_JYVASKYLA_KUOPIO_MIKKELI_JOENSUU", "Central and eastern Finland inland zone.", 0.10, "low", "Broad central/eastern inland load and colder regime."),
        WeatherZone("FI", "FI_OULU_VAASA", "Oulu and Vaasa northern/western coastal zone.", 0.10, "low", "Northern and western coastal load representation."),
    ]


def representative_locations() -> list[RepresentativeLocation]:
    raw = [
        ("SE1", "SE1_LULEA_PITEA_BODEN", "Lulea", 65.5848, 22.1547),
        ("SE1", "SE1_LULEA_PITEA_BODEN", "Pitea", 65.3172, 21.4794),
        ("SE1", "SE1_LULEA_PITEA_BODEN", "Boden", 65.8252, 21.6886),
        ("SE1", "SE1_KIRUNA_GALLIVARE", "Kiruna", 67.8558, 20.2253),
        ("SE1", "SE1_KIRUNA_GALLIVARE", "Gallivare", 67.1339, 20.6528),
        ("SE1", "SE1_SKELLEFTEA", "Skelleftea", 64.7507, 20.9528),
        ("SE1", "SE1_HAPARANDA", "Haparanda", 65.8355, 24.1368),
        ("SE2", "SE2_SUNDSVALL_HARNOSAND_ORNSKOLDSVIK", "Sundsvall", 62.3908, 17.3069),
        ("SE2", "SE2_SUNDSVALL_HARNOSAND_ORNSKOLDSVIK", "Harnosand", 62.6323, 17.9379),
        ("SE2", "SE2_SUNDSVALL_HARNOSAND_ORNSKOLDSVIK", "Ornskoldsvik", 63.2909, 18.7153),
        ("SE2", "SE2_UMEA", "Umea", 63.8258, 20.2630),
        ("SE2", "SE2_HUDIKSVALL", "Hudiksvall", 61.7290, 17.1036),
        ("SE2", "SE2_SOLLEFTEA_KRAMFORS", "Solleftea", 63.1667, 17.2667),
        ("SE2", "SE2_SOLLEFTEA_KRAMFORS", "Kramfors", 62.9316, 17.7765),
        ("SE2", "SE2_OSTERSUND_ARE", "Ostersund", 63.1792, 14.6357),
        ("SE2", "SE2_OSTERSUND_ARE", "Are", 63.3990, 13.0810),
        ("FI", "FI_HELSINKI_ESPOO_VANTAA_RING", "Helsinki", 60.1699, 24.9384),
        ("FI", "FI_HELSINKI_ESPOO_VANTAA_RING", "Espoo", 60.2055, 24.6559),
        ("FI", "FI_HELSINKI_ESPOO_VANTAA_RING", "Vantaa", 60.2934, 25.0378),
        ("FI", "FI_HELSINKI_ESPOO_VANTAA_RING", "Kerava", 60.4034, 25.1050),
        ("FI", "FI_HELSINKI_ESPOO_VANTAA_RING", "Kirkkonummi", 60.1238, 24.4385),
        ("FI", "FI_TURKU_PORI", "Turku", 60.4518, 22.2666),
        ("FI", "FI_TURKU_PORI", "Pori", 61.4851, 21.7972),
        ("FI", "FI_TAMPERE_LAHTI_HAMEENLINNA_KOUVOLA", "Tampere", 61.4978, 23.7610),
        ("FI", "FI_TAMPERE_LAHTI_HAMEENLINNA_KOUVOLA", "Lahti", 60.9827, 25.6615),
        ("FI", "FI_TAMPERE_LAHTI_HAMEENLINNA_KOUVOLA", "Hameenlinna", 60.9959, 24.4643),
        ("FI", "FI_TAMPERE_LAHTI_HAMEENLINNA_KOUVOLA", "Kouvola", 60.8667, 26.7042),
        ("FI", "FI_JYVASKYLA_KUOPIO_MIKKELI_JOENSUU", "Jyvaskyla", 62.2426, 25.7473),
        ("FI", "FI_JYVASKYLA_KUOPIO_MIKKELI_JOENSUU", "Kuopio", 62.8924, 27.6770),
        ("FI", "FI_JYVASKYLA_KUOPIO_MIKKELI_JOENSUU", "Mikkeli", 61.6886, 27.2723),
        ("FI", "FI_JYVASKYLA_KUOPIO_MIKKELI_JOENSUU", "Joensuu", 62.6010, 29.7636),
        ("FI", "FI_OULU_VAASA", "Oulu", 65.0121, 25.4651),
        ("FI", "FI_OULU_VAASA", "Vaasa", 63.0951, 21.6165),
    ]
    counts = defaultdict(int)
    for _, zone_id, _, _, _ in raw:
        counts[zone_id] += 1
    out = []
    for area, zone_id, name, lat, lon in raw:
        out.append(RepresentativeLocation(area, zone_id, f"{zone_id}_{ascii_id(name)}", name, lat, lon, 1.0 / counts[zone_id]))
    return out


def ascii_id(value: str) -> str:
    return value.upper().replace(" ", "_")


def zone_weights() -> list[dict[str, object]]:
    return [
        {
            "area_code": zone.area_code,
            "zone_id": zone.zone_id,
            "zone_weight": zone.weight,
            "confidence": zone.confidence,
            "rationale": zone.rationale,
            "source": "manual_deterministic_load_centre_approximation",
            "generated_by_package": PACKAGE_ID,
        }
        for zone in weather_zones()
    ]


def run_p0056d_retest(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
    start_date: date = START_DATE,
    end_date: date = END_DATE,
) -> P0056DResult:
    started = time.monotonic()
    feature_path = Path(feature_db).expanduser()
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)
    reset_progress_log(evidence_path)

    with sqlite3.connect(feature_path, timeout=60.0) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=60000")
        create_schema(conn)
        reset_package_tables(conn)
        fetch_summary = fetch_and_store_openmeteo(conn, start_date, end_date, evidence_path)
        if fetch_summary.get("status") != "PASS":
            summary = {
                "package_id": PACKAGE_ID,
                "label": LABEL,
                "status": "WARN",
                "runtime_seconds": round(time.monotonic() - started, 3),
                "feature_db": str(feature_path),
                "date_range": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
                "openmeteo_contract": openmeteo_contract(start_date, end_date),
                "fetch_summary": fetch_summary,
                "row_counts": row_counts(conn),
                "reason": "Open-Meteo fetch incomplete; checkpoint written for later resume.",
                "no_devices": True,
                "no_runtime_change": True,
                "no_production_activation": True,
            }
            evidence = write_fetch_incomplete_evidence(evidence_path, summary)
            return P0056DResult(status="WARN", row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]
        weights_summary = persist_weights(conn)
        proxy_summary = build_area_weather_features(conn)
        retest_summary = run_forecast_retest(conn, evidence_path)
        comparison = compare_against_p0056c(retest_summary["area_results"])  # type: ignore[arg-type]
        leakage = p0056d_leakage_review(
            retest_summary["scored_rows"],  # type: ignore[arg-type]
            p0056c.p0056c_feature_names(),
            retest_summary["target_contract"],  # type: ignore[arg-type]
            retest_summary["weather_contract"],  # type: ignore[arg-type]
            retest_summary["area_results"],  # type: ignore[arg-type]
        )
        status = decide_status(fetch_summary, proxy_summary, retest_summary, leakage)
        summary = {
            "package_id": PACKAGE_ID,
            "label": LABEL,
            "status": status,
            "runtime_seconds": round(time.monotonic() - started, 3),
            "feature_db": str(feature_path),
            "date_range": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "openmeteo_contract": openmeteo_contract(start_date, end_date),
            "weather_zones": [zone.__dict__ for zone in weather_zones()],
            "representative_locations": [location.__dict__ for location in representative_locations()],
            "zone_weights": zone_weights(),
            "weights_summary": weights_summary,
            "fetch_summary": fetch_summary,
            "proxy_summary": proxy_summary,
            "forecast_retest": without_scored_rows(retest_summary),
            "comparison": comparison,
            "leakage_review": leakage,
            "row_counts": row_counts(conn),
            "no_devices": True,
            "no_runtime_change": True,
            "no_production_activation": True,
            "no_spot_price_features": True,
            "no_flow_exchange_a61_capacity_features": True,
            "no_old_physical_balance_target": True,
            "no_future_actual_load_leakage": True,
            "no_holdout_fitting_or_selection": True,
        }
        evidence = write_evidence(evidence_path, summary)
        return P0056DResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {ZONE_TABLE} (
            timestamp_utc TEXT NOT NULL,
            area_code TEXT NOT NULL,
            zone_id TEXT NOT NULL,
            location_id TEXT NOT NULL,
            location_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            location_weight_in_zone REAL NOT NULL,
            temperature_2m REAL,
            apparent_temperature REAL,
            wind_speed_10m REAL,
            wind_speed_100m REAL,
            wind_gusts_10m REAL,
            cloud_cover REAL,
            shortwave_radiation REAL,
            precipitation REAL,
            snowfall REAL,
            relative_humidity_2m REAL,
            pressure_msl REAL,
            heating_degree_proxy REAL,
            cooling_degree_proxy REAL,
            fetched_at_utc TEXT NOT NULL,
            source_endpoint TEXT NOT NULL,
            source_model TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (timestamp_utc, location_id, generated_by_package)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {WEIGHT_TABLE} (
            area_code TEXT NOT NULL,
            zone_id TEXT NOT NULL,
            zone_weight REAL NOT NULL,
            confidence TEXT NOT NULL,
            rationale TEXT NOT NULL,
            source TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (area_code, zone_id, generated_by_package)
        )
        """
    )
    for table in (PROXY_TABLE, FEATURE_TABLE):
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table} (
                timestamp_utc TEXT NOT NULL,
                area_code TEXT NOT NULL,
                weather_proxy_version TEXT NOT NULL,
                temperature_2m REAL NOT NULL,
                apparent_temperature REAL NOT NULL,
                wind_speed REAL NOT NULL,
                cloud_cover REAL NOT NULL,
                relative_humidity REAL NOT NULL,
                precipitation REAL NOT NULL,
                snowfall REAL NOT NULL,
                snow_depth REAL,
                heating_degree_proxy REAL NOT NULL,
                cooling_degree_proxy REAL NOT NULL,
                temperature_2m_roll_mean_24h REAL NOT NULL,
                source_zone_ids TEXT NOT NULL,
                source_station_or_proxy_ids TEXT NOT NULL,
                zone_weights TEXT NOT NULL,
                missingness_flags TEXT NOT NULL,
                generated_by_package TEXT NOT NULL,
                PRIMARY KEY (timestamp_utc, area_code, generated_by_package)
            )
            """
        )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {FORECAST_TABLE} (
            forecast_origin_timestamp_utc TEXT NOT NULL,
            input_data_cutoff_utc TEXT NOT NULL,
            target_timestamp_utc TEXT NOT NULL,
            horizon_hours INTEGER NOT NULL,
            area_code TEXT NOT NULL,
            model_name TEXT NOT NULL,
            prediction_kind TEXT NOT NULL,
            predicted_consumption_mw REAL NOT NULL,
            actual_consumption_mw REAL NOT NULL,
            evaluation_scope TEXT NOT NULL,
            split TEXT NOT NULL,
            weather_proxy_version TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (forecast_origin_timestamp_utc, target_timestamp_utc, area_code, model_name, generated_by_package)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {METRICS_TABLE} (
            area_code TEXT NOT NULL,
            model_name TEXT NOT NULL,
            metric_scope TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL,
            metric_text TEXT,
            weather_proxy_version TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (area_code, model_name, metric_scope, metric_name, generated_by_package)
        )
        """
    )
    conn.commit()


def reset_package_tables(conn: sqlite3.Connection) -> None:
    # Keep location-level Open-Meteo rows across reruns so a 429 or timeout can resume
    # without refetching already complete locations.
    for table in (WEIGHT_TABLE, PROXY_TABLE, FEATURE_TABLE, FORECAST_TABLE, METRICS_TABLE):
        conn.execute(f"DELETE FROM {table} WHERE generated_by_package=?", (PACKAGE_ID,))
    conn.commit()


def fetch_and_store_openmeteo(conn: sqlite3.Connection, start_date: date, end_date: date, evidence_dir: Path) -> dict[str, object]:
    chunks = fetch_chunks(start_date, end_date)
    expected_total_hours = len(expected_utc_hours(start_date, end_date))
    fetched_at = utc_now()
    location_summaries = []
    checkpoint_rows: list[dict[str, object]] = []
    total_rows = 0
    total_jobs = len(representative_locations()) * len(chunks)
    job_index = 0
    for location in representative_locations():
        location_rows_before = location_row_count(conn, location.location_id)
        if location_rows_before == expected_total_hours:
            for period_start, period_end in chunks:
                job_index += 1
                expected_rows = len(expected_utc_hours(period_start, period_end))
                row = checkpoint_row(location, period_start, period_end, "done", 0, expected_rows, "", utc_now(), "")
                checkpoint_rows.append(row)
                progress(evidence_dir, "fetch", location.location_id, job_index, total_jobs, "cached", extra={"period": f"{period_start}..{period_end}", "rows": expected_rows})
            location_summaries.append({"area_code": location.area_code, "zone_id": location.zone_id, "location_id": location.location_id, "rows": location_rows_before, "fetch_status": "cached_complete"})
            total_rows += location_rows_before
            write_fetch_checkpoint_evidence(evidence_dir, checkpoint_rows, fetch_checkpoint_summary(checkpoint_rows, "RUNNING"))
            continue
        weather_location = WeatherLocation(
            location_id=location.location_id,
            name=location.name,
            latitude=location.latitude,
            longitude=location.longitude,
            weight=location.location_weight_in_zone,
            area_proxy=location.area_code,
            source="openmeteo_archive",
        )
        for period_start, period_end in chunks:
            job_index += 1
            expected_hours = expected_utc_hours(period_start, period_end)
            existing_rows = location_period_row_count(conn, location.location_id, period_start, period_end)
            if existing_rows == len(expected_hours):
                row = checkpoint_row(location, period_start, period_end, "done", 0, existing_rows, "", utc_now(), "")
                checkpoint_rows.append(row)
                progress(evidence_dir, "fetch", location.location_id, job_index, total_jobs, "cached", extra={"period": f"{period_start}..{period_end}", "rows": existing_rows})
                write_fetch_checkpoint_evidence(evidence_dir, checkpoint_rows, fetch_checkpoint_summary(checkpoint_rows, "RUNNING"))
                continue
            progress(evidence_dir, "fetch", location.location_id, job_index, total_jobs, "start", extra={"period": f"{period_start}..{period_end}", "existing_rows": existing_rows})
            attempts = 0
            try:
                payload, attempts = fetch_open_meteo_payload_with_backoff(weather_location, period_start, period_end, evidence_dir, job_index)
                observations = parse_open_meteo_response(payload, weather_location, expected_hours)
                upsert_location_observations(conn, location, observations, fetched_at)
                conn.commit()
                loaded_rows = location_period_row_count(conn, location.location_id, period_start, period_end)
                row = checkpoint_row(location, period_start, period_end, "done", attempts, loaded_rows, "", utc_now(), "")
                checkpoint_rows.append(row)
                progress(evidence_dir, "fetch", location.location_id, job_index, total_jobs, "done", extra={"period": f"{period_start}..{period_end}", "rows": loaded_rows})
                write_fetch_checkpoint_evidence(evidence_dir, checkpoint_rows, fetch_checkpoint_summary(checkpoint_rows, "RUNNING"))
                time.sleep(REQUEST_SPACING_SECONDS)
            except Exception as exc:  # pragma: no cover - live Open-Meteo rate-limit path.
                row = checkpoint_row(location, period_start, period_end, "rate_limited", attempts, existing_rows, str(exc)[:240], utc_now(), "")
                checkpoint_rows.append(row)
                summary = fetch_checkpoint_summary(checkpoint_rows, "WARN")
                summary["blocking_location_id"] = location.location_id
                summary["blocking_period_start"] = period_start.isoformat()
                summary["blocking_period_end"] = period_end.isoformat()
                summary["last_error"] = str(exc)[:400]
                write_fetch_checkpoint_evidence(evidence_dir, checkpoint_rows, summary)
                return summary
        final_location_rows = location_row_count(conn, location.location_id)
        total_rows += final_location_rows
        summary = {"area_code": location.area_code, "zone_id": location.zone_id, "location_id": location.location_id, "rows": final_location_rows, "fetch_status": "complete_or_partial"}
        location_summaries.append(summary)
    conn.commit()
    summary = fetch_checkpoint_summary(checkpoint_rows, "PASS")
    summary.update({
        "locations": len(location_summaries),
        "rows": total_rows,
        "expected_hours_per_location": expected_total_hours,
        "chunks_per_location": len(chunks),
        "location_summaries": location_summaries,
    })
    write_fetch_checkpoint_evidence(evidence_dir, checkpoint_rows, summary)
    return summary


def fetch_chunks(start_date: date, end_date: date) -> list[tuple[date, date]]:
    chunks = []
    current = start_date
    while current <= end_date:
        next_start = add_months(current, FETCH_CHUNK_MONTHS)
        chunk_end = min(end_date, next_start - timedelta(days=1))
        chunks.append((current, chunk_end))
        current = chunk_end + timedelta(days=1)
    return chunks


def add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, days_in_month(year, month))
    return date(year, month, day)


def days_in_month(year: int, month: int) -> int:
    if month == 12:
        return 31
    return (date(year, month + 1, 1) - timedelta(days=1)).day


def location_row_count(conn: sqlite3.Connection, location_id: str) -> int:
    return int(
        conn.execute(
            f"SELECT COUNT(*) FROM {ZONE_TABLE} WHERE generated_by_package=? AND location_id=?",
            (PACKAGE_ID, location_id),
        ).fetchone()[0]
    )


def location_period_row_count(conn: sqlite3.Connection, location_id: str, period_start: date, period_end: date) -> int:
    start_ts = compact_hour_z(datetime(period_start.year, period_start.month, period_start.day, tzinfo=timezone.utc))
    end_ts = compact_hour_z(datetime(period_end.year, period_end.month, period_end.day, 23, tzinfo=timezone.utc))
    return int(
        conn.execute(
            f"""
            SELECT COUNT(*) FROM {ZONE_TABLE}
            WHERE generated_by_package=? AND location_id=?
              AND timestamp_utc >= ? AND timestamp_utc <= ?
            """,
            (PACKAGE_ID, location_id, start_ts, end_ts),
        ).fetchone()[0]
    )


def compact_hour_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def fetch_open_meteo_payload_with_backoff(
    location: WeatherLocation,
    start_date: date,
    end_date: date,
    evidence_dir: Path,
    job_index: int,
) -> tuple[bytes, int]:
    delays = (0.0, 60.0, 180.0, 420.0, 900.0)
    last_error: Exception | None = None
    for attempt, delay in enumerate(delays, start=1):
        if delay:
            progress(evidence_dir, "fetch-backoff", location.location_id, job_index, len(representative_locations()), "sleep", extra={"attempt": attempt, "delay_seconds": delay})
            time.sleep(delay)
        try:
            return fetch_open_meteo_range(location, start_date, end_date, timeout=90.0), attempt
        except Exception as exc:  # pragma: no cover - live network failure path.
            last_error = exc
            progress(evidence_dir, "fetch-backoff", location.location_id, job_index, len(representative_locations()), "retry", extra={"attempt": attempt, "error": str(exc)[:160]})
    raise RuntimeError(f"open-meteo fetch failed for {location.location_id} {start_date}..{end_date}: {last_error}") from last_error


def checkpoint_row(
    location: RepresentativeLocation,
    period_start: date,
    period_end: date,
    status: str,
    attempt_count: int,
    row_count_loaded: int,
    last_error: str,
    last_attempt_at: str,
    next_retry_after_if_known: str,
) -> dict[str, object]:
    return {
        "location_id": location.location_id,
        "zone_id": location.zone_id,
        "area_code": location.area_code,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "status": status,
        "attempt_count": attempt_count,
        "row_count_loaded": row_count_loaded,
        "last_error": last_error,
        "last_attempt_at": last_attempt_at,
        "next_retry_after_if_known": next_retry_after_if_known,
    }


def fetch_checkpoint_summary(checkpoint_rows: list[dict[str, object]], status: str) -> dict[str, object]:
    return {
        "status": status,
        "checkpoint_rows": checkpoint_rows,
        "done_chunks": sum(1 for row in checkpoint_rows if row["status"] == "done"),
        "rate_limited_chunks": sum(1 for row in checkpoint_rows if row["status"] == "rate_limited"),
        "pending_or_unvisited_chunks": len(representative_locations()) * len(fetch_chunks(START_DATE, END_DATE)) - len(checkpoint_rows),
        "expected_chunks": len(representative_locations()) * len(fetch_chunks(START_DATE, END_DATE)),
        "resume_command": "python3 -B -m src.mac.services.spotprice_model_diagnostics.p0056d",
    }


def upsert_location_observations(
    conn: sqlite3.Connection,
    location: RepresentativeLocation,
    observations: list[WeatherObservation],
    fetched_at_utc: str,
) -> int:
    rows = []
    for observation in observations:
        values = observation.values
        temp = float(values["temperature_2m"])
        rows.append(
            (
                observation.utc_hour_start,
                location.area_code,
                location.zone_id,
                location.location_id,
                location.name,
                location.latitude,
                location.longitude,
                location.location_weight_in_zone,
                values["temperature_2m"],
                values["apparent_temperature"],
                values["wind_speed_10m"],
                values["wind_speed_100m"],
                values["wind_gusts_10m"],
                values["cloud_cover"],
                values["shortwave_radiation"],
                values["precipitation"],
                values["snowfall"],
                values["relative_humidity_2m"],
                values["pressure_msl"],
                max(0.0, 17.0 - temp),
                max(0.0, temp - 22.0),
                fetched_at_utc,
                ARCHIVE_URL,
                observation.source_model,
                PACKAGE_ID,
            )
        )
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {ZONE_TABLE}
        (timestamp_utc, area_code, zone_id, location_id, location_name, latitude, longitude,
         location_weight_in_zone, temperature_2m, apparent_temperature, wind_speed_10m,
         wind_speed_100m, wind_gusts_10m, cloud_cover, shortwave_radiation, precipitation,
         snowfall, relative_humidity_2m, pressure_msl, heating_degree_proxy,
         cooling_degree_proxy, fetched_at_utc, source_endpoint, source_model, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    return len(rows)


def persist_weights(conn: sqlite3.Connection) -> dict[str, object]:
    rows = zone_weights()
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {WEIGHT_TABLE}
        (area_code, zone_id, zone_weight, confidence, rationale, source, generated_by_package)
        VALUES (:area_code, :zone_id, :zone_weight, :confidence, :rationale, :source, :generated_by_package)
        """,
        rows,
    )
    conn.commit()
    sums = {
        row["area_code"]: float(row["sum_weight"])
        for row in conn.execute(
            f"SELECT area_code, SUM(zone_weight) AS sum_weight FROM {WEIGHT_TABLE} WHERE generated_by_package=? GROUP BY area_code",
            (PACKAGE_ID,),
        )
    }
    return {"rows": len(rows), "area_weight_sums": sums, "ok": all(abs(value - 1.0) < 1e-9 for value in sums.values()) and set(sums) == set(SCOPED_AREAS)}


def build_area_weather_features(conn: sqlite3.Connection) -> dict[str, object]:
    rows = load_location_weather_for_aggregation(conn)
    weights = {str(row["zone_id"]): float(row["zone_weight"]) for row in zone_weights()}
    zones_by_area = defaultdict(list)
    for zone in weather_zones():
        zones_by_area[zone.area_code].append(zone.zone_id)
    by_area_ts: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_area_ts[(str(row["area_code"]), str(row["timestamp_utc"]))].append(row)

    feature_rows = []
    zone_weights_json = {area: json.dumps({zone_id: weights[zone_id] for zone_id in zone_ids}, sort_keys=True) for area, zone_ids in zones_by_area.items()}
    for (area, ts), group in sorted(by_area_ts.items()):
        zone_means = aggregate_zone_means(group)
        expected_zones = zones_by_area[area]
        missing_zones = [zone_id for zone_id in expected_zones if zone_id not in zone_means]
        if missing_zones:
            continue
        aggregate = weighted_area_weather(zone_means, weights)
        feature_rows.append(
            {
                "timestamp_utc": ts,
                "area_code": area,
                "weather_proxy_version": PACKAGE_ID,
                **aggregate,
                "temperature_2m_roll_mean_24h": 0.0,
                "source_zone_ids": ",".join(expected_zones),
                "source_station_or_proxy_ids": ",".join(sorted(str(row["location_id"]) for row in group)),
                "zone_weights": zone_weights_json[area],
                "missingness_flags": "snow_depth_unavailable;no_missing_required_variables",
                "generated_by_package": PACKAGE_ID,
            }
        )
    add_rolling_temperature(feature_rows)
    persist_feature_rows(conn, feature_rows)
    by_area = summarize_feature_rows(feature_rows)
    return {
        "status": "PASS" if all(by_area.get(area, {}).get("rows", 0) > 0 for area in SCOPED_AREAS) else "STOP",
        "rows": len(feature_rows),
        "areas": by_area,
        "snow_depth_available": False,
    }


def load_location_weather_for_aggregation(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(
        conn.execute(
            f"""
            SELECT timestamp_utc, area_code, zone_id, location_id, location_weight_in_zone,
                   temperature_2m, apparent_temperature, wind_speed_10m, cloud_cover,
                   relative_humidity_2m, precipitation, snowfall, heating_degree_proxy,
                   cooling_degree_proxy
            FROM {ZONE_TABLE}
            WHERE generated_by_package=?
            ORDER BY area_code, timestamp_utc, zone_id, location_id
            """,
            (PACKAGE_ID,),
        )
    )


def aggregate_zone_means(group: list[dict[str, object] | sqlite3.Row]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[dict[str, object] | sqlite3.Row]] = defaultdict(list)
    for row in group:
        grouped[str(row["zone_id"])].append(row)
    out = {}
    for zone_id, rows in grouped.items():
        total_weight = sum(float(row["location_weight_in_zone"]) for row in rows)
        out[zone_id] = {
            "temperature_2m": weighted_mean(rows, "temperature_2m", total_weight),
            "apparent_temperature": weighted_mean(rows, "apparent_temperature", total_weight),
            "wind_speed": weighted_mean(rows, "wind_speed_10m", total_weight),
            "cloud_cover": weighted_mean(rows, "cloud_cover", total_weight),
            "relative_humidity": weighted_mean(rows, "relative_humidity_2m", total_weight),
            "precipitation": weighted_mean(rows, "precipitation", total_weight),
            "snowfall": weighted_mean(rows, "snowfall", total_weight),
            "heating_degree_proxy": weighted_mean(rows, "heating_degree_proxy", total_weight),
            "cooling_degree_proxy": weighted_mean(rows, "cooling_degree_proxy", total_weight),
        }
    return out


def weighted_mean(rows: list[dict[str, object] | sqlite3.Row], key: str, total_weight: float) -> float:
    if total_weight <= 0:
        return 0.0
    return sum(float(row[key]) * float(row["location_weight_in_zone"]) for row in rows) / total_weight


def weighted_area_weather(zone_means: dict[str, dict[str, float]], weights: dict[str, float]) -> dict[str, float | None]:
    keys = ("temperature_2m", "apparent_temperature", "wind_speed", "cloud_cover", "relative_humidity", "precipitation", "snowfall", "heating_degree_proxy", "cooling_degree_proxy")
    out: dict[str, float | None] = {}
    for key in keys:
        out[key] = sum(zone_means[zone_id][key] * weights[zone_id] for zone_id in zone_means)
    out["snow_depth"] = None
    return out


def add_rolling_temperature(rows: list[dict[str, object]]) -> None:
    by_area = defaultdict(list)
    for row in rows:
        by_area[str(row["area_code"])].append(row)
    for area_rows in by_area.values():
        area_rows.sort(key=lambda row: str(row["timestamp_utc"]))
        temps: list[float] = []
        for row in area_rows:
            temps.append(float(row["temperature_2m"]))
            subset = temps[-24:]
            row["temperature_2m_roll_mean_24h"] = sum(subset) / len(subset)


def persist_feature_rows(conn: sqlite3.Connection, rows: list[dict[str, object]]) -> None:
    payload = [
        (
            row["timestamp_utc"],
            row["area_code"],
            row["weather_proxy_version"],
            row["temperature_2m"],
            row["apparent_temperature"],
            row["wind_speed"],
            row["cloud_cover"],
            row["relative_humidity"],
            row["precipitation"],
            row["snowfall"],
            row["snow_depth"],
            row["heating_degree_proxy"],
            row["cooling_degree_proxy"],
            row["temperature_2m_roll_mean_24h"],
            row["source_zone_ids"],
            row["source_station_or_proxy_ids"],
            row["zone_weights"],
            row["missingness_flags"],
            row["generated_by_package"],
        )
        for row in rows
    ]
    for table in (PROXY_TABLE, FEATURE_TABLE):
        conn.executemany(
            f"""
            INSERT OR REPLACE INTO {table}
            (timestamp_utc, area_code, weather_proxy_version, temperature_2m, apparent_temperature,
             wind_speed, cloud_cover, relative_humidity, precipitation, snowfall, snow_depth,
             heating_degree_proxy, cooling_degree_proxy, temperature_2m_roll_mean_24h,
             source_zone_ids, source_station_or_proxy_ids, zone_weights, missingness_flags,
             generated_by_package)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            payload,
        )
    conn.commit()


def summarize_feature_rows(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    by_area = defaultdict(list)
    for row in rows:
        by_area[str(row["area_code"])].append(row)
    return {
        area: {
            "rows": len(area_rows),
            "min_timestamp_utc": min(str(row["timestamp_utc"]) for row in area_rows),
            "max_timestamp_utc": max(str(row["timestamp_utc"]) for row in area_rows),
            "missingness_flags": sorted({str(row["missingness_flags"]) for row in area_rows}),
        }
        for area, area_rows in by_area.items()
    }


def load_p0056d_area_weather_rows(conn: sqlite3.Connection) -> tuple[dict[str, dict[str, dict[str, object]]], dict[str, object]]:
    weather: dict[str, dict[str, dict[str, object]]] = {area: {} for area in SCOPED_AREAS}
    for row in conn.execute(
        f"""
        SELECT timestamp_utc, area_code, temperature_2m, apparent_temperature, wind_speed,
               cloud_cover, relative_humidity, precipitation, snow_depth, heating_degree_proxy,
               cooling_degree_proxy, temperature_2m_roll_mean_24h, source_station_or_proxy_ids,
               missingness_flags, generated_by_package
        FROM {FEATURE_TABLE}
        WHERE generated_by_package=?
        ORDER BY area_code, timestamp_utc
        """,
        (PACKAGE_ID,),
    ):
        area = str(row["area_code"])
        if area not in weather:
            continue
        ts = p0052.normalize_utc_text(row["timestamp_utc"])
        weather[area][ts] = {
            "weather_proxy_temperature_2m_area": p0056c.safe_float_or_zero(row["temperature_2m"]),
            "weather_proxy_apparent_temperature_area": p0056c.safe_float_or_zero(row["apparent_temperature"]),
            "weather_proxy_wind_speed_area": p0056c.safe_float_or_zero(row["wind_speed"]),
            "weather_proxy_cloud_cover_area": p0056c.safe_float_or_zero(row["cloud_cover"]),
            "weather_proxy_humidity_area": p0056c.safe_float_or_zero(row["relative_humidity"]),
            "weather_proxy_precipitation_area": p0056c.safe_float_or_zero(row["precipitation"]),
            "weather_proxy_snow_depth_area": p0056c.safe_float_or_zero(row["snow_depth"]),
            "weather_proxy_heating_degree_hours_area": p0056c.safe_float_or_zero(row["heating_degree_proxy"]),
            "weather_proxy_cooling_degree_hours_area": p0056c.safe_float_or_zero(row["cooling_degree_proxy"]),
            "weather_proxy_temperature_roll_mean_24h_area": p0056c.safe_float_or_zero(row["temperature_2m_roll_mean_24h"]),
            "weather_proxy_source_station_or_proxy_ids": str(row["source_station_or_proxy_ids"]),
            "weather_proxy_missingness_flags": str(row["missingness_flags"]),
            "weather_proxy_label": P0056D_WEATHER_LABEL,
        }
    by_area = {}
    for area, rows in weather.items():
        timestamps = sorted(rows)
        by_area[area] = {
            "rows": len(rows),
            "min_timestamp_utc": min(timestamps) if timestamps else "",
            "max_timestamp_utc": max(timestamps) if timestamps else "",
            "fallback_weather_proxy": False,
            "snow_depth_available": False,
        }
    return weather, {
        "ok": all(meta["rows"] > 0 for meta in by_area.values()),
        "source_table": FEATURE_TABLE,
        "generated_by_package": PACKAGE_ID,
        "input_classification": "historical_observed_only_weather_actual_proxy",
        "proxy_label": P0056D_WEATHER_LABEL,
        "areas": by_area,
        "fallback_areas": [],
        "production_weather_forecast": False,
        "snow_depth_available": False,
    }


def run_forecast_retest(conn: sqlite3.Connection, evidence_dir: Path) -> dict[str, object]:
    targets_all, target_contract_all = p0056c.load_area_targets(conn)
    targets = {area: targets_all[area] for area in SCOPED_AREAS}
    target_contract = {
        **target_contract_all,
        "areas": {area: target_contract_all["areas"][area] for area in SCOPED_AREAS},  # type: ignore[index]
        "ok": all(target_contract_all["areas"][area]["rows"] > 0 for area in SCOPED_AREAS),  # type: ignore[index]
    }
    weather, weather_contract = load_p0056d_area_weather_rows(conn)
    environment = p0054r.capture_environment_status()
    specs = [spec for spec in p0054k.model_specs(environment["imports"]) if spec.family in p0054k.MODEL_FAMILIES]  # type: ignore[arg-type]
    feature_names = p0056c.p0056c_feature_names()
    reduced_feature_names = p0056c.p0056c_reduced_feature_names()

    job_status = []
    area_results = []
    metrics_by_area = {}
    scored_rows = []
    failed_areas = []
    completed_jobs = 0
    total_jobs = len(SCOPED_AREAS) * 2

    for area_index, area_code in enumerate(SCOPED_AREAS):
        learn_job = area_index * 2 + 1
        test_job = area_index * 2 + 2
        try:
            learn = progress(evidence_dir, "learn", area_code, learn_job, total_jobs, "start")
            area_rows = p0056c.build_area_modeling_rows(area_code, targets[area_code], weather[area_code], set(p0054n.HORIZONS_36H))
            for row in area_rows:
                row["weather_proxy_label"] = P0056D_WEATHER_LABEL
                row["weather_source_generated_by_package"] = PACKAGE_ID
                row["dataset_kind"] = "offline_labb_p0056d_weather_proxy_retest_not_deployable"
            model_result = p0056c.learn_area_model(area_code, area_rows, feature_names, reduced_feature_names, specs)
            completed_jobs += 1
            job_status.append(progress(evidence_dir, "learn", area_code, learn_job, total_jobs, "done", started_at=learn["timestamp"], extra={"model_status": model_result["status"], "rows": len(area_rows)}))

            test = progress(evidence_dir, "test", area_code, test_job, total_jobs, "start")
            metrics = p0056c.evaluate_area_model(area_code, model_result["rows"], p0056c.PREDICTION_COLUMN)
            persist_area_outputs(conn, area_code, model_result["rows"], metrics)
            completed_jobs += 1
            job_status.append(progress(evidence_dir, "test", area_code, test_job, total_jobs, "done", started_at=test["timestamp"], extra={"dayahead_rows": metrics["row_counts"]["dayahead_rows"], "full36_rows": metrics["row_counts"]["full36_rows"]}))
            result = p0056c.area_result_summary(area_code, model_result, metrics, targets[area_code], weather[area_code])
            result["weather_proxy_version"] = PACKAGE_ID
            result["weather_fallback_proxy"] = False
            area_results.append(result)
            metrics_by_area[area_code] = metrics
            scored_rows.extend(model_result["rows"])
        except Exception as exc:  # pragma: no cover - package evidence path.
            failed = {"area_code": area_code, "error_type": type(exc).__name__, "error": str(exc)[:600]}
            failed_areas.append(failed)
            job_status.append(progress(evidence_dir, "test", area_code, test_job, total_jobs, "failed", extra=failed))

    return {
        "environment": environment,
        "model_method_contract": p0056c.model_method_contract(feature_names, reduced_feature_names, specs),
        "split_policy": p0056c.split_policy(),
        "target_contract": target_contract,
        "weather_contract": weather_contract,
        "job_status": job_status,
        "completed_jobs": completed_jobs,
        "total_jobs": total_jobs,
        "failed_areas": failed_areas,
        "area_results": area_results,
        "metrics_by_area": metrics_by_area,
        "scored_rows": scored_rows,
    }


def persist_area_outputs(conn: sqlite3.Connection, area_code: str, rows: list[dict[str, object]], metrics: dict[str, object]) -> None:
    selected_ids = {
        (str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"]))
        for row in p0054q.selected_full36_rows(rows) + p0054q.selected_dayahead_rows(rows)
    }
    forecast_rows = []
    for row in rows:
        key = (str(row["forecast_origin_timestamp_utc"]), str(row["target_timestamp_utc"]))
        if row.get("split") != "holdout" or row.get(p0056c.PREDICTION_COLUMN) is None or key not in selected_ids:
            continue
        forecast_rows.append(
            (
                row["forecast_origin_timestamp_utc"],
                row["input_data_cutoff_utc"],
                row["target_timestamp_utc"],
                int(row["horizon_hours"]),
                area_code,
                p0056c.MODEL_NAME,
                "consumption_mw",
                float(row[p0056c.PREDICTION_COLUMN]),
                float(row[p0054k.TARGET_FIELD]),
                "dayahead_or_full36",
                row["split"],
                PACKAGE_ID,
                PACKAGE_ID,
            )
        )
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {FORECAST_TABLE}
        (forecast_origin_timestamp_utc, input_data_cutoff_utc, target_timestamp_utc, horizon_hours,
         area_code, model_name, prediction_kind, predicted_consumption_mw, actual_consumption_mw,
         evaluation_scope, split, weather_proxy_version, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        forecast_rows,
    )
    metric_rows = []
    for row in p0056c.metrics_rows(area_code, metrics):
        metric_rows.append((*row[:-1], PACKAGE_ID, PACKAGE_ID))
    conn.executemany(
        f"""
        INSERT OR REPLACE INTO {METRICS_TABLE}
        (area_code, model_name, metric_scope, metric_name, metric_value, metric_text, weather_proxy_version, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        metric_rows,
    )
    conn.commit()


def compare_against_p0056c(area_results: list[dict[str, object]]) -> dict[str, object]:
    baseline = load_p0056c_baseline()
    rows = []
    for result in area_results:
        area = str(result["area_code"])
        base = baseline[area]
        new_da = float(result["DayAhead_hourly_MAE"])
        new_full = float(result["full_36h_MAE"])
        new_daily = float(result["daily_energy_error_percent_of_actual"])
        base_da = float(base["DayAhead_hourly_MAE"])
        base_full = float(base["full_36h_MAE"])
        base_daily = float(base["daily_energy_error_percent_of_actual"])
        delta_da = new_da - base_da
        delta_full = new_full - base_full
        delta_daily = new_daily - base_daily
        da_improvement = percent_improvement(base_da, new_da)
        full_improvement = percent_improvement(base_full, new_full)
        daily_improvement = percent_improvement(base_daily, new_daily)
        candidate_default = (
            da_improvement >= 2.0
            or (full_improvement >= 2.0 and da_improvement >= 0.0)
            or (daily_improvement >= 5.0 and da_improvement >= -1.0)
        )
        rows.append(
            {
                "area_code": area,
                "P0056C_DayAhead_MAE": base_da,
                "P0056D_DayAhead_MAE": new_da,
                "delta_vs_P0056C_DayAhead_MW": delta_da,
                "delta_vs_P0056C_DayAhead_percent": percent_delta(base_da, new_da),
                "P0056C_full36_MAE": base_full,
                "P0056D_full36_MAE": new_full,
                "delta_vs_P0056C_full36_MW": delta_full,
                "delta_vs_P0056C_full36_percent": percent_delta(base_full, new_full),
                "P0056C_daily_energy_percent": base_daily,
                "P0056D_daily_energy_percent": new_daily,
                "delta_vs_P0056C_daily_energy_percent": delta_daily,
                "dayahead_improvement_percent": da_improvement,
                "full36_improvement_percent": full_improvement,
                "daily_energy_improvement_percent": daily_improvement,
                "candidate_default": candidate_default,
                "decision": "candidate_default" if candidate_default else "keep_P0056B_default",
            }
        )
    return {
        "rows": rows,
        "candidate_default_areas": [row["area_code"] for row in rows if row["candidate_default"]],
        "keep_p0056b_default_areas": [row["area_code"] for row in rows if not row["candidate_default"]],
    }


def load_p0056c_baseline() -> dict[str, dict[str, object]]:
    with P0056C_BASELINE_CSV.open("r", encoding="utf-8") as handle:
        return {row["area_code"]: row for row in csv.DictReader(handle) if row["area_code"] in SCOPED_AREAS}


def percent_delta(baseline: float, new_value: float) -> float:
    return ((new_value - baseline) / baseline) * 100.0 if baseline else 0.0


def percent_improvement(baseline: float, new_value: float) -> float:
    return ((baseline - new_value) / baseline) * 100.0 if baseline else 0.0


def p0056d_leakage_review(
    rows: list[dict[str, object]],
    feature_names: list[str],
    target_contract: dict[str, object],
    weather_contract: dict[str, object],
    area_results: list[dict[str, object]],
) -> dict[str, object]:
    review = p0056c.leakage_review(rows, feature_names, target_contract, weather_contract, area_results)
    review.update(
        {
            "weather_source_table": FEATURE_TABLE,
            "weather_source_generated_by_package": PACKAGE_ID,
            "weather_input_classification": "historical_observed_only_weather_actual_proxy",
            "production_weather_forecast": False,
            "spot_price_feature_used": False,
            "flow_exchange_a61_capacity_feature_used": False,
            "future_actual_load_feature_used": False,
        }
    )
    return review


def decide_status(
    fetch_summary: dict[str, object],
    proxy_summary: dict[str, object],
    retest_summary: dict[str, object],
    leakage: dict[str, object],
) -> str:
    if (
        fetch_summary.get("status") != "PASS"
        or proxy_summary.get("status") != "PASS"
        or int(retest_summary.get("completed_jobs", 0)) != int(retest_summary.get("total_jobs", 1))
        or retest_summary.get("failed_areas")
        or not leakage.get("ok")
    ):
        return "STOP"
    return "WARN"


def row_counts(conn: sqlite3.Connection) -> dict[str, int]:
    return {
        "location_weather_rows": table_count(conn, ZONE_TABLE),
        "weight_rows": table_count(conn, WEIGHT_TABLE),
        "proxy_rows": table_count(conn, PROXY_TABLE),
        "feature_rows": table_count(conn, FEATURE_TABLE),
        "forecast_log_rows": table_count(conn, FORECAST_TABLE),
        "metrics_rows": table_count(conn, METRICS_TABLE),
    }


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {table} WHERE generated_by_package=?", (PACKAGE_ID,)).fetchone()[0])


def expected_utc_hours(start_date: date, end_date: date) -> tuple[datetime, ...]:
    start = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
    end = datetime(end_date.year, end_date.month, end_date.day, 23, tzinfo=timezone.utc)
    hours = []
    current = start
    while current <= end:
        hours.append(current)
        current += timedelta(hours=1)
    return tuple(hours)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def reset_progress_log(evidence_dir: Path) -> None:
    write(evidence_dir / "progress-log.md", "# P0056D Progress Log\n\n")


def progress(
    evidence_dir: Path,
    phase: str,
    item: str,
    job: int,
    total_jobs: int,
    status: str,
    *,
    started_at: str | None = None,
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    now = utc_now()
    elapsed = None
    if started_at:
        elapsed = (p0052.parse_utc(now) - p0052.parse_utc(started_at)).total_seconds()
    parts = [f"[P0056D progress] phase={phase}", f"item={item}", f"job={job}/{total_jobs}", f"status={status}"]
    if status == "start":
        parts.append(f"timestamp={now}")
    if elapsed is not None:
        parts.append(f"elapsed_seconds={elapsed:.3f}")
    if extra:
        parts.extend(f"{key}={value}" for key, value in extra.items())
    line = " ".join(parts)
    print(line, flush=True)
    with (evidence_dir / "progress-log.md").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    return {"phase": phase, "item": item, "job": job, "total_jobs": total_jobs, "status": status, "timestamp": now, "elapsed_seconds": elapsed, **(extra or {})}


def openmeteo_contract(start_date: date, end_date: date) -> dict[str, object]:
    return {
        "endpoint": ARCHIVE_URL,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "timezone": "GMT",
        "models": "best_match",
        "variables": list(WEATHER_VARIABLES),
        "minimum_required_variables": ["temperature_2m"],
        "preferred_variables_present": ["apparent_temperature", "wind_speed_10m", "cloud_cover", "relative_humidity_2m", "precipitation"],
        "preferred_variables_missing": ["snow_depth"],
        "batching": f"one representative location-period per request; {FETCH_CHUNK_MONTHS}-month chunks; upserted incrementally by chunk",
        "utc_handling": "Open-Meteo GMT hourly timestamps parsed as UTC and stored with Z suffix",
    }


def without_scored_rows(summary: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in summary.items() if key != "scored_rows"}


def write_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    comparison_rows = summary["comparison"]["rows"]  # type: ignore[index]
    area_results = summary["forecast_retest"]["area_results"]  # type: ignore[index]
    evidence = {
        "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", changelog_md(summary)),
        "labb-label.md": write(evidence_dir / "labb-label.md", labb_label_md()),
        "p0056c-baseline-review.md": write(evidence_dir / "p0056c-baseline-review.md", p0056c_baseline_review_md()),
        "weather-zone-design.md": write(evidence_dir / "weather-zone-design.md", weather_zone_design_md(summary)),
        "zone-weighting-method.md": write(evidence_dir / "zone-weighting-method.md", zone_weighting_method_md(summary)),
        "openmeteo-fetch-contract.md": write(evidence_dir / "openmeteo-fetch-contract.md", json_report("P0056D Open-Meteo Fetch Contract", summary["openmeteo_contract"])),
        "openmeteo-fetch-evidence.md": write(evidence_dir / "openmeteo-fetch-evidence.md", json_report("P0056D Open-Meteo Fetch Evidence", compact_fetch_summary(summary["fetch_summary"]))),
        "output-table-schema.md": write(evidence_dir / "output-table-schema.md", output_table_schema_md()),
        "weather-feature-contract.md": write(evidence_dir / "weather-feature-contract.md", weather_feature_contract_md(summary)),
        "coverage-and-missingness.md": write(evidence_dir / "coverage-and-missingness.md", json_report("P0056D Coverage And Missingness", summary["proxy_summary"])),
        "weather-proxy-validation.md": write(evidence_dir / "weather-proxy-validation.md", weather_proxy_validation_md(summary)),
        "forecast-retest-method.md": write(evidence_dir / "forecast-retest-method.md", forecast_retest_method_md(summary)),
        "area-results.md": write(evidence_dir / "area-results.md", area_results_md(area_results)),
        "comparison-vs-p0056c.md": write(evidence_dir / "comparison-vs-p0056c.md", comparison_md(comparison_rows)),
        "leakage-review.md": write(evidence_dir / "leakage-review.md", json_report("P0056D Leakage Review", summary["leakage_review"])),
        "decision.md": write(evidence_dir / "decision.md", decision_md(summary)),
        "what-we-learned.md": write(evidence_dir / "what-we-learned.md", what_we_learned_md(summary)),
        "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", next_package_recommendation_md()),
        "zone-weights.csv": write_csv(evidence_dir / "zone-weights.csv", summary["zone_weights"]),  # type: ignore[arg-type]
        "station-location-selection.csv": write_csv(evidence_dir / "station-location-selection.csv", summary["representative_locations"]),  # type: ignore[arg-type]
        "weather-coverage-summary.csv": write_csv(evidence_dir / "weather-coverage-summary.csv", coverage_csv_rows(summary)),
        "area-results.csv": write_csv(evidence_dir / "area-results.csv", area_results),  # type: ignore[arg-type]
        "comparison-vs-p0056c.csv": write_csv(evidence_dir / "comparison-vs-p0056c.csv", comparison_rows),  # type: ignore[arg-type]
        "metrics-summary.json": write(evidence_dir / "metrics-summary.json", json.dumps(json_safe(compact_summary(summary)), indent=2, sort_keys=True) + "\n"),
    }
    return evidence


def write_fetch_checkpoint_evidence(
    evidence_dir: Path,
    checkpoint_rows: list[dict[str, object]],
    summary: dict[str, object],
) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    return {
        "openmeteo-fetch-checkpoint.md": write(evidence_dir / "openmeteo-fetch-checkpoint.md", fetch_checkpoint_md(checkpoint_rows, summary)),
        "openmeteo-fetch-progress.md": write(evidence_dir / "openmeteo-fetch-progress.md", fetch_progress_md(checkpoint_rows, summary)),
        "openmeteo-resume-instructions.md": write(evidence_dir / "openmeteo-resume-instructions.md", fetch_resume_instructions_md(summary)),
    }


def write_fetch_incomplete_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    fetch_summary = summary["fetch_summary"]  # type: ignore[index]
    checkpoint_rows = fetch_summary.get("checkpoint_rows", []) if isinstance(fetch_summary, dict) else []
    evidence = write_fetch_checkpoint_evidence(evidence_dir, checkpoint_rows, fetch_summary if isinstance(fetch_summary, dict) else {})
    evidence.update(
        {
            "CHANGELOG.md": write(evidence_dir / "CHANGELOG.md", fetch_incomplete_changelog_md(summary)),
            "openmeteo-fetch-evidence.md": write(evidence_dir / "openmeteo-fetch-evidence.md", json_report("P0056D Open-Meteo Fetch Evidence", compact_fetch_summary(fetch_summary))),
            "coverage-and-missingness.md": write(evidence_dir / "coverage-and-missingness.md", fetch_incomplete_coverage_md(summary)),
            "decision.md": write(evidence_dir / "decision.md", fetch_incomplete_decision_md(summary)),
            "next-package-recommendation.md": write(evidence_dir / "next-package-recommendation.md", fetch_incomplete_next_package_md(summary)),
        }
    )
    return evidence


def fetch_checkpoint_md(checkpoint_rows: list[dict[str, object]], summary: dict[str, object]) -> str:
    lines = [
        "# P0056D Open-Meteo Fetch Checkpoint",
        "",
        f"- Status: `{summary.get('status', 'UNKNOWN')}`",
        f"- Done chunks: `{summary.get('done_chunks', 0)}`",
        f"- Rate-limited chunks: `{summary.get('rate_limited_chunks', 0)}`",
        f"- Pending/unvisited chunks: `{summary.get('pending_or_unvisited_chunks', 0)}`",
        "",
        "| location_id | zone_id | period_start | period_end | status | attempts | rows | last_error | last_attempt_at | next_retry_after |",
        "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for row in checkpoint_rows:
        lines.append(
            f"| {row.get('location_id')} | {row.get('zone_id')} | {row.get('period_start')} | {row.get('period_end')} | {row.get('status')} | {row.get('attempt_count')} | {row.get('row_count_loaded')} | {str(row.get('last_error', '')).replace('|', '/')} | {row.get('last_attempt_at')} | {row.get('next_retry_after_if_known')} |"
        )
    lines.append("")
    return "\n".join(lines)


def fetch_progress_md(checkpoint_rows: list[dict[str, object]], summary: dict[str, object]) -> str:
    by_status: dict[str, int] = defaultdict(int)
    by_area_done: dict[str, int] = defaultdict(int)
    for row in checkpoint_rows:
        by_status[str(row.get("status"))] += 1
        if row.get("status") == "done":
            by_area_done[str(row.get("area_code"))] += 1
    return json_report(
        "P0056D Open-Meteo Fetch Progress",
        {
            "summary": compact_fetch_summary(summary),
            "checkpoint_status_counts": dict(sorted(by_status.items())),
            "done_chunks_by_area": dict(sorted(by_area_done.items())),
        },
    )


def compact_fetch_summary(fetch_summary: object) -> object:
    if not isinstance(fetch_summary, dict):
        return fetch_summary
    return {key: value for key, value in fetch_summary.items() if key != "checkpoint_rows"}


def fetch_resume_instructions_md(summary: dict[str, object]) -> str:
    return "\n".join(
        [
            "# P0056D Open-Meteo Resume Instructions",
            "",
            "Resume command:",
            "",
            "```bash",
            str(summary.get("resume_command", "python3 -B -m src.mac.services.spotprice_model_diagnostics.p0056d")),
            "```",
            "",
            "The runner skips chunks whose expected row count is already present in `area_weather_zone_openmeteo_hourly_p0056d_v1` and fetches only missing location-period chunks.",
            "",
            f"Current blocking location: `{summary.get('blocking_location_id', '')}`",
            f"Current blocking period: `{summary.get('blocking_period_start', '')}..{summary.get('blocking_period_end', '')}`",
            f"Last error: `{summary.get('last_error', '')}`",
            "",
        ]
    )


def fetch_incomplete_changelog_md(summary: dict[str, object]) -> str:
    fetch_summary = summary["fetch_summary"]  # type: ignore[index]
    return "\n".join(
        [
            "# P0056D Changelog",
            "",
            "- Status: `WARN`",
            "- P0056D Open-Meteo fetch is incomplete but resumable.",
            f"- Done chunks: `{fetch_summary.get('done_chunks', 0)}`",
            f"- Pending/unvisited chunks: `{fetch_summary.get('pending_or_unvisited_chunks', 0)}`",
            f"- Blocking location: `{fetch_summary.get('blocking_location_id', '')}`",
            f"- Blocking period: `{fetch_summary.get('blocking_period_start', '')}..{fetch_summary.get('blocking_period_end', '')}`",
            "- No proxy build, model retest, devices, runtime changes or production activation were performed.",
            "",
        ]
    )


def fetch_incomplete_coverage_md(summary: dict[str, object]) -> str:
    row_counts = summary.get("row_counts", {})
    return json_report(
        "P0056D Coverage And Missingness",
        {
            "status": "WARN",
            "reason": summary.get("reason"),
            "row_counts": row_counts,
            "fetch_summary": summary.get("fetch_summary"),
            "forecast_retest_run": False,
        },
    )


def fetch_incomplete_decision_md(summary: dict[str, object]) -> str:
    return "\n".join(
        [
            "# P0056D Decision",
            "",
            "`WARN`",
            "",
            "Open-Meteo fetch is incomplete and checkpointed for resume. No candidate-default decision can be made until all SE1/SE2/FI weather chunks are complete and the forecast retest has run.",
            "",
            "Keep P0056B as default.",
            "",
        ]
    )


def fetch_incomplete_next_package_md(summary: dict[str, object]) -> str:
    return "\n".join(
        [
            "# P0056D Next Package Recommendation",
            "",
            "Continue P0056D with the same resume command after Open-Meteo rate-limit cooldown. The runner will fetch only missing location-period chunks.",
            "",
        ]
    )


def changelog_md(summary: dict[str, object]) -> str:
    row_counts = summary["row_counts"]  # type: ignore[index]
    return "\n".join(
        [
            "# P0056D Changelog",
            "",
            f"- Status: `{summary['status']}`",
            f"- Runtime seconds: `{summary['runtime_seconds']}`",
            f"- Location weather rows: `{row_counts['location_weather_rows']}`",
            f"- Feature rows: `{row_counts['feature_rows']}`",
            f"- Forecast log rows: `{row_counts['forecast_log_rows']}`",
            "- Scope: SE1, SE2 and FI only.",
            "- No devices, runtime changes, production activation, spot price, flow/exchange/A61/capacity or future actual load leakage.",
            "",
        ]
    )


def labb_label_md() -> str:
    return "# P0056D LABB Label\n\nP0056D is LABB-only weather-proxy and consumption-forecast retest evidence. It is not G2-KANDIDAT and does not activate a production proxy.\n"


def p0056c_baseline_review_md() -> str:
    baseline = load_p0056c_baseline()
    lines = ["# P0056C Baseline Review", "", "| area | DayAhead MAE MW | MAE percent mean | full36 MAE MW |", "| --- | ---: | ---: | ---: |"]
    for area in SCOPED_AREAS:
        row = baseline[area]
        lines.append(f"| {area} | {float(row['DayAhead_hourly_MAE']):.3f} | {float(row['MAE_percent_of_mean_actual']):.3f} | {float(row['full_36h_MAE']):.3f} |")
    lines.append("")
    return "\n".join(lines)


def weather_zone_design_md(summary: dict[str, object]) -> str:
    lines = ["# P0056D Weather Zone Design", "", "| area | zone | weight | confidence | description |", "| --- | --- | ---: | --- | --- |"]
    for zone in summary["weather_zones"]:  # type: ignore[union-attr]
        lines.append(f"| {zone['area_code']} | {zone['zone_id']} | {float(zone['weight']):.3f} | {zone['confidence']} | {zone['description']} |")
    lines.append("")
    return "\n".join(lines)


def zone_weighting_method_md(summary: dict[str, object]) -> str:
    lines = [
        "# P0056D Zone Weighting Method",
        "",
        "Weights are deterministic manual first-pass load-centre approximations because no local population/load-distribution metadata was found in bootstrap. Weights sum to 1.0 per area and are retained as LABB assumptions.",
        "",
        "| area | zone | weight | confidence | rationale |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in summary["zone_weights"]:  # type: ignore[union-attr]
        lines.append(f"| {row['area_code']} | {row['zone_id']} | {float(row['zone_weight']):.3f} | {row['confidence']} | {row['rationale']} |")
    lines.append("")
    return "\n".join(lines)


def output_table_schema_md() -> str:
    return "\n".join(
        [
            "# P0056D Output Table Schema",
            "",
            f"- `{ZONE_TABLE}`: representative location-hour Open-Meteo observations with zone membership.",
            f"- `{WEIGHT_TABLE}`: area-zone weights and confidence/rationale.",
            f"- `{PROXY_TABLE}`: weighted area weather proxy rows.",
            f"- `{FEATURE_TABLE}`: P0056C-compatible weighted area weather feature rows.",
            f"- `{FORECAST_TABLE}`: SE1/SE2/FI holdout selected forecast-origin predictions.",
            f"- `{METRICS_TABLE}`: SE1/SE2/FI retest metrics.",
            "",
            "All tables are keyed by `generated_by_package='P0056D'` and do not overwrite P0056B or P0056C rows.",
            "",
        ]
    )


def weather_feature_contract_md(summary: dict[str, object]) -> str:
    return json_report(
        "P0056D Weather Feature Contract",
        {
            "feature_table": FEATURE_TABLE,
            "weather_proxy_version": PACKAGE_ID,
            "input_classification": "historical_observed_only_weather_actual_proxy",
            "production_weather_forecast": False,
            "model_feature_names": [feature for feature in p0056c.p0056c_feature_names() if feature.startswith("weather_proxy_")],
            "snow_depth": "unavailable; stored null in table and zero-filled only for P0056C-compatible model matrix",
            "units": {
                "temperature_2m": "degC",
                "apparent_temperature": "degC",
                "wind_speed": "km/h from Open-Meteo wind_speed_10m",
                "cloud_cover": "percent",
                "relative_humidity": "percent",
                "precipitation": "mm",
                "snowfall": "cm per Open-Meteo hourly variable",
            },
        },
    )


def weather_proxy_validation_md(summary: dict[str, object]) -> str:
    return json_report(
        "P0056D Weather Proxy Validation",
        {
            "weights_summary": summary["weights_summary"],
            "proxy_summary": summary["proxy_summary"],
            "required_area_scope": SCOPED_AREAS,
            "rows_loaded_for_all_scoped_areas": all(summary["proxy_summary"]["areas"].get(area, {}).get("rows", 0) > 0 for area in SCOPED_AREAS),  # type: ignore[index]
        },
    )


def forecast_retest_method_md(summary: dict[str, object]) -> str:
    retest = summary["forecast_retest"]  # type: ignore[index]
    return json_report(
        "P0056D Forecast Retest Method",
        {
            "areas": SCOPED_AREAS,
            "model_method_contract": retest["model_method_contract"],
            "split_policy": retest["split_policy"],
            "target_contract": retest["target_contract"],
            "weather_contract": retest["weather_contract"],
            "completed_jobs": retest["completed_jobs"],
            "total_jobs": retest["total_jobs"],
            "failed_areas": retest["failed_areas"],
        },
    )


def area_results_md(rows: list[dict[str, object]]) -> str:
    lines = ["# P0056D Area Results", "", "| area | status | DayAhead MAE | MAE % mean | full36 MAE | daily energy % |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    for row in rows:
        lines.append(f"| {row['area_code']} | {row['status']} | {float(row['DayAhead_hourly_MAE']):.3f} | {float(row['MAE_percent_of_mean_actual']):.3f} | {float(row['full_36h_MAE']):.3f} | {float(row['daily_energy_error_percent_of_actual']):.3f} |")
    lines.append("")
    return "\n".join(lines)


def comparison_md(rows: list[dict[str, object]]) -> str:
    lines = ["# P0056D Comparison Vs P0056C", "", "| area | delta DayAhead MW | delta DayAhead % | delta full36 MW | delta full36 % | decision |", "| --- | ---: | ---: | ---: | ---: | --- |"]
    for row in rows:
        lines.append(f"| {row['area_code']} | {float(row['delta_vs_P0056C_DayAhead_MW']):.3f} | {float(row['delta_vs_P0056C_DayAhead_percent']):.3f} | {float(row['delta_vs_P0056C_full36_MW']):.3f} | {float(row['delta_vs_P0056C_full36_percent']):.3f} | {row['decision']} |")
    lines.append("")
    return "\n".join(lines)


def decision_md(summary: dict[str, object]) -> str:
    comparison = summary["comparison"]  # type: ignore[index]
    return json_report(
        "P0056D Decision",
        {
            "status": summary["status"],
            "candidate_default_areas": comparison["candidate_default_areas"],
            "keep_p0056b_default_areas": comparison["keep_p0056b_default_areas"],
            "rule": "candidate if DayAhead improves >=2%, or full36 improves >=2% without DayAhead worsening, or daily energy improves >=5% without DayAhead worsening >1%",
            "production_activation": False,
        },
    )


def what_we_learned_md(summary: dict[str, object]) -> str:
    return "\n".join(
        [
            "# P0056D What We Learned",
            "",
            "- SE1, SE2 and FI can be retested with explicit zone-weighted Open-Meteo proxies without changing P0056B defaults.",
            "- Manual zone weights are useful for first-pass LABB exploration but should be replaced by population/load metadata before candidate evaluation.",
            "- `snow_depth` is not requested by the existing weather-history Open-Meteo helper; P0056D labels it unavailable rather than expanding older package contracts.",
            "- Historical actual-weather proxy results remain diagnostic only and require a separate forecast-safe weather model before production use.",
            "",
        ]
    )


def next_package_recommendation_md() -> str:
    return "\n".join(
        [
            "# P0056D Next Package Recommendation",
            "",
            "Recommended next package: replace manual SE1/SE2/FI zone weights with durable population or load-share metadata, then rerun only areas where P0056D indicates candidate-default potential.",
            "",
        ]
    )


def coverage_csv_rows(summary: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    areas = summary["proxy_summary"]["areas"]  # type: ignore[index]
    for area, meta in areas.items():  # type: ignore[union-attr]
        rows.append({"area_code": area, **meta})
    return rows


def compact_summary(summary: dict[str, object]) -> dict[str, object]:
    return {
        "status": summary["status"],
        "runtime_seconds": summary["runtime_seconds"],
        "row_counts": summary["row_counts"],
        "comparison": summary["comparison"],
        "leakage_ok": summary["leakage_review"]["ok"],  # type: ignore[index]
    }


def json_report(title: str, data: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(json_safe(data), indent=2, sort_keys=True)}\n```\n"


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return str(value)


def write_csv(path: Path, rows: object) -> str:
    typed_rows = list(rows) if isinstance(rows, list) else []
    keys: list[str] = []
    for row in typed_rows:
        if isinstance(row, dict):
            for key in row:
                if key not in keys:
                    keys.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        for row in typed_rows:
            writer.writerow({key: json_safe(row.get(key)) if isinstance(row, dict) else "" for key in keys})
    return str(path)


def main() -> int:
    result = run_p0056d_retest()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
