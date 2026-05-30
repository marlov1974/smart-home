# Package P0032: SE1 system-proxy history

## Status

planned

## Package order

P0032

## Primary area

G2 / Mac tooling / spotprice history / system proxy / area differential / future ML input

## Linked requirements

Epic:
- E0001

Features:
- F0001

User stories:
- US0001

## Decision summary

Use SE1 spotprice as the project-local practical system-price proxy for spotprice V2 modeling.

P0032 must fetch/backfill SE1 hourly spotprice history, store it in the same durable price-storage model as P0030 where possible, and create/query/store derived SE3-vs-SE1 proxy series:

```text
system_proxy_price = SE1 spot price
area_diff_proxy_SE3 = SE3 spot price - SE1 spot price
area_ratio_proxy_SE3 = SE3 spot price / SE1 spot price
```

P0032 must not claim that SE1 is the official Nord Pool system price. It is a practical `system_proxy` for the model until a reliable/licensed true Nordic SYS source is introduced by a later package.

P0032 must be complete when Codex finishes:

```text
1. SE1 spotprice history is backfilled from 2022-05-30 through latest safely available actual data
2. SE1 daily ingest is wired into the existing P0030 spotprice history service/job or a clearly justified companion job
3. derived SE3-vs-SE1 system-proxy series/views are created and validated
4. evidence proves SE1 and SE3 coverage alignment and derived series correctness
```

P0032 is data/service work only. It must not implement the future ML model, weather normalization, optimizer/control changes, Shelly runtime changes, Home Assistant integration, or device control.

## Terminology

Use these terms internally:

```text
system_proxy_price
area_diff_proxy
area_ratio_proxy
```

Do not use these as truth labels:

```text
SYS
EPAD
```

because:

- `SYS` normally means official Nordic system price.
- `EPAD` normally refers to financial area-differential contracts/forwards.
- P0032 creates a realized historical proxy using SE1, not official SYS or traded EPAD data.

Durable definitions:

```text
system_proxy_price(area_proxy=SE1) = hourly SE1 spot price
area_diff_proxy_SE3 = hourly SE3 spot price - hourly SE1 spot price
area_ratio_proxy_SE3 = hourly SE3 spot price / hourly SE1 spot price
```

If SE1 is zero or near zero, ratio handling must be explicit and safe. Codex must define denominator policy in design; suggested default is `NULL`/missing ratio when `abs(SE1) < epsilon` rather than unsafe division.

## Context and rationale

The future spotprice V2 architecture separates price forecasting into components:

```text
- relative curve model
- week/month/year level model
- system-proxy level
- area-differential proxy
- combiner
```

The project first explored official Nordic system price, but a direct open source for true SYS is uncertain. SE1 can serve as a practical system-level proxy because it helps separate broad northern/nordic price level from SE3 local congestion/area premium.

P0030 provides SE3 spotprice history and daily ingest. P0032 extends the same price-history foundation with SE1 and derived SE3-vs-SE1 proxy series.

## Current behavior

P0030 is expected to provide:

```text
~/.smart-home/data/spotprice_history.sqlite3
```

with SE3 hourly spotprice history from 2022-05-30 and a daily ingest job.

Before P0032, the project does not have a durable SE1 system-proxy series or derived SE3-vs-SE1 differential/ratio available for future V2 model features.

## Problem

A future V2 spotprice model should not learn SE3 price as one monolithic series. It needs a practical decomposition:

```text
SE3 = system_proxy + area_diff_proxy
```

Without SE1 history aligned to SE3, the model cannot distinguish broad system-level price movement from SE3-specific area spread behavior.

## Target behavior

Build Mac-side tooling/data changes that can:

1. fetch/backfill SE1 hourly actual spotprice from 2022-05-30 through latest safely available actual data
2. store SE1 in the P0030 spotprice SQLite database if schema supports multi-area storage
3. otherwise extend/migrate the P0030 schema safely or STOP/WARN if incompatible
4. update daily ingest so SE1 stays current together with SE3
5. compute derived SE3-vs-SE1 proxy series
6. expose derived series as SQLite views, materialized tables or deterministic query/export functions as chosen in design
7. validate SE1 continuity and SE1/SE3 timestamp alignment
8. validate derived diff/ratio calculations
9. update docs/evidence for future ML consumption

