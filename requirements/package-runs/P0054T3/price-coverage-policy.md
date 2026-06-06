# P0054T3 LABB

Status: `WARN`

```json
{
  "matched_p0_diagnostic": {
    "coverage_source": "intersection(P0054R no-price skeleton, P0054N exact-origin P0054L2-compatible price rows)",
    "ok": true,
    "reason": "matched P0 diagnostic on safe P1 price forecast coverage",
    "rows": 16102
  },
  "p0_primary_coverage": "full P0054R no-price origin skeleton",
  "p0_rows": 52173,
  "p1_coverage": "safe P0054N exact-origin P0054L2-compatible forecast rows",
  "p1_narrower_than_p0": true,
  "p1_rows": 16102,
  "price_delta_rule": "compare P1 only against P0_on_price_coverage, never against full P0 as a coverage-confounded delta"
}
```
