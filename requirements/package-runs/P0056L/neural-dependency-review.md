# P0056L Neural Dependency Review

```json
{
  "numpy": true,
  "selected_framework": "scikit-learn MLPRegressor",
  "skipped": [
    {
      "model_id": "N3_TCN_1D_CNN",
      "reason": "torch unavailable; no local TCN dependency"
    },
    {
      "model_id": "N4_NBEATS_NHITS",
      "reason": "no supported local dependency and heavy dependency install is out of scope"
    }
  ],
  "sklearn": true,
  "torch": false
}
```
