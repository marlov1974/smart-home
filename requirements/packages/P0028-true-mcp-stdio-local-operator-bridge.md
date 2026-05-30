# Package P0028: True MCP stdio local operator bridge

## Status

planned

## Package order

P0028

## Primary area

G2 / Mac tooling / MCP / local operator bridge / Shelly diagnostics

## Linked requirements

Epic:
- E0001

Features:
- F0001

User stories:
- US0001

## Decision summary

Promote the P0027 MCP-shaped local JSON-RPC bridge into a true MCP stdio-compatible server for the existing read-only Shelly KVS tool.

P0028 must keep the same operational safety scope as P0027:

```text
one tool only: shelly_kvs_get_by_nat_octet
read-only only
P0026 remains the Shelly HTTP/KVS implementation
```

The goal is protocol compatibility, not new device capability.

P0028 should implement enough of MCP stdio to work with an MCP-compatible local host/client:

- `initialize`
- initialized notification handling
- `tools/list`
- `tools/call`
- JSON-RPC error handling
- newline-delimited stdio transport
- MCP tool result shape

P0028 must not add Shelly writes, Codex runner functionality, generic HTTP access, shell execution, persistent production service installation, or any broader local operator permissions.

## External protocol basis

P0028 targets MCP specification version:

```text
2025-06-18
```

Relevant MCP facts from the current spec:

- MCP uses JSON-RPC messages encoded as UTF-8.
- stdio transport uses stdin/stdout between a client-launched subprocess and server.
- stdio messages are individual JSON-RPC messages delimited by newlines and must not contain embedded newlines.
- The server must not write anything to stdout that is not a valid MCP message.
- Servers supporting tools must declare the `tools` capability.
- `tools/list` returns tool definitions with `name`, `description` and `inputSchema`.
- `tools/call` invokes a named tool and returns a tool result with `content` and `isError`.

Codex must verify the current MCP spec before implementation and document any material version difference in `requirements/package-runs/P0028/review.md` or `design.md`.

## Solution model

P0028 should wrap or extend the P0027 bridge rather than replace P0026/P0027 behavior.

Expected architecture:

```text
MCP-compatible local host/client
        |
        | stdio JSON-RPC MCP messages
        v
src/mac/services/local_operator_mcp/ or equivalent
        |
        | protocol adapter
        v
src/mac/services/local_operator_bridge
        |
        | delegates valid tool call
        v
src.mac.tools.local_kvs_read.kvs_get_by_nat_octet(...)
        |
        v
http://192.168.86.240:80XX/rpc/KVS.Get?key=<key>
```

P0027 remains the internal one-tool bridge model. P0028 adds real MCP lifecycle/protocol surface around it.

If Codex can implement true stdio MCP compatibility safely using Python standard library only, it should do so.

If Codex determines that true MCP compatibility requires an external SDK/dependency or protocol surface larger than this package can safely implement, it must stop with `STOP` or continue with `WARN` only if it still creates useful documentation/evidence without claiming true MCP compatibility. It must not silently re-create another MCP-shaped POC and call it true MCP.

## Current behavior

P0026 is a verified-local-live read-only helper for one Shelly `KVS.Get` through the operator NAT convention.

P0027 implemented a local bridge process:

```bash
python3 -m src.mac.services.local_operator_bridge serve
```

P0027 supports newline-delimited JSON-RPC-like messages over stdin/stdout with:

```text
tools/list
tools/call
```

but explicitly does not claim true MCP stdio compatibility. It omits full MCP initialization, capability negotiation and MCP result shape.

P0027 live bridge verification succeeded for:

```text
tool: shelly_kvs_get_by_nat_octet
octet: 30
key: hp.price.status
result_status: success
result value: "ok"
```

## Problem

The project now has a safe local bridge POC, but an MCP-compatible host will expect MCP lifecycle semantics and result shapes, not just the P0027 bridge's local JSON-RPC shape.

To let ChatGPT/Codex-compatible MCP hosts use the local bridge as a tool server, P0028 must add a real MCP stdio server layer while preserving the exact one-tool read-only boundary.

## Target behavior

Build Python standard-library Mac tooling that can:

