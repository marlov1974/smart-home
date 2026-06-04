# Package P0053A: ENTSO-E A09/A11 internal Swedish flow/exchange historical backfill

## Status

planned

## Package order

P0053A

## Primary area

G2 / Mac tooling / spotprice V2 / physical market signals / ENTSO-E A09 scheduled exchange / ENTSO-E A11 physical flow / Swedish internal bidding-zone borders / historical backfill

## Decision summary

P0051 ingested SE1-SE4 production and consumption from eSett.

P0052/P0052A/P0052B/P0052C investigated transfer capacity, exchange and flow. The current decision is:

```text
Use ENTSO-E A09 scheduled exchange and A11 physical flow as historical physical signals.
Do not use ENTSO-E A61 A02/A03/A04 as capacity ceiling, utilization denominator or bottleneck margin.
```

P0052C showed A61 A02/A03/A04 are not safe capacity ceilings because A09 scheduled exchange and A11 physical flow can exceed them materially.

P0053A must now backfill the useful and validated signals across the historical modeling period:

```text
A09 scheduled_exchange_mw
A11 physical_flow_mw
```

for internal Swedish bidding-zone borders:

```text
SE1-SE2
SE2-SE3
SE3-SE4
```

P0053A is a data backfill, validation and feature-dataset package. It must not build a SE3 forecast model yet.

## Preconditions

P0053A may start only after P0052C PASS/WARN evidence exists.

Required P0052C facts:

```text
- token safety was re-verified with no leak
- A61 A02/A03/A04 were sanity-checked against A09 and A11
- A61 is kept blocked for utilization and bottleneck margin
- A09 scheduled exchange is usable as historical observed signal
- A11 physical flow is usable as historical observed signal
- no continental price levels were ingested
```

Required local state:

```text
- ENTSO-E token remains available locally through the same safe mechanism used in P0052A/P0052B/P0052C
- token/secret path remains outside repository or gitignored and non-committable
```

P0053A must STOP before API fetch if token safety cannot be re-verified.

## Scope

P0053A owns:

```text
1. Re-verify token safety without exposing token.
2. Backfill ENTSO-E A09 scheduled exchange for internal Swedish borders.
3. Backfill ENTSO-E A11 physical flow for internal Swedish borders.
4. Cover the full P0051 modeling period if feasible.
5. Store data idempotently in the existing transfer_capacity_flow tables/views.
6. Create or update a clean wide modeling view for internal Swedish A09/A11 signals.
7. Validate coverage, timestamps, direction conventions, duplicates, missingness and joins to price/P0051 data.
8. Create derived net-direction and chain-pressure features.
9. Produce initial diagnostics against SE3 price and SE3-SE1 over the backfilled period.
10. Recommend P0053B physical-regime diagnostics/modeling scope.
```

## Hard non-goals

P0053A must not:

```text
- ingest or use A61 capacity for utilization/bottleneck margin
- create capacity utilization
- create bottleneck margin
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
- retain previously stored A61 raw rows, but exclude them from P0053A derived features and diagnostics unless only used to confirm exclusion
- fetch external non-price flow only if needed to debug ENTSO-E request mechanics, but P0053A deliverables must focus on internal Swedish borders
```

## Secret handling

P0053A must repeat token safety checks from P0052A/P0052B/P0052C.

Required evidence fields:

```text
token_source_class
secret_checked
secret_safe
secret_gitignored_or_outside_repo
token_in_logs = false
token_in_evidence = false
```

P0053A must not include:

```text
- actual token value
- token-bearing URLs
- raw exceptions containing token
- unmasked request strings
```

If any token leakage is detected, STOP and report remediation steps.

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

Required ENTSO-E measures:

```text
A09 scheduled_exchange_mw
A11 physical_flow_mw
```

Do not backfill A61 as part of P0053A unless the code path requires no-op verification. A61 must not be part of derived P0053A features.

## Historical period

Target full overlap period inherited from P0051:

