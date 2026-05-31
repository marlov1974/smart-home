"""P0033 temperature-normalized spotprice feature-store builder."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
import csv
import math
import sqlite3
from statistics import median
from typing import Iterable


DEFAULT_FEATURE_DB_PATH = Path.home() / ".smart-home" / "data" / "spotprice_model_features.sqlite3"
DEFAULT_PRICE_DB_PATH = Path.home() / ".smart-home" / "data" / "spotprice_history.sqlite3"
DEFAULT_WEATHER_DB_PATH = Path.home() / ".smart-home" / "data" / "weather_history.sqlite3"
DEFAULT_CALENDAR_CSV_PATH = Path("data/calendar/se_special_days_2022_2035.csv")
SCHEMA_VERSION = "3"
M1_VERSION = "m1_calm_normal_price_v1"
M2_VERSION = "m2_smooth_cyclic_climate_normals_v2"
M3A_VERSION = "m3a_temperature_delta_v1"
M3B_VERSION = "m3b_special_day_delta_v1"

TARGETS = {
    "system_proxy_se1": "actual_se1",
    "area_diff_proxy_se3": "actual_area_diff",
}

SE1_SYSTEM_SIGNALS = {
    "se1_system_temperature": (
        ("se1_temperature", 0.70),
        ("nordic_temperature", 0.25),
        ("south_temperature", 0.05),
    ),
    "se1_system_apparent_temperature": (
        ("se1_apparent_temperature", 0.70),
        ("nordic_apparent_temperature", 0.25),
        ("south_apparent_temperature", 0.05),
    ),
    "se1_system_heating_degree": (
        ("se1_heating_degree", 0.70),
        ("nordic_heating_degree", 0.25),
        ("south_heating_degree", 0.05),
    ),
    "se1_system_cooling_degree": (
        ("se1_cooling_degree", 0.70),
        ("nordic_cooling_degree", 0.25),
        ("south_cooling_degree", 0.05),
    ),
}

AREA_DIFF_SIGNALS = (
    "se3_load_temperature",
    "temp_gradient_se3_load_minus_se1_core",
    "apparent_temp_gradient_se3_load_minus_se1_core",
    "heating_degree_gradient_se3_load_minus_se1_core",
    "south_temp_gradient_minus_se1_core",
)

M3_PRIMARY_ANOMALY_SIGNAL = {
    "system_proxy_se1": "se1_system_temperature",
    "area_diff_proxy_se3": "temp_gradient_se3_load_minus_se1_core",
}


def default_feature_db_path() -> Path:
    return DEFAULT_FEATURE_DB_PATH


def open_feature_database(path: Path | str) -> sqlite3.Connection:
    db_path = Path(path).expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS model_runs (
          run_id INTEGER PRIMARY KEY AUTOINCREMENT,
          started_at TEXT NOT NULL,
          completed_at TEXT,
          status TEXT NOT NULL,
          price_db TEXT NOT NULL,
          weather_db TEXT NOT NULL,
          start_date TEXT NOT NULL,
          end_date TEXT NOT NULL,
          row_count INTEGER NOT NULL DEFAULT 0,
          message TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS m1_normal_price_v1 (
          target TEXT NOT NULL,
          utc_hour_start TEXT NOT NULL,
          local_date TEXT NOT NULL,
          local_hour INTEGER NOT NULL,
          iso_week INTEGER NOT NULL,
          weekday INTEGER NOT NULL,
          normal_price REAL NOT NULL,
          sample_count INTEGER NOT NULL,
          bucket_year_count INTEGER NOT NULL,
          method TEXT NOT NULL,
          run_id INTEGER NOT NULL,
          PRIMARY KEY (target, utc_hour_start)
        );
        CREATE TABLE IF NOT EXISTS m2_climate_weights (
          target TEXT NOT NULL,
          input_signal TEXT NOT NULL,
          weight REAL NOT NULL,
          rationale TEXT NOT NULL,
          run_id INTEGER NOT NULL,
          PRIMARY KEY (target, input_signal)
        );
        CREATE TABLE IF NOT EXISTS m2_climate_normals (
          signal TEXT NOT NULL,
          utc_hour_start TEXT NOT NULL,
          local_date TEXT NOT NULL,
          local_hour INTEGER NOT NULL,
          day_of_year INTEGER NOT NULL,
          normal_value REAL NOT NULL,
          sample_count INTEGER NOT NULL,
          bucket_year_count INTEGER NOT NULL,
          method TEXT NOT NULL,
          run_id INTEGER NOT NULL,
          PRIMARY KEY (signal, utc_hour_start)
        );
        CREATE TABLE IF NOT EXISTS m2_climate_anomalies (
          signal TEXT NOT NULL,
          utc_hour_start TEXT NOT NULL,
          local_date TEXT NOT NULL,
          local_hour INTEGER NOT NULL,
          actual_value REAL NOT NULL,
          normal_value REAL NOT NULL,
          anomaly_value REAL NOT NULL,
          run_id INTEGER NOT NULL,
          PRIMARY KEY (signal, utc_hour_start)
        );
        CREATE TABLE IF NOT EXISTS m3_temperature_delta_buckets (
          target TEXT NOT NULL,
          anomaly_signal TEXT NOT NULL,
          bucket TEXT NOT NULL,
          sample_count INTEGER NOT NULL,
          median_residual REAL NOT NULL,
          smoothed_delta REAL NOT NULL,
          run_id INTEGER NOT NULL,
          PRIMARY KEY (target, anomaly_signal, bucket)
        );
        CREATE TABLE IF NOT EXISTS m3_temperature_delta_v1 (
          target TEXT NOT NULL,
          utc_hour_start TEXT NOT NULL,
          local_date TEXT NOT NULL,
          local_hour INTEGER NOT NULL,
          anomaly_signal TEXT NOT NULL,
          anomaly_value REAL NOT NULL,
          bucket TEXT NOT NULL,
          temp_delta REAL NOT NULL,
          run_id INTEGER NOT NULL,
          PRIMARY KEY (target, utc_hour_start)
        );
        CREATE TABLE IF NOT EXISTS calendar_special_days (
          local_date TEXT PRIMARY KEY,
          special_day_type TEXT NOT NULL,
          special_day_name TEXT NOT NULL,
          special_day_group TEXT NOT NULL,
          holiday_strength REAL NOT NULL,
          is_public_holiday INTEGER NOT NULL,
          is_major_social_holiday INTEGER NOT NULL,
          is_holiday_eve INTEGER NOT NULL,
          is_bridge_day INTEGER NOT NULL,
          bridge_strength TEXT NOT NULL,
          bridge_anchor TEXT NOT NULL,
          is_holiday_period_day INTEGER NOT NULL,
          period_name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS m3a_temperature_delta_buckets (
          target TEXT NOT NULL,
          anomaly_signal TEXT NOT NULL,
          bucket TEXT NOT NULL,
          sample_count INTEGER NOT NULL,
          median_residual REAL NOT NULL,
          smoothed_delta REAL NOT NULL,
          run_id INTEGER NOT NULL,
          PRIMARY KEY (target, anomaly_signal, bucket)
        );
        CREATE TABLE IF NOT EXISTS m3a_temperature_delta (
          target TEXT NOT NULL,
          utc_hour_start TEXT NOT NULL,
          local_date TEXT NOT NULL,
          local_hour INTEGER NOT NULL,
          anomaly_signal TEXT NOT NULL,
          anomaly_value REAL NOT NULL,
          bucket TEXT NOT NULL,
          temp_delta REAL NOT NULL,
          run_id INTEGER NOT NULL,
          PRIMARY KEY (target, utc_hour_start)
        );
        CREATE TABLE IF NOT EXISTS m3b_special_day_delta (
          target TEXT NOT NULL,
          utc_hour_start TEXT NOT NULL,
          local_date TEXT NOT NULL,
          local_hour INTEGER NOT NULL,
          special_day_type TEXT NOT NULL,
          special_day_name TEXT NOT NULL,
          special_day_group TEXT NOT NULL,
          bridge_anchor TEXT NOT NULL,
          holiday_strength REAL NOT NULL,
          model_delta REAL NOT NULL,
          sample_count INTEGER NOT NULL,
          shrinkage_factor REAL NOT NULL,
          run_id INTEGER NOT NULL,
          PRIMARY KEY (target, utc_hour_start)
        );
        CREATE TABLE IF NOT EXISTS m3b_special_day_delta_buckets (
          target TEXT NOT NULL,
          special_day_type TEXT NOT NULL,
          special_day_name TEXT NOT NULL,
          special_day_group TEXT NOT NULL,
          bridge_anchor TEXT NOT NULL,
          sample_count INTEGER NOT NULL,
          median_residual REAL NOT NULL,
          model_delta REAL NOT NULL,
          shrinkage_factor REAL NOT NULL,
          run_id INTEGER NOT NULL,
          PRIMARY KEY (target, special_day_type, special_day_name, special_day_group, bridge_anchor)
        );
        CREATE TABLE IF NOT EXISTS m3ab_normalized_prices (
          utc_hour_start TEXT PRIMARY KEY,
          local_date TEXT NOT NULL,
          local_hour INTEGER NOT NULL,
          actual_se1 REAL NOT NULL,
          actual_area_diff REAL NOT NULL,
          actual_se3 REAL NOT NULL,
          normal_price_v1_se1 REAL NOT NULL,
          normal_price_v1_area_diff REAL NOT NULL,
          m3a_temperature_delta_se1 REAL NOT NULL,
          m3a_temperature_delta_area_diff REAL NOT NULL,
          m3b_special_day_delta_se1 REAL NOT NULL,
          m3b_special_day_delta_area_diff REAL NOT NULL,
          m3ab_normalized_price_se1 REAL NOT NULL,
          m3ab_normalized_area_diff REAL NOT NULL,
          m3ab_normalized_se3 REAL NOT NULL,
          special_day_type TEXT NOT NULL,
          special_day_name TEXT NOT NULL,
          special_day_group TEXT NOT NULL,
          is_special_day INTEGER NOT NULL,
          run_id INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS m3_temp_normalized_prices_v1 (
          utc_hour_start TEXT PRIMARY KEY,
          local_date TEXT NOT NULL,
          local_hour INTEGER NOT NULL,
          actual_se1 REAL NOT NULL,
          actual_area_diff REAL NOT NULL,
          actual_se3 REAL NOT NULL,
          normal_price_v1_se1 REAL NOT NULL,
          normal_price_v1_area_diff REAL NOT NULL,
          temp_delta_v1_se1 REAL NOT NULL,
          temp_delta_v1_area_diff REAL NOT NULL,
          temp_normalized_price_v1_se1 REAL NOT NULL,
          temp_normalized_area_diff_v1 REAL NOT NULL,
          temp_normalized_price_v1_se3 REAL NOT NULL,
          run_id INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS training_foundation_manifest (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_m2_anomalies_signal_hour
          ON m2_climate_anomalies(signal, utc_hour_start);
        CREATE INDEX IF NOT EXISTS idx_m3_delta_target_hour
          ON m3_temperature_delta_v1(target, utc_hour_start);
        CREATE INDEX IF NOT EXISTS idx_m3a_delta_target_hour
          ON m3a_temperature_delta(target, utc_hour_start);
        CREATE INDEX IF NOT EXISTS idx_m3b_delta_target_hour
          ON m3b_special_day_delta(target, utc_hour_start);
        """
    )
    conn.execute(
        "INSERT OR REPLACE INTO training_foundation_manifest(key, value) VALUES('schema_version', ?)",
        (SCHEMA_VERSION,),
    )
    _ensure_column(conn, "m1_normal_price_v1", "bucket_year_count", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(conn, "m2_climate_normals", "bucket_year_count", "INTEGER NOT NULL DEFAULT 0")


def dump_p0032_location_weights(weather_db: Path | str) -> list[dict[str, object]]:
    with sqlite3.connect(Path(weather_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT area_proxy, name, latitude, longitude, weight
            FROM weather_locations
            WHERE area_proxy IN (
              'se1_core_weather',
              'nordic_connected_weather',
              'south_connected_weather',
              'se3_load_weather'
            )
            ORDER BY area_proxy, weight DESC, name
            """
        ).fetchall()
        return [_dict(row) for row in rows]


def select_m2_target_weights() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target in (
        "se1_system_temperature",
        "se1_system_apparent_temperature",
        "se1_system_heating_degree",
        "se1_system_cooling_degree",
    ):
        rows.extend(
            [
                {
                    "target": target,
                    "input_signal": "se1_core_weather",
                    "weight": 0.70,
                    "rationale": "dominant northern SE1 core climate",
                },
                {
                    "target": target,
                    "input_signal": "nordic_connected_weather",
                    "weight": 0.25,
                    "rationale": "connected Nordic climate pressure",
                },
                {
                    "target": target,
                    "input_signal": "south_connected_weather",
                    "weight": 0.05,
                    "rationale": "small broader connected-market climate component",
                },
            ]
        )
    for signal in AREA_DIFF_SIGNALS:
        rows.append(
            {
                "target": signal,
                "input_signal": signal,
                "weight": 1.0,
                "rationale": "preserve P0032 area-diff gradient as separate signal",
            }
        )
    return rows


def load_price_targets(
    conn: sqlite3.Connection,
    price_db: Path | str,
    weather_db: Path | str,
    start_date: date,
    end_date: date | None,
) -> list[dict[str, object]]:
    return _load_joined_rows(conn, price_db, weather_db, start_date, end_date)


def load_weather_proxy_features(
    conn: sqlite3.Connection,
    price_db: Path | str,
    weather_db: Path | str,
    start_date: date,
    end_date: date | None,
) -> list[dict[str, object]]:
    return _load_joined_rows(conn, price_db, weather_db, start_date, end_date)


def _load_joined_rows(
    conn: sqlite3.Connection,
    price_db: Path | str,
    weather_db: Path | str,
    start_date: date,
    end_date: date | None,
) -> list[dict[str, object]]:
    price_path = str(Path(price_db).expanduser())
    weather_path = str(Path(weather_db).expanduser())
    _detach_if_present(conn, "price_source")
    _detach_if_present(conn, "weather_source")
    conn.execute("ATTACH DATABASE ? AS price_source", (price_path,))
    conn.execute("ATTACH DATABASE ? AS weather_source", (weather_path,))
    upper = end_date.isoformat() if end_date else "9999-12-31"
    cursor = conn.execute(
        """
        SELECT
          p.utc_hour_start,
          p.local_date,
          p.local_hour,
          CAST(strftime('%j', p.local_date) AS INTEGER) AS day_of_year,
          CAST(strftime('%w', p.local_date) AS INTEGER) AS sqlite_weekday,
          p.se3_price AS actual_se3,
          p.se1_system_proxy_price AS actual_se1,
          p.area_diff_proxy_se3 AS actual_area_diff,
          se1.weighted_temperature_2m AS se1_temperature,
          se1.weighted_apparent_temperature AS se1_apparent_temperature,
          se1.heating_degree_hours AS se1_heating_degree,
          se1.cooling_degree_hours AS se1_cooling_degree,
          nordic.weighted_temperature_2m AS nordic_temperature,
          nordic.weighted_apparent_temperature AS nordic_apparent_temperature,
          nordic.heating_degree_hours AS nordic_heating_degree,
          nordic.cooling_degree_hours AS nordic_cooling_degree,
          south.weighted_temperature_2m AS south_temperature,
          south.weighted_apparent_temperature AS south_apparent_temperature,
          south.heating_degree_hours AS south_heating_degree,
          south.cooling_degree_hours AS south_cooling_degree,
          se3.weighted_temperature_2m AS se3_load_temperature,
          g.temp_gradient_se3_load_minus_se1_core,
          g.apparent_temp_gradient_se3_load_minus_se1_core,
          g.heating_degree_gradient_se3_load_minus_se1_core,
          g.south_temp_gradient_minus_se1_core
        FROM price_source.spotprice_system_proxy_hourly p
        JOIN weather_source.weather_proxy_se1_core_hourly se1
          ON se1.utc_hour_start = p.utc_hour_start
        JOIN weather_source.weather_proxy_nordic_connected_hourly nordic
          ON nordic.utc_hour_start = p.utc_hour_start
        JOIN weather_source.weather_proxy_south_connected_hourly south
          ON south.utc_hour_start = p.utc_hour_start
        JOIN weather_source.weather_proxy_se3_load_hourly se3
          ON se3.utc_hour_start = p.utc_hour_start
        JOIN weather_source.weather_proxy_gradients_hourly g
          ON g.utc_hour_start = p.utc_hour_start
         AND g.area_proxy = 'se3_area_diff_weather'
        WHERE p.local_date BETWEEN ? AND ?
        ORDER BY p.utc_hour_start
        """,
        (start_date.isoformat(), upper),
    )
    rows = cursor.fetchall()
    cursor.close()
    result: list[dict[str, object]] = []
    for row in rows:
        item = _dict(row)
        item["weekday"] = _sqlite_to_monday_weekday(int(item.pop("sqlite_weekday")))
        item["iso_week"] = date.fromisoformat(str(item["local_date"])).isocalendar().week
        _add_climate_signals(item)
        result.append(item)
    return result


def compute_m1_calm_normal_price(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_target_bucket: dict[str, dict[tuple[int, int, int], list[float]]] = {
        target: defaultdict(list) for target in TARGETS
    }
    by_target_hour: dict[str, dict[int, list[float]]] = {target: defaultdict(list) for target in TARGETS}
    bucket_years: dict[tuple[int, int, int], set[int]] = defaultdict(set)
    hour_years: dict[int, set[int]] = defaultdict(set)
    for row in rows:
        key = (int(row["iso_week"]), int(row["weekday"]), int(row["local_hour"]))
        year = date.fromisoformat(str(row["local_date"])).year
        bucket_years[key].add(year)
        hour_years[int(row["local_hour"])].add(year)
        for target, field in TARGETS.items():
            value = float(row[field])
            by_target_bucket[target][key].append(value)
            by_target_hour[target][int(row["local_hour"])].append(value)

    normal_by_target_bucket: dict[tuple[str, int, int, int], tuple[float, int, int]] = {}
    for target in TARGETS:
        for iso_week, weekday, hour in by_target_bucket[target]:
            values: list[float] = []
            years: set[int] = set()
            for week, candidate_weekday, candidate_hour in by_target_bucket[target]:
                if candidate_weekday != weekday or candidate_hour != hour:
                    continue
                if _week_distance(week, iso_week) <= 2:
                    values.extend(by_target_bucket[target][(week, candidate_weekday, candidate_hour)])
                    years.update(bucket_years[(week, candidate_weekday, candidate_hour)])
            if not values:
                values = by_target_hour[target][hour]
                years.update(hour_years[hour])
            normal_by_target_bucket[(target, iso_week, weekday, hour)] = (float(median(values)), len(values), len(years))

    output: list[dict[str, object]] = []
    for row in rows:
        for target, field in TARGETS.items():
            normal, sample_count, bucket_year_count = normal_by_target_bucket[
                (target, int(row["iso_week"]), int(row["weekday"]), int(row["local_hour"]))
            ]
            output.append(
                {
                    "target": target,
                    "utc_hour_start": row["utc_hour_start"],
                    "local_date": row["local_date"],
                    "local_hour": row["local_hour"],
                    "iso_week": row["iso_week"],
                    "weekday": row["weekday"],
                    "normal_price": normal,
                    "sample_count": sample_count,
                    "bucket_year_count": bucket_year_count,
                    "method": "median_same_weekday_hour_iso_week_plus_minus_2",
                }
            )
    return output


def compute_m2_climate_normals(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    signal_values: dict[str, dict[tuple[int, int], list[tuple[float, int]]]] = {
        signal: defaultdict(list) for signal in _all_m2_signals()
    }
    for row in rows:
        for signal in _all_m2_signals():
            signal_values[signal][(int(row["day_of_year"]), int(row["local_hour"]))].append(
                (float(row[signal]), date.fromisoformat(str(row["local_date"])).year)
            )

    normal_by_signal_bucket: dict[tuple[str, int, int], tuple[float, int, int]] = {}
    for signal in _all_m2_signals():
        for day_of_year, hour in signal_values[signal]:
            values: list[float] = []
            years: set[int] = set()
            close_values: list[float] = []
            broad_values: list[float] = []
            for (candidate_day, candidate_hour), bucket_items in signal_values[signal].items():
                if candidate_hour != hour:
                    continue
                distance = _day_distance(candidate_day, day_of_year)
                if distance <= 7:
                    close_values.extend(value for value, _year in bucket_items)
                if distance <= 21:
                    broad_values.extend(value for value, _year in bucket_items)
                    years.update(year for _value, year in bucket_items)
            sample_count = len(broad_values) if broad_values else len(close_values)
            if close_values:
                broad_mean = sum(broad_values) / len(broad_values) if broad_values else sum(close_values) / len(close_values)
                values = [0.70 * float(median(close_values)) + 0.30 * broad_mean]
            else:
                values = broad_values
            normal_by_signal_bucket[(signal, day_of_year, hour)] = (float(median(values)), sample_count, len(years))

    output: list[dict[str, object]] = []
    for row in rows:
        for signal in _all_m2_signals():
            normal, sample_count, bucket_year_count = normal_by_signal_bucket[
                (signal, int(row["day_of_year"]), int(row["local_hour"]))
            ]
            output.append(
                {
                    "signal": signal,
                    "utc_hour_start": row["utc_hour_start"],
                    "local_date": row["local_date"],
                    "local_hour": row["local_hour"],
                    "day_of_year": row["day_of_year"],
                    "normal_value": normal,
                    "sample_count": sample_count,
                    "bucket_year_count": bucket_year_count,
                    "method": "smooth_cyclic_robust_same_hour_day_plus_minus_7_21",
                }
            )
    return output


def compute_m2_climate_anomalies(
    rows: list[dict[str, object]],
    normals: list[dict[str, object]],
) -> list[dict[str, object]]:
    normal_map = {(row["signal"], row["utc_hour_start"]): float(row["normal_value"]) for row in normals}
    output: list[dict[str, object]] = []
    for row in rows:
        for signal in _all_m2_signals():
            actual = float(row[signal])
            normal = normal_map[(signal, row["utc_hour_start"])]
            output.append(
                {
                    "signal": signal,
                    "utc_hour_start": row["utc_hour_start"],
                    "local_date": row["local_date"],
                    "local_hour": row["local_hour"],
                    "actual_value": actual,
                    "normal_value": normal,
                    "anomaly_value": actual - normal,
                }
            )
    return output


def compute_m3_statistical_temperature_delta(
    rows: list[dict[str, object]],
    m1_rows: list[dict[str, object]],
    anomaly_rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    m1_map = {(row["target"], row["utc_hour_start"]): float(row["normal_price"]) for row in m1_rows}
    anomaly_map = {(row["signal"], row["utc_hour_start"]): float(row["anomaly_value"]) for row in anomaly_rows}
    residuals_by_target_bucket: dict[tuple[str, str, str], list[float]] = defaultdict(list)

    for row in rows:
        for target, actual_field in TARGETS.items():
            signal = M3_PRIMARY_ANOMALY_SIGNAL[target]
            anomaly = anomaly_map[(signal, row["utc_hour_start"])]
            bucket = temperature_bucket(anomaly)
            residual = float(row[actual_field]) - m1_map[(target, row["utc_hour_start"])]
            residuals_by_target_bucket[(target, signal, bucket)].append(residual)

    bucket_rows: list[dict[str, object]] = []
    delta_by_target_signal_bucket: dict[tuple[str, str, str], float] = {}
    for target in TARGETS:
        signal = M3_PRIMARY_ANOMALY_SIGNAL[target]
        normal_values = residuals_by_target_bucket.get((target, signal, "normal"), [])
        normal_median = float(median(normal_values)) if normal_values else 0.0
        cap = 0.50 if target == "system_proxy_se1" else 0.35
        for bucket in ("extreme_cold", "cold", "normal", "warm", "extreme_warm"):
            values = residuals_by_target_bucket.get((target, signal, bucket), [])
            med = float(median(values)) if values else normal_median
            raw_delta = 0.0 if bucket == "normal" else 0.50 * (med - normal_median)
            delta = max(-cap, min(cap, raw_delta))
            delta_by_target_signal_bucket[(target, signal, bucket)] = delta
            bucket_rows.append(
                {
                    "target": target,
                    "anomaly_signal": signal,
                    "bucket": bucket,
                    "sample_count": len(values),
                    "median_residual": med,
                    "smoothed_delta": delta,
                }
            )

    delta_rows: list[dict[str, object]] = []
    for row in rows:
        for target in TARGETS:
            signal = M3_PRIMARY_ANOMALY_SIGNAL[target]
            anomaly = anomaly_map[(signal, row["utc_hour_start"])]
            bucket = temperature_bucket(anomaly)
            delta_rows.append(
                {
                    "target": target,
                    "utc_hour_start": row["utc_hour_start"],
                    "local_date": row["local_date"],
                    "local_hour": row["local_hour"],
                    "anomaly_signal": signal,
                    "anomaly_value": anomaly,
                    "bucket": bucket,
                    "temp_delta": delta_by_target_signal_bucket[(target, signal, bucket)],
                }
            )
    return delta_rows, bucket_rows


def compute_m3a_statistical_temperature_delta(
    rows: list[dict[str, object]],
    m1_rows: list[dict[str, object]],
    anomaly_rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    return compute_m3_statistical_temperature_delta(rows, m1_rows, anomaly_rows)


def load_special_day_calendar(calendar_csv: Path | str = DEFAULT_CALENDAR_CSV_PATH) -> dict[str, dict[str, object]]:
    path = Path(calendar_csv)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {row["date"]: _calendar_row(row) for row in rows}


def compute_m3b_special_day_delta(
    rows: list[dict[str, object]],
    m1_rows: list[dict[str, object]],
    m3a_rows: list[dict[str, object]],
    calendar_rows: dict[str, dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    m1_map = {(row["target"], row["utc_hour_start"]): float(row["normal_price"]) for row in m1_rows}
    m3a_map = {(row["target"], row["utc_hour_start"]): float(row["temp_delta"]) for row in m3a_rows}
    residuals_by_bucket: dict[tuple[str, str, str, str, str], list[float]] = defaultdict(list)

    for row in rows:
        calendar = calendar_rows.get(str(row["local_date"]), _normal_calendar(str(row["local_date"])))
        if not _is_special_calendar_day(calendar):
            continue
        for target, actual_field in TARGETS.items():
            residual = float(row[actual_field]) - m1_map[(target, row["utc_hour_start"])] - m3a_map[(target, row["utc_hour_start"])]
            residuals_by_bucket[_m3b_bucket_key(target, calendar)].append(residual)

    bucket_rows: list[dict[str, object]] = []
    delta_by_key: dict[tuple[str, str, str, str, str], tuple[float, int, float, float]] = {}
    for key, values in sorted(residuals_by_bucket.items()):
        target = key[0]
        sample_count = len(values)
        med = float(median(values))
        shrinkage = sample_count / (sample_count + 24.0)
        cap = 0.50 if target == "system_proxy_se1" else 0.35
        delta = max(-cap, min(cap, med * shrinkage))
        delta_by_key[key] = (delta, sample_count, shrinkage, med)
        bucket_rows.append(
            {
                "target": target,
                "special_day_type": key[1],
                "special_day_name": key[2],
                "special_day_group": key[3],
                "bridge_anchor": key[4],
                "sample_count": sample_count,
                "median_residual": med,
                "model_delta": delta,
                "shrinkage_factor": shrinkage,
            }
        )

    delta_rows: list[dict[str, object]] = []
    for row in rows:
        calendar = calendar_rows.get(str(row["local_date"]), _normal_calendar(str(row["local_date"])))
        for target in TARGETS:
            key = _m3b_bucket_key(target, calendar)
            delta, sample_count, shrinkage, _med = delta_by_key.get(key, (0.0, 0, 0.0, 0.0))
            delta_rows.append(
                {
                    "target": target,
                    "utc_hour_start": row["utc_hour_start"],
                    "local_date": row["local_date"],
                    "local_hour": row["local_hour"],
                    "special_day_type": calendar["special_day_type"],
                    "special_day_name": calendar["special_day_name"],
                    "special_day_group": calendar["special_day_group"],
                    "bridge_anchor": calendar["bridge_anchor"],
                    "holiday_strength": calendar["holiday_strength"],
                    "model_delta": delta,
                    "sample_count": sample_count,
                    "shrinkage_factor": shrinkage,
                }
            )
    return delta_rows, bucket_rows


def temperature_bucket(anomaly: float) -> str:
    if anomaly <= -8.0:
        return "extreme_cold"
    if anomaly <= -3.0:
        return "cold"
    if anomaly < 3.0:
        return "normal"
    if anomaly < 8.0:
        return "warm"
    return "extreme_warm"


def build_temp_normalized_training_series(
    rows: list[dict[str, object]],
    m1_rows: list[dict[str, object]],
    delta_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    m1_map = {(row["target"], row["utc_hour_start"]): float(row["normal_price"]) for row in m1_rows}
    delta_map = {(row["target"], row["utc_hour_start"]): float(row["temp_delta"]) for row in delta_rows}
    output: list[dict[str, object]] = []
    for row in rows:
        se1_delta = delta_map[("system_proxy_se1", row["utc_hour_start"])]
        area_delta = delta_map[("area_diff_proxy_se3", row["utc_hour_start"])]
        normalized_se1 = float(row["actual_se1"]) - se1_delta
        normalized_area = float(row["actual_area_diff"]) - area_delta
        output.append(
            {
                "utc_hour_start": row["utc_hour_start"],
                "local_date": row["local_date"],
                "local_hour": row["local_hour"],
                "actual_se1": float(row["actual_se1"]),
                "actual_area_diff": float(row["actual_area_diff"]),
                "actual_se3": float(row["actual_se3"]),
                "normal_price_v1_se1": m1_map[("system_proxy_se1", row["utc_hour_start"])],
                "normal_price_v1_area_diff": m1_map[("area_diff_proxy_se3", row["utc_hour_start"])],
                "temp_delta_v1_se1": se1_delta,
                "temp_delta_v1_area_diff": area_delta,
                "temp_normalized_price_v1_se1": normalized_se1,
                "temp_normalized_area_diff_v1": normalized_area,
                "temp_normalized_price_v1_se3": normalized_se1 + normalized_area,
            }
        )
    return output


def build_m3ab_normalized_training_series(
    rows: list[dict[str, object]],
    m1_rows: list[dict[str, object]],
    m3a_rows: list[dict[str, object]],
    m3b_rows: list[dict[str, object]],
    calendar_rows: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    m1_map = {(row["target"], row["utc_hour_start"]): float(row["normal_price"]) for row in m1_rows}
    m3a_map = {(row["target"], row["utc_hour_start"]): float(row["temp_delta"]) for row in m3a_rows}
    m3b_map = {(row["target"], row["utc_hour_start"]): float(row["model_delta"]) for row in m3b_rows}
    output: list[dict[str, object]] = []
    for row in rows:
        calendar = calendar_rows.get(str(row["local_date"]), _normal_calendar(str(row["local_date"])))
        se1_m3a = m3a_map[("system_proxy_se1", row["utc_hour_start"])]
        area_m3a = m3a_map[("area_diff_proxy_se3", row["utc_hour_start"])]
        se1_m3b = m3b_map[("system_proxy_se1", row["utc_hour_start"])]
        area_m3b = m3b_map[("area_diff_proxy_se3", row["utc_hour_start"])]
        norm_se1 = float(row["actual_se1"]) - se1_m3a - se1_m3b
        norm_area = float(row["actual_area_diff"]) - area_m3a - area_m3b
        output.append(
            {
                "utc_hour_start": row["utc_hour_start"],
                "local_date": row["local_date"],
                "local_hour": row["local_hour"],
                "actual_se1": float(row["actual_se1"]),
                "actual_area_diff": float(row["actual_area_diff"]),
                "actual_se3": float(row["actual_se3"]),
                "normal_price_v1_se1": m1_map[("system_proxy_se1", row["utc_hour_start"])],
                "normal_price_v1_area_diff": m1_map[("area_diff_proxy_se3", row["utc_hour_start"])],
                "m3a_temperature_delta_se1": se1_m3a,
                "m3a_temperature_delta_area_diff": area_m3a,
                "m3b_special_day_delta_se1": se1_m3b,
                "m3b_special_day_delta_area_diff": area_m3b,
                "m3ab_normalized_price_se1": norm_se1,
                "m3ab_normalized_area_diff": norm_area,
                "m3ab_normalized_se3": norm_se1 + norm_area,
                "special_day_type": calendar["special_day_type"],
                "special_day_name": calendar["special_day_name"],
                "special_day_group": calendar["special_day_group"],
                "is_special_day": 1 if _is_special_calendar_day(calendar) else 0,
            }
        )
    return output


def build_training_foundation(
    *,
    price_db: Path | str = DEFAULT_PRICE_DB_PATH,
    weather_db: Path | str = DEFAULT_WEATHER_DB_PATH,
    feature_db: Path | str = DEFAULT_FEATURE_DB_PATH,
    calendar_csv: Path | str = DEFAULT_CALENDAR_CSV_PATH,
    start_date: date = date(2022, 5, 30),
    end_date: date | None = None,
) -> dict[str, object]:
    feature_path = Path(feature_db).expanduser()
    price_path = Path(price_db).expanduser()
    weather_path = Path(weather_db).expanduser()
    with open_feature_database(feature_path) as conn:
        initialize_schema(conn)
        _clear_generated_tables(conn)
        rows = _load_joined_rows(conn, price_path, weather_path, start_date, end_date)
        if not rows:
            raise ValueError("no joined P0033 input rows")
        calendar_rows = load_special_day_calendar(calendar_csv)
        actual_end = str(rows[-1]["local_date"])
        run_id = _create_run(conn, price_path, weather_path, start_date, actual_end)
        try:
            m1_rows = compute_m1_calm_normal_price(rows)
            normals = compute_m2_climate_normals(rows)
            anomalies = compute_m2_climate_anomalies(rows, normals)
            delta_rows, bucket_rows = compute_m3a_statistical_temperature_delta(rows, m1_rows, anomalies)
            m3b_rows, m3b_bucket_rows = compute_m3b_special_day_delta(rows, m1_rows, delta_rows, calendar_rows)
            normalized_rows = build_temp_normalized_training_series(rows, m1_rows, delta_rows)
            m3ab_rows = build_m3ab_normalized_training_series(rows, m1_rows, delta_rows, m3b_rows, calendar_rows)
            _store_calendar(conn, calendar_rows)
            _store_weights(conn, run_id)
            _store_m1(conn, run_id, m1_rows)
            _store_m2_normals(conn, run_id, normals)
            _store_m2_anomalies(conn, run_id, anomalies)
            _store_m3a_buckets(conn, run_id, bucket_rows)
            _store_m3a_delta(conn, run_id, delta_rows)
            _store_m3_buckets(conn, run_id, bucket_rows)
            _store_m3_delta(conn, run_id, delta_rows)
            _store_m3b_buckets(conn, run_id, m3b_bucket_rows)
            _store_m3b_delta(conn, run_id, m3b_rows)
            _store_normalized(conn, run_id, normalized_rows)
            _store_m3ab_normalized(conn, run_id, m3ab_rows)
            _store_manifest(
                conn,
                {
                    "package_id": "P0035",
                    "schema_version": SCHEMA_VERSION,
                    "m1_version": M1_VERSION,
                    "m2_version": M2_VERSION,
                    "m3a_version": M3A_VERSION,
                    "m3b_version": M3B_VERSION,
                    "price_db": str(price_path),
                    "weather_db": str(weather_path),
                    "feature_db": str(feature_path),
                    "calendar_csv": str(Path(calendar_csv)),
                    "start_date": str(rows[0]["local_date"]),
                    "end_date": actual_end,
                    "row_count": str(len(rows)),
                    "m4_m5_m6_m7": "deferred",
                    "device_access": "none",
                },
            )
            conn.execute(
                "UPDATE model_runs SET completed_at=?, status='ok', row_count=?, message=? WHERE run_id=?",
                (_now(), len(rows), "P0033 build complete", run_id),
            )
            summary = validate_training_foundation(conn)
            summary["run_id"] = run_id
            summary["feature_db"] = str(feature_path)
            return summary
        except Exception as exc:
            conn.execute(
                "UPDATE model_runs SET completed_at=?, status='failed', message=? WHERE run_id=?",
                (_now(), str(exc), run_id),
            )
            raise


def validate_training_foundation(conn: sqlite3.Connection) -> dict[str, object]:
    required = (
        "model_runs",
        "calendar_special_days",
        "m1_normal_price_v1",
        "m2_climate_normals",
        "m2_climate_anomalies",
        "m2_climate_weights",
        "m3a_temperature_delta",
        "m3a_temperature_delta_buckets",
        "m3_temperature_delta_v1",
        "m3_temperature_delta_buckets",
        "m3b_special_day_delta",
        "m3b_special_day_delta_buckets",
        "m3ab_normalized_prices",
        "m3_temp_normalized_prices_v1",
        "training_foundation_manifest",
    )
    counts = {table: _count(conn, table) for table in required}
    coverage = conn.execute(
        """
        SELECT MIN(local_date) AS start_date, MAX(local_date) AS end_date, COUNT(*) AS row_count
        FROM m3_temp_normalized_prices_v1
        """
    ).fetchone()
    normalized_count = int(coverage["row_count"] or 0)
    expected_multi = {
        "m1_normal_price_v1": normalized_count * 2,
        "m2_climate_normals": normalized_count * len(_all_m2_signals()),
        "m2_climate_anomalies": normalized_count * len(_all_m2_signals()),
        "m3a_temperature_delta": normalized_count * 2,
        "m3_temperature_delta_v1": normalized_count * 2,
        "m3b_special_day_delta": normalized_count * 2,
        "m3ab_normalized_prices": normalized_count,
        "m3_temp_normalized_prices_v1": normalized_count,
    }
    missing = [table for table in required if counts[table] == 0]
    mismatches = {
        table: {"actual": counts[table], "expected": expected}
        for table, expected in expected_multi.items()
        if counts[table] != expected
    }
    return {
        "ok": not missing and not mismatches and normalized_count > 0,
        "start_date": coverage["start_date"],
        "end_date": coverage["end_date"],
        "row_count": normalized_count,
        "table_counts": counts,
        "missing_tables": missing,
        "count_mismatches": mismatches,
    }


def summarize_temperature_normalization(conn: sqlite3.Connection) -> dict[str, object]:
    summary: dict[str, object] = {
        "validation": validate_training_foundation(conn),
        "m1_residuals": {},
        "m2_anomalies": {},
        "m3_deltas": {},
        "temperature_association": {},
        "bucket_residuals": {},
    }
    for target, actual_column, normal_column, normalized_column, delta_column in (
        (
            "system_proxy_se1",
            "actual_se1",
            "normal_price_v1_se1",
            "temp_normalized_price_v1_se1",
            "temp_delta_v1_se1",
        ),
        (
            "area_diff_proxy_se3",
            "actual_area_diff",
            "normal_price_v1_area_diff",
            "temp_normalized_area_diff_v1",
            "temp_delta_v1_area_diff",
        ),
    ):
        residuals = [
            float(row["residual"])
            for row in conn.execute(
                f"SELECT {actual_column} - {normal_column} AS residual FROM m3_temp_normalized_prices_v1"
            )
        ]
        normalized_residuals = [
            float(row["residual"])
            for row in conn.execute(
                f"SELECT {normalized_column} - {normal_column} AS residual FROM m3_temp_normalized_prices_v1"
            )
        ]
        deltas = [float(row[delta_column]) for row in conn.execute(f"SELECT {delta_column} FROM m3_temp_normalized_prices_v1")]
        signal = M3_PRIMARY_ANOMALY_SIGNAL[target]
        anomalies = [
            float(row["anomaly_value"])
            for row in conn.execute(
                "SELECT anomaly_value FROM m2_climate_anomalies WHERE signal=? ORDER BY utc_hour_start",
                (signal,),
            )
        ]
        summary["m1_residuals"][target] = _stats(residuals)
        summary["m3_deltas"][target] = _stats(deltas)
        summary["temperature_association"][target] = {
            "anomaly_signal": signal,
            "before_corr": _pearson(anomalies, residuals),
            "after_corr": _pearson(anomalies, normalized_residuals),
        }
    for signal in _all_m2_signals():
        values = [
            float(row["anomaly_value"])
            for row in conn.execute("SELECT anomaly_value FROM m2_climate_anomalies WHERE signal=?", (signal,))
        ]
        summary["m2_anomalies"][signal] = _stats(values)
    bucket_rows = conn.execute(
        """
        SELECT target, bucket, sample_count, median_residual, smoothed_delta
        FROM m3_temperature_delta_buckets
        ORDER BY target, bucket
        """
    ).fetchall()
    for row in bucket_rows:
        summary["bucket_residuals"][f"{row['target']}:{row['bucket']}"] = _dict(row)
    return summary


def _add_climate_signals(row: dict[str, object]) -> None:
    for signal, parts in SE1_SYSTEM_SIGNALS.items():
        row[signal] = sum(float(row[field]) * weight for field, weight in parts)


def _all_m2_signals() -> tuple[str, ...]:
    return (*SE1_SYSTEM_SIGNALS.keys(), *AREA_DIFF_SIGNALS)


def _store_weights(conn: sqlite3.Connection, run_id: int) -> None:
    conn.executemany(
        """
        INSERT INTO m2_climate_weights (target, input_signal, weight, rationale, run_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (row["target"], row["input_signal"], row["weight"], row["rationale"], run_id)
            for row in select_m2_target_weights()
        ],
    )


def _store_calendar(conn: sqlite3.Connection, rows: dict[str, dict[str, object]]) -> None:
    conn.execute("DELETE FROM calendar_special_days")
    conn.executemany(
        """
        INSERT INTO calendar_special_days
        (local_date, special_day_type, special_day_name, special_day_group, holiday_strength,
         is_public_holiday, is_major_social_holiday, is_holiday_eve, is_bridge_day,
         bridge_strength, bridge_anchor, is_holiday_period_day, period_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["date"],
                row["special_day_type"],
                row["special_day_name"],
                row["special_day_group"],
                row["holiday_strength"],
                1 if row["is_public_holiday"] else 0,
                1 if row["is_major_social_holiday"] else 0,
                1 if row["is_holiday_eve"] else 0,
                1 if row["is_bridge_day"] else 0,
                row["bridge_strength"],
                row["bridge_anchor"],
                1 if row["is_holiday_period_day"] else 0,
                row["period_name"],
            )
            for row in rows.values()
        ],
    )


def _store_m1(conn: sqlite3.Connection, run_id: int, rows: Iterable[dict[str, object]]) -> None:
    conn.executemany(
        """
        INSERT INTO m1_normal_price_v1
        (target, utc_hour_start, local_date, local_hour, iso_week, weekday, normal_price, sample_count, bucket_year_count, method, run_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["target"],
                row["utc_hour_start"],
                row["local_date"],
                row["local_hour"],
                row["iso_week"],
                row["weekday"],
                row["normal_price"],
                row["sample_count"],
                row["bucket_year_count"],
                row["method"],
                run_id,
            )
            for row in rows
        ],
    )


def _store_m2_normals(conn: sqlite3.Connection, run_id: int, rows: Iterable[dict[str, object]]) -> None:
    conn.executemany(
        """
        INSERT INTO m2_climate_normals
        (signal, utc_hour_start, local_date, local_hour, day_of_year, normal_value, sample_count, bucket_year_count, method, run_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["signal"],
                row["utc_hour_start"],
                row["local_date"],
                row["local_hour"],
                row["day_of_year"],
                row["normal_value"],
                row["sample_count"],
                row["bucket_year_count"],
                row["method"],
                run_id,
            )
            for row in rows
        ],
    )


def _store_m2_anomalies(conn: sqlite3.Connection, run_id: int, rows: Iterable[dict[str, object]]) -> None:
    conn.executemany(
        """
        INSERT INTO m2_climate_anomalies
        (signal, utc_hour_start, local_date, local_hour, actual_value, normal_value, anomaly_value, run_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["signal"],
                row["utc_hour_start"],
                row["local_date"],
                row["local_hour"],
                row["actual_value"],
                row["normal_value"],
                row["anomaly_value"],
                run_id,
            )
            for row in rows
        ],
    )


