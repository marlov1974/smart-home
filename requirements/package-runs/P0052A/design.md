# P0052A implementation design

## Package interpretation

P0052A amends P0052 by using the newly available ENTSO-E token to test and ingest internal Swedish border capacity/exchange/flow where possible. It must not expose the token or replace existing SvK/Statnett rows.

## Implementation structure

Create `src/mac/services/spotprice_model_diagnostics/p0052a.py` using Python standard library only.

The module will:

- load the token from environment or the local secret file without printing it,
- verify secret safety and repo status,
- build sanitized ENTSO-E API requests,
- parse ENTSO-E XML MarketDocument/Acknowledgement responses,
- ingest ENTSO-E rows into the existing P0052 long tables with `source_name = ENTSO-E Transparency Platform`,
- add/update wide-table columns for scheduled exchange, physical flow, directional capacity and utilization/margin where possible,
- write P0052A evidence under `requirements/package-runs/P0052A/`.

## Source strategy

Default live ingestion will use the already verified P0052 recent overlap:

```text
2026-05-01T00:00:00Z .. 2026-05-25T22:00:00Z
```

This is intentionally narrower than P0051's full period to keep the token-backed API run bounded while still overlapping P0051/P0052 rows. P0052A evidence will state that full historical backfill remains incomplete unless a later package expands the range.

Documents to ingest for internal Swedish borders:

- `A09`: scheduled commercial exchange candidate, stored as `scheduled_exchange_mw`.
- `A11`: physical flow candidate, stored as `physical_flow_mw`.
- `A61` with `contract_MarketAgreement.Type=A02`, `A03`, `A04`: capacity candidates, stored as `capacity_mw` with contract-specific capacity labels.

## Database changes

Reuse and extend:

- `transfer_capacity_flow_raw_v1`
- `transfer_capacity_flow_hourly_v1`
- `transfer_capacity_flow_se1_se4_hourly_v1`

The long tables will receive ENTSO-E rows with source identity in the natural key, preserving P0052 SvK/Statnett rows.

The wide table will be altered in place if missing columns for:

- `scheduled_exchange_se1_to_se2_mw`, `scheduled_exchange_se2_to_se1_mw`, etc.
- `physical_flow_se1_to_se2_mw`, `physical_flow_se2_to_se1_mw`, etc.
- directional internal capacity columns already exist in P0052; P0052A will fill them when compatible capacity exists.
- `flow_or_exchange_*`, `north_to_south_capacity_min`, utilization and bottleneck margin columns.

## Secret handling

Token source priority:

1. `ENTSOE_SECURITY_TOKEN`
2. `~/.smart-home/secrets/entsoe_transparency_token`

The token must never be written to evidence. Request URLs with tokens will not be logged. Errors will be represented by HTTP status and acknowledgement text only.

## Test strategy

Unit tests will cover:

- token loader shape without printing token,
- token masking helper,
- request parameter builder excluding token from evidence,
- EIC mapping for SE1-SE4,
- timestamp/fixed-CET derivation,
- ENTSO-E XML parser for success and acknowledgement responses,
- idempotent insertion into long tables,
- utilization null/zero handling,
- forbidden document/path checks.

Live verification will run the P0052A module with the local token and SQLite feature database. If the sandbox blocks network or database writes, rerun with approved escalation.

## Risks and uncertainties

- ENTSO-E document type names and capacity contract types are subtle; P0052A stores explicit labels and avoids silent concept mixing.
- `A61` contract type meaning may require later domain review before production modeling. P0052A can compute diagnostics but should keep forecast-safety conservative.
- Full P0051 historical backfill may require chunking/rate-limit management in a later package.
