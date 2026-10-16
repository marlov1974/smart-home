# P0080 EFFECT + pair-energy v4 — installed release

This directory freezes the 2026-10-16 release built over the two installed v2
device bases. It combines the revised EFFECT controller and its RAM-only gain
import with Shelly pair-energy executor 1.5.1. The firmware is installed on
both Procon units, and the non-actuating Shelly runtime path has passed live
validation. No physical energy-delivery mission was run as part of this
qualification.

## Changes from installed v2

- Mode uses the current 45 C production supply guard and the continuous EFFECT
  controller qualified by the host and ARM suites.
- Service owns the adaptive kW-to-Hz model behind the existing private veneers.
  The public layout fingerprint remains unchanged.
- Debug Command accepts the supervised `C077` gain-seed envelope. It checks all
  96 UID bits, the range 700–2000, and the maintenance gate. One value may be
  accepted per boot; an exact retry is idempotent. The imported gain exists only
  in RAM and falls back to 1350 after reboot unless Shelly seeds it again.
- Diagnostic schema 4 exposes the model gain and evidence counters, plus the
  seeded flag at input register 346.
- Shelly 1.5.1 consumes a strict rolling four-quarter KVS plan, integrates each
  pump independently, carries bounded energy debt, activates a staged revision
  atomically at a quarter boundary, and restores native control after expiry.
- Shelly stores only the slowly learned gain in a UID-bound KVS record. It uses
  compare-and-swap plus readback, requires stable evidence before saving, and
  seeds firmware only after the exact device identity has been read.
- The host runner now snapshots the complete Script 7 slot, its configuration,
  KVS state and serial transport before mutation. It quiesces and verifies the
  script before publishing a plan or uploading code, preserves the original
  evidence file, restores the complete previous state after any failed
  validation, and verifies that the serial configuration did not change.

## Device compositions

The images are device specific and are not interchangeable.

| Device | Installed v2 base | v4 candidate | OTA modules |
| --- | --- | --- | --- |
| VP1 / D1 | `4bf657aa` | `57ee1885` | Mode, Service, Debug Command; slots 2, 4, 5 |
| VP2 / D2 | `e11851e8` | `fd001ec7` | Mode, Service, Debug Command; slots 2, 4, 5 |

The atomic OTA mask is `0x34`. The private Service veneers remain
`effect_model_op=0x08012069` and `effect_model_tick=0x0801206d`; the public
layout ID remains `3833993797`. Mode uses 11,904 of 12,288 bytes, Service uses
2,824 of 4,096 bytes, and Debug Command uses 192 of 4,096 bytes.

`vp1/install.bin` and `vp2/install.bin` are complete recovery/composition
artifacts. They are not instructions to rewrite BL2. The bundled OTA plans are
sanitized audit records only. A live plan must be regenerated after reading the
exact UID and installed manifest from the intended unit.

## Verification status

`VERIFICATION.json` is the authoritative machine-readable status. The complete
sanitized host chain, 36 focused Python tests (including all 31 Shelly/runner
safety tests), six Node regressions, JavaScript
syntax, the 37-case full ARM suite, both device-specific ARM paths, the ARM
gain-seed path, flash-RAM fault tests, and 2,579 mock-OTA interruption cuts per
device passed. A clean
extraction of `source.tar.gz` passes the host chain, 63 selected Python tests
and all six Node regressions. Its ARM rebuild reproduces the generic final
firmware artifacts byte for byte.

Both devices accepted the 92-frame atomic OTA without frame retries or repair,
and now report manifests `57ee1885` and `fd001ec7`. Shelly 1.5.1 then passed a
read-only runtime validation with zero holding-register writes. Its exact
30,501-byte production source remains installed in Script 7, stopped and
disabled. The temporary plan and status keys were restored to absent, serial
remained Modbus client 9600 8N1, and both controllers remained idle in native
curve mode.

The first validation with 1.5.0 timed out because stale startup feedback kept
the validation-only path from reaching its self-stop. Its transactional
rollback restored the complete previous Script 7 and KVS state. Version 1.5.1
fixes that ordering defect, and the new end-to-end regression reproduces the
stale startup state while proving self-stop and zero writes. Both evidence sets
are retained. This validates installation and the non-actuating runtime path;
physical energy tracking remains unqualified.

## Contents

- `COMPOSITION.json`: exact v2 baselines, v4 candidates, module identities and
  hashes.
- `VERIFICATION.json`: offline and live gates, evidence paths and remaining
  qualification limits.
- `INSTALLATION.json`: exact live OTA and read-only Shelly validation outcome.
- `vp1/`, `vp2/`: complete device-specific compositions, audit-only OTA plans
  and mock-OTA results.
- `shelly/energy_pair_v1.js`: pair-energy executor 1.5.1.
- `tools/compose_effect_energy_v4.py`: strict three-module offline composer.
- `tests/`: the six JavaScript energy/model/validation regressions.
- `source.tar.gz`: frozen standalone buildable source and tests, preserving the
  runner's repository-relative `procon/modular` layout. It contains the exact
  safety-gated runner and its ten focused tests.
- `SOURCE_FILES.txt`: exact archive inventory.
- `logs/`: captured build, audit and test records.
- `SHA256SUMS`: hashes for every release file except itself.
