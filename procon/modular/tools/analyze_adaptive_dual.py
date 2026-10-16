"""Offline adaptive dual-trial analysis; never imports a live/device module.

Uses the adjacent analyze_source_trial.py only for offline mathematics/reporting.
Outputs adaptive-analysis.json, adaptive-observations.json and PNG/SVG figures.
Example: python analyze_adaptive_dual.py adaptive-dual-RUN_DIRECTORY
--self-test DIRECTORY writes clearly marked synthetic fixtures, not live results.
"""
import argparse
import copy
import hashlib
import json
import math
import statistics
from pathlib import Path

import analyze_source_trial as base
from matplotlib import pyplot as plt


def normalize(row, anchor):
    snap, feedback, native = row["snapshot"], row["feedback"], row["native"]
    sc, fc = row["snapshot_capture_interval"], row["feedback_capture_interval"]
    samples = snap["samples"]
    value = lambda name: samples[name]["value"] if base.valid(samples[name]) and not snap["link_lost"] else None
    hz, mode = value("compressor_Hz"), value("operating_mode_raw")
    if hz == 255:
        hz = None
    native_mode = native["operating_mode"]
    if mode in (1, 6) or native_mode in (1, 6):
        category = "dhw"
    elif mode in (0, 2, 7) and native_mode in (0, 2, 7) and hz == 0:
        category = "pause"
    elif mode in (2, 7) and native_mode in (2, 7) and hz is not None and hz > 0:
        category = "heating"
    else:
        category = "unknown_or_transition"
    available = (feedback.get("short_w") is not None and feedback.get("short_count", 0) > 0
                 and feedback.get("last_age_s") is not None and feedback["last_age_s"] < 60
                 and feedback["quality"] in (0, 1, 2, 9) and category == "heating")
    qualified = available and feedback["quality"] in (0, 2) and feedback["short_count"] >= 3 and feedback["short_span_s"] >= 20
    heat = value("heat_W")
    return {
        "sid": row["sid"], "t": sc["midpoint"] - anchor, "feedback_t": fc["midpoint"] - anchor,
        "native_t": row["t"] - anchor, "capture_end_t": row["capture_finished_monotonic"] - anchor,
        "snapshot_read_width_s": sc["end"] - sc["begin"], "feedback_read_width_s": fc["end"] - fc["begin"],
        "source_heat_t": sc["midpoint"] - anchor - samples["heat_W"]["age_ms"] / 1000 if heat is not None else None,
        "source_heat_key": tuple(samples[k]["generation"] for k in ("flow_cC", "return_cC", "flow_cL_min")),
        "category": category, "hz": hz, "mode": mode, "link_lost": snap["link_lost"],
        "native_operating_mode": native_mode, "raw_heat_W": heat,
        "space_hydraulic_W": heat if category in ("heating", "pause") else None,
        "compressor_gated_space_W": (0 if category == "pause" else heat) if category in ("heating", "pause") else None,
        "short_W": feedback["short_w"] if qualified else None,
        "partial_short_W": feedback["short_w"] if available and not qualified else None,
        "quality": feedback["quality"], "quality_name": feedback["quality_name"],
        "short_count": feedback["short_count"], "short_span_s": feedback["short_span_s"],
        "feedback_source_age_s": feedback["last_age_s"], "feedback_accepted_count": feedback["accepted_count"],
        "supply_C": value("flow_cC") / 100 if value("flow_cC") is not None else None,
        "return_C": value("return_cC") / 100 if value("return_cC") is not None else None,
        "flow_L_min": value("flow_cL_min") / 100 if value("flow_cL_min") is not None else None,
        "demand_C": native["flow"] / 100, "native_control_mode": native["mode"],
        "effect_phase": row["effect"]["phase"], "limit_reason": row["effect"]["limit_reason"],
        "control_state": row["control"]["state"], "control_error": row["control"]["error"],
        "lease_s": row["control"]["lease_s"], "sources": {name: samples[name] for name in base.SOURCES},
    }


def load(path):
    events, incomplete, digest = base.read_events(path)
    start = next((e for e in events if e["kind"] == "both_active"), None)
    if not start:
        raise ValueError("No confirmed both_active yet; no trial results generated")
    anchor = start["data"]["confirmed_monotonic"]
    targets = {int(sid): watts for sid, watts in start["data"]["targets_w"].items()}
    if set(targets) != {1, 2}:
        raise ValueError("Expected individual targets for devices1 and2")
    rows, seen, restoring, thermal = {sid: [] for sid in targets}, set(), set(), []
    for event in events:
        kind, payload = event["kind"], event["data"]
        if kind == "command_intent" and payload.get("packet", {}).get("words", [0, 0, 0])[2] == 1:
            restoring.add(payload["sid"])
        if kind == "thermal_envelope":
            thermal.append(payload)
        candidates = payload.get("rows", []) if kind == "dual_sample" else [payload] if kind == "capture" else []
        for row in candidates:
            sid = row.get("sid")
            if sid not in rows or sid in restoring or "snapshot" not in row:
                continue
            if "snapshot_capture_interval" not in row or "feedback_capture_interval" not in row:
                raise ValueError("Missing explicit per-device capture/feedback intervals")
            key = (sid, row["snapshot"]["sequence"], row["snapshot_capture_interval"]["midpoint"])
            if key not in seen:
                seen.add(key); rows[sid].append(normalize(row, anchor))
    for series in rows.values():
        series.sort(key=lambda row: row["t"])
    return {"rows": rows, "anchor": start, "duration_s": start["data"]["duration_s"], "targets_W": targets,
            "incomplete_final_line": incomplete, "events_sha256": digest, "thermal_observer_events": thermal,
            "fixture": bool(start["data"].get("synthetic_fixture")),
            "outcome": base.optional_json(path / "outcome.json"), "failure": base.optional_json(path / "failure.json"),
            "restoration": base.optional_json(path / "restoration.json")}


