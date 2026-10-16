#!/usr/bin/env python3
"""Extract controller-identification facts from a Shelly pair-energy trial.

The program is deliberately read-only.  It separates the nominal pair command
published by the energy script from the two EFFECT targets that were actually
accepted by the Procon devices.  Counterfactual model fits are labelled as
such; measured energy and restoration are never inferred from those fits.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean, median
from typing import Iterable, Sequence


TARGETS_WH = (1500, 2000, 2500, 4000, 2500, 2000, 1500)
INVALID_S32 = -(1 << 31)


def signed32(high: int, low: int) -> int:
    value = high * 65536 + low
    return value - (1 << 32) if value >= (1 << 31) else value


def parse_kvs(text: str | None) -> dict[str, str]:
    fields: dict[str, str] = {}
    for item in (text or "").split("|"):
        if "=" in item:
            key, value = item.split("=", 1)
            fields[key] = value
    return fields


def rounded_device_target(pair_w: int) -> int:
    """Match Shelly v1.3.1 round500(pair/2), including its upward tie."""
    return ((pair_w // 2 + 250) // 500) * 500


@dataclass(frozen=True)
class DeviceSample:
    target_w: int
    short_w: int
    hz: int
    phase: int
    reason: int


@dataclass(frozen=True)
class Sample:
    timestamp: float
    elapsed_s: float
    quarter: int
    nominal_pair_w: int
    status_phase: str
    devices: dict[int, DeviceSample]

    @property
    def sent_pair_w(self) -> int:
        return sum(device.target_w for device in self.devices.values())

    @property
    def pair_power_w(self) -> int | None:
        if len(self.devices) != 2 or any(
            device.short_w == INVALID_S32 for device in self.devices.values()
        ):
            return None
        return sum(device.short_w for device in self.devices.values())


def _time(value: str) -> float:
    return datetime.fromisoformat(value).timestamp()


def load_trial(path: Path) -> tuple[list[Sample], list[int], float]:
    events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    started = next(_time(event["time"]) for event in events if event.get("kind") == "started")
    samples: list[Sample] = []
    final_results: list[int] = []
    for event in events:
        if event.get("kind") != "sample":
            continue
        data = event["data"]
        kvs = parse_kvs(data.get("kvs"))
        if "q" not in kvs or "cmd" not in kvs:
            continue
        devices: dict[int, DeviceSample] = {}
        for sid_text, raw in data.get("devices", {}).items():
            words = raw.get("feedback")
            if not words or len(words) < 22:
                continue
            devices[int(sid_text)] = DeviceSample(
                target_w=words[3],
                short_w=signed32(words[7], words[8]),
                hz=words[21],
                phase=words[1],
                reason=words[2],
            )
        samples.append(
            Sample(
                timestamp=_time(event["time"]),
                elapsed_s=_time(event["time"]) - started,
                quarter=int(kvs["q"]),
                nominal_pair_w=int(kvs["cmd"]),
                status_phase=kvs.get("phase", ""),
                devices=devices,
            )
        )
        if kvs.get("phase") == "complete":
            final_results = [int(value) for value in kvs.get("results", "").split(",")]
    if not samples or len(final_results) != len(TARGETS_WH):
        raise ValueError("trial lacks samples or a complete seven-quarter result")
    return samples, final_results, started


def _percentile(values: Sequence[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[int((len(ordered) - 1) * fraction)]


def _linear_fit(xs: Sequence[float], ys: Sequence[float]) -> dict[str, float]:
    xbar, ybar = mean(xs), mean(ys)
    denominator = sum((value - xbar) ** 2 for value in xs)
    if not denominator:
        raise ValueError("singular linear fit")
    gain = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / denominator
    bias = ybar - gain * xbar
    predicted = [gain * value + bias for value in xs]
    residual = sum((actual - ybar) ** 2 for actual in ys)
    squared_error = sum((actual - estimate) ** 2 for actual, estimate in zip(ys, predicted))
    return {
        "gain_w_per_hz": gain,
        "bias_w": bias,
        "mae_w": mean(abs(actual - estimate) for actual, estimate in zip(ys, predicted)),
        "rmse_w": math.sqrt(squared_error / len(ys)),
        "r_squared": 1.0 - squared_error / residual,
        "samples": len(xs),
    }


def fit_hz_to_power(samples: Sequence[Sample], sid: int) -> dict[str, float | int | str]:
    """Fit power to earlier reported Hz at a discrete host-sample lag.

    The fit identifies a useful predictor, not an intervention on native Hz.
    Phase 3 (ordinary hold) and phase 4/reason 4 (temperature limited) are both
    retained because the Hz-to-water-power relationship remains physical.
    """
    interval = median(
        later.timestamp - earlier.timestamp for earlier, later in zip(samples, samples[1:])
    )
    candidates: list[dict[str, float | int]] = []
    for lag in range(5):
        xs: list[float] = []
        ys: list[float] = []
        for index in range(lag, len(samples)):
            current = samples[index].devices.get(sid)
            source = samples[index - lag].devices.get(sid)
            if not current or not source:
                continue
            if current.short_w == INVALID_S32 or source.hz < 20 or source.hz > 120:
                continue
            if current.phase not in (3, 4) or source.phase not in (3, 4):
                continue
            elapsed = samples[index].timestamp - samples[index - lag].timestamp
            if lag and elapsed > interval * (lag + 0.55):
                continue
            xs.append(source.hz)
            ys.append(current.short_w)
        fit = _linear_fit(xs, ys)
        fit["lag_samples"] = lag
        fit["lag_s"] = lag * interval
        candidates.append(fit)
    best = min(candidates, key=lambda result: float(result["mae_w"]))
    return {
        **best,
        "classification": "descriptive predictor; not a causal counterfactual",
    }


def _solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [matrix[row][:] + [vector[row]] for row in range(size)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        if abs(scale) < 1e-12:
            raise ValueError("singular normal equations")
        for index in range(column, size + 1):
            augmented[column][index] /= scale
        for row in range(size):
            if row == column:
                continue
            scale = augmented[row][column]
            for index in range(column, size + 1):
                augmented[row][index] -= scale * augmented[column][index]
    return [augmented[row][size] for row in range(size)]


def _ols(rows: Sequence[Sequence[float]], values: Sequence[float]) -> tuple[list[float], float]:
    size = len(rows[0])
    matrix = [
        [sum(row[left] * row[right] for row in rows) for right in range(size)]
        for left in range(size)
    ]
    vector = [sum(row[index] * value for row, value in zip(rows, values)) for index in range(size)]
    coefficients = _solve(matrix, vector)
    mae = mean(
        abs(value - sum(coefficient * item for coefficient, item in zip(coefficients, row)))
        for row, value in zip(rows, values)
    )
    return coefficients, mae


def fit_request_response(
    samples: Sequence[Sample], sid: int, phase: int
) -> dict[str, float | int | str]:
    """Fit P[k]=c+a*P[k-1]+b*request[k-delay] for one regime."""
    interval = median(
        later.timestamp - earlier.timestamp for earlier, later in zip(samples, samples[1:])
    )
    candidates: list[dict[str, float | int]] = []
    for lag in range(8):
        rows: list[list[float]] = []
        values: list[float] = []
        for index in range(max(1, lag), len(samples)):
            current = samples[index].devices.get(sid)
            previous = samples[index - 1].devices.get(sid)
            request = samples[index - lag].devices.get(sid)
            if not current or not previous or not request:
                continue
            if current.short_w == INVALID_S32 or previous.short_w == INVALID_S32:
                continue
            if current.phase != phase or previous.phase != phase:
                continue
            if samples[index].timestamp - samples[index - 1].timestamp > 45:
                continue
            rows.append([1.0, previous.short_w, request.target_w])
            values.append(current.short_w)
        coefficients, mae = _ols(rows, values)
        intercept, memory, request_coefficient = coefficients
        if 0 < memory < 1:
            tau_s = -interval / math.log(memory)
            steady_gain = request_coefficient / (1 - memory)
            steady_bias = intercept / (1 - memory)
        else:
            tau_s = steady_gain = steady_bias = float("nan")
        candidates.append(
            {
                "lag_samples": lag,
                "lag_s": lag * interval,
                "memory": memory,
                "request_coefficient": request_coefficient,
                "intercept_w": intercept,
                "steady_gain": steady_gain,
                "steady_bias_w": steady_bias,
                "time_constant_s": tau_s,
                "mae_w": mae,
                "samples": len(values),
            }
        )
    best = min(candidates, key=lambda result: float(result["mae_w"]))
    return {
        **best,
        "classification": "regime-conditioned ARX description; counterfactual use is unvalidated",
    }


def _active(samples: Iterable[Sample]) -> list[Sample]:
    return [
        sample
        for sample in samples
        if len(sample.devices) == 2 and sample.status_phase != "complete"
    ]


def _command_split(samples: Sequence[Sample]) -> dict[str, object]:
    active = _active(samples)
    duration = extra_wh = odd_duration = 0.0
    transition_samples = 0
    exact_samples = 0
    for current, later in zip(active, active[1:]):
        dt = min(60.0, later.timestamp - current.timestamp)
        expected = 2 * rounded_device_target(current.nominal_pair_w)
        duration += dt
        if expected != current.nominal_pair_w:
            odd_duration += dt
            extra_wh += (expected - current.nominal_pair_w) * dt / 3600
        if current.sent_pair_w == expected:
            exact_samples += 1
        else:
            transition_samples += 1
    return {
        "rule": "sent_each=round500(nominal_pair/2)",
        "examples": {"6500": [3500, 3500], "13500": [7000, 7000]},
        "duration_s": duration,
        "up_rounded_duration_s": odd_duration,
        "up_rounded_fraction": odd_duration / duration,
        "extra_requested_command_area_wh": extra_wh,
        "stable_rule_samples": exact_samples,
        "sequential_transition_samples": transition_samples,
        "classification": "command-area difference; not measured extra heat",
    }


def _quarter_metrics(samples: Sequence[Sample], measured: Sequence[int]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    cumulative_error = 0
    for quarter, (target, actual) in enumerate(zip(TARGETS_WH, measured)):
        selected = [
            sample
            for sample in samples
            if sample.quarter == quarter and len(sample.devices) == 2 and sample.status_phase != "complete"
        ]
        valid = [sample for sample in selected if sample.pair_power_w is not None]
        pair_power = [sample.pair_power_w for sample in valid]
        nominal = [sample.nominal_pair_w for sample in selected]
        sent = [sample.sent_pair_w for sample in selected]
        cumulative_error += actual - target
        limited_fraction = {
            str(sid): sum(
                sample.devices[sid].phase == 4 and sample.devices[sid].reason == 4
                for sample in selected
            )
            / len(selected)
            for sid in (1, 2)
        }
        both_limited = [
            sample.pair_power_w
            for sample in valid
            if all(
                sample.devices[sid].phase == 4 and sample.devices[sid].reason == 4
                for sid in (1, 2)
            )
        ]
        output.append(
            {
                "quarter": quarter + 1,
                "target_wh": target,
                "measured_wh": actual,
                "error_wh": actual - target,
                "cumulative_error_wh": cumulative_error,
                "sample_count": len(selected),
                "valid_pair_samples": len(valid),
                "nominal_command_mean_w": mean(nominal),
                "sent_target_mean_w": mean(sent),
                "pair_power_mean_w": mean(pair_power),
                "tracking_to_sent_ratio": sum(pair_power) / sum(sample.sent_pair_w for sample in valid),
                "temperature_limited_fraction": limited_fraction,
                "both_limited_samples": len(both_limited),
                "both_limited_power_mean_w": mean(both_limited) if both_limited else None,
                "both_limited_power_min_w": min(both_limited) if both_limited else None,
                "both_limited_power_max_w": max(both_limited) if both_limited else None,
            }
        )
    return output


def _device_summary(samples: Sequence[Sample], sid: int) -> dict[str, object]:
    active = [
        sample
        for sample in samples
        if sid in sample.devices and sample.status_phase != "complete"
    ]
    valid = [sample for sample in active if sample.devices[sid].short_w != INVALID_S32]
    unconstrained = [sample.devices[sid] for sample in valid if sample.devices[sid].phase == 3]
    limited = [
        sample.devices[sid]
        for sample in valid
        if sample.devices[sid].phase == 4 and sample.devices[sid].reason == 4
    ]

    first_valid = next(sample for sample in active if sample.devices[sid].short_w != INVALID_S32)
    first_2kw = next(sample for sample in active if sample.devices[sid].short_w >= 2000)

    # The clearest running upward excursion started when the requested target
    # first exceeded 5 kW after quarter one.  Report the best power reached in
    # the following ten minutes without treating that maximum as a guarantee.
    up_start = next(
        sample
        for sample in valid
        if sample.elapsed_s > 900 and sample.devices[sid].target_w > 5000
    )
    up_window = [
        sample
        for sample in valid
        if up_start.timestamp <= sample.timestamp <= up_start.timestamp + 600
    ]
    up_end = max(up_window, key=lambda sample: sample.devices[sid].short_w)
    up_duration = up_end.timestamp - up_start.timestamp
    up_delta = up_end.devices[sid].short_w - up_start.devices[sid].short_w

    # The final constant-target segment is a measured down-ramp at the 3 kW
    # request floor.  It is not assumed to be a settled minimum.
    final_target = valid[-1].devices[sid].target_w
    segment: list[Sample] = []
    for sample in reversed(valid):
        if sample.devices[sid].target_w != final_target:
            break
        segment.append(sample)
    segment.reverse()
    start, end = segment[0], segment[-1]
    duration_s = end.timestamp - start.timestamp
    delta_w = end.devices[sid].short_w - start.devices[sid].short_w

    dwell: list[tuple[int, float]] = []
    dwell_start = active[0].timestamp
    dwell_value = active[0].devices[sid].target_w
    for sample in active[1:]:
        target = sample.devices[sid].target_w
        if target != dwell_value:
            dwell.append((dwell_value, sample.timestamp - dwell_start))
            dwell_start, dwell_value = sample.timestamp, target
    dwell.append((dwell_value, active[-1].timestamp - dwell_start))

    def regime(items: Sequence[DeviceSample]) -> dict[str, float | int]:
        ratios = [item.short_w / item.target_w for item in items]
        return {
            "samples": len(items),
            "mean_tracking_ratio": mean(ratios),
            "median_tracking_ratio": median(ratios),
            "mean_error_w": mean(item.short_w - item.target_w for item in items),
        }

    return {
        "first_valid_power_s": first_valid.elapsed_s,
        "first_2kw_s": first_2kw.elapsed_s,
        "unconstrained_tracking": regime(unconstrained),
        "temperature_limited_tracking": regime(limited),
        "temperature_limited_samples": len(limited),
        "hz_to_power": fit_hz_to_power(samples, sid),
        "request_response_unconstrained": fit_request_response(samples, sid, 3),
        "request_response_temperature_limited": fit_request_response(samples, sid, 4),
        "observed_running_up_segment": {
            "start_s": up_start.elapsed_s,
            "end_s": up_end.elapsed_s,
            "duration_s": up_duration,
            "start_request_w": up_start.devices[sid].target_w,
            "end_request_w": up_end.devices[sid].target_w,
            "start_power_w": up_start.devices[sid].short_w,
            "end_power_w": up_end.devices[sid].short_w,
            "change_w_per_min": up_delta * 60 / up_duration,
            "classification": "observed rising excursion; not a guaranteed slew rate",
        },
        "terminal_floor_segment": {
            "request_w": final_target,
            "start_s": start.elapsed_s,
            "end_s": end.elapsed_s,
            "duration_s": duration_s,
            "start_power_w": start.devices[sid].short_w,
            "end_power_w": end.devices[sid].short_w,
            "change_w_per_min": delta_w * 60 / duration_s,
            "classification": "observed transient; not a settled continuous minimum",
        },
        "target_dwell": {
            "segments": len(dwell),
            "changes": len(dwell) - 1,
            "median_s": median(duration for _, duration in dwell),
            "segments_below_120s": sum(duration < 120 for _, duration in dwell),
            "note": "each changed target resets EFFECT trim and breaks its active model window",
        },
    }


def analyze(events_path: Path, restoration_path: Path | None = None) -> dict[str, object]:
    samples, measured, started = load_trial(events_path)
    active = _active(samples)
    limited_pair = [
        sample.pair_power_w
        for sample in active
        if sample.pair_power_w is not None
        and all(
            sample.devices[sid].phase == 4 and sample.devices[sid].reason == 4
            for sid in (1, 2)
        )
    ]
    restoration: dict[str, object] | None = None
    if restoration_path and restoration_path.exists():
        raw = json.loads(restoration_path.read_text())
        restoration = {
            "verified": all(
                item.get("verified") is True
                and item.get("control", {}).get("state") == 0
                and item.get("control", {}).get("saved") == 0
                and item.get("control", {}).get("lease_s") == 0
                and item.get("native", {}).get("power") == 1
                and item.get("native", {}).get("mode") == 2
                and item.get("native", {}).get("boost") == 0
                for item in raw.values()
            ),
            "devices": raw,
        }
    return {
        "evidence": {
            "events": str(events_path),
            "sha256": hashlib.sha256(events_path.read_bytes()).hexdigest(),
            "started_unix_s": started,
            "samples": len(samples),
            "duration_s": samples[-1].timestamp - samples[0].timestamp,
        },
        "energy": {
            "target_wh": sum(TARGETS_WH),
            "measured_wh": sum(measured),
            "error_wh": sum(measured) - sum(TARGETS_WH),
            "quarters": _quarter_metrics(samples, measured),
        },
        "command_split": _command_split(samples),
        "devices": {str(sid): _device_summary(samples, sid) for sid in (1, 2)},
        "limited_pair_capacity_observation": {
            "samples": len(limited_pair),
            "mean_w": mean(limited_pair),
            "median_w": median(limited_pair),
            "p10_w": _percentile(limited_pair, 0.10),
            "p90_w": _percentile(limited_pair, 0.90),
            "minimum_w": min(limited_pair),
            "maximum_w": max(limited_pair),
            "classification": "time-varying observed envelope; not a fixed plant rating",
        },
        "restoration": restoration,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("events", type=Path)
    parser.add_argument("--restoration", type=Path)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = analyze(arguments.events, arguments.restoration)
    text = json.dumps(result, indent=2) + "\n"
    if arguments.output:
        arguments.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
