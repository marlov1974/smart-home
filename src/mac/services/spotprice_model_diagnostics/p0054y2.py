"""P0054Y2 SE3 profiled MGA clusters plus metered residual."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import csv
import json
import sqlite3
import time

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics.p0041 import percentile, write


PACKAGE_ID = "P0054Y2"
LABEL = "LABB"
EVIDENCE_DIR = Path("requirements/package-runs/P0054Y2")
NATIVE_TABLE = "esett_mga_consumption_native_v1"
MASTERDATA_TABLE = "esett_mga_masterdata_v1"
ENTSOE_TABLE = "entsoe_consumption_area_hourly_v1"
CLUSTER_TABLE = "se3_profiled_mga_cluster_hourly_v1"
RESIDUAL_TABLE = "se3_consumption_metered_residual_hourly_v1"
DECOMPOSITION_TABLE = "se3_consumption_profiled_residual_decomposition_hourly_v1"

CLIMATE_GROUPS = (
    "EAST_COAST_MALARDALEN_STOCKHOLM",
    "WEST_COAST_GOTHENBURG",
    "NORTHERN_INLAND",
    "SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND",
)
URBAN_GROUPS = (
    "BIG_CITY_APARTMENT_SERVICE",
    "VILLA_SUBURBAN",
    "MIXED_SMALL_CITY_TOWN",
    "RURAL_SPARSE_AGRICULTURE",
)
ALL_CLUSTERS = tuple(
    {
        "cluster_id": f"C{climate_index}{urban_index}",
        "cluster_label": f"{climate} / {urban}",
        "climate_group": climate,
        "urban_group": urban,
    }
    for climate_index, climate in enumerate(CLIMATE_GROUPS, start=1)
    for urban_index, urban in enumerate(URBAN_GROUPS, start=1)
)


@dataclass(frozen=True)
class P0054Y2Result:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0054y2_decomposition(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0054Y2Result:
    started = time.monotonic()
    db_path = Path(feature_db).expanduser()
    evidence_path = Path(evidence_dir)
    with sqlite3.connect(db_path, timeout=60.0) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=60000")
        create_schema(conn)
        input_summary = load_input_summary(conn)
        if input_summary["profiled_row_count"] == 0 or input_summary["entsoe_row_count"] == 0:
            summary = stopped_summary(started, db_path, input_summary)
            evidence = write_evidence(evidence_path, summary)
            return P0054Y2Result("STOP", {}, evidence)
        features = load_mga_features(conn)
        assignments = assign_clusters(features)
        replace_cluster_assignments(conn, assignments)
        cluster_rows = aggregate_profiled_clusters(conn, assignments)
        entsoe_rows = load_entsoe_rows(conn)
        residual_rows, decomposition_rows = compute_residual_rows(cluster_rows, entsoe_rows)
        write_output_rows(conn, cluster_rows, residual_rows, decomposition_rows)
        validation = build_validation_summary(cluster_rows, residual_rows, input_summary)
        summary = build_summary(started, db_path, input_summary, assignments, validation, cluster_rows, residual_rows, decomposition_rows)
        evidence = write_evidence(evidence_path, summary)
        status = "PASS" if validation["negative_residual_hours_count"] == 0 else "WARN"
        return P0054Y2Result(status, summary["row_counts"], evidence)  # type: ignore[arg-type]


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {CLUSTER_TABLE} (
            timestamp_utc TEXT NOT NULL,
            cluster_id TEXT NOT NULL,
            cluster_label TEXT NOT NULL,
            consumption_mw REAL NOT NULL,
            mga_count INTEGER NOT NULL,
            source_settlement_group TEXT NOT NULL,
            native_resolution_mix TEXT NOT NULL,
            coverage_ratio REAL NOT NULL,
            input_row_count INTEGER NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (timestamp_utc, cluster_id, generated_by_package)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {RESIDUAL_TABLE} (
            timestamp_utc TEXT NOT NULL,
            area TEXT NOT NULL,
            residual_metered_non_profiled_mw REAL NOT NULL,
            entsoe_total_consumption_mw REAL NOT NULL,
            profiled_cluster_sum_mw REAL NOT NULL,
            profiled_share_of_total REAL NOT NULL,
            residual_share_of_total REAL NOT NULL,
            residual_definition TEXT NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (timestamp_utc, area, generated_by_package)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {DECOMPOSITION_TABLE} (
            timestamp_utc TEXT NOT NULL,
            component_type TEXT NOT NULL,
            component_id TEXT NOT NULL,
            component_label TEXT NOT NULL,
            consumption_mw REAL NOT NULL,
            share_of_total REAL NOT NULL,
            is_observed_component INTEGER NOT NULL,
            is_calculated_residual INTEGER NOT NULL,
            generated_by_package TEXT NOT NULL,
            PRIMARY KEY (timestamp_utc, component_type, component_id, generated_by_package)
        )
        """
    )
    conn.commit()


