# Package P0012 Implementation Design

## Package

`P0012`

## Package interpretation

P0012 corrects the current G2 `spotprice_v0_9_0` test script and Mac verification contract after P0011 used the wrong G1 source. The package should keep the successful Mac-side chunked RPC upload path, replace the Tibber/fallback spotprice implementation with the correct elprisetjustnu template, verify corrected KVS keys, rebuild generated spotprice output and run the allowed live dampers test.

## Correct G1 spotprice source

Source:

```text
/Users/marcus.lovenstad/dev/shelly/devices/dampers-8813bfdaa0c0/scripts/spotprice.js
```

The G1 source is a self-contained IIFE. The G2 source will adapt its body into `src/shelly/spotprice/spotprice.js` without the outer IIFE because the G2 Shelly build tool already generates the wrapper and strict mode.

Required retained behavior:

- use `https://www.elprisetjustnu.se/api/v1/prices/<yyyy>/<MM-DD>_SE3.json`
- `PRICE_AREA = "SE3"`
- try tomorrow first, matching the G1 template
- parse `SEK_per_kWh`
- require 96 quarter-hour values
- aggregate 8 quarters per 2-hour block into 12 values
- apply VAT, retailer, energy-tax and grid-tariff model
- write only final spotprice KVS keys

Forbidden behavior check:

- no actuator/output/switch/relay/cover/component/device-config behavior
- no Tibber token reads
- no fallback/debug/source KVS keys

## Corrected KVS contract

Allowed/read/verified KVS keys:

```text
hp.price.2h
hp.price.date
hp.price.area
hp.price.status
hp.price.updated
```

Verification criteria:

- `hp.price.status` must be present.
- For success, status must be `ok`.
- `hp.price.2h` must contain exactly 12 numeric comma-separated values.
- `hp.price.area` must equal `SE3`.
- `hp.price.date` and `hp.price.updated` must be present.

P0011 keys removed from the current G2 spotprice test contract:

```text
hp.price.source
hp.price.debug
hp.price.debug.len
```

## Repo chunks vs RPC upload chunks cleanup decision

RPC upload chunks remain required for Mac direct deploy and stay implemented in `src/mac/tools/shelly_live/core.py`.

Repo deploy chunk generation remains in the Shelly build tool because it is an existing deterministic build contract and P0012 does not allow changing `src/mac/tools/shelly_build/**`. The generated `dep/s/ch/spotprice_v0_9_0/01.js` and `dep/s/rec/spotprice_v0_9_0.json` will be rebuilt from corrected source, but Mac direct deploy will continue reading `build/shelly/spotprice/spotprice_v0_9_0.js` and uploading it through in-memory RPC chunks.

No P0011 evidence will be edited or deleted. Existing `hello_v1_0_0` fixture deploy artifacts are not removed in P0012 because the fixture source still exists and they are not the current spotprice contract mismatch.

## Live dampers verification plan

Target endpoint:

```text
http://192.168.86.240:8030/
```

Live command shape:

```bash
python3 -m src.mac.tools.shelly_live deploy-spotprice --base-url http://192.168.86.240:8030/ --script build/shelly/spotprice/spotprice_v0_9_0.js --expect spotprice --upload-chunk-bytes 1500 --log-timeout 30 --kvs-timeout 30
```

Expected evidence:

- upload chunk size and count
- log excerpt containing `spotprice`, ideally `GET https://www.elprisetjustnu.se/...SE3.json`
- KVS summary with status `ok`, area `SE3`, 12 price values, date and updated timestamp
- final script installed and stopped
- no forbidden RPC operations

## Chosen implementation structure

### Files/modules to change

- `src/shelly/spotprice/spotprice.js`
  - Replace Tibber/fallback implementation with corrected elprisetjustnu-based adapted G1 template.
