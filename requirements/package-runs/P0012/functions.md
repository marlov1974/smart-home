# Package P0012 Function Design

## Package

`P0012`

## Scope

Shelly spotprice test source and Mac-side live deploy/KVS verification.

## New functions

None planned.

## Changed functions

### spotprice.js helper/runtime functions

Current purpose:
- P0011 Tibber/fallback implementation fetches Tibber data or writes fallback prices.

Change:
- Replace with adapted G1 dampers elprisetjustnu implementation:
  - `urlForDate()`
  - `shouldFetchTomorrow()`
  - `buildBlocksFromBody()`
  - `fetchAndSave()`
  - `totalPriceIncVat()`
  - `saveBlocks()`
  - `run()`

Inputs changed:
- Removes Tibber token/text input.
- Uses public elprisetjustnu HTTP response body.

Outputs changed:
- Writes `hp.price.area`.
- Stops writing `hp.price.source`, `hp.price.debug`, `hp.price.debug.len`.

Side effects changed:
- Removes `Text.GetStatus`.
- Keeps `HTTP.GET`.
- Keeps `KVS.Set` only for corrected spotprice-owned keys.

Reason:
- P0012 corrects the template source and KVS contract.
- P0012 attempts 1-2 found tomorrow prices may be unavailable before publication time and the double-fetch path can exceed Shelly memory. The test script therefore uses today's elprisetjustnu data before 14:00 and retries today only when a post-14 tomorrow request is still not ready.

Tests:
- Source grep checks.
- Build and validate commands.
- Live dampers log and KVS verification.

### SPOTPRICE_KVS_KEYS

Current purpose:
- Defines P0011 Tibber/fallback KVS keys for Mac read verification.

Change:
- Replace with corrected P0012 keys:
  - `hp.price.2h`
  - `hp.price.date`
  - `hp.price.area`
  - `hp.price.status`
  - `hp.price.updated`

Inputs changed:
- N/A.

Outputs changed:
- `read_spotprice_kvs()` reads the corrected key set.

Side effects changed:
- Fewer read-only `KVS.Get` calls.

Reason:
- Align Mac verification with correct G1 dampers template.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`.

### verify_spotprice_kvs()

Current purpose:
- Accepts P0011 fallback/success values with source/debug metadata.

Change:
- Require corrected success contract:
  - status exists and equals `ok`
  - 12 numeric two-hour values
  - area equals `SE3`
  - date and updated exist

Inputs changed:
- Expects `hp.price.area`.
- No longer expects source/debug keys.

Outputs changed:
- Summary includes `area`.
- Summary no longer includes `source` or `debug_len`.

Side effects changed:
- None.

Reason:
- P0012 requires corrected KVS verification.

Tests:
- Unit tests for valid and malformed KVS values.
- Live dampers KVS verification.

### deploy_spotprice()

Current purpose:
- Deploys `spotprice_v0_9_0`, captures logs, waits for P0011 KVS verification and stops script.

Change:
- Keep orchestration and RPC upload chunking unchanged.
- Its KVS verification now uses the corrected P0012 contract through `wait_for_spotprice_kvs()`.
- Stop `spotprice_v0_9_0` in a `finally` block after starting it, even when KVS verification fails.

Inputs changed:
- None.

Outputs changed:
- `kvs_summary` shape changes to include `area` and omit source/debug fields.

Side effects changed:
- Live operations remain limited to allowed script lifecycle and read-only corrected KVS keys.

Reason:
- Preserve successful P0011 Mac direct deploy behavior while correcting the contract.
- P0012 attempt 1 found failed KVS verification could otherwise leave the live test script running.

Tests:
- Existing orchestration test updated for corrected KVS reads.
- Live dampers test.

## Removed functions

No Python functions removed.

Shelly source functions removed by replacement:

- `readTibberToken()`
- `tibberPayload()`
- `tibberHeaders()`
- `fetchTibberPrices()`
- `fallbackSeasonSeries()`
- `writeFallbackPrices()`
- `writeDebug()`
- `fallback()`

Reason:
- The correct G1 dampers template does not use Tibber token/fallback/debug behavior.

Replacement:
- Correct elprisetjustnu fetch, parse and KVS write flow.

Tests:
- Grep/source checks and live verification.

## Important unchanged functions

### split_rpc_upload_chunks()

Reason for no change:
- P0012 must preserve in-memory RPC chunking for Mac direct deploy.

### put_script_code_chunked()

Reason for no change:
- P0012 must continue uploading large scripts through bounded RPC chunks.

### ensure_allowed_script_name()

Reason for no change:
- Existing script-name safety boundary already matches P0012.

### cleanup_hello_residue()

Reason for no change:
- P0012 live boundary does not authorize deleting unrelated scripts and does not require changing P0010 cleanup behavior.

## Design deviations during implementation

Attempt 1 added `fetchAndSave()` to support a today retry when tomorrow data is not ready, and changed `deploy_spotprice()` stop handling to use `finally`.

Attempt 2 added `shouldFetchTomorrow()` and `FETCH_TOMORROW_AFTER_HOUR` to avoid known-not-ready tomorrow fetches before 14:00.