Expected local DB path:

```text
~/.smart-home/data/spotprice_history.sqlite3
```

Expected source:

```text
same or compatible source used by P0030 for SE3, but area=SE1
```

If P0030 source cannot provide SE1 continuously from 2022-05-30, Codex must STOP/WARN and document blocker.

## Source policy

Preferred:

- reuse P0030 source, fetcher, schema, DB and launchd pattern
- fetch SE1 using the same public/read-only source used for SE3
- avoid introducing a new source if P0030 source supports SE1

Allowed:

- read-only HTTP fetches
- schema migration/views within P0030 spotprice DB
- updating P0030 daily ingest to cover both SE3 and SE1 if safe

Forbidden or STOP/WARN conditions:

- unclear source/license
- source cannot provide SE1 continuously from 2022-05-30
- P0030 DB schema cannot safely support multi-area data and migration is unsafe
- external Python dependency required
- source requires secrets/account credentials
- derived series would hide gaps or synthesize missing values

## Database/storage requirements

P0032 should prefer storing SE1 in the existing P0030 table, e.g.:

```text
spot_prices(area='SE1', ...)
spot_prices(area='SE3', ...)
```

Derived series may be represented as views such as:

```text
spotprice_system_proxy_hourly
```

or equivalent deterministic export/query functions.

Expected derived fields:

```text
timestamp_utc or timestamp_local
local_date
local_hour
se3_price
se1_system_proxy_price
area_diff_proxy_se3
area_ratio_proxy_se3
source_coverage_status
computed_at or build/ingest id
```

If materialized table is chosen, Codex must document update strategy and ensure idempotent recomputation/upsert.

## Daily ingest requirement

P0032 must make SE1 part of ongoing daily price-history maintenance.

Preferred implementation:

```text
extend P0030 ingest-daily so it can ingest configured areas, at least SE3 and SE1, in the same daily job
```

Alternative:

```text
create a companion user-level launchd job for SE1 only
```

Use the preferred implementation unless Codex finds a concrete blocker.

The daily job must:

1. ingest missing latest complete day/hour for SE1
2. keep SE3 ingest behavior intact
3. recompute or make available derived SE3-vs-SE1 proxy series after ingest
4. record ingest metadata per area
5. preserve idempotency
6. not silently hide gaps

If launchd job configuration changes, Codex must back up or document existing plist state, update safely, verify launchd status, and document rollback commands.

## Validation requirements

P0032 must validate and report:

- SE1 first timestamp
- SE1 last timestamp
- SE1 row count
- SE1 expected row count
- SE1 gap count
- SE1 duplicate count
- SE1 negative-price count
- SE1 min/max/mean per year
- SE3-vs-SE1 aligned timestamp count
- missing SE1 for SE3 timestamps
- missing SE3 for SE1 timestamps
- derived diff min/max/mean per year
- derived ratio null count and min/max/mean per year where denominator valid
- DB file size impact
- launchd/daily ingest status

Completeness rule:

```text
SE1 complete=true only if no gaps exist from 2022-05-30 through selected end timestamp.
Derived proxy complete=true only for the intersection where both SE1 and SE3 exist for every expected timestamp in the selected range.
```

If SE1 or derived proxy has gaps:

- do not fill synthetically
- record exact missing ranges
- mark incomplete
- classify WARN/STOP according to design

## API / consumer requirements

P0032 must expose a clear consumer path for future model packages.

At minimum, provide one or more of:

```text
- SQLite view for SE3-vs-SE1 proxy series
- CLI export command for derived proxy data
- documented query contract in docs/functions/mac/spotprice-history-dataset.md
```

Future P0033/P0034 model packages must be able to read:

```text
timestamp
SE3 price
SE1 system proxy price
area_diff_proxy_SE3
area_ratio_proxy_SE3
```

without reimplementing the join logic.

## Non-goals

