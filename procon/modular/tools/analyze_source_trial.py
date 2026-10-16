"""Offline analysis of source_trial_vp1.py evidence; no live-module imports.

Usage: /tmp/procon-dev-venv/bin/python analyze_source_trial.py RUN_DIRECTORY
Creates source-analysis.json, source-trial.png and source-trial.svg.
Requires explicit monotonic capture intervals; never synthesizes physical data.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import statistics

os.environ.setdefault("MPLCONFIGDIR", "/tmp/procon-source-analysis-mpl")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SOURCES = ("compressor_Hz", "flow_cC", "return_cC", "flow_cL_min", "heat_W", "operating_mode_raw")
HEATING_MODES = (2, 7)


def read_events(path):
    raw = (path / "events.jsonl").read_bytes()
    events, incomplete = [], False
    lines = raw.splitlines()
    for index, line in enumerate(lines):
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            if index != len(lines) - 1:
                raise
            incomplete = True  # Concurrent append; retain only complete events.
    return events, incomplete, hashlib.sha256(raw).hexdigest()


def valid(sample):
    return (sample.get("status") == 1 and sample.get("value") is not None
            and 0 <= sample.get("age_ms", 60000) < 60000)


def optional_json(path):
    return json.loads(path.read_text()) if path.exists() else None


def load(path):
    events, incomplete, digest = read_events(path)
    start = next((e for e in events if e["kind"] == "trial_start"), None)
    if start is None:
        raise ValueError("No confirmed trial_start yet; no physical trial analysis generated")
    anchor = start["data"].get("mission_start_monotonic")
    if anchor is None:
        raise ValueError("Missing monotonic mission origin; cannot claim exact capture-time integration")
    duration = start["data"]["duration_s"]
    observations, restoring, seen = [], False, set()
    for event in events:
        kind, row = event["kind"], event["data"]
        if kind == "command_intent" and row.get("packet", {}).get("words", [0, 0, 0])[2] == 1:
            restoring = True
        if restoring or kind not in ("capture", "trial_sample") or row.get("sid") != 1 or "snapshot" not in row:
            continue
        if "snapshot_capture_interval" not in row or "feedback_capture_interval" not in row:
            raise ValueError("Capture lacks explicit snapshot/feedback timing intervals")
        snap, feedback, native = row["snapshot"], row["feedback"], row["native"]
        sc, fc = row["snapshot_capture_interval"], row["feedback_capture_interval"]
        key = (snap["sequence"], sc["midpoint"])
        if key in seen:
            continue
        seen.add(key)
        samples = snap["samples"]
        value = lambda name: samples[name]["value"] if valid(samples[name]) and not snap["link_lost"] else None
        hz, mode = value("compressor_Hz"), value("operating_mode_raw")
        if hz == 255:
            hz = None
        native_mode = native["operating_mode"]
        if mode in (1, 6) or native_mode in (1, 6):
            category = "dhw"
        elif mode in (0, 2, 7) and native_mode in (0, 2, 7) and hz == 0:
            category = "pause"
        elif mode in HEATING_MODES and native_mode in HEATING_MODES and hz is not None and hz > 0:
            category = "heating"
        else:
            category = "unknown_or_transition"
        short_available = (feedback.get("short_w") is not None and feedback.get("short_count", 0) > 0
                           and feedback.get("last_age_s") is not None and feedback["last_age_s"] < 60
                           and feedback["quality"] in (0, 1, 2, 9) and category == "heating")
        short_qualified = (short_available and feedback["quality"] in (0, 2)
                           and feedback["short_count"] >= 3 and feedback["short_span_s"] >= 20)
        heat = value("heat_W")
        source_key = tuple(samples[k]["generation"] for k in ("flow_cC", "return_cC", "flow_cL_min"))
        observations.append({
            "t": sc["midpoint"] - anchor, "feedback_t": fc["midpoint"] - anchor,
            "native_t": row["t"] - anchor, "capture_end_t": row["capture_finished_monotonic"] - anchor,
            "snapshot_read_width_s": sc["end"] - sc["begin"], "feedback_read_width_s": fc["end"] - fc["begin"],
            "source_heat_t": sc["midpoint"] - anchor - samples["heat_W"]["age_ms"] / 1000 if heat is not None else None,
            "source_heat_key": source_key, "category": category, "hz": hz, "mode": mode, "link_lost": snap["link_lost"],
            "native_operating_mode": native_mode, "raw_heat_W": heat,
            "space_hydraulic_W": heat if category in ("heating", "pause") else None,
            "compressor_gated_space_W": (0 if category == "pause" else heat) if category in ("heating", "pause") else None,
            "short_W": feedback["short_w"] if short_qualified else None,
            "partial_short_W": feedback["short_w"] if short_available and not short_qualified else None,
            "quality": feedback["quality"], "quality_name": feedback["quality_name"],
            "short_count": feedback["short_count"], "short_span_s": feedback["short_span_s"],
            "feedback_source_age_s": feedback["last_age_s"], "feedback_accepted_count": feedback["accepted_count"],
            "supply_C": value("flow_cC") / 100 if value("flow_cC") is not None else None,
            "return_C": value("return_cC") / 100 if value("return_cC") is not None else None,
            "flow_L_min": value("flow_cL_min") / 100 if value("flow_cL_min") is not None else None,
            "demand_C": native["flow"] / 100, "native_control_mode": native["mode"],
            "effect_phase": row["effect"]["phase"], "limit_reason": row["effect"]["limit_reason"],
            "control_state": row["control"]["state"], "control_error": row["control"]["error"],
            "lease_s": row["control"]["lease_s"], "sources": {name: samples[name] for name in SOURCES},
        })
    observations.sort(key=lambda r: r["t"])
    return {"rows": observations, "anchor": start, "duration_s": duration,
            "target_W": start["data"].get("target_w", 6000), "incomplete_final_line": incomplete,
            "events_sha256": digest, "outcome": optional_json(path / "outcome.json"),
            "failure": optional_json(path / "failure.json"), "restoration": optional_json(path / "restoration.json")}


def pieces(points, start, end, max_gap):
    for (ta, va), (tb, vb) in zip(points, points[1:]):
        low, high = max(start, ta), min(end, tb)
        if high <= low or tb <= ta or tb - ta > max_gap or va is None or vb is None:
            continue
        interp = lambda t: va + (vb - va) * (t - ta) / (tb - ta)
        yield low, high, interp(low), interp(high)


def integrate(points, start, end, max_gap=90):
    segments = list(pieces(points, start, end, max_gap))
    covered = sum(b - a for a, b, _, _ in segments)
    area = sum((pa + pb) * (b - a) / 2 for a, b, pa, pb in segments)
    missing, cursor = [], start
    for a, b, _, _ in segments:
        if a > cursor + 1e-7:
            missing.append([cursor, a])
        cursor = max(cursor, b)
    if cursor < end - 1e-7:
        missing.append([cursor, end])
    def boundary(at):
        return next(({"before_s": a, "after_s": b, "before_W": va, "after_W": vb}
                     for (a, va), (b, vb) in zip(points, points[1:])
                     if a <= at <= b and 0 < b - a <= max_gap and va is not None and vb is not None), None)
    return {"interval_s": [start, end], "energy_kWh_covered": area / 3600000,
            "time_weighted_mean_W_on_covered_interval": area / covered if covered else None,
            "coverage_s": covered, "complete_coverage": end > start and abs(covered - (end - start)) < 1e-6,
            "missing_intervals_s": missing, "start_boundary": boundary(start), "end_boundary": boundary(end)}


def linear_trend(points):
    if len(points) < 3:
        return None
    mt, mw = statistics.mean(t for t, _ in points), statistics.mean(w for _, w in points)
    d = sum((t - mt) ** 2 for t, _ in points)
    return 60 * sum((t - mt) * (w - mw) for t, w in points) / d if d else None


def point_stats(points, start, end, max_gap):
    chosen = [(t, value) for t, value in points if start <= t <= end and value is not None]
    values = [value for _, value in chosen]
    return {"interval_s": [start, end], "observations": len(values),
            "sample_mean_W": statistics.mean(values) if values else None,
            "min_W": min(values, default=None), "max_W": max(values, default=None),
            "sample_std_W": statistics.pstdev(values) if values else None,
            "linear_trend_W_per_min": linear_trend(chosen), "integration": integrate(points, start, end, max_gap)}


def source_summary(rows):
    report = {}
    for name in SOURCES:
        samples = [r["sources"][name] for r in rows]
        good = [s for s in samples if valid(s)]
        transitions = sum(a["generation"] != b["generation"] for a, b in zip(good, good[1:]))
        ages = [s["age_ms"] / 1000 for s in good]
        report[name] = {"status_valid_observations": len(good), "status_counts": dict(Counter(s["status"] for s in samples)),
                        "link_lost_observations": sum(r["link_lost"] for r in rows),
                        "sentinel255_observations": sum(s.get("value") == 255 for s in samples) if name == "compressor_Hz" else None,
                        "minimum_age_s": min(ages, default=None), "maximum_age_s": max(ages, default=None),
                        "median_age_s": statistics.median(ages) if ages else None,
                        "observations_age15_to59_s": sum(15 <= age < 60 for age in ages),
                        "generation_transitions": transitions,
                        "consecutive_duplicate_generation_observations": max(0, len(good) - 1 - transitions)}
    return report


def source_heat_points(rows):
    """Additional source-time estimate; constituent generations dedupe cached reads."""
    result, seen = [], set()
    for r in rows:
        if r["space_hydraulic_W"] is None:
            result.append((r["t"], None))
            continue
        key = r["source_heat_key"]
        if key in seen:
            continue
        seen.add(key)
        result.append((r["source_heat_t"], r["space_hydraulic_W"]))
    return sorted(result, key=lambda p: p[0])


def report(data, max_gap):
    rows, duration = data["rows"], data["duration_s"]
    complete = bool(data["outcome"] and data["outcome"].get("completed") and data["outcome"].get("execute", True))
    observed_end = max((r["t"] for r in rows), default=0)
    end = duration if complete else min(duration, max(0, observed_end))
    mission = [r for r in rows if 0 <= r["t"] <= end]
    raw = [(r["t"], r["space_hydraulic_W"]) for r in rows]
    gated = [(r["t"], r["compressor_gated_space_W"]) for r in rows]
    short = [(r["feedback_t"], r["short_W"]) for r in rows]
    first_index = next((i for i, r in enumerate(rows) if 0 <= r["t"] <= end and r["category"] == "heating"), None)
    first_hz = rows[first_index]["t"] if first_index is not None else None
    previous_hz_row = rows[first_index - 1] if first_index is not None and first_index else None
    restart_interval = ([previous_hz_row["t"], first_hz] if previous_hz_row and previous_hz_row["hz"] == 0
                        and first_hz - previous_hz_row["t"] <= max_gap else None)
    premission = next((r for r in reversed(rows) if r["t"] < 0), None)
    already_running = bool(premission and -premission["t"] <= max_gap and premission["category"] == "heating")
    thresholds = {}
    for percent in (90, 95, 100):
        watts = data["target_W"] * percent / 100
        index = next((i for i, (t, w) in enumerate(short) if 0 <= t <= end and w is not None and w >= watts), None)
        first = short[index][0] if index is not None else None
        prior = short[index - 1] if index is not None and index else None
        bracket = ([prior[0], first] if prior and prior[1] is not None and prior[1] < watts and first - prior[0] <= max_gap else None)
        thresholds[str(percent)] = {"threshold_W": watts, "first_observed_feedback_s": first,
                                   "previous_below_to_first_above_read_interval_s": bracket,
                                   "since_first_observed_heating_Hz_s": first - first_hz if first is not None and first_hz is not None else None}
    stops, stopped, running, last_running = [], None, already_running, premission["t"] if already_running else None
    for r in mission:
        if r["hz"] is not None and r["hz"] > 0:
            if stopped is not None:
                stopped["resumed_s"] = r["t"]; stops.append(stopped); stopped = None
            running = True; last_running = r["t"]
        elif running and r["hz"] == 0:
            if stopped is None:
                stopped = {"last_positive_observed_s": last_running, "first_zero_s": r["t"], "zero_observations": 0, "categories": []}
            stopped["last_zero_s"] = r["t"]; stopped["zero_observations"] += 1
            if r["category"] not in stopped["categories"]:
                stopped["categories"].append(r["category"])
    if stopped is not None:
        stops.append(stopped)
    demands = [r["demand_C"] for r in mission if r["native_control_mode"] == 1]
    supply = [r["supply_C"] for r in mission if r["supply_C"] is not None]
    heating_supply = [r["supply_C"] for r in mission if r["supply_C"] is not None and r["category"] in ("heating", "pause")]
    points = source_heat_points(rows)
    return {"completed": complete, "failure": data["failure"], "outcome": data["outcome"],
            "restoration": data["restoration"], "requested_active_interval_s": [0, duration],
            "statistics_interval_s": [0, end], "observed_snapshot_end_s": observed_end,
            "anchor": data["anchor"], "events_sha256": data["events_sha256"],
            "incomplete_final_log_line": data["incomplete_final_line"], "target_W": data["target_W"],
            "max_interpolation_gap_s": max_gap, "observations": len(mission),
            "category_observation_counts": dict(Counter(r["category"] for r in mission)),
            "feedback_quality_counts": dict(Counter(r["quality_name"] for r in mission)),
            "space_water_model_capture_time": integrate(raw, 0, duration, max_gap),
            "space_water_model_distinct_source_time_estimate": integrate(points, 0, duration, max_gap),
            "compressor_gated_space_water_model": integrate(gated, 0, duration, max_gap),
            "qualified_short_feedback": point_stats(short, 0, end, max_gap),
            "last5min_qualified_short_feedback": point_stats(short, max(0, end - 300), end, max_gap),
            "last5min_raw_space_water_model": point_stats(raw, max(0, end - 300), end, max_gap),
            "first_observed_heating_Hz_s": first_hz,
            "already_running_at_mission_start_last_observation": already_running,
            "first_heating_Hz_left_censored": first_hz is not None and restart_interval is None,
            "initial_heating_start_read_interval_s": restart_interval,
            "thresholds_of_qualified_short_feedback": thresholds, "observed_post_start_stops": stops,
            "unknown_Hz_observations": sum(r["hz"] is None for r in mission),
            "actual_supply_max_C_all_modes": max(supply, default=None),
            "actual_supply_max_C_heating_pause": max(heating_supply, default=None),
            "requested_supply_range_C": [min(demands), max(demands)] if demands else None,
            "temperature_limited_observations": sum(r["effect_phase"] == 4 for r in mission),
            "control_errors": sorted(set(r["control_error"] for r in mission)),
            "minimum_lease_s": min((r["lease_s"] for r in mission), default=None),
            "source_age_and_generation": source_summary(mission),
            "maximum_capture_uncertainty_s": max((r["snapshot_read_width_s"] for r in rows), default=None),
            "maximum_feedback_read_duration_s": max((r["feedback_read_width_s"] for r in rows), default=None),
            "notes": [
                "Offline only. Snapshot capture, feedback read and native readback have different clocks. Restoration reads are excluded; unpaired pre-restore captures retain a possible guard-triggering observation.",
                "Heat/energy are uncalibrated water-model estimates (rho1, cp4180), not electrical power, COP, or compressor-only calorimetry. Valid raw heat may include auxiliary heat or residual circulation.",
                "Frozen raw400 telemetry is an atomic cache image, not simultaneous physical sensor acquisition. Source-time estimate subtracts recorded heat age and deduplicates constituent generations; capture-time integral separately uses observed read times.",
                "Main water-model energy includes valid signed residual circulation during native pause. Compressor-gated variant explicitly assumes zero compressor production atHz0. DHW/unknown modes are missing space-heating coverage, never silently zero.",
                "Feedback short_W is the firmware arithmetic sample mean over a trailing, possibly partial60s window. Here its time-weighted mean is separately integrated over host feedback read times. Pending quality can retain valid historical averages; warmup/settling values are plotted separately and excluded from qualified thresholds.",
                "Threshold times are first observed qualified short-mean readings, limited by sampling, source ages and averaging delay; they do not prove instantaneous or sustained achievement.",
                "Only adjacent supported observations within the configured gap are interpolated. Missing endpoints/gaps remain uncovered; no extrapolated energy or future samples are invented.",
                "Last5min ends at requested duration for completed trials, or the observed interval end while partial/aborted. Range and trend are descriptive; overlapping averages and quantization do not provide independent confidence intervals.",
                "Observed post-startHz0 episodes distinguish pauses/DHW; absence of sampled stops is not continuous proof through unknown telemetry gaps."]}


def plot(data, result, out):
    rows = [r for r in data["rows"] if r["t"] >= -60]
    if not rows:
        raise ValueError("No observations to plot")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.grid": True, "grid.alpha": .18})
    fig, axes = plt.subplots(4, 1, figsize=(12, 12), sharex=True, constrained_layout=True,
                             gridspec_kw={"height_ratios": [1.4, 1.2, 1, 1]})
    restoration_error = data["restoration"] and any("error" in item for item in data["restoration"].values())
    state = "avbrutet" if data["failure"] else "avslutat" if result["completed"] else "återställning ej verifierad" if restoration_error else "pågående"
    fig.suptitle(f"VP1 · effektmål {data['target_W']/1000:g} kW · {data['duration_s']/60:g} min · {state}", fontsize=17, weight="bold")
    values = lambda key: [r[key] if r[key] is not None else math.nan for r in rows]
    t, ft, nt = ([r[key] / 60 for r in rows] for key in ("t", "feedback_t", "native_t"))
    def gapped(times, ys):
        tx, vx = [], []
        for index, (at, value) in enumerate(zip(times, ys)):
            if index and (at - times[index - 1]) * 60 > result["max_interpolation_gap_s"]:
                tx.append((at + times[index - 1]) / 2); vx.append(math.nan)
            tx.append(at); vx.append(value)
        return tx, vx
    axes[0].axhline(data["target_W"] / 1000, color="#444", ls="--", label="Effektmål")
    axes[0].scatter(t, [v / 1000 for v in values("space_hydraulic_W")], s=17, color="#9faebb", label="Rå uppskattad vatteneffekt")
    axes[0].plot(*gapped(ft, [v / 1000 for v in values("short_W")]), "o-", ms=3, lw=2, color="#0871b3", label="Kvalificerat kort medel")
    axes[0].scatter(ft, [v / 1000 for v in values("partial_short_W")], facecolors="none", edgecolors="#7c6994", s=28, label="Delmedel under uppstart")
    axes[0].set_ylabel("Uppskattad värmeeffekt (kW)")
    observed_power = [r[k] / 1000 for r in rows for k in ("space_hydraulic_W", "short_W", "partial_short_W") if r[k] is not None]
    axes[0].set_ylim(min(-.3, min(observed_power, default=0) - .2), max(7, max(observed_power, default=6) + .3))
    axes[0].legend(loc="lower right", fontsize=8)
    axes[1].step(*gapped(nt, values("demand_C")), where="post", color="#dc8a20", label="Verifierat börvärde")
    axes[1].plot(*gapped(t, values("supply_C")), color="#b53642", lw=2, label="Faktisk framledning")
    axes[1].plot(*gapped(t, values("return_C")), color="#397a52", label="Retur")
    axes[1].axhline(40, color="#b53642", ls="--", alpha=.65, label="Gräns faktisk framledning")
    limited = [r for r in rows if r["effect_phase"] == 4 and r["supply_C"] is not None]
    axes[1].scatter([r["t"]/60 for r in limited], [r["supply_C"] for r in limited], marker="x", s=20, color="#333", label="Begränsningsläge")
    axes[1].set_ylabel("Temperatur (°C)"); axes[1].legend(ncol=2, fontsize=8)
    axes[2].step(*gapped(t, values("hz")), where="post", color="#654085", lw=1.5)
    for label, qualities, color in (("Ready", (0,), "#2b9463"), ("Pending", (2,), "#df9528"),
                                    ("Uppstart/väntan", (1, 8, 9), "#897096"), ("Övrig kvalitet", (3, 4, 5, 6, 7), "#c43d42")):
        selected = [r for r in rows if r["quality"] in qualities and r["hz"] is not None]
        if selected:
            axes[2].scatter([r["t"]/60 for r in selected], [r["hz"] for r in selected], color=color, s=23, label=label)
    axes[2].set_ylabel("Kompressor (Hz)"); axes[2].set_ylim(-2, max(70, max((r["hz"] for r in rows if r["hz"] is not None), default=0) + 10)); axes[2].legend(ncol=4, fontsize=8)
    for name, label, color in (("compressor_Hz", "Hz-källa", "#654085"), ("flow_cC", "Temperaturkälla", "#b53642"), ("flow_cL_min", "Flödeskälla", "#397a52")):
        age = [r["sources"][name]["age_ms"] / 1000 if r["sources"][name]["age_ms"] < 3600000 else math.nan for r in rows]
        axes[3].plot(*gapped(t, age), ".-", ms=3, lw=1, color=color, label=label)
    axes[3].axhline(15, ls="--", color="#555", label="15 s: gräns för snabb reglering")
    axes[3].axhline(60, ls=":", color="#b53642", label="60 s: gammal källa")
    axes[3].set(ylabel="Källålder vid snapshot (s)", xlabel="Tid från bekräftad EFFECT-start (min)", ylim=(0, 65))
    axes[3].legend(ncol=3, fontsize=8)
    for axis in axes:
        axis.axvline(0, color="#555", lw=.7, alpha=.6)
        axis.axvline(data["duration_s"] / 60, color="#555", lw=.7, ls=":")
        axis.set_xlim(-.5, data["duration_s"] / 60 + .3)
        for before, after in zip(rows, rows[1:]):
            if after["t"] - before["t"] <= result["max_interpolation_gap_s"] and before["category"] in ("dhw", "pause"):
                axis.axvspan(before["t"] / 60, after["t"] / 60,
                             color="#e98a27" if before["category"] == "dhw" else "#81778b", alpha=.055)
    axes[2].text(.01, .96, "Grått band: observerad paus · orange band: varmvatten. Markörer visar separat återkopplingskvalitet.",
                 transform=axes[2].transAxes, va="top", fontsize=8)
    fig.savefig(out / "source-trial.png", dpi=150, bbox_inches="tight", pad_inches=.15)
    fig.savefig(out / "source-trial.svg", bbox_inches="tight", pad_inches=.15)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--max-gap", type=float, default=90)
    args = parser.parse_args()
    if args.max_gap <= 0:
        parser.error("--max-gap must be positive")
    data = load(args.evidence)
    result = report(data, args.max_gap)
    out = args.out or args.evidence
    out.mkdir(parents=True, exist_ok=True)
    plot(data, result, out)
    (out / "source-analysis.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (out / "source-observations.json").write_text(json.dumps(data["rows"], indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