def thermal_exposure(points, start, end, threshold, max_gap):
    """Strictly above threshold, only along supported adjacent linear segments."""
    covered, above, degree_seconds, segments, hot = 0.0, 0.0, 0.0, [], []
    for low, high, va, vb in base.pieces(points, start, end, max_gap):
        covered += high - low
        segments.append((low, high))
        if va <= threshold and vb <= threshold:
            continue
        a, b = low, high
        if va <= threshold:
            a = low + (threshold - va) * (high - low) / (vb - va)
        if vb <= threshold:
            b = low + (threshold - va) * (high - low) / (vb - va)
        if b <= a:
            continue
        value = lambda at: va + (vb - va) * (at - low) / (high - low)
        left, right = max(0, value(a) - threshold), max(0, value(b) - threshold)
        above += b - a
        degree_seconds += (left + right) * (b - a) / 2
        hot.append((a, b, left, right))
    excursions = []
    for a, b, left, right in hot:
        if excursions and abs(a - excursions[-1]["end_s"]) < 1e-7 and left > 1e-7 and excursions[-1]["end_excess_C"] > 1e-7:
            excursions[-1]["end_s"] = b; excursions[-1]["end_excess_C"] = right
        else:
            excursions.append({"start_s": a, "end_s": b, "start_excess_C": left, "end_excess_C": right})
    for episode in excursions:
        episode.update(duration_s=episode["end_s"] - episode["start_s"],
                       start_crossing_unobserved=episode["start_excess_C"] > 1e-7,
                       end_crossing_unobserved=episode["end_excess_C"] > 1e-7)
    missing, cursor = [], start
    for a, b in segments:
        if a > cursor + 1e-7:
            missing.append([cursor, a])
        cursor = max(cursor, b)
    if cursor < end - 1e-7:
        missing.append([cursor, end])
    return {"threshold_C": threshold, "comparison": "strictly_greater", "interval_s": [start, end],
            "interpolated_seconds_above": above, "interpolated_seconds_at_or_below": max(0, covered - above),
            "known_coverage_s": covered, "unknown_s": max(0, end - start - covered), "missing_intervals_s": missing,
            "complete_coverage": end > start and abs(covered - (end - start)) < 1e-6,
            "degree_minutes_above": degree_seconds / 60, "excursions": excursions,
            "longest_supported_excursion_s": max((e["duration_s"] for e in excursions), default=0),
            "informational_episode_over180s": any(e["duration_s"] >= 180 for e in excursions),
            "temperature_or_duration_abort": False,
            "method": "Piecewise linear between adjacent valid observations; unknown intervals are never counted as hot or cool."}


def strict_goal_exposure(points, start, end, threshold, max_gap):
    """Account for equality separately without changing legacy >threshold fields.

    A line crossing the threshold at one instant adds no duration. A supported
    flat segment exactly at the threshold does: it fails the strict < goal.
    """
    strict = thermal_exposure(points, start, end, threshold, max_gap)
    equal = sum(b - a for a, b, va, vb in base.pieces(points, start, end, max_gap)
                if va == threshold and vb == threshold)
    greater = strict["interpolated_seconds_above"]
    at_or_above = greater + equal
    return {"threshold_C": threshold, "goal_comparison": "strictly_less",
            "exposure_comparison": "greater_or_equal", "interval_s": [start, end],
            "interpolated_seconds_at_or_above": at_or_above,
            "interpolated_seconds_above": greater,
            "interpolated_seconds_exactly_at_threshold": equal,
            "interpolated_seconds_strictly_below": max(0, strict["known_coverage_s"] - at_or_above),
            "known_coverage_s": strict["known_coverage_s"], "unknown_s": strict["unknown_s"],
            "missing_intervals_s": strict["missing_intervals_s"],
            "complete_coverage": strict["complete_coverage"],
            "temperature_or_duration_abort": False,
            "method": "Supported piecewise-linear observations only. Exactly at the threshold does not meet the strict goal. No inference is made inside unknown intervals."}


