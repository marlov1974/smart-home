"""CLI for P0031 weather history service."""

from __future__ import annotations

import argparse
from dataclasses import asdict, is_dataclass
from datetime import date
import json
from pathlib import Path
import sys

from .ingest import backfill, ingest_daily, latest_safe_complete_day
from .launchd import install_launchd_plist
from .storage import connect_db, default_db_path, initialize_schema, validate_weather_continuity


DEFAULT_START_DATE = date(2022, 5, 30)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m src.mac.services.weather_history")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init-db")
    init_parser.add_argument("--db", default=str(default_db_path()))

    backfill_parser = sub.add_parser("backfill")
    backfill_parser.add_argument("--db", default=str(default_db_path()))
    backfill_parser.add_argument("--start-date", "--start", dest="start_date", default=DEFAULT_START_DATE.isoformat())
    backfill_parser.add_argument("--end-date", "--end", dest="end_date")

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--db", default=str(default_db_path()))
    validate_parser.add_argument("--start-date", "--start", dest="start_date", default=DEFAULT_START_DATE.isoformat())
    validate_parser.add_argument("--end-date", "--end", dest="end_date")

    ingest_parser = sub.add_parser("ingest-daily")
    ingest_parser.add_argument("--db", default=str(default_db_path()))

    install_parser = sub.add_parser("install-daily-job")
    install_parser.add_argument("--db", default=str(default_db_path()))
    install_parser.add_argument("--no-launchctl", action="store_true")

    args = parser.parse_args(argv)
    try:
        db_path = str(Path(args.db).expanduser())
        if args.command == "init-db":
            initialize_schema(db_path)
            print(_json({"ok": True, "db_path": db_path}))
            return 0
        initialize_schema(db_path)
        with connect_db(db_path) as conn:
            if args.command == "backfill":
                start = date.fromisoformat(args.start_date)
                end = date.fromisoformat(args.end_date) if args.end_date else latest_safe_complete_day()
                print(_json(backfill(conn, start_date=start, end_date=end, db_path=db_path)))
                return 0
            if args.command == "validate":
                start = date.fromisoformat(args.start_date)
                end = date.fromisoformat(args.end_date) if args.end_date else latest_safe_complete_day()
                report = validate_weather_continuity(conn, start, end, db_path=db_path)
                print(_json(report))
                return 0 if report.complete else 2
            if args.command == "ingest-daily":
                print(_json(ingest_daily(conn, db_path=db_path)))
                return 0
            if args.command == "install-daily-job":
                result = install_launchd_plist(db_path=db_path, run_launchctl=not args.no_launchctl)
                print(_json(result))
                return 0 if result.loaded or args.no_launchctl else 3
    except Exception as exc:
        print(_json({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    return 2


def _json(value: object) -> str:
    return json.dumps(_plain(value), sort_keys=True, separators=(",", ":"))


def _plain(value: object) -> object:
    if is_dataclass(value):
        return _plain(asdict(value))
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
