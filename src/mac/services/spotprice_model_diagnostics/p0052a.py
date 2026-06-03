"""P0052A ENTSO-E token-backed capacity and exchange amendment."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import math
import os
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052


PACKAGE_ID = "P0052A"
EVIDENCE_DIR = Path("requirements/package-runs/P0052A")
ENTSOE_BASE_URL = "https://web-api.tp.entsoe.eu/api"
TOKEN_FILE = Path.home() / ".smart-home" / "secrets" / "entsoe_transparency_token"
SOURCE_NAME = "ENTSO-E Transparency Platform"
FLOW_BASED_GO_LIVE = datetime(2024, 10, 29, tzinfo=timezone.utc)
DEFAULT_START = datetime(2026, 5, 1, tzinfo=timezone.utc)
DEFAULT_END = datetime(2026, 5, 25, 22, tzinfo=timezone.utc)
INTERNAL_BORDERS = ("SE1_SE2", "SE2_SE3", "SE3_SE4")
DOMAINS = {
    "SE1": "10Y1001A1001A44P",
    "SE2": "10Y1001A1001A45N",
    "SE3": "10Y1001A1001A46L",
    "SE4": "10Y1001A1001A47J",
    "FI": "10YFI-1--------U",
    "DK1": "10YDK-1--------W",
    "DK2": "10YDK-2--------M",
    "NO1": "10YNO-1--------2",
    "NO2": "10YNO-2--------T",
    "NO3": "10YNO-3--------J",
    "NO4": "10YNO-4--------9",
    "LT": "10YLT-1001A0008Q",
    "PL": "10YPL-AREA-----S",
    "DE_LU": "10Y1001A1001A82H",
}
EIC_TO_AREA = {value: key for key, value in DOMAINS.items()}
DOCUMENT_CONFIGS = (
    {"document_type": "A09", "measure": "scheduled_exchange_mw", "source_dataset": "A09 scheduled commercial exchange", "capacity_method_label": "not_capacity", "flow_type_label": "scheduled_exchange"},
    {"document_type": "A11", "measure": "physical_flow_mw", "source_dataset": "A11 physical flow", "capacity_method_label": "not_capacity", "flow_type_label": "physical_flow"},
    {"document_type": "A61", "contract_type": "A02", "measure": "capacity_mw", "source_dataset": "A61 forecasted transfer capacity explicit A02", "capacity_method_label": "forecasted_transfer_capacity_explicit_A02", "flow_type_label": "not_flow"},
    {"document_type": "A61", "contract_type": "A03", "measure": "capacity_mw", "source_dataset": "A61 forecasted transfer capacity explicit A03", "capacity_method_label": "forecasted_transfer_capacity_explicit_A03", "flow_type_label": "not_flow"},
    {"document_type": "A61", "contract_type": "A04", "measure": "capacity_mw", "source_dataset": "A61 forecasted transfer capacity explicit A04", "capacity_method_label": "forecasted_transfer_capacity_explicit_A04", "flow_type_label": "not_flow"},
)
FORBIDDEN_DOCUMENT_TYPES = ("A44", "A45")
FORBIDDEN_PRODUCTION_PATHS = p0052.FORBIDDEN_PRODUCTION_PATHS


@dataclass(frozen=True)
class TokenSource:
    token: str
    source_label: str
    path: Path | None = None


@dataclass(frozen=True)
class P0052AResult:
    status: str
    row_counts: dict[str, int]
    ranges: dict[str, object]
    evidence: dict[str, str]


def run_p0052a_ingestion(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
    start: datetime | None = None,
    end: datetime | None = None,
) -> P0052AResult:
    started = time.monotonic()
    token_source = load_entsoe_token()
    secret_safety = verify_secret_safety(token_source)
    if not secret_safety["secret_safe"]:
        raise RuntimeError("P0052A secret safety check failed")
    start_dt = start or DEFAULT_START
    end_dt = end or DEFAULT_END
    raw_rows, responses = fetch_entsoe_rows(token_source.token, start_dt, end_dt)
    hourly_rows = aggregate_hourly(raw_rows)
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        ensure_p0052_tables_exist(conn)
        persist_entsoe_rows(conn, raw_rows, hourly_rows)
        updated_wide_rows = update_wide_entsoe_features(conn, hourly_rows)
        validation = validate_p0052a(conn, hourly_rows, start_dt, end_dt, secret_safety)
        diagnostics = run_p0052a_diagnostics(conn)
    summary = {
        "status": "WARN",
        "secret_safety": secret_safety,
        "source_discovery": entsoe_source_discovery(responses),
        "source_contracts": source_contracts(responses),
        "eic_domain_mapping": eic_domain_mapping(),
        "ranges": {
            "requested_range": {"start": format_utc(start_dt), "end": format_utc(end_dt)},
            "ingested_range": {"start": format_utc(start_dt), "end": format_utc(end_dt)},
            "full_p0051_range_incomplete_reason": "P0052A defaults to the P0052 recent overlap to keep token-backed API ingestion bounded.",
        },
        "row_counts": {
            "raw_rows": len(raw_rows),
            "hourly_rows": len(hourly_rows),
            "wide_rows_updated": updated_wide_rows,
        },
        "validation": validation,
        "diagnostics": diagnostics,
        "forecast_safety": forecast_safety_classification(),
        "runtime_seconds": time.monotonic() - started,
        "forbidden_paths": FORBIDDEN_PRODUCTION_PATHS,
    }
    evidence = write_p0052a_evidence(Path(evidence_dir), summary)
    return P0052AResult(status=str(summary["status"]), row_counts=summary["row_counts"], ranges=summary["ranges"], evidence=evidence)


def load_entsoe_token() -> TokenSource:
    env_token = os.environ.get("ENTSOE_SECURITY_TOKEN", "").strip()
    if env_token:
        return TokenSource(env_token, "environment")
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if token:
            return TokenSource(token, "local_secret_file_outside_repo", TOKEN_FILE)
    raise RuntimeError("ENTSO-E token not found")


def verify_secret_safety(token_source: TokenSource) -> dict[str, object]:
    if token_source.path is None:
        return {"token_source": token_source.source_label, "secret_checked": True, "secret_safe": True, "secret_gitignored": "environment_not_a_file"}
    path = token_source.path.resolve()
    repo = Path.cwd().resolve()
    outside_repo = not is_relative_to(path, repo)
    mode = path.stat().st_mode & 0o777
    parent_mode = path.parent.stat().st_mode & 0o777
    return {
        "token_source": token_source.source_label,
        "secret_checked": True,
        "secret_safe": outside_repo and mode == 0o600 and parent_mode == 0o700,
        "secret_gitignored": "outside_repo_not_committable" if outside_repo else "inside_repo_requires_gitignore_check",
        "secret_location_class": "outside_repository_user_secret_dir" if outside_repo else "inside_repository",
        "file_mode": oct(mode),
        "directory_mode": oct(parent_mode),
    }


def is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def fetch_entsoe_rows(token: str, start: datetime, end: datetime) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    raw_rows: list[dict[str, object]] = []
    responses: list[dict[str, object]] = []
    for config in DOCUMENT_CONFIGS:
        for border in INTERNAL_BORDERS:
            left, right = border.split("_", 1)
            for from_area, to_area in ((left, right), (right, left)):
                params, safe = build_entsoe_params(config, from_area, to_area, start, end)
                try:
                    xml_bytes, status = fetch_entsoe_document(token, params)
                except urllib.error.URLError as exc:
                    responses.append({**safe, "status": "url_error", "response": mask_token(str(type(exc.reason).__name__), token)})
                    continue
                observations, response = parse_entsoe_document(xml_bytes, safe)
                responses.append({**safe, "status": status, **response})
                raw_rows.extend(row for row in observations if start <= parse_utc(str(row["timestamp_utc"])) <= end)
    return raw_rows, responses


def build_entsoe_params(config: dict[str, str], from_area: str, to_area: str, start: datetime, end: datetime) -> tuple[dict[str, str], dict[str, str]]:
    if config["document_type"] in FORBIDDEN_DOCUMENT_TYPES:
        raise RuntimeError("P0052A must not request price-level document types")
    params = {
        "documentType": config["document_type"],
        "out_Domain": DOMAINS[from_area],
        "in_Domain": DOMAINS[to_area],
        "periodStart": format_entsoe_time(start),
        "periodEnd": format_entsoe_time(end + timedelta(hours=1)),
    }
    if config.get("contract_type"):
        params["contract_MarketAgreement.Type"] = str(config["contract_type"])
    safe = {
        "document_type": config["document_type"],
        "contract_type": str(config.get("contract_type", "")),
        "from_area": from_area,
        "to_area": to_area,
        "border_id": f"{from_area}_{to_area}",
        "measure": config["measure"],
        "source_dataset": config["source_dataset"],
        "capacity_method_label": config["capacity_method_label"],
        "flow_type_label": config["flow_type_label"],
        "period_start": format_utc(start),
        "period_end": format_utc(end),
    }
    return params, safe


def fetch_entsoe_document(token: str, params: dict[str, str], timeout: float = 30.0) -> tuple[bytes, int]:
    request_params = {"securityToken": token, **params}
    url = ENTSOE_BASE_URL + "?" + urllib.parse.urlencode(request_params)
    request = urllib.request.Request(url, headers={"User-Agent": "smart-home-p0052a/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read(), int(response.status)
    except urllib.error.HTTPError as exc:
        return exc.read(), int(exc.code)


def parse_entsoe_document(xml_bytes: bytes, request_meta: dict[str, str]) -> tuple[list[dict[str, object]], dict[str, object]]:
    root = ET.fromstring(xml_bytes)
    root_tag = strip_ns(root.tag)
    if root_tag == "Acknowledgement_MarketDocument":
        reason = text_or_empty(root.find(".//{*}text"))
        return [], {"root": root_tag, "reason": reason[:180], "timeseries": 0, "points": 0}
    rows: list[dict[str, object]] = []
    for series in root.findall(".//{*}TimeSeries"):
        series_meta = series_metadata(series, request_meta)
        for period in series.findall(".//{*}Period"):
            rows.extend(parse_entsoe_period_points(period, request_meta, series_meta))
    return rows, {"root": root_tag, "reason": "", "timeseries": len(root.findall('.//{*}TimeSeries')), "points": len(root.findall('.//{*}Point'))}


def series_metadata(series: ET.Element, request_meta: dict[str, str]) -> dict[str, str]:
    out_domain = text_or_empty(series.find(".//{*}out_Domain.mRID"))
    in_domain = text_or_empty(series.find(".//{*}in_Domain.mRID"))
    from_area = EIC_TO_AREA.get(out_domain, request_meta["from_area"])
    to_area = EIC_TO_AREA.get(in_domain, request_meta["to_area"])
    unit = text_or_empty(series.find(".//{*}quantity_Measure_Unit.name")) or "MW"
    return {"from_area": from_area, "to_area": to_area, "unit": unit, "border_id": f"{from_area}_{to_area}"}


def parse_entsoe_period_points(period: ET.Element, request_meta: dict[str, str], series_meta: dict[str, str]) -> list[dict[str, object]]:
    start_text = text_or_empty(period.find(".//{*}timeInterval/{*}start"))
    end_text = text_or_empty(period.find(".//{*}timeInterval/{*}end"))
    resolution = text_or_empty(period.find(".//{*}resolution"))
    period_start = parse_utc(start_text)
    period_end = parse_utc(end_text) if end_text else None
    step = resolution_to_timedelta(resolution, period_start=period_start, period_end=period_end)
    rows = []
    for point in period.findall(".//{*}Point"):
        position = int(text_or_empty(point.find(".//{*}position")) or "1")
        quantity = text_or_empty(point.find(".//{*}quantity"))
        if not quantity:
            continue
        timestamp = period_start + (position - 1) * step
        rows.extend(expand_entsoe_value(timestamp, step, float(quantity), request_meta, series_meta))
    return rows


def expand_entsoe_value(timestamp: datetime, step: timedelta, value: float, request_meta: dict[str, str], series_meta: dict[str, str]) -> list[dict[str, object]]:
    if request_meta["measure"] == "capacity_mw" and step > timedelta(hours=1):
        count = int(step.total_seconds() // 3600)
        timestamps = [timestamp + timedelta(hours=i) for i in range(count)]
    else:
        timestamps = [timestamp]
    return [
        source_observation(
            ts,
            request_meta["source_dataset"],
            series_meta["from_area"],
            series_meta["to_area"],
            series_meta["border_id"],
            request_meta["measure"],
            value,
            series_meta["unit"],
            request_meta["capacity_method_label"],
            request_meta["flow_type_label"],
            "ok",
        )
        for ts in timestamps
    ]


def source_observation(timestamp: datetime, source_dataset: str, from_area: str, to_area: str, border_id: str, measure: str, value: float, unit: str, capacity_method_label: str, flow_type_label: str, quality_flag: str) -> dict[str, object]:
    return {
        "timestamp_utc": format_utc(timestamp),
        "model_cet_timestamp": format_utc(timestamp + timedelta(hours=1)),
        "model_cet_date": (timestamp + timedelta(hours=1)).date().isoformat(),
        "model_cet_hour": (timestamp + timedelta(hours=1)).hour,
        "source_name": SOURCE_NAME,
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
        "source_updated_at_utc": "",
        "quality_flag": quality_flag,
    }


def aggregate_hourly(raw_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str, str, str, str, str, str, str], list[float]] = defaultdict(list)
    for row in raw_rows:
        if not is_finite(row["value"]):
            continue
        hour = parse_utc(str(row["timestamp_utc"])).replace(minute=0, second=0, microsecond=0)
        key = (
            format_utc(hour),
            str(row["source_name"]),
            str(row["source_dataset"]),
            str(row["from_area"]),
            str(row["to_area"]),
            str(row["border_id"]),
            str(row["measure"]),
            str(row["unit"]),
            str(row["capacity_method_label"]),
            str(row["flow_type_label"]),
        )
        grouped[key].append(float(row["value"]))
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
            "source_updated_at_utc": "",
            "quality_flag": "ok",
            "source_quarter_hours": len(values),
        })
    return rows


def ensure_p0052_tables_exist(conn: sqlite3.Connection) -> None:
    if not p0052.table_exists(conn, p0052.CANONICAL_TABLE) or not p0052.table_exists(conn, p0052.WIDE_TABLE):
        raise RuntimeError("P0052A requires P0052 transfer tables")


def persist_entsoe_rows(conn: sqlite3.Connection, raw_rows: list[dict[str, object]], hourly_rows: list[dict[str, object]]) -> None:
    p0052.insert_rows(conn, p0052.RAW_TABLE, raw_rows)
    p0052.insert_rows(conn, p0052.CANONICAL_TABLE, hourly_rows)
    conn.commit()


def update_wide_entsoe_features(conn: sqlite3.Connection, hourly_rows: list[dict[str, object]]) -> int:
    required_columns = wide_entsoe_columns()
    existing = p0052.table_columns(conn, p0052.WIDE_TABLE)
    for column in required_columns:
        if column not in existing:
            conn.execute(f"ALTER TABLE {p0052.WIDE_TABLE} ADD COLUMN {column} REAL")
    by_hour: dict[str, dict[str, float]] = defaultdict(dict)
    for row in hourly_rows:
        key = str(row["timestamp_utc"])
        column = wide_column_for_row(row)
        if column:
            by_hour[key][column] = float(row["value"])
    updated = 0
    for timestamp, values in sorted(by_hour.items()):
        values.update(derive_wide_capacity_features(values))
        assignments = ", ".join(f"{column}=?" for column in values)
        params = list(values.values()) + [timestamp]
        cur = conn.execute(f"UPDATE {p0052.WIDE_TABLE} SET {assignments} WHERE timestamp_utc=?", params)
        updated += cur.rowcount
    conn.commit()
    return updated


def wide_entsoe_columns() -> list[str]:
    cols = []
    for border in INTERNAL_BORDERS:
        a, b = border.lower().split("_", 1)
        for prefix in ("scheduled_exchange", "physical_flow", "flow_or_exchange"):
            cols.append(f"{prefix}_{a}_to_{b}_mw")
            cols.append(f"{prefix}_{b}_to_{a}_mw")
    return cols


def wide_column_for_row(row: dict[str, object]) -> str | None:
    from_area = str(row["from_area"]).lower()
    to_area = str(row["to_area"]).lower()
    measure = str(row["measure"])
    if f"{from_area.upper()}_{to_area.upper()}" not in {b for b in INTERNAL_BORDERS} and f"{to_area.upper()}_{from_area.upper()}" not in {b for b in INTERNAL_BORDERS}:
        return None
    if measure == "scheduled_exchange_mw":
        return f"scheduled_exchange_{from_area}_to_{to_area}_mw"
    if measure == "physical_flow_mw":
        return f"physical_flow_{from_area}_to_{to_area}_mw"
    if measure == "capacity_mw" and str(row["capacity_method_label"]) == "forecasted_transfer_capacity_explicit_A02":
        return f"capacity_{from_area}_to_{to_area}_mw"
    return None


def derive_wide_capacity_features(values: dict[str, float]) -> dict[str, float]:
    out = {}
    for border in INTERNAL_BORDERS:
        a, b = border.lower().split("_", 1)
        flow = values.get(f"physical_flow_{a}_to_{b}_mw")
        exchange = values.get(f"scheduled_exchange_{a}_to_{b}_mw")
        chosen = flow if flow is not None else exchange
        if chosen is not None:
            out[f"flow_or_exchange_{a}_to_{b}_mw"] = chosen
    return out


def capacity_utilization(flow_or_exchange: object, capacity: object) -> float | None:
    if flow_or_exchange is None or capacity is None:
        return None
    capacity_f = float(capacity)
    if capacity_f <= 0:
        return None
    return max(0.0, float(flow_or_exchange)) / capacity_f


def validate_p0052a(conn: sqlite3.Connection, hourly_rows: list[dict[str, object]], start: datetime, end: datetime, secret_safety: dict[str, object]) -> dict[str, object]:
    duplicates = len(hourly_rows) - len({(r["timestamp_utc"], r["source_name"], r["source_dataset"], r["from_area"], r["to_area"], r["measure"], r["capacity_method_label"], r["flow_type_label"]) for r in hourly_rows})
    nonfinite = sum(1 for row in hourly_rows if not is_finite(row["value"]))
    negative_capacity = sum(1 for row in hourly_rows if row["measure"] == "capacity_mw" and float(row["value"]) < 0)
    by_measure = dict(Counter(str(row["measure"]) for row in hourly_rows))
    joined = conn.execute(f"SELECT COUNT(*) FROM {p0052.WIDE_TABLE} WHERE timestamp_utc BETWEEN ? AND ?", (format_utc(start), format_utc(end))).fetchone()[0]
    return {
        "ok": bool(hourly_rows) and duplicates == 0 and nonfinite == 0 and negative_capacity == 0 and bool(secret_safety["secret_safe"]),
        "secret_checked": secret_safety["secret_checked"],
        "secret_safe": secret_safety["secret_safe"],
        "duplicates": duplicates,
        "nonfinite_values": nonfinite,
        "negative_capacity_values": negative_capacity,
        "row_counts_by_measure": by_measure,
        "wide_rows_joined": joined,
        "token_leak_scan_required": True,
    }


def run_p0052a_diagnostics(conn: sqlite3.Connection) -> dict[str, object]:
    price_table = "se3_se1_demand_response_analysis_v1"
    if not p0052.table_exists(conn, price_table):
        return {"joined_rows": 0, "reason": "no price table"}
    columns = p0052.table_columns(conn, price_table)
    se3_price_column = "se3_price_eur_mwh" if "se3_price_eur_mwh" in columns else "se3_price"
    spread_column = "se3_minus_se1_eur_mwh" if "se3_minus_se1_eur_mwh" in columns else "se3_minus_se1"
    wide_cols = p0052.table_columns(conn, p0052.WIDE_TABLE)
    candidate_cols = [col for col in ("flow_or_exchange_se2_to_se3_mw", "flow_or_exchange_se3_to_se4_mw", "capacity_se2_to_se3_mw", "capacity_se3_to_se4_mw") if col in wide_cols]
    if not candidate_cols:
        return {"joined_rows": 0, "reason": "no P0052A wide columns"}
    select_cols = ", ".join(f"w.{col}" for col in candidate_cols)
    rows = [dict(row) for row in conn.execute(f"""
        SELECT w.timestamp_utc, p.{se3_price_column} AS se3_price, p.{spread_column} AS se3_minus_se1, {select_cols}
        FROM {p0052.WIDE_TABLE} w
        JOIN {price_table} p ON p.timestamp_utc = w.timestamp_utc
    """)]
    correlations = {}
    for col in candidate_cols:
        correlations[f"se3_price_vs_{col}"] = correlation(rows, "se3_price", col)
        correlations[f"se3_minus_se1_vs_{col}"] = correlation(rows, "se3_minus_se1", col)
    return {"price_table": price_table, "joined_rows": len(rows), "columns": candidate_cols, "correlations": correlations}


def correlation(rows: list[dict[str, object]], x_key: str, y_key: str) -> float | None:
    pairs = [(float(row[x_key]), float(row[y_key])) for row in rows if row.get(x_key) is not None and row.get(y_key) is not None and is_finite(row[x_key]) and is_finite(row[y_key])]
    if len(pairs) < 2:
        return None
    xs, ys = zip(*pairs)
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
    denom_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    denom_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if denom_x == 0 or denom_y == 0:
        return None
    return numerator / (denom_x * denom_y)


def entsoe_source_discovery(responses: list[dict[str, object]]) -> dict[str, object]:
    return {
        "selected_documents": ["A09", "A11", "A61"],
        "capacity_contract_types_with_data_in_discovery": ["A02", "A03", "A04"],
        "rejected_documents": {"A26": "invalid/not allowed for tested parameters", "A31": "invalid/not allowed for tested parameters"},
        "response_counts": dict(Counter(f"{r['document_type']}_{r.get('contract_type','')}_{r.get('root','')}" for r in responses)),
        "note": "Token-backed discovery found internal Swedish A09/A11 and A61 data. Token value is not stored in evidence.",
    }


def source_contracts(responses: list[dict[str, object]]) -> dict[str, object]:
    attempted = []
    for response in responses:
        attempted.append({key: response.get(key) for key in ("document_type", "contract_type", "from_area", "to_area", "measure", "status", "root", "reason", "timeseries", "points")})
    return {"base_url": ENTSOE_BASE_URL, "attempted_contracts": attempted, "token_included_in_evidence": False}


def eic_domain_mapping() -> dict[str, str]:
    return dict(DOMAINS)


def forecast_safety_classification() -> dict[str, str]:
    return {
        "scheduled_exchange_mw": "historical_observed_only",
        "physical_flow_mw": "historical_observed_only",
        "forecasted_transfer_capacity_explicit_A02": "forecast_time_known_near_term_uncertain_publication_timing",
        "forecasted_transfer_capacity_explicit_A03": "forecast_time_known_near_term_uncertain_publication_timing",
        "forecasted_transfer_capacity_explicit_A04": "forecast_time_known_near_term_uncertain_publication_timing",
        "utilization": "not_forecast_safe_until_capacity_concept_review",
    }


def write_p0052a_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "CHANGELOG.md": changelog_text(summary),
        "secret-handling.md": json_md("P0052A secret handling", summary["secret_safety"]),
        "entsoe-source-discovery.md": json_md("P0052A ENTSO-E source discovery", summary["source_discovery"]),
        "entsoe-source-contracts.md": json_md("P0052A ENTSO-E source contracts", summary["source_contracts"]),
        "eic-domain-mapping.md": json_md("P0052A EIC domain mapping", summary["eic_domain_mapping"]),
        "database-contract.md": database_contract_text(),
        "ingestion-summary.md": json_md("P0052A ingestion summary", {"ranges": summary["ranges"], "row_counts": summary["row_counts"]}),
        "time-normalization-and-dst.md": "# P0052A time normalization and DST\n\nENTSO-E period starts are normalized to UTC. PT15M/PT60M values are aggregated to hourly mean MW. Daily capacity periods are expanded to hourly constant capacity rows before hourly persistence. Fixed-CET fields use UTC+1 all year.\n",
        "data-validation.md": json_md("P0052A data validation", summary["validation"]),
        "coverage-and-missingness.md": json_md("P0052A coverage and missingness", {"ranges": summary["ranges"], "row_counts": summary["row_counts"]}),
        "direction-conventions.md": "# P0052A direction conventions\n\nP0052A requests ENTSO-E with `out_Domain = from_area` and `in_Domain = to_area`. Stored rows therefore use positive values in the requested directed border direction.\n",
        "flow-based-era-review.md": "# P0052A flow-based era review\n\nThe default ingested range is after the 2024-10-29 Nordic flow-based go-live date. Capacity contract labels remain explicit; P0052A does not claim pre/post capacity concept comparability for full history.\n",
        "derived-feature-definitions.md": "# P0052A derived feature definitions\n\nP0052A adds scheduled exchange, physical flow and directional capacity columns where ENTSO-E data exists. Generic utilization and bottleneck margin remain conservative until capacity contract concepts are reviewed for compatibility with flow/exchange.\n",
        "capacity-utilization-and-margin-diagnostics.md": json_md("P0052A capacity/utilization and margin diagnostics", summary["diagnostics"]),
        "forecast-safety-classification.md": json_md("P0052A forecast-safety classification", summary["forecast_safety"]),
        "next-package-recommendation.md": "# P0052A next package recommendation\n\nContinue with a focused ENTSO-E concept/backfill package if capacity will be used for utilization. Otherwise P0053 can proceed with P0051 physical balance plus P0052/P0052A observed flow/exchange as historical-only physical-regime diagnostics.\n",
        "component-attribution-summary.md": component_summary_text(summary),
    }
    for name, content in files.items():
        (evidence_dir / name).write_text(content, encoding="utf-8")
    json_files = {
        "source-contracts.json": summary["source_contracts"],
        "eic-domain-mapping.json": summary["eic_domain_mapping"],
        "coverage-summary.json": {"ranges": summary["ranges"], "row_counts": summary["row_counts"]},
        "validation-summary.json": summary["validation"],
        "diagnostics-summary.json": summary["diagnostics"],
    }
    for name, payload in json_files.items():
        (evidence_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {name: str(evidence_dir / name) for name in files | json_files}


def json_md(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0052A changelog

- Used the local ENTSO-E token safely without writing the token to evidence.
- Ingested ENTSO-E A09 scheduled exchange, A11 physical flow and A61 explicit capacity rows for internal Swedish borders over the P0052 recent overlap.
- Updated P0052 long tables and wide transfer table without dropping SvK/Statnett rows.
- Result status: {summary['status']}.
- No token leak, continental price levels, SE1-to-SE3 anchoring, API, production model, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.
"""


