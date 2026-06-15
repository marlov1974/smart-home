# P0066 Design

## Interpretation

The user wants a durable file listing in `smart-home` so ChatGPT/GitHub review contexts can find paths without local filesystem listing.

## Implementation Structure

- Add `REPOSITORY_FILES.md` at repository root.
- Generate the file list from Git tracked paths.
- Add a README pointer near the existing layout documentation.
- Capture package-run evidence under `requirements/package-runs/P0066/`.

## Refactoring Decisions

No refactoring. This is a documentation/package-evidence change.

## Test Strategy

- Compare `REPOSITORY_FILES.md` entries to `git ls-files`.
- Run `git diff --check`.

## Risks and Uncertainties

- The index can become stale if future packages do not regenerate it after path changes.
- The index intentionally excludes untracked local files.
