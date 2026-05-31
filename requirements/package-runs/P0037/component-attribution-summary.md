# P0037 component attribution summary

Status: WARN

## Required answers

1. M3A improves full-year observed reconstruction versus M1: helps (0.379889 vs 0.387574).
2. M3A temperature-correlation details are in `m3a-temperature-attribution.md`.
3. M3A extreme bucket over/under-correction is shown by bucket signed error in `m3a-temperature-attribution.md`.
4. M3B improves special-day hours versus M1: helps (0.403284 vs 0.457370).
5. M3B hurts non-special-day hours: no material change (0.382662 vs 0.382662).
6. M4 improves M3AB-normalized structural target versus train-only M1: hurts/no improvement (0.392919 vs 0.376549). Area_diff: helps (0.307435 vs 0.324534). SE1: hurts/no improvement (0.363589 vs 0.362448).
7. P0036 PASS remains valid under full-year holdout: no.
8. Most suspect remaining component/error source: remaining recomposed SE3 observed MAE 0.392919; inspect largest SE1/area spikes and M4-worsened rows.
9. Concentration by temperature/special-day subsets is in the attribution files.
10. P0036 is diagnostic-PASS for full-year structural M4 if item 7 is yes; otherwise treat as WARN.

No M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.
