# P0054P2 operator clarification: actual load, not ENTSO-E flows

## Status

clarification for P0054P2

## Operator clarification

The project already has ENTSO-E data in the database, but that existing data is import/export flow data between bidding zones.

That is not the requested target.

For P0054P2, Codex must load or obtain the actual consumption/load inside each Swedish bidding zone:

```text
SE1 actual load / consumption
SE2 actual load / consumption
SE3 actual load / consumption
SE4 actual load / consumption
```

The correct source class is:

```text
ENTSO-E Actual Total Load / Total Load - Actual by bidding zone or area
```

The incorrect source classes for this package are:

```text
cross-border physical flows
net positions
scheduled exchanges
A09/A11 flow or exchange data
A61 capacity data
production data
price data
```

Existing ENTSO-E import/export flow rows may be documented as available for future flow/export-import packages, but they must not be transformed into consumption targets.

## Required behavior

Before writing `entsoe_consumption_area_hourly_v1`, Codex must prove that the selected source measures load/consumption within the area, not transfer between areas.

Required evidence wording:

```text
source_type = actual_total_load
area_scope = bidding_zone_internal_consumption_or_load
usable_for_consumption_target = true
```

If Codex only finds flow/exchange/capacity data, it must STOP and request an Actual Total Load export/source for SE1-SE4 from 2022-06-01 onward.

## Relationship to P0054P2

This clarification strengthens P0054P2 and must be followed together with:

```text
requirements/packages/P0054P2-labb-entsoe-actual-load-fetch-se1-se4.md
```
