# P0013 Functions

## Shelly runtime

### `spotprice_v0_9_0`
Source: `src/shelly/spotprice/spotprice.js`

Responsibilities:
- select today or tomorrow using the documented publish-window policy
- fetch compact `se.elpris.eu` SE3 `avg24` payload
- parse the `p` array without `JSON.parse`
- calculate 12 two-hour total prices using the dampers G1 price model
- write only the corrected P0013 KVS keys

Forbidden:
- actuator/output/relay/switch/cover/device configuration calls
- Mac/Home Assistant runtime dependency
- P0011 Tibber token/source/debug KVS contract

## Mac deploy tool

### `deploy_spotprice`
Source: `src/mac/tools/shelly_live/core.py`

Responsibilities:
- deploy only `spotprice_v0_9_0`
- upload with bounded in-memory RPC chunks
- start, capture bounded logs, read corrected KVS keys and stop the script
- stop the script even when KVS verification fails after a successful start

### `verify_spotprice_kvs`
Source: `src/mac/tools/shelly_live/core.py`

Responsibilities:
- require `hp.price.status == ok`
- require `hp.price.area == SE3`
- require 12 numeric values in `hp.price.2h`
- require date and updated timestamp
