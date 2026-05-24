# P0013 Findings

## se.elpris compact source

`avg24` returns a compact JSON payload with a `p` array containing 24 hourly SEK/kWh values. This is suitable for dampers because the script only needs to locate and parse the `p` values, then reduce them to 12 two-hour totals.

## Date availability

Tomorrow may return `not_available_yet` early in the day. P0013 uses a single-request policy: today before 14:00 local, tomorrow at or after 14:00 local.

## Live dampers result

The P0013 low-memory runtime passed live verification on dampers on the first attempt. `spotprice_v0_9_0` fetched the compact SE3 `avg24` endpoint, wrote the corrected KVS contract and stopped after verification. No memory pressure was observed in the bounded evidence.
