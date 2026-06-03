"""P0052 SE1-SE4 transfer flow and import/export ingestion."""

from __future__ import annotations

from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import math
import sqlite3
import subprocess
import time
import urllib.error
import urllib.request

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB


PACKAGE_ID = "P0052"
EVIDENCE_DIR = Path("requirements/package-runs/P0052")
SVK_FLOW_URL = "https://www.svk.se/services/controlroom/v2/map/flow?ticks={ticks}"
RAW_TABLE = "transfer_capacity_flow_raw_v1"
CANONICAL_TABLE = "transfer_capacity_flow_hourly_v1"
WIDE_TABLE = "transfer_capacity_flow_se1_se4_hourly_v1"
PHYSICAL_TABLE = "physical_balance_se1_se4_hourly_v1"
FLOW_SOURCE_START = datetime(2026, 5, 1, tzinfo=timezone.utc)
FLOW_BASED_GO_LIVE = datetime(2024, 10, 29, tzinfo=timezone.utc)
SE_ZONES = ("SE1", "SE2", "SE3", "SE4")
INTERNAL_BORDERS = ("SE1_SE2", "SE2_SE3", "SE3_SE4")
SWEDISH_BORDERS = {
    "SE1_SE2",
    "SE2_SE3",
    "SE3_SE4",
    "FI_SE1",
    "FI_SE3",
    "NO1_SE3",
    "NO3_SE2",
    "NO4_SE1",
    "NO4_SE2",
    "DK1_SE3",
    "DE_SE4",
    "LT_SE4",
    "SE4_DK2",
    "SE4_PL",
}
FORBIDDEN_PRODUCTION_PATHS = (
    "CONTINENTAL_PRICE_PRESSURE",
    "SE1_TO_SE3_ANCHORING",
    "SE3_API",
    "PRODUCTION_MODEL",
    "DEPLOYABLE_MODEL_ARTIFACT",
    "M5",
    "M6",
    "M7",
    "SHELLY",
    "DEVICE",
    "KVS",
    "HA",
)


@dataclass(frozen=True)
class P0052Result:
    status: str
    row_counts: dict[str, int | str]
    ranges: dict[str, object]
    evidence: dict[str, str]


def run_p0052_ingestion(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
    start: datetime | None = None,
    end: datetime | None = None,
    workers: int = 8,
) -> P0052Result:
    started = time.monotonic()
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        ranges = load_p0052_ranges(conn, start=start, end=end)
        existing = load_existing_transfer_tables(conn, ranges["final_ingested_range"])
        if existing:
            raw_rows, hourly_rows, wide_rows = existing
            raw_count: int | str = len(raw_rows)
        else:
            raw_rows = fetch_svk_flow_period(
                parse_utc(str(ranges["final_ingested_range"]["start"])),
                parse_utc(str(ranges["final_ingested_range"]["end"])) + timedelta(hours=1),
                workers=workers,
            )
            raw_count = len(raw_rows)
            hourly_rows = aggregate_hourly(raw_rows)
            physical_rows = load_physical_rows(conn)
            wide_rows = build_wide_hourly(hourly_rows, physical_rows)
            persist_transfer_flow(conn, raw_rows, hourly_rows, wide_rows)
        validation = validate_transfer_flow(conn, hourly_rows, wide_rows, ranges)
        diagnostics = run_initial_diagnostics(conn, wide_rows)
    summary = {
        "status": "WARN" if hourly_rows and wide_rows else "STOP",
        "source_discovery": source_discovery(),
        "source_contracts": source_contracts(),
        "ranges": ranges,
        "row_counts": {
            "raw_rows": raw_count,
            "hourly_rows": len(hourly_rows),
            "wide_rows": len(wide_rows),
        },
        "validation": validation,
        "diagnostics": diagnostics,
        "derived_features": derived_feature_definitions(),
        "forecast_safety": forecast_safety_classification(),
        "runtime_seconds": time.monotonic() - started,
        "forbidden_paths": FORBIDDEN_PRODUCTION_PATHS,
    }
    evidence = write_p0052_evidence(Path(evidence_dir), summary)
    return P0052Result(status=str(summary["status"]), row_counts=summary["row_counts"], ranges=ranges, evidence=evidence)


def load_p0052_ranges(conn: sqlite3.Connection, *, start: datetime | None = None, end: datetime | None = None) -> dict[str, object]:
    if not table_exists(conn, PHYSICAL_TABLE):
        raise RuntimeError(f"P0052 requires P0051 table {PHYSICAL_TABLE}")
    physical = conn.execute(f"SELECT MIN(timestamp_utc), MAX(timestamp_utc), COUNT(*) FROM {PHYSICAL_TABLE}").fetchone()
    physical_start = parse_utc(str(physical[0]))
    physical_end = parse_utc(str(physical[1]))
    requested_start = start or physical_start
    requested_end = end or physical_end
    final_start = max(requested_start, FLOW_SOURCE_START)
    final_end = min(requested_end, physical_end)
    if final_start > final_end:
        raise RuntimeError("P0052 has no overlap between P0051 and the reliable SvK/Statnett flow range")
    return {
        "p0051_overlap_range": {"start": normalize_utc_text(physical[0]), "end": normalize_utc_text(physical[1]), "rows": physical[2]},
        "requested_range": {"start": format_utc(requested_start), "end": format_utc(requested_end)},
        "source_available_range": {"start": format_utc(FLOW_SOURCE_START), "end": format_utc(physical_end), "note": "SvK/Statnett flow endpoint returned 500 for tested 2024/2025 timestamps. P0052 defaults to the recent reliable P0051 overlap from 2026-05-01 for practical full quarter-hour ingestion."},
        "final_ingested_range": {"start": format_utc(final_start), "end": format_utc(final_end)},
        "missing_range_reason": "Capacity is blocked without ENTSO-E token. Flow/import-export source history is partial; older P0051 overlap is not synthesized.",
    }


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return bool(conn.execute("SELECT 1 FROM sqlite_master WHERE type IN ('table','view') AND name=?", (table,)).fetchone())


