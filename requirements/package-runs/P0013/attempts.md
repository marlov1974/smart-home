# P0013 Attempts

## Attempt 1 - live dampers

Result: PASS

Command:

```bash
python3 -m src.mac.tools.shelly_live deploy-spotprice --base-url http://192.168.86.240:8030/ --script build/shelly/spotprice/spotprice_v0_9_0.js --expect spotprice --upload-chunk-bytes 1500 --log-timeout 30 --kvs-timeout 30
```

Target: `http://192.168.86.240:8030`

Observed:
- script: `spotprice_v0_9_0`, id `1`
- upload chunk bytes: `1500`
- upload chunk count: `4`
- selected URL: `https://se.elpris.eu/api/v1/prices/2026/05-24_SE3.json?avg24`
- date policy: before 14:00 local, fetched today
- KVS status: `ok`
- KVS area: `SE3`
- KVS price count: `12`
- final script status: installed and stopped
- memory pressure: no `out_of_memory` observed in bounded log/output
