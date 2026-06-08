# P0056I Consistency Review

## Classification

WARN

## Evidence Reviewed

- `requirements/packages/P0056I-labb-se2-train-window-sensitivity.md`
- `requirements/package-runs/P0056H2/area-summary-results.md`
- `requirements/package-runs/P0056H2/comparison-vs-static-baseline.md`
- `requirements/package-runs/P0056H/area-summary-results.md`
- `requirements/package-runs/P0056G/area-summary-results.md`
- `requirements/package-runs/P0056F/feature-ablation-results.md`
- `src/mac/services/spotprice_model_diagnostics/p0056h2.py`
- `memory/energy-market-ai-lab.md`

## Consistency Result

P0056I is consistent with repository truth and can be implemented as a narrow SE2-only LABB diagnostic.

The package's baseline values match the latest local evidence:

- P0056F SE2 W12 static full36: `197.547 MW`
- P0056H SE2 L2 recursive 36h: `242.579 MW`
- P0056H2 SE2 static-style 36h: `228.549 MW`
- P0056G SE2 weekly: `207.757 MW`

## Assumptions

- Use the same HGB no-price model method as P0056H2 to keep the only intended variable as training-window length.
- Use P0056H2 static-style origin-anchored lag construction and SE2 W12 feature stack.
- Use P0056D SE2 weather rows with the same `actual_weather_proxy_LABB` protocol as P0056H2.
- Rolling two-year and three-year windows are implemented by calendar-year subtraction from each forecast origin timestamp.

## Scope/Safety

No Shelly, Home Assistant, device, API, runtime, production, spot price, flow/exchange/A61/capacity or old physical_balance changes are needed.

The package may write local DB metrics tables for P0056I evidence only.
