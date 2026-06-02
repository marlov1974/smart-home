# Design backlog: continental price pressure for SE3/SE4

## Status

parked

## Priority

Later. Do not work on this until the current SE3-SE1 / SE3 foundation is stable enough.

## Context

The SE3/SE4 price picture is not only a Swedish internal north/south balance problem.

German, Danish, Polish, Baltic and other connected market prices can increasingly affect southern Sweden through export/import coupling and available transmission capacity.

This topic was discussed during the SE3-SE1 bottleneck work, but the decision is to postpone it until the rest of the SE3 foundation is in better shape.

## Hypothesis

Continental prices can create an external market-pressure component:

```text
high DE/DK/PL/Baltic prices
+ available interconnector capacity
+ Swedish south/north internal constraints
→ higher SE4 and sometimes SE3 prices
→ larger SE3-SE1 / SE4-SE1 spread
```

The likely model should eventually distinguish at least three pressure families:

```text
1. internal Swedish balance pressure
   production/consumption/net-load SE1-SE4

2. local SE3/SE4 demand-response pressure
   industry, heat pumps, local price-rank response

3. external continental export pressure
   DE/DK/PL/Baltic price levels and flows/capacity
```

## Candidate future features

Potential external price features:

```text
DE/LU price
DK1 price
DK2 price
PL price
LT/LV/EE price
NO1/NO2 price
FI price
continental_price_index
max_continent_price
weighted_continent_price
DE_minus_SE4
DE_minus_SE3
DK2_minus_SE4
PL_minus_SE4
max_continent_minus_SE4
max_continent_minus_SE3
```

Potential flow/capacity features:

```text
SE4↔DE flow
SE4↔PL flow
SE4↔LT flow
SE4↔DK2 flow
SE3↔DK1 flow
SE3↔NO1 flow
net_export_south
available_transfer_capacity
south_export_pressure
```

Potential derived model signals:

```text
external_market_pressure
continental_pull_pressure
south_export_pressure
internal_balance_pressure × continental_price_pressure
```

## Forecast-safety note

For historical explanation, actual external spot prices and flows can be used as explanatory signals.

For a future 7-day forecast, external spot prices are only actually known for published spot horizons. Longer horizons need forecasts, forward/futures proxies, normal profiles or another explicitly documented assumption.

## Deferred package idea

A future package may be created when ready:

```text
P00xx: External market pressure signal discovery for SE3/SE4
```

Suggested scope:

```text
- discover available historical external prices and flow/capacity data
- verify sources, units, time zones, latency and coverage
- build small samples for DE/DK/PL/Baltic/NO/FI vs SE3/SE4
- analyze correlation and event behavior versus SE3 price, SE4 price, SE3-SE1 and SE4-SE1
- determine forecast-safe vs explanatory-only features
- recommend whether external_market_pressure should enter the SE3/SE4 model architecture
```

## Current decision

Do not add continental price pressure to the active P0050 demand-response / heat-pump analysis.

Do not start external market-pressure modeling until the current SE3-SE1 / SE3 architecture questions are resolved.
