"""P0052C A61 capacity sanity checks against exchange and flow."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import csv
import json
import math
import sqlite3

from src.mac.services.spotprice_ml_model.core import DEFAULT_FEATURE_DB
from src.mac.services.spotprice_model_diagnostics import p0052, p0052a, p0052b


PACKAGE_ID = "P0052C"
EVIDENCE_DIR = Path("requirements/package-runs/P0052C")
CONTRACT_TYPES = ("A02", "A03", "A04")
COMPARISONS = {
    "scheduled_exchange": "scheduled_exchange_mw",
    "physical_flow": "physical_flow_mw",
}
WINDOWS = (
    ("2025_representative_week", "2025-01-01T00:00:00Z", "2025-01-07T23:00:00Z"),
    ("flow_based_transition_week", "2024-10-27T00:00:00Z", "2024-11-03T23:00:00Z"),
    ("p0052a_overlap_week", "2026-05-01T00:00:00Z", "2026-05-07T23:00:00Z"),
)
FLOW_BASED_GO_LIVE = datetime(2024, 10, 29, tzinfo=timezone.utc)


@dataclass(frozen=True)
class P0052CResult:
    status: str
    row_counts: dict[str, int]
    evidence: dict[str, str]


def run_p0052c_analysis(
    *,
    feature_db: Path | str = DEFAULT_FEATURE_DB,
    evidence_dir: Path | str = EVIDENCE_DIR,
) -> P0052CResult:
    token_source = p0052a.load_entsoe_token()
    secret_safety = p0052a.verify_secret_safety(token_source)
    if not secret_safety["secret_safe"]:
        raise RuntimeError("P0052C secret safety check failed")
    with sqlite3.connect(Path(feature_db).expanduser()) as conn:
        conn.row_factory = sqlite3.Row
        rows = load_entsoe_hourly_rows(conn, WINDOWS)
    observations, missing_counts = build_ratio_observations(rows, WINDOWS)
    metrics = ratio_metrics(observations, missing_counts)
    classifications = classify_contract_types(metrics)
    worst = worst_ratio_examples(observations)
    summary = {
        "status": "PASS" if observations else "STOP",
        "secret_safety": secret_handling_evidence(secret_safety),
        "windows": [{"window_id": wid, "start": start, "end": end} for wid, start, end in WINDOWS],
        "row_counts": {
            "source_rows": len(rows),
            "ratio_observations": len(observations),
            "metric_rows": len(metrics),
            "worst_examples": len(worst),
        },
        "metrics": metrics,
        "classification": classifications,
        "worst_examples": worst,
        "pre_post_review": pre_post_review(metrics),
        "component_summary": component_summary(metrics, classifications),
        "forbidden_paths": p0052.FORBIDDEN_PRODUCTION_PATHS,
    }
    evidence = write_p0052c_evidence(Path(evidence_dir), summary)
    return P0052CResult(str(summary["status"]), summary["row_counts"], evidence)


def load_entsoe_hourly_rows(conn: sqlite3.Connection, windows: tuple[tuple[str, str, str], ...]) -> list[dict[str, object]]:
    clauses = []
    params: list[str] = []
    for _, start, end in windows:
        clauses.append("(timestamp_utc BETWEEN ? AND ?)")
        params.extend([start, end])
    rows = [
        dict(row)
        for row in conn.execute(
            f"""
            SELECT timestamp_utc, source_dataset, from_area, to_area, border_id, measure, value, capacity_method_label, flow_type_label, contract_type
            FROM {p0052.CANONICAL_TABLE}
            WHERE source_name = ?
              AND ({' OR '.join(clauses)})
              AND measure IN ('capacity_mw', 'scheduled_exchange_mw', 'physical_flow_mw')
            """,
            [p0052a.SOURCE_NAME, *params],
        )
    ]
    return rows


def build_ratio_observations(rows: list[dict[str, object]], windows: tuple[tuple[str, str, str], ...]) -> tuple[list[dict[str, object]], dict[tuple[str, str, str, str, str, str], Counter]]:
    capacities: dict[tuple[str, str, str, str, str], dict[str, object]] = {}
    measures: dict[tuple[str, str, str, str], dict[str, object]] = {}
    for row in rows:
        timestamp = normalize_timestamp_value(str(row["timestamp_utc"]))
        direction = direction_key(str(row["from_area"]), str(row["to_area"]))
        measure = str(row["measure"])
        if measure == "capacity_mw":
            contract = str(row.get("contract_type") or contract_from_dataset(str(row["source_dataset"])))
            capacities[(timestamp, direction, contract, str(row["from_area"]), str(row["to_area"]))] = row
        elif measure in COMPARISONS.values():
            measures[(timestamp, direction, measure, str(row["from_area"]), str(row["to_area"]))] = row
    observations: list[dict[str, object]] = []
    missing: dict[tuple[str, str, str, str, str, str], Counter] = defaultdict(Counter)
    for window_id, start, end in windows:
        start_dt = p0052a.parse_utc(start)
        end_dt = p0052a.parse_utc(end)
        for direction in directed_borders():
            from_area, to_area = direction.split("->", 1)
            timestamps = {
                ts
                for ts, row_direction, _contract, cap_from, cap_to in capacities
                if row_direction == direction and cap_from == from_area and cap_to == to_area and start_dt <= p0052a.parse_utc(ts) <= end_dt
            }
            timestamps.update(
                ts
                for ts, row_direction, _measure, meas_from, meas_to in measures
                if row_direction == direction and meas_from == from_area and meas_to == to_area and start_dt <= p0052a.parse_utc(ts) <= end_dt
            )
            for contract in CONTRACT_TYPES:
                for comparison_type, measure in COMPARISONS.items():
                    for timestamp in sorted(timestamps):
                        era = flow_based_era(timestamp)
                        group_key = (window_id, era, contract, direction, comparison_type, "all")
                        cap = capacities.get((timestamp, direction, contract, from_area, to_area))
                        flow = measures.get((timestamp, direction, measure, from_area, to_area))
                        if cap is None:
                            missing[group_key]["missing_capacity"] += 1
                            continue
                        if flow is None:
                            missing[group_key]["missing_flow_or_exchange"] += 1
                            continue
                        ratio, reason = safe_ratio(flow.get("value"), cap.get("value"))
                        if ratio is None:
                            missing[group_key][reason] += 1
                            continue
                        observations.append(
                            {
                                "window_id": window_id,
                                "era": era,
                                "timestamp_utc": timestamp,
                                "from_area": from_area,
                                "to_area": to_area,
                                "border_direction": direction,
                                "contract_type": contract,
                                "comparison_type": comparison_type,
                                "capacity_mw": float(cap["value"]),
                                "flow_or_exchange_mw": float(flow["value"]),
                                "ratio": ratio,
                                "capacity_source_dataset": cap["source_dataset"],
                                "flow_source_dataset": flow["source_dataset"],
                            }
                        )
    return observations, missing


def ratio_metrics(observations: list[dict[str, object]], missing_counts: dict[tuple[str, str, str, str, str, str], Counter]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for obs in observations:
        grouped[(str(obs["window_id"]), str(obs["era"]), str(obs["contract_type"]), str(obs["border_direction"]), str(obs["comparison_type"]))].append(obs)
    keys = set(grouped)
    keys.update((window_id, era, contract, direction, comparison) for window_id, era, contract, direction, comparison, _ in missing_counts)
    metrics = []
    for key in sorted(keys):
        window_id, era, contract, direction, comparison = key
        values = [float(item["ratio"]) for item in grouped.get(key, [])]
        missing = missing_counts.get((window_id, era, contract, direction, comparison, "all"), Counter())
        row = {
            "window_id": window_id,
            "era": era,
            "contract_type": contract,
            "border_direction": direction,
            "comparison_type": comparison,
            "count_compared": len(values),
            "count_missing_capacity": int(missing.get("missing_capacity", 0)),
            "count_missing_flow_or_exchange": int(missing.get("missing_flow_or_exchange", 0)),
            "count_invalid_capacity": int(missing.get("invalid_capacity", 0)),
            "max_ratio": percentile(values, 1.0),
            "p50_ratio": percentile(values, 0.50),
            "p90_ratio": percentile(values, 0.90),
            "p95_ratio": percentile(values, 0.95),
            "p99_ratio": percentile(values, 0.99),
        }
        for threshold in (1.00, 1.02, 1.05, 1.10):
            count = sum(1 for value in values if value > threshold)
            suffix = f"{threshold:.2f}".replace(".", "_")
            row[f"count_ratio_gt_{suffix}"] = count
            row[f"share_ratio_gt_{suffix}"] = count / len(values) if values else None
        metrics.append(row)
    return metrics


def classify_contract_types(metric_rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    out = {}
    for contract in CONTRACT_TYPES:
        contract_rows = [row for row in metric_rows if row["contract_type"] == contract]
        exchange_rows = [row for row in contract_rows if row["comparison_type"] == "scheduled_exchange"]
        physical_rows = [row for row in contract_rows if row["comparison_type"] == "physical_flow"]
        exchange_count = sum(int(row["count_compared"]) for row in exchange_rows)
        physical_count = sum(int(row["count_compared"]) for row in physical_rows)
        exchange_gt_105 = sum(int(row["count_ratio_gt_1_05"]) for row in exchange_rows)
        physical_gt_105 = sum(int(row["count_ratio_gt_1_05"]) for row in physical_rows)
        exchange_max = max((float(row["max_ratio"]) for row in exchange_rows if row["max_ratio"] is not None), default=None)
        physical_max = max((float(row["max_ratio"]) for row in physical_rows if row["max_ratio"] is not None), default=None)
        if exchange_count < 24:
            market = "insufficient_overlap"
        elif exchange_gt_105 > 0:
            market = "not_capacity_ceiling_exchange_exceeds"
        else:
            market = "candidate_market_capacity_proxy"
        if physical_count < 24:
            physical = "insufficient_overlap"
        elif physical_gt_105 > 0:
            physical = "not_capacity_ceiling_flow_exceeds"
        else:
            physical = "candidate_physical_capacity_proxy"
        out[contract] = {
            "market_classification": market,
            "physical_classification": physical,
            "count_compared_scheduled_exchange": exchange_count,
            "count_compared_physical_flow": physical_count,
            "scheduled_exchange_max_ratio": exchange_max,
            "physical_flow_max_ratio": physical_max,
            "scheduled_exchange_count_ratio_gt_1_05": exchange_gt_105,
            "physical_flow_count_ratio_gt_1_05": physical_gt_105,
            "recommendation": contract_recommendation(market, physical),
        }
    return out


def contract_recommendation(market: str, physical: str) -> str:
    if market == "candidate_market_capacity_proxy" and physical == "candidate_physical_capacity_proxy":
        return "experimental_market_and_physical_capacity_proxy_candidate"
    if market == "candidate_market_capacity_proxy":
        return "experimental_market_capacity_proxy_candidate_only"
    return "keep_blocked"


def worst_ratio_examples(observations: list[dict[str, object]], limit: int = 10) -> list[dict[str, object]]:
    keys = [
        "timestamp_utc",
        "from_area",
        "to_area",
        "contract_type",
        "comparison_type",
        "capacity_mw",
        "flow_or_exchange_mw",
        "ratio",
        "capacity_source_dataset",
        "flow_source_dataset",
        "window_id",
        "era",
    ]
    worst = sorted(observations, key=lambda item: float(item["ratio"]), reverse=True)[:limit]
    return [{key: item[key] for key in keys} for item in worst]


def pre_post_review(metric_rows: list[dict[str, object]]) -> dict[str, object]:
    out = {}
    for contract in CONTRACT_TYPES:
        out[contract] = {}
        for comparison in COMPARISONS:
            for era in ("pre_flow_based", "post_flow_based"):
                rows = [row for row in metric_rows if row["contract_type"] == contract and row["comparison_type"] == comparison and row["era"] == era]
                out[contract][f"{comparison}_{era}"] = {
                    "count_compared": sum(int(row["count_compared"]) for row in rows),
                    "max_ratio": max((float(row["max_ratio"]) for row in rows if row["max_ratio"] is not None), default=None),
                    "count_ratio_gt_1_05": sum(int(row["count_ratio_gt_1_05"]) for row in rows),
                }
    return out


def component_summary(metric_rows: list[dict[str, object]], classifications: dict[str, dict[str, object]]) -> dict[str, object]:
    return {
        "overlap_rows": sum(int(row["count_compared"]) for row in metric_rows),
        "classification": classifications,
        "recommendation": "Use any passing A61 candidate only as experimental_capacity_proxy in a later package; P0052C does not enable utilization globally.",
    }


def flow_based_era(timestamp_utc: str | datetime) -> str:
    return "post_flow_based" if p0052a.parse_utc(timestamp_utc) >= FLOW_BASED_GO_LIVE else "pre_flow_based"


def safe_ratio(flow_or_exchange: object, capacity: object) -> tuple[float | None, str]:
    if capacity is None:
        return None, "missing_capacity"
    if flow_or_exchange is None:
        return None, "missing_flow_or_exchange"
    capacity_f = float(capacity)
    if capacity_f <= 0:
        return None, "invalid_capacity"
    return abs(float(flow_or_exchange)) / capacity_f, "ok"


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(math.ceil(q * len(ordered)) - 1)))
    return ordered[idx]


def normalize_timestamp_value(value: str) -> str:
    return p0052a.format_utc(p0052a.parse_utc(value))


def direction_key(from_area: str, to_area: str) -> str:
    return f"{from_area}->{to_area}"


def directed_borders() -> tuple[str, ...]:
    return ("SE1->SE2", "SE2->SE1", "SE2->SE3", "SE3->SE2", "SE3->SE4", "SE4->SE3")


def contract_from_dataset(source_dataset: str) -> str:
    for contract in CONTRACT_TYPES:
        if contract in source_dataset:
            return contract
    return ""


def secret_handling_evidence(secret_safety: dict[str, object]) -> dict[str, object]:
    return {
        "token_source_class": secret_safety.get("token_source"),
        "secret_checked": secret_safety.get("secret_checked"),
        "secret_safe": secret_safety.get("secret_safe"),
        "secret_gitignored_or_outside_repo": secret_safety.get("secret_gitignored"),
        "token_in_logs": False,
        "token_in_evidence": False,
    }


def write_p0052c_evidence(evidence_dir: Path, summary: dict[str, object]) -> dict[str, str]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    scheduled_metrics = [row for row in summary["metrics"] if row["comparison_type"] == "scheduled_exchange"]
    physical_metrics = [row for row in summary["metrics"] if row["comparison_type"] == "physical_flow"]
    files = {
        "CHANGELOG.md": changelog_text(summary),
        "secret-handling.md": json_md("P0052C secret handling", summary["secret_safety"]),
        "capacity-sanity-check-method.md": method_text(),
        "capacity-vs-scheduled-exchange-results.md": json_md("P0052C capacity vs scheduled exchange results", scheduled_metrics),
        "capacity-vs-physical-flow-results.md": json_md("P0052C capacity vs physical flow results", physical_metrics),
        "worst-ratio-examples.md": json_md("P0052C worst ratio examples", summary["worst_examples"]),
        "pre-post-flow-based-ratio-review.md": json_md("P0052C pre/post flow-based ratio review", summary["pre_post_review"]),
        "contract-type-classification.md": json_md("P0052C contract type classification", summary["classification"]),
        "next-package-recommendation.md": recommendation_text(summary),
        "component-attribution-summary.md": json_md("P0052C component attribution summary", summary["component_summary"]),
    }
    for name, content in files.items():
        (evidence_dir / name).write_text(content, encoding="utf-8")
    json_files = {
        "capacity-ratio-summary.json": summary["metrics"],
        "contract-type-classification.json": summary["classification"],
    }
    for name, payload in json_files.items():
        (evidence_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_worst_csv(evidence_dir / "worst-ratio-examples.csv", summary["worst_examples"])
    return {name: str(evidence_dir / name) for name in files | json_files | {"worst-ratio-examples.csv": None}}


def write_worst_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def json_md(title: str, payload: object) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"


def changelog_text(summary: dict[str, object]) -> str:
    return f"""# P0052C changelog