def load_existing_transfer_tables(conn: sqlite3.Connection, expected_range: dict[str, str]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]] | None:
    if not table_exists(conn, RAW_TABLE) or not table_exists(conn, CANONICAL_TABLE) or not table_exists(conn, WIDE_TABLE):
        return None
    row = conn.execute(f"SELECT MIN(timestamp_utc), MAX(timestamp_utc), COUNT(*) FROM {WIDE_TABLE}").fetchone()
    if not row or normalize_utc_text(row[0]) != normalize_utc_text(expected_range["start"]) or normalize_utc_text(row[1]) != normalize_utc_text(expected_range["end"]):
        return None
    raw = [dict(item) for item in conn.execute(f"SELECT * FROM {RAW_TABLE} ORDER BY timestamp_utc, source_dataset, border_id, measure")]
    hourly = [dict(item) for item in conn.execute(f"SELECT * FROM {CANONICAL_TABLE} ORDER BY timestamp_utc, source_dataset, border_id, measure")]
    wide = [dict(item) for item in conn.execute(f"SELECT * FROM {WIDE_TABLE} ORDER BY timestamp_utc")]
    return raw, hourly, wide


def fetch_svk_flow_period(start: datetime, end: datetime, *, workers: int = 8) -> list[dict[str, object]]:
    timestamps = list(quarter_hours(start, end))
    observations: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        future_map = {executor.submit(fetch_and_parse_snapshot, ts): ts for ts in timestamps}
        for future in as_completed(future_map):
            observations.extend(future.result())
    return sorted(observations, key=lambda row: (str(row["timestamp_utc"]), str(row["source_dataset"]), str(row["border_id"]), str(row["measure"])))


