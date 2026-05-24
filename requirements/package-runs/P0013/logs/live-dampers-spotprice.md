# P0013 Live Dampers Spotprice Log

## Attempt 1

Command:

```bash
python3 -m src.mac.tools.shelly_live deploy-spotprice --base-url http://192.168.86.240:8030/ --script build/shelly/spotprice/spotprice_v0_9_0.js --expect spotprice --upload-chunk-bytes 1500 --log-timeout 30 --kvs-timeout 30
```

Output:

```text
target=http://192.168.86.240:8030
script=spotprice_v0_9_0 id=1
cleaned_hello=false
upload_chunk_bytes=1500
upload_chunk_count=4
before_scripts=[{"id":1,"name":"spotprice_v0_9_0","enable":false,"running":false}]
after_scripts=[{"id":1,"name":"spotprice_v0_9_0","enable":false,"running":false}]
kvs_summary={"area":"SE3","date":"2026-05-24","price_count":12,"price_max":1.692,"price_min":0.69,"status":"ok","updated":"2026-05-24T07:59:10"}
kvs_values_begin
{"hp.price.2h":"1.07,0.993,0.977,1.037,0.89,0.794,0.698,0.69,0.835,1.533,1.692,1.619","hp.price.area":"SE3","hp.price.date":"2026-05-24","hp.price.status":"ok","hp.price.updated":"2026-05-24T07:59:10"}
kvs_values_end
log_excerpt_begin
5571 [May 24 07:59:06.413] I shelly_debug.cpp:236    Streaming logs to 192.168.86.38:51909
5572 [May 24 07:59:06.701] I shos_rpc_inst.c:243     Script.Start [1@] via HTTP_in POST 192.168.86.38:51910
5573 [May 24 07:59:06.702] I shelly_user_script.:203 JS RAM stat: initial: 111400 after: 111360, used: 40
5574 [May 24 07:59:06.702] I spotprice_v0_9_0 GET https://se.elpris.eu/api/v1/prices/2026/05-24_SE3.json?avg24
log_excerpt_end
```

Final live state: `spotprice_v0_9_0` installed and stopped on dampers. Corrected P0013 KVS values present with `status=ok`.
