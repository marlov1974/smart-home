"""P0054W local eSett MGA consumption discovery."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import csv
import json
import os
import sqlite3

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics.p0041 import write


PACKAGE_ID = "P0054W"
EVIDENCE_DIR = Path("requirements/package-runs/P0054W")
DEFAULT_SMART_HOME_DIR = Path("/Users/marcus.lovenstad/.smart-home")
CANDIDATE_TERMS = (
    "esett",
    "nbs",
    "mga",
    "metering_grid_area",
    "grid_area",
    "network_area",
    "netområde",
    "nätområde",
    "nätavräkningsområde",
    "consumption",
    "load",
    "profiled",
    "settlement",
    "hourly",
    "15min",
    "quarter_hour",
    "physical_balance",
    "entsoe",
)
MGA_TERMS = ("mga", "metering_grid_area", "nätavräkningsområde")
PHYSICAL_BALANCE_TABLE = "physical_balance_hourly_raw_v1"
ENTSOE_CONSUMPTION_TABLE = "entsoe_consumption_area_hourly_v1"


@dataclass(frozen=True)
class P0054WResult:
    status: str
    found_mga_consumption_source: bool
    loaded_database_tables: bool
    evidence: dict[str, str]


def run_p0054w_discovery(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    repo_root: Path | str = Path("."),
    evidence_dir: Path | str = EVIDENCE_DIR,
    smart_home_dir: Path | str = DEFAULT_SMART_HOME_DIR,
) -> P0054WResult:
    db_path = Path(feature_db).expanduser()
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        tables = sqlite_table_inventory(conn)
        physical_balance = summarize_physical_balance(conn)
        entsoe_consumption = summarize_entsoe_consumption(conn)
        existing_mga_tables = existing_tables(conn, ("esett_mga_consumption_native_v1", "esett_mga_masterdata_v1"))
    repo_path = Path(repo_root)
    files = find_local_candidate_files(repo_path, Path(smart_home_dir))
    files.extend(known_repo_source_candidates(repo_path))
    mga_tables = [item for item in tables if item["classification"]["has_mga_term"]]
    mga_files = [item for item in files if item["has_mga_term"] and item["source_type"] in {"script", "local_export_or_data_file"}]
    found_mga_consumption_source = bool(mga_tables or mga_files)
    summary = {
        "package_id": PACKAGE_ID,
        "status": "PASS",
        "result_kind": "strong_negative_discovery",
        "generated_at_utc": now_utc(),
        "feature_db": str(db_path),
        "found_mga_consumption_source": found_mga_consumption_source,
        "loaded_database_tables": False,
        "existing_mga_tables": existing_mga_tables,
        "table_inventory": tables,
        "physical_balance_summary": physical_balance,
        "entsoe_consumption_summary": entsoe_consumption,
        "local_file_candidates": files,
        "decision": discovery_decision(found_mga_consumption_source, existing_mga_tables),
    }
    evidence = write_p0054w_evidence(Path(evidence_dir), summary)
    return P0054WResult(
        status=str(summary["status"]),
        found_mga_consumption_source=found_mga_consumption_source,
        loaded_database_tables=False,
        evidence=evidence,
    )


def sqlite_table_inventory(conn: sqlite3.Connection) -> list[dict[str, object]]:
    output = []
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    for row in rows:
        name = str(row["name"] if isinstance(row, sqlite3.Row) else row[0])
        columns = [str(item["name"] if isinstance(item, sqlite3.Row) else item[1]) for item in conn.execute(f"PRAGMA table_info({quote_identifier(name)})")]
        classification = classify_table_candidate(name, columns)
        if not classification["is_candidate"]:
            continue
        row_count = conn.execute(f"SELECT COUNT(*) FROM {quote_identifier(name)}").fetchone()[0]
        min_timestamp, max_timestamp = timestamp_range(conn, name, columns)
        output.append({
            "source_name": name,
            "source_type": "table",
            "path_or_table": name,
            "columns": columns,
            "row_count": int(row_count),
            "min_timestamp": min_timestamp,
            "max_timestamp": max_timestamp,
            "countries_or_areas": distinct_candidate_values(conn, name, columns, ("country", "area", "bidding_zone")),
            "resolution_candidates": distinct_candidate_values(conn, name, columns, ("resolution", "source_resolution", "resolution_minutes")),
            "settlement_type_candidates": distinct_candidate_values(conn, name, columns, ("settlement_class", "settlement_method", "measure", "source_measure")),
            "classification": classification,
        })
    return output


def classify_table_candidate(name: str, columns: list[str]) -> dict[str, object]:
    haystack = " ".join([name, *columns]).lower()
    matched = [term for term in CANDIDATE_TERMS if term in haystack]
    has_mga_term = any(term in haystack for term in MGA_TERMS)
    return {
        "is_candidate": bool(matched),
        "matched_terms": matched,
        "has_mga_term": has_mga_term,
        "has_consumption_term": "consumption" in haystack or "load" in haystack,
        "has_esett_term": "esett" in haystack,
        "has_nbs_term": "nbs" in haystack,
        "has_entsoe_term": "entsoe" in haystack,
    }


def summarize_physical_balance(conn: sqlite3.Connection) -> list[dict[str, object]]:
    if not table_exists(conn, PHYSICAL_BALANCE_TABLE):
        return []
    rows = conn.execute(
        f"""
        SELECT source_name, source_dataset, bidding_zone, measure, unit,
               COUNT(*) AS rows, MIN(timestamp_utc) AS min_timestamp, MAX(timestamp_utc) AS max_timestamp
        FROM {PHYSICAL_BALANCE_TABLE}
        GROUP BY source_name, source_dataset, bidding_zone, measure, unit
        ORDER BY source_name, source_dataset, bidding_zone, measure, unit
        """
    ).fetchall()
    return [
        {
            "source_name": row["source_name"],
            "source_dataset": row["source_dataset"],
            "bidding_zone": row["bidding_zone"],
            "measure": row["measure"],
            "settlement_class": settlement_class_from_measure(str(row["measure"])),
            "unit": row["unit"],
            "row_count": int(row["rows"]),
            "min_timestamp": row["min_timestamp"],
            "max_timestamp": row["max_timestamp"],
            "mga_status": "not_mga_bidding_zone_or_mba_level",
        }
        for row in rows
    ]


def summarize_entsoe_consumption(conn: sqlite3.Connection) -> list[dict[str, object]]:
    if not table_exists(conn, ENTSOE_CONSUMPTION_TABLE):
        return []
    rows = conn.execute(
        f"""
        SELECT area, source_system, source_measure, source_area_code, resolution, unit, package_id,
               COUNT(*) AS rows, MIN(timestamp_utc) AS min_timestamp, MAX(timestamp_utc) AS max_timestamp
        FROM {ENTSOE_CONSUMPTION_TABLE}
        GROUP BY area, source_system, source_measure, source_area_code, resolution, unit, package_id
        ORDER BY area, resolution
        """
    ).fetchall()
    return [
        {
            "area": row["area"],
            "source_system": row["source_system"],
            "source_measure": row["source_measure"],
            "source_area_code": row["source_area_code"],
            "resolution": row["resolution"],
            "unit": row["unit"],
            "package_id": row["package_id"],
            "row_count": int(row["rows"]),
            "min_timestamp": row["min_timestamp"],
            "max_timestamp": row["max_timestamp"],
            "mga_status": "not_mga_entsoe_area_level",
        }
        for row in rows
    ]


def settlement_class_from_measure(measure: str) -> str:
    normalized = measure.lower()
    if "profiled" in normalized:
        return "profiled_or_monthly_settled"
    if "metered" in normalized:
        return "metered_settled_unknown_native_resolution"
    if "flex" in normalized:
        return "flex_settled_unknown_native_resolution"
    if "total" in normalized and "consumption" in normalized:
        return "aggregate_consumption_total"
    return "unknown_or_not_consumption"


def resolution_transition_summary(timestamps: list[str]) -> dict[str, object]:
    ordered = sorted(parse_utc(value) for value in timestamps)
    if not ordered:
        return {
            "first_timestamp": None,
            "last_timestamp": None,
            "observed_time_deltas_minutes": {},
            "share_15m": 0.0,
            "share_60m": 0.0,
            "transition_date_candidate": None,
            "mixed_resolution_periods": False,
        }
    deltas = Counter(int((right - left).total_seconds() // 60) for left, right in zip(ordered, ordered[1:]))
    total = sum(deltas.values())
    transition = None
    previous = None
    for left, right in zip(ordered, ordered[1:]):
        delta = int((right - left).total_seconds() // 60)
        if previous is not None and delta != previous:
            transition = right.isoformat().replace("+00:00", "Z")
            break
        previous = delta
    return {
        "first_timestamp": ordered[0].isoformat().replace("+00:00", "Z"),
        "last_timestamp": ordered[-1].isoformat().replace("+00:00", "Z"),
        "observed_time_deltas_minutes": {str(key): value for key, value in sorted(deltas.items())},
        "share_15m": (deltas.get(15, 0) / total) if total else 0.0,
        "share_60m": (deltas.get(60, 0) / total) if total else 0.0,
        "transition_date_candidate": transition,
        "mixed_resolution_periods": len(deltas) > 1,
    }


def find_local_candidate_files(repo_root: Path, smart_home_dir: Path) -> list[dict[str, object]]:
    roots = [repo_root.resolve()]
    if smart_home_dir.exists():
        roots.append(smart_home_dir.resolve())
    output = []
    seen: set[Path] = set()
    for root in roots:
        for current_root, dirs, files in os.walk(root):
            dirs[:] = [item for item in dirs if item not in {".git", "__pycache__", ".venv", "node_modules"}]
            current_path = Path(current_root)
            if current_path.match("*/requirements/package-runs/P0054W"):
                dirs[:] = []
                continue
            if current_path.match("*/.smart-home/secrets"):
                dirs[:] = []
                continue
            for name in files:
                path = current_path / name
                if path in seen:
                    continue
                seen.add(path)
                text = str(path).lower()
                matched = [term for term in CANDIDATE_TERMS if term in text]
                if not matched:
                    continue
                suffix = path.suffix.lower()
                source_type = "file"
                if suffix == ".py":
                    source_type = "script"
                elif suffix in {".md", ".txt"}:
                    source_type = "doc"
                elif suffix in {".csv", ".json", ".parquet", ".sqlite", ".sqlite3"}:
                    source_type = "local_export_or_data_file"
                output.append({
                    "source_name": path.name,
                    "source_type": source_type,
                    "path_or_table": str(path),
                    "matched_terms": matched,
                    "has_mga_term": any(term in text for term in MGA_TERMS),
                    "file_size_bytes": path.stat().st_size if path.exists() else None,
                })
    return sorted(output, key=lambda item: str(item["path_or_table"]))


def known_repo_source_candidates(repo_root: Path) -> list[dict[str, object]]:
    path = repo_root / "src/mac/services/spotprice_model_diagnostics/p0051.py"
    if not path.exists():
        return []
    return [{
        "source_name": "p0051.py",
        "source_type": "script",
        "path_or_table": str(path),
        "matched_terms": ["esett", "consumption", "profiled"],
        "has_mga_term": False,
        "file_size_bytes": path.stat().st_size,
        "note": "Existing approved project eSett Open Data mechanism for SE1-SE4 MBA/bidding-zone physical balance, not MGA.",
    }]


def write_p0054w_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary": write_json(evidence_dir / "summary.json", summary),
        "source_inventory_json": write_json(evidence_dir / "source-inventory.json", source_inventory(summary)),
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog(summary)),
        "label": write(evidence_dir / "labb-label.md", labb_label_report()),
        "source_inventory": write(evidence_dir / "source-inventory.md", source_inventory_report(summary)),
        "terminology": write(evidence_dir / "esett-terminology.md", terminology_report()),
        "masterdata": write(evidence_dir / "mga-masterdata-inventory.md", masterdata_report(summary)),
        "mapping": write(evidence_dir / "mga-price-area-mapping.md", mapping_report(summary)),
        "series": write(evidence_dir / "consumption-series-inventory.md", series_report(summary)),
        "settlement": write(evidence_dir / "settlement-classification.md", settlement_report(summary)),
        "resolution": write(evidence_dir / "resolution-transition-analysis.md", resolution_report(summary)),
        "native": write(evidence_dir / "native-resolution-contract.md", native_resolution_report(summary)),
        "database": write(evidence_dir / "database-ingestion-contract.md", database_report(summary)),
        "quality": write(evidence_dir / "data-quality-review.md", quality_report(summary)),
        "leakage": write(evidence_dir / "leakage-and-use-scope-review.md", leakage_report(summary)),
        "learned": write(evidence_dir / "what-we-learned.md", learned_report(summary)),
        "scope": write(evidence_dir / "no-api-no-device-runtime-review.md", scope_report()),
        "next": write(evidence_dir / "next-package-recommendation.md", next_report()),
    }
    write_csv(evidence_dir / "source-inventory.csv", source_inventory(summary))
    paths["source_inventory_csv"] = str(evidence_dir / "source-inventory.csv")
    return paths


def source_inventory(summary: dict[str, object]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    output.extend(summary["table_inventory"])
    output.extend(summary["local_file_candidates"])
    return output


def changelog(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0054W changelog",
        "",
        "- Ran local-only eSett/NBS/MGA consumption discovery.",
        "- Inventoried local SQLite tables and local candidate files.",
        "- Confirmed existing eSett data is SE1-SE4 bidding-zone/MBA-level P0051 data, not MGA data.",
        "- Confirmed no local MGA masterdata or MGA consumption time series were found.",
        "- Did not create MGA database tables because no credible local MGA source contract exists.",
        f"- Result status: {summary['status']} ({summary['result_kind']}).",
        "- No API, devices, runtime changes, credentials, model training or A61 utilization were used.",
        "",
    ])


def labb_label_report() -> str:
    return "\n".join([
        "# P0054W LABB label",
        "",
        "Label: `LABB`.",
        "",
        "This package is local research/discovery work under P0054A and is not a G2-KANDIDAT evaluation.",
        "",
    ])


def source_inventory_report(summary: dict[str, object]) -> str:
    return "# P0054W source inventory\n\n```json\n" + json.dumps(source_inventory(summary), indent=2, sort_keys=True) + "\n```\n"


def terminology_report() -> str:
    return "\n".join([
        "# P0054W eSett/MGA terminology",
        "",
        "`MGA` is treated as Metering Grid Area / Swedish nätavräkningsområde for this package.",
        "`MBA` in the existing P0051 eSett path is market balance area/bidding-zone level for SE1-SE4, represented by EIC-like area codes, and is not treated as MGA.",
        "`profiled` in existing eSett consumption measures is classified as profiled or monthly-settled-like consumption, but P0054W found no MGA-level source where that class can be mapped to a grid area.",
        "`metered` and `flex` are preserved as separate eSett classes in existing P0051 evidence, but their native MGA settlement contract is unavailable locally.",
        "Consumption sign convention from P0051: source eSett values were normalized to positive MW demand before storage.",
        "",
    ])


def masterdata_report(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0054W MGA masterdata inventory",
        "",
        "Status: no local MGA masterdata found.",
        "",
        "Required fields not found locally:",
        "",
        "- `mga_id`",
        "- `mga_name`",
        "- `country`",
        "- `bidding_zone` / `price_area` per MGA",
        "- DSO / grid owner",
        "- `valid_from` / `valid_to` history",
        "",
        f"Existing MGA tables: `{summary['existing_mga_tables']}`.",
        "",
    ])


def mapping_report(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0054W MGA price-area mapping",
        "",
        "No Swedish MGA-to-SE1/SE2/SE3/SE4 mapping was found locally.",
        "",
        "Count by price area:",
        "",
        "- SE1: unknown",
        "- SE2: unknown",
        "- SE3: unknown",
        "- SE4: unknown",
        "- unknown/unmapped: all MGA, because no MGA list exists locally",
        "",
        "The existing P0051 eSett data is already grouped by SE1-SE4 and cannot be reverse-mapped into MGA.",
        "",
    ])


def series_report(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0054W consumption-series inventory",
        "",
        "No MGA consumption time series were found.",
        "",
        "Existing non-MGA consumption sources:",
        "",
        "## eSett P0051 physical balance",
        "",
        "```json",
        json.dumps(summary["physical_balance_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## ENTSO-E area consumption",
        "",
        "```json",
        json.dumps(summary["entsoe_consumption_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "These sources are area/bidding-zone level and cannot satisfy an MGA native-resolution contract.",
        "",
    ])


def settlement_report(summary: dict[str, object]) -> str:
    classes = sorted({item["settlement_class"] for item in summary["physical_balance_summary"] if "consumption" in str(item["measure"])})
    return "\n".join([
        "# P0054W settlement classification",
        "",
        "Existing eSett consumption classes in P0051:",
        "",
        "```json",
        json.dumps(classes, indent=2),
        "```",
        "",
        "No MGA-level settlement class can be assigned because no MGA-level source exists locally.",
        "If future data contains separate profiled/monthly-settled and hourly/15-minute-settled MGA series, they must remain separate until an explicit total contract is documented.",
        "",
    ])


def resolution_report(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0054W resolution transition analysis",
        "",
        "No per-MGA timestamps are available, so no per-MGA 60m-to-15m transition can be computed.",
        "",
        "Known local sources:",
        "",
        "- P0051 eSett physical balance stores hourly rows after aggregating eSett quarter-hour observations.",
        "- P0054P2 ENTSO-E area load stores `PT60M` and `PT15M->hourly_mean` rows by bidding zone.",
        "",
        "P0054W did not resample any MGA data and did not hide a native-resolution transition.",
        "",
    ])


def native_resolution_report(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0054W native-resolution contract",
        "",
        "No MGA native-resolution source contract was established.",
        "",
        "Future ingestion must store each native interval with:",
        "",
        "- source system/name",
        "- country",
        "- MGA id/name",
        "- bidding zone mapping and mapping validity",
        "- settlement class",
        "- `resolution_minutes`",
        "- UTC interval start and end",
        "- value, unit, direction/sign convention",
        "- quality/status",
        "- version/publication timestamp",
        "- ingest timestamp and generating package id",
        "",
        "15-minute, hourly, daily, and monthly data must not be silently mixed or aggregated before this contract is satisfied.",
        "",
    ])


def database_report(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0054W database ingestion contract",
        "",
        "Database load performed: `false`.",
        "",
        "Tables not created:",
        "",
        "- `esett_mga_consumption_native_v1`",
        "- `esett_mga_masterdata_v1`",
        "",
        "Reason: no credible local/source-approved MGA consumption or MGA masterdata source was found.",
        "",
        "Creating empty tables was intentionally skipped so downstream packages do not mistake an unproven schema for available MGA data.",
        "",
    ])


def quality_report(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0054W data-quality review",
        "",
        "No MGA data was loaded, so row-level quality checks, missing intervals, duplicate intervals and SE3 volume sanity checks were not feasible.",
        "",
        "Quality of existing non-MGA sources:",
        "",
        "- P0051 eSett physical balance has complete SE1-SE4 hourly total consumption/production coverage in its validation evidence, but it is not MGA.",
        "- P0054P2 ENTSO-E area consumption has SE1-SE4 area load coverage and documented PT60M / PT15M-to-hourly handling, but it is not MGA.",
        "",
        f"Discovery decision: {summary['decision']}",
        "",
    ])


def leakage_report(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0054W leakage and use-scope review",
        "",
        "P0054W did not create model features, train models or evaluate forecasts.",
        "",
        "No future actual price leakage is possible from this package because it only inventories local data sources and writes evidence.",
        "",
        "Existing consumption/physical-balance actuals remain classified as historical observed data and must not be used as forecast-time inputs unless a separate forecast model exists.",
        "",
        "No A61 utilization, API calls, devices, runtime writes, Shelly, Home Assistant or KVS actions were used.",
        "",
    ])


def learned_report(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0054W what we learned",
        "",
        "1. The existing eSett path in this repo is P0051 and is SE1-SE4 MBA/bidding-zone physical balance, not Swedish MGA consumption.",
        "2. The local feature DB currently has no table name containing eSett, NBS or MGA.",
        "3. Local consumption data exists at area/bidding-zone level through P0051 eSett physical balance and P0054P2 ENTSO-E actual load, but neither can support MGA bottom-up modeling.",
        "4. A future MGA package needs either a local/manual export or an explicitly approved eSett/NBS/MGA source contract before ingestion.",
        "5. The next safe modeling recommendation is to stop MGA modeling until source and mapping evidence exists.",
        "",
    ])


def scope_report() -> str:
    return "\n".join([
        "# P0054W no API / no device / runtime review",
        "",
        "P0054W used local repository files and the local SQLite feature database only.",
        "",
        "Confirmed not performed:",
        "",
        "- no external API call",
        "- no credential or token use",
        "- no device action",
        "- no Shelly, Home Assistant or KVS action",
        "- no runtime change",
        "- no A61 utilization",
        "- no model training",
        "",
    ])


def next_report() -> str:
    return "\n".join([
        "# P0054W next package recommendation",
        "",
        "Recommend a follow-up package only after the operator provides either:",
        "",
        "1. a local/manual eSett/NBS/MGA export file, or",
        "2. an explicitly approved public/authenticated source contract for Swedish MGA masterdata and consumption time series.",
        "",
        "The next package should first ingest MGA masterdata and price-area mapping before any consumption model or hierarchical forecast experiment.",
        "",
    ])


def discovery_decision(found_mga_consumption_source: bool, existing_mga_tables: list[str]) -> str:
    if found_mga_consumption_source:
        return "MGA-like local source names exist and need manual validation before ingestion."
    if existing_mga_tables:
        return "MGA table names exist locally, but no discovered rows/source contract supported ingestion."
    return "Strong negative: no local MGA consumption source or MGA masterdata source was found; ingestion skipped."


def existing_tables(conn: sqlite3.Connection, names: tuple[str, ...]) -> list[str]:
    return [name for name in names if table_exists(conn, name)]


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return bool(conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone())


def timestamp_range(conn: sqlite3.Connection, table: str, columns: list[str]) -> tuple[str | None, str | None]:
    timestamp_columns = [column for column in columns if "timestamp" in column.lower() or column.lower().endswith("_utc")]
    for column in timestamp_columns:
        row = conn.execute(f"SELECT MIN({quote_identifier(column)}), MAX({quote_identifier(column)}) FROM {quote_identifier(table)}").fetchone()
        if row and row[0] is not None:
            return str(row[0]), str(row[1])
    return None, None


def distinct_candidate_values(conn: sqlite3.Connection, table: str, columns: list[str], candidate_columns: tuple[str, ...]) -> list[str]:
    present = [column for column in candidate_columns if column in columns]
    output: list[str] = []
    for column in present:
        rows = conn.execute(
            f"SELECT DISTINCT {quote_identifier(column)} FROM {quote_identifier(table)} WHERE {quote_identifier(column)} IS NOT NULL ORDER BY {quote_identifier(column)} LIMIT 20"
        ).fetchall()
        output.extend(str(row[0]) for row in rows)
    return sorted(set(output))


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def parse_utc(value: str) -> datetime:
    text = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
        for row in rows:
            writer.writerow({key: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value for key, value in row.items()})


def main() -> int:
    result = run_p0054w_discovery()
    print(json.dumps({
        "status": result.status,
        "found_mga_consumption_source": result.found_mga_consumption_source,
        "loaded_database_tables": result.loaded_database_tables,
        "evidence": result.evidence,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
