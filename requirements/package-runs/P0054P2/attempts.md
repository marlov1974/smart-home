# Attempts

## Attempt 1

Command:

```text
PYTHONPYCACHEPREFIX=/private/tmp/p0054p2-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0054p2
```

Result: failed before DB write in sandbox with `sqlite3.OperationalError: attempt to write a readonly database`.

Action: reran with approved escalation because P0054P2 explicitly allows local ENTSO-E actual-load ingestion into the local feature database.

## Attempt 2

Result: fetched and persisted ENTSO-E actual-load rows, then failed during evidence generation because percentile helper was called with `50/5/95` instead of `0.50/0.05/0.95`.

Action: fixed percentile calls and reduced request chunking from monthly to yearly intervals.

## Attempt 3

Result: PASS, but evidence review found old-source comparison used the wrong old table column naming convention and volume evidence used calendar seasons instead of the required winter/summer half-year split.

Action: fixed old-source columns to `consumption_se1`...`consumption_se4`, changed volume evidence to winter/summer half-year, added p25/p75 and daily energy metrics, then regenerated package evidence.

## Final

Result: PASS.

Rows loaded:

```text
raw_rows = 192905
hourly_rows = 140175
```

Canonical table:

```text
entsoe_consumption_area_hourly_v1
```
