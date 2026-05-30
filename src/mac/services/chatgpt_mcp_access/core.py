"""Streamable HTTP MCP wrapper for the P0028 read-only local operator tool."""

from __future__ import annotations

import argparse
import json
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from src.mac.services.local_operator_mcp.core import (
    JSONRPC_VERSION,
    MCP_PROTOCOL_VERSION,
    BridgeHandler,
    handle_mcp_message,
)


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MCP_PATH = "/mcp"
SERVER_NAME = "g2-chatgpt-mcp-access"
LOCAL_ORIGIN_HOSTS = frozenset({"localhost", "127.0.0.1", "[::1]", "::1"})


def is_allowed_origin(origin: str | None) -> bool:
    """Return whether an HTTP Origin is safe for the localhost wrapper."""

    if not origin:
        return True
    parsed = urlparse(origin)
    return parsed.scheme in {"http", "https"} and parsed.hostname in {"localhost", "127.0.0.1", "::1"}


def json_response_bytes(payload: dict[str, Any]) -> bytes:
    """Serialize an MCP/JSON-RPC payload for HTTP response bodies."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _json_rpc_error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "error": {"code": code, "message": message}}


def handle_http_mcp_message(
    message: Any,
    bridge_handler: BridgeHandler | None = None,
) -> dict[str, Any] | None:
    """Delegate one Streamable HTTP JSON-RPC message to the P0028 MCP core."""

    return handle_mcp_message(message, bridge_handler=bridge_handler)


def make_handler(bridge_handler: BridgeHandler | None = None) -> type[BaseHTTPRequestHandler]:
    """Create a request handler class for the package-scoped MCP HTTP endpoint."""

    class ChatGptMcpAccessHandler(BaseHTTPRequestHandler):
        server_version = SERVER_NAME

        def log_message(self, format: str, *args: Any) -> None:
            print(f"{self.address_string()} - {format % args}", file=sys.stderr)

        def _send_empty(self, status: HTTPStatus, allow: str | None = None) -> None:
            self.send_response(status)
            if allow:
                self.send_header("Allow", allow)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
            body = json_response_bytes(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("MCP-Protocol-Version", MCP_PROTOCOL_VERSION)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _reject_if_bad_origin(self) -> bool:
            origin = self.headers.get("Origin")
            if is_allowed_origin(origin):
                return False
            self._send_empty(HTTPStatus.FORBIDDEN)
            return True

        def do_GET(self) -> None:
            if self.path != MCP_PATH:
                self._send_empty(HTTPStatus.NOT_FOUND)
                return
            if self._reject_if_bad_origin():
                return
            self._send_empty(HTTPStatus.METHOD_NOT_ALLOWED, allow="POST, GET")

        def do_DELETE(self) -> None:
            if self.path != MCP_PATH:
                self._send_empty(HTTPStatus.NOT_FOUND)
                return
            self._send_empty(HTTPStatus.METHOD_NOT_ALLOWED, allow="POST, GET")

        def do_POST(self) -> None:
            if self.path != MCP_PATH:
                self._send_empty(HTTPStatus.NOT_FOUND)
                return
            if self._reject_if_bad_origin():
                return
            content_type = self.headers.get("Content-Type", "")
            if content_type.split(";", 1)[0].strip().lower() != "application/json":
                self._send_json(HTTPStatus.BAD_REQUEST, _json_rpc_error(None, -32600, "Content-Type must be application/json"))
                return

            content_length = self.headers.get("Content-Length")
            if content_length is None:
                self._send_json(HTTPStatus.BAD_REQUEST, _json_rpc_error(None, -32600, "missing Content-Length"))
                return
            try:
                length = int(content_length)
            except ValueError:
                self._send_json(HTTPStatus.BAD_REQUEST, _json_rpc_error(None, -32600, "invalid Content-Length"))
                return
            if length <= 0 or length > 65536:
                self._send_json(HTTPStatus.BAD_REQUEST, _json_rpc_error(None, -32600, "invalid body length"))
                return

            raw = self.rfile.read(length)
            try:
                message = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, _json_rpc_error(None, -32700, f"parse error: {exc}"))
                return

            response = handle_http_mcp_message(message, bridge_handler=bridge_handler)
            if response is None:
                self._send_empty(HTTPStatus.ACCEPTED)
                return
            self._send_json(HTTPStatus.OK, response)

    return ChatGptMcpAccessHandler


def serve(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    bridge_handler: BridgeHandler | None = None,
) -> int:
    """Serve the local Streamable HTTP MCP wrapper until interrupted."""

    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("P0029 server must bind to localhost unless a later package explicitly approves exposure")
    handler_class = make_handler(bridge_handler=bridge_handler)
    with ThreadingHTTPServer((host, port), handler_class) as httpd:
        print(f"{SERVER_NAME} listening on http://{host}:{port}{MCP_PATH}", file=sys.stderr)
        httpd.serve_forever()
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the P0029 ChatGPT MCP access CLI."""

    parser = argparse.ArgumentParser(prog="python3 -m src.mac.services.chatgpt_mcp_access")
    subparsers = parser.add_subparsers(dest="command", required=True)
    serve_parser = subparsers.add_parser("serve")
    serve_parser.add_argument("--host", default=DEFAULT_HOST)
    serve_parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)

    if args.command == "serve":
        return serve(host=args.host, port=args.port)
    return 1
