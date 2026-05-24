# Package P0014: Device management safe dampers baseline

## Status
planned

## Package order
P0014

## Primary area
G2 / Mac tooling / Shelly device management

## Decision summary

P0014 extends Mac-side device management so it can apply a small, explicitly allowed baseline to the dampers lab device.

Target baseline:

```text
device name: ftx_dampers
channel name: dampers
restore state when rebooted: enabled
number component: House Temp
```

This package is intentionally narrow. It should prove that Mac tooling can plan, apply and verify safe configuration on one Shelly device without touching physical outputs.

## Target device

```text
logical device: dampers
stable LAN address: 192.168.77.30
current outside-Mac access knowledge: current Mac may need to reach the device through the existing outside/NAT endpoint
```

The stable Shelly LAN address is `192.168.77.30`. The current Mac is outside the `192.168.77.0/24` network and may need local/operator knowledge to translate that LAN address to the currently reachable endpoint, for example the existing `192.168.86.240:8030` access path.

That translated outside endpoint is not the device identity and must not be treated as hardcoded repository truth. It is Mac/Codex access knowledge for the current execution environment.

Future Macs on `192.168.77.0/24` should normally use the direct LAN endpoint:

```text
http://192.168.77.30/
```

Codex must confirm the target device from repository memory and from live device identity/status before applying changes. The package must not identify the device by outside endpoint alone.

## Required behavior

Build or extend Python standard-library Mac tooling that can:

1. read current relevant device state
2. produce a plan for the P0014 baseline
3. apply only the P0014 baseline changes
4. verify readback after apply
5. run a second time idempotently
6. store evidence under `requirements/package-runs/P0014/`

The tool must discover and document the exact Shelly RPC/API calls for device name, channel name, restore-on-reboot behavior and number component creation before live apply.

If the API for any requested setting/component is unclear or unsupported, Codex must stop before applying that item.

The tool should accept an explicit `--base-url` or equivalent runtime argument. It should not require the outside translated endpoint to be stored as durable device identity.

## Allowed live changes

On dampers only, P0014 may:

- set device name to `ftx_dampers`
- set channel name to `dampers`
- enable restore state when rebooted
- create or verify one non-actuating number component named `House Temp`
- read back relevant status/config/component state

P0014 must not change actuator state or perform broad unrelated configuration.

## Component requirement

Create or verify a number component named:

```text
House Temp
```

If a neutral initial value is required by the Shelly API, Codex must choose a harmless value and document it in design/evidence.

If user-created number components are unsupported on dampers, Codex must stop and report evidence instead of substituting another component type.

## Non-goals

- No production rollout beyond dampers.
- No Home Assistant changes.
- No Shelly runtime script changes.
- No physical-control logic.
- No broad multi-device registry.
- No external Python packages.

## Invariants

- Python standard library only.
- Idempotent plan/apply/verify behavior.
- Exact APIs must be documented before apply.
- Before/after evidence is required.
- Stable LAN address is device network truth; outside translated endpoints are execution-environment access knowledge.
- Failed-package cleanup from `memory/05-package-lifecycle.md` applies if verification fails after allowed attempts.

## Files to inspect

- `AGENTS.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/device-management/identity-and-registry.md`
- `memory/device-management/mac-layer.md`
- `memory/infrastructure/devices.md`
- `src/mac/tools/shelly_live/**`
- `tests/mac/tools/shelly_live/**`
- Shelly API documentation or observed RPC schema for the target APIs

## Files allowed to change

- `src/mac/tools/**`
- `tests/mac/tools/**`
- `docs/functions/**`
- `memory/device-management/**`
- `memory/knowhow/**`
- `requirements/package-runs/P0014/**`
- `requirements/packages/P0014-device-management-safe-dampers-baseline.md`

## Forbidden changes

- no G1 repository changes
- no Shelly runtime script changes
- no Home Assistant changes
- no external Python package dependencies
- no broad refactor outside Mac device-management tooling needed for P0014
- do not rewrite previous package-run evidence

## Codex phase requirements

Codex must create these before implementation:

```text
requirements/package-runs/P0014/review.md
requirements/package-runs/P0014/design.md
requirements/package-runs/P0014/functions.md
```

The design must include:

```text
Target device confirmation
Access endpoint selection
Shelly API/RPC discovery
Plan/apply/verify model
Idempotency model
Rollback/cleanup model
```

## Live test/debug policy

Live testing allowed: yes, dampers only.

Live changes allowed: only the P0014 baseline listed above.

Max implementation/debug attempts: 3.

Codex must stop immediately if the target device or required APIs cannot be confirmed safely.

## Test cases

### TC1: Plan output
Given current dampers state
When the tool runs in plan mode
Then it reports the exact baseline changes needed.

### TC2: Allowlist enforcement
Given a requested change outside the P0014 baseline
When the plan is validated
Then the tool rejects it before apply.

### TC3: Apply and verify names
Given dampers current state
When P0014 applies
Then readback verifies device name `ftx_dampers` and channel name `dampers`.

### TC4: Apply and verify restore behavior
Given dampers current state
When P0014 applies
Then readback verifies restore state when rebooted is enabled.

### TC5: Apply and verify number component
Given dampers current state
When P0014 applies
Then readback verifies a number component named `House Temp` exists.

### TC6: Idempotent rerun
Given P0014 has already applied successfully
When the tool runs again
Then it reports no required changes or makes no unnecessary writes.

### TC7: Endpoint is not device identity
Given the tool receives a runtime base URL
When it plans/applies P0014
Then it still verifies the target device identity/status and does not treat the outside translated endpoint as durable device identity.

## Verification commands

Codex must define final commands in design, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/tools
git diff --check
```

Live evidence must include base URL used, stable LAN address, device identity/status evidence, before-state summary, plan, after-state summary, idempotent rerun result and final status.

## Rollback plan

If a baseline setting is applied incorrectly, rollback must use the before-state evidence and remain inside the P0014 scope. Do not perform power-cycle testing.

If an incorrect duplicate `House Temp` component is created, Codex may remove only the duplicate it created if the API supports safe removal and evidence identifies it unambiguously. Otherwise stop and report.

## Expected Codex output

- PASS/WARN/STOP review
- design path
- functions path
- base URL used for this Mac execution
- stable LAN address and identity/status verification
- discovered APIs/RPCs
- files changed
- tests run
- plan/apply command and target endpoint
- before/after evidence path
- idempotent rerun result
- verification result
- commit SHA after push, or evidence-only stopped commit SHA if failed
- uncertainty
- diff summary

## Completion notes

Filled after implementation.
