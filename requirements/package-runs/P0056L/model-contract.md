# P0056L Model Contract

```json
{
  "N1_TabularMLP": {
    "architecture": "MLPRegressor hidden=(48,24)",
    "feature_count": 36,
    "framework": "scikit-learn",
    "kind": "tabular"
  },
  "N2_SequenceMLP_168h": {
    "architecture": "MLPRegressor hidden=(32,), 168h flattened known-at-origin load window",
    "feature_count": 204,
    "framework": "scikit-learn",
    "kind": "sequence"
  }
}
```
