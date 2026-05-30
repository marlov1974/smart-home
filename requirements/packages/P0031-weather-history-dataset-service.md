# Package P0031: Weather history dataset service

## Status

planned

## Package order

P0031

## Primary area

G2 / Mac tooling / weather history / data foundation / future ML input

## Linked requirements

Epic:
- E0001

Features:
- F0001

User stories:
- US0001

## Decision summary

Create a complete Mac-side weather history data foundation for future spotprice V2 ML and weather-normalization work.

P0031 follows P0030:

```text
P0030 = spotprice history database and daily spotprice ingest
P0031 = weather history database and daily weather ingest
```

P0031 must backfill historical Open-Meteo weather data for the same time span as P0030 and then productionize a daily Mac job that keeps the local weather database current.

Target period:

```text
start: 2022-05-30
end:   latest safely available actual/historical weather data at build time
```

P0031 must fetch and store all weather series requested for future V2 modeling:

```text
temperature_2m
apparent_temperature
wind_speed_10m
wind_speed_100m
wind_gusts_10m
cloud_cover
shortwave_radiation
precipitation
snowfall
relative_humidity_2m
pressure_msl
```

P0031 must be complete when Codex finishes:

```text
1. historical weather data is backfilled into a local SQLite database
2. a user-level launchd job is installed/enabled
3. the job runs daily and ingests the newest safely available complete weather day
4. validation/evidence proves the database and job state
```

P0031 must not implement the future ML model, weather-normalized price model, optimizer/control changes, Shelly runtime changes, Home Assistant integration, or device control.

## External source basis

Use Open-Meteo Historical Weather API as the expected data source unless Codex finds a concrete blocker during review.

Relevant current Open-Meteo facts to verify in review/design:

- Historical Weather API exposes historical weather from 1940 until now.
- ERA5/ERA5-Land provide gap-free and consistent reanalysis data suitable for multi-year history.
- The `/v1/archive` endpoint accepts latitude, longitude, start_date, end_date, hourly variables and timezone parameters.
- Open-Meteo documents the required hourly variables or equivalents for the requested series.
- ERA5 and ERA5-Land historical data may have daily update delay; Codex must design daily ingest around latest safely available complete day rather than assuming yesterday is always available.

Codex must verify current Open-Meteo documentation during P0031 review. If API behavior or variable names differ, Codex must document the difference in `requirements/package-runs/P0031/review.md` and adjust safely.

## Context and rationale

The future spotprice V2 model is expected to use:

- weather normalization
- temperature anomaly
- wind anomaly
- season and trend features
- solar/radiation proxies
- precipitation/snow proxies
- calendar/time features
- P0030 spotprice history

P0031 creates the weather half of that data foundation. It is intentionally data/storage/service work only.

## Current behavior

Before P0031, the project has spotprice history and/or spot-index work from P0030, but no durable Open-Meteo weather-history SQLite store with a daily production ingest job for future ML features.

## Problem

A future advanced ML spotprice model cannot reliably learn weather effects unless historical weather is stored in a reproducible, queryable local database with the same time coverage as the spotprice database.

A one-time ad-hoc weather export is not sufficient; the Mac needs a productionized daily ingest path.

## Target behavior

Build Mac-side tooling and local data artifacts that can:

1. initialize a weather history SQLite database
2. backfill Open-Meteo historical weather from 2022-05-30 through latest safely available actual/historical data
3. ingest all requested hourly variables
4. store per-location raw weather observations
5. store or compute an SE3 weather proxy suitable for future price modeling
6. validate continuity, duplicates, missing hours and source coverage
7. install and enable a user-level launchd job that runs daily
8. perform an idempotent daily ingest of the newest safely available complete weather day
9. record ingest runs and manifest/evidence
10. expose a query/export path for future feature-store/model packages

## Geography / SE3 weather proxy

P0031 must decide and document a geographic representation for SE3-relevant weather.

Default expected approach unless Codex finds a better repo-established convention:

```text
multi-location weighted SE3 proxy
```

Candidate locations, to be finalized in design:

```text
Stockholm / Mälardalen
Göteborg / western SE3
Örebro / inland SE3
Linköping / eastern/southern SE3
```