def _store_m3_buckets(conn: sqlite3.Connection, run_id: int, rows: Iterable[dict[str, object]]) -> None:
    conn.executemany(
        """
        INSERT INTO m3_temperature_delta_buckets
        (target, anomaly_signal, bucket, sample_count, median_residual, smoothed_delta, run_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["target"],
                row["anomaly_signal"],
                row["bucket"],
                row["sample_count"],
                row["median_residual"],
                row["smoothed_delta"],
                run_id,
            )
            for row in rows
        ],
    )


def _store_m3_delta(conn: sqlite3.Connection, run_id: int, rows: Iterable[dict[str, object]]) -> None:
    conn.executemany(
        """
        INSERT INTO m3_temperature_delta_v1
        (target, utc_hour_start, local_date, local_hour, anomaly_signal, anomaly_value, bucket, temp_delta, run_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["target"],
                row["utc_hour_start"],
                row["local_date"],
                row["local_hour"],
                row["anomaly_signal"],
                row["anomaly_value"],
                row["bucket"],
                row["temp_delta"],
                run_id,
            )
            for row in rows
        ],
    )


def _store_m3a_buckets(conn: sqlite3.Connection, run_id: int, rows: Iterable[dict[str, object]]) -> None:
    conn.executemany(
        """
        INSERT INTO m3a_temperature_delta_buckets
        (target, anomaly_signal, bucket, sample_count, median_residual, smoothed_delta, run_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["target"],
                row["anomaly_signal"],
                row["bucket"],
                row["sample_count"],
                row["median_residual"],
                row["smoothed_delta"],
                run_id,
            )
            for row in rows
        ],
    )


def _store_m3a_delta(conn: sqlite3.Connection, run_id: int, rows: Iterable[dict[str, object]]) -> None:
    conn.executemany(
        """
        INSERT INTO m3a_temperature_delta
        (target, utc_hour_start, local_date, local_hour, anomaly_signal, anomaly_value, bucket, temp_delta, run_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["target"],
                row["utc_hour_start"],
                row["local_date"],
                row["local_hour"],
                row["anomaly_signal"],
                row["anomaly_value"],
                row["bucket"],
                row["temp_delta"],
                run_id,
            )
            for row in rows
        ],
    )


