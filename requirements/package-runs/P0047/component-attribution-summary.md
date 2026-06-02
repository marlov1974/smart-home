# P0047 component attribution summary

Status: PASS
1. Exported fixed-CET window 2025-01-01 .. 2025-12-31 with 8760 rows.
2. SE3-SE1 median=0.249630, mean=0.327542, p95=1.083767, p99=1.726652, max=4.457907.
3. Near-zero share=0.267123; positive bottleneck share=0.576598; negative bottleneck share=0.000571.
4. Lag-1 same-regime share=0.818130.
5. Weather gradients requested by P0047 are not available in the AI2 v2 table; available system proxies are reported.
6. Recommendation: next package should compare two-stage bottleneck classification+severity against direct SE3 AI-1/AI-2 modeling.
7. Confirmed: no SE1-to-SE3 anchoring, no API, no production model, no M5/M6/M7 and no device actions.
