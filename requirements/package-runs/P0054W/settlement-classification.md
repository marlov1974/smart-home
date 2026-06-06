# P0054W settlement classification

eSett `EXP18/LoadProfile` is stored as `profiled_load_profile`.

P0054W did not merge this source with measured, flex or total consumption. Future packages must keep `EXP15/Consumption` and `EXP18/LoadProfile` separate unless a source contract explicitly defines a safe total.
