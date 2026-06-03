"""P0051 SE1-SE4 physical balance ingestion from eSett Open Data."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import csv
import json
import math
import sqlite3
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics.p0041 import persist_rows, write


PACKAGE_ID = "P0051"
EVIDENCE_DIR = Path("requirements/package-runs/P0051")
ESETT_BASE_URL = "https://api.opendata.esett.com"
RAW_TABLE = "physical_balance_hourly_raw_v1"
CANONICAL_TABLE = "physical_balance_hourly_v1"
WIDE_TABLE = "physical_balance_se1_se4_hourly_v1"
ZONES = {
    "SE1": "10Y1001A1001A44P",
    "SE2": "10Y1001A1001A45N",
    "SE3": "10Y1001A1001A46L",
    "SE4": "10Y1001A1001A47J",
}
PRODUCTION_TYPES = ("hydro", "nuclear", "solar", "thermal", "wind", "windOffshore", "energyStorage", "other", "total")
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
class P0051Result:
    status: str
    row_counts: dict[str, int]
    ranges: dict[str, object]
    evidence: dict[str, str]


def run_p0051_ingestion(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
    chunk_days: int = 31,
) -> P0051Result:
    started = time.monotonic()
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        ranges = load_existing_ranges(conn)
    start = parse_utc(str(ranges["final_overlap_range"]["start"]))
    end = parse_utc(str(ranges["final_overlap_range"]["end"])) + timedelta(hours=1)
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        existing = load_existing_physical_tables(conn, ranges["final_overlap_range"])
        if existing:
            hourly_rows, wide_rows = existing
            observations = []
        else:
            observations = fetch_esett_period(start, end, ZONES, chunk_days=chunk_days)
            hourly_rows = aggregate_hourly(observations)
            wide_rows = build_wide_hourly(hourly_rows)
            persist_physical_balance(conn, hourly_rows, wide_rows)
        diagnostics = run_initial_diagnostics(conn, wide_rows)
    validation = validate_physical_balance(hourly_rows, wide_rows, ranges["final_overlap_range"])
    summary = {
        "status": "PASS" if hourly_rows and wide_rows else "STOP",
        "source_discovery": source_discovery(),
        "source_contracts": source_contracts(),
        "ranges": ranges,
        "row_counts": {
            "observations": len(observations) if observations else "reused_existing_tables",
            "hourly_rows": len(hourly_rows),
            "wide_rows": len(wide_rows),
        },
        "measures": sorted({row["measure"] for row in hourly_rows}),
        "zones": sorted({row["bidding_zone"] for row in hourly_rows}),
        "validation": validation,
        "diagnostics": diagnostics,
        "forecast_safety": forecast_safety_classification(),
        "runtime_seconds": time.monotonic() - started,
        "forbidden_paths": FORBIDDEN_PRODUCTION_PATHS,
    }
    evidence = write_p0051_evidence(Path(evidence_dir), summary)
    return P0051Result(status=str(summary["status"]), row_counts=summary["row_counts"], ranges=ranges, evidence=evidence)


def load_existing_ranges(conn: sqlite3.Connection) -> dict[str, object]:
    candidates = [
        "se3_se1_demand_response_analysis_v1",
        "se3_se1_bottleneck_reservoir_analysis_v1",
        "se3_se1_bottleneck_training_dataset_v1",
    ]
    modeling = None
    for table in candidates:
        if table_exists(conn, table):
            row = conn.execute(f"SELECT MIN(timestamp_utc), MAX(timestamp_utc), COUNT(*) FROM {table}").fetchone()
            modeling = {"table": table, "start": row[0], "end": row[1], "rows": row[2]}
            break
    if not modeling:
        raise RuntimeError("P0051 could not find a current modeling range table")
    weather = {"table": "unknown", "start": modeling["start"], "end": modeling["end"], "rows": 0}
    if table_exists(conn, "weather_area_hourly"):
        row = conn.execute("SELECT MIN(utc_hour_start), MAX(utc_hour_start), COUNT(*) FROM weather_area_hourly").fetchone()
        weather = {"table": "weather_area_hourly", "start": normalize_utc_text(row[0]), "end": normalize_utc_text(row[1]), "rows": row[2]}
    price = {"table": modeling["table"], "start": modeling["start"], "end": modeling["end"], "rows": modeling["rows"]}
    return {
        "existing_price_range": price,
        "existing_weather_range": weather,
        "existing_modeling_range": modeling,
        "final_overlap_range": {"start": modeling["start"], "end": modeling["end"]},
    }


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return bool(conn.execute("SELECT 1 FROM sqlite_master WHERE type IN ('table','view') AND name=?", (table,)).fetchone())


def load_existing_physical_tables(conn: sqlite3.Connection, expected_range: dict[str, str]) -> tuple[list[dict[str, object]], list[dict[str, object]]] | None:
    if not table_exists(conn, CANONICAL_TABLE) or not table_exists(conn, WIDE_TABLE):
        return None
    row = conn.execute(f"SELECT MIN(timestamp_utc), MAX(timestamp_utc), COUNT(*) FROM {WIDE_TABLE}").fetchone()
    if not row or normalize_utc_text(row[0]) != normalize_utc_text(expected_range["start"]) or normalize_utc_text(row[1]) != normalize_utc_text(expected_range["end"]):
        return None
    hourly = [dict(item) for item in conn.execute(f"SELECT * FROM {CANONICAL_TABLE} ORDER BY timestamp_utc, bidding_zone, measure, production_type")]
    wide = [dict(item) for item in conn.execute(f"SELECT * FROM {WIDE_TABLE} ORDER BY timestamp_utc")]
    return hourly, wide


def fetch_esett_period(start: datetime, end: datetime, zones: dict[str, str], *, chunk_days: int = 31) -> list[dict[str, object]]:
    observations: list[dict[str, object]] = []
    current = start
    while current < end:
        chunk_end = min(end, current + timedelta(days=chunk_days))
        for zone, mba in zones.items():
            consumption = fetch_json(esett_url("/EXP15/Consumption", mba, current, chunk_end))
            production = fetch_json(esett_url("/EXP16/Volumes", mba, current, chunk_end))
            observations.extend(parse_esett_consumption(consumption, zone))
            observations.extend(parse_esett_production(production, zone))
        current = chunk_end
    return observations


def esett_url(path: str, mba: str, start: datetime, end: datetime) -> str:
    query = urllib.parse.urlencode({
        "mba": mba,
        "start": format_esett_time(start),
        "end": format_esett_time(end),
    })
    return f"{ESETT_BASE_URL}{path}?{query}"


def fetch_json(url: str, timeout: float = 30.0) -> object:
    request = urllib.request.Request(url, headers={"User-Agent": "smart-home-p0051/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError:
        return json.loads(subprocess.check_output(["curl", "-fsSL", url], timeout=timeout).decode("utf-8"))


def parse_esett_consumption(payload: object, zone: str) -> list[dict[str, object]]:
    output = []
    for item in payload if isinstance(payload, list) else []:
        timestamp = normalize_utc_text(item["timestampUTC"])
        total = item.get("total")
        metered = item.get("metered")
        profiled = item.get("profiled")
        flex = item.get("flex")
        output.append(source_observation(timestamp, zone, "consumption_total", None, positive_consumption(total), "MW", "EXP15/Consumption"))
        if metered is not None:
            output.append(source_observation(timestamp, zone, "consumption_metered", None, positive_consumption(metered), "MW", "EXP15/Consumption"))
        if profiled is not None:
            output.append(source_observation(timestamp, zone, "consumption_profiled", None, positive_consumption(profiled), "MW", "EXP15/Consumption"))
        if flex is not None:
            output.append(source_observation(timestamp, zone, "consumption_flex", None, positive_consumption(flex), "MW", "EXP15/Consumption"))
    return output


def parse_esett_production(payload: object, zone: str) -> list[dict[str, object]]:
    output = []
    for item in payload if isinstance(payload, list) else []:
        timestamp = normalize_utc_text(item["timestampUTC"])
        for production_type in PRODUCTION_TYPES:
            value = item.get(production_type)
            if value is not None:
                measure = "production_total" if production_type == "total" else f"production_{camel_to_snake(production_type)}"
                output.append(source_observation(timestamp, zone, measure, production_type, float(value), "MW", "EXP16/Volumes"))
    return output


def source_observation(timestamp: str, zone: str, measure: str, production_type: str | None, value: float, unit: str, dataset: str) -> dict[str, object]:
    return {
        "timestamp_utc": timestamp,
        "source_name": "eSett Open Data",
        "source_dataset": dataset,
        "bidding_zone": zone,
        "measure": measure,
        "production_type": production_type or "",
        "value": value,
        "unit": unit,
        "quality_flag": "ok",
    }


def positive_consumption(value: object) -> float:
    return abs(float(value or 0.0))


def aggregate_hourly(observations: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str, str, str, str], list[float]] = defaultdict(list)
    for obs in observations:
        hour = parse_utc(str(obs["timestamp_utc"])).replace(minute=0, second=0, microsecond=0).isoformat().replace("+00:00", "Z")
        key = (
            hour,
            str(obs["source_name"]),
            str(obs["source_dataset"]),
            str(obs["bidding_zone"]),
            str(obs["measure"]),
            str(obs["production_type"]),
            str(obs["unit"]),
        )
        grouped[key].append(float(obs["value"]))
    ingested = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows = []
    for key, values in sorted(grouped.items()):
        timestamp, source, dataset, zone, measure, production_type, unit = key
        rows.append({
            "timestamp_utc": timestamp,
            **fixed_cet_fields(timestamp),
            "source_name": source,
            "source_dataset": dataset,
            "bidding_zone": zone,
            "measure": measure,
            "production_type": production_type,
            "value": sum(values) / len(values),
            "unit": unit,
            "ingested_at_utc": ingested,
            "source_updated_at_utc": "",
            "quality_flag": "ok" if len(values) == 4 else f"quarter_count_{len(values)}",
        })
    return rows


def build_wide_hourly(hourly_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_hour: dict[str, dict[str, object]] = {}
    for row in hourly_rows:
        if row["measure"] not in ("consumption_total", "production_total"):
            continue
        hour = str(row["timestamp_utc"])
        target = by_hour.setdefault(hour, {"timestamp_utc": hour, **fixed_cet_fields(hour)})
        zone = str(row["bidding_zone"]).lower()
        if row["measure"] == "consumption_total":
            target[f"consumption_{zone}"] = float(row["value"])
        else:
            target[f"production_{zone}"] = float(row["value"])
    output = []
    for hour in sorted(by_hour):
        row = by_hour[hour]
        for zone in ("se1", "se2", "se3", "se4"):
            row.setdefault(f"consumption_{zone}", 0.0)
            row.setdefault(f"production_{zone}", 0.0)
            row[f"net_load_{zone}"] = float(row[f"consumption_{zone}"]) - float(row[f"production_{zone}"])
        row["production_north"] = float(row["production_se1"]) + float(row["production_se2"])
        row["production_south"] = float(row["production_se3"]) + float(row["production_se4"])
        row["consumption_north"] = float(row["consumption_se1"]) + float(row["consumption_se2"])
        row["consumption_south"] = float(row["consumption_se3"]) + float(row["consumption_se4"])
        row["net_load_north"] = float(row["net_load_se1"]) + float(row["net_load_se2"])
        row["net_load_south"] = float(row["net_load_se3"]) + float(row["net_load_se4"])
        row["net_load_south_minus_north"] = float(row["net_load_south"]) - float(row["net_load_north"])
        row["production_south_minus_north"] = float(row["production_south"]) - float(row["production_north"])
        row["consumption_south_minus_north"] = float(row["consumption_south"]) - float(row["consumption_north"])
        output.append(row)
    return output


def persist_physical_balance(conn: sqlite3.Connection, hourly_rows: list[dict[str, object]], wide_rows: list[dict[str, object]]) -> None:
    persist_rows(conn, RAW_TABLE, hourly_rows)
    persist_rows(conn, CANONICAL_TABLE, hourly_rows)
    persist_rows(conn, WIDE_TABLE, wide_rows)


def validate_physical_balance(hourly_rows: list[dict[str, object]], wide_rows: list[dict[str, object]], expected_range: dict[str, str]) -> dict[str, object]:
    keys = Counter((row["timestamp_utc"], row["source_name"], row["bidding_zone"], row["measure"], row["production_type"]) for row in hourly_rows)
    duplicates = sum(1 for count in keys.values() if count > 1)
    nonfinite = sum(1 for row in hourly_rows if not math.isfinite(float(row["value"])))
    expected_hours = int((parse_utc(expected_range["end"]) - parse_utc(expected_range["start"])).total_seconds() // 3600) + 1
    missing = {}
    for zone in ZONES:
        for measure in ("consumption_total", "production_total"):
            present = {row["timestamp_utc"] for row in hourly_rows if row["bidding_zone"] == zone and row["measure"] == measure}
            missing[f"{zone}_{measure}"] = max(0, expected_hours - len(present))
    negative_values = sum(1 for row in hourly_rows if float(row["value"]) < 0)
    by_measure = dict(sorted(Counter(f"{row['bidding_zone']}_{row['measure']}" for row in hourly_rows).items()))
    return {
        "ok": duplicates == 0 and nonfinite == 0 and len(wide_rows) > 0,
        "duplicates": duplicates,
        "nonfinite_values": nonfinite,
        "negative_values_after_normalization": negative_values,
        "expected_hours": expected_hours,
        "missing_hours": missing,
        "row_counts_by_zone_measure": by_measure,
    }


def run_initial_diagnostics(conn: sqlite3.Connection, wide_rows: list[dict[str, object]]) -> dict[str, object]:
    price_table = "se3_se1_demand_response_analysis_v1" if table_exists(conn, "se3_se1_demand_response_analysis_v1") else "se3_se1_bottleneck_training_dataset_v1"
    conn.row_factory = sqlite3.Row
    price_rows = {
        normalize_utc_text(str(row["timestamp_utc"])): dict(row)
        for row in conn.execute(f"SELECT timestamp_utc, se3_price, se3_minus_se1, se3_is_top4_day, se3_is_top8_day, se3_is_bottom4_day, se3_is_bottom8_day FROM {price_table}")
    }
    joined = []
    for row in wide_rows:
        price = price_rows.get(normalize_utc_text(str(row["timestamp_utc"])))
        if price:
            item = dict(row)
            item.update(price)
            joined.append(item)
    fields = ("consumption_se3", "production_se3", "net_load_se3", "net_load_south_minus_north", "production_south_minus_north", "consumption_south_minus_north")
    correlations = {}
    for target in ("se3_price", "se3_minus_se1"):
        for field in fields:
            correlations[f"{target}_vs_{field}"] = pearson([float(row[target]) for row in joined], [float(row[field]) for row in joined])
    events = {}
    for flag in ("se3_is_top4_day", "se3_is_top8_day", "se3_is_bottom4_day", "se3_is_bottom8_day"):
        subset = [row for row in joined if int(row.get(flag) or 0)]
        other = [row for row in joined if not int(row.get(flag) or 0)]
        events[f"{flag}_consumption_se3_lift"] = mean([float(row["consumption_se3"]) for row in subset]) - mean([float(row["consumption_se3"]) for row in other])
        events[f"{flag}_net_load_se3_lift"] = mean([float(row["net_load_se3"]) for row in subset]) - mean([float(row["net_load_se3"]) for row in other])
    return {"price_table": price_table, "joined_rows": len(joined), "correlations": correlations, "event_lifts": events}


def source_discovery() -> dict[str, object]:
    return {
        "investigated": ["eSett Open Data", "Svenska kraftnat public statistics/control room"],
        "selected_source": "eSett Open Data",
        "reason": "Public OpenAPI exposes SE1-SE4 MBA options plus consumption and production endpoints without authentication.",
        "svk_result": "Investigated as public statistics/control-room source, not selected because P0051 needs stable machine-readable SE1-SE4 production and consumption contracts.",
    }


def source_contracts() -> dict[str, object]:
    return {
        "source_name": "eSett Open Data",
        "base_url": ESETT_BASE_URL,
        "authentication": "none",
        "rate_limit": "eSett API info states public rate limit currently 5 calls/second/user",
        "consumption_endpoint": "/EXP15/Consumption",
        "production_endpoint": "/EXP16/Volumes",
        "parameters": ["mba", "start", "end"],
        "time_format": "yyyy-MM-dd'T'HH:mm:ss.SSSX",
        "source_resolution": "15 minutes in observed sample",
        "stored_resolution": "hourly mean MW",
        "unit": "MW",
        "zones": ZONES,
        "production_types": PRODUCTION_TYPES,
        "consumption_sign": "source total/metered/profiled values are negative in sample; stored consumption is abs(value) positive demand MW",
        "fetch_note": "Python urllib is attempted first; curl fallback is used when local Python TLS cannot handshake with eSett.",
    }


def forecast_safety_classification() -> dict[str, str]:
    return {
        "consumption_total": "historical_observed_only",
        "production_total": "historical_observed_only",
        "production_by_type": "historical_observed_only",
        "net_load": "requires_separate_forecast_model",
        "north_south_aggregates": "requires_separate_forecast_model",
    }


def write_p0051_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    write_json(evidence_dir / "source-contracts.json", summary["source_contracts"])
    write_json(evidence_dir / "coverage-summary.json", {"ranges": summary["ranges"], "row_counts": summary["row_counts"]})
    write_json(evidence_dir / "validation-summary.json", summary["validation"])
    write_json(evidence_dir / "diagnostics-summary.json", summary["diagnostics"])
    paths = {
        "CHANGELOG": write(evidence_dir / "CHANGELOG.md", changelog(summary)),
        "source_discovery": write(evidence_dir / "source-discovery.md", source_discovery_report(summary)),
        "source_contracts": write(evidence_dir / "source-contracts.md", source_contract_report(summary)),
        "database": write(evidence_dir / "database-contract.md", database_report(summary)),
        "ingestion": write(evidence_dir / "ingestion-summary.md", ingestion_report(summary)),
        "time": write(evidence_dir / "time-normalization-and-dst.md", time_report(summary)),
        "validation": write(evidence_dir / "data-validation.md", validation_report(summary)),
        "coverage": write(evidence_dir / "coverage-and-missingness.md", coverage_report(summary)),
        "features": write(evidence_dir / "derived-feature-definitions.md", feature_report(summary)),
        "diagnostics": write(evidence_dir / "initial-physical-signal-diagnostics.md", diagnostics_report(summary)),
        "forecast": write(evidence_dir / "forecast-safety-classification.md", forecast_report(summary)),
        "next": write(evidence_dir / "next-package-recommendation.md", next_report(summary)),
        "component": write(evidence_dir / "component-attribution-summary.md", component_report(summary)),
    }
    return paths


def changelog(summary: dict[str, object]) -> str:
    return f"# P0051 changelog\n\n- Selected eSett Open Data for SE1-SE4 production/consumption ingestion.\n- Built `{CANONICAL_TABLE}` and `{WIDE_TABLE}` with {summary['row_counts']['hourly_rows']} canonical rows and {summary['row_counts']['wide_rows']} wide hourly rows.\n- Created source contracts, validation, coverage, derived feature and initial diagnostic evidence.\n- Result status: {summary['status']}.\n- No continental price pressure, SE1-to-SE3 anchoring, API, production model, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.\n"


def source_discovery_report(summary: dict[str, object]) -> str:
    return "# P0051 source discovery\n\n```json\n" + json.dumps(summary["source_discovery"], indent=2, sort_keys=True) + "\n```\n"


def source_contract_report(summary: dict[str, object]) -> str:
    return "# P0051 source contracts\n\n```json\n" + json.dumps(summary["source_contracts"], indent=2, sort_keys=True) + "\n```\n"


def database_report(summary: dict[str, object]) -> str:
    return f"# P0051 database contract\n\nTables created/rebuilt:\n\n- `{RAW_TABLE}`\n- `{CANONICAL_TABLE}`\n- `{WIDE_TABLE}`\n\nCanonical columns include timestamp, fixed-CET fields, source, zone, measure, production_type, value, unit and quality flag.\n"


def ingestion_report(summary: dict[str, object]) -> str:
    return "# P0051 ingestion summary\n\n```json\n" + json.dumps({"row_counts": summary["row_counts"], "measures": summary["measures"], "zones": summary["zones"]}, indent=2, sort_keys=True) + "\n```\n"


def time_report(summary: dict[str, object]) -> str:
    return "# P0051 time normalization and DST\n\nSource `timestampUTC` is normalized to UTC and bucketed to hourly UTC keys. Fixed-CET fields use `timestamp_utc + 1h` all year. DST 23/25-hour local days do not affect primary keys because local civil time is not used as identity.\n"


def validation_report(summary: dict[str, object]) -> str:
    return "# P0051 data validation\n\n```json\n" + json.dumps(summary["validation"], indent=2, sort_keys=True) + "\n```\n"


def coverage_report(summary: dict[str, object]) -> str:
    return "# P0051 coverage and missingness\n\n```json\n" + json.dumps({"ranges": summary["ranges"], "missing_hours": summary["validation"]["missing_hours"]}, indent=2, sort_keys=True) + "\n```\n"


def feature_report(summary: dict[str, object]) -> str:
    return "# P0051 derived feature definitions\n\n`net_load = consumption - production`; positive means local demand exceeds local production. North is SE1+SE2; south is SE3+SE4. Difference fields are south minus north.\n"


def diagnostics_report(summary: dict[str, object]) -> str:
    return "# P0051 initial physical signal diagnostics\n\n```json\n" + json.dumps(summary["diagnostics"], indent=2, sort_keys=True) + "\n```\n"


def forecast_report(summary: dict[str, object]) -> str:
    return "# P0051 forecast-safety classification\n\n```json\n" + json.dumps(summary["forecast_safety"], indent=2, sort_keys=True) + "\n```\n"


def next_report(summary: dict[str, object]) -> str:
    return "# P0051 next package recommendation\n\nP0052 should validate whether physical balance actuals improve historical SE3/SE3-SE1 explanation, then decide whether separate production/consumption forecast models are needed before these signals enter a forecast-safe SE3 model.\n"


def component_report(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0051 component attribution summary",
        "",
        f"Status: {summary['status']}",
        "1. Sources investigated: eSett Open Data and Svenska kraftnat public statistics/control-room sources.",
        "2. eSett provided usable SE1-SE4 quarter-hour production and consumption via EXP15/EXP16; stored as hourly mean MW.",
        "3. Svenska kraftnat was investigated but not selected because eSett exposed the required direct OpenAPI contracts.",
        "4. Selected source: eSett Open Data, due to public auth-free SE1-SE4 MBA options and consumption/production endpoints.",
        f"5. Historical range ingested: {summary['ranges']['final_overlap_range']}.",
        f"6. Measures/zones stored: measures={summary['measures']} zones={summary['zones']}.",
        "7. Units/timestamps: MW, source timestampUTC normalized to UTC, fixed-CET derived as UTC+1 all year.",
        f"8. Tables: `{RAW_TABLE}`, `{CANONICAL_TABLE}`, `{WIDE_TABLE}`.",
        f"9. Row counts: {summary['row_counts']}.",
        f"10. Missingness/quality: {summary['validation']}.",
        "11. Production totals split by type are available from eSett EXP16 where non-null.",
        "12. Derived features: zone consumption/production/net_load plus north/south aggregate and south-minus-north balance fields.",
        f"13. Initial diagnostics: {summary['diagnostics']}.",
        f"14. Forecast safety: {summary['forecast_safety']}.",
        "15. Recommendation: P0052 should evaluate physical-balance historical features and decide on separate forecasts before forecast-safe model use.",
        "16. Confirmed: no continental price pressure, no SE1-to-SE3 anchoring, no API, no production model and no device actions.",
        "",
    ])


def fixed_cet_fields(timestamp_utc: str) -> dict[str, object]:
    dt = parse_utc(timestamp_utc)
    fixed = dt + timedelta(hours=1)
    return {
        "model_cet_timestamp": fixed.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        "model_cet_date": fixed.date().isoformat(),
        "model_cet_hour": fixed.hour,
    }


def normalize_utc_text(value: str) -> str:
    return parse_utc(value).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    text = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_esett_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def camel_to_snake(value: str) -> str:
    output = []
    for char in value:
        if char.isupper() and output:
            output.append("_")
        output.append(char.lower())
    return "".join(output)


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return 0.0
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    deny = math.sqrt(sum((y - my) ** 2 for y in ys))
    return 0.0 if denx <= 0 or deny <= 0 else num / (denx * deny)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def write_json(path: Path, value: object) -> None:
    write(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> int:
    result = run_p0051_ingestion()
    print(json.dumps({"status": result.status, "row_counts": result.row_counts, "ranges": result.ranges, "evidence": result.evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
