# Package P0027: Read-only MCP local operator bridge

## Status

verified-local-live

## Package order

P0027

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

Build the first local MCP/operator bridge POC on top of the verified P0026 local KVS read helper.

P0027 should expose exactly one read-only MCP-style tool for local operator use:

```text
shelly_kvs_get_by_nat_octet(octet, key)
```

The tool must call the existing P0026 implementation rather than reimplementing Shelly HTTP access.

P0027 is intentionally still read-only. It must not add Shelly writes, Codex runner functionality, generic HTTP access, persistent production service installation, or broad local device control.

## Solution model

P0027 introduces a small local bridge process or module that can be run on the Mac and communicate using an MCP-compatible JSON-RPC/tool model.

Expected initial architecture:

```text
MCP-compatible local host/client
        |
        | tool call: shelly_kvs_get_by_nat_octet
        v
src/mac/services/local_operator_bridge/ or equivalent
        |
        | calls existing P0026 implementation
        v
src/mac/tools/local_kvs_read.kvs_get_by_nat_octet(...)
        |
        v
http://192.168.86.240:80XX/rpc/KVS.Get?key=<key>
```

P0027 may implement a minimal MCP stdio server if practical with Python standard library only. If full MCP protocol support would require an external package or too much protocol work, Codex may instead implement a strict local JSON-RPC/stdin-stdout compatibility wrapper and document the gap. In that case, P0027 should still keep the function shape and safety model compatible with a later true MCP package.

The package must explicitly document whether it is:

```text
- true MCP stdio-compatible server
- MCP-shaped local JSON-RPC bridge POC
```

and what remains for a future package.

## Current behavior

P0026 created and live-verified a local Mac CLI/module for one read-only Shelly `KVS.Get` through the operator NAT convention.

The durable P0026 function contract is documented in:

```text
docs/functions/mac/local-kvs-read-poc.md
```

The implementation lives in:

```text
src/mac/tools/local_kvs_read/core.py
```

P0026 is verified live with:

```text
octet: 30
key: hp.price.status
result_status: success
result value: "ok"
```

## Problem

The project needs a controlled local bridge so ChatGPT/Codex-compatible clients can call safe local tools without turning the Mac into a generic shell, proxy or unrestricted device controller.

The safest next proof after P0026 is to expose the existing read-only KVS helper through a small local bridge interface while preserving all P0026 restrictions.

## Target behavior

Build Python standard-library Mac tooling that can:

1. start a local bridge process for operator/dev use
2. expose one tool named `shelly_kvs_get_by_nat_octet`
3. accept JSON input with only:
   - `octet`
   - `key`
   - optional `timeout`
4. call P0026 `kvs_get_by_nat_octet(...)`
5. return structured JSON with the P0026 result fields
6. preserve P0026 validation and audit logging
7. expose a simple list-tools/discovery response for the one tool
8. reject unknown tools
9. reject any additional operation that would imply writes or generic network access
10. include unit tests without requiring live local network access
11. document the bridge contract in `docs/functions/mac/`
12. create package-run evidence under `requirements/package-runs/P0027/`

Suggested manual command shape:

```bash
python3 -m src.mac.services.local_operator_bridge serve
```

or, if Codex chooses a Mac tools path instead of services for the POC:

```bash
python3 -m src.mac.tools.local_operator_bridge serve
```

Codex must choose and justify the path in `requirements/package-runs/P0027/design.md` before implementation.

## Non-goals

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
- No Mac local API bridge beyond the one P0026 KVS-read tool.
- No persistent production service/launchd installation.
- No external Python dependencies unless Codex stops with `WARN`/`STOP` and documents why standard library is insufficient.
- No G1 repository changes.

## Invariants

- Python standard library only unless the package stops before implementation and explicitly asks for a dependency decision.
- Read-only by construction.
- The bridge must call P0026 for Shelly KVS reads rather than duplicating network logic.
- The only supported bridge tool in P0027 is `shelly_kvs_get_by_nat_octet`.
- Unknown tool names must be rejected.
- The bridge must not accept a full arbitrary URL.
- The bridge must not expose any write-capable Shelly RPC.
- The bridge must not run arbitrary shell commands.
- Unit tests must run without local network/device access.
- Any live verification must be explicitly read-only and must use only `KVS.Get`.

## Knowledge updates

Create or update:

- `docs/functions/mac/local-operator-bridge.md`
- `docs/functions/00-index.md` if needed

Update only if a durable lesson is discovered:

- `memory/knowhow/shelly.md`
- `memory/knowhow/codex.md`
- `memory/device-management/mac-layer.md`

Do not update broad architecture memory unless the package establishes a durable bridge pattern that later packages must inherit.

## Implementation updates

Expected areas, final path to be chosen in design:

