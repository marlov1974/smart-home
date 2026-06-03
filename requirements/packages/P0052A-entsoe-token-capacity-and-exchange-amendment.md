# Package P0052A: ENTSO-E token capacity and exchange amendment

## Status

verified WARN

## Package order

P0052A

## Primary area

G2 / Mac tooling / spotprice V2 / physical market signals / ENTSO-E token / transfer capacity / scheduled exchange / Swedish bidding-zone borders

## Decision summary

P0052 produced useful short-range SvK/Statnett flow/import-export data but could not retrieve historical capacity because ENTSO-E required a security token.

The ENTSO-E token now exists locally under a secret directory inside the `smart-home` working tree.

P0052A is an amendment package. Its job is to use the local ENTSO-E token safely to investigate and, where possible, ingest historical transfer capacity, offered capacity, allocated capacity, scheduled commercial exchange and/or physical-flow data relevant to Swedish bidding-zone borders.

The token must never be committed, logged, printed in evidence, or written to package-run files.

## Preconditions

P0052A may start only after P0052 WARN evidence exists.

Required P0052 facts:

```text
- SvK/Statnett auth-free source gave recent SE1-SE4 flows/import-export only.
- Selected SvK/Statnett source had no capacity fields.
- ENTSO-E Transparency Platform was blocked by missing security token.
- P0052 created transfer_capacity_flow_raw_v1, transfer_capacity_flow_hourly_v1 and transfer_capacity_flow_se1_se4_hourly_v1.
- P0052 did not ingest continental price levels.
```

Required local state:

```text
- ENTSO-E security token is available locally under a secret directory inside smart-home.
- The secret directory is gitignored or otherwise confirmed not committable.
```

P0052A must STOP before any API fetch if the token path cannot be found safely or if the secret directory appears in `git status --short` as committable/unignored.

## Secret handling

P0052A must support reading the token from one or more local-only mechanisms:

```text
1. ENTSOE_SECURITY_TOKEN environment variable
2. local .env file, if already supported by project conventions
3. local secret file under smart-home secret directory
```

Codex must discover the local secret path without printing the token.

Required secret rules:

```text
- never echo the token
- never log the token
- never write the token to markdown/json/csv/sql evidence
- never include token in command history snippets or example requests
- mask token in any error messages if upstream libraries include request URLs
- confirm secret directory is ignored by git
- do not modify token storage except if needed to read it
```

Evidence may say:

```text
token_source = local_secret_file or environment
secret_checked = true
secret_gitignored = true
```

Evidence must not include actual path if the path name itself reveals the token or secret value. A generic path class is enough.

## Scope

P0052A owns:

```text
1. Use ENTSO-E token to query Transparency API safely.
2. Determine whether ENTSO-E provides historical capacity/exchange/flow for internal Swedish bidding-zone borders SE1-SE2, SE2-SE3 and SE3-SE4.
3. If internal Swedish borders are available, ingest the relevant data for the P0051 historical period where possible.
4. If internal Swedish borders are not available, document exact API/document-type/domain evidence and test external Swedish bidding-zone borders only as source discovery, without importing continental price levels.
5. Create/update database tables/views from P0052 contract without breaking existing SvK/Statnett data.
6. Create capacity/utilization/bottleneck-margin features only when the capacity concept is valid and documented.
7. Update P0052A evidence and recommend the next route.
```

## Hard non-goals

P0052A must not:

```text
- ingest external price levels such as DE/DK/PL/Baltic prices
- start the parked continental price-pressure model
- build a SE3 forecast model
- build a SE3-SE1 bottleneck model
- build production API
- anchor SE1 to SE3
- train direct SE3 AI-1/AI-2
- touch Shelly/Home Assistant/KVS/devices
- build M5/M6/M7
- ingest futures/forward curves
```

Clarification:

```text
External cross-border capacity/flow to DK/FI/NO/LT/PL/DE may be discovered if it helps determine ENTSO-E coverage or zone import/export completeness.
But price levels for those areas remain out of scope.
```

