# P0054P2 Review

Status: `WARN`

## Consistency Result

P0054P2 is implementable within G2 LABB scope.

P0054P stopped correctly because external ENTSO-E fetch was forbidden. P0054P2 explicitly authorizes loading ENTSO-E actual load from 2022-06-01 onward, while preserving the boundary that flow/exchange/capacity data must not be used as consumption target.

## Repository Truth

Existing ENTSO-E rows in `transfer_capacity_flow_hourly_v1` are not load:

```text
A09 scheduled commercial exchange
A11 physical flow
A61 forecasted transfer capacity
```

Existing SE1-SE4 consumption rows in `physical_balance_hourly_raw_v1` and `physical_balance_se1_se4_hourly_v1` are from eSett Open Data, not ENTSO-E actual load.

P0052A already provides token-safe ENTSO-E request/parsing patterns, EIC bidding-zone mapping and secret handling.

## WARN Rationale

The exact ENTSO-E actual-load API contract must be verified live. The intended contract is:

```text
documentType = A65
processType = A16
outBiddingZone_Domain = SE1/SE2/SE3/SE4 EIC
```

If ENTSO-E rejects that contract or returns no actual-load rows, P0054P2 must STOP with sanitized API evidence.

## Safety

Allowed:

- token-backed ENTSO-E actual-load fetch
- local SQLite writes to the canonical target table
- compact package-run evidence

Forbidden:

- credentials in evidence
- flow/exchange/capacity as load target
- model retraining
- device/runtime/Nord Pool/workplace integration
- large raw export commits
