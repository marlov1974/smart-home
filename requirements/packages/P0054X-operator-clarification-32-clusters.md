# P0054X operator clarification: 32 clusters with settlement split

## Status

clarification for P0054X

## Operator intent

P0054X should target approximately 32 SE3 MGA modeling clusters, not only 16.

The intended primary taxonomy is:

```text
2 settlement/measurement behavior groups
x 4 urban/load-structure groups
x 4 climate/geography groups
= approximately 32 clusters
```

The settlement/measurement split is important because measured 15m/60m series and monthly-settled/profiled series likely have different behavior and should not be forced into the same modeling cluster.

## Primary settlement/measurement dimension

Use these two top-level modeling groups where data supports it:

```text
M = measured_15m_or_60m
P = monthly_settled_or_profiled
```

`measured_15m_or_60m` includes:

```text
15m measured
60m measured
mixed 60m->15m measured transition
hourly_settled
15m_settled
```

`monthly_settled_or_profiled` includes:

```text
monthly_settled
profiled
monthly/profile allocated hourly if source provides allocated profiles
```

If an MGA has both measured and profiled/monthly components, preserve both components and allow the same MGA to contribute to both modeling groups if the source data is split by settlement_class.

If settlement_class is unknown, place it in:

```text
U = unknown_settlement
```

Unknown should not be silently merged into measured or profiled clusters.

## Revised target cluster design

The main P0054X taxonomy should be:

```text
settlement_group x climate_group x urban_load_group
```

Where:

```text
settlement_group:
  measured_15m_or_60m
  monthly_settled_or_profiled
  unknown_settlement if needed

climate_group:
  northern_inland
  east_coast_malardalen_stockholm
  west_coast_gothenburg
  southern_inland_smaland_north_gotaland
  unknown_climate if needed

urban_load_group:
  big_city_apartment_service
  villa_suburban
  mixed_small_city_town
  rural_sparse_or_agriculture
  industrial_or_large_site if clearly needed
  unknown_urban if needed
```

The target is approximately 32 normal clusters:

```text
2 x 4 x 4 = 32
```

Plus optional special/unknown clusters:

```text
industrial_or_large_site
unknown_settlement
unknown_climate
unknown_urban
low-confidence catch-all
```

## 15m vs 60m handling

15m and 60m measured series may be modeled together if they represent the same settlement/measurement behavior and are correctly normalized to a common hourly modeling view.

However, P0054X must still preserve:

```text
native_resolution_group:
  measured_15m
  measured_60m
  measured_mixed_60m_to_15m
  monthly_or_profiled
  unknown
```

This native resolution group should be available as:

```text
cluster metadata
possible modeling feature
quality/caveat flag
```

Do not collapse 15m/60m/monthly into one indistinct group.

## Cluster IDs

Use readable cluster IDs, for example:

```text
M_EAST_BIGCITY
M_EAST_VILLA
M_EAST_MIXEDTOWN
M_EAST_RURAL
M_WEST_BIGCITY
...
P_EAST_BIGCITY
P_EAST_VILLA
...
```

Where:

```text
M = measured_15m_or_60m
P = monthly_settled_or_profiled
```

If unknowns are needed:

```text
U_UNKNOWN
M_UNKNOWN_CLIMATE_VILLA
P_EAST_UNKNOWN_URBAN
```

## Required evidence updates

P0054X must update or include:

```text
requirements/package-runs/P0054X/recommended-32-cluster-taxonomy.md
requirements/package-runs/P0054X/settlement-split-cluster-design.md
requirements/package-runs/P0054X/cluster-quality-review.md
```

The previous 16-cluster evidence can still be included as an intermediate design, but the final recommendation should target 32 clusters unless data quality forces merges.

## Quality rule

Do not force all 32 clusters if some are too small.

Instead:

```text
start from 32-cluster target
merge low-volume or low-confidence clusters
preserve settlement split unless there is no safe alternative
report final cluster count and why it differs from 32
```

## Relationship to main package

This clarification strengthens and amends:

```text
requirements/packages/P0054X-labb-se3-mga-cluster-taxonomy.md
```

If there is any conflict, follow this clarification.