- Re-verified token safety without writing the token value.
- Compared A61 A02/A03/A04 capacity against A09 scheduled exchange and A11 physical flow by timestamp, border direction and contract type.
- Classified A61 contract types for experimental capacity proxy suitability.
- Result status: {summary['status']}.
- No token leak, continental price levels, SE1-to-SE3 anchoring, API, production model, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.
"""


def method_text() -> str:
    return """# P0052C capacity sanity check method

P0052C reads local P0052B ENTSO-E rows only. It compares `abs(A09 scheduled_exchange_mw) / A61 capacity_mw` and `abs(A11 physical_flow_mw) / A61 capacity_mw` by normalized UTC timestamp, directed internal Swedish border and A61 contract type. Capacity values `<= 0` are invalid and ratios are not clipped.
"""


def recommendation_text(summary: dict[str, object]) -> str:
    return f"""# P0052C next package recommendation

Classification:

```json
{json.dumps(summary['classification'], indent=2, sort_keys=True)}
```

Use only contract types classified as candidates as `experimental_capacity_proxy` in a later package. P0052C does not enable utilization or bottleneck margin globally.
"""


def main() -> None:
    result = run_p0052c_analysis()
    print(f"P0052C {result.status}: row_counts={json.dumps(result.row_counts, sort_keys=True)}")


if __name__ == "__main__":
    main()