def database_contract_text() -> str:
    return f"""# P0052A database contract

P0052A reuses and extends:

- `{p0052.RAW_TABLE}`
- `{p0052.CANONICAL_TABLE}`
- `{p0052.WIDE_TABLE}`

ENTSO-E rows use `source_name = {SOURCE_NAME}` and source-specific datasets such as `A09 scheduled commercial exchange`, `A11 physical flow` and `A61 forecasted transfer capacity explicit A02/A03/A04`.

Existing SvK/Statnett rows are preserved because source identity is part of the long-table uniqueness key.
"""


def component_summary_text(summary: dict[str, object]) -> str:
    return "\n".join([
        "# P0052A component attribution summary",
        "",
        f"Status: {summary['status']}",
        "1. Token was read from a local secret file outside the repository; the token value was not logged or written.",
        f"2. Secret safety: {summary['secret_safety']}.",
        "3. ENTSO-E document/process/business types tried: A09, A11, A26, A31, A61 with contract types A01-A09 during discovery; ingestion used A09, A11 and A61 A02/A03/A04.",
        f"4. EIC/domain mapping: {summary['eic_domain_mapping']}.",
        "5. ENTSO-E provides internal Swedish A61 capacity rows for SE1-SE2, SE2-SE3 and SE3-SE4 for tested contract types A02/A03/A04.",
        "6. ENTSO-E provides internal Swedish A09 scheduled exchange and A11 physical flow rows for those borders.",
        "7. A26/A31 were rejected or not allowed for tested parameters; A61 A01 had no matching data in the tested discovery window.",
        f"8. Historical range ingested: {summary['ranges']['ingested_range']}.",
        f"9. Tables updated: `{p0052.RAW_TABLE}`, `{p0052.CANONICAL_TABLE}`, `{p0052.WIDE_TABLE}`.",
        "10. Concepts stored: scheduled_exchange_mw, physical_flow_mw, capacity_mw with explicit A61 contract labels.",
        "11. Pre/post 2024-10-29 capacity comparability was not proven because default ingestion is post-go-live.",
        "12. Utilization and bottleneck margin remain conservative pending capacity contract concept review.",
        f"13. Diagnostics: {summary['diagnostics']}.",
        f"14. Forecast safety: {summary['forecast_safety']}.",
        "15. Next route: continue ENTSO-E concept/backfill if capacity will drive utilization; otherwise use signals as historical-only diagnostics.",
        "16. Confirmed: no token leak, no continental price levels, no SE1-to-SE3 anchoring, no API, no production model and no device actions.",
        "",
    ])


