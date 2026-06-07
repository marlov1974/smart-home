# P0055B2 nonlinear monotone fit review

```json
{
  "fit_allows_jumps_and_flats": true,
  "fit_constraint": "non_zero_profiled_clusters fitted non-decreasing by weighted PAVA; zero clusters forced zero; residual is remaining share",
  "fit_data": "train_fit_only",
  "fit_is_cluster_specific": true,
  "fit_is_nonlinear": true,
  "holdout_used_for_fit": false,
  "interpretation": "PAVA enforces a diagnostic monotone allocation curve; observed deltas remain the authority for readability.",
  "method": "cluster_specific_weighted_pava_non_decreasing_reference_latest_stable_train_fit_window",
  "observed_not_monotone_enough_clusters": [
    "C11",
    "C12",
    "C13",
    "C21",
    "C22",
    "C31",
    "C32",
    "C33",
    "C42",
    "C43",
    "C44"
  ],
  "observed_primary_signal_readable": false
}
```