def _store_m3b_buckets(conn: sqlite3.Connection, run_id: int, rows: Iterable[dict[str, object]]) -> None:
    conn.executemany(
        """
        INSERT INTO m3b_special_day_delta_buckets
        (target, special_day_type, special_day_name, special_day_group, bridge_anchor,
         sample_count, median_residual, model_delta, shrinkage_factor, run_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["target"],
                row["special_day_type"],
                row["special_day_name"],
                row["special_day_group"],
                row["bridge_anchor"],
                row["sample_count"],
                row["median_residual"],
                row["model_delta"],
                row["shrinkage_factor"],
                run_id,
            )
            for row in rows
        ],
    )


def _store_m3b_delta(conn: sqlite3.Connection, run_id: int, rows: Iterable[dict[str, object]]) -> None:
    conn.executemany(
        """
        INSERT INTO m3b_special_day_delta
        (target, utc_hour_start, local_date, local_hour, special_day_type, special_day_name,
         special_day_group, bridge_anchor, holiday_strength, model_delta, sample_count,
         shrinkage_factor, run_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["target"],
                row["utc_hour_start"],
                row["local_date"],
                row["local_hour"],
                row["special_day_type"],
                row["special_day_name"],
                row["special_day_group"],
                row["bridge_anchor"],
                row["holiday_strength"],
                row["model_delta"],
                row["sample_count"],
                row["shrinkage_factor"],
                run_id,
            )
            for row in rows
        ],
    )


