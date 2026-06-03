# P0052A consistency review

Status: WARN

P0052A follows verified P0052 WARN evidence. P0052 created the transfer flow/import-export tables, did not ingest continental price levels, and documented ENTSO-E as blocked only because the security token was unavailable.

Secret review:

- The ENTSO-E token is present in a local file outside the repository under the user's home `.smart-home` secret area.
- The secret directory is not inside the git worktree, so it cannot appear in `git status` or be committed from this repository.
- Directory permissions were verified as owner-only and the token file as owner read/write only.
- This differs from the package wording that says the token is under a secret directory inside the `smart-home` working tree. The outside-repo location is safer and satisfies the package safety intent. Evidence must record this as `local_secret_file_outside_repo`, without the token value.

Source discovery review:

- Token-based ENTSO-E Transparency API calls succeeded without printing the token.
- Internal Swedish bidding-zone borders SE1-SE2, SE2-SE3 and SE3-SE4 returned data for `documentType=A09` and `documentType=A11`.
- `documentType=A61` required `contract_MarketAgreement.Type`; contract types `A02`, `A03` and `A04` returned data for internal Swedish borders in the tested 2025-01-01 window.
- Candidate document types `A26` and `A31` returned invalid/not-allowed responses for the tested parameters.

WARN reasons:

- P0052A is an amendment over already verified P0052 tables, and must preserve existing SvK/Statnett rows.
- ENTSO-E capacity concept labels must be kept explicit by contract type; concept comparability pre/post 2024-10-29 remains to be validated by evidence, not assumed.
- Full P0051 historical ingestion may be too slow in one package run; package scope allows a representative P0052 recent overlap or pre/post windows when documented.

Decision:

Proceed with a WARN implementation. Use the local token safely, ingest ENTSO-E `A09`, `A11` and `A61` for internal Swedish borders over the P0052 recent overlap by default, update P0052 long tables without overwriting SvK rows, update wide rows with scheduled exchange / physical flow / capacity fields, and document any missing range or concept uncertainty.

Forbidden work remains out of scope: no token leak, no continental price levels, no SE1-to-SE3 anchoring, no SE3 forecast model, no production API, no deployable model artifact, no Shelly/Home Assistant/KVS/device actions, no M5/M6/M7 and no futures.
