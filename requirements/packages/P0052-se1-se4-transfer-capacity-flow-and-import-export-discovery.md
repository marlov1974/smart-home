# Package P0052: SE1-SE4 transfer capacity, flow and import/export discovery

## Status

verified

## Package order

P0052

## Primary area

G2 / Mac tooling / spotprice V2 / physical market signals / SE1-SE4 transfer capacity / flow / import-export / bottleneck regime features

## Decision summary

P0052 follows P0051 and investigates whether historical transfer capacity, actual flows and import/export balances can be retrieved and stored for Swedish bidding zones SE1, SE2, SE3 and SE4.

P0051 added production and consumption by bidding zone. P0052 adds the missing grid/market-exchange layer:

```text
production/consumption/net load per zone
+ transfer capacity and actual flows between zones/neighbours
+ import/export per zone
→ bottleneck pressure / capacity utilization / physical balance regime
→ later SE3 price or SE3-SE1 modeling
```

Important framing:

```text
Import/export is not merely metadata.
For each price area, import behaves like extra production/supply and export behaves like extra consumption/demand.
```

Therefore P0052 must try to build both border-level and zone-level import/export features.

P0052 is a data discovery, contract, ingestion and validation package. It must not build a SE3 model yet.

## Preconditions

P0052 may start only after P0051 PASS evidence exists.

Required P0051 facts:

```text
- eSett Open Data ingestion exists for SE1-SE4 production and consumption.
- physical_balance_hourly_raw_v1, physical_balance_hourly_v1 and physical_balance_se1_se4_hourly_v1 exist.
- P0051 final overlap range is 2022-05-29T23:00:00+00:00 .. 2026-05-25T22:00:00+00:00.
- P0051 derived net_load = consumption - production.
- Continental price pressure is parked in requirements/design-backlog/continental-price-pressure-for-se3-se4.md and must not be started here.
```

P0052 must STOP before ingestion if no reliable transfer-capacity/flow/import-export source can be identified.

## Scope

P0052 owns:

```text
1. Discover historical transfer capacity and actual flow data sources for Swedish bidding-zone borders.
2. Discover import/export data per bidding zone SE1-SE4 if available directly.
3. Ingest available data for the same overlap period as P0051 where possible.
4. Normalize timestamps to UTC and derive fixed-CET fields.
5. Store border-level capacity/flow and zone-level import/export features in the same local database.
6. Validate row counts, direction conventions, units, duplicates, missing hours and DST handling.
7. Create derived capacity utilization, import/export and bottleneck-margin features.
8. Produce initial diagnostics against SE3 price and SE3-SE1.
```

## Hard non-goals

P0052 must not:

```text
- build a SE3 forecast model
- build a SE3-SE1 bottleneck model
- build production API
- anchor SE1 to SE3
- ingest continental price levels or external price-pressure features
- train direct SE3 AI-1/AI-2
- touch Shelly/Home Assistant/KVS/devices
- build M5/M6/M7
- ingest futures/forward curves
```

Clarification:

```text
Cross-border flow/capacity to neighbouring areas may be discovered if needed to compute SE1-SE4 import/export.
But external price levels such as DE/DK/PL/Baltic prices are parked and must not be ingested in P0052.
```

## Candidate data sources

Codex must investigate at least:

```text
ENTSO-E Transparency Platform
Svenska kraftnät open data/API/statistics/control-room sources
Nordic flow-based capacity data sources, if machine-readable and accessible
```

Optional if discovered during source review:

```text
eSett Open Data import/export or exchange endpoints
Nord Pool flow/capacity data if available without forbidden access/secrets
```

Discovery must document:

```text
source_name
base_url
endpoint_or_download_path
authentication requirement
query parameters
available bidding zones/borders
available measures
historical start date
latest available date
update latency
resolution
units
time zone / timestamp convention
direction convention
license/usage notes if visible
rate limits if visible
example request
example response shape
```

If a source requires an API key not available in the repo environment, document the exact blocker and do not fake ingestion.

## Required border coverage

P0052 must prioritize Swedish internal bidding-zone borders:

```text
SE1-SE2
SE2-SE3
SE3-SE4
```

For each border, attempt to retrieve:

```text
capacity direction A->B
capacity direction B->A
actual flow direction A->B / signed flow
scheduled commercial exchange if physical flow is unavailable
```

Preferred canonical internal border columns:

```text
capacity_se1_to_se2_mw
capacity_se2_to_se1_mw
flow_se1_to_se2_mw
flow_se2_to_se1_mw or signed_flow_se1_to_se2_mw

capacity_se2_to_se3_mw
capacity_se3_to_se2_mw
flow_se2_to_se3_mw
flow_se3_to_se2_mw or signed_flow_se2_to_se3_mw

capacity_se3_to_se4_mw
capacity_se4_to_se3_mw
flow_se3_to_se4_mw
flow_se4_to_se3_mw or signed_flow_se3_to_se4_mw
```

