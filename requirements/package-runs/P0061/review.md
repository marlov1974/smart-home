# P0061 Review

## Classification

WARN

## Consistency Review

The request is consistent with repository direction: the existing G2 repository contains a large energy-market lab surface that is not required for current smart-home/FTX/runtime work.

The target repository exists at:

```text
/Users/marcus.lovenstad/dev/Market-Simulator
https://github.com/marlov74/Market-Simulator.git
```

The target repository is empty except for a short README, so it can receive the migrated source, tests, docs, data and package evidence.

## Assumptions

- `spotprisprognos, förbrukningsprognos, etc` means the Mac-side market simulation/lab code and evidence, not Shelly deploy artifacts.
- `src/shelly/spotprice` and `dep/s/spotprice*` are left in G2 for a later explicit runtime/deploy cleanup package because they are closer to Shelly/runtime history.
- The first migration preserves the existing `src.mac...` Python import namespace inside `Market-Simulator` to avoid a broad rename while moving ownership.

## Risk

- Some historical documentation in G2 may still mention market work. This package removes the active docs/functions and bootstrap market docs but does not rewrite unrelated historical package text.
- Some migrated tests may require local datasets or optional ML dependencies. Verification will run focused smoke tests rather than every long-running lab experiment.
