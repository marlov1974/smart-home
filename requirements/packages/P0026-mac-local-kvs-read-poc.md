# Package P0026: Mac local KVS read POC

## Status

planned

## Package order

P0026

## Primary area

G2 / Mac tooling / local operator bridge / Shelly diagnostics

## Linked requirements

Epic:
- E0001

Features:
- F0001

User stories:
- US0001

## Decision summary

Create a minimal proof of concept that lets the local Mac read one Shelly KVS key through the existing operator-side NAT convention:

```text
http://192.168.86.240:80XX/rpc/KVS.Get?key=<key>
```

where `XX` is the last octet of the Shelly device's internal technical-network IP address.

Examples:

```text
internal 192.168.77.40 -> operator URL http://192.168.86.240:8040/
internal 192.168.77.30 -> operator URL http://192.168.86.240:8030/
```

This package is intentionally read-only. It must not introduce any Shelly write capability, device-control capability, generic HTTP proxy, or broad local operator bridge.

## Solution model

P0026 introduces a small Mac-side tool/service module that exposes one safe operation:

```text
shelly_kvs_get_by_nat_octet(octet, key)
```

The tool derives the runtime endpoint from the fixed operator NAT host and the supplied internal-IP last octet:

```text
base host: 192.168.86.240
port:      80XX
path:      /rpc/KVS.Get
query:     key=<url-encoded KVS key>
```

The implementation should be useful both as a CLI/debug helper and as the first read-only building block for a later local MCP/operator bridge.

P0026 must keep these layers separate:

```text
stable/internal device address: 192.168.77.XX
operator-side runtime endpoint: http://192.168.86.240:80XX/
KVS key: user-supplied key string for KVS.Get only
```

This package may use octet-based addressing only for the POC. It does not need to implement full logical device lookup or device-registry resolution.

## Current behavior

The repository documents the operator NAT pattern, and previous packages have used direct Mac/Shelly HTTP/RPC access for live verification. However, there is no minimal reusable local tool whose only job is to read a KVS key from a NAT-derived Shelly endpoint.

## Problem

Future ChatGPT/Codex/local operator workflows need a very small, verifiable first bridge into local devices. Starting with full MCP, Codex orchestration, Shelly writes, dimming, switch control, or arbitrary local HTTP access would be too broad and unsafe.

The safe first proof is:

```text
read one KVS key from one explicitly selected Shelly octet
```

## Target behavior

Build Python standard-library Mac tooling that can:

1. accept an octet and KVS key as explicit inputs
2. validate the octet as an integer in `1..254`
3. construct the NAT base URL as `http://192.168.86.240:80XX/`
4. URL-encode the KVS key safely
5. perform only `KVS.Get`
6. use a bounded timeout
7. parse the Shelly JSON-RPC response when possible
8. return or print a clear success/failure result
9. audit-log each call with timestamp, octet, key, built URL, HTTP status, result status and error summary if any
10. provide unit tests that do not require a live Shelly device
11. document the function/tool contract in `docs/functions/mac/`
12. store package-run evidence under `requirements/package-runs/P0026/`

Suggested CLI shape:

```bash
python3 -m src.mac.tools.local_kvs_read get --octet 40 --key hp.price.status
```

Codex may choose the exact module name and command shape in `requirements/package-runs/P0026/design.md`, but the tool must remain narrow and read-only.

## Non-goals

- No MCP server implementation is required in P0026.
- No Codex-runner integration.
- No Shelly writes.
- No `KVS.Set`.
- No `Script.*` operations.
- No `Switch.*`, `Light.*`, `Cover.*`, relay, dimmer or actuator operations.
- No component creation/update/delete.
- No device configuration changes.
- No generic HTTP proxy or arbitrary URL input.
- No Home Assistant changes.
- No G1 repository changes.
- No logical device registry implementation beyond optional documentation notes.
- No production service/launchd installation.

## Invariants

- Python standard library only.
- Read-only by construction.
- Runtime URL must be derived only from fixed host `192.168.86.240`, fixed path `/rpc/KVS.Get`, supplied octet, and supplied KVS key.
- The tool must not accept a full arbitrary URL.
- The tool must not expose any write-capable Shelly RPC.
- The tool must have an HTTP timeout and must not hang indefinitely.
- The tool must audit-log live calls.
- Unit tests must run without local network/device access.
- Any live test must be explicitly documented and must read only the requested KVS key.

## Knowledge updates

Update or create if useful:

- `docs/functions/mac/local-kvs-read-poc.md`
- `memory/knowhow/shelly.md` only if Codex discovers a reusable Shelly KVS/RPC lesson
- `memory/device-management/mac-layer.md` only if the package establishes a durable Mac-layer pattern beyond this POC

Do not update broad architecture memory unless the implementation discovers a durable decision that future packages must inherit.

## Implementation updates

Expected areas:

- `src/mac/tools/local_kvs_read/**` or an equivalent narrow Mac tool path chosen in design
- `tests/mac/tools/local_kvs_read/**` or equivalent tests
- `docs/functions/mac/local-kvs-read-poc.md`
- `requirements/package-runs/P0026/**`

## Files to inspect

- `README.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/08-context-bootstrap-modes.md`
- `memory/infrastructure/network.md`
- `memory/infrastructure/router-nat.md`
- `memory/infrastructure/devices.md`
- `memory/device-management/mac-layer.md`
- `memory/knowhow/shelly.md`
- `requirements/packages/TEMPLATE.md`
- relevant existing `src/mac/tools/**` and `tests/mac/tools/**` structure

## Files allowed to change

