# P0044 overlap and leakage notes

AI-1 target rows use local windows D-2..D+4 over continuous `model_cet_date`, so adjacent rows overlap heavily and are not iid samples. Chronological validation and holdout are still used, but metrics should be read as model-selection diagnostics rather than independent-sample confidence estimates.

Local-window rank metrics use continuous date arithmetic and may cross calendar years. They require all seven window center dates to be present in the evaluated split, so windows adjacent to train/validate/holdout boundaries are skipped to avoid cross-split evaluation leakage. They are not skipped merely because they cross a calendar-year boundary.

Training features are time, Swedish calendar and weather-derived fields from the P0042 AI-1 dataset. P0044 does not use actual future spot prices, absolute day price, day ratio diagnostics, AI-2 predictions, combined forecast outputs or anchored absolute forecast errors as model features or targets.

Weather features are intended as forecast-time-known/proxy forecast-known inputs for the future AI-1 combination track. P0044 records this assumption but does not implement forecast ingestion.
