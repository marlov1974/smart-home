# P0054Q Implementation Design

## Interpretation

P0054Q reruns the P0054N-style SE3 DayAhead/full_36h experiment using the corrected ENTSO-E Actual Total Load target from P0054P2.

This package is LABB only. It does not deploy runtime code, touch devices, call live APIs, integrate Nord Pool/workplace systems or promote a G2 candidate.

## Implementation Structure

Create:

```text
src/mac/services/spotprice_model_diagnostics/p0054q.py
tests/mac/services/spotprice_model_diagnostics/test_p0054q.py
```

The module will:

1. Load SE3 target rows from `entsoe_consumption_area_hourly_v1`.
2. Normalize target rows into the existing P0054K/P0054N in-memory row contract.
3. Reuse P0054K weather/profile/model helpers.
4. Reuse P0054N exact DayAhead price feature and full_36h/DayAhead evaluation helpers where safe.
5. Add corrected-target percent and daily-energy metrics.
6. Write required P0054Q evidence.

## Intended Changes

- Add a corrected-target loader with explicit source contract.
- Add leakage validation that checks the persisted target source table and forbids old target names and flow/A61 columns.
- Add P0054Q evidence writers.
- Add durable function documentation to `docs/functions/mac/spotprice-model-diagnostics.md`.
- Mark the P0054Q package completed only after verification passes.

## Deliberate Reuse

P0054Q should reuse P0054N rather than copying model/evaluation logic. This keeps the comparison focused on target-source correction.

The in-memory target field remains `target_consumption_se3_mw` because existing helpers expect that field. Evidence must state that the persisted source is ENTSO-E `consumption_mw`, not the old physical-balance target.

## Test Strategy

Unit tests:

- target loader rejects missing table/area and maps ENTSO-E rows to P0054K-compatible fields
- source contract names `entsoe_consumption_area_hourly_v1.consumption_mw`
- leakage review rejects old physical-balance target names
- percent metric helper computes MAE percent of mean and median actual

Verification:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054q
PYTHONPYCACHEPREFIX=/private/tmp/p0054q-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0054q
sqlite3 /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3 target checks
git diff --check
```

## Risks

- Optional model packages may be missing or slow. Package allows WARN if required core results are still available.
- Weather remains an actual-as-forecast proxy, so production DayAhead claims remain blocked.
- The advanced-price branch must be skipped or WARN if exact-origin price rows cannot be built safely.

## Uncertainties

Final model ranking and percent error are unknown until the local run completes.
