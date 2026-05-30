# P0029 ChatGPT access evidence

## Access path

Chosen path:

```text
package-scoped localhost Streamable HTTP MCP wrapper
```

Local endpoint:

```text
http://127.0.0.1:8765/mcp
```

CLI:

```bash
python3 -m src.mac.services.chatgpt_mcp_access serve --host 127.0.0.1 --port 8765
```

## ChatGPT requirement

P0029 does not create a public or authenticated remote endpoint. It creates the local private MCP HTTP endpoint that ChatGPT can reach only after one of these manual/operator-approved steps:

```text
Secure MCP Tunnel to http://127.0.0.1:8765/mcp
approved authenticated reverse proxy to http://127.0.0.1:8765/mcp
```

Manual ChatGPT registration remains required:

```text
ChatGPT web/workspace settings
Settings -> Apps -> Advanced settings -> Developer mode
Create app / custom MCP connector
Endpoint: tunnel or authenticated remote endpoint
Scan tools
```

Expected tool:

```text
shelly_kvs_get_by_nat_octet
```

## Verified locally

Tool discovery:

```text
POST /mcp tools/list
HTTP 200
MCP-Protocol-Version: 2025-06-18
tool count: 1
tool name: shelly_kvs_get_by_nat_octet
```

Tool call:

```text
POST /mcp tools/call
tool: shelly_kvs_get_by_nat_octet
octet: 30
key: hp.price.status
timeout: 5
HTTP 200
MCP isError: false
P0026 result_status: success
P0026 HTTP status: 200
value: "ok"
```

## ChatGPT host visibility

ChatGPT host visibility was not verified from Codex because:

```text
No Secure MCP Tunnel instance or approved remote endpoint exists yet.
Browser access to ChatGPT settings was unavailable in this Codex session.
The package must not store credentials, tunnel secrets or private auth material in repo.
```

Operator verification step:

```text
After registering the tunnel/remote endpoint in ChatGPT, verify ChatGPT lists exactly shelly_kvs_get_by_nat_octet and can call it with octet=30, key=hp.price.status, timeout=5.
```

## Secrets

No secrets, bearer tokens, tunnel credentials or private auth material were added to repo evidence.
