import ast
import json
import unittest
from pathlib import Path

from src.mac.tools.shelly_device.core import (
    HOUSE_TEMP_NAME,
    TARGET_CHANNEL_NAME,
    TARGET_DEVICE_NAME,
    TARGET_INITIAL_STATE,
    PlannedAction,
    ShellyDeviceError,
    apply_plan,
    build_plan,
    find_house_temp_component,
    normalize_base_url,
    read_device_state,
    rpc_call,
    run_apply,
    run_plan,
    validate_plan,
    verify_baseline,
    verify_target_identity,
)


class FakeResponse:
    def __init__(self, body=b""):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


class FakeOpener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, request, timeout=0):
        self.requests.append((request, timeout))
        if not self.responses:
            raise AssertionError("no fake response queued")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def rpc_response(result):
    return FakeResponse(json.dumps({"id": 1, "result": result}).encode("utf-8"))


def state_responses(*, configured=False, components=None):
    device_name = TARGET_DEVICE_NAME if configured else None
    switch_name = TARGET_CHANNEL_NAME if configured else "Switch0"
    initial_state = TARGET_INITIAL_STATE if configured else "off"
    if components is None:
        components = configured_components() if configured else []
    return [
        rpc_response(
            {
                "id": "shellypro1pm-8813bfd99f54",
                "model": "SPSW-001PE16EU",
                "app": "Pro1PM",
                "ver": "1.4.4",
            }
        ),
        rpc_response({"online": True}),
        rpc_response({"device": {"name": device_name}}),
        rpc_response({"id": 0, "name": switch_name, "initial_state": initial_state}),
        rpc_response({"id": 0, "output": False}),
        rpc_response({"components": components}),
    ]


def configured_components(component_id=200):
    return [
        {
            "key": f"number:{component_id}",
            "config": {
                "id": component_id,
                "name": HOUSE_TEMP_NAME,
                "min": 10,
                "max": 30,
                "default_value": 21,
                "persisted": True,
                "meta": {"ui": {"view": "field", "step": 0.1, "unit": "C"}},
            },
            "status": {"value": 21},
        }
    ]


def methods(opener):
    return [
        json.loads(request.data.decode("utf-8"))["method"]
        for request, _timeout in opener.requests
        if request.get_method() == "POST"
    ]