def source_temperature_points(rows):
    seen, points = set(), []
    for row in rows:
        sample = row["sources"]["flow_cC"]
        if row["supply_C"] is None:
            points.append((row["t"], None))
        elif sample["generation"] not in seen:
            seen.add(sample["generation"])
            points.append((row["t"] - sample["age_ms"] / 1000, row["supply_C"]))
    return sorted(points, key=lambda p: p[0])


def restoration_status(record):
    devices = record.get("devices", {}) if record else {}
    final = {str(sid): devices.get(str(sid), devices.get(sid)) for sid in (1, 2)}
    verified = bool(record) and all(isinstance(v, dict) and v.get("verified") is True and "error" not in v for v in final.values())
    incomplete = bool(record) and any(not isinstance(v, dict) or "error" in v for v in final.values())
    return {"both_verified": verified, "incomplete_or_failed": incomplete, "devices": final,
            "initial_auto_attempt_errors": record.get("initial_auto_attempt_errors", {}) if record else {}}


def supported_value(points, at, max_gap):
    """Interpolate adjacent valid points only; no endpoint/gap extrapolation."""
    for stamp, value in points:
        if abs(stamp - at) < 1e-8:
            return value
    for (a, va), (b, vb) in zip(points, points[1:]):
        if a < at < b:
            if va is None or vb is None or b - a > max_gap:
                return None
            return va + (vb - va) * (at - a) / (b - a)
    return None


def paired_points(left, right, start, end, max_gap):
    # Include every original timestamp (also invalid ones), so a regular grid
    # cannot accidentally interpolate over an unsupported interval.
    stamps = sorted({start, end, *(t for t, _ in left + right if start <= t <= end)})
    return [(t, supported_value(left, t, max_gap), supported_value(right, t, max_gap)) for t in stamps]


def pair_correlation(left, right, start, end, max_gap, lag_s=0):
    # Regular sampling prevents dense/repeated bus reads from getting more weight.
    # Positive lag compares VP1(t) with VP2(t+lag); this does not establish causality.
    times = [start + 10 * i for i in range(max(0, math.floor((end - start) / 10)) + 1)]
    pairs = [(t, supported_value(left, t, max_gap), supported_value(right, t + lag_s, max_gap))
             for t in times if start <= t + lag_s <= end]
    overlap_start, overlap_end = max(start, start - lag_s), min(end, end - lag_s)
    supported_pairs = paired_points(left, [(t - lag_s, value) for t, value in right], overlap_start, overlap_end, max_gap) if overlap_end > overlap_start else []
    support_s = base.integrate([(t, 0 if a is not None and b is not None else None) for t, a, b in supported_pairs], overlap_start, overlap_end, max_gap)["coverage_s"] if supported_pairs else 0
    pairs = [(t, a, b) for t, a, b in pairs if a is not None and b is not None]
    result = {"lag_s": lag_s, "paired_grid_observations": len(pairs), "grid_s": 10,
              "common_supported_duration_s": support_s,
              "supported_time_span_s": pairs[-1][0] - pairs[0][0] if pairs else 0,
              "pearson": None, "pearson_after_linear_detrending": None}
    if len(pairs) < 10 or result["supported_time_span_s"] < 90:
        return result
    def correlation(a, b):
        ma, mb = statistics.mean(a), statistics.mean(b)
        aa, bb = [x - ma for x in a], [x - mb for x in b]
        denominator = math.sqrt(sum(x * x for x in aa) * sum(x * x for x in bb))
        return sum(x * y for x, y in zip(aa, bb)) / denominator if denominator > 1e-10 else None
    times, a, b = zip(*pairs)
    mt = statistics.mean(times)
    denominator = sum((t - mt) ** 2 for t in times)
    def detrend(values):
        mean = statistics.mean(values)
        slope = sum((t - mt) * (v - mean) for t, v in zip(times, values)) / denominator
        return [v - mean - slope * (t - mt) for t, v in zip(times, values)]
    result["pearson"] = correlation(a, b)
    result["pearson_after_linear_detrending"] = correlation(detrend(a), detrend(b))
    return result


