# CHANGELOG P0015: package changelog bootstrap policy

## Status

done

## User-visible behavior changed

- Workflow now distinguishes full bootstrap for new sessions from package bootstrap for active-thread follow-up fixes.
- Future packages should produce `requirements/package-runs/<Pxxxx>/CHANGELOG.md` so follow-up work can start from delivered package delta.
- Spot-price fixture files are excluded from ordinary bootstrap/package-bootstrap unless a package explicitly requires them.

## Files changed

- `memory/bootstrap-manifest.json`: bumped manifest version to 13 and added the new bootstrap-mode memory file, changelog template and P0015 package to mandatory read order.
- `memory/08-context-bootstrap-modes.md`: new durable workflow rule for full bootstrap, package bootstrap and large-data avoidance.
- `requirements/package-runs/TEMPLATE-changelog.md`: new template for package-run changelogs.
- `requirements/packages/P0015-package-changelog-bootstrap-policy.md`: package record for this governance change.
- `requirements/package-runs/P0015/CHANGELOG.md`: this package-run delta-bootstrap summary.

## Contracts changed

- Package-run evidence convention now includes `CHANGELOG.md` for packages after P0015.
- Package bootstrap is now a documented context contract for active-thread follow-up work.
- Full bootstrap remains mandatory for new sessions and absent context.

## Important implementation notes

- Documentation/governance package only.
- No source code, deploy artifacts, tests or spot-price data files were changed.
- Updating `requirements/package-runs/README.md` was attempted but blocked by tooling, so the core rule is stored in durable memory, the template, manifest and package file.

## Verification performed

- Read the relevant workflow and package documentation before making changes.
- Confirmed the manifest references the new durable policy and template.
- Confirmed no spot-price data files were inspected or edited.

## Known limitations / follow-up

- A later package may update `requirements/package-runs/README.md` if needed.
- Historic packages before P0015 are not required to have retroactive changelogs.

## Bootstrap for next package

Read first:

- `README.md`
- `memory/bootstrap-manifest.json`
- `memory/08-context-bootstrap-modes.md`
- this changelog
- current/latest relevant package file and its package-run `CHANGELOG.md`

Do not read by default:

- spot-price fixture files
- large data files
- broad evidence folders
- unrelated source/deploy/test areas
