"""Bounded live deploy/log verification for inert Shelly test scripts."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


HELLO_SCRIPT_NAME = "hello_v1_0_0"
SPOTPRICE_SCRIPT_NAME = "spotprice_v0_9_0"
ALLOWED_SCRIPT_NAME = HELLO_SCRIPT_NAME
ALLOWED_SCRIPT_NAMES = frozenset({HELLO_SCRIPT_NAME, SPOTPRICE_SCRIPT_NAME})
SPOTPRICE_KVS_KEYS = (
    "hp.price.2h",
    "hp.price.date",
    "hp.price.status",
    "hp.price.updated",
    "hp.price.source",
    "hp.price.debug",
    "hp.price.debug.len",
)
DEFAULT_UPLOAD_CHUNK_BYTES = 1500
DEFAULT_HTTP_TIMEOUT_SECONDS = 5.0
DEFAULT_LOG_TIMEOUT_SECONDS = 20.0
DEFAULT_KVS_TIMEOUT_SECONDS = 30.0


class ShellyLiveError(Exception):
    """Raised when live Shelly deploy or log verification fails."""


@dataclass(frozen=True)
class DeployResult:
    """Evidence returned by one live deploy/log run."""

    base_url: str
    script_name: str
    script_id: int
    before_scripts: tuple[dict[str, Any], ...]
    after_scripts: tuple[dict[str, Any], ...]
    log_excerpt: str
    cleaned_up: bool


@dataclass(frozen=True)
class SpotpriceDeployResult:
    """Evidence returned by one P0011 spotprice deploy/KVS run."""

    base_url: str
    script_name: str
    script_id: int
    before_scripts: tuple[dict[str, Any], ...]
    after_scripts: tuple[dict[str, Any], ...]
    cleaned_hello: bool
    upload_chunk_bytes: int
    upload_chunk_count: int
    log_excerpt: str
    kvs_values: dict[str, Any]
    kvs_summary: dict[str, Any]


OpenUrl = Callable[..., Any]


def normalize_base_url(base_url: str) -> str:
    """Normalize a Shelly base URL for deterministic path assembly."""

    value = str(base_url or "").strip()
    if not value:
        raise ShellyLiveError("base URL is required")
    return value.rstrip("/")


def _url(base_url: str, path: str) -> str:
    return f"{normalize_base_url(base_url)}{path}"


def rpc_call(
    base_url: str,
    method: str,
    params: dict[str, Any] | None = None,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> Any:
    """Send one Shelly JSON-RPC call and return its result."""

    payload = {"id": 1, "method": method}
    if params is not None:
        payload["params"] = params
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        _url(base_url, "/rpc"),
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    open_url = opener or urllib.request.urlopen
    try:
        with open_url(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise ShellyLiveError(f"RPC {method} failed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ShellyLiveError(f"RPC {method} returned invalid JSON") from exc

    if not isinstance(data, dict):
        raise ShellyLiveError(f"RPC {method} returned non-object response")
    if "error" in data:
        raise ShellyLiveError(f"RPC {method} returned error: {data['error']}")
    return data.get("result")


def get_status(
    base_url: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> Any:
    """Read Shelly device status."""

    return rpc_call(base_url, "Shelly.GetStatus", timeout=timeout, opener=opener)


def list_scripts(
    base_url: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> list[dict[str, Any]]:
    """Read Shelly script list."""

    result = rpc_call(base_url, "Script.List", timeout=timeout, opener=opener)
    scripts = result.get("scripts") if isinstance(result, dict) else result
    if not isinstance(scripts, list):
        raise ShellyLiveError("Script.List returned no scripts list")
    if not all(isinstance(script, dict) for script in scripts):
        raise ShellyLiveError("Script.List contains non-object script entries")
    return scripts


def find_script(scripts: list[dict[str, Any]], script_name: str) -> dict[str, Any] | None:
    """Find a script by exact name."""

    for script in scripts:
        if script.get("name") == script_name:
            return script
    return None


def ensure_allowed_script_name(script_name: str) -> None:
    """Reject any live-write script name outside the current package boundary."""

    if script_name not in ALLOWED_SCRIPT_NAMES:
        raise ShellyLiveError(f"forbidden script name: {script_name}")


def _script_id(script: dict[str, Any]) -> int:
    raw_id = script.get("id")
    if not isinstance(raw_id, int):
        raise ShellyLiveError("script entry has no numeric id")
    return raw_id


def ensure_script(
    base_url: str,
    script_name: str = ALLOWED_SCRIPT_NAME,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> int:
    """Create the allowed script if missing and return its script id."""

    ensure_allowed_script_name(script_name)
    existing = find_script(list_scripts(base_url, timeout=timeout, opener=opener), script_name)
    if existing is not None:
        return _script_id(existing)

    result = rpc_call(
        base_url,
        "Script.Create",
        {"name": script_name},
        timeout=timeout,
        opener=opener,
    )
    if not isinstance(result, dict) or not isinstance(result.get("id"), int):
        raise ShellyLiveError("Script.Create returned no numeric script id")
    return result["id"]


def put_script_code(
    base_url: str,
    script_id: int,
    script_name: str,
    code: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> Any:
    """Upload code to the allowed script slot."""

    ensure_allowed_script_name(script_name)
    return rpc_call(
        base_url,
        "Script.PutCode",
        {"id": script_id, "code": code, "append": False},
        timeout=timeout,
        opener=opener,
    )


def split_rpc_upload_chunks(code: str, upload_chunk_bytes: int = DEFAULT_UPLOAD_CHUNK_BYTES) -> list[str]:
    """Split script code into bounded in-memory RPC upload chunks."""

    if upload_chunk_bytes < 1:
        raise ShellyLiveError("upload chunk bytes must be positive")
    if code == "":
        return [""]

    chunks: list[str] = []
    current = ""
    for char in code:
        candidate = current + char
        if current and len(candidate.encode("utf-8")) > upload_chunk_bytes:
            chunks.append(current)
            current = char
        else:
            current = candidate
        if len(current.encode("utf-8")) > upload_chunk_bytes:
            raise ShellyLiveError("one character exceeds upload chunk bytes")
    if current:
        chunks.append(current)
    return chunks


def put_script_code_chunked(
    base_url: str,
    script_id: int,
    script_name: str,
    code: str,
    upload_chunk_bytes: int = DEFAULT_UPLOAD_CHUNK_BYTES,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> int:
    """Upload script code with append-based RPC chunks."""

    ensure_allowed_script_name(script_name)
    chunks = split_rpc_upload_chunks(code, upload_chunk_bytes)
    for index, chunk in enumerate(chunks):
        rpc_call(
            base_url,
            "Script.PutCode",
            {"id": script_id, "code": chunk, "append": index > 0},
            timeout=timeout,
            opener=opener,
        )
    return len(chunks)


def start_script(
    base_url: str,
    script_id: int,
    script_name: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> Any:
    """Start the allowed script."""

    ensure_allowed_script_name(script_name)
    return rpc_call(
        base_url,
        "Script.Start",
        {"id": script_id},
        timeout=timeout,
        opener=opener,
    )


def stop_script(
    base_url: str,
    script_id: int,
    script_name: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> Any:
    """Stop the allowed script."""

    ensure_allowed_script_name(script_name)
    return rpc_call(
        base_url,
        "Script.Stop",
        {"id": script_id},
        timeout=timeout,
        opener=opener,
    )


def delete_script(
    base_url: str,
    script_id: int,
    script_name: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> Any:
    """Delete the allowed script."""

    ensure_allowed_script_name(script_name)
    return rpc_call(
        base_url,
        "Script.Delete",
        {"id": script_id},
        timeout=timeout,
        opener=opener,
    )


def cleanup_hello_residue(
    base_url: str,
    scripts: list[dict[str, Any]],
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> bool:
    """Stop and delete only the P0010 hello residue script when present."""

    existing = find_script(scripts, HELLO_SCRIPT_NAME)
    if existing is None:
        return False
    script_id = _script_id(existing)
    if existing.get("running") is True:
        stop_script(base_url, script_id, HELLO_SCRIPT_NAME, timeout=timeout, opener=opener)
    delete_script(base_url, script_id, HELLO_SCRIPT_NAME, timeout=timeout, opener=opener)
    return True


def capture_debug_log(
    base_url: str,
    expected_text: str,
    log_timeout: float = DEFAULT_LOG_TIMEOUT_SECONDS,
    http_timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> str:
    """Capture bounded debug-log output until expected text is observed."""

    if not expected_text:
        raise ShellyLiveError("expected log text is required")

    deadline = time.monotonic() + log_timeout
    lines: list[str] = []
    open_url = opener or urllib.request.urlopen
    request = urllib.request.Request(_url(base_url, "/debug/log"), method="GET")
    try:
        with open_url(request, timeout=http_timeout) as response:
            while time.monotonic() < deadline:
                raw_line = response.readline()
                if raw_line == b"":
                    break
                line = raw_line.decode("utf-8", errors="replace")
                lines.append(line)
                if expected_text in line:
                    return "".join(lines)
    except urllib.error.URLError as exc:
        raise ShellyLiveError(f"debug log capture failed: {exc}") from exc

    excerpt = "".join(lines)
    raise ShellyLiveError(f"expected log text not observed: {expected_text}\n{excerpt}")


def kvs_get(
    base_url: str,
    key: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> Any:
    """Read one documented spotprice KVS key."""

    if key not in SPOTPRICE_KVS_KEYS:
        raise ShellyLiveError(f"forbidden KVS key: {key}")
    try:
        result = rpc_call(base_url, "KVS.Get", {"key": key}, timeout=timeout, opener=opener)
    except ShellyLiveError as exc:
        message = str(exc)
        if "not found" in message and "KVS.Get" in message:
            return None
        raise
    if isinstance(result, dict):
        return result.get("value")
    return None


def read_spotprice_kvs(
    base_url: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> dict[str, Any]:
    """Read all documented spotprice KVS keys."""

    return {key: kvs_get(base_url, key, timeout=timeout, opener=opener) for key in SPOTPRICE_KVS_KEYS}


def verify_spotprice_kvs(kvs_values: dict[str, Any]) -> dict[str, Any]:
    """Validate and summarize spotprice KVS output."""

    status = str(kvs_values.get("hp.price.status") or "")
    price_csv = str(kvs_values.get("hp.price.2h") or "")
    if not status:
        raise ShellyLiveError("spotprice KVS status is empty")
    parts = price_csv.split(",") if price_csv else []
    if len(parts) != 12:
        raise ShellyLiveError("spotprice KVS price series must contain 12 values")
    prices = []
    for part in parts:
        try:
            prices.append(float(part))
        except ValueError as exc:
            raise ShellyLiveError("spotprice KVS price series contains non-numeric value") from exc

    summary = {
        "status": status,
        "price_count": len(prices),
        "price_min": min(prices),
        "price_max": max(prices),
        "date": kvs_values.get("hp.price.date"),
        "updated": kvs_values.get("hp.price.updated"),
        "source": kvs_values.get("hp.price.source"),
        "debug_len": kvs_values.get("hp.price.debug.len"),
    }
    if not summary["date"] or not summary["updated"] or not summary["source"]:
        raise ShellyLiveError("spotprice KVS date, updated and source must be present")
    return summary


def wait_for_spotprice_kvs(
    base_url: str,
    kvs_timeout: float = DEFAULT_KVS_TIMEOUT_SECONDS,
    http_timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Poll spotprice KVS until it validates or timeout expires."""

    deadline = time.monotonic() + kvs_timeout
    last_error = "spotprice KVS was not read"
    values: dict[str, Any] = {}
    while time.monotonic() < deadline:
        values = read_spotprice_kvs(base_url, timeout=http_timeout, opener=opener)
        try:
            return values, verify_spotprice_kvs(values)
        except ShellyLiveError as exc:
            last_error = str(exc)
            time.sleep(0.5)
    raise ShellyLiveError(f"spotprice KVS verification timed out: {last_error}")