## ENTSO-E document/API discovery

P0052A must investigate relevant ENTSO-E Transparency API document types and process types for:

```text
- offered transfer capacity / cross-border capacity
- net transfer capacity / NTC if available
- allocated capacity
- scheduled commercial exchange
- physical flow
- total commercial schedules if applicable
```

Codex must document the actual API parameters that worked or failed, including:

```text
documentType
processType
businessType if used
in_Domain / out_Domain
periodStart / periodEnd
area EIC codes
resolution
curve type
units
timezone semantics
```

Do not guess EIC codes silently. Discover and document the domain codes used for:

```text
SE1
SE2
SE3
SE4
SE
DK1
DK2
FI
NO1/NO2/NO3/NO4 as needed
LT
PL
DE/LU or German TSOs if encountered
```

If ENTSO-E exposes only external borders and not internal Swedish bidding-zone borders, P0052A must explicitly state that.

## Priority borders

Primary internal borders:

```text
SE1-SE2
SE2-SE3
SE3-SE4
```

For each primary border and direction, attempt:

```text
capacity_se1_to_se2_mw
capacity_se2_to_se1_mw
scheduled_exchange_se1_to_se2_mw or physical_flow_se1_to_se2_mw

capacity_se2_to_se3_mw
capacity_se3_to_se2_mw
scheduled_exchange_se2_to_se3_mw or physical_flow_se2_to_se3_mw

capacity_se3_to_se4_mw
capacity_se4_to_se3_mw
scheduled_exchange_se3_to_se4_mw or physical_flow_se3_to_se4_mw
```

Secondary Swedish external borders for coverage discovery only:

```text
SE1-FI / SE1-NO4 if available
SE2-NO3 / SE2-NO4 if available
SE3-NO1 / SE3-DK1 / SE3-FI if available
SE4-DK2 / SE4-DE / SE4-PL / SE4-LT if available
```

Again: flows/capacity/exchange only, no price levels.

## Historical period

Requested period should align with P0051:

```text
2022-05-29T23:00:00Z .. 2026-05-25T22:00:00Z
```

However ENTSO-E API may require smaller date chunks. P0052A should chunk safely and idempotently.

Required evidence:

```text
requested_range
attempted_range_by_document_type
successful_range_by_border_measure
failed_range_reason
```

If full period is too slow or rate-limited, P0052A may first ingest:

```text
- 2025 full year
- P0052 recent overlap period
- representative pre/post flow-based market coupling windows
```

but must document what remains incomplete.

## Time model

Use existing fixed-CET convention:

```text
timestamp_utc = primary identity
model_cet_timestamp = timestamp_utc + 1h all year
model_cet_date
model_cet_hour
```

ENTSO-E period timestamps must be normalized to UTC before insertion.

Handle:

```text
- hourly and quarter-hour periods
- period intervals with resolution PT15M/PT60M
- DST effects through UTC normalization
- duplicate time series points
- missing intervals
```

Aggregation:

```text
MW-like values: hourly mean if source resolution is sub-hourly.
MWh-like values: document unit-specific aggregation, normally sum.
```

## Database storage

Extend or reuse P0052 tables:

```text
transfer_capacity_flow_raw_v1
transfer_capacity_flow_hourly_v1
transfer_capacity_flow_se1_se4_hourly_v1
```

Required source labels:

```text
source_name = ENTSO-E Transparency Platform
source_dataset = exact document/process/business type label
```

Required long-format fields:

```text
timestamp_utc
model_cet_timestamp
model_cet_date
model_cet_hour
source_name
source_dataset
from_area
to_area
border_id
measure
value
unit
capacity_method_label
flow_type_label
ingested_at_utc
quality_flag
```

Natural key must include:

```text
timestamp_utc + source_name + source_dataset + from_area + to_area + measure + capacity_method_label + flow_type_label
```

P0052A must not overwrite SvK/Statnett rows unless the source identity makes the upsert unambiguous.

## Capacity concept labels

P0052A must not mix capacity concepts silently.

Allowed labels include:

```text
offered_capacity_mw
allocated_capacity_mw
ntc_mw
cross_border_capacity_mw
available_transfer_capacity_mw
scheduled_exchange_mw
physical_flow_mw
unknown_capacity_concept_STOP
```

If ENTSO-E returns data but the meaning is ambiguous, store it only if clearly labeled as exploratory raw evidence; do not use it for utilization or bottleneck margin.

## Derived features

Only create utilization and bottleneck margin when both flow/exchange and compatible directional capacity exist.

Candidate derived features:

```text
utilization_se1_se2_north_to_south
utilization_se2_se3_north_to_south
utilization_se3_se4_north_to_south

capacity_se1_to_se2_mw
capacity_se2_to_se3_mw
capacity_se3_to_se4_mw
north_to_south_capacity_min

flow_or_exchange_se1_to_se2_mw
flow_or_exchange_se2_to_se3_mw
flow_or_exchange_se3_to_se4_mw
north_to_south_flow_min_or_chain_proxy

north_to_south_bottleneck_margin
flow_based_market_coupling_flag
capacity_method_label
```

`north_to_south_bottleneck_margin` must be defined explicitly. Example:

```text
min(direction_capacity_north_to_south - max(0, direction_flow_or_exchange_north_to_south)) across internal north-south borders
```

If capacity is missing, keep these features null and document why.

## Flow-based era handling

P0052A must revisit the Nordic flow-based transition.

Required:

```text
flow_based_go_live_date = 2024-10-29 unless evidence says otherwise
flow_based_market_coupling_flag
capacity_method_label before/after go-live
```

P0052A must test whether ENTSO-E data uses comparable capacity concepts before and after 2024-10-29.

If concepts differ, diagnostics must be split pre/post go-live.

## Validation

Required validation:

```text
- secret not leaked in git diff, logs or evidence
- source fetcher works with token and masks token in errors
- timestamp normalization to UTC is deterministic
- fixed-CET fields are derived correctly
- no duplicate canonical rows after ingestion
- values are numeric and finite
- units are documented
- direction conventions are documented
- missing hours are reported per border/measure
- internal Swedish border mapping is correct where available
- capacity values are non-negative unless source semantics explicitly differ
- utilization handles zero/null capacity safely
- joins to P0051/P0052 timestamps work
- no continental price levels are ingested
```

## Diagnostics

If usable capacity/exchange is available, update diagnostics against SE3 price and SE3-SE1:

```text
SE3 price vs north_to_south_bottleneck_margin
SE3-SE1 vs north_to_south_bottleneck_margin
SE3-SE1 vs utilization_se2_se3_north_to_south
SE3-SE1 vs utilization_se3_se4_north_to_south
SE3-SE1 by utilization bucket
SE3-SE1 by capacity regime before/after flow-based go-live
SE3-SE1 spike events vs bottleneck margin
```

If internal Swedish capacity is not available, diagnostics should instead explain the blocker and optionally report external flow/capacity coverage counts without using them as SE3-SE1 drivers.

## Forecast-safety classification

Classify every ENTSO-E-derived signal:

```text
historical_observed_only
forecast_time_known_near_term
forecastable_from_grid/outage/capacity_publication
requires_separate_forecast_model
not_forecast_safe
```

Actual flow/exchange is historical observed only. Capacity may be forecast-time-known only if the source publication timing supports it; otherwise label conservatively.

## Required evidence files

P0052A must create:

