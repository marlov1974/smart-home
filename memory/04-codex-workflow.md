# ChatGPT / Codex Workflow

## Roles

Human operator:
- owns priorities
- validates physical reality
- approves design and deploy decisions

ChatGPT:
- reasoning partner
- requirements/design author
- package framer
- reviewer

Codex:
- local coding and diagnostics agent
- independent package consistency reviewer
- reads repo context
- implements packages
- runs tests and verification
- performs active debugging within package scope
- prepares diffs/commits when allowed

## Standard flow

1. Human and ChatGPT discuss problem and design.
2. ChatGPT writes or updates an ordered package file.
3. Codex reads bootstrap and the active package.
4. Codex performs package consistency review.
5. Codex reports `PASS`, `WARN` or `STOP`.
6. If `PASS` or acceptable `WARN`, Codex summarizes understanding and plan.
7. Codex implements within package scope.
8. Codex runs package test cases and verification commands.
9. If live testing is allowed, Codex captures logs and checks runtime health.
10. Codex may fix package-scoped defects and retry up to the package attempt limit.
11. Codex reports diff, tests, logs/observations and uncertainty.
12. Human/ChatGPT reviews before deploy.

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

After 3 failed attempts, Codex must stop and report:

- what was tried
- evidence from outputs/logs
- current hypothesis
- remaining uncertainty
- whether the package likely needs design/scope changes

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
- files changed
- tests run
- verification output
- log/runtime observations when live tested
- debug attempts used
- uncertainty / skipped checks
- whether deploy artifacts changed
- rollback implications
