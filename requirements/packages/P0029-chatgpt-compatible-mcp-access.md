# Package P0029: ChatGPT-compatible MCP access for local operator tool

## Status

planned

## Package order

P0029

## Primary area

G2 / Mac tooling / MCP / ChatGPT integration / local operator bridge / Shelly diagnostics

## Linked requirements

Epic:
- E0001

Features:
- F0001

User stories:
- US0001

## Decision summary

Make the existing P0028 read-only local operator MCP tool available to ChatGPT, which cannot currently use the local stdio MCP server directly in this environment.

P0029 is required because P0028 evidence shows:

- P0028 stdio MCP server works locally and is configured for Codex.
- ChatGPT Desktop/App version `1.2026.118` was found, including MCP-related binary strings.
- No documented or safely editable local ChatGPT stdio MCP config path/format was found.
- Official OpenAI-facing ChatGPT MCP integration guidance observed during P0028 remediation points to remote MCP endpoints via SSE/streaming HTTP or Secure MCP Tunnel rather than direct local stdio config.
- P0028 explicitly forbids adding Streamable HTTP/SSE transport or dependency/service expansion, so a new package is required.

P0029 must preserve the P0028/P0027/P0026 safety boundary:

```text
one tool only: shelly_kvs_get_by_nat_octet
read-only only
no new Shelly capability
no generic proxy
no shell
no Codex runner
```

## Solution model

P0029 must determine and implement the narrowest safe ChatGPT-compatible path for the existing tool. Allowed candidate approaches:

1. **Secure MCP Tunnel path**
   - If an official or already-installed Secure MCP Tunnel mechanism is available on the Mac, configure it to expose the existing P0028 stdio server to ChatGPT-compatible remote MCP access.
   - Do not install unknown third-party tunnel software.
   - Do not expose the server publicly without the tunnel's documented authentication/authorization model.

2. **Package-scoped remote MCP wrapper path**
   - If Secure MCP Tunnel is unavailable or not verifiable, implement a minimal package-scoped SSE/streamable HTTP MCP wrapper around the existing P0028/P0027/P0026 tool path.
   - Bind locally by default unless a reviewed tunnel/reverse-proxy step is explicitly documented.
   - Expose only the package-required MCP surface and only the one read-only tool.

3. **STOP with evidence**
   - If neither path can be implemented safely within package constraints, stop with a clear `STOP` review and document the exact blocker and required user/manual action.

P0029 must not silently create a broad local HTTP API. Any HTTP/SSE/streamable server must be MCP-scoped and tool-allowlisted.

## Current behavior

P0026 provides a verified-local-live read-only helper for:

```text
http://192.168.86.240:80XX/rpc/KVS.Get?key=<key>
```

P0027 provides an MCP-shaped local JSON-RPC bridge with exactly one tool:

```text
shelly_kvs_get_by_nat_octet
```

P0028 provides a true MCP stdio-compatible server:

```bash
python3 -m src.mac.services.local_operator_mcp serve
```

P0028 is configured for Codex through:

```text
/Users/marcus.lovenstad/.codex/config.toml
```

using wrapper:

```text
/Users/marcus.lovenstad/bin/g2-local-operator-mcp
```

P0028 evidence states ChatGPT Desktop/App is not currently wired to the local stdio server and that a later package must provide a remote/SSE/streamable HTTP wrapper or Secure MCP Tunnel setup for ChatGPT integration.

## Problem

The project goal is for ChatGPT in the active chat surface to call the local operator tool. P0028 created the safe local MCP server, but ChatGPT Desktop/App did not expose a safe local stdio MCP config path. Therefore ChatGPT cannot currently discover or invoke `shelly_kvs_get_by_nat_octet` from this chat.

P0029 must bridge the host compatibility gap without changing the tool's safety semantics.

## Target behavior

Build or configure a ChatGPT-compatible MCP access path that can, after any required user-side ChatGPT UI registration/approval:

1. expose exactly one MCP tool named `shelly_kvs_get_by_nat_octet`
2. accept only `octet`, `key` and optional `timeout`
3. delegate to existing P0028/P0027/P0026 code paths
4. preserve P0026 audit logging
5. reject unknown tools
6. reject extra arguments such as `url`, `host`, `path`, `method`, `shell`, write hints or arbitrary endpoint data
7. return MCP-compatible tool results with `content` and `isError`
8. provide local unit tests with mocked P0028/P0027/P0026 calls
9. provide one safe local smoke test for discovery and tool call
10. document the exact ChatGPT registration/configuration steps that remain manual, if any
11. record whether ChatGPT can see the tool after the chosen path is configured, or document why that cannot be proven from Codex