def shared_load_report(data, result, max_gap):
    end = min(d["statistics_interval_s"][1] for d in result["devices"].values())
    start_last5 = max(0, end - 300)
    powers = {sid: [(r["feedback_t"], r["short_W"]) for r in rows] for sid, rows in data["rows"].items()}
    returns = {sid: [(r["t"], r["return_C"] if r["category"] == "heating" and r["flow_L_min"] is not None and r["flow_L_min"] > 0 else None) for r in rows] for sid, rows in data["rows"].items()}
    pairs = paired_points(powers[1], powers[2], 0, end, max_gap)
    total = [(t, a + b if a is not None and b is not None else None) for t, a, b in pairs]
    temperature_pairs = paired_points(returns[1], returns[2], start_last5, end, max_gap)
    differences = [a - b for _, a, b in temperature_pairs if a is not None and b is not None]
    valid_return_pairs = [(t, a, b) for t, a, b in temperature_pairs if a is not None and b is not None]
    feedback_evidence = {}
    for sid, rows in data["rows"].items():
        observed = [r for r in rows if start_last5 <= r["feedback_t"] <= end]
        qualified = [r for r in observed if r["short_W"] is not None]
        feedback_evidence[str(sid)] = {
            "original_observations": len(observed), "qualified_observations": len(qualified),
            "distinct_accepted_count_values": len(set(r["feedback_accepted_count"] for r in qualified)),
            "largest_adjacent_original_feedback_gap_s": max((b["feedback_t"] - a["feedback_t"] for a, b in zip(observed, observed[1:])), default=None)}
    return {"interval_s": [0, end], "last5min_interval_s": [start_last5, end],
            "total_target_W": sum(data["targets_W"].values()),
            "time_aligned_sum_of_short_means": base.point_stats(total, 0, end, max_gap),
            "last5min_sum_of_short_means": base.point_stats(total, start_last5, end, max_gap),
            "sum_series": total,
            "last5min_original_feedback_evidence": feedback_evidence,
            "power_correlation_full_observed_interval": pair_correlation(powers[1], powers[2], 0, end, max_gap),
            "power_correlation_last5min": pair_correlation(powers[1], powers[2], start_last5, end, max_gap),
            "power_correlation_last5min_lag_scan": [pair_correlation(powers[1], powers[2], start_last5, end, max_gap, lag) for lag in range(-60, 61, 10)],
            "return_temperature_last5min": {
                "VP1_minus_VP2_min_C": min(differences, default=None),
                "VP1_minus_VP2_max_C": max(differences, default=None),
                "VP1_minus_VP2_sample_mean_C": statistics.mean(differences) if differences else None,
                "VP1_trend_C_per_min": base.linear_trend([(t, a) for t, a, _ in valid_return_pairs]),
                "VP2_trend_C_per_min": base.linear_trend([(t, b) for t, _, b in valid_return_pairs]),
                "correlation": pair_correlation(returns[1], returns[2], start_last5, end, max_gap)},
            "notes": [
                "The pumps share floor heating, so a common hydraulic load is expected. These observations do not establish unstable interaction between controllers.",
                "The plotted sum reconstructs qualified delayed short means at common times by bounded interpolation. It is not a simultaneous instantaneous power measurement or calibrated calorimetry.",
                "Partial statistics end at the shorter observed device interval. No future interpolation or missing-data filling is used.",
                "Startup ramps, source delays, quantized temperatures and overlapping moving averages can produce strong correlations. Detrending removes only a linear trend; it does not remove these confounders.",
                "The10s grid adds no independent observations. Five minutes contain only a few independent trailing-mean windows; original qualified reads/accepted-count diversity and supported duration are reported separately.",
                "Return-temperature comparisons include only observed heating with positive reported water flow. Pause/stagnation, DHW and unknown states are excluded from this shared circulating-load comparison.",
                "Correlation and the lag scan are descriptive, without significance claims. Positive lag means VP1(t) is compared with VP2(t+lag), not that VP1 caused a response.",
                "A negative correlation alone does not demonstrate hunting. Sustained repeated opposing changes with total-power and temperature behavior would be needed to support that interpretation."]}


