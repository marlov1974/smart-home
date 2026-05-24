# Package Lifecycle

This document defines the standard G2 change process from idea to verified package and lessons learned.

## Lifecycle summary

```text
Idea -> design -> design freeze -> package -> Codex review/implementation/debug/evidence/commit/push -> ChatGPT repo review -> deploy/rollback -> lessons learned
```

If a package fails verification, the lifecycle is:

```text
package attempt -> evidence -> cleanup -> evidence commit/push -> follow-up package
```

## Current phase: pre-production G2

G2 is currently a pre-production system. It may run controlled live tests on selected physical devices, but it is not yet the production owner of the house control runtime.

In pre-production, committing/pushing verified G2 package results is considered documentation and source-of-truth hygiene, not production activation.

Therefore, a quick package command authorizes Codex to commit and push verified package results, including live-write packages, when all of these are true:

- the active package explicitly allowed the live writes that were performed
- live actions stayed inside the package allowlist
- no actuator/output actions occurred unless the package explicitly allowed them
- tests and required verification commands passed
- live verification passed when required
- package-run evidence and completion notes were updated
- `git diff --check` passed
- the diff is inside package scope

This does not authorize production activation, broad rollout, G1 runtime migration, Home Assistant production changes, secrets, destructive actions or live actions outside the package allowlist.

## Future phase: production G2

When G2 becomes production control, packages must distinguish:

```text
commit/push:
  Save verified source, deploy artifacts, evidence and documentation to repository truth.

deploy/stage:
  Put code/config onto one or more devices but do not necessarily make it production-active.

production activation:
  Make G2 code/config the active controller for production behavior.
```

For production-critical G2 runtime packages, the active package must explicitly state what successful verification authorizes:

```text
commit/push only
commit/push plus staged deploy
commit/push plus production activation
```

Production activation always requires explicit package permission and operator approval.

## Future production rollback requirement

Production G2 must support simple operator rollback by target version/package.

The operator goal is a command such as:

```text
backa till 27
```

Meaning:

```text
Restore the relevant production devices/services to the desired known-good target version associated with package/version 27.
```

Rollback remains a forward-moving controlled operation. It should not require ad-hoc manual editing or hidden history rewriting.

A future rollback implementation must define:

- what target version means per logical device/service
- which deploy artifacts/config/scripts belong to that target
- how to verify device identity before rollback writes
- how to stage rollback safely
- how to verify success and runtime health after rollback
- how to record rollback evidence in the repo

## Future production pre-live test levels

Production G2 should reduce risk before central devices receive new runtime behavior.

Useful test levels:

### Mac/API contract tests

Before deploying Shelly runtime changes, the Mac/Codex should test external APIs and data contracts where practical.

Examples:

- verify that a weather API returns expected schema/units before deploying a Shelly weather script
- verify spot-price endpoint shape before Shelly runtime consumes it
- validate forecast output schema before Home Assistant or Shelly reads it

This catches ordinary code/data-contract errors before they become device-runtime errors.

### Low-criticality device test

A production device that is not central to the current control path may act as a safer live Shelly test target.

Example:

```text
A cooling-dimmer device may test a new weather script before dampers receives the production version.
```

This is not a substitute for final target verification, but it can catch runtime, heap, HTTP, KVS and Shelly API issues on real hardware with lower system risk.

### Staged rollout

Production packages should support deploying to a less central device or one logical device before broad rollout when the change type allows it.

Staged rollout evidence should record:

- test device identity
- why it is safe/lower criticality
- script/config deployed
- runtime health
- whether the central target is still unchanged
- what must be reverified on the central target before activation

### Non-actuating live verification

Prefer read-only or non-actuating live verification before production activation when possible.

Examples:

- read status/config/logs
- run script in a mode that writes only diagnostic KVS
- verify API parsing without changing outputs
- verify computed intent without applying it to actuators

## Roles

Human operator:
- brings ideas, observations and priorities
- validates real-world behavior
- approves design, live permissions and deploy decisions
- tells Codex when to run the next package

ChatGPT:
- helps reason and design
- writes design summaries and package drafts
- creates or updates package files when appropriate
- updates pure documentation/memory facts directly when no package trace is needed
- reviews Codex results directly from the repository
- helps extract lessons learned after completion

Codex:
- bootstraps repository context
- reviews the package for consistency before editing
- implements within package scope
- tests, debugs and stores package-run evidence
- cleans up failed package attempts so unverified implementation changes do not remain as current truth
- promotes reusable lessons into knowhow when appropriate
- commits and pushes verified package results when verification passes and the diff is inside package scope
- commits and pushes evidence-only failed-package records when implementation/live verification fails and the package evidence is useful
- reports a short result to the human operator, including commit SHA when pushed

## Process

### 1. Idea

The human operator describes a new function, change, problem or observation.

### 2. Design with ChatGPT

Human and ChatGPT discuss:

- target behavior
- solution model
- constraints and safety
- G1/G2 boundary
- tests and verification
- rollback
- what is decided vs temporary discussion

For pure physical/documentation facts, design discussion may be unnecessary. ChatGPT may update memory directly when the change only records or corrects already-decided knowledge.

### 3. Design freeze

Before package-driven repository updates, ChatGPT presents a final proposed solution:

- documentation/memory changes
- package content
- Codex mandate
- expected test/debug/review behavior
- live permissions, if any

The human operator reviews and corrects misunderstandings.

For direct documentation-only updates, the relevant review is simply whether the fact is correct and belongs in memory.

