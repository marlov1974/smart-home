# P0043 component attribution summary

Status: PASS
1. Corrected dataset used: `ai2_hour_to_day_training_targets_v2`.
2. Split: train earliest..2024-12-31, validate 2025, holdout 2026.
3. SE1 winning group: F4_full.
4. area_diff winning group: F0_time_only.
system_proxy_se1: model_MAE=0.447322, B0_MAE=0.600354, spearman=0.648630.
area_diff_proxy_se3: model_MAE=0.483767, B0_MAE=0.510112, spearman=0.319550.
Weather delta and relative/rank feature effects are documented in `feature-ablation-results.md`.
AI-2 is ready for combination with future AI-1 if review accepts the metrics.
P0044 should train AI-1 next unless ChatGPT requests another AI-2 correction.
No AI-1 training, M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.
