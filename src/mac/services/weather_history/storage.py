"""SQLite storage and validation for P0031 weather history."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import sqlite3
from typing import Sequence
from zoneinfo import ZoneInfo

from .models import WEATHER_VARIABLES, WeatherLocation, WeatherObservation, ValidationReport


SCHEMA_VERSION = "2"
AREA_PROXY = "SE3"
SOURCE = "open-meteo archive"
SOURCE_MODEL = "era5_seamless"
STOCKHOLM = ZoneInfo("Europe/Stockholm")
DEFAULT_DB_PATH = Path.home() / ".smart-home" / "data" / "weather_history.sqlite3"

DEFAULT_LOCATIONS = (
    WeatherLocation("stockholm", "Stockholm / Malardalen", 59.3293, 18.0686, 0.35, AREA_PROXY, SOURCE),
    WeatherLocation("goteborg", "Goteborg / western SE3", 57.7089, 11.9746, 0.25, AREA_PROXY, SOURCE),
    WeatherLocation("orebro", "Orebro / inland SE3", 59.2753, 15.2134, 0.20, AREA_PROXY, SOURCE),
    WeatherLocation("linkoping", "Linkoping / southern SE3", 58.4108, 15.6214, 0.20, AREA_PROXY, SOURCE),
)

P0032_PROXY_LOCATIONS = (
    WeatherLocation("se1_core_kiruna", "Kiruna", 67.8558, 20.2253, 0.11, "se1_core_weather", SOURCE),
    WeatherLocation("se1_core_gallivare", "Gallivare", 67.1339, 20.6528, 0.10, "se1_core_weather", SOURCE),
    WeatherLocation("se1_core_lulea", "Lulea", 65.5848, 22.1547, 0.10, "se1_core_weather", SOURCE),
    WeatherLocation("se1_core_skelleftea", "Skelleftea", 64.7507, 20.9528, 0.09, "se1_core_weather", SOURCE),
    WeatherLocation("se1_core_umea", "Umea", 63.8258, 20.2630, 0.09, "se1_core_weather", SOURCE),
    WeatherLocation("se1_core_ostersund", "Ostersund", 63.1792, 14.6357, 0.08, "se1_core_weather", SOURCE),
    WeatherLocation("se1_core_sundsvall", "Sundsvall", 62.3908, 17.3069, 0.08, "se1_core_weather", SOURCE),
    WeatherLocation("se1_core_rovaniemi", "Rovaniemi", 66.5039, 25.7294, 0.08, "se1_core_weather", SOURCE),
    WeatherLocation("se1_core_oulu", "Oulu", 65.0121, 25.4651, 0.08, "se1_core_weather", SOURCE),
    WeatherLocation("se1_core_tromso", "Tromso", 69.6492, 18.9553, 0.07, "se1_core_weather", SOURCE),
    WeatherLocation("se1_core_narvik", "Narvik", 68.4385, 17.4273, 0.06, "se1_core_weather", SOURCE),
    WeatherLocation("se1_core_bodo", "Bodo", 67.2804, 14.4049, 0.06, "se1_core_weather", SOURCE),
    WeatherLocation("nordic_connected_trondheim", "Trondheim", 63.4305, 10.3951, 0.18, "nordic_connected_weather", SOURCE),
    WeatherLocation("nordic_connected_oslo", "Oslo", 59.9139, 10.7522, 0.18, "nordic_connected_weather", SOURCE),
    WeatherLocation("nordic_connected_bergen", "Bergen", 60.3913, 5.3221, 0.14, "nordic_connected_weather", SOURCE),
    WeatherLocation("nordic_connected_helsinki", "Helsinki", 60.1699, 24.9384, 0.18, "nordic_connected_weather", SOURCE),
    WeatherLocation("nordic_connected_tampere", "Tampere", 61.4978, 23.7610, 0.16, "nordic_connected_weather", SOURCE),
    WeatherLocation("nordic_connected_turku", "Turku", 60.4518, 22.2666, 0.16, "nordic_connected_weather", SOURCE),
    WeatherLocation("south_connected_stockholm", "Stockholm", 59.3293, 18.0686, 0.06, "south_connected_weather", SOURCE),
    WeatherLocation("south_connected_goteborg", "Goteborg", 57.7089, 11.9746, 0.05, "south_connected_weather", SOURCE),
    WeatherLocation("south_connected_malmo", "Malmo", 55.6050, 13.0038, 0.05, "south_connected_weather", SOURCE),
    WeatherLocation("south_connected_copenhagen", "Copenhagen", 55.6761, 12.5683, 0.04, "south_connected_weather", SOURCE),
    WeatherLocation("se3_load_stockholm", "Stockholm", 59.3293, 18.0686, 0.16, "se3_load_weather", SOURCE),
    WeatherLocation("se3_load_orebro", "Orebro", 59.2753, 15.2134, 0.10, "se3_load_weather", SOURCE),
    WeatherLocation("se3_load_vasteras", "Vasteras", 59.6099, 16.5448, 0.10, "se3_load_weather", SOURCE),
    WeatherLocation("se3_load_linkoping", "Linkoping", 58.4108, 15.6214, 0.09, "se3_load_weather", SOURCE),
    WeatherLocation("se3_load_norrkoping", "Norrkoping", 58.5877, 16.1924, 0.08, "se3_load_weather", SOURCE),
    WeatherLocation("se3_load_goteborg", "Goteborg", 57.7089, 11.9746, 0.10, "se3_load_weather", SOURCE),
    WeatherLocation("se3_load_jonkoping", "Jonkoping", 57.7826, 14.1618, 0.08, "se3_load_weather", SOURCE),
    WeatherLocation("se3_load_karlstad", "Karlstad", 59.4022, 13.5115, 0.07, "se3_load_weather", SOURCE),
    WeatherLocation("se3_load_borlange", "Borlange", 60.4858, 15.4371, 0.06, "se3_load_weather", SOURCE),
    WeatherLocation("se3_load_gavle", "Gavle", 60.6749, 17.1413, 0.06, "se3_load_weather", SOURCE),
    WeatherLocation("se3_load_kalmar", "Kalmar", 56.6634, 16.3568, 0.05, "se3_load_weather", SOURCE),
    WeatherLocation("se3_load_vaxjo", "Vaxjo", 56.8790, 14.8059, 0.05, "se3_load_weather", SOURCE),
)


def default_db_path() -> Path:
    return DEFAULT_DB_PATH


def connect_db(path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(Path(path).expanduser())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_schema(path: Path | str) -> None:
    db_path = Path(path).expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect_db(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_meta (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS weather_locations (
              location_id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              latitude REAL NOT NULL,
              longitude REAL NOT NULL,
              weight REAL NOT NULL,
              area_proxy TEXT NOT NULL,
              source TEXT NOT NULL,
              active INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS weather_ingest_runs (
              run_id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_type TEXT NOT NULL,
              started_at TEXT NOT NULL,
              completed_at TEXT,
              source TEXT NOT NULL,
              source_model TEXT NOT NULL,
              start_date TEXT NOT NULL,
              end_date TEXT NOT NULL,
              status TEXT NOT NULL,
              locations_requested INTEGER NOT NULL,
              records_inserted INTEGER NOT NULL DEFAULT 0,
              records_updated INTEGER NOT NULL DEFAULT 0,
              gaps_detected INTEGER NOT NULL DEFAULT 0,
              error_summary TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS weather_observations (
              location_id TEXT NOT NULL,
              utc_hour_start TEXT NOT NULL,
              local_hour_start TEXT NOT NULL,
              local_date TEXT NOT NULL,
              local_hour INTEGER NOT NULL,
              timezone TEXT NOT NULL,
              utc_offset TEXT NOT NULL,
              fold INTEGER NOT NULL,
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
              source_model TEXT NOT NULL,
              source TEXT NOT NULL,
              fetched_at TEXT NOT NULL,
              ingest_run_id INTEGER,
              PRIMARY KEY (location_id, utc_hour_start)
            );
            CREATE INDEX IF NOT EXISTS idx_weather_observations_local_date
              ON weather_observations(local_date);
            CREATE TABLE IF NOT EXISTS weather_area_hourly (
              area_proxy TEXT NOT NULL,
              utc_hour_start TEXT NOT NULL,
              local_hour_start TEXT NOT NULL,
              local_date TEXT NOT NULL,
              local_hour INTEGER NOT NULL,
              timezone TEXT NOT NULL,
              utc_offset TEXT NOT NULL,
              fold INTEGER NOT NULL,
              weighted_temperature_2m REAL,
              weighted_apparent_temperature REAL,
              weighted_wind_speed_10m REAL,
              weighted_wind_speed_100m REAL,
              weighted_wind_gusts_10m REAL,
              weighted_cloud_cover REAL,
              weighted_shortwave_radiation REAL,
              weighted_precipitation REAL,
              weighted_snowfall REAL,
              weighted_relative_humidity_2m REAL,
              weighted_pressure_msl REAL,
              heating_degree_hours REAL NOT NULL,
              cooling_degree_hours REAL NOT NULL,
              source_coverage_count INTEGER NOT NULL,
              source_coverage_weight REAL NOT NULL,
              source_model TEXT NOT NULL,
              source TEXT NOT NULL,
              fetched_at TEXT NOT NULL,
              ingest_run_id INTEGER,
              PRIMARY KEY (area_proxy, utc_hour_start)
            );
            CREATE INDEX IF NOT EXISTS idx_weather_area_hourly_local_date
              ON weather_area_hourly(local_date);
            CREATE TABLE IF NOT EXISTS weather_proxy_gradients_hourly (
              area_proxy TEXT NOT NULL,
              utc_hour_start TEXT NOT NULL,
              local_hour_start TEXT NOT NULL,
              local_date TEXT NOT NULL,
              local_hour INTEGER NOT NULL,
              temp_gradient_se3_load_minus_se1_core REAL,
              apparent_temp_gradient_se3_load_minus_se1_core REAL,
              heating_degree_gradient_se3_load_minus_se1_core REAL,
              wind_100m_gradient_nordic_connected_minus_se3_load REAL,
              south_temp_gradient_minus_se1_core REAL,
              source_coverage_status TEXT NOT NULL,
              computed_at TEXT NOT NULL,
              ingest_run_id INTEGER,
              PRIMARY KEY (area_proxy, utc_hour_start)
            );
            CREATE VIEW IF NOT EXISTS weather_proxy_se1_core_hourly AS
              SELECT * FROM weather_area_hourly WHERE area_proxy='se1_core_weather';
            CREATE VIEW IF NOT EXISTS weather_proxy_nordic_connected_hourly AS
              SELECT * FROM weather_area_hourly WHERE area_proxy='nordic_connected_weather';
            CREATE VIEW IF NOT EXISTS weather_proxy_south_connected_hourly AS
              SELECT * FROM weather_area_hourly WHERE area_proxy='south_connected_weather';
            CREATE VIEW IF NOT EXISTS weather_proxy_se3_load_hourly AS
              SELECT * FROM weather_area_hourly WHERE area_proxy='se3_load_weather';
            """
        )
        conn.execute("INSERT OR REPLACE INTO schema_meta(key, value) VALUES('schema_version', ?)", (SCHEMA_VERSION,))
        for location in DEFAULT_LOCATIONS + P0032_PROXY_LOCATIONS:
            conn.execute(
                """
                INSERT OR REPLACE INTO weather_locations
                (location_id, name, latitude, longitude, weight, area_proxy, source, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    location.location_id,
                    location.name,
                    location.latitude,
                    location.longitude,
                    location.weight,
                    location.area_proxy,
                    location.source,
                    1 if location.active else 0,
                ),
            )


def all_area_proxies(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT DISTINCT area_proxy FROM weather_locations WHERE active=1 ORDER BY area_proxy"
    ).fetchall()
    return [str(row["area_proxy"]) for row in rows]


def configured_locations(conn: sqlite3.Connection, area_proxy: str = AREA_PROXY) -> list[WeatherLocation]:
    rows = conn.execute(
        """
        SELECT location_id, name, latitude, longitude, weight, area_proxy, source, active
        FROM weather_locations
        WHERE active=1 AND area_proxy=?
        ORDER BY location_id
        """,
        (area_proxy,),
    ).fetchall()
    return [
        WeatherLocation(
            row["location_id"],
            row["name"],
            float(row["latitude"]),
            float(row["longitude"]),
            float(row["weight"]),
            row["area_proxy"],
            row["source"],
            bool(row["active"]),
        )
        for row in rows
    ]


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


def expected_utc_hours_for_range(start_date: date, end_date: date) -> tuple[datetime, ...]:
    hours: list[datetime] = []
    current = start_date
    while current <= end_date:
        hours.extend(expected_utc_hours_for_local_date(current))
        current += timedelta(days=1)
    return tuple(hours)


def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:00Z")


def local_parts(utc_dt: datetime) -> tuple[str, str, int, str, int]:
    local = utc_dt.astimezone(STOCKHOLM)
    offset = local.strftime("%z")
    return (
        local.isoformat(),
        local.date().isoformat(),
        local.hour,
        f"{offset[:3]}:{offset[3:]}",
        int(getattr(local, "fold", 0)),
    )


def create_ingest_run(
    conn: sqlite3.Connection,
    *,
    run_type: str,
    start_date: date,
    end_date: date,
    locations_requested: int,
    status: str = "running",
) -> int:
    now = _now()
    cursor = conn.execute(
        """
        INSERT INTO weather_ingest_runs
        (run_type, started_at, source, source_model, start_date, end_date, status, locations_requested)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (run_type, now, SOURCE, SOURCE_MODEL, start_date.isoformat(), end_date.isoformat(), status, locations_requested),
    )
    return int(cursor.lastrowid)