```text
requirements/package-runs/P0052A/CHANGELOG.md
requirements/package-runs/P0052A/review.md
requirements/package-runs/P0052A/design.md
requirements/package-runs/P0052A/functions.md
requirements/package-runs/P0052A/secret-handling.md
requirements/package-runs/P0052A/entsoe-source-discovery.md
requirements/package-runs/P0052A/entsoe-source-contracts.md
requirements/package-runs/P0052A/eic-domain-mapping.md
requirements/package-runs/P0052A/database-contract.md
requirements/package-runs/P0052A/ingestion-summary.md
requirements/package-runs/P0052A/time-normalization-and-dst.md
requirements/package-runs/P0052A/data-validation.md
requirements/package-runs/P0052A/coverage-and-missingness.md
requirements/package-runs/P0052A/direction-conventions.md
requirements/package-runs/P0052A/flow-based-era-review.md
requirements/package-runs/P0052A/derived-feature-definitions.md
requirements/package-runs/P0052A/capacity-utilization-and-margin-diagnostics.md
requirements/package-runs/P0052A/forecast-safety-classification.md
requirements/package-runs/P0052A/next-package-recommendation.md
requirements/package-runs/P0052A/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0052A/source-contracts.json
requirements/package-runs/P0052A/eic-domain-mapping.json
requirements/package-runs/P0052A/coverage-summary.json
requirements/package-runs/P0052A/validation-summary.json
requirements/package-runs/P0052A/diagnostics-summary.json
requirements/package-runs/P0052A/modeling-dataset-sample.csv
```

Do not commit raw large API dumps. Do not commit secrets.

## Required answers

P0052A must explicitly answer:

```text
1. How was the local ENTSO-E token read safely?
2. Is the secret directory/file ignored by git?
3. Which ENTSO-E document/process/business types were tried?
4. Which EIC/domain codes were used for SE1-SE4 and relevant neighbours?
5. Does ENTSO-E provide internal Swedish bidding-zone capacity for SE1-SE2, SE2-SE3 and SE3-SE4?
6. Does ENTSO-E provide internal Swedish scheduled exchange or physical flow for those borders?
7. If not, what exact API responses or absence proves the blocker?
8. What exact historical range was ingested, if any?
9. What tables/views were updated?
10. What capacity/exchange/flow concepts were stored?
11. Are pre/post 2024-10-29 capacity concepts comparable?
12. Could utilization and bottleneck margin be computed safely?
13. Do the new signals improve initial diagnostics against SE3 price or SE3-SE1?
14. Which signals are forecast-safe and which require separate forecasts?
15. Should the next package continue capacity-source work, proceed with P0051-only physical-balance regime modeling, or use external flows only as parked design input?
16. Confirm no token leak, no continental price levels, no SE1-to-SE3 anchoring, no API, no production model and no device actions.
```

## Tests

Required automated tests:

```text
- token loader returns a token without printing it
- secret path is excluded from git status or explicitly gitignored
- token is masked in request/error logging
- ENTSO-E request builder does not serialize token into evidence
- EIC/domain mapping tests cover SE1-SE4
- timestamp normalization to UTC is deterministic
- fixed-CET fields are derived correctly
- parser handles at least one successful or mocked ENTSO-E response
- idempotent ingestion does not duplicate rows
- canonical uniqueness key is enforced or tested
- utilization formula handles null/zero capacity safely
- no continental price-level document types are requested/ingested
- no SE1 shape is anchored to SE3
- no production forecast API is created
- no deployable model artifact is created
- no M5/M6/M7/API/device path is touched
```

## Pass/fail interpretation

PASS requires:

```text
- token is handled safely and not leaked
- ENTSO-E contracts/domains/document types are tested and documented
- either useful internal Swedish capacity/exchange data is ingested, or a precise ENTSO-E blocker is documented
- validation and coverage evidence are present
- next architecture recommendation is explicit
- forbidden continental-price/API/device/model work is not done
```

WARN is acceptable if:

```text
- ENTSO-E only provides external borders but not internal SE1-SE4 borders
- scheduled exchange exists but capacity does not
- capacity exists only for partial periods or concept changes after flow-based go-live
- rate limits prevent full history but representative windows are tested
```

STOP if:

```text
- token may have leaked
- secret directory is committable
- timestamp or direction semantics are ambiguous and cannot be normalized safely
- data cannot be mapped to SE1-SE4 / Swedish borders
- Codex ingests external price levels
- Codex creates production/API/device work
```

## Expected Codex output

