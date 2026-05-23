# Package Lifecycle

This document defines the standard G2 change process from idea to verified package and lessons learned.

## Lifecycle summary

```text
Idea -> design -> design freeze -> package -> Codex review/implementation/debug/evidence -> ChatGPT repo review -> deploy/rollback -> lessons learned
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
- promotes reusable lessons into knowhow when appropriate
- reports a short result to the human operator

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

Codex must:

- bootstrap
- read the package
- perform package consistency review
- return PASS/WARN/STOP
- implement only within scope when allowed
- test and debug
- store package-run evidence under `requirements/package-runs/<Pxxxx>/`
- promote durable lessons into `memory/knowhow/` when appropriate
- give the human operator a short result

### 6. ChatGPT repository review

The human operator tells ChatGPT that Codex is done or stopped.

ChatGPT reads the repository directly rather than relying on pasted Codex output.

Review sources may include:

```text
requirements/packages/Pxxxx-<name>.md
requirements/package-runs/Pxxxx/review.md
requirements/package-runs/Pxxxx/attempts.md
requirements/package-runs/Pxxxx/findings.md
requirements/package-runs/Pxxxx/logs/
memory/knowhow/
changed memory files
changed source/deploy/test files
commit/diff history when available
```

ChatGPT then reviews the result with the human operator.

### 7. If wrong or misunderstood

If Codex misunderstood the package or changed the wrong thing:

- human operator asks Codex to back out/revert if needed
- ChatGPT and human adjust the design
- either update the package if it has not become a stable historical record, or create a new forward package

If runtime/deploy state was already affected, rollback should normally be a new forward package.

### 8. Verified/live completion

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

Codex output should be stored in the repository.

ChatGPT should review Codex results from the repository, not from pasted terminal output, unless repository access is unavailable.

## Package history

Created by `P0005-package-lifecycle-and-repo-review-process`.
