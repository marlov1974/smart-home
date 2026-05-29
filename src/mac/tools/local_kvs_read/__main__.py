"""Command-line entry point for read-only local Shelly KVS.Get tooling."""

from .core import main

if __name__ == "__main__":
    raise SystemExit(main())