def fetch_and_parse_snapshot(timestamp_utc: datetime) -> list[dict[str, object]]:
    try:
        payload = fetch_svk_flow_snapshot(timestamp_utc)
    except (subprocess.SubprocessError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return [quality_observation(timestamp_utc, "fetch_error")]
    return parse_svk_flow_payload(payload, timestamp_utc)


def fetch_svk_flow_snapshot(timestamp_utc: datetime, timeout: float = 30.0) -> object:
    url = SVK_FLOW_URL.format(ticks=epoch_millis(timestamp_utc))
    headers = {
        "User-Agent": "smart-home-p0052/1.0",
        "Referer": "https://www.svk.se/en/national-grid/the-control-room/",
    }
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError:
        cmd = ["curl", "-fsSL", "-H", f"Referer: {headers['Referer']}", "-H", f"User-Agent: {headers['User-Agent']}", url]
        return json.loads(subprocess.check_output(cmd, timeout=timeout, stderr=subprocess.DEVNULL).decode("utf-8"))


def parse_svk_flow_payload(payload: object, requested_timestamp: datetime) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if not isinstance(payload, dict):
        return [quality_observation(requested_timestamp, "invalid_payload")]
    last_updated = epoch_millis_to_utc(payload.get("LastUpdated")) if payload.get("LastUpdated") is not None else ""
    datasets = payload.get("Data", [])
    if not isinstance(datasets, list):
        return [quality_observation(requested_timestamp, "invalid_data")]
    for dataset in datasets:
        if not isinstance(dataset, dict):
            continue
        if dataset.get("id") == "1":
            for item in dataset.get("data", []):
                if isinstance(item, dict) and item.get("id") in SWEDISH_BORDERS:
                    rows.extend(parse_signed_border_flow(item, requested_timestamp, last_updated))
        elif dataset.get("id") == "2":
            for country in dataset.get("data", []):
                if isinstance(country, dict) and country.get("id") == "SE":
                    for area in country.get("ElectricalAreas") or []:
                        if isinstance(area, dict) and area.get("AreaName") in SE_ZONES:
                            rows.extend(parse_zone_import_export(area, requested_timestamp, last_updated))
    return rows


def parse_signed_border_flow(item: dict[str, object], timestamp_utc: datetime, last_updated: str) -> list[dict[str, object]]:
    border_id = str(item["id"])
    value = float(item.get("value") or 0.0)
    left, right = border_id.split("_", 1)
    rows = [
        source_observation(timestamp_utc, "SvK Kontrollrummet / Statnett", "map/flow", left, right, border_id, "signed_flow_mw", value, "MW", "flow-based-or-control-room", "control_room_flow", last_updated, "ok")
    ]
    rows.extend(directed_border_values(timestamp_utc, border_id, value, last_updated))
    return rows


def directed_border_values(timestamp_utc: datetime, border_id: str, signed_value: float, last_updated: str = "") -> list[dict[str, object]]:
    left, right = border_id.split("_", 1)
    if signed_value >= 0:
        from_area, to_area, value = left, right, signed_value
    else:
        from_area, to_area, value = right, left, abs(signed_value)
    return [source_observation(timestamp_utc, "SvK Kontrollrummet / Statnett", "map/flow", from_area, to_area, border_id, "flow_mw", value, "MW", "flow-based-or-control-room", "control_room_flow", last_updated, "ok")]


def parse_zone_import_export(area: dict[str, object], timestamp_utc: datetime, last_updated: str) -> list[dict[str, object]]:
    zone = str(area["AreaName"])
    imp = float(area.get("Import") or 0.0)
    exp = float(area.get("Export") or 0.0)
    return [
        source_observation(timestamp_utc, "SvK Kontrollrummet / Statnett", "map/flow/netto", "external", zone, zone, "import_mw", imp, "MW", "not_capacity", "control_room_import_export", last_updated, "ok"),
        source_observation(timestamp_utc, "SvK Kontrollrummet / Statnett", "map/flow/netto", zone, "external", zone, "export_mw", exp, "MW", "not_capacity", "control_room_import_export", last_updated, "ok"),
        source_observation(timestamp_utc, "SvK Kontrollrummet / Statnett", "map/flow/netto", "external", zone, zone, "net_import_mw", imp - exp, "MW", "not_capacity", "control_room_import_export", last_updated, "ok"),
    ]


def source_observation(
    timestamp_utc: datetime,
    source_name: str,
    source_dataset: str,
    from_area: str,
    to_area: str,
    border_id: str,
    measure: str,
    value: float,
    unit: str,
    capacity_method_label: str,
    flow_type_label: str,
    source_updated_at_utc: str,
    quality_flag: str,
) -> dict[str, object]:
    return {
        "timestamp_utc": format_utc(timestamp_utc),
        "model_cet_timestamp": format_utc(timestamp_utc + timedelta(hours=1)),
        "model_cet_date": (timestamp_utc + timedelta(hours=1)).date().isoformat(),
        "model_cet_hour": (timestamp_utc + timedelta(hours=1)).hour,
        "source_name": source_name,
        "source_dataset": source_dataset,
        "from_area": from_area,
        "to_area": to_area,
        "border_id": border_id,
        "measure": measure,
        "value": value,
        "unit": unit,
        "capacity_method_label": capacity_method_label,
        "flow_type_label": flow_type_label,
        "ingested_at_utc": format_utc(datetime.now(timezone.utc)),
        "source_updated_at_utc": source_updated_at_utc,
        "quality_flag": quality_flag,
    }


def quality_observation(timestamp_utc: datetime, quality_flag: str) -> dict[str, object]:
    return source_observation(timestamp_utc, "SvK Kontrollrummet / Statnett", "map/flow", "", "", "", "fetch_status", float("nan"), "", "not_capacity", "control_room_flow", "", quality_flag)


def aggregate_hourly(observations: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str, str, str, str, str, str, str, str], list[float]] = defaultdict(list)
    latest_update: dict[tuple[str, str, str, str, str, str, str, str, str, str, str], str] = {}
    flags: dict[tuple[str, str, str, str, str, str, str, str, str, str, str], set[str]] = defaultdict(set)
    for obs in observations:
        if obs["measure"] == "fetch_status" or not is_finite(obs["value"]):
            continue
        hour = parse_utc(str(obs["timestamp_utc"])).replace(minute=0, second=0, microsecond=0)
        key = (
            format_utc(hour),
            str(obs["source_name"]),
            str(obs["source_dataset"]),
            str(obs["from_area"]),
            str(obs["to_area"]),
            str(obs["border_id"]),
            str(obs["measure"]),
            str(obs["unit"]),
            str(obs["capacity_method_label"]),
            str(obs["flow_type_label"]),
            str(obs["quality_flag"]),
        )
        grouped[key].append(float(obs["value"]))
        latest_update[key] = str(obs["source_updated_at_utc"])
        flags[key].add(str(obs["quality_flag"]))
    rows = []
    for key, values in sorted(grouped.items()):
        hour = parse_utc(key[0])
        rows.append({
            "timestamp_utc": key[0],
            "model_cet_timestamp": format_utc(hour + timedelta(hours=1)),
            "model_cet_date": (hour + timedelta(hours=1)).date().isoformat(),
            "model_cet_hour": (hour + timedelta(hours=1)).hour,
            "source_name": key[1],
            "source_dataset": key[2],
            "from_area": key[3],
            "to_area": key[4],
            "border_id": key[5],
            "measure": key[6],
            "value": sum(values) / len(values),
            "unit": key[7],
            "capacity_method_label": key[8],
            "flow_type_label": key[9],
            "ingested_at_utc": format_utc(datetime.now(timezone.utc)),
            "source_updated_at_utc": latest_update.get(key, ""),
            "quality_flag": "ok" if flags[key] == {"ok"} else ",".join(sorted(flags[key])),
            "source_quarter_hours": len(values),
        })
    return rows