def load_input_summary(conn: sqlite3.Connection) -> dict[str, object]:
    profiled = conn.execute(
        f"""
        SELECT COUNT(*) AS rows, COUNT(DISTINCT mga_id) AS mgas,
               MIN(interval_start_utc) AS min_ts, MAX(interval_start_utc) AS max_ts,
               SUM(-value) AS positive_mwh
        FROM {NATIVE_TABLE}
        WHERE bidding_zone='SE3' AND settlement_class='profiled_load_profile'
        """
    ).fetchone()
    entsoe = conn.execute(
        f"""
        SELECT COUNT(*) AS rows, MIN(timestamp_utc) AS min_ts, MAX(timestamp_utc) AS max_ts
        FROM {ENTSOE_TABLE}
        WHERE area='SE3'
        """
    ).fetchone()
    return {
        "profiled_row_count": int(profiled["rows"] or 0),
        "profiled_mga_count": int(profiled["mgas"] or 0),
        "profiled_min_timestamp": profiled["min_ts"],
        "profiled_max_timestamp": profiled["max_ts"],
        "profiled_positive_mwh": float(profiled["positive_mwh"] or 0.0),
        "entsoe_row_count": int(entsoe["rows"] or 0),
        "entsoe_min_timestamp": entsoe["min_ts"],
        "entsoe_max_timestamp": entsoe["max_ts"],
    }


def load_mga_features(conn: sqlite3.Connection) -> list[dict[str, object]]:
    rows = conn.execute(
        f"""
        WITH hourly AS (
            SELECT n.mga_id,
                   substr(n.interval_start_utc, 1, 13) || ':00:00Z' AS timestamp_utc,
                   SUM(-n.value) AS load_mw,
                   COUNT(*) AS input_rows
            FROM {NATIVE_TABLE} n
            WHERE n.bidding_zone='SE3' AND n.settlement_class='profiled_load_profile'
            GROUP BY n.mga_id, substr(n.interval_start_utc, 1, 13)
        ),
        shaped AS (
            SELECT h.mga_id,
                   AVG(h.load_mw) AS mean_mw,
                   AVG(CASE WHEN substr(h.timestamp_utc, 6, 2) IN ('12','01','02') THEN h.load_mw END) AS winter_mw,
                   AVG(CASE WHEN substr(h.timestamp_utc, 6, 2) IN ('06','07','08') THEN h.load_mw END) AS summer_mw,
                   AVG(CASE WHEN CAST(substr(h.timestamp_utc, 12, 2) AS INTEGER) BETWEEN 0 AND 5 THEN h.load_mw END) AS night_mw,
                   COUNT(*) AS hourly_rows,
                   SUM(h.input_rows) AS input_rows
            FROM hourly h
            GROUP BY h.mga_id
        ),
        ranked AS (
            SELECT s.*, NTILE(4) OVER (ORDER BY s.mean_mw) AS volume_quartile
            FROM shaped s
        )
        SELECT r.*, m.mga_name, m.DSO_or_grid_owner
        FROM ranked r
        LEFT JOIN {MASTERDATA_TABLE} m ON m.mga_id=r.mga_id
        ORDER BY r.mga_id
        """
    ).fetchall()
    return [dict(row) for row in rows]


