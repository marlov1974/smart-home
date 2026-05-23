# ChatGPT / Codex Workflow

## Roles

Human operator:
- owns priorities
- validates physical reality
- approves design and deploy decisions
- tells Codex when a package should run
- tells ChatGPT when Codex has completed or stopped

ChatGPT:
- reasoning partner
- requirements/design author
- package framer
- reviewer
- reviews Codex results directly from repository evidence

Codex:
- local coding and diagnostics agent
- independent package consistency reviewer
- reads repo context
- performs package-scoped implementation design
- documents function-level design for code packages
- implements packages
- runs tests and verification
- performs active debugging within package scope
- stores useful package evidence and promotes reusable lessons
- prepares diffs/commits when allowed

## Standard flow

1. Human and ChatGPT discuss problem and design.
2. ChatGPT presents a final design/package proposal for human review.
3. ChatGPT creates or updates an ordered package file.
4. Human tells Codex a new package exists.
5. Codex reads bootstrap and the active package.
6. Codex performs package consistency review.
7. Codex reports `PASS`, `WARN` or `STOP`.
8. Codex stores useful review evidence under `requirements/package-runs/<Pxxxx>/review.md`.
9. If `PASS` or acceptable `WARN`, Codex writes package-scoped implementation design.
10. For code packages, Codex writes package-scoped function design before implementation.
11. Codex implements within package scope according to package, design and function docs.
12. Codex runs package test cases and verification commands.
13. If live testing is allowed, Codex captures logs and checks runtime health.
14. Codex may fix package-scoped defects and retry up to the package attempt limit.
15. Codex stores useful attempt/debug evidence under `requirements/package-runs/<Pxxxx>/`.
16. Codex updates cross-package function catalog when functions are created, changed or removed.
17. Codex promotes reusable global lessons into `memory/knowhow/` when appropriate.
18. Codex gives the human a short result.
19. Human tells ChatGPT Codex is done or stopped.
20. ChatGPT reads the repository directly and reviews the package result with the human.

## Context-reset phase gates

For substantial code packages, Codex should work in explicit phases. Each phase may be run in a fresh Codex context.

The next phase must read repository artifacts from earlier phases rather than relying on unwritten prior reasoning.

Repository state is the memory.

Recommended phases:

```text
0. bootstrap
1. package consistency review
2. implementation design
3. function design
4. implementation
5. build / generated deploy artifacts
6. test / debug / verification
7. final evidence and report
```

Small documentation-only packages may combine phases, but code packages, live-device packages, installer work and Mac/Shelly contract packages should use the phase-gate model.

## Codex bootstrap before coding

Codex must read:

1. `README.md`
2. `AGENTS.md`
3. `memory/bootstrap-manifest.json`
4. every file in manifest `read_order`
5. the active package file
6. relevant source/deploy files listed by the package

Codex must not edit before producing:

- package consistency result
- short understanding summary
- implementation/debug plan

## Repository-first ChatGPT review

ChatGPT should review Codex results from repository state, not pasted terminal output, whenever repository access is available.

Review sources may include:

```text
requirements/packages/Pxxxx-<name>.md
requirements/package-runs/Pxxxx/review.md
requirements/package-runs/Pxxxx/design.md
requirements/package-runs/Pxxxx/functions.md
requirements/package-runs/Pxxxx/attempts.md
requirements/package-runs/Pxxxx/findings.md
requirements/package-runs/Pxxxx/logs/
docs/functions/
memory/knowhow/
changed memory files
changed source/deploy/test files
commit/diff history when available
```

If repository access is unavailable, pasted Codex output may be used as fallback.

## Package consistency review

Codex must independently review the package before implementation.

Classification:

```text
PASS = package is consistent with repository truth
WARN = package is implementable but has assumptions/uncertainty
STOP = package conflicts with repo truth, is unsafe, underspecified or out of scope
```

Review against:

- memory files
- linked requirements
- previous packages
- implementation and deploy structure
- G1/G2 boundary
- invariants
- testability
- rollback feasibility

If Codex returns `STOP`, it must not edit. It should report the conflict and cite the relevant files/sections.

If Codex returns `WARN`, it may continue only when the uncertainty is minor and within package scope. Otherwise it should stop.

Useful review output should be stored in:

```text
requirements/package-runs/<Pxxxx>/review.md
```

## Implementation design

For code packages, Codex must write package-scoped implementation design before coding:

```text
requirements/package-runs/<Pxxxx>/design.md
```

The design must include:

