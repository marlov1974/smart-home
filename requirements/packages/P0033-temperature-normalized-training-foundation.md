# Package P0033: Temperature-normalized training foundation

## Status

planned

## Package order

P0033

## Primary area

G2 / Mac tooling / spotprice V2 / temperature normalization / model training data foundation

## Linked requirements

Epic:
- E0001

Features:
- F0001

User stories:
- US0001

## Decision summary

Build the first spotprice V2 temperature-normalized training foundation.

P0033 must implement the macro/normalization layer, not the final production forecast model.

P0033 owns:

```text
M1: Calm normal spotprice model v1
M2: Normal climate model with explicit city/proxy weighting
M3: Statistical weather-normalization delta model v1
Temperature-normalized training series for later M4
```

P0033 must use the completed data foundations:

```text
P0030: SE3 spotprice history
P0031: weather history
P0032: SE1 system_proxy, SE3-SE1 area_diff_proxy, weather proxy groups and gradients
```

P0033 must not build M4, M5, M6 or M7.

## Model roadmap context

The current roadmap is:

```text
M1: Simple calm normal spotprice model, split into SE1 and SE3-SE1.
M2: Simple normal climate model.
M3: Weather-normalization delta model, simple statistical variant, split into target-specific weather/gradient inputs.
M4: Real ML spot model trained on temperature-normalized prices, split into SE1 and SE3-SE1.
M5: Real ML temperature delta model for forecast-time residuals between M4 and actual prices.
M6: Forecast API combining M4 + M5, where SE1 and SE3-SE1 are added to produce SE3.
M7: Absolute long-term forecast requiring futures/forward input.
```

P0033 implements only M1, M2, M3 and the training data output that M4 will consume.

## Core decomposition

P0033 must preserve the P0032 decomposition:

```text
SE1 system_proxy_price
area_diff_proxy_SE3 = SE3 - SE1
SE3 = SE1 + area_diff_proxy_SE3
```

All models and outputs must be split into two primary targets:

```text
system_proxy_se1
area_diff_proxy_se3
```

Do not train or normalize SE3 as one monolithic raw target except as a derived recomposition for diagnostics.

## M1: Calm normal spotprice model v1

M1 creates a calm, weather-blind baseline. It is intentionally not the best possible predictor.

Purpose:

```text
Create a stable normal-price surface so M3 can see temperature-related residuals.
```

Targets:

```text
M1A: SE1 system_proxy_price
M1B: SE3-SE1 area_diff_proxy
```

Required behavior:

- Use broad historical averaging/median behavior across the full available P0030/P0032 history.
- Use heavy smoothing across neighboring weeks/days/periods.
- Use robust statistics that smear out weather events instead of memorizing them.
- Create calm normal prices per target and timestamp.
- Preserve slow calendar/period structure while avoiding short-term weather or price-event learning.

Allowed features:

```text
local_hour
period_of_day
weekday/weekend
holiday flag if repo has calendar support
week_of_year or day_of_year smooth/cyclic representation
broad year/regime trend only if very smoothed and documented
```

Forbidden M1 features:

```text
temperature
apparent_temperature
heating_degree_hours
weather gradients
wind
cloud/solar/radiation
precipitation/snowfall
short price lags
rolling 24h/7d price features
anything that lets M1 learn acute weather events
```

M1 output examples:

```text
normal_price_v1_se1
normal_price_v1_area_diff
normal_price_v1_se3 = normal_price_v1_se1 + normal_price_v1_area_diff
```

## M2: Normal climate model

M2 creates normal climate and climate anomalies for the weather signals needed by M3.

P0033 must not assume P0032 proxy group weights are automatically sufficient for model targets. It must create and document a target-specific climate weighting layer.

M2 must include two weighting levels:

```text
Level 1: city/location -> P0032 proxy group
Level 2: proxy group/gradient -> model target climate signal
```

P0033 must first read the actual installed P0032 weather location weights from the local SQLite database and save them as evidence:

```bash
sqlite3 ~/.smart-home/data/weather_history.sqlite3 "
select area_proxy, name, latitude, longitude, weight
from weather_locations
where area_proxy in (
  'se1_core_weather',
  'nordic_connected_weather',
  'south_connected_weather',
  'se3_load_weather'
)
order by area_proxy, weight desc, name;
"
```

Store the result in:

```text
requirements/package-runs/P0033/p0032-weather-location-weights.md
```

If the local DB is unavailable, Codex must inspect the implementation that seeds `weather_locations` and record the source. If neither DB nor implementation can be read, STOP before building M2/M3.

### Level 1 weighting: city/location -> proxy group

P0032 already created proxy groups. P0033 must verify the actual P0032 weights and then either:

```text
A. preserve the existing P0032 location weights if they match the intended group semantics
B. propose a corrective package if they are materially wrong
```

P0033 should not silently rewrite P0032 location weights unless explicitly required by design and validated. If location-weight changes are needed, document them and classify as WARN unless the change is clearly safe and package-scoped.

Required intended group semantics:

```text
se1_core_weather:
  dominated by northern Sweden, northern Finland and northern/northwestern Norway.

nordic_connected_weather:
  lower-weight connected Nordic weather/load signal: southern/mid Norway and southern Finland.

south_connected_weather:
  low-weight southern connected load/weather signal only.

se3_load_weather:
  SE3 demand/load weather signal.
```

### Proposed Level 1 v1 weights

These are the proposed intended weights if P0032 implementation does not already define better weights. Codex must compare them to the actual DB/code before deciding.

#### se1_core_weather

Normalize these to sum to 1.0 inside the group:

```text
Kiruna       0.11
Gällivare    0.10
Luleå        0.11
Skellefteå   0.09
Umeå         0.09
Östersund    0.08
Sundsvall    0.07
Rovaniemi    0.08
Oulu         0.08
Tromsø       0.07
Narvik       0.06
Bodø         0.06
```

Rationale:

```text
High aggregate weight on northern Sweden and North Nordic weather. Finland/Norway north included because SE1/system-proxy is affected by Nordic production and balance, not only Swedish load.
```

#### nordic_connected_weather

Normalize to sum to 1.0 inside the group:

```text
Trondheim  0.18
Oslo       0.17
Bergen     0.13
Helsinki   0.20
Tampere    0.17
Turku      0.15
```

Rationale:

```text
Connected Nordic weather/load signal. Southern Finland and southern/mid Norway may affect the SE1/system-proxy level, but with lower model-level weight than se1_core_weather.
```

#### south_connected_weather

Normalize to sum to 1.0 inside the group:

```text
Stockholm   0.30
Göteborg    0.25
Malmö       0.20
Copenhagen  0.25
```

Rationale:

```text
Southern connected load/weather signal. It may affect broad Nordic/system-proxy conditions, but it must not dominate SE1 weather.
```

#### se3_load_weather

Normalize to sum to 1.0 inside the group:

```text
Stockholm   0.18
Örebro      0.08
Västerås    0.08
Linköping   0.09
Norrköping  0.07
Göteborg    0.14
Jönköping   0.08
Karlstad    0.06
Borlänge    0.05
Gävle       0.05
Kalmar      0.06
Växjö       0.06
```

Rationale:

```text
SE3 load/weather proxy weighted toward major demand centers and geographically distributed SE3 load/weather exposure.
```

### Level 2 weighting: proxy group/gradient -> target climate signal

P0033 must create a target-specific climate weighting layer for M2/M3. These weights are not final ML weights; they are initial v1 climate-signal construction weights for M3.

P0033 must evaluate candidate weights against M1 residuals and store selected weights in a manifest/table with:

```text
version
target
input_signal
variable
weight
rationale
validation_score
```

Initial v1 proposal:

#### Target: SE1 system_proxy_price

Use climate signal focused on broad northern/nordic conditions:

```text
se1_system_climate_signal_temperature =
  0.70 * se1_core_weather.temperature_2m
+ 0.25 * nordic_connected_weather.temperature_2m
+ 0.05 * south_connected_weather.temperature_2m
```

Same group weights should be tested for:

```text
apparent_temperature
heating_degree_hours
cooling_degree_hours
```

For wind/system balance features, use:

```text
se1_system_climate_signal_wind_100m =
  0.60 * se1_core_weather.wind_speed_100m
+ 0.40 * nordic_connected_weather.wind_speed_100m
```

but P0033/M3 temperature normalization should only consume temperature/apparent/heating-degree features unless wind is explicitly documented as deferred. Wind feature construction may be stored for future packages but must not drive M3 unless design justifies it.

Constraints for SE1 climate weights:

```text
se1_core_weather >= 0.55
south_connected_weather <= 0.10
all weights >= 0
weights sum to 1.0 for each target signal
```

#### Target: SE3-SE1 area_diff_proxy

Use climate signal focused on gradients between SE3 load weather and SE1 core weather, with small southern pressure input.

Preferred M3 inputs are separate gradient features, not a single collapsed scalar:

```text
temp_gradient_se3_load_minus_se1_core
apparent_temp_gradient_se3_load_minus_se1_core
heating_degree_gradient_se3_load_minus_se1_core
south_temp_gradient_minus_se1_core
```

Initial v1 scalar area-diff climate signal if needed:

```text
area_diff_climate_signal_temperature =
  0.55 * temp_gradient_se3_load_minus_se1_core
+ 0.25 * heating_degree_gradient_se3_load_minus_se1_core
+ 0.15 * south_temp_gradient_minus_se1_core
+ 0.05 * apparent_temp_gradient_se3_load_minus_se1_core
```

Alternative design allowed:

```text
Keep the four gradient features separate and let the simple M3 statistical model bucket/score them jointly.
```

This is preferred if implementation remains understandable and robust.

Constraints for area-diff climate inputs:

```text
se3_load_minus_se1_core temperature/heating gradients must dominate
south-connected signal must not exceed 0.20 of scalar weight
no raw south or se3 signal may replace the gradient basis
all weights >= 0 unless design explicitly uses signed gradients
```

## M2 normal climate outputs

For each proxy group and target climate signal, P0033 must compute normals and anomalies.

Required normal models:

```text
normal_temperature by day_of_year/hour or smoothed calendar-hour
normal_apparent_temperature
normal_heating_degree_hours
normal_cooling_degree_hours
normal_temperature_gradient where applicable
```

Required anomaly outputs:

```text
temperature_anomaly
apparent_temperature_anomaly
heating_degree_anomaly
cooling_degree_anomaly
temperature_gradient_anomaly
heating_degree_gradient_anomaly
```

Normals must be smoothed enough that they represent climate seasonality, not individual weather events.

## M3: Statistical weather-normalization delta model v1

M3 uses M1 residuals and M2 anomalies to estimate a conservative temperature delta used only to create M4 training data.

Targets:

```text
M3A target = actual_SE1 - M1_normal_price_v1_SE1
M3B target = actual_area_diff_proxy_SE3 - M1_normal_price_v1_area_diff
```

M3 is not the later forecast-time ML temperature model. M3 remains in the future as a macro/data-cleaning layer.

Required approach:

- simple statistical variant, not full ML
- robust buckets/medians/smoothing/dead-zones
- no external ML dependency
- split per target: SE1 and SE3-SE1
- use temperature/anomaly features only for P0033; wind/solar are deferred
- keep adjustments conservative so it does not erase structural price patterns

Example M3 behavior:

```text
if temperature anomaly is near normal, predicted temp delta should be near zero.
if cold anomaly is extreme during high-load periods, predicted temp delta may be positive.
if warm anomaly reduces heating demand, predicted temp delta may be negative.
```

## Temperature-normalized training output

P0033 must produce timestamp-aligned output series:

```text
temp_delta_v1_se1
temp_delta_v1_area_diff
temp_normalized_price_v1_se1 = actual_se1 - temp_delta_v1_se1
temp_normalized_area_diff_v1 = actual_area_diff - temp_delta_v1_area_diff
temp_normalized_price_v1_se3 = temp_normalized_price_v1_se1 + temp_normalized_area_diff_v1
```

This output is the training input for P0034/M4.