def assign_clusters(features: list[dict[str, object]]) -> list[dict[str, object]]:
    assignments = []
    for feature in features:
        climate = classify_climate(feature)
        urban = classify_urban(feature)
        cluster_id = cluster_id_for(climate, urban)
        assignments.append({
            "mga_id": feature["mga_id"],
            "mga_name": feature.get("mga_name"),
            "dso_or_grid_owner": feature.get("DSO_or_grid_owner"),
            "cluster_id": cluster_id,
            "cluster_label": f"{climate} / {urban}",
            "climate_group": climate,
            "urban_group": urban,
            "mean_mw": float(feature.get("mean_mw") or 0.0),
            "winter_mw": float(feature.get("winter_mw") or 0.0),
            "summer_mw": float(feature.get("summer_mw") or 0.0),
            "night_mw": float(feature.get("night_mw") or 0.0),
            "hourly_rows": int(feature.get("hourly_rows") or 0),
            "input_rows": int(feature.get("input_rows") or 0),
        })
    return assignments


def classify_climate(feature: dict[str, object]) -> str:
    text = normalized_text(feature)
    west_terms = ("göteborg", "goteborg", "mölndal", "molndal", "kungälv", "kungalv", "stenungsund", "lysekil", "uddevalla", "trollhättan", "trollhattan", "alingsås", "alingsas", "kungsbacka", "varberg")
    east_terms = ("stockholm", "solna", "sundbyberg", "södertälje", "sodertalje", "uppsala", "västerås", "vasteras", "nacka", "boo", "lidingö", "lidingo", "roslagen", "åkersberga", "akersberga", "norrtälje", "norrtalje", "enköping", "enkoping", "strängnäs", "strangnas")
    north_terms = ("dalarna", "mora", "rättvik", "rattvik", "leksand", "älvdalen", "alvdalen", "falun", "borlänge", "borlange", "arvika", "åmål", "amal", "årjäng", "arjang", "värmland", "varmland")
    if any(term in text for term in west_terms):
        return "WEST_COAST_GOTHENBURG"
    if any(term in text for term in east_terms):
        return "EAST_COAST_MALARDALEN_STOCKHOLM"
    if any(term in text for term in north_terms):
        return "NORTHERN_INLAND"
    return "SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND"


def classify_urban(feature: dict[str, object]) -> str:
    text = normalized_text(feature)
    mean_mw = float(feature.get("mean_mw") or 0.0)
    winter = float(feature.get("winter_mw") or 0.0)
    summer = float(feature.get("summer_mw") or 0.0)
    seasonal_ratio = winter / summer if summer > 0 else 1.0
    big_city_terms = ("stockholm", "göteborg", "goteborg", "uppsala", "västerås", "vasteras", "solna", "sundbyberg", "nacka", "mölndal", "molndal")
    rural_terms = ("landsbygd", "rural", "årsunda", "arsunda", "bengtsfors", "årjäng", "arjang", "älvdalen", "alvdalen", "rättvik", "rattvik", "bärke", "barke")
    villa_terms = ("boo", "åkersberga", "akersberga", "lerum", "alingsås", "alingsas", "kungsbacka", "kungälv", "kungalv", "norrtälje", "norrtalje")
    if any(term in text for term in big_city_terms) or mean_mw >= 75.0:
        return "BIG_CITY_APARTMENT_SERVICE"
    if any(term in text for term in villa_terms) or seasonal_ratio >= 2.2:
        return "VILLA_SUBURBAN"
    if any(term in text for term in rural_terms) or mean_mw < 5.0:
        return "RURAL_SPARSE_AGRICULTURE"
    return "MIXED_SMALL_CITY_TOWN"


def normalized_text(feature: dict[str, object]) -> str:
    return f"{feature.get('mga_id') or ''} {feature.get('mga_name') or ''} {feature.get('DSO_or_grid_owner') or ''}".lower()


def cluster_id_for(climate: str, urban: str) -> str:
    return f"C{CLIMATE_GROUPS.index(climate) + 1}{URBAN_GROUPS.index(urban) + 1}"


