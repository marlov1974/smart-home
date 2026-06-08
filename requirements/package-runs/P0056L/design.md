# P0056L Implementation Design

## Package Interpretation

P0056L tests whether small neural models show enough SE2 realistic DayAhead upside to justify a larger neural package. It is LABB-only and not production promotion.

The package uses the P0056K DayAhead protocol:

- forecast origin: D-1 12:00 Europe/Stockholm
- delivery day: D 00:00..23:00 Europe/Stockholm
- train rows strictly before forecast origin
- weather protocol: `actual_weather_proxy_LABB`
- lag protocol: `DA-L3 seasonal_safe`

## Implementation Structure

Create `src/mac/services/spotprice_model_diagnostics/p0056l.py`.

The module will:

- load SE2 targets and P0056D weather rows from the existing feature DB
- reuse P0056K origin/rad construction
- select a deterministic representative origin subset
- run scikit-learn neural smoke models
- write package-run evidence and progress files

## Models

Implemented:

- `N1_TabularMLP`: `MLPRegressor` over the same tabular feature list as P0056K
- `N2_SequenceMLP_168h`: `MLPRegressor` over P0056K tabular features plus a 168 hour known-at-origin SE2 load window

Skipped:

- `N3_TCN_1D_CNN`: PyTorch is unavailable and no existing local TCN stack is present
- `N4_NBEATS_NHITS`: no supported local dependency and package forbids adding heavy dependencies

## Subset Policy

Use every fourth P0056K-valid SE2 origin, producing 60 origins from the 240-origin SE2 P0056K grid. This is a representative smoke subset across the full holdout period, but it is not a full fair origin set. Status is therefore `WARN`.

## Refactoring Decisions

No P0056K behavior will be changed. P0056L reuses P0056K helpers rather than modifying them.

## Test Strategy

- Unit tests verify subset selection, sequence feature naming and leakage terms.
- Run the P0056L module end-to-end.
- Run `py_compile`, unit tests and `git diff --check`.

## Risks and Uncertainties

- MLPRegressor may converge poorly on expanding, nonstationary load data.
- Reduced subset means neural results are smoke evidence only.
- P0056K baselines are aggregate full-origin baselines, not same-subset controls.
