"""P0056B northern Europe area weather actual-proxy features."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import csv
import json
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write
from src.mac.services.weather_history.storage import DEFAULT_DB_PATH as DEFAULT_WEATHER_DB


PACKAGE_ID = "P0056B"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0056B")
OUTPUT_TABLE = "area_weather_features_hourly_v1"
START_UTC = "2022-06-01T00:00Z"
REQUIRED_AREAS = (
    "SE1",
    "SE2",
    "SE3",
    "SE4",
    "NO1",
    "NO2",
    "NO3",
    "NO4",
    "NO5",
    "DK1",
    "DK2",
    "FI",
    "EE",
    "LV",
    "LT",
    "DE_LU",
    "PL",
    "NL",
)
DIRECT_OR_STRONG_PROXY_AREAS = {"SE1", "SE2", "SE3", "SE4", "NO1", "NO2", "NO3", "NO4", "NO5", "DK2", "FI"}
FALLBACK_AREAS = tuple(area for area in REQUIRED_AREAS if area not in DIRECT_OR_STRONG_PROXY_AREAS)
HEATING_BASE_C = 17.0
COOLING_BASE_C = 22.0


@dataclass(frozen=True)
class P0056BResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0056b_weather_proxies(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0056BResult:
    started = time.monotonic()
    feature_path = Path(feature_db).expanduser()
    weather_path = Path(weather_db).expanduser()
    evidence_path = Path(evidence_dir)
    with sqlite3.connect(feature_path, timeout=60.0) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=60000")
        conn.execute("ATTACH DATABASE ? AS weather_db", (str(weather_path),))
        create_schema(conn)
        source_inventory = load_source_inventory(conn)
        if not source_inventory["has_local_weather_source"]:
            summary = stopped_summary(started, feature_path, weather_path, source_inventory)
            evidence = write_evidence(evidence_path, summary)
            return P0056BResult("STOP", {}, evidence)
        rows = build_area_weather_rows(conn)
        replace_output_rows(conn, rows)
        validation = validate_area_weather(conn)
        summary = build_summary(started, feature_path, weather_path, source_inventory, validation)
        evidence = write_evidence(evidence_path, summary)
        status = decide_status(validation)
        return P0056BResult(status=status, row_counts=summary["row_counts"], evidence=evidence)  # type: ignore[arg-type]


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {OUTPUT_TABLE} (
            timestamp_utc TEXT NOT NULL,
            area_code TEXT NOT NULL,
            temperature_2m REAL NOT NULL,
            apparent_temperature REAL,
            wind_speed REAL,
            cloud_cover REAL,
            relative_humidity REAL,
            precipitation REAL,
            snow_depth REAL,
            heating_degree_proxy REAL NOT NULL,
            cooling_degree_proxy REAL,
            temperature_2m_roll_mean_24h REAL NOT NULL,
            source_station_or_proxy_ids TEXT NOT NULL,
            missingness_flags TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (timestamp_utc, area_code, generated_by_package)
        )
        """
    )
    conn.execute(
        f"""
        CREATE INDEX IF NOT EXISTS idx_{OUTPUT_TABLE}_area_time
        ON {OUTPUT_TABLE}(area_code, timestamp_utc)
        """
    )
    conn.commit()


