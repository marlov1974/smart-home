# P0054W operator clarification: complete fetch, not half step

## Status

clarification for P0054W

## Operator intent

The operator wants complete packages, not repeated half-steps that spend tokens without producing the dataset.

For P0054W, the goal is not only to discover that SE3 MGA consumption exists. The goal is:

```text
1. run a small preflight/test fetch
2. if the preflight passes, fetch and load all SE3 MGA consumption data from 2022-06-01 onward
3. store it in the local database with native resolution and settlement class preserved
```

It is acceptable if the Mac runs for one or several hours. Runtime alone is not a valid reason to stop after preflight.

## Required behavior

Codex must treat the preflight as a safety gate only.

```text
preflight passes -> continue to full SE3 MGA load
preflight fails  -> STOP/WARN with exact reason
```

A package result that only performs discovery or a tiny preflight sample is incomplete unless the full fetch is impossible for a concrete reason.

## Concrete acceptable stop reasons

Codex may stop before full load only for one of these reasons:

```text
- no eSett/NBS MGA consumption source exists or can be located
- access/credentials are missing
- source terms or local config explicitly prevent download
- source returns errors that prevent continued fetching
- schema cannot be classified safely enough to preserve settlement class/resolution
- database write/upsert fails
- disk space is insufficient
- process is interrupted after checkpointing progress
```

Do not stop merely because:

```text
- there are many MGAs
- the date range starts 2022-06-01
- 15m data creates many rows
- estimated runtime is high but manageable
- the fetch takes an hour or more
```

## Required full-fetch workflow

After preflight passes, run the full load:

```text
1. identify all SE3 MGAs
2. create/check DB schema
3. create/check ingestion checkpoint
4. fetch all SE3 MGAs from 2022-06-01 onward
5. load native rows incrementally
6. preserve resolution_minutes and settlement_class
7. run post-load row counts and min/max timestamps
8. run SE3 volume sanity check if mapping/units allow
9. write final evidence
```

## Runtime and resume policy

The full load should be resumable, but resumability is not a substitute for actually starting and continuing the full load.

If the run is interrupted after real progress, Codex must return WARN with:

```text
loaded_mga_count
loaded_period_count
loaded_row_count
remaining_mga_count
remaining_period_count
checkpoint_location
exact_resume_command
```

If Codex finishes the full load, return PASS/WARN depending on data quality.

## Token-efficiency rule

Codex should avoid creating new requirement-only packages unless the current package is truly blocked.

For P0054W, prefer implementing the full fetch/load in the same package run rather than returning another planning package.

## Evidence requirements

P0054W must include:

```text
requirements/package-runs/P0054W/preflight-fetch-results.md
requirements/package-runs/P0054W/full-fetch-progress.md
requirements/package-runs/P0054W/database-load-evidence.md
requirements/package-runs/P0054W/resume-instructions.md
```

`full-fetch-progress.md` must not be empty. It must show either completed full load or real checkpointed progress with a resume command.

## Relationship to main package

This clarification strengthens and amends:

```text
requirements/packages/P0054W-labb-esett-mga-consumption-discovery.md
requirements/packages/P0054W-operator-clarification-heavy-se3-mga-fetch.md
```

If there is any conflict, follow this clarification.