def finish_ingest_run(
    conn: sqlite3.Connection,
    run_id: int,
    *,
    status: str,
    records_inserted: int,
    records_updated: int,
    gaps_detected: int,
    error_summary: str = "",
) -> None:
    conn.execute(
        """
        UPDATE weather_ingest_runs
        SET completed_at=?, status=?, records_inserted=?, records_updated=?, gaps_detected=?, error_summary=?
        WHERE run_id=?
        """,
        (_now(), status, records_inserted, records_updated, gaps_detected, error_summary, run_id),
    )


def upsert_weather_observations(
    conn: sqlite3.Connection,
    observations: Sequence[WeatherObservation],
    ingest_run_id: int,
) -> int:
    now = _now()
    conn.executemany(
        f"""
        INSERT INTO weather_observations (
          location_id, utc_hour_start, local_hour_start, local_date, local_hour,
          timezone, utc_offset, fold, {", ".join(WEATHER_VARIABLES)},
          source_model, source, fetched_at, ingest_run_id
        ) VALUES ({", ".join("?" for _ in range(8 + len(WEATHER_VARIABLES) + 4))})
        ON CONFLICT(location_id, utc_hour_start) DO UPDATE SET
          local_hour_start=excluded.local_hour_start,
          local_date=excluded.local_date,
          local_hour=excluded.local_hour,
          timezone=excluded.timezone,
          utc_offset=excluded.utc_offset,
          fold=excluded.fold,
          {", ".join(f"{name}=excluded.{name}" for name in WEATHER_VARIABLES)},
          source_model=excluded.source_model,
          source=excluded.source,
          fetched_at=excluded.fetched_at,
          ingest_run_id=excluded.ingest_run_id
        """,
        [
            (
                obs.location_id,
                obs.utc_hour_start,
                obs.local_hour_start,
                obs.local_date,
                obs.local_hour,
                obs.timezone,
                obs.utc_offset,
                obs.fold,
                *(obs.values[name] for name in WEATHER_VARIABLES),
                obs.source_model,
                obs.source,
                now,
                ingest_run_id,
            )
            for obs in observations
        ],
    )
    return len(observations)


