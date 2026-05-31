"""CLI for P0034 normal spot ML model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .core import (
    DEFAULT_FEATURE_DB,
    build_feature_store,
    backtest_m4,
    default_model_dir,
    train_m4,
    validate_m4_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m src.mac.services.spotprice_ml_model")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("build-features-m4", "train-m4", "backtest-m4", "validate-m4"):
        item = sub.add_parser(command)
        item.add_argument("--feature-db", default=str(DEFAULT_FEATURE_DB))
        item.add_argument("--model-dir", default=str(default_model_dir()))
    args = parser.parse_args(argv)
    try:
        kwargs = {
            "feature_db": Path(args.feature_db).expanduser(),
            "model_dir": Path(args.model_dir).expanduser(),
        }
        if args.command == "build-features-m4":
            result = build_feature_store(**kwargs)
        elif args.command == "train-m4":
            result = train_m4(**kwargs)
        elif args.command == "backtest-m4":
            result = backtest_m4(**kwargs)
        elif args.command == "validate-m4":
            result = validate_m4_outputs(**kwargs)
        else:
            return 2
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0 if result.get("ok") else 2
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