class ShellyDeviceTests(unittest.TestCase):
    def test_normalize_base_url_strips_trailing_slash(self):
        self.assertEqual("http://device", normalize_base_url("http://device/"))

        with self.assertRaisesRegex(ShellyDeviceError, "base URL"):
            normalize_base_url("")

    def test_rpc_call_posts_json_rpc_body(self):
        opener = FakeOpener([rpc_response({"ok": True})])

        result = rpc_call("http://device/", "Shelly.GetStatus", opener=opener)

        self.assertEqual({"ok": True}, result)
        request, timeout = opener.requests[0]
        self.assertEqual("http://device/rpc", request.full_url)
        self.assertEqual("POST", request.get_method())
        self.assertEqual(5.0, timeout)
        self.assertEqual({"id": 1, "method": "Shelly.GetStatus"}, json.loads(request.data.decode("utf-8")))

    def test_read_device_state_and_identity_verification(self):
        opener = FakeOpener(state_responses())

        state = read_device_state("http://device", opener=opener)

        verify_target_identity(state)
        self.assertEqual("shellypro1pm-8813bfd99f54", state.device_info["id"])
        self.assertEqual(
            [
                "Shelly.GetDeviceInfo",
                "Shelly.GetStatus",
                "Sys.GetConfig",
                "Switch.GetConfig",
                "Switch.GetStatus",
                "Shelly.GetComponents",
            ],
            methods(opener),
        )

    def test_identity_mismatch_is_rejected(self):
        responses = state_responses()
        responses[0] = rpc_response({"id": "shellypro1pm-deadbeef0000"})
        state = read_device_state("http://device", opener=FakeOpener(responses))

        with self.assertRaisesRegex(ShellyDeviceError, "identity mismatch"):
            verify_target_identity(state)

    def test_build_plan_contains_exact_baseline_actions(self):
        state = read_device_state("http://device", opener=FakeOpener(state_responses()))

        actions = build_plan(state)

        self.assertEqual(
            ["device-name", "switch-name", "switch-restore-last", "house-temp-create"],
            [action.key for action in actions],
        )
        validate_plan(actions)

    def test_build_plan_is_idempotent_when_configured(self):
        state = read_device_state("http://device", opener=FakeOpener(state_responses(configured=True)))

        self.assertEqual((), build_plan(state))
        self.assertTrue(verify_baseline(state)["verified"])

    def test_find_house_temp_rejects_duplicates_and_wrong_type(self):
        duplicate_state = read_device_state(
            "http://device",
            opener=FakeOpener(
                state_responses(
                    components=[
                        *configured_components(200),
                        *configured_components(201),
                    ]
                )
            ),
        )
        with self.assertRaisesRegex(ShellyDeviceError, "multiple House Temp"):
            find_house_temp_component(duplicate_state)

        wrong_type = read_device_state(
            "http://device",
            opener=FakeOpener(
                state_responses(
                    components=[
                        {
                            "key": "text:200",
                            "config": {"name": HOUSE_TEMP_NAME},
                        }
                    ]
                )
            ),
        )
        with self.assertRaisesRegex(ShellyDeviceError, "unsupported component type"):
            find_house_temp_component(wrong_type)

    def test_validate_plan_rejects_outside_allowlist(self):
        with self.assertRaisesRegex(ShellyDeviceError, "forbidden"):
            validate_plan([PlannedAction("bad", "Switch.Set", {"id": 0, "on": True}, "bad")])

        with self.assertRaisesRegex(ShellyDeviceError, "outside P0014"):
            validate_plan(
                [
                    PlannedAction(
                        "bad-config",
                        "Switch.SetConfig",
                        {"id": 0, "config": {"auto_off": True}},
                        "bad",
                    )
                ]
            )

    def test_apply_plan_uses_only_allowlisted_methods_and_sets_initial_house_temp(self):
        actions = (
            PlannedAction(
                "device-name",
                "Sys.SetConfig",
                {"config": {"device": {"name": TARGET_DEVICE_NAME}}},
                "test",
            ),
            PlannedAction(
                "house-temp-create",
                "Virtual.Add",
                {"type": "number", "config": {"name": HOUSE_TEMP_NAME}},
                "test",
            ),
        )
        opener = FakeOpener([rpc_response({"restart_required": False}), rpc_response({"id": 200}), rpc_response(None)])

        results = apply_plan("http://device", actions, opener=opener)

        self.assertEqual(3, len(results))
        self.assertEqual(["Sys.SetConfig", "Virtual.Add", "Number.Set"], methods(opener))
        self.assertFalse(any(method in {"Switch.Set", "Switch.Toggle"} for method in methods(opener)))

    def test_run_plan_reports_action_count(self):
        opener = FakeOpener(state_responses())

        result = run_plan("http://device", opener=opener)

        self.assertEqual("plan", result["mode"])
        self.assertEqual(4, result["action_count"])

    def test_run_apply_verifies_after_state(self):
        opener = FakeOpener(
            [
                *state_responses(),
                rpc_response({"restart_required": False}),
                rpc_response({"restart_required": False}),
                rpc_response({"restart_required": False}),
                rpc_response({"id": 200}),
                rpc_response(None),
                *state_responses(configured=True),
            ]
        )

        result = run_apply("http://device", opener=opener)

        self.assertEqual("apply", result["mode"])
        self.assertEqual(4, result["action_count"])
        self.assertTrue(result["verification"]["verified"])
        forbidden = {"Switch.Set", "Switch.Toggle", "Relay.Set", "Cover.Set"}
        self.assertFalse(any(method in forbidden for method in methods(opener)))

    def test_tool_uses_standard_library_imports_only(self):
        package_root = Path(__file__).resolve().parents[4] / "src" / "mac" / "tools" / "shelly_device"
        allowed_roots = {
            "__future__",
            "argparse",
            "dataclasses",
            "json",
            "sys",
            "typing",
            "urllib",
        }

        for path in package_root.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    imports.add(node.module.split(".")[0])
            self.assertLessEqual(imports, allowed_roots, path)


if __name__ == "__main__":
    unittest.main()
