# Package P0052B: ENTSO-E capacity concept review, join fix and historical backfill

## Status

planned

## Package order

P0052B

## Primary area

G2 / Mac tooling / spotprice V2 / physical market signals / ENTSO-E A61 capacity concepts / scheduled exchange / physical flow / historical backfill / bottleneck margin

## Decision summary

P0052A proved that the local ENTSO-E token works and that ENTSO-E exposes internal Swedish bidding-zone data for:

```text
A09 scheduled exchange
A11 physical flow
A61 capacity rows for contract types A02/A03/A04
```

for internal Swedish borders:

```text
SE1-SE2
SE2-SE3
SE3-SE4
```

However P0052A remained WARN because:

```text
- ingestion was limited to 2026-05-01 .. 2026-05-25
- A61 A02/A03/A04 capacity semantics were not reviewed enough to compute utilization safely
- pre/post 2024-10-29 flow-based comparability was not proven
- diagnostics joined zero rows to price data
```

P0052B must fix those issues before any physical-regime model is built.

P0052B is still a data/contract/backfill/validation package. It must not build a production SE3 forecast or bottleneck model.

## Preconditions

P0052B may start only after P0052A WARN evidence exists.

Required P0052A facts:

```text
- token was handled safely with no leak
- EIC/domain mapping exists for SE1-SE4
- ENTSO-E A09/A11/A61 returned internal Swedish border rows
- A61 A02/A03/A04 returned capacity rows in the discovery window
- P0052A updated transfer_capacity_flow_raw_v1, transfer_capacity_flow_hourly_v1 and transfer_capacity_flow_se1_se4_hourly_v1
- P0052A diagnostics had joined_rows = 0 and therefore need a join/timestamp/view fix
```

Required local state:

```text
- ENTSO-E token remains available locally through the same safe mechanism used in P0052A
- token/secret path remains outside repository or gitignored and non-committable
```

P0052B must STOP before API fetch if token safety cannot be re-verified.

## Scope

P0052B owns:

```text
1. Re-verify token safety without exposing token.
2. Review ENTSO-E A61 A02/A03/A04 capacity semantics using official/API-local evidence where available.
3. Decide which capacity concept, if any, is suitable for utilization/bottleneck-margin diagnostics.
4. Fix the P0052A zero-row diagnostics join.
5. Backfill A09/A11/A61 for the historical overlap period needed for modeling.
6. Split and compare pre/post Nordic flow-based market coupling go-live.
7. Create safe utilization and bottleneck-margin features only if concept review passes.
8. Update evidence with coverage, validation, joins and diagnostics.
9. Recommend whether P0053 can begin physical-regime modeling or whether source/concept work must continue.
```

## Hard non-goals