def area_proxy_selection() -> list[dict[str, object]]:
    selections = {
        "SE1": [
            source("area_proxy", "se1_core_weather", 1.00, "Northern Sweden load-weighted weather proxy.", False),
        ],
        "SE2": [
            source("area_proxy", "se1_core_weather", 0.65, "Cold northern Swedish component.", False),
            source("area_proxy", "se3_load_weather", 0.35, "Southern transition component for SE2 load geography.", False),
        ],
        "SE3": [
            source("area_proxy", "se3_load_weather", 1.00, "Existing SE3 broad load weather proxy.", False),
        ],
        "SE4": [
            source("area_proxy", "se4_load_weather", 1.00, "Existing SE4 load weather proxy.", False),
        ],
        "NO1": [
            source("location", "nordic_connected_oslo", 0.80, "Oslo/East Norway load centre.", False),
            source("location", "nordic_connected_bergen", 0.20, "Western Norwegian weather influence.", False),
        ],
        "NO2": [
            source("location", "nordic_connected_bergen", 0.55, "South-west Norway load and coast component.", False),
            source("location", "nordic_connected_oslo", 0.25, "South Norway inland/east component.", False),
            source("location", "south_connected_goteborg", 0.20, "Nearby southern Nordic fallback component.", False),
        ],
        "NO3": [
            source("location", "nordic_connected_trondheim", 0.80, "Central Norway load centre.", False),
            source("location", "nordic_connected_bergen", 0.20, "Coastal Norway moderation.", False),
        ],
        "NO4": [
            source("location", "se1_core_tromso", 0.35, "Northern Norway coastal component.", False),
            source("location", "se1_core_bodo", 0.25, "Nordland coastal component.", False),
            source("location", "se1_core_narvik", 0.25, "Northern inland/coastal transition.", False),
            source("location", "nordic_connected_trondheim", 0.15, "Southern NO4 transition component.", False),
        ],
        "NO5": [
            source("location", "nordic_connected_bergen", 0.75, "West Norway load centre.", False),
            source("location", "nordic_connected_oslo", 0.25, "Inland/east transition component.", False),
        ],
        "DK1": [
            source("location", "south_connected_copenhagen", 0.45, "Available Denmark station, fallback for Jutland.", True),
            source("location", "south_connected_malmo", 0.30, "Nearby southern Scandinavia fallback.", True),
            source("location", "south_connected_goteborg", 0.25, "Western Scandinavia fallback.", True),
        ],
        "DK2": [
            source("location", "south_connected_copenhagen", 0.80, "Zealand/Copenhagen load centre.", False),
            source("location", "south_connected_malmo", 0.20, "Oresund regional component.", False),
        ],
        "FI": [
            source("location", "nordic_connected_helsinki", 0.35, "Southern Finland load centre.", False),
            source("location", "nordic_connected_tampere", 0.25, "Inland Finland load centre.", False),
            source("location", "nordic_connected_turku", 0.20, "South-west Finland component.", False),
            source("location", "se1_core_oulu", 0.10, "Northern Finland component.", False),
            source("location", "se1_core_rovaniemi", 0.10, "Lapland component.", False),
        ],
        "EE": [
            source("location", "nordic_connected_helsinki", 0.45, "Nearest configured Baltic-adjacent station.", True),
            source("location", "south_connected_stockholm", 0.30, "Baltic Sea regional fallback.", True),
            source("location", "nordic_connected_turku", 0.25, "South Finland fallback.", True),
        ],
        "LV": [
            source("location", "nordic_connected_helsinki", 0.30, "Baltic north fallback.", True),
            source("location", "south_connected_stockholm", 0.30, "Baltic Sea regional fallback.", True),
            source("location", "south_connected_copenhagen", 0.20, "Southern Baltic fallback.", True),
            source("location", "south_connected_malmo", 0.20, "Southern Baltic fallback.", True),
        ],
        "LT": [
            source("location", "south_connected_copenhagen", 0.30, "Southern Baltic fallback.", True),
            source("location", "south_connected_malmo", 0.25, "Southern Baltic fallback.", True),
            source("location", "south_connected_stockholm", 0.25, "Baltic Sea regional fallback.", True),
            source("location", "nordic_connected_helsinki", 0.20, "Northern Baltic fallback.", True),
        ],
        "DE_LU": [
            source("location", "south_connected_copenhagen", 0.45, "Closest configured continental-adjacent station.", True),
            source("location", "south_connected_malmo", 0.35, "Southern Baltic/North Germany fallback.", True),
            source("location", "south_connected_goteborg", 0.20, "Western Scandinavian fallback.", True),
        ],
        "PL": [
            source("location", "south_connected_malmo", 0.40, "Southern Baltic fallback.", True),
            source("location", "se3_load_kalmar", 0.30, "South-east Sweden/Baltic fallback.", True),
            source("location", "south_connected_copenhagen", 0.20, "Western Baltic fallback.", True),
            source("location", "south_connected_stockholm", 0.10, "Baltic regional fallback.", True),
        ],
        "NL": [
            source("location", "south_connected_copenhagen", 0.45, "Closest configured North Sea-adjacent fallback.", True),
            source("location", "south_connected_malmo", 0.30, "Southern Scandinavia fallback.", True),
            source("location", "south_connected_goteborg", 0.25, "Western Scandinavia fallback.", True),
        ],
    }
    rows: list[dict[str, object]] = []
    for area in REQUIRED_AREAS:
        for item in selections[area]:
            row = dict(item)
            row["area_code"] = area
            rows.append(row)
    return rows


def source(kind: str, source_id: str, weight: float, reason: str, fallback: bool) -> dict[str, object]:
    return {
        "source_kind": kind,
        "source_id": source_id,
        "weight": float(weight),
        "reason": reason,
        "fallback_proxy": bool(fallback),
    }


def load_source_inventory(conn: sqlite3.Connection) -> dict[str, object]:
    area_rows = [dict(row) for row in conn.execute(
        """
        SELECT area_proxy, COUNT(*) AS rows, MIN(utc_hour_start) AS min_ts, MAX(utc_hour_start) AS max_ts
        FROM weather_db.weather_area_hourly
        GROUP BY area_proxy
        ORDER BY area_proxy
        """
    )]
    location_rows = [dict(row) for row in conn.execute(
        """
        SELECT l.location_id, l.name, l.latitude, l.longitude, l.weight, l.area_proxy, l.source, l.active,
               COUNT(o.utc_hour_start) AS rows,
               MIN(o.utc_hour_start) AS min_ts,
               MAX(o.utc_hour_start) AS max_ts
        FROM weather_db.weather_locations l
        LEFT JOIN weather_db.weather_observations o ON o.location_id=l.location_id
        WHERE l.active=1
        GROUP BY l.location_id
        ORDER BY l.area_proxy, l.location_id
        """
    )]
    consumption_rows = [dict(row) for row in conn.execute(
        """
        SELECT area_code, COUNT(*) AS rows, MIN(timestamp_utc) AS min_ts, MAX(timestamp_utc) AS max_ts
        FROM area_consumption_hourly_v1
        WHERE generated_by_package='P0056A'
        GROUP BY area_code
        ORDER BY area_code
        """
    )]
    required_sources = {(str(row["source_kind"]), str(row["source_id"])) for row in area_proxy_selection()}
    existing_area_proxies = {str(row["area_proxy"]) for row in area_rows}
    existing_locations = {str(row["location_id"]) for row in location_rows}
    missing_sources = sorted(
        f"{kind}:{source_id}"
        for kind, source_id in required_sources
        if (kind == "area_proxy" and source_id not in existing_area_proxies)
        or (kind == "location" and source_id not in existing_locations)
    )
    return {
        "weather_area_hourly": area_rows,
        "weather_locations": location_rows,
        "p0056a_consumption": consumption_rows,
        "required_areas": list(REQUIRED_AREAS),
        "fallback_areas": list(FALLBACK_AREAS),
        "missing_required_sources": missing_sources,
        "has_local_weather_source": bool(area_rows or location_rows) and not missing_sources,
    }


