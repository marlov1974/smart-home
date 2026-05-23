# Package Run Evidence

This folder stores package-specific review, test and debug evidence.

Use this for material that is useful for human/ChatGPT review but not yet a global reusable lesson.

## Structure

```text
requirements/package-runs/Pxxxx/
  review.md
  attempts.md
  logs/
    README.md
    <short-log-name>.log or <short-log-name>.md
  findings.md
```

## Files

### review.md

Package consistency review output:

- PASS/WARN/STOP
- conflicts or assumptions
- files checked
- decision to continue or stop

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

## Promotion rule

If a package-specific finding becomes a reusable lesson, promote it to `memory/knowhow/` in the same package or a later package.
