# Package Run Evidence

This folder stores package-specific review, design, test and debug evidence.

Use this for material that is useful for human/ChatGPT review but not yet a global reusable lesson.

The repository is the memory between Codex phases. For substantial code packages, later phases should read these files instead of relying on unwritten prior reasoning.

## Standard structure

```text
requirements/package-runs/Pxxxx/
  review.md
  design.md
  functions.md
  attempts.md
  findings.md
  logs/
    README.md
    <short-log-name>.log or <short-log-name>.md
```

## Files

### review.md

Package consistency review output:

- PASS/WARN/STOP
- conflicts or assumptions
- files checked
- decision to continue or stop

### design.md

Package-scoped implementation design before coding:

- package interpretation
- chosen implementation structure
- files/modules intended to change
- files/modules intentionally not changed
- deliberate refactoring decisions and reasons
- test strategy
- risks and uncertainties

### functions.md

Package-scoped function design before coding:

- functions to create
- functions to change
- functions to remove
- important functions intentionally left unchanged
- purpose, inputs, outputs, side effects, reason and test coverage

If implementation requires an undocumented function-level change, update this file and explain the deviation, or stop if the change expands package scope.

### attempts.md

Implementation/debug attempts:

- attempt number
- change summary
- tests run
- result
- reason for next attempt or stop

### logs/

Raw or excerpted log evidence.

Prefer concise excerpts unless full logs are required by the package.

### findings.md

Package-specific oddities and issues for human/ChatGPT review.

Findings should include whether they were:

- fixed inside the package
- left open
- promoted to `memory/knowhow/`
- require a new package

## Templates

```text
requirements/package-runs/TEMPLATE-review.md
requirements/package-runs/TEMPLATE-design.md
requirements/package-runs/TEMPLATE-functions.md
requirements/package-runs/TEMPLATE-attempts.md
```

## Cross-package function catalog

Durable function documentation belongs under:

```text
docs/functions/
```

Package-local `functions.md` is the plan for one package. `docs/functions/` is the durable current function catalog after implementation.

## Promotion rule

If a package-specific finding becomes a reusable lesson, promote it to `memory/knowhow/` in the same package or a later package.
