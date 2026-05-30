# Spot Price Knowhow

Durable lessons about spot price sources, parsing and local history ingestion.

## Historical source shape

P0030 showed that `se.elpris.eu` compact `avg24` is useful for low-memory current-day Shelly runtime payloads, but it is not sufficient as the sole historical backfill source. On 2026-05-30, `https://se.elpris.eu/api/v1/prices/2022/05-30_SE3.json?avg24` returned HTTP 410 while direct Elprisetjustnu history for the same date returned data.

For Mac-side historical backfill, prefer direct Elprisetjustnu daily object-list URLs and parse both old hourly rows and newer quarter-hour rows:

```text
https://www.elprisetjustnu.se/api/v1/prices/YYYY/MM-DD_SE3.json
```

Quarter-hour rows should be aggregated to hourly means before storing hourly history. Do not synthesize missing hours.

## HTTP client behavior

Elprisetjustnu may reject default Python urllib requests with HTTP 403. Use a clear project User-Agent for read-only source fetches.

## Backfill robustness

Long historical backfills should commit per source day and be safe to rerun. A single transient timeout must not discard already validated days. Error messages should include the area and local date that failed.
