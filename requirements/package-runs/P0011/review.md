# Package P0011 Review Evidence

## Package

`P0011`

## Result

WARN

## Files Checked

- `AGENTS.md`
- `README.md`
- `memory/bootstrap-manifest.json`
- mandatory G2 bootstrap files listed by the manifest
- `requirements/packages/P0011-mac-rpc-chunked-upload-and-spotprice-kvs-test.md`
- `requirements/packages/P0010-shelly-deploy-tool-and-log-listener.md`
- `requirements/package-runs/P0010/logs/live-dampers-hello.md`
- `src/mac/tools/shelly_live/**`
- `tests/mac/tools/shelly_live/**`
- `memory/infrastructure/devices.md`
- G1 bootstrap and relevant runtime files under `/Users/marcus.lovenstad/dev/shelly`
- G1 spotprice recipe and sources:
  - `/Users/marcus.lovenstad/dev/shelly/rt/recipes/dampers/spotprice.json`
  - `/Users/marcus.lovenstad/dev/shelly/rt/common/wrapper.start.js`
  - `/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/base.js`
  - `/Users/marcus.lovenstad/dev/shelly/rt/common/script.js`
  - `/Users/marcus.lovenstad/dev/shelly/rt/common/helpers.js`
  - `/Users/marcus.lovenstad/dev/shelly/rt/common/kvs.js`
  - `/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/config.js`
  - `/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/auth.js`
  - `/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/tibber-query.js`
  - `/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/http.js`
  - `/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/price-model.js`
  - `/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/parse.js`
  - `/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/output.js`
  - `/Users/marcus.lovenstad/dev/shelly/rt/spotprice-dampers/main.js`
  - `/Users/marcus.lovenstad/dev/shelly/rt/common/wrapper.end.js`

## Consistency Review

P0011 is consistent with the G2 package model and P0010 live-test boundary. The dampers endpoint is documented in G2 as:

```text
ftx-dampers / http://192.168.86.240:8030/
```

The package is allowed to perform live writes, but only for `hello_v1_0_0` cleanup and the `spotprice_v0_9_0` script lifecycle.

The G1 spotprice source and KVS contract are identifiable. Current G1 spotprice code writes these KVS keys:

```text
hp.price.2h
hp.price.date
hp.price.status
hp.price.updated
hp.price.source
hp.price.debug
hp.price.debug.len
```

Older dampers documentation also mentions `hp.price.area`, but the current G1 runtime source does not write it in the active recipe path. P0011 should verify the current runtime-source keys above.

## Warning

The current G1 spotprice source uses fixed `SCRIPT_ID = 4` and `selfStop()` calls `Script.Stop` on that fixed id. That is unsafe for a dynamically created G2 test script because P0011 may create `spotprice_v0_9_0` with a different script id.

Implementation may continue only if the G2 copied/adapted test source removes hardcoded self-stop behavior and the Mac deploy tool stops only the actual `spotprice_v0_9_0` script id after verification.

## Decision

Continue with the documented warning and adaptation.
