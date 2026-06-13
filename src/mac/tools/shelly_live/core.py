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
WEATHER_SCRIPT_NAME = "weather_v0_9_0"
SUPPLY_UNI_PUB_SCRIPT_NAME = "supply_uni_pub"
SUPPLY_UNI_REFRESH_SCRIPT_NAME = "supply_uni_refresh"
FTX_STATE_SCRIPT_NAME = "state_v1_8_0"
ALLOWED_SCRIPT_NAME = HELLO_SCRIPT_NAME
ALLOWED_SCRIPT_NAMES = frozenset(
    {
        HELLO_SCRIPT_NAME,
        SPOTPRICE_SCRIPT_NAME,
        WEATHER_SCRIPT_NAME,
        SUPPLY_UNI_PUB_SCRIPT_NAME,
        SUPPLY_UNI_REFRESH_SCRIPT_NAME,
        FTX_STATE_SCRIPT_NAME,
    }
)
SPOTPRICE_KVS_KEYS = (
    "hp.price.2h",
    "hp.price.date",
    "hp.price.area",
    "hp.price.status",
    "hp.price.updated",
)
WEATHER_KVS_KEY = "g2.weather.act"
SUPPLY_UNI_KVS_KEY = "tele.supply_uni"
FTX_STATE_RUN_KVS_KEY = "ftx.state.run"
FTX_STATE_HIST_KVS_KEY = "ftx.state.hist"
FTX_STATE_VVX_EFFICIENCY_ID = 202
TARGET_DAMPERS_PHYSICAL_ID = "8813bfd99f54"
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
    """Evidence returned by one spotprice deploy/KVS run."""

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


@dataclass(frozen=True)
class WeatherDeployResult:
    """Evidence returned by one weather deploy/KVS run."""

    base_url: str
    live_device_id: str
    script_name: str
    script_id: int
    before_scripts: tuple[dict[str, Any], ...]
    after_scripts: tuple[dict[str, Any], ...]
    upload_chunk_bytes: int
    upload_chunk_count: int
    log_excerpt: str
    kvs_value: dict[str, Any]
    kvs_summary: dict[str, Any]


@dataclass(frozen=True)
class SupplyUniDeployResult:
    """Evidence returned by one P0016 supply UNI deploy/KVS run."""

    supply_base_url: str
    dampers_base_url: str
    supply_device_id: str
    dampers_device_id: str
    supply_status_summary: dict[str, Any]
    publisher_script_id: int
    refresher_script_id: int
    before_scripts: tuple[dict[str, Any], ...]
    after_scripts: tuple[dict[str, Any], ...]
    publisher_upload_chunk_count: int
    refresher_upload_chunk_count: int
    publisher_log_excerpt: str
    refresher_log_excerpt: str
    kvs_value: dict[str, Any]
    kvs_summary: dict[str, Any]


@dataclass(frozen=True)
class FtxStateDeployResult:
    """Evidence returned by one P0063 FTX state deploy/run."""

    base_url: str
    live_device_id: str
    script_name: str
    script_id: int
    before_scripts: tuple[dict[str, Any], ...]
    after_scripts: tuple[dict[str, Any], ...]
    upload_chunk_bytes: int
    upload_chunk_count: int
    log_excerpt: str
    zero_vvx_summary: dict[str, Any]


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


