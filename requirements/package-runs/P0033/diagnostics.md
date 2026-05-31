# P0033 diagnostics

Command:

```bash
python3 -m src.mac.services.spotprice_temperature_normalization diagnostics --feature-db /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
```

## Validation

```text
ok = true
start_date = 2022-05-30
end_date = 2026-05-24
row_count = 34944
count_mismatches = {}
missing_tables = []
```

## M1 residual summaries

```text
system_proxy_se1:
  count = 34944
  min = -1.16973625
  max = 5.915365
  mean = 0.12536943552541313
  stddev = 0.5204795860340544

area_diff_proxy_se3:
  count = 34944
  min = -0.9398050000000002
  max = 7.783650000000001
  mean = 0.20283137570112206
  stddev = 0.6297834051590987
```

## M2 anomaly summaries

```text
se1_system_temperature:
  min = -13.4007
  max = 10.648024999999999
  mean = -0.0975933872767844
  stddev = 3.356075908261852

se1_system_apparent_temperature:
  min = -14.258849999999997
  max = 10.774100000000004
  mean = -0.1511672597584696
  stddev = 3.7336976794452856

se1_system_heating_degree:
  min = -10.648024999999999
  max = 13.400700000000008
  mean = 0.2376739991128689
  stddev = 3.2010847481623914

se1_system_cooling_degree:
  min = 0.0
  max = 4.784850000000003
  mean = 0.022940695112179523
  stddev = 0.23018306746096673

se3_load_temperature:
  min = -15.968000000000002
  max = 10.017500000000002
  mean = -0.0851527300824181
  stddev = 3.0977667654093723

temp_gradient_se3_load_minus_se1_core:
  min = -16.1705
  max = 12.636
  mean = 0.11432054143772685
  stddev = 2.9844600100137355

apparent_temp_gradient_se3_load_minus_se1_core:
  min = -16.659000000000002
  max = 12.802500000000002
  mean = 0.189086037660257
  stddev = 3.260246070734163

heating_degree_gradient_se3_load_minus_se1_core:
  min = -12.636000000000003
  max = 16.1705
  mean = -0.19013395718864293
  stddev = 2.850683183513195

south_temp_gradient_minus_se1_core:
  min = -20.268
  max = 12.952499999999999
  mean = 0.10865494791666722
  stddev = 3.211077480232598
```

## M3 delta summaries

```text
system_proxy_se1:
  count = 34944
  min = -0.14330375
  max = 0.26243187500000004
  mean = 0.01221785717862497
  stddev = 0.06043749539600947

area_diff_proxy_se3:
  count = 34944
  min = -0.0011050000000000226
  max = 0.18590687500000003
  mean = 0.006181245635874052
  stddev = 0.020811992573350556
```

## Temperature association before/after

```text
system_proxy_se1:
  anomaly_signal = se1_system_temperature
  before_corr = -0.29503144999780184
  after_corr = -0.19968312245517977

area_diff_proxy_se3:
  anomaly_signal = temp_gradient_se3_load_minus_se1_core
  before_corr = -0.08089063808643632
  after_corr = -0.06124586918938008
```

Assessment: absolute residual association with the selected temperature anomaly decreased for both targets after M3.
