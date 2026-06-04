# P0054G Function Design

No functions are created, changed or removed in P0054G.

## Reason

The package stopped at consistency and leakage review. Generating train-period rows with the existing P0053C-B/P0045 functions would violate the forecast-origin cutoff contract because the upstream M4 shape model is trained on the full canonical train period.

## Future Function Needs

A future package that safely creates train-period forecast rows will likely need new or changed functions for:

| function area | purpose | safety requirement |
|---|---|---|
| origin selection | choose train/validation/holdout forecast origins under one cadence | deterministic and documented |
| origin-local AI1/AI2 fitting | train shape models using only rows available before each origin or blocked out-of-fold folds | no data after cutoff |
| anchor construction | reuse P0053C-B 48h anchor history logic | anchor timestamps strictly before origin |
| forecast log persistence | write train/validation/holdout rows with full origin metadata | schema compatible with P0054F retry |
| leakage audit | prove cutoff, origin, anchor and selection rules | fail closed |

Durable function catalog documentation was not changed because no function changed in this package.