def build_area_weather_rows(conn: sqlite3.Connection) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in area_proxy_selection():
        grouped[str(item["area_code"])].append(item)

    source_cache: dict[tuple[str, str], dict[str, dict[str, float | None]]] = {}
    output: list[dict[str, object]] = []
    for area_code in REQUIRED_AREAS:
        sources = grouped[area_code]
        source_series = []
        for item in sources:
            key = (str(item["source_kind"]), str(item["source_id"]))
            if key not in source_cache:
                source_cache[key] = load_weather_source_series(conn, key[0], key[1])
            source_series.append((item, source_cache[key]))
        output.extend(build_features_for_area(area_code, source_series))
    return output


def load_weather_source_series(conn: sqlite3.Connection, kind: str, source_id: str) -> dict[str, dict[str, float | None]]:
    if kind == "area_proxy":
        rows = conn.execute(
            """
            SELECT utc_hour_start AS timestamp_utc,
                   weighted_temperature_2m AS temperature_2m,
                   weighted_apparent_temperature AS apparent_temperature,
                   weighted_wind_speed_100m AS wind_speed,
                   weighted_cloud_cover AS cloud_cover,
                   weighted_relative_humidity_2m AS relative_humidity,
                   weighted_precipitation AS precipitation
            FROM weather_db.weather_area_hourly
            WHERE area_proxy=? AND utc_hour_start >= ?
            ORDER BY utc_hour_start
            """,
            (source_id, START_UTC),
        ).fetchall()
    elif kind == "location":
        rows = conn.execute(
            """
            SELECT utc_hour_start AS timestamp_utc,
                   temperature_2m,
                   apparent_temperature,
                   wind_speed_100m AS wind_speed,
                   cloud_cover,
                   relative_humidity_2m AS relative_humidity,
                   precipitation
            FROM weather_db.weather_observations
            WHERE location_id=? AND utc_hour_start >= ?
            ORDER BY utc_hour_start
            """,
            (source_id, START_UTC),
        ).fetchall()
    else:
        raise ValueError(f"Unsupported weather source kind: {kind}")
    return {
        str(row["timestamp_utc"]): {
            "temperature_2m": nullable_float(row["temperature_2m"]),
            "apparent_temperature": nullable_float(row["apparent_temperature"]),
            "wind_speed": nullable_float(row["wind_speed"]),
            "cloud_cover": nullable_float(row["cloud_cover"]),
            "relative_humidity": nullable_float(row["relative_humidity"]),
            "precipitation": nullable_float(row["precipitation"]),
        }
        for row in rows
    }


def build_features_for_area(
    area_code: str,
    source_series: list[tuple[dict[str, object], dict[str, dict[str, float | None]]]],
) -> list[dict[str, object]]:
    timestamps = sorted({timestamp for _, series in source_series for timestamp in series})
    rows: list[dict[str, object]] = []
    rolling: deque[float] = deque(maxlen=24)
    source_ids = [str(item["source_id"]) for item, _ in source_series]
    source_weight_total = sum(float(item["weight"]) for item, _ in source_series)
    fallback_area = any(bool(item["fallback_proxy"]) for item, _ in source_series)
    for timestamp in timestamps:
        values = {}
        for feature in ("temperature_2m", "apparent_temperature", "wind_speed", "cloud_cover", "relative_humidity", "precipitation"):
            values[feature] = weighted_feature(source_series, timestamp, feature)
        temperature = values["temperature_2m"]
        if temperature is None:
            continue
        rolling.append(float(temperature))
        coverage_weight = sum(float(item["weight"]) for item, series in source_series if timestamp in series)
        flags = []
        if coverage_weight + 1e-9 < source_weight_total:
            flags.append("partial_source_coverage")
        else:
            flags.append("complete_source_coverage")
        flags.append("snow_depth_unavailable")
        if fallback_area:
            flags.append("fallback_proxy")
        rows.append(
            {
                "timestamp_utc": timestamp,
                "area_code": area_code,
                "temperature_2m": float(temperature),
                "apparent_temperature": values["apparent_temperature"],
                "wind_speed": values["wind_speed"],
                "cloud_cover": values["cloud_cover"],
                "relative_humidity": values["relative_humidity"],
                "precipitation": values["precipitation"],
                "snow_depth": None,
                "heating_degree_proxy": max(0.0, HEATING_BASE_C - float(temperature)),
                "cooling_degree_proxy": max(0.0, float(temperature) - COOLING_BASE_C),
                "temperature_2m_roll_mean_24h": sum(rolling) / len(rolling),
                "source_station_or_proxy_ids": json.dumps(source_ids, sort_keys=True),
                "missingness_flags": ",".join(flags),
                "generated_by_package": PACKAGE_ID,
            }
        )
    return rows


