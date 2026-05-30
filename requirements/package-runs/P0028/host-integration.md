# P0028 Mac host integration follow-up

## Status

Codex Desktop/App MCP config updated for local server `g2-local-operator`.

## Wrapper

Created local wrapper:

```text
/Users/marcus.lovenstad/bin/g2-local-operator-mcp
```

Wrapper contract:

```sh
#!/bin/sh
cd /Users/marcus.lovenstad/dev/smart-home || exit 1
exec python3 -m src.mac.services.local_operator_mcp serve
```

The wrapper avoids host cwd assumptions.

## Host Discovery

Identified local OpenAI/Codex host evidence:

- `/Users/marcus.lovenstad/Library/Application Support/Codex`
- `/Users/marcus.lovenstad/.codex/config.toml`
- Existing `[mcp_servers.node_repl]` entry in `.codex/config.toml`

ChatGPT desktop/app evidence:

- `/Users/marcus.lovenstad/Library/Application Support/com.openai.chat` exists.
- No clear MCP config file was found under `com.openai.chat` during focused local search.

Current host classification:

```text
Codex Desktop/App config found and updated.
ChatGPT Desktop MCP config unknown/not found locally.
```

## Config Change

Config file changed:

```text
/Users/marcus.lovenstad/.codex/config.toml
```

Backup created before edit:

```text
/Users/marcus.lovenstad/.codex/config.toml.p0028-host-backup-20260530
```

Added server config:

```toml
[mcp_servers.g2-local-operator]
args = []
command = "/Users/marcus.lovenstad/bin/g2-local-operator-mcp"
startup_timeout_sec = 30
```

No secrets or token values were added. Existing config content with environment values was not changed.

## Smoke Tests

Required tests passed:

```bash
python3 -m unittest discover tests/mac/services/local_operator_mcp
python3 -m unittest discover tests/mac/services
python3 -m unittest discover tests/mac/tools
git diff --check
```

Direct MCP stdio smoke-test through module:

- `initialize`: returned `protocolVersion: 2025-06-18` and tools capability.
- `notifications/initialized`: accepted with no stdout response.
- `tools/list`: returned exactly `shelly_kvs_get_by_nat_octet`.
- `tools/call`: sandboxed run returned MCP `isError: true` because P0026 had `network_error` and audit permission error.
- Escalated read-only run returned MCP `isError: false`, P0026 HTTP `200`, `result_status: success`, value `"ok"`.

Wrapper smoke-test:

```bash
printf ... | /Users/marcus.lovenstad/bin/g2-local-operator-mcp
```

Result:

- `tools/list`: returned exactly `shelly_kvs_get_by_nat_octet`.
- `tools/call`: HTTP `200`, P0026 `result_status: success`, MCP `isError: false`, value `"ok"`.

## Host Visibility

The current running Codex session cannot prove dynamic host discovery of the new MCP server because MCP server tools are loaded when the host starts or reloads its config. The config is present on disk and the configured command starts successfully.

Expected next action if the tool is not visible in ChatGPT/Codex:

1. Restart or reload the Codex Desktop/App host so it rereads `/Users/marcus.lovenstad/.codex/config.toml`.
2. Check for MCP server `g2-local-operator`.
3. Check that tool `shelly_kvs_get_by_nat_octet` appears.
4. If using ChatGPT Desktop instead of Codex, add an equivalent MCP server entry in ChatGPT's MCP config once its config path/format is known.

## ChatGPT Desktop/App Local MCP Follow-up

Follow-up date:

```text
2026-05-30
```

Goal:

```text
Determine whether ChatGPT Desktop/App on this Mac supports local MCP server config and, only if a safe config path/format is identified, add P0028 as a ChatGPT-local MCP server.
```

Installed ChatGPT app evidence:

```text
path: /Applications/ChatGPT.app
bundle id: com.openai.chat
CFBundleShortVersionString: 1.2026.118
CFBundleVersion: 1777682760
```

Local paths checked:

