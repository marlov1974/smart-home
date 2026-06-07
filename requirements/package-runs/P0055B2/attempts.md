# P0055B2 attempts

## Attempt 1

Implemented a separate P0055B2 redo module and tests.

Verification:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0055b2 tests.mac.services.spotprice_model_diagnostics.test_p0055b
```

Result:

```text
Ran 8 tests in 0.002s
OK
```

Full package command initially failed in the escalated environment because `python3` resolved to an interpreter without `numpy`.

## Attempt 2

Verified that `/usr/bin/python3` sees the user-installed `numpy 2.0.2` and `scikit-learn 1.6.1`, then ran:

```text
PYTHONPYCACHEPREFIX=/private/tmp/p0055b2-pycache /usr/bin/python3 -m src.mac.services.spotprice_model_diagnostics.p0055b2
```

Result:

```text
status = WARN
aligned_hours = 22709
monthly_allocation_rows = 561
normalized_component_rows = 386053
forecast_component_count = 17
normalized_decomposition_rows = 33582
```

Finding:

The first successful run revealed reused P0055B normalization helpers left normalized hourly DB rows stamped as `generated_by_package = P0055B`.

## Attempt 3

Fixed P0055B2 to restamp normalized rows and normalization validation rows before DB persistence. Also compacted large evidence output.

Verification:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0055b2 tests.mac.services.spotprice_model_diagnostics.test_p0055b
PYTHONPYCACHEPREFIX=/private/tmp/p0055b2-pycache /usr/bin/python3 -m src.mac.services.spotprice_model_diagnostics.p0055b2
PYTHONPYCACHEPREFIX=/private/tmp/p0055b2-pycache /usr/bin/python3 -m py_compile src/mac/services/spotprice_model_diagnostics/p0055b2.py tests/mac/services/spotprice_model_diagnostics/test_p0055b2.py
```

Results:

```text
tests: OK, 8 tests
package run: WARN
compile: OK
```

SQLite generated-package verification:

```text
se3_component_monthly_allocation_v1: P0055B2, 561
se3_profiled_cluster_normalized_hourly_v1: P0055B2, 363344
se3_residual_normalized_hourly_v1: P0055B2, 22709
se3_normalized_decomposition_hourly_v1: P0055B2, 22709
```

Known non-blocking warning:

```text
sklearn UserWarning: X does not have valid feature names, but LGBMRegressor was fitted with feature names
```

This warning also appears in prior LABB model runs and did not stop scoring.
