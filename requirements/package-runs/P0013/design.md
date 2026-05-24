# P0013 Design

## Low-memory se.elpris source model
Runtime source is `https://se.elpris.eu/api/v1/prices/YYYY/MM-DD_SE3.json?avg24`.

Observed compact shape:

```json
{"src":"Elprisetjustnu.se","via":"se.elpris.eu","t0":"2026-05-24T00:00:00+02:00","s":3600,"u":"SEK","raw":96,"p":[...24 hourly values...]}
```

The Shelly script reads only `p`. The 24 hourly values are converted into 12 two-hour total price values by averaging pairs after applying the dampers G1 VAT, retailer, tax and grid model.

## Date selection policy
Use one deterministic request to avoid keeping two HTTP responses in memory:

```text
if local hour >= 14:
  fetch tomorrow
else:
  fetch today
```

The live test on 2026-05-24 at 07:51 CEST should therefore target today, which is already available.

## Corrected KVS contract
P0013 writes and Mac verification reads only:

```text
hp.price.2h
hp.price.date
hp.price.area
hp.price.status
hp.price.updated
```

`hp.price.status` must be `ok` for live verification to pass. `hp.price.area` must be `SE3`. The P0011 `hp.price.source`, `hp.price.debug` and `hp.price.debug.len` keys are historical only and are not part of the P0013 current contract.

## Memory strategy
- Use the compact `avg24` endpoint instead of the larger object-list response.
- Avoid `JSON.parse`.
- Locate the `p` array with string search and parse numeric tokens in place.
- Do not store hourly prices in an array.
- Accumulate two values at a time and store only 12 final two-hour values.
- Write only compact KVS strings.

## Repo chunks vs RPC upload chunks
Repo deploy chunks under `dep/s/**` are generated artifacts from the Shelly build tool. They are retained only because the current build tool emits them.

Mac direct deploy uses bounded in-memory RPC upload chunks from `shelly_live`. P0013 live verification uses those RPC chunks, not repo chunk files, as the deployment transport.

## Live dampers verification plan
Target dampers endpoint:

```text
http://192.168.86.240:8030/
```

Commands:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/spotprice/manifest.json --build-root build/shelly/spotprice --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/spotprice --dep-root dep/s --role spotprice_v0_9_0
python3 -m src.mac.tools.shelly_live deploy-spotprice --base-url http://192.168.86.240:8030/ --script build/shelly/spotprice/spotprice_v0_9_0.js --expect spotprice --upload-chunk-bytes 1500 --log-timeout 30 --kvs-timeout 30
git diff --check
```

Evidence must record the selected URL/date, upload chunk size/count, log excerpt, corrected KVS values or summary, final script list/status and any memory-related log lines.

## Failed-package cleanup if verification fails
If P0013 live verification fails after three attempts:

- preserve package-run evidence
- update package status to `failed-live` or stopped
- revert unverified current-state implementation changes
- commit/push evidence-only failure record when safe
- leave the worktree clean or report the blocker
