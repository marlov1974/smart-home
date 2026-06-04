# P0053C Old Split Audit

## Scope Audited

- `requirements/package-runs/P0043/`
- `requirements/package-runs/P0044/`
- `requirements/package-runs/P0045/`
- `requirements/package-runs/P0053B/`
- `requirements/package-runs/P0053B-A/`
- `requirements/packages/P0043*`
- `requirements/packages/P0044*`
- `requirements/packages/P0045*`
- `requirements/packages/P0053B*`

## Findings

| Area | Old assumption found | Result |
| --- | --- | --- |
| P0043 | train earliest..2024-12-31, validate 2025, holdout 2026 | split-incompatible |
| P0044 | train earliest..2024-12-31, validate 2025, holdout 2026 | split-incompatible |
| P0045 | validation windows in 2025 and holdout windows in 2026 | split-incompatible |
| P0053B | train earliest..2024-12-31, validate 2025, holdout 2026 | rebuilt under P0053C policy |
| P0053B-A | STOP due missing forecast-origin price source | still valid as a source-safety conclusion |

## Source Search Evidence

The audit found explicit old split strings in:

```text
requirements/packages/P0043-train-ai2-hour-to-day-shape-model.md
requirements/packages/P0044-train-ai1-day-to-local-week-shape-scale-model.md
requirements/packages/P0045-combine-ai1-ai2-168h-shape-forecast.md
requirements/package-runs/P0043/training-split.md
requirements/package-runs/P0043/component-attribution-summary.md
requirements/package-runs/P0044/metrics-summary.json
requirements/package-runs/P0044/component-attribution-summary.md
requirements/package-runs/P0045/design.md
requirements/package-runs/P0053B/*
```

Old metric tables remain useful for historical traceability, but not for direct comparison to P0053C-and-later metrics.