## Non-goals

- No new Shelly read tools.
- No Shelly writes.
- No `KVS.Set`.
- No `Script.*` operations.
- No `Switch.*`, `Light.*`, `Cover.*`, relay, dimmer or actuator operations.
- No component creation/update/delete.
- No device configuration changes.
- No Codex runner or package execution integration.
- No generic shell execution.
- No generic HTTP proxy, URL fetch or arbitrary endpoint access.
- No Home Assistant bridge.
- No Mac local API bridge beyond the one KVS-read tool.
- No unauthenticated public exposure of the local tool.
- No persistent launchd/service installation unless a later package explicitly approves production service installation.
- No external Python dependency unless Codex stops before implementation and explicitly asks for a dependency decision.
- No G1 repository changes.

## Invariants

- P0029 is host/protocol access adaptation, not device capability expansion.
- The only supported tool is `shelly_kvs_get_by_nat_octet`.
- The underlying device operation remains read-only P0026 `KVS.Get`.
- Unknown tool names must be rejected before any P0026 call.
- Full arbitrary URL input is forbidden.
- Shell execution is forbidden.
- Generic HTTP proxy behavior is forbidden.
- Device writes are forbidden.
- Unit tests must run without local network/device access.
- Live verification may perform at most one explicit read-only KVS.Get through the new access path.
- If any ChatGPT-facing endpoint is exposed beyond localhost, authentication/tunnel constraints must be documented before use.
- Do not store secrets, tokens, tunnel URLs with credentials, or private auth material in repo evidence.

## Knowledge updates

Create or update:

- `docs/functions/mac/chatgpt-mcp-access.md`
- `docs/functions/00-index.md`

Update only if a durable lesson is discovered:

- `memory/device-management/mac-layer.md`
- `memory/knowhow/codex.md`
- `memory/knowhow/shelly.md`

Do not update broad architecture memory unless the package establishes a durable ChatGPT MCP access pattern that later packages must inherit.

## Implementation updates

Expected areas depend on the chosen path.

If using Secure MCP Tunnel/config-only path:

- `requirements/package-runs/P0029/**`
- `docs/functions/mac/chatgpt-mcp-access.md`
- optional Mac-local wrapper/config instructions only if safe and documented

If implementing package-scoped HTTP/SSE/streamable wrapper:

- `src/mac/services/chatgpt_mcp_access/**` or equivalent P0029-specific path chosen in design
- `tests/mac/services/chatgpt_mcp_access/**`
- `docs/functions/mac/chatgpt-mcp-access.md`
- `docs/functions/00-index.md`
- `requirements/package-runs/P0029/**`

Reuse existing code:

```text
src.mac.services.local_operator_mcp
src.mac.services.local_operator_bridge
src.mac.tools.local_kvs_read
```

## Files to inspect

- `README.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/08-context-bootstrap-modes.md`
- `memory/device-management/mac-layer.md`
- `memory/knowhow/codex.md`
- `requirements/packages/P0026-mac-local-kvs-read-poc.md`
- `requirements/package-runs/P0026/CHANGELOG.md`
- `docs/functions/mac/local-kvs-read-poc.md`
- `src/mac/tools/local_kvs_read/**`
- `requirements/packages/P0027-read-only-mcp-local-operator-bridge.md`
- `requirements/package-runs/P0027/CHANGELOG.md`
- `docs/functions/mac/local-operator-bridge.md`
- `src/mac/services/local_operator_bridge/**`
- `requirements/packages/P0028-true-mcp-stdio-local-operator-bridge.md`
- `requirements/package-runs/P0028/CHANGELOG.md`
- `requirements/package-runs/P0028/host-integration.md`
- `docs/functions/mac/local-operator-mcp.md`
- `src/mac/services/local_operator_mcp/**`
- official/current ChatGPT MCP integration documentation available to Codex locally or online
- local ChatGPT Desktop/App version/config evidence gathered in P0028

## Files allowed to change

- `src/mac/services/chatgpt_mcp_access/**` or equivalent P0029-specific path documented in design
- `tests/mac/services/chatgpt_mcp_access/**` or equivalent P0029-specific test path documented in design
- `docs/functions/mac/chatgpt-mcp-access.md`
- `docs/functions/00-index.md`
- `memory/device-management/mac-layer.md` only for durable Mac/ChatGPT access pattern documentation discovered by this package
- `memory/knowhow/codex.md` only for reusable Codex/MCP host lessons
- `memory/knowhow/shelly.md` only for reusable Shelly/MCP lessons
- `requirements/package-runs/P0029/**`
- `requirements/packages/P0029-chatgpt-compatible-mcp-access.md`

