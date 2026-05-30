import io
import json
import unittest

from src.mac.services.local_operator_bridge import TOOL_NAME, BridgeError
from src.mac.services.local_operator_mcp import (
    MCP_PROTOCOL_VERSION,
    handle_initialize,
    handle_mcp_message,
    list_mcp_tools,
    process_mcp_line,
    serve,
)
from src.mac.services.local_operator_mcp.core import call_mcp_tool, format_mcp_tool_result


class FakeBridge:
    def __init__(self, *, ok=True):
        self.ok = ok
        self.calls = []

    def __call__(self, name, arguments):
        self.calls.append((name, arguments))
        if name != TOOL_NAME:
            raise BridgeError(f"unknown tool: {name!r}")
        return {
            "tool": TOOL_NAME,
            "result": {
                "ok": self.ok,
                "octet": arguments["octet"],
                "key": arguments["key"],
                "url": "http://192.168.86.240:8030/rpc/KVS.Get?key=hp.price.status",
                "http_status": 200 if self.ok else None,
                "result_status": "success" if self.ok else "network_error",
                "result": {"value": "ok"} if self.ok else None,
                "error_summary": None if self.ok else "network unavailable",
                "audit_path": "/tmp/audit.jsonl" if self.ok else None,
                "audit_error": None,
            },
        }


class LocalOperatorMcpTests(unittest.TestCase):
    def test_initialize_response_declares_tools_capability(self):
        result = handle_initialize(
            {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"},
            }
        )

        self.assertEqual(MCP_PROTOCOL_VERSION, result["protocolVersion"])
        self.assertEqual({"listChanged": False}, result["capabilities"]["tools"])
        self.assertEqual("g2-local-operator-mcp", result["serverInfo"]["name"])

    def test_initialized_notification_produces_no_response(self):
        response = handle_mcp_message({"jsonrpc": "2.0", "method": "notifications/initialized"})

        self.assertIsNone(response)

    def test_tools_list_exposes_exactly_one_mcp_tool(self):
        tools = list_mcp_tools()["tools"]

        self.assertEqual([TOOL_NAME], [tool["name"] for tool in tools])
        self.assertIn("inputSchema", tools[0])
        self.assertNotIn("input_schema", tools[0])
        self.assertFalse(tools[0]["inputSchema"]["additionalProperties"])
        self.assertEqual({"octet", "key", "timeout"}, set(tools[0]["inputSchema"]["properties"]))

    def test_tools_call_delegates_to_bridge_once(self):
        bridge = FakeBridge()

        result = call_mcp_tool(
            {"name": TOOL_NAME, "arguments": {"octet": 30, "key": "hp.price.status", "timeout": 5}},
            bridge_handler=bridge,
        )

        self.assertEqual([(TOOL_NAME, {"octet": 30, "key": "hp.price.status", "timeout": 5})], bridge.calls)
        self.assertFalse(result["isError"])
        payload = json.loads(result["content"][0]["text"])
        self.assertEqual("success", payload["result"]["result_status"])

    def test_tool_result_shape_for_delegated_failure(self):
        result = format_mcp_tool_result(
            {
                "tool": TOOL_NAME,
                "result": {
                    "ok": False,
                    "result_status": "network_error",
                    "error_summary": "network unavailable",
                },
            }
        )

        self.assertTrue(result["isError"])
        self.assertEqual("text", result["content"][0]["type"])
        self.assertIn("network_error", result["content"][0]["text"])

    def test_unknown_tools_are_rejected_without_delegating_to_p0026(self):
        bridge = FakeBridge()
        response = handle_mcp_message(
            {
                "jsonrpc": "2.0",
                "id": 9,
                "method": "tools/call",
                "params": {"name": "unknown", "arguments": {"octet": 30, "key": "hp.price.status"}},
            },
            bridge_handler=bridge,
        )

        self.assertEqual(-32602, response["error"]["code"])
        self.assertEqual([], bridge.calls)

    def test_write_like_tool_names_are_rejected(self):
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
        bridge = FakeBridge()

        for name in forbidden:
            with self.subTest(name=name):
                response = handle_mcp_message(
                    {
                        "jsonrpc": "2.0",
                        "id": name,
                        "method": "tools/call",
                        "params": {"name": name, "arguments": {"octet": 30, "key": "hp.price.status"}},
                    },
                    bridge_handler=bridge,
                )
                self.assertEqual(-32602, response["error"]["code"])

        self.assertEqual([], bridge.calls)

    def test_extra_arguments_are_rejected_before_delegation(self):
        bridge = FakeBridge()
        response = handle_mcp_message(
            {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {
                    "name": TOOL_NAME,
                    "arguments": {"octet": 30, "key": "hp.price.status", "url": "http://evil"},
                },
            },
            bridge_handler=bridge,
        )

        self.assertEqual(-32602, response["error"]["code"])
        self.assertEqual([], bridge.calls)

    def test_stdout_contains_only_mcp_messages(self):
        bridge = FakeBridge()
        source = io.StringIO(
            "\n".join(
                [
                    json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
                    json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
                    json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": 3,
                            "method": "tools/call",
                            "params": {"name": TOOL_NAME, "arguments": {"octet": 30, "key": "hp.price.status"}},
                        }
                    ),
                ]
            )
            + "\n"
        )
        output = io.StringIO()
        error = io.StringIO()

        status = serve(source, output, error, bridge_handler=bridge)

        self.assertEqual(0, status)
        self.assertEqual("", error.getvalue())
        lines = output.getvalue().splitlines()
        self.assertEqual(3, len(lines))
        for line in lines:
            self.assertEqual("2.0", json.loads(line)["jsonrpc"])

    def test_process_malformed_json_returns_parse_error(self):
        line = process_mcp_line("{not-json")
        response = json.loads(line)

        self.assertEqual(-32700, response["error"]["code"])


if __name__ == "__main__":
    unittest.main()