def deploy_hello(
    base_url: str,
    script_path: str | Path,
    expected_text: str = "hello",
    log_timeout: float = DEFAULT_LOG_TIMEOUT_SECONDS,
    http_timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    cleanup: bool = False,
    opener: OpenUrl | None = None,
) -> DeployResult:
    """Deploy, start and verify the inert P0010 hello script."""

    script_name = HELLO_SCRIPT_NAME
    code = Path(script_path).read_text(encoding="utf-8")

    get_status(base_url, timeout=http_timeout, opener=opener)
    before_scripts = tuple(list_scripts(base_url, timeout=http_timeout, opener=opener))
    existing = find_script(list(before_scripts), script_name)
    if existing is not None and existing.get("running") is True:
        stop_script(base_url, _script_id(existing), script_name, timeout=http_timeout, opener=opener)

    script_id = ensure_script(base_url, script_name, timeout=http_timeout, opener=opener)
    put_script_code(base_url, script_id, script_name, code, timeout=http_timeout, opener=opener)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        log_future = executor.submit(
            capture_debug_log,
            base_url,
            expected_text,
            log_timeout,
            http_timeout,
            opener,
        )
        time.sleep(0.05)
        start_script(base_url, script_id, script_name, timeout=http_timeout, opener=opener)
        try:
            log_excerpt = log_future.result(timeout=log_timeout + http_timeout + 1.0)
        except concurrent.futures.TimeoutError as exc:
            raise ShellyLiveError("debug log capture timed out") from exc
    stop_script(base_url, script_id, script_name, timeout=http_timeout, opener=opener)
    after_scripts = tuple(list_scripts(base_url, timeout=http_timeout, opener=opener))

    if cleanup:
        delete_script(base_url, script_id, script_name, timeout=http_timeout, opener=opener)

    return DeployResult(
        base_url=normalize_base_url(base_url),
        script_name=script_name,
        script_id=script_id,
        before_scripts=before_scripts,
        after_scripts=after_scripts,
        log_excerpt=log_excerpt,
        cleaned_up=cleanup,
    )