def build_wide_hourly(hourly_rows: list[dict[str, object]], physical_rows: dict[str, dict[str, float]] | None = None) -> list[dict[str, object]]:
    by_hour: dict[str, dict[str, object]] = {}
    for row in hourly_rows:
        ts = str(row["timestamp_utc"])
        wide = by_hour.setdefault(ts, base_wide_row(ts))
        measure = str(row["measure"])
        border = str(row["border_id"]).lower()
        value = float(row["value"])
        if measure == "signed_flow_mw" and str(row["border_id"]) in INTERNAL_BORDERS:
            column = f"signed_flow_{border}_mw"
            wide[column] = value
        elif measure in {"import_mw", "export_mw", "net_import_mw"} and row["border_id"] in SE_ZONES:
            zone = str(row["border_id"]).lower()
            wide[f"{measure.replace('_mw', '')}_{zone}_mw"] = value
    for wide in by_hour.values():
        fill_directional_internal_flow(wide)
        derive_import_export_features(wide)
        attach_physical_residuals(wide, physical_rows or {})
    return [by_hour[ts] for ts in sorted(by_hour)]


def base_wide_row(timestamp_utc: str) -> dict[str, object]:
    dt = parse_utc(timestamp_utc)
    row: dict[str, object] = {
        "timestamp_utc": timestamp_utc,
        "model_cet_timestamp": format_utc(dt + timedelta(hours=1)),
        "model_cet_date": (dt + timedelta(hours=1)).date().isoformat(),
        "model_cet_hour": (dt + timedelta(hours=1)).hour,
        "flow_based_market_coupling_flag": flow_based_market_coupling_flag(timestamp_utc),
        "flow_based_go_live_date": FLOW_BASED_GO_LIVE.date().isoformat(),
        "capacity_method_label": "capacity_unavailable_svk_flow_only",
    }
    for border in INTERNAL_BORDERS:
        col = border.lower()
        row[f"signed_flow_{col}_mw"] = None
        row[f"flow_{col}_mw"] = None
        left, right = col.split("_", 1)
        row[f"capacity_{left}_to_{right}_mw"] = None
        row[f"capacity_{right}_to_{left}_mw"] = None
    for zone in ("se1", "se2", "se3", "se4"):
        row[f"import_{zone}_mw"] = None
        row[f"export_{zone}_mw"] = None
        row[f"net_import_{zone}_mw"] = None
        row[f"balance_residual_{zone}"] = None
    row.update({
        "utilization_se1_se2_north_to_south": None,
        "utilization_se2_se3_north_to_south": None,
        "utilization_se3_se4_north_to_south": None,
        "north_to_south_capacity_min": None,
        "north_to_south_flow_min_or_chain_proxy": None,
        "north_to_south_bottleneck_margin": None,
        "se3_import_pressure": None,
        "se4_import_pressure": None,
        "south_import_pressure": None,
        "north_export_pressure": None,
    })
    return row


def fill_directional_internal_flow(wide: dict[str, object]) -> None:
    signed_values = []
    for border in INTERNAL_BORDERS:
        col = border.lower()
        signed = wide.get(f"signed_flow_{col}_mw")
        if signed is None:
            continue
        signed_f = float(signed)
        wide[f"flow_{col}_mw"] = signed_f
        left, right = col.split("_", 1)
        wide[f"flow_{left}_to_{right}_mw"] = max(0.0, signed_f)
        wide[f"flow_{right}_to_{left}_mw"] = max(0.0, -signed_f)
        signed_values.append(max(0.0, signed_f))
    if signed_values:
        wide["north_to_south_flow_min_or_chain_proxy"] = min(signed_values)


def derive_import_export_features(wide: dict[str, object]) -> None:
    for zone in ("se1", "se2", "se3", "se4"):
        imp = none_to_zero(wide.get(f"import_{zone}_mw"))
        exp = none_to_zero(wide.get(f"export_{zone}_mw"))
        if wide.get(f"net_import_{zone}_mw") is None and (imp is not None or exp is not None):
            wide[f"net_import_{zone}_mw"] = none_to_zero(imp) - none_to_zero(exp)
    wide["se3_import_pressure"] = wide.get("net_import_se3_mw")
    wide["se4_import_pressure"] = wide.get("net_import_se4_mw")
    if wide.get("net_import_se3_mw") is not None and wide.get("net_import_se4_mw") is not None:
        wide["south_import_pressure"] = float(wide["net_import_se3_mw"]) + float(wide["net_import_se4_mw"])
    if wide.get("net_import_se1_mw") is not None and wide.get("net_import_se2_mw") is not None:
        wide["north_export_pressure"] = -(float(wide["net_import_se1_mw"]) + float(wide["net_import_se2_mw"]))


def attach_physical_residuals(wide: dict[str, object], physical_rows: dict[str, dict[str, float]]) -> None:
    physical = physical_rows.get(str(wide["timestamp_utc"]))
    if not physical:
        return
    for zone in ("se1", "se2", "se3", "se4"):
        prod = physical.get(f"production_{zone}")
        cons = physical.get(f"consumption_{zone}")
        imp = wide.get(f"import_{zone}_mw")
        exp = wide.get(f"export_{zone}_mw")
        if None not in (prod, cons, imp, exp):
            wide[f"balance_residual_{zone}"] = float(prod) + float(imp) - float(cons) - float(exp)


def none_to_zero(value: object) -> float:
    return 0.0 if value is None else float(value)


def capacity_utilization(flow: object, capacity: object) -> float | None:
    if flow is None or capacity is None:
        return None
    capacity_f = float(capacity)
    if capacity_f <= 0:
        return None
    return max(0.0, float(flow)) / capacity_f


