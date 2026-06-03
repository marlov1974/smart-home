# P0052B implementation design

## Package interpretation

P0052B should turn P0052A from a short proof into a safer historical source amendment. The package must not build a model or production API. It should document A61 concepts, backfill A09/A11/A61 where feasible, fix diagnostics joins and produce evidence that tells whether P0053 can start physical-regime modeling.

## Implementation structure

Add a new package module:

```text
src/mac/services/spotprice_model_diagnostics/p0052b.py
```

The module will reuse P0052A token loading, EIC mapping, request construction, HTTP fetch and XML parsing where practical. P0052B owns orchestration, metadata enrichment, schema migration, historical chunking, wide-row insertion/update, timestamp-normalized joins, diagnostics and evidence.

## Intended changes

- Re-verify token safety before any API call.
- Add required metadata columns to P0052 raw/hourly long tables if absent:
  - `document_type`
  - `process_type`
  - `business_type`
  - `contract_type`
  - `entsoe_curve_type`
  - `entsoe_resolution`
  - `capacity_concept_status`
- Preserve existing rows by adding nullable metadata columns and using existing source/dataset labels.
- Backfill representative windows first:
  - `2025-01-01T00:00:00Z .. 2025-12-31T23:00:00Z`
  - `2024-09-01T00:00:00Z .. 2024-12-31T23:00:00Z`
  - `2026-05-01T00:00:00Z .. 2026-05-25T22:00:00Z`
- Use safe chunks by month for A09/A11 and by requested window for A61, adjusting if live API behavior requires smaller chunks.
- Upsert long rows idempotently and update/create wide rows for ENTSO-E timestamps.
- Keep `timestamp_utc` stored in P0052B-generated transfer rows as `...Z`, but join by normalized epoch/time expression so `...+00:00` price rows still match.
- Compute diagnostics for scheduled exchange and physical flow. Capacity utilization and bottleneck margin remain blocked if concept status is uncertain.

## Deliberate refactoring decisions

- Do not rewrite P0052A in place. P0052B can import and wrap P0052A helpers to keep package ownership clear.
- Do not drop/recreate P0052 tables. P0052B performs additive schema migration and idempotent upserts to protect existing P0052/P0052A rows.
- Do not normalize older price-table timestamps in place; use normalized joins to avoid changing P0050 contract data.

## Test strategy

- Add `tests/mac/services/spotprice_model_diagnostics/test_p0052b.py`.
- Cover A61 contract concept mapping, metadata enrichment, schema migration, idempotent upsert, wide row creation for missing timestamps, normalized timestamp join, uncertain-capacity utilization behavior, and no price-document request.
- Run P0052A and P0052B unit tests plus the broader P0048-P0052B diagnostics suite.
- Run live P0052B ingestion if token safety passes.

## Evidence strategy

Write all required P0052B evidence files under:

```text
requirements/package-runs/P0052B/
```

Evidence must include source-contract counts, concept review, backfill range/chunk summary, join diagnosis, validation, diagnostics, forecast safety and next-package recommendation. It must not include token value or token-bearing URLs.

## Risks and uncertainties

- ENTSO-E may rate-limit or timeout full-year monthly chunks. P0052B will document failed chunks and may remain WARN.
- A61 capacity values may be long-term capacity contract products, not directly compatible with hourly scheduled exchange. Utilization/margin stays disabled unless proven safe.
- P0052 wide table initially had only P0052A recent timestamps. P0052B must insert new wide rows carefully with required base columns and null existing SvK fields.