def weighted_feature(
    source_series: list[tuple[dict[str, object], dict[str, dict[str, float | None]]]],
    timestamp: str,
    feature: str,
) -> float | None:
    numerator = 0.0
    denominator = 0.0
    for item, series in source_series:
        source_row = series.get(timestamp)
        if not source_row:
            continue
        value = source_row.get(feature)
        if value is None:
            continue
        weight = float(item["weight"])
        numerator += float(value) * weight
        denominator += weight
    if denominator <= 0.0:
        return None
    return numerator / denominator


def replace_output_rows(conn: sqlite3.Connection, rows: list[dict[str, object]]) -> None:
    conn.execute(f"DELETE FROM {OUTPUT_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,))
    if rows:
        columns = list(rows[0])
        placeholders = ", ".join("?" for _ in columns)
        conn.executemany(
            f"INSERT OR REPLACE INTO {OUTPUT_TABLE} ({', '.join(columns)}) VALUES ({placeholders})",
            [tuple(row[column] for column in columns) for row in rows],
        )
    conn.commit()


def validate_area_weather(conn: sqlite3.Connection) -> dict[str, object]:
    area_rows = [dict(row) for row in conn.execute(
        f"""
        SELECT area_code,
               COUNT(*) AS row_count,
               MIN(timestamp_utc) AS min_timestamp_utc,
               MAX(timestamp_utc) AS max_timestamp_utc,
               AVG(temperature_2m) AS mean_temperature,
               AVG(CASE WHEN SUBSTR(timestamp_utc, 6, 2) IN ('12','01','02') THEN temperature_2m END) AS winter_mean_temperature,
               AVG(CASE WHEN SUBSTR(timestamp_utc, 6, 2) IN ('06','07','08') THEN temperature_2m END) AS summer_mean_temperature,
               SUM(CASE WHEN snow_depth IS NULL THEN 1 ELSE 0 END) AS snow_depth_null_rows,
               SUM(CASE WHEN missingness_flags LIKE '%fallback_proxy%' THEN 1 ELSE 0 END) AS fallback_rows
        FROM {OUTPUT_TABLE}
        WHERE generated_by_package=?
        GROUP BY area_code
        ORDER BY area_code
        """,
        (PACKAGE_ID,),
    )]
    temperature_values = load_temperature_values(conn)
    coverage_rows = []
    for row in area_rows:
        values = temperature_values[str(row["area_code"])]
        expected = expected_hours(str(row["min_timestamp_utc"]), str(row["max_timestamp_utc"]))
        coverage_rows.append({
            **row,
            "coverage_ratio": float(row["row_count"]) / expected if expected else 0.0,
            "missing_hour_count": max(0, expected - int(row["row_count"])),
            "p05_temperature": percentile(values, 0.05),
            "p95_temperature": percentile(values, 0.95),
        })
    se3_consistency = se3_proxy_consistency(conn)
    p0056a_alignment = p0056a_alignment_summary(conn)
    regional = regional_validation(coverage_rows)
    required_present = set(REQUIRED_AREAS) == {str(row["area_code"]) for row in coverage_rows}
    max_missing_hours = max((int(row["missing_hour_count"]) for row in coverage_rows), default=0)
    return {
        "coverage": coverage_rows,
        "required_areas_present": required_present,
        "missing_required_areas": sorted(set(REQUIRED_AREAS) - {str(row["area_code"]) for row in coverage_rows}),
        "max_missing_hour_count": max_missing_hours,
        "fallback_areas": list(FALLBACK_AREAS),
        "all_area_weather_proxies_identical": all_area_weather_proxies_identical(coverage_rows),
        "regional_validation": regional,
        "se3_consistency": se3_consistency,
        "p0056a_alignment": p0056a_alignment,
        "snow_depth_available": False,
        "ready_for_multi_area_consumption_forecast": required_present and bool(se3_consistency["ok"]) and max_missing_hours == 0,
    }


def load_temperature_values(conn: sqlite3.Connection) -> dict[str, list[float]]:
    values: dict[str, list[float]] = defaultdict(list)
    for row in conn.execute(
        f"""
        SELECT area_code, temperature_2m
        FROM {OUTPUT_TABLE}
        WHERE generated_by_package=?
        ORDER BY area_code, timestamp_utc
        """,
        (PACKAGE_ID,),
    ):
        values[str(row["area_code"])].append(float(row["temperature_2m"]))
    return values


def se3_proxy_consistency(conn: sqlite3.Connection) -> dict[str, object]:
    table_exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table','view') AND name='se3_climate_zone_weather_hourly_v1'"
    ).fetchone()
    if not table_exists:
        return {"ok": False, "reason": "missing_se3_climate_zone_weather_hourly_v1"}
    rows = conn.execute(
        f"""
        SELECT COUNT(*) AS overlap_count,
               MAX(ABS(w.temperature_2m - z.feature_value)) AS max_abs_temperature_delta,
               AVG(ABS(w.temperature_2m - z.feature_value)) AS mean_abs_temperature_delta
        FROM {OUTPUT_TABLE} w
        JOIN se3_climate_zone_weather_hourly_v1 z
          ON z.timestamp_utc=w.timestamp_utc
         AND z.climate_zone_id='SE3_BROAD_PROXY'
         AND z.feature_name='temperature_2m'
         AND z.generated_by_package='P0054Z'
        WHERE w.generated_by_package=? AND w.area_code='SE3'
        """,
        (PACKAGE_ID,),
    ).fetchone()
    overlap = int(rows["overlap_count"] or 0)
    max_delta = float(rows["max_abs_temperature_delta"] or 0.0)
    return {
        "ok": overlap > 0 and max_delta <= 1e-9,
        "overlap_count": overlap,
        "max_abs_temperature_delta": max_delta,
        "mean_abs_temperature_delta": float(rows["mean_abs_temperature_delta"] or 0.0),
    }


