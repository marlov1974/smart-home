# EFFECT + energy v4 — installation 2026-10-16

Status: firmware installation and read-only Shelly runtime validation verified;
no heating-power mission was started.

## Procon OTA

Mode, Service and Debug Command were installed atomically, one Procon at a time
while the peer was held in WAIT. Only OTA slots 2, 4 and 5 changed. BL2, Common,
Dispatcher, Drift and Debug Telemetry stayed byte-identical to each device's
installed base.

| Device | Previous manifest | Installed manifest | Changed slots |
| --- | --- | --- | --- |
| VP1 / SID 1 | `0x4bf657aa` | `0x57ee1885` | 2 (Mode), 4 (Service), 5 (Debug Command) |
| VP2 / SID 2 | `0xe11851e8` | `0xfd001ec7` | 2 (Mode), 4 (Service), 5 (Debug Command) |

Each device accepted 92 OTA frames. Every decoded response had status zero and
matched the frozen sequence. Neither device needed a frame retry, recovery
branch or the prepared 199-frame full-image repair. VP1's peer WAIT needed two
BUSY replies before acceptance and VP2's needed six; both then completed
normally.

Cleanup succeeded on its first attempt after each device: the helper was
stopped and disabled, its prior source was restored, the peer WAIT expired and
the serial transport returned to Modbus client mode at 9600 8N1. Both relays
were off. Final resident reads reported protocol 2, layout `0xe4861a45`, the
expected device UID and manifest, valid image and ready state.

Both controllers were IDLE with no saved ownership, active lease, write or
error. Native power, heat-curve mode, 52.00 C DHW target and boost-off state
were preserved. The curve-derived flow target changed during the observations;
it is dynamic native state and was not used as a preservation invariant.

Primary evidence is stored in
`evidence/effect-energy-v4-install-20261016T050551Z/`, including `plan.json`,
`outcome.json`, both OTA reply logs, recovery records, cleanup records and final
native captures.

## Shelly 1.5.1 runtime validation

The first validation attempt exposed a defect in the validation-only branch of
Shelly 1.5.0. Both newly booted firmware instances still reported the invalid
power sentinel and age 65535. Production correctly holds in that state, but the
validation branch returned before reaching its self-stop. The 75-second host
timeout fired. Its transactional cleanup restored the absent plan and status
keys, unchanged serial configuration, and the complete previous 15,420-byte
Script 7 source, stopped and disabled.

Version 1.5.1 moves only the validation-only call into the already completed
identity/model/feedback/plan path before the stale-feedback production hold.
It still stops before `commandBoth()` and never invokes C077. An end-to-end
Node regression reproduces the invalid startup feedback, waits through the
30-second missing-model-record allowance, proves `phase=validated`, self-stop
and zero holding-register writes. The ordinary stale-feedback hold regression
continues to pass.

The second live attempt passed:

- plan revision `1792128725` was installed and read back exactly;
- the validation script published `phase=validated` and stopped itself;
- both devices were read with correct UID/schema, controller IDLE and native
  heat-curve mode;
- the temporary plan and status KVS keys were restored to absent;
- serial remained Modbus client 9600 8N1;
- the exact 30,501-byte production source was installed in Script 7, stopped
  and disabled, SHA-256
  `29813a747a7c2decef73aa80bc041383344a51dd8c5ab8d907dd926e9f1832a5`.

The failed and successful evidence sets are respectively
`evidence/shelly-energy-v4-validation-20261016/` and
`evidence/shelly-energy-v4-validation-20261016-attempt2/`. The failed set is
retained because it explains the discovered defect and proves rollback.

## Persistence boundary

Firmware retains the learned affine model only in RAM. Shelly stores only the
long-term gain `a` in a strict UID-bound KVS record and may seed it through
C077 once per Procon boot when an execution plan is started. Bias, trim,
confidence and transient controller state are not persisted. The validation
run deliberately bypassed seeding; final I310 remained the default 1350 and
I346 remained zero on both devices.

This result qualifies installation, transaction rollback and the non-actuating
runtime path. It is not a physical energy-delivery or tracking trial.