Codex must choose exact coordinates and weights in `requirements/package-runs/P0031/design.md` and explain why. The design must support future replacement/refinement without breaking the database contract.

Minimum acceptable if multi-location fetching is blocked:

```text
single representative SE3 coordinate with WARN evidence
```

but the package should prefer the weighted multi-location model.

## Data source/model selection

Codex must choose Open-Meteo model settings deliberately.

Expected preference for long-term consistency:

```text
ERA5 or ERA5-Land / ERA5-Seamless as appropriate for variables
```

Because P0031 requires wind, gusts, cloud cover, solar radiation, precipitation, snowfall, humidity and pressure, Codex must verify which Open-Meteo model supports the full variable set. If a single model cannot safely provide all variables, Codex must document the chosen combination or select Open-Meteo `best_match` only if the consistency tradeoff is explicit.

## Required hourly variables

P0031 must fetch/store these Open-Meteo hourly variables or documented equivalents:

```text
temperature_2m
apparent_temperature
wind_speed_10m
wind_speed_100m
wind_gusts_10m
cloud_cover
shortwave_radiation
precipitation
snowfall
relative_humidity_2m
pressure_msl
```

Codex may also store metadata variables useful for validation/source traceability, such as location id, latitude, longitude, elevation, timezone, utc offset and Open-Meteo generation time.

## Derived feature preparation

P0031 may compute simple deterministic derived weather columns or views if they are pure data features, not ML:

```text
heating_degree_hours
cooling_degree_hours
se3_weighted_temperature_2m
se3_weighted_wind_speed_100m
se3_weighted_shortwave_radiation
```

P0031 must not train a model or implement weather-normalized price prediction.

Temperature anomaly, wind anomaly and broader feature-store work may be prepared by schema/docs but should be implemented in a later feature-store/model package unless Codex can compute them as deterministic climatology-free transforms. Any anomaly requiring climate normals should be deferred unless explicitly designed from the same historical dataset without model training.

## Storage requirements

Use SQLite unless Codex finds a concrete repository-policy blocker.

Expected local DB path:

```text
~/.smart-home/data/weather_history.sqlite3
```

The full generated SQLite database normally stays local and is not committed to repo.

Repo must commit:

```text
- schema/migration definition
- builder/ingest/validator code
- launchd install/render code
- small deterministic test fixtures
- docs/functions/mac/weather-history-dataset.md
- package-run evidence summaries
```

Repo must not commit:

```text
- large raw Open-Meteo dumps
- secrets
- generated full local SQLite DB unless explicitly justified
```

## Database schema requirements

Codex must design a stable SQLite schema with at least:

```text
weather_locations
  location_id
  name
  latitude
  longitude
  weight
  area_proxy
  source
  active

weather_observations
  location_id
  timestamp_utc or timestamp_local with explicit timezone policy
  local_date
  local_hour
  timezone
  temperature_2m
  apparent_temperature
  wind_speed_10m
  wind_speed_100m
  wind_gusts_10m
  cloud_cover
  shortwave_radiation
  precipitation
  snowfall
  relative_humidity_2m
  pressure_msl
  source_model
  source
  fetched_at
  ingest_run_id
  PRIMARY KEY or UNIQUE(location_id, timestamp_*)

weather_area_hourly
  area_proxy
  timestamp_utc or timestamp_local with explicit timezone policy
  local_date
  local_hour
  weighted_temperature_2m
  weighted_apparent_temperature
  weighted_wind_speed_10m
  weighted_wind_speed_100m
  weighted_wind_gusts_10m
  weighted_cloud_cover
  weighted_shortwave_radiation
  weighted_precipitation
  weighted_snowfall
  weighted_relative_humidity_2m
  weighted_pressure_msl
  heating_degree_hours
  cooling_degree_hours
  source_coverage_count
  source_coverage_weight
  ingest_run_id
  PRIMARY KEY or UNIQUE(area_proxy, timestamp_*)

weather_ingest_runs
  run_id
  run_type: backfill | daily | validate | install_job
  started_at
  completed_at
  source
  source_model
  start_date
  end_date
  status
  locations_requested
  records_inserted
  records_updated
  gaps_detected
  error_summary
```

