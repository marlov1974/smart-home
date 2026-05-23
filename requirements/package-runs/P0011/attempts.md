# Package P0011 Attempts

## Attempt 1

Local verification before live test passed:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/spotprice/manifest.json --build-root build/shelly/spotprice --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/spotprice --dep-root dep/s --role spotprice_v0_9_0
```

Live command:

```bash
python3 -m src.mac.tools.shelly_live deploy-spotprice --base-url http://192.168.86.240:8030/ --script build/shelly/spotprice/spotprice_v0_9_0.js --expect spotprice --upload-chunk-bytes 1500 --log-timeout 30 --kvs-timeout 30
```

Result:

```text
error: RPC KVS.Get returned error: {'code': -105, 'message': "Argument 'key', value 'hp.price.2h' not found!"}
```

Interpretation:

The tool reached the live device and got as far as KVS verification. Shelly returns missing KVS keys as an RPC error. That is expected before the spotprice script has written output and should be treated as an absent value during bounded polling.

Fix:

`kvs_get()` now returns `None` for documented KVS keys when Shelly reports a missing key. Verification still fails if the keys do not become valid before timeout.

## Attempt 2

Local verification after the fix passed:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/spotprice --dep-root dep/s --role spotprice_v0_9_0
```

Live command:

```bash
python3 -m src.mac.tools.shelly_live deploy-spotprice --base-url http://192.168.86.240:8030/ --script build/shelly/spotprice/spotprice_v0_9_0.js --expect spotprice --upload-chunk-bytes 1500 --log-timeout 30 --kvs-timeout 30
```

Result:

```text
passed
upload_chunk_bytes=1500
upload_chunk_count=6
status=no_token
source=fallback
price_count=12
```

Evidence:

- `requirements/package-runs/P0011/logs/live-dampers-spotprice.md`