```text
/Users/marcus.lovenstad/Library/Application Support/com.openai.chat
/Users/marcus.lovenstad/Library/Preferences
/Users/marcus.lovenstad/Library/Containers
/Users/marcus.lovenstad/Library/Application Support
/Applications/ChatGPT.app/Contents
```

Observed ChatGPT support/preference files:

```text
/Users/marcus.lovenstad/Library/Application Support/com.openai.chat
/Users/marcus.lovenstad/Library/Application Support/com.openai.chat/connectors-4f2e078c-1f99-4fc6-944b-a35551a357b4/connectors.data
/Users/marcus.lovenstad/Library/Preferences/com.openai.chat.plist
/Users/marcus.lovenstad/Library/Preferences/com.openai.chat.StatsigService.plist
/Users/marcus.lovenstad/Library/Preferences/com.openai.chat.RemoteFeatureFlags.4f2e078c-1f99-4fc6-944b-a35551a357b4.plist
/Users/marcus.lovenstad/Library/Preferences/ChatGPTHelper.plist
```

Search result:

```text
No safe local ChatGPT MCP config file was found.
No ChatGPT-local config file with a clear mcpServers/mcp_servers/custom stdio server format was found.
No file was found under ChatGPT support/preferences/containers that safely matched the Codex-style local stdio MCP config model.
The only connector-looking local ChatGPT file found was connectors.data, identified by file(1) as binary data; it was not treated as a safe config target.
Focused string/search checks did not find a usable local MCP config entry for g2-local-operator or stdio local server configuration.
```

ChatGPT binary evidence:

```text
The installed ChatGPT app contains MCP-related strings such as MCPSession, mcpServers, MCP_SERVER_CONFIG, mcpServerStatus/list, mcpServer/oauth/login and config/mcpServer/reload.
This proves MCP/app support exists in the app binary, but does not identify a safe local filesystem config path or stdio local-server format.
```

Official OpenAI documentation checked:

```text
OpenAI Help Center: Developer mode and MCP apps in ChatGPT, updated May 2026.
OpenAI developer docs: ChatGPT Developer mode.
OpenAI developer docs: Building MCP servers for ChatGPT Apps and API integrations.
```

Relevant current documentation facts:

```text
ChatGPT developer mode creates apps from remote MCP servers.
Supported ChatGPT developer-mode MCP protocols are SSE and streaming HTTP.
OpenAI Help Center FAQ says ChatGPT cannot connect to a local MCP server directly; if the MCP server runs locally, on-premises or on a private network, use Secure MCP Tunnel.
```

Conclusion:

```text
ChatGPT-local-MCP config not found.
No ChatGPT Desktop/App filesystem config was modified.
No backup was needed because no safe ChatGPT config target was identified.
The P0028 MCP server is currently configured only for Codex through /Users/marcus.lovenstad/.codex/config.toml.
```

Next manual ChatGPT UI steps:

```text
1. In ChatGPT, check Settings -> Apps or Settings -> Connectors.
2. If available, enable Advanced settings -> Developer mode.
3. Use Create app / Create custom MCP connector.
4. ChatGPT expects a remote MCP endpoint, not the local stdio wrapper.
5. To use this P0028 server from ChatGPT, add a remote/SSE or streamable HTTP wrapper or use OpenAI Secure MCP Tunnel once that flow is chosen and package-scoped.
```

## ChatGPT Desktop/App Local MCP Diagnostic Rerun

Rerun date:

```text
2026-05-30
```

Reason:

```text
The first follow-up searched local ChatGPT files but needed a clearer Mac-level diagnosis of whether this installed ChatGPT Desktop/App version supports direct local MCP servers at all.
```

Repository sync state before rerun:

```text
git fetch origin: passed
git status --short --branch:
## main...origin/main
 M requirements/package-runs/P0028/CHANGELOG.md
 M requirements/package-runs/P0028/host-integration.md
```

The modified files were the current P0028 evidence files from the active host-integration follow-up.

Installed ChatGPT Desktop/App:

```text
path: /Applications/ChatGPT.app
bundle id: com.openai.chat
version: 1.2026.118
build: 1777682760
```

Local Mac diagnostic commands and results:

