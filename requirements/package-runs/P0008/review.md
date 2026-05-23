# Package P0008 Review Evidence

## Package

`P0008`

## Consistency result

PASS

## Files checked

- `AGENTS.md`
- `README.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `memory/device-management/shelly-deploy-structure.md`
- `requirements/packages/P0006-device-management-and-deploy-architecture.md`
- `requirements/packages/P0007-codex-phased-package-build-process.md`
- `requirements/packages/P0008-g2-shelly-build-deploy-tools.md`
- `requirements/package-runs/TEMPLATE-review.md`
- `requirements/package-runs/TEMPLATE-design.md`
- `requirements/package-runs/TEMPLATE-functions.md`

## Checks

### Package vs memory

P0008 matches the documented G2 source/build/deploy separation:

```text
src/shelly/ -> build/shelly/ -> dep/s/
```

The package keeps Mac build tooling as first-class G2 code and keeps Shelly devices fetching only from deploy artifacts under `dep/s/`.

### Package vs linked requirements

P0008 follows P0006 by implementing generated numeric Shelly chunks and compact recipes. It follows P0007 by requiring package-run review, implementation design and function design before implementation.

### Package vs previous packages

P0001-P0007 establish the repository, G1/G2 boundary, package lifecycle, evidence storage and device-management architecture. P0008 is the first implementation package for the Shelly build/deploy tooling and does not contradict earlier package outcomes.

### Package vs implementation/deploy structure

The repository currently has no `src/`, `build/`, `dep/` or `tests/` implementation tree. P0008 explicitly allows creating only the needed package-scoped paths:

- `src/mac/tools/shelly_build/**`
- `tests/mac/tools/shelly_build/**`
- `src/shelly/fixture/**`
- `build/shelly/fixture/**`
- `dep/s/ch/hello/**`
- `dep/s/rec/hello.json`

### Package vs G1/G2 boundary

The package is contained in `marlov1974/smart-home`, forbids G1 changes and does not claim that G2 deploy tooling describes current G1 runtime behavior.

### Package vs invariants

The requested tooling can satisfy the invariants:

- Python standard library only
- deterministic build output
- generated chunks as deploy artifacts
- exact reconstruction validation
- chunk size validation
- no live Shelly access

### Package vs testability and rollback

The package is testable locally with `python3 -m unittest discover tests/mac/tools/shelly_build`. Rollback can be a forward package that removes or supersedes the tool and generated artifacts.

### Chat-only assumptions

No chat-only assumptions are required. One implementation choice is left to Codex: the script build manifest format. The chosen format must be documented in `design.md`, covered by tests and remain package-scoped.

## Decision

Continue.

## Notes for human/ChatGPT review

P0008 is consistent and implementable. The only design freedom is the local manifest schema used by the first build tool. That is acceptable because P0008 requires only "read a script build manifest" and does not prescribe the exact schema.
