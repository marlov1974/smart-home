# P0052 source contracts

```json
{
  "entsoe_capacity_blocker": {
    "authentication": "securityToken required; unauthenticated request returned HTTP 401",
    "url": "https://web-api.tp.entsoe.eu/api"
  },
  "svk_statnett_flow": {
    "available_borders": [
      "DE_SE4",
      "DK1_SE3",
      "FI_SE1",
      "FI_SE3",
      "LT_SE4",
      "NO1_SE3",
      "NO3_SE2",
      "NO4_SE1",
      "NO4_SE2",
      "SE1_SE2",
      "SE2_SE3",
      "SE3_SE4",
      "SE4_DK2",
      "SE4_PL"
    ],
    "available_measures": [
      "signed_flow_mw",
      "flow_mw",
      "import_mw",
      "export_mw",
      "net_import_mw"
    ],
    "capacity_measures": [],
    "query_parameters": {
      "ticks": "epoch milliseconds for requested quarter-hour"
    },
    "response_shape": "Data id=1 contains border signed flows; Data id=2 contains country/area import/export; LastUpdated is epoch milliseconds.",
    "unit": "MW",
    "url": "https://www.svk.se/services/controlroom/v2/map/flow?ticks={ticks}"
  }
}
```