1. start a true MCP stdio-compatible local server process
2. handle MCP `initialize`
3. advertise server metadata and capabilities including `tools`
4. accept initialized notification if sent by the client
5. handle `tools/list`
6. expose exactly one tool: `shelly_kvs_get_by_nat_octet`
7. use MCP `inputSchema`, not the P0027 `input_schema` spelling, for tool metadata
8. handle `tools/call` for that one tool
9. delegate valid calls to the P0027/P0026 path
10. return MCP-style tool results with `content` and `isError`
11. encode the P0026 structured result as JSON text in the tool result content, unless Codex documents a better MCP-compatible structured-content choice
12. reject unknown methods/tools with JSON-RPC/MCP-compatible errors
13. log diagnostics only to stderr, never stdout
14. include unit tests without requiring live local network access
15. document MCP server configuration/usage in `docs/functions/mac/`
16. create package-run evidence under `requirements/package-runs/P0028/`

Suggested manual command shape:

```bash
python3 -m src.mac.services.local_operator_mcp serve
```

Codex must choose and justify the path in `requirements/package-runs/P0028/design.md` before implementation.

## Non-goals

- No new Shelly read tools beyond `shelly_kvs_get_by_nat_octet`.
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
- No Streamable HTTP MCP server.
- No persistent production service/launchd installation.
- No external Python dependency unless Codex stops and explicitly asks for a dependency/package decision.
- No G1 repository changes.

## Invariants

- Python standard library only unless the package stops before implementation and requests a dependency decision.
- Read-only by construction.
- P0028 is protocol adaptation, not capability expansion.
- The only supported MCP tool in P0028 is `shelly_kvs_get_by_nat_octet`.
- Unknown tool names must be rejected before any P0026 call.
- The server must not accept a full arbitrary URL.
- The server must not expose any write-capable Shelly RPC.
- The server must not run arbitrary shell commands.
- stdout must contain only valid MCP/JSON-RPC messages.
- diagnostics/logging must go to stderr.
- Unit tests must run without local network/device access.
- Any live verification must be explicitly read-only and must use only `KVS.Get` through the existing P0026 path.

## Knowledge updates

Create or update:

- `docs/functions/mac/local-operator-mcp.md`
- `docs/functions/00-index.md`

Update only if a durable lesson is discovered:

- `memory/knowhow/codex.md`
- `memory/knowhow/shelly.md`
- `memory/device-management/mac-layer.md`

Do not update broad architecture memory unless the package establishes a durable MCP server pattern that later packages must inherit.

## Implementation updates

Expected areas, final path to be chosen in design:

- `src/mac/services/local_operator_mcp/**`
- `tests/mac/services/local_operator_mcp/**`
- `docs/functions/mac/local-operator-mcp.md`
- `docs/functions/00-index.md`
- `requirements/package-runs/P0028/**`

The implementation should reuse existing bridge/tooling:

```text
src.mac.services.local_operator_bridge
src.mac.tools.local_kvs_read
```

Codex may refactor shared P0027 protocol/tool routing only if it stays package-scoped, is documented in design/functions, and does not expand capability.

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
- `tests/mac/tools/local_kvs_read/**`
- `requirements/packages/P0027-read-only-mcp-local-operator-bridge.md`
- `requirements/package-runs/P0027/CHANGELOG.md`
- `requirements/package-runs/P0027/review.md`
- `requirements/package-runs/P0027/design.md`
- `requirements/package-runs/P0027/functions.md`
- `requirements/package-runs/P0027/attempts.md`
- `docs/functions/mac/local-operator-bridge.md`
- `src/mac/services/local_operator_bridge/**`
- `tests/mac/services/local_operator_bridge/**`
- current MCP 2025-06-18 spec pages for stdio transport, lifecycle and tools

## Files allowed to change

