"""Shared forecast modeling period policy for spotprice diagnostics."""

from __future__ import annotations

from datetime import datetime, timezone


POLICY_VERSION = "forecast_period_policy_v1_p0053c"
MODELING_START_UTC = datetime(2022, 6, 1, 0, 0, tzinfo=timezone.utc)
TRAIN_END_UTC = datetime(2024, 12, 31, 23, 0, tzinfo=timezone.utc)
VALIDATION_START_UTC = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
VALIDATION_END_UTC = datetime(2025, 5, 31, 23, 0, tzinfo=timezone.utc)
HOLDOUT_START_UTC = datetime(2025, 6, 1, 0, 0, tzinfo=timezone.utc)


def parse_policy_timestamp(timestamp_utc: str | datetime) -> datetime:
    if isinstance(timestamp_utc, datetime):
        value = timestamp_utc
    else:
        value = datetime.fromisoformat(timestamp_utc.replace("Z", "+00:00"))
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def is_modeling_target_timestamp(timestamp_utc: str | datetime) -> bool:
    return parse_policy_timestamp(timestamp_utc) >= MODELING_START_UTC


def canonical_split_for_timestamp(timestamp_utc: str | datetime) -> str:
    value = parse_policy_timestamp(timestamp_utc)
    if value < MODELING_START_UTC:
        raise ValueError(f"timestamp before canonical modeling start: {timestamp_utc}")
    if value <= TRAIN_END_UTC:
        return "train"
    if value <= VALIDATION_END_UTC:
        return "validate"
    return "holdout"


def policy_summary() -> dict[str, object]:
    return {
        "policy_version": POLICY_VERSION,
        "forecast_modeling_start_utc": "2022-06-01T00:00:00Z",
        "model_development_start_utc": "2022-06-01T00:00:00Z",
        "model_development_end_utc": "2025-05-31T23:00:00Z",
        "train_start_utc": "2022-06-01T00:00:00Z",
        "train_end_utc": "2024-12-31T23:00:00Z",
        "validation_start_utc": "2025-01-01T00:00:00Z",
        "validation_end_utc": "2025-05-31T23:00:00Z",
        "holdout_start_utc": "2025-06-01T00:00:00Z",
        "boundary_identity": "timestamp_utc",
        "fixed_cet_rule": "model_cet_timestamp = timestamp_utc + 1h all year; calendar feature only",
        "context_only_lag_warmup": True,
    }
