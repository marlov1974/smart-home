# P0047 consistency review

Status: PASS

P0047 is consistent with repository state and previous package evidence.

## Evidence checked

- `requirements/packages/P0047-se3-se1-bottleneck-data-export-and-model-design.md`
- `requirements/package-runs/P0046/CHANGELOG.md`
- `requirements/package-runs/P0046/dataset-contract.md`
- `requirements/package-runs/P0046/area-diff-diagnostics.md`
- `src/mac/services/spotprice_model_diagnostics/p0042.py`
- `src/mac/services/spotprice_model_diagnostics/p0045.py`
- `src/mac/services/spotprice_model_diagnostics/p0046.py`
- local feature DB table `ai2_hour_to_day_training_targets_v2`

## Consistency result

P0046 selected an SE1-only anchored absolute-price path and kept `area_diff_proxy_se3` diagnostic. P0047 explicitly pauses the API/anchoring path and asks for raw `SE3-SE1` spread export plus bottleneck/regime analysis. That is consistent with P0046 evidence.

The local corrected P0042 fixed-CET table exists and contains both:

```text
system_proxy_se1      2022-05-30 .. 2026-05-25
area_diff_proxy_se3   2022-05-30 .. 2026-05-25
```

The preferred export window `2025-01-01 .. 2025-12-31` is a complete fixed-CET model-year slice and is inside the available dataset.

## Assumptions

- `area_diff_proxy_se3.hour_price` is the repository's current `SE3 - SE1` target, as documented by P0042/P0045/P0046.
- `se3_price` in the export can be reconstructed as `system_proxy_se1.hour_price + area_diff_proxy_se3.hour_price`.
- Some requested north/south/central weather gradient fields are not present in the committed AI2 v2 table. P0047 may document them as missing rather than rebuilding the full P0042 source pipeline.

## Safety and scope

No live device access is needed or allowed. No Shelly, Home Assistant, KVS, forecast API, M5/M6/M7, production model, or SE1-to-SE3 anchoring work is required.

## Classification

PASS. Continue with package-scoped diagnostic implementation and evidence generation.
