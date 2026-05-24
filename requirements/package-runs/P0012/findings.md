# Package P0012 Findings

## Stopped: Shelly out_of_memory during elprisetjustnu fetch

P0012 corrected the source template from Tibber/fallback to elprisetjustnu and corrected the Mac KVS verification contract, but live dampers verification did not pass within the 3-attempt package limit.

## Evidence

Attempt 1:

```text
status=bad_count
tomorrow URL from Mac returned 404: Data not found or not ready yet
```

Attempt 2:

```text
status=fetching
script:1 errors=["out_of_memory"]
```

Attempt 3:

```text
status=fetching
script:1 errors=["out_of_memory"]
script stopped after failure
```

## Fixed inside package

- Corrected current G2 spotprice source from Tibber/fallback to elprisetjustnu-based logic.
- Corrected Mac-side KVS verification keys to:

```text
hp.price.2h
hp.price.date
hp.price.area
hp.price.status
hp.price.updated
```

- Preserved RPC upload chunking.
- Fixed `deploy_spotprice()` so it stops `spotprice_v0_9_0` even when KVS verification fails.
- Clarified RPC upload chunks vs repo deploy chunks in memory docs.

## Left open

Live dampers execution still fails with Shelly script `out_of_memory` before the corrected elprisetjustnu script writes `hp.price.area` and `status=ok`.

## Current hypothesis

The dampers Shelly cannot fetch and hold the full elprisetjustnu JSON response body plus the current script within available script memory. A future package likely needs one of:

- Mac-side fetch/preprocessing with Shelly receiving compact 12-block output
- a smaller Shelly spotprice parser/runtime
- a different source endpoint or transport that does not allocate the full JSON response in Shelly script memory
- a device/runtime memory investigation before continuing Shelly-side public API fetches

## Promotion

Not promoted to `memory/knowhow/` yet. The finding is important, but should be confirmed by the next package or a focused Shelly memory investigation before becoming a general rule.