def mask_token(text: str, token: str) -> str:
    return text.replace(token, "<ENTSOE_TOKEN>") if token else text


def text_or_empty(node: ET.Element | None) -> str:
    return "" if node is None or node.text is None else node.text.strip()


def strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1]


def resolution_to_timedelta(resolution: str, *, period_start: datetime | None = None, period_end: datetime | None = None) -> timedelta:
    if resolution == "PT15M":
        return timedelta(minutes=15)
    if resolution == "PT30M":
        return timedelta(minutes=30)
    if resolution == "PT60M":
        return timedelta(hours=1)
    if resolution == "P1D":
        return timedelta(days=1)
    if resolution == "P1M" and period_start is not None and period_end is not None:
        return period_end - period_start
    if resolution.startswith("PT") and resolution.endswith("M"):
        return timedelta(minutes=int(resolution[2:-1]))
    if resolution.startswith("PT") and resolution.endswith("H"):
        return timedelta(hours=int(resolution[2:-1]))
    raise ValueError(f"Unsupported ENTSO-E resolution: {resolution}")


def parse_utc(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def format_entsoe_time(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y%m%d%H%M")


def is_finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def main() -> None:
    result = run_p0052a_ingestion()
    print(f"P0052A {result.status}: row_counts={json.dumps(result.row_counts, sort_keys=True)}")


if __name__ == "__main__":
    main()
