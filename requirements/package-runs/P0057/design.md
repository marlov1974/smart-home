# Package P0057 Implementation Design

## Package

`P0057`

## Package interpretation

Import the current G1 FTX Shelly runtime as the first G2 FTX runtime baseline, preserving behavior and provenance. Future FTX runtime questions should use the imported G2 source first.

## Chosen implementation structure

Create a G2-owned FTX source subtree:

```text
src/shelly/ftx/
  README.md
  import-manifest.json
  common/
  brain/
  state/
  scripts/
    dampers/
    supply-fan/
    extract-fan/
    heat-dimmer/
    cool-dimmer/
    vvx/
  recipes/
```

The directory structure mirrors the current G1 runtime enough to keep recipe paths understandable while making ownership local to G2.

## Intended changes

### Files/modules to change

- `src/shelly/ftx/**`: imported runtime source and provenance.
- `memory/03-g1-g2-boundary.md`: record P0057 source-of-truth migration rule.
- `memory/physical/ftx/00-index.md`: point FTX runtime source readers to `src/shelly/ftx`.
- `docs/functions/shelly/ftx-runtime-baseline.md`: high-level catalog of imported runtime entry points and safety-critical behavior.
- `requirements/package-runs/P0057/CHANGELOG.md`: package delta summary.

### Files/modules intentionally not changed

- `dep/s/**`: no deploy artifacts generated in this package.
- live Shelly devices: no writes.
- Home Assistant config: no writes.
- G1 repository: no edits.
- existing G2 Shelly examples: left intact.

## Refactoring decisions

No behavior refactor. Imported G1 source should remain byte-for-byte copied where practical. Any G2-specific notes go into `README.md` and `import-manifest.json`, not into the imported source files.

## Test strategy

- Verify expected imported file inventory exists.
- Verify G1 provenance recorded.
- Run `git diff --check`.
- Run Mac tool unit tests if practical to ensure the package did not break existing tooling.

## Build / generated artifact strategy

Do not generate `dep/s` deploy artifacts in P0057. The existing G2 build tool wraps source inside an IIFE and may not be behavior-preserving for already complete Shelly scripts or G1 wrapper-based recipes. A later package should design a deterministic FTX build/recipe path.

## Risks and uncertainties

- The imported G1 runtime is not yet represented as G2 deploy artifacts.
- Some G1 recipes reference `rt/...` paths. P0057 preserves recipes as imported metadata; later tooling must either understand import-root mapping or generate G2-native manifests.
- The current G1 runtime may continue evolving until the operator fully freezes it. Future comparison packages may be needed.

## Design deviations during implementation

Three imported files had trailing blank lines that failed `git diff --check` in G2:

- `src/shelly/ftx/common/kvs.js`
- `src/shelly/ftx/common/number.js`
- `src/shelly/ftx/common/wrapper.start.js`

The trailing blank lines were removed. This is whitespace-only and does not change runtime behavior.
