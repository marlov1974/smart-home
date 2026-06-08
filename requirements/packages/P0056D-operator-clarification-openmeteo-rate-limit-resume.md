# P0056D operator clarification: Open-Meteo rate-limit resume

## Status

clarification for P0056D

## Problem

The P0056D Open-Meteo historical weather fetch hit archive rate limits before the weather dataset was complete.

This is not a forecast-method failure. It is a data-fetch runtime condition.

P0056D must continue from checkpoint/resume instead of restarting from scratch or treating the package as failed.

## Required knowhow

Before continuing P0056D, Codex must read and follow:

```text
memory/knowhow/openmeteo-archive-rate-limit-resume.md
```

If that file is missing, STOP and report the missing file.

## Required resume behavior

Codex must:

```text
1. inspect already loaded Open-Meteo location-period rows
2. identify only missing location-period chunks
3. fetch only missing chunks
4. write progress after every completed chunk
5. use conservative request pacing
6. use backoff on rate-limit responses
7. never delete already fetched weather rows because a later fetch fails
8. resume until all required P0056D weather zones are complete
```

## Fetch chunking

Use small chunks if rate limits were hit.

Preferred:

```text
one representative location at a time
one month or one quarter at a time
```

Codex may use larger chunks only if the knowhow file says it is safe.

## Checkpoint evidence

Create or update:

```text
requirements/package-runs/P0056D/openmeteo-fetch-checkpoint.md
requirements/package-runs/P0056D/openmeteo-fetch-progress.md
requirements/package-runs/P0056D/openmeteo-resume-instructions.md
```

Each checkpoint row should include:

```text
location_id
zone_id
period_start
period_end
status: pending/running/done/rate_limited/failed
attempt_count
row_count_loaded
last_error
last_attempt_at
next_retry_after_if_known
```

## Rate-limit handling

If Open-Meteo returns rate limit / too many requests / temporary block:

```text
- persist checkpoint immediately
- record exact failed location and period
- wait/back off if runtime allows
- otherwise return WARN with exact resume command
```

Do not classify this as STOP unless repeated retries show the source cannot be accessed at all.

## Forecast retest gating

Do not run the SE1/SE2/FI forecast retest until all required P0056D weather zones are complete, unless clearly labeled as partial sensitivity.

Primary P0056D result requires complete weather coverage for:

```text
SE1 zones
SE2 zones
FI zones
```

## Expected outcome

After resume completes, continue normal P0056D:

```text
1. build revised weighted weather proxies
2. retrain SE1, SE2 and FI
3. test on holdout
4. compare against P0056C baseline
5. decide whether P0056D proxy becomes default candidate per area
```

## Relationship to main package

This clarification strengthens and amends:

```text
requirements/packages/P0056D-labb-se1-se2-fi-openmeteo-weather-proxy-retune.md
```

If there is conflict, follow this clarification and the Open-Meteo knowhow file.
