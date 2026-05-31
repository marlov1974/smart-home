"""CLI for P0033 temperature-normalized spotprice foundation."""

from __future__ import annotations

import argparse
from dataclasses import asdict, is_dataclass
from datetime import date
import json
from pathlib import Path
import sys

from .core import (
    DEFAULT_PRICE_DB_PATH,
    DEFAULT_WEATHER_DB_PATH,
    build_training_foundation,
    default_feature_db_path,
    dump_p0032_location_weights,
    open_feature_database,
    summarize_temperature_normalization,
    validate_training_foundation,
)
from .launchd import install_launchd_plist


DEFAULT_START_DATE = date(2022, 5, 30)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m src.mac.services.spotprice_temperature_normalization")
    sub = parser.add_subparsers(dest="command", required=True)

    build_parser = sub.add_parser("build")
    build_parser.add_argument("--price-db", default=str(DEFAULT_PRICE_DB_PATH))
    build_parser.add_argument("--weather-db", default=str(DEFAULT_WEATHER_DB_PATH))
    build_parser.add_argument("--feature-db", default=str(default_feature_db_path()))
    build_parser.add_argument("--start-date", default=DEFAULT_START_DATE.isoformat())
    build_parser.add_argument("--end-date")

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--feature-db", default=str(default_feature_db_path()))

    diagnostics_parser = sub.add_parser("diagnostics")
    diagnostics_parser.add_argument("--feature-db", default=str(default_feature_db_path()))

    weights_parser = sub.add_parser("dump-weights")
    weights_parser.add_argument("--weather-db", default=str(DEFAULT_WEATHER_DB_PATH))

    install_parser = sub.add_parser("install-daily-job")
    install_parser.add_argument("--price-db", default=str(DEFAULT_PRICE_DB_PATH))
    install_parser.add_argument("--weather-db", default=str(DEFAULT_WEATHER_DB_PATH))
    install_parser.add_argument("--feature-db", default=str(default_feature_db_path()))
    install_parser.add_argument("--no-launchctl", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            result = build_training_foundation(
                price_db=Path(args.price_db).expanduser(),
                weather_db=Path(args.weather_db).expanduser(),
                feature_db=Path(args.feature_db).expanduser(),
                start_date=date.fromisoformat(args.start_date),
                end_date=date.fromisoformat(args.end_date) if args.end_date else None,
            )
            print(_json(result))
            return 0 if result["ok"] else 2
        if args.command == "validate":
            with open_feature_database(Path(args.feature_db).expanduser()) as conn:
                result = validate_training_foundation(conn)
            print(_json(result))
            return 0 if result["ok"] else 2
        if args.command == "diagnostics":
            with open_feature_database(Path(args.feature_db).expanduser()) as conn:
                result = summarize_temperature_normalization(conn)
            print(_json(result))
            return 0 if result["validation"]["ok"] else 2
        if args.command == "dump-weights":
            print(_json(dump_p0032_location_weights(Path(args.weather_db).expanduser())))
            return 0
        if args.command == "install-daily-job":
            result = install_launchd_plist(
                price_db=Path(args.price_db).expanduser(),
                weather_db=Path(args.weather_db).expanduser(),
                feature_db=Path(args.feature_db).expanduser(),
                run_launchctl=not args.no_launchctl,
            )
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
