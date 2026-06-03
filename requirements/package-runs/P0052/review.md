# P0052 consistency review

Status: WARN

P0052 follows a verified P0051 result. P0051 evidence confirms that `physical_balance_hourly_v1` and `physical_balance_se1_se4_hourly_v1` exist, with final overlap range `2022-05-29T23:00:00+00:00` through `2026-05-25T22:00:00+00:00`, and with `net_load = consumption - production`.

P0052 is consistent with the repository direction as a Mac/local database discovery and diagnostics package. It must not build a model, API, Shelly runtime, HA integration, KVS flow, M5/M6/M7 or continental price-pressure feature.

Source review result:

- eSett Open Data was checked first because P0051 selected it. Its OpenAPI contract exposes production, consumption, imbalance and settlement datasets, but no transfer capacity, border flow or import/export endpoint.
- Svenska kraftnat Kontrollrummet exposes an auth-free browser endpoint backed by Statnett for flow-map data: `/services/controlroom/v2/map/flow?ticks=<epoch_ms>`. The response includes directed border flows and already aggregated import/export per country and Swedish electrical area.
- SvK Kontrollrummet documents Statnett as the displayed flow data source in the flow-map component. The page says prices and flows are quarter-hour values and notes a new data-import method from 2026-05-08.
- ENTSO-E Transparency Platform API was checked as the likely historical capacity/flow source. The API endpoint returns HTTP 401 without a security token, so no auth-free ingestion is possible from this environment.

WARN reasons:

- Capacity values are not available from the auth-free SvK/Statnett flow endpoint. Capacity ingestion is therefore documented as an ENTSO-E/API-token blocker instead of faked.
- SvK/Statnett historical flow endpoint works for recent 2026 timestamps but returned server errors for tested 2025 and 2024 timestamps. P0052 can ingest the maximum reliable overlap with P0051, but not the full P0051 history.
- The SvK endpoint exposes actual/scheduled display flows and precomputed import/export, not a formal capacity-domain or NTC contract.

Decision:

Proceed with a WARN implementation. Ingest reliable SvK/Statnett SE1-SE4 flow and import/export history over the overlap available before P0051's end date, store capacity fields as unavailable/null, and produce evidence that P0053 should not treat capacity as available until ENTSO-E token-backed ingestion or another capacity source exists.

Forbidden work remains out of scope: no continental price levels, no SE1-to-SE3 anchoring, no SE3 forecast model, no production API, no deployable model artifact, no Shelly/Home Assistant/KVS/device actions, no M5/M6/M7 and no futures.
