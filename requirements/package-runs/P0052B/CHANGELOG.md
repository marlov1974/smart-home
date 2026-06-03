# P0052B changelog

- Re-verified ENTSO-E token safety without writing the token value.
- Added metadata-compatible P0052 schema columns and backfilled ENTSO-E A09/A11/A61 representative historical windows.
- Fixed P0052A diagnostics join by normalizing `Z` and `+00:00` UTC timestamp strings.
- A61 A02/A03/A04 are documented as weekly/monthly/yearly contract types; utilization and bottleneck margin remain blocked because capacity concept compatibility is uncertain.
- Result status: WARN.
- No token leak, continental price levels, SE1-to-SE3 anchoring, API, production model, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.
