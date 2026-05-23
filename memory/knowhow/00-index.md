# Knowhow Memory Index

Knowhow memory stores durable lessons learned from debugging, testing, operations and package reviews.

This is for reusable truths that should affect future design or implementation.

Do not store one-off package artifacts here unless they have been promoted into a general lesson.

## Files

```text
shelly.md     Shelly platform/runtime/debugging lessons
codex.md      Codex workflow lessons
```

## Promotion rule

A package may produce observations under `requirements/package-runs/<Pxxxx>/`.

If an observation becomes a reusable global lesson, promote it into the appropriate `memory/knowhow/` file through the same package or a later package.

Example:

```text
Package observation:
  P0012 attempt 2 showed three parallel RPC calls inside a timer can hang the script.

Promoted knowhow:
  Avoid launching multiple parallel Shelly RPC calls from one timer callback; serialize them unless proven safe.
```

## Package history

Created by `P0004-codex-debug-evidence-and-learning-policy`.
