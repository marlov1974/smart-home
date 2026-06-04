# P0054J Changelog

- Built SE1 consumption modeling rows under `LABB_P0054_TRAIN_THROUGH_MAY_2025`.
- Trained paired no-price and with-P0054H-price-forecast models for HGB, ExtraTrees, LightGBM and XGBoost.
- Used identical row sets for every no-price vs with-price model family.
- Skipped MLP by design because it is optional and the required tree/boosting families ran.
- Wrote direct, weekly path, conditional, ablation and feature-importance evidence.
- No actual future spot price, P0053C-B train feature, production/export/import/A61/future-flow, live API, device or runtime path was used.

Result status: PASS.
