# Package P0052C: ENTSO-E A61 capacity sanity check against flow/exchange

## Status

verified PASS

## Package order

P0052C

## Primary area

G2 / Mac tooling / spotprice V2 / physical market signals / ENTSO-E A61 sanity check / capacity vs scheduled exchange / capacity vs physical flow

## Decision summary

P0052B reviewed ENTSO-E A61 capacity concepts and concluded that A61 A02/A03/A04 should be stored but not used for utilization or bottleneck margin because concept compatibility remained uncertain.

P0052C adds a focused sanity check:

```text
Compare ENTSO-E A61 A02/A03/A04 capacity values against actual A09 scheduled exchange and A11 physical flow.
```

If scheduled exchange or physical flow often exceeds an A61 capacity value, that A61 variant is not a valid hourly capacity ceiling for our purposes.

If scheduled exchange never exceeds a specific A61 variant, that variant may be a candidate market-capacity proxy, subject to further review.

P0052C is an analysis/amendment package only. It must not build a model or production forecast.

## Preconditions

P0052C may start only after P0052B WARN evidence exists.

Required P0052B facts:

```text
- token safety was re-verified with no leak
- A61 A02/A03/A04 were identified as weekly/monthly/yearly capacity contract types
- no A61 contract type was selected for utilization diagnostics
- A09 scheduled_exchange_mw and A11 physical_flow_mw exist for internal Swedish borders
- join issue was fixed by timestamp normalization
- diagnostics have non-zero joined rows
```

P0052C must STOP before API fetch if token safety cannot be re-verified.

## Scope

P0052C owns:

```text
1. Re-verify token safety without exposing token.
2. Ensure A09/A11/A61 data exists for the chosen sanity-check windows.
3. Join A61 capacity values to A09 scheduled exchange and A11 physical flow by timestamp, border, direction and contract type.
4. Compute ratio tests per border/direction/contract/flow-type.
5. Report whether exchange/flow ever exceeds capacity.
6. Decide whether any A61 variant can be considered a candidate capacity ceiling.
7. Update P0052B/P0052C evidence with a clear recommendation.
```

## Hard non-goals

P0052C must not:

```text
- ingest continental price levels
- start the parked continental price-pressure model
- build SE3 forecast API
- build SE3 or SE3-SE1 production model
- anchor SE1 to SE3
- train direct SE3 AI-1/AI-2
- touch Shelly/Home Assistant/KVS/devices
- build M5/M6/M7
- ingest futures/forward curves
```

Allowed:

```text
- use already ingested or newly fetched ENTSO-E A09/A11/A61 internal Swedish border data
- fetch additional A09/A11/A61 rows for sanity-check windows if needed
```

## Secret handling

P0052C must repeat token safety checks from P0052A/P0052B.

Required evidence fields:

```text
token_source_class
secret_checked
secret_safe
secret_gitignored_or_outside_repo
token_in_logs = false
token_in_evidence = false
```

Do not include actual token value, token-bearing URLs, or unmasked request strings.

## Borders and directions

Primary internal Swedish borders:

```text
SE1-SE2
SE2-SE3
SE3-SE4
```

Directions:

```text
SE1->SE2
SE2->SE1
SE2->SE3
SE3->SE2
SE3->SE4
SE4->SE3
```

For each direction, compare:

```text
A61 A02 capacity_mw vs A09 scheduled_exchange_mw
A61 A03 capacity_mw vs A09 scheduled_exchange_mw
A61 A04 capacity_mw vs A09 scheduled_exchange_mw

A61 A02 capacity_mw vs A11 physical_flow_mw
A61 A03 capacity_mw vs A11 physical_flow_mw
A61 A04 capacity_mw vs A11 physical_flow_mw
```

## Required sanity-check windows

Use the P0052B representative windows at minimum:

```text
2025-01-01T00:00:00Z .. 2025-01-07T23:00:00Z
2024-10-27T00:00:00Z .. 2024-11-03T23:00:00Z
2026-05-01T00:00:00Z .. 2026-05-07T23:00:00Z
```

If feasible, extend to:

```text
2025 full year
2024-09-01 .. 2024-12-31
full P0051 range 2022-05-29 .. 2026-05-25
```

But do not spend excessive runtime on full backfill if the sanity check can answer the conceptual question with representative windows.

## Join rules

The join must be based on normalized timestamps, not string equality.

Required join keys:

```text
timestamp_utc normalized to UTC instant
from_area
to_area
border_id
contract_type for A61
measure type for A09/A11
```

P0052C must explicitly avoid the P0052A bug:

```text
Z vs +00:00 exact text mismatch
```

## Ratio definitions

For each timestamp/border/direction/contract:

```text
scheduled_exchange_ratio = abs(scheduled_exchange_mw) / capacity_mw
physical_flow_ratio = abs(physical_flow_mw) / capacity_mw
```

