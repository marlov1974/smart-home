# Package P0019 Attempts

## Attempt 1

Result: passed

## Changes

- Added root `.gitignore` for local Python artifacts.
- Added P0019 package definition and package-run evidence.

## Verification

### `git status --short --branch`

```text
## main...origin/main
?? .gitignore
?? requirements/package-runs/P0019/
?? requirements/packages/P0019-ignore-local-python-artifacts.md
```

Only P0019-scoped files are untracked.

### `git check-ignore .venv/ src/mac/tools/shelly_live/__pycache__/x.cpython-312.pyc tests/mac/tools/__pycache__/x.pyc`

```text
.venv/
src/mac/tools/shelly_live/__pycache__/x.cpython-312.pyc
tests/mac/tools/__pycache__/x.pyc
```

Expected ignore rules matched.

### `git diff --check`

Passed with no output.

## Live actions

None.

## Knowhow promotion

Skipped. The durable rule is captured directly by `.gitignore`; no additional reusable runtime, deploy or API lesson was discovered.