## Storage requirements

Use local SQLite. Prefer a separate feature/model DB unless design finds a strong reason to keep all model artifacts in the price DB.

Expected default:

```text
~/.smart-home/data/spotprice_model_features.sqlite3
```

Input DBs:

```text
~/.smart-home/data/spotprice_history.sqlite3
~/.smart-home/data/weather_history.sqlite3
```

Do not commit generated local SQLite DBs to repo.

Repo must commit:

```text
- model/feature builder code
- schema/migration definitions
- tests with small fixtures
- docs/functions/mac/spotprice-temperature-normalization.md
- package-run evidence and manifests
```

## Required tables/views or equivalents

Final schema to be chosen in design, but must support:

```text
model_runs
m1_normal_price_v1
m2_climate_normals
m2_climate_anomalies
m2_climate_weights
m3_temperature_delta_v1
m3_temperature_delta_buckets
m3_temp_normalized_prices_v1
training_foundation_manifest
```

## Validation and diagnostics

P0033 must validate:

- full join coverage between SE1/SE3-SE1 price data and weather proxy data over the overlapping period
- no hidden gaps
- no timestamp mismatches
- M1 outputs exist for both targets
- M2 normals/anomalies exist for required climate signals
- M3 deltas exist for both targets
- temp-normalized outputs exist for SE1, area_diff and derived SE3
- generated rows match expected coverage

Required diagnostics:

```text
M1 residual min/max/mean/std by target
M2 anomaly min/max/mean/std by signal
M3 delta min/max/mean/std by target
correlation/residual association with temperature anomaly before M3
correlation/residual association with temperature anomaly after M3
extreme cold/warm bucket residual before/after
row counts and date coverage
```

Primary sanity target:

```text
association between M1 residual and temperature anomaly should decrease after M3 normalization, without collapsing calendar/weekly structure.
```

## Non-goals

- No M4 real ML spot model.
- No M5 real ML temperature forecast delta model.
- No M6 forecast API.
- No M7 futures/absolute long-term model.
- No wind normalization in P0033.
- No solar/cloud/radiation normalization in P0033.
- No optimizer/control changes.
- No Shelly runtime changes.
- No Shelly deploy.
- No KVS writes.
- No Home Assistant integration.
- No FTX/heating-control policy.
- No MCP/tunnel work.
- No live device access.
- No external ML dependencies.

## Invariants

- Mac-side only.
- Python standard library only unless Codex stops for explicit dependency decision.
- No device writes.
- No Shelly RPC calls.
- No actuator/output/switch/cover/relay actions.
- No secrets.
- P0033 must be reproducible from P0030/P0031/P0032 local SQLite data.
- Unit tests must run without network access.
- Full local generated feature DB stays out of repo.
- M3 is a permanent macro/data-cleaning stage; M5 later does not replace it.

## Knowledge updates

Create or update:

- `docs/functions/mac/spotprice-temperature-normalization.md`
- `docs/functions/00-index.md`

Update if durable model architecture knowledge is created:

- `docs/functions/mac/spotprice-history.md`
- `docs/functions/mac/weather-history-dataset.md`
- `memory/device-management/mac-layer.md`
- `memory/knowhow/codex.md`

## Implementation updates

Expected areas, final paths to be chosen in design:

- `src/mac/services/spotprice_temperature_normalization/**` or equivalent
- `tests/mac/services/spotprice_temperature_normalization/**` or equivalent
- `docs/functions/mac/spotprice-temperature-normalization.md`
- `docs/functions/00-index.md`
- `requirements/package-runs/P0033/**`
- `requirements/packages/P0033-temperature-normalized-training-foundation.md`

## Files to inspect

- `README.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/08-context-bootstrap-modes.md`
- `memory/device-management/mac-layer.md`
- `requirements/packages/P0030-historical-spotprice-dataset-foundation.md`
- all P0030 amendments
- `requirements/packages/P0031-weather-history-dataset-service.md`
- `requirements/packages/P0032-se1-system-proxy-history.md`
- `requirements/packages/P0032-amendment-weather-proxy-groups.md`
- `requirements/package-runs/P0030/**`
- `requirements/package-runs/P0031/**`
- `requirements/package-runs/P0032/**`
- `docs/functions/mac/spotprice-history.md`
- `docs/functions/mac/weather-history-dataset.md`
- `src/mac/services/spotprice_history/**`
- `src/mac/services/weather_history/**`
- tests for spotprice/weather history