If direction is already directional and values are non-negative, still use abs only after documenting why it is safe. If the source stores signed values for direction, use direction-correct positive flow.

Invalid cases:

```text
capacity_mw <= 0 -> ratio = null and flagged invalid_capacity
missing capacity -> missing_capacity
missing flow/exchange -> missing_flow_or_exchange
```

Do not silently clip ratios.

## Required metrics

For each:

```text
contract_type: A02/A03/A04
border_direction
comparison_type: scheduled_exchange vs physical_flow
period/window
pre/post flow-based era
```

compute:

```text
count_compared
count_missing_capacity
count_missing_flow_or_exchange
count_invalid_capacity
max_ratio
p50_ratio
p90_ratio
p95_ratio
p99_ratio
count_ratio_gt_1_00
count_ratio_gt_1_02
count_ratio_gt_1_05
count_ratio_gt_1_10
share_ratio_gt_1_00
share_ratio_gt_1_05
worst_10_examples
```

Worst examples must include:

```text
timestamp_utc
from_area
to_area
contract_type
capacity_mw
scheduled_exchange_mw or physical_flow_mw
ratio
source_dataset labels
```

No token or token-bearing URL may appear in examples.

## Interpretation rules

P0052C must classify each A61 contract type separately.

Candidate categories:

```text
candidate_market_capacity_proxy
candidate_physical_capacity_proxy
not_capacity_ceiling_exchange_exceeds
not_capacity_ceiling_flow_exceeds
insufficient_overlap
invalid_or_missing_capacity
inconclusive
```

Rules:

```text
If scheduled_exchange_ratio never exceeds 1.00 or only exceeds by tiny documented rounding tolerance, mark as candidate_market_capacity_proxy.

If physical_flow_ratio often exceeds 1.00 but scheduled_exchange_ratio does not, mark candidate_market_capacity_proxy but not physical_capacity_proxy.

If scheduled_exchange_ratio exceeds 1.05 frequently or materially, mark not_capacity_ceiling_exchange_exceeds.

If physical_flow_ratio exceeds 1.05 frequently while exchange does not, document likely loop-flow/physical-vs-market distinction.

If too few rows overlap, mark insufficient_overlap.
```

Tolerance guidance:

```text
<= 1.02 may be rounding/timestamp/aggregation tolerance if rare.
> 1.05 requires review.
> 1.10 is material violation.
```

## Flow-based era split

P0052C must split results by:

```text
pre_flow_based: before 2024-10-29
post_flow_based: on/after 2024-10-29
```

It must report whether A61 ratio behavior changes across the flow-based transition.

If only post-flow-based windows are available, state this as a limitation.

## Derived outputs

P0052C must not enable utilization/bottleneck margin globally.

It may recommend one of:

```text
1. keep A61 blocked
2. allow A61 contract type X as candidate market-capacity proxy for diagnostics only
3. allow A61 contract type X as candidate physical-capacity proxy for diagnostics only
4. require more backfill/concept work
```

Even if a contract type passes sanity checks, any utilization/margin feature must be labeled:

```text
experimental_capacity_proxy
```

until a later package explicitly accepts it.

## Required evidence files

P0052C must create:

```text
requirements/package-runs/P0052C/CHANGELOG.md
requirements/package-runs/P0052C/review.md
requirements/package-runs/P0052C/design.md
requirements/package-runs/P0052C/functions.md
requirements/package-runs/P0052C/secret-handling.md
requirements/package-runs/P0052C/capacity-sanity-check-method.md
requirements/package-runs/P0052C/capacity-vs-scheduled-exchange-results.md
requirements/package-runs/P0052C/capacity-vs-physical-flow-results.md
requirements/package-runs/P0052C/worst-ratio-examples.md
requirements/package-runs/P0052C/pre-post-flow-based-ratio-review.md
requirements/package-runs/P0052C/contract-type-classification.md
requirements/package-runs/P0052C/next-package-recommendation.md
requirements/package-runs/P0052C/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0052C/capacity-ratio-summary.json
requirements/package-runs/P0052C/worst-ratio-examples.csv
requirements/package-runs/P0052C/contract-type-classification.json
```

Do not commit large raw API dumps. Do not commit secrets.

## Required answers

P0052C must explicitly answer:

```text
1. Was token safety re-verified with no leak?
2. Which windows were checked?
3. How many rows overlapped between A61 and A09/A11 per contract/border/direction?
4. Does A09 scheduled exchange ever exceed A61 A02 capacity?
5. Does A09 scheduled exchange ever exceed A61 A03 capacity?
6. Does A09 scheduled exchange ever exceed A61 A04 capacity?
7. Does A11 physical flow ever exceed A61 A02/A03/A04 capacity?
8. Are violations rare/tiny or frequent/material?
9. Which contract type, if any, is a candidate market-capacity proxy?
10. Which contract type, if any, is a candidate physical-capacity proxy?
11. Does behavior differ pre/post 2024-10-29 flow-based go-live?
12. Should A61 remain blocked or be allowed as experimental capacity proxy in the next package?
13. Confirm no token leak, no continental price levels, no SE1-to-SE3 anchoring, no API, no production model and no device actions.
```