def _store_normalized(conn: sqlite3.Connection, run_id: int, rows: Iterable[dict[str, object]]) -> None:
    conn.executemany(
        """
        INSERT INTO m3_temp_normalized_prices_v1
        (
          utc_hour_start, local_date, local_hour, actual_se1, actual_area_diff, actual_se3,
          normal_price_v1_se1, normal_price_v1_area_diff,
          temp_delta_v1_se1, temp_delta_v1_area_diff,
          temp_normalized_price_v1_se1, temp_normalized_area_diff_v1,
          temp_normalized_price_v1_se3, run_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["utc_hour_start"],
                row["local_date"],
                row["local_hour"],
                row["actual_se1"],
                row["actual_area_diff"],
                row["actual_se3"],
                row["normal_price_v1_se1"],
                row["normal_price_v1_area_diff"],
                row["temp_delta_v1_se1"],
                row["temp_delta_v1_area_diff"],
                row["temp_normalized_price_v1_se1"],
                row["temp_normalized_area_diff_v1"],
                row["temp_normalized_price_v1_se3"],
                run_id,
            )
            for row in rows
        ],
    )


def _store_m3ab_normalized(conn: sqlite3.Connection, run_id: int, rows: Iterable[dict[str, object]]) -> None:
    conn.executemany(
        """
        INSERT INTO m3ab_normalized_prices
        (
          utc_hour_start, local_date, local_hour, actual_se1, actual_area_diff, actual_se3,
          normal_price_v1_se1, normal_price_v1_area_diff,
          m3a_temperature_delta_se1, m3a_temperature_delta_area_diff,
          m3b_special_day_delta_se1, m3b_special_day_delta_area_diff,
          m3ab_normalized_price_se1, m3ab_normalized_area_diff, m3ab_normalized_se3,
          special_day_type, special_day_name, special_day_group, is_special_day, run_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["utc_hour_start"],
                row["local_date"],
                row["local_hour"],
                row["actual_se1"],
                row["actual_area_diff"],
                row["actual_se3"],
                row["normal_price_v1_se1"],
                row["normal_price_v1_area_diff"],
                row["m3a_temperature_delta_se1"],
                row["m3a_temperature_delta_area_diff"],
                row["m3b_special_day_delta_se1"],
                row["m3b_special_day_delta_area_diff"],
                row["m3ab_normalized_price_se1"],
                row["m3ab_normalized_area_diff"],
                row["m3ab_normalized_se3"],
                row["special_day_type"],
                row["special_day_name"],
                row["special_day_group"],
                row["is_special_day"],
                run_id,
            )
            for row in rows
        ],
    )


