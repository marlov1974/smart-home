# Hot Water / VVB / VVC Baseline

## Scope

This file is a placeholder for domestic hot water, VVB and VVC physical/system knowledge.

## Current imported baseline

VP1 has a daily sacred opportunity to restore its domestic-hot-water tank:

```text
00-02
```

In summer, the protected low operating level is intended to let VP1 handle domestic hot water without meaningful house-heating intent:

```text
VP1 20/52
```

VP2 low/base support can be:

```text
VP2 28/52
```

## Open gaps

To be filled by later packages:

- VVB hardware identity
- VVC hardware identity
- VVC schedule/default behavior
- temperature sensors and IDs
- Home Assistant integration points
- fallback/default behavior
- interaction with heat-pump planner

## Source

Imported from G1 heat-pump operating schedule memory during `P0002`.
