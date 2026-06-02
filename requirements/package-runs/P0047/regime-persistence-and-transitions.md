# P0047 regime persistence and transitions

lag1_same_regime_share = 0.818130

## Run Summary

| group | count | min | p05 | median | mean | p95 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| spread_near_zero | 343 | 1.000000 | 1.000000 | 5.000000 | 6.822157 | 17.900000 | 74.000000 |
| spread_negative | 2 | 2.000000 | 2.050000 | 2.500000 | 2.500000 | 2.950000 | 3.000000 |
| spread_positive | 537 | 1.000000 | 1.000000 | 6.000000 | 7.832402 | 21.000000 | 48.000000 |
| spread_small_nonzero | 533 | 1.000000 | 1.000000 | 2.000000 | 2.559099 | 8.000000 | 26.000000 |
| spread_spike_positive | 179 | 1.000000 | 1.000000 | 4.000000 | 4.720670 | 15.000000 | 45.000000 |

## Transition Matrix

| from \ to | spread_near_zero | spread_negative | spread_positive | spread_small_nonzero | spread_spike_positive |
|---|---:|---:|---:|---:|---:|
| spread_near_zero | 1997 | 0 | 105 | 236 | 2 |
| spread_negative | 0 | 3 | 1 | 1 | 0 |
| spread_positive | 72 | 0 | 3669 | 293 | 172 |
| spread_small_nonzero | 267 | 2 | 258 | 831 | 5 |
| spread_spike_positive | 3 | 0 | 173 | 3 | 666 |
