# P0056N Target Anomaly 2026-03-28

## Classification

`probable_target_source_anomaly`

## Evidence

- Hourly mean actual MW: `5487.60763888889`
- Hourly max actual MW: `7279.0`
- Hourly row count: `24`
- Hourly coverage distribution: `ok:22,partial_hour:2`
- Native mean MW: `5505.787234042553`
- Native max MW: `7306.0`
- Native row count: `94`
- Native resolution distribution: `15:94`
- Interpretation: The 2026-03-28 extreme is already present in P0056A native source rows. Hourly UTC timestamps have normal shape, but the local day has partial source coverage on two hourly rows and only 94 native 15-minute rows instead of an expected 96. The anomaly is not explained by the separate 2026-03-29 DayAhead DST duplicate. Without an independent source it should be treated as a probable target/source anomaly or target-definition/coverage issue, not as a confirmed real load regime.
