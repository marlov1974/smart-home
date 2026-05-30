"""Data models for P0031 weather history."""

from __future__ import annotations

from dataclasses import dataclass


WEATHER_VARIABLES = (
    "temperature_2m",
    "apparent_temperature",
    "wind_speed_10m",
    "wind_speed_100m",
    "wind_gusts_10m",
    "cloud_cover",
    "shortwave_radiation",
    "precipitation",
    "snowfall",
    "relative_humidity_2m",
    "pressure_msl",
)


@dataclass(frozen=True)
class WeatherLocation:
    location_id: str
    name: str
    latitude: float
    longitude: float
    weight: float
    area_proxy: str
    source: str
    active: bool = True


@dataclass(frozen=True)
class WeatherObservation:
    location_id: str
    utc_hour_start: str
    local_hour_start: str
    local_date: str
    local_hour: int
    timezone: str
    utc_offset: str
    fold: int
    values: dict[str, float]
    source_model: str
    source: str


@dataclass(frozen=True)
class ValidationReport:
    db_path: str
    area_proxy: str
    start_date: str
    end_date: str
    complete: bool
    location_row_count: int
    location_expected_count: int
    area_row_count: int
    area_expected_count: int
    first_utc_hour_start: str | None
    last_utc_hour_start: str | None
    location_gap_count: int
    area_gap_count: int
    duplicate_location_rows: int
    duplicate_area_rows: int
    null_counts: dict[str, int]
    per_year_location_counts: dict[str, int]
    per_year_area_counts: dict[str, int]
    variable_stats: dict[str, dict[str, float | None]]
    db_size_bytes: int
    errors: tuple[str, ...]


@dataclass(frozen=True)
class IngestSummary:
    db_path: str
    start_date: str
    end_date: str
    locations_requested: int
    fetched_location_ranges: int
    observations_upserted: int
    area_rows_upserted: int
    status: str
    validation: ValidationReport


@dataclass(frozen=True)
class LaunchdInstallResult:
    label: str
    plist_path: str
    loaded: bool
    message: str
