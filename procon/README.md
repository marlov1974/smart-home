# Procon firmware development

Latest experimental build: [P0072 MVP r1](releases/P0072-mvp-r1/README.md). Read-only version with18 mapped/derived telemetry fields plus2 unavailable brine-pump fields, water heat calculation, freshness/status/raw diagnostics and alternating exclusive service27/28 operations. [API](docs/MVP_API.md), [pump research](docs/PUMPS.md).

**Physical P0072 validation pending. Controls are not implemented:** every Modbus write is rejected; no SET commands. Operator alone flashes. Last hardware-confirmed baseline is P0071 r2: repeated completed27/28raw5 and operator display5 at one point, with20Hz compressor and zero communication errors. Original and earlier release artifacts remain immutable for recovery.

Build `make -C procon verify` after `sh procon/tools/setup.sh`. Artifacts in releases/P0072-mvp-r1. Inferred STM32L433 assumption unchanged; code7596bytes,BSS844,package96KiB. No unrelated Shelly runtime change. Readback helper `procon/tools/read_mvp.py`; input0=888,1=72,68=1. See hardware/recovery docs before operator installation.