def p0056a_alignment_summary(conn: sqlite3.Connection) -> list[dict[str, object]]:
    rows = []
    for row in conn.execute(
        f"""
        SELECT c.area_code,
               c.rows AS p0056a_consumption_rows,
               c.max_ts AS p0056a_max_timestamp_utc,
               w.rows AS weather_rows,
               w.max_ts AS weather_max_timestamp_utc
        FROM (
          SELECT area_code, COUNT(*) AS rows, MAX(timestamp_utc) AS max_ts
          FROM area_consumption_hourly_v1
          WHERE generated_by_package='P0056A'
          GROUP BY area_code
        ) c
        LEFT JOIN (
          SELECT area_code, COUNT(*) AS rows, MAX(timestamp_utc) AS max_ts
          FROM {OUTPUT_TABLE}
          WHERE generated_by_package=?
          GROUP BY area_code
        ) w ON w.area_code=c.area_code
        ORDER BY c.area_code
        """,
        (PACKAGE_ID,),
    ):
        rows.append(dict(row))
    return rows


def regional_validation(coverage_rows: list[dict[str, object]]) -> dict[str, object]:
    mean_by_area = {str(row["area_code"]): float(row["mean_temperature"]) for row in coverage_rows}
    warm_reference = [mean_by_area[area] for area in ("DK1", "DK2", "NL", "DE_LU") if area in mean_by_area]
    warm_mean = sum(warm_reference) / len(warm_reference) if warm_reference else None
    return {
        "warm_reference_areas": ["DK1", "DK2", "NL", "DE_LU"],
        "warm_reference_mean_temperature": warm_mean,
        "no4_colder_than_warm_reference": warm_mean is not None and mean_by_area.get("NO4", 999.0) < warm_mean,
        "se1_colder_than_warm_reference": warm_mean is not None and mean_by_area.get("SE1", 999.0) < warm_mean,
        "mean_temperature_range": max(mean_by_area.values()) - min(mean_by_area.values()) if mean_by_area else 0.0,
    }


def all_area_weather_proxies_identical(coverage_rows: list[dict[str, object]]) -> bool:
    means = {round(float(row["mean_temperature"]), 6) for row in coverage_rows}
    return len(means) <= 1


def build_summary(
    started: float,
    feature_path: Path,
    weather_path: Path,
    source_inventory: dict[str, object],
    validation: dict[str, object],
) -> dict[str, object]:
    row_counts = {
        "area_weather_features_hourly_v1_rows": sum(int(row["row_count"]) for row in validation["coverage"]),  # type: ignore[index]
        "areas": len(validation["coverage"]),  # type: ignore[arg-type]
        "fallback_areas": len(FALLBACK_AREAS),
    }
    return {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": decide_status(validation),
        "runtime_seconds": round(time.monotonic() - started, 3),
        "feature_db": str(feature_path),
        "weather_db": str(weather_path),
        "source_inventory": source_inventory,
        "selection": enriched_selection(source_inventory),
        "schema": output_schema(),
        "feature_contract": feature_contract(),
        "validation": validation,
        "row_counts": row_counts,
        "no_api": True,
        "no_devices": True,
        "no_runtime_change": True,
        "no_model_training": True,
        "no_spot_price_features": True,
        "actual_weather_proxy_not_production_forecast": True,
    }


def stopped_summary(started: float, feature_path: Path, weather_path: Path, source_inventory: dict[str, object]) -> dict[str, object]:
    return {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": "STOP",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "feature_db": str(feature_path),
        "weather_db": str(weather_path),
        "source_inventory": source_inventory,
        "row_counts": {},
        "stop_reason": "missing local weather source required by P0056B",
    }


def decide_status(validation: dict[str, object]) -> str:
    if not validation.get("required_areas_present") or not validation.get("se3_consistency", {}).get("ok"):  # type: ignore[union-attr]
        return "STOP"
    if FALLBACK_AREAS or not validation.get("snow_depth_available"):
        return "WARN"
    return "PASS"


def enriched_selection(source_inventory: dict[str, object]) -> list[dict[str, object]]:
    location_meta = {str(row["location_id"]): row for row in source_inventory.get("weather_locations", [])}  # type: ignore[union-attr]
    area_meta = {str(row["area_proxy"]): row for row in source_inventory.get("weather_area_hourly", [])}  # type: ignore[union-attr]
    rows = []
    for item in area_proxy_selection():
        source_id = str(item["source_id"])
        meta = location_meta.get(source_id) if item["source_kind"] == "location" else area_meta.get(source_id, {})
        rows.append({
            **item,
            "source_name": meta.get("name", source_id),
            "country_region": country_region(str(item["area_code"])),
            "latitude": meta.get("latitude"),
            "longitude": meta.get("longitude"),
            "coverage_start": meta.get("min_ts"),
            "coverage_end": meta.get("max_ts"),
            "missingness": "complete_source_rows" if meta.get("rows") else "missing",
        })
    return rows


