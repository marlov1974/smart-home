# P0061 Design

## Interpretation

G2 should stop owning the market simulator and forecasting lab. The new repository becomes the source for spot price history/forecast, weather history, consumption/price diagnostics and weekly optimizer experiments.

## Implementation Structure

1. Copy market artifacts into `../Market-Simulator` while preserving paths:
   - `src/mac/services/...`
   - `src/mac/labs/...`
   - `tests/mac/...`
   - `docs/functions/mac/...`
   - `memory/...`
   - `requirements/...`
   - `data/...`
2. Add a Market-Simulator README and migration note.
3. Remove the migrated files from G2.
4. Update G2 bootstrap/function indexes so mandatory reads no longer point at removed market docs.
5. Add P0061 package evidence in G2.

## Deliberate Refactoring Decisions

- Preserve import paths in the new repository for this package. Renaming packages to `market_simulator` should be a later change with dedicated test coverage.
- Do not alter runtime Shelly deploy artifacts in this migration.
- Do not rewrite historical package contents except by moving files to the new repository.

## Test Strategy

- Run G2 focused tests for remaining Shelly FTX and Mac local-operator/tooling surfaces.
- Run Market-Simulator smoke tests covering imported market services and weekly optimizer imports.
- Run `git diff --check` in both repositories.

## Risks and Uncertainty

- Long-running lab tests may require network, local databases or optional dependencies.
- Some smart-home references to market history may remain in historical docs; active bootstrap/index references will be cleaned.