Codex may choose a normalized long-form observation schema instead of wide columns if design justifies it for future ML. The final schema must make future feature extraction straightforward without external dependencies.

## Timezone and DST policy

P0031 must use the same timezone/DST strategy as P0030 where possible.

Expected local timezone:

```text
Europe/Stockholm
```

The database must preserve enough information to join weather rows to P0030 spotprice rows hour-by-hour. DST 23-hour and 25-hour days must be handled explicitly and validated.

## Completeness and validation requirements

P0031 must validate and report:

- first timestamp
- last timestamp
- total rows per table
- row count per year
- expected hour count per year/segment under DST policy
- duplicate rows per location/hour and area/hour
- missing hours/gaps
- variable null counts
- min/max/mean per variable per year
- source model
- source update availability / delay assumptions
- database file size
- dataset completeness status

Completeness rule:

```text
complete=true only if no gaps exist from 2022-05-30 through the selected end timestamp for required locations and the SE3 area proxy.
```

If gaps exist:

- do not fill them synthetically
- record exact missing date/hour ranges
- mark dataset incomplete
- classify `WARN` or `STOP` depending on whether a useful partial artifact is intentionally installed

## Backfill requirement

P0031 must not stop at code/schema only.

It must backfill the local database used by the service:

```text
~/.smart-home/data/weather_history.sqlite3
```

from:

```text
2022-05-30
```

to latest safely available historical weather data at build time.

Backfill must be read-only HTTP only and must record concise evidence. Do not store large raw HTTP payloads in repo.

## Daily ingest job requirement

P0031 must install and enable a user-level launchd job.

Expected label:

```text
se.mlovholm.smart-home.weather-history-daily
```

Expected daily behavior:

1. run every day at a safe local time selected by Codex after reviewing Open-Meteo update delays
2. open `~/.smart-home/data/weather_history.sqlite3`
3. determine the newest safely available complete historical weather day
4. fetch only missing complete day(s) for all configured locations
5. upsert rows by unique location+timestamp and area_proxy+timestamp keys
6. record ingest run metadata
7. validate the affected tail and update/export manifest summary
8. exit success with `no_new_complete_day_available` if Open-Meteo has not published the relevant historical day yet
9. never synthesize missing values or hide gaps

The user requested daily retrieval of the day's result. Because historical/reanalysis data can have source delay, Codex must define exactly which day the job attempts to ingest at runtime. Acceptable design examples:

```text
- daily at 15:00, ingest latest safely available complete historical day
- daily at 14:30, try yesterday; if not available, exit no_new_complete_day_available and retry the next day
```

Codex must justify the chosen schedule and semantics.

## Launchd/service requirements

P0031 must install a user-level LaunchAgent, not a system-wide root daemon.

Expected plist path:

```text
~/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
```

The plist must include or equivalent:

```text
StartCalendarInterval with chosen daily time
StandardOutPath ~/.smart-home/logs/weather-history-daily.out.log
StandardErrorPath ~/.smart-home/logs/weather-history-daily.err.log
WorkingDirectory <smart-home repo root>
```

Codex must create required local directories:

```text
~/.smart-home/data
~/.smart-home/logs
```

Codex must:

1. render/create the plist
2. install it to user LaunchAgents
3. load/bootstrap/enable it with current macOS `launchctl` flow
4. run manual ingest verification
5. verify `launchctl print gui/$(id -u)/se.mlovholm.smart-home.weather-history-daily` or document precise WARN/STOP blocker
6. document rollback/unload commands

If the Codex sandbox blocks launchd operations, Codex must create all artifacts, run direct command verification, and record `WARN` with exact manual commands. But the intended package outcome is an installed and enabled daily job.

## Source timing / daily schedule

Codex must review Open-Meteo update timing and choose a robust daily run time.

Because Open-Meteo documents ERA5/ERA5-Land update delays, P0031 must avoid treating missing newest days as hard failure. The job should ingest the latest safely available complete day, not necessarily the previous calendar day.

If Codex chooses an IFS or best-match source with less delay, it must still record source consistency tradeoffs for future ML.

## Non-goals

