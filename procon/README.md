# Procon firmware development

Latest experimental build: [P0072 MVP r1](releases/P0072-mvp-r1/README.md). Read-only version with18 mapped/derived telemetry fields plus2 unavailable brine-pump fields, water heat calculation, freshness/status/raw diagnostics and alternating exclusive service27/28 operations. [API](docs/MVP_API.md), [pump research](docs/PUMPS.md).

**Physical P0072 validation pending. Controls are not implemented:** every Modbus write is rejected; no SET commands. Operator alone flashes. Last hardware-confirmed baseline is P0071 r2: repeated completed27/28raw5 and operator display5 at one point, with20Hz compressor and zero communication errors. Original and earlier release artifacts remain immutable for recovery.

Build `make -C procon verify` after `sh procon/tools/setup.sh`. Artifacts in releases/P0072-mvp-r1. Inferred STM32L433 assumption unchanged; code7596bytes,BSS844,package96KiB. No unrelated Shelly runtime change. Readback helper `procon/tools/read_mvp.py`; input0=888,1=72,68=1. See hardware/recovery docs before operator installation.

P0073: a sanitized standalone export is prepared in the private repository [procon-melcobems-mini-a1m](https://github.com/marlov1974/procon-melcobems-mini-a1m). GPL-3.0-only selected under operator delegation. It includes independent build/CI,protocol catalogs and explicit coverage limitations; no vendor artifacts or private logs. Smart Home evidence: requirements/package-runs/P0073. Visibility remains operator-controlled.

## P0072 r2 update

Revision2 adds supervised, reference-backed control commands with snapshot/readback/runtime lease restoration. See [control API](docs/CONTROL_API.md). Earlier r1 read-only statements remain historical. No hardware control validation or reboot restoration is claimed.