- `src/mac/services/local_operator_mcp/**`
- `tests/mac/services/local_operator_mcp/**`
- `src/mac/services/local_operator_bridge/**` only for narrow shared-routing refactor documented in P0028 design/functions
- `tests/mac/services/local_operator_bridge/**` only if the shared-routing refactor requires test updates
- `docs/functions/mac/local-operator-mcp.md`
- `docs/functions/00-index.md`
- `memory/knowhow/codex.md` only for reusable lessons discovered during implementation/verification
- `memory/knowhow/shelly.md` only for reusable lessons discovered during implementation/verification
- `memory/device-management/mac-layer.md` only for durable MCP server pattern documentation discovered by this package
- `requirements/package-runs/P0028/**`
- `requirements/packages/P0028-true-mcp-stdio-local-operator-bridge.md`

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
- No Streamable HTTP MCP transport.
- No launchd/persistent service installation.
- No external Python package dependencies unless the package stops before implementation and asks for a dependency decision.
- No broad refactor outside the minimal P0028 MCP adapter/test/docs scope.
- Do not read large data files, raw logs or spot-price fixtures for this package.

## Pre-implementation consistency review

Before editing, Codex must verify this package against repository truth and current MCP spec and classify it as:

- `PASS`: consistent; continue implementation.
- `WARN`: implementable with stated minor uncertainty.
- `STOP`: inconsistent, unsafe, underspecified, dependency-blocked or out of scope; do not edit.

Required checks:

- P0026 is present and verified-local-live.
- P0027 is present, read-only, and documented as MCP-shaped JSON-RPC POC.
- P0028 reuses P0027/P0026 and does not duplicate/expand Shelly network access.
- Current MCP stdio transport uses newline-delimited JSON-RPC messages over stdin/stdout.
- Current MCP tools use `tools/list`, `tools/call`, `inputSchema`, and tool results with `content`/`isError`.
- Proposed files are inside Mac service/test/docs/package-run scope.
- The package does not create a generic local network, shell or device-control primitive.
- No live writes are required for verification.
- If true MCP compatibility cannot be implemented safely with standard library in this package, stop or warn explicitly and do not claim true MCP compatibility.

Store review evidence in:

```text
requirements/package-runs/P0028/review.md
```

## Implementation design policy

Codex must create package-scoped implementation design before coding:

```text
requirements/package-runs/P0028/design.md
```

The design must include:

```text
- chosen module path
- MCP spec/version checked
- stdio framing model
- initialization/lifecycle model
- serverInfo and capabilities model
- tools/list model
- tools/call model
- MCP tool result content model
- P0027/P0026 integration model
- validation and error mapping
- stdout/stderr logging rule
- explicit list of forbidden operations not implemented
- live-test boundary, if live test is attempted
```

## Function design policy

Codex must create package-scoped function design before coding:

```text
requirements/package-runs/P0028/functions.md
```

The function design must document intended functions such as:

```text
handle_initialize(...)
handle_initialized_notification(...)
list_mcp_tools(...)
call_mcp_tool(...)
format_mcp_tool_result(...)
handle_mcp_message(...)
process_mcp_line(...)
serve(...)
main(argv=None)
```

Codex may choose different names, but equivalent responsibilities must be documented before implementation.

Update durable function documentation under `docs/functions/mac/local-operator-mcp.md` after implementation.

## Context-reset phase gates

Use the standard package phase model:

```text
sync -> bootstrap -> review -> design -> function design -> implementation -> tests -> verification -> evidence/changelog
```

Each phase must rely on repository artifacts rather than unwritten chat context.

## Live test/debug policy

Live testing allowed: yes, read-only only.

Live write actions allowed: no.

Shelly log capture required: no.

KVS read verification allowed: yes, but only through the P0028 MCP server path calling the existing P0027/P0026 path and only for one explicitly selected octet/key per command/test.

Max implementation/debug attempts: 3.

