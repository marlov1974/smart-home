# Package P0012 Debug Attempts

## Package

`P0012`

## Attempt limit

Default: 3

## Attempt 1

### Change summary

- Replaced Tibber/fallback spotprice source with corrected elprisetjustnu source.
- Updated Mac KVS verification from P0011 keys to P0012 keys.
- Rebuilt spotprice artifact and ran initial live dampers test.

### Tests run

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/spotprice/manifest.json --build-root build/shelly/spotprice --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/spotprice --dep-root dep/s --role spotprice_v0_9_0
python3 -m src.mac.tools.shelly_live deploy-spotprice --base-url http://192.168.86.240:8030/ --script build/shelly/spotprice/spotprice_v0_9_0.js --expect spotprice --upload-chunk-bytes 1500 --log-timeout 30 --kvs-timeout 30
```

### Output/state result

Local unit/build/validate passed after one unit test fixture correction.

Live test failed:

```text
error: spotprice KVS verification timed out: spotprice KVS status is not ok: bad_count
```

### Log/runtime observations

Read-only diagnostics showed:

```text
Script.List: spotprice_v0_9_0 id=1 was still running after the failed tool run.
hp.price.status = bad_count
hp.price.area missing
hp.price.2h/date/updated were stale P0011 values
```

Mac fetch of the same tomorrow URL returned:

```text
https://www.elprisetjustnu.se/api/v1/prices/2026/05-25_SE3.json -> 404: Data not found or not ready yet
```

Mac fetch of today's URL returned current elprisetjustnu JSON with `SEK_per_kWh` values.

### Result

NEEDS FIX

### Next action

Add package-scoped debug fixes:

- keep tomorrow primary but retry today's elprisetjustnu date if tomorrow is not ready
- make `deploy_spotprice()` stop the script even when KVS verification fails
- rerun local and live verification

## Attempt 2

### Change summary

- Added today retry for not-ready tomorrow data.
- Changed `deploy_spotprice()` to stop `spotprice_v0_9_0` in a `finally` block when KVS verification fails.
- Rebuilt spotprice artifact and reran live dampers test.

### Tests run

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/spotprice/manifest.json --build-root build/shelly/spotprice --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/spotprice --dep-root dep/s --role spotprice_v0_9_0
python3 -m src.mac.tools.shelly_live deploy-spotprice --base-url http://192.168.86.240:8030/ --script build/shelly/spotprice/spotprice_v0_9_0.js --expect spotprice --upload-chunk-bytes 1500 --log-timeout 30 --kvs-timeout 30
```

### Output/state result

Local unit/build/validate passed.

Live test failed:

```text
error: spotprice KVS verification timed out: spotprice KVS status is not ok: fetching
```

### Log/runtime observations

Read-only diagnostics showed:

```text
Script.List: spotprice_v0_9_0 id=1 running=false
Shelly.GetStatus: script:1 errors=["out_of_memory"]
hp.price.status = fetching
hp.price.area missing
```

The `finally` stop behavior worked: the script was no longer running after the failed live test.

### Result

NEEDS FIX

### Next action

Add publication-hour guard so the script does not perform a known-not-ready tomorrow fetch before 14:00, then rerun verification.

## Attempt 3

### Change summary

- Added `FETCH_TOMORROW_AFTER_HOUR = 14` and `shouldFetchTomorrow()` so the script fetches today's elprisetjustnu data before tomorrow prices are expected to be published.
- Rebuilt spotprice artifact and reran live dampers test.

### Tests run

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/spotprice/manifest.json --build-root build/shelly/spotprice --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/spotprice --dep-root dep/s --role spotprice_v0_9_0
python3 -m src.mac.tools.shelly_live deploy-spotprice --base-url http://192.168.86.240:8030/ --script build/shelly/spotprice/spotprice_v0_9_0.js --expect spotprice --upload-chunk-bytes 1500 --log-timeout 30 --kvs-timeout 30
```

### Output/state result

Local unit/build/validate passed.

Live test failed:

```text
error: spotprice KVS verification timed out: spotprice KVS status is not ok: fetching
```

### Log/runtime observations

Read-only diagnostics after failure:

```text
Script.List: spotprice_v0_9_0 id=1 running=false
hp.price.status = fetching
hp.price.area missing
Shelly.GetStatus script:1 errors=["out_of_memory"]
Script.Stop?id=1 returned was_running=false
```

The Mac tool stopped the script after failure. No forbidden actuator/output/config operations were performed by the tool.

### Result

FAIL

### Next action

Stop per package attempt limit. Current hypothesis: the dampers Shelly cannot fetch and hold the full elprisetjustnu response body plus this script within available script memory. P0012 likely needs a design change, such as Mac-side fetch/preprocessing for this test, a smaller Shelly parser/runtime, or a different endpoint/transport that does not allocate the full JSON response in Shelly script memory.

## Final status

Stopped after 3 failed live attempts.

## Remaining uncertainty

The current corrected elprisetjustnu source builds and unit tests pass, but live dampers execution fails with Shelly `out_of_memory` before corrected KVS output is written. The device is left with `spotprice_v0_9_0` installed and stopped.
