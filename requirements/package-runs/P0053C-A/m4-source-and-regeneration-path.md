# P0053C-A M4 Source And Regeneration Path

Used code paths:

```text
src/mac/services/spotprice_model_diagnostics/p0043.py
src/mac/services/spotprice_model_diagnostics/p0044.py
src/mac/services/spotprice_model_diagnostics/p0045.py
src/mac/services/spotprice_model_diagnostics/p0053ca.py
```

Dataset tables:

```text
ai1_day_to_local_week_training_targets_v2
ai2_hour_to_day_training_targets_v2
```

P0053C-A regenerates AI-1 and AI-2 predictions deterministically from the old selected P0043/P0044 feature policies, then applies the old P0045 combination formulas under the new P0053C split policy.

Output is price shape/index, not absolute price.