P0052B must not:

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
- external flow/capacity discovery only when needed to understand ENTSO-E contracts
- no external price-level ingestion
```

## Secret handling

P0052B must repeat the P0052A secret-safety check.

Required evidence fields:

```text
token_source_class
secret_checked
secret_safe
secret_gitignored_or_outside_repo
file_mode_or_unavailable_reason
directory_mode_or_unavailable_reason
token_in_logs = false
token_in_evidence = false
```

P0052B must not include:

```text
- actual token value
- token-bearing URLs
- raw exceptions containing token
- unmasked request strings
```

If any token leakage is detected, STOP and report remediation steps.

## Capacity concept review

P0052B must determine what A61 contract types mean in the ENTSO-E API context.

P0052A found rows for:

```text
A61 A02
A61 A03
A61 A04
```

P0052B must document:

```text
contract_type
ENTSO-E label/meaning
whether it is directional
whether it is a capacity value suitable for flow/capacity utilization
whether it represents forecasted/offered/allocated capacity
publication timing if discoverable
whether it is comparable before/after 2024-10-29
whether it should be used for modeling diagnostics
```

If exact meaning cannot be proven from local code/API/docs, P0052B must mark it:

```text
capacity_concept_uncertain
```

and must not compute production-intent utilization from it.

P0052B should keep raw/canonical storage even if concept remains uncertain, but derived utilization must remain null in that case.

## Border and EIC coverage

Primary internal borders:

```text
SE1-SE2
SE2-SE3
SE3-SE4
```

Directions:

```text
SE1->SE2 and SE2->SE1
SE2->SE3 and SE3->SE2
SE3->SE4 and SE4->SE3
```

Required measures to backfill where available:

```text
A09 scheduled_exchange_mw
A11 physical_flow_mw
A61 capacity_mw by validated contract type(s)
```

P0052B must keep `from_area`, `to_area`, `border_id`, `measure`, `document_type`, `contract_type` and `capacity_method_label` explicit.

## Historical backfill

Requested full modeling overlap:

```text
2022-05-29T23:00:00Z .. 2026-05-25T22:00:00Z
```

P0052B should backfill the full range if feasible.

If full range is too slow/rate-limited, minimum acceptable backfill windows are:

```text
1. 2025-01-01T00:00:00Z .. 2025-12-31T23:00:00Z
2. 2024-09-01T00:00:00Z .. 2024-12-31T23:00:00Z   # pre/post flow-based transition window
3. 2026-05-01T00:00:00Z .. 2026-05-25T22:00:00Z   # P0052A overlap revalidation
```

P0052B must chunk API requests safely and idempotently. It must respect API rate limits and store progress in a restart-safe way if repository conventions support it.

Required evidence:

```text
requested_range
actual_ingested_range_by_border_measure_contract
chunk_size
retry/rate-limit behavior
rows_inserted_or_upserted
rows_reused
failed_chunks
failure_reason
```

## Join fix

P0052A diagnostics had:

```text
joined_rows = 0
```

P0052B must diagnose and fix why the ENTSO-E capacity/flow view did not join to:

```text
se3_se1_demand_response_analysis_v1
```

Required checks:

```text
- timestamp_utc data type and timezone normalization
- fixed-CET derived fields
- hourly aggregation timestamp boundary convention
- table/view source filters
- document_type/contract_type filtering
- null columns in wide view
- price table range overlap
- duplicate timestamp rows in wide view
```

PASS requires a non-zero join for any period where ENTSO-E data and price data overlap, unless price data truly lacks that period.

## Time model

Use existing fixed-CET convention:

```text
timestamp_utc = primary identity
model_cet_timestamp = timestamp_utc + 1h all year
model_cet_date
model_cet_hour
```

ENTSO-E intervals must be normalized to UTC.

Rules:

```text
- PT15M/PT60M periods handled correctly
- hourly MW values use mean when aggregating sub-hour intervals
- interval start is the timestamp identity unless source evidence proves otherwise
- DST handled only through UTC normalization
```

## Database contract

Reuse/extend:

```text
transfer_capacity_flow_raw_v1
transfer_capacity_flow_hourly_v1
transfer_capacity_flow_se1_se4_hourly_v1
```

Do not break P0052/P0052A existing SvK/Statnett rows.

Required canonical long-format additions if not already present:

```text
document_type
process_type
business_type
contract_type
entsoe_curve_type
entsoe_resolution
capacity_concept_status
```

Required wide-view columns where data exists:

```text
scheduled_exchange_se1_to_se2_mw
scheduled_exchange_se2_to_se1_mw
physical_flow_se1_to_se2_mw
physical_flow_se2_to_se1_mw
capacity_se1_to_se2_mw
capacity_se2_to_se1_mw

scheduled_exchange_se2_to_se3_mw
scheduled_exchange_se3_to_se2_mw
physical_flow_se2_to_se3_mw
physical_flow_se3_to_se2_mw
capacity_se2_to_se3_mw
capacity_se3_to_se2_mw

scheduled_exchange_se3_to_se4_mw
scheduled_exchange_se4_to_se3_mw
physical_flow_se3_to_se4_mw
physical_flow_se4_to_se3_mw
capacity_se3_to_se4_mw
capacity_se4_to_se3_mw
```

For derived north-to-south features, prefer north-to-south direction:

```text
SE1->SE2
SE2->SE3
SE3->SE4
```

## Derived utilization and bottleneck margin

Only if capacity concept review passes, create:

```text
flow_or_exchange_se1_to_se2_mw
flow_or_exchange_se2_to_se3_mw
flow_or_exchange_se3_to_se4_mw

utilization_se1_se2_north_to_south
utilization_se2_se3_north_to_south
utilization_se3_se4_north_to_south

