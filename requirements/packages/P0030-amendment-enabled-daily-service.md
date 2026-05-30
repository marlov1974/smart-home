# P0030 amendment: Enabled daily spotprice history service

## Status

planned amendment to P0030

## Applies to

```text
requirements/packages/P0030-historical-spotprice-dataset-foundation.md
requirements/packages/P0030-amendment-daily-ingest-and-storage.md
```

This amendment supersedes the earlier cautious scheduling default in `P0030-amendment-daily-ingest-and-storage.md`.

## User clarification

The package should be more complete when Codex finishes.

When P0030 is complete, the Mac should have:

```text
1. historical SE3 spotprice data backfilled into the local database
2. a daily local service/job installed and enabled
3. the job scheduled to fetch new spotprice data every day at 14:00 local time
```

P0030 should still not implement ML, weather normalization, optimizer changes, Shelly runtime changes, Home Assistant integration, or device control.

## Scheduling decision override

Replace the earlier default:

```text
Implement the ingest command and provide a documented launchd template, but do not install/enable a persistent job automatically.
```

with:

```text
Implement, install and enable a user-level launchd job during P0030 verification, unless Codex finds a concrete safety/repo-policy blocker and records WARN/STOP evidence.
```

The target schedule is:

```text
every day at 14:00 local Mac time
```

Rationale:

- Spotprice data for the next/current complete day is generally not a midnight artifact.
- 14:00 is the required operator-selected daily ingest time for this project.
- The history database should stay current without manual daily commands.

## Launchd/service requirements

Codex must create a user-level launchd job for the Mac, not a system-wide root daemon.

Expected label, unless design chooses a better repo-consistent name:

```text
se.mlovholm.smart-home.spotprice-history-daily
```

Expected command target:

```bash
python3 -m src.mac.services.spotprice_history ingest-daily --area SE3 --db ~/.smart-home/data/spotprice_history.sqlite3
```

The job must run from the smart-home repo root or through a wrapper that sets the repo root explicitly.

The launchd plist must include or equivalent:

```text
StartCalendarInterval Hour=14 Minute=0
StandardOutPath ~/.smart-home/logs/spotprice-history-daily.out.log
StandardErrorPath ~/.smart-home/logs/spotprice-history-daily.err.log
WorkingDirectory <smart-home repo root>
```

Codex must create needed local directories, for example:

```text
~/.smart-home/data
~/.smart-home/logs
```

## Installation requirements

P0030 must include Mac-side install/enable/verify behavior for the launchd job.

Codex must:

1. create or render the launchd plist
2. install it to the correct user LaunchAgents location, normally:

```text
~/Library/LaunchAgents/se.mlovholm.smart-home.spotprice-history-daily.plist
```

3. load/bootstrap/enable the job using the current macOS-supported `launchctl` flow
4. run a manual kickstart or direct ingest verification so evidence proves the command works
5. verify that launchd lists the job or otherwise records a precise warning/error
6. document exact unload/disable rollback commands

If user-level launchd cannot be installed or verified in the Codex sandbox, Codex must still create the plist/template and exact install command, then mark the install phase `WARN` with the blocker. But the intended package outcome is an enabled daily job.

## Backfill completion requirement

P0030 must not stop after creating schema/code only.

It must backfill the local database used by the service:

```text
~/.smart-home/data/spotprice_history.sqlite3
```

from:

```text
2022-05-30
```

to:

```text
latest safely available actual 2026 spotprice data at build time
```

It must then validate the database and record:

```text
- first timestamp
- last timestamp
- total row count
- expected row count
- complete true/false
- gap count and gap ranges if any
- duplicate count
- negative-price count
- yearly min/max/mean
- database file size
```

If the backfill cannot complete with continuous data, Codex must `WARN` or `STOP`; it must not silently install a daily job over a known-bad or incomplete database without clearly recording that status.

## Daily job behavior requirements

The daily job must be idempotent and safe if run multiple times.

At 14:00 each day it should:

