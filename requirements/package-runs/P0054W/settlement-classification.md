# P0054W settlement classification

eSett `EXP18/LoadProfile` is stored as `profiled_load_profile`.

P0054W did not merge this source with measured, flex or total consumption. Future packages must keep `EXP15/Consumption` and `EXP18/LoadProfile` separate unless a source contract explicitly defines a safe total.

## 2026-06-06 clarification

Resolution and settlement/measurement class are separate dimensions. A monthly-settled/profiled source can still be delivered as 15m or 60m rows.

The loaded `EXP18/LoadProfile` per-MGA rows match `EXP15/Consumption.profiled` at SE3/MBA level. The large missing component is `EXP15/Consumption.metered`, which was found at SE3/MBA level but not per MGA in public eSett Open Data.

Until a per-MGA `metered/non_profiled` source is found, this dataset is a partial `profiled/load_profile` component only, not complete SE3 MGA consumption.
