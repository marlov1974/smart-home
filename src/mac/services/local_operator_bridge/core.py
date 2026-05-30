"""MCP-shaped read-only local operator bridge for P0026 KVS.Get."""

from __future__ import annotations

import argparse
import io
import json
import sys
from typing import Any, Callable, TextIO

from src.mac.tools.local_kvs_read import LocalKvsReadError, kvs_get_by_nat_octet


TOOL_NAME = "shelly_kvs_get_by_nat_octet"
JSONRPC_VERSION = "2.0"
ALLOWED_ARGUMENTS = frozenset({"octet", "key", "timeout"})

KvsReader = Callable[..., Any]


class BridgeError(Exception):
    """Raised when the local operator bridge rejects a request."""

    def __init__(self, message: str, code: int = -32602):
        super().__init__(message)
        self.code = code


def list_tools() -> dict[str, Any]:
    """Return the one-tool discovery response for the P0027 bridge."""

    return {
        "tools": [
            {
                "name": TOOL_NAME,
                "description": "Read one Shelly KVS key through the P0026 operator NAT helper.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "octet": {"type": "integer", "minimum": 1, "maximum": 254},
                        "key": {"type": "string", "minLength": 1},
                        "timeout": {"type": "number", "exclusiveMinimum": 0},
                    },
                    "required": ["octet", "key"],
                    "additionalProperties": False,
                },
            }
        ]
    }


def validate_tool_arguments(arguments: Any) -> dict[str, Any]:
    """Validate the bridge-level tool arguments before P0026 delegation."""

    if not isinstance(arguments, dict):
        raise BridgeError("tool arguments must be an object")
    extra = sorted(set(arguments) - ALLOWED_ARGUMENTS)
    if extra:
        raise BridgeError(f"unsupported argument(s): {', '.join(extra)}")
    if "octet" not in arguments:
        raise BridgeError("missing required argument: octet")
    if "key" not in arguments:
        raise BridgeError("missing required argument: key")
    sanitized = {"octet": arguments["octet"], "key": arguments["key"]}
    if "timeout" in arguments:
        timeout = arguments["timeout"]
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
            raise BridgeError("timeout must be a positive number")
        sanitized["timeout"] = float(timeout)
    return sanitized


def _result_to_dict(result: Any) -> dict[str, Any]:
    if hasattr(result, "to_dict"):
        value = result.to_dict()
    else:
        value = result
    if not isinstance(value, dict):
        raise BridgeError("P0026 reader returned non-object result", code=-32603)
    return value


def handle_shelly_kvs_get_by_nat_octet(
    arguments: Any,
    kvs_reader: KvsReader | None = None,
) -> dict[str, Any]:
    """Handle the single supported P0027 tool by delegating to P0026."""

    sanitized = validate_tool_arguments(arguments)
    reader = kvs_reader or kvs_get_by_nat_octet
    try:
        result = reader(**sanitized)
    except LocalKvsReadError as exc:
        raise BridgeError(str(exc)) from exc
    return _result_to_dict(result)


def handle_tool_call(
    name: Any,
    arguments: Any,
    kvs_reader: KvsReader | None = None,
) -> dict[str, Any]:
    """Route one tool call by name."""

    if name != TOOL_NAME:
        raise BridgeError(f"unknown tool: {name!r}")
    return {
        "tool": TOOL_NAME,
        "result": handle_shelly_kvs_get_by_nat_octet(arguments, kvs_reader=kvs_reader),
    }


def _json_rpc_result(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}


def _json_rpc_error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "error": {"code": code, "message": message}}


def handle_json_rpc_message(
    message: Any,
    kvs_reader: KvsReader | None = None,
) -> dict[str, Any]:
    """Process one decoded JSON-RPC-like message."""

    if not isinstance(message, dict):
        return _json_rpc_error(None, -32600, "request must be an object")
    request_id = message.get("id")
    method = message.get("method")
    if not isinstance(method, str):
        return _json_rpc_error(request_id, -32600, "method must be a string")

    try:
        if method == "tools/list":
            return _json_rpc_result(request_id, list_tools())
        if method == "tools/call":
            params = message.get("params")
            if not isinstance(params, dict):
                raise BridgeError("tools/call params must be an object")
            return _json_rpc_result(
                request_id,
                handle_tool_call(params.get("name"), params.get("arguments", {}), kvs_reader=kvs_reader),
            )
        return _json_rpc_error(request_id, -32601, f"unknown method: {method}")
    except BridgeError as exc:
        return _json_rpc_error(request_id, exc.code, str(exc))


def process_json_line(line: str, kvs_reader: KvsReader | None = None) -> str:
    """Process one newline-delimited JSON-RPC-like request line."""

    try:
        message = json.loads(line)
    except json.JSONDecodeError as exc:
        response = _json_rpc_error(None, -32700, f"parse error: {exc.msg}")
    else:
        response = handle_json_rpc_message(message, kvs_reader=kvs_reader)
    return json.dumps(response, sort_keys=True, separators=(",", ":")) + "\n"


def serve(
    input_stream: TextIO | None = None,
    output_stream: TextIO | None = None,
    kvs_reader: KvsReader | None = None,
) -> int:
    """Serve newline-delimited JSON-RPC-like requests until EOF."""

    source = input_stream or sys.stdin
    sink = output_stream or sys.stdout
    for line in source:
        if not line.strip():
            continue
        sink.write(process_json_line(line, kvs_reader=kvs_reader))
        sink.flush()
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the P0027 local operator bridge CLI."""

    parser = argparse.ArgumentParser(prog="python3 -m src.mac.services.local_operator_bridge")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("serve")
    args = parser.parse_args(argv)

    if args.command == "serve":
        return serve()
    return 1


def _serve_string(payload: str, kvs_reader: KvsReader | None = None) -> str:
    """Test helper for serving in-memory text without touching stdio."""

    output = io.StringIO()
    serve(io.StringIO(payload), output, kvs_reader=kvs_reader)
    return output.getvalue()
