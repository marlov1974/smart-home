# P0042 area_diff scale root cause

`area_diff_proxy_se3 = SE3 - SE1` is often near zero or flat. Under P0041 the denominator could fall to `0.001`, so small centered spread changes divided by a tiny scale produced extreme targets.

Baseline AI-2 area_diff hour_shape: p01=-10.000000, p99=32.616033, max=230.000000, std=9.242008.

Selected policy AI-2 area_diff hour_shape: p01=-1.686771, p99=2.908536, max=16.973383, std=0.858910.
