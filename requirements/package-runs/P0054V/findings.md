# P0054V findings

Status: `STOP`

P0054V cannot be completed under its current gate because the current local P0054R no-price baseline no longer reproduces within the package's `<= 1.0 MW` tolerance from `253.70062353819162 MW`.

Current repeated reproduction:

```text
HorizonBiasCorrected_WeightedEnsemble_no_price DayAhead MAE = 252.4272878651775 MW
absolute delta from package target = 1.2733356730141168 MW
```

The row counts remain aligned with prior P0054T4 evidence:

```text
source_rows = 35125
direct_rows = 52173
path_rows = 52173
train_fit_rows = 38985
holdout_rows = 13188
internal_train_rows = 35675
internal_validation_rows = 3310
```

This suggests a reproducibility/data/environment drift issue, not a coverage shrink in the consumption row contract.

Recommended follow-up:

```text
Create P0054W to investigate and either freeze the P0054R/P0054T4 baseline reproducibility contract or deliberately update the P0054V baseline gate before running the full price-value test.
```
