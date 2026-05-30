# Package P0030: Historical spotprice dataset foundation

## Status

planned

## Package order

P0030

## Primary area

G2 / Mac tooling / spotprice history / data foundation / future ML input

## Linked requirements

Epic:
- E0001

Features:
- F0001

User stories:
- US0001

## Decision summary

Create a robust Mac-side historical spotprice dataset foundation for future advanced spotprice forecasting and ML work.

P0030 must build the data layer only. It must not implement the future ML algorithm, weather normalization, optimizer changes, Shelly runtime changes, or control-policy changes.

The dataset target is a continuous SE3 hourly actual spotprice series starting:

```text
2022-05-30
```

and ending at the latest safely available actual 2026 spotprice data at build time.

The package must not silently accept gaps. If any hour is missing within the expected range, the dataset must be marked incomplete and the package must WARN or STOP according to the design. P0030 must not fill gaps synthetically; interpolation/imputation belongs to later ML/weather-normalization packages.

## Context and rationale

The project is expected to evolve toward an advanced Mac-side ML price algorithm using weather normalization, seasonal patterns, weekday/weekend behavior, intraday profiles, forecast-vs-actual diagnostics and later optimizer integration.

That future work requires a clean, reproducible actual-price history first.

Existing repository context:

- P0013 established the Shelly low-memory spotprice runtime using `se.elpris.eu`, SE3, 12 two-hour values and the current Shelly KVS spotprice contract.
- `docs/functions/mac/spot-forecast.md` documents the Mac `spot_forecast` service that produces compact period indexes.
- P0024/P0025 extended weekly optimizer work with hourly spot planning, actual-price fixture loading, forecast-sum-preserving actual-price patching, fixed known-horizon planning and forecast-vs-actual diagnostics.

P0030 must build from that context but remain a data-foundation package.

## Current behavior

The repository has Mac-side spot forecast and weekly optimizer components, but the durable dataset layer for a continuous 2022-05-30 through 2026 historical hourly SE3 spotprice series is not yet established as a package-scoped contract.

## Problem

Future ML/weather-normalized spotprice algorithms need a reliable historical actual-price dataset. Without an explicit dataset builder, schema, validation and manifest, later model work may be based on partial, implicit or non-reproducible data.

P0030 must establish:

- source selection
- normalized schema
- fixture/storage convention
- validation rules
- completeness/gap reporting
- dataset manifest
- reproducible build command

## Target behavior

Build Mac-side tooling and data artifacts that can create and validate a historical SE3 spotprice dataset.

Required date range:

```text
start: 2022-05-30
end:   latest safely available actual 2026 spotprice data at build time
```

Required data scope:

```text
price area: SE3 by default
resolution: hourly actual spot price
```

Required years/segments:

```text
2022-05-30 through 2022-12-31
all of 2023
all of 2024
all of 2025
2026 through latest safely available actual data
```

The dataset must be continuous hour-by-hour under the chosen time-zone/DST policy. The package must explicitly handle 23-hour and 25-hour DST days.

## Dataset schema requirements

Codex must choose the exact on-disk format in `requirements/package-runs/P0030/design.md`, but the normalized record schema must support these fields or equivalents:

```text
timestamp or local date-hour
date
hour
price_area
raw spot price
currency/unit
source
dataset_build_at or fetched_at
```

The schema should be stable enough for future ML/weather-normalization packages.

## Completeness and validation requirements

P0030 must validate and report:

- first timestamp
- last timestamp
- total record count
- record count per year
- expected hour count per year/segment under DST policy
- duplicate records per area/hour
- missing hours/gaps
- negative-price count per year
- min/max/mean spot price per year
- source and build/fetch timestamp
- dataset completeness status

Completeness rule:

```text
complete=true only if no gaps exist from 2022-05-30 through the selected end timestamp.
```

If gaps exist:

- do not fill them synthetically
- record exact missing date/hour ranges in the manifest/evidence
- mark dataset status incomplete
- classify the package `WARN` or `STOP` depending on whether a useful partial artifact is intentionally committed

Outlier rule:

- negative prices are valid spot market values and must not be dropped
- extreme outliers must be summarized but not removed without a later explicit package rule

## Source policy

Preferred approach:

- inspect existing repository spotprice fixtures/data first
- reuse established source conventions if suitable
- consider `se.elpris.eu` because P0013 already uses it, but verify whether it supports reliable historical hourly data back to 2022-05-30

Allowed:

- read-only HTTP fetches for public price data
- deterministic local normalization/validation
- compact committed fixtures if repository-size impact is acceptable

Forbidden or STOP/WARN conditions:

- unclear source/license
- source cannot provide continuous data from 2022-05-30
- data would be unreasonably large for repo
- external Python dependency is required
- source requires secrets or account credentials
- only raw large API dumps are available and no compact normalized representation is designed

## Expected format

Codex must decide in design. Acceptable examples:

```text
JSONL per year
compact CSV per year
small normalized JSON manifest plus compact annual records
```

Avoid:

- huge raw dumps
- binary formats that are difficult to diff/review
- formats requiring external Python packages
- opaque compressed blobs unless explicitly justified by repo-size constraints and documented reader tests

## Non-goals

- No ML model.
- No model training.
- No weather normalization.
- No forecast algorithm change.
- No optimizer/control algorithm change.
- No Shelly `spotprice_v0_9_0` change.
- No Shelly deploy.
- No KVS writes.
- No Home Assistant integration.
- No FTX/heating-control policy.
- No MCP/tunnel work.
- No live device access.
- No synthetic gap filling, interpolation or imputation.

## Invariants

- Mac-side only.
- Python standard library only unless Codex stops for an explicit dependency decision.
- Read-only HTTP only if fetching is required.
- No device writes.
- No Shelly RPC calls.
- No actuator/output/switch/cover/relay actions.
- No secrets.
- Dataset build and validation must be reproducible.
- Unit tests must be able to run without network access.
- Live fetch, if used, must be separately documented as read-only.

## Knowledge updates

Create or update if durable:

- `docs/functions/mac/spotprice-history-dataset.md`
- `docs/functions/00-index.md`

Update only if a durable lesson is discovered:

- `docs/functions/mac/spot-forecast.md`
- `memory/device-management/mac-layer.md`
- `memory/knowhow/codex.md`
- `memory/knowhow/shelly.md`

Do not update Shelly runtime documentation unless this package discovers a durable cross-package spotprice data contract that Shelly later needs to consume. P0030 itself must not change Shelly runtime behavior.

## Implementation updates

Expected areas, final paths to be chosen in design:

- `src/mac/services/spotprice_history/**` or equivalent Mac-side data builder/validator path
- `tests/mac/services/spotprice_history/**` or equivalent test path
- a compact fixture/data path selected by design, for example under a repo-existing fixture convention
- `docs/functions/mac/spotprice-history-dataset.md`
- `docs/functions/00-index.md`
- `requirements/package-runs/P0030/**`
- `requirements/packages/P0030-historical-spotprice-dataset-foundation.md`

Codex must inspect existing data/test conventions before choosing paths.

## Files to inspect

- `README.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/08-context-bootstrap-modes.md`
- `memory/device-management/mac-layer.md`
- `memory/knowhow/shelly.md`
- `requirements/packages/P0013-spotprice-low-memory-se-elpris-runtime.md`
- `requirements/package-runs/P0013/**` if present locally
- `docs/functions/mac/spot-forecast.md`
- `docs/functions/mac/weekly-home-optimizer-poc.md`
- existing spot/price/weather/optimizer source and test directories
- existing fixture/data directories and repo-size conventions
- P0024/P0025 package-run evidence if present locally

## Files allowed to change

