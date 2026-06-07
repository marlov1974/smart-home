# P0055B stale after P0055B2

P0055B metrics and allocation-normalization evidence are stale for the operator's updated nonlinear monotone clarification.

Use P0055B only as historical baseline for the first linear train-fit allocation attempt.

Current redo:

```text
requirements/package-runs/P0055B2/
```

Reason:

- P0055B used a simple train-fit linear monthly share model.
- The operator clarification requires cluster-specific nonlinear monotone migration evaluation.
- P0055B2 re-ran the package as a forward-moving redo with weighted PAVA monotone cluster fits, latest train-fit reference window and explicit per-cluster delta evidence.
