# P0062 Review

## Classification

WARN

## Evidence

`P0058` correctly changed `src/shelly/ftx/state/perf-vvx.js`, and `src/shelly/ftx/recipes/state.json` references `rt/state/perf-vvx.js`.

However, the repository still contains a legacy duplicate implementation:

```text
src/shelly/ftx/state/feature-vvx-efficiency.js
```

That file still calculates and writes VVX efficiency without checking `ctx.run.vvx`.

`P0058` also explicitly did not build `dep/s` artifacts and did not deploy to live Shelly, so a nonzero live HA value can still come from an older deployed script.

## Decision

Implementable with caveat. Patch the duplicate source path and strengthen source tests. Do not perform live writes in this package.

## Risk

This may not by itself change the live HA value if the live Shelly state script is old. A later deploy package is required for live behavior.