def deploy_spotprice(
    base_url: str,
    script_path: str | Path,
    expected_text: str = "spotprice",
    upload_chunk_bytes: int = DEFAULT_UPLOAD_CHUNK_BYTES,
    log_timeout: float = DEFAULT_LOG_TIMEOUT_SECONDS,
    kvs_timeout: float = DEFAULT_KVS_TIMEOUT_SECONDS,
    http_timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> SpotpriceDeployResult:
    """Deploy, start and verify the P0011 spotprice script."""

    if upload_chunk_bytes < 1:
        raise ShellyLiveError("upload chunk bytes must be positive")

    script_name = SPOTPRICE_SCRIPT_NAME
    code = Path(script_path).read_text(encoding="utf-8")

    get_status(base_url, timeout=http_timeout, opener=opener)
    before_scripts = tuple(list_scripts(base_url, timeout=http_timeout, opener=opener))
    cleaned_hello = cleanup_hello_residue(
        base_url,
        list(before_scripts),
        timeout=http_timeout,
        opener=opener,
    )
    scripts_after_cleanup = list_scripts(base_url, timeout=http_timeout, opener=opener)
    existing = find_script(scripts_after_cleanup, script_name)
    if existing is not None and existing.get("running") is True:
        stop_script(base_url, _script_id(existing), script_name, timeout=http_timeout, opener=opener)

    script_id = ensure_script(base_url, script_name, timeout=http_timeout, opener=opener)
    upload_chunk_count = put_script_code_chunked(
        base_url,
        script_id,
        script_name,
        code,
        upload_chunk_bytes=upload_chunk_bytes,
        timeout=http_timeout,
        opener=opener,
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        log_future = executor.submit(
            capture_debug_log,
            base_url,
            expected_text,
            log_timeout,
            http_timeout,
            opener,
        )
        time.sleep(0.05)
        start_script(base_url, script_id, script_name, timeout=http_timeout, opener=opener)
        try:
            log_excerpt = log_future.result(timeout=log_timeout + http_timeout + 1.0)
        except concurrent.futures.TimeoutError as exc:
            raise ShellyLiveError("debug log capture timed out") from exc

    kvs_values, kvs_summary = wait_for_spotprice_kvs(
        base_url,
        kvs_timeout=kvs_timeout,
        http_timeout=http_timeout,
        opener=opener,
    )
    stop_script(base_url, script_id, script_name, timeout=http_timeout, opener=opener)
    after_scripts = tuple(list_scripts(base_url, timeout=http_timeout, opener=opener))

    return SpotpriceDeployResult(
        base_url=normalize_base_url(base_url),
        script_name=script_name,
        script_id=script_id,
        before_scripts=before_scripts,
        after_scripts=after_scripts,
        cleaned_hello=cleaned_hello,
        upload_chunk_bytes=upload_chunk_bytes,
        upload_chunk_count=upload_chunk_count,
        log_excerpt=log_excerpt,
        kvs_values=kvs_values,
        kvs_summary=kvs_summary,
    )


def main(argv: list[str] | None = None) -> int:
    """Run Shelly live tooling from the command line."""

    parser = argparse.ArgumentParser(prog="python3 -m src.mac.tools.shelly_live")
    subparsers = parser.add_subparsers(dest="command", required=True)

    deploy_parser = subparsers.add_parser("deploy-hello")
    deploy_parser.add_argument("--base-url", required=True)
    deploy_parser.add_argument("--script", required=True)
    deploy_parser.add_argument("--expect", default="hello")
    deploy_parser.add_argument("--log-timeout", type=float, default=DEFAULT_LOG_TIMEOUT_SECONDS)
    deploy_parser.add_argument("--http-timeout", type=float, default=DEFAULT_HTTP_TIMEOUT_SECONDS)
    deploy_parser.add_argument("--cleanup", action="store_true")

    spot_parser = subparsers.add_parser("deploy-spotprice")
    spot_parser.add_argument("--base-url", required=True)
    spot_parser.add_argument("--script", required=True)
    spot_parser.add_argument("--expect", default="spotprice")
    spot_parser.add_argument("--upload-chunk-bytes", type=int, default=DEFAULT_UPLOAD_CHUNK_BYTES)
    spot_parser.add_argument("--log-timeout", type=float, default=DEFAULT_LOG_TIMEOUT_SECONDS)
    spot_parser.add_argument("--kvs-timeout", type=float, default=DEFAULT_KVS_TIMEOUT_SECONDS)
    spot_parser.add_argument("--http-timeout", type=float, default=DEFAULT_HTTP_TIMEOUT_SECONDS)

    args = parser.parse_args(argv)
    try:
        if args.command == "deploy-hello":
            result = deploy_hello(
                args.base_url,
                args.script,
                expected_text=args.expect,
                log_timeout=args.log_timeout,
                http_timeout=args.http_timeout,
                cleanup=args.cleanup,
            )
            print(f"target={result.base_url}")
            print(f"script={result.script_name} id={result.script_id}")
            print(f"before_scripts={json.dumps(result.before_scripts, separators=(',', ':'))}")
            print(f"after_scripts={json.dumps(result.after_scripts, separators=(',', ':'))}")
            print(f"cleaned_up={str(result.cleaned_up).lower()}")
            print("log_excerpt_begin")
            print(result.log_excerpt.rstrip("\n"))
            print("log_excerpt_end")
            return 0
        if args.command == "deploy-spotprice":
            result = deploy_spotprice(
                args.base_url,
                args.script,
                expected_text=args.expect,
                upload_chunk_bytes=args.upload_chunk_bytes,
                log_timeout=args.log_timeout,
                kvs_timeout=args.kvs_timeout,
                http_timeout=args.http_timeout,
            )
            print(f"target={result.base_url}")
            print(f"script={result.script_name} id={result.script_id}")
            print(f"cleaned_hello={str(result.cleaned_hello).lower()}")
            print(f"upload_chunk_bytes={result.upload_chunk_bytes}")
            print(f"upload_chunk_count={result.upload_chunk_count}")
            print(f"before_scripts={json.dumps(result.before_scripts, separators=(',', ':'))}")
            print(f"after_scripts={json.dumps(result.after_scripts, separators=(',', ':'))}")
            print(f"kvs_summary={json.dumps(result.kvs_summary, separators=(',', ':'), sort_keys=True)}")
            print("kvs_values_begin")
            print(json.dumps(result.kvs_values, separators=(",", ":"), sort_keys=True))
            print("kvs_values_end")
            print("log_excerpt_begin")
            print(result.log_excerpt.rstrip("\n"))
            print("log_excerpt_end")
            return 0
    except (OSError, ShellyLiveError) as exc:
        print(f"error: {exc}")
        return 1

    return 1