Codex must stop immediately if a live command would require any write-capable RPC, arbitrary URL, shell command, generic proxy, Streamable HTTP server, persistent install, or URL outside the P0026 NAT construction model.

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/P0028/
```

Expected evidence files:

```text
CHANGELOG.md
review.md
design.md
functions.md
attempts.md
```

If live verification is performed, record the MCP stdio command/session, initialize request/response summary, tools/list summary, tools/call summary, octet/key, result status and proof that only P0026 `KVS.Get` was invoked. Do not store large raw logs.

## Test cases

### TC1: MCP initialize response

Given an MCP `initialize` request
When the P0028 server handles it
Then it returns a JSON-RPC response with protocol version, serverInfo and tools capability.

### TC2: Initialized notification handling

Given an MCP initialized notification
When the P0028 server handles it
Then it accepts it without producing an invalid stdout response if the protocol expects no response for notifications, or otherwise follows the documented chosen handling.

### TC3: MCP tools/list exposes exactly one tool

Given an MCP `tools/list` request
When the server handles it
Then the only tool is:

```text
shelly_kvs_get_by_nat_octet
```

and its schema uses `inputSchema` with only `octet`, `key` and optional `timeout`.

### TC4: MCP tools/call delegates to P0027/P0026

Given a mocked bridge/P0026 reader
When `tools/call` invokes `shelly_kvs_get_by_nat_octet`
Then the server delegates exactly once and returns an MCP tool result.

### TC5: MCP tool result shape

Given a successful delegated read
When the server formats the result
Then the response contains `content` with JSON text and `isError: false`.

Given a delegated P0026 read failure such as network error or Shelly error
When the server formats the result
Then the response still uses MCP tool result shape and sets `isError` according to the documented design.

### TC6: Unknown tools rejected

Given a `tools/call` request for any unknown tool name
When the server handles it
Then it returns an MCP/JSON-RPC error or tool error without calling P0026.

### TC7: Write-like names and arbitrary operations absent/rejected

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

When the server handles them
Then each is rejected and no network/shell/device operation is performed.

### TC8: Extra arguments rejected

Given valid tool name but arguments containing `url`, `host`, `path`, `method`, `shell`, write hints or other extra fields
When the server validates the call
Then it rejects the request before delegation.

### TC9: stdout contains only MCP messages

Given the server processes requests
When tests capture stdout/stderr
Then stdout contains only JSON-RPC/MCP response lines and diagnostics, if any, go to stderr.

### TC10: Unit tests do not require live network

Given the test suite
When tests run
Then all P0028 tests pass with mocked P0027/P0026 calls and no local network access.

### TC11: Optional read-only live MCP test

Given explicit octet/key for live verification
When Codex calls the MCP server through initialize, tools/list and tools/call
Then the server performs exactly one read-only KVS.Get through the existing P0027/P0026 path and records the result.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/tools/local_kvs_read
python3 -m unittest discover tests/mac/tools
python3 -m unittest discover tests/mac/services/local_operator_bridge
python3 -m unittest discover tests/mac/services/local_operator_mcp
python3 -m unittest discover tests/mac/services
git diff --check
```

If the chosen MCP path differs, use the equivalent package-scoped test command and document it in `design.md` and `attempts.md`.

Optional live verification command must use the P0028 MCP stdio entry point and include initialize, tools/list and tools/call messages. Codex must document exact command/session format after implementation.

## Runtime health checks

For optional live read-only MCP verification, record:

- MCP server command/session used
- protocol version advertised/negotiated
- initialize response summary
- tools/list tool names
- tools/call tool name
- octet
- KVS key
- P0026-derived URL if available in returned result
- timeout used
- result status
- HTTP status or connection error
- proof that no write-capable RPC, generic proxy or shell command was called

No actuator/device state checks are required because the package is read-only.

## Deployment plan

No production deployment.

This package creates a local Mac-side MCP stdio server POC. It may be run manually by Codex/operator for read-only verification. It must not install a persistent service or launchd job.

## Rollback plan

Rollback is a new forward-moving package if the MCP server shape is wrong.

If implementation fails verification after allowed attempts, Codex must preserve useful package-run evidence and revert unverified source/test/doc changes unless the package evidence explicitly says a documentation-only finding should remain.

## Expected Codex output

- consistency review result: PASS/WARN/STOP
- MCP spec/version checked
- whether true MCP stdio compatibility was implemented, or explicit reason for STOP/WARN
- design path
- functions path
- files changed
- tests run
- verification results
- optional live MCP session and result, if live test performed
- package-run evidence paths created/updated
- function catalog update path
- uncertainty / skipped checks
- commit SHA after push, if successful and pushed
- diff summary

## Completion notes

To be filled after implementation.
