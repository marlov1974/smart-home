# P0039 sequential residual contract

```text
M1B = holiday-clean baseline
M3A target = actual - M1B
M3B target = actual - M1B - M3A
M3C target = actual - M1B - M3A - M3B
M3D target = actual - M1B - M3A - M3B - M3C
M4 target = actual - M1B - M3A - M3B - M3C - M3D
```

P0039 implements M1B, M3A_m1b and M3B_m1b. M3C_m1b, M3D_m1b and M4_m1b are documented contracts for future packages and are not promoted here.