def _store_manifest(conn: sqlite3.Connection, values: dict[str, str]) -> None:
    conn.executemany(
        "INSERT OR REPLACE INTO training_foundation_manifest(key, value) VALUES (?, ?)",
        sorted(values.items()),
    )


def _clear_generated_tables(conn: sqlite3.Connection) -> None:
    for table in (
        "calendar_special_days",
        "m1_normal_price_v1",
        "m2_climate_weights",
        "m2_climate_normals",
        "m2_climate_anomalies",
        "m3a_temperature_delta_buckets",
        "m3a_temperature_delta",
        "m3_temperature_delta_buckets",
        "m3_temperature_delta_v1",
        "m3b_special_day_delta_buckets",
        "m3b_special_day_delta",
        "m3ab_normalized_prices",
        "m3_temp_normalized_prices_v1",
        "training_foundation_manifest",
    ):
        conn.execute(f"DELETE FROM {table}")


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {str(row["name"]) for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _create_run(
    conn: sqlite3.Connection,
    price_db: Path,
    weather_db: Path,
    start_date: date,
    end_date: str,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO model_runs (started_at, status, price_db, weather_db, start_date, end_date)
        VALUES (?, 'running', ?, ?, ?, ?)
        """,
        (_now(), str(price_db), str(weather_db), start_date.isoformat(), end_date),
    )
    return int(cursor.lastrowid)


def _count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"])


def _stats(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "min": None, "max": None, "mean": None, "stddev": None}
    mean = sum(values) / len(values)
    var = sum((value - mean) ** 2 for value in values) / len(values)
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": mean,
        "stddev": math.sqrt(var),
    }


def _pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_den = math.sqrt(sum((a - left_mean) ** 2 for a in left))
    right_den = math.sqrt(sum((b - right_mean) ** 2 for b in right))
    if left_den == 0 or right_den == 0:
        return None
    return numerator / (left_den * right_den)


def _week_distance(left: int, right: int) -> int:
    direct = abs(left - right)
    return min(direct, 53 - direct)


def _day_distance(left: int, right: int) -> int:
    direct = abs(left - right)
    return min(direct, 366 - direct)


def _sqlite_to_monday_weekday(sqlite_weekday: int) -> int:
    return 6 if sqlite_weekday == 0 else sqlite_weekday - 1


def _detach_if_present(conn: sqlite3.Connection, schema: str) -> None:
    rows = conn.execute("PRAGMA database_list").fetchall()
    if any(row["name"] == schema for row in rows):
        conn.execute(f"DETACH DATABASE {schema}")


def _dict(row: sqlite3.Row) -> dict[str, object]:
    return {key: row[key] for key in row.keys()}


def _calendar_row(row: dict[str, str]) -> dict[str, object]:
    return {
        "date": row["date"],
        "special_day_type": row["special_day_type"],
        "special_day_name": row["special_day_name"],
        "special_day_group": row["special_day_group"],
        "bridge_anchor": row.get("bridge_anchor", ""),
        "bridge_strength": row.get("bridge_strength", ""),
        "holiday_strength": float(row.get("holiday_strength") or 0.0),
        "is_public_holiday": _csv_bool(row.get("is_public_holiday", "")),
        "is_major_social_holiday": _csv_bool(row.get("is_major_social_holiday", "")),
        "is_holiday_eve": _csv_bool(row.get("is_holiday_eve", "")),
        "is_bridge_day": _csv_bool(row.get("is_bridge_day", "")),
        "is_holiday_period_day": _csv_bool(row.get("is_holiday_period_day", "")),
        "period_name": row.get("period_name", ""),
    }


def _normal_calendar(local_date: str) -> dict[str, object]:
    return {
        "date": local_date,
        "special_day_type": "normal_weekday",
        "special_day_name": "normal_weekday",
        "special_day_group": "normal",
        "bridge_anchor": "",
        "bridge_strength": "",
        "holiday_strength": 0.0,
        "is_public_holiday": False,
        "is_major_social_holiday": False,
        "is_holiday_eve": False,
        "is_bridge_day": False,
        "is_holiday_period_day": False,
        "period_name": "",
    }


def _is_special_calendar_day(row: dict[str, object]) -> bool:
    return str(row["special_day_group"]) != "normal" or bool(row["is_bridge_day"]) or bool(row["is_holiday_period_day"])


def _m3b_bucket_key(target: str, calendar: dict[str, object]) -> tuple[str, str, str, str, str]:
    if not _is_special_calendar_day(calendar):
        return (target, "normal", "normal", "normal", "")
    return (
        target,
        str(calendar["special_day_type"]),
        str(calendar["special_day_name"]),
        str(calendar["special_day_group"]),
        str(calendar["bridge_anchor"]),
    )


def _csv_bool(value: str) -> bool:
    return str(value).strip().lower() in ("1", "true", "yes")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