### 4. Package creation

Once agreed, package-driven work is created or updated under:

```text
requirements/packages/Pxxxx-<name>.md
```

Documentation may be updated by ChatGPT when it is pure design/memory work.

For code packages, Codex normally updates documentation as part of the package so code, tests and memory stay synchronized.

A package is not required for documentation-only fact capture that is independent of an active package. Examples include documenting hardware brand/model/properties or correcting a physical inventory note.

A documentation change should be linked to a package when it was discovered during that package, explains that package's implementation or verification, records package evidence, or changes understanding that the package relies on. Example: if P0014 discovers that `ftx-dampers` is now a Shelly Pro 1PM rather than a Shelly Pro 2, the finding belongs in P0014 evidence/logs and the memory update should reference the package context.

### 5. Codex execution

The human operator tells Codex that a new package exists.

A short command such as `bygg paket 9`, `build package 9`, or `kör P0009` is enough for Codex to run the full package workflow when the package exists.

Codex must:

- synchronize the local repository with `origin/main` before reading package files
- bootstrap
- read the package
- perform package consistency review
- return PASS/WARN/STOP
- implement only within scope when allowed
- test and debug
- store package-run evidence under `requirements/package-runs/<Pxxxx>/`
- promote durable lessons into `memory/knowhow/` when appropriate
- check `git status` and confirm the diff is inside package scope
- run required verification commands and `git diff --check`
- commit and push verified package results when verification passes
- if verification fails after allowed attempts, run the failed-package cleanup process before stopping
- give the human operator a short result including commit SHA, files changed, tests run and uncertainty

Quick package commands do not grant extra permission for live writes, actuator changes, device writes, Home Assistant writes, secrets or destructive actions. Those still require explicit package permission.

In pre-production G2, quick package commands do authorize commit/push after verified success, including for live-write packages, under the pre-production conditions defined above.

### 6. Failed package cleanup

When implementation, tests or live verification fail after the package's allowed attempts, Codex must not leave the repository in a half-current state.

Codex must:

- keep useful package-run evidence under `requirements/package-runs/<Pxxxx>/`
- document what passed, what failed, attempted fixes, remaining hypothesis and live/device state
- update the package status to a non-success state such as `stopped`, `failed-live`, or `failed-verification` when appropriate
- preserve historical evidence from previous packages
- revert unverified source, generated artifact, test, doc and memory changes unless the package explicitly says a failed partial artifact should become current truth
- run `git diff --check`
- commit and push the evidence-only failed-package record if it is useful and safe
- leave the working tree clean, or explicitly report why cleanup is blocked

Evidence-only failed-package commits must not make unverified runtime code or deploy artifacts look like the current implementation.

For live packages, Codex must also record final live state, for example which test script remains installed/stopped and which KVS keys may have been written.

### 7. ChatGPT repository review

The human operator tells ChatGPT that Codex is done or stopped.

ChatGPT reads the repository directly rather than relying on pasted Codex output.

Review sources may include:

```text
requirements/packages/Pxxxx-<name>.md
requirements/package-runs/Pxxxx/review.md
requirements/package-runs/Pxxxx/design.md
requirements/package-runs/Pxxxx/functions.md
requirements/package-runs/Pxxxx/attempts.md
requirements/package-runs/Pxxxx/findings.md
requirements/package-runs/Pxxxx/logs/
memory/knowhow/
changed memory files
changed source/deploy/test files
commit/diff history when available
```

ChatGPT then reviews the result with the human operator.

### 8. If wrong or misunderstood

If Codex misunderstood the package or changed the wrong thing:

- human operator asks Codex to back out/revert if needed
- ChatGPT and human adjust the design
- either update the package if it has not become a stable historical record, or create a new forward package

If runtime/deploy state was already affected, rollback should normally be a new forward package.

For documentation-only updates that are not tied to package execution, correction can be another direct documentation update.

### 9. Verified/live completion

When the package is implemented, reviewed and live/verified as applicable:

- package status is updated
- package-run evidence is kept
- reusable lessons are promoted to knowhow
- package template/process improvements are captured in a later package if needed

## Package status values

Suggested status values:

```text
planned
active
implemented
pending-review
verified
deployed
stopped
failed-verification
failed-live
rolled-back
superseded
```

## Documentation ownership rule

ChatGPT may update documentation directly for small, pure design/memory changes.

Documentation-only physical facts and inventory corrections do not need package traceability unless they were discovered during package work or affect package implementation/verification.

Codex should update documentation as part of the package when:

- code changed
- deploy artifacts changed
- tests or diagnostics changed
- package review found conflicts
- local repo inspection is required
- the documentation records a finding discovered during package execution

## Repository-first review rule

Codex output should be stored in the repository and pushed when verification passes and the diff is inside package scope, under the current phase rules above.

For failed packages, useful evidence should also be stored in the repository and pushed after unverified implementation changes are reverted.

ChatGPT should review Codex results from the repository, not from pasted output, unless repository access is unavailable.

## Package history

Created by `P0005-package-lifecycle-and-repo-review-process`.

Updated after P0008 to make Codex commit/push the default for verified non-live package work.

Updated after the stopped P0012 spotprice attempt to require failed-package cleanup and evidence-only commits.

Updated by direct documentation correction to clarify that pure documentation and hardware fact updates do not require package traceability unless tied to package work.

Updated by direct documentation correction to define pre-production G2 commit/push policy and future production rollback/pre-live test requirements.
