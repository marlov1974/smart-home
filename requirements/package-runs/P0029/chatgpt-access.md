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

## Tunnel / ChatGPT registration phase

Date:

```text
2026-05-30
```

Result:

```text
STOP for tunnel configuration from Codex.
```

Reason:

```text
No safe/offical Secure MCP Tunnel command-line mechanism was found on this Mac.
ChatGPT UI registration appears to require manual ChatGPT web/workspace action.
Browser access to ChatGPT settings was unavailable from Codex in this session.
No third-party tunnel was installed because package instructions forbid installing third-party tunnel software without explicit separate approval.
```

Official ChatGPT/OpenAI evidence checked:

```text
OpenAI Help Center: Developer mode and MCP apps in ChatGPT
URL: https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt
Observed facts:
- ChatGPT connects to remote MCP servers.
- ChatGPT cannot connect directly to local MCP servers.
- Local/private-network/on-premises/developer-machine MCP servers require Secure MCP Tunnel for supported OpenAI products.
- Apps/full MCP/developer mode are available on ChatGPT web for Business and Enterprise/Edu; Pro can use developer mode for custom apps with read/fetch permissions.
- Custom app configuration is done in ChatGPT/workspace Apps UI by providing the MCP endpoint, choosing auth if applicable, clicking Scan Tools, then Create.
```

Local P0029 verification before tunnel check:

```text
server:
python3 -m src.mac.services.chatgpt_mcp_access serve --host 127.0.0.1 --port 8765

tools/list:
HTTP 200
MCP-Protocol-Version: 2025-06-18
tool count: 1
tool name: shelly_kvs_get_by_nat_octet

tools/call:
HTTP 200
tool: shelly_kvs_get_by_nat_octet
octet: 30
key: hp.price.status
timeout: 5
MCP isError: false
P0026 result_status: success
P0026 HTTP status: 200
value: "ok"
derived URL: http://192.168.86.240:8030/rpc/KVS.Get?key=hp.price.status
```

Local tunnel checks:

```text
command -v tunnel-client => not found
command -v mcp-tunnel => not found
command -v openai => not found
command -v cloudflared => not found
command -v ngrok => not found
command -v tailscale => not found
find /Applications/ChatGPT.app/Contents ... '*tunnel*'/'*mcp*'/'*connector*' => no matching executable/config file
ChatGPT app strings include MCP server status/config markers, but no local Secure MCP Tunnel CLI or local tunnel setup command was identified.
ChatGPT Application Support connector-like file remains connectors.data only; not a safe manually editable config target.
```

ChatGPT UI access check:

```text
Attempted Browser navigation to https://chatgpt.com/#settings/Apps
Result: Browser is not available: iab
```

Manual steps required from the operator:

```text
1. Keep the local P0029 server running:
   python3 -m src.mac.services.chatgpt_mcp_access serve --host 127.0.0.1 --port 8765

2. In OpenAI/ChatGPT web, create or enable a Secure MCP Tunnel for:
   local target: http://127.0.0.1:8765/mcp

3. Do not paste tunnel secrets/tokens into repo or package evidence.

4. In ChatGPT web/workspace settings, enable Developer mode if needed:
   - Business: admins/owners can enable developer mode from User Settings -> Apps -> Advanced settings -> Developer mode or Workspace settings -> Apps -> Create.
   - Enterprise/Edu: admins/owners grant access in Workspace Settings -> Permissions & Roles -> Connected Data; enabled users then toggle Settings -> Apps -> Advanced Settings.
   - Pro: developer mode is still required for custom apps, with read/fetch permissions.

5. Create a custom MCP app/connector:
   - Settings or Workspace Settings -> Apps -> Create
   - endpoint: the Secure MCP Tunnel remote endpoint
   - auth: use the tunnel/OpenAI-recommended auth option; do not use unauthenticated public exposure
   - click Scan Tools
   - verify exactly one tool appears: shelly_kvs_get_by_nat_octet
   - click Create

6. In a new ChatGPT chat, enable/select the draft/dev app and test:
   tool: shelly_kvs_get_by_nat_octet
   arguments: {"octet":30,"key":"hp.price.status","timeout":5}

7. Expected result:
   result_status: success
   value: "ok"
```

ChatGPT host visibility:

```text
Not verified by Codex.
Blocked on manual Secure MCP Tunnel creation and ChatGPT app registration.
```

Safety:

```text
No KVS.Set, Script.*, Switch/Light/Cover/relay/dimmer/actuator call, shell tool, generic proxy, Codex runner, public unauthenticated endpoint, third-party tunnel install, secret storage or ChatGPT filesystem config edit was performed.
```