- No official Nordic SYS implementation.
- No traded EPAD/forward contract data.
- No ML model.
- No model training.
- No weather normalization.
- No forecast algorithm change except exposing new data for later use.
- No optimizer/control algorithm change.
- No Shelly runtime change.
- No Shelly deploy.
- No KVS writes.
- No Home Assistant integration.
- No FTX/heating-control policy.
- No MCP/tunnel work.
- No live device access.
- No synthetic gap filling/interpolation/imputation.
- No external Python dependencies unless Codex stops for explicit dependency decision.

## Invariants

- Mac-side only.
- Python standard library only unless Codex stops for explicit dependency decision.
- Read-only HTTP only if fetching is required.
- No device writes.
- No Shelly RPC calls.
- No actuator/output/switch/cover/relay actions.
- No secrets.
- Use SE1 terminology as `system_proxy`, not true `SYS`.
- Use SE3-SE1 terminology as `area_diff_proxy`, not true `EPAD`.
- Database build and validation must be reproducible.
- Unit tests must run without network access.
- Full local database normally stays out of repo.
- User-level launchd only if job changes are required; no root/system daemon.

## Knowledge updates

Create or update:

- `docs/functions/mac/spotprice-history-dataset.md`
- `docs/functions/00-index.md` if new durable doc/catalog entry is needed

Update if durable cross-package model/data terminology is created:

- `memory/device-management/mac-layer.md`
- `memory/knowhow/codex.md`
- `memory/knowhow/shelly.md` only if a reusable source lesson matters to future Shelly packages

## Implementation updates

Expected areas, final paths to be chosen in design:

- existing `src/mac/services/spotprice_history/**` if P0030 created it
- existing `tests/mac/services/spotprice_history/**`
- optional P0032-specific tests under same service path
- docs for spotprice history dataset consumer query/view
- `requirements/package-runs/P0032/**`
- `requirements/packages/P0032-se1-system-proxy-history.md`

P0032 should avoid creating a second separate price-history service unless P0030 architecture makes extension unsafe.

## Files to inspect

- `README.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/08-context-bootstrap-modes.md`
- `memory/device-management/mac-layer.md`
- `memory/knowhow/codex.md`
- all P0030 package files and amendments
- `requirements/package-runs/P0030/**`
- `docs/functions/mac/spotprice-history-dataset.md` if present
- `src/mac/services/spotprice_history/**`
- `tests/mac/services/spotprice_history/**`
- current launchd plist for P0030 daily spotprice job
- P0031 only for awareness of weather data separation; do not modify weather service unless necessary

## Files allowed to change

- `src/mac/services/spotprice_history/**`
- `tests/mac/services/spotprice_history/**`
- selected launchd plist/template/render code for the existing spotprice history job
- `docs/functions/mac/spotprice-history-dataset.md`
- `docs/functions/00-index.md` if needed
- `memory/device-management/mac-layer.md` only for durable Mac data-service pattern documentation
- `memory/knowhow/codex.md` only for reusable package/service lessons
- `memory/knowhow/shelly.md` only for reusable source lessons
- `requirements/package-runs/P0032/**`
- `requirements/packages/P0032-se1-system-proxy-history.md`

Local Mac artifacts expected after verification:

```text
~/.smart-home/data/spotprice_history.sqlite3
~/Library/LaunchAgents/se.mlovholm.smart-home.spotprice-history-daily.plist
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
- No official SYS claim.
- No traded EPAD/forward data implementation.
- No synthetic gap filling/interpolation/imputation.
- No external Python package dependencies unless the package stops and asks for a dependency decision.
- No secrets or credentialed data sources.
- No root/system launch daemon.
- No public network service exposure.
- No broad refactor outside the minimal P0032 price-history/service/docs scope.

## Pre-implementation consistency review

Before editing implementation/data files, Codex must verify this package against repository truth and classify it as:

- `PASS`: P0030 price-history service/storage is present, SE1 source is available through same/compatible source, DB/schema can support SE1, and daily ingest can be extended safely.
- `WARN`: implementable with documented uncertainty, for example P0030 source supports SE1 but launchd update cannot be fully verified in sandbox.
- `STOP`: source/license/format is unclear, SE1 cannot be fetched continuously from 2022-05-30, P0030 schema cannot safely support multiple areas, daily job extension is unsafe, or task requires scope expansion.

Required review checks:

- P0030 is complete enough locally to extend.
- P0030 DB path and schema are identified.
- P0030 source/API supports SE1.
- SE1 can be fetched continuously from 2022-05-30.
- Existing daily ingest launchd job can be updated or companion job justified.
- Derived SE3-vs-SE1 series can be computed without gaps or hidden missingness.
- No Shelly/device access is required.

Store review evidence in:

```text
requirements/package-runs/P0032/review.md
```

## Implementation design policy

Codex must create package-scoped implementation design before coding/fetching substantial data:

```text
requirements/package-runs/P0032/design.md
```

The design must document:

```text
- P0030 DB schema/path found
- P0030 source and SE1 URL/API pattern
- exact date interval
- terminology: system_proxy vs SYS, area_diff_proxy vs EPAD
- storage model for SE1
- view/table/query model for derived proxy series
- denominator policy for area_ratio_proxy
- backfill command
- daily ingest update strategy
- launchd label/plist changes if any
- validation model for SE1
- validation model for SE3/SE1 alignment
- derived summary model
- rollback plan for any launchd/config changes
- why no ML/weather/optimizer/Shelly work is implemented in P0032
- how future model packages should consume system_proxy/area_diff_proxy
```

## Function design policy

Codex must create package-scoped function design before implementation:

```text
requirements/package-runs/P0032/functions.md
```

The function design must document intended functions such as:

```text
fetch_area_price_range(area='SE1', ...)
backfill_area(...)
ingest_daily_for_areas(...)
create_or_update_system_proxy_view(...)
compute_area_diff_proxy(...)
compute_area_ratio_proxy(...)
validate_area_continuity(...)
validate_area_alignment(...)
summarize_system_proxy(...)
export_system_proxy_manifest(...)
update_spotprice_launchd_job_if_needed(...)
main(argv=None)
```

Codex may choose different names, but equivalent responsibilities must be documented before implementation.

## Context-reset phase gates

Use the standard package phase model:

```text
sync -> bootstrap -> review -> design -> function design -> implementation/data backfill -> tests -> validation -> daily ingest/launchd verification -> evidence/changelog
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
requirements/package-runs/P0032/
```

Expected evidence files:

```text
CHANGELOG.md
review.md
design.md
functions.md
attempts.md
system-proxy-summary.md
launchd-update.md
```

Evidence must include:

- source selected
- fetch/build commands
- validation commands
- date interval achieved
- SE1 completeness status
- SE1 total row count and per-year counts
- SE1 gap/duplicate/negative summaries
- SE3/SE1 alignment summary
- derived diff/ratio summary
- DB path and DB file size impact
- launchd job update or companion job status
- manual daily ingest verification result
- rollback/unload commands if launchd changed
- repo-size impact summary
- no secrets and no device access

Do not store large raw HTTP payloads or raw logs in package evidence.

## Test cases

### TC1: SE1 area fetch parsing

Given a small source fixture for SE1
When parsing runs
Then normalized SE1 records match the P0030 area-price schema.

### TC2: Multi-area schema support

Given an initialized spotprice DB
When SE1 rows are inserted alongside SE3
Then unique constraints allow distinct areas at same timestamp and prevent duplicates within area/timestamp.

### TC3: SE1 continuity validation

Given SE1 rows with no gaps
When validation runs
Then completeness is true.

Given missing SE1 hours
When validation runs
Then exact gaps are reported.

### TC4: SE3/SE1 alignment validation

Given SE3 and SE1 rows
When alignment validation runs
Then matched/missing counts are reported and incomplete intersections are not hidden.

### TC5: Area diff proxy calculation

Given matching SE3 and SE1 prices
When derived series is computed
Then `area_diff_proxy_SE3 = SE3 - SE1`.

### TC6: Area ratio proxy calculation

Given matching SE3 and SE1 prices with valid denominator
When derived series is computed
Then `area_ratio_proxy_SE3 = SE3 / SE1`.

Given zero or near-zero SE1 denominator
Then ratio is NULL/omitted according to design, not unsafe division.

### TC7: Derived view/query updates after ingest

Given newly ingested SE1 rows
When proxy query/view is read
Then the new rows are reflected without manual recomputation unless design explicitly uses materialized tables and runs update.

### TC8: Daily ingest includes SE1

Given daily ingest configured for SE3 and SE1
When ingest runs
Then both areas are attempted and metadata is recorded per area.

### TC9: Launchd update safety

Given existing P0030 LaunchAgent
When P0032 updates or verifies it
Then user-level launchd path/label is preserved and rollback commands are documented.

### TC10: No-network unit tests

Given unit tests
When tests run
Then parsing, DB insertion, derived calculations and validation are tested without live HTTP.

### TC11: Optional live SE1 backfill/fetch

Given source review passes
When live backfill runs
Then it performs only read-only HTTP and writes SE1 rows plus manifest/summary.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/services/spotprice_history
python3 -m unittest discover tests/mac/services
python3 -m unittest discover tests/mac/tools
git diff --check
```