1. open the configured SQLite database
2. determine missing/latest actual day or hour
3. fetch only missing available actual data
4. upsert rows by unique area+timestamp key
5. record an ingest run row
6. validate the tail and update/export the manifest summary
7. exit with success if no new complete day is available yet, but record a clear `no_new_complete_day_available` status
8. never synthesize prices or hide gaps

## Repository artifacts required

P0030 must commit the durable implementation artifacts, not the operator-specific generated database unless explicitly justified.

Expected repo artifacts:

```text
src/mac/services/spotprice_history/**
tests/mac/services/spotprice_history/**
docs/functions/mac/spotprice-history-dataset.md
docs/functions/00-index.md
requirements/package-runs/P0030/**
requirements/packages/P0030-historical-spotprice-dataset-foundation.md
requirements/packages/P0030-amendment-daily-ingest-and-storage.md
requirements/packages/P0030-amendment-enabled-daily-service.md
```

Expected local Mac artifacts after verification:

```text
~/.smart-home/data/spotprice_history.sqlite3
~/.smart-home/logs/spotprice-history-daily.out.log
~/.smart-home/logs/spotprice-history-daily.err.log
~/Library/LaunchAgents/se.mlovholm.smart-home.spotprice-history-daily.plist
```

The full generated SQLite database normally stays local and is not committed to repo.

## Safety constraints

This amendment permits a user-level Mac launchd job for the spotprice history daily ingest only.

It still forbids:

```text
- ML training
- weather normalization
- optimizer/control changes
- Shelly deploy
- Shelly RPC/KVS writes
- Home Assistant integration
- actuator/device access
- synthetic gap filling
- external Python dependencies without STOP/approval
- system-wide/root launch daemon installation
- public network service exposure
```

## Additional design requirements

`requirements/package-runs/P0030/design.md` must now include:

```text
- launchd label
- launchd plist path
- local database path
- local log paths
- daily schedule set to 14:00 local time
- install/load/enable command plan
- verification plan for launchd visibility
- rollback/unload commands
- behavior if daily ingest runs before source has new complete data
```

## Additional function requirements

`requirements/package-runs/P0030/functions.md` must include functions or equivalents for:

```text
render_launchd_plist(...)
install_launchd_plist(...)
load_or_enable_launchd_job(...)
verify_launchd_job(...)
print_rollback_commands(...)
```

If Codex implements installation as a documented CLI subcommand rather than direct function names, the equivalent responsibilities must be documented.

## Additional test cases

Add tests or evidence for:

```text
TC17: launchd plist renders expected label and 14:00 StartCalendarInterval
TC18: launchd plist uses user-level paths, not root/system daemon paths
TC19: install command refuses to target system LaunchDaemons
TC20: daily ingest command remains idempotent under repeated launchd-style execution
```

## Additional verification commands

Codex must define exact commands in design/attempts, but expected equivalents are:

```bash
python3 -m src.mac.services.spotprice_history backfill --start 2022-05-30 --area SE3 --db ~/.smart-home/data/spotprice_history.sqlite3
python3 -m src.mac.services.spotprice_history validate --db ~/.smart-home/data/spotprice_history.sqlite3
python3 -m src.mac.services.spotprice_history install-daily-job --area SE3 --db ~/.smart-home/data/spotprice_history.sqlite3 --hour 14 --minute 0
python3 -m src.mac.services.spotprice_history ingest-daily --area SE3 --db ~/.smart-home/data/spotprice_history.sqlite3
launchctl print gui/$(id -u)/se.mlovholm.smart-home.spotprice-history-daily
```

If actual command names differ, document the equivalents.

## Expected Codex output added

Codex final output must include:

```text
- historical database path
- whether historical backfill completed
- first/last timestamp in DB
- completeness status and gap summary
- launchd plist path
- launchd label
- proof that the job is installed/enabled or exact WARN/STOP blocker
- daily schedule: 14:00 local time
- manual ingest result
- rollback/unload commands
- confirmation that no ML/weather/Shelly/device work was performed
```