- No full ML model.
- No model training.
- No weather-normalized spotprice prediction.
- No spotprice optimizer/control changes.
- No Shelly runtime changes.
- No Shelly deploy.
- No KVS writes.
- No Home Assistant integration.
- No FTX/heating-control policy.
- No MCP/tunnel work.
- No live device access.
- No synthetic gap filling, interpolation or imputation.
- No external Python dependencies unless Codex stops for explicit dependency decision.

## Invariants

- Mac-side only.
- Python standard library only unless Codex stops for explicit dependency decision.
- Read-only HTTP only.
- No device writes.
- No Shelly RPC calls.
- No actuator/output/switch/cover/relay actions.
- No secrets.
- Database build and validation must be reproducible.
- Unit tests must run without network access.
- Full local database normally stays out of repo.
- User-level launchd only; no root/system daemon.

## Knowledge updates

Create or update:

- `docs/functions/mac/weather-history-dataset.md`
- `docs/functions/00-index.md`

Update if durable cross-package storage/feature-store knowledge is created:

- `memory/device-management/mac-layer.md`
- `memory/knowhow/codex.md`
- `memory/knowhow/shelly.md` only if a reusable weather/spotprice source lesson matters to Shelly packages

## Implementation updates

Expected areas, final paths to be chosen in design:

- `src/mac/services/weather_history/**`
- `tests/mac/services/weather_history/**`
- launchd plist template or renderer under a repo-consistent Mac tooling path
- `docs/functions/mac/weather-history-dataset.md`
- `docs/functions/00-index.md`
- `requirements/package-runs/P0031/**`
- `requirements/packages/P0031-weather-history-dataset-service.md`

## Files to inspect

- `README.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/08-context-bootstrap-modes.md`
- `memory/device-management/mac-layer.md`
- `memory/knowhow/codex.md`
- `requirements/packages/P0030-historical-spotprice-dataset-foundation.md`
- all P0030 amendments
- `requirements/package-runs/P0030/**` if P0030 has been implemented locally
- `docs/functions/mac/spotprice-history-dataset.md` if present
- `docs/functions/mac/spot-forecast.md`
- existing weather source/test directories
- existing Mac launchd/service patterns
- current Open-Meteo Historical Weather API documentation

## Files allowed to change

- `src/mac/services/weather_history/**`
- `tests/mac/services/weather_history/**`
- selected launchd template/render code documented in design
- selected small weather test fixtures documented in design
- `docs/functions/mac/weather-history-dataset.md`
- `docs/functions/00-index.md`
- `memory/device-management/mac-layer.md` only for durable Mac data-service pattern documentation
- `memory/knowhow/codex.md` only for reusable package/service lessons
- `memory/knowhow/shelly.md` only for reusable future Shelly-relevant source lessons
- `requirements/package-runs/P0031/**`
- `requirements/packages/P0031-weather-history-dataset-service.md`

Local Mac artifacts expected after verification:

```text
~/.smart-home/data/weather_history.sqlite3
~/.smart-home/logs/weather-history-daily.out.log
~/.smart-home/logs/weather-history-daily.err.log
~/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
```

## Forbidden changes

- No G1 repository changes.
- No deploy artifact changes under `dep/s/**`.
- No Home Assistant changes.
- No Shelly runtime script changes.
- No live Shelly calls.
- No KVS writes.
- No actuator/output/switch/cover/relay implementation or calls.
- No FTX/heating-control policy changes.
- No optimizer policy changes.
- No ML training or model artifacts.
- No weather-normalized price prediction implementation.
- No synthetic gap filling/interpolation/imputation.
- No external Python package dependencies unless the package stops and asks for a dependency decision.
- No secrets or credentialed data sources.
- No root/system launch daemon.
- No public network service exposure.
- No broad refactor outside the minimal P0031 data builder/validator/service/docs scope.

## Pre-implementation consistency review

Before editing implementation/data files, Codex must verify this package against repository truth and current Open-Meteo truth and classify it as:

- `PASS`: source, variables, format, DB placement and launchd plan are clear; data can be backfilled and daily job can be installed.
- `WARN`: implementable with documented uncertainty, for example source delay means latest days are intentionally behind, multi-location source limitations, or launchd sandbox verification restrictions.
- `STOP`: source/license/format is unclear; requested variables cannot be fetched safely; data would be too large; external dependency is required; launchd installation is unsafe; or the task requires scope expansion.

