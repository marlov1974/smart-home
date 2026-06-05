# P0054L2 Runtime Policy

Long runtime is accepted. Models run one family at a time in this order: HGB, ExtraTrees, LightGBM, XGBoost, optional Ensemble. Each family writes a checkpoint before the next begins.
