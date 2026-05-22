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

Current G1 runtime behavior still belongs in `marlov1974/shelly` until explicit migration.

This folder contains physical facts that G2 can use when designing future control.

Created by `P0002-import-infrastructure-and-physical-baseline`.
