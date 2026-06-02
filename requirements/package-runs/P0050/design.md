# P0050 implementation design

## Package interpretation

P0050 must test whether local SE3 price rank/top-N windows and cold/high-price heat-pump pressure explain future baseline-corrected SE3-SE1 residual behavior. It must correct raw spread for train-only expected spread baseline before interpreting day-type behavior.

## Input and output

Primary input:

```text
se3_se1_bottleneck_training_dataset_v1
```

Joined optional P0049 reservoir input:

```text
se3_se1_bottleneck_reservoir_analysis_v1
```

Derived output:

```text
se3_se1_demand_response_analysis_v1
```

The derived table is local diagnostics data in `~/.smart-home/data/spotprice_model_features.sqlite3`; no generated dataset file is committed.

## Implementation structure

Create `src/mac/services/spotprice_model_diagnostics/p0050.py` following the P0049 style:

- load and validate source rows
- fit train-only expected-spread baselines
- select one baseline for residual analysis using validation MAE with deterministic tie-breaking
- add day/48h local SE3 price-rank features
- add optimizer response features
- add heat-pump/cold-pressure features
- add future residual/spread targets
- persist a derived local analysis table
- write Markdown/CSV/JSON evidence under `requirements/package-runs/P0050/`

## Baseline strategy

Fit three train-only baselines:

- `B0_hour_weekday`: median spread by weekday/hour with global train median fallback
- `B1_hour_daytype_season`: median spread by hour/daytype/month with broader fallback
- `B2_smoothed_hour_daytype_dayofyear`: weighted median blend of day-of-year neighborhood, daytype/hour and global fallback

Select the lowest validation MAE baseline, with simpler baseline tie preference if MAE differs by less than 0.001.

## Price-rank strategy

Day ranks use complete fixed-CET model dates as explanatory behavioral features. Deterministic tie handling sorts by `(price, timestamp)` and assigns one-based ranks.

48h ranks use trailing 48h windows for deployable/causal-style features and also create explicitly labeled `oracle` same-window response diagnostics where package questions require full local-rank behavior. Forward-known fields are named with `oracle` and documented as not deployable.

## Heat-pump pressure strategy

Use `temperature_south_proxy_actual` as `temperature_south_or_se3_actual` and `temperature_south_proxy_delta` as `temperature_south_or_se3_delta_from_normal`.

Cold thresholds are train-only p25/p10. `heat_debt_pressure` accumulates cold intensity multiplied by local high-price pressure and is relieved by bottom-N cheap recovery hours.

## Evidence strategy

Write all required evidence files plus machine-readable summaries. `component-attribution-summary.md` must answer the package's 14 required questions explicitly.

## Tests

Add focused unit tests for:

- spread arithmetic and fixed-CET contract
- train-only baseline fitting and residual calculation
- deterministic rank/tie handling
- top-N and percentile flags
- backward-looking response counters
- oracle labels
- heat-pump pressure formula reproducibility
- chronological split validation
- forbidden path constants

## Deliberate non-changes

Do not alter P0048/P0049 implementation. Do not build production APIs, deploy artifacts, models, or device integrations. Do not use external packages.

## Uncertainty

Effect sizes may be suggestive rather than decisive. That is allowed by P0050 WARN criteria, provided the package produces the requested diagnostics and explicit recommendation.