Required review checks:

- P0030 is complete enough locally to align timezone/DB conventions.
- Open-Meteo source supports the requested period and required variables.
- Determine source model and update-delay semantics.
- Determine multi-location coordinates/weights.
- Estimate DB size and repo impact.
- Confirm no Shelly/device access is required.
- Confirm user-level launchd install path and label.

Store review evidence in:

```text
requirements/package-runs/P0031/review.md
```

## Implementation design policy

Codex must create package-scoped implementation design before coding/fetching substantial data:

```text
requirements/package-runs/P0031/design.md
```

The design must document:

```text
- Open-Meteo documentation checked and date
- source URL/API pattern
- source model choice and consistency/delay tradeoff
- exact date interval
- weather variables
- SE3 proxy locations/coordinates/weights
- timezone/DST policy
- SQLite schema and DB path
- estimated DB size
- fetch/backfill command
- ingest-daily command
- validation command
- launchd label/plist path/schedule
- install/load/enable command plan
- rollback/unload commands
- gap detection model
- duplicate detection model
- variable null-count model
- annual summary model
- handling of source publication delay
- why no ML/weather-normalization is implemented in P0031
- how future P0032/P0033 feature-store/model packages should consume the data
```

## Function design policy

Codex must create package-scoped function design before implementation:

```text
requirements/package-runs/P0031/functions.md
```

The function design must document intended functions such as:

```text
open_database(...)
initialize_schema(...)
fetch_open_meteo_range(...)
parse_open_meteo_response(...)
normalize_weather_observation(...)
upsert_weather_observations(...)
compute_area_proxy_hourly(...)
record_weather_ingest_run(...)
get_latest_stored_weather_hour(...)
ingest_daily(...)
validate_weather_continuity(...)
summarize_weather_by_year(...)
export_weather_manifest(...)
render_launchd_plist(...)
install_launchd_plist(...)
load_or_enable_launchd_job(...)
verify_launchd_job(...)
main(argv=None)
```

Codex may choose different names, but equivalent responsibilities must be documented before implementation.

## Context-reset phase gates

Use the standard package phase model:

```text
sync -> bootstrap -> review -> design -> function design -> implementation/data build -> tests -> backfill -> validation -> launchd install -> daily ingest verification -> evidence/changelog
```

Each phase must rely on repository artifacts rather than unwritten chat context.

## Live fetch/debug policy

Live read-only HTTP fetch allowed: yes, if source review passes.

Live device actions allowed: no.

Shelly log capture required: no.

Max implementation/debug attempts: 3.

