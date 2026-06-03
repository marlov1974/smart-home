# P0051 source contracts

```json
{
  "authentication": "none",
  "base_url": "https://api.opendata.esett.com",
  "consumption_endpoint": "/EXP15/Consumption",
  "consumption_sign": "source total/metered/profiled values are negative in sample; stored consumption is abs(value) positive demand MW",
  "fetch_note": "Python urllib is attempted first; curl fallback is used when local Python TLS cannot handshake with eSett.",
  "parameters": [
    "mba",
    "start",
    "end"
  ],
  "production_endpoint": "/EXP16/Volumes",
  "production_types": [
    "hydro",
    "nuclear",
    "solar",
    "thermal",
    "wind",
    "windOffshore",
    "energyStorage",
    "other",
    "total"
  ],
  "rate_limit": "eSett API info states public rate limit currently 5 calls/second/user",
  "source_name": "eSett Open Data",
  "source_resolution": "15 minutes in observed sample",
  "stored_resolution": "hourly mean MW",
  "time_format": "yyyy-MM-dd'T'HH:mm:ss.SSSX",
  "unit": "MW",
  "zones": {
    "SE1": "10Y1001A1001A44P",
    "SE2": "10Y1001A1001A45N",
    "SE3": "10Y1001A1001A46L",
    "SE4": "10Y1001A1001A47J"
  }
}
```
