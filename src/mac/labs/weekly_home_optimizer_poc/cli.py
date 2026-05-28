"""CLI for the P0018 weekly home optimizer POC."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence, TextIO

from .planner import build_weekly_plan
from .ppm_plan import DEFAULT_OCCUPANCY_GAIN_PPM_H
from .tables import format_csv, format_json, format_table


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse the public POC CLI arguments."""

    parser = argparse.ArgumentParser(description="Build a weekly heat, PPM and RH-policy POC plan.")
    parser.add_argument("--week", required=True, type=int, help="ISO week number, 1..53.")
    parser.add_argument("--ppm", required=True, type=float, help="Current house PPM.")
    parser.add_argument("--house-temp", required=True, type=float, help="Current house temperature in C.")
    parser.add_argument(
        "--occupancy-gain-ppm-h",
        type=float,
        default=DEFAULT_OCCUPANCY_GAIN_PPM_H,
        help="POC occupancy gain per hour. Defaults to 70.",
    )
    parser.add_argument("--format", choices=("table", "json", "csv"), default="table")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None, stdout: TextIO | None = None) -> int:
    """Run the CLI and write the requested output format."""

    out = stdout if stdout is not None else sys.stdout
    args = parse_args(argv)
    plan = build_weekly_plan(
        args.week,
        args.ppm,
        args.house_temp,
        occupancy_gain_ppm_h=args.occupancy_gain_ppm_h,
    )
    if args.format == "json":
        out.write(format_json(plan))
    elif args.format == "csv":
        out.write(format_csv(plan))
    else:
        out.write(format_table(plan))
    return 0
