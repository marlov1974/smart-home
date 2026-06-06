# P0054W operator clarification: heavy SE3 MGA fetch policy

## Status

clarification for P0054W

## Operator intent

The operator wants P0054W to fetch and load all available MGA consumption data for SE3 from 2022-06-01 onward if eSett/NBS data is accessible.

The operator acknowledges this may be heavy.

Therefore, P0054W must not avoid the fetch merely because it is large. Instead it must implement a safe heavy-fetch policy.

## Required execution policy

If SE3 MGA data is available through approved access, Codex must fetch/load it using a batch, checkpoint and resume design.

Required behavior:

```text
1. discover SE3 MGA list first
2. count/estimate expected request and row volume
3. create ingestion manifest/checkpoint table or file
4. fetch one MGA or small MGA batch at a time
5. fetch time ranges in monthly or quarterly chunks
6. commit data to local DB incrementally
7. record per-MGA/per-period status: pending/running/done/failed/skipped
8. make reruns idempotent and resume from last successful checkpoint
9. throttle requests and retry transient failures
10. never discard completed chunks if a later chunk fails
```

## Suggested chunking

Preferred chunking:

```text
outer loop: MGA
inner loop: month
start: 2022-06-01
end: latest available
```

Alternative if eSett/source is more efficient by date:

```text
outer loop: month
inner loop: MGA batch
```

Codex must document the chosen strategy and why.

## Mandatory preflight before full fetch

Before a full SE3 fetch, run a preflight:

```text
1. fetch metadata/masterdata only
2. identify SE3 MGAs
3. run a tiny sample load for 1-3 MGAs and 1-2 months
4. validate native resolution, settlement class and units
5. validate DB upsert/idempotency
6. estimate total rows and duration
```

If preflight fails, STOP or WARN with exact reason.

If preflight passes, proceed to full SE3 MGA fetch unless runtime or source limits make it impossible in the current Codex run.

## Runtime policy

The full fetch may take a long time. That is acceptable.

Codex must not abort just because the run is heavy. It may stop only for a concrete reason such as:

```text
credentials/access missing
source denies or rate-limits all requests
schema cannot be classified safely
DB write failure
runtime budget exhausted after checkpointed partial progress
```

If runtime budget is exhausted after partial progress, return WARN, not failure, and include:

```text
completed_mga_count
completed_period_count
loaded_row_count
remaining_mga_count
remaining_period_count
resume_command
checkpoint_location
```

## Database checkpointing

If the repo/database supports it, create a checkpoint table such as:

```text
esett_mga_consumption_ingestion_checkpoint_v1
```

Minimum columns:

```text
source_system
mga_id
period_start_utc
period_end_utc
settlement_class nullable
status
attempt_count
row_count_loaded
first_attempt_at_utc
last_attempt_at_utc
last_error nullable
generated_by_package = P0054W
```

If a DB checkpoint table is not practical, use a small committed evidence summary and an uncommitted local working checkpoint. Do not commit large raw data.

## Rate limit and politeness

Codex must use conservative request pacing:

```text
serial by default
small concurrency only if clearly safe
retry with backoff for transient failures
respect source errors and documented rate limits
```

## Data storage rules

Continue to follow P0054W native-storage rules:

```text
native 15m/60m/monthly resolution preserved
settlement_class preserved
unit and value_kind preserved
no silent hourly-only aggregation
no mixing monthly/profiled and measured series without labels
```

## Evidence additions

P0054W must add or include:

```text
requirements/package-runs/P0054W/heavy-fetch-plan.md
requirements/package-runs/P0054W/ingestion-checkpoint-contract.md
requirements/package-runs/P0054W/preflight-fetch-results.md
requirements/package-runs/P0054W/full-fetch-progress.md
requirements/package-runs/P0054W/resume-instructions.md
```

## Relationship to main package

This clarification strengthens and amends:

```text
requirements/packages/P0054W-labb-esett-mga-consumption-discovery.md
```

If there is any conflict, follow this operator clarification.