- `src/mac/tools/shelly_live/core.py`
  - Replace P0011 KVS key list and KVS verifier with P0012 contract.
  - Keep chunked upload functions unchanged except comments/docstrings naming P0012 where needed.
- `tests/mac/tools/shelly_live/test_core.py`
  - Update fake KVS values and expected reads.
  - Add/keep tests for chunked upload and forbidden operations.
- `docs/functions/mac/shelly-live-deploy-tool.md`
  - Update KVS contract and P0012 last-changed notes.
- `memory/device-management/source-build-deploy-layers.md`
  - Clarify RPC upload chunks vs repo deploy chunks.
- `memory/device-management/mac-layer.md`
  - Clarify Mac direct deploy uses in-memory RPC chunks and not repo chunks.
- `build/shelly/spotprice/spotprice_v0_9_0.js`
  - Regenerated.
- `dep/s/ch/spotprice_v0_9_0/01.js`
  - Regenerated build output, optional for Mac direct deploy.
- `dep/s/rec/spotprice_v0_9_0.json`
  - Regenerated build recipe.
- `requirements/package-runs/P0012/**`
  - Review, design, function design, attempts and live evidence.
- `requirements/packages/P0012-correct-spotprice-template-and-clean-deploy-artifacts.md`
  - Completion notes after implementation.

### Files/modules intentionally not changed

- P0011 package-run evidence remains historical and unchanged.
- `src/mac/tools/shelly_build/**` remains unchanged; P0012 does not need build-tool behavior changes.
- G1 repository files are read-only inputs and are not changed.
- Real FTX runtime source is not touched.

## Refactoring decisions

No broad refactor is planned.

Targeted contract cleanup:

- `SPOTPRICE_KVS_KEYS` changes from the P0011 Tibber/fallback set to the corrected P0012 set.
- `verify_spotprice_kvs()` changes its success criteria to require `status == "ok"` and `area == "SE3"`.

This is inside package scope because P0012 explicitly corrects the spotprice KVS contract.

## Test strategy

Run:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/spotprice/manifest.json --build-root build/shelly/spotprice --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/spotprice --dep-root dep/s --role spotprice_v0_9_0
git diff --check
```

Additional source checks:

```bash
rg -n "Tibber|tibber|hp\\.price\\.(source|debug|debug\\.len)|elprisetjustnu|hp\\.price\\.area" src/shelly/spotprice src/mac/tools/shelly_live tests/mac/tools/shelly_live docs/functions/mac/shelly-live-deploy-tool.md
```

Live test is allowed by P0012 on dampers only.

## Build / generated artifact strategy

After source updates, run the Shelly build tool for the spotprice manifest. Commit both corrected source and deterministic generated spotprice artifacts.

## Risks and uncertainties

- Live fetch depends on the dampers device reaching `www.elprisetjustnu.se`.
- Correct source has no fallback, so an external HTTP failure may prevent `hp.price.2h` from being written.
- The built script may still fit into one repo chunk, while RPC upload should use multiple chunks at 1500 bytes. Unit and live evidence will report the RPC chunk count.

## Design deviations during implementation

Attempt 1 live verification found that `FETCH_TOMORROW = true` can hit a normal elprisetjustnu not-ready window before tomorrow prices are published. The adapted G2 test source now keeps tomorrow as the intended request but only uses it after `FETCH_TOMORROW_AFTER_HOUR = 14`; before then it fetches today's elprisetjustnu data directly. If tomorrow is attempted and still not ready, it retries today's elprisetjustnu date once. This preserves the elprisetjustnu template and avoids reintroducing Tibber/fallback price-series behavior.

Attempt 1 also found that `deploy_spotprice()` left the script running when KVS verification raised. The Mac tool now stops `spotprice_v0_9_0` in a `finally` block after starting it.

Attempt 2 live verification found the double fetch path could leave the Shelly script with `out_of_memory` and status `fetching`. The publication-hour guard was added to avoid a known-not-ready tomorrow fetch before 14:00.
