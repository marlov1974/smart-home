# P0047 spike and outlier review

| timestamp_utc | model_day | hour | se1 | se3 | spread | regime | wind | special_day_type |
|---|---|---:|---:|---:|---:|---|---:|---|
| 2025-10-14T16:00:00+00:00 | 2025-10-14 | 17 | 0.094823 | 4.552730 | 4.457907 | spread_spike_positive | 0.835331 | normal_weekday |
| 2025-10-14T17:00:00+00:00 | 2025-10-14 | 18 | 0.089258 | 4.381298 | 4.292040 | spread_spike_positive | 1.000000 | normal_weekday |
| 2025-01-20T07:00:00+00:00 | 2025-01-20 | 8 | 0.770490 | 4.542140 | 3.771650 | spread_spike_positive | 0.942564 | normal_weekday |
| 2025-01-20T15:00:00+00:00 | 2025-01-20 | 16 | 0.119850 | 3.771300 | 3.651450 | spread_spike_positive | 1.000000 | normal_weekday |
| 2025-01-20T16:00:00+00:00 | 2025-01-20 | 17 | 0.106340 | 3.752940 | 3.646600 | spread_spike_positive | 1.000000 | normal_weekday |
| 2025-01-15T07:00:00+00:00 | 2025-01-15 | 8 | 0.027630 | 3.485500 | 3.457870 | spread_spike_positive | 0.750000 | normal_weekday |
| 2025-10-02T17:00:00+00:00 | 2025-10-02 | 18 | -0.817205 | 2.471960 | 3.289165 | spread_spike_positive | 0.529600 | normal_weekday |
| 2025-11-25T16:00:00+00:00 | 2025-11-25 | 17 | 0.474108 | 3.665000 | 3.190892 | spread_spike_positive | 0.838849 | normal_weekday |
| 2025-11-25T15:00:00+00:00 | 2025-11-25 | 16 | 0.488142 | 3.667172 | 3.179030 | spread_spike_positive | 0.851992 | normal_weekday |
| 2025-02-14T16:00:00+00:00 | 2025-02-14 | 17 | 0.159460 | 3.294550 | 3.135090 | spread_spike_positive | 0.864046 | normal_weekday |
| 2025-10-02T16:00:00+00:00 | 2025-10-02 | 17 | -0.711210 | 2.373795 | 3.085005 | spread_spike_positive | 0.516815 | normal_weekday |
| 2025-09-09T17:00:00+00:00 | 2025-09-09 | 18 | 0.096530 | 3.142590 | 3.046060 | spread_spike_positive | 1.000000 | normal_weekday |
| 2025-02-14T17:00:00+00:00 | 2025-02-14 | 18 | 0.147270 | 3.093900 | 2.946630 | spread_spike_positive | 1.000000 | normal_weekday |
| 2025-01-20T14:00:00+00:00 | 2025-01-20 | 15 | 0.268450 | 3.172730 | 2.904280 | spread_spike_positive | 0.932250 | normal_weekday |
| 2025-11-25T11:00:00+00:00 | 2025-11-25 | 12 | 0.456885 | 3.325255 | 2.868370 | spread_spike_positive | 0.859024 | normal_weekday |
| 2025-11-25T07:00:00+00:00 | 2025-11-25 | 8 | 0.476118 | 3.306818 | 2.830700 | spread_spike_positive | 0.975824 | normal_weekday |
| 2025-10-01T17:00:00+00:00 | 2025-10-01 | 18 | 0.372245 | 3.123397 | 2.751152 | spread_spike_positive | 0.281900 | normal_weekday |
| 2025-10-15T06:00:00+00:00 | 2025-10-15 | 7 | 0.070775 | 2.772413 | 2.701638 | spread_spike_positive | 0.750992 | normal_weekday |
| 2025-10-15T05:00:00+00:00 | 2025-10-15 | 6 | 0.066227 | 2.734930 | 2.668702 | spread_spike_positive | 0.776793 | normal_weekday |
| 2025-11-25T10:00:00+00:00 | 2025-11-25 | 11 | 0.461477 | 3.118275 | 2.656798 | spread_spike_positive | 0.917480 | normal_weekday |
| 2025-05-13T18:00:00+00:00 | 2025-05-13 | 19 | -0.367520 | 2.259280 | 2.626800 | spread_spike_positive | 0.813509 | normal_weekday |
| 2025-10-07T06:00:00+00:00 | 2025-10-07 | 7 | 0.085815 | 2.678260 | 2.592445 | spread_spike_positive | 0.439858 | normal_weekday |
| 2025-01-20T06:00:00+00:00 | 2025-01-20 | 7 | 0.235430 | 2.826340 | 2.590910 | spread_spike_positive | 0.835750 | normal_weekday |
| 2025-11-25T08:00:00+00:00 | 2025-11-25 | 9 | 0.454132 | 3.044723 | 2.590590 | spread_spike_positive | 0.947863 | normal_weekday |
| 2025-10-14T15:00:00+00:00 | 2025-10-14 | 16 | 0.222037 | 2.798130 | 2.576092 | spread_spike_positive | 0.651294 | normal_weekday |

Top spike rows are also written to `top-spike-hours.csv`.