Mac-local files may be created/changed only if explicitly documented and safe:

- wrapper/config files needed for a Secure MCP Tunnel or local access wrapper
- local backups before any config edit

## Forbidden changes

- No G1 repository changes.
- No deploy artifact changes under `dep/s/**`.
- No Home Assistant changes.
- No Shelly runtime script changes.
- No live Shelly writes.
- No new Shelly capabilities beyond read-only P0026 `KVS.Get`.
- No `KVS.Set` implementation.
- No `Script.*` implementation.
- No `Switch.*`, `Light.*`, `Cover.*`, relay, dimmer or actuator implementation.
- No component/config/device write implementation.
- No generic HTTP proxy.
- No arbitrary shell execution.
- No Codex package-runner implementation.
- No broad local network API.
- No persistent service/launchd installation.
- No external Python package dependencies unless the package stops before implementation and asks for a dependency decision.
- No broad refactor outside the minimal P0029 adapter/config/test/docs scope.
- Do not read large data files, raw logs or spot-price fixtures for this package.
- Do not store credentials, bearer tokens, tunnel secrets or private URLs with auth material in repo.

## Pre-implementation consistency review

Before editing, Codex must verify this package against repository truth and current ChatGPT/MCP integration truth and classify it as:

- `PASS`: consistent; continue implementation/configuration.
- `WARN`: implementable with stated minor uncertainty.
- `STOP`: inconsistent, unsafe, dependency-blocked, host-blocked, underspecified or out of scope; do not edit beyond evidence.

Required checks:

- P0026 is present and verified-local-live.
- P0027 is present and read-only.
- P0028 is present and works as true stdio MCP for the one tool.
- ChatGPT Desktop/App local stdio config remains unavailable or unsafe to edit.
- Current supported ChatGPT MCP access path is identified: Secure MCP Tunnel, remote SSE/streamable HTTP, or unavailable.
- The chosen path does not expand tool/device capability.
- The chosen path can be tested without writes.
- Any public/remote exposure has a documented authentication/tunnel boundary.
- If a dependency, tunnel service or external account setup is required, Codex must stop or ask for a separate explicit decision rather than installing silently.

Store review evidence in:

```text
requirements/package-runs/P0029/review.md
```

## Implementation design policy

Codex must create package-scoped implementation design before coding/configuring:

```text
requirements/package-runs/P0029/design.md
```

The design must include:

```text
- chosen path: Secure MCP Tunnel, SSE/streamable HTTP wrapper, or STOP
- ChatGPT MCP access evidence and source/date
- module/config path, if implementation proceeds
- transport model
- authentication/exposure model
- tool discovery model
- tool call model
- P0028/P0027/P0026 delegation model
- validation and error mapping
- logging and secrets handling
- explicit list of forbidden operations not implemented
- live-test boundary, if live test is attempted
- manual ChatGPT registration/approval steps, if any
```

## Function design policy

If implementation proceeds with an HTTP/SSE/streamable wrapper, Codex must create:

```text
requirements/package-runs/P0029/functions.md
```

Document intended functions such as:

```text
list_chatgpt_mcp_tools(...)
handle_chatgpt_mcp_tool_call(...)
format_chatgpt_mcp_response(...)
serve_chatgpt_mcp_endpoint(...)
validate_chatgpt_tool_arguments(...)
main(argv=None)
```

Codex may choose different names, but equivalent responsibilities must be documented before implementation.

If implementation is config/tunnel-only or STOP, `functions.md` should document why no new code functions were created.

Update durable function documentation under `docs/functions/mac/chatgpt-mcp-access.md` after implementation or STOP evidence.

## Context-reset phase gates

Use the standard package phase model:

```text
sync -> bootstrap -> review -> design -> function design if applicable -> implementation/configuration -> tests -> verification -> evidence/changelog
```

Each phase must rely on repository artifacts rather than unwritten chat context.

## Live test/debug policy

Live testing allowed: yes, read-only only.

Live write actions allowed: no.

Shelly log capture required: no.

KVS read verification allowed: yes, but only through the chosen P0029 ChatGPT-compatible path and only for one explicitly selected octet/key per command/test.

Max implementation/debug attempts: 3.

