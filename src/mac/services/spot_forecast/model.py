"""Week-weight spot period index model for P0017."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable, Sequence

from src.mac.services.spotprice_history.storage import connect_db, default_db_path, validate_range


PERIOD_COUNT = 21
DEFAULT_AREA = "SE3"
DEFAULT_START_DATE = "2022-05-30"
DEFAULT_HISTORY_PATH = (
    Path(__file__).resolve().parents[4]
    / "data"
    / "spot"
    / "spotprices-2025-winter-8h-weekly-period-index.json"
)


class SpotForecastError(Exception):
    """Raised when spot forecast source data or model state is invalid."""


class WeekNotFoundError(SpotForecastError):
    """Raised when a valid ISO week cannot be modeled from available data."""


@dataclass(frozen=True)
class HistoricalWeek:
    """One historical week with 21 normalized period indexes."""

    iso_year: int
    iso_week: int
    price_index: tuple[float, ...]


def _number(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise SpotForecastError(f"{field} is not numeric") from exc


def _history_record(raw: Any, index: int) -> HistoricalWeek:
    if not isinstance(raw, dict):
        raise SpotForecastError(f"weeks[{index}] is not an object")
    try:
        iso_year = int(raw["iso_year"])
        iso_week = int(raw["iso_week"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SpotForecastError(f"weeks[{index}] has invalid iso year/week") from exc
    values = raw.get("price_index")
    if not isinstance(values, list) or len(values) != PERIOD_COUNT:
        raise SpotForecastError(f"weeks[{index}].price_index must contain {PERIOD_COUNT} values")
    return HistoricalWeek(
        iso_year=iso_year,
        iso_week=iso_week,
        price_index=tuple(_number(value, f"weeks[{index}].price_index") for value in values),
    )


def load_history(path: Path | str = DEFAULT_HISTORY_PATH) -> list[HistoricalWeek]:
    """Load and validate the committed historical period-index dataset."""

    source = Path(path)
    try:
        root = json.loads(source.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SpotForecastError(f"history read failed: {source}") from exc
    except json.JSONDecodeError as exc:
        raise SpotForecastError("history file is not valid JSON") from exc
    if not isinstance(root, dict):
        raise SpotForecastError("history root is not an object")
    weeks = root.get("weeks")
    if not isinstance(weeks, list) or not weeks:
        raise SpotForecastError("history weeks must be a non-empty list")
    records = [_history_record(item, index) for index, item in enumerate(weeks)]
    return records


def load_history_from_db(
    path: Path | str = default_db_path(),
    area: str = DEFAULT_AREA,
    require_start_date: str | None = DEFAULT_START_DATE,
) -> list[HistoricalWeek]:
    """Load P0030 SQLite spot history and derive normalized weekly period indexes."""

    db_path = Path(path).expanduser()
    if not db_path.exists():
        raise SpotForecastError(f"spot history DB missing: {db_path}")
    try:
        with connect_db(db_path) as conn:
            coverage = _coverage(conn, area)
            if coverage is None:
                raise SpotForecastError(f"spot history DB has no rows for area {area}")
            start_date, end_date = coverage
            validation_start = require_start_date or start_date
            report = validate_range(conn, area, _date_from_text(validation_start), _date_from_text(end_date), db_path=str(db_path))
            if not report.ok:
                raise SpotForecastError(f"spot history DB incomplete: {report.errors}")
            if require_start_date and start_date > require_start_date:
                raise SpotForecastError(
                    f"spot history DB starts at {start_date}; expected {require_start_date}"
                )
            rows = conn.execute(
                """
                SELECT local_date, local_hour, price_sek_per_kwh
                FROM spot_prices
                WHERE area=?
                ORDER BY utc_hour_start
                """,
                (area,),
            ).fetchall()
    except sqlite3.Error as exc:
        raise SpotForecastError(f"spot history DB read failed: {db_path}") from exc
    return _weekly_history_from_rows(rows)


def db_history_metadata(path: Path | str = default_db_path(), area: str = DEFAULT_AREA) -> dict[str, object]:
    """Return public metadata for the DB-backed spot period-index model."""

    db_path = Path(path).expanduser()
    if not db_path.exists():
        raise SpotForecastError(f"spot history DB missing: {db_path}")
    with connect_db(db_path) as conn:
        coverage = _coverage(conn, area)
        if coverage is None:
            raise SpotForecastError(f"spot history DB has no rows for area {area}")
        start_date, end_date = coverage
        report = validate_range(conn, area, _date_from_text(start_date), _date_from_text(end_date), db_path=str(db_path))
    return {
        "source": "sqlite",
        "db_path": str(db_path),
        "area": area,
        "start_date": start_date,
        "end_date": end_date,
        "row_count": report.row_count,
        "expected_count": report.expected_count,
        "gap_count": report.gap_count,
        "negative_price_count": report.negative_price_count,
        "per_year_counts": report.per_year_counts,
    }


def _coverage(conn: sqlite3.Connection, area: str) -> tuple[str, str] | None:
    row = conn.execute(
        "SELECT MIN(local_date) AS start_date, MAX(local_date) AS end_date FROM spot_prices WHERE area=?",
        (area,),
    ).fetchone()
    if row is None or row["start_date"] is None or row["end_date"] is None:
        return None
    return str(row["start_date"]), str(row["end_date"])


def _date_from_text(value: str):
    from datetime import date

    return date.fromisoformat(value)


def _weekly_history_from_rows(rows: Sequence[sqlite3.Row]) -> list[HistoricalWeek]:
    buckets: dict[tuple[int, int], list[list[float]]] = {}
    for row in rows:
        iso_year, iso_week, iso_day = _date_from_text(row["local_date"]).isocalendar()
        period = (int(iso_day) - 1) * 3 + (int(row["local_hour"]) // 8)
        key = (int(iso_year), int(iso_week))
        buckets.setdefault(key, [[] for _ in range(PERIOD_COUNT)])[period].append(
            float(row["price_sek_per_kwh"])
        )
    records: list[HistoricalWeek] = []
    for (iso_year, iso_week), period_values in sorted(buckets.items()):
        if any(not values for values in period_values):
            continue
        averages = [sum(values) / len(values) for values in period_values]
        mean = sum(averages) / PERIOD_COUNT
        if mean <= 0:
            continue
        records.append(
            HistoricalWeek(
                iso_year=iso_year,
                iso_week=iso_week,
                price_index=tuple(value / mean for value in averages),
            )
        )
    if not records:
        raise SpotForecastError("spot history DB has no modelable complete ISO weeks")
    return records


def week_weight(distance: int) -> float:
    """Return the P0017 week-neighborhood weight for an ISO week distance."""

    if distance == 0:
        return 1.0
    if distance == 1:
        return 0.7
    if distance == 2:
        return 0.4
    return 0.0


def weighted_average_indexes(target_week: int, history: Sequence[HistoricalWeek]) -> list[float]:
    """Compute unnormalized weighted period indexes for a target week."""

    totals = [0.0] * PERIOD_COUNT
    total_weight = 0.0
    for record in history:
        weight = week_weight(abs(target_week - record.iso_week))
        if weight <= 0:
            continue
        total_weight += weight
        for index, value in enumerate(record.price_index):
            totals[index] += value * weight
    if total_weight <= 0:
        raise WeekNotFoundError(f"week not found: {target_week}")
    return [value / total_weight for value in totals]


def normalize_indexes(indexes: Sequence[float]) -> list[float]:
    """Normalize 21 period indexes to arithmetic mean 1.0."""

    if len(indexes) != PERIOD_COUNT:
        raise SpotForecastError(f"expected {PERIOD_COUNT} indexes")
    mean = sum(indexes) / PERIOD_COUNT
    if mean <= 0:
        raise SpotForecastError("index mean must be positive")
    return [float(value) / mean for value in indexes]


def round_indexes(indexes: Iterable[float]) -> list[float]:
    """Round public index output to two decimals."""

    values = list(indexes)
    if len(values) != PERIOD_COUNT:
        raise SpotForecastError(f"expected {PERIOD_COUNT} indexes")
    return [round(float(value), 2) for value in values]


def forecast_period_indexes(
    target_week: int,
    history: Sequence[HistoricalWeek] | None = None,
    db_path: Path | str | None = None,
    area: str = DEFAULT_AREA,
) -> list[float]:
    """Forecast compact 21-period price indexes for one ISO week."""

    records = list(history) if history is not None else load_history_from_db(db_path or default_db_path(), area)
    averaged = weighted_average_indexes(target_week, records)
    normalized = normalize_indexes(averaged)
    return round_indexes(normalized)
