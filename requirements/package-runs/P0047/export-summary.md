# P0047 export summary

export_window = {'start': '2025-01-01', 'end': '2025-12-31'}
row_count = 8760
regeneration_command = `python3 -m src.mac.services.spotprice_model_diagnostics.p0047`

SE3-SE1 min/p01/p05/median/mean/p95/p99/max = -0.288740, -0.044425, -0.010630, 0.249630, 0.327542, 1.083767, 1.726652, 4.457907

regime_counts = {'spread_near_zero': 2340, 'spread_negative': 5, 'spread_positive': 4206, 'spread_small_nonzero': 1364, 'spread_spike_positive': 845}
regime_share = {'spread_near_zero': 0.2671232876712329, 'spread_negative': 0.0005707762557077625, 'spread_positive': 0.48013698630136986, 'spread_small_nonzero': 0.15570776255707763, 'spread_spike_positive': 0.09646118721461187}

Plots were not committed. P0047 uses committed tables/CSV/JSON to avoid adding image dependencies or large binary evidence.
