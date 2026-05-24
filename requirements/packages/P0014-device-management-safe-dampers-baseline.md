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
restore output state when rebooted: enabled
number component: House Temp
```

This package is intentionally narrow. It should prove that Mac tooling can plan, apply and verify safe configuration on one Shelly device without touching physical outputs.

P0014 is also an API-discovery and device-management proof. It tests whether Mac tooling can safely set device/channel names, restore-output behavior and create a non-actuating number component.

## Target device

```text
infrastructure role / logical device candidate: ftx-dampers
physical Shelly id: 8813bfd99f54
stable LAN address: 192.168.77.30
```

The stable Shelly LAN address is `192.168.77.30`.

The endpoint used by a Mac to reach that device is execution-environment knowledge, not durable package truth. The current Mac may be outside the `192.168.77.0/24` network and may need a translated/NAT access endpoint known to the operator or current Codex environment. A future Mac on `192.168.77.0/24` should normally use the direct LAN endpoint.

P0014 must not hardcode a translated outside endpoint as package truth or device identity.

The device-management tool must support explicit runtime endpoint selection, for example:

```text
--base-url <reachable endpoint for this Mac right now>
```

Future device-management tooling may add an access resolver/profile, but P0014 must at minimum keep these separate:

```text
stable device network address: 192.168.77.30
physical Shelly id: 8813bfd99f54
runtime access endpoint: supplied by operator/Codex for current Mac environment
verified physical device identity/status: read from Shelly before live writes
```

Codex must confirm the target device from repository memory and live device identity/status before applying changes. The package must not identify the device by runtime endpoint alone.

## Naming model for this package

G2 must distinguish between device identity and Shelly display/config names.

P0014 uses these exact values:

```text
physical Shelly id: 8813bfd99f54
stable infrastructure role: ftx-dampers
Shelly device name to set/test: ftx_dampers
Shelly channel name to set/test: dampers
```

The underscore device name is a deliberate test value for the live device-management API behavior. It is not yet a final naming standard for every G2 device.

If P0014 succeeds, a later package may standardize whether Shelly device display names should use kebab-case logical names, underscore variants, or another convention. Until then, stable repository identity remains the logical/infrastructure role, not the test display name.

## Required behavior

Build or extend Python standard-library Mac tooling that can:

1. read current relevant device state from a runtime `--base-url`
2. verify the target physical Shelly id `8813bfd99f54` and status before writes
3. produce a plan for the P0014 baseline
4. apply only the P0014 baseline changes
5. verify readback after apply
6. run a second time idempotently
7. store evidence under `requirements/package-runs/P0014/`

The tool must discover and document the exact Shelly RPC/API calls for device name, channel name, restore-output-on-reboot behavior and number component creation before live apply.

If the API for any requested setting/component is unclear or unsupported, Codex must stop before applying that item.

The tool should accept an explicit `--base-url` or equivalent runtime argument. It should not require any translated outside endpoint to be stored as durable device identity.

## Restore-output requirement

`restore state when rebooted` means restore output state after reboot.

If the output is on/open before reboot, the Shelly should restore that output state after boot so the FTX does not need to treat a short device reboot as a full ventilation-system failure.

Expected physical/system behavior:

```text
If dampers reboots while dampers are open/on:
  dampers may begin closing briefly during the reboot gap
  after Shelly boot, the output should restore on/open
  other FTX devices such as fans, heating battery and VVX should not need to adapt to this short reboot transient
```

P0014 must identify the exact Shelly setting that controls this output restore behavior. It must not change any actuator state directly while configuring or verifying it.

If the relevant setting cannot be found or read back safely, Codex must stop before applying that item.

## Allowed live changes

On dampers only, P0014 may:

- set Shelly device name to `ftx_dampers`
- set channel name to `dampers`
- enable restore output state when rebooted
- create or verify one non-actuating number component named `House Temp`
- read back relevant status/config/component state

P0014 must not change actuator state or perform broad unrelated configuration.

## Component requirement

Create or verify a number component named:

```text
House Temp
```

Current P0014 purpose:

```text
Test that the Mac device-management tool can create a user component on a Shelly device.
```

Future intended G2 meaning:

`House Temp` is expected to become a desired house temperature input used by the future G2 FTX control device. Later G2 control may use this value to influence FTX, heat pumps and floor cooling. P0014 does not implement that behavior.

For P0014, `House Temp` is not authoritative control input and must not affect any runtime control.

If a neutral initial value is required by the Shelly API, Codex must choose a harmless value and document it in design/evidence.

If the API requires range/unit/persistence metadata, Codex must document the chosen values before apply. Suggested harmless baseline, if supported:

```text
unit: C or °C according to Shelly API support
range: 10..30
initial value: 21
persisted: yes, if the API supports persistence for number components
```

If user-created number components are unsupported on dampers, Codex must stop and report evidence instead of substituting another component type.

## Known non-P0014 design areas

Floor cooling remains in inventory/design-waiting state. Some ordered devices are not yet installed or physically connected. P0014 must not begin floor-cooling control design or implementation.

Heat-pump Smart Grid control requires a later manual/operator verification step before G2 live control packages. The heat pumps must continue functioning in their current unmanaged/ostyrt operating mode until the project is ready for that verification and control migration.

## Non-goals

- No production rollout beyond dampers.
- No Home Assistant changes.
- No Shelly runtime script changes.
- No physical-control logic.
- No floor-cooling design or implementation.
- No heat-pump Smart Grid control implementation.
- No broad multi-device registry.
- No external Python packages.

## Invariants

- Python standard library only.
- Idempotent plan/apply/verify behavior.
- Exact APIs must be documented before apply.
- Before/after evidence is required.
- Stable LAN address and physical Shelly id are device identity facts; runtime endpoints are execution-environment access knowledge.
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
- no floor-cooling control changes
- no heat-pump control changes
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
Runtime access endpoint selection
Shelly API/RPC discovery
Plan/apply/verify model
Restore-output read/write/readback model
House Temp component contract
Idempotency model
Rollback/cleanup model
```

## Live test/debug policy

Live testing allowed: yes, dampers only.

Live changes allowed: only the P0014 baseline listed above.

Max implementation/debug attempts: 3.

Codex must stop immediately if the target device, physical Shelly id or required APIs cannot be confirmed safely.

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

### TC4: Apply and verify restore output behavior
Given dampers current state
When P0014 applies
Then readback verifies restore output state when rebooted is enabled.

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
Then it verifies physical Shelly id `8813bfd99f54` and does not treat the runtime endpoint as durable device identity.

### TC8: No actuator-state change
Given the restore-output setting is configured
When P0014 applies and verifies it
Then the tool does not perform output/switch/relay on/off operations to test physical state.

## Verification commands

Codex must define final commands in design, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/tools
git diff --check
```

Live evidence must include runtime base URL used, stable LAN address, physical Shelly id, device identity/status evidence, before-state summary, plan, after-state summary, idempotent rerun result and final status.

## Rollback plan

If a baseline setting is applied incorrectly, rollback must use the before-state evidence and remain inside the P0014 scope. Do not perform power-cycle testing.

If an incorrect duplicate `House Temp` component is created, Codex may remove only the duplicate it created if the API supports safe removal and evidence identifies it unambiguously. Otherwise stop and report.

## Expected Codex output

- PASS/WARN/STOP review
- design path
- functions path
- runtime base URL used for this Mac execution
- stable LAN address and physical Shelly id verification
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
