# P0046 package consistency review

Status: PASS

P0046 is consistent with current repository truth and can proceed.

Evidence checked before editing:

- Repository was synchronized with `origin/main` before reading package files.
- P0046 package file exists at `requirements/packages/P0046-se1-anchored-absolute-price-backtest.md`.
- P0042, P0043, P0044 and P0045 package-run changelogs exist.
- P0045 status is PASS and its evidence selects `system_proxy_se1 = combined_scaled` as the deployable SE1 shape formula.
- P0045 evidence says P0046 may proceed as an anchored absolute-price backtest, not a production API.
- Existing code has a reusable Mac-only P0045 diagnostics module at `src/mac/services/spotprice_model_diagnostics/p0045.py`.
- Existing tests use package-scoped diagnostics tests under `tests/mac/services/spotprice_model_diagnostics/`.

Consistency result:

- PASS: P0046 is Mac-only historical evaluation and fits the established diagnostics package pattern.
- PASS: The required SE1-first path is available through P0045 regenerated predictions and `combined_scaled` shape construction.
- PASS: No package requirement needs Shelly, Home Assistant, KVS, live devices, production API, M5/M6/M7 or AI retraining.

Implementation assumptions:

- P0046 may import and reuse P0045 helpers to regenerate deterministic AI-1/AI-2 evaluation predictions from committed code and local corrected feature DB rows. This is reuse of the P0045 selected path, not new model development or hyperparameter search.
- The primary Monday 06:00 fixed-CET origin can be emulated by taking P0045 fixed-CET daily windows and rotating each accepted 168h window to start at local hour 06:00 when the next seven days are fully covered.
- Anchor scenarios use the first N hours after the forecast origin; all evaluation metrics exclude those N hours.

Safety review:

- Allowed changes are limited to Mac diagnostics code/tests/docs and P0046 package-run evidence.
- P0046 must not create any server/API, write KVS, access devices, touch Shelly/Home Assistant paths or train new model variants.