Codex must stop immediately if the task would require device access, secrets, third-party paid/credentialed API, external Python dependencies, root/system daemon installation, or synthetic gap filling.

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/P0031/
```

Expected evidence files:

```text
CHANGELOG.md
review.md
design.md
functions.md
attempts.md
weather-dataset-manifest-summary.md
launchd-service.md
```

Evidence must include:

- source selected
- source model and update-delay assumption
- fetch/build commands
- validation commands
- date interval achieved
- variables fetched
- locations/weights used
- completeness status
- total row counts
- per-year row counts
- gap summary
- duplicate summary
- null-count summary per variable
- min/max/mean per variable per year where concise
- DB path and DB file size
- launchd plist path
- launchd label
- daily schedule
- launchd installed/enabled proof or WARN/STOP blocker
- manual daily ingest verification result
- rollback/unload commands
- repo-size impact summary
- no secrets and no device access

Do not store large raw HTTP payloads or raw logs in package evidence.

## Test cases

### TC1: Schema initialization

Given an empty SQLite DB
When schema initialization runs
Then all expected tables, indexes and unique constraints exist.

### TC2: Open-Meteo response parsing

Given a small fixture response with all required hourly variables
When parsing runs
Then normalized weather observations are produced for each location/hour.

### TC3: Required variable validation

Given a response missing a required variable
When normalization runs
Then validation fails clearly and no silent partial record is accepted.

### TC4: Timestamp/DST handling

Given normal days and DST transition days
When expected-hour validation runs
Then 23-hour and 25-hour days are handled according to the documented timezone policy.

### TC5: Duplicate detection

Given duplicate location/hour or area/hour records
When validation runs
Then duplicates are reported.

### TC6: Gap detection

Given missing hours
When validation runs
Then gap count and exact ranges are reported.

### TC7: Multi-location weighting

Given observations for configured locations
When area proxy computation runs
Then weighted SE3 hourly rows are produced with coverage count/weight.

### TC8: Variable null counts

Given records with null/missing values
When validation runs
Then null counts per variable are reported and completeness is affected according to design.

### TC9: Idempotent daily ingest

Given data already present for a day
When daily ingest runs again
Then records are upserted without duplicates and ingest metadata is recorded.

### TC10: No-op when no new complete day is available

Given source delay or no missing complete day
When daily ingest runs
Then it exits cleanly with `no_new_complete_day_available` or equivalent status.

### TC11: Launchd plist rendering

Given job parameters
When plist rendering runs
Then label, command, DB path, log paths and daily schedule are correct.

### TC12: User-level launchd only

Given install command
When target path is selected
Then it uses `~/Library/LaunchAgents`, not `/Library/LaunchDaemons`.

### TC13: No-network unit tests

Given unit tests
When tests run
Then parser, validator, schema, weighting and launchd rendering are tested without live HTTP.

### TC14: Optional live backfill/fetch

Given source review passes
When live backfill runs
Then it performs only read-only HTTP requests and writes normalized SQLite rows plus manifest.

### TC15: Production service verification

Given the LaunchAgent is installed
When verification runs
Then `launchctl print gui/$(id -u)/se.mlovholm.smart-home.weather-history-daily` succeeds or precise WARN evidence is recorded.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/services/weather_history
python3 -m unittest discover tests/mac/services
python3 -m unittest discover tests/mac/tools
git diff --check
```

Weather-specific command equivalents expected:

```bash
python3 -m src.mac.services.weather_history init-db --db ~/.smart-home/data/weather_history.sqlite3
python3 -m src.mac.services.weather_history backfill --start 2022-05-30 --db ~/.smart-home/data/weather_history.sqlite3
python3 -m src.mac.services.weather_history validate --db ~/.smart-home/data/weather_history.sqlite3
python3 -m src.mac.services.weather_history install-daily-job --db ~/.smart-home/data/weather_history.sqlite3
python3 -m src.mac.services.weather_history ingest-daily --db ~/.smart-home/data/weather_history.sqlite3
launchctl print gui/$(id -u)/se.mlovholm.smart-home.weather-history-daily
```

If actual command names differ, document the equivalents in design and attempts.

## Runtime health checks

For dataset validation and service verification, record:

- source
- source model
- date interval
- locations/weights
- total raw observation rows
- total SE3 proxy rows
- expected records
- complete true/false
- gaps count
- duplicate count
- null-count summary
- per-year summaries
- DB path
- DB file size
- launchd label
- launchd plist path
- launchd schedule
- launchd installed/enabled status
- manual ingest status
- rollback commands

No device/runtime health checks are required because P0031 is Mac-side weather-data-only.

## Deployment plan

P0031 productionizes the local Mac weather history ingest service.

Deployment means:

```text
- local SQLite database created/backfilled
- user-level LaunchAgent installed/enabled
- daily ingest scheduled
```

No network service, Home Assistant integration, Shelly deploy or device runtime change is part of P0031.

## Rollback plan

Codex must document rollback commands, including:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
rm ~/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
```

Codex must also document how to preserve or remove the local database:

```text
~/.smart-home/data/weather_history.sqlite3
```

Rollback is otherwise a new forward-moving package if the dataset shape is wrong.

## Expected Codex output

- consistency review result: PASS/WARN/STOP
- Open-Meteo source and model selected
- design path
- functions path
- files changed
- DB path
- locations/weights
- variables fetched
- backfill result
- first/last timestamp in DB
- completeness status and gap summary
- validation results
- daily ingest result
- launchd plist path
- launchd label
- proof that job is installed/enabled or exact WARN/STOP blocker
- daily schedule chosen and reason
- tests run
- repo-size impact
- rollback/unload commands
- uncertainty / skipped checks
- commit SHA after push, if successful and pushed
- diff summary

## Completion notes

To be filled after implementation.
