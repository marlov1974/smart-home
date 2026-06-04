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

P0051 verified that eSett Open Data endpoints are public and useful for SE1-SE4 physical balance history. The API returns quarter-hour `timestampUTC` rows. On the local Mac Python 3.9 runtime, `urllib` can fail the eSett TLS handshake while `curl` succeeds, so ingestion tooling may need a `curl` fallback. eSett consumption values are negative in source payloads and should be sign-normalized to positive demand before feature storage.

P0052 verified that Svenska kraftnat Kontrollrummet exposes current/recent Nordic flow-map data through `/services/controlroom/v2/map/flow?ticks=<epoch_ms>`, with Statnett named as data source in the page component. Reliable access needs browser-like `User-Agent` and `Referer` headers. The endpoint provides signed border flows plus SE area import/export values, but no capacity values. ENTSO-E Transparency API remains the likely capacity source and requires a security token.

P0052A verified that token-backed ENTSO-E Transparency API calls can return internal Swedish bidding-zone data for A09 scheduled commercial exchange, A11 physical flow and A61 capacity with contract types A02/A03/A04. Keep `securityToken` out of evidence-safe request records and add it only inside the HTTP fetch. Capacity responses may use `P1M` resolution; parse those from the source period start/end rather than assuming a fixed month length, then filter expanded hourly rows back to the requested UTC interval.

P0052B found two important ENTSO-E backfill robustness rules. First, clip long-period capacity values to the requested UTC chunk before hourly expansion; filtering after expansion can make month/year capacity responses too slow. Second, historical diagnostic tables may store equivalent UTC timestamps as either `...Z` or `...+00:00`; use cheap UTC text normalization for joins instead of rewriting older tables or applying expensive `datetime()` joins over large tables.

P0052C showed that ENTSO-E A61 A02/A03/A04 should remain blocked as internal Swedish capacity ceilings for utilization and bottleneck margin: in post-flow-based data, A09 scheduled exchange and A11 physical flow materially exceeded all three variants. A61 rows may stay as labeled evidence, but do not use them as capacity denominators without a different source/concept.

P0053A showed that ENTSO-E A09/A11 internal Swedish border directions can be naturally sparse by direction. For modeling diagnostics, validate raw border/direction missingness separately from derived net-feature completeness. Net features may safely treat the missing opposite direction as zero when the source only publishes the active direction, but evidence must still report directional missingness and never relabel sparse reverse-direction rows as complete source coverage.

P0053B showed that SE1 consumption is a practical first physical forecast target. For forecast-safe consumption modeling, calendar, Swedish special-day features, origin-safe load lags/rollups and train-only weather normals are safe; realized weather belongs in a separate diagnostic-only group unless a future package supplies true forecast-time weather features. In the first P0053B split, bridge days, weekends and January cold/high-load periods dominated transparent baseline errors.

P0053B-A showed that old price-prediction artifacts without forecast-origin timestamps must not be used as forecast-safe consumption features. Even when prediction tables contain target timestamps and predicted SE1 prices, they are not safe for response testing unless each row can prove `forecast_origin_timestamp_utc <= example_origin_timestamp_utc`. Actual spot history and regenerated evaluation diagnostics are not substitutes for an immutable historical forecast archive.

## Backfill robustness

Long historical backfills should commit per source day and be safe to rerun. A single transient timeout must not discard already validated days. Error messages should include the area and local date that failed.
