"""CLI for the P0018 weekly home optimizer POC."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence, TextIO

from .planner import build_weekly_plan
from .ppm_plan import DEFAULT_PEOPLE
from .tables import format_csv, format_json, format_table


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse the public POC CLI arguments."""

    parser = argparse.ArgumentParser(description="Build a weekly heat, PPM and RH-policy POC plan.")
    parser.add_argument("--week", required=True, type=int, help="ISO week number, 1..53.")
    parser.add_argument("--ppm", required=True, type=float, help="Current house PPM.")
    parser.add_argument("--house-temp", required=True, type=float, help="Current house temperature in C.")
    parser.add_argument("--people", type=float, default=DEFAULT_PEOPLE, help="People count for POC CO2 load.")
    parser.add_argument("--format", choices=("table", "json", "csv"), default="table")
    parser.add_argument("--fixture-weather", action="store_true", help="Use deterministic fixture weather.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None, stdout: TextIO | None = None) -> int:
    """Run the CLI and write the requested output format."""

    out = stdout if stdout is not None else sys.stdout
    args = parse_args(argv)
    plan = build_weekly_plan(
        args.week,
        args.ppm,
        args.house_temp,
        people=args.people,
        prefer_real_weather=not args.fixture_weather,
    )
    if args.format == "json":
        out.write(format_json(plan))
    elif args.format == "csv":
        out.write(format_csv(plan))
    else:
        out.write(format_table(plan))
    return 0
