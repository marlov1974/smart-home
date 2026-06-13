# Package P0057 Changelog

## Status

verified

## Behavior Change

No live runtime behavior changed.

P0057 imported the current G1 FTX Shelly runtime source into G2 and changed repository guidance so future FTX runtime inspection starts from G2.

## Files Changed

- Added `src/shelly/ftx/**`
- Added `src/shelly/ftx/README.md`
- Added `src/shelly/ftx/import-manifest.json`
- Added `docs/functions/shelly/ftx-runtime-baseline.md`
- Updated `docs/functions/00-index.md`
- Updated `memory/03-g1-g2-boundary.md`
- Updated `memory/physical/ftx/00-index.md`
- Updated `memory/knowhow/codex.md`
- Added P0057 package and package-run evidence

## Source Provenance

```text
source repo: marlov1974/shelly
source commit: 761cc4bc1c527d6bdffa0a0783f0cfd1761040f4
source summary: Make VVX executor thermal-local
```

## Contracts Changed

- FTX runtime source-of-truth for future inspection is now `src/shelly/ftx/`.
- G1 is historical provenance unless a package explicitly asks for pre-import comparison or G1 maintenance.

## Verification

```text
diff -qr /Users/marcus.lovenstad/dev/shelly/rt/common src/shelly/ftx/common
diff -qr /Users/marcus.lovenstad/dev/shelly/rt/brain src/shelly/ftx/brain
diff -qr /Users/marcus.lovenstad/dev/shelly/rt/state src/shelly/ftx/state
diff -qr /Users/marcus.lovenstad/dev/shelly/rt/scripts/{role} src/shelly/ftx/scripts/{role}
diff -qr /Users/marcus.lovenstad/dev/shelly/rt/recipes src/shelly/ftx/recipes
git diff --check
python3 -m unittest discover tests/mac/tools
```

Results:

```text
imported G1 source directories matched except three trailing blank lines removed to satisfy git diff --check
git diff --check passed
68 Mac tool tests passed
```

## Known Limitations

- No deploy artifacts were generated.
- No live devices were written.
- Imported G1 recipes preserve G1 path names and need a later G2 build/deploy mapping package.
- The known VVX efficiency display limitation remains intentionally unchanged.

## Bootstrap Hints

For follow-up FTX runtime work:

1. Read this changelog.
2. Read `src/shelly/ftx/README.md`.
3. Read `src/shelly/ftx/import-manifest.json`.
4. Inspect the relevant source under `src/shelly/ftx/`.
5. Use G1 only for explicit historical comparison.
