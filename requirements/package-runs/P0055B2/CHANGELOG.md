# P0055B2 changelog

Status: `WARN`

- Rebuilt P0055B as a forward-moving redo under the operator nonlinear monotone clarification.
- Used cluster-specific weighted PAVA monotone train-fit allocation curves and latest stable train-fit reference window.
- Wrote local DB tables for monthly allocation and normalized component series with `generated_by_package = P0055B2`.
- Normalized decomposition delta vs direct DayAhead MAE: `3.498063611370563` percent.
- Normalized decomposition delta vs raw decomposition DayAhead MAE: `-8.101025030247728` percent.
- No API, devices, runtime writes, spot-price features, old physical_balance target, flow/A61/capacity features, model binaries or large raw prediction dumps.
