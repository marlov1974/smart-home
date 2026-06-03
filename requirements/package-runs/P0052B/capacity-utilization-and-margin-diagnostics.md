# P0052B capacity/utilization and margin diagnostics

```json
{
  "columns": [
    "scheduled_exchange_se2_to_se3_mw",
    "scheduled_exchange_se3_to_se4_mw",
    "physical_flow_se2_to_se3_mw",
    "physical_flow_se3_to_se4_mw"
  ],
  "correlations": {
    "se3_minus_se1_vs_physical_flow_se2_to_se3_mw": 0.38412719744105916,
    "se3_minus_se1_vs_physical_flow_se3_to_se4_mw": 0.27973232818142946,
    "se3_minus_se1_vs_scheduled_exchange_se2_to_se3_mw": 0.42565969140971466,
    "se3_minus_se1_vs_scheduled_exchange_se3_to_se4_mw": 0.3029315165538603,
    "se3_price_vs_physical_flow_se2_to_se3_mw": 0.41571351461496286,
    "se3_price_vs_physical_flow_se3_to_se4_mw": 0.2558203018170429,
    "se3_price_vs_scheduled_exchange_se2_to_se3_mw": 0.498456459490933,
    "se3_price_vs_scheduled_exchange_se3_to_se4_mw": 0.27673096734886243
  },
  "joined_rows": 12287,
  "price_table": "se3_se1_demand_response_analysis_v1",
  "utilization_margin_status": "blocked_capacity_concept_uncertain"
}
```