```text
2022-05-29T23:00:00Z .. 2026-05-25T22:00:00Z
```

P0053A should attempt full period backfill.

If runtime/rate limits prevent full range in one run, use restart-safe chunking and continue until complete. If still not feasible, minimum acceptable coverage for WARN is:

```text
2024-01-01T00:00:00Z .. 2026-05-25T22:00:00Z
```

because this covers the pre/post 2024-10-29 flow-based transition plus recent data.

Required evidence:

```text
requested_range
actual_ingested_range_by_border_measure_direction
chunk_size
retry/rate-limit behavior
rows_fetched
rows_inserted_or_reused
failed_chunks
failure_reason
completion_percent_by_border_measure_direction
```

## ENTSO-E request contract

Use the EIC/domain mapping established in P0052A/P0052B.

P0053A must document the actual request contract for:

```text
A09 scheduled exchange
A11 physical flow
```

including:

```text
documentType
processType if used
businessType if used
in_Domain/out_Domain or equivalent
periodStart
periodEnd
resolution
curve type
units
```

Do not include token in evidence.

## Time model

Use the fixed-CET convention already established:

```text
timestamp_utc = primary identity
model_cet_timestamp = timestamp_utc + 1h all year
model_cet_date
model_cet_hour
```

ENTSO-E intervals must be normalized to UTC.

Rules:

```text
- interval start is timestamp identity unless evidence proves otherwise
- PT15M/PT60M periods handled correctly
- MW-like values use hourly mean when aggregating sub-hour intervals
- DST handled through UTC normalization only
- never use timestamp string equality for joins
```

P0053A must explicitly avoid the P0052A bug:

```text
Z vs +00:00 text mismatch
```

## Database contract

Reuse/extend existing P0052 tables:

```text
transfer_capacity_flow_raw_v1
transfer_capacity_flow_hourly_v1
transfer_capacity_flow_se1_se4_hourly_v1
```

Required source labels:

```text
source_name = ENTSO-E Transparency Platform
source_dataset = A09 or A11 plus any relevant process/business labels
```

Required canonical long-format fields:

```text
timestamp_utc
model_cet_timestamp
model_cet_date
model_cet_hour
source_name
source_dataset
document_type
from_area
to_area
border_id
measure
value
unit
flow_type_label
ingested_at_utc
quality_flag
```

Natural key must include at least:

```text
timestamp_utc + source_name + source_dataset + document_type + from_area + to_area + measure + flow_type_label
```

P0053A must not overwrite SvK/Statnett rows unless source identity makes the upsert unambiguous.

## Required wide-view columns

Create/update a clean wide view with at least:

```text
timestamp_utc
model_cet_timestamp
model_cet_date
model_cet_hour
flow_based_market_coupling_flag

scheduled_exchange_se1_to_se2_mw
scheduled_exchange_se2_to_se1_mw
scheduled_exchange_se2_to_se3_mw
scheduled_exchange_se3_to_se2_mw
scheduled_exchange_se3_to_se4_mw
scheduled_exchange_se4_to_se3_mw

physical_flow_se1_to_se2_mw
physical_flow_se2_to_se1_mw
physical_flow_se2_to_se3_mw
physical_flow_se3_to_se2_mw
physical_flow_se3_to_se4_mw
physical_flow_se4_to_se3_mw
```

## Derived feature definitions

P0053A must create derived A09/A11 features that do not require capacity.

Required net-direction features:

```text
net_scheduled_exchange_se1_se2_mw = scheduled_exchange_se1_to_se2_mw - scheduled_exchange_se2_to_se1_mw
net_scheduled_exchange_se2_se3_mw = scheduled_exchange_se2_to_se3_mw - scheduled_exchange_se3_to_se2_mw
net_scheduled_exchange_se3_se4_mw = scheduled_exchange_se3_to_se4_mw - scheduled_exchange_se4_to_se3_mw

net_physical_flow_se1_se2_mw = physical_flow_se1_to_se2_mw - physical_flow_se2_to_se1_mw
net_physical_flow_se2_se3_mw = physical_flow_se2_to_se3_mw - physical_flow_se3_to_se2_mw
net_physical_flow_se3_se4_mw = physical_flow_se3_to_se4_mw - physical_flow_se4_to_se3_mw
```

