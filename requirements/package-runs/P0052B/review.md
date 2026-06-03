# P0052B consistency review

Status: WARN

## Repository truth checked

- P0052A package-run evidence exists and ended `verified WARN`.
- P0052A token handling evidence says the token source is a local secret file outside the repository, with directory mode `0700` and file mode `0600`.
- P0052A ingested ENTSO-E A09, A11 and A61 A02/A03/A04 for internal Swedish borders over `2026-05-01T00:00:00Z .. 2026-05-25T22:00:00Z`.
- Local SQLite has `transfer_capacity_flow_*` tables and `se3_se1_demand_response_analysis_v1`.
- The P0052A zero-row join is reproducible: transfer timestamps use `Z`, while the price diagnostic table uses `+00:00`.

## Official/API-local evidence

- ENTSO-E Transparency Platform API documentation lists `A09` as finalised schedule, `A11` as aggregated energy data report and `A61` as maximum possible.
- ENTSO-E `Contract_MarketAgreement.Type` / `ContractTypeList` defines `A02=Weekly`, `A03=Monthly` and `A04=Yearly`; those are contract horizons/procedures, not enough alone to prove production-safe utilization semantics.
- P0052A API-local evidence shows all three A61 contract types returned internal Swedish rows in the tested window.

## Consistency result

P0052B is consistent with repo state and package ordering. It is implementable as a data/contract/backfill package with conservative derived-feature handling.

## WARN reasons

- Full `2022-05-29T23:00:00Z .. 2026-05-25T22:00:00Z` token-backed backfill may be slow or rate-limited. The package explicitly permits representative windows if full range is not feasible.
- A61 A02/A03/A04 meanings can be documented as weekly/monthly/yearly capacity contract types, but production-intent utilization should remain blocked unless the package can prove compatibility with scheduled exchange or physical flow.
- The existing P0052/P0052A long-table schema does not include explicit ENTSO-E metadata columns yet, so P0052B must migrate carefully without dropping existing SvK/Statnett rows.

## Decision

Proceed with WARN. Keep token-safe handling, add metadata-compatible long-table migration, fix timestamp-normalized joins, perform bounded historical backfill, and keep utilization/margin null if A61 concept compatibility remains uncertain.
