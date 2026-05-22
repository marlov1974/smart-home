# FTX Temperature and Sensor Placement

## Canonical temperature channels

G2 inherits these FTX temperature concepts from current G1 measurements:

```text
t.house              house/extract air before VVX
t.out                outdoor/supply air before VVX
t.post_vvx           supply air after VVX before battery
t.to_house           supply air to house after battery
t.to_outdoor         exhaust air after VVX to outdoor
t.brine              brine or cooling water reference
t.brine_post_shunt   brine after cooling shunt toward cooling battery
t.hotwater           heating water reference
t.hotwater_post_shunt hot water after heating shunt toward heating battery
```

## Interpretation rule

A temperature channel is only meaningful together with sensor placement.

Do not treat a reading as a perfect thermodynamic node if the sensor is exposed to ambient air, poorly insulated or affected by radiation.

## House temperature

`t.house` is measured from extract/from-house air before VVX and acts as the house proxy for control logic.

## Current process/extract UNI temperature mapping

Current imported G1 mapping:

```text
temperature:100 = t.to_house
  supply air to house after battery

temperature:101 = t.brine
  brine reference before shunt/blending

temperature:102 = t.brine_post_shunt
  brine after cooling shunt toward cooling battery

temperature:103 = t.hotwater
  hot water / heating water reference before shunt/blending

temperature:104 = t.hotwater_post_shunt
  hot water after heating shunt toward heating battery
```

## Design principle

Before changing control logic based on a temperature, verify that the sensor represents the intended physical point.

## Source

Imported from G1 `memory/ftx-fysiskt/07-temperature-and-sensor-placement.md` during `P0002`.