- PASS/WARN/STOP status
- token safety summary without token value
- ENTSO-E source discovery summary
- EIC/domain mapping summary
- selected document types and reason
- database tables/views created or updated
- historical range and row counts
- validation/missingness summary
- capacity/utilization/bottleneck margin result
- diagnostics summary
- forecast-safety classification
- recommendation for next package
- tests run
- files changed
- no token leak / no continental price levels / no API / no device confirmation
- commit SHA after push

## Completion notes

P0052A completed as `WARN` on 2026-06-03.

Result:

```text
requested_range = 2026-05-01T00:00:00Z .. 2026-05-25T22:00:00Z
raw_rows = 20334
hourly_rows = 7795
wide_rows_updated = 599
validation_ok = true
```

WARN reasons:

```text
- Ingestion intentionally used the bounded P0052 recent overlap period, not the full P0051 historical range.
- Initial SE3/SE3-SE1 diagnostics had zero joined rows in the local price diagnostic table for the amended range.
- Forecast use remains conservative: actual exchange/flow is historical-observed-only; capacity publication timing still needs a separate forecast-safety package before production modeling.
```

Required answers:

```text
1. Token was read from a local user secret file outside the repository, or from ENTSOE_SECURITY_TOKEN if set. The token value was not printed or written to evidence.
2. The token file is outside the repository, so it is not committable; directory mode was 0700 and token file mode was 0600.
3. ENTSO-E A09, A11 and A61 were used. Discovery also found A26/A31 invalid or not allowed for tested parameters; A61 required contract_MarketAgreement.Type and A02/A03/A04 returned internal Swedish data.
4. EIC/domain codes for SE1-SE4 and relevant neighbours were documented in `requirements/package-runs/P0052A/eic-domain-mapping.md` and `.json`.
5. ENTSO-E returned internal Swedish A61 capacity for SE1-SE2, SE2-SE3 and SE3-SE4 in both directions for the tested period.
6. ENTSO-E returned internal Swedish A09 scheduled exchange and A11 physical flow for those borders.
7. No internal-border blocker remains for the tested period; remaining blocker is historical-period completeness and conservative forecast-safety classification.
8. Ingested range was 2026-05-01T00:00:00Z .. 2026-05-25T22:00:00Z.
9. Existing P0052 tables were amended: transfer_capacity_flow_raw_v1, transfer_capacity_flow_hourly_v1 and transfer_capacity_flow_se1_se4_hourly_v1.
10. Stored concepts: scheduled_exchange_mw, physical_flow_mw and capacity_mw with explicit A61 A02/A03/A04 capacity labels; A02 capacity was used for compatible wide capacity fields.
11. Pre/post 2024-10-29 comparability was not proven across full history because this package only ingested the recent post-flow-based overlap.
12. Utilization can be computed safely only when compatible A02 capacity and flow-or-exchange exist; null/zero capacity is handled as null.
13. Initial diagnostics did not improve SE3/SE3-SE1 evidence because joined diagnostic rows were zero for the amended range.
14. Actual flow/exchange is historical_observed_only; capacity is conservatively not production forecast-safe until publication timing and forecast availability are verified.
15. Next package should extend P0052A chunked historical backfill and publication-timing validation before using capacity in any forecast model.
16. Confirmed: no token leak found, no continental price levels ingested, no SE1-to-SE3 anchoring, no API, no production model and no device actions.
```

Live/debug attempts:

```text
attempt_1 = failed on ENTSO-E capacity resolution P1M
attempt_2 = passed after period-bound P1M handling and requested-range filtering
```

Automated tests:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0052a
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0048 tests.mac.services.spotprice_model_diagnostics.test_p0049 tests.mac.services.spotprice_model_diagnostics.test_p0050 tests.mac.services.spotprice_model_diagnostics.test_p0051 tests.mac.services.spotprice_model_diagnostics.test_p0052 tests.mac.services.spotprice_model_diagnostics.test_p0052a
```

Evidence:

```text
requirements/package-runs/P0052A/
docs/functions/mac/spotprice-model-diagnostics.md
memory/knowhow/spotprice.md
```
