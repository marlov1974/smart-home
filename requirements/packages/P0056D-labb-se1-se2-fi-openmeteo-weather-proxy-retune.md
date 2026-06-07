# Package P0056D: LABB SE1/SE2/FI Open-Meteo weather proxy retune

## Status

planned

## Package order

P0056D

## Label

```text
LABB
```

## Purpose

Improve the weather proxies for the weakest or strategically important P0056C areas, then rerun consumption forecasts and compare against the latest P0056C baseline.

P0056D must:

```text
1. Define weather zones for SE1, SE2 and FI.
2. Set population/load-based weights for each price-area proxy.
3. Select one or more weather series for every weather zone.
4. Fetch the required historical weather series from Open-Meteo.
5. Build revised area weather proxies for SE1, SE2 and FI.
6. Retrain and retest SE1, SE2 and FI with the same best consumption model as P0056C.
7. Compare new results against P0056C baseline.
```

This package is both weather-proxy data work and a targeted forecast retest for SE1, SE2 and FI only.

## Areas in scope

```text
SE1
SE2
FI
```

Other P0056C areas must not be changed unless needed for shared helper code.

## Baseline to compare against

Use P0056C as the baseline:

```text
requirements/package-runs/P0056C/area-results.md
```

Baseline values to compare:

```text
SE1 DayAhead MAE 126.498 MW, MAE percent mean 10.031%, full36 MAE 124.609 MW
SE2 DayAhead MAE 209.519 MW, MAE percent mean 12.120%, full36 MAE 201.827 MW
FI  DayAhead MAE 332.717 MW, MAE percent mean 3.336%,  full36 MAE 311.189 MW
```

If exact baseline values differ in local evidence, document the exact source and use the latest committed P0056C values.

## Weather-zone design

### SE1 weather zones

Create zones:

```text
SE1_LULEA_PITEA_BODEN
SE1_KIRUNA_GALLIVARE
SE1_SKELLEFTEA
SE1_HAPARANDA
```

Intended representative places:

```text
SE1_LULEA_PITEA_BODEN: Lulea, Pitea, Boden
SE1_KIRUNA_GALLIVARE: Kiruna, Gallivare
SE1_SKELLEFTEA: Skelleftea
SE1_HAPARANDA: Haparanda
```

### SE2 weather zones

Create zones:

```text
SE2_SUNDSVALL_HARNOSAND_ORNSKOLDSVIK
SE2_UMEA
SE2_HUDIKSVALL
SE2_SOLLEFTEA_KRAMFORS
SE2_OSTERSUND_ARE
```

Intended representative places:

```text
SE2_SUNDSVALL_HARNOSAND_ORNSKOLDSVIK: Sundsvall, Harnosand, Ornskoldsvik
SE2_UMEA: Umea
SE2_HUDIKSVALL: Hudiksvall
SE2_SOLLEFTEA_KRAMFORS: Solleftea, Kramfors
SE2_OSTERSUND_ARE: Ostersund, Are
```

### FI weather zones

Create zones:

```text
FI_HELSINKI_ESPOO_VANTAA_RING
FI_TURKU_PORI
FI_TAMPERE_LAHTI_HAMEENLINNA_KOUVOLA
FI_JYVASKYLA_KUOPIO_MIKKELI_JOENSUU
FI_OULU_VAASA
```

Intended representative places:

```text
FI_HELSINKI_ESPOO_VANTAA_RING: Helsinki, Espoo, Vantaa, Kerava, Kirkkonummi and surrounding municipalities
FI_TURKU_PORI: Turku, Pori
FI_TAMPERE_LAHTI_HAMEENLINNA_KOUVOLA: Tampere, Lahti, Hameenlinna, Kouvola
FI_JYVASKYLA_KUOPIO_MIKKELI_JOENSUU: Jyvaskyla, Kuopio, Mikkeli, Joensuu
FI_OULU_VAASA: Oulu, Vaasa
```

## Weighting requirement

P0056D must set weights for every weather zone within each price area.

Weights should represent population share or load share. Use the best available local source.

Allowed weight sources:

```text
local population/municipality metadata if present
local grid/load distribution metadata if present
manual deterministic weights with documented rationale
operator-provided weights if later supplied
```

If exact population data is not available locally, create first-pass deterministic weights from city/municipality population estimates or reasonable load-centre approximations, and label confidence.

Requirements:

```text
weights per area must sum to 1.0
weights must be documented
confidence must be documented: high / medium / low
manual assumptions must be explicit
```

Do not use equal weights unless justified.

## Open-Meteo fetch requirement

Fetch historical hourly weather for every selected representative location from Open-Meteo.

Required time period:

```text
2022-06-01T00:00:00Z onward
through latest complete available overlap with P0056A/P0056C data
```

Use a safe batching strategy:

```text
one location at a time
monthly or yearly chunks if needed
write incrementally
cache locally or store in DB
rerunnable without duplicate rows
```

Do not commit large raw weather dumps.

Document exact Open-Meteo endpoint, parameters and variables used.

## Required weather variables

Minimum:

```text
temperature_2m
```

Preferred:

```text
apparent_temperature
wind_speed_10m
cloud_cover
relative_humidity_2m
precipitation
snow_depth if available
```

Derived features:

```text
heating_degree_proxy
cooling_degree_proxy if used
rolling temperature features required by current model
```

Document units and UTC handling.

## Output tables

Create or populate revised proxy tables that do not overwrite P0056B without clear versioning.

Preferred names:

```text
area_weather_zone_openmeteo_hourly_p0056d_v1
area_weather_proxy_hourly_p0056d_v1
area_weather_features_hourly_p0056d_v1
area_weather_proxy_weights_p0056d_v1
```

Minimum proxy feature columns:

