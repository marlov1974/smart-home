import json
import unittest

from src.mac.services import local_operator_bridge
from src.mac.services.local_operator_bridge.core import (
    TOOL_NAME,
    BridgeError,
    handle_json_rpc_message,
    handle_shelly_kvs_get_by_nat_octet,
    handle_tool_call,
    list_tools,
    process_json_line,
    serve,
    validate_tool_arguments,
)


class FakeP0026Reader:
    def __init__(self):
        self.calls = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "ok": True,
            "octet": kwargs["octet"],
            "key": kwargs["key"],
            "url": "http://192.168.86.240:8030/rpc/KVS.Get?key=hp.price.status",
            "http_status": 200,
            "result_status": "success",
            "result": {"value": "ok"},
            "error_summary": None,
            "audit_path": "/tmp/audit.jsonl",
            "audit_error": None,
        }


class LocalOperatorBridgeTests(unittest.TestCase):
    def test_list_tools_exposes_exactly_one_tool(self):
        tools = list_tools()["tools"]

        self.assertEqual([TOOL_NAME], [tool["name"] for tool in tools])
        self.assertFalse(tools[0]["input_schema"]["additionalProperties"])

    def test_kvs_tool_delegates_to_p0026_once(self):
        reader = FakeP0026Reader()

        result = handle_shelly_kvs_get_by_nat_octet(
            {"octet": 30, "key": "hp.price.status", "timeout": 5},
            kvs_reader=reader,
        )

        self.assertEqual([{"octet": 30, "key": "hp.price.status", "timeout": 5.0}], reader.calls)
        self.assertTrue(result["ok"])
        self.assertEqual("success", result["result_status"])

    def test_unknown_tool_is_rejected_without_p0026_call(self):
        reader = FakeP0026Reader()

        with self.assertRaisesRegex(BridgeError, "unknown tool"):
            handle_tool_call("unknown", {"octet": 30, "key": "hp.price.status"}, kvs_reader=reader)

        self.assertEqual([], reader.calls)

    def test_write_like_tool_names_are_absent_and_rejected(self):
        forbidden = [
            "kvs_set_by_nat_octet",
            "script_start",
            "switch_set",
            "light_set",
            "cover_set",
            "fetch_url",
            "run_shell",
            "codex_run_package",
        ]
        public_names = set(local_operator_bridge.__all__)
        reader = FakeP0026Reader()

        for name in forbidden:
            with self.subTest(name=name):
                self.assertNotIn(name, public_names)
                with self.assertRaises(BridgeError):
                    handle_tool_call(name, {"octet": 30, "key": "hp.price.status"}, kvs_reader=reader)

        self.assertEqual([], reader.calls)

    def test_arbitrary_url_and_override_arguments_are_rejected(self):
        for field in ["url", "host", "path", "method", "shell"]:
            with self.subTest(field=field):
                with self.assertRaisesRegex(BridgeError, "unsupported argument"):
                    validate_tool_arguments({"octet": 30, "key": "hp.price.status", field: "bad"})

    def test_protocol_framing_success(self):
        reader = FakeP0026Reader()
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": TOOL_NAME,
                "arguments": {"octet": 30, "key": "hp.price.status", "timeout": 5},
            },
        }

        response = handle_json_rpc_message(request, kvs_reader=reader)

        self.assertEqual("2.0", response["jsonrpc"])
        self.assertEqual(7, response["id"])
        self.assertEqual(TOOL_NAME, response["result"]["tool"])
        self.assertEqual("success", response["result"]["result"]["result_status"])
        self.assertEqual(1, len(reader.calls))

    def test_protocol_framing_error_handling(self):
        reader = FakeP0026Reader()

        response_line = process_json_line("{not-json", kvs_reader=reader)
        response = json.loads(response_line)

        self.assertEqual(-32700, response["error"]["code"])
        self.assertEqual([], reader.calls)

    def test_tools_list_protocol_response(self):
        response = handle_json_rpc_message({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})

        self.assertEqual([TOOL_NAME], [tool["name"] for tool in response["result"]["tools"]])

    def test_serve_processes_one_line(self):
        reader = FakeP0026Reader()
        lines = []

        class Output:
            def write(self, value):
                lines.append(value)

            def flush(self):
                return None

        request = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": "abc",
                "method": "tools/call",
                "params": {"name": TOOL_NAME, "arguments": {"octet": 30, "key": "hp.price.status"}},
            }
        )

        status = serve([request + "\n"], Output(), kvs_reader=reader)

        self.assertEqual(0, status)
        self.assertEqual("abc", json.loads(lines[0])["id"])
        self.assertEqual(1, len(reader.calls))


if __name__ == "__main__":
    unittest.main()