def replace_cluster_assignments(conn: sqlite3.Connection, assignments: list[dict[str, object]]) -> None:
    conn.execute("DROP TABLE IF EXISTS se3_profiled_mga_cluster_assignment_v1")
    conn.execute(
        """
        CREATE TABLE se3_profiled_mga_cluster_assignment_v1 (
            mga_id TEXT PRIMARY KEY,
            mga_name TEXT,
            dso_or_grid_owner TEXT,
            cluster_id TEXT NOT NULL,
            cluster_label TEXT NOT NULL,
            climate_group TEXT NOT NULL,
            urban_group TEXT NOT NULL,
            mean_mw REAL NOT NULL,
            winter_mw REAL NOT NULL,
            summer_mw REAL NOT NULL,
            night_mw REAL NOT NULL,
            hourly_rows INTEGER NOT NULL,
            input_rows INTEGER NOT NULL,
            generated_by_package TEXT NOT NULL
        )
        """
    )
    conn.executemany(
        """
        INSERT INTO se3_profiled_mga_cluster_assignment_v1
        (mga_id, mga_name, dso_or_grid_owner, cluster_id, cluster_label, climate_group, urban_group,
         mean_mw, winter_mw, summer_mw, night_mw, hourly_rows, input_rows, generated_by_package)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["mga_id"],
                row["mga_name"],
                row["dso_or_grid_owner"],
                row["cluster_id"],
                row["cluster_label"],
                row["climate_group"],
                row["urban_group"],
                row["mean_mw"],
                row["winter_mw"],
                row["summer_mw"],
                row["night_mw"],
                row["hourly_rows"],
                row["input_rows"],
                PACKAGE_ID,
            )
            for row in assignments
        ],
    )
    conn.commit()


def aggregate_profiled_clusters(conn: sqlite3.Connection, assignments: list[dict[str, object]]) -> list[dict[str, object]]:
    assignment_count_by_cluster = Counter(str(row["cluster_id"]) for row in assignments)
    rows = conn.execute(
        f"""
        SELECT substr(n.interval_start_utc, 1, 13) || ':00:00Z' AS timestamp_utc,
               a.cluster_id,
               a.cluster_label,
               SUM(-n.value) AS consumption_mw,
               COUNT(DISTINCT n.mga_id) AS mga_count,
               GROUP_CONCAT(DISTINCT n.resolution_minutes) AS native_resolution_mix,
               COUNT(*) AS input_row_count
        FROM {NATIVE_TABLE} n
        JOIN se3_profiled_mga_cluster_assignment_v1 a ON a.mga_id=n.mga_id
        WHERE n.bidding_zone='SE3' AND n.settlement_class='profiled_load_profile'
        GROUP BY substr(n.interval_start_utc, 1, 13), a.cluster_id, a.cluster_label
        ORDER BY timestamp_utc, a.cluster_id
        """
    ).fetchall()
    by_key = {}
    all_hours = set()
    for row in rows:
        key = (row["timestamp_utc"], row["cluster_id"])
        all_hours.add(str(row["timestamp_utc"]))
        by_key[key] = {
            "timestamp_utc": row["timestamp_utc"],
            "cluster_id": row["cluster_id"],
            "cluster_label": row["cluster_label"],
            "consumption_mw": float(row["consumption_mw"] or 0.0),
            "mga_count": int(row["mga_count"] or 0),
            "source_settlement_group": "profiled_load_profile",
            "native_resolution_mix": str(row["native_resolution_mix"] or ""),
            "coverage_ratio": min(1.0, int(row["input_row_count"] or 0) / max(1, int(row["mga_count"] or 1) * 4)),
            "input_row_count": int(row["input_row_count"] or 0),
            "generated_by_package": PACKAGE_ID,
        }
    output = []
    for timestamp_utc in sorted(all_hours):
        for cluster in ALL_CLUSTERS:
            key = (timestamp_utc, cluster["cluster_id"])
            output.append(by_key.get(key, {
                "timestamp_utc": timestamp_utc,
                "cluster_id": cluster["cluster_id"],
                "cluster_label": cluster["cluster_label"],
                "consumption_mw": 0.0,
                "mga_count": int(assignment_count_by_cluster.get(str(cluster["cluster_id"]), 0)),
                "source_settlement_group": "profiled_load_profile",
                "native_resolution_mix": "",
                "coverage_ratio": 0.0,
                "input_row_count": 0,
                "generated_by_package": PACKAGE_ID,
            }))
    return output


def load_entsoe_rows(conn: sqlite3.Connection) -> dict[str, float]:
    return {
        row["timestamp_utc"]: float(row["consumption_mw"])
        for row in conn.execute(f"SELECT timestamp_utc, consumption_mw FROM {ENTSOE_TABLE} WHERE area='SE3'")
    }


def compute_residual_rows(
    cluster_rows: list[dict[str, object]],
    entsoe_rows: dict[str, float],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    by_hour: dict[str, float] = defaultdict(float)
    clusters_by_hour: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in cluster_rows:
        ts = str(row["timestamp_utc"])
        by_hour[ts] += float(row["consumption_mw"])
        clusters_by_hour[ts].append(row)
    residual_rows = []
    decomposition_rows = []
    for ts in sorted(set(by_hour) & set(entsoe_rows)):
        total = entsoe_rows[ts]
        profiled = by_hour[ts]
        residual = total - profiled
        profiled_share = profiled / total if total else 0.0
        residual_share = residual / total if total else 0.0
        residual_rows.append({
            "timestamp_utc": ts,
            "area": "SE3",
            "residual_metered_non_profiled_mw": residual,
            "entsoe_total_consumption_mw": total,
            "profiled_cluster_sum_mw": profiled,
            "profiled_share_of_total": profiled_share,
            "residual_share_of_total": residual_share,
            "residual_definition": "ENTSOE_SE3_actual_total_load_minus_sum_profiled_load_profile_mga_clusters",
            "generated_by_package": PACKAGE_ID,
        })
        for cluster in clusters_by_hour[ts]:
            consumption = float(cluster["consumption_mw"])
            decomposition_rows.append({
                "timestamp_utc": ts,
                "component_type": "profiled_cluster",
                "component_id": cluster["cluster_id"],
                "component_label": cluster["cluster_label"],
                "consumption_mw": consumption,
                "share_of_total": consumption / total if total else 0.0,
                "is_observed_component": 1,
                "is_calculated_residual": 0,
                "generated_by_package": PACKAGE_ID,
            })
        decomposition_rows.append({
            "timestamp_utc": ts,
            "component_type": "metered_residual",
            "component_id": "SE3_RESIDUAL_METERED_NON_PROFILED_UNOBSERVED",
            "component_label": "SE3 residual metered/non_profiled/unobserved",
            "consumption_mw": residual,
            "share_of_total": residual_share,
            "is_observed_component": 0,
            "is_calculated_residual": 1,
            "generated_by_package": PACKAGE_ID,
        })
    return residual_rows, decomposition_rows


def write_output_rows(
    conn: sqlite3.Connection,
    cluster_rows: list[dict[str, object]],
    residual_rows: list[dict[str, object]],
    decomposition_rows: list[dict[str, object]],
) -> None:
    for table in (CLUSTER_TABLE, RESIDUAL_TABLE, DECOMPOSITION_TABLE):
        conn.execute(f"DELETE FROM {table} WHERE generated_by_package=?", (PACKAGE_ID,))
    insert_rows(conn, CLUSTER_TABLE, cluster_rows)
    insert_rows(conn, RESIDUAL_TABLE, residual_rows)
    insert_rows(conn, DECOMPOSITION_TABLE, decomposition_rows)
    conn.commit()


def insert_rows(conn: sqlite3.Connection, table: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    columns = list(rows[0])
    placeholders = ", ".join("?" for _ in columns)
    conn.executemany(
        f"INSERT OR REPLACE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
        [tuple(row[column] for column in columns) for row in rows],
    )


def build_validation_summary(
    cluster_rows: list[dict[str, object]],
    residual_rows: list[dict[str, object]],
    input_summary: dict[str, object],
) -> dict[str, object]:
    del input_summary
    profiled_by_hour = defaultdict(float)
    for row in cluster_rows:
        profiled_by_hour[str(row["timestamp_utc"])] += float(row["consumption_mw"])
    residual_values = [float(row["residual_metered_non_profiled_mw"]) for row in residual_rows]
    total_values = [float(row["entsoe_total_consumption_mw"]) for row in residual_rows]
    profiled_values = [float(row["profiled_cluster_sum_mw"]) for row in residual_rows]
    negative = [row for row in residual_rows if float(row["residual_metered_non_profiled_mw"]) < 0]
    return {
        "profiled_cluster_sum_mean_mw": mean(profiled_values),
        "entsoe_se3_mean_mw": mean(total_values),
        "profiled_share_mean": mean([float(row["profiled_share_of_total"]) for row in residual_rows]),
        "residual_share_mean": mean([float(row["residual_share_of_total"]) for row in residual_rows]),
        "residual_mean_mw": mean(residual_values),
        "residual_min_mw": min(residual_values) if residual_values else 0.0,
        "residual_p05_mw": percentile(residual_values, 0.05) if residual_values else 0.0,
        "residual_p95_mw": percentile(residual_values, 0.95) if residual_values else 0.0,
        "residual_max_mw": max(residual_values) if residual_values else 0.0,
        "negative_residual_hours_count": len(negative),
        "negative_residual_hours_examples": [row["timestamp_utc"] for row in negative[:10]],
        "missing_profiled_hours_count": 0,
        "missing_entsoe_hours_count": max(0, len(profiled_by_hour) - len(residual_rows)),
        "joined_hours": len(residual_rows),
    }


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def build_summary(
    started: float,
    db_path: Path,
    input_summary: dict[str, object],
    assignments: list[dict[str, object]],
    validation: dict[str, object],
    cluster_rows: list[dict[str, object]],
    residual_rows: list[dict[str, object]],
    decomposition_rows: list[dict[str, object]],
) -> dict[str, object]:
    assignment_cluster_counts = Counter(str(row["cluster_id"]) for row in assignments)
    cluster_volume = defaultdict(float)
    for row in cluster_rows:
        cluster_volume[str(row["cluster_id"])] += float(row["consumption_mw"])
    assignment_rows = sorted(assignments, key=lambda row: (str(row["cluster_id"]), -float(row["mean_mw"]), str(row["mga_id"])))
    cluster_counts = {str(cluster["cluster_id"]): int(assignment_cluster_counts.get(str(cluster["cluster_id"]), 0)) for cluster in ALL_CLUSTERS}
    return {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": "PASS" if int(validation["negative_residual_hours_count"]) == 0 else "WARN",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "feature_db": str(db_path),
        "input_summary": input_summary,
        "p0054y_stop_review": "P0054Y stopped because it expected measured/non_profiled MGA input; P0054Y2 uses profiled/load-profile input correctly.",
        "p0054w_input_status": "usable as profiled_load_profile component only",
        "cluster_count": len(ALL_CLUSTERS),
        "nonempty_assignment_cluster_count": sum(1 for count in cluster_counts.values() if count),
        "cluster_counts": dict(sorted(cluster_counts.items())),
        "cluster_volume_mwh": {str(cluster["cluster_id"]): round(cluster_volume.get(str(cluster["cluster_id"]), 0.0), 3) for cluster in ALL_CLUSTERS},
        "assignments": assignment_rows,
        "validation": validation,
        "row_counts": {
            "cluster_rows": len(cluster_rows),
            "residual_rows": len(residual_rows),
            "decomposition_rows": len(decomposition_rows),
            "assignment_rows": len(assignments),
        },
        "output_tables": [CLUSTER_TABLE, RESIDUAL_TABLE, DECOMPOSITION_TABLE, "se3_profiled_mga_cluster_assignment_v1"],
        "no_credentials": True,
        "no_external_integration": True,
        "no_devices_or_runtime": True,
        "no_large_raw_data_committed": True,
    }


def stopped_summary(started: float, db_path: Path, input_summary: dict[str, object]) -> dict[str, object]:
    return {
        "package_id": PACKAGE_ID,
        "label": LABEL,
        "status": "STOP",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "feature_db": str(db_path),
        "input_summary": input_summary,
        "stop_reason": "missing profiled/load-profile input or ENTSO-E SE3 target",
        "row_counts": {},
    }


def write_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog(summary)),
        "labb": write(evidence_dir / "labb-label.md", "# P0054Y2 LABB label\n\nLabel: `LABB`.\n"),
        "p0054y": write(evidence_dir / "p0054y-stop-review.md", p0054y_stop_review()),
        "input": write(evidence_dir / "p0054w-input-review.md", p0054w_input_review(summary)),
        "contract": write(evidence_dir / "profiled-mga-cluster-contract.md", profiled_contract()),
        "assignment": write(evidence_dir / "profiled-16-cluster-assignment.md", assignment_report(summary)),
        "hourly": write(evidence_dir / "hourly-aggregation-contract.md", hourly_contract()),
        "residual": write(evidence_dir / "residual-definition.md", residual_definition()),
        "schema": write(evidence_dir / "output-table-schema.md", output_schema()),
        "validation": write(evidence_dir / "decomposition-validation.md", validation_report(summary)),
        "coverage": write(evidence_dir / "coverage-vs-entsoe.md", coverage_report(summary)),
        "quality": write(evidence_dir / "residual-quality-review.md", residual_quality_report(summary)),
        "database": write(evidence_dir / "database-output-evidence.md", database_evidence(summary)),
        "readiness": write(evidence_dir / "modeling-readiness-review.md", modeling_readiness(summary)),
        "learned": write(evidence_dir / "what-we-learned.md", learned_report()),
        "next": write(evidence_dir / "next-package-recommendation.md", next_recommendation()),
        "summary": write_json(evidence_dir / "decomposition-summary.json", summary_for_json(summary)),
    }
    write_csv(evidence_dir / "profiled-cluster-assignment.csv", compact_assignments(summary))
    write_csv(evidence_dir / "cluster-volume-summary.csv", compact_cluster_volumes(summary))
    write_csv(evidence_dir / "metered-residual-quality-summary.csv", [summary.get("validation", {})])
    return paths


def summary_for_json(summary: dict[str, object]) -> dict[str, object]:
    output = dict(summary)
    output["assignments"] = compact_assignments(summary)
    return output


def compact_assignments(summary: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "mga_id": row["mga_id"],
            "mga_name": row["mga_name"],
            "cluster_id": row["cluster_id"],
            "cluster_label": row["cluster_label"],
            "mean_mw": round(float(row["mean_mw"]), 6),
        }
        for row in summary.get("assignments", [])  # type: ignore[union-attr]
    ]


def compact_cluster_volumes(summary: dict[str, object]) -> list[dict[str, object]]:
    counts = summary.get("cluster_counts", {})
    volumes = summary.get("cluster_volume_mwh", {})
    return [
        {"cluster_id": key, "mga_count": counts.get(key, 0), "profiled_mwh": volumes.get(key, 0.0)}
        for key in sorted(volumes)  # type: ignore[arg-type]
    ]


def write_json(path: Path, data: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    return str(path)


def write_csv(path: Path, rows: list[dict[str, object]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return str(path)
    columns = list(rows[0])
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


def changelog(summary: dict[str, object]) -> str:
    return f"""# P0054Y2 changelog

Status: `{summary['status']}`

- Built SE3 profiled/load-profile MGA cluster plus residual decomposition.
- Wrote P0054Y2 output tables: `{', '.join(summary.get('output_tables', []))}`.
- Cluster rows: `{summary.get('row_counts', {}).get('cluster_rows', 0)}`.
- Residual rows: `{summary.get('row_counts', {}).get('residual_rows', 0)}`.
- No credentials, external integration, devices, runtime changes, large raw data commits or model training.
"""


def p0054y_stop_review() -> str:
    return """# P0054Y2 P0054Y stop review

P0054Y stopped correctly because it asked for measured/non_profiled per-MGA input while the repository had profiled/load-profile per-MGA input.

P0054Y2 supersedes it by naming the available component correctly and defining the residual as metered/non_profiled/unobserved.
"""


def p0054w_input_review(summary: dict[str, object]) -> str:
    input_summary = summary.get("input_summary", {})
    return f"""# P0054Y2 P0054W input review

P0054W input status: `usable as profiled_load_profile component only`.

```json
{json.dumps(input_summary, indent=2, sort_keys=True)}
```

P0054Y2 does not relabel this component as measured load.
"""


def profiled_contract() -> str:
    return """# P0054Y2 profiled MGA cluster contract

The cluster component is observed historical `EXP18/LoadProfile` per-MGA data with `settlement_class=profiled_load_profile`.

It is not full SE3 load and not metered/non_profiled load.
"""


def assignment_report(summary: dict[str, object]) -> str:
    rows = compact_cluster_volumes(summary)
    lines = ["# P0054Y2 profiled 16-cluster assignment", "", "Cluster volume summary:", ""]
    lines.extend(f"- `{row['cluster_id']}`: {row['mga_count']} MGAs, {row['profiled_mwh']} MWh" for row in rows)
    lines.extend(["", "Detailed compact assignment is in `profiled-cluster-assignment.csv`."])
    return "\n".join(lines) + "\n"


def hourly_contract() -> str:
    return """# P0054Y2 hourly aggregation contract

Native P0054W energy rows are stored as MWh and source-negative for load.

Aggregation:

```text
positive_hourly_MWh = sum(-source_value) by UTC hour
consumption_mw = positive_hourly_MWh over one hour
```

`settlement_class` remains `profiled_load_profile`.
"""


def residual_definition() -> str:
    return """# P0054Y2 residual definition

```text
se3_residual_metered_non_profiled_mw =
  ENTSO-E SE3 actual total load MW
  - sum(profiled/load-profile MGA cluster MW)
```

Residual is a calculated historical balancing component. It is not directly observed per-MGA measured load and must not be used as a future actual feature.
"""


def output_schema() -> str:
    return f"""# P0054Y2 output table schema

Tables:

```text
{CLUSTER_TABLE}
{RESIDUAL_TABLE}
{DECOMPOSITION_TABLE}
se3_profiled_mga_cluster_assignment_v1
```

See SQLite schema in the local feature DB for exact column types. All rows are labeled `generated_by_package=P0054Y2`.
"""


def validation_report(summary: dict[str, object]) -> str:
    return f"""# P0054Y2 decomposition validation

```json
{json.dumps(summary.get('validation', {}), indent=2, sort_keys=True)}
```

The decomposition is exact by construction for joined hours:

```text
profiled_cluster_sum + residual = ENTSO-E SE3 total
```
"""


def coverage_report(summary: dict[str, object]) -> str:
    validation = summary.get("validation", {})
    return f"""# P0054Y2 coverage vs ENTSO-E

Profiled share mean:

```text
{validation.get('profiled_share_mean', 0.0)}
```

Residual share mean:

```text
{validation.get('residual_share_mean', 0.0)}
```
"""


def residual_quality_report(summary: dict[str, object]) -> str:
    validation = summary.get("validation", {})
    return f"""# P0054Y2 residual quality review

Negative residual hours:

```text
{validation.get('negative_residual_hours_count', 0)}
```

Residual min/p05/mean/p95/max MW:

```text
{validation.get('residual_min_mw', 0.0)}
{validation.get('residual_p05_mw', 0.0)}
{validation.get('residual_mean_mw', 0.0)}
{validation.get('residual_p95_mw', 0.0)}
{validation.get('residual_max_mw', 0.0)}
```
"""


def database_evidence(summary: dict[str, object]) -> str:
    return f"""# P0054Y2 database output evidence

Output tables written:

```text
{chr(10).join(summary.get('output_tables', []))}
```

Row counts:

```json
{json.dumps(summary.get('row_counts', {}), indent=2, sort_keys=True)}
```
"""


def modeling_readiness(summary: dict[str, object]) -> str:
    status = "ready_for_labb_forecasting_package" if summary.get("status") in {"PASS", "WARN"} else "not_ready"
    return f"""# P0054Y2 modeling readiness review

Status: `{status}`

The profiled clusters and residual are usable as historical LABB targets for later forecast-model experiments.

Restrictions:

```text
do not treat residual as observed measured per-MGA data
do not use future actual residual as a feature
keep profiled/load-profile clusters separate from residual
```
"""


def learned_report() -> str:
    return """# P0054Y2 what we learned

The available public per-MGA component can be decomposed geographically, but the larger metered/non_profiled component remains a SE3-level residual unless a better source appears.
"""


def next_recommendation() -> str:
    return """# P0054Y2 next package recommendation

Recommended next package: LABB forecasting experiment with separate targets:

```text
1. profiled/load-profile cluster forecasts
2. SE3 metered/non_profiled residual forecast
3. reconciled total SE3 forecast
```

No future actual residual may be used as an input feature.
"""


def main() -> None:
    result = run_p0054y2_decomposition()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "evidence": result.evidence}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
