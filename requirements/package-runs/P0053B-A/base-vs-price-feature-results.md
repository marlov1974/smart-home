# P0053B-A Base Vs Price Feature Results

## Status

No base-vs-G7 model comparison was run.

## Reason

The package stopped before modeling because no forecast-safe historical SE1 price forecast source was found.

## Metrics

Not available:

```text
M4_base
M4_plus_G7
M7_base
M7_plus_G7
```

Running these comparisons without a valid G7 source would either use actual future prices or originless predictions, both of which violate the package safety rules.
