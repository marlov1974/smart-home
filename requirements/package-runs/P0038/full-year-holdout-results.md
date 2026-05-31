# P0038 full-year holdout results

| variant | target | MAE | RMSE | signed_error | MAE_delta_vs_m3ab | MAE_delta_vs_previous |
|---|---|---:|---:|---:|---:|---:|
| M1+M3A+M3B | system_proxy_se1 | 0.357918 | 0.456056 | 0.268534 | 0.000000 | 0.000000 |
| M1+M3A+M3B | area_diff_proxy_se3 | 0.324534 | 0.488748 | -0.218325 | 0.000000 | 0.000000 |
| M1+M3A+M3B | recomposed_se3 | 0.373992 | 0.508448 | 0.050210 | 0.000000 | 0.000000 |
| M1+M3A+M3B+M3C | system_proxy_se1 | 0.358306 | 0.456391 | 0.268945 | 0.000388 | 0.000388 |
| M1+M3A+M3B+M3C | area_diff_proxy_se3 | 0.324534 | 0.488748 | -0.218325 | 0.000000 | 0.000000 |
| M1+M3A+M3B+M3C | recomposed_se3 | 0.374421 | 0.508737 | 0.050620 | 0.000429 | 0.000429 |
| M1+M3A+M3B+M3C+M3D | system_proxy_se1 | 0.366869 | 0.463078 | 0.289768 | 0.008952 | 0.008564 |
| M1+M3A+M3B+M3C+M3D | area_diff_proxy_se3 | 0.324534 | 0.488748 | -0.218325 | 0.000000 | 0.000000 |
| M1+M3A+M3B+M3C+M3D | recomposed_se3 | 0.369620 | 0.502778 | 0.071443 | -0.004372 | -0.004801 |
| M1+M3A+M3B+M3C+M3D+M4_area_diff_only | system_proxy_se1 | 0.366869 | 0.463078 | 0.289768 | 0.008952 | 0.000000 |
| M1+M3A+M3B+M3C+M3D+M4_area_diff_only | area_diff_proxy_se3 | 0.307230 | 0.465271 | -0.171653 | -0.017304 | -0.017304 |
| M1+M3A+M3B+M3C+M3D+M4_area_diff_only | recomposed_se3 | 0.385883 | 0.518460 | 0.118116 | 0.011891 | 0.016263 |
| M1+M3A+M3B+M3C+M3D+M4_SE1_and_area_diff_diagnostic | system_proxy_se1 | 0.366869 | 0.463078 | 0.289768 | 0.008952 | 0.000000 |
| M1+M3A+M3B+M3C+M3D+M4_SE1_and_area_diff_diagnostic | area_diff_proxy_se3 | 0.307230 | 0.465271 | -0.171653 | -0.017304 | 0.000000 |
| M1+M3A+M3B+M3C+M3D+M4_SE1_and_area_diff_diagnostic | recomposed_se3 | 0.385883 | 0.518460 | 0.118116 | 0.011891 | 0.000000 |