```text
/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' /Applications/ChatGPT.app/Contents/Info.plist
=> com.openai.chat

/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' /Applications/ChatGPT.app/Contents/Info.plist
=> 1.2026.118

/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' /Applications/ChatGPT.app/Contents/Info.plist
=> 1777682760

find ~/Library/Application Support/com.openai.chat -maxdepth 3 ... config-like files
=> /Users/marcus.lovenstad/Library/Application Support/com.openai.chat/connectors-4f2e078c-1f99-4fc6-944b-a35551a357b4/connectors.data

file .../connectors.data
=> data

find ~/Library/Preferences -maxdepth 1 '*openai*'/'*chatgpt*'
=> com.openai.chat.plist, com.openai.chat.StatsigService.plist, com.openai.chat.RemoteFeatureFlags..., ChatGPTHelper.plist, com.openai.codex.plist, com.openai.sky.CUAService.plist

find ~/Library/Containers -maxdepth 1 '*openai*'/'*chatgpt*'
=> no matching ChatGPT/OpenAI containers
```

MCP-related app-binary evidence:

```text
strings -a /Applications/ChatGPT.app/Contents/Frameworks/ChatGPT.framework/Versions/A/ChatGPT | rg 'MCP_SERVER_CONFIG|mcpServers|config/mcpServer/reload|mcpServerStatus/list|mcpServer/oauth/login|MCPSession|CodexRemoteMCPToolCall'
=> CodexRemoteMCPToolCall
=> MCPSession
=> config/mcpServer/reload
=> mcpServerStatus/list
=> mcpServer/oauth/login
=> MCP_SERVER_CONFIG
=> mcpServers
```

This shows the installed ChatGPT app includes MCP-related client/status/config code paths, but it does not identify a documented or safe local filesystem config path for launching a local stdio MCP server.

Negative local config evidence:

```text
strings -a .../connectors.data | rg 'mcpServers|mcp_servers|MCP_SERVER_CONFIG|stdio|g2-local|local-operator|/Users/marcus.lovenstad/bin/g2-local-operator-mcp'
=> no matches

rg -a -n 'mcpServers|mcp_servers|MCP_SERVER_CONFIG|stdio|g2-local|local-operator' ChatGPT plist/preferences
=> no matches
```

Documented OpenAI/ChatGPT support checked:

```text
https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt
https://platform.openai.com/docs/guides/developer-mode
https://platform.openai.com/docs/mcp
```

Documentation result:

```text
OpenAI's ChatGPT developer-mode documentation describes creating an app for a remote MCP server.
The documented ChatGPT developer-mode MCP protocols are SSE and streaming HTTP.
The Help Center FAQ explicitly says ChatGPT cannot connect to a local MCP server directly; local, private-network, on-premises or developer-machine MCP servers require Secure MCP Tunnel for supported OpenAI products.
The Help Center also scopes apps/full MCP/developer mode primarily to ChatGPT web/workspace settings, not a documented local ChatGPT Desktop stdio config file.
```

Conclusion for ChatGPT Desktop/App version 1.2026.118:

```text
This installed ChatGPT Desktop/App version cannot be verified as supporting direct local stdio MCP server configuration.
No documented ChatGPT Desktop local MCP config path or local stdio config format was found.
No ChatGPT Desktop/App config was modified.
The current P0028 local stdio MCP server is usable from Codex, where ~/.codex/config.toml is documented/observed and already configured, but it is not usable directly from this ChatGPT Desktop/App surface right now.
```

Documented ChatGPT path if ChatGPT integration is still desired:

```text
1. Use ChatGPT web/workspace settings, not a local Desktop plist/TOML file.
2. Enable Developer mode where available:
   Settings -> Apps -> Advanced settings -> Developer mode
   or workspace/admin Apps settings depending on plan/workspace.
3. Create/import a custom app/connector by providing a remote MCP endpoint.
4. Use SSE or streaming HTTP as the MCP transport.
5. For a local/developer-machine server, use Secure MCP Tunnel or build a package-scoped remote/SSE/streamable-HTTP wrapper around the P0028 read-only tool.
```

