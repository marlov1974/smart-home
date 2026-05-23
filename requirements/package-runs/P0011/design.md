# Package P0011 Implementation Design

## Package Interpretation

P0011 extends the P0010 Mac live deploy tool with direct RPC upload chunks and a live spotprice KVS verification test on the dampers device.

The package will copy/adapt the G1 dampers spotprice source into G2 test source, build it with the existing Shelly build tool, upload the built script to dampers as `spotprice_v0_9_0`, verify log output and read only the documented spotprice KVS keys.

## G1 spotprice source and KVS contract

Source recipe:

```text
/Users/marcus.lovenstad/dev/shelly/rt/recipes/dampers/spotprice.json
```

Source files copied/adapted:

```text
/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/base.js
/Users/marcus.lovenstad/dev/shelly/rt/common/script.js
/Users/marcus.lovenstad/dev/shelly/rt/common/helpers.js
/Users/marcus.lovenstad/dev/shelly/rt/common/kvs.js
/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/config.js
/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/auth.js
/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/tibber-query.js
/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/http.js
/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/price-model.js
/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/parse.js
/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/output.js
/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/main.js
```

The G2 manifest will add the existing G2 build wrapper/header, so G1 wrapper chunks are not copied.

Allowed KVS keys:

```text
hp.price.2h
hp.price.date
hp.price.status
hp.price.updated
hp.price.source
hp.price.debug
hp.price.debug.len
```

Live verification criteria:

- `hp.price.status` is present and non-empty.
- `hp.price.2h` is parseable as 12 comma-separated numeric values.
- `hp.price.date`, `hp.price.updated` and `hp.price.source` are present when status indicates a completed fallback or successful price write.
- debug keys may be present for fallback/error paths and are recorded as safe summaries.

## Safety Adaptations

The copied G2 spotprice source will:

- use `SCRIPT_NAME = "spotprice_v0_9_0"`
- not call `Script.Stop` with hardcoded G1 id `4`
- not contain actuator/output/switch/relay/cover/device-config RPC calls
- write only the documented spotprice KVS keys

The Mac deploy tool will stop only the actual `spotprice_v0_9_0` script id returned by `Script.List`/`Script.Create`.

## Implementation Structure

Update:

```text
src/mac/tools/shelly_live/core.py
tests/mac/tools/shelly_live/test_core.py
```

Add:

```text
src/shelly/spotprice/manifest.json
src/shelly/spotprice/*.js
build/shelly/spotprice/spotprice_v0_9_0.js
docs/functions/mac/shelly-live-deploy-tool.md
requirements/package-runs/P0011/attempts.md
requirements/package-runs/P0011/logs/
```

Generated repo deploy chunks under `dep/s/**` are not used by the Mac direct deploy proof because P0011 focuses on temporary in-memory RPC upload chunks. The existing Shelly build command still emits `dep/s/ch/spotprice_v0_9_0/**` and `dep/s/rec/spotprice_v0_9_0.json` deterministically as part of its normal contract, so those generated files are included only as build output, not as the upload mechanism.

## Tool Behavior

Add a `deploy-spotprice` CLI command:

```text
python3 -m src.mac.tools.shelly_live deploy-spotprice \
  --base-url http://192.168.86.240:8030/ \
  --script build/shelly/spotprice/spotprice_v0_9_0.js \
  --expect spotprice \
  --upload-chunk-bytes 1500 \
  --log-timeout 30
```

The command will:

1. read status and scripts
2. stop/delete only `hello_v1_0_0` if present
3. create/reuse `spotprice_v0_9_0`
4. clear/replace script code with first upload chunk using `append:false`
5. append remaining upload chunks with `append:true`
6. start `spotprice_v0_9_0`
7. capture bounded debug log
8. read allowed KVS keys
9. stop only `spotprice_v0_9_0`
10. print structured evidence

## Test Strategy

Local verification:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/spotprice/manifest.json --build-root build/shelly/spotprice --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/spotprice --dep-root dep/s --role spotprice_v0_9_0
git diff --check
```

Live verification:

```bash
python3 -m src.mac.tools.shelly_live deploy-spotprice --base-url http://192.168.86.240:8030/ --script build/shelly/spotprice/spotprice_v0_9_0.js --expect spotprice --upload-chunk-bytes 1500 --log-timeout 30
```

## Risks and Uncertainties

- The dampers device or external Tibber request may be unavailable. The script has fallback behavior that should still write KVS.
- Shelly firmware may differ in exact `Script.PutCode` append behavior for chunked upload. Unit tests verify the request sequence; live verification confirms the real behavior.
- Live network access may require operator approval.
