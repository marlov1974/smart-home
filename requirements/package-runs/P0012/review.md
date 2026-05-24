# Package P0012 Review Evidence

## Package

`P0012`

## Consistency result

WARN

## Files checked

- `AGENTS.md`
- `README.md`
- `memory/bootstrap-manifest.json`
- mandatory G2 bootstrap files listed by the manifest
- `requirements/packages/P0012-correct-spotprice-template-and-clean-deploy-artifacts.md`
- `requirements/packages/P0011-mac-rpc-chunked-upload-and-spotprice-kvs-test.md`
- `requirements/package-runs/P0011/review.md`
- `requirements/package-runs/P0011/logs/live-dampers-spotprice.md`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `memory/infrastructure/devices.md`
- `src/mac/tools/shelly_live/**`
- `tests/mac/tools/shelly_live/**`
- `src/shelly/spotprice/**`
- `build/shelly/spotprice/spotprice_v0_9_0.js`
- `dep/s/ch/spotprice_v0_9_0/01.js`
- `dep/s/rec/spotprice_v0_9_0.json`
- `/Users/marcus.lovenstad/dev/shelly/devices/dampers-8813bfdaa0c0/scripts/spotprice.js`

## Checks

### Package vs memory

P0012 is consistent with the G2 package model, G1/G2 boundary and Mac tooling model. Mac direct deploy remains an installer/orchestrator path, while source/build/deploy layers remain separate.

The existing memory still describes repo deploy chunks as generated artifacts for Shelly deploy structure. P0012 explicitly narrows the current Mac-direct-deploy behavior: RPC upload chunks are required for Mac direct upload, while repo chunks are optional/future Shelly-side pull/install artifacts.

### Package vs linked requirements

P0012 supersedes P0011 current-state spotprice source and KVS contract without rewriting P0011 evidence. This is consistent with the package history rule.

### Package vs previous packages

P0011 proved chunked upload and KVS verification using the wrong Tibber/fallback template. P0012 keeps the useful Mac chunked upload behavior and replaces only current-state source/contract/docs/tests.

### Package vs implementation/deploy structure

Current G2 source still contains Tibber/fallback behavior and old KVS keys:

```text
hp.price.source
hp.price.debug
hp.price.debug.len
```

The correct G1 template exists at:

```text
/Users/marcus.lovenstad/dev/shelly/devices/dampers-8813bfdaa0c0/scripts/spotprice.js
```

That template uses `elprisetjustnu.se`, `PRICE_AREA = "SE3"`, 96 quarter-hour values and these KVS keys:

```text
hp.price.2h
hp.price.date
hp.price.area
hp.price.status
hp.price.updated
```

### Package vs G1/G2 boundary

P0012 reads the G1 source as a template but must not edit G1. The adapted G2 copy must remove only wrapper duplication and keep runtime behavior aligned with the intended test template.

### Package vs invariants

The correct G1 template performs `HTTP.GET` and writes only spotprice-owned KVS keys. It contains no actuator, output, switch, relay, cover, component, device config, Wi-Fi, MQTT, Bluetooth or cloud operations.

The Mac live tool already limits live script writes to `hello_v1_0_0` and `spotprice_v0_9_0` and uses read-only KVS gets for verification.

### Package vs testability and rollback

Unit tests can cover KVS contract correction, forbidden key rejection, and chunked upload preservation. Build validation can cover regenerated artifacts. Live dampers verification is allowed by the package.

Rollback remains a new forward package.

### Chat-only assumptions

No package-critical behavior is inferred from chat only. The active package, P0011 evidence and the correct local G1 source define the work.

## Warning

The correct elprisetjustnu template has no fallback price series. If the Shelly device cannot reach `www.elprisetjustnu.se`, live verification may end with `hp.price.status = http_error` and no 12-value `hp.price.2h`. That is an operational live-test failure to debug within the package attempt limit, not a package inconsistency.

## Decision

Continue with warning.

## Notes for human/ChatGPT review

The implementation should preserve P0011 evidence unchanged and document that P0012 supersedes current source/contract only.
