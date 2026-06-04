# P0054G Next Package Recommendation

Recommended next package:

```text
P0054H LABB rolling-origin SE1 anchored price forecast-origin log
```

Purpose:

- implement a forecast-origin-safe train-period SE1 price forecast log
- use rolling-origin, expanding-origin or blocked out-of-fold upstream shape training
- preserve P0053C global split semantics
- retain P0053C-B validation/holdout contract where possible
- produce a table suitable for a later P0054F retry

Only after that source exists should a package retry the SE1 consumption no-price vs with-price-forecast ablation.
