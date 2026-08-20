# FTX Temperature and Sensor Placement

## Canonical temperature channels

Current G2 FTX runtime uses these temperature concepts:

```text
t.house               house/extract air before VVX
t.out                 outdoor/supply air before VVX
t.post_vvx            supply air after VVX before battery
t.to_house            supply air to house after battery
t.to_outdoor          exhaust air after VVX to outdoor
t.brine               brine or cooling water reference
t.brine_post_shunt    brine after cooling shunt toward cooling battery
t.hotwater            heating water reference
t.hotwater_post_shunt hot water after heating shunt toward heating battery
```

## Interpretation rule

A temperature channel is only meaningful together with sensor placement.

Do not treat a reading as a perfect thermodynamic node if the sensor is exposed to ambient air, poorly insulated or affected by radiation.

## House temperature

`t.house` is measured from extract/from-house air before VVX and acts as the house proxy for control logic.

Current source reads it on the extract-fan Pro device:

```text
ftx-extract-fan / temperature:105 = t.house
```

House relative humidity is read from the same Sensor Add-On channel family:

```text
ftx-extract-fan / humidity:105 = house RH
```

## Current supply-side temperature mapping

Current source reads the following local components on the supply-fan Pro device:

```text
ftx-supply-fan / temperature:100 = t.to_house
ftx-supply-fan / temperature:101 = t.post_vvx
ftx-supply-fan / temperature:102 = t.out
ftx-supply-fan / temperature:103 = t.brine
ftx-supply-fan / temperature:104 = t.brine_post_shunt
ftx-supply-fan / temperature:105 = t.hotwater
ftx-supply-fan / temperature:106 = t.hotwater_post_shunt
```

These values are read locally by `telemetry_publisher_supply_fan_v0_1_0.js`.

Selected thermal values are also distributed directly to the heat/cool L2 devices:

```text
heat receives:
  t.to_house
  t.hotwater
  t.hotwater_post_shunt

cool receives:
  t.to_house
  t.brine
  t.brine_post_shunt
```

## Current extract-side temperature mapping

Current source reads:

```text
ftx-extract-fan / temperature:100 = t.to_outdoor
ftx-extract-fan / temperature:105 = t.house
```

The former standalone process/extract/supply UNI mapping is retired and should only be treated as historical provenance.

## Design principle

Before changing control logic based on a temperature, verify that the sensor represents the intended physical point.

For L2 local regulation, distinguish between:

- the local actuator device that applies output
- the sensor-owning Pro device that measures the process value
- direct peer-to-peer telemetry that copies the required process value into the actuator device's local KVS/cache

The actuator device can therefore regulate locally without requiring L3 to stay online, provided the required peer telemetry remains fresh.

## Source

Original temperature concepts were imported from G1 during `P0002`.

Current channel ownership is aligned with:

```text
src/shelly/ftx/scripts/supply-fan/telemetry_publisher_supply_fan_v0_1_0.js
src/shelly/ftx/scripts/extract-fan/telemetry_publisher_extract_fan_v0_1_0.js
```

and with operator-confirmed removal of the former standalone UNI devices.
