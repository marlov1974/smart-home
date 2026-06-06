# P0054T2 Implementation Design

## Interpretation

P0054T2 must explain why P0054R's advanced no-price result was much better than P0054T's W0/P0 matrix result and why P0054T M1 equaled M2.

This package is diagnostic. The expected output is evidence and root cause, not a corrected full matrix.

## Implementation Structure

Add `src/mac/services/spotprice_model_diagnostics/p0054t2.py` as a package-scoped diagnostic runner.

The runner will:

- summarize required source evidence from P0054R and P0054T package-run files,
- build current P0054R no-price origin rows and current P0054T exact-origin rows,
- compute row/origin overlap metrics,
- inspect current model implementation semantics,
- run an R-like P0054R reproduction through `p0054r.run_p0054r_analysis` into a temporary evidence directory,
- run a minimal T-like W0/P0 reproduction inside the P0054T harness path,
- compare metrics and prediction distributions,
- write required P0054T2 evidence files.

## Intended Changes

Create:

- `src/mac/services/spotprice_model_diagnostics/p0054t2.py`
- `tests/mac/services/spotprice_model_diagnostics/test_p0054t2.py`
- `requirements/package-runs/P0054T2/**`

Update:

- `requirements/packages/P0054T2-labb-reproduce-p0054r-in-matrix-debug.md`
- `docs/functions/mac/spotprice-model-diagnostics.md`

## Deliberate Non-Changes

- Do not change P0054R or P0054T implementation in this package unless diagnostics prove a tiny package-scoped helper fix is required.
- Do not rewrite previous package-run evidence.
- Do not run or store a corrected 12-combination matrix.
- Do not use live APIs, devices, Nord Pool, workplace integration, A61, flow/exchange/capacity targets or the old physical-balance target.

## Test Strategy

Unit tests cover deterministic helper behavior:

- row/origin set diff summarization,
- M1/M2 alias decision summarization,
- prediction difference summary on compact synthetic rows.

Verification commands:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/p0054t2-pycache python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054t2
PYTHONPYCACHEPREFIX=/private/tmp/p0054t2-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0054t2
git diff --check
find requirements/package-runs/P0054T2 src/mac/services/spotprice_model_diagnostics tests/mac/services/spotprice_model_diagnostics docs/functions/mac -type f -size +1M -print
```

## Risks and Uncertainties

- Full P0054R reproduction may take several minutes.
- Optional ML libraries may be present or absent; diagnostics must record environment.
- Exact metrics may differ slightly from historic evidence if upstream helper code changed.
- P0054T no-price rows are currently coupled to P0054N exact-origin price coverage; this is expected to be a core difference.
