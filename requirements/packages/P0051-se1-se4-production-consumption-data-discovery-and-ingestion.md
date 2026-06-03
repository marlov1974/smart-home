# Package P0051: SE1-SE4 production/consumption data discovery and ingestion

## Status

verified

## Package order

P0051

## Primary area

G2 / Mac tooling / spotprice V2 / physical market signals / SE1-SE4 production and consumption / eSett and SvK discovery / database ingestion

## Decision summary

P0051 investigates and, if feasible, ingests hourly production and consumption data for Swedish bidding zones SE1, SE2, SE3 and SE4.

Candidate data sources:

```text
eSett Open Data
Svenska kraftnät open data/API
```

The goal is to add physical balance signals covering the same historical period as the existing price/weather/modeling dataset.

These signals are expected to become a more physical intermediate layer for future SE3/SE3-SE1 modeling:

```text
weather + daytype + response effects
→ production/consumption forecasts per bidding zone
→ net load / north-south balance / bottleneck risk
→ SE3 price or SE1 + SE3-SE1
```

P0051 must not build a SE3 price model yet. It is a data discovery, contract, ingestion and validation package.

## Preconditions

P0051 follows P0050.

Relevant current facts:

```text
- P0047-P0050 showed SE3-SE1 is not just a simple price-shape residual.
- Lagged spread and local SE3 top-N price-rank features matter.
- Heat-pump and demand-response proxies are incomplete without direct consumption/production signals.
- Continental price pressure is parked in requirements/design-backlog/continental-price-pressure-for-se3-se4.md and must not be started in P0051.
```

P0051 must STOP before ingestion if no reliable production/consumption source can be identified.

## Scope

P0051 owns:

```text
1. Discover whether eSett and/or Svenska kraftnät provide hourly production and consumption data by bidding zone SE1-SE4.
2. Document endpoint/API/file contracts, parameters, units, time zones, latency and historical coverage.
3. Select a preferred source or source-combination.
4. Build an ingestion path into the same local database used by current spotprice/weather/modeling data.
5. Store data for the same historical period as existing SE1/SE3 price and weather data where available.
6. Validate row counts, timestamps, units, duplicates, missing hours and DST/fixed-CET handling.
7. Create derived physical balance features.
8. Produce initial correlation/event diagnostics against SE3 price and SE3-SE1, without training a deployable model.
```

## Hard non-goals

P0051 must not:

```text
- build a SE3 forecast model
- build a SE3-SE1 bottleneck model
- build production API
- anchor SE1 to SE3
- use continental/DE/DK/PL/Baltic price pressure; that is parked for later
- touch Shelly/Home Assistant/KVS/devices
- build M5/M6/M7
- ingest futures/forward curves
```

Small diagnostics/correlation scripts are allowed. No deployable model artifact may be created.

## Data source discovery

Codex must investigate at least:

```text
eSett Open Data API/root:
  https://api.opendata.esett.com

Svenska kraftnät public data/API sources available in repo environment or web access
```

Discovery must document:

```text
source_name
base_url
endpoint_or_download_path
authentication requirement
query parameters
available bidding zones / market areas
available measures
historical start date
latest available date
update latency
resolution
units
time zone / timestamp convention
license/usage notes if visible
rate limits if visible
example request
example response shape
```

If online access is unavailable in Codex environment, Codex must document the failure mode and may still create source adapters behind feature flags only if contracts are known from local docs. Do not guess silently.

## Required measures

P0051 should try to obtain, at minimum, hourly values for:

```text
consumption_SE1
consumption_SE2
consumption_SE3
consumption_SE4
production_SE1
production_SE2
production_SE3
production_SE4
```

If data is split by production type, keep both:

```text
production_total
production_by_type where available
```

Useful production types if available:

```text
wind
solar
hydro
nuclear
thermal
other
```

If only all-Sweden totals are available from one source, that source is insufficient for the primary goal unless another source provides bidding-zone split.

## Historical period

P0051 must align with the current modeling data coverage.

Required behavior:

```text
1. Inspect existing local database tables/views to find the available price/weather/modeling timestamp range.
2. Ingest production/consumption for the overlapping period available from source.
3. Prefer all available history if it matches or exceeds the existing price/weather data period.
4. At minimum, cover the P0048/P0049/P0050 period if source limitations prevent full history.
```

P0051 must report exact ranges:

```text
existing_price_range
existing_weather_range
production_consumption_range
final_overlap_range
```

## Time model

Use existing P0042 fixed-CET convention for derived modeling fields:

```text
timestamp_utc = primary identity
model_cet_timestamp = timestamp_utc + 1h all year
model_cet_date
model_cet_hour
```