Codex must stop immediately if a live command would require any write-capable RPC, arbitrary URL, shell command, generic proxy, persistent public exposure without auth/tunnel, or URL outside the P0026 NAT construction model.

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/P0029/
```

Expected evidence files:

```text
CHANGELOG.md
review.md
design.md
functions.md
attempts.md
chatgpt-access.md
```

Evidence must include:

- chosen access path
- any official/current documentation checked
- any local ChatGPT version/config facts
- any wrapper/config created
- exact smoke-test commands and redacted results
- whether ChatGPT can see the tool, cannot see the tool, or requires manual UI registration
- proof that only P0026 `KVS.Get` was invoked for live tests
- no secrets/tokens in repo

## Test cases

### TC1: Tool surface remains one-tool-only

Given the P0029 access path
When tool discovery is performed
Then the only tool exposed is:

```text
shelly_kvs_get_by_nat_octet
```

### TC2: Tool call delegates to P0028/P0027/P0026

Given a mocked underlying tool path
When P0029 handles a valid tool call
Then it delegates exactly once and returns a ChatGPT/MCP-compatible result.

### TC3: Unknown tools rejected

Given a request for any unknown tool name
When P0029 handles it
Then it returns a protocol/tool error and performs no device/network operation.

### TC4: Write-like names rejected

Given requests for names such as:

```text
kvs_set_by_nat_octet
script_start
switch_set
light_set
cover_set
fetch_url
run_shell
codex_run_package
```

When P0029 handles them
Then each is rejected and no network/shell/device operation is performed.

### TC5: Extra arguments rejected

Given valid tool name but arguments containing `url`, `host`, `path`, `method`, `shell`, write hints or other extra fields
When P0029 validates the call
Then it rejects before delegation.

### TC6: No broad HTTP/proxy behavior

Given arbitrary HTTP paths, URLs, methods or non-MCP requests
When the P0029 wrapper receives them
Then it rejects them and does not forward arbitrary traffic.

### TC7: Unit tests do not require live network

Given the test suite
When tests run
Then all P0029 tests pass with mocked P0028/P0027/P0026 calls and no local network access.

### TC8: Optional read-only live ChatGPT-compatible test

Given explicit octet/key for live verification
When Codex calls the P0029 access path
Then exactly one read-only KVS.Get is performed through P0028/P0027/P0026 and result evidence is recorded.

### TC9: ChatGPT host visibility check

Given the chosen P0029 path and any required manual registration
When Codex can check host/tool visibility
Then it records whether ChatGPT sees `shelly_kvs_get_by_nat_octet`. If Codex cannot check it, evidence must state why and what the user must verify manually.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/tools/local_kvs_read
python3 -m unittest discover tests/mac/services/local_operator_bridge
python3 -m unittest discover tests/mac/services/local_operator_mcp
python3 -m unittest discover tests/mac/services
python3 -m unittest discover tests/mac/services/chatgpt_mcp_access
git diff --check
```

If no new code is created because the package is config/tunnel-only or STOP, run the relevant existing tests and document omitted commands.

Optional live verification command must use the chosen P0029 ChatGPT-compatible path and include exactly one read-only KVS request.

## Runtime health checks

For optional live read-only verification, record:

- access path used: Secure MCP Tunnel, local wrapper, SSE/streamable HTTP wrapper or STOP
- tool name
- octet
- KVS key
- P0026-derived URL if available in returned result
- timeout used
- result status
- HTTP status or connection/tunnel error
- whether ChatGPT host visibility was verified
- proof that no write-capable RPC, generic proxy or shell command was called

No actuator/device state checks are required because the package is read-only.

## Deployment plan

No production deployment by default.

P0029 may create a manual/dev-only access wrapper or tunnel configuration if safe. It must not install launchd, persistent services or public endpoints without a later explicit package.

## Rollback plan

Rollback is a new forward-moving package if the access shape is wrong.

If local config files are changed, Codex must create a timestamped backup first and document the backup path. If verification fails, Codex must restore or document rollback steps.

## Expected Codex output

- consistency review result: PASS/WARN/STOP
- chosen access path or STOP reason
- official/current ChatGPT MCP access evidence checked
- design path
- functions path or reason no functions were created
- files changed
- local config/wrapper changes and backups if any
- tests run
- verification results
- optional live access command/session and result, if performed
- whether ChatGPT can see the tool, cannot see it, or requires manual UI registration
- package-run evidence paths created/updated
- function catalog update path
- uncertainty / skipped checks
- commit SHA after push, if successful and pushed
- diff summary

## Completion notes

To be filled after implementation.
