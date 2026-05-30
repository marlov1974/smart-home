# P0030 amendment: Spot index API must use full historical dataset

## Status

planned amendment to P0030

## Applies to

```text
requirements/packages/P0030-historical-spotprice-dataset-foundation.md
requirements/packages/P0030-amendment-daily-ingest-and-storage.md
requirements/packages/P0030-amendment-enabled-daily-service.md
```

This amendment is part of P0030 scope and must be read by Codex together with the other P0030 package files before P0030 review/design/implementation.

## User clarification

The project already has a Mac-side API that returns an index curve derived from historical spotprice data using a simple statistical / ML-light model.

P0030 must update that existing API so it uses the full historical dataset/database established by P0030, rather than continuing to use older limited fixtures or partial history.

This is still not the future full ML model. It is the required data-source upgrade for the existing index API.

## Added decision summary

P0030 must now deliver four connected outcomes:

```text
1. historical SE3 hourly spotprice database backfilled from 2022-05-30
2. enabled daily Mac launchd ingest job at 14:00 local time
3. validation/manifest proving database completeness or explicit WARN/STOP if incomplete
4. existing spot index API updated to read from the new full SQLite dataset
```

The existing statistical/ML-light index logic may remain simple in P0030, but its input must become the complete P0030 dataset.

## Existing API to inspect

Codex must locate and inspect the current spot index API, expected from prior function docs as:

```text
src.mac.services.spot_forecast
GET /spot/period-index?week=WW
```

Durable function doc to inspect:

```text
docs/functions/mac/spot-forecast.md
```

Codex must also inspect P0024/P0025 weekly optimizer evidence/code because those packages reportedly added actual-price fixture loading, hourly spot planning, fixed known horizon and forecast-vs-actual diagnostics.

## Required API behavior change

The current API that returns an index curve must use the P0030 SQLite history database as its canonical historical input.

Expected default DB path:

```text
~/.smart-home/data/spotprice_history.sqlite3
```

The API must not require the full database to be committed to repo. It should load from local DB by default and support an explicit `--db` option or equivalent config override for tests and development.

If the DB is missing or incomplete, the API must fail clearly with a structured error rather than silently falling back to stale limited fixtures.

## Model scope for P0030

Allowed:

- keep the existing simple statistical / ML-light index algorithm if it remains valid
- refactor it so historical input comes from SQLite
- recompute week/period/day-profile indexes from all available validated history
- add source metadata showing database coverage used
- add diagnostics comparing old fixture-based output vs new full-history output if useful

Not allowed in P0030:

- full ML model training
- weather normalization
- learned model artifacts
- optimizer policy changes
- heating/FTX control changes
- Shelly runtime changes

## API contract requirements

The spot index API must expose enough metadata for future debugging and model evolution.

For the existing endpoint, or a package-compatible extension, response should include or be able to provide:

```text
- index curve values
- area
- requested week or period selector
- source: sqlite history database
- database first timestamp
- database last timestamp
- number of historical hours/records used
- completeness status
- model/version identifier for the simple statistical method
```

If the existing compact API contract must remain a bare array for current consumers, Codex may preserve it and add a separate metadata endpoint or CLI diagnostic command, but this tradeoff must be documented in design.

## Design requirements added

`requirements/package-runs/P0030/design.md` must include:

```text
- current spot index API location and behavior
- current historical input source/fixture
- new SQLite input path/config model
- how the API handles missing/incomplete DB
- whether existing response contract remains bare array or gains metadata
- how all available history is selected and weighted
- how partial 2026 is included without bias or with documented weighting
- how daily ingest updates become visible to the API
- backward compatibility for existing weekly optimizer consumers
- tests comparing mocked DB input to expected index output
```

## Function requirements added

`requirements/package-runs/P0030/functions.md` must include functions or equivalent responsibilities for:

```text
load_history_from_database(...)
select_history_for_period_index(...)
compute_index_curve_from_history(...)
build_spot_index_response(...)
handle_missing_or_incomplete_history_db(...)
```

If existing function names are reused, document the before/after behavior.

## Test cases added

Add or update tests for:

```text
TC21: spot index API reads history from SQLite, not legacy fixture, when DB is available
TC22: spot index API fails clearly when DB is missing
TC23: spot index API fails or reports incomplete when DB has validation gaps
TC24: spot index API output changes when DB history changes, proving it uses the database
TC25: existing endpoint backward compatibility is preserved or migration is explicitly documented
TC26: response or diagnostic metadata reports DB coverage and model/version
TC27: daily ingest/upserted records are visible to subsequent index API computation
```

## Verification added

After backfill and daily ingest verification, Codex must verify the index API against the populated P0030 database.

Expected command equivalents:

```bash
python3 -m src.mac.services.spot_forecast --once --week 2 --db ~/.smart-home/data/spotprice_history.sqlite3
python3 -m src.mac.services.spot_forecast --host 127.0.0.1 --port 8080 --db ~/.smart-home/data/spotprice_history.sqlite3
curl 'http://127.0.0.1:8080/spot/period-index?week=2'
```

If actual commands differ, document the equivalents in design and attempts.

Verification evidence must include:

```text
- API command run
- DB path used
- DB first/last timestamp
- number of rows used by index computation
- output length/shape
- whether metadata is available and where
- proof that legacy fixture was not the data source for this verification
```

## Documentation updates required

Codex must update:

```text
docs/functions/mac/spot-forecast.md
```

to reflect that the spot index service now reads from the P0030 SQLite historical database, or document a compatibility mode if both old and new paths remain.

If a new durable doc is created for the historical dataset, it must cross-link the spot forecast API as a consumer.

## Safety constraints unchanged

This amendment does not permit:

```text
- full ML training
- weather normalization
- optimizer/control policy changes
- Shelly deploy
- Shelly RPC/KVS writes
- Home Assistant integration
- actuator/device access
- synthetic gap filling
- external Python dependencies without STOP/approval
```

## Expected Codex output added

Codex final output must include:

```text
- current spot index API identified
- whether the API was updated to use SQLite
- DB path used by API verification
- endpoint/CLI verification result
- output shape and metadata availability
- backward-compatibility decision
- confirmation that this remains simple statistical/ML-light, not full ML/weather-normalized training
```