- `src/mac/services/spotprice_history/**` or equivalent path documented in design
- `tests/mac/services/spotprice_history/**` or equivalent path documented in design
- selected compact historical spotprice fixture/data files documented in design
- selected dataset manifest file documented in design
- `docs/functions/mac/spotprice-history-dataset.md`
- `docs/functions/00-index.md`
- `docs/functions/mac/spot-forecast.md` only if a durable consumer-facing contract changes
- `memory/device-management/mac-layer.md` only for durable Mac data-pipeline pattern documentation discovered by this package
- `memory/knowhow/codex.md` only for reusable lessons discovered during implementation/verification
- `memory/knowhow/shelly.md` only for reusable spotprice-source lessons relevant to future Shelly packages
- `requirements/package-runs/P0030/**`
- `requirements/packages/P0030-historical-spotprice-dataset-foundation.md`

## Forbidden changes

- No G1 repository changes.
- No deploy artifact changes under `dep/s/**`.
- No Home Assistant changes.
- No Shelly runtime script changes.
- No live Shelly calls.
- No KVS writes.
- No actuator/output/switch/cover/relay implementation or calls.
- No FTX/heating-control policy changes.
- No optimizer policy changes beyond optional read-only data-consumer tests if required by existing test structure.
- No ML training or model artifacts.
- No weather normalization implementation.
- No synthetic gap filling/interpolation/imputation.
- No external Python package dependencies unless the package stops and asks for a dependency decision.
- No secrets or credentialed data sources.
- No broad refactor outside the minimal P0030 data builder/validator/test/docs scope.

## Pre-implementation consistency review

Before editing implementation/data files, Codex must verify this package against repository truth and classify it as:

- `PASS`: source, format and repo placement are clear; continuous data from 2022-05-30 can be built.
- `WARN`: implementable with documented uncertainty, for example partial 2026 through latest actual data or a useful partial artifact that is explicitly marked incomplete.
- `STOP`: source/license/format is unclear; data has unavoidable gaps from 2022-05-30; dataset would be too large; external dependency is required; or the task would require scope expansion.

Required review checks:

- Identify existing spotprice/actual-price fixture locations.
- Identify existing 2026 data, if any.
- Determine whether 2022-05-30 through current 2026 actual data can be fetched/normalized continuously.
- Determine source license/usage risk at least enough to decide PASS/WARN/STOP.
- Estimate repo-size impact before committing data.
- Confirm no Shelly/device access is required.

Store review evidence in:

```text
requirements/package-runs/P0030/review.md
```

## Implementation design policy

Codex must create package-scoped implementation design before coding/fetching substantial data:

```text
requirements/package-runs/P0030/design.md
```

The design must document:

```text
- chosen source
- source URL/API pattern
- exact date interval
- price area
- timezone/DST policy
- file format
- schema version
- repository data path
- estimated file size
- fetch/rebuild command
- validation command
- gap detection model
- duplicate detection model
- annual summary model
- handling of partial 2026
- why no ML/weather-normalization is implemented in P0030
- how future ML/weather-normalization can consume the data
```

## Function design policy

Codex must create package-scoped function design before implementation:

```text
requirements/package-runs/P0030/functions.md
```

The function design must document intended functions such as:

```text
fetch_spotprice_range(...)
parse_source_record(...)
normalize_hourly_record(...)
write_dataset_files(...)
load_dataset(...)
validate_continuity(...)
detect_duplicates(...)
summarize_by_year(...)
write_dataset_manifest(...)
main(argv=None)
```

Codex may choose different names, but equivalent responsibilities must be documented before implementation.

Update durable function documentation under `docs/functions/mac/spotprice-history-dataset.md` after implementation.

## Context-reset phase gates

Use the standard package phase model:

```text
sync -> bootstrap -> review -> design -> function design -> implementation/data build -> tests -> validation -> evidence/changelog
```

Each phase must rely on repository artifacts rather than unwritten chat context.

## Live fetch/debug policy

Live read-only HTTP fetch allowed: yes, if source review passes.

