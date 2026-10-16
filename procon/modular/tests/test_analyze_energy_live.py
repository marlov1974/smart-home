#!/usr/bin/env python3
"""Focused synthetic checks for the offline energy_pair_v1 1.4.1 analyzer."""

from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile
import unittest


MODULAR_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = MODULAR_ROOT / "tools/analyze_energy_live.py"
SPEC = importlib.util.spec_from_file_location("analyze_energy_live", MODULE_PATH)
assert SPEC and SPEC.loader
LIVE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LIVE
SPEC.loader.exec_module(LIVE)

BASE = datetime(2026, 10, 15, 3, 0, tzinfo=timezone.utc)


def stamp(seconds: float) -> str:
    return (BASE + timedelta(seconds=seconds)).isoformat()


def words32(value: int) -> tuple[int, int]:
    raw = value & 0xFFFFFFFF
    return raw >> 16, raw & 0xFFFF


def device(
    target: int,
    short: int | None,
    *,
    phase: int = 3,
    reason: int = 0,
    age: int = 1,
    hz: int = 40,
    state: int = 4,
    saved: int = 1,
) -> dict[str, object]:
    feedback = [0] * 32
    feedback[0:5] = [1, phase, reason, target, 5500]
    high, low = words32(LIVE.INVALID_S32 if short is None else short)
    feedback[7:9] = [high, low]
    feedback[13:18] = [0, 1, 4, age, 30]
    feedback[18:22] = [3500, 0, 10, hz]
    feedback[28] = 0
    feedback[30:32] = [1, 0]
    return {
        "control": {
            "state": state,
            "accepted": 1,
            "applied": 1,
            "rejected": 0,
            "error": 0,
            "saved": saved,
            "touched": 12 if saved else 0,
            "mode": 5 if state == 4 else 0,
            "lease_s": 170 if state == 4 else 0,
            "acks": 1,
        },
        "feedback": feedback,
    }


def sample_event(
    seconds: float,
    *,
    quarter: int,
    qwh: int,
    total: int,
    unknown: int,
    results: tuple[int, ...],
    first: dict[str, object],
    second: dict[str, object],
    phase: str = "running",
    command: int = 7000,
    sent: int = 7000,
) -> dict[str, object]:
    kvs = (
        f"v=2|phase={phase}|q={quarter}|qwh={qwh}|totalwh={total}"
        f"|p1=0|p2=0|want={command}|cmd={command}|sent={sent}|reach=24000"
        f"|shortw=1234|ferr=-12|lim=3/0,3/0|unknown={unknown}"
        f"|results={','.join(str(value) for value in results)}"
    )
    return {
        "time": stamp(seconds),
        "kind": "sample",
        "data": {"script": {"running": phase != "complete"}, "kvs": kvs, "devices": {"1": first, "2": second}},
    }


def write_events(directory: Path, events: list[dict[str, object]], fragment: str = "") -> None:
    payload = "".join(json.dumps(event) + "\n" for event in events) + fragment
    (directory / "events.jsonl").write_text(payload)


def baseline(flow: int = 3050) -> dict[str, object]:
    return {
        str(sid): {
            "native": {
                "power": 1,
                "mode": 2,
                "flow": flow,
                "dhw": 5200,
                "boost": 0,
                "operating_mode": 2,
                "diagnostic_age_s": 1,
            }
        }
        for sid in (1, 2)
    }