def load_physical_rows(conn: sqlite3.Connection) -> dict[str, dict[str, float]]:
    if not table_exists(conn, PHYSICAL_TABLE):
        return {}
    rows = {}
    for row in conn.execute(f"SELECT timestamp_utc, consumption_se1, production_se1, consumption_se2, production_se2, consumption_se3, production_se3, consumption_se4, production_se4 FROM {PHYSICAL_TABLE}"):
        rows[normalize_utc_text(row[0])] = {
            "consumption_se1": row[1],
            "production_se1": row[2],
            "consumption_se2": row[3],
            "production_se2": row[4],
            "consumption_se3": row[5],
            "production_se3": row[6],
            "consumption_se4": row[7],
            "production_se4": row[8],
        }
    return rows


def persist_transfer_flow(conn: sqlite3.Connection, raw_rows: list[dict[str, object]], hourly_rows: list[dict[str, object]], wide_rows: list[dict[str, object]]) -> None:
    conn.execute(f"DROP TABLE IF EXISTS {RAW_TABLE}")
    conn.execute(f"DROP TABLE IF EXISTS {CANONICAL_TABLE}")
    conn.execute(f"DROP TABLE IF EXISTS {WIDE_TABLE}")
    create_long_table(conn, RAW_TABLE, include_source_quarters=False)
    create_long_table(conn, CANONICAL_TABLE, include_source_quarters=True)
    create_wide_table(conn, WIDE_TABLE)
    insert_rows(conn, RAW_TABLE, raw_rows)
    insert_rows(conn, CANONICAL_TABLE, hourly_rows)
    insert_rows(conn, WIDE_TABLE, wide_rows)
    conn.commit()


def create_long_table(conn: sqlite3.Connection, table: str, *, include_source_quarters: bool) -> None:
    extra = ", source_quarter_hours INTEGER" if include_source_quarters else ""
    conn.execute(f"""
        CREATE TABLE {table} (
            timestamp_utc TEXT NOT NULL,
            model_cet_timestamp TEXT NOT NULL,
            model_cet_date TEXT NOT NULL,
            model_cet_hour INTEGER NOT NULL,
            source_name TEXT NOT NULL,
            source_dataset TEXT NOT NULL,
            from_area TEXT NOT NULL,
            to_area TEXT NOT NULL,
            border_id TEXT NOT NULL,
            measure TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL,
            capacity_method_label TEXT NOT NULL,
            flow_type_label TEXT NOT NULL,
            ingested_at_utc TEXT NOT NULL,
            source_updated_at_utc TEXT,
            quality_flag TEXT NOT NULL{extra}
        )
    """)
    conn.execute(f"CREATE UNIQUE INDEX {table}_uk ON {table}(timestamp_utc, source_name, source_dataset, from_area, to_area, border_id, measure, capacity_method_label, flow_type_label)")


def create_wide_table(conn: sqlite3.Connection, table: str) -> None:
    conn.execute(f"""
        CREATE TABLE {table} (
            timestamp_utc TEXT PRIMARY KEY,
            model_cet_timestamp TEXT NOT NULL,
            model_cet_date TEXT NOT NULL,
            model_cet_hour INTEGER NOT NULL,
            flow_based_market_coupling_flag INTEGER NOT NULL,
            flow_based_go_live_date TEXT NOT NULL,
            capacity_method_label TEXT NOT NULL,
            signed_flow_se1_se2_mw REAL,
            signed_flow_se2_se3_mw REAL,
            signed_flow_se3_se4_mw REAL,
            flow_se1_se2_mw REAL,
            flow_se2_se3_mw REAL,
            flow_se3_se4_mw REAL,
            flow_se1_to_se2_mw REAL,
            flow_se2_to_se1_mw REAL,
            flow_se2_to_se3_mw REAL,
            flow_se3_to_se2_mw REAL,
            flow_se3_to_se4_mw REAL,
            flow_se4_to_se3_mw REAL,
            capacity_se1_to_se2_mw REAL,
            capacity_se2_to_se1_mw REAL,
            capacity_se2_to_se3_mw REAL,
            capacity_se3_to_se2_mw REAL,
            capacity_se3_to_se4_mw REAL,
            capacity_se4_to_se3_mw REAL,
            utilization_se1_se2_north_to_south REAL,
            utilization_se2_se3_north_to_south REAL,
            utilization_se3_se4_north_to_south REAL,
            north_to_south_capacity_min REAL,
            north_to_south_flow_min_or_chain_proxy REAL,
            north_to_south_bottleneck_margin REAL,
            import_se1_mw REAL,
            export_se1_mw REAL,
            net_import_se1_mw REAL,
            import_se2_mw REAL,
            export_se2_mw REAL,
            net_import_se2_mw REAL,
            import_se3_mw REAL,
            export_se3_mw REAL,
            net_import_se3_mw REAL,
            import_se4_mw REAL,
            export_se4_mw REAL,
            net_import_se4_mw REAL,
            balance_residual_se1 REAL,
            balance_residual_se2 REAL,
            balance_residual_se3 REAL,
            balance_residual_se4 REAL,
            se3_import_pressure REAL,
            se4_import_pressure REAL,
            south_import_pressure REAL,
            north_export_pressure REAL
        )
    """)