P0052 must document whether the data represents:

```text
- physical flow
- scheduled commercial exchange
- NTC/offered capacity
- allocated capacity
- flow-based capacity-domain output
- another capacity concept
```

Do not mix concepts silently.

## Required zone import/export coverage

P0052 must attempt to produce zone-level import/export for each Swedish bidding zone:

```text
import_se1_mw
export_se1_mw
net_import_se1_mw

import_se2_mw
export_se2_mw
net_import_se2_mw

import_se3_mw
export_se3_mw
net_import_se3_mw

import_se4_mw
export_se4_mw
net_import_se4_mw
```

Definition:

```text
import_z = sum of positive inbound flows to zone z
export_z = sum of positive outbound flows from zone z
net_import_z = import_z - export_z
```

Interpretation:

```text
net_import_z > 0 means the zone is supplied by imports.
net_import_z < 0 means the zone is net exporter.
```

These zone import/export features should include both internal Swedish borders and external cross-border flows if available and needed for complete zone balance.

External neighbour border candidates may include:

```text
SE1-FI / SE1-NO4 if applicable
SE2-NO3 / SE2-NO4 if applicable
SE3-NO1 / SE3-DK1 / SE3-FI if applicable
SE4-DK2 / SE4-DE / SE4-PL / SE4-LT if applicable
```

Do not ingest neighbour price levels in P0052.

## Balance consistency check

P0052 must compare import/export against P0051 production/consumption.

For each zone:

```text
balance_residual_z = production_z + import_z - consumption_z - export_z
```

This should be close to zero only if:

```text
- production/consumption definitions are compatible
- import/export includes all relevant borders
- flow data uses matching physical/scheduled concepts
```

If it is not close to zero, P0052 must document why and whether the mismatch is expected.

Do not force-close the balance by inventing residual production or consumption.

## Flow-based market coupling era

P0052 must account for the Nordic flow-based market-coupling transition.

Required fields:

```text
flow_based_market_coupling_flag
flow_based_go_live_date
capacity_method_label
```

Known reference date to verify/document:

```text
2024-10-29 Nordic flow-based market coupling go-live
```

P0052 must investigate whether capacity data changes concept before/after this date.

If post-flow-based data no longer maps cleanly to border NTC values, P0052 must store method labels and avoid pretending all capacity values are the same concept.

## Historical period

P0052 must align with P0051:

```text
preferred start: 2022-05-29T23:00:00+00:00
preferred end:   2026-05-25T22:00:00+00:00
```

If a source has shorter coverage, ingest the maximum reliable overlap and document:

```text
requested_range
source_available_range
final_ingested_range
missing_range_reason
```

## Time model

Use existing P0042 fixed-CET convention:

```text
timestamp_utc = primary identity
model_cet_timestamp = timestamp_utc + 1h all year
model_cet_date
model_cet_hour
```

Source timestamps must be normalized to UTC before insertion.

P0052 must explicitly handle:

```text
- DST 23/25-hour source days
- duplicate source rows
- missing hours
- ambiguous local timestamps
- quarter-hour vs hourly source resolution
```

If source resolution is quarter-hour, aggregate to hourly and document aggregation method:

```text
mean MW for power/flow/capacity values
sum MWh only if source values are energy volumes and units demand it
```

## Database storage contract

Create/update source tables using repository database conventions.

Preferred logical raw/canonical tables:

```text
transfer_capacity_flow_raw_v1
transfer_capacity_flow_hourly_v1
```

Minimum canonical long-format columns:

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
source_updated_at_utc if available
quality_flag
```

Allowed measure examples:

```text
capacity_mw
flow_mw
scheduled_exchange_mw
allocated_capacity_mw
```

Preferred wide modeling view:

```text
transfer_capacity_flow_se1_se4_hourly_v1
```

with columns for:

```text
internal border capacities/flows
zone import/export/net_import for SE1-SE4
capacity utilization features
bottleneck margin features
flow-based era fields
```

## Derived features

Required derived features where inputs exist:

```text
utilization_se1_se2_north_to_south
utilization_se2_se3_north_to_south
utilization_se3_se4_north_to_south

north_to_south_capacity_min
north_to_south_flow_min_or_chain_proxy
north_to_south_bottleneck_margin

import_se1_mw
export_se1_mw
net_import_se1_mw
import_se2_mw
export_se2_mw
net_import_se2_mw
import_se3_mw
export_se3_mw
net_import_se3_mw
import_se4_mw
export_se4_mw
net_import_se4_mw

balance_residual_se1
balance_residual_se2
balance_residual_se3
balance_residual_se4

