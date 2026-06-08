# P0056D Decision

```json
{
  "candidate_default_areas": [
    "SE2"
  ],
  "keep_p0056b_default_areas": [
    "SE1",
    "FI"
  ],
  "production_activation": false,
  "rule": "candidate if DayAhead improves >=2%, or full36 improves >=2% without DayAhead worsening, or daily energy improves >=5% without DayAhead worsening >1%",
  "status": "WARN"
}
```