- `src/mac/tools/local_kvs_read/**` or the equivalent P0026-specific Mac tool path documented in design
- `tests/mac/tools/local_kvs_read/**` or the equivalent P0026-specific test path documented in design
- `docs/functions/mac/local-kvs-read-poc.md`
- `docs/functions/00-index.md` if adding the new function document requires indexing
- `memory/knowhow/shelly.md` only for reusable lessons discovered during implementation/verification
- `memory/device-management/mac-layer.md` only for durable Mac-layer pattern documentation discovered by this package
- `requirements/package-runs/P0026/**`
- `requirements/packages/P0026-mac-local-kvs-read-poc.md`

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
- No external Python package dependencies.
- No broad refactor outside the minimal P0026 tool/test/docs scope.
- Do not read large data files, raw logs or spot-price fixtures for this package.

## Pre-implementation consistency review

Before editing, Codex must verify this package against repository truth and classify it as:

- `PASS`: consistent; continue implementation.
- `WARN`: implementable with stated minor uncertainty.
- `STOP`: inconsistent, unsafe, underspecified or out of scope; do not edit.

Required checks:

- NAT convention matches `memory/infrastructure/router-nat.md`.
- Read-only behavior is consistent with live-action safety rules.
- Proposed files are inside Mac tooling/test/docs/package-run scope.
- The tool does not create a generic local network access primitive.
- No live writes are required for verification.

Store review evidence in:

```text
requirements/package-runs/P0026/review.md
```

## Implementation design policy

Codex must create package-scoped implementation design before coding:

```text
requirements/package-runs/P0026/design.md
```

The design must include:

```text
- chosen module/CLI structure
- URL construction model
- input validation model
- KVS key encoding model
- HTTP timeout/error model
- JSON response handling model
- audit-log model
- live-test boundary, if live test is attempted
- explicit list of forbidden RPC methods not implemented
```

## Function design policy

Codex must create package-scoped function design before coding:

```text
requirements/package-runs/P0026/functions.md
```

The function design must document at least:

```text
build_nat_base_url(octet)
build_kvs_get_url(octet, key)
kvs_get_by_nat_octet(octet, key, timeout)
write_audit_record(...)
CLI entrypoint function(s), if any
```

Codex may choose different names, but equivalent responsibilities must be documented before implementation.

Update durable function documentation under `docs/functions/mac/local-kvs-read-poc.md` after implementation.

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

KVS read verification allowed: yes, but only for one explicitly selected octet/key per command.

Max implementation/debug attempts: 3.

Codex must stop immediately if a live command would require any write-capable RPC or a URL outside the fixed P0026 NAT construction model.

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/P0026/
```

Expected evidence files:

```text
CHANGELOG.md
review.md
design.md
functions.md
attempts.md
```

If live verification is performed, record the live command and result in `attempts.md` or a focused log/evidence file. Do not store large raw logs.

## Test cases

### TC1: NAT base URL construction

Given octet `40`
When the URL builder runs
Then it returns:

```text
http://192.168.86.240:8040/
```

Given octet `30`
When the URL builder runs
Then it returns:

```text
http://192.168.86.240:8030/
```

### TC2: Octet validation

Given octets outside `1..254`, non-integers or malformed values
When validation runs
Then the tool rejects them before making any HTTP request.

### TC3: KVS key URL encoding

Given a KVS key containing dots or characters requiring URL encoding
When the request URL is built
Then the key is encoded only as a query parameter for `/rpc/KVS.Get`.

### TC4: No arbitrary URL input

Given a caller tries to supply a full URL, host, path or method override
When the tool validates inputs
Then it rejects or ignores that attempt and still only supports the fixed NAT host/path model.

### TC5: HTTP success parsing

Given a mocked Shelly HTTP response for `KVS.Get`
When the tool reads it
Then it returns the parsed JSON-RPC result/value and records a success audit entry.

### TC6: HTTP and JSON error handling

Given mocked HTTP timeout, non-200 status, malformed JSON or Shelly error object
When the tool reads it
Then it returns a clear failure result and records an audit entry.

### TC7: Write RPCs are absent

Given the implemented P0026 module
When tests/search inspect supported operations
Then no `KVS.Set`, `Script.*`, `Switch.*`, `Light.*`, `Cover.*`, component/config/device write helpers or generic HTTP proxy are implemented.

### TC8: Optional live KVS read

Given an explicit octet and key provided for live verification
When Codex runs the tool
Then it performs exactly one read-only `KVS.Get` request through the derived NAT URL and records status/result evidence.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m unittest discover tests/mac/tools/local_kvs_read
git diff --check
```

If the chosen test path differs, use the equivalent package-scoped test command and document it.

Optional live verification command shape:

```bash
python3 -m src.mac.tools.local_kvs_read get --octet 40 --key <explicit-key> --timeout 5
```

Live verification is not required if the local network/device is unavailable. If skipped, Codex must state why and rely on unit tests.

## Runtime health checks

For optional live read-only verification, record:

- octet
- KVS key
- derived URL
- timeout used
- HTTP status or connection error
- parsed Shelly result or error summary
- proof that no write-capable RPC was called

No actuator/device state checks are required because the package is read-only.

## Deployment plan

No production deployment.

This package creates a local Mac-side POC tool. It may be run manually by Codex/operator for read-only verification. It must not install a persistent service or launchd job.

## Rollback plan

Rollback is a new forward-moving package if the POC shape is wrong.

If implementation fails verification after allowed attempts, Codex must preserve useful package-run evidence and revert unverified source/test/doc changes unless the package evidence explicitly says a documentation-only finding should remain.

## Expected Codex output

- consistency review result: PASS/WARN/STOP
- design path
- functions path
- files changed
- tests run
- verification results
- optional live command and derived URL, if live test performed
- audit-log evidence summary
- package-run evidence paths created/updated
- function catalog update path
- uncertainty / skipped checks
- commit SHA after push, if successful and pushed
- diff summary

## Completion notes

To be filled after implementation.
