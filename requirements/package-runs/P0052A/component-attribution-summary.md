# P0052A component attribution summary

Status: WARN
1. Token was read from a local secret file outside the repository; the token value was not logged or written.
2. Secret safety: {'token_source': 'local_secret_file_outside_repo', 'secret_checked': True, 'secret_safe': True, 'secret_gitignored': 'outside_repo_not_committable', 'secret_location_class': 'outside_repository_user_secret_dir', 'file_mode': '0o600', 'directory_mode': '0o700'}.
3. ENTSO-E document/process/business types tried: A09, A11, A26, A31, A61 with contract types A01-A09 during discovery; ingestion used A09, A11 and A61 A02/A03/A04.
4. EIC/domain mapping: {'SE1': '10Y1001A1001A44P', 'SE2': '10Y1001A1001A45N', 'SE3': '10Y1001A1001A46L', 'SE4': '10Y1001A1001A47J', 'FI': '10YFI-1--------U', 'DK1': '10YDK-1--------W', 'DK2': '10YDK-2--------M', 'NO1': '10YNO-1--------2', 'NO2': '10YNO-2--------T', 'NO3': '10YNO-3--------J', 'NO4': '10YNO-4--------9', 'LT': '10YLT-1001A0008Q', 'PL': '10YPL-AREA-----S', 'DE_LU': '10Y1001A1001A82H'}.
5. ENTSO-E provides internal Swedish A61 capacity rows for SE1-SE2, SE2-SE3 and SE3-SE4 for tested contract types A02/A03/A04.
6. ENTSO-E provides internal Swedish A09 scheduled exchange and A11 physical flow rows for those borders.
7. A26/A31 were rejected or not allowed for tested parameters; A61 A01 had no matching data in the tested discovery window.
8. Historical range ingested: {'start': '2026-05-01T00:00:00Z', 'end': '2026-05-25T22:00:00Z'}.
9. Tables updated: `transfer_capacity_flow_raw_v1`, `transfer_capacity_flow_hourly_v1`, `transfer_capacity_flow_se1_se4_hourly_v1`.
10. Concepts stored: scheduled_exchange_mw, physical_flow_mw, capacity_mw with explicit A61 contract labels.
11. Pre/post 2024-10-29 capacity comparability was not proven because default ingestion is post-go-live.
12. Utilization and bottleneck margin remain conservative pending capacity contract concept review.
13. Diagnostics: {'price_table': 'se3_se1_demand_response_analysis_v1', 'joined_rows': 0, 'columns': ['flow_or_exchange_se2_to_se3_mw', 'flow_or_exchange_se3_to_se4_mw', 'capacity_se2_to_se3_mw', 'capacity_se3_to_se4_mw'], 'correlations': {'se3_price_vs_flow_or_exchange_se2_to_se3_mw': None, 'se3_minus_se1_vs_flow_or_exchange_se2_to_se3_mw': None, 'se3_price_vs_flow_or_exchange_se3_to_se4_mw': None, 'se3_minus_se1_vs_flow_or_exchange_se3_to_se4_mw': None, 'se3_price_vs_capacity_se2_to_se3_mw': None, 'se3_minus_se1_vs_capacity_se2_to_se3_mw': None, 'se3_price_vs_capacity_se3_to_se4_mw': None, 'se3_minus_se1_vs_capacity_se3_to_se4_mw': None}}.
14. Forecast safety: {'scheduled_exchange_mw': 'historical_observed_only', 'physical_flow_mw': 'historical_observed_only', 'forecasted_transfer_capacity_explicit_A02': 'forecast_time_known_near_term_uncertain_publication_timing', 'forecasted_transfer_capacity_explicit_A03': 'forecast_time_known_near_term_uncertain_publication_timing', 'forecasted_transfer_capacity_explicit_A04': 'forecast_time_known_near_term_uncertain_publication_timing', 'utilization': 'not_forecast_safe_until_capacity_concept_review'}.
15. Next route: continue ENTSO-E concept/backfill if capacity will drive utilization; otherwise use signals as historical-only diagnostics.
16. Confirmed: no token leak, no continental price levels, no SE1-to-SE3 anchoring, no API, no production model and no device actions.