def country_region(area_code: str) -> str:
    mapping = {
        "SE1": "Sweden north",
        "SE2": "Sweden north/central",
        "SE3": "Sweden central/south",
        "SE4": "Sweden south",
        "NO1": "Norway east",
        "NO2": "Norway south-west",
        "NO3": "Norway central",
        "NO4": "Norway north",
        "NO5": "Norway west",
        "DK1": "Denmark west",
        "DK2": "Denmark east",
        "FI": "Finland",
        "EE": "Estonia fallback",
        "LV": "Latvia fallback",
        "LT": "Lithuania fallback",
        "DE_LU": "Germany/Luxembourg fallback",
        "PL": "Poland fallback",
        "NL": "Netherlands fallback",
    }
    return mapping[area_code]


def output_schema() -> list[dict[str, str]]:
    return [
        {"column": "timestamp_utc", "type": "TEXT", "description": "UTC hour start"},
        {"column": "area_code", "type": "TEXT", "description": "P0056A primary area"},
        {"column": "temperature_2m", "type": "REAL", "description": "Weighted Celsius actual-weather proxy"},
        {"column": "apparent_temperature", "type": "REAL nullable", "description": "Weighted Celsius actual-weather proxy"},
        {"column": "wind_speed", "type": "REAL nullable", "description": "Weighted 100m wind speed proxy"},
        {"column": "cloud_cover", "type": "REAL nullable", "description": "Weighted cloud cover proxy"},
        {"column": "relative_humidity", "type": "REAL nullable", "description": "Weighted relative humidity proxy"},
        {"column": "precipitation", "type": "REAL nullable", "description": "Weighted precipitation proxy"},
        {"column": "snow_depth", "type": "REAL nullable", "description": "Null; source has snowfall, not snow depth"},
        {"column": "heating_degree_proxy", "type": "REAL", "description": "max(0, 17C - temperature_2m)"},
        {"column": "cooling_degree_proxy", "type": "REAL nullable", "description": "max(0, temperature_2m - 22C)"},
        {"column": "temperature_2m_roll_mean_24h", "type": "REAL", "description": "Current plus prior 23 UTC hours"},
        {"column": "source_station_or_proxy_ids", "type": "TEXT", "description": "JSON list of source IDs"},
        {"column": "missingness_flags", "type": "TEXT", "description": "Comma-separated source/fallback flags"},
        {"column": "generated_by_package", "type": "TEXT", "description": PACKAGE_ID},
    ]


def feature_contract() -> dict[str, object]:
    return {
        "input_class": "historical_observed_only",
        "prediction_kind": "weather_actual_proxy",
        "heating_degree_base_c": HEATING_BASE_C,
        "cooling_degree_base_c": COOLING_BASE_C,
        "rolling_windows": ["temperature_2m_roll_mean_24h"],
        "utc_handling": "timestamps are UTC hour starts; no local-time or DST join is performed",
        "spot_price_features": False,
        "model_training": False,
        "production_weather_forecast": False,
    }


def write_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence: dict[str, str] = {}
    evidence["CHANGELOG.md"] = write(evidence_dir / "CHANGELOG.md", changelog_md(summary))
    evidence["labb-label.md"] = write(evidence_dir / "labb-label.md", labb_label_md(summary))
    evidence["p0056a-input-review.md"] = write(evidence_dir / "p0056a-input-review.md", p0056a_input_review_md(summary))
    evidence["weather-source-inventory.md"] = write(evidence_dir / "weather-source-inventory.md", weather_source_inventory_md(summary))
    evidence["area-weather-scope.md"] = write(evidence_dir / "area-weather-scope.md", area_weather_scope_md(summary))
    evidence["station-proxy-selection.md"] = write(evidence_dir / "station-proxy-selection.md", station_proxy_selection_md(summary))
    evidence["output-table-schema.md"] = write(evidence_dir / "output-table-schema.md", output_table_schema_md(summary))
    evidence["weather-feature-contract.md"] = write(evidence_dir / "weather-feature-contract.md", weather_feature_contract_md(summary))
    evidence["coverage-and-missingness.md"] = write(evidence_dir / "coverage-and-missingness.md", coverage_and_missingness_md(summary))
    evidence["weather-proxy-validation.md"] = write(evidence_dir / "weather-proxy-validation.md", weather_proxy_validation_md(summary))
    evidence["se3-proxy-consistency-check.md"] = write(evidence_dir / "se3-proxy-consistency-check.md", se3_proxy_consistency_md(summary))
    evidence["database-output-evidence.md"] = write(evidence_dir / "database-output-evidence.md", database_output_evidence_md(summary))
    evidence["forecast-safety-review.md"] = write(evidence_dir / "forecast-safety-review.md", forecast_safety_review_md(summary))
    evidence["modeling-readiness-review.md"] = write(evidence_dir / "modeling-readiness-review.md", modeling_readiness_review_md(summary))
    evidence["what-we-learned.md"] = write(evidence_dir / "what-we-learned.md", what_we_learned_md(summary))
    evidence["next-package-recommendation.md"] = write(evidence_dir / "next-package-recommendation.md", next_package_recommendation_md(summary))
    evidence["area-weather-summary.csv"] = write_csv(evidence_dir / "area-weather-summary.csv", summary["validation"].get("coverage", []))  # type: ignore[union-attr]
    evidence["station-proxy-selection.csv"] = write_csv(evidence_dir / "station-proxy-selection.csv", summary.get("selection", []))  # type: ignore[arg-type]
    evidence["weather-coverage-summary.csv"] = write_csv(evidence_dir / "weather-coverage-summary.csv", summary["validation"].get("p0056a_alignment", []))  # type: ignore[union-attr]
    return evidence


