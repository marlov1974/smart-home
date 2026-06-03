# P0052C implementation design

## Package interpretation

P0052C tests whether ENTSO-E A61 A02/A03/A04 capacity values behave like ceilings against A09 scheduled exchange and A11 physical flow. It does not enable utilization or bottleneck margin globally.

## Implementation structure

Add:

```text
src/mac/services/spotprice_model_diagnostics/p0052c.py
tests/mac/services/spotprice_model_diagnostics/test_p0052c.py
```

The module will read existing P0052B data from `transfer_capacity_flow_hourly_v1`, compute ratios by timestamp/border/direction/contract and write P0052C evidence.

## Data source

Use already ingested local ENTSO-E rows:

- A61 `capacity_mw` by `contract_type` A02/A03/A04
- A09 `scheduled_exchange_mw`
- A11 `physical_flow_mw`

No API fetch is planned because the local DB covers all required representative windows.

## Analysis method

For each required window, border direction, contract type and comparison type:

- Build the union of timestamps where either capacity or flow/exchange exists.
- Count missing capacity and missing flow/exchange.
- For rows with positive capacity and available flow/exchange, compute `abs(value) / capacity_mw`.
- Compute max, p50, p90, p95, p99 and violation counts above 1.00, 1.02, 1.05 and 1.10.
- Capture worst examples without secrets.
- Split metrics by pre/post 2024-10-29 flow-based era.

## Classification

Classify each contract type separately:

- `candidate_market_capacity_proxy` if scheduled exchange does not materially exceed capacity and overlap is meaningful.
- `not_capacity_ceiling_exchange_exceeds` if scheduled exchange materially exceeds capacity.
- `candidate_physical_capacity_proxy` only if physical flow also stays within capacity.
- `not_capacity_ceiling_flow_exceeds` if physical flow materially exceeds capacity.
- `insufficient_overlap` if compared rows are too sparse.

Even if a contract passes, recommendation remains experimental diagnostic proxy only until a later package accepts it.

## Test strategy

Unit tests cover timestamp normalization, ratio calculation with missing/zero capacity, per-contract grouping, worst-example sanitization and deterministic flow-based era split.

## Risks and uncertainties

- P0052B data may include partial rows from interrupted attempts. P0052C treats local rows as valid because P0052B validation passed and the DB integrity check was OK.
- A61 can pass a ceiling sanity check without proving publication timing or operational suitability. P0052C classification remains diagnostic, not production.