## Tests

Required automated tests:

```text
- token loader returns token without printing it
- no token appears in generated evidence
- timestamp normalization avoids Z vs +00:00 mismatch
- ratio formula handles null/zero capacity safely
- ratio calculation is per direction and contract type
- worst examples do not contain secrets
- pre/post flow-based split is deterministic
- no continental price-level document types are requested/ingested
- no SE1 shape is anchored to SE3
- no production forecast API is created
- no deployable model artifact is created
- no M5/M6/M7/API/device path is touched
```

## Pass/fail interpretation

PASS requires:

```text
- token remains safe
- A61 vs A09/A11 overlap is measured
- ratio metrics are reported by contract/border/direction
- worst violations are listed if present
- each contract type is classified
- recommendation for A61 blocked vs experimental proxy is explicit
- forbidden price/API/device/model work is not done
```

WARN is acceptable if:

```text
- overlap is limited but enough for preliminary classification
- physical flow violates capacity while scheduled exchange does not
- pre/post flow-based comparison is limited
- a contract type is only suitable as experimental diagnostic proxy
```

STOP if:

```text
- token may have leaked
- no meaningful A61/A09/A11 overlap can be created
- timestamp/direction semantics cannot be normalized safely
- Codex ingests external price levels
- Codex creates production/API/device work
```

## Expected Codex output

- PASS/WARN/STOP status
- token safety summary without token value
- checked windows
- overlap counts
- ratio summaries by contract/border/direction
- worst violation examples
- pre/post flow-based comparison
- contract-type classification
- recommendation for next package
- tests run
- files changed
- no token leak / no continental price levels / no API / no device confirmation
- commit SHA after push

## Completion notes

P0052C completed as `PASS` on 2026-06-03.

Result:

```text
source_rows = 8190
ratio_observations = 5492
metric_rows = 144
worst_examples = 10
```

Checked windows:

```text
2025-01-01T00:00:00Z .. 2025-01-07T23:00:00Z
2024-10-27T00:00:00Z .. 2024-11-03T23:00:00Z
2026-05-01T00:00:00Z .. 2026-05-07T23:00:00Z
```

Contract classification:

```text
A02 = keep_blocked
A03 = keep_blocked
A04 = keep_blocked
```

Key findings:

```text
- A09 scheduled exchange materially exceeded all A61 contract types in post-flow-based data.
- A11 physical flow materially exceeded all A61 contract types in post-flow-based data.
- A02 scheduled_exchange max ratio = 1.1414; physical_flow max ratio = 1.3079.
- A03 scheduled_exchange max ratio = 1.1414; physical_flow max ratio = 1.3079.
- A04 scheduled_exchange max ratio = 1.2977; physical_flow max ratio = 1.3582.
- Pre-flow-based sample did not exceed 1.05, but overlap is smaller and does not override post-flow-based violations.
```

Required answers:

```text
1. Token safety was re-verified and no token leak was found.
2. Checked the three required representative windows listed above.
3. Overlap counts: A02 scheduled 580 / physical 479; A03 scheduled 464 / physical 407; A04 scheduled 1932 / physical 1630.
4. A09 scheduled exchange exceeds A61 A02 capacity.
5. A09 scheduled exchange exceeds A61 A03 capacity.
6. A09 scheduled exchange exceeds A61 A04 capacity.
7. A11 physical flow exceeds A61 A02/A03/A04 capacity.
8. Violations are material in post-flow-based data, including ratios above 1.10.
9. No A61 contract type is a candidate market-capacity proxy.
10. No A61 contract type is a candidate physical-capacity proxy.
11. Behavior differs: pre-flow-based sample had no >1.05 violations, while post-flow-based sample had material violations.
12. A61 should remain blocked for utilization and bottleneck margin. Do not allow it as experimental proxy without a different source/concept.
13. Confirmed: no token leak, no continental price levels, no SE1-to-SE3 anchoring, no API, no production model and no device actions.
```

Tests run:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0052c
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0048 tests.mac.services.spotprice_model_diagnostics.test_p0049 tests.mac.services.spotprice_model_diagnostics.test_p0050 tests.mac.services.spotprice_model_diagnostics.test_p0051 tests.mac.services.spotprice_model_diagnostics.test_p0052 tests.mac.services.spotprice_model_diagnostics.test_p0052a tests.mac.services.spotprice_model_diagnostics.test_p0052b tests.mac.services.spotprice_model_diagnostics.test_p0052c
```

Evidence:

```text
requirements/package-runs/P0052C/
src/mac/services/spotprice_model_diagnostics/p0052c.py
tests/mac/services/spotprice_model_diagnostics/test_p0052c.py
```
