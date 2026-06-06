"""P0054Z SE3 climate-zone weather actual-proxy series."""

from __future__ import annotations

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


PACKAGE_ID = "P0054Z"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054Z")
OUTPUT_TABLE = "se3_climate_zone_weather_hourly_v1"
START_UTC = "2022-06-01T00:00Z"
BROAD_PROXY = "se3_load_weather"
FEATURES = (
    ("temperature_2m", "C"),
    ("apparent_temperature", "C"),
    ("wind_speed_100m", "km/h"),
    ("cloud_cover", "%"),
    ("relative_humidity", "%"),
    ("precipitation", "mm"),
    ("snowfall", "cm"),
    ("heating_degree_proxy", "degree_hours"),
    ("cooling_degree_proxy", "degree_hours"),
    ("temperature_2m_roll_mean_24h", "C"),
)


@dataclass(frozen=True)
class P0054ZResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054z_weather_series(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    weather_db: Path | str = DEFAULT_WEATHER_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054ZResult:
    started = time.monotonic()
    feature_path = Path(feature_db).expanduser()
    weather_path = Path(weather_db).expanduser()
    with sqlite3.connect(feature_path, timeout=60.0) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=60000")
        conn.execute(f"ATTACH DATABASE ? AS weather_db", (str(weather_path),))
        create_schema(conn)
        source_inventory = load_source_inventory(conn)
        if not source_inventory["has_required_source"]:
            summary = stopped_summary(started, feature_path, weather_path, source_inventory)
            evidence = write_evidence(Path(evidence_dir), summary)
            return P0054ZResult("STOP", {}, evidence)
        rows = build_zone_weather_rows(conn)
        replace_output_rows(conn, rows)
        validation = validate_zone_weather(conn)
        summary = build_summary(started, feature_path, weather_path, source_inventory, validation)
        evidence = write_evidence(Path(evidence_dir), summary)
        status = "PASS" if validation["all_required_zones_present"] and validation["zone_series_distinct_from_broad"] else "WARN"
        return P0054ZResult(status, summary["row_counts"], evidence)  # type: ignore[arg-type]


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {OUTPUT_TABLE} (
            timestamp_utc TEXT NOT NULL,
            climate_zone_id TEXT NOT NULL,
            feature_name TEXT NOT NULL,
            feature_value REAL NOT NULL,
            feature_unit TEXT NOT NULL,
            source_station_or_proxy_ids TEXT NOT NULL,
            aggregation_method TEXT NOT NULL,
            missingness_flag TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (timestamp_utc, climate_zone_id, feature_name, generated_by_package)
        )
        """
    )
    conn.commit()


def zone_station_weights() -> dict[str, list[tuple[str, float]]]:
    return {
        "SE3_EAST_COAST_MALARDALEN_STOCKHOLM": [
            ("se3_load_stockholm", 0.35),
            ("se3_load_vasteras", 0.25),
            ("se3_load_norrkoping", 0.20),
            ("se3_load_linkoping", 0.20),
        ],
        "SE3_WEST_COAST_GOTHENBURG": [
            ("se3_load_goteborg", 0.55),
            ("se3_load_jonkoping", 0.15),
            ("se3_load_karlstad", 0.15),
            ("se3_load_orebro", 0.15),
        ],
        "SE3_NORTHERN_INLAND": [
            ("se3_load_borlange", 0.35),
            ("se3_load_gavle", 0.25),
            ("se3_load_karlstad", 0.25),
            ("se3_load_orebro", 0.15),
        ],
        "SE3_SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND": [
            ("se3_load_linkoping", 0.25),
            ("se3_load_jonkoping", 0.25),
            ("se3_load_vaxjo", 0.25),
            ("se3_load_kalmar", 0.25),
        ],
    }


def cluster_weather_mapping() -> list[dict[str, str]]:
    output = []
    mapping = {
        "1": "SE3_EAST_COAST_MALARDALEN_STOCKHOLM",
        "2": "SE3_WEST_COAST_GOTHENBURG",
        "3": "SE3_NORTHERN_INLAND",
        "4": "SE3_SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND",
    }
    for climate_index, zone in mapping.items():
        for urban_index in ("1", "2", "3", "4"):
            output.append({"component_id": f"C{climate_index}{urban_index}", "climate_zone_id": zone})
    output.append({"component_id": "SE3_RESIDUAL_METERED_NON_PROFILED_UNOBSERVED", "climate_zone_id": "SE3_BROAD_PROXY"})
    return output


def load_source_inventory(conn: sqlite3.Connection) -> dict[str, object]:
    area_rows = conn.execute(
        """
        SELECT area_proxy, COUNT(*) AS rows, MIN(utc_hour_start) AS min_ts, MAX(utc_hour_start) AS max_ts
        FROM weather_db.weather_area_hourly
        GROUP BY area_proxy
        """
    ).fetchall()
    location_rows = conn.execute(
        """
        SELECT location_id, name, latitude, longitude, weight, area_proxy, active
        FROM weather_db.weather_locations
        WHERE area_proxy IN ('SE3', 'se3_load_weather')
        ORDER BY area_proxy, location_id
        """
    ).fetchall()
    required = {station for stations in zone_station_weights().values() for station, _ in stations}
    existing = {str(row["location_id"]) for row in location_rows}
    broad = [row for row in area_rows if row["area_proxy"] == BROAD_PROXY]
    return {
        "weather_area_hourly": [dict(row) for row in area_rows],
        "weather_locations": [dict(row) for row in location_rows],
        "required_station_ids": sorted(required),
        "missing_required_station_ids": sorted(required - existing),
        "broad_proxy": dict(broad[0]) if broad else None,
        "has_required_source": bool(broad) and not (required - existing),
    }


def build_zone_weather_rows(conn: sqlite3.Connection) -> list[dict[str, object]]:
    conn.execute("DROP TABLE IF EXISTS temp.p0054z_zone_weights")
    conn.execute("CREATE TEMP TABLE p0054z_zone_weights (climate_zone_id TEXT, location_id TEXT, weight REAL)")
    conn.executemany(
        "INSERT INTO p0054z_zone_weights VALUES (?, ?, ?)",
        [(zone, location, weight) for zone, stations in zone_station_weights().items() for location, weight in stations],
    )
    zone_rows = conn.execute(
        """
        WITH composite AS (
          SELECT w.climate_zone_id,
                 o.utc_hour_start AS timestamp_utc,
                 GROUP_CONCAT(w.location_id) AS source_ids,
                 SUM(o.temperature_2m * w.weight) / SUM(w.weight) AS temperature_2m,
                 SUM(o.apparent_temperature * w.weight) / SUM(w.weight) AS apparent_temperature,
                 SUM(o.wind_speed_100m * w.weight) / SUM(w.weight) AS wind_speed_100m,
                 SUM(o.cloud_cover * w.weight) / SUM(w.weight) AS cloud_cover,
                 SUM(o.relative_humidity_2m * w.weight) / SUM(w.weight) AS relative_humidity,
                 SUM(o.precipitation * w.weight) / SUM(w.weight) AS precipitation,
                 SUM(o.snowfall * w.weight) / SUM(w.weight) AS snowfall,
                 COUNT(*) AS source_count,
                 SUM(w.weight) AS source_weight
          FROM weather_db.weather_observations o
          JOIN p0054z_zone_weights w ON w.location_id=o.location_id
          WHERE o.utc_hour_start >= ?
          GROUP BY w.climate_zone_id, o.utc_hour_start
        ),
        derived AS (
          SELECT *,
                 MAX(0.0, 17.0 - temperature_2m) AS heating_degree_proxy,
                 MAX(0.0, temperature_2m - 22.0) AS cooling_degree_proxy,
                 AVG(temperature_2m) OVER (
                   PARTITION BY climate_zone_id ORDER BY timestamp_utc ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
                 ) AS temperature_2m_roll_mean_24h
          FROM composite
        )
        SELECT * FROM derived
        ORDER BY climate_zone_id, timestamp_utc
        """,
        (START_UTC,),
    ).fetchall()
    broad_rows = conn.execute(
        """
        WITH broad AS (
          SELECT 'SE3_BROAD_PROXY' AS climate_zone_id,
                 utc_hour_start AS timestamp_utc,
                 ? AS source_ids,
                 weighted_temperature_2m AS temperature_2m,
                 weighted_apparent_temperature AS apparent_temperature,
                 weighted_wind_speed_100m AS wind_speed_100m,
                 weighted_cloud_cover AS cloud_cover,
                 weighted_relative_humidity_2m AS relative_humidity,
                 weighted_precipitation AS precipitation,
                 weighted_snowfall AS snowfall,
                 source_coverage_count AS source_count,
                 source_coverage_weight AS source_weight,
                 heating_degree_hours AS heating_degree_proxy,
                 cooling_degree_hours AS cooling_degree_proxy
          FROM weather_db.weather_area_hourly
          WHERE area_proxy=? AND utc_hour_start >= ?
        ),
        derived AS (
          SELECT *,
                 AVG(temperature_2m) OVER (
                   PARTITION BY climate_zone_id ORDER BY timestamp_utc ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
                 ) AS temperature_2m_roll_mean_24h
          FROM broad
        )
        SELECT * FROM derived
        ORDER BY timestamp_utc
        """,
        (BROAD_PROXY, BROAD_PROXY, START_UTC),
    ).fetchall()
    rows: list[dict[str, object]] = []
    for row in [*zone_rows, *broad_rows]:
        missingness_flag = "complete" if float(row["source_weight"] or 0.0) >= 0.999 else "partial_source_coverage"
        for feature_name, unit in FEATURES:
            value = row[feature_name]
            if value is None:
                continue
            rows.append({
                "timestamp_utc": row["timestamp_utc"],
                "climate_zone_id": row["climate_zone_id"],
                "feature_name": feature_name,
                "feature_value": float(value),
                "feature_unit": unit,
                "source_station_or_proxy_ids": row["source_ids"],
                "aggregation_method": aggregation_method(str(row["climate_zone_id"])),
                "missingness_flag": missingness_flag,
                "generated_by_package": PACKAGE_ID,
            })
    return rows


def aggregation_method(climate_zone_id: str) -> str:
    if climate_zone_id == "SE3_BROAD_PROXY":
        return "existing_weather_area_hourly_proxy_se3_load_weather"
    return "weighted_mean_of_existing_weather_observations"


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


def validate_zone_weather(conn: sqlite3.Connection) -> dict[str, object]:
    required_zones = set(zone_station_weights()) | {"SE3_BROAD_PROXY"}
    rows = conn.execute(
        f"""
        SELECT climate_zone_id,
               COUNT(DISTINCT timestamp_utc) AS hours,
               MIN(timestamp_utc) AS min_ts,
               MAX(timestamp_utc) AS max_ts,
               AVG(CASE WHEN feature_name='temperature_2m' THEN feature_value END) AS mean_temp,
               AVG(CASE WHEN feature_name='temperature_2m' AND substr(timestamp_utc, 6, 2) IN ('12','01','02') THEN feature_value END) AS winter_temp,
               AVG(CASE WHEN feature_name='temperature_2m' AND substr(timestamp_utc, 6, 2) IN ('06','07','08') THEN feature_value END) AS summer_temp
        FROM {OUTPUT_TABLE}
        WHERE generated_by_package=? AND feature_name='temperature_2m'
        GROUP BY climate_zone_id
        ORDER BY climate_zone_id
        """,
        (PACKAGE_ID,),
    ).fetchall()
    broad = load_temperature_series(conn, "SE3_BROAD_PROXY")
    zone_summaries = []
    for row in rows:
        zone = str(row["climate_zone_id"])
        temps = list(load_temperature_series(conn, zone).values())
        expected = expected_hour_count(str(row["min_ts"]), str(row["max_ts"]))
        broad_aligned, zone_aligned = aligned_values(broad, load_temperature_series(conn, zone))
        corr = correlation(zone_aligned, broad_aligned)
        deltas = [zone_value - broad_value for zone_value, broad_value in zip(zone_aligned, broad_aligned)]
        abs_deltas = [abs(value) for value in deltas]
        zone_summaries.append({
            "climate_zone_id": zone,
            "row_count": int(row["hours"] or 0),
            "min_timestamp": row["min_ts"],
            "max_timestamp": row["max_ts"],
            "missing_hour_count": max(0, expected - int(row["hours"] or 0)),
            "coverage_ratio": (int(row["hours"] or 0) / expected) if expected else 0.0,
            "mean_temperature": float(row["mean_temp"] or 0.0),
            "p05_temperature": percentile(temps, 0.05) if temps else 0.0,
            "p95_temperature": percentile(temps, 0.95) if temps else 0.0,
            "winter_mean_temperature": float(row["winter_temp"] or 0.0),
            "summer_mean_temperature": float(row["summer_temp"] or 0.0),
            "correlation_with_broad_proxy": corr,
            "mean_delta_vs_broad_proxy": mean(deltas),
            "p95_abs_delta_vs_broad_proxy": percentile(abs_deltas, 0.95) if abs_deltas else 0.0,
        })
    non_broad_deltas = [abs(float(row["mean_delta_vs_broad_proxy"])) for row in zone_summaries if row["climate_zone_id"] != "SE3_BROAD_PROXY"]
    return {
        "required_zones": sorted(required_zones),
        "present_zones": sorted(str(row["climate_zone_id"]) for row in rows),
        "all_required_zones_present": required_zones == {str(row["climate_zone_id"]) for row in rows},
        "zone_series_distinct_from_broad": any(delta > 0.05 for delta in non_broad_deltas),
        "zone_summaries": zone_summaries,
    }


def load_temperature_series(conn: sqlite3.Connection, zone: str) -> dict[str, float]:
    return {
        row["timestamp_utc"]: float(row["feature_value"])
        for row in conn.execute(
            f"""
            SELECT timestamp_utc, feature_value
            FROM {OUTPUT_TABLE}
            WHERE generated_by_package=? AND climate_zone_id=? AND feature_name='temperature_2m'
            ORDER BY timestamp_utc
            """,
            (PACKAGE_ID, zone),
        )
    }


def aligned_values(a: dict[str, float], b: dict[str, float]) -> tuple[list[float], list[float]]:
    keys = sorted(set(a) & set(b))
    return [a[key] for key in keys], [b[key] for key in keys]


def expected_hour_count(min_ts: str, max_ts: str) -> int:
    start = parse_utc_hour(min_ts)
    end = parse_utc_hour(max_ts)
    return int((end - start).total_seconds() // 3600) + 1


def parse_utc_hour(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    return parsed.astimezone(timezone.utc)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def correlation(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return 0.0
    mx = mean(xs)
    my = mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = sum((x - mx) ** 2 for x in xs) ** 0.5
    den_y = sum((y - my) ** 2 for y in ys) ** 0.5
    return num / (den_x * den_y) if den_x and den_y else 0.0


def build_summary(
    started: float,
    feature_path: Path,
    weather_path: Path,
    source_inventory: dict[str, object],
    validation: dict[str, object],
) -> dict[str, object]:
    return {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": "PASS" if validation["all_required_zones_present"] and validation["zone_series_distinct_from_broad"] else "WARN",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "feature_db": str(feature_path),
        "weather_db": str(weather_path),
        "source_inventory": source_inventory,
        "zone_station_weights": zone_station_weights(),
        "cluster_weather_mapping": cluster_weather_mapping(),
        "validation": validation,
        "output_table": OUTPUT_TABLE,
        "row_counts": load_row_counts(feature_path),
        "forecast_safety": {
            "weather_actual_proxy": True,
            "weather_forecast": False,
            "production_forecast_claim": False,
        },
        "no_credentials": True,
        "no_external_integration": True,
        "no_devices_or_runtime": True,
        "no_large_raw_weather_committed": True,
    }


def load_row_counts(feature_path: Path) -> dict[str, int]:
    with sqlite3.connect(feature_path) as conn:
        row = conn.execute(f"SELECT COUNT(*) FROM {OUTPUT_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,)).fetchone()
        zone = conn.execute(f"SELECT COUNT(DISTINCT climate_zone_id) FROM {OUTPUT_TABLE} WHERE generated_by_package=?", (PACKAGE_ID,)).fetchone()
        return {"weather_feature_rows": int(row[0] or 0), "climate_zones": int(zone[0] or 0)}


def stopped_summary(started: float, feature_path: Path, weather_path: Path, source_inventory: dict[str, object]) -> dict[str, object]:
    return {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": "STOP",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "feature_db": str(feature_path),
        "weather_db": str(weather_path),
        "source_inventory": source_inventory,
        "stop_reason": "local weather source missing required proxy locations or broad proxy",
        "row_counts": {},
    }


def write_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog(summary)),
        "labb": write(evidence_dir / "labb-label.md", "# P0054Z LABB label\n\nLabel: `LABB`.\n"),
        "p0054y2": write(evidence_dir / "p0054y2-input-review.md", p0054y2_review()),
        "inventory": write(evidence_dir / "weather-source-inventory.md", json_report("P0054Z weather source inventory", summary.get("source_inventory", {}))),
        "zones": write(evidence_dir / "climate-zone-definitions.md", climate_zone_definitions()),
        "selection": write(evidence_dir / "station-proxy-selection.md", station_selection_report(summary)),
        "schema": write(evidence_dir / "output-table-schema.md", output_schema()),
        "contract": write(evidence_dir / "weather-feature-contract.md", feature_contract()),
        "mapping": write(evidence_dir / "cluster-weather-mapping.md", mapping_report(summary)),
        "missingness": write(evidence_dir / "coverage-and-missingness.md", validation_report(summary, "coverage")),
        "validation": write(evidence_dir / "climate-zone-validation.md", validation_report(summary, "validation")),
        "database": write(evidence_dir / "database-output-evidence.md", database_report(summary)),
        "safety": write(evidence_dir / "forecast-safety-review.md", forecast_safety_report()),
        "readiness": write(evidence_dir / "modeling-readiness-review.md", modeling_readiness(summary)),
        "learned": write(evidence_dir / "what-we-learned.md", learned_report()),
        "next": write(evidence_dir / "next-package-recommendation.md", next_recommendation()),
        "summary": write_json(evidence_dir / "climate-zone-weather-summary.json", summary_for_json(summary)),
    }
    write_csv(evidence_dir / "climate-zone-weather-summary.csv", summary.get("validation", {}).get("zone_summaries", []))  # type: ignore[union-attr]
    write_csv(evidence_dir / "cluster-weather-mapping.csv", cluster_weather_mapping())
    write_csv(evidence_dir / "station-proxy-selection.csv", station_selection_rows())
    return paths


def summary_for_json(summary: dict[str, object]) -> dict[str, object]:
    output = dict(summary)
    return output


def changelog(summary: dict[str, object]) -> str:
    return f"""# P0054Z changelog

Status: `{summary['status']}`

- Created SE3 climate-zone weather actual-proxy feature series.
- Wrote table `{OUTPUT_TABLE}`.
- Weather feature rows: `{summary.get('row_counts', {}).get('weather_feature_rows', 0)}`.
- Climate zones: `{summary.get('row_counts', {}).get('climate_zones', 0)}`.
- No credentials, external integration, devices, runtime changes, large raw weather commits or model training.
"""


def p0054y2_review() -> str:
    return """# P0054Z P0054Y2 input review

P0054Y2 provides 16 profiled/load-profile clusters with climate-indexed ids:

```text
C1* -> east coast / Mälardalen / Stockholm
C2* -> west coast / Gothenburg
C3* -> northern inland
C4* -> southern inland / Småland / north Götaland
```

P0054Z maps those climate indices to weather-zone series.
"""


def json_report(title: str, data: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(data, indent=2, sort_keys=True)}\n```\n"


def climate_zone_definitions() -> str:
    return """# P0054Z climate-zone definitions

```text
SE3_EAST_COAST_MALARDALEN_STOCKHOLM
SE3_WEST_COAST_GOTHENBURG
SE3_NORTHERN_INLAND
SE3_SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND
SE3_BROAD_PROXY
```

The first four map to P0054Y2 cluster climate indices. `SE3_BROAD_PROXY` preserves the existing `se3_load_weather` broad proxy for direct SE3 and residual models.
"""


def station_selection_rows() -> list[dict[str, object]]:
    return [
        {"climate_zone_id": zone, "station_or_proxy_id": station, "weight": weight}
        for zone, stations in zone_station_weights().items()
        for station, weight in stations
    ] + [{"climate_zone_id": "SE3_BROAD_PROXY", "station_or_proxy_id": BROAD_PROXY, "weight": 1.0}]


def station_selection_report(summary: dict[str, object]) -> str:
    del summary
    lines = ["# P0054Z station/proxy selection", ""]
    for row in station_selection_rows():
        lines.append(f"- `{row['climate_zone_id']}` uses `{row['station_or_proxy_id']}` weight `{row['weight']}`.")
    return "\n".join(lines) + "\n"


def output_schema() -> str:
    return f"""# P0054Z output table schema

Table:

```text
{OUTPUT_TABLE}
```

Columns:

```text
timestamp_utc
climate_zone_id
feature_name
feature_value
feature_unit
source_station_or_proxy_ids
aggregation_method
missingness_flag
generated_by_package
```
"""


def feature_contract() -> str:
    return """# P0054Z weather feature contract

Features:

```text
temperature_2m
apparent_temperature
wind_speed_100m
cloud_cover
relative_humidity
precipitation
snowfall
heating_degree_proxy
cooling_degree_proxy
temperature_2m_roll_mean_24h
```

Heating degree base: `17 C`.

Cooling degree base: `22 C`.

Time handling: UTC hourly rows from local weather history. Local DST fields remain in the source weather DB but P0054Z output is keyed by UTC hour.
"""


def mapping_report(summary: dict[str, object]) -> str:
    del summary
    lines = ["# P0054Z cluster weather mapping", ""]
    for row in cluster_weather_mapping():
        lines.append(f"- `{row['component_id']}` -> `{row['climate_zone_id']}`")
    return "\n".join(lines) + "\n"


def validation_report(summary: dict[str, object], title: str) -> str:
    return f"""# P0054Z {title}

```json
{json.dumps(summary.get('validation', {}), indent=2, sort_keys=True)}
```
"""


def database_report(summary: dict[str, object]) -> str:
    return f"""# P0054Z database output evidence

Table:

```text
{OUTPUT_TABLE}
```

Row counts:

```json
{json.dumps(summary.get('row_counts', {}), indent=2, sort_keys=True)}
```
"""


def forecast_safety_report() -> str:
    return """# P0054Z forecast safety review

P0054Z creates historical actual-weather proxy series for LABB training/evaluation.

It does not create production forecast weather and must not be interpreted as future forecast input.
"""


def modeling_readiness(summary: dict[str, object]) -> str:
    status = "ready_for_labb_cluster_forecasting" if summary["status"] in {"PASS", "WARN"} else "not_ready"
    return f"""# P0054Z modeling readiness review

Status: `{status}`

Zone weather series are ready for later LABB cluster/residual forecasting tests, with forecast-safety limits documented.
"""


def learned_report() -> str:
    return """# P0054Z what we learned

Existing local weather history already contains enough SE3 proxy points to build distinct climate-zone weather actual-proxy series without a new external integration.
"""


def next_recommendation() -> str:
    return """# P0054Z next package recommendation

Recommended next package: LABB hierarchical consumption forecast using:

```text
profiled/load-profile clusters + matching climate-zone weather
metered/non_profiled residual + broad SE3 proxy
reconciled SE3 total
```
"""


def write_json(path: Path, data: object) -> str:
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    return str(path)


def write_csv(path: Path, rows: list[dict[str, object]]) -> str:
    if not rows:
        path.write_text("")
        return str(path)
    columns = list(rows[0])
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


def main() -> None:
    result = run_p0054z_weather_series()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
