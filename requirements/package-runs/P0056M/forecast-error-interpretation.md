# P0056M Forecast Error Interpretation

## Context

This note stores the post-run interpretation of why SE2 M6 realistic DayAhead forecasts fail on the worst cases. It is an interpretation of the committed P0056M evidence, not a new model run.

## Primary interpretation

The main problem does not look like "use a stronger regressor" as the first fix. The evidence points to missing regime and target-quality understanding.

The model is broadly mean-reverting:

- high-load days: `322.868903` MW MAE, `-214.221078` MW bias
- low-load days: `188.379106` MW MAE, `+69.540848` MW bias
- high-ramp days: `324.748433` MW MAE
- low-ramp days: `162.075323` MW MAE

When SE2 load jumps high, M6 underforecasts. When load is low, M6 tends to overforecast. That means the current feature set does not tell the model strongly enough which load regime the next delivery day belongs to.

## Strongest anomaly

The strongest red flag is delivery day `2026-03-28`.

Observed P0056M day-level values:

```text
delivery_date = 2026-03-28
mean_actual_load_mw = 5487.607639
mean_forecast_load_mw = 1800.414999
hourly_MAE = 3708.638703
bias_mw = -3687.192640
daily_energy_error_percent = 67.191259
largest_error_mw = -5459.048777
```

Neighboring day-level means from P0056M:

```text
2026-03-25 mean_actual_load_mw = 1827.781250
2026-03-26 mean_actual_load_mw = 2224.083333
2026-03-27 mean_actual_load_mw = 1829.590278
2026-03-28 mean_actual_load_mw = 5487.607639
2026-03-29 mean_actual_load_mw = 1822.520833
2026-03-30 mean_actual_load_mw = 1929.916667
2026-03-31 mean_actual_load_mw = 1984.621528
```

This looks more like a target-data anomaly, target-definition shift or source-quality issue than an ordinary forecast miss. If the actual load is correct, then the system lacks a forecast-safe signal for a massive SE2 load-regime jump. If it is not correct, the model is being scored against a bad target row.

The next package should audit this date before model changes.

## Likely missing information

### 1. Target QA and outlier policy

The first missing layer is target-quality diagnostics for extreme actual-load days. Before improving the model, verify raw/native rows, input row counts, source resolution and source definition around extreme days such as `2026-03-28` and the December worst cases.

### 2. Industrial load and holiday/weekend regime

The worst tests are concentrated in winter, weekend/holiday-adjacent periods and high-ramp days. For SE2, industrial operating schedules, shutdowns, restarts and holiday bridge effects are likely important. Ordinary calendar and weather features are not enough to infer these regimes.

### 3. Stronger forecast-safe state at origin

P0056K uses origin-safe lags and weekly seasonal lags, but the slice evidence suggests it still underrepresents recent state changes. Candidate improvements should remain forecast-safe and focus on:

- recent origin-level load level
- recent ramp direction
- multi-day load trend
- deviation from same-week and same-season normal
- high-load/high-ramp regime flags

### 4. Regime-specific correction

M6 uses a weighted ensemble with broad historical weighting. The evidence suggests a single global correction is too blunt. The next model package should test targeted corrections for high-load, high-ramp, winter and weekend/holiday regimes before broad architecture changes.

### 5. DST and local-day audit

P0056M hour rows around `2026-03-29` show duplicate-looking local-time/DST behavior in the compact CSV. This does not explain the `2026-03-28` extreme, but the DayAhead local-day construction should be audited for 23/25-hour days and duplicate target rows before any production-grade interpretation.

## Recommended next package

Recommended next step:

```text
P0056N: SE2 target anomaly, DST and high-ramp audit before model changes.
```

Minimum scope:

- audit `2026-03-25..2026-03-31`
- audit December worst cases from P0056M
- verify raw target source rows, native resolution, aggregation count and duplicate target timestamps
- separate target/data anomalies from real load-regime failures
- rerun clean error slices after excluding or labeling confirmed target anomalies
- only then test targeted high-load/high-ramp/winter/weekend corrections

## Safety

This interpretation does not authorize model promotion or runtime use. It remains LABB-only.
