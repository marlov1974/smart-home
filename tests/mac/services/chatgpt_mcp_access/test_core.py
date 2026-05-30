import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

from src.mac.services.chatgpt_mcp_access.core import MCP_PATH, is_allowed_origin, make_handler
from src.mac.services.local_operator_bridge import TOOL_NAME


class ChatGptMcpAccessHttpTests(unittest.TestCase):
    def setUp(self):
        self.calls = []

        def bridge_handler(name, arguments):
            self.calls.append((name, arguments))
            return {"tool": name, "result": {"ok": True, "value": "ok"}}

        handler_class = make_handler(bridge_handler=bridge_handler)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler_class)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.host, self.port = self.server.server_address

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def post_json(self, payload, headers=None):
        body = json.dumps(payload).encode("utf-8")
        conn = HTTPConnection(self.host, self.port, timeout=5)
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Content-Length": str(len(body)),
        }
        if headers:
            request_headers.update(headers)
        conn.request("POST", MCP_PATH, body=body, headers=request_headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        decoded = json.loads(data.decode("utf-8")) if data else None
        return response.status, dict(response.getheaders()), decoded

    def test_origin_validation(self):
        self.assertTrue(is_allowed_origin(None))
        self.assertTrue(is_allowed_origin("http://localhost:8765"))
        self.assertTrue(is_allowed_origin("http://127.0.0.1:8765"))
        self.assertFalse(is_allowed_origin("https://example.com"))

    def test_tools_list_exposes_one_tool(self):
        status, _, payload = self.post_json({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})

        self.assertEqual(status, 200)
        tools = payload["result"]["tools"]
        self.assertEqual([TOOL_NAME], [tool["name"] for tool in tools])
        self.assertIn("inputSchema", tools[0])
        self.assertEqual([], self.calls)

    def test_tool_call_delegates_once(self):
        status, _, payload = self.post_json(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": TOOL_NAME, "arguments": {"octet": 30, "key": "hp.price.status"}},
            }
        )

        self.assertEqual(status, 200)
        self.assertFalse(payload["result"]["isError"])
        self.assertEqual([(TOOL_NAME, {"octet": 30, "key": "hp.price.status"})], self.calls)

    def test_unknown_tool_rejected_without_delegation(self):
        status, _, payload = self.post_json(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "kvs_set_by_nat_octet", "arguments": {"octet": 30, "key": "x"}},
            }
        )

        self.assertEqual(status, 200)
        self.assertIn("unknown tool", payload["error"]["message"])
        self.assertEqual([], self.calls)

    def test_extra_argument_rejected_without_delegation(self):
        status, _, payload = self.post_json(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": TOOL_NAME,
                    "arguments": {"octet": 30, "key": "x", "url": "http://example.test"},
                },
            }
        )

        self.assertEqual(status, 200)
        self.assertIn("unsupported argument", payload["error"]["message"])
        self.assertEqual([], self.calls)

    def test_notification_returns_accepted(self):
        status, _, payload = self.post_json({"jsonrpc": "2.0", "method": "notifications/initialized"})

        self.assertEqual(status, 202)
        self.assertIsNone(payload)

    def test_non_local_origin_rejected(self):
        status, _, payload = self.post_json(
            {"jsonrpc": "2.0", "id": 5, "method": "tools/list"},
            headers={"Origin": "https://example.com"},
        )

        self.assertEqual(status, 403)
        self.assertIsNone(payload)
        self.assertEqual([], self.calls)

    def test_bad_content_type_rejected(self):
        body = json.dumps({"jsonrpc": "2.0", "id": 6, "method": "tools/list"}).encode("utf-8")
        conn = HTTPConnection(self.host, self.port, timeout=5)
        conn.request(
            "POST",
            MCP_PATH,
            body=body,
            headers={"Content-Type": "text/plain", "Content-Length": str(len(body))},
        )
        response = conn.getresponse()
        data = response.read()
        conn.close()

        self.assertEqual(response.status, 400)
        self.assertIn("Content-Type", json.loads(data.decode("utf-8"))["error"]["message"])
        self.assertEqual([], self.calls)

    def test_get_mcp_returns_405(self):
        conn = HTTPConnection(self.host, self.port, timeout=5)
        conn.request("GET", MCP_PATH, headers={"Accept": "text/event-stream"})
        response = conn.getresponse()
        response.read()
        conn.close()

        self.assertEqual(response.status, 405)

    def test_unknown_path_rejected(self):
        conn = HTTPConnection(self.host, self.port, timeout=5)
        conn.request("POST", "/anything", body=b"{}", headers={"Content-Length": "2"})
        response = conn.getresponse()
        response.read()
        conn.close()

        self.assertEqual(response.status, 404)


if __name__ == "__main__":
    unittest.main()