```text
timestamp_utc
area_code
weather_proxy_version = P0056D
feature columns used by model
source_zone_ids
zone_weights
missingness_flags
generated_by_package = P0056D
```

## Forecast retest

Retrain and retest only:

```text
SE1
SE2
FI
```

Use the same model method and split policy as P0056C:

```text
HorizonBiasCorrected_WeightedEnsemble_no_price
train_fit: 2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
internal validation strictly inside train_fit
```

Use P0056A consumption targets and the new P0056D weather features for these areas.

No spot price features. No flow/exchange/capacity features. No future actual load leakage. No holdout fitting.

## Metrics

For SE1, SE2 and FI report:

```text
DayAhead MAE
DayAhead RMSE
DayAhead bias
MAE percent of mean actual
MAE percent of median actual
absolute daily energy error MWh
signed daily energy error MWh
daily energy error percent of actual
full36 MAE
full36 RMSE
full36 bias
p90 absolute error
p95 absolute error
MAE_0_6h
MAE_0_12h
MAE_0_24h
MAE_24_36h
weekday/weekend split
cold/high-load/ramp regimes where available
```

Comparison metrics:

```text
delta_vs_P0056C_DayAhead_MW
delta_vs_P0056C_DayAhead_percent
delta_vs_P0056C_full36_MW
delta_vs_P0056C_full36_percent
delta_vs_P0056C_daily_energy_percent
```

## Decision rules

Improved weather proxy is a candidate default for an area if:

```text
DayAhead MAE improves by >= 2%
or full36 MAE improves by >= 2% without worsening DayAhead
or daily energy error improves by >= 5% without worsening DayAhead by > 1%
```

If improvements are below thresholds, keep P0056B proxy as default and retain P0056D as evidence.

## Required evidence files

Create:

```text
requirements/package-runs/P0056D/CHANGELOG.md
requirements/package-runs/P0056D/review.md
requirements/package-runs/P0056D/design.md
requirements/package-runs/P0056D/functions.md
requirements/package-runs/P0056D/labb-label.md
requirements/package-runs/P0056D/p0056c-baseline-review.md
requirements/package-runs/P0056D/weather-zone-design.md
requirements/package-runs/P0056D/zone-weighting-method.md
requirements/package-runs/P0056D/openmeteo-fetch-contract.md
requirements/package-runs/P0056D/openmeteo-fetch-evidence.md
requirements/package-runs/P0056D/output-table-schema.md
requirements/package-runs/P0056D/weather-feature-contract.md
requirements/package-runs/P0056D/coverage-and-missingness.md
requirements/package-runs/P0056D/weather-proxy-validation.md
requirements/package-runs/P0056D/forecast-retest-method.md
requirements/package-runs/P0056D/area-results.md
requirements/package-runs/P0056D/comparison-vs-p0056c.md
requirements/package-runs/P0056D/leakage-review.md
requirements/package-runs/P0056D/decision.md
requirements/package-runs/P0056D/what-we-learned.md
requirements/package-runs/P0056D/next-package-recommendation.md
```

Optional compact evidence:

```text
zone-weights.csv
station-location-selection.csv
weather-coverage-summary.csv
area-results.csv
comparison-vs-p0056c.csv
metrics-summary.json
```

Do not commit large raw Open-Meteo dumps, full prediction dumps, model binaries, caches or virtualenvs.

## Files to inspect

```text
requirements/package-runs/P0056B/station-proxy-selection.md
requirements/package-runs/P0056B/weather-proxy-validation.md
requirements/package-runs/P0056C/area-results.md
requirements/package-runs/P0056C/cross-area-summary.md
requirements/package-runs/P0056C/component-job-status.md
src/mac/** weather/proxy/forecast scripts
tests/mac/** relevant tests
docs/functions/mac/**
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0056D-labb-se1-se2-fi-openmeteo-weather-proxy-retune.md
requirements/package-runs/P0056D/**
src/mac/** narrowly scoped Open-Meteo weather proxy and SE1/SE2/FI retest code if needed
tests/mac/** narrowly scoped tests for zone weights, weather joins and leakage if code is added
docs/functions/mac/** if durable docs need updating
local DB tables for P0056D weather and metrics if repo owns them
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No changes to unrelated areas' forecasts.
No spot price features.
No flow/exchange/A61/capacity features.
No old physical_balance target.
No future actual load leakage.
No holdout fitting or selection.
No large raw data/model/prediction artifacts committed.
```

## Verification

Codex must define final commands in design.md and run equivalent checks for:

```text
zone weights sum to 1 per area
Open-Meteo rows loaded for all selected zones
coverage complete or missingness documented
P0056D proxy rows produced for SE1/SE2/FI
SE1/SE2/FI retrained and retested
comparison vs P0056C computed
no holdout fitting/selection
no forbidden features
leakage review passes
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP

PASS requires:

```text
all weather zones have selected series
weights are documented and sum to 1
Open-Meteo data is fetched or verified for all zones
SE1, SE2 and FI forecasts are rerun and compared to P0056C
leakage review passes
```

WARN is acceptable if:

```text
some weights are manual low-confidence assumptions
some optional weather variables are missing
one area improves but others do not
Open-Meteo has minor missingness with documented fallback
```

STOP if:

```text
Open-Meteo data cannot be fetched or loaded
weights cannot be assigned defensibly
forecast retest cannot run
leakage is found
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
weather zones and weights
Open-Meteo data coverage
forecast rerun status for SE1/SE2/FI
P0056C baseline metrics
new metrics
improvement/worsening by area
default proxy decision by area
tests/commands run
files changed
confirmation no forbidden features/no large artifacts/no device runtime changes
```

## Completion notes

To be filled after implementation.
