# P0052 source discovery

```json
{
  "investigated": [
    {
      "authentication": "none",
      "base_url": "https://api.opendata.esett.com",
      "result": "No transfer capacity, border flow or import/export endpoint found in OpenAPI contract.",
      "source_name": "eSett Open Data"
    },
    {
      "authentication": "none observed; browser-style User-Agent and Referer are required for reliable access",
      "base_url": "https://www.svk.se",
      "direction_convention": "positive A_B means A to B; negative means B to A",
      "endpoint_or_download_path": "/services/controlroom/v2/map/flow?ticks=<epoch_ms>",
      "resolution": "quarter-hour display values",
      "selected": true,
      "source_name": "Svenska kraftnat Kontrollrummet / Statnett",
      "units": "MW"
    },
    {
      "authentication": "security token required",
      "base_url": "https://web-api.tp.entsoe.eu/api",
      "result": "HTTP 401 without security token. Candidate for historical capacity/flow once token is available.",
      "selected": false,
      "source_name": "ENTSO-E Transparency Platform"
    }
  ],
  "selected_source": "Svenska kraftnat Kontrollrummet / Statnett",
  "selection_reason": "Only discovered auth-free machine-readable source with SE1-SE4 border flows and zone import/export values."
}
```
