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

### 3. Design freeze

Before repository updates, ChatGPT presents a final proposed solution:

- documentation/memory changes
- package content
- Codex mandate
- expected test/debug/review behavior
- live permissions, if any

The human operator reviews and corrects misunderstandings.

### 4. Package creation

Once agreed, a package is created or updated under:

```text
requirements/packages/Pxxxx-<name>.md
```

Documentation may be updated by ChatGPT when it is pure design/memory work.

For code packages, Codex normally updates documentation as part of the package so code, tests and memory stay synchronized.

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

Codex should update documentation as part of the package when:

- code changed
- deploy artifacts changed
- tests or diagnostics changed
- package review found conflicts
- local repo inspection is required

## Repository-first review rule

Codex output should be stored in the repository and pushed for non-live packages when verification passes.

For failed packages, useful evidence should also be stored in the repository and pushed after unverified implementation changes are reverted.

ChatGPT should review Codex results from the repository, not from pasted terminal output, unless repository access is unavailable.

## Package history

Created by `P0005-package-lifecycle-and-repo-review-process`.

Updated after P0008 to make Codex commit/push the default for verified non-live package work.

Updated after the stopped P0012 spotprice attempt to require failed-package cleanup and evidence-only commits.
