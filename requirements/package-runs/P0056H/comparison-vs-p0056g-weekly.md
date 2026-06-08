# P0056H Comparison

| area | mode | baseline | rolling 36h MAE | delta % |
| --- | --- | ---: | ---: | ---: |
| SE1 | L1_origin_known_fallback | 131.253 | 172.754 | 31.619 |
| SE1 | L2_recursive_lags | 131.253 | 138.317 | 5.382 |
| SE2 | L1_origin_known_fallback | 207.757 | 307.044 | 47.790 |
| SE2 | L2_recursive_lags | 207.757 | 242.579 | 16.761 |
| SE3 | L1_origin_known_fallback | 282.365 | 638.040 | 125.963 |
| SE3 | L2_recursive_lags | 282.365 | 361.881 | 28.161 |
| FI | L1_origin_known_fallback | 422.324 | 612.830 | 45.109 |
| FI | L2_recursive_lags | 422.324 | 367.057 | -13.086 |