def compute_area_proxy_hourly(
    conn: sqlite3.Connection,
    *,
    area_proxy: str,
    start_date: date,
    end_date: date,
    ingest_run_id: int,
) -> int:
    locations = configured_locations(conn, area_proxy)
    weights = {location.location_id: location.weight for location in locations}
    expected = [iso_z(hour) for hour in expected_utc_hours_for_range(start_date, end_date)]
    rows = conn.execute(
        f"""
        SELECT *
        FROM weather_observations
        WHERE local_date BETWEEN ? AND ? AND location_id IN ({", ".join("?" for _ in locations)})
        """,
        (start_date.isoformat(), end_date.isoformat(), *(location.location_id for location in locations)),
    ).fetchall()
    by_hour: dict[str, list[sqlite3.Row]] = {}
    for row in rows:
        by_hour.setdefault(row["utc_hour_start"], []).append(row)

    now = _now()
    payload = []
    for utc_hour in expected:
        hour_rows = by_hour.get(utc_hour, [])
        if not hour_rows:
            continue
        first = hour_rows[0]
        values: dict[str, float | None] = {}
        coverage_weight = 0.0
        for variable in WEATHER_VARIABLES:
            total = 0.0
            variable_weight = 0.0
            for row in hour_rows:
                value = row[variable]
                if value is None:
                    continue
                weight = weights[row["location_id"]]
                total += float(value) * weight
                variable_weight += weight
            values[variable] = total / variable_weight if variable_weight > 0 else None
            coverage_weight = max(coverage_weight, variable_weight)
        temp = values["temperature_2m"]
        heating = max(0.0, 17.0 - float(temp)) if temp is not None else 0.0
        cooling = max(0.0, float(temp) - 22.0) if temp is not None else 0.0
        payload.append(
            (
                area_proxy,
                utc_hour,
                first["local_hour_start"],
                first["local_date"],
                first["local_hour"],
                first["timezone"],
                first["utc_offset"],
                first["fold"],
                *(values[name] for name in WEATHER_VARIABLES),
                heating,
                cooling,
                len(hour_rows),
                coverage_weight,
                SOURCE_MODEL,
                SOURCE,
                now,
                ingest_run_id,
            )
        )
    conn.executemany(
        f"""
        INSERT INTO weather_area_hourly (
          area_proxy, utc_hour_start, local_hour_start, local_date, local_hour,
          timezone, utc_offset, fold,
          {", ".join("weighted_" + name for name in WEATHER_VARIABLES)},
          heating_degree_hours, cooling_degree_hours, source_coverage_count,
          source_coverage_weight, source_model, source, fetched_at, ingest_run_id
        ) VALUES ({", ".join("?" for _ in range(8 + len(WEATHER_VARIABLES) + 8))})
        ON CONFLICT(area_proxy, utc_hour_start) DO UPDATE SET
          local_hour_start=excluded.local_hour_start,
          local_date=excluded.local_date,
          local_hour=excluded.local_hour,
          timezone=excluded.timezone,
          utc_offset=excluded.utc_offset,
          fold=excluded.fold,
          {", ".join(f"weighted_{name}=excluded.weighted_{name}" for name in WEATHER_VARIABLES)},
          heating_degree_hours=excluded.heating_degree_hours,
          cooling_degree_hours=excluded.cooling_degree_hours,
          source_coverage_count=excluded.source_coverage_count,
          source_coverage_weight=excluded.source_coverage_weight,
          source_model=excluded.source_model,
          source=excluded.source,
          fetched_at=excluded.fetched_at,
          ingest_run_id=excluded.ingest_run_id
        """,
        payload,
    )
    return len(payload)


