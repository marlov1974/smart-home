# CHANGELOG P____: <package name>

## Status

`done` / `partial` / `stopped` / `failed-verification`

## User-visible behavior changed

- ...

## Files changed

- `path/file`: one-line purpose and effect

## Repository file index

State one of:

- `REPOSITORY_FILES.md updated for tracked file path changes.`
- `No tracked files were added, removed or moved, so REPOSITORY_FILES.md did not change.`

## Contracts changed

Document any changed external or cross-module contract:

- input/output fields
- JSON schemas
- CLI/API behavior
- generated artifacts
- deploy artifact naming/versioning
- KVS keys/contracts
- normalization/index rules
- backwards compatibility notes

If no contracts changed, state: `No contract changes.`

## Important implementation notes

- ...

## Verification performed

- command/check: result

## Known limitations / follow-up

- ...

## Bootstrap for next package

Read first:

- this changelog
- `requirements/packages/P____-<name>.md`
- relevant package-run evidence listed here
- relevant implementation files listed here
- `REPOSITORY_FILES.md` when file discovery is needed or when tracked file paths changed

Do not read by default:

- large data files
- raw logs unless named as necessary
- spot-price fixture/raw data files unless the next package explicitly requires raw data inspection

## Notes for ChatGPT/Codex

This file is the delta-bootstrap for follow-up fixes. Keep it short, factual and grounded in the final repository state.
