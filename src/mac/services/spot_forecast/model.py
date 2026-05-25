"""Week-weight spot period index model for P0017."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable, Sequence


PERIOD_COUNT = 21
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
) -> list[float]:
    """Forecast compact 21-period price indexes for one ISO week."""

    records = list(history) if history is not None else load_history()
    averaged = weighted_average_indexes(target_week, records)
    normalized = normalize_indexes(averaged)
    return round_indexes(normalized)

