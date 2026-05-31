"""CLI for P0035 Swedish special-day calendar."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import generate_calendar, write_calendar_csv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m src.mac.services.swedish_calendar")
    parser.add_argument("--start-year", type=int, default=2022)
    parser.add_argument("--end-year", type=int, default=2035)
    parser.add_argument("--csv", default="data/calendar/se_special_days_2022_2035.csv")
    args = parser.parse_args(argv)
    rows = generate_calendar(args.start_year, args.end_year)
    write_calendar_csv(rows, Path(args.csv))
    print(json.dumps({"ok": True, "rows": len(rows), "csv": args.csv}, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