def report(data, max_gap):
    duration = data["duration_s"]
    result = {"synthetic_fixture": data["fixture"], "requested_interval_s": [0, duration], "targets_W": data["targets_W"],
              "completed": bool(data["outcome"] and data["outcome"].get("completed") and data["outcome"].get("execute", True)),
              "anchor": data["anchor"], "failure": data["failure"], "outcome": data["outcome"],
              "restoration": restoration_status(data["restoration"]), "incomplete_final_log_line": data["incomplete_final_line"],
              "events_sha256": data["events_sha256"], "max_interpolation_gap_s": max_gap, "devices": {}}
    result["regulation_objectives"] = {
        "primary": {"quantity": "actual_supply_temperature_C", "comparison": "strictly_less", "threshold": 40,
                    "exactly40C_meets_goal": False},
        "secondary": {"quantity": "estimated_heating_power_W", "targets_by_device": data["targets_W"]},
        "priority": "Keeping actual supply strictly below40C takes precedence over reaching the individual power targets.",
        "temperature_or_duration_abort": False,
        "hot_response": "Regulation should reduce demand and continue the mission; temperature or time above40C is not an abort condition."}
    for sid, rows in data["rows"].items():
        if not rows:
            raise ValueError(f"No instrumented observations for device{sid}")
        device = {**data, "rows": rows, "target_W": data["targets_W"][sid]}
        d = base.report(device, max_gap)
        end = d["statistics_interval_s"][1]
        mission = [r for r in rows if 0 <= r["t"] <= end]
        last = [r for r in rows if max(0, end - 300) <= r["t"] <= end]
        d["last5min_Hz_range"] = [min((r["hz"] for r in last if r["hz"] is not None), default=None), max((r["hz"] for r in last if r["hz"] is not None), default=None)]
        temperature = [(r["t"], r["supply_C"]) for r in rows]
        source_temperature = source_temperature_points(rows)
        d["thermal_exposure_capture_time"] = {str(threshold): thermal_exposure(temperature, 0, end, threshold, max_gap) for threshold in (40, 42)}
        d["thermal_exposure_distinct_source_time_estimate"] = {str(threshold): thermal_exposure(source_temperature, 0, end, threshold, max_gap) for threshold in (40, 42)}
        d["strict_supply_goal_capture_time"] = strict_goal_exposure(temperature, 0, end, 40, max_gap)
        d["strict_supply_goal_distinct_source_time_estimate"] = strict_goal_exposure(source_temperature, 0, end, 40, max_gap)
        d["last_in_interval_observation"] = mission[-1] if mission else None
        d["last_pre_restore_boundary_observation"] = rows[-1]
        phase_codes = sorted(set(r["effect_phase"] for r in mission))
        d["effect_phase_observation_counts"] = {str(code): sum(r["effect_phase"] == code for r in mission) for code in phase_codes}
        phase_groups = {}
        for name, phase_test in (("thermal_limited_phase4", lambda phase: phase == 4), ("other_phases", lambda phase: phase != 4)):
            group = [r for r in rows if max(0, end - 300) <= r["feedback_t"] <= end and r["short_W"] is not None and phase_test(r["effect_phase"])]
            watts = [r["short_W"] for r in group]
            phase_groups[name] = {"observations": len(watts), "sample_mean_W": statistics.mean(watts) if watts else None,
                                  "min_W": min(watts, default=None), "max_W": max(watts, default=None),
                                  "under_target_observations": sum(w < data["targets_W"][sid] for w in watts)}
        d["last5min_feedback_grouped_by_current_phase"] = {"groups": phase_groups,
            "meaning": "Current observed phase beside delayed short feedback, not power caused instantaneously by that phase. Groups are descriptive sample statistics, not time-weighted causal effects."}
        d["thermal_observer_note"] = "Harness timers may begin before both_active, persist through invalid samples and extend after the window. They are not substituted for supported exposure estimates."
        result["devices"][str(sid)] = d
    result["combined_energy"] = {}
    for key in ("space_water_model_capture_time", "space_water_model_distinct_source_time_estimate", "compressor_gated_space_water_model"):
        metrics = [d[key] for d in result["devices"].values()]
        all_complete = all(m["complete_coverage"] for m in metrics)
        result["combined_energy"][key] = {"both_full_coverage": all_complete,
                                            "whole_interval_kWh": sum(m["energy_kWh_covered"] for m in metrics) if all_complete else None,
                                            "coverage_s_by_device": {sid: d[key]["coverage_s"] for sid, d in result["devices"].items()}}
    rolling = [d["qualified_short_feedback"]["integration"] for d in result["devices"].values()]
    rolling_complete = all(m["complete_coverage"] and m["interval_s"] == [0, duration] for m in rolling)
    result["combined_energy"]["qualified_rolling_mean_integral"] = {
        "both_full_coverage": rolling_complete,
        "whole_interval_kWh": sum(m["energy_kWh_covered"] for m in rolling) if rolling_complete else None,
        "meaning": "Integral of delayed trailing arithmetic sample means; not instantaneous calibrated heat energy."}
    result["flat_target_reference_kWh"] = sum(data["targets_W"].values()) * duration / 3600000
    result["shared_load_analysis"] = shared_load_report(data, result, max_gap)
    result["notes"] = [
        "Offline analysis only. No device calls, control writes or temperature/duration aborts.",
        "Actual supply strictly below40C is the higher-priority regulation goal; the individual power targets are secondary. Exactly40C does not meet the strict goal. Neither temperature nor duration above40C is an abort condition;42C and180s are informational only.",
        "Existing thermal_exposure fields retain strictly>40/42 semantics. Separate strict_supply_goal fields distinguish >=40, >40, exactly40 and <40 durations without counting unknown intervals as goal attainment.",
        "All temperatures/power observations are per-device sequential reads. A dual_sample batch does not establish simultaneous measurements or simultaneous target attainment.",
        "Thermal exposure is interpolation over supported source-valid samples, with explicit unknown coverage. Source-time estimates deduplicate generations and subtract ages; they remain separate from capture-time estimates.",
        "Energy is not claimed for the full interval unless all required intervals are covered. Differently covered partial device energies are never silently summed as a full-window total.",
        "Uncalibrated water-model estimates, quantized sensors, overlapping feedback averages and shared hydraulics limit physical interpretation.",
        "Snapshot endpoints can bracket the interval while source-time endpoints or invalid intermediate heat pairs leave missing energy coverage.",
        "Final restoration results take precedence over preliminary AUTO transport errors; original raw restoration evidence is retained."]
    return result


