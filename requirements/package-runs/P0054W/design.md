# P0054W design

Strategy: outer loop MGA, inner loop calendar month.

Reason: eSett `EXP18/LoadProfile` accepts one optional `mga` filter, and monthly chunks keep each request bounded while preserving native 15m/60m rows.

Tables:

- `esett_mga_masterdata_v1`
- `esett_mga_consumption_native_v1`
- `esett_mga_consumption_ingestion_checkpoint_v1`

Verification commands:

```bash
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054w tests.mac.services.spotprice_model_diagnostics.test_p0054w_esett_fetch
PYTHONPYCACHEPREFIX=/private/tmp/p0054w-pycache python3 -m py_compile src/mac/services/spotprice_model_diagnostics/p0054w.py src/mac/services/spotprice_model_diagnostics/p0054w_esett_fetch.py tests/mac/services/spotprice_model_diagnostics/test_p0054w.py tests/mac/services/spotprice_model_diagnostics/test_p0054w_esett_fetch.py
PYTHONPYCACHEPREFIX=/private/tmp/p0054w-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0054w_esett_fetch --mode full
git diff --check
```
