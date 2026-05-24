# P0013 Review

## Status
PASS

## Scope
Build a low-memory autonomous `spotprice_v0_9_0` Shelly runtime for dampers using `se.elpris.eu`, with Mac-side deploy/log/KVS verification only.

## Inputs reviewed
- `AGENTS.md`
- `README.md`
- `memory/bootstrap-manifest.json`
- `memory/05-package-lifecycle.md`
- bootstrap manifest read-order files
- `requirements/packages/P0013-spotprice-low-memory-se-elpris-runtime.md`
- P0011/P0012 package and package-run evidence
- current G2 spotprice source and Mac live deploy tool
- G1 dampers spotprice reference source, read-only
- `se.elpris.eu` endpoint behavior for SE3 `avg24`

## Findings
- Current G2 spotprice source still uses the P0011 Tibber/fallback model and P0011 `hp.price.source/debug` keys. P0013 must replace that current runtime truth.
- `https://se.elpris.eu/api/v1/prices/2026/05-24_SE3.json?avg24` returns a compact response with `p` containing 24 hourly SEK/kWh values.
- `https://se.elpris.eu/api/v1/prices/2026/05-25_SE3.json?avg24` can return `not_available_yet` before publication, so the script must not blindly fetch tomorrow early in the day.
- Mac RPC upload chunking is still present and should remain the live deploy transport.
- P0012 live evidence showed `out_of_memory`/fetch/parser failure on the larger direct elprisetjustnu response; P0013 should avoid JSON.parse and avoid large intermediate arrays.

## Decision
Proceed with implementation under P0013 scope. Use a single deterministic date request, parse only the compact `p` array, write only corrected KVS keys, and verify live on dampers.