def plot(data, result, out):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.grid": True, "grid.alpha": .16})
    fig, all_axes = plt.subplots(5, 2, figsize=(16, 15), sharex="col", sharey="row", constrained_layout=True,
                                 gridspec_kw={"height_ratios": [1.4, 1.3, 1, .9, 1]})
    grid = all_axes[4, 0].get_subplotspec().get_gridspec()
    all_axes[4, 0].remove(); all_axes[4, 1].remove()
    total_ax = fig.add_subplot(grid[4, :])
    axes = all_axes[:4, :]
    state = "avbrutet" if data["failure"] else "avslutat" if result["completed"] else "återställning ej verifierad" if result["restoration"]["incomplete_or_failed"] else "pågående"
    prefix = "SYNTETISKT TEST · EJ FYSISK MÄTNING · " if data["fixture"] else ""
    title = f"{prefix}Effektprov VP1 {data['targets_W'][1]/1000:g} kW + VP2 {data['targets_W'][2]/1000:g} kW · {data['duration_s']/60:g} min · {state}"
    fig.suptitle(title, fontsize=16 if not data["fixture"] else 12, weight="bold")
    all_rows = [r for rows in data["rows"].values() for r in rows if r["t"] >= -60]
    powers = [r[k] / 1000 for r in all_rows for k in ("space_hydraulic_W", "short_W", "partial_short_W") if r[k] is not None]
    power_bounds = min(-.3, min(powers, default=0) - .2), max(7, max(powers, default=6) + .3)
    hz_top = max(70, max((r["hz"] for r in all_rows if r["hz"] is not None), default=0) + 10)
    for col, sid in enumerate((1, 2)):
        rows = [r for r in data["rows"][sid] if r["t"] >= -60]
        values = lambda key: [r[key] if r[key] is not None else math.nan for r in rows]
        t, ft, nt = ([r[key] / 60 for r in rows] for key in ("t", "feedback_t", "native_t"))
        def gapped(times, ys):
            tx, vx = [], []
            for index, (at, value) in enumerate(zip(times, ys)):
                if index and (at - times[index - 1]) * 60 > result["max_interpolation_gap_s"]:
                    tx.append((at + times[index - 1]) / 2); vx.append(math.nan)
                tx.append(at); vx.append(value)
            return tx, vx
        ax = axes[0, col]
        ax.axhline(data["targets_W"][sid] / 1000, color="#444", ls="--", label=f"Effektmål {data['targets_W'][sid]/1000:g} kW (prioritet 2)")
        ax.scatter(t, [v / 1000 for v in values("space_hydraulic_W")], s=12, color="#a3b0bd", label="Rå uppskattad vatteneffekt")
        ax.plot(*gapped(ft, [v / 1000 for v in values("short_W")]), "o-", ms=2.3, lw=1.7, color="#086eac", label="Kvalificerat kort medel")
        ax.scatter(ft, [v / 1000 for v in values("partial_short_W")], facecolors="none", edgecolors="#7b5a8c", s=17, label="Delmedel under uppstart")
        ax.set(title=f"VP{sid}", ylabel="Uppskattad värmeeffekt (kW)", ylim=power_bounds)
        ax.legend(fontsize=7, loc="lower right")
        ax = axes[1, col]
        ax.step(*gapped(nt, values("demand_C")), where="post", color="#d58b21", label="Verifierat börvärde")
        ax.plot(*gapped(t, values("supply_C")), color="#b63843", lw=1.8, label="Faktisk framledning")
        ax.plot(*gapped(t, values("return_C")), color="#3b7c55", label="Retur")
        ax.axhline(40, color="#b63843", ls="--", alpha=.7, label="Prioritet 1: faktisk <40 °C")
        ax.axhline(42, color="#777", ls=":", alpha=.6, label="Observation 42 °C")
        hot = [r for r in rows if r["supply_C"] is not None and r["supply_C"] > 40]
        ax.scatter([r["t"] / 60 for r in hot], [r["supply_C"] for r in hot], s=17, facecolors="none", edgecolors="#b63843")
        limited = [r for r in rows if r["effect_phase"] == 4 and r["supply_C"] is not None]
        ax.scatter([r["t"] / 60 for r in limited], [r["supply_C"] for r in limited], s=15, marker="x", color="#444", label="Begränsningsläge")
        ax.set_ylabel("Temperatur (°C)"); ax.legend(ncol=2, fontsize=7)
        ax = axes[2, col]
        ax.step(*gapped(t, values("hz")), where="post", color="#74458d", lw=1.5)
        for label, qualities, color in (("Ready", (0,), "#309168"), ("Pending", (2,), "#d49429"), ("Uppstart/väntan", (1, 8, 9), "#957ca0"), ("Övrig kvalitet", (3, 4, 5, 6, 7), "#b63843")):
            selected = [r for r in rows if r["quality"] in qualities and r["hz"] is not None]
            if selected:
                ax.scatter([r["t"] / 60 for r in selected], [r["hz"] for r in selected], s=15, color=color, label=label)
        ax.set(ylabel="Kompressor (Hz)", ylim=(-2, hz_top)); ax.legend(fontsize=7, ncol=2)
        ax = axes[3, col]
        for name, label, color in (("compressor_Hz", "Hz-källa", "#74458d"), ("flow_cC", "Temperaturkälla", "#b63843"), ("flow_cL_min", "Flödeskälla", "#3b7c55")):
            ages = [r["sources"][name]["age_ms"] / 1000 if r["sources"][name]["age_ms"] < 3600000 else math.nan for r in rows]
            ax.plot(*gapped(t, ages), ".-", ms=2, lw=.9, color=color, label=label)
        ax.axhline(15, color="#555", ls="--", alpha=.65, label="15 s")
        ax.axhline(60, color="#b63843", ls=":", alpha=.6, label="60 s")
        ax.set(ylabel="Källålder (s)", xlabel="Tid från båda ACTIVE (min)", ylim=(0, 65)); ax.legend(fontsize=7, ncol=3)
        ax.tick_params(labelbottom=True)
        for axis in axes[:, col]:
            axis.axvline(0, color="#555", lw=.7, alpha=.6)
            axis.axvline(data["duration_s"] / 60, color="#555", lw=.7, ls=":")
            axis.set_xlim(-.5, data["duration_s"] / 60 + .3)
            for before, after in zip(rows, rows[1:]):
                if after["t"] - before["t"] <= result["max_interpolation_gap_s"] and before["category"] in ("pause", "dhw"):
                    axis.axvspan(before["t"] / 60, after["t"] / 60, color="#e59035" if before["category"] == "dhw" else "#82778d", alpha=.07)
    shared = result["shared_load_analysis"]
    total_ax.axhline(shared["total_target_W"] / 1000, color="#444", ls="--", label=f"Gemensamt effektmål {shared['total_target_W']/1000:g} kW (prioritet 2)")
    total_ax.plot([t / 60 for t, _ in shared["sum_series"]], [w / 1000 if w is not None else math.nan for _, w in shared["sum_series"]], color="#086eac", lw=1.8,
                  label="Summa kortmedel, tidsinterpolerad (asynkrona källor)")
    total_ax.axvline(data["duration_s"] / 60, color="#555", ls=":", lw=.7)
    total_ax.set(xlabel="Tid från båda ACTIVE (min)", ylabel="Sammanlagd uppskattad effekt (kW)", xlim=(-.5, data["duration_s"] / 60 + .3),
                 ylim=(0, max(12, max((w / 1000 for _, w in shared["sum_series"] if w is not None), default=0) + .5)))
    total_ax.legend(fontsize=8, loc="lower right")
    fig.savefig(out / "adaptive-trial.png", dpi=150, bbox_inches="tight", pad_inches=.15)
    fig.savefig(out / "adaptive-trial.svg", bbox_inches="tight", pad_inches=.15)
    plt.close(fig)


