# P0054X operator clarification: cluster size is load/data, not MGA count

## Status

clarification for P0054X

## Operator clarification

A modeling cluster should not be considered small merely because it contains few MGAs.

Each MGA can represent many customers and many properties. Even a small count of MGAs may correspond to a large and stable consumption volume.

Therefore, P0054X must judge cluster size primarily by:

```text
total mean load MW
annual energy volume MWh
share of SE3 load
data coverage
signal stability
```

not by:

```text
raw MGA count alone
```

## Cluster merge policy

Do not merge clusters only because the cluster has few MGA members.

A cluster may be considered too small for standalone modeling only if one or more of these are true:

```text
very low total load volume
poor data coverage
unstable or sparse time series
settlement/resolution cannot be classified safely
cluster is dominated by unknown labels
cluster has too little validation history for model assessment
```

A cluster with few MGAs but large load volume and good data quality should remain as its own cluster.

## Evidence requirements

P0054X cluster-quality evidence must report both:

```text
member_mga_count
total_mean_load_mw
annual_energy_mwh
share_of_se3_load
coverage_ratio
```

and must not use `member_mga_count` as the primary merge criterion.

## Relationship to 32-cluster target

This clarification strengthens the 32-cluster target:

```text
2 settlement groups x 4 urban/load groups x 4 climate groups ≈ 32 clusters
```

Do not collapse the target taxonomy merely because some cells have few MGAs. Collapse only if volume/data/signal quality makes the cluster unsuitable.

## Relationship to main package

This clarification strengthens and amends:

```text
requirements/packages/P0054X-labb-se3-mga-cluster-taxonomy.md
requirements/packages/P0054X-operator-clarification-32-clusters.md
```

If there is any conflict, follow this clarification.
