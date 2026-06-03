# P0052 component attribution summary

Status: WARN
1. Sources investigated: eSett Open Data, Svenska kraftnat Kontrollrummet / Statnett and ENTSO-E Transparency Platform.
2. Selected source: SvK Kontrollrummet / Statnett, because it is auth-free and exposes SE1-SE4 border flows plus zone import/export values.
3. Swedish internal border flow values were available for SE1-SE2, SE2-SE3 and SE3-SE4 over the partial reliable range.
4. Historical capacity values were not available from the selected source; ENTSO-E requires a security token.
5. Zone-level import/export was computed from SvK `ElectricalAreas` values for SE1-SE4.
6. Import/export includes internal Swedish and external neighbour borders as represented by the SvK/Statnett flow map.
7. Historical range ingested: {'start': '2026-05-01T00:00:00Z', 'end': '2026-05-25T22:00:00Z'}.
8. Tables: `transfer_capacity_flow_raw_v1`, `transfer_capacity_flow_hourly_v1`, `transfer_capacity_flow_se1_se4_hourly_v1`.
9. Units/direction: MW; positive `A_B` signed flow means A to B, negative means B to A.
10. Row counts: {'raw_rows': 95840, 'hourly_rows': 24542, 'wide_rows': 599}.
11. Missingness/quality: {'ok': True, 'duplicates': 0, 'nonfinite_values': 0, 'negative_capacity_values': 0, 'expected_hours': 599, 'missing_hours': {'signed_flow_mw': 0, 'import_mw': 0, 'export_mw': 0, 'net_import_mw': 0}, 'joined_p0051_hours': 599, 'wide_rows': 599, 'capacity_available': False, 'capacity_blocker': 'ENTSO-E Transparency API requires a security token; SvK/Statnett flow endpoint has no capacity fields.', 'row_counts_by_measure': {'flow_mw': 8968, 'signed_flow_mw': 8386, 'export_mw': 2396, 'import_mw': 2396, 'net_import_mw': 2396}}.
12. Capacity concept after flow-based go-live is not stored because no capacity source was available.
13. Derived features: {'net_import_z': 'import_z - export_z; positive means the zone is supplied by imports.', 'balance_residual_z': 'production_z + import_z - consumption_z - export_z. Reported only as compatibility diagnostic.', 'south_import_pressure': 'net_import_se3_mw + net_import_se4_mw', 'north_export_pressure': '-(net_import_se1_mw + net_import_se2_mw)', 'north_to_south_flow_min_or_chain_proxy': 'minimum positive internal north-to-south flow across SE1-SE2, SE2-SE3 and SE3-SE4 where present.', 'capacity_utilization': 'null in P0052 because capacity is unavailable from selected auth-free source.'}.
14. Initial diagnostics: {'price_table': 'se3_se1_demand_response_analysis_v1', 'price_columns': {'se3_price': 'se3_price', 'se3_minus_se1': 'se3_minus_se1'}, 'joined_rows': 599, 'correlations': {'se3_price_vs_net_import_se3_mw': 0.6765189198733116, 'se3_price_vs_south_import_pressure': 0.7396667513331376, 'se3_price_vs_north_to_south_bottleneck_margin': None, 'se3_minus_se1_vs_net_import_se3_mw': 0.25066644313977, 'se3_minus_se1_vs_south_import_pressure': 0.2660402951401065, 'se3_minus_se1_vs_north_to_south_bottleneck_margin': None, 'se3_minus_se1_vs_utilization_se2_se3_north_to_south': None, 'se3_minus_se1_vs_utilization_se3_se4_north_to_south': None}, 'note': 'Diagnostics are explanatory only. Capacity/utilization correlations are null because capacity is unavailable.'}.
15. Import/export features are strong enough for historical P0053 physical-regime diagnostics, not for forecast use without separate forecasts.
16. Forecast safety: {'signed_flow_mw': 'historical_observed_only', 'flow_mw': 'historical_observed_only', 'import_mw': 'historical_observed_only', 'export_mw': 'historical_observed_only', 'net_import_mw': 'requires_separate_forecast_model', 'capacity_mw': 'not_forecast_safe_until_source_available', 'south_import_pressure': 'requires_separate_forecast_model', 'north_export_pressure': 'requires_separate_forecast_model'}.
17. Confirmed: no continental price pressure levels, no SE1-to-SE3 anchoring, no API, no production model and no device actions.
