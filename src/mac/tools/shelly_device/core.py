"""P0014 dampers device-management plan/apply/verify tooling."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable


PACKAGE_ID = "P0014"
TARGET_ROLE = "ftx-dampers"
TARGET_PHYSICAL_ID = "8813bfd99f54"
TARGET_STABLE_LAN = "192.168.77.30"
TARGET_DEVICE_NAME = "ftx_dampers"
TARGET_SWITCH_ID = 0
TARGET_CHANNEL_NAME = "dampers"
TARGET_INITIAL_STATE = "restore_last"
HOUSE_TEMP_NAME = "House Temp"
HOUSE_TEMP_VALUE = 21
HOUSE_TEMP_MIN = 10
HOUSE_TEMP_MAX = 30
HOUSE_TEMP_UNIT = "C"
HOUSE_TEMP_STEP = 0.1
DEFAULT_HTTP_TIMEOUT_SECONDS = 5.0

ALLOWED_WRITE_METHODS = frozenset(
    {
        "Sys.SetConfig",
        "Switch.SetConfig",
        "Virtual.Add",
        "Number.SetConfig",
        "Number.Set",
    }
)
FORBIDDEN_METHOD_PREFIXES = (
    "Switch.Set",
    "Switch.Toggle",
    "Relay.",
    "Cover.",
    "Light.Set",
    "RGB.Set",
    "RGBW.Set",
)


class ShellyDeviceError(Exception):
    """Raised when P0014 device management cannot continue safely."""


@dataclass(frozen=True)
class DeviceState:
    """P0014-relevant live device state."""

    base_url: str
    device_info: dict[str, Any]
    status: dict[str, Any]
    sys_config: dict[str, Any]
    switch_config: dict[str, Any]
    switch_status: dict[str, Any]
    components: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class PlannedAction:
    """One allowlisted P0014 configuration action."""

    key: str
    method: str
    params: dict[str, Any]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "method": self.method,
            "params": self.params,
            "reason": self.reason,
        }


OpenUrl = Callable[..., Any]


def normalize_base_url(base_url: str) -> str:
    """Normalize a Shelly base URL for deterministic path assembly."""

    value = str(base_url or "").strip()
    if not value:
        raise ShellyDeviceError("base URL is required")
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
        raise ShellyDeviceError(f"RPC {method} failed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ShellyDeviceError(f"RPC {method} returned invalid JSON") from exc

    if not isinstance(data, dict):
        raise ShellyDeviceError(f"RPC {method} returned non-object response")
    if "error" in data:
        raise ShellyDeviceError(f"RPC {method} returned error: {data['error']}")
    return data.get("result")


def _dict_result(method: str, result: Any) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise ShellyDeviceError(f"RPC {method} returned non-object result")
    return result


def _component_list(result: Any) -> tuple[dict[str, Any], ...]:
    components = result.get("components") if isinstance(result, dict) else result
    if components is None:
        components = []
    if not isinstance(components, list):
        raise ShellyDeviceError("Shelly.GetComponents returned no component list")
    if not all(isinstance(component, dict) for component in components):
        raise ShellyDeviceError("Shelly.GetComponents contains non-object entries")
    return tuple(components)


def read_device_state(
    base_url: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> DeviceState:
    """Gather the live state needed by P0014."""

    normalized = normalize_base_url(base_url)
    device_info = _dict_result(
        "Shelly.GetDeviceInfo",
        rpc_call(normalized, "Shelly.GetDeviceInfo", timeout=timeout, opener=opener),
    )
    status = _dict_result(
        "Shelly.GetStatus",
        rpc_call(normalized, "Shelly.GetStatus", timeout=timeout, opener=opener),
    )
    sys_config = _dict_result(
        "Sys.GetConfig",
        rpc_call(normalized, "Sys.GetConfig", timeout=timeout, opener=opener),
    )
    switch_config = _dict_result(
        "Switch.GetConfig",
        rpc_call(
            normalized,
            "Switch.GetConfig",
            {"id": TARGET_SWITCH_ID},
            timeout=timeout,
            opener=opener,
        ),
    )
    switch_status = _dict_result(
        "Switch.GetStatus",
        rpc_call(
            normalized,
            "Switch.GetStatus",
            {"id": TARGET_SWITCH_ID},
            timeout=timeout,
            opener=opener,
        ),
    )
    components = _component_list(
        rpc_call(
            normalized,
            "Shelly.GetComponents",
            {"include": ["config", "status"]},
            timeout=timeout,
            opener=opener,
        )
    )
    return DeviceState(
        base_url=normalized,
        device_info=device_info,
        status=status,
        sys_config=sys_config,
        switch_config=switch_config,
        switch_status=switch_status,
        components=components,
    )


def _normalized_id(value: Any) -> str:
    return "".join(char for char in str(value or "").lower() if char.isalnum())


def verify_target_identity(state: DeviceState) -> None:
    """Confirm that the reached endpoint is the intended dampers device."""

    live_id = _normalized_id(state.device_info.get("id"))
    target = _normalized_id(TARGET_PHYSICAL_ID)
    if not live_id.endswith(target):
        raise ShellyDeviceError(
            f"target identity mismatch: expected {TARGET_PHYSICAL_ID}, got {state.device_info.get('id')!r}"
        )


def _component_key(component: dict[str, Any]) -> str:
    raw = component.get("key")
    if isinstance(raw, str):
        return raw
    component_type = component.get("type")
    component_id = component.get("id")
    if isinstance(component_type, str) and isinstance(component_id, int):
        return f"{component_type}:{component_id}"
    return ""


def _component_config(component: dict[str, Any]) -> dict[str, Any]:
    config = component.get("config")
    if isinstance(config, dict):
        return config
    return component


def _component_name(component: dict[str, Any]) -> str | None:
    name = _component_config(component).get("name")
    return name if isinstance(name, str) else None


def find_house_temp_component(state: DeviceState) -> int | None:
    """Find the unique House Temp virtual number component."""

    matches = [component for component in state.components if _component_name(component) == HOUSE_TEMP_NAME]
    if not matches:
        return None
    if len(matches) > 1:
        raise ShellyDeviceError("multiple House Temp components found")
    key = _component_key(matches[0])
    if not key.startswith("number:"):
        raise ShellyDeviceError(f"House Temp exists with unsupported component type: {key or 'unknown'}")
    raw_id = key.split(":", 1)[1]
    try:
        return int(raw_id)
    except ValueError as exc:
        raise ShellyDeviceError(f"House Temp component id is not numeric: {key}") from exc


def _house_temp_config() -> dict[str, Any]:
    return {
        "name": HOUSE_TEMP_NAME,
        "min": HOUSE_TEMP_MIN,
        "max": HOUSE_TEMP_MAX,
        "default_value": HOUSE_TEMP_VALUE,
        "persisted": True,
        "meta": {
            "ui": {
                "view": "field",
                "step": HOUSE_TEMP_STEP,
                "unit": HOUSE_TEMP_UNIT,
            }
        },
    }


def _component_by_number_id(state: DeviceState, component_id: int) -> dict[str, Any] | None:
    key = f"number:{component_id}"
    for component in state.components:
        if _component_key(component) == key:
            return component
    return None


def _needs_house_temp_config(state: DeviceState, component_id: int) -> bool:
    component = _component_by_number_id(state, component_id)
    if component is None:
        return True
    config = _component_config(component)
    target = _house_temp_config()
    ui = config.get("meta", {}).get("ui", {}) if isinstance(config.get("meta"), dict) else {}
    return any(
        (
            config.get("name") != target["name"],
            config.get("min") != target["min"],
            config.get("max") != target["max"],
            config.get("default_value") != target["default_value"],
            config.get("persisted") is not True,
            ui.get("unit") != HOUSE_TEMP_UNIT,
            ui.get("step") != HOUSE_TEMP_STEP,
        )
    )


def build_plan(state: DeviceState) -> tuple[PlannedAction, ...]:
    """Build the P0014 baseline plan from current state."""

    verify_target_identity(state)
    actions: list[PlannedAction] = []
    device_config = state.sys_config.get("device", {})
    if not isinstance(device_config, dict):
        raise ShellyDeviceError("Sys.GetConfig returned no device config")
    if device_config.get("name") != TARGET_DEVICE_NAME:
        actions.append(
            PlannedAction(
                key="device-name",
                method="Sys.SetConfig",
                params={"config": {"device": {"name": TARGET_DEVICE_NAME}}},
                reason="set P0014 dampers device display name",
            )
        )
    if state.switch_config.get("name") != TARGET_CHANNEL_NAME:
        actions.append(
            PlannedAction(
                key="switch-name",
                method="Switch.SetConfig",
                params={"id": TARGET_SWITCH_ID, "config": {"name": TARGET_CHANNEL_NAME}},
                reason="set P0014 dampers switch channel name",
            )
        )
    if state.switch_config.get("initial_state") != TARGET_INITIAL_STATE:
        actions.append(
            PlannedAction(
                key="switch-restore-last",
                method="Switch.SetConfig",
                params={"id": TARGET_SWITCH_ID, "config": {"initial_state": TARGET_INITIAL_STATE}},
                reason="enable restore output state after reboot",
            )
        )

    house_temp_id = find_house_temp_component(state)
    if house_temp_id is None:
        actions.append(
            PlannedAction(
                key="house-temp-create",
                method="Virtual.Add",
                params={"type": "number", "config": _house_temp_config()},
                reason="create P0014 non-actuating House Temp number component",
            )
        )
    elif _needs_house_temp_config(state, house_temp_id):
        actions.append(
            PlannedAction(
                key="house-temp-config",
                method="Number.SetConfig",
                params={"id": house_temp_id, "config": _house_temp_config()},
                reason="align P0014 House Temp number component config",
            )
        )
    return tuple(actions)


def validate_plan(actions: tuple[PlannedAction, ...] | list[PlannedAction]) -> None:
    """Reject any write outside the P0014 allowlist."""

    for action in actions:
        if action.method not in ALLOWED_WRITE_METHODS:
            raise ShellyDeviceError(f"forbidden write method: {action.method}")
        if action.method in {"Switch.Set", "Switch.Toggle"}:
            raise ShellyDeviceError(f"forbidden actuator method: {action.method}")
        for prefix in FORBIDDEN_METHOD_PREFIXES:
            if action.method.startswith(prefix) and action.method != "Switch.SetConfig":
                raise ShellyDeviceError(f"forbidden actuator method: {action.method}")
        if action.method == "Switch.SetConfig" and action.params.get("id") != TARGET_SWITCH_ID:
            raise ShellyDeviceError("Switch.SetConfig outside switch id 0 is forbidden")
        if action.method == "Sys.SetConfig" and action.params != {
            "config": {"device": {"name": TARGET_DEVICE_NAME}}
        }:
            raise ShellyDeviceError("Sys.SetConfig payload is outside P0014 baseline")
        if action.method == "Switch.SetConfig":
            config = action.params.get("config")
            if config not in ({"name": TARGET_CHANNEL_NAME}, {"initial_state": TARGET_INITIAL_STATE}):
                raise ShellyDeviceError("Switch.SetConfig payload is outside P0014 baseline")


def apply_plan(
    base_url: str,
    actions: tuple[PlannedAction, ...] | list[PlannedAction],
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> list[dict[str, Any]]:
    """Execute allowlisted P0014 actions."""

    validate_plan(actions)
    results: list[dict[str, Any]] = []
    for action in actions:
        result = rpc_call(base_url, action.method, action.params, timeout=timeout, opener=opener)
        results.append({"action": action.to_dict(), "result": result})
        if action.key == "house-temp-create":
            if not isinstance(result, dict) or not isinstance(result.get("id"), int):
                raise ShellyDeviceError("Virtual.Add returned no numeric number component id")
            set_result = rpc_call(
                base_url,
                "Number.Set",
                {"id": result["id"], "value": HOUSE_TEMP_VALUE},
                timeout=timeout,
                opener=opener,
            )
            results.append(
                {
                    "action": PlannedAction(
                        key="house-temp-initial-value",
                        method="Number.Set",
                        params={"id": result["id"], "value": HOUSE_TEMP_VALUE},
                        reason="set neutral initial House Temp value after creation",
                    ).to_dict(),
                    "result": set_result,
                }
            )
    return results


def verify_baseline(state: DeviceState) -> dict[str, Any]:
    """Verify that live readback matches the P0014 baseline."""

    verify_target_identity(state)
    device_config = state.sys_config.get("device", {})
    if not isinstance(device_config, dict) or device_config.get("name") != TARGET_DEVICE_NAME:
        raise ShellyDeviceError("device name baseline is not verified")
    if state.switch_config.get("name") != TARGET_CHANNEL_NAME:
        raise ShellyDeviceError("switch channel name baseline is not verified")
    if state.switch_config.get("initial_state") != TARGET_INITIAL_STATE:
        raise ShellyDeviceError("switch restore-output baseline is not verified")
    house_temp_id = find_house_temp_component(state)
    if house_temp_id is None:
        raise ShellyDeviceError("House Temp number component is not verified")
    if _needs_house_temp_config(state, house_temp_id):
        raise ShellyDeviceError("House Temp number component config is not verified")
    return state_summary(state) | {"verified": True, "house_temp_id": house_temp_id}


def state_summary(state: DeviceState) -> dict[str, Any]:
    """Return compact evidence for the P0014-relevant state."""

    house_temp_id = find_house_temp_component(state)
    return {
        "package": PACKAGE_ID,
        "base_url": state.base_url,
        "target_role": TARGET_ROLE,
        "stable_lan_address": TARGET_STABLE_LAN,
        "target_physical_id": TARGET_PHYSICAL_ID,
        "live_device_id": state.device_info.get("id"),
        "model": state.device_info.get("model"),
        "app": state.device_info.get("app"),
        "fw_version": state.device_info.get("ver"),
        "device_name": state.sys_config.get("device", {}).get("name")
        if isinstance(state.sys_config.get("device"), dict)
        else None,
        "switch_id": TARGET_SWITCH_ID,
        "switch_name": state.switch_config.get("name"),
        "switch_initial_state": state.switch_config.get("initial_state"),
        "switch_output_observed_only": state.switch_status.get("output"),
        "house_temp_id": house_temp_id,
        "component_count": len(state.components),
    }


def run_plan(
    base_url: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> dict[str, Any]:
    """Read state and return the current P0014 plan."""

    before = read_device_state(base_url, timeout=timeout, opener=opener)
    actions = build_plan(before)
    validate_plan(actions)
    return {
        "mode": "plan",
        "summary": state_summary(before),
        "actions": [action.to_dict() for action in actions],
        "action_count": len(actions),
    }


def run_apply(
    base_url: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> dict[str, Any]:
    """Apply the P0014 baseline and verify readback."""

    before = read_device_state(base_url, timeout=timeout, opener=opener)
    actions = build_plan(before)
    validate_plan(actions)
    results = apply_plan(before.base_url, actions, timeout=timeout, opener=opener)
    after = read_device_state(before.base_url, timeout=timeout, opener=opener)
    verification = verify_baseline(after)
    return {
        "mode": "apply",
        "before": state_summary(before),
        "actions": [action.to_dict() for action in actions],
        "action_count": len(actions),
        "results": results,
        "after": state_summary(after),
        "verification": verification,
    }


def run_verify(
    base_url: str,
    timeout: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    opener: OpenUrl | None = None,
) -> dict[str, Any]:
    """Verify the P0014 baseline without writing."""

    state = read_device_state(base_url, timeout=timeout, opener=opener)
    return {"mode": "verify", "verification": verify_baseline(state)}


def main(argv: list[str] | None = None) -> int:
    """Run P0014 device-management tooling from the command line."""

    parser = argparse.ArgumentParser(prog="python3 -m src.mac.tools.shelly_device")
    parser.add_argument("command", choices=("plan", "apply", "verify"))
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--http-timeout", type=float, default=DEFAULT_HTTP_TIMEOUT_SECONDS)
    args = parser.parse_args(argv)

    try:
        if args.command == "plan":
            result = run_plan(args.base_url, timeout=args.http_timeout)
        elif args.command == "apply":
            result = run_apply(args.base_url, timeout=args.http_timeout)
        else:
            result = run_verify(args.base_url, timeout=args.http_timeout)
    except ShellyDeviceError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0
