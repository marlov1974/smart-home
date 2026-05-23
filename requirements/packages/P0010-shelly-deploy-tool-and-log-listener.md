# Package P0010: Shelly deploy tool and log listener

## Status
planned

## Package order
P0010

## Primary area
G2 / Mac tooling / Shelly live test tooling

## Decision summary

P0010 is not a separate design-only package. It is the first package that builds Mac-side tooling for deploying built Shelly scripts to a real Shelly device and listening to its debug log.

The first live target is the dampers device, which is allowed only as a safe test target. P0010 may deploy and run an inert hello script named `hello_v1_0_0` and verify that `hello` appears in the device log.

Script names must use semantic names and versions such as:

```text
installer_v2_0_0
hello_v1_0_0
```

Do not use `g2-*` script names.

## Solution model

P0010 adds a Mac-side live deploy/log tool that can:

1. take an already-built Shelly script
2. upload it to a Shelly device as a named script
3. start the script
4. listen to the Shelly debug log
5. verify expected log output

The test script is inert and exists only to prove deploy/start/log observation works.

This package does not implement the Shelly-side installer yet.

## Current behavior

P0008/P0009 can build and chunk Shelly scripts into generated deploy artifacts. There is not yet Mac-side tooling that pushes a built script to a Shelly device and verifies runtime log output.

## Problem

Before building the Shelly-side installer, we need a safe Mac-side deploy/log harness that can prove we can push inert code to a test device, start it, and observe logs without changing device settings or actuator state.

## Target behavior

Create Python 3 standard-library tooling that can:

- connect to a Shelly device over local HTTP/RPC
- upload a built script as `hello_v1_0_0`
- start `hello_v1_0_0`
- stream or poll the device debug log for a bounded time
- verify that expected text from the hello script appears in the log
- fail clearly if deploy, start or log verification fails
- use an inert hello fixture that only prints/logs
- record live-test evidence under `requirements/package-runs/P0010/`

The tool may be a new module or an extension under existing Mac tooling. Codex must choose and document the structure in `requirements/package-runs/P0010/design.md` before implementation.

## Script naming rule

Scripts installed by this package must be named exactly:

```text
hello_v1_0_0
```

Future installer script naming should follow the same pattern, e.g.:

```text
installer_v2_0_0
```

No `g2-` prefix should be used for script names.

## Dampers live-test boundary

The dampers device may be used only for inert script deploy/start/log verification.

Allowed live actions:

- read device status
- read script list/status
- create/update/delete only the `hello_v1_0_0` test script if needed
- upload inert hello code to `hello_v1_0_0`
- start/stop only `hello_v1_0_0`
- read or stream debug log

Forbidden live actions:

- no device setting changes
- no Wi-Fi/network/MQTT/Bluetooth changes
- no component/config changes unless explicitly added by a later package
- no actuator/output/switch/cover/relay RPC calls
- no real damper control code
- no script names other than `hello_v1_0_0` in this package
- no installer implementation or installer upload in this package

## Non-goals

- No Shelly-side installer implementation.
- No `installer_v2_0_0` deployment yet.
- No real damper code.
- No actuator or output control.
- No device configuration changes.
- No Home Assistant changes.
- No external Python packages.

## Invariants

- Python standard library only.
- Device writes are limited to the `hello_v1_0_0` script lifecycle.
- The hello script must be inert and only print/log.
- Live commands must be bounded and must not hang indefinitely.
- Live log capture must have a timeout.
- The package must be safe to run on dampers without changing physical state.

## Knowledge updates

Update if needed:

- `memory/knowhow/shelly.md`
- `memory/knowhow/codex.md`
- `docs/functions/mac/shelly-live-deploy-tool.md`

## Files to inspect

- `AGENTS.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `requirements/packages/P0008-g2-shelly-build-deploy-tools.md`
- `requirements/packages/P0009-shelly-build-wrapper-and-metadata.md`
- `src/mac/tools/shelly_build/**`
- `tests/mac/tools/shelly_build/**`
- `src/shelly/fixture/**`

## Files allowed to change

- `src/mac/tools/**`
- `tests/mac/tools/**`
- `src/shelly/fixture/**`
- `build/shelly/fixture/**`
- `dep/s/**`
- `docs/functions/**`
- `memory/knowhow/**`
- `requirements/package-runs/P0010/**`
- `requirements/packages/P0010-shelly-deploy-tool-and-log-listener.md`

## Forbidden changes

- no G1 repository changes
- no real FTX runtime source changes
- no Shelly-side installer implementation
- no device configuration changes
- no actuator/output control code
- no script names other than `hello_v1_0_0` for live deployment in this package
- no external Python package dependencies

## Codex phase requirements

Codex must create these before implementation:

```text
requirements/package-runs/P0010/review.md
requirements/package-runs/P0010/design.md
requirements/package-runs/P0010/functions.md
```

Use the P0007 phase-gate model.

## Live test/debug policy

Live testing allowed: yes, dampers only

Live write actions allowed: yes, but only for the `hello_v1_0_0` script lifecycle described above

Shelly log capture required: yes

Max implementation/debug attempts: 3

Codex must stop immediately if it cannot identify the dampers device endpoint safely or if any required live command would exceed the allowed action list.

## Test cases

### TC1: Build inert hello script
Given the hello fixture
When the build tool runs
Then it produces a complete wrapped built script for `hello_v1_0_0` or equivalent fixture source selected by the deploy tool.

### TC2: Deploy tool dry-run or unit tests
Given a mocked or local testable deploy client
When deploy/start/log functions are tested
Then they build correct bounded HTTP/RPC requests and reject forbidden operations.

### TC3: Live dampers deploy
Given the dampers device endpoint is known
When the deploy tool uploads `hello_v1_0_0`
Then the device script list/status shows `hello_v1_0_0` present.

### TC4: Live dampers start and log observation
Given `hello_v1_0_0` is installed
When the tool starts it and listens to the log
Then the expected `hello` log output is observed within the timeout.

### TC5: No forbidden operations
Given the package live boundary
When reviewing tool code and logs
Then there are no device settings changes and no actuator/output/relay/cover/switch RPC calls.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/fixture/manifest.json --build-root build/shelly/fixture --dep-root dep/s
git diff --check
```

For live dampers test, Codex must document the exact command it ran, the target endpoint, log timeout, observed log evidence and final script status.

## Runtime health checks

During live test, check and record:

- target endpoint used
- script list/status before and after
- deploy/start result
- bounded log excerpt containing expected hello output
- absence of forbidden RPC calls in the package/tool/log evidence

## Deployment plan

No production deployment. This is a controlled live test on dampers only.

## Rollback plan

After live test, Codex should either leave `hello_v1_0_0` installed if the package explicitly documents it as harmless test residue, or remove only `hello_v1_0_0` if the implemented tool supports safe removal and the package-run design chooses cleanup.

Codex must not remove or alter unrelated scripts.

## Expected Codex output

- PASS/WARN/STOP review
- design path
- functions path
- files changed
- tests run
- live test command and target endpoint
- log evidence path
- verification results
- commit SHA after push
- uncertainty
- diff summary

## Completion notes

Filled after implementation.
