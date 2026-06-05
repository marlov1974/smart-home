# Attempts

## Attempt 1

Command:

```text
PYTHONPYCACHEPREFIX=/private/tmp/p0054q-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0054q
```

Result: failed before analysis because shell `python3` resolved to Homebrew Python 3.12, which did not have the local ML stack installed.

## Attempt 2

Command:

```text
/usr/bin/python3 -m src.mac.services.spotprice_model_diagnostics.p0054q
```

Result: PASS.

Runtime note: the full model matrix took longer than initial expectation because the corrected ENTSO-E target is about 2.4x the old target scale and the full local model set was run. The process completed before any manual termination was needed.