- package interpretation
- chosen implementation structure
- files/modules intended to change
- files/modules intentionally not changed
- deliberate refactoring decisions and reasons
- test strategy
- risks and uncertainties

Codex may refactor deliberately when the refactor is needed for target behavior, testability, safety, contract clarity or package-scoped maintainability.

Codex must not perform unrelated cleanup, broad renames, formatting churn or opportunistic refactors.

## Function design and catalog

For code packages, Codex must write package-local function design before implementation:

```text
requirements/package-runs/<Pxxxx>/functions.md
```

Function design should list intended new, changed and removed functions.

For each relevant function, document:

- status: new / changed / removed / unchanged-but-relevant
- purpose
- inputs
- outputs
- side effects
- change description
- reason
- test coverage

If implementation requires a function-level change that was not documented, Codex must update `functions.md` and explain the design deviation, or stop if the change expands package scope.

Cross-package durable function documentation belongs under:

```text
docs/functions/
```

Codex must update the cross-package function catalog when a function is created, changed, removed or becomes relevant for future packages.

Package-local function design records the plan for one package. Cross-package function catalog records the durable current function design after implementation.

## Active debugging policy

Codex may actively debug defects discovered during verification if they are inside package scope.

Default attempt limit:

```text
3 implementation/debug attempts per package
```

Each attempt must:

- change only package-scoped files
- run the package test cases and verification commands
- capture relevant logs when live Shelly testing is involved
- verify expected output/state
- inspect runtime health and unexpected side effects
- summarize failure, fix and result
- store useful attempt/debug evidence under `requirements/package-runs/<Pxxxx>/`

After 3 failed attempts, Codex must stop and report:

- what was tried
- evidence from outputs/logs
- current hypothesis
- remaining uncertainty
- whether the package likely needs design/scope changes

## Evidence storage

Package-specific evidence belongs under:

```text
requirements/package-runs/<Pxxxx>/
  review.md
  design.md
  functions.md
  attempts.md
  logs/
  findings.md
```

Use package-run evidence for:

- consistency review details
- implementation design
- function-level design
- warnings and assumptions
- failed/passed attempts
- log excerpts
- runtime anomalies
- semantic side effects
- package-specific findings for human/ChatGPT review

Do not put raw one-off package logs into global memory.

## Knowhow promotion

Reusable global lessons belong under:

```text
memory/knowhow/
```

Promote an observation to knowhow when it becomes generally useful for future packages.

Examples:

- Shelly RPC sequencing limitations
- KVS size/shape limits
- heap/memory safety patterns
- package-writing mistakes that repeatedly cause review warnings
- reliable diagnostics patterns

A finding can be both package evidence and promoted knowhow: keep the package evidence where it occurred and add the reusable lesson to knowhow.

## Shelly live-debug guidance

When live Shelly testing is explicitly allowed, Codex should observe execution as well as final output.

Useful read-only diagnostics include:

```bash
curl -N http://192.168.86.240:8040/debug/log
curl -s http://192.168.86.240:8040/rpc/Shelly.GetStatus
curl -s 'http://192.168.86.240:8040/rpc/KVS.Get?key=<key>'
```

Use bounded log capture so commands do not hang. On macOS:

```bash
perl -e 'alarm shift; exec @ARGV' 60 curl -N http://192.168.86.240:8040/debug/log
```

Log capture itself is read-only. Starting/stopping scripts, writing KVS, uploading scripts, changing components or changing actuators are live actions and require explicit package permission.

## Runtime health checks

Live verification should check more than expected output.

Look for:

- missing expected KVS/output
- HTTP errors
- KVS errors
- JSON parse errors
- script errors
- unexpected restarts
- repeated start/stop loops
- unexpectedly long execution time
- low or falling heap margin
- unexpected actuator intent
- semantically wrong side effects given the system model

Example: if a test expects low supply-air target and that value is produced, but ventilation percentage collapses in a way that violates the intended system behavior, Codex should treat it as a discovered problem, not a pass.

## Safety defaults

Codex may use read-only diagnostics by default.

Codex must not write to live devices unless the active package explicitly permits live write actions.

Forbidden by default:

- actuator-changing RPC calls
- `KVS.Set` against live devices
- script upload/start/stop against live devices
- Home Assistant config changes outside package scope

## Package output expectation

Codex must report:

- consistency review result: PASS/WARN/STOP
- implementation design path
- function design path
- files changed
- tests run
- verification output
- log/runtime observations when live tested
- debug attempts used
- package-run evidence paths created/updated
- function catalog updates
- knowhow promotions created/updated
- uncertainty / skipped checks
- whether deploy artifacts changed
- rollback implications
