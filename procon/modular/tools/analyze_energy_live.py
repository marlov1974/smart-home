#!/usr/bin/env python3
"""Offline analysis of a Shelly ``energy_pair_v1`` 1.4.1 field run.

The analyzer only reads local evidence files.  It deliberately does not import
the live runner or any networking module.  A growing JSONL file is accepted: a
single incomplete final line is ignored and reported, while malformed earlier
lines remain fatal.

Pair power comes from each device's signed EFFECT short-window feedback.  KVS
``shortw`` is the planner's forecast shortfall and is never treated as power.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Iterable, Sequence


TARGETS_WH = (1500, 2000, 2500, 4000, 2500, 2000, 1500)
QUARTER_SECONDS = 900.0
TRIAL_SECONDS = QUARTER_SECONDS * len(TARGETS_WH)
INVALID_S32 = -(1 << 31)
SATURATION_REASONS = {4, 15}
EXPECTED_EXECUTOR_VERSION = "1.4.1"
EXPECTED_EXECUTOR_SHA256 = "f5278ee41f8058d82e8e54014729931fdfa00e26a8aa4c2a437386a1a6bfac11"

PHASE_NAMES = {
    0: "off",
    1: "start",
    2: "capture",
    3: "hold",
    4: "limited",
    5: "invalid_feedback",
    6: "restoring",
    7: "wait_native",
    8: "settling",
}

REASON_NAMES = {
    0: "ok",
    1: "bad_feedback",
    2: "native_inhibit",
    3: "mode_changed",
    4: "temperature_cap",
    5: "unknown_unreachable",
    6: "cumulative_cap",
    7: "link_lost",
    8: "lease_expired",
    9: "aborted",
    10: "temperature_floor",
    11: "read_timeout",
    12: "readback_mismatch",
    13: "wait_timeout",
    14: "response_pending",
    15: "request_cap",
    16: "minimum_output",
    17: "source_stale",
}


def signed32(high: int, low: int) -> int:
    value = high * 65536 + low
    return value - (1 << 32) if value >= (1 << 31) else value


def signed16(value: int) -> int:
    return value - 65536 if value >= 32768 else value


def parse_kvs(text: str | None) -> dict[str, str]:
    fields: dict[str, str] = {}
    for item in (text or "").split("|"):
        if "=" in item:
            key, value = item.split("=", 1)
            fields[key] = value
    return fields


def _integer(fields: dict[str, str], key: str) -> int | None:
    try:
        return int(fields[key])
    except (KeyError, TypeError, ValueError):
        return None


def _timestamp(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def _read_json(path: Path) -> object | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def executor_identity(directory: Path, installed: object) -> dict[str, object]:
    # This analyzer describes the completed 1.4.1 field run. Keep its identity
    # pinned to the frozen release when the canonical executor moves forward.
    # A standalone source archive intentionally does not embed another release;
    # retain the expected identity there without failing the offline analysis.
    source = (
        Path(__file__).resolve().parents[1]
        / "release-effect-energy-v2-20261014/shelly/energy_pair_v1.js"
    )
    source_bytes = source.read_bytes() if source.is_file() else None
    source_digest = hashlib.sha256(source_bytes).hexdigest() if source_bytes is not None else None
    before = _read_json(directory / "script7-before.json")
    before_code = before.get("data") if isinstance(before, dict) else None
    before_bytes = before_code.encode() if isinstance(before_code, str) else None
    installed = installed if isinstance(installed, dict) else {}
    return {
        "expected_version": EXPECTED_EXECUTOR_VERSION,
        "expected_sha256": EXPECTED_EXECUTOR_SHA256,
        "repository_source": str(source),
        "repository_source_available": source_bytes is not None,
        "repository_source_bytes": len(source_bytes) if source_bytes is not None else None,
        "repository_source_sha256": source_digest,
        "repository_source_matches_expected": (
            source_digest == EXPECTED_EXECUTOR_SHA256 if source_digest is not None else None
        ),
        "installed_event_bytes": installed.get("bytes"),
        "installed_event_source": installed.get("source"),
        "installed_event_size_matches": (
            installed.get("bytes") == len(source_bytes) if source_bytes is not None else None
        ),
        "script7_before_bytes": len(before_bytes) if before_bytes is not None else None,
        "script7_before_sha256": hashlib.sha256(before_bytes).hexdigest() if before_bytes is not None else None,
        "script7_before_matches_expected": (
            hashlib.sha256(before_bytes).hexdigest() == EXPECTED_EXECUTOR_SHA256
            if before_bytes is not None
            else None
        ),
        "proof_limit": "The runner verifies the uploaded source in memory but does not persist its post-upload hash; the installed event records only source path and byte count.",
    }


def read_events(path: Path) -> tuple[list[dict[str, object]], bool, str]:
    raw = path.read_bytes()
    terminated = raw.endswith(b"\n")
    lines = raw.decode("utf-8").splitlines()
    events: list[dict[str, object]] = []
    incomplete_final_line = False
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            if index == len(lines) - 1 and not terminated:
                incomplete_final_line = True
                break
            raise
        if not isinstance(event, dict):
            raise ValueError(f"event line {index + 1} is not an object")
        events.append(event)
    return events, incomplete_final_line, hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class DeviceSample:
    target_w: int
    short_w: int | None
    phase: int
    reason: int
    quality: int | None
    ready: int | None
    age_s: int | None
    span_s: int | None
    hz: int | None
    derivative_w_per_min: int | None
    control_state: int | None
    control_saved: int | None

    @property
    def fresh_short_w(self) -> int | None:
        # Match the live executor's ``w >= 0 && age < 60`` admission rule.
        # INT32_MIN is decoded to None above, but any other negative power is
        # also unavailable to EFFECT and must not enter field-run statistics.
        if (
            self.short_w is None
            or self.short_w < 0
            or self.age_s is None
            or self.age_s >= 60
        ):
            return None
        return self.short_w


@dataclass(frozen=True)
class Sample:
    timestamp: float
    elapsed_s: float
    script_running: bool | None
    status_phase: str
    quarter: int | None
    quarter_wh: int | None
    total_wh: int | None
    wanted_pair_w: int | None
    command_pair_w: int | None
    sent_pair_w: int | None
    reachable_pair_w: int | None
    forecast_shortfall_w: int | None
    forecast_error_wh: int | None
    unknown_s: int | None
    results_wh: tuple[int, ...]
    devices: dict[int, DeviceSample]

    @property
    def pair_power_w(self) -> int | None:
        if set(self.devices) != {1, 2}:
            return None
        powers = [self.devices[sid].fresh_short_w for sid in (1, 2)]
        if any(value is None for value in powers):
            return None
        return int(powers[0]) + int(powers[1])

    @property
    def accepted_target_sum_w(self) -> int | None:
        if set(self.devices) != {1, 2}:
            return None
        if any(self.devices[sid].control_state != 4 for sid in (1, 2)):
            return None
        return sum(self.devices[sid].target_w for sid in (1, 2))


def _decode_device(raw: object) -> DeviceSample | None:
    if not isinstance(raw, dict):
        return None
    words = raw.get("feedback")
    if not isinstance(words, list) or len(words) < 22:
        return None
    try:
        short_w = signed32(int(words[7]), int(words[8]))
        if short_w == INVALID_S32:
            short_w = None
        control = raw.get("control") if isinstance(raw.get("control"), dict) else {}
        return DeviceSample(
            target_w=int(words[3]),
            short_w=short_w,
            phase=int(words[1]),
            reason=int(words[2]),
            quality=int(words[13]) if len(words) > 13 else None,
            ready=int(words[14]) if len(words) > 14 else None,
            age_s=int(words[16]) if len(words) > 16 else None,
            span_s=int(words[17]) if len(words) > 17 else None,
            hz=int(words[21]) if len(words) > 21 else None,
            derivative_w_per_min=(signed16(int(words[28])) if len(words) > 28 else None),
            control_state=(int(control["state"]) if "state" in control else None),
            control_saved=(int(control["saved"]) if "saved" in control else None),
        )
    except (IndexError, TypeError, ValueError):
        return None


def _decode_sample(event: dict[str, object], started: float) -> Sample | None:
    if event.get("kind") != "sample" or not isinstance(event.get("data"), dict):
        return None
    data = event["data"]
    fields = parse_kvs(data.get("kvs") if isinstance(data.get("kvs"), str) else None)
    if "phase" not in fields:
        return None
    devices: dict[int, DeviceSample] = {}
    raw_devices = data.get("devices")
    if isinstance(raw_devices, dict):
        for sid in (1, 2):
            decoded = _decode_device(raw_devices.get(str(sid), raw_devices.get(sid)))
            if decoded is not None:
                devices[sid] = decoded
    results: tuple[int, ...] = ()
    if fields.get("results"):
        try:
            results = tuple(int(value) for value in fields["results"].split(","))
        except ValueError:
            results = ()
    stamp = _timestamp(str(event["time"]))
    script = data.get("script") if isinstance(data.get("script"), dict) else {}
    running = script.get("running")
    return Sample(
        timestamp=stamp,
        elapsed_s=stamp - started,
        script_running=running if isinstance(running, bool) else None,
        status_phase=fields.get("phase", ""),
        quarter=_integer(fields, "q"),
        quarter_wh=_integer(fields, "qwh"),
        total_wh=_integer(fields, "totalwh"),
        wanted_pair_w=_integer(fields, "want"),
        command_pair_w=_integer(fields, "cmd"),
        sent_pair_w=_integer(fields, "sent"),
        reachable_pair_w=_integer(fields, "reach"),
        forecast_shortfall_w=_integer(fields, "shortw"),
        forecast_error_wh=_integer(fields, "ferr"),
        unknown_s=_integer(fields, "unknown"),
        results_wh=results,
        devices=devices,
    )


def _deduplicate_points(points: Iterable[tuple[float, float | int | None]]) -> list[tuple[float, float | None]]:
    by_time: dict[float, float | None] = {}
    for stamp, value in points:
        by_time[float(stamp)] = None if value is None else float(value)
    return sorted(by_time.items())


def _linear_value(t0: float, value0: float, t1: float, value1: float, at: float) -> float:
    if t1 == t0:
        return value1
    return value0 + (value1 - value0) * (at - t0) / (t1 - t0)


def supported_stats(
    points: Iterable[tuple[float, float | int | None]],
    start: float,
    end: float,
    max_gap_s: float,
) -> dict[str, float | int | None | str]:
    """Time-weighted linear statistics without bridging invalid or long gaps."""
    ordered = _deduplicate_points(points)
    area = square_area = coverage = 0.0
    for (t0, value0), (t1, value1) in zip(ordered, ordered[1:]):
        if value0 is None or value1 is None or t1 <= t0 or t1 - t0 > max_gap_s:
            continue
        low, high = max(start, t0), min(end, t1)
        if high <= low:
            continue
        left = _linear_value(t0, value0, t1, value1, low)
        right = _linear_value(t0, value0, t1, value1, high)
        duration = high - low
        area += (left + right) * duration / 2
        square_area += (left * left + left * right + right * right) * duration / 3
        coverage += duration
    observations = [(stamp, value) for stamp, value in ordered if start <= stamp <= end and value is not None]
    observed_values = [value for _, value in observations]
    weighted_mean = area / coverage if coverage else None
    variance = max(0.0, square_area / coverage - weighted_mean * weighted_mean) if coverage else None
    trend = None
    if len(observations) >= 2:
        center_t = mean(stamp for stamp, _ in observations)
        center_y = mean(value for _, value in observations)
        denominator = sum((stamp - center_t) ** 2 for stamp, _ in observations)
        if denominator:
            trend = (
                sum((stamp - center_t) * (value - center_y) for stamp, value in observations)
                / denominator
                * 60
            )
    return {
        "observations": len(observations),
        "supported_s": coverage,
        "unsupported_s": max(0.0, end - start - coverage),
        "time_weighted_mean_w": weighted_mean,
        "time_weighted_stddev_w": math.sqrt(variance) if variance is not None else None,
        "sampled_min_w": min(observed_values) if observed_values else None,
        "sampled_peak_w": max(observed_values) if observed_values else None,
        "observed_linear_trend_w_per_min": trend,
    }


def _quarter_window(started: float, quarter: int, observed_end: float) -> tuple[float, float]:
    low = started + quarter * QUARTER_SECONDS
    high = min(started + (quarter + 1) * QUARTER_SECONDS, observed_end)
    return low, max(low, high)


def allocate_unknown(
    samples: Sequence[Sample], started: float, observed_end: float
) -> tuple[list[dict[str, float]], dict[str, object]]:
    """Allocate a cumulative union counter with honest boundary uncertainty.

    A counter increase observed wholly inside a quarter is exact for that
    quarter.  If its observation interval crosses a boundary, the estimate is
    proportional to overlap and the lower/upper bounds retain that ambiguity.
    """
    points: list[tuple[float, int]] = [(started, 0)]
    for sample in samples:
        if sample.unknown_s is None:
            continue
        stamp = min(max(sample.timestamp, started), observed_end)
        points.append((stamp, sample.unknown_s))
    deduplicated: dict[float, int] = {}
    for stamp, value in points:
        deduplicated[stamp] = value
    ordered = sorted(deduplicated.items())
    buckets = [dict(estimate_s=0.0, lower_bound_s=0.0, upper_bound_s=0.0) for _ in TARGETS_WH]
    decreases: list[dict[str, float | int]] = []
    unallocated = 0.0
    for (before_t, before), (after_t, after) in zip(ordered, ordered[1:]):
        if after < before:
            decreases.append({"at_s": after_t - started, "from": before, "to": after})
            continue
        delta = float(after - before)
        if not delta:
            continue
        duration = after_t - before_t
        if duration <= 0:
            unallocated += delta
            continue
        overlaps: list[tuple[int, float]] = []
        for quarter in range(len(TARGETS_WH)):
            low = started + quarter * QUARTER_SECONDS
            high = low + QUARTER_SECONDS
            overlap = max(0.0, min(after_t, high) - max(before_t, low))
            if overlap:
                overlaps.append((quarter, overlap))
        total_overlap = sum(overlap for _, overlap in overlaps)
        if not total_overlap:
            unallocated += delta
            continue
        for quarter, overlap in overlaps:
            buckets[quarter]["estimate_s"] += delta * overlap / total_overlap
            buckets[quarter]["upper_bound_s"] += delta
        if len(overlaps) == 1:
            buckets[overlaps[0][0]]["lower_bound_s"] += delta
    for quarter, bucket in enumerate(buckets):
        observed = max(0.0, min(observed_end, started + (quarter + 1) * QUARTER_SECONDS) - (started + quarter * QUARTER_SECONDS))
        bucket["upper_bound_s"] = min(observed, bucket["upper_bound_s"])
    final_total = ordered[-1][1] if ordered else 0
    return buckets, {
        "observed_total_s": final_total,
        "allocated_estimate_s": sum(bucket["estimate_s"] for bucket in buckets),
        "unallocated_s": unallocated,
        "counter_decreases": decreases,
        "method": "KVS unknown is a cumulative union counter. Per-quarter estimates split each observed increment by interval overlap; bounds retain quarter-boundary ambiguity.",
    }


def _observed_sequence(values: Iterable[int | None]) -> list[int]:
    sequence: list[int] = []
    for value in values:
        if value is not None and (not sequence or sequence[-1] != value):
            sequence.append(value)
    return sequence


def command_stats(samples: Sequence[Sample]) -> dict[str, object]:
    sent_uninitialized = sum(sample.sent_pair_w == 0 for sample in samples)
    sent = [sample.sent_pair_w for sample in samples if sample.sent_pair_w is not None and sample.sent_pair_w > 0]
    command = [sample.command_pair_w for sample in samples if sample.command_pair_w is not None]
    accepted = [sample.accepted_target_sum_w for sample in samples if sample.accepted_target_sum_w is not None]
    mismatch = sum(
        sample.sent_pair_w is not None
        and sample.sent_pair_w > 0
        and sample.command_pair_w is not None
        and sample.sent_pair_w != sample.command_pair_w
        for sample in samples
    )
    accepted_mismatch = sum(
        sample.sent_pair_w is not None
        and sample.sent_pair_w > 0
        and sample.accepted_target_sum_w is not None
        and sample.sent_pair_w != sample.accepted_target_sum_w
        for sample in samples
    )
    return {
        "observations": len(sent),
        "sent_uninitialized_observations": sent_uninitialized,
        "sent_sample_mean_w": mean(sent) if sent else None,
        "sent_min_w": min(sent) if sent else None,
        "sent_max_w": max(sent) if sent else None,
        "sent_observed_sequence_w": _observed_sequence(sent),
        "command_observed_sequence_w": _observed_sequence(command),
        "accepted_target_sum_observed_sequence_w": _observed_sequence(accepted),
        "command_vs_sent_mismatch_observations": mismatch,
        "sent_vs_accepted_target_mismatch_observations": accepted_mismatch,
    }


def limiter_stats(samples: Sequence[Sample], sid: int, max_gap_s: float) -> dict[str, object]:
    timeline = [
        (
            sample.timestamp,
            sample.devices[sid]
            if sid in sample.devices
            and sample.devices[sid].control_state == 4
            and sample.status_phase != "complete"
            else None,
        )
        for sample in samples
    ]
    observed = [(stamp, device) for stamp, device in timeline if device is not None]
    reasons = Counter(device.reason for _, device in observed if device.phase == 4)
    limited = sum(device.phase == 4 for _, device in observed)
    saturation = sum(device.phase == 4 and device.reason in SATURATION_REASONS for _, device in observed)
    confirmed_limited = 0.0
    confirmed_reasons: Counter[int] = Counter()
    for (before_t, before), (after_t, after) in zip(timeline, timeline[1:]):
        duration = after_t - before_t
        if before is None or after is None or duration <= 0 or duration > max_gap_s:
            continue
        if before.phase == 4 and after.phase == 4:
            confirmed_limited += duration
            if before.reason == after.reason:
                confirmed_reasons[before.reason] += duration
    return {
        "observations": len(observed),
        "limited_observations": limited,
        "limited_fraction": limited / len(observed) if observed else None,
        "saturation_observations": saturation,
        "saturation_fraction": saturation / len(observed) if observed else None,
        "limited_reason_observations": {
            f"{reason}:{REASON_NAMES.get(reason, 'unknown')}": count for reason, count in sorted(reasons.items())
        },
        "confirmed_limited_s": confirmed_limited,
        "confirmed_same_reason_s": {
            f"{reason}:{REASON_NAMES.get(reason, 'unknown')}": duration
            for reason, duration in sorted(confirmed_reasons.items())
        },
    }


def _ramp_stats(samples: Sequence[Sample], sid: int, max_gap_s: float) -> dict[str, object]:
    timeline = [
        (
            sample,
            sample.devices[sid]
            if sid in sample.devices
            and sample.devices[sid].control_state == 4
            and sample.status_phase != "complete"
            else None,
        )
        for sample in samples
    ]
    rates: list[float] = []
    for (before_sample, before), (after_sample, after) in zip(timeline, timeline[1:]):
        duration = after_sample.timestamp - before_sample.timestamp
        if before is None or after is None or duration <= 0 or duration > max_gap_s:
            continue
        left, right = before.fresh_short_w, after.fresh_short_w
        if left is None or right is None:
            continue
        rates.append((right - left) * 60 / duration)
    rising = [rate for rate in rates if rate > 0]
    falling = [rate for rate in rates if rate < 0]
    return {
        "supported_adjacent_intervals": len(rates),
        "steepest_observed_rise_w_per_min": max(rising) if rising else None,
        "median_observed_rise_w_per_min": median(rising) if rising else None,
        "steepest_observed_fall_w_per_min": min(falling) if falling else None,
        "median_observed_fall_w_per_min": median(falling) if falling else None,
        "classification": "descriptive slopes of overlapping short-window means; not an independent physical slew limit",
    }


def _target_segments(samples: Sequence[Sample], sid: int, max_gap_s: float) -> list[dict[str, object]]:
    groups: list[list[Sample]] = []
    current: list[Sample] = []
    for sample in samples:
        active = (
            sid in sample.devices
            and sample.devices[sid].control_state == 4
            and sample.status_phase != "complete"
        )
        if not active:
            if current:
                groups.append(current)
                current = []
            continue
        changed = current and current[-1].devices[sid].target_w != sample.devices[sid].target_w
        gap = current and sample.timestamp - current[-1].timestamp > max_gap_s
        if changed or gap:
            groups.append(current)
            current = []
        current.append(sample)
    if current:
        groups.append(current)
    output: list[dict[str, object]] = []
    for group in groups:
        target = group[0].devices[sid].target_w
        valid = [sample for sample in group if sample.devices[sid].fresh_short_w is not None]
        duration = group[-1].timestamp - group[0].timestamp
        start_w = valid[0].devices[sid].fresh_short_w if valid else None
        end_w = valid[-1].devices[sid].fresh_short_w if valid else None
        output.append(
            {
                "target_w": target,
                "first_observed_s": group[0].elapsed_s,
                "last_observed_s": group[-1].elapsed_s,
                "observed_dwell_s": duration,
                "observations": len(group),
                "valid_power_observations": len(valid),
                "start_power_w": start_w,
                "end_power_w": end_w,
                "net_change_w": (end_w - start_w if start_w is not None and end_w is not None else None),
                "net_change_w_per_min": (
                    (end_w - start_w) * 60 / duration
                    if start_w is not None and end_w is not None and duration > 0
                    else None
                ),
                "limited_observations": sum(sample.devices[sid].phase == 4 for sample in group),
            }
        )
    return output


def _stable_hold(samples: Sequence[Sample], sid: int, max_gap_s: float) -> dict[str, object]:
    target = None
    target_since = None
    last_active_at = None
    errors: list[float] = []
    powers: list[float] = []
    targets: set[int] = set()
    for sample in samples:
        active = (
            sid in sample.devices
            and sample.devices[sid].control_state == 4
            and sample.status_phase != "complete"
        )
        if not active:
            target = target_since = last_active_at = None
            continue
        device = sample.devices[sid]
        if last_active_at is None or sample.timestamp - last_active_at > max_gap_s:
            target = None
            target_since = sample.timestamp
        if device.target_w != target:
            target = device.target_w
            target_since = sample.timestamp
        last_active_at = sample.timestamp
        power = device.fresh_short_w
        if (
            power is not None
            and target_since is not None
            and sample.timestamp - target_since >= 180
            and device.phase == 3
            and device.reason == 0
        ):
            errors.append(power - device.target_w)
            powers.append(power)
            targets.add(device.target_w)
    return {
        "qualification": "target observed unchanged for >=180s, EFFECT hold/ok, feedback age <60s",
        "classification": "descriptive tracking subset; HOLD and an unchanged target do not prove a stationary plant",
        "observations": len(errors),
        "targets_w": sorted(targets),
        "mean_error_w": mean(errors) if errors else None,
        "mean_absolute_error_w": mean(abs(value) for value in errors) if errors else None,
        "error_stddev_w": pstdev(errors) if len(errors) >= 2 else (0.0 if errors else None),
        "within_500w_fraction": sum(abs(value) <= 500 for value in errors) / len(errors) if errors else None,
        "power_mean_w": mean(powers) if powers else None,
        "power_stddev_w": pstdev(powers) if len(powers) >= 2 else (0.0 if powers else None),
    }


def device_summary(
    samples: Sequence[Sample], sid: int, started: float, observed_end: float, max_gap_s: float
) -> dict[str, object]:
    active = [
        sample for sample in samples
        if sid in sample.devices
        and sample.devices[sid].control_state == 4
        and sample.status_phase != "complete"
    ]
    points = [
        (
            sample.timestamp,
            sample.devices[sid].fresh_short_w
            if sid in sample.devices
            and sample.devices[sid].control_state == 4
            and sample.status_phase != "complete"
            else None,
        )
        for sample in samples
    ]
    hz = [sample.devices[sid].hz for sample in active if sample.devices[sid].hz not in (None, 255)]
    last_start = max(started, observed_end - 300)
    return {
        "active_control_observations": len(active),
        "power": supported_stats(points, started, observed_end, max_gap_s),
        "last_5_minutes": supported_stats(points, last_start, observed_end, max_gap_s),
        "ramp": _ramp_stats(samples, sid, max_gap_s),
        "stable_hold": _stable_hold(samples, sid, max_gap_s),
        "accepted_target_segments": _target_segments(samples, sid, max_gap_s),
        "limiter": limiter_stats(samples, sid, max_gap_s),
        "observed_hz_range": [min(hz), max(hz)] if hz else None,
    }


def restoration_summary(
    directory: Path,
    events: Sequence[dict[str, object]],
    execution_complete: bool,
) -> dict[str, object]:
    original = _read_json(directory / "original-settings.json")
    raw = _read_json(directory / "restoration.json")
    postflight = _read_json(directory / "postflight.json")
    source = "restoration.json" if raw is not None else None
    if raw is None:
        restoration_events = [event for event in events if event.get("kind") == "restoration"]
        if restoration_events and isinstance(restoration_events[-1].get("data"), dict):
            raw = restoration_events[-1]["data"]
            source = "events.jsonl restoration event"
    cleanup_errors = [event for event in events if event.get("kind") == "script_cleanup_error"]
    postflight_script = (
        postflight.get("script_7")
        if isinstance(postflight, dict) and isinstance(postflight.get("script_7"), dict)
        else None
    )
    cleanup_verified = (
        postflight_script.get("running") is False
        and postflight_script.get("enabled") is False
        if postflight_script is not None
        else None
    )
    if cleanup_errors:
        cleanup_verified = False
    if not isinstance(raw, dict):
        return {
            "present": False,
            "state": "missing" if execution_complete else "pending",
            "verified": None,
            "devices": {},
            "script_cleanup_error_events": len(cleanup_errors),
            "script_stopped_and_disabled_verified": cleanup_verified,
            "postflight_present": postflight is not None,
        }
    devices: dict[str, object] = {}
    verified = True
    for sid in (1, 2):
        item = raw.get(str(sid), raw.get(sid))
        before = original.get(str(sid), original.get(sid)) if isinstance(original, dict) else None
        item = item if isinstance(item, dict) else {}
        before = before if isinstance(before, dict) else {}
        control = item.get("control") if isinstance(item.get("control"), dict) else {}
        native = item.get("native") if isinstance(item.get("native"), dict) else {}
        expected_native = before.get("native") if isinstance(before.get("native"), dict) else {}
        native_keys = ("power", "mode", "flow", "dhw", "boost")
        required_native_keys = ("power", "mode", "dhw", "boost")
        comparisons = {
            key: {
                "before": expected_native.get(key),
                "after": native.get(key),
                "match": key in expected_native and native.get(key) == expected_native.get(key),
            }
            for key in native_keys
        }
        control_idle = (
            control.get("state") == 0
            and control.get("saved") == 0
            and control.get("touched") == 0
            and control.get("lease_s") == 0
            and control.get("error") == 0
        )
        strict = item.get("verified") is True and control_idle and all(
            comparisons[key]["match"] for key in required_native_keys
        )
        verified = verified and strict
        devices[str(sid)] = {
            "verified": strict,
            "runner_verified": item.get("verified") is True,
            "control_idle": control_idle,
            "native_snapshot": comparisons,
            "control_after": control,
            "native_before": expected_native,
            "native_after": native,
            "error": item.get("error"),
        }
    if verified and cleanup_verified is True:
        state = "native_control_and_cleanup_verified"
    elif verified and cleanup_verified is None:
        state = "native_control_verified_cleanup_unverified"
    else:
        state = "incomplete_or_failed"
    return {
        "present": True,
        "source": source,
        "state": state,
        "verified": verified,
        "devices": devices,
        "script_cleanup_error_events": len(cleanup_errors),
        "script_stopped_and_disabled_verified": cleanup_verified,
        "postflight_present": postflight is not None,
        "postflight_verified_at": (
            postflight.get("verified_at") if isinstance(postflight, dict) else None
        ),
        "note": (
            "Device restoration verifies idle control and baseline power/mode/DHW/boost. "
            "Curve-mode flow is diagnostic because it can change naturally. Script cleanup "
            "is positively verified only when postflight.json records Script 7 stopped and disabled."
        ),
    }


def _quarter_samples(samples: Sequence[Sample], quarter: int) -> list[Sample]:
    return [
        sample
        for sample in samples
        if sample.quarter == quarter and sample.status_phase != "complete"
    ]


def analyze(directory: Path, max_gap_s: float = 60.0) -> dict[str, object]:
    if directory.is_file():
        events_path = directory
        directory = directory.parent
    else:
        events_path = directory / "events.jsonl"
    events, incomplete_final_line, digest = read_events(events_path)
    started_events = [event for event in events if event.get("kind") == "started"]
    if not started_events:
        raise ValueError("events contain no started event")
    if len(started_events) != 1:
        raise ValueError("events contain multiple started events; split reused evidence into one run per directory")
    started_event = started_events[0]
    started = _timestamp(str(started_event["time"]))
    samples = [decoded for event in events if (decoded := _decode_sample(event, started)) is not None]
    samples.sort(key=lambda sample: sample.timestamp)
    if not samples:
        raise ValueError("events contain no decodable status samples")

    final = samples[-1]
    execution_complete = final.status_phase == "complete" and final.script_running is False
    results_complete = len(final.results_wh) == len(TARGETS_WH)
    complete = execution_complete and results_complete
    fixed_end = started + TRIAL_SECONDS
    observed_end = fixed_end if execution_complete else min(samples[-1].timestamp, fixed_end)
    current_quarter = final.quarter if final.quarter is not None else 0
    unknown_buckets, unknown_total = allocate_unknown(samples, started, observed_end)

    pair_points = [(sample.timestamp, sample.pair_power_w) for sample in samples]
    quarters: list[dict[str, object]] = []
    cumulative_error = 0
    cumulative_available = True
    for quarter, target in enumerate(TARGETS_WH):
        selected = _quarter_samples(samples, quarter)
        if complete:
            measured = final.results_wh[quarter]
            state = "complete"
        elif quarter < current_quarter and quarter < len(final.results_wh):
            measured = final.results_wh[quarter]
            state = "complete"
        elif quarter == current_quarter and quarter < len(TARGETS_WH):
            measured = final.quarter_wh
            state = "in_progress"
        else:
            measured = None
            state = "pending"
        error = measured - target if measured is not None and state == "complete" else None
        provisional_error = measured - target if measured is not None and state == "in_progress" else None
        if error is None:
            cumulative_available = False
        elif cumulative_available:
            cumulative_error += error
        low, high = _quarter_window(started, quarter, observed_end)
        power = supported_stats(pair_points, low, high, max_gap_s) if high > low else None
        sent_commands = command_stats(selected) if selected else None
        limiter = (
            {str(sid): limiter_stats(selected, sid, max_gap_s) for sid in (1, 2)}
            if selected
            else None
        )
        quarters.append(
            {
                "quarter": quarter + 1,
                "state": state,
                "target_wh": target,
                "measured_wh": measured,
                "error_wh": error,
                "provisional_error_vs_full_target_wh": provisional_error,
                "cumulative_error_wh": cumulative_error if error is not None and cumulative_available else None,
                "credited_mean_w": measured * 4 if measured is not None and state == "complete" else None,
                "observed_duration_s": high - low,
                "unknown_s": unknown_buckets[quarter],
                "pair_power": power,
                "sent_commands": sent_commands,
                "limiter": limiter,
            }
        )

    installed = next((event.get("data") for event in events if event.get("kind") == "installed"), None)
    identity = executor_identity(directory, installed)
    status_versions = sorted(
        {
            parse_kvs(event["data"].get("kvs")).get("v")
            for event in events
            if event.get("kind") == "sample"
            and isinstance(event.get("data"), dict)
            and isinstance(event["data"].get("kvs"), str)
        }
        - {None}
    )
    total_measured = (
        final.total_wh
        if final.total_wh is not None
        else (sum(final.results_wh) if complete else None)
    )
    total_target = sum(TARGETS_WH)
    active_samples = [sample for sample in samples if sample.status_phase != "complete"]
    transitions = []
    previous_sent = None
    for sample in active_samples:
        if sample.sent_pair_w is None or sample.sent_pair_w <= 0 or sample.sent_pair_w == previous_sent:
            continue
        mailboxes = {
            str(sid): {
                "target_w": sample.devices[sid].target_w,
                "control_state": sample.devices[sid].control_state,
                "accepted_active_target": sample.devices[sid].control_state == 4,
            }
            for sid in (1, 2)
            if sid in sample.devices
        }
        transitions.append(
            {
                "first_observed_s": sample.elapsed_s,
                "quarter": min(7, max(1, int(sample.elapsed_s // QUARTER_SECONDS) + 1)),
                "from_w": previous_sent,
                "to_w": sample.sent_pair_w,
                "command_w": sample.command_pair_w,
                "accepted_device_targets_w": {
                    sid: item["target_w"]
                    for sid, item in mailboxes.items()
                    if item["accepted_active_target"]
                },
                "observed_device_mailboxes": mailboxes,
            }
        )
        previous_sent = sample.sent_pair_w

    result = {
        "schema_version": 1,
        "analyzer": "energy_pair_v1 1.4.1 offline field analysis",
        "evidence": {
            "directory": str(directory),
            "events_path": str(events_path),
            "events_sha256": digest,
            "incomplete_final_jsonl_line": incomplete_final_line,
            "event_count": len(events),
            "status_samples": len(samples),
            "started_unix_s": started,
            "observed_duration_s": observed_end - started,
            "installed_event": installed,
            "executor_identity": identity,
            "kvs_versions": status_versions,
            "read_only": True,
        },
        "run": {
            "complete": complete,
            "execution_phase_complete": execution_complete,
            "seven_result_slots_present": results_complete,
            "current_phase": final.status_phase,
            "script_running": final.script_running,
            "current_quarter_index": current_quarter,
            "nonterminal_complete_samples": sum(
                sample.status_phase == "complete" for sample in samples[:-1]
            ),
        },
        "energy": {
            "target_wh": total_target,
            "measured_wh": total_measured,
            "error_wh": total_measured - total_target if complete and total_measured is not None else None,
            "provisional_total_wh": total_measured if not complete else None,
            "ledger_total_wh": final.total_wh,
            "results_sum_minus_ledger_wh": (
                sum(final.results_wh) - final.total_wh
                if complete and final.total_wh is not None
                else None
            ),
            "final_values": complete,
            "quarters": quarters,
            "unknown": unknown_total,
        },
        "pair_power": supported_stats(pair_points, started, observed_end, max_gap_s),
        "commands": {
            "all_samples": command_stats(active_samples),
            "observed_sent_transitions": transitions,
        },
        "devices": {
            str(sid): device_summary(samples, sid, started, observed_end, max_gap_s)
            for sid in (1, 2)
        },
        "restoration": restoration_summary(directory, events, execution_complete),
        "definitions": {
            "effect_phases": PHASE_NAMES,
            "effect_reasons": REASON_NAMES,
            "saturation_reasons": sorted(SATURATION_REASONS),
            "power_statistics": (
                f"Piecewise-linear integration between adjacent fresh feedback observations; "
                f"invalid/inactive samples and gaps over {max_gap_s:g}s break support. Peaks are "
                "sampled short-window means, not instantaneous maxima."
            ),
            "sent_commands": (
                "KVS sent is sampled asynchronously. Value 0 is the startup/uninitialized sentinel "
                "and is counted separately, not as a command."
            ),
            "limiter_denominator": "observations with decoded device feedback and active EFFECT control state 4",
        },
        "limitations": [
            "Hydraulic power is the firmware short-window water-side estimate, not electrical power or COP.",
            "Final quarter Wh values and their credited means are rounded executor ledger values.",
            "VP1 and VP2 feedback are sequential host RPC reads, so pair observations are near-simultaneous rather than atomic.",
            "Short-window means overlap; samples and adjacent slopes are not statistically independent.",
            "KVS shortw is forecast shortfall W and is excluded from all power statistics.",
            "Per-quarter unknown time is reconstructed from a cumulative union counter; boundary-crossing increments have explicit bounds.",
            "Command and device-target reads are sequential; transition mismatches require persistence before they indicate a failed command.",
        ],
    }
    return result


def _number(value: object, digits: int = 0) -> str:
    if value is None:
        return "—"
    return f"{float(value):.{digits}f}"


def render_markdown(result: dict[str, object]) -> str:
    energy = result["energy"]
    run = result["run"]
    state = "slutfört" if run["complete"] else f"pågående ({run['current_phase']})"
    measured_label = "uppmätt" if run["complete"] else "uppmätt hittills (provisoriskt)"
    lines = [
        "# EFFECT pair-energy 1.4.1 — offlineanalys",
        "",
        f"Status: **{state}**. Mål {_number(energy['target_wh'])} Wh, "
        f"{measured_label} {_number(energy['measured_wh'])} Wh, fel {_number(energy['error_wh'])} Wh. "
        f"Exekverarens kumulativa okända tid är {_number(energy['unknown']['observed_total_s'], 1)} s.",
        "",
        "| Kvart | Status | Mål Wh | Uppmätt Wh | Fel Wh | Okänd tid s (est.; intervall) | Par W medel | Par W peak* | Sent W sekvens; sample-medel/räckvidd | Limiter VP1 / VP2 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for quarter in energy["quarters"]:
        unknown = quarter["unknown_s"]
        pair = quarter["pair_power"] or {}
        sent = quarter["sent_commands"]
        limiter = quarter["limiter"]
        limiter_text = (
            " / ".join(
                f"{limiter[str(sid)]['saturation_observations']} av {limiter[str(sid)]['observations']}"
                for sid in (1, 2)
            )
            if limiter
            else "—"
        )
        if sent and sent["observations"]:
            sent_sequence = "→".join(str(value) for value in sent["sent_observed_sequence_w"])
            sent_range = (
                f"{sent_sequence}; {_number(sent['sent_sample_mean_w'])} / "
                f"{_number(sent['sent_min_w'])}–{_number(sent['sent_max_w'])}"
            )
        else:
            sent_range = "—"
        unknown_text = (
            f"{_number(unknown['estimate_s'], 1)}; "
            f"{_number(unknown['lower_bound_s'], 1)}–{_number(unknown['upper_bound_s'], 1)}"
        )
        lines.append(
            f"| {quarter['quarter']} | {quarter['state']} | {_number(quarter['target_wh'])} | "
            f"{_number(quarter['measured_wh'])} | {_number(quarter['error_wh'])} | {unknown_text} | "
            f"{_number(pair.get('time_weighted_mean_w'))} | {_number(pair.get('sampled_peak_w'))} | "
            f"{sent_range} | {limiter_text} |"
        )
    lines.extend(
        [
            "",
            "Limiterkolumnen visar observationer med fas `LIMITED` och orsak 4/15 per observation med aktiv EFFECT-kontroll (state 4). Par-effekten är tidsvägd endast över stödda färska intervall.",
            "",
            "| Pump | Aktivt medel W | Peak W* | Sista 5 min medel ± σ W (stöd/300 s) | Trend W/min | Brantaste upp / ned W/min | Stabil hold MAE ± fel-σ W (n; mål W) |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for sid in (1, 2):
        device = result["devices"][str(sid)]
        power, last, ramp, stable = (
            device["power"],
            device["last_5_minutes"],
            device["ramp"],
            device["stable_hold"],
        )
        stable_targets = ",".join(str(value) for value in stable["targets_w"]) or "—"
        lines.append(
            f"| VP{sid} | {_number(power['time_weighted_mean_w'])} | {_number(power['sampled_peak_w'])} | "
            f"{_number(last['time_weighted_mean_w'])} ± {_number(last['time_weighted_stddev_w'])} "
            f"({_number(last['supported_s'], 1)}/300) | "
            f"{_number(last['observed_linear_trend_w_per_min'])} | "
            f"{_number(ramp['steepest_observed_rise_w_per_min'])} / {_number(ramp['steepest_observed_fall_w_per_min'])} | "
            f"{_number(stable['mean_absolute_error_w'])} ± {_number(stable['error_stddev_w'])} "
            f"({stable['observations']}; {stable_targets}) |"
        )
    restoration = result["restoration"]
    device_restore = (
        "verifierad" if restoration["verified"] is True else
        "inte verifierad" if restoration["verified"] is False else
        "väntar"
    )
    cleanup = restoration["script_stopped_and_disabled_verified"]
    cleanup_text = "verifierat" if cleanup is True else "fel observerat" if cleanup is False else "ej verifierat"
    lines.extend(
        [
            "",
            f"Enhetsåterställning: **{device_restore}**; Script 7 stopp/inaktiverad: **{cleanup_text}**. "
            "Enhetskontrollen kräver idle control, rensad snapshot/lease och samma power, mode, DHW och boost som före provet. Flow jämförs endast diagnostiskt eftersom kurvläge kan ändra målet naturligt.",
            "",
            "* Peak är högsta samplade kortmedel, inte ett momentant maximum. Rampvärdena är beskrivande lutningar hos överlappande kortmedel och inte en kalibrerad fysisk slew-gräns.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path, help="evidence directory or its events.jsonl")
    parser.add_argument("--output", type=Path, help="write JSON analysis here")
    parser.add_argument("--markdown", type=Path, help="write a concise Markdown report here")
    parser.add_argument("--max-gap", type=float, default=60.0)
    arguments = parser.parse_args()
    if arguments.max_gap <= 0:
        parser.error("--max-gap must be positive")
    result = analyze(arguments.evidence, arguments.max_gap)
    rendered = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output:
        arguments.output.write_text(rendered)
    if arguments.markdown:
        arguments.markdown.write_text(render_markdown(result))
    if not arguments.output and not arguments.markdown:
        print(rendered, end="")


if __name__ == "__main__":
    main()
