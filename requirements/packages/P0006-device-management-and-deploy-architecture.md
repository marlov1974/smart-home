# Package P0006: Device management and deploy architecture

## Status
implemented

## Package order
P0006

## Primary area
G2 device management / Shelly deploy / Mac tooling architecture

## Linked requirements

Epic:
- none yet

Features:
- none yet

User stories:
- none yet

## Decision summary

G2 Shelly device management is declarative and installer-driven.

Major decisions:

- Stable identity is the logical device name, not physical Shelly id.
- `dep/s/reg/d.json` maps physical Shelly id to logical device and per-device target version.
- Device replacement should normally require changing only the registry mapping.
- Each logical device has split desired-state files under `dep/s/dev/<logical>/`.
- Local Shelly installer state uses one persistent text component that stores only last verified target version.
- KVS is runtime/cache/bootstrap state, not installer truth.
- Shelly source, built script and deploy chunks are three separate layers.
- Deploy chunks are generated numeric byte-size chunks such as `01.js`, `02.js`.
- Recipes only need chunk count.
- Deploy/build tooling is Mac code and should be built deterministically, not manually improvised by an LLM.
- Mac tools and Mac services are both first-class G2 code. A package may update Mac and Shelly code together.

## Solution model

Shelly installer flow:

```text
own physical id -> dep/s/reg/d.json -> logical device + target version -> local state check -> dep/s/dev/<logical>/i.json -> apply desired parts -> verify -> write local verified version last
```

Shelly code flow:

```text
src/shelly logical source -> build complete script -> dep/s numeric chunks
```

Mac layer includes build/deploy tools, forecast services, diagnostics and future ML/POC services.

## Current behavior

Earlier G2 memory defined package workflow, physical baseline and Codex evidence policies, but not the G2 device-management architecture or new source/build/deploy separation.

## Problem

G2 will have many Shelly devices and must support hardware replacement, compact deploy files, installer convergence, generated chunks and cross-environment packages.

A single device-id-named manifest and hand-maintained logical chunks would not scale.

## Target behavior

G2 documentation defines:

- logical vs physical identity
- compact device registry
- per-device target version
- split desired-state files
- minimal local installer state
- KVS policy
- source/build/deploy layers
- Mac tooling/service model

## Non-goals

- No implementation of installer code.
- No implementation of Python build tools.
- No generated `dep/s/` artifacts yet.
- No live device access.
- No G1 repository changes.

## Invariants

- Shelly devices fetch from `dep/s/` only.
- Stable device identity is logical device name.
- Physical Shelly id is replaceable.
- KVS must not be the only installer truth.
- Installer writes local verified version only after successful convergence.
- Deploy chunks are generated artifacts and should not encode source architecture.
- Code changes still belong to exactly one package.

## Knowledge updates

Created:

- `memory/device-management/00-index.md`
- `memory/device-management/identity-and-registry.md`
- `memory/device-management/installer-model.md`
- `memory/device-management/local-state.md`
- `memory/device-management/shelly-deploy-structure.md`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`

Updated:

- `memory/00-index.md`
- `memory/01-system-overview.md`
- `memory/02-design-principles.md`

## Implementation updates

None.

## Files to inspect

- `memory/device-management/00-index.md`
- `memory/device-management/identity-and-registry.md`
- `memory/device-management/installer-model.md`
- `memory/device-management/local-state.md`
- `memory/device-management/shelly-deploy-structure.md`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `memory/00-index.md`
- `memory/01-system-overview.md`
- `memory/02-design-principles.md`

## Files allowed to change

- `memory/device-management/**`
- `memory/00-index.md`
- `memory/01-system-overview.md`
- `memory/02-design-principles.md`
- `memory/bootstrap-manifest.json`
- this package file

## Forbidden changes

- no source code changes
- no deploy artifact changes
- no live device access
- no G1 repository changes

## Pre-implementation consistency review

This package is consistent if it:

- preserves package-driven workflow
- preserves G1/G2 boundary
- keeps Shelly deploy paths under `dep/s/`
- keeps `src/` and deploy artifacts separate
- supports device replacement by changing physical-to-logical mapping
- avoids using KVS as installer truth

## Live test/debug policy

Live testing allowed:
no

Live write actions allowed:
no

Shelly log capture required:
no

Max implementation/debug attempts:
3

## Evidence and learning policy

No package-run evidence is required for this documentation-only package.

## Test cases

### TC1: Device replacement is documented
Given a physical Shelly device fails
When reading `memory/device-management/identity-and-registry.md`
Then it explains that changing `dep/s/reg/d.json` can map a new physical id to the same logical device.

### TC2: Local state is minimal
Given a future installer design
When reading `memory/device-management/local-state.md`
Then local state stores only schema and verified device target version.

### TC3: Deploy chunks are generated numeric chunks
Given a future Shelly build package
When reading `memory/device-management/source-build-deploy-layers.md`
Then chunks are generated from complete built scripts and named `01.js`, `02.js`, etc.

### TC4: Mac tools are first-class G2 code
Given future Shelly build tooling or spot forecast work
When reading `memory/device-management/mac-layer.md`
Then Mac tools and Mac services are both part of the Mac layer.

## Verification commands

```bash
git grep -n "dep/s/reg/d.json" memory/device-management
git grep -n "1|49" memory/device-management/local-state.md
git grep -n "01.js" memory/device-management/source-build-deploy-layers.md memory/device-management/shelly-deploy-structure.md
git grep -n "Mac tools" memory/device-management/mac-layer.md memory/01-system-overview.md
```

## Runtime health checks

No live runtime test.

## Deployment plan

No runtime deploy.

## Rollback plan

If the device-management model changes, create a new forward package that supersedes or refines this architecture.

## Expected Codex output
- consistency review result: PASS/WARN/STOP
- understanding summary
- files changed
- tests run
- verification results
- uncertainty / skipped checks
- diff summary

## Completion notes

P0006 documents the G2 device-management, installer, deploy registry, local state and source/build/deploy architecture decisions.
