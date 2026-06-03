# P0052C capacity sanity check method

P0052C reads local P0052B ENTSO-E rows only. It compares `abs(A09 scheduled_exchange_mw) / A61 capacity_mw` and `abs(A11 physical_flow_mw) / A61 capacity_mw` by normalized UTC timestamp, directed internal Swedish border and A61 contract type. Capacity values `<= 0` are invalid and ratios are not clipped.
