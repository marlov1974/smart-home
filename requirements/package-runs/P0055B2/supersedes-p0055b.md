# P0055B2 supersedes P0055B

P0055B2 supersedes the original P0055B LABB run for interpretation under the operator clarification:

```text
requirements/packages/P0055B-operator-clarification-nonlinear-monotone-migration.md
```

P0055B remains useful as a historical baseline for the simple linear allocation attempt.

Primary current interpretation:

```text
WARN: cluster-specific migration is not safely readable.
```

Summary:

- All 11 required non-zero clusters were evaluated separately.
- All 11 required clusters failed observed monotone-enough readability.
- Weighted PAVA produced a diagnostic monotone fit without holdout reference or fit leakage.
- Normalized decomposition improved raw decomposition but remained worse than direct SE3.