bottleneck_margin_se1_se2_north_to_south
bottleneck_margin_se2_se3_north_to_south
bottleneck_margin_se3_se4_north_to_south

north_to_south_capacity_min
north_to_south_utilization_max
north_to_south_bottleneck_margin_min
north_to_south_binding_border_candidate
```

Definitions:

```text
flow_or_exchange = prefer scheduled_exchange if concept aligns with market capacity; otherwise physical_flow for physical diagnostics only.
utilization = max(0, north_to_south_flow_or_exchange) / north_to_south_capacity
bottleneck_margin = north_to_south_capacity - max(0, north_to_south_flow_or_exchange)
```

If using physical_flow instead of scheduled_exchange, label derived features:

```text
physical_diagnostic_only
```

If capacity concept remains uncertain, all utilization/margin features must remain null and diagnostics must explain why.

## Flow-based market coupling review

Known transition to verify/document:

```text
2024-10-29 Nordic flow-based market coupling go-live
```

P0052B must compare data availability and concept labels across:

```text
pre_flow_based: before 2024-10-29
post_flow_based: on/after 2024-10-29
```

Required report:

```text
- are A61 contract types available before go-live?
- are A61 contract types available after go-live?
- do values/ranges look comparable?
- does ENTSO-E represent flow-based capacity differently?
- should model features include flow_based_market_coupling_flag?
```

## Validation

Required validation:

```text
- token safety rechecked and no leak found
- ENTSO-E parser handles A09, A11 and A61 responses
- timestamp normalization to UTC deterministic
- fixed-CET fields derived correctly
- no duplicate canonical rows after ingestion
- natural key includes document_type + contract_type where relevant
- values numeric and finite
- capacity values non-negative
- units documented
- direction conventions documented
- hourly aggregation tested for PT15M/PT60M
- missing hours reported by border/measure/contract
- wide view has one row per timestamp_utc
- join to price table has non-zero rows in overlap
- no continental price-level data ingested
- no token in git diff or evidence
```

## Diagnostics

If join is fixed, compute diagnostics for at least:

```text
SE3 price vs scheduled_exchange_se2_to_se3_mw
SE3 price vs scheduled_exchange_se3_to_se4_mw
SE3 price vs physical_flow_se2_to_se3_mw
SE3 price vs physical_flow_se3_to_se4_mw
SE3-SE1 vs scheduled_exchange_se2_to_se3_mw
SE3-SE1 vs scheduled_exchange_se3_to_se4_mw
SE3-SE1 vs physical_flow_se2_to_se3_mw
SE3-SE1 vs physical_flow_se3_to_se4_mw
```

If utilization/margin is safe:

```text
SE3-SE1 vs utilization_se2_se3_north_to_south
SE3-SE1 vs utilization_se3_se4_north_to_south
SE3-SE1 vs bottleneck_margin_se2_se3_north_to_south
SE3-SE1 vs bottleneck_margin_se3_se4_north_to_south
SE3-SE1 by utilization bucket
SE3-SE1 spike events by binding_border_candidate
pre/post flow-based diagnostic split
```

If utilization/margin is not safe, explicitly state:

```text
capacity stored but not used for utilization because capacity_concept_status = uncertain
```

## Forecast-safety classification

Classify:

```text
scheduled_exchange_mw
physical_flow_mw
capacity_mw by contract_type
utilization
bottleneck_margin
flow_based_market_coupling_flag
```

Allowed labels:

```text
historical_observed_only
forecast_time_known_near_term
forecastable_from_grid/outage/capacity_publication
requires_separate_forecast_model
not_forecast_safe
not_forecast_safe_until_capacity_concept_review
```

Be conservative.

## Required evidence files

P0052B must create:

```text
requirements/package-runs/P0052B/CHANGELOG.md
requirements/package-runs/P0052B/review.md
requirements/package-runs/P0052B/design.md
requirements/package-runs/P0052B/functions.md
requirements/package-runs/P0052B/secret-handling.md
requirements/package-runs/P0052B/entsoe-capacity-concept-review.md
requirements/package-runs/P0052B/entsoe-source-contracts.md
requirements/package-runs/P0052B/eic-domain-mapping.md
requirements/package-runs/P0052B/database-contract.md
requirements/package-runs/P0052B/backfill-plan-and-summary.md
requirements/package-runs/P0052B/time-normalization-and-dst.md
requirements/package-runs/P0052B/data-validation.md
requirements/package-runs/P0052B/coverage-and-missingness.md
requirements/package-runs/P0052B/direction-conventions.md
requirements/package-runs/P0052B/join-fix-analysis.md
requirements/package-runs/P0052B/flow-based-era-review.md
requirements/package-runs/P0052B/derived-feature-definitions.md
requirements/package-runs/P0052B/capacity-utilization-and-margin-diagnostics.md
requirements/package-runs/P0052B/forecast-safety-classification.md
requirements/package-runs/P0052B/next-package-recommendation.md
requirements/package-runs/P0052B/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0052B/capacity-concept-review.json
requirements/package-runs/P0052B/source-contracts.json
requirements/package-runs/P0052B/coverage-summary.json
requirements/package-runs/P0052B/validation-summary.json
requirements/package-runs/P0052B/diagnostics-summary.json
requirements/package-runs/P0052B/modeling-dataset-sample.csv
```

Do not commit large raw API dumps. Do not commit secrets.

## Required answers

P0052B must explicitly answer:

```text
1. Was token safety re-verified with no leak?
2. What do A61 A02, A03 and A04 mean in this ENTSO-E context?
3. Which A61 contract type, if any, should be used as capacity for utilization diagnostics?
4. Does ENTSO-E internal Swedish capacity cover SE1-SE2, SE2-SE3 and SE3-SE4 historically?
5. Does ENTSO-E internal Swedish A09/A11 cover those borders historically?
6. What range was backfilled per border/measure/contract?
7. Why did P0052A diagnostics join zero rows, and what was fixed?
8. How many rows now join to SE3 price / SE3-SE1 data?
9. Are pre/post 2024-10-29 capacity concepts comparable?
10. Can utilization and bottleneck margin be computed safely?
11. If yes, do utilization/margin signals relate to SE3 price or SE3-SE1?
12. If no, what remains blocked?
13. Which signals are forecast-safe and which are historical-only?
14. Should P0053 begin physical-regime modeling or continue source/concept work?
15. Confirm no token leak, no continental price levels, no SE1-to-SE3 anchoring, no API, no production model and no device actions.
```

## Tests

Required automated tests:

```text
- token loader returns a token without printing it
- token is masked in request/error logging
- no token appears in git diff, package-run evidence or generated json/csv
- A09/A11/A61 parser tests pass
- A61 contract type mapping is documented/tested
- EIC/domain mapping tests cover SE1-SE4
- timestamp normalization to UTC is deterministic
- fixed-CET fields are derived correctly
- PT15M/PT60M aggregation tests pass
- idempotent ingestion does not duplicate rows
- canonical uniqueness key includes document_type and contract_type
- wide view has one row per timestamp_utc
- join to price table returns non-zero rows in overlap
- utilization formula handles null/zero/uncertain capacity safely
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
- A61 capacity concepts are reviewed and documented
- P0052A join issue is fixed
- useful historical backfill exists for at least one meaningful window
- diagnostics run with non-zero joined rows
- utilization/margin is either safely computed or explicitly blocked by documented concept uncertainty
- next package recommendation is explicit
- forbidden price/API/device/model work is not done
```

WARN is acceptable if:

```text
- full 2022-2026 backfill is not completed but representative windows are
- capacity concept remains partly uncertain, so utilization remains blocked
- pre/post flow-based comparability is inconclusive
- rate limits require smaller chunks or follow-up package
```

STOP if:

```text
- token may have leaked
- secret path is committable
- join issue cannot be diagnosed
- timestamp or direction semantics cannot be normalized safely
- data cannot be mapped to internal Swedish borders
- Codex ingests external price levels
- Codex creates production/API/device work
```

## Expected Codex output

- PASS/WARN/STOP status
- token safety summary without token value
- A61 concept review conclusion
- selected capacity concept or reason none selected
- backfill range and row counts
- join-fix summary and joined row count
- pre/post flow-based review
- utilization/margin status
- diagnostics summary
- forecast-safety classification
- recommendation for P0053
- tests run
- files changed
- no token leak / no continental price levels / no API / no device confirmation
- commit SHA after push

## Completion notes

To be filled after implementation.
