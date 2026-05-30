"""CLI for the P0030 spot price history store."""

from __future__ import annotations

import argparse
from dataclasses import asdict, is_dataclass
from datetime import date, timedelta
import json
from pathlib import Path
import sys

from .ingest import backfill, ingest_daily, ingest_daily_for_areas
from .launchd import install_daily_job
from .storage import connect_db, default_db_path, init_db, validate_range, validate_system_proxy


DEFAULT_START_DATE = date(2022, 5, 30)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m src.mac.services.spotprice_history")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init-db")
    init_parser.add_argument("--db", default=str(default_db_path()))

    backfill_parser = sub.add_parser("backfill")
    _add_common(backfill_parser)
    backfill_parser.add_argument("--start-date", default=DEFAULT_START_DATE.isoformat())
    backfill_parser.add_argument("--end-date")

    ingest_parser = sub.add_parser("ingest-daily")
    _add_common(ingest_parser)
    ingest_parser.add_argument("--areas", default="SE3,SE1")

    validate_parser = sub.add_parser("validate")
    _add_common(validate_parser)
    validate_parser.add_argument("--start-date", default=DEFAULT_START_DATE.isoformat())
    validate_parser.add_argument("--end-date")

    proxy_parser = sub.add_parser("validate-system-proxy")
    proxy_parser.add_argument("--db", default=str(default_db_path()))
    proxy_parser.add_argument("--start-date", default=DEFAULT_START_DATE.isoformat())
    proxy_parser.add_argument("--end-date")

    launchd_parser = sub.add_parser("install-daily-job")
    _add_common(launchd_parser)
    launchd_parser.add_argument("--no-launchctl", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "init-db":
            init_db(args.db)
            print(_json({"ok": True, "db_path": str(Path(args.db).expanduser())}))
            return 0

        db_path = str(Path(args.db).expanduser())
        init_db(db_path)
        with connect_db(db_path) as conn:
            if args.command == "backfill":
                start = date.fromisoformat(args.start_date)
                end = date.fromisoformat(args.end_date) if args.end_date else date.today() - timedelta(days=1)
                summary = backfill(conn, area=args.area, start_date=start, end_date=end, db_path=db_path)
                print(_json(summary))
                return 0
            if args.command == "ingest-daily":
                areas = [area.strip() for area in args.areas.split(",") if area.strip()] if args.areas else [args.area]
                summary = ingest_daily_for_areas(conn, areas=areas, db_path=db_path)
                print(_json(summary))
                return 0
            if args.command == "validate":
                start = date.fromisoformat(args.start_date)
                end = date.fromisoformat(args.end_date) if args.end_date else None
                report = validate_range(conn, args.area, start, end, db_path=db_path)
                print(_json(report))
                return 0 if report.ok else 2
            if args.command == "validate-system-proxy":
                start = date.fromisoformat(args.start_date)
                end = date.fromisoformat(args.end_date) if args.end_date else None
                if end is None:
                    row = conn.execute("SELECT MAX(local_date) AS local_date FROM spot_prices WHERE area='SE1'").fetchone()
                    end = date.fromisoformat(row["local_date"]) if row and row["local_date"] else start
                report = validate_system_proxy(conn, start, end, db_path=db_path)
                print(_json(report))
                return 0 if report["complete"] else 2
            if args.command == "install-daily-job":
                result = install_daily_job(db_path=db_path, run_launchctl=not args.no_launchctl)
                print(_json(result))
                return 0 if result.loaded or args.no_launchctl else 3
    except Exception as exc:
        print(_json({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    return 2


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--area", default="SE3")
    parser.add_argument("--db", default=str(default_db_path()))


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