se3_import_pressure
se4_import_pressure
south_import_pressure = net_import_se3_mw + net_import_se4_mw
north_export_pressure = -(net_import_se1_mw + net_import_se2_mw)
```

`utilization` must be defined carefully depending on direction and available capacity concept.

Example for directional north-to-south capacity:

```text
utilization = max(0, flow_north_to_south) / capacity_north_to_south
```

Clip or null invalid values; do not hide data errors.

## Idempotent ingestion

Ingestion must be idempotent.

Required behavior:

```text
- repeated runs do not duplicate rows
- source rows are upserted or replaced deterministically by natural key
- natural key includes timestamp_utc + source_name + from_area + to_area + measure + capacity_method_label/flow_type_label where relevant
- partial failed fetches do not leave inconsistent committed data unless marked quality_flag
```

## Data validation

Required validation:

```text
- timestamp_utc is not null
- value is numeric and finite
- unit is documented
- direction convention is documented
- no duplicate canonical rows after normalization
- expected hourly row counts per border/measure over final overlap range
- missing hours summary per border/measure
- negative values reviewed and interpreted according to direction convention
- capacity values are non-negative unless source semantics explicitly allow signed capacity
- utilization values are finite or null with documented reason
- fixed-CET derived fields are present
- joins to P0051 physical_balance_se1_se4_hourly_v1 succeed
- balance residual checks are reported
```

## Initial diagnostics

P0052 must produce non-model diagnostics against SE3 price and SE3-SE1.

Required diagnostics:

```text
SE3 price vs net_import_se3_mw
SE3 price vs south_import_pressure
SE3 price vs north_to_south_bottleneck_margin
SE3-SE1 vs net_import_se3_mw
SE3-SE1 vs south_import_pressure
SE3-SE1 vs north_to_south_bottleneck_margin
SE3-SE1 vs utilization_se2_se3_north_to_south
SE3-SE1 vs utilization_se3_se4_north_to_south
SE3-SE1 by utilization bucket
SE3-SE1 by capacity regime before/after flow-based go-live
SE3 top4/top8 day events vs import/export/net_import
SE3-SE1 spike events vs utilization/import/export
```

These diagnostics are explanatory only and must not become a production forecast.

## Forecast-safety classification

P0052 must classify every new signal as one of:

```text
historical_observed_only
forecast_time_known_near_term
forecastable_from_grid/outage/capacity_publication
requires_separate_forecast_model
not_forecast_safe
```

Actual flows and realized import/export are historical observed values. For future 7-day use they require forecasts or forecast-safe capacity/availability assumptions.

Capacity may be forecast-time-known for near-term if published before market clearing or operationally available; Codex must document this rather than assume.

## Required evidence files

P0052 must create:

```text
requirements/package-runs/P0052/CHANGELOG.md
requirements/package-runs/P0052/review.md
requirements/package-runs/P0052/design.md
requirements/package-runs/P0052/functions.md
requirements/package-runs/P0052/source-discovery.md
requirements/package-runs/P0052/source-contracts.md
requirements/package-runs/P0052/database-contract.md
requirements/package-runs/P0052/ingestion-summary.md
requirements/package-runs/P0052/time-normalization-and-dst.md
requirements/package-runs/P0052/data-validation.md
requirements/package-runs/P0052/coverage-and-missingness.md
requirements/package-runs/P0052/direction-conventions.md
requirements/package-runs/P0052/flow-based-era-review.md
requirements/package-runs/P0052/derived-feature-definitions.md
requirements/package-runs/P0052/import-export-balance-check.md
requirements/package-runs/P0052/initial-capacity-flow-diagnostics.md
requirements/package-runs/P0052/forecast-safety-classification.md
requirements/package-runs/P0052/next-package-recommendation.md
requirements/package-runs/P0052/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0052/source-contracts.json
requirements/package-runs/P0052/coverage-summary.json
requirements/package-runs/P0052/validation-summary.json
requirements/package-runs/P0052/diagnostics-summary.json
requirements/package-runs/P0052/modeling-dataset-sample.csv
```

Do not commit large raw data dumps.

## Required answers

P0052 must explicitly answer:

```text
1. Which data sources were investigated?
2. Which source was selected and why?
3. Were SE1-SE2, SE2-SE3 and SE3-SE4 capacity values available historically?
4. Were internal border flows or scheduled exchanges available historically?
5. Could zone-level import/export be computed for SE1-SE4?
6. Did import/export include external neighbour borders or only internal Swedish borders?
7. What exact historical range was ingested?
8. What database tables/views were created or updated?
9. What units and direction conventions were used?
10. How many rows were ingested per source/border/measure?
11. What missingness, duplicates or quality issues exist?
12. How did capacity concepts change before/after Nordic flow-based market coupling?
13. What derived features were created?
14. Do capacity/utilization/import/export signals show useful initial relationship to SE3 price or SE3-SE1?
15. Are import/export features strong enough to join P0051 production/consumption for P0053 physical-regime modeling?
16. Which signals are forecast-safe and which require separate forecasts?
17. Confirm no continental price pressure levels, no SE1-to-SE3 anchoring, no API, no production model and no device actions.
```

## Tests

Required automated tests:

```text
- source contract parser/fetcher handles example response
- timestamp normalization to UTC is deterministic
- fixed-CET fields are derived correctly
- idempotent ingestion does not duplicate rows
- canonical uniqueness key is enforced or tested
- Swedish bidding-zone border mapping is correct
- import/export aggregation from directed flows is correct
- net_import = import - export
- balance_residual = production + import - consumption - export
- utilization formula is reproducible and handles zero/null capacity safely
- flow-based era flag is deterministic
- missing-hour report covers each border/measure
- joins to P0051 physical balance timestamps work
- no continental price levels are ingested
- no SE1 shape is anchored to SE3
- no production forecast API is created
- no deployable model artifact is created
- no M5/M6/M7/API/device path is touched
```

## Pass/fail interpretation

PASS requires:

```text
- at least one reliable source for capacity/flow/import-export is identified
- data is ingested or a precise source/API-key blocker is documented if ingestion is impossible
- database contract and time normalization are documented
- validation and coverage evidence are present
- zone import/export features are created if sufficient flow data exists
- next architecture recommendation is explicit
- forbidden continental/API/device/model work is not done
```

WARN is acceptable if:

```text
- only flow but not capacity is available
- only scheduled exchange but not physical flow is available
- only internal Swedish borders are available
- post-flow-based capacity concepts are not directly comparable to pre-flow-based NTC
- source coverage is partial but documented
```

STOP if:

```text
- no reliable source can be identified and no safe ingestion contract can be created
- timestamp or direction semantics are ambiguous and cannot be normalized safely
- data cannot be mapped to SE1-SE4 / Swedish borders
- Codex accidentally ingests external price levels
- Codex creates production/API/device work
```

## Expected Codex output

- PASS/WARN/STOP status
- source discovery summary
- selected source and reason
- database tables/views created or updated
- historical range and row counts
- direction convention summary
- validation/missingness summary
- import/export balance-check summary
- derived features summary
- initial relationship diagnostics
- forecast-safety classification
- recommendation for P0053
- tests run
- files changed
- no continental price levels / no API / no device confirmation
- commit SHA after push

## Completion notes

Implemented and verified with result status `WARN`.

Selected source:

```text
Svenska kraftnat Kontrollrummet / Statnett
```

Selected reason:

```text
Auth-free machine-readable flow-map endpoint exposes Swedish internal border flows and SE1-SE4 import/export values.
```

Tables created/rebuilt:

```text
transfer_capacity_flow_raw_v1
transfer_capacity_flow_hourly_v1
transfer_capacity_flow_se1_se4_hourly_v1
```

Historical range ingested:

```text
2026-05-01T00:00:00Z .. 2026-05-25T22:00:00Z
```

Row counts:

```text
raw quarter-hour rows: 95840
canonical hourly rows: 24542
wide hourly rows: 599
```

Validation summary:

```text
duplicates: 0
nonfinite values: 0
negative capacity values: 0
wide rows joined to P0051: 599 / 599
missing signed_flow/import/export/net_import hours: 0
```

Capacity result:

```text
No historical capacity values were available from the selected auth-free SvK/Statnett source.
ENTSO-E Transparency Platform remains the likely capacity source but requires a security token; unauthenticated request returned HTTP 401.
No capacity values were invented.
```

Diagnostics summary:

```text
joined rows: 599
SE3 price vs net_import_se3_mw: 0.6765189198733116
SE3 price vs south_import_pressure: 0.7396667513331376
SE3-SE1 vs net_import_se3_mw: 0.25066644313977
SE3-SE1 vs south_import_pressure: 0.2660402951401065
capacity/utilization diagnostics: null because capacity is unavailable
```

Forecast safety:

```text
flows and realized import/export: historical_observed_only
net import and pressure features: require separate forecast model before forecast use
capacity: not forecast-safe until a source is available
```

Recommendation:

```text
P0053 may use P0051 physical balance plus P0052 observed flow/import-export for historical physical-regime diagnostics.
P0053 must not treat these features as forecast-safe without separate forecasts or forecast-time-known inputs.
Capacity should be handled by a separate ENTSO-E/token-backed package or another reliable capacity source.
```

Forbidden work confirmation:

```text
No continental price levels, no SE1-to-SE3 anchoring, no production API, no production model, no deployable model artifact, no M5/M6/M7, no Shelly, no Home Assistant, no KVS and no device actions.
```