## Files allowed to change

- `src/mac/services/spotprice_temperature_normalization/**` or equivalent path documented in design
- `tests/mac/services/spotprice_temperature_normalization/**` or equivalent test path documented in design
- `docs/functions/mac/spotprice-temperature-normalization.md`
- `docs/functions/00-index.md`
- `docs/functions/mac/spotprice-history.md` only for cross-link/query contract updates
- `docs/functions/mac/weather-history-dataset.md` only for cross-link/query contract updates
- `memory/device-management/mac-layer.md` only for durable Mac model-pipeline documentation
- `memory/knowhow/codex.md` only for reusable package/model lessons
- `requirements/package-runs/P0033/**`
- `requirements/packages/P0033-temperature-normalized-training-foundation.md`

Local Mac artifacts expected after verification:

```text
~/.smart-home/data/spotprice_model_features.sqlite3
```

## Forbidden changes

- No G1 repository changes.
- No deploy artifact changes under `dep/s/**`.
- No Home Assistant changes.
- No Shelly runtime script changes.
- No live Shelly calls.
- No KVS writes.
- No actuator/output/switch/cover/relay implementation or calls.
- No optimizer policy changes.
- No M4/M5/M6/M7 implementation.
- No full ML training.
- No weather forecast API.
- No futures data.
- No external Python package dependencies unless the package stops and asks for a dependency decision.
- No secrets or credentialed data sources.
- No root/system launch daemon.
- No public network service exposure.
- No broad refactor outside the minimal P0033 model-foundation scope.

## Pre-implementation consistency review

Before editing implementation/data files, Codex must classify as:

- `PASS`: P0030/P0031/P0032 data exists locally with sufficient overlap; P0032 weights can be read; P0033 can build M1/M2/M3 outputs safely.
- `WARN`: implementable with documented uncertainty, for example P0032 location weights must be inferred from implementation rather than DB.
- `STOP`: P0032 weights cannot be read/inferred; local DBs are missing; overlap is insufficient; or task requires M4/M5/full ML.

Required review checks:

- P0030/P0032 spotprice DB exists.
- P0031/P0032 weather DB exists.
- `spotprice_system_proxy_hourly` is available.
- P0032 weather proxy group views/gradient table are available.
- Actual P0032 city/location weights are dumped to evidence.
- Date overlap between price and weather data is sufficient.
- No device access is required.

Store review evidence in:

```text
requirements/package-runs/P0033/review.md
```

## Implementation design policy

Codex must create design before coding:

```text
requirements/package-runs/P0033/design.md
```

Design must document:

```text
- input DBs and date overlap
- actual P0032 Level 1 weights found
- selected/validated P0033 Level 2 weights
- M1 calm baseline algorithm
- M2 climate normal algorithm
- M3 statistical delta algorithm
- dead-zone and bucket policy
- storage schema/path
- build command
- validation command
- diagnostics command
- why M4/M5/M6/M7 are deferred
```

## Function design policy

Codex must create function design before implementation:

```text
requirements/package-runs/P0033/functions.md
```

Document functions or equivalent responsibilities:

```text
open_feature_database(...)
initialize_schema(...)
load_price_targets(...)
load_weather_proxy_features(...)
dump_p0032_location_weights(...)
compute_m1_calm_normal_price(...)
compute_m2_climate_normals(...)
compute_m2_climate_anomalies(...)
select_m2_target_weights(...)
compute_m3_statistical_temperature_delta(...)
build_temp_normalized_training_series(...)
validate_training_foundation(...)
summarize_temperature_normalization(...)
main(argv=None)
```

## Context-reset phase gates

Use:

