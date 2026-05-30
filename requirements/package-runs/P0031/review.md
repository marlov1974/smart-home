# P0031 review

## Classification

PASS

## Repository consistency

P0030 is complete locally and provides the Mac data-service pattern P0031 should follow:

- local mutable SQLite DB under `~/.smart-home/data`
- code/tests/docs committed, not the generated DB
- read-only HTTP fetch
- user LaunchAgent under `~/Library/LaunchAgents`
- package-run evidence under `requirements/package-runs/Pxxxx`

P0031 does not require Shelly, Home Assistant, MCP, KVS, scripts, relays, covers, switches, dimmers or any live device access.

## Open-Meteo documentation checked

Checked current Open-Meteo Historical Weather API documentation on 2026-05-30.

Relevant facts:

- `/v1/archive` provides historical weather data.
- Historical weather is available from 1940 until now.
- The API accepts latitude, longitude, `start_date`, `end_date`, hourly variables and `timezone`.
- ERA5 and ERA5-Land are documented as gap-free reanalysis datasets with daily updates and about 5 days delay.
- The requested variables are documented hourly variables or equivalents:
  - `temperature_2m`
  - `apparent_temperature`
  - `wind_speed_10m`
  - `wind_speed_100m`
  - `wind_gusts_10m`
  - `cloud_cover`
  - `shortwave_radiation`
  - `precipitation`
  - `snowfall`
  - `relative_humidity_2m`
  - `pressure_msl`

## Live source checks

Read-only checks used `archive-api.open-meteo.com/v1/archive` with:

```text
models=era5_seamless
timezone=Europe/Stockholm
hourly=<all required P0031 variables>
```

Results:

- `2026-05-20` returned complete non-null hourly values for the requested variables.
- `2026-05-29` returned 24 hourly timestamps but all requested variable values were null.
- `2026-05-25` returned only the first two non-null hours and nulls for the rest.
- `2026-05-24` returned complete non-null hourly values.

Therefore, on 2026-05-30 the latest safely available complete ERA5-Seamless historical day is `2026-05-24`. The daily ingest must use a conservative publication delay rather than assuming yesterday is available.

## Source/model decision

Use Open-Meteo Historical Weather API with `models=era5_seamless`.

Rationale:

- It supports the full requested variable set in one API response.
- It is intended for consistent historical/reanalysis access.
- It avoids mixing ad-hoc forecast/current products into the historical dataset.

Tradeoff:

- Recent days can be delayed or partially null. P0031 treats latest safely available complete day as `today - 6 days` by default and validates nulls rather than hiding them.

## SE3 proxy decision

Use weighted multi-location SE3 proxy:

```text
stockholm: 59.3293, 18.0686, weight 0.35
goteborg: 57.7089, 11.9746, weight 0.25
orebro: 59.2753, 15.2134, weight 0.20
linkoping: 58.4108, 15.6214, weight 0.20
```

This covers Mälardalen/eastern SE3, western SE3, inland SE3 and southern/eastern SE3 while keeping source volume small and deterministic.

## DB size/repo impact estimate

For 2022-05-30 through 2026-05-24:

- area proxy hours: about 34944
- location observations: about 139776 for four locations
- wide SQLite rows with 11 numeric variables should remain modest, expected low tens of MB locally

The generated SQLite DB is not committed to repo.

## Review conclusion

PASS with one deliberate source-delay rule:

```text
latest safely available complete day = local today - 6 days
```
