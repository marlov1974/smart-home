# P0039 changelog

- Added holiday-clean M1B diagnostics and strict train-only M1B-trained M3A/M3B chain.
- Corrected P0039 follow-up: M1B is a training/normalization base only; holdout chains apply M1B-trained deltas on the M1 baseplate.
- Added P0039 taxonomy and sequential residual evidence.
- Added local feature DB output tables with M1B-suffixed names.
- Deferred M3C_m1b, M3D_m1b and M4_m1b implementation to future packages; P0039 documents their target contract.
- No M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.