def write_csv(path: Path, rows: object) -> str:
    rows = list(rows) if isinstance(rows, list) else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        if not rows:
            handle.write("")
            return str(path)
        columns = list(rows[0].keys())
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


def changelog_md(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0056B Changelog",
        "",
        f"- Status: `{summary['status']}`",
        "- Created deterministic LABB area weather actual-proxy features for all P0056A primary areas.",
        f"- Output table: `{OUTPUT_TABLE}`.",
        f"- Rows written: `{summary.get('row_counts', {}).get('area_weather_features_hourly_v1_rows', 0)}`.",
        "- No API, devices, runtime changes, model training, or spot price features.",
        "",
    ])


def labb_label_md(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0056B LABB Label",
        "",
        f"Label: `{LABEL}`",
        "",
        "This package creates LABB data-preparation artifacts only. It is not a G2-KANDIDAT evaluation and does not promote production runtime behavior.",
        "",
    ])


def p0056a_input_review_md(summary: dict[str, object]) -> str:
    rows = summary["source_inventory"].get("p0056a_consumption", [])  # type: ignore[union-attr]
    lines = ["# P0056A Input Review", "", "| area | rows | min | max |", "| --- | ---: | --- | --- |"]
    for row in rows:
        lines.append(f"| {row['area_code']} | {row['rows']} | {row['min_ts']} | {row['max_ts']} |")
    lines.extend(["", "P0056B uses the P0056A primary area scope but does not read consumption values as weather features.", ""])
    return "\n".join(lines)


def weather_source_inventory_md(summary: dict[str, object]) -> str:
    inventory = summary["source_inventory"]  # type: ignore[assignment]
    lines = [
        "# Weather Source Inventory",
        "",
        f"Weather DB: `{summary['weather_db']}`",
        "",
        "## Area proxies",
        "",
        "| proxy | rows | min | max |",
        "| --- | ---: | --- | --- |",
    ]
    for row in inventory.get("weather_area_hourly", []):  # type: ignore[union-attr]
        lines.append(f"| {row['area_proxy']} | {row['rows']} | {row['min_ts']} | {row['max_ts']} |")
    lines.extend([
        "",
        "## Source status",
        "",
        f"- Missing required sources: `{inventory.get('missing_required_sources', [])}`",
        f"- Fallback areas: `{', '.join(inventory.get('fallback_areas', []))}`",
        "",
    ])
    return "\n".join(lines)


def area_weather_scope_md(summary: dict[str, object]) -> str:
    return "\n".join([
        "# Area Weather Scope",
        "",
        "Canonical P0056B weather proxies were built for:",
        "",
        "```text",
        "\n".join(REQUIRED_AREAS),
        "```",
        "",
        f"Fallback composite areas: `{', '.join(FALLBACK_AREAS)}`",
        "",
    ])


