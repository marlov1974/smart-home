# P0029 consistency review

## Result

WARN

P0029 is consistent with repository truth and implementable, but full ChatGPT visibility cannot be completed from Codex alone because ChatGPT requires a remote MCP endpoint registered through ChatGPT/Workspace UI or Secure MCP Tunnel.

## Repository evidence

- P0026 exists and provides the verified read-only `KVS.Get` NAT helper.
- P0027 exists and exposes exactly one read-only local operator tool.
- P0028 exists, implements true MCP stdio for `shelly_kvs_get_by_nat_octet`, and is configured for Codex through `/Users/marcus.lovenstad/.codex/config.toml`.
- P0028 host-integration evidence found ChatGPT Desktop/App `1.2026.118`, but no documented local stdio MCP config path or safe filesystem config format for ChatGPT.

## Current external evidence

Checked on 2026-05-30:

- OpenAI Help Center: ChatGPT cannot connect directly to a local MCP server; local/private/developer-machine MCP servers require Secure MCP Tunnel.
- OpenAI ChatGPT developer-mode docs: custom app configuration is done through ChatGPT/Workspace Apps UI by providing an MCP endpoint and scanning tools.
- MCP `2025-06-18` transport spec: remote Streamable HTTP uses one MCP endpoint supporting POST and GET; POST accepts JSON-RPC and may return `application/json`; GET may return `405 Method Not Allowed` when no server-initiated SSE stream is offered.

## Local host evidence

- `command -v cloudflared`: not installed.
- `command -v ngrok`: not installed.
- `command -v tailscale`: not installed.
- `command -v openai`: not installed.
- `tunnel-client`: not found in PATH during P0028 evidence and no local ChatGPT tunnel CLI was identified.
- Codex MCP list shows `g2-local-operator` configured and enabled.

## Chosen path

Proceed with `WARN` using package candidate 2:

```text
package-scoped Streamable HTTP wrapper bound to 127.0.0.1 by default
```

This does not by itself expose the server to ChatGPT. It creates the private MCP endpoint that a later Secure MCP Tunnel profile, approved reverse proxy, or manual ChatGPT remote endpoint flow can use.

## Safety review

The implementation can preserve package invariants:

- one tool only: `shelly_kvs_get_by_nat_octet`
- read-only P0028/P0027/P0026 delegation
- no generic HTTP proxy
- no arbitrary URL input
- no shell execution
- no device writes
- localhost bind by default
- Origin validation for browser-origin requests
- no secrets in repo

## Remaining uncertainty

ChatGPT host visibility cannot be proven until the operator creates or provides a ChatGPT-accessible remote endpoint and registers it in ChatGPT Apps/Developer mode.
