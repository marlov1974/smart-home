# P0055A changelog

Status: `PASS`

- Built LABB direct-vs-decomposition SE3 consumption forecast comparison.
- Direct model: `HorizonBiasCorrected_WeightedEnsemble_no_price` no-price contract.
- Component forecasts: `18` including direct, 16 clusters and calculated residual.
- Decomposition delta vs direct DayAhead MAE: `12.62156476221414` percent.
- Reconciled delta vs direct DayAhead MAE: `12.622418467491874` percent.
- No API, devices, runtime writes, spot-price features, old physical_balance target, flow/A61/capacity features, model binaries or large raw prediction dumps.