def station_proxy_selection_md(summary: dict[str, object]) -> str:
    rows = summary.get("selection", [])
    lines = [
        "# Station / Proxy Selection",
        "",
        "| area | source_kind | source_id | source_name | weight | fallback | coverage_start | coverage_end | reason |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for row in rows:  # type: ignore[union-attr]
        lines.append(
            f"| {row['area_code']} | {row['source_kind']} | {row['source_id']} | {row['source_name']} | "
            f"{float(row['weight']):.3f} | {row['fallback_proxy']} | {row['coverage_start']} | {row['coverage_end']} | {row['reason']} |"
        )
    lines.append("")
    return "\n".join(lines)


def output_table_schema_md(summary: dict[str, object]) -> str:
    lines = ["# Output Table Schema", "", f"Table: `{OUTPUT_TABLE}`", "", "| column | type | description |", "| --- | --- | --- |"]
    for row in summary["schema"]:  # type: ignore[index]
        lines.append(f"| {row['column']} | {row['type']} | {row['description']} |")
    lines.append("")
    return "\n".join(lines)


def weather_feature_contract_md(summary: dict[str, object]) -> str:
    contract = summary["feature_contract"]  # type: ignore[assignment]
    return "\n".join([
        "# Weather Feature Contract",
        "",
        f"- Input class: `{contract['input_class']}`",
        f"- Prediction kind: `{contract['prediction_kind']}`",
        f"- Heating base: `{contract['heating_degree_base_c']} C`",
        f"- Cooling base: `{contract['cooling_degree_base_c']} C`",
        f"- Rolling windows: `{contract['rolling_windows']}`",
        f"- UTC/local handling: {contract['utc_handling']}",
        f"- Spot price features: `{contract['spot_price_features']}`",
        f"- Model training: `{contract['model_training']}`",
        f"- Production weather forecast claim: `{contract['production_weather_forecast']}`",
        "",
    ])


def coverage_and_missingness_md(summary: dict[str, object]) -> str:
    coverage = summary["validation"].get("coverage", [])  # type: ignore[union-attr]
    lines = [
        "# Coverage And Missingness",
        "",
        "| area | rows | min | max | coverage_ratio | missing_hours | fallback_rows | snow_depth_null_rows |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in coverage:
        lines.append(
            f"| {row['area_code']} | {row['row_count']} | {row['min_timestamp_utc']} | {row['max_timestamp_utc']} | "
            f"{float(row['coverage_ratio']):.6f} | {row['missing_hour_count']} | {row['fallback_rows']} | {row['snow_depth_null_rows']} |"
        )
    lines.append("")
    return "\n".join(lines)


def weather_proxy_validation_md(summary: dict[str, object]) -> str:
    validation = summary["validation"]  # type: ignore[assignment]
    regional = validation["regional_validation"]
    lines = [
        "# Weather Proxy Validation",
        "",
        f"- Required areas present: `{validation['required_areas_present']}`",
        f"- Missing required areas: `{validation['missing_required_areas']}`",
        f"- All proxies identical: `{validation['all_area_weather_proxies_identical']}`",
        f"- NO4 colder than warm reference: `{regional['no4_colder_than_warm_reference']}`",
        f"- SE1 colder than warm reference: `{regional['se1_colder_than_warm_reference']}`",
        f"- Mean temperature range: `{float(regional['mean_temperature_range']):.6f}`",
        "",
        "| area | mean | p05 | p95 | winter_mean | summer_mean |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in validation["coverage"]:
        lines.append(
            f"| {row['area_code']} | {float(row['mean_temperature']):.3f} | {float(row['p05_temperature']):.3f} | "
            f"{float(row['p95_temperature']):.3f} | {float(row['winter_mean_temperature']):.3f} | {float(row['summer_mean_temperature']):.3f} |"
        )
    lines.append("")
    return "\n".join(lines)


def se3_proxy_consistency_md(summary: dict[str, object]) -> str:
    check = summary["validation"]["se3_consistency"]  # type: ignore[index]
    return "\n".join([
        "# SE3 Proxy Consistency Check",
        "",
        "P0056B SE3 uses the existing `se3_load_weather` broad proxy and is checked against P0054Z `SE3_BROAD_PROXY` temperature rows.",
        "",
        f"- OK: `{check['ok']}`",
        f"- Overlap rows: `{check.get('overlap_count', 0)}`",
        f"- Max abs temperature delta: `{float(check.get('max_abs_temperature_delta', 0.0)):.12f}`",
        f"- Mean abs temperature delta: `{float(check.get('mean_abs_temperature_delta', 0.0)):.12f}`",
        "",
    ])


def database_output_evidence_md(summary: dict[str, object]) -> str:
    rows = summary["row_counts"]  # type: ignore[assignment]
    return "\n".join([
        "# Database Output Evidence",
        "",
        f"- Feature DB: `{summary['feature_db']}`",
        f"- Output table: `{OUTPUT_TABLE}`",
        f"- Rows written by P0056B: `{rows.get('area_weather_features_hourly_v1_rows', 0)}`",
        f"- Areas: `{rows.get('areas', 0)}`",
        "",
    ])


def forecast_safety_review_md(summary: dict[str, object]) -> str:
    return "\n".join([
        "# Forecast Safety Review",
        "",
        "- P0056B writes historical actual-weather proxies for LABB work.",
        "- It does not call weather APIs.",
        "- It does not train or select models.",
        "- It does not include spot price features.",
        "- It must not be interpreted as production forecast weather.",
        "",
    ])


def modeling_readiness_review_md(summary: dict[str, object]) -> str:
    validation = summary["validation"]  # type: ignore[assignment]
    return "\n".join([
        "# Modeling Readiness Review",
        "",
        f"- Ready for multi-area consumption forecast LABB input: `{validation['ready_for_multi_area_consumption_forecast']}`",
        f"- Status: `{summary['status']}`",
        "- Main limitation: fallback composites for areas without direct local weather stations.",
        "- Future production-like work needs separate weather forecast inputs, not these actual proxies.",
        "",
    ])


def what_we_learned_md(summary: dict[str, object]) -> str:
    return "\n".join([
        "# What We Learned",
        "",
        "- Existing local weather data can cover all 18 P0056A areas with deterministic proxies.",
        "- Direct or strong proxy coverage exists for Swedish, Norwegian, Finnish, and DK2 areas.",
        "- DK1, Baltics, DE_LU, PL, and NL need fallback composites until better local or operator-provided sources exist.",
        "- SE3 broad proxy consistency can be checked exactly against P0054Z.",
        "",
    ])


def next_package_recommendation_md(summary: dict[str, object]) -> str:
    return "\n".join([
        "# Next Package Recommendation",
        "",
        "Recommended next package: P0056C LABB multi-area consumption forecast baseline.",
        "",
        "Scope should use P0056A measured consumption targets plus P0056B weather proxies with calendar and historical load features, no spot price features, no devices, and no production weather forecast claim.",
        "",
    ])


def nullable_float(value: object) -> float | None:
    if value is None:
        return None
    return float(value)


def expected_hours(min_ts: str, max_ts: str) -> int:
    start = parse_utc_hour(min_ts)
    end = parse_utc_hour(max_ts)
    return int((end - start).total_seconds() // 3600) + 1


def parse_utc_hour(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    if len(value) == len("2022-06-01T00:00Z"):
        normalized = value.replace("Z", ":00+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


def main() -> int:
    result = run_p0056b_weather_proxies()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
