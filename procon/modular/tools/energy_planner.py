#!/usr/bin/env python3
"""Pure reference math for the P0080 four-quarter energy planner.

This module performs no I/O and sends no device commands. Power feedback books
energy; response forecasts and allocation never alter the delivered counter.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable, Optional, Sequence


@dataclass(frozen=True)
class PowerPoint:
    time_s: float
    power_w: float


@dataclass(frozen=True)
class EnergyIntegral:
    wh: float
    covered_s: float
    unknown_s: float


def integrate_power(
    points: Iterable[PowerPoint], *, max_gap_s: float = 60.0
) -> EnergyIntegral:
    """Integrate fresh adjacent samples and report uncovered elapsed time."""
    ordered = sorted(points, key=lambda point: point.time_s)
    if len(ordered) < 2:
        return EnergyIntegral(0.0, 0.0, 0.0)
    wh = covered = unknown = 0.0
    previous = ordered[0]
    for current in ordered[1:]:
        dt = current.time_s - previous.time_s
        if dt <= 0:
            previous = current
            continue
        if dt < max_gap_s:
            wh += (previous.power_w + current.power_w) * 0.5 * dt / 3600.0
            covered += dt
        else:
            unknown += dt
        previous = current
    return EnergyIntegral(wh, covered, unknown)


def required_average_w(
    target_wh: float, delivered_wh: float, seconds_remaining: float
) -> float:
    """Average physical power needed for the remainder of a quarter."""
    if seconds_remaining <= 0:
        return 0.0
    return max(0.0, (target_wh - delivered_wh) * 3600.0 / seconds_remaining)


@dataclass(frozen=True)
class DeviceEnvelope:
    minimum_continuous_w: int = 3000
    maximum_feasible_w: int = 9000
    available: bool = True
    running: bool = False
    thermal_margin_cC: int = 500


@dataclass(frozen=True)
class ResponseLimits:
    startup_delay_s: float = 300.0
    ramp_up_w_per_s: float = 4000.0 / 300.0
    ramp_down_w_per_s: float = 2000.0 / 300.0


@dataclass(frozen=True)
class ResponseState:
    power_w: float = 0.0
    enabled: bool = False
    startup_remaining_s: float = 0.0


def project_toward(
    state: ResponseState,
    requested_w: float,
    seconds: float,
    limits: ResponseLimits = ResponseLimits(),
) -> ResponseState:
    """Project one device through startup and bounded physical ramps.

    This predicts feasible response; callers still book energy from measured
    power samples. A transition all the way to zero creates a new startup delay.
    """
    if seconds < 0 or requested_w < 0:
        raise ValueError("time and requested power must be nonnegative")
    if seconds == 0:
        return state
    power = max(0.0, state.power_w)
    enabled = state.enabled
    remaining = max(0.0, state.startup_remaining_s)
    if requested_w == 0:
        power = max(0.0, power - limits.ramp_down_w_per_s * seconds)
        if power == 0:
            enabled = False
            remaining = 0.0
        return ResponseState(power, enabled, remaining)
    if not enabled:
        enabled = True
        remaining = limits.startup_delay_s
    active_seconds = seconds
    if remaining:
        consumed = min(remaining, active_seconds)
        remaining -= consumed
        active_seconds -= consumed
    if active_seconds and remaining == 0:
        if requested_w >= power:
            power = min(requested_w, power + limits.ramp_up_w_per_s * active_seconds)
        else:
            power = max(requested_w, power - limits.ramp_down_w_per_s * active_seconds)
    return ResponseState(power, enabled, remaining)


@dataclass(frozen=True)
class Allocation:
    target_w: tuple[int, int]
    duty_fraction: float
    feasible_pair_w: int
    requested_pair_w: int
    shortfall_w: int
    lead: int


def _actions(device: DeviceEnvelope, step_w: int) -> Sequence[int]:
    if not device.available or device.maximum_feasible_w < device.minimum_continuous_w:
        return (0,)
    values = list(range(device.minimum_continuous_w, device.maximum_feasible_w + 1, step_w))
    if values[-1] != device.maximum_feasible_w:
        values.append(device.maximum_feasible_w)
    return (0, *values)


def allocate_pair(
    requested_pair_w: float,
    devices: Sequence[DeviceEnvelope],
    *,
    lead: int = 0,
    step_w: int = 500,
) -> Allocation:
    """Choose a stable split; return duty cycling below one-device minimum.

    The allocation is deliberately static. A later MPC layer decides when a
    duty interval is feasible after accounting for restart delay and lookahead.
    """
    if len(devices) != 2:
        raise ValueError("exactly two devices are required")
    if lead not in (0, 1) or step_w <= 0:
        raise ValueError("invalid allocator configuration")
    requested = max(0, int(round(requested_pair_w)))
    usable = [d for d in devices if d.available and d.maximum_feasible_w >= d.minimum_continuous_w]
    if not usable or requested == 0:
        return Allocation((0, 0), 0.0, 0, requested, requested, lead)

    floor = min(d.minimum_continuous_w for d in usable)
    if requested < floor:
        chosen = lead if devices[lead].available else 1 - lead
        target = [0, 0]
        target[chosen] = devices[chosen].minimum_continuous_w
        return Allocation(
            tuple(target), requested / target[chosen], target[chosen], requested, 0, chosen
        )

    choices = [_actions(device, step_w) for device in devices]
    best: Optional[tuple[tuple[int, ...], tuple[int, int]]] = None
    for first, second in product(*choices):
        total = first + second
        error = abs(total - requested)
        running_count = int(first > 0) + int(second > 0)
        starts = int(first > 0 and not devices[0].running) + int(second > 0 and not devices[1].running)
        # Exact energy capacity dominates. Split when both devices can remain at
        # or above their continuous floors; otherwise keep one stable device.
        split_possible = len(usable) == 2 and requested >= sum(
            d.minimum_continuous_w for d in usable
        )
        topology = abs(first - second) if split_possible else running_count * step_w
        lead_penalty = 0 if (first, second)[lead] > 0 else 1
        thermal_penalty = (
            (10000 - devices[0].thermal_margin_cC) * int(first > 0)
            + (10000 - devices[1].thermal_margin_cC) * int(second > 0)
        )
        score = (error, topology, starts, lead_penalty, thermal_penalty)
        if best is None or score < best[0]:
            best = (score, (first, second))
    assert best is not None
    targets = best[1]
    feasible = sum(targets)
    return Allocation(
        targets,
        1.0,
        feasible,
        requested,
        max(0, requested - feasible),
        lead,
    )


def quarter_allocation(
    target_wh: float,
    delivered_wh: float,
    seconds_remaining: float,
    devices: Sequence[DeviceEnvelope],
    *,
    lead: int = 0,
) -> Allocation:
    return allocate_pair(
        required_average_w(target_wh, delivered_wh, seconds_remaining),
        devices,
        lead=lead,
    )


@dataclass(frozen=True)
class PairModel:
    """Small model fitted to the 2026-10-14 pair-energy field run."""

    response_fraction: float = 0.15
    rise_w_per_s: float = 30.0
    fall_w_per_s: float = 3.0
    step_s: int = 30
    startup_delay_s: int = 330


@dataclass(frozen=True)
class MpcDecision:
    command_w: int
    energy_score_wh: float
    command_movement_kw: float


@dataclass(frozen=True)
class RemainingEnergyDecision:
    """One constant-time receding-deadline decision.

    ``required_w`` is the physical pair power needed after the response-lag
    window. ``wanted_w`` is the reachable physical request after blending the
    current and next accounting deadlines. ``command_w`` is the EFFECT target
    after response-gain compensation and command slew limits.
    """

    command_w: int
    required_w: float
    wanted_w: float
    reachable_w: float
    projected_shortfall_w: float
    forecast_error_wh: float


@dataclass(frozen=True)
class CommittedProjection:
    """Energy which may safely be credited during the response window."""

    wh: float
    end_power_w: float


@dataclass(frozen=True)
class RetargetDecision:
    """Result of applying the actuator dwell and collapse-recovery guard."""

    command_w: int
    changed: bool
    collapse_recovery: bool


def round_step_half_up(value: float, step: int) -> int:
    """Match Shelly's positive-value ``floor((x + step/2) / step)``."""
    if value < 0 or step <= 0:
        raise ValueError("value must be nonnegative and step positive")
    return int((value + step / 2.0) // step) * step


def _cumulative_target(targets: Sequence[int], quarter: int) -> float:
    return float(sum(targets[: min(quarter + 1, len(targets))]))


def conservative_committed_projection(
    *,
    power_w: float,
    command_w: float,
    seconds: float,
    thermal_limited: bool = False,
    command_changing: bool = True,
) -> CommittedProjection:
    """Project already committed energy without crediting a stale high output.

    While a command is changing, output above its raw request is not assumed
    to survive the response window. During active thermal limiting
    even a higher command cannot guarantee retained output. Stable, unlimited
    measured output is credited unchanged, so model error cannot create a
    permanent upward bias.
    """
    if seconds < 0:
        raise ValueError("time must be nonnegative")
    power = max(0.0, power_w)
    command = max(0.0, command_w)
    # The lag is the settling window: credit a straight-line path to no more
    # than the lower commanded response. A thermally limited device has no
    # guaranteed retained output, so its conservative end is zero.
    if thermal_limited:
        end_power = 0.0
    elif command_changing:
        end_power = min(power, command)
    else:
        end_power = power
    return CommittedProjection(
        (power + end_power) * 0.5 * seconds / 3600.0,
        end_power,
    )


def apply_retarget_dwell(
    *,
    current_command_w: int,
    planned_command_w: int,
    power_w: float,
    previous_power_w: Optional[float],
    seconds_since_previous_power: float,
    seconds_since_retarget: float,
    limited_down: bool = False,
    seconds_since_recovery: float = 120.0,
    ramp_down_w_per_s: float = 1250.0 / 300.0,
    dwell_s: float = 120.0,
    collapse_margin_w: float = 1500.0,
    command_margin_w: float = 500.0,
    recovery_step_w: int = 1000,
) -> RetargetDecision:
    """Apply normal dwell, with one bounded response to an output collapse.

    The bypass requires all of: a requested increase, output below the current
    command, and a fall larger than the ordinary down-ramp plus a 1.5 kW
    margin.  A separate dwell between bypasses prevents 30-second chasing.
    """
    values = (
        seconds_since_previous_power,
        seconds_since_retarget,
        seconds_since_recovery,
        ramp_down_w_per_s,
        dwell_s,
        collapse_margin_w,
        command_margin_w,
        recovery_step_w,
    )
    if any(value < 0 for value in values):
        raise ValueError("timing, margins, rates and steps must be nonnegative")
    if planned_command_w == current_command_w:
        return RetargetDecision(current_command_w, False, False)
    if limited_down or seconds_since_retarget >= dwell_s:
        return RetargetDecision(planned_command_w, True, False)

    collapse = False
    if previous_power_w is not None and planned_command_w > current_command_w:
        ordinary_fall = ramp_down_w_per_s * min(
            seconds_since_previous_power, 300.0
        )
        collapse = (
            power_w + command_margin_w < current_command_w
            and previous_power_w - power_w > ordinary_fall + collapse_margin_w
            and seconds_since_recovery >= dwell_s
        )
    if collapse:
        command = min(planned_command_w, current_command_w + recovery_step_w)
        return RetargetDecision(command, command != current_command_w, True)
    return RetargetDecision(current_command_w, False, False)


def remaining_energy_command(
    *,
    elapsed_s: int,
    delivered_wh: float,
    power_w: float,
    current_command_w: int,
    quarter_targets_wh: Sequence[int],
    response_gain: float = 1.0,
    reachable_w: float = 24000.0,
    floor_w: int = 6000,
    ceiling_w: int = 24000,
    response_lag_s: int = 300,
    ramp_up_w_per_s: float = 2000.0 / 300.0,
    ramp_down_w_per_s: float = 1250.0 / 300.0,
    command_up_step_w: int = 2000,
    command_down_step_w: int = 1000,
    command_step_w: int = 500,
    thermal_limited: bool = False,
    command_changing: bool = True,
) -> RemainingEnergyDecision:
    """Return the array-free Shelly v2 energy decision.

    The response lag credits a conservative projection from measured power
    toward a lower command, or downward while thermally limited. The remaining
    energy is converted to physical average power at both the current and next
    quarter boundary. A late, physically unreachable current deadline is not
    chased: doing so only moves its response into the following quarter. The
    next boundary then becomes the recovery target.

    This is deliberately closed form. It has no candidate loop or retained
    trajectory and maps directly to the constrained Shelly JavaScript runtime.
    """
    if not quarter_targets_wh:
        raise ValueError("at least one quarter target is required")
    if response_gain <= 0 or command_step_w <= 0:
        raise ValueError("response gain and command step must be positive")
    qcount = len(quarter_targets_wh)
    quarter = min(max(0, elapsed_s // 900), qcount - 1)
    into = max(0, elapsed_s - quarter * 900)
    remaining = max(1, 900 - into)
    power = max(0.0, power_w)

    lag = min(float(response_lag_s), float(remaining))
    committed = conservative_committed_projection(
        power_w=power,
        command_w=current_command_w,
        seconds=lag,
        thermal_limited=thermal_limited,
        command_changing=command_changing,
    )
    committed_wh = committed.wh
    active_after_lag = max(0.0, remaining - lag)
    required = (
        _cumulative_target(quarter_targets_wh, quarter)
        - delivered_wh
        - committed_wh
    ) * 3600.0 / max(30.0, active_after_lag)

    if quarter + 1 < qcount:
        next_horizon = remaining + 900.0
        next_required = (
            _cumulative_target(quarter_targets_wh, quarter + 1)
            - delivered_wh
            - committed_wh
        ) * 3600.0 / max(30.0, next_horizon - lag)
    else:
        next_required = required

    # The next deadline gradually receives more weight in the last two lag
    # windows. This prepositions a steep next quarter without a boundary step.
    preparation = max(
        0.0,
        min(1.0, (into - (900.0 - 2.0 * response_lag_s)) / (2.0 * response_lag_s)),
    )
    next_weight = 1.0 + 3.0 * preparation

    response_start = committed.end_power_w
    deadline_maximum_end = min(
        reachable_w, response_start + ramp_up_w_per_s * active_after_lag
    )
    deadline_minimum_end = max(
        min(float(floor_w), response_start),
        response_start - ramp_down_w_per_s * active_after_lag,
    )
    maximum_average = (response_start + deadline_maximum_end) * 0.5
    minimum_average = (response_start + deadline_minimum_end) * 0.5
    if required > maximum_average or required < minimum_average:
        # The current boundary is no longer reachable. Continue best effort
        # against the next boundary instead of storing up a delayed overshoot.
        wanted = next_required
    else:
        wanted = (required + next_weight * next_required) / (1.0 + next_weight)
    reachable = max(float(floor_w), min(float(ceiling_w), reachable_w))
    wanted = max(float(floor_w), min(reachable, wanted))
    raw_command = wanted / response_gain
    raw_command = max(
        current_command_w - command_down_step_w,
        min(current_command_w + command_up_step_w, raw_command),
    )
    command = round_step_half_up(raw_command, command_step_w)
    command = max(floor_w, min(ceiling_w, command))
    forecast_end = max(
        deadline_minimum_end, min(deadline_maximum_end, wanted)
    )
    forecast_average = (response_start + forecast_end) * 0.5
    forecast_error = (
        delivered_wh
        + committed_wh
        + forecast_average * active_after_lag / 3600.0
        - _cumulative_target(quarter_targets_wh, quarter)
    )
    return RemainingEnergyDecision(
        command,
        required,
        wanted,
        reachable,
        max(0.0, required - maximum_average),
        forecast_error,
    )


def project_pair_step(
    power_w: float,
    command_w: float,
    startup_remaining_s: float,
    model: PairModel = PairModel(),
) -> tuple[float, float]:
    """Project one pair step through startup and asymmetric response."""
    if startup_remaining_s > 0:
        return 0.0, max(0.0, startup_remaining_s - model.step_s)
    delta = model.response_fraction * (command_w - power_w)
    delta = min(model.rise_w_per_s * model.step_s, delta)
    delta = max(-model.fall_w_per_s * model.step_s, delta)
    return max(0.0, power_w + delta), 0.0


def scalar_mpc_command(
    *,
    elapsed_s: int,
    delivered_wh: float,
    power_w: float,
    current_command_w: int,
    startup_remaining_s: float,
    quarter_targets_wh: Sequence[int],
    floor_w: int = 6000,
    ceiling_w: int = 24000,
    candidate_step_w: int = 500,
    candidate_commands: Optional[Sequence[int]] = None,
    model: PairModel = PairModel(),
) -> MpcDecision:
    """Select one scalar command using a current-plus-three-quarter horizon.

    A candidate is retained for five simulated minutes. Later simulated actions
    follow cumulative energy debt. This makes dead time and slow braking visible
    to the current decision without storing a trajectory on Shelly.
    """
    if not quarter_targets_wh or candidate_step_w <= 0:
        raise ValueError("targets and a positive candidate step are required")
    qcount = len(quarter_targets_wh)

    def cumulative_target(q: int) -> float:
        return float(sum(quarter_targets_wh[: min(q + 1, qcount)]))

    best: Optional[MpcDecision] = None
    horizon_end = min(qcount * 900, elapsed_s + 4 * 900)
    candidates = candidate_commands or range(floor_w, ceiling_w + 1, candidate_step_w)
    for candidate in candidates:
        candidate = max(
            floor_w,
            min(ceiling_w, int(round(candidate / candidate_step_w)) * candidate_step_w),
        )
        simulated_t = elapsed_s
        simulated_wh = delivered_wh
        simulated_power = power_w
        simulated_startup = startup_remaining_s
        simulated_command = candidate
        previous_command = current_command_w
        movement = abs(simulated_command - previous_command) / 1000.0
        energy_score = 0.0
        previous_q = elapsed_s // 900
        while simulated_t < horizon_end:
            new_power, simulated_startup = project_pair_step(
                simulated_power, simulated_command, simulated_startup, model
            )
            simulated_wh += (
                simulated_power + new_power
            ) * 0.5 * model.step_s / 3600.0
            simulated_power = new_power
            simulated_t += model.step_s
            q = simulated_t // 900
            if q > previous_q:
                target = sum(quarter_targets_wh[: min(q, qcount)])
                boundary_error = abs(simulated_wh - target)
                energy_score += boundary_error
                if q >= qcount:
                    energy_score += 4.0 * boundary_error
                previous_q = q
            if simulated_t < elapsed_s + 300:
                next_command = candidate
            else:
                active_q = min(simulated_t // 900, qcount - 1)
                into = simulated_t - active_q * 900
                remaining = max(model.step_s, 900 - into)
                needed = (
                    cumulative_target(active_q) - simulated_wh
                ) * 3600.0 / remaining
                next_command = int(round(needed / candidate_step_w)) * candidate_step_w
                next_command = max(floor_w, min(ceiling_w, next_command))
            movement += abs(next_command - simulated_command) / 1000.0
            simulated_command = next_command
        decision = MpcDecision(candidate, energy_score, movement)
        if best is None or (
            decision.energy_score_wh,
            decision.command_movement_kw,
            abs(decision.command_w - current_command_w),
            decision.command_w,
        ) < (
            best.energy_score_wh,
            best.command_movement_kw,
            abs(best.command_w - current_command_w),
            best.command_w,
        ):
            best = decision
    assert best is not None
    return best


def bounded_mpc_command(**kwargs) -> MpcDecision:
    """Shelly-equivalent local up/down search with a four-quarter score."""
    current = kwargs["current_command_w"]
    return scalar_mpc_command(
        **kwargs,
        candidate_commands=(current - 1500, current + 1500),
    )
