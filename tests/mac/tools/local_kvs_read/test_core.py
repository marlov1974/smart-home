import json
import socket
import tempfile
import unittest
import urllib.error
from pathlib import Path

from src.mac.tools import local_kvs_read
from src.mac.tools.local_kvs_read.core import (
    KVS_GET_PATH,
    NAT_HOST,
    LocalKvsReadError,
    build_kvs_get_url,
    build_nat_base_url,
    kvs_get_by_nat_octet,
    validate_kvs_key,
    validate_octet,
)


class FakeResponse:
    def __init__(self, body=b"", status=200):
        self.body = body
        self.status = status

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


def json_response(payload, status=200):
    return FakeResponse(json.dumps(payload).encode("utf-8"), status=status)


class LocalKvsReadTests(unittest.TestCase):
    def test_build_nat_base_url_matches_documented_examples(self):
        self.assertEqual("http://192.168.86.240:8040/", build_nat_base_url(40))
        self.assertEqual("http://192.168.86.240:8030/", build_nat_base_url("30"))

    def test_validate_octet_rejects_invalid_values_before_network(self):
        invalid_values = [0, 255, -1, "", "  ", "4.0", "04x", True, False, object()]
        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(LocalKvsReadError):
                    validate_octet(value)

        opener = FakeOpener([json_response({"result": {"value": 1}})])
        with self.assertRaises(LocalKvsReadError):
            kvs_get_by_nat_octet(0, "hp.price.status", opener=opener)
        self.assertEqual([], opener.requests)

    def test_build_kvs_get_url_encodes_key_only_as_query_parameter(self):
        url = build_kvs_get_url(40, "hp.price status/a?b=c")

        self.assertEqual(
            "http://192.168.86.240:8040/rpc/KVS.Get?key=hp.price+status%2Fa%3Fb%3Dc",
            url,
        )

    def test_rejects_arbitrary_url_or_path_input(self):
        for key in [
            "http://evil.local/rpc/KVS.Set",
            "https://evil.local/rpc/KVS.Get",
            "/rpc/KVS.Get?key=hp.price.status",
            "ok./rpc/KVS.Set",
        ]:
            with self.subTest(key=key):
                with self.assertRaises(LocalKvsReadError):
                    validate_kvs_key(key)

        self.assertEqual(NAT_HOST, "192.168.86.240")
        self.assertEqual(KVS_GET_PATH, "/rpc/KVS.Get")

    def test_http_success_parses_json_result_and_writes_audit(self):
        opener = FakeOpener([json_response({"id": 1, "result": {"value": "ok"}})])
        with tempfile.TemporaryDirectory() as tempdir:
            audit_path = Path(tempdir) / "audit.jsonl"

            result = kvs_get_by_nat_octet(40, "hp.price.status", opener=opener, audit_path=audit_path)

            self.assertTrue(result.ok)
            self.assertEqual({"value": "ok"}, result.result)
            self.assertEqual(200, result.http_status)
            self.assertEqual("success", result.result_status)
            self.assertEqual(str(audit_path), result.audit_path)
            request, timeout = opener.requests[0]
            self.assertEqual("GET", request.get_method())
            self.assertEqual("http://192.168.86.240:8040/rpc/KVS.Get?key=hp.price.status", request.full_url)
            self.assertEqual(5.0, timeout)

            records = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(1, len(records))
            self.assertEqual("P0026", records[0]["package_id"])
            self.assertEqual("success", records[0]["result_status"])
            self.assertEqual("hp.price.status", records[0]["key"])

    def test_http_error_records_clear_failure_and_audit(self):
        error = urllib.error.HTTPError(
            "http://192.168.86.240:8040/rpc/KVS.Get?key=missing",
            404,
            "Not Found",
            hdrs=None,
            fp=None,
        )
        opener = FakeOpener([error])
        with tempfile.TemporaryDirectory() as tempdir:
            audit_path = Path(tempdir) / "audit.jsonl"

            result = kvs_get_by_nat_octet(40, "missing", opener=opener, audit_path=audit_path)

            self.assertFalse(result.ok)
            self.assertEqual(404, result.http_status)
            self.assertEqual("http_error", result.result_status)
            self.assertIn("HTTP 404", result.error_summary)
            self.assertIn('"result_status":"http_error"', audit_path.read_text(encoding="utf-8"))

    def test_timeout_records_clear_failure_and_audit(self):
        opener = FakeOpener([socket.timeout("timed out")])
        with tempfile.TemporaryDirectory() as tempdir:
            audit_path = Path(tempdir) / "audit.jsonl"

            result = kvs_get_by_nat_octet(40, "hp.price.status", opener=opener, audit_path=audit_path)

            self.assertFalse(result.ok)
            self.assertEqual("timeout", result.result_status)
            self.assertIn("timed out", result.error_summary)
            self.assertIn('"result_status":"timeout"', audit_path.read_text(encoding="utf-8"))

    def test_malformed_json_records_clear_failure(self):
        opener = FakeOpener([FakeResponse(b"not-json")])
        with tempfile.TemporaryDirectory() as tempdir:
            result = kvs_get_by_nat_octet(
                40,
                "hp.price.status",
                opener=opener,
                audit_path=Path(tempdir) / "audit.jsonl",
            )

        self.assertFalse(result.ok)
        self.assertEqual("json_error", result.result_status)
        self.assertEqual(200, result.http_status)

    def test_shelly_error_object_records_clear_failure(self):
        opener = FakeOpener([json_response({"id": 1, "error": {"code": -105, "message": "no such key"}})])
        with tempfile.TemporaryDirectory() as tempdir:
            result = kvs_get_by_nat_octet(
                40,
                "missing",
                opener=opener,
                audit_path=Path(tempdir) / "audit.jsonl",
            )

        self.assertFalse(result.ok)
        self.assertEqual("shelly_error", result.result_status)
        self.assertIn("no such key", result.error_summary)

    def test_write_rpcs_and_generic_proxy_operations_are_absent(self):
        forbidden_public_names = {
            "kvs_set_by_nat_octet",
            "script_start",
            "script_stop",
            "switch_set",
            "light_set",
            "cover_set",
            "fetch_url",
            "proxy",
        }

        self.assertTrue(forbidden_public_names.isdisjoint(set(local_kvs_read.__all__)))
        for name in forbidden_public_names:
            self.assertFalse(hasattr(local_kvs_read, name), name)


if __name__ == "__main__":
    unittest.main()