def insert_rows(conn: sqlite3.Connection, table: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    columns = list(rows[0].keys())
    placeholders = ", ".join("?" for _ in columns)
    conn.executemany(
        f"INSERT OR REPLACE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
        [[row.get(column) for column in columns] for row in rows],
    )


def validate_transfer_flow(conn: sqlite3.Connection, hourly_rows: list[dict[str, object]], wide_rows: list[dict[str, object]], ranges: dict[str, object]) -> dict[str, object]:
    duplicates = len(hourly_rows) - len({(r["timestamp_utc"], r["source_name"], r["source_dataset"], r["from_area"], r["to_area"], r["border_id"], r["measure"], r["capacity_method_label"], r["flow_type_label"]) for r in hourly_rows})
    nonfinite = sum(1 for row in hourly_rows if not is_finite(row["value"]))
    negative_capacity = sum(1 for row in hourly_rows if row["measure"] == "capacity_mw" and float(row["value"]) < 0)
    start = parse_utc(str(ranges["final_ingested_range"]["start"]))
    end = parse_utc(str(ranges["final_ingested_range"]["end"]))
    expected_hours = int((end - start).total_seconds() // 3600) + 1
    missing_hours = {}
    for measure in ["signed_flow_mw", "import_mw", "export_mw", "net_import_mw"]:
        count = len({row["timestamp_utc"] for row in hourly_rows if row["measure"] == measure})
        missing_hours[measure] = max(0, expected_hours - count)
    join_count = 0
    if table_exists(conn, PHYSICAL_TABLE) and wide_rows:
        placeholders = ",".join("?" for _ in wide_rows)
        join_count = conn.execute(f"SELECT COUNT(*) FROM {PHYSICAL_TABLE} WHERE timestamp_utc IN ({placeholders})", [row["timestamp_utc"] for row in wide_rows]).fetchone()[0]
    return {
        "ok": duplicates == 0 and nonfinite == 0 and negative_capacity == 0 and bool(wide_rows),
        "duplicates": duplicates,
        "nonfinite_values": nonfinite,
        "negative_capacity_values": negative_capacity,
        "expected_hours": expected_hours,
        "missing_hours": missing_hours,
        "joined_p0051_hours": join_count,
        "wide_rows": len(wide_rows),
        "capacity_available": False,
        "capacity_blocker": "ENTSO-E Transparency API requires a security token; SvK/Statnett flow endpoint has no capacity fields.",
        "row_counts_by_measure": dict(Counter(str(row["measure"]) for row in hourly_rows)),
    }


def run_initial_diagnostics(conn: sqlite3.Connection, wide_rows: list[dict[str, object]]) -> dict[str, object]:
    price_table = "se3_se1_demand_response_analysis_v1"
    if not table_exists(conn, price_table):
        price_table = "se3_se1_bottleneck_training_dataset_v1"
    if not table_exists(conn, price_table):
        return {"joined_rows": 0, "reason": "no price table"}
    columns = table_columns(conn, price_table)
    se3_price_column = "se3_price_eur_mwh" if "se3_price_eur_mwh" in columns else "se3_price"
    se3_minus_se1_column = "se3_minus_se1_eur_mwh" if "se3_minus_se1_eur_mwh" in columns else "se3_minus_se1"
    price_rows = {
        normalize_utc_text(row[0]): {"se3_price": row[1], "se3_minus_se1": row[2]}
        for row in conn.execute(f"SELECT timestamp_utc, {se3_price_column}, {se3_minus_se1_column} FROM {price_table}")
    }
    joined = []
    for row in wide_rows:
        price = price_rows.get(str(row["timestamp_utc"]))
        if price:
            merged = dict(row)
            merged.update(price)
            joined.append(merged)
    correlations = {
        "se3_price_vs_net_import_se3_mw": correlation(joined, "se3_price", "net_import_se3_mw"),
        "se3_price_vs_south_import_pressure": correlation(joined, "se3_price", "south_import_pressure"),
        "se3_price_vs_north_to_south_bottleneck_margin": correlation(joined, "se3_price", "north_to_south_bottleneck_margin"),
        "se3_minus_se1_vs_net_import_se3_mw": correlation(joined, "se3_minus_se1", "net_import_se3_mw"),
        "se3_minus_se1_vs_south_import_pressure": correlation(joined, "se3_minus_se1", "south_import_pressure"),
        "se3_minus_se1_vs_north_to_south_bottleneck_margin": correlation(joined, "se3_minus_se1", "north_to_south_bottleneck_margin"),
        "se3_minus_se1_vs_utilization_se2_se3_north_to_south": correlation(joined, "se3_minus_se1", "utilization_se2_se3_north_to_south"),
        "se3_minus_se1_vs_utilization_se3_se4_north_to_south": correlation(joined, "se3_minus_se1", "utilization_se3_se4_north_to_south"),
    }
    return {
        "price_table": price_table,
        "price_columns": {"se3_price": se3_price_column, "se3_minus_se1": se3_minus_se1_column},
        "joined_rows": len(joined),
        "correlations": correlations,
        "note": "Diagnostics are explanatory only. Capacity/utilization correlations are null because capacity is unavailable.",
    }


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {str(row[1]) for row in conn.execute(f"PRAGMA table_info({table})")}


def correlation(rows: list[dict[str, object]], x_key: str, y_key: str) -> float | None:
    pairs = [(float(row[x_key]), float(row[y_key])) for row in rows if row.get(x_key) is not None and row.get(y_key) is not None and is_finite(row[x_key]) and is_finite(row[y_key])]
    if len(pairs) < 2:
        return None
    xs, ys = zip(*pairs)
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def source_discovery() -> dict[str, object]:
    return {
        "investigated": [
            {
                "source_name": "eSett Open Data",
                "base_url": "https://api.opendata.esett.com",
                "result": "No transfer capacity, border flow or import/export endpoint found in OpenAPI contract.",
                "authentication": "none",
            },
            {
                "source_name": "Svenska kraftnat Kontrollrummet / Statnett",
                "base_url": "https://www.svk.se",
                "endpoint_or_download_path": "/services/controlroom/v2/map/flow?ticks=<epoch_ms>",
                "authentication": "none observed; browser-style User-Agent and Referer are required for reliable access",
                "resolution": "quarter-hour display values",
                "units": "MW",
                "direction_convention": "positive A_B means A to B; negative means B to A",
                "selected": True,
            },
            {
                "source_name": "ENTSO-E Transparency Platform",
                "base_url": "https://web-api.tp.entsoe.eu/api",
                "result": "HTTP 401 without security token. Candidate for historical capacity/flow once token is available.",
                "authentication": "security token required",
                "selected": False,
            },
        ],
        "selected_source": "Svenska kraftnat Kontrollrummet / Statnett",
        "selection_reason": "Only discovered auth-free machine-readable source with SE1-SE4 border flows and zone import/export values.",
    }


def source_contracts() -> dict[str, object]:
    return {
        "svk_statnett_flow": {
            "url": SVK_FLOW_URL,
            "query_parameters": {"ticks": "epoch milliseconds for requested quarter-hour"},
            "response_shape": "Data id=1 contains border signed flows; Data id=2 contains country/area import/export; LastUpdated is epoch milliseconds.",
            "available_borders": sorted(SWEDISH_BORDERS),
            "available_measures": ["signed_flow_mw", "flow_mw", "import_mw", "export_mw", "net_import_mw"],
            "capacity_measures": [],
            "unit": "MW",
        },
        "entsoe_capacity_blocker": {
            "url": "https://web-api.tp.entsoe.eu/api",
            "authentication": "securityToken required; unauthenticated request returned HTTP 401",
        },
    }


def derived_feature_definitions() -> dict[str, str]:
    return {
        "net_import_z": "import_z - export_z; positive means the zone is supplied by imports.",
        "balance_residual_z": "production_z + import_z - consumption_z - export_z. Reported only as compatibility diagnostic.",
        "south_import_pressure": "net_import_se3_mw + net_import_se4_mw",
        "north_export_pressure": "-(net_import_se1_mw + net_import_se2_mw)",
        "north_to_south_flow_min_or_chain_proxy": "minimum positive internal north-to-south flow across SE1-SE2, SE2-SE3 and SE3-SE4 where present.",
        "capacity_utilization": "null in P0052 because capacity is unavailable from selected auth-free source.",
    }


def forecast_safety_classification() -> dict[str, str]:
    return {
        "signed_flow_mw": "historical_observed_only",
        "flow_mw": "historical_observed_only",
        "import_mw": "historical_observed_only",
        "export_mw": "historical_observed_only",
        "net_import_mw": "requires_separate_forecast_model",
        "capacity_mw": "not_forecast_safe_until_source_available",
        "south_import_pressure": "requires_separate_forecast_model",
        "north_export_pressure": "requires_separate_forecast_model",
    }


def write_p0052_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "CHANGELOG.md": changelog_text(summary),
        "source-discovery.md": json_md("P0052 source discovery", summary["source_discovery"]),
        "source-contracts.md": json_md("P0052 source contracts", summary["source_contracts"]),
        "database-contract.md": database_contract_text(),
        "ingestion-summary.md": json_md("P0052 ingestion summary", {"row_counts": summary["row_counts"], "ranges": summary["ranges"]}),
        "time-normalization-and-dst.md": "# P0052 time normalization and DST\n\nSvK `ticks` are epoch milliseconds and are normalized to UTC. Quarter-hour MW values are aggregated to hourly mean MW. Fixed-CET fields use `timestamp_utc + 1h` all year, so DST 23/25-hour local days do not change the primary key.\n",
        "data-validation.md": json_md("P0052 data validation", summary["validation"]),
        "coverage-and-missingness.md": json_md("P0052 coverage and missingness", {"ranges": summary["ranges"], "missing_hours": summary["validation"]["missing_hours"]}),
        "direction-conventions.md": "# P0052 direction conventions\n\nSvK border id `A_B` with positive value means flow from A to B. Negative value means flow from B to A. Zone import/export follows SvK `ElectricalAreas` values; `net_import = import - export`.\n",
        "flow-based-era-review.md": "# P0052 flow-based era review\n\nNordic flow-based market coupling go-live is recorded as 2024-10-29. P0052's selected SvK/Statnett flow range is after go-live, so all ingested rows have `flow_based_market_coupling_flag = 1`. Capacity concepts remain unavailable and are not mixed with flow values.\n",
        "derived-feature-definitions.md": json_md("P0052 derived feature definitions", summary["derived_features"]),
        "import-export-balance-check.md": "# P0052 import/export balance check\n\nBalance residual fields are stored as `production + import - consumption - export` where P0051 physical rows join. Residuals are diagnostic only because SvK/Statnett flow/import-export concepts may not close exactly against eSett production/consumption definitions.\n",
        "initial-capacity-flow-diagnostics.md": json_md("P0052 initial capacity/flow diagnostics", summary["diagnostics"]),
        "forecast-safety-classification.md": json_md("P0052 forecast-safety classification", summary["forecast_safety"]),
        "next-package-recommendation.md": "# P0052 next package recommendation\n\nP0053 should use P0051 production/consumption plus P0052 observed flow/import-export only as historical explanatory signals unless separate forecast-safe flow/import-export inputs are built. Capacity work should be a separate token-backed ENTSO-E or equivalent source package.\n",
        "component-attribution-summary.md": component_summary_text(summary),
    }
    for name, content in files.items():
        (evidence_dir / name).write_text(content, encoding="utf-8")
    json_files = {
        "source-contracts.json": summary["source_contracts"],
        "coverage-summary.json": {"ranges": summary["ranges"], "missing_hours": summary["validation"]["missing_hours"]},
        "validation-summary.json": summary["validation"],
        "diagnostics-summary.json": summary["diagnostics"],
    }
    for name, payload in json_files.items():
        (evidence_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {name: str(evidence_dir / name) for name in files | json_files}


def json_md(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0052 changelog

- Selected SvK Kontrollrummet / Statnett as the auth-free source for observed SE1-SE4 border flows and zone import/export.
- Built `{CANONICAL_TABLE}` and `{WIDE_TABLE}` with {summary['row_counts']['hourly_rows']} canonical rows and {summary['row_counts']['wide_rows']} wide hourly rows.
- Documented ENTSO-E token blocker for historical capacity ingestion; no capacity values were invented.
- Result status: {summary['status']}.
- No continental price pressure, SE1-to-SE3 anchoring, API, production model, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.
"""


def database_contract_text() -> str:
    return f"""# P0052 database contract

Tables created/rebuilt:

- `{RAW_TABLE}`
- `{CANONICAL_TABLE}`
- `{WIDE_TABLE}`

Long-format columns include timestamp, fixed-CET fields, source, dataset, from/to area, border id, measure, value, unit, capacity method label, flow type label and quality flag.

Wide columns include internal SE1-SE2/SE2-SE3/SE3-SE4 signed flows, SE1-SE4 import/export/net import, balance residual diagnostics, pressure features and nullable capacity/utilization fields.
"""


def component_summary_text(summary: dict[str, object]) -> str:
    validation = summary["validation"]
    diagnostics = summary["diagnostics"]
    return "\n".join([
        "# P0052 component attribution summary",
        "",
        f"Status: {summary['status']}",
        "1. Sources investigated: eSett Open Data, Svenska kraftnat Kontrollrummet / Statnett and ENTSO-E Transparency Platform.",
        "2. Selected source: SvK Kontrollrummet / Statnett, because it is auth-free and exposes SE1-SE4 border flows plus zone import/export values.",
        "3. Swedish internal border flow values were available for SE1-SE2, SE2-SE3 and SE3-SE4 over the partial reliable range.",
        "4. Historical capacity values were not available from the selected source; ENTSO-E requires a security token.",
        "5. Zone-level import/export was computed from SvK `ElectricalAreas` values for SE1-SE4.",
        "6. Import/export includes internal Swedish and external neighbour borders as represented by the SvK/Statnett flow map.",
        f"7. Historical range ingested: {summary['ranges']['final_ingested_range']}.",
        f"8. Tables: `{RAW_TABLE}`, `{CANONICAL_TABLE}`, `{WIDE_TABLE}`.",
        "9. Units/direction: MW; positive `A_B` signed flow means A to B, negative means B to A.",
        f"10. Row counts: {summary['row_counts']}.",
        f"11. Missingness/quality: {validation}.",
        "12. Capacity concept after flow-based go-live is not stored because no capacity source was available.",
        f"13. Derived features: {summary['derived_features']}.",
        f"14. Initial diagnostics: {diagnostics}.",
        "15. Import/export features are strong enough for historical P0053 physical-regime diagnostics, not for forecast use without separate forecasts.",
        f"16. Forecast safety: {summary['forecast_safety']}.",
        "17. Confirmed: no continental price pressure levels, no SE1-to-SE3 anchoring, no API, no production model and no device actions.",
        "",
    ])


def quarter_hours(start: datetime, end: datetime):
    current = start.replace(minute=(start.minute // 15) * 15, second=0, microsecond=0)
    while current < end:
        yield current
        current += timedelta(minutes=15)


def flow_based_market_coupling_flag(timestamp_utc: str | datetime) -> int:
    return 1 if parse_utc(timestamp_utc) >= FLOW_BASED_GO_LIVE else 0


def parse_utc(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def normalize_utc_text(value: object) -> str:
    return format_utc(parse_utc(str(value)))


def format_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def epoch_millis(dt: datetime) -> int:
    return int(dt.astimezone(timezone.utc).timestamp() * 1000)


def epoch_millis_to_utc(value: object) -> str:
    return format_utc(datetime.fromtimestamp(float(value) / 1000.0, tz=timezone.utc))


def is_finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def main() -> None:
    result = run_p0052_ingestion()
    print(f"P0052 {result.status}: row_counts={json.dumps(result.row_counts, sort_keys=True)}")


if __name__ == "__main__":
    main()