Source timestamps must be normalized to UTC before insertion.

P0051 must explicitly handle:

```text
- DST 23/25-hour days in source data
- duplicate source rows
- missing hours
- ambiguous local timestamps
- leap/no-leap edge cases if present
```

Do not use Europe/Stockholm civil time as a primary database key.

## Database storage contract

Create or update source tables using repository database conventions.

Preferred logical table/view names:

```text
physical_balance_hourly_raw_v1
physical_balance_hourly_v1
```

Minimum canonical columns:

```text
timestamp_utc
model_cet_timestamp
model_cet_date
model_cet_hour
source_name
source_dataset
bidding_zone
measure
value
unit
ingested_at_utc
source_updated_at_utc if available
quality_flag
```

Where practical, also create a wide modeling view:

```text
physical_balance_se1_se4_hourly_v1
```

with columns:

```text
timestamp_utc
model_cet_timestamp
model_cet_date
model_cet_hour
consumption_se1
consumption_se2
consumption_se3
consumption_se4
production_se1
production_se2
production_se3
production_se4
net_load_se1
net_load_se2
net_load_se3
net_load_se4
production_north = production_se1 + production_se2
production_south = production_se3 + production_se4
consumption_north = consumption_se1 + consumption_se2
consumption_south = consumption_se3 + consumption_se4
net_load_north = net_load_se1 + net_load_se2
net_load_south = net_load_se3 + net_load_se4
net_load_south_minus_north
production_south_minus_north
consumption_south_minus_north
```

`net_load` should be defined and documented. Preferred:

```text
net_load = consumption - production
```

Positive net_load means local demand exceeds local production.

## Idempotent ingestion

Ingestion must be idempotent.

Required behavior:

```text
- repeated runs do not duplicate rows
- source rows are upserted or replaced deterministically by natural key
- natural key includes timestamp_utc + source_name + bidding_zone + measure + production_type if relevant
- partial failed fetches do not leave inconsistent committed data unless marked quality_flag
```

If production type is available, table key must distinguish type-specific rows from production_total.

## Data validation

Required validation:

```text
- timestamp_utc is not null
- value is numeric and finite
- unit is documented
- no duplicate canonical rows after normalization
- expected hourly row counts per zone/measure over final overlap range
- missing hours summary per zone/measure
- negative values reviewed and documented
- production and consumption magnitude sanity checks
- total production_by_type equals production_total if both exist, within tolerance
- fixed-CET derived fields are present
- joins to existing price/weather timestamp range succeed
```

## Derived diagnostics

P0051 must produce initial non-model diagnostics.

Required correlations/event summaries:

```text
SE3 price vs consumption_se3
SE3 price vs production_se3
SE3 price vs net_load_se3
SE3-SE1 vs net_load_se3
SE3-SE1 vs net_load_south_minus_north
SE3-SE1 vs production_south_minus_north
SE3-SE1 vs consumption_south_minus_north
SE3 top4/top8 day events vs consumption_se3 residual/change
SE3 bottom4/bottom8 day events vs consumption_se3 residual/change
cold + high SE3 rank vs consumption_se3 / net_load_se3
```

These diagnostics are explanatory only and must not become a production forecast.

## Forecast-safety classification

P0051 must classify every new signal as one of:

```text
historical_observed_only
forecast_time_known_near_term
forecastable_from_weather_calendar
requires_separate_forecast_model
not_forecast_safe
```

Consumption and production actuals are historical observed values. For future 7-day use they require their own forecasts or proxy/normal models.

## Required evidence files

P0051 must create:

```text
requirements/package-runs/P0051/CHANGELOG.md
requirements/package-runs/P0051/review.md
requirements/package-runs/P0051/design.md
requirements/package-runs/P0051/functions.md
requirements/package-runs/P0051/source-discovery.md
requirements/package-runs/P0051/source-contracts.md
requirements/package-runs/P0051/database-contract.md
requirements/package-runs/P0051/ingestion-summary.md
requirements/package-runs/P0051/time-normalization-and-dst.md
requirements/package-runs/P0051/data-validation.md
requirements/package-runs/P0051/coverage-and-missingness.md
requirements/package-runs/P0051/derived-feature-definitions.md
requirements/package-runs/P0051/initial-physical-signal-diagnostics.md
requirements/package-runs/P0051/forecast-safety-classification.md
requirements/package-runs/P0051/next-package-recommendation.md
requirements/package-runs/P0051/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0051/source-contracts.json
requirements/package-runs/P0051/coverage-summary.json
requirements/package-runs/P0051/validation-summary.json
requirements/package-runs/P0051/diagnostics-summary.json
requirements/package-runs/P0051/modeling-dataset-sample.csv
```