P0032-specific command equivalents expected:

```bash
python3 -m src.mac.services.spotprice_history backfill --start 2022-05-30 --area SE1 --db ~/.smart-home/data/spotprice_history.sqlite3
python3 -m src.mac.services.spotprice_history validate --area SE1 --db ~/.smart-home/data/spotprice_history.sqlite3
python3 -m src.mac.services.spotprice_history validate-system-proxy --area SE3 --proxy-area SE1 --db ~/.smart-home/data/spotprice_history.sqlite3
python3 -m src.mac.services.spotprice_history ingest-daily --areas SE3,SE1 --db ~/.smart-home/data/spotprice_history.sqlite3
launchctl print gui/$(id -u)/se.mlovholm.smart-home.spotprice-history-daily
```

If actual command names differ, document the equivalents in design and attempts.

## Runtime health checks

For dataset/service verification, record:

- source
- date interval
- SE1 total rows
- SE1 expected rows
- SE1 complete true/false
- SE1 gaps count
- SE1 duplicates count
- SE1 negative count
- SE3/SE1 aligned rows
- missing SE1 for SE3 timestamps
- missing SE3 for SE1 timestamps
- derived diff min/max/mean
- derived ratio null/min/max/mean
- DB path
- DB file size impact
- launchd label/plist path/status if changed
- manual ingest status
- rollback commands if launchd changed

No device/runtime health checks are required because P0032 is Mac-side price-data-only.

## Deployment plan

P0032 productionizes SE1 as the system-proxy series in the local Mac price-history database.

Deployment means:

```text
- SE1 backfilled into spotprice DB
- derived SE3-vs-SE1 proxy query/view available
- daily ingest includes SE1 or companion job is installed/verified
```

No network service, Home Assistant integration, Shelly deploy or device runtime change is part of P0032.

## Rollback plan

Codex must document rollback commands/steps, including how to:

- restore previous launchd job if it was changed
- remove/ignore SE1 rows if necessary
- drop derived views/tables if necessary
- preserve the original P0030 SE3 data

Rollback is otherwise a new forward-moving package if the dataset shape is wrong.

## Expected Codex output

- consistency review result: PASS/WARN/STOP
- source selected
- design path
- functions path
- files changed
- DB path
- SE1 backfill result
- first/last SE1 timestamp in DB
- SE1 completeness status and gap summary
- SE3/SE1 alignment summary
- derived system-proxy view/table/query path
- derived diff/ratio summary
- daily ingest update result
- launchd status if changed
- tests run
- repo-size impact
- rollback/unload commands if applicable
- terminology confirmation: SE1 system_proxy, not official SYS; SE3-SE1 area_diff_proxy, not EPAD
- uncertainty / skipped checks
- commit SHA after push, if successful and pushed
- diff summary

## Completion notes

To be filled after implementation.