def compute_all_area_proxy_hourly(
    conn: sqlite3.Connection,
    *,
    start_date: date,
    end_date: date,
    ingest_run_id: int,
) -> int:
    total = 0
    for area_proxy in all_area_proxies(conn):
        total += compute_area_proxy_hourly(
            conn,
            area_proxy=area_proxy,
            start_date=start_date,
            end_date=end_date,
            ingest_run_id=ingest_run_id,
        )
    total += compute_weather_gradients(conn, start_date=start_date, end_date=end_date, ingest_run_id=ingest_run_id)
    return total


def compute_weather_gradients(
    conn: sqlite3.Connection,
    *,
    start_date: date,
    end_date: date,
    ingest_run_id: int,
) -> int:
    now = _now()
    rows = conn.execute(
        """
        SELECT
          se3.utc_hour_start,
          se3.local_hour_start,
          se3.local_date,
          se3.local_hour,
          se3.weighted_temperature_2m AS se3_temp,
          se3.weighted_apparent_temperature AS se3_apparent,
          se3.heating_degree_hours AS se3_heating,
          se3.weighted_wind_speed_100m AS se3_wind_100m,
          se1.weighted_temperature_2m AS se1_temp,
          se1.weighted_apparent_temperature AS se1_apparent,
          se1.heating_degree_hours AS se1_heating,
          nordic.weighted_wind_speed_100m AS nordic_wind_100m,
          south.weighted_temperature_2m AS south_temp
        FROM weather_area_hourly se3
        JOIN weather_area_hourly se1
          ON se1.utc_hour_start=se3.utc_hour_start AND se1.area_proxy='se1_core_weather'
        JOIN weather_area_hourly nordic
          ON nordic.utc_hour_start=se3.utc_hour_start AND nordic.area_proxy='nordic_connected_weather'
        JOIN weather_area_hourly south
          ON south.utc_hour_start=se3.utc_hour_start AND south.area_proxy='south_connected_weather'
        WHERE se3.area_proxy='se3_load_weather'
          AND se3.local_date BETWEEN ? AND ?
        ORDER BY se3.utc_hour_start
        """,
        (start_date.isoformat(), end_date.isoformat()),
    ).fetchall()
    payload = []
    for row in rows:
        payload.append(
            (
                "se3_area_diff_weather",
                row["utc_hour_start"],
                row["local_hour_start"],
                row["local_date"],
                row["local_hour"],
                _diff(row["se3_temp"], row["se1_temp"]),
                _diff(row["se3_apparent"], row["se1_apparent"]),
                _diff(row["se3_heating"], row["se1_heating"]),
                _diff(row["nordic_wind_100m"], row["se3_wind_100m"]),
                _diff(row["south_temp"], row["se1_temp"]),
                "se1_core+nordic_connected+south_connected+se3_load_aligned",
                now,
                ingest_run_id,
            )
        )
    conn.executemany(
        """
        INSERT INTO weather_proxy_gradients_hourly (
          area_proxy, utc_hour_start, local_hour_start, local_date, local_hour,
          temp_gradient_se3_load_minus_se1_core,
          apparent_temp_gradient_se3_load_minus_se1_core,
          heating_degree_gradient_se3_load_minus_se1_core,
          wind_100m_gradient_nordic_connected_minus_se3_load,
          south_temp_gradient_minus_se1_core,
          source_coverage_status,
          computed_at,
          ingest_run_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(area_proxy, utc_hour_start) DO UPDATE SET
          local_hour_start=excluded.local_hour_start,
          local_date=excluded.local_date,
          local_hour=excluded.local_hour,
          temp_gradient_se3_load_minus_se1_core=excluded.temp_gradient_se3_load_minus_se1_core,
          apparent_temp_gradient_se3_load_minus_se1_core=excluded.apparent_temp_gradient_se3_load_minus_se1_core,
          heating_degree_gradient_se3_load_minus_se1_core=excluded.heating_degree_gradient_se3_load_minus_se1_core,
          wind_100m_gradient_nordic_connected_minus_se3_load=excluded.wind_100m_gradient_nordic_connected_minus_se3_load,
          south_temp_gradient_minus_se1_core=excluded.south_temp_gradient_minus_se1_core,
          source_coverage_status=excluded.source_coverage_status,
          computed_at=excluded.computed_at,
          ingest_run_id=excluded.ingest_run_id
        """,
        payload,
    )
    return len(payload)


