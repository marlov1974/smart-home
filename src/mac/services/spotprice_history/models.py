"""Data models for the P0030 spot price history store."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HourlySpotPrice:
    area: str
    utc_hour_start: str
    local_hour_start: str
    local_date: str
    local_hour: int
    utc_offset: str
    fold: int
    price_sek_per_kwh: float
    price_eur_per_kwh: float | None
    exchange_rate: float | None
    source: str
    source_resolution: str
    samples: int


@dataclass(frozen=True)
class ValidationReport:
    area: str
    db_path: str
    start_date: str
    end_date: str
    ok: bool
    row_count: int
    expected_count: int
    first_utc_hour_start: str | None
    last_utc_hour_start: str | None
    duplicate_count: int
    gap_count: int
    negative_price_count: int
    min_price_sek_per_kwh: float | None
    max_price_sek_per_kwh: float | None
    mean_price_sek_per_kwh: float | None
    per_year_counts: dict[str, int]
    errors: tuple[str, ...]


@dataclass(frozen=True)
class IngestSummary:
    area: str
    db_path: str
    start_date: str
    end_date: str
    fetched_days: int
    upserted_rows: int
    validation: ValidationReport


@dataclass(frozen=True)
class LaunchdInstallResult:
    label: str
    plist_path: str
    loaded: bool
    message: str