def get_device_info(
    base_url: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> dict[str, Any]:
    """Read Shelly device identity."""

    result = rpc_call(base_url, "Shelly.GetDeviceInfo", timeout=timeout, opener=opener)
    if not isinstance(result, dict):
        raise ShellyLiveError("Shelly.GetDeviceInfo returned non-object result")
    return result


def _normalized_id(value: Any) -> str:
    return "".join(char for char in str(value or "").lower() if char.isalnum())


def verify_dampers_identity(device_info: dict[str, Any]) -> str:
    """Verify that the live endpoint is the P0015 dampers target."""

    live_id = _normalized_id(device_info.get("id"))
    target_id = _normalized_id(TARGET_DAMPERS_PHYSICAL_ID)
    if not live_id.endswith(target_id):
        raise ShellyLiveError(
            f"target identity mismatch: expected {TARGET_DAMPERS_PHYSICAL_ID}, got {device_info.get('id')!r}"
        )
    return str(device_info.get("id"))


def verify_supply_identity(device_info: dict[str, Any]) -> str:
    """Verify that the endpoint looks like a Shelly supply UNI device."""

    live_id = str(device_info.get("id") or "")
    if not _normalized_id(live_id):
        raise ShellyLiveError("supply UNI identity is missing")
    return live_id


def _component(status: dict[str, Any], key: str) -> dict[str, Any] | None:
    value = status.get(key)
    return value if isinstance(value, dict) else None


def _number_from(component: dict[str, Any] | None, *names: str) -> float | None:
    if component is None:
        return None
    for name in names:
        value = component.get(name)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _round1(value: float) -> float:
    return round(float(value), 1)


def _clip(value: float, lower: float, upper: float) -> float:
    number = float(value)
    if number < lower:
        return lower
    if number > upper:
        return upper
    return number


def parse_supply_status(status: dict[str, Any]) -> dict[str, Any]:
    """Parse supply UNI local status into the P0016 telemetry shape."""

    if not isinstance(status, dict):
        raise ShellyLiveError("supply UNI status is not an object")
    pressure = _number_from(_component(status, "voltmeter:100"), "xvoltage", "value", "pa", "pressure")
    rpm = _number_from(_component(status, "input:2"), "xfreq", "value", "rpm", "frequency")
    post_vvx = _number_from(_component(status, "temperature:100"), "tC", "tc", "value", "temp")
    outdoor = _number_from(_component(status, "temperature:101"), "tC", "tc", "value", "temp")
    to_outdoor = _number_from(_component(status, "temperature:102"), "tC", "tc", "value", "temp")

    missing = []
    for name, value in (
        ("supply_pa", pressure),
        ("supply_rpm", rpm),
        ("post_vvx", post_vvx),
        ("outdoor", outdoor),
        ("to_outdoor", to_outdoor),
    ):
        if value is None:
            missing.append(name)
    if missing:
        raise ShellyLiveError(f"supply UNI status missing required values: {', '.join(missing)}")

    return {
        "supply_pa": int(round(_clip(pressure, 0, 999))),
        "outdoor": _round1(_clip(outdoor, -99.9, 99.9)),
        "post_vvx": _round1(_clip(post_vvx, -99.9, 99.9)),
        "to_outdoor": _round1(_clip(to_outdoor, -99.9, 99.9)),
        "supply_rpm": int(round(_clip(rpm, 0, 9999))),
    }


def verify_supply_snapshot(kvs_value: Any) -> dict[str, Any]:
    """Validate and summarize the P0016 supply UNI telemetry snapshot."""

    if not isinstance(kvs_value, dict):
        raise ShellyLiveError("supply UNI KVS value is not an object")
    expected_keys = {"t", "supply_pa", "outdoor", "post_vvx", "to_outdoor", "supply_rpm"}
    actual_keys = set(kvs_value)
    if actual_keys != expected_keys:
        raise ShellyLiveError(f"supply UNI KVS keys mismatch: {sorted(actual_keys)}")
    return {
        "t": int(_number_in_range(kvs_value.get("t"), 0, 4_102_444_800, "t")),
        "supply_pa": int(round(_number_in_range(kvs_value.get("supply_pa"), 0, 999, "supply_pa"))),
        "outdoor": round(_number_in_range(kvs_value.get("outdoor"), -99.9, 99.9, "outdoor"), 1),
        "post_vvx": round(_number_in_range(kvs_value.get("post_vvx"), -99.9, 99.9, "post_vvx"), 1),
        "to_outdoor": round(_number_in_range(kvs_value.get("to_outdoor"), -99.9, 99.9, "to_outdoor"), 1),
        "supply_rpm": int(round(_number_in_range(kvs_value.get("supply_rpm"), 0, 9999, "supply_rpm"))),
    }


def supply_snapshot_changed(current: dict[str, Any], previous: dict[str, Any] | None) -> bool:
    """Mirror the P0016 publisher delta thresholds for tests and review."""

    if previous is None:
        return True
    cur = verify_supply_snapshot(current)
    prev = verify_supply_snapshot(previous)
    return (
        abs(cur["supply_pa"] - prev["supply_pa"]) >= 10
        or abs(cur["outdoor"] - prev["outdoor"]) >= 1.0
        or abs(cur["post_vvx"] - prev["post_vvx"]) >= 1.0
        or abs(cur["to_outdoor"] - prev["to_outdoor"]) >= 1.0
        or abs(cur["supply_rpm"] - prev["supply_rpm"]) >= 100
    )


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


def _ftx_recipe_chunk_path(recipe_path: Path, chunk: str) -> Path:
    if not chunk.startswith("rt/"):
        raise ShellyLiveError(f"unsupported FTX recipe chunk path: {chunk}")
    return recipe_path.parent.parent / chunk[3:]


def build_ftx_recipe_script(recipe_path: str | Path) -> str:
    """Build one complete FTX runtime script from an imported G1-style recipe."""

    path = Path(recipe_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    chunks = data.get("chunks") if isinstance(data, dict) else None
    if not isinstance(chunks, list) or not all(isinstance(chunk, str) for chunk in chunks):
        raise ShellyLiveError("FTX recipe has no string chunks list")

    parts: list[str] = []
    for chunk in chunks:
        chunk_path = _ftx_recipe_chunk_path(path, chunk)
        if not chunk_path.is_file():
            raise ShellyLiveError(f"FTX recipe chunk missing: {chunk}")
        parts.append(chunk_path.read_text(encoding="utf-8").rstrip("\n"))
    return "\n".join(parts) + "\n"


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


def weather_kvs_get(
    base_url: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> Any:
    """Read the documented P0015 weather KVS key."""

    try:
        result = rpc_call(base_url, "KVS.Get", {"key": WEATHER_KVS_KEY}, timeout=timeout, opener=opener)
    except ShellyLiveError as exc:
        message = str(exc)
        if "not found" in message and "KVS.Get" in message:
            return None
        raise
    if isinstance(result, dict):
        return result.get("value")
    return None


def supply_uni_kvs_get(
    base_url: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> Any:
    """Read the documented P0016 supply UNI telemetry KVS key."""

    try:
        result = rpc_call(base_url, "KVS.Get", {"key": SUPPLY_UNI_KVS_KEY}, timeout=timeout, opener=opener)
    except ShellyLiveError as exc:
        message = str(exc)
        if "not found" in message and "KVS.Get" in message:
            return None
        raise
    if isinstance(result, dict):
        return result.get("value")
    return None


def ftx_state_kvs_get(
    base_url: str,
    key: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> Any:
    """Read one P0063-allowed FTX state KVS key."""

    if key not in (FTX_STATE_RUN_KVS_KEY, FTX_STATE_HIST_KVS_KEY):
        raise ShellyLiveError(f"forbidden FTX state KVS key: {key}")
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


def ftx_state_number_get(
    base_url: str,
    number_id: int,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> float:
    """Read one P0063-allowed FTX state virtual number."""

    if number_id != FTX_STATE_VVX_EFFICIENCY_ID:
        raise ShellyLiveError(f"forbidden FTX state number id: {number_id}")
    result = rpc_call(base_url, "Number.GetStatus", {"id": number_id}, timeout=timeout, opener=opener)
    if not isinstance(result, dict) or not isinstance(result.get("value"), (int, float)):
        raise ShellyLiveError(f"Number.GetStatus returned no numeric value for id {number_id}")
    return float(result["value"])


def verify_ftx_state_zero_vvx(
    base_url: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> dict[str, Any]:
    """Verify that stopped VVX reports zero efficiency and zero history."""

    run = ftx_state_kvs_get(base_url, FTX_STATE_RUN_KVS_KEY, timeout=timeout, opener=opener)
    if not isinstance(run, dict):
        raise ShellyLiveError("ftx.state.run is missing or not an object")
    vvx_run = int(run.get("vvx") or 0)
    if vvx_run != 0:
        raise ShellyLiveError(f"ftx.state.run.vvx is not 0: {vvx_run}")

    efficiency = ftx_state_number_get(
        base_url,
        FTX_STATE_VVX_EFFICIENCY_ID,
        timeout=timeout,
        opener=opener,
    )
    if efficiency != 0:
        raise ShellyLiveError(f"VVX efficiency is not zero: {efficiency}")

    hist = ftx_state_kvs_get(base_url, FTX_STATE_HIST_KVS_KEY, timeout=timeout, opener=opener)
    if not isinstance(hist, dict):
        raise ShellyLiveError("ftx.state.hist is missing or not an object")
    hist_summary = {name: float(hist.get(name) or 0) for name in ("r0", "r1", "r2")}
    if any(value != 0 for value in hist_summary.values()):
        raise ShellyLiveError(f"ftx.state.hist is not zeroed: {hist_summary}")

    return {
        "run_vvx": vvx_run,
        "number_202": efficiency,
        "hist": hist_summary,
    }


def read_spotprice_kvs(
    base_url: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> dict[str, Any]:
    """Read all documented spotprice KVS keys."""

    return {key: kvs_get(base_url, key, timeout=timeout, opener=opener) for key in SPOTPRICE_KVS_KEYS}


def _number_in_range(value: Any, lower: float, upper: float, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ShellyLiveError(f"weather KVS {field} is not numeric") from exc
    if number < lower or number > upper:
        raise ShellyLiveError(f"weather KVS {field} is outside range")
    return number


def verify_weather_kvs(kvs_value: Any) -> dict[str, Any]:
    """Validate and summarize P0015 weather KVS output."""

    if not isinstance(kvs_value, dict):
        raise ShellyLiveError("weather KVS value is not an object")
    solar = _number_in_range(kvs_value.get("solar_kwh_today"), 0, 999, "solar_kwh_today")
    temp_now = _number_in_range(kvs_value.get("temp_now"), -99.9, 99.9, "temp_now")
    temp_avg = _number_in_range(kvs_value.get("temp_avg_today"), -99.9, 99.9, "temp_avg_today")
    humidity = _number_in_range(kvs_value.get("humidity_avg_today"), 0, 100, "humidity_avg_today")
    return {
        "solar_kwh_today": int(round(solar)),
        "temp_now": round(temp_now, 1),
        "temp_avg_today": round(temp_avg, 1),
        "humidity_avg_today": round(humidity, 1),
    }


def verify_spotprice_kvs(kvs_values: dict[str, Any]) -> dict[str, Any]:
    """Validate and summarize spotprice KVS output."""

    status = str(kvs_values.get("hp.price.status") or "")
    area = str(kvs_values.get("hp.price.area") or "")
    price_csv = str(kvs_values.get("hp.price.2h") or "")
    if not status:
        raise ShellyLiveError("spotprice KVS status is empty")
    if status != "ok":
        raise ShellyLiveError(f"spotprice KVS status is not ok: {status}")
    if area != "SE3":
        raise ShellyLiveError(f"spotprice KVS area is not SE3: {area}")
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
        "area": area,
        "updated": kvs_values.get("hp.price.updated"),
    }
    if not summary["date"] or not summary["updated"]:
        raise ShellyLiveError("spotprice KVS date and updated must be present")
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


def wait_for_weather_kvs(
    base_url: str,
    kvs_timeout: float = DEFAULT_KVS_TIMEOUT_SECONDS,
    http_timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Poll weather KVS until it validates or timeout expires."""

    deadline = time.monotonic() + kvs_timeout
    last_error = "weather KVS was not read"
    value: Any = None
    while time.monotonic() < deadline:
        value = weather_kvs_get(base_url, timeout=http_timeout, opener=opener)
        try:
            summary = verify_weather_kvs(value)
            return value, summary
        except ShellyLiveError as exc:
            last_error = str(exc)
            time.sleep(0.5)
    raise ShellyLiveError(f"weather KVS verification timed out: {last_error}")


def wait_for_supply_uni_kvs(
    base_url: str,
    kvs_timeout: float = DEFAULT_KVS_TIMEOUT_SECONDS,
    http_timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Poll supply UNI telemetry KVS until it validates or timeout expires."""

    deadline = time.monotonic() + kvs_timeout
    last_error = "supply UNI KVS was not read"
    value: Any = None
    while time.monotonic() < deadline:
        value = supply_uni_kvs_get(base_url, timeout=http_timeout, opener=opener)
        try:
            summary = verify_supply_snapshot(value)
            return value, summary
        except ShellyLiveError as exc:
            last_error = str(exc)
            time.sleep(0.5)
    raise ShellyLiveError(f"supply UNI KVS verification timed out: {last_error}")


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
    """Deploy, start and verify the spotprice script."""

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
            kvs_values, kvs_summary = wait_for_spotprice_kvs(
                base_url,
                kvs_timeout=kvs_timeout,
                http_timeout=http_timeout,
                opener=opener,
            )
        except concurrent.futures.TimeoutError as exc:
            raise ShellyLiveError("debug log capture timed out") from exc
        finally:
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


def _ensure_no_memory_pressure(log_excerpt: str) -> None:
    lowered = log_excerpt.lower()
    for marker in ("out_of_memory", "out of memory", "oom"):
        if marker in lowered:
            raise ShellyLiveError(f"memory pressure marker observed in log: {marker}")


def deploy_weather(
    base_url: str,
    script_path: str | Path,
    expected_text: str = "weather_v0_9_0 DONE",
    upload_chunk_bytes: int = DEFAULT_UPLOAD_CHUNK_BYTES,
    log_timeout: float = DEFAULT_LOG_TIMEOUT_SECONDS,
    kvs_timeout: float = DEFAULT_KVS_TIMEOUT_SECONDS,
    http_timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> WeatherDeployResult:
    """Deploy, start and verify the P0015 weather script."""

    if upload_chunk_bytes < 1:
        raise ShellyLiveError("upload chunk bytes must be positive")

    script_name = WEATHER_SCRIPT_NAME
    code = Path(script_path).read_text(encoding="utf-8")

    device_info = get_device_info(base_url, timeout=http_timeout, opener=opener)
    live_device_id = verify_dampers_identity(device_info)
    get_status(base_url, timeout=http_timeout, opener=opener)
    before_scripts = tuple(list_scripts(base_url, timeout=http_timeout, opener=opener))
    existing = find_script(list(before_scripts), script_name)
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
            _ensure_no_memory_pressure(log_excerpt)
            kvs_value, kvs_summary = wait_for_weather_kvs(
                base_url,
                kvs_timeout=kvs_timeout,
                http_timeout=http_timeout,
                opener=opener,
            )
        except concurrent.futures.TimeoutError as exc:
            raise ShellyLiveError("debug log capture timed out") from exc
        finally:
            stop_script(base_url, script_id, script_name, timeout=http_timeout, opener=opener)
    after_scripts = tuple(list_scripts(base_url, timeout=http_timeout, opener=opener))

    return WeatherDeployResult(
        base_url=normalize_base_url(base_url),
        live_device_id=live_device_id,
        script_name=script_name,
        script_id=script_id,
        before_scripts=before_scripts,
        after_scripts=after_scripts,
        upload_chunk_bytes=upload_chunk_bytes,
        upload_chunk_count=upload_chunk_count,
        log_excerpt=log_excerpt,
        kvs_value=kvs_value,
        kvs_summary=kvs_summary,
    )


def deploy_ftx_state(
    base_url: str,
    recipe_path: str | Path,
    expected_text: str = "state DON",
    upload_chunk_bytes: int = DEFAULT_UPLOAD_CHUNK_BYTES,
    log_timeout: float = DEFAULT_LOG_TIMEOUT_SECONDS,
    http_timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> FtxStateDeployResult:
    """Deploy, start and verify the P0063 FTX state script on dampers."""

    if upload_chunk_bytes < 1:
        raise ShellyLiveError("upload chunk bytes must be positive")

    script_name = FTX_STATE_SCRIPT_NAME
    code = build_ftx_recipe_script(recipe_path)
    if "!ctx.run || !ctx.run.vvx" not in code:
        raise ShellyLiveError("FTX state script is missing VVX run guard")

    device_info = get_device_info(base_url, timeout=http_timeout, opener=opener)
    live_device_id = verify_dampers_identity(device_info)
    get_status(base_url, timeout=http_timeout, opener=opener)
    before_scripts = tuple(list_scripts(base_url, timeout=http_timeout, opener=opener))
    existing = find_script(list(before_scripts), script_name)
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
            _ensure_no_memory_pressure(log_excerpt)
            zero_vvx_summary = verify_ftx_state_zero_vvx(
                base_url,
                timeout=http_timeout,
                opener=opener,
            )
        except concurrent.futures.TimeoutError as exc:
            raise ShellyLiveError("debug log capture timed out") from exc
    after_scripts = tuple(list_scripts(base_url, timeout=http_timeout, opener=opener))

    return FtxStateDeployResult(
        base_url=normalize_base_url(base_url),
        live_device_id=live_device_id,
        script_name=script_name,
        script_id=script_id,
        before_scripts=before_scripts,
        after_scripts=after_scripts,
        upload_chunk_bytes=upload_chunk_bytes,
        upload_chunk_count=upload_chunk_count,
        log_excerpt=log_excerpt,
        zero_vvx_summary=zero_vvx_summary,
    )


def deploy_supply_uni(
    supply_base_url: str,
    dampers_base_url: str,
    publisher_script_path: str | Path,
    refresher_script_path: str | Path,
    publisher_expected_text: str = "supply_uni_pub PUB OK",
    refresher_expected_text: str = "supply_uni_refresh DONE",
    upload_chunk_bytes: int = DEFAULT_UPLOAD_CHUNK_BYTES,
    log_timeout: float = DEFAULT_LOG_TIMEOUT_SECONDS,
    kvs_timeout: float = DEFAULT_KVS_TIMEOUT_SECONDS,
    http_timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> SupplyUniDeployResult:
    """Deploy and verify the P0016 supply UNI publisher/refresher proof."""

    if upload_chunk_bytes < 1:
        raise ShellyLiveError("upload chunk bytes must be positive")

    publisher_code = Path(publisher_script_path).read_text(encoding="utf-8")
    refresher_code = Path(refresher_script_path).read_text(encoding="utf-8")

    supply_info = get_device_info(supply_base_url, timeout=http_timeout, opener=opener)
    supply_device_id = verify_supply_identity(supply_info)
    supply_status = get_status(supply_base_url, timeout=http_timeout, opener=opener)
    supply_status_summary = parse_supply_status(supply_status)

    dampers_info = get_device_info(dampers_base_url, timeout=http_timeout, opener=opener)
    dampers_device_id = verify_dampers_identity(dampers_info)
    get_status(dampers_base_url, timeout=http_timeout, opener=opener)

    before_scripts = tuple(list_scripts(supply_base_url, timeout=http_timeout, opener=opener))
    for script_name in (SUPPLY_UNI_PUB_SCRIPT_NAME, SUPPLY_UNI_REFRESH_SCRIPT_NAME):
        existing = find_script(list(before_scripts), script_name)
        if existing is not None and existing.get("running") is True:
            stop_script(supply_base_url, _script_id(existing), script_name, timeout=http_timeout, opener=opener)

    publisher_script_id = ensure_script(
        supply_base_url,
        SUPPLY_UNI_PUB_SCRIPT_NAME,
        timeout=http_timeout,
        opener=opener,
    )
    publisher_upload_chunk_count = put_script_code_chunked(
        supply_base_url,
        publisher_script_id,
        SUPPLY_UNI_PUB_SCRIPT_NAME,
        publisher_code,
        upload_chunk_bytes=upload_chunk_bytes,
        timeout=http_timeout,
        opener=opener,
    )
    refresher_script_id = ensure_script(
        supply_base_url,
        SUPPLY_UNI_REFRESH_SCRIPT_NAME,
        timeout=http_timeout,
        opener=opener,
    )
    refresher_upload_chunk_count = put_script_code_chunked(
        supply_base_url,
        refresher_script_id,
        SUPPLY_UNI_REFRESH_SCRIPT_NAME,
        refresher_code,
        upload_chunk_bytes=upload_chunk_bytes,
        timeout=http_timeout,
        opener=opener,
    )

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        log_future = executor.submit(
            capture_debug_log,
            supply_base_url,
            publisher_expected_text,
            log_timeout,
            http_timeout,
            opener,
        )
        time.sleep(0.05)
        start_script(supply_base_url, publisher_script_id, SUPPLY_UNI_PUB_SCRIPT_NAME, timeout=http_timeout, opener=opener)
        try:
            publisher_log_excerpt = log_future.result(timeout=log_timeout + http_timeout + 1.0)
            _ensure_no_memory_pressure(publisher_log_excerpt)
            kvs_value, kvs_summary = wait_for_supply_uni_kvs(
                dampers_base_url,
                kvs_timeout=kvs_timeout,
                http_timeout=http_timeout,
                opener=opener,
            )
        except concurrent.futures.TimeoutError as exc:
            raise ShellyLiveError("publisher debug log capture timed out") from exc

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        log_future = executor.submit(
            capture_debug_log,
            supply_base_url,
            refresher_expected_text,
            log_timeout,
            http_timeout,
            opener,
        )
        time.sleep(0.05)
        start_script(supply_base_url, refresher_script_id, SUPPLY_UNI_REFRESH_SCRIPT_NAME, timeout=http_timeout, opener=opener)
        try:
            refresher_log_excerpt = log_future.result(timeout=log_timeout + http_timeout + 1.0)
            _ensure_no_memory_pressure(refresher_log_excerpt)
        except concurrent.futures.TimeoutError as exc:
            raise ShellyLiveError("refresher debug log capture timed out") from exc

    after_scripts = tuple(list_scripts(supply_base_url, timeout=http_timeout, opener=opener))
    return SupplyUniDeployResult(
        supply_base_url=normalize_base_url(supply_base_url),
        dampers_base_url=normalize_base_url(dampers_base_url),
        supply_device_id=supply_device_id,
        dampers_device_id=dampers_device_id,
        supply_status_summary=supply_status_summary,
        publisher_script_id=publisher_script_id,
        refresher_script_id=refresher_script_id,
        before_scripts=before_scripts,
        after_scripts=after_scripts,
        publisher_upload_chunk_count=publisher_upload_chunk_count,
        refresher_upload_chunk_count=refresher_upload_chunk_count,
        publisher_log_excerpt=publisher_log_excerpt,
        refresher_log_excerpt=refresher_log_excerpt,
        kvs_value=kvs_value,
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

    weather_parser = subparsers.add_parser("deploy-weather")
    weather_parser.add_argument("--base-url", required=True)
    weather_parser.add_argument("--script", required=True)
    weather_parser.add_argument("--expect", default="weather_v0_9_0 DONE")
    weather_parser.add_argument("--upload-chunk-bytes", type=int, default=DEFAULT_UPLOAD_CHUNK_BYTES)
    weather_parser.add_argument("--log-timeout", type=float, default=DEFAULT_LOG_TIMEOUT_SECONDS)
    weather_parser.add_argument("--kvs-timeout", type=float, default=DEFAULT_KVS_TIMEOUT_SECONDS)
    weather_parser.add_argument("--http-timeout", type=float, default=DEFAULT_HTTP_TIMEOUT_SECONDS)

    supply_parser = subparsers.add_parser("deploy-supply-uni")
    supply_parser.add_argument("--supply-base-url", required=True)
    supply_parser.add_argument("--dampers-base-url", required=True)
    supply_parser.add_argument("--publisher-script", required=True)
    supply_parser.add_argument("--refresher-script", required=True)
    supply_parser.add_argument("--publisher-expect", default="supply_uni_pub PUB OK")
    supply_parser.add_argument("--refresher-expect", default="supply_uni_refresh DONE")
    supply_parser.add_argument("--upload-chunk-bytes", type=int, default=DEFAULT_UPLOAD_CHUNK_BYTES)
    supply_parser.add_argument("--log-timeout", type=float, default=DEFAULT_LOG_TIMEOUT_SECONDS)
    supply_parser.add_argument("--kvs-timeout", type=float, default=DEFAULT_KVS_TIMEOUT_SECONDS)
    supply_parser.add_argument("--http-timeout", type=float, default=DEFAULT_HTTP_TIMEOUT_SECONDS)

    ftx_state_parser = subparsers.add_parser("deploy-ftx-state")
    ftx_state_parser.add_argument("--base-url", required=True)
    ftx_state_parser.add_argument("--recipe", required=True)
    ftx_state_parser.add_argument("--expect", default="state DON")
    ftx_state_parser.add_argument("--upload-chunk-bytes", type=int, default=DEFAULT_UPLOAD_CHUNK_BYTES)
    ftx_state_parser.add_argument("--log-timeout", type=float, default=DEFAULT_LOG_TIMEOUT_SECONDS)
    ftx_state_parser.add_argument("--http-timeout", type=float, default=DEFAULT_HTTP_TIMEOUT_SECONDS)

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
        if args.command == "deploy-weather":
            result = deploy_weather(
                args.base_url,
                args.script,
                expected_text=args.expect,
                upload_chunk_bytes=args.upload_chunk_bytes,
                log_timeout=args.log_timeout,
                kvs_timeout=args.kvs_timeout,
                http_timeout=args.http_timeout,
            )
            print(f"target={result.base_url}")
            print(f"live_device_id={result.live_device_id}")
            print(f"script={result.script_name} id={result.script_id}")
            print(f"upload_chunk_bytes={result.upload_chunk_bytes}")
            print(f"upload_chunk_count={result.upload_chunk_count}")
            print(f"before_scripts={json.dumps(result.before_scripts, separators=(',', ':'))}")
            print(f"after_scripts={json.dumps(result.after_scripts, separators=(',', ':'))}")
            print(f"kvs_summary={json.dumps(result.kvs_summary, separators=(',', ':'), sort_keys=True)}")
            print("kvs_value_begin")
            print(json.dumps(result.kvs_value, separators=(",", ":"), sort_keys=True))
            print("kvs_value_end")
            print("log_excerpt_begin")
            print(result.log_excerpt.rstrip("\n"))
            print("log_excerpt_end")
            return 0
        if args.command == "deploy-supply-uni":
            result = deploy_supply_uni(
                args.supply_base_url,
                args.dampers_base_url,
                args.publisher_script,
                args.refresher_script,
                publisher_expected_text=args.publisher_expect,
                refresher_expected_text=args.refresher_expect,
                upload_chunk_bytes=args.upload_chunk_bytes,
                log_timeout=args.log_timeout,
                kvs_timeout=args.kvs_timeout,
                http_timeout=args.http_timeout,
            )
            print(f"supply_target={result.supply_base_url}")
            print(f"dampers_target={result.dampers_base_url}")
            print(f"supply_device_id={result.supply_device_id}")
            print(f"dampers_device_id={result.dampers_device_id}")
            print(f"supply_status_summary={json.dumps(result.supply_status_summary, separators=(',', ':'), sort_keys=True)}")
            print(f"publisher_script=supply_uni_pub id={result.publisher_script_id}")
            print(f"refresher_script=supply_uni_refresh id={result.refresher_script_id}")
            print(f"upload_chunk_bytes={args.upload_chunk_bytes}")
            print(f"publisher_upload_chunk_count={result.publisher_upload_chunk_count}")
            print(f"refresher_upload_chunk_count={result.refresher_upload_chunk_count}")
            print(f"before_scripts={json.dumps(result.before_scripts, separators=(',', ':'))}")
            print(f"after_scripts={json.dumps(result.after_scripts, separators=(',', ':'))}")
            print(f"kvs_summary={json.dumps(result.kvs_summary, separators=(',', ':'), sort_keys=True)}")
            print("kvs_value_begin")
            print(json.dumps(result.kvs_value, separators=(",", ":"), sort_keys=True))
            print("kvs_value_end")
            print("publisher_log_excerpt_begin")
            print(result.publisher_log_excerpt.rstrip("\n"))
            print("publisher_log_excerpt_end")
            print("refresher_log_excerpt_begin")
            print(result.refresher_log_excerpt.rstrip("\n"))
            print("refresher_log_excerpt_end")
            return 0
        if args.command == "deploy-ftx-state":
            result = deploy_ftx_state(
                args.base_url,
                args.recipe,
                expected_text=args.expect,
                upload_chunk_bytes=args.upload_chunk_bytes,
                log_timeout=args.log_timeout,
                http_timeout=args.http_timeout,
            )
            print(f"target={result.base_url}")
            print(f"live_device_id={result.live_device_id}")
            print(f"script={result.script_name} id={result.script_id}")
            print(f"upload_chunk_bytes={result.upload_chunk_bytes}")
            print(f"upload_chunk_count={result.upload_chunk_count}")
            print(f"before_scripts={json.dumps(result.before_scripts, separators=(',', ':'))}")
            print(f"after_scripts={json.dumps(result.after_scripts, separators=(',', ':'))}")
            print(f"zero_vvx_summary={json.dumps(result.zero_vvx_summary, separators=(',', ':'), sort_keys=True)}")
            print("log_excerpt_begin")
            print(result.log_excerpt.rstrip("\n"))
            print("log_excerpt_end")
            return 0
    except (OSError, ShellyLiveError) as exc:
        print(f"error: {exc}")
        return 1

    return 1