class LiveAnalyzerTests(unittest.TestCase):
    def started(self) -> dict[str, object]:
        return {"time": stamp(0), "kind": "started", "data": {}}

    def test_negative_power_is_unavailable_like_live_executor(self):
        decoded = LIVE._decode_device(device(3500, -1, age=0))
        self.assertIsNotNone(decoded)
        self.assertIsNone(decoded.fresh_short_w)

    def test_partial_log_invalid_stale_gap_and_last_fragment(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            zeros = (0,) * 7
            events = [
                self.started(),
                sample_event(
                    5,
                    quarter=0,
                    qwh=0,
                    total=0,
                    unknown=0,
                    results=zeros,
                    first=device(3500, 1000),
                    second=device(3500, 2000),
                    sent=0,
                ),
                sample_event(
                    35,
                    quarter=0,
                    qwh=100,
                    total=100,
                    unknown=30,
                    results=zeros,
                    first=device(3500, None, phase=4, reason=4),
                    second=device(3500, 2100),
                ),
                sample_event(
                    65,
                    quarter=0,
                    qwh=200,
                    total=200,
                    unknown=30,
                    results=zeros,
                    first=device(3500, 1200, age=60),
                    second=device(3500, 2200),
                ),
                sample_event(
                    95,
                    quarter=0,
                    qwh=300,
                    total=300,
                    unknown=30,
                    results=zeros,
                    first=device(3500, 1300),
                    second=device(3500, 2300),
                ),
                sample_event(
                    125,
                    quarter=0,
                    qwh=500,
                    total=500,
                    unknown=30,
                    results=zeros,
                    first=device(3500, 1400),
                    second=device(3500, 2400),
                ),
            ]
            write_events(directory, events, '{"time":')
            (directory / "original-settings.json").write_text(json.dumps(baseline()))

            result = LIVE.analyze(directory)

            self.assertFalse(result["run"]["complete"])
            self.assertTrue(result["evidence"]["incomplete_final_jsonl_line"])
            self.assertEqual(result["energy"]["measured_wh"], 500)
            self.assertIsNone(result["energy"]["error_wh"])
            first = result["energy"]["quarters"][0]
            self.assertEqual(first["state"], "in_progress")
            self.assertIsNone(first["error_wh"])
            self.assertEqual(first["provisional_error_vs_full_target_wh"], -1000)
            self.assertAlmostEqual(first["unknown_s"]["estimate_s"], 30)
            self.assertAlmostEqual(first["pair_power"]["supported_s"], 30)
            self.assertEqual(first["pair_power"]["sampled_peak_w"], 3800)
            self.assertEqual(first["limiter"]["1"]["saturation_observations"], 1)
            self.assertEqual(first["sent_commands"]["sent_uninitialized_observations"], 1)
            self.assertEqual(first["sent_commands"]["sent_min_w"], 7000)
            self.assertEqual(result["restoration"]["state"], "pending")

    def test_complete_energy_commands_limiter_stability_and_restoration(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            results = LIVE.TARGETS_WH
            events: list[dict[str, object]] = [self.started()]
            running_results = [0] * 7
            # A long first target gives the stable-hold qualification two samples.
            for seconds, short1, short2 in (
                (10, 3000, 3100),
                (70, 3200, 3250),
                (130, 3350, 3400),
                (190, 3450, 3500),
                (250, 3500, 3550),
            ):
                events.append(
                    sample_event(
                        seconds,
                        quarter=0,
                        qwh=int(seconds * 6000 / 3600),
                        total=int(seconds * 6000 / 3600),
                        unknown=0,
                        results=tuple(running_results),
                        first=device(3500, short1),
                        second=device(3500, short2),
                    )
                )
            # Boundary-straddling unknown increment and the two v1.4.1 cap reasons.
            events.extend(
                [
                    sample_event(
                        890,
                        quarter=0,
                        qwh=1490,
                        total=1490,
                        unknown=10,
                        results=tuple(running_results),
                        first=device(3500, 3600, phase=4, reason=4),
                        second=device(3500, 3700, phase=4, reason=15),
                    ),
                    sample_event(
                        910,
                        quarter=1,
                        qwh=20,
                        total=1520,
                        unknown=30,
                        results=(1500, 0, 0, 0, 0, 0, 0),
                        first=device(4000, 3650, phase=4, reason=4),
                        second=device(4000, 3750, phase=4, reason=15),
                        command=8500,
                        sent=8000,
                    ),
                    sample_event(
                        940,
                        quarter=1,
                        qwh=80,
                        total=1580,
                        unknown=30,
                        results=(1500, 0, 0, 0, 0, 0, 0),
                        first=device(4250, 3800),
                        second=device(4250, 3900),
                        command=8500,
                        sent=8500,
                    ),
                ]
            )
            # One observation in every remaining quarter keeps status parsing generic.
            cumulative = [1500, 3500, 6000, 10000, 12500, 14500]
            commands = [10000, 16000, 10000, 8000, 6000]
            for quarter in range(2, 7):
                running_results[quarter - 1] = results[quarter - 1]
                seconds = quarter * 900 + 30
                target = commands[quarter - 2] // 2
                events.append(
                    sample_event(
                        seconds,
                        quarter=quarter,
                        qwh=50,
                        total=cumulative[quarter - 1] + 50,
                        unknown=30,
                        results=tuple(running_results),
                        first=device(target, target - 100),
                        second=device(target, target + 100),
                        command=commands[quarter - 2],
                        sent=commands[quarter - 2],
                    )
                )
            events.append(
                sample_event(
                    6301,
                    quarter=7,
                    qwh=1500,
                    total=16000,
                    unknown=30,
                    results=results,
                    first=device(3000, None, phase=0, reason=9, state=0, saved=0),
                    second=device(3000, None, phase=0, reason=9, state=0, saved=0),
                    phase="complete",
                    command=6000,
                    sent=6000,
                )
            )
            write_events(directory, events)
            original = baseline()
            (directory / "original-settings.json").write_text(json.dumps(original))
            restored = {
                str(sid): {
                    "control": {
                        "state": 0,
                        "saved": 0,
                        "touched": 0,
                        "lease_s": 0,
                        "error": 0,
                    },
                    "native": original[str(sid)]["native"],
                    "verified": True,
                }
                for sid in (1, 2)
            }
            (directory / "restoration.json").write_text(json.dumps(restored))

            result = LIVE.analyze(directory)

            self.assertTrue(result["run"]["complete"])
            self.assertEqual(result["energy"]["measured_wh"], 16000)
            self.assertEqual(result["energy"]["error_wh"], 0)
            self.assertEqual([q["credited_mean_w"] for q in result["energy"]["quarters"]], [6000, 8000, 10000, 16000, 10000, 8000, 6000])
            self.assertAlmostEqual(result["energy"]["quarters"][0]["unknown_s"]["estimate_s"], 20)
            self.assertAlmostEqual(result["energy"]["quarters"][1]["unknown_s"]["estimate_s"], 10)
            self.assertEqual(result["energy"]["quarters"][0]["limiter"]["1"]["saturation_observations"], 1)
            self.assertEqual(result["energy"]["quarters"][0]["limiter"]["2"]["saturation_observations"], 1)
            self.assertGreaterEqual(result["commands"]["all_samples"]["command_vs_sent_mismatch_observations"], 1)
            self.assertGreaterEqual(result["devices"]["1"]["stable_hold"]["observations"], 2)
            self.assertIsNotNone(result["devices"]["1"]["ramp"]["steepest_observed_rise_w_per_min"])
            self.assertTrue(result["restoration"]["verified"])
            identity = result["evidence"]["executor_identity"]
            self.assertEqual(identity["expected_sha256"], LIVE.EXPECTED_EXECUTOR_SHA256)
            if identity["repository_source_available"]:
                self.assertTrue(identity["repository_source_matches_expected"])
            else:
                self.assertIsNone(identity["repository_source_matches_expected"])
            markdown = LIVE.render_markdown(result)
            self.assertIn("| 4 | complete | 4000 | 4000 | 0 |", markdown)
            self.assertIn("Enhetsåterställning: **verifierad**", markdown)
            self.assertIn("Script 7 stopp/inaktiverad: **ej verifierat**", markdown)

            postflight = {
                "schema_version": 1,
                "verified_at": stamp(6310),
                "script_7": {"running": False, "enabled": False, "cpu_percent": 0},
            }
            (directory / "postflight.json").write_text(json.dumps(postflight))
            postflight_result = LIVE.analyze(directory)
            self.assertEqual(
                postflight_result["restoration"]["state"],
                "native_control_and_cleanup_verified",
            )
            self.assertTrue(
                postflight_result["restoration"]["script_stopped_and_disabled_verified"]
            )
            self.assertIn(
                "Script 7 stopp/inaktiverad: **verifierat**",
                LIVE.render_markdown(postflight_result),
            )

            restored["2"]["native"]["flow"] = 3000
            (directory / "restoration.json").write_text(json.dumps(restored))
            mismatch = LIVE.analyze(directory)
            self.assertTrue(mismatch["restoration"]["verified"])
            self.assertFalse(mismatch["restoration"]["devices"]["2"]["native_snapshot"]["flow"]["match"])

            restored["2"]["native"]["dhw"] = 5100
            (directory / "restoration.json").write_text(json.dumps(restored))
            mismatch = LIVE.analyze(directory)
            self.assertFalse(mismatch["restoration"]["verified"])
            self.assertFalse(mismatch["restoration"]["devices"]["2"]["native_snapshot"]["dhw"]["match"])

    def test_missing_feedback_breaks_series_and_stale_complete_is_not_final(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            zeros = (0,) * 7
            events = [
                self.started(),
                sample_event(
                    5,
                    quarter=0,
                    qwh=0,
                    total=0,
                    unknown=0,
                    results=zeros,
                    first=device(3500, 1000),
                    second=device(3500, 2000),
                ),
                sample_event(
                    35,
                    quarter=7,
                    qwh=0,
                    total=0,
                    unknown=0,
                    results=zeros,
                    first=device(3500, None, state=0, saved=0),
                    second=device(3500, None, state=0, saved=0),
                    phase="complete",
                ),
                sample_event(
                    55,
                    quarter=0,
                    qwh=100,
                    total=100,
                    unknown=0,
                    results=zeros,
                    first=device(3500, 2000),
                    second=device(3500, 3000),
                ),
            ]
            write_events(directory, events)
            (directory / "original-settings.json").write_text(json.dumps(baseline()))

            result = LIVE.analyze(directory)

            self.assertFalse(result["run"]["complete"])
            self.assertEqual(result["run"]["current_phase"], "running")
            self.assertTrue(result["run"]["script_running"])
            self.assertEqual(result["run"]["nonterminal_complete_samples"], 1)
            self.assertEqual(result["pair_power"]["supported_s"], 0)
            self.assertEqual(result["devices"]["1"]["ramp"]["supported_adjacent_intervals"], 0)
            self.assertEqual(len(result["devices"]["1"]["accepted_target_segments"]), 2)

    def test_complete_malformed_line_and_multiple_runs_are_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            (directory / "events.jsonl").write_text(json.dumps(self.started()) + "\n{" + "\n")
            with self.assertRaises(json.JSONDecodeError):
                LIVE.analyze(directory)

            write_events(directory, [self.started(), self.started()])
            with self.assertRaisesRegex(ValueError, "multiple started"):
                LIVE.analyze(directory)


if __name__ == "__main__":
    unittest.main()