- `src/mac/services/local_operator_bridge/**` or `src/mac/tools/local_operator_bridge/**`
- `tests/mac/services/local_operator_bridge/**` or `tests/mac/tools/local_operator_bridge/**`
- `docs/functions/mac/local-operator-bridge.md`
- `docs/functions/00-index.md` if adding the bridge to the function catalog
- `requirements/package-runs/P0027/**`

The implementation must import/reuse P0026:

```text
src.mac.tools.local_kvs_read
```

## Files to inspect

- `README.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/08-context-bootstrap-modes.md`
- `memory/device-management/mac-layer.md`
- `memory/knowhow/shelly.md`
- `requirements/packages/P0026-mac-local-kvs-read-poc.md`
- `requirements/package-runs/P0026/CHANGELOG.md`
- `requirements/package-runs/P0026/review.md`
- `requirements/package-runs/P0026/design.md`
- `requirements/package-runs/P0026/functions.md`
- `requirements/package-runs/P0026/attempts.md`
- `docs/functions/mac/local-kvs-read-poc.md`
- `src/mac/tools/local_kvs_read/**`
- `tests/mac/tools/local_kvs_read/**`
- relevant existing `src/mac/tools/**`, `src/mac/services/**`, `tests/mac/tools/**`, and `tests/mac/services/**` structure

## Files allowed to change

- `src/mac/services/local_operator_bridge/**` or the equivalent P0027-specific path documented in design
- `src/mac/tools/local_operator_bridge/**` only if design chooses a tools path instead of services
- `tests/mac/services/local_operator_bridge/**` or the equivalent P0027-specific test path documented in design
- `tests/mac/tools/local_operator_bridge/**` only if design chooses a tools path instead of services
- `docs/functions/mac/local-operator-bridge.md`
- `docs/functions/00-index.md`
- `memory/knowhow/shelly.md` only for reusable lessons discovered during implementation/verification
- `memory/knowhow/codex.md` only for reusable lessons discovered during implementation/verification
- `memory/device-management/mac-layer.md` only for durable Mac bridge pattern documentation discovered by this package
- `requirements/package-runs/P0027/**`
- `requirements/packages/P0027-read-only-mcp-local-operator-bridge.md`

## Forbidden changes

- No G1 repository changes.
- No deploy artifact changes under `dep/s/**`.
- No Home Assistant changes.
- No Shelly runtime script changes.
- No live Shelly writes.
- No `KVS.Set` implementation.
- No `Script.*` implementation.
- No `Switch.*`, `Light.*`, `Cover.*`, relay, dimmer or actuator implementation.
- No component/config/device write implementation.
- No generic HTTP proxy.
- No arbitrary shell execution.
- No Codex package-runner implementation.
- No external Python package dependencies unless the package stops before implementation and asks for a dependency decision.
- No broad refactor outside the minimal P0027 bridge/test/docs scope.
- Do not read large data files, raw logs or spot-price fixtures for this package.

## Pre-implementation consistency review

Before editing, Codex must verify this package against repository truth and classify it as:

- `PASS`: consistent; continue implementation.
- `WARN`: implementable with stated minor uncertainty.
- `STOP`: inconsistent, unsafe, underspecified or out of scope; do not edit.

Required checks:

- P0026 is present and verified-local-live.
- P0027 reuses the P0026 implementation and does not duplicate/expand Shelly network access.
- Proposed bridge remains read-only and one-tool-only.
- Proposed files are inside Mac tooling/service/test/docs/package-run scope.
- The package does not create a generic local network, shell or device-control primitive.
- No live writes are required for verification.
- If true MCP compatibility cannot be implemented safely with standard library in the package scope, Codex must choose `WARN` or `STOP` and document the gap before implementation.

Store review evidence in:

```text
requirements/package-runs/P0027/review.md
```

## Implementation design policy

Codex must create package-scoped implementation design before coding:

```text
requirements/package-runs/P0027/design.md
```

The design must include:

```text
- chosen module path: service vs tool
- whether the implementation is true MCP stdio-compatible or MCP-shaped JSON-RPC POC
- protocol/message model
- tool discovery/list-tools model
- tool-call input schema
- output schema
- P0026 integration model
- validation and error mapping
- audit behavior inheritance from P0026
- explicit list of forbidden operations not implemented
- live-test boundary, if live test is attempted
```

## Function design policy

Codex must create package-scoped function design before coding:

```text
requirements/package-runs/P0027/functions.md
```

The function design must document intended functions such as:

```text
list_tools()
handle_tool_call(name, arguments)
handle_shelly_kvs_get_by_nat_octet(arguments)
read_json_message(...), if applicable
write_json_response(...), if applicable
serve(...), if applicable
main(argv=None)
```

Codex may choose different names, but equivalent responsibilities must be documented before implementation.

