# P0056H Comparison

| area | mode | baseline | rolling 36h MAE | delta % |
| --- | --- | ---: | ---: | ---: |
| SE1 | L1_origin_known_fallback | 123.509 | 172.754 | 39.872 |
| SE1 | L2_recursive_lags | 123.509 | 138.317 | 11.990 |
| SE2 | L1_origin_known_fallback | 197.547 | 307.044 | 55.428 |
| SE2 | L2_recursive_lags | 197.547 | 242.579 | 22.795 |
| SE3 | L1_origin_known_fallback | 250.928 | 638.040 | 154.272 |
| SE3 | L2_recursive_lags | 250.928 | 361.881 | 44.217 |
| FI | L1_origin_known_fallback | 311.189 | 612.830 | 96.932 |
| FI | L2_recursive_lags | 311.189 | 367.057 | 17.953 |