```text
sync -> bootstrap -> review -> design -> function design -> implementation -> build local feature DB -> tests -> validation/diagnostics -> evidence/changelog
```

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/P0033/
```

Expected evidence files:

```text
CHANGELOG.md
review.md
design.md
functions.md
attempts.md
p0032-weather-location-weights.md
climate-weight-selection.md
training-foundation-summary.md
diagnostics.md
```

Evidence must include:

- P0032 actual location weights
- selected Level 2 model target weights
- input coverage
- output coverage
- M1 residual summaries
- M2 anomaly summaries
- M3 delta summaries
- before/after temperature association diagnostics
- feature DB path and size
- tests run
- no ML/full forecast/device work

## Test cases

### TC1: P0032 weights extraction

Given a weather DB with proxy locations
When P0033 dumps weights
Then it records area_proxy, name, coordinates and weight for all relevant groups.

### TC2: M1 calm baseline avoids weather features

Given price and weather inputs
When M1 runs
Then M1 uses only allowed calendar/smoothed price structure and no weather columns.

### TC3: M2 climate normal creation

Given historical proxy weather data
When M2 runs
Then normal climate and anomaly rows are created for required signals.

### TC4: Level 2 climate weights

Given candidate proxy/gradient signals
When weight selection runs
Then selected weights satisfy constraints and are stored with rationale.

### TC5: M3 residual target

Given actual prices and M1 outputs
When M3 trains/builds statistical deltas
Then target residual equals actual minus M1 baseline for SE1 and area_diff.

### TC6: Dead-zone behavior

Given near-normal temperature anomaly
When M3 predicts delta
Then delta is near zero according to design.

### TC7: Temperature-normalized output

Given actual price and M3 delta
When normalized series is built
Then normalized = actual - delta for SE1 and area_diff, and SE3 is recomposed.

### TC8: Join completeness

Given P0030/P0031/P0032 input DBs
When P0033 builds outputs
Then all expected overlapping timestamps are present or exact gaps are reported.

### TC9: Before/after diagnostics

Given M1 residuals and M3-normalized residuals
When diagnostics run
Then temperature association before/after is reported.

### TC10: No-network/unit tests

Given tests
When unit tests run
Then they pass without network or device access.

## Verification commands

Codex must define final commands in design, but expected equivalents are:

```bash
python3 -m unittest discover tests/mac/services/spotprice_temperature_normalization
python3 -m unittest discover tests/mac/services
python3 -m src.mac.services.spotprice_temperature_normalization build --price-db ~/.smart-home/data/spotprice_history.sqlite3 --weather-db ~/.smart-home/data/weather_history.sqlite3 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --start-date 2022-05-30
python3 -m src.mac.services.spotprice_temperature_normalization validate --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3
python3 -m src.mac.services.spotprice_temperature_normalization diagnostics --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3
git diff --check
```

If actual commands differ, document equivalents.

## Runtime health checks

Record:

- input price DB path
- input weather DB path
- feature DB path
- date interval
- row counts per output table
- complete true/false
- missing timestamp count
- M1 residual summaries
- M2 anomaly summaries
- M3 delta summaries
- before/after temperature association metrics
- feature DB size

No launchd, service, device or runtime deployment health checks are required in P0033.

## Deployment plan

P0033 creates a local model-feature/training foundation database. It is not a production forecast service.

No launchd job, API server, Shelly deploy, Home Assistant integration or device interaction is part of P0033.

## Rollback plan

Rollback means removing or ignoring:

```text
~/.smart-home/data/spotprice_model_features.sqlite3
```

Repo rollback is a new forward-moving package if the model foundation shape is wrong.

## Expected Codex output

- consistency review result: PASS/WARN/STOP
- P0032 actual location weights evidence path
- selected Level 2 climate weights
- M1 algorithm summary
- M2 algorithm summary
- M3 algorithm summary
- feature DB path
- date interval achieved
- output row counts
- diagnostics before/after temperature normalization
- tests run
- files changed
- no M4/M5/M6/M7 confirmation
- no device/Shelly/HA confirmation
- commit SHA after push, if successful and pushed
- diff summary

## Completion notes

To be filled after implementation.