Positive net values mean north-to-south flow/exchange for the ordered borders:

```text
SE1->SE2
SE2->SE3
SE3->SE4
```

Required chain/pressure features:

```text
north_to_south_scheduled_exchange_min_mw
north_to_south_scheduled_exchange_max_mw
north_to_south_scheduled_exchange_mean_mw
north_to_south_physical_flow_min_mw
north_to_south_physical_flow_max_mw
north_to_south_physical_flow_mean_mw

se3_import_from_se2_scheduled_mw = net_scheduled_exchange_se2_se3_mw
se3_import_from_se2_physical_mw = net_physical_flow_se2_se3_mw
se4_import_from_se3_scheduled_mw = net_scheduled_exchange_se3_se4_mw
se4_import_from_se3_physical_mw = net_physical_flow_se3_se4_mw

southward_exchange_pressure = max(0, net_scheduled_exchange_se2_se3_mw) + max(0, net_scheduled_exchange_se3_se4_mw)
southward_physical_flow_pressure = max(0, net_physical_flow_se2_se3_mw) + max(0, net_physical_flow_se3_se4_mw)
```

P0053A must clearly state these are pressure/exchange diagnostics, not utilization or bottleneck margin.

## Join dataset

Create or document a joined analysis view/table, if practical:

```text
physical_balance_flow_exchange_analysis_v1
```

It should join:

```text
P0051 physical_balance_se1_se4_hourly_v1
P0053A transfer_capacity_flow_se1_se4_hourly_v1 or clean A09/A11 view
SE1/SE3 price and SE3-SE1 source table used in P0050/P0052B diagnostics
```

Minimum columns:

```text
timestamp_utc
model_cet_timestamp
model_cet_date
model_cet_hour
se1_price
se3_price
se3_minus_se1
P0051 production/consumption/net_load features
P0053A scheduled exchange/physical flow features
flow_based_market_coupling_flag
```

This joined dataset is for diagnostics and future P0053B modeling. P0053A must not train a production model.

## Validation

Required validation:

```text
- token safety rechecked and no leak found
- ENTSO-E parser handles A09 and A11 responses
- timestamp normalization to UTC deterministic
- fixed-CET fields derived correctly
- PT15M/PT60M aggregation tested
- no duplicate canonical rows after ingestion
- natural key includes document_type and direction
- values numeric and finite
- units documented
- direction conventions documented
- missing hours reported by border/direction/measure
- wide view has one row per timestamp_utc
- joined analysis view has non-zero rows
- joined rows cover intended historical range
- no A61 capacity used in derived features
- no utilization or bottleneck margin created
- no continental price-level data ingested
- no token in git diff or evidence
```

## Initial diagnostics

P0053A must produce diagnostics over the backfilled period.

Required correlations:

```text
SE3 price vs scheduled_exchange_se2_to_se3_mw
SE3 price vs scheduled_exchange_se3_to_se4_mw
SE3 price vs physical_flow_se2_to_se3_mw
SE3 price vs physical_flow_se3_to_se4_mw
SE3 price vs net_scheduled_exchange_se2_se3_mw
SE3 price vs net_physical_flow_se2_se3_mw
SE3 price vs southward_exchange_pressure
SE3 price vs southward_physical_flow_pressure

SE3-SE1 vs scheduled_exchange_se2_to_se3_mw
SE3-SE1 vs scheduled_exchange_se3_to_se4_mw
SE3-SE1 vs physical_flow_se2_to_se3_mw
SE3-SE1 vs physical_flow_se3_to_se4_mw
SE3-SE1 vs net_scheduled_exchange_se2_se3_mw
SE3-SE1 vs net_physical_flow_se2_se3_mw
SE3-SE1 vs southward_exchange_pressure
SE3-SE1 vs southward_physical_flow_pressure
```

