# P0056A attempts

## Attempt 1

Implemented `p0056a.py` as a separate LABB ingestion module using ENTSO-E `A65` / `A16` actual total load and explicit area/EIC mapping for all 18 primary areas.

Verification:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0056a
PYTHONPYCACHEPREFIX=/private/tmp/p0056a-pycache /usr/bin/python3 -m py_compile src/mac/services/spotprice_model_diagnostics/p0056a.py tests/mac/services/spotprice_model_diagnostics/test_p0056a.py
PYTHONPYCACHEPREFIX=/private/tmp/p0056a-pycache /usr/bin/python3 -m src.mac.services.spotprice_model_diagnostics.p0056a
```

Result:

```text
tests: OK, 4 tests
compile: OK
package run: PASS
```

Package run output:

```text
area_catalog_rows: 18
native_rows: 1244180
hourly_rows: 632871
status: PASS
```

SQLite verification:

```text
area_consumption_area_catalog_v1: P0056A, 18
area_consumption_native_v1: P0056A, 1244180
area_consumption_hourly_v1: P0056A, 632871
```

SE3 consistency:

```text
overlap_rows: 35125
max_abs_delta_mw: 0.0
mean_abs_delta_mw: 0.0
```
