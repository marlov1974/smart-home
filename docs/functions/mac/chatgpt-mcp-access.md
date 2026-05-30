# Mac ChatGPT MCP Access

Last changed: P0029

## Purpose

`src.mac.services.chatgpt_mcp_access` is a local Streamable HTTP MCP wrapper for the P0028 read-only local operator MCP tool. It exists because ChatGPT does not use the local stdio MCP config that Codex uses.

The wrapper exposes exactly one MCP tool:

```text
shelly_kvs_get_by_nat_octet
```

It delegates to P0028, which delegates to P0027 and P0026. It adds no Shelly capability.

## Transport

Default local endpoint:

```text
http://127.0.0.1:8765/mcp
```

Supported methods:

- `POST /mcp` for MCP JSON-RPC requests
- `GET /mcp` returns `405 Method Not Allowed`; P0029 does not provide a server-initiated SSE stream

The server returns JSON-RPC/MCP responses with:

```text
Content-Type: application/json
MCP-Protocol-Version: 2025-06-18
```

## CLI

```bash
python3 -m src.mac.services.chatgpt_mcp_access serve --host 127.0.0.1 --port 8765
```

The server refuses non-local binds. It is not a production service and is not installed with launchd.

## Safety Boundary

Implemented:

- localhost bind by default
- localhost-origin enforcement for browser-origin requests
- one MCP endpoint
- one tool only
- strict P0027/P0028 argument validation

Not implemented:

- authentication
- public exposure
- generic proxying
- arbitrary URL fetch
- shell execution
- Codex runner
- write-capable Shelly RPCs
- persistent service installation

## ChatGPT Registration

P0029 does not itself register the endpoint in ChatGPT. ChatGPT still needs a remote endpoint through one of these operator-approved paths:

```text
Secure MCP Tunnel -> http://127.0.0.1:8765/mcp
approved authenticated reverse proxy -> http://127.0.0.1:8765/mcp
```

OpenAI Help Center guidance checked during P0029 says ChatGPT connects to remote MCP servers and cannot connect directly to local MCP servers. For local/private-network/on-premises/developer-machine MCP servers, use Secure MCP Tunnel.

Manual registration steps:

```text
1. Start local P0029:
   python3 -m src.mac.services.chatgpt_mcp_access serve --host 127.0.0.1 --port 8765

2. In OpenAI/ChatGPT web, create or enable Secure MCP Tunnel to:
   http://127.0.0.1:8765/mcp

3. In ChatGPT web/workspace settings, enable Developer mode if required.

4. Create a custom MCP app/connector:
   Settings or Workspace Settings -> Apps -> Create
   endpoint: Secure MCP Tunnel remote endpoint
   auth: tunnel/OpenAI-recommended authenticated path
   Scan Tools
   Create
```

Expected tool list:

```text
shelly_kvs_get_by_nat_octet
```

Do not store tunnel tokens, secrets or private auth material in repo evidence. Do not expose this endpoint publicly without an authenticated tunnel/reverse-proxy boundary.

## Functions

### `is_allowed_origin(origin)`

Accepts missing or localhost origins and rejects non-local origins.

### `json_response_bytes(payload)`

Serializes JSON-RPC/MCP response payloads for HTTP.

### `handle_http_mcp_message(message, bridge_handler=None)`

Delegates one decoded MCP JSON-RPC message to P0028.

### `make_handler(bridge_handler=None)`

Creates the package-scoped HTTP request handler class.

### `serve(host="127.0.0.1", port=8765, bridge_handler=None)`

Runs the local Streamable HTTP MCP wrapper.

### `main(argv=None)`

CLI entry point.
