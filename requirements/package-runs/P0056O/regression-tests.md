# P0056O Regression Tests

- Recorded status: `PASS`
- Required tests are implemented in `tests/mac/test_p0056o_dayahead_dst_fix.py`.
- `PYTHONPYCACHEPREFIX=/private/tmp/p0056o-pycache python3 -m py_compile src/mac/services/spotprice_model_diagnostics/p0056k.py src/mac/services/spotprice_model_diagnostics/p0056l.py src/mac/services/spotprice_model_diagnostics/p0056m.py src/mac/services/spotprice_model_diagnostics/p0056n.py src/mac/services/spotprice_model_diagnostics/p0056o.py tests/mac/test_p0056o_dayahead_dst_fix.py tests/mac/test_p0056n_dst_audit.py tests/mac/test_p0056k_dayahead_protocol.py` passed.
- `PYTHONPYCACHEPREFIX=/private/tmp/p0056o-pycache python3 -m unittest tests.mac.test_p0056o_dayahead_dst_fix tests.mac.test_p0056n_dst_audit tests.mac.test_p0056k_dayahead_protocol` passed: 12 tests.
- `PYTHONPYCACHEPREFIX=/private/tmp/p0056o-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0056o` passed with package status `PASS`.
