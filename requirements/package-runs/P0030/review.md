# P0030 review

## Classification

PASS

## Package interpretation

P0030 creates the Mac-side historical spot price foundation for SE3 and upgrades the existing compact spot period-index API so it uses the full local SQLite history instead of the old committed winter fixture.

The package amendments are part of the active scope:

- SQLite is the canonical mutable local store at `~/.smart-home/data/spotprice_history.sqlite3`.
- Daily ingest is idempotent and stores only complete actual days/hours.
- A user-level launchd job should be installed and enabled at 14:00 local time if the Mac sandbox permits it.
- The existing `src.mac.services.spot_forecast` API must default to the SQLite dataset and fail clearly if the DB is missing or incomplete.

## Consistency review

The package is consistent with repository state:

- Existing P0017 spot forecast code uses `data/spot/spotprices-2025-winter-8h-weekly-period-index.json`, so P0030 needs a real source migration.
- Existing P0024/P0025 weekly optimizer code uses a separate 2025 hourly actual-price fixture and does not provide a durable full-history store.
- `data/spot/README.md` documents fixture-only 2025 data, not canonical history.
- P0030 is Mac-only and does not require Shelly, Home Assistant or actuator writes.

## Source evidence

Read-only HTTP checks on 2026-05-30:

- `https://se.elpris.eu/api/v1/prices/2026/05-29_SE3.json?avg24` returned compact 24-hour SEK values.
- `https://se.elpris.eu/api/v1/prices/2022/05-30_SE3.json?avg24` returned HTTP 410, so `se.elpris.eu?avg24` cannot be the full backfill source for the requested range.
- `https://www.elprisetjustnu.se/api/v1/prices/2022/05-30_SE3.json` returned 24 hourly records.
- `https://www.elprisetjustnu.se/api/v1/prices/2026/05-29_SE3.json` returned 96 quarter-hour records.

Implementation should therefore support both:

- direct Elprisetjustnu object-list responses with `time_start`, `time_end`, `SEK_per_kWh`, `EUR_per_kWh`, `EXR`;
- compact `se.elpris.eu?avg24` responses as a future-friendly read path, but not as the sole historical source.

Quarter-hour days must be aggregated to hourly rows by local hour start. Older hourly days can be stored directly.

## Assumptions

- `latest safely available actual` means the latest fully completed local date that the source returns with all expected hours. On 2026-05-30 this is expected to be no later than 2026-05-29.
- Negative prices are valid observations and must be reported, not rejected.
- The repo should commit code, tests and docs, but not the mutable full SQLite DB.
- Installing the user LaunchAgent writes outside the repository and may require explicit sandbox escalation.

## Safety

No device writes, Shelly calls, Home Assistant calls, KVS writes, Script calls, relay/dimmer/cover/switch/light calls, shell tool exposure or generic proxy behavior are in scope.
