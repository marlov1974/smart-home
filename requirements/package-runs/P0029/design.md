# P0029 implementation design

## Package interpretation

P0029 must bridge the host compatibility gap between P0028 local stdio MCP and ChatGPT's documented remote MCP model without expanding Shelly capability.

## Chosen path

Implement a minimal Streamable HTTP MCP wrapper:

```text
src/mac/services/chatgpt_mcp_access/
```

The server is development/manual only and binds to `127.0.0.1` by default. It is suitable as the private target for Secure MCP Tunnel or another explicitly approved remote ingress.

## Transport model

Endpoint:

```text
POST /mcp
GET /mcp
```

POST accepts one JSON-RPC MCP message and returns:

- `application/json` JSON-RPC response for requests with `id`
- HTTP `202 Accepted` with no body for accepted notifications
- JSON-RPC error for malformed or rejected requests

GET returns `405 Method Not Allowed` because P0029 does not offer a server-initiated SSE stream. This is allowed by MCP Streamable HTTP for servers that do not provide a GET SSE stream.

## Authentication and exposure model

P0029 does not implement authentication and must not be exposed publicly.

Defaults:

```text
host: 127.0.0.1
port: 8765
path: /mcp
```

Origin handling:

- no `Origin` header is accepted for non-browser/tooling clients
- localhost origins are accepted
- non-local origins are rejected with `403`

Any non-local exposure must happen through a later configured Secure MCP Tunnel or approved authenticated proxy.

## Tool discovery model

Delegate `tools/list` to P0028 `list_mcp_tools()`. The exposed tool list remains exactly:

```text
shelly_kvs_get_by_nat_octet
```

## Tool call model

Delegate `tools/call` to P0028 `handle_mcp_message(...)`, which delegates to P0027 and P0026. P0027 validates allowed arguments and rejects extra fields before P0026 is called.

## Error model

Transport errors:

- bad path: `404`
- unsupported method: `405`
- non-local origin: `403`
- invalid content type or JSON body: `400`
- accepted notification: `202`

MCP errors use JSON-RPC error objects from P0028 where possible.

## Logging and secrets

Diagnostics go to stderr. No tokens, tunnel URLs with credentials, or auth material are stored in repo evidence.

## Forbidden operations not implemented

- no `KVS.Set`
- no `Script.*`
- no switch/light/cover/relay/dimmer/actuator calls
- no generic HTTP proxy
- no arbitrary URL fetch
- no shell execution
- no Codex runner
- no persistent launchd/service installation
- no public unauthenticated exposure

## Test strategy

Unit tests use mocked P0028 bridge handlers and standard-library HTTP clients. They verify:

- `tools/list`
- valid `tools/call`
- unknown tool rejection without delegation
- extra argument rejection without delegation
- arbitrary paths/methods rejected
- non-local origin rejected
- notifications return `202`
- no live network needed

Verification commands:

```bash
python3 -m unittest discover tests/mac/tools/local_kvs_read
python3 -m unittest discover tests/mac/services/local_operator_bridge
python3 -m unittest discover tests/mac/services/local_operator_mcp
python3 -m unittest discover tests/mac/services/chatgpt_mcp_access
python3 -m unittest discover tests/mac/services
git diff --check
```

## Live-test boundary

Optional live verification may perform at most one read-only `KVS.Get` through the local HTTP wrapper:

```text
octet: 30
key: hp.price.status
timeout: 5
```

If sandbox network access blocks the device call, record the blocked result rather than expanding scope.

## Manual ChatGPT registration

After P0029, ChatGPT still needs a remote endpoint:

1. Create Secure MCP Tunnel in OpenAI Platform tunnel settings or provide another approved authenticated remote ingress.
2. Point it at `http://127.0.0.1:8765/mcp`.
3. In ChatGPT web/workspace settings, enable Developer mode if available.
4. Create a custom app/connector using the tunnel/remote endpoint.
5. Scan tools and verify only `shelly_kvs_get_by_nat_octet` appears.
