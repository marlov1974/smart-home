# FTX Sensors

This file maps current FTX sensor roles to the Shelly devices that own them.

Device identity and reachability are defined in:

```text
memory/infrastructure/devices.md
```

## Current sensor architecture

The former standalone `ftx-supply-uni`, `ftx-extract-uni` and `ftx-process-uni` devices have been removed from the current physical system.

Their relevant measurement roles are now attached to the Pro devices that also own the supply- and extract-fan actuator roles, using Shelly Sensor Add-On hardware.

Current runtime source reads those sensors locally from `Shelly.GetStatus` on the supply/extract devices and distributes selected values directly to other L2 devices through HTTP/RPC KVS writes.

## Supply Pro + Sensor Add-On

Device role:

```text
ftx-supply-fan / 192.168.77.10
```

Current source mapping from `telemetry_publisher_supply_fan_v0_1_0.js`:

```text
input:100       = supply differential pressure signal / Pa model

temperature:100 = t.to_house
temperature:101 = t.post_vvx
temperature:102 = t.out
temperature:103 = t.brine
temperature:104 = t.brine_post_shunt
temperature:105 = t.hotwater
temperature:106 = t.hotwater_post_shunt
```

The supply device also reads its local fan/light actuator status from `light:0`.

### Direct thermal publication

The supply device publishes selected local sensor values directly to the heat and cool L2 devices:

```text
ftx.tel.thermal.cool -> 192.168.77.13
  to_house
  brine
  brine_post_shunt

ftx.tel.thermal.heat -> 192.168.77.12
  to_house
  hotwater
  hotwater_post_shunt
```

The same publisher sends aggregate supply telemetry as `ftx.tel.dev.sup` to the dampers/coordination host at `192.168.77.30`.

## Extract Pro + Sensor Add-On

Device role:

```text
ftx-extract-fan / 192.168.77.11
```

Current source mapping from `telemetry_publisher_extract_fan_v0_1_0.js`:

```text
input:100        = extract differential pressure signal / Pa model
input:101        = house air-quality / ppm-like signal

temperature:100  = t.to_outdoor
temperature:105  = t.house
humidity:105     = house relative humidity
```

The extract device also reads its local fan/light actuator status from `light:0`.

Aggregate extract telemetry is published as `ftx.tel.dev.ext` to the dampers/coordination host at `192.168.77.30`.

## Pressure sensors

Identified pressure sensors:

```text
Manufacturer: Siemens
Model: QBM2030-5
Quantity: 2
Role: supply and extract differential pressure measurement
Signal: 0-10 V
```

Current source reads the pressure signals through `input:100` on the corresponding supply/extract Pro devices.

Open details:

- confirm exact measurement range/scaling represented by `xpercent`/input configuration on each current Pro device
- confirm physical measurement-point interpretation against installation when recalibrating airflow

Measurement caution:

Pressure measurements can refer to different physical points and must not be mixed:

- pressure at/over a measurement nipple or stoss
- pressure across a fan
- duct/static pressure
- house indoor/outdoor differential pressure

Only comparable measurement points should be used for calibration.

## Air quality sensor

Identified sensor:

```text
Siemens QPM2102
```

Current extract-side source reads its ppm-like signal through `input:101`.

Known behavior:

The air-quality signal can report high ppm-like values from VOC events, not only human CO2.

Known triggers include:

- hair spray
- perfume
- ethanol/brine spill

Control implication:

Do not treat all high ppm readings as occupancy-driven CO2.

## Retired UNI provenance

Historical G1/P0002/P0016 documentation may refer to:

```text
ftx-supply-uni  / 192.168.77.20
ftx-extract-uni / 192.168.77.21
ftx-process-uni / 192.168.77.22
```

These are retired hardware roles and must not be used as the current topology. Preserve package-run evidence that refers to them as historical evidence.

## Source

Original sensor inventory was imported from G1 during `P0002` and later publisher work.

Current device/channel ownership is aligned with the current G2 runtime source under:

```text
src/shelly/ftx/scripts/supply-fan/
src/shelly/ftx/scripts/extract-fan/
```

and with operator-confirmed removal of the standalone UNI devices.
