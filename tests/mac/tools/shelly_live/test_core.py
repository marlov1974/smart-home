import ast
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src.mac.tools.shelly_live.core import (
    ALLOWED_SCRIPT_NAME,
    ShellyLiveError,
    capture_debug_log,
    deploy_hello,
    ensure_allowed_script_name,
    ensure_script,
    find_script,
    normalize_base_url,
    put_script_code,
    rpc_call,
)


class FakeResponse:
    def __init__(self, body=b"", lines=None):
        self.body = body
        self.lines = list(lines or [])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body

    def readline(self):
        if self.lines:
            return self.lines.pop(0)
        return b""


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


class ShellyLiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.script_path = self.tmp / "hello_v1_0_0.js"
        self.script_path.write_text('print("hello world");\n', encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_normalize_base_url_strips_trailing_slash(self):
        self.assertEqual("http://device", normalize_base_url("http://device/"))

    def test_rpc_call_posts_json_rpc_body(self):
        opener = FakeOpener([rpc_response({"ok": True})])

        result = rpc_call("http://device/", "Script.List", opener=opener)

        self.assertEqual({"ok": True}, result)
        request, timeout = opener.requests[0]
        self.assertEqual("http://device/rpc", request.full_url)
        self.assertEqual("POST", request.get_method())
        self.assertEqual(5.0, timeout)
        self.assertEqual({"id": 1, "method": "Script.List"}, json.loads(request.data.decode("utf-8")))

    def test_rpc_call_raises_for_rpc_error(self):
        opener = FakeOpener([FakeResponse(b'{"id":1,"error":{"code":-1,"message":"bad"}}')])

        with self.assertRaisesRegex(ShellyLiveError, "returned error"):
            rpc_call("http://device", "Script.List", opener=opener)

    def test_find_script_matches_exact_name(self):
        scripts = [{"id": 1, "name": "other"}, {"id": 2, "name": ALLOWED_SCRIPT_NAME}]

        self.assertEqual({"id": 2, "name": ALLOWED_SCRIPT_NAME}, find_script(scripts, ALLOWED_SCRIPT_NAME))
        self.assertIsNone(find_script(scripts, "missing"))

    def test_forbidden_script_name_is_rejected(self):
        ensure_allowed_script_name(ALLOWED_SCRIPT_NAME)

        with self.assertRaisesRegex(ShellyLiveError, "forbidden script name"):
            ensure_allowed_script_name("g2-hello")

    def test_ensure_script_reuses_existing_allowed_script(self):
        opener = FakeOpener([rpc_response({"scripts": [{"id": 7, "name": ALLOWED_SCRIPT_NAME}]})])

        self.assertEqual(7, ensure_script("http://device", opener=opener))
        self.assertEqual(1, len(opener.requests))

    def test_ensure_script_creates_missing_allowed_script(self):
        opener = FakeOpener([rpc_response({"scripts": []}), rpc_response({"id": 8})])

        self.assertEqual(8, ensure_script("http://device", opener=opener))
        body = json.loads(opener.requests[1][0].data.decode("utf-8"))
        self.assertEqual("Script.Create", body["method"])
        self.assertEqual({"name": ALLOWED_SCRIPT_NAME}, body["params"])

    def test_put_script_code_uses_only_script_rpc(self):
        opener = FakeOpener([rpc_response({})])

        put_script_code("http://device", 9, ALLOWED_SCRIPT_NAME, "print(1);", opener=opener)

        body = json.loads(opener.requests[0][0].data.decode("utf-8"))
        self.assertEqual("Script.PutCode", body["method"])
        self.assertEqual({"id": 9, "code": "print(1);", "append": False}, body["params"])

    def test_capture_debug_log_stops_when_expected_text_appears(self):
        opener = FakeOpener([FakeResponse(lines=[b"boot\n", b"hello world\n"])])

        excerpt = capture_debug_log("http://device", "hello", opener=opener)

        self.assertIn("hello world", excerpt)
        self.assertEqual("http://device/debug/log", opener.requests[0][0].full_url)

    def test_deploy_hello_orchestrates_allowed_rpc_sequence(self):
        opener = FakeOpener(
            [
                rpc_response({"online": True}),
                rpc_response({"scripts": []}),
                rpc_response({"scripts": []}),
                rpc_response({"id": 3}),
                rpc_response({}),
                FakeResponse(lines=[b"hello world\n"]),
                rpc_response({}),
                rpc_response({}),
                rpc_response({"scripts": [{"id": 3, "name": ALLOWED_SCRIPT_NAME, "running": False}]}),
            ]
        )

        result = deploy_hello("http://device", self.script_path, opener=opener)

        self.assertEqual(ALLOWED_SCRIPT_NAME, result.script_name)
        methods = [
            json.loads(request.data.decode("utf-8"))["method"]
            for request, _timeout in opener.requests
            if request.get_method() == "POST"
        ]
        self.assertEqual(
            [
                "Shelly.GetStatus",
                "Script.List",
                "Script.List",
                "Script.Create",
                "Script.PutCode",
                "Script.Start",
                "Script.Stop",
                "Script.List",
            ],
            methods,
        )
        forbidden_fragments = ("Switch.", "Relay.", "Cover.", "KVS.", "Wifi.", "Mqtt.", "Bluetooth.")
        self.assertFalse(any(any(fragment in method for fragment in forbidden_fragments) for method in methods))

    def test_tool_uses_standard_library_imports_only(self):
        package_root = Path(__file__).resolve().parents[4] / "src" / "mac" / "tools" / "shelly_live"
        allowed_roots = {
            "__future__",
            "argparse",
            "concurrent",
            "dataclasses",
            "json",
            "pathlib",
            "time",
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
