# P0029 changelog

## Status

Implemented and locally verified.

## User-visible behavior changed

Added a localhost Streamable HTTP MCP wrapper for the existing P0028 read-only tool:

```bash
python3 -m src.mac.services.chatgpt_mcp_access serve --host 127.0.0.1 --port 8765
```

Endpoint:

```text
http://127.0.0.1:8765/mcp
```

It exposes exactly one tool:

```text
shelly_kvs_get_by_nat_octet
```

## Files changed

- Added `src/mac/services/chatgpt_mcp_access/`.
- Added `tests/mac/services/chatgpt_mcp_access/`.
- Added `docs/functions/mac/chatgpt-mcp-access.md`.
- Updated `docs/functions/00-index.md`.
- Added P0029 package-run review/design/functions/attempts/chatgpt-access evidence.
- Updated `requirements/packages/P0029-chatgpt-compatible-mcp-access.md` completion notes.

## Contracts changed

P0029 adds a local HTTP MCP access wrapper around P0028. It does not add device capability. The underlying device action remains P0026 read-only `KVS.Get`.

Security/access defaults:

```text
bind: 127.0.0.1 only
path: /mcp
public exposure: not implemented
auth: not implemented; must be provided by Secure MCP Tunnel or an approved remote ingress before ChatGPT use
```

## Verification performed

```bash
python3 -m unittest discover tests/mac/services/chatgpt_mcp_access
python3 -m unittest discover tests/mac/services/local_operator_mcp
python3 -m unittest discover tests/mac/services/local_operator_bridge
python3 -m unittest discover tests/mac/tools/local_kvs_read
python3 -m unittest discover tests/mac/services
python3 -m unittest discover tests/mac/tools
```

Local HTTP smoke test:

```text
tools/list: HTTP 200, one tool, shelly_kvs_get_by_nat_octet
tools/call: HTTP 200, MCP isError=false, P0026 result_status=success, value="ok"
```

## Known limitations and follow-up

- ChatGPT still requires manual UI registration through a Secure MCP Tunnel or approved authenticated remote endpoint.
- ChatGPT host visibility was not verified by Codex.
- No persistent service/launchd installation was added.
- No public unauthenticated endpoint was created.

## Bootstrap for next package

Read `docs/functions/mac/chatgpt-mcp-access.md` for the durable P0029 access wrapper contract. Implementation lives in `src/mac/services/chatgpt_mcp_access/core.py`. Tests live in `tests/mac/services/chatgpt_mcp_access/test_core.py`. ChatGPT registration evidence is in `requirements/package-runs/P0029/chatgpt-access.md`.
