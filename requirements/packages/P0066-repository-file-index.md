# P0066 - Repository File Index

## Intent

Create a tracked repository file index for `smart-home` so external GitHub/chat review tools that cannot list repository files can still discover path names.

## Scope

- Add root `REPOSITORY_FILES.md`.
- Update `README.md` to link to the file index.
- Store package-run evidence under `requirements/package-runs/P0066/`.

## Out of Scope

- Runtime code changes.
- Shelly, Home Assistant or Mac live writes.
- Generated artifact deploys.
- G1 changes.

## Implementation Notes

- The index lists tracked Git files only.
- The index excludes untracked local files, ignored build products and `.git` internals.
- The file should be regenerated when future packages add, remove or move many files.

## Verification

- Confirm the index matches `git ls-files`.
- Run `git diff --check`.

## Commit and Push Authorization

If verification passes and the diff remains inside this documentation/package scope, commit and push this package result.