Update durable function documentation under `docs/functions/mac/local-operator-bridge.md` after implementation.

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

KVS read verification allowed: yes, but only through the P0027 bridge calling P0026 and only for one explicitly selected octet/key per command/test.

Max implementation/debug attempts: 3.

Codex must stop immediately if a live command would require any write-capable RPC, arbitrary URL, shell command, generic proxy or URL outside the P0026 NAT construction model.

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/P0027/
```

Expected evidence files:

```text
CHANGELOG.md
review.md
design.md
functions.md
attempts.md
```

If live verification is performed, record the bridge command/session, derived tool call, octet/key, result status and proof that only P0026 `KVS.Get` was invoked. Do not store large raw logs.

## Test cases

### TC1: Tool discovery exposes exactly one tool

Given the P0027 bridge
When a tool discovery/list-tools request is handled
Then the only supported tool is:

```text
shelly_kvs_get_by_nat_octet
```

### TC2: KVS tool delegates to P0026

Given a mocked P0026 `kvs_get_by_nat_octet` implementation
When the bridge handles `shelly_kvs_get_by_nat_octet` with octet/key
Then it calls P0026 exactly once with those inputs and returns the structured result.

### TC3: Unknown tool rejection

Given a request for any unknown tool name
When the bridge handles it
Then it returns a clear error and performs no Shelly/network operation.

### TC4: Write-like tool names are absent/rejected

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

When the bridge handles them
Then each is rejected and no network/shell/device operation is performed.

### TC5: No arbitrary URL input

Given arguments containing URL, host, path or method override fields
When the bridge validates the tool call
Then the bridge ignores/rejects unsupported fields and still only permits P0026 octet/key/timeout semantics.

### TC6: Protocol framing success

Given a valid local bridge request for `shelly_kvs_get_by_nat_octet`
When the bridge processes it through its selected protocol model
Then it returns a valid JSON/protocol response with the P0026 result payload.

### TC7: Protocol framing error handling

Given malformed JSON/protocol input
When the bridge processes it
Then it returns a clear local protocol error and performs no Shelly/network operation.

### TC8: Unit tests do not require live network

Given the test suite
When tests run
Then all bridge tests pass with mocked P0026 calls and no local network access.

### TC9: Optional read-only live bridge test

Given explicit octet/key for live verification
When Codex calls the bridge tool
Then the bridge performs exactly one read-only KVS.Get through P0026 and records the result.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/tools/local_kvs_read
python3 -m unittest discover tests/mac/tools
python3 -m unittest discover tests/mac/services
git diff --check
```

If the chosen bridge path is under `tests/mac/tools`, the service test command may be omitted and replaced with the equivalent package-scoped command, documented in `design.md` and `attempts.md`.

Optional live verification command must use a local bridge entry point and an explicit read-only KVS request. Codex must document exact command/session format after choosing the protocol model.

## Runtime health checks

For optional live read-only bridge verification, record:

- bridge command/session used
- tool name
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

This package creates a local Mac-side bridge POC. It may be run manually by Codex/operator for read-only verification. It must not install a persistent service or launchd job.

## Rollback plan

Rollback is a new forward-moving package if the bridge shape is wrong.

If implementation fails verification after allowed attempts, Codex must preserve useful package-run evidence and revert unverified source/test/doc changes unless the package evidence explicitly says a documentation-only finding should remain.

## Expected Codex output

- consistency review result: PASS/WARN/STOP
- whether the bridge is true MCP stdio-compatible or MCP-shaped JSON-RPC POC
- design path
- functions path
- files changed
- tests run
- verification results
- optional live bridge command/session and result, if live test performed
- package-run evidence paths created/updated
- function catalog update path
- uncertainty / skipped checks
- commit SHA after push, if successful and pushed
- diff summary

## Completion notes

Implemented as an MCP-shaped newline-delimited JSON-RPC bridge POC, not a true MCP stdio server.

Chosen path:

```text
src/mac/services/local_operator_bridge/
```

Supported bridge methods:

```text
tools/list
tools/call
```

Supported tool:

```text
shelly_kvs_get_by_nat_octet
```

The bridge delegates to P0026 `kvs_get_by_nat_octet(...)` and does not duplicate Shelly HTTP access.

Read-only live verification through the bridge succeeded for:

```text
tool: shelly_kvs_get_by_nat_octet
octet: 30
key: hp.price.status
timeout: 5
derived URL: http://192.168.86.240:8030/rpc/KVS.Get?key=hp.price.status
HTTP status: 200
result_status: success
result value: "ok"
```

No `KVS.Set`, `Script.*`, actuator call, arbitrary URL fetch, shell command, generic proxy, Codex runner, Home Assistant bridge or production service installation was implemented or used.
