"""Read one Shelly KVS key through the operator NAT convention."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


PACKAGE_ID = "P0026"
NAT_HOST = "192.168.86.240"
NAT_PORT_BASE = 8000
KVS_GET_PATH = "/rpc/KVS.Get"
DEFAULT_TIMEOUT_SECONDS = 5.0
DEFAULT_AUDIT_PATH = Path.home() / ".smart-home" / "local_kvs_read_audit.jsonl"

OpenUrl = Callable[..., Any]


class LocalKvsReadError(Exception):
    """Raised when P0026 local KVS input validation fails."""


@dataclass(frozen=True)
class KvsReadResult:
    """Structured result from one read-only KVS.Get attempt."""

    ok: bool
    octet: int
    key: str
    url: str
    http_status: int | None
    result_status: str
    result: Any = None
    error_summary: str | None = None
    audit_path: str | None = None
    audit_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_octet(octet: int | str) -> int:
    """Normalize and validate an internal technical-network last octet."""

    if isinstance(octet, bool):
        raise LocalKvsReadError("octet must be an integer in 1..254")
    if isinstance(octet, int):
        value = octet
    elif isinstance(octet, str):
        text = octet.strip()
        if not text or not text.isdecimal():
            raise LocalKvsReadError("octet must be an integer in 1..254")
        value = int(text, 10)
    else:
        raise LocalKvsReadError("octet must be an integer in 1..254")
    if value < 1 or value > 254:
        raise LocalKvsReadError("octet must be an integer in 1..254")
    return value


def build_nat_base_url(octet: int | str) -> str:
    """Build the fixed operator-side NAT base URL for one Shelly octet."""

    value = validate_octet(octet)
    return f"http://{NAT_HOST}:{NAT_PORT_BASE + value}/"


def validate_kvs_key(key: str) -> str:
    """Normalize and validate a KVS key without accepting endpoint overrides."""

    if not isinstance(key, str):
        raise LocalKvsReadError("key must be a non-empty string")
    value = key.strip()
    if not value:
        raise LocalKvsReadError("key must be a non-empty string")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise LocalKvsReadError("key must not contain control characters")
    lowered = value.lower()
    if "://" in value or lowered.startswith(("http:", "https:")):
        raise LocalKvsReadError("key must not be a URL")
    if value.startswith("/") or "/rpc/" in lowered:
        raise LocalKvsReadError("key must not contain a path or RPC override")
    return value


def build_kvs_get_url(octet: int | str, key: str) -> str:
    """Build the complete fixed-path KVS.Get URL with encoded key query."""

    base_url = build_nat_base_url(octet).rstrip("/")
    safe_key = validate_kvs_key(key)
    query = urllib.parse.urlencode({"key": safe_key})
    return f"{base_url}{KVS_GET_PATH}?{query}"


def _utc_timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def write_audit_record(record: Mapping[str, Any], audit_path: str | Path | None = None) -> Path:
    """Append one JSONL audit record and return the path used."""

    path = Path(audit_path).expanduser() if audit_path is not None else DEFAULT_AUDIT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")) + "\n")
    return path


def _result(
    *,
    ok: bool,
    octet: int,
    key: str,
    url: str,
    http_status: int | None,
    result_status: str,
    result: Any = None,
    error_summary: str | None = None,
) -> KvsReadResult:
    return KvsReadResult(
        ok=ok,
        octet=octet,
        key=key,
        url=url,
        http_status=http_status,
        result_status=result_status,
        result=result,
        error_summary=error_summary,
    )


def _with_audit(result: KvsReadResult, audit_path: str | Path | None) -> KvsReadResult:
    record = {
        "timestamp": _utc_timestamp(),
        "package_id": PACKAGE_ID,
        "octet": result.octet,
        "key": result.key,
        "url": result.url,
        "http_status": result.http_status,
        "result_status": result.result_status,
        "error_summary": result.error_summary,
    }
    try:
        written_path = write_audit_record(record, audit_path=audit_path)
    except OSError as exc:
        return KvsReadResult(**{**result.to_dict(), "audit_error": str(exc)})
    return KvsReadResult(**{**result.to_dict(), "audit_path": str(written_path)})


def _decode_response(raw: bytes) -> dict[str, Any]:
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LocalKvsReadError("response is not valid JSON") from exc
    if not isinstance(data, dict):
        raise LocalKvsReadError("response root is not an object")
    return data


def kvs_get_by_nat_octet(
    octet: int | str,
    key: str,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    audit_path: str | Path | None = None,
    opener: OpenUrl | None = None,
) -> KvsReadResult:
    """Perform one read-only Shelly KVS.Get through the derived NAT URL."""

    value = validate_octet(octet)
    safe_key = validate_kvs_key(key)
    url = build_kvs_get_url(value, safe_key)
    open_url = opener or urllib.request.urlopen
    request = urllib.request.Request(url, method="GET")

    try:
        with open_url(request, timeout=timeout) as response:
            raw = response.read()
            status = int(getattr(response, "status", 200))
    except urllib.error.HTTPError as exc:
        body = exc.read() if getattr(exc, "fp", None) is not None else b""
        summary = f"HTTP {exc.code}"
        if body:
            summary = f"{summary}: {body.decode('utf-8', errors='replace')[:200]}"
        return _with_audit(
            _result(
                ok=False,
                octet=value,
                key=safe_key,
                url=url,
                http_status=int(exc.code),
                result_status="http_error",
                error_summary=summary,
            ),
            audit_path,
        )
    except (TimeoutError, socket.timeout) as exc:
        return _with_audit(
            _result(
                ok=False,
                octet=value,
                key=safe_key,
                url=url,
                http_status=None,
                result_status="timeout",
                error_summary=str(exc) or "request timed out",
            ),
            audit_path,
        )
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        status = "timeout" if isinstance(reason, (TimeoutError, socket.timeout)) else "network_error"
        return _with_audit(
            _result(
                ok=False,
                octet=value,
                key=safe_key,
                url=url,
                http_status=None,
                result_status=status,
                error_summary=str(reason),
            ),
            audit_path,
        )
    except Exception as exc:  # pragma: no cover - defensive CLI diagnostics.
        return _with_audit(
            _result(
                ok=False,
                octet=value,
                key=safe_key,
                url=url,
                http_status=None,
                result_status="unexpected_error",
                error_summary=str(exc),
            ),
            audit_path,
        )

    try:
        data = _decode_response(raw)
    except LocalKvsReadError as exc:
        return _with_audit(
            _result(
                ok=False,
                octet=value,
                key=safe_key,
                url=url,
                http_status=status,
                result_status="json_error",
                error_summary=str(exc),
            ),
            audit_path,
        )

    if "error" in data:
        return _with_audit(
            _result(
                ok=False,
                octet=value,
                key=safe_key,
                url=url,
                http_status=status,
                result_status="shelly_error",
                result=data.get("error"),
                error_summary=json.dumps(data.get("error"), sort_keys=True),
            ),
            audit_path,
        )

    return _with_audit(
        _result(
            ok=True,
            octet=value,
            key=safe_key,
            url=url,
            http_status=status,
            result_status="success",
            result=data.get("result", data),
        ),
        audit_path,
    )


def main(argv: list[str] | None = None) -> int:
    """Run the P0026 local KVS read CLI."""

    parser = argparse.ArgumentParser(prog="python3 -m src.mac.tools.local_kvs_read")
    subparsers = parser.add_subparsers(dest="command", required=True)

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("--octet", required=True)
    get_parser.add_argument("--key", required=True)
    get_parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    get_parser.add_argument("--audit-path")

    args = parser.parse_args(argv)
    try:
        if args.command == "get":
            result = kvs_get_by_nat_octet(
                args.octet,
                args.key,
                timeout=args.timeout,
                audit_path=args.audit_path,
            )
        else:
            return 1
    except LocalKvsReadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0 if result.ok else 1
