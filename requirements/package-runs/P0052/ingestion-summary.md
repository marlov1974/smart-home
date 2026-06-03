# P0052 ingestion summary

```json
{
  "ranges": {
    "final_ingested_range": {
      "end": "2026-05-25T22:00:00Z",
      "start": "2026-05-01T00:00:00Z"
    },
    "missing_range_reason": "Capacity is blocked without ENTSO-E token. Flow/import-export source history is partial; older P0051 overlap is not synthesized.",
    "p0051_overlap_range": {
      "end": "2026-05-25T22:00:00Z",
      "rows": 34968,
      "start": "2022-05-29T23:00:00Z"
    },
    "requested_range": {
      "end": "2026-05-25T22:00:00Z",
      "start": "2022-05-29T23:00:00Z"
    },
    "source_available_range": {
      "end": "2026-05-25T22:00:00Z",
      "note": "SvK/Statnett flow endpoint returned 500 for tested 2024/2025 timestamps. P0052 defaults to the recent reliable P0051 overlap from 2026-05-01 for practical full quarter-hour ingestion.",
      "start": "2026-05-01T00:00:00Z"
    }
  },
  "row_counts": {
    "hourly_rows": 24542,
    "raw_rows": 95840,
    "wide_rows": 599
  }
}
```
