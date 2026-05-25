"""Compact API schema helpers for the P0017 spot forecast service."""

from __future__ import annotations

import json


class InvalidWeekError(ValueError):
    """Raised when an API or CLI week argument is invalid."""


def parse_week(raw: str | None) -> int:
    """Parse and validate an ISO week number."""

    if raw is None or raw == "":
        raise InvalidWeekError("invalid week")
    try:
        week = int(raw)
    except (TypeError, ValueError) as exc:
        raise InvalidWeekError("invalid week") from exc
    if week < 1 or week > 53:
        raise InvalidWeekError("invalid week")
    return week


def compact_json(value: object) -> str:
    """Encode a compact JSON response."""

    return json.dumps(value, separators=(",", ":"))