Live device actions allowed: no.

Shelly log capture required: no.

Max implementation/debug attempts: 3.

Codex must stop immediately if the task would require device access, secrets, third-party paid/credentialed API, external Python dependencies, or synthetic gap filling.

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/P0030/
```

Expected evidence files:

```text
CHANGELOG.md
review.md
design.md
functions.md
attempts.md
dataset-manifest-summary.md
```

Evidence must include:

- source selected
- fetch/build commands
- validation commands
- date interval achieved
- completeness status
- total record counts
- per-year record counts
- gap summary
- duplicate summary
- negative-price summary
- min/max/mean per year
- repo-size impact summary
- whether 2026 is partial and through what date/hour
- no secrets and no device access

Do not store large raw logs in package evidence.

## Test cases

### TC1: Schema validation

Given normalized records
When schema validation runs
Then required fields exist and types/units are valid.

### TC2: Timestamp parsing and ordering

Given source records around normal days and DST days
When normalization runs
Then timestamps are ordered and represented consistently under the chosen time-zone policy.

### TC3: DST day handling

Given DST transition days
When expected-hour validation runs
Then 23-hour and 25-hour days are accepted only where appropriate.

### TC4: Duplicate detection

Given duplicate records for the same area/hour
When validation runs
Then duplicates are reported and completeness cannot be silently marked clean.

### TC5: Missing-hour/gap detection

Given a dataset missing one or more expected hours
When validation runs
Then gap count and exact missing ranges are reported.

### TC6: Completeness status

Given a continuous dataset from 2022-05-30 through the selected end timestamp
When validation runs
Then `complete=true`.

Given any missing expected hour
When validation runs
Then `complete=false` or package STOP/WARN evidence is produced.

### TC7: Negative prices preserved

Given negative spot prices
When normalization/validation runs
Then records are preserved and yearly negative counts are reported.

### TC8: Yearly summary generation

Given valid records spanning multiple years
When summary generation runs
Then per-year count, min, max, mean and negative count are produced.

### TC9: No-network unit tests

Given unit tests
When tests run
Then normalizer/validator behavior is verified without live HTTP.

### TC10: Optional read-only live fetch

Given source review passes
When live fetch/build runs
Then it performs only read-only HTTP requests and writes normalized compact dataset files plus manifest.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/services/spotprice_history
python3 -m unittest discover tests/mac/services
python3 -m unittest discover tests/mac/tools
git diff --check
```

Dataset-specific commands must also be documented and run, for example:

```bash
python3 -m src.mac.services.spotprice_history build --start 2022-05-30 --area SE3
python3 -m src.mac.services.spotprice_history validate
```

If paths/commands differ, document the equivalents in design and attempts.

## Runtime health checks

For dataset validation, record:

- source
- area
- start date
- end date/hour
- total records
- expected records
- complete true/false
- gaps count
- duplicates count
- negative count
- per-year summaries
- build timestamp
- file paths
- file sizes

No device/runtime health checks are required because P0030 is Mac-side data-only.

## Deployment plan

No production deployment.

P0030 creates a Mac-side historical dataset and supporting builder/validator. Future packages may consume it for ML/weather-normalized forecasting, but P0030 itself must not deploy or schedule anything.

## Rollback plan

Rollback is a new forward-moving package if the dataset shape is wrong.

If implementation fails validation after allowed attempts, Codex must preserve useful package-run evidence and revert unverified source/data/test/doc changes unless the package evidence explicitly says a partial documentation-only finding should remain.

## Expected Codex output

- consistency review result: PASS/WARN/STOP
- source selected and license/usage note
- design path
- functions path
- files changed
- dataset files created/updated
- dataset manifest path
- tests run
- validation results
- completeness status
- date interval achieved
- gap summary
- duplicate summary
- negative-price summary
- repo-size impact
- uncertainty / skipped checks
- commit SHA after push, if successful and pushed
- diff summary

## Completion notes

To be filled after implementation.