def validate_proxy_groups(
    conn: sqlite3.Connection,
    start_date: date,
    end_date: date,
    db_path: str = "",
) -> dict[str, object]:
    reports = {
        area_proxy: validate_weather_continuity(conn, start_date, end_date, area_proxy=area_proxy, db_path=db_path)
        for area_proxy in ("se1_core_weather", "nordic_connected_weather", "south_connected_weather", "se3_load_weather")
    }
    expected = len(expected_utc_hours_for_range(start_date, end_date))
    gradient_rows = conn.execute(
        """
        SELECT *
        FROM weather_proxy_gradients_hourly
        WHERE area_proxy='se3_area_diff_weather' AND local_date BETWEEN ? AND ?
        """,
        (start_date.isoformat(), end_date.isoformat()),
    ).fetchall()
    gradient_null_count = 0
    for row in gradient_rows:
        for key in (
            "temp_gradient_se3_load_minus_se1_core",
            "apparent_temp_gradient_se3_load_minus_se1_core",
            "heating_degree_gradient_se3_load_minus_se1_core",
            "wind_100m_gradient_nordic_connected_minus_se3_load",
            "south_temp_gradient_minus_se1_core",
        ):
            if row[key] is None:
                gradient_null_count += 1
    return {
        "db_path": db_path,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "complete": all(report.complete for report in reports.values()) and len(gradient_rows) == expected and gradient_null_count == 0,
        "proxy_groups": reports,
        "gradient_row_count": len(gradient_rows),
        "gradient_expected_count": expected,
        "gradient_null_count": gradient_null_count,
    }