Do not commit large raw data dumps.

## Required answers

P0051 must explicitly answer:

```text
1. Which data sources were investigated?
2. Did eSett provide usable SE1-SE4 hourly production and consumption?
3. Did Svenska kraftnät provide usable SE1-SE4 hourly production and consumption?
4. Which source was selected and why?
5. What exact historical range was ingested?
6. What measures and zones were successfully stored?
7. What units and timestamp conventions were used?
8. What database tables/views were created or updated?
9. How many rows were ingested per source/zone/measure?
10. What missingness, duplicates or quality issues exist?
11. Are production totals split by type available?
12. What derived features were created?
13. Do net_load / production / consumption signals show useful initial relationship to SE3 price or SE3-SE1?
14. Which signals are forecast-safe and which require separate forecasts?
15. Should P0052 build production/consumption forecast models, add these as historical features to SE3 modeling, or do more source work?
16. Confirm no continental price pressure work, no SE1-to-SE3 anchoring, no API, no production model and no device actions.
```

## Tests

Required automated tests:

```text
- source contract parser/fetcher handles example response
- timestamp normalization to UTC is deterministic
- fixed-CET fields are derived correctly
- idempotent ingestion does not duplicate rows
- canonical uniqueness key is enforced or tested
- SE1-SE4 zone mapping is correct
- production/consumption measure mapping is correct
- net_load = consumption - production
- derived north/south aggregates are correct
- missing-hour report covers each zone/measure
- joins to existing price/weather/modeling timestamps work
- no continental price pressure data is ingested
- no SE1 shape is anchored to SE3
- no production forecast API is created
- no deployable model artifact is created
- no M5/M6/M7/API/device path is touched
```

## Pass/fail interpretation

PASS requires:

```text
- at least one reliable source for SE1-SE4 hourly production/consumption is identified
- data is ingested or a precise source-blocker is documented if API access blocks ingestion
- database contract and time normalization are documented
- validation and coverage evidence are present
- derived net-load/north-south features are created if data exists
- next architecture recommendation is explicit
- forbidden continental/API/device/model work is not done
```

WARN is acceptable if:

```text
- only partial history is available
- production exists but consumption is delayed or vice versa
- source has quality/missingness issues but they are documented
- ingestion works for one source but the other source remains unresolved
```

STOP if:

```text
- no reliable source can be identified and no safe ingestion contract can be created
- timestamp semantics are ambiguous and cannot be normalized safely
- data cannot be mapped to SE1-SE4
- Codex accidentally starts continental price pressure work
- Codex creates production/API/device work
```

## Expected Codex output

- PASS/WARN/STOP status
- source discovery summary
- selected source and reason
- database tables/views created or updated
- historical range and row counts
- validation/missingness summary
- derived features summary
- initial relationship diagnostics
- forecast-safety classification
- recommendation for P0052
- tests run
- files changed
- no continental price pressure / no API / no device confirmation
- commit SHA after push

## Completion notes

P0051 PASS.

Selected source:

```text
eSett Open Data
```

Created/rebuilt local SQLite tables:

```text
physical_balance_hourly_raw_v1
physical_balance_hourly_v1
physical_balance_se1_se4_hourly_v1
```

Ingested range:

```text
2022-05-29T23:00:00Z through 2026-05-25T22:00:00Z
```

Row counts:

```text
first live fetch observations = 4450240 quarter-hour source observations
canonical hourly rows = 1350313
wide hourly rows = 34968
```

Validation:

```text
duplicates = 0
nonfinite_values = 0
negative_values_after_normalization = 0
missing required consumption_total/production_total hours = 0 for SE1-SE4
```

Main initial diagnostics:

```text
SE3 price vs net_load_se3 correlation = 0.602094
SE3 price vs net_load_south_minus_north correlation = 0.562751
SE3-SE1 vs net_load_south_minus_north correlation = 0.342777
SE3-SE1 vs production_south_minus_north correlation = -0.360256
SE3 top8 day consumption_se3 lift = 350.553 MW
SE3 bottom8 day consumption_se3 lift = -441.039 MW
```

Recommendation:

```text
P0052 should evaluate physical-balance historical features and decide whether separate production/consumption forecasts are needed before forecast-safe SE3 model use.
```

Confirmed:

```text
No continental price pressure work, no SE1-to-SE3 anchoring, no SE3 API, no production model artifact, no M5/M6/M7, no Shelly, no Home Assistant, no KVS and no device actions.
```
