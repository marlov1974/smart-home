# FTX Sensors

This file maps FTX sensor roles to known Shelly/UNI device sources.

Device identity and reachability are defined in:

```text
memory/infrastructure/devices.md
```

## Supply UNI

Device:

```text
ftx-supply-uni / 192.168.77.20
```

Known imported roles:

- supply-side differential pressure / Pa
- outdoor or supply air before VVX proxy
- supply air after VVX
- supply fan RPM

Pressure sensor:

```text
Manufacturer: Siemens
Model: QBM2030-5
Signal: 0-10 V pressure measurement to Shelly Plus UNI
Role: supply differential pressure measurement
```

Runtime usage:

- supply pressure channel is read by `ftx-supply-uni`
- runtime poll logic converts the pressure signal to Pa and derived l/s airflow

## Extract UNI

Device:

```text
ftx-extract-uni / 192.168.77.21
```

Known imported roles:

- extract-side differential pressure / Pa
- extract/house air before VVX
- exhaust/to-outdoor temperature after VVX
- extract fan RPM

Pressure sensor:

```text
Manufacturer: Siemens
Model: QBM2030-5
Signal: 0-10 V pressure measurement to Shelly Plus UNI
Role: extract differential pressure measurement
```

Runtime usage:

- extract pressure channel is read by `ftx-extract-uni`
- runtime poll logic converts the pressure signal to Pa and derived l/s airflow

## Pressure sensor inventory and open checks

Identified pressure sensors:

```text
Manufacturer: Siemens
Model: QBM2030-5
Quantity: 2
Role: supply and extract differential pressure measurement
Signal: 0-10 V pressure measurement to Shelly Plus UNI
```

Open details:

- confirm exact measurement range interpretation for QBM2030-5 in current wiring/config
- confirm which physical sensor is supply vs extract if not obvious from installation

Measurement caution:

Pressure measurements can refer to different physical points and must not be mixed:

- pressure at/over a measurement nipple or stoss
- pressure across a fan
- duct/static pressure
- house indoor/outdoor differential pressure

Only comparable measurement points should be used for calibration.

## Process UNI

Device:

```text
ftx-process-uni / 192.168.77.22
```

Known imported roles:

- house CO2/VOC ppm-equivalent input
- house relative humidity
- VVX RPM
- supply air to house after battery
- brine reference
- brine after cooling shunt
- hot water / heating water reference
- hot water after heating shunt

## Air quality sensor

Identified sensor:

```text
Siemens QPM2102
```

Known behavior:

The air-quality signal can report high ppm-like values from VOC events, not only human CO2.

Known triggers include:

- hair spray
- perfume
- ethanol/brine spill

Control implication:

Do not treat all high ppm readings as occupancy-driven CO2.

## Source

Imported from G1 `memory/ftx-fysiskt/02-hardware-inventory.md` during `P0002`.

Pressure sensor model and pressure-measurement caution imported from G1 `memory/ftx-fysiskt/02-hardware-inventory.md` and `memory/ftx-fysiskt/03-airflow-and-pressure-model.md` during `P0009`.
