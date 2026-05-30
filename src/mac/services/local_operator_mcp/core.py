"""True MCP stdio adapter for the read-only P0027 local operator bridge."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable, TextIO

from src.mac.services.local_operator_bridge import TOOL_NAME, BridgeError, handle_tool_call, validate_tool_arguments


JSONRPC_VERSION = "2.0"
MCP_PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {
    "name": "g2-local-operator-mcp",
    "title": "G2 Local Operator MCP",
    "version": "0.1.0",
}

BridgeHandler = Callable[..., dict[str, Any]]


class McpError(Exception):
    """Raised when a P0028 MCP request should return a JSON-RPC error."""

    def __init__(self, message: str, code: int = -32602, data: Any | None = None):
        super().__init__(message)
        self.code = code
        self.data = data


def _json_rpc_result(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}


def _json_rpc_error(request_id: Any, code: int, message: str, data: Any | None = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "error": error}


def handle_initialize(params: Any) -> dict[str, Any]:
    """Return the MCP initialize result for the local operator server."""

    requested = MCP_PROTOCOL_VERSION
    if isinstance(params, dict) and isinstance(params.get("protocolVersion"), str):
        requested = params["protocolVersion"]
    protocol_version = requested if requested == MCP_PROTOCOL_VERSION else MCP_PROTOCOL_VERSION
    return {
        "protocolVersion": protocol_version,
        "capabilities": {"tools": {"listChanged": False}},
        "serverInfo": SERVER_INFO,
        "instructions": "Read-only local operator MCP server exposing one Shelly KVS.Get tool.",
    }


def handle_initialized_notification(params: Any | None = None) -> None:
    """Accept the MCP initialized notification without producing a response."""

    return None


def list_mcp_tools() -> dict[str, Any]:
    """Return MCP tool metadata using inputSchema spelling."""

    return {
        "tools": [
            {
                "name": TOOL_NAME,
                "title": "Shelly KVS Get By NAT Octet",
                "description": "Read one Shelly KVS key through the verified P0026 read-only NAT helper.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "octet": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 254,
                            "description": "Last octet of the internal 192.168.77.x Shelly IP.",
                        },
                        "key": {
                            "type": "string",
                            "minLength": 1,
                            "description": "KVS key to read with KVS.Get.",
                        },
                        "timeout": {
                            "type": "number",
                            "exclusiveMinimum": 0,
                            "description": "Optional HTTP timeout in seconds.",
                        },
                    },
                    "required": ["octet", "key"],
                    "additionalProperties": False,
                },
            }
        ]
    }


def format_mcp_tool_result(tool_payload: dict[str, Any]) -> dict[str, Any]:
    """Convert the P0027/P0026 payload to an MCP CallToolResult."""

    result = tool_payload.get("result") if isinstance(tool_payload, dict) else None
    is_error = True
    if isinstance(result, dict):
        is_error = not bool(result.get("ok"))
    text = json.dumps(tool_payload, sort_keys=True, separators=(",", ":"))
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


def call_mcp_tool(
    params: Any,
    bridge_handler: BridgeHandler | None = None,
) -> dict[str, Any]:
    """Handle MCP tools/call by delegating to P0027."""

    if not isinstance(params, dict):
        raise McpError("tools/call params must be an object")
    name = params.get("name")
    if name != TOOL_NAME:
        raise McpError(f"unknown tool: {name!r}")
    try:
        arguments = validate_tool_arguments(params.get("arguments", {}))
    except BridgeError as exc:
        raise McpError(str(exc), code=exc.code) from exc
    handler = bridge_handler or handle_tool_call
    try:
        payload = handler(name, arguments)
    except BridgeError as exc:
        raise McpError(str(exc), code=exc.code) from exc
    if not isinstance(payload, dict):
        raise McpError("bridge returned non-object payload", code=-32603)
    return format_mcp_tool_result(payload)


def handle_mcp_message(
    message: Any,
    bridge_handler: BridgeHandler | None = None,
) -> dict[str, Any] | None:
    """Process one decoded MCP JSON-RPC message."""

    if not isinstance(message, dict):
        return _json_rpc_error(None, -32600, "request must be an object")
    request_id = message.get("id")
    method = message.get("method")
    if not isinstance(method, str):
        return _json_rpc_error(request_id, -32600, "method must be a string")

    is_notification = "id" not in message
    if method == "notifications/initialized":
        handle_initialized_notification(message.get("params"))
        return None
    if is_notification:
        return None

    try:
        if method == "initialize":
            return _json_rpc_result(request_id, handle_initialize(message.get("params", {})))
        if method == "tools/list":
            return _json_rpc_result(request_id, list_mcp_tools())
        if method == "tools/call":
            return _json_rpc_result(request_id, call_mcp_tool(message.get("params"), bridge_handler=bridge_handler))
        return _json_rpc_error(request_id, -32601, f"unknown method: {method}")
    except McpError as exc:
        return _json_rpc_error(request_id, exc.code, str(exc), data=exc.data)


def process_mcp_line(
    line: str,
    bridge_handler: BridgeHandler | None = None,
) -> str | None:
    """Process one newline-delimited MCP JSON-RPC line."""

    try:
        message = json.loads(line)
    except json.JSONDecodeError as exc:
        response = _json_rpc_error(None, -32700, f"parse error: {exc.msg}")
    else:
        response = handle_mcp_message(message, bridge_handler=bridge_handler)
    if response is None:
        return None
    return json.dumps(response, sort_keys=True, separators=(",", ":")) + "\n"


def serve(
    input_stream: TextIO | None = None,
    output_stream: TextIO | None = None,
    error_stream: TextIO | None = None,
    bridge_handler: BridgeHandler | None = None,
) -> int:
    """Run the MCP stdio server loop until EOF."""

    source = input_stream or sys.stdin
    sink = output_stream or sys.stdout
    for line in source:
        if not line.strip():
            continue
        response_line = process_mcp_line(line, bridge_handler=bridge_handler)
        if response_line is not None:
            sink.write(response_line)
            sink.flush()
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the P0028 local operator MCP CLI."""

    parser = argparse.ArgumentParser(prog="python3 -m src.mac.services.local_operator_mcp")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("serve")
    args = parser.parse_args(argv)

    if args.command == "serve":
        return serve()
    return 1