def self_test(out):
    """Explicitly synthetic parser/coverage/exposure checks, isolated from live logs."""
    out.mkdir(parents=True, exist_ok=False)
    points = [(0, 39), (10, 41), (20, 43), (30, None), (40, 39), (60, 39)]
    hot40 = thermal_exposure(points, 0, 60, 40, 90)
    hot42 = thermal_exposure(points, 0, 60, 42, 90)
    assert hot40["known_coverage_s"] == 40 and hot40["interpolated_seconds_above"] == 15
    assert hot42["interpolated_seconds_above"] == 5 and hot40["unknown_s"] == 20
    assert thermal_exposure([(0, 41), (200, 41)], 0, 200, 40, 90)["known_coverage_s"] == 0
    plateau = [(0, 39), (10, 40), (20, 40), (30, 41), (40, 40), (50, 40), (60, 39)]
    goal = strict_goal_exposure(plateau, 0, 60, 40, 90)
    assert goal["interpolated_seconds_above"] == 20
    assert goal["interpolated_seconds_exactly_at_threshold"] == 20
    assert goal["interpolated_seconds_at_or_above"] == 40
    assert goal["interpolated_seconds_strictly_below"] == 20
    assert goal["complete_coverage"] and not goal["temperature_or_duration_abort"]
    assert strict_goal_exposure([(0, 40), (60, 40)], 0, 60, 40, 90)["interpolated_seconds_strictly_below"] == 0
    assert strict_goal_exposure([(0, 40), (200, 40)], 0, 200, 40, 90)["unknown_s"] == 200
    a = [(0, 6000), (30, None), (60, 6000)]
    b = [(0, 5000), (60, 5000)]
    combined = paired_points(a, b, 0, 60, 90)
    assert combined == [(0, 6000, 5000), (30, None, 5000), (60, 6000, 5000)]
    assert supported_value(b, 61, 90) is None and supported_value([(0, 1), (100, 2)], 50, 90) is None
    wave = [(t, math.sin(t / 13)) for t in range(0, 301, 10)]
    opposite = [(t, -v) for t, v in wave]
    corr = pair_correlation(wave, opposite, 0, 300, 90)
    assert abs(corr["pearson_after_linear_detrending"] + 1) < 1e-9
    assert pair_correlation([(0, 1), (300, 1)], [(0, 1), (300, 1)], 0, 300, 90)["pearson"] is None
    linear = [(t, 3 + t * 2) for t in range(0, 301, 10)]
    assert pair_correlation(linear, linear, 0, 300, 90)["pearson_after_linear_detrending"] is None
    assert pair_correlation(wave, wave, 0, 300, 90)["common_supported_duration_s"] == 300
    events, raw_rows = [], []
    anchor = 1000
    for index, (at, temp) in enumerate([(-5, 39), *points, (65, 39)]):
        batch = []
        for sid, target in ((1, 6000), (2, 5000)):
            stamp = anchor + at + (sid - 1) * .2
            vals = {"compressor_Hz": 50, "flow_cC": round(temp * 100) if temp is not None else None,
                    "return_cC": 3300, "flow_cL_min": 1400, "heat_W": target if temp is not None else None, "operating_mode_raw": 2}
            samples = {name: {"value": value, "status": 1 if value is not None else 2, "age_ms": 1000, "generation": index + 1} for name, value in vals.items()}
            row = {"sid": sid, "t": stamp - .2, "capture_finished_monotonic": stamp + .5,
                   "snapshot_capture_interval": {"begin": stamp - .1, "end": stamp + .1, "midpoint": stamp},
                   "feedback_capture_interval": {"begin": stamp + .2, "end": stamp + .4, "midpoint": stamp + .3},
                   "snapshot": {"sequence": index + 1, "link_lost": False, "samples": samples},
                   "native": {"operating_mode": 2, "mode": 1, "flow": 4300},
                   "feedback": {"short_w": target, "short_count": 8, "short_span_s": 50, "last_age_s": 1,
                                "quality": 0, "quality_name": "ready", "accepted_count": index + 1},
                   "effect": {"phase": 4, "limit_reason": 4}, "control": {"state": 4, "error": 0, "lease_s": 120}}
            events.append({"time": "synthetic", "kind": "capture", "data": row}); batch.append(row); raw_rows.append(row)
        if at == 0:
            events.append({"time": "synthetic", "kind": "both_active", "data": {"confirmed_monotonic": anchor,
                           "duration_s": 60, "targets_w": {"1": 6000, "2": 5000}, "synthetic_fixture": True}})
        events.append({"time": "synthetic", "kind": "dual_sample", "data": {"rows": batch}})
    # Restoration capture must be excluded, even though it has plausible telemetry.
    events.append({"time": "synthetic", "kind": "command_intent", "data": {"sid": 1, "packet": {"words": [0, 0, 1]}}})
    restored = copy.deepcopy(raw_rows[-2]); restored["snapshot"]["sequence"] = 999
    restored["snapshot_capture_interval"]["midpoint"] += 20
    events.append({"time": "synthetic", "kind": "capture", "data": restored})
    (out / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    (out / "outcome.json").write_text(json.dumps({"completed": True, "execute": True, "synthetic_fixture": True}))
    (out / "restoration.json").write_text(json.dumps({"devices": {"1": {"verified": True}, "2": {"verified": True}}, "initial_auto_attempt_errors": {"1": "synthetic recoverable error"}}))
    data = load(out); result = report(data, 90)
    assert len(data["rows"][1]) == len(data["rows"][2]) == len(points) + 2
    assert result["targets_W"] == {1: 6000, 2: 5000}
    assert result["regulation_objectives"]["secondary"]["targets_by_device"] == {1: 6000, 2: 5000}
    assert not result["regulation_objectives"]["primary"]["exactly40C_meets_goal"]
    assert not result["regulation_objectives"]["temperature_or_duration_abort"]
    assert result["shared_load_analysis"]["total_target_W"] == 11000
    assert result["restoration"]["both_verified"] and not result["restoration"]["incomplete_or_failed"]
    assert result["combined_energy"]["space_water_model_capture_time"]["whole_interval_kWh"] is None
    assert result["devices"]["1"]["thermal_exposure_capture_time"]["40"]["interpolated_seconds_above"] == 15
    assert restoration_status({"devices": {"1": {"error": "fixture"}, "2": {"verified": True}}})["incomplete_or_failed"]
    plot(data, result, out)
    (out / "adaptive-analysis.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"synthetic_fixture": True, "passed": True, "directory": str(out)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path, nargs="?")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--max-gap", type=float, default=90)
    parser.add_argument("--self-test", type=Path, metavar="NEW_DIRECTORY")
    args = parser.parse_args()
    if args.self_test:
        self_test(args.self_test); return
    if args.evidence is None or args.max_gap <= 0:
        parser.error("Provide evidence directory and a positive maximum gap")
    data = load(args.evidence); result = report(data, args.max_gap)
    result["analyzer_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["offline_helper_sha256"] = hashlib.sha256(Path(base.__file__).read_bytes()).hexdigest()
    out = args.out or args.evidence; out.mkdir(parents=True, exist_ok=True)
    plot(data, result, out)
    (out / "adaptive-analysis.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (out / "adaptive-observations.json").write_text(json.dumps(data["rows"], indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
