# FTX Shelly Runtime Baseline

This directory contains the P0057 import of the current G1 FTX Shelly runtime.

P0057 establishes this imported source as the first G2 FTX runtime baseline for future inspection and package work.

## Provenance

```text
source repo: /Users/marcus.lovenstad/dev/shelly
source commit: 761cc4bc1c527d6bdffa0a0783f0cfd1761040f4
source summary: Make VVX executor thermal-local
import package: P0057
```

## Scope

Imported source areas:

```text
common/   shared runtime helpers used by G1 recipes
brain/    FTX brain modules
state/    FTX aggregate state/performance modules
scripts/  local device scripts
recipes/  G1 recipe metadata preserved as import context
```

The import is source-only. It does not deploy to any device and does not generate `dep/s` artifacts.

## Source-of-Truth Rule

After P0057, future FTX runtime questions should inspect this G2 source first. The G1 repository is historical provenance unless a package explicitly asks for comparison against pre-import behavior.

## Known Imported Limitation

The imported VVX efficiency calculation is the current baseline and can be misleading when VVX is off while active cooling changes `to_house`. P0057 intentionally does not fix that behavior.
