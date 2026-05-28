# Package P0019 Implementation Design

## Package

`P0019`

## Package interpretation

Prevent local Python artifacts from making the G2 repository appear dirty during package bootstrap and synchronization.

## Chosen implementation structure

Add a root `.gitignore` with narrow Python local-artifact patterns only.

## Intended changes

### Files/modules to change

- `.gitignore`: ignore `.venv/`, `__pycache__/`, and `*.py[cod]`.
- `requirements/packages/P0019-ignore-local-python-artifacts.md`: package definition.
- `requirements/package-runs/P0019/review.md`: consistency evidence.
- `requirements/package-runs/P0019/design.md`: implementation design.
- `requirements/package-runs/P0019/functions.md`: confirms no function-level changes.
- `requirements/package-runs/P0019/attempts.md`: verification evidence.

### Files/modules intentionally not changed

- `src/**`: no source behavior changes.
- `tests/**`: no test behavior changes.
- `dep/**`: no deploy artifacts.
- `memory/**`: no durable architecture update needed.
- `docs/functions/**`: no function catalog changes.

## Refactoring decisions

No refactoring.

## Test strategy

Run:

```bash
git status --short --branch
git check-ignore .venv/ src/mac/tools/shelly_live/__pycache__/x.cpython-312.pyc tests/mac/tools/__pycache__/x.pyc
git diff --check
```

## Build / generated artifact strategy

No build or generated deploy artifacts.

## Risks and uncertainties

Risk is low. The main risk is over-broad ignore patterns, so the package uses only narrow Python local-artifact patterns.

## Design deviations during implementation

None.
