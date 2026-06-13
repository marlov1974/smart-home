# FTX Physical Index

This folder contains physical knowledge about the FTX ventilation aggregate used by G2.

## Files

```text
devices.md       physical FTX device roles and major components
sensors.md       sensor/channel mapping
airflow.md       airflow, pressure and K-factor model
temperatures.md  temperature channels and interpretation
cooling-risk.md  cooling and condensate constraints
```

## Boundary

P0057 imported the current G1 FTX runtime as the first G2 FTX runtime baseline.

Runtime source inspection for FTX should now start in:

```text
src/shelly/ftx/
```

The G1 repository remains historical provenance or an explicit maintenance target, not the default place to inspect post-P0057 FTX behavior.

This folder contains physical facts that G2 can use when designing future control.

Created by `P0002-import-infrastructure-and-physical-baseline`.