Required event diagnostics:

```text
SE3-SE1 positive bottleneck events vs SE2->SE3 exchange/flow buckets
SE3-SE1 spike events vs SE2->SE3 exchange/flow buckets
SE3 top4/top8 day price events vs SE2->SE3 and SE3->SE4 exchange/flow
pre/post flow-based split for all key diagnostics
```

Do not overinterpret causality. These are historical observed signals.

## Forecast-safety classification

Classify:

```text
scheduled_exchange_mw
physical_flow_mw
net_scheduled_exchange_* features
net_physical_flow_* features
southward_exchange_pressure
southward_physical_flow_pressure
flow_based_market_coupling_flag
```

Allowed labels:

```text
historical_observed_only
forecast_time_known_near_term
requires_separate_forecast_model
not_forecast_safe
```

Expected:

```text
A09/A11 actuals are historical_observed_only.
For future 7-day use they require separate forecast models or proxy assumptions.
```

## Required evidence files

P0053A must create:

```text
requirements/package-runs/P0053A/CHANGELOG.md
requirements/package-runs/P0053A/review.md
requirements/package-runs/P0053A/design.md
requirements/package-runs/P0053A/functions.md
requirements/package-runs/P0053A/secret-handling.md
requirements/package-runs/P0053A/entsoe-a09-a11-source-contracts.md
requirements/package-runs/P0053A/eic-domain-mapping.md
requirements/package-runs/P0053A/database-contract.md
requirements/package-runs/P0053A/backfill-plan-and-summary.md
requirements/package-runs/P0053A/time-normalization-and-dst.md
requirements/package-runs/P0053A/data-validation.md
requirements/package-runs/P0053A/coverage-and-missingness.md
requirements/package-runs/P0053A/direction-conventions.md
requirements/package-runs/P0053A/derived-feature-definitions.md
requirements/package-runs/P0053A/joined-analysis-dataset.md
requirements/package-runs/P0053A/initial-flow-exchange-diagnostics.md
requirements/package-runs/P0053A/pre-post-flow-based-diagnostics.md
requirements/package-runs/P0053A/forecast-safety-classification.md
requirements/package-runs/P0053A/next-package-recommendation.md
requirements/package-runs/P0053A/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0053A/source-contracts.json
requirements/package-runs/P0053A/coverage-summary.json
requirements/package-runs/P0053A/validation-summary.json
requirements/package-runs/P0053A/diagnostics-summary.json
requirements/package-runs/P0053A/modeling-dataset-sample.csv
```

Do not commit large raw API dumps. Do not commit secrets.

## Required answers

P0053A must explicitly answer:

```text
1. Was token safety re-verified with no leak?
2. What historical range was requested and what range was actually backfilled?
3. Were A09 scheduled exchange rows backfilled for all internal Swedish borders and directions?
4. Were A11 physical flow rows backfilled for all internal Swedish borders and directions?
5. What missingness remains per border/direction/measure?
6. What tables/views were updated or created?
7. What derived net-direction and pressure features were created?
8. Did joins to P0051 physical balance and SE3/SE3-SE1 price data succeed?
9. How many joined rows exist?
10. What are the strongest exchange/flow relationships with SE3 price and SE3-SE1?
11. Do relationships differ pre/post flow-based go-live?
12. Are A09/A11 sufficiently complete for P0053B physical-regime diagnostics/modeling?
13. Confirm A61 is excluded from derived features, no utilization/bottleneck margin was created, no token leak, no continental price levels, no SE1-to-SE3 anchoring, no API, no production model and no device actions.
```

## Tests

Required automated tests:

```text
- token loader returns token without printing it
- no token appears in generated evidence
- A09/A11 request builder does not serialize token into evidence
- A09/A11 parser tests pass
- EIC/domain mapping tests cover SE1-SE4
- timestamp normalization avoids Z vs +00:00 mismatch
- fixed-CET fields are derived correctly
- PT15M/PT60M aggregation tests pass
- idempotent ingestion does not duplicate rows
- canonical uniqueness key includes document_type and direction
- net-direction feature formulas are correct
- pressure feature formulas are correct
- wide view has one row per timestamp_utc
- joined analysis dataset returns non-zero rows
- no A61 data is used in derived features
- no utilization/bottleneck margin columns are created or populated by P0053A
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
- A09/A11 are backfilled for the target range or a documented substantial range
- internal Swedish border/direction coverage is validated
- derived exchange/flow features are created
- joins to P0051/price data work
- diagnostics are produced
- P0053B recommendation is explicit
- A61/utilization/margin remain excluded
- forbidden price/API/device/model work is not done
```

WARN is acceptable if:

```text
- full 2022-2026 backfill is not complete but >= 2024-01-01 .. 2026-05-25 is complete
- one direction has sparse rows because actual exchange/flow rarely occurs that way
- API rate limits require follow-up chunking
- physical flow and scheduled exchange differ materially but are documented
```

STOP if:

```text
- token may have leaked
- A09/A11 cannot be backfilled meaningfully
- timestamp/direction semantics cannot be normalized safely
- joins to P0051/price data fail
- Codex ingests external price levels
- Codex creates production/API/device work
```

## Expected Codex output

- PASS/WARN/STOP status
- token safety summary without token value
- backfill range and row counts
- coverage/missingness summary
- tables/views changed
- derived features created
- joined row count
- key diagnostics and pre/post flow-based comparison
- forecast-safety classification
- recommendation for P0053B
- tests run
- files changed
- no token leak / no A61-derived utilization / no continental price levels / no API / no device confirmation
- commit SHA after push

## Completion notes

Completed with status: WARN.

Summary:

- Implemented `src/mac/services/spotprice_model_diagnostics/p0053a.py`.
- Added focused tests in `tests/mac/services/spotprice_model_diagnostics/test_p0053a.py`.
- Added P0053A package-run evidence under `requirements/package-runs/P0053A/`.
- Updated durable function catalog in `docs/functions/mac/spotprice-model-diagnostics.md`.
- Re-verified token safety without printing or storing the token value.
- Backfilled ENTSO-E A09/A11 rows over the full requested target range where the source returned data.
- Created/updated `physical_balance_flow_exchange_analysis_v1`.

Live result:

```text
status = WARN
requested_range = 2022-05-29T23:00:00Z .. 2026-05-25T22:00:00Z
analysis_rows = 34968
analysis_range = 2022-05-29T23:00:00Z .. 2026-05-25T22:00:00Z
canonical_a09_a11_rows_in_range = 231649
failed_chunks = 0
A61 requested = false
```

WARN reason:

- Directional raw coverage is intentionally sparse for low-use reverse directions.
- Full-range net feature coverage is not complete, mainly for older A09 scheduled exchange on SE2-SE3/SE3-SE4.
- WARN-minimum net feature coverage from `2024-01-01T00:00:00Z` through `2026-05-25T22:00:00Z` is substantial: minimum net-feature completion is `95.624%`; A11 net physical flow coverage is at least `99.8%`.

Verification:

```text
PYTHONPYCACHEPREFIX=/private/tmp/p0053a-pycache python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0052 tests.mac.services.spotprice_model_diagnostics.test_p0052a tests.mac.services.spotprice_model_diagnostics.test_p0052b tests.mac.services.spotprice_model_diagnostics.test_p0052c tests.mac.services.spotprice_model_diagnostics.test_p0053a
git diff --check
repo token leak scan: 0 matches
```

No Shelly, Home Assistant, KVS, device, production API, deployable model, continental price-level ingestion, A61 request, utilization derivation or bottleneck-margin derivation was performed.