def _diff(left: object, right: object) -> float | None:
    if left is None or right is None:
        return None
    return float(left) - float(right)


def latest_complete_local_date(conn: sqlite3.Connection, area_proxy: str = AREA_PROXY) -> date | None:
    rows = conn.execute(
        "SELECT DISTINCT local_date FROM weather_area_hourly WHERE area_proxy=? ORDER BY local_date DESC",
        (area_proxy,),
    ).fetchall()
    for row in rows:
        candidate = date.fromisoformat(row["local_date"])
        report = validate_weather_continuity(conn, candidate, candidate, area_proxy=area_proxy, db_path="")
        if report.complete:
            return candidate
    return None


def validate_weather_continuity(
    conn: sqlite3.Connection,
    start_date: date,
    end_date: date,
    *,
    area_proxy: str = AREA_PROXY,
    db_path: str = "",
) -> ValidationReport:
    locations = configured_locations(conn, area_proxy)
    expected_hours = [iso_z(hour) for hour in expected_utc_hours_for_range(start_date, end_date)]
    expected_set = set(expected_hours)
    expected_location_count = len(expected_hours) * len(locations)
    location_ids = [location.location_id for location in locations]
    location_rows = conn.execute(
        f"""
        SELECT *
        FROM weather_observations
        WHERE local_date BETWEEN ? AND ? AND location_id IN ({", ".join("?" for _ in location_ids)})
        ORDER BY utc_hour_start
        """,
        (start_date.isoformat(), end_date.isoformat(), *location_ids),
    ).fetchall()
    area_rows = conn.execute(
        """
        SELECT *
        FROM weather_area_hourly
        WHERE area_proxy=? AND local_date BETWEEN ? AND ?
        ORDER BY utc_hour_start
        """,
        (area_proxy, start_date.isoformat(), end_date.isoformat()),
    ).fetchall()
    loc_keys = [(row["location_id"], row["utc_hour_start"]) for row in location_rows]
    area_keys = [row["utc_hour_start"] for row in area_rows]
    duplicate_location_rows = len(loc_keys) - len(set(loc_keys))
    duplicate_area_rows = len(area_keys) - len(set(area_keys))
    loc_present = set(loc_keys)
    missing_locations = [
        (location.location_id, hour)
        for location in locations
        for hour in expected_hours
        if (location.location_id, hour) not in loc_present
    ]
    missing_area = [hour for hour in expected_hours if hour not in set(area_keys)]
    null_counts: dict[str, int] = {}
    for variable in WEATHER_VARIABLES:
        null_counts[variable] = sum(1 for row in location_rows if row[variable] is None)
        null_counts["weighted_" + variable] = sum(1 for row in area_rows if row["weighted_" + variable] is None)
    per_year_location: dict[str, int] = {}
    for row in location_rows:
        year = row["local_date"][:4]
        per_year_location[year] = per_year_location.get(year, 0) + 1
    per_year_area: dict[str, int] = {}
    for row in area_rows:
        year = row["local_date"][:4]
        per_year_area[year] = per_year_area.get(year, 0) + 1
    stats: dict[str, dict[str, float | None]] = {}
    for variable in WEATHER_VARIABLES:
        vals = [float(row["weighted_" + variable]) for row in area_rows if row["weighted_" + variable] is not None]
        stats[variable] = {
            "min": min(vals) if vals else None,
            "max": max(vals) if vals else None,
            "mean": (sum(vals) / len(vals)) if vals else None,
        }
    errors: list[str] = []
    if missing_locations:
        errors.append(f"missing_location_hours={len(missing_locations)}")
    if missing_area:
        errors.append(f"missing_area_hours={len(missing_area)}")
    if duplicate_location_rows:
        errors.append(f"duplicate_location_rows={duplicate_location_rows}")
    if duplicate_area_rows:
        errors.append(f"duplicate_area_rows={duplicate_area_rows}")
    nonzero_nulls = {key: value for key, value in null_counts.items() if value}
    if nonzero_nulls:
        errors.append(f"null_values={sum(nonzero_nulls.values())}")
    db_size = Path(db_path).expanduser().stat().st_size if db_path and Path(db_path).expanduser().exists() else 0
    first = min([row["utc_hour_start"] for row in area_rows], default=None)
    last = max([row["utc_hour_start"] for row in area_rows], default=None)
    return ValidationReport(
        db_path=db_path,
        area_proxy=area_proxy,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        complete=not errors,
        location_row_count=len(location_rows),
        location_expected_count=expected_location_count,
        area_row_count=len(area_rows),
        area_expected_count=len(expected_hours),
        first_utc_hour_start=first,
        last_utc_hour_start=last,
        location_gap_count=len(missing_locations),
        area_gap_count=len(missing_area),
        duplicate_location_rows=duplicate_location_rows,
        duplicate_area_rows=duplicate_area_rows,
        null_counts=null_counts,
        per_year_location_counts=per_year_location,
        per_year_area_counts=per_year_area,
        variable_stats=stats,
        db_size_bytes=db_size,
        errors=tuple(errors),
    )


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
