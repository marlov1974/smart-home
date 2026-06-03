# P0052B component attribution summary

Status: WARN
1. Token safety was re-verified; no token value is stored in evidence.
2. A61 A02/A03/A04 mean weekly/monthly/yearly contract types in the ENTSO-E context.
3. No A61 contract type is selected for utilization diagnostics because concept compatibility remains uncertain.
4. Internal Swedish capacity/exchange/flow was backfilled for representative windows where ENTSO-E returned rows.
5. Backfill row counts: {'raw_rows_fetched': 12689, 'hourly_rows_aggregated': 8182, 'raw_rows_inserted_or_reused': 12689, 'hourly_rows_inserted_or_reused': 8182, 'raw_rows_net_new': 0, 'hourly_rows_net_new': 0, 'wide_rows_inserted': 0, 'wide_rows_updated': 528}.
6. Join fix: {'price_table_exists': True, 'issue': 'P0052A used exact text join; transfer timestamps used Z while price timestamps used +00:00.', 'exact_join_rows': 0, 'normalized_join_rows': 12287, 'normalized_join_rows_with_entsoe_signal': 12287}.
7. Pre/post 2024-10-29 comparability remains inconclusive for utilization.
8. Utilization and bottleneck margin remain blocked.
9. Diagnostics: {'price_table': 'se3_se1_demand_response_analysis_v1', 'joined_rows': 12287, 'columns': ['scheduled_exchange_se2_to_se3_mw', 'scheduled_exchange_se3_to_se4_mw', 'physical_flow_se2_to_se3_mw', 'physical_flow_se3_to_se4_mw'], 'correlations': {'se3_price_vs_scheduled_exchange_se2_to_se3_mw': 0.498456459490933, 'se3_minus_se1_vs_scheduled_exchange_se2_to_se3_mw': 0.42565969140971466, 'se3_price_vs_scheduled_exchange_se3_to_se4_mw': 0.27673096734886243, 'se3_minus_se1_vs_scheduled_exchange_se3_to_se4_mw': 0.3029315165538603, 'se3_price_vs_physical_flow_se2_to_se3_mw': 0.41571351461496286, 'se3_minus_se1_vs_physical_flow_se2_to_se3_mw': 0.38412719744105916, 'se3_price_vs_physical_flow_se3_to_se4_mw': 0.2558203018170429, 'se3_minus_se1_vs_physical_flow_se3_to_se4_mw': 0.27973232818142946}, 'utilization_margin_status': 'blocked_capacity_concept_uncertain'}.
10. Forecast safety: {'scheduled_exchange_mw': 'historical_observed_only', 'physical_flow_mw': 'historical_observed_only', 'capacity_mw_A02': 'not_forecast_safe_until_capacity_concept_review', 'capacity_mw_A03': 'not_forecast_safe_until_capacity_concept_review', 'capacity_mw_A04': 'not_forecast_safe_until_capacity_concept_review', 'utilization': 'not_forecast_safe_until_capacity_concept_review', 'bottleneck_margin': 'not_forecast_safe_until_capacity_concept_review', 'flow_based_market_coupling_flag': 'forecast_time_known_near_term'}.
11. Recommendation: P0053 may use historical exchange/flow diagnostics, not A61 utilization/margin.
12. Confirmed: no token leak, no continental price levels, no SE1-to-SE3 anchoring, no API, no production model and no device actions.
