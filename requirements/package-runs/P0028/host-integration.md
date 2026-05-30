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

## Safety

No `KVS.Set`, `Script.*`, switch/light/cover/relay/dimmer/actuator call, generic proxy, shell-tool, Codex-runner, launchd service or persistent daemon was added.