## Post-blocker Clean Rerun

Date:

```text
2026-05-30
```

Blocker handling:

```text
Committed and pushed prior P0028 ChatGPT-local-MCP diagnosis evidence as:
cac330f docs: record P0028 ChatGPT local MCP diagnosis
```

Clean sync after push:

```text
git fetch origin: passed
git status --short --branch:
## main...origin/main
```

Local Mac diagnosis from clean sync state:

```text
ChatGPT Desktop/App path: /Applications/ChatGPT.app
bundle id: com.openai.chat
version: 1.2026.118
build: 1777682760
config-like file found under ChatGPT Application Support: connectors.data only
connectors.data type: binary data
ChatGPT app binary MCP strings: CodexRemoteMCPToolCall, MCPSession, config/mcpServer/reload, mcpServerStatus/list, mcpServer/oauth/login, MCP_SERVER_CONFIG, mcpServers
ChatGPT preferences search for mcpServers/mcp_servers/MCP_SERVER_CONFIG/stdio/g2-local/local-operator: no matches
```

Clean-rerun conclusion:

```text
No change from the earlier diagnosis.
ChatGPT Desktop/App 1.2026.118 on this Mac has MCP-related code paths, but direct local stdio MCP server config support is not documented and no safe local config path/format was found.
This ChatGPT surface cannot use the P0028 local stdio MCP server directly right now.
Codex can use the server through /Users/marcus.lovenstad/.codex/config.toml.
```

## ChatGPT Access Remediation Check

Date:

```text
2026-05-30
```

Operator request:

```text
Fix what needs to be fixed so ChatGPT can access the P0028 function.
```

Current technical requirement from official OpenAI documentation:

```text
ChatGPT does not connect directly to local stdio MCP servers.
ChatGPT custom MCP apps/connectors use remote MCP endpoints.
Documented ChatGPT developer-mode MCP transports are SSE and streaming HTTP.
If the MCP server is local, private-network, on-premises or on a developer machine, OpenAI documents Secure MCP Tunnel as the supported bridge path.
```

Local remediation checks:

```text
command -v cloudflared => not installed
command -v ngrok => not installed
command -v tailscale => not installed
command -v openai => not installed
codex mcp list => g2-local-operator configured and enabled for Codex
ChatGPT app strings search => no local Secure MCP Tunnel CLI or direct local stdio config path identified
Browser plugin attempt for ChatGPT settings => Browser is not available: iab
```

Package-scope decision:

```text
STOP for P0028 implementation changes.
P0028 explicitly forbids Streamable HTTP MCP transport, generic HTTP proxy, persistent service installation and dependency expansion.
Making ChatGPT access this function requires a new package/scope, not another P0028 stdio host-integration edit.
```

What is already fixed:

```text
Codex access is fixed and configured through /Users/marcus.lovenstad/.codex/config.toml.
The wrapper command /Users/marcus.lovenstad/bin/g2-local-operator-mcp starts the P0028 stdio server.
The only exposed tool remains shelly_kvs_get_by_nat_octet.
```

What remains required for ChatGPT:

```text
1. A ChatGPT-compatible remote MCP endpoint:
   - Secure MCP Tunnel to the local/developer-machine MCP server if available in the ChatGPT/OpenAI UI, or
   - a new package-scoped SSE/streamable HTTP MCP wrapper around the existing read-only tool.
2. ChatGPT web/UI configuration:
   - Settings -> Apps -> Advanced settings -> Developer mode, then
   - Create app / custom MCP connector with the remote endpoint.
3. Verification from ChatGPT that tool shelly_kvs_get_by_nat_octet is listed and callable.
```

Safety decision:

```text
No ChatGPT filesystem config was edited.
No tunnel service was installed.
No Streamable HTTP/SSE server was added under P0028.
No device writes were performed.
```

## Safety

No `KVS.Set`, `Script.*`, switch/light/cover/relay/dimmer/actuator call, generic proxy, shell-tool, Codex-runner, launchd service or persistent daemon was added.
