# P0037 design

## Package interpretation

P0037 must answer whether P0036 remains credible under a full-year 2025 holdout and attribute errors to M1, M3A, M3B and M4.

This is an analysis package. It may add reusable diagnostic code, but it must not promote a production model or build M5/M6/M7/API behavior.

## Split

Primary strict split:

```text
train:    2022-05-30..2023-12-31
validate: 2024-01-01..2024-12-31
holdout:  2025-01-01..2025-12-31
```

## Component fitting

- M1 is fit from train rows only using the established iso-week +/- 2, same weekday/hour median method.
- M2 climate normals for M3A anomaly buckets are fit from train rows only and applied to validate/holdout.
- M3A bucket deltas are fit from train residuals only and applied to all splits.
- M3B special-day deltas are fit from train special-day residuals only and applied to all splits.
- M4 HGB residual models are trained on train rows and selected by validate year 2024.

## Evaluation modes

Mode A: M3AB-normalized structural target.

```text
target = actual - strict_M3A - strict_M3B
variants = M1, M1 + M4
```

Mode B: observed reconstruction.

```text
target = actual
variants = M1, M1+M3A, M1+M3B, M1+M3A+M3B, M1+M4,
           M1+M3A+M4, M1+M3B+M4, M1+M3A+M3B+M4
```

## Evidence

The analysis writes the required P0037 Markdown files plus a concise JSON matrix. Large row-level predictions stay local/in memory and are not committed.

## Risk

Because 2025 is used as a full-year historical holdout and M5 is absent, M3A is only observed-weather attribution, not forecast deployability.
