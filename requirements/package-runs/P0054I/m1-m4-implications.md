# P0054I M1/M4 Implications

For the P0054 LABB comparison line, M1 and M4 results must be interpreted under this rule:

```text
train/fitting data ends before 2025-06-01T00:00:00Z
final holdout evaluation starts at 2025-06-01T00:00:00Z
```

Earlier M1/M4 packages that used the P0053C split remain historical evidence. P0054I does not rewrite them.

Future M1/M4 comparisons in this LABB line must be refit or regenerated under:

```text
LABB_P0054_TRAIN_THROUGH_MAY_2025
```

M4-specific note:

P0054H is not M4. It is a forecast-safe origin-local historical baseline. A future M4 rerun under the P0054I policy must not reuse the old P0053C-B metrics as if they were trained through May 2025.
