# P0052A changelog

- Used the local ENTSO-E token safely without writing the token to evidence.
- Ingested ENTSO-E A09 scheduled exchange, A11 physical flow and A61 explicit capacity rows for internal Swedish borders over the P0052 recent overlap.
- Updated P0052 long tables and wide transfer table without dropping SvK/Statnett rows.
- Result status: WARN.
- No token leak, continental price levels, SE1-to-SE3 anchoring, API, production model, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.
