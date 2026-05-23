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


ALLOWED_SCRIPT_NAME = "hello_v1_0_0"
DEFAULT_HTTP_TIMEOUT_SECONDS = 5.0
DEFAULT_LOG_TIMEOUT_SECONDS = 20.0


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
    """Reject any live-write script name outside the P0010 boundary."""

    if script_name != ALLOWED_SCRIPT_NAME:
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

    script_name = ALLOWED_SCRIPT_NAME
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
    except (OSError, ShellyLiveError) as exc:
        print(f"error: {exc}")
        return 1

    return 1
