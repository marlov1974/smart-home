# P0075 pure opcode sweep results — 2026-10-07

## Verified result

The specifically risk-authorized single-byte survey completed `00..FF` once in ascending order. All 256 recorded sends accepted exactly one byte; 256 matching terminal results validated with no gaps or sequence/count errors. No parameter bytes, retry, interleaved discovery, last-ACK or other UART helper command was sent by this adapter. UART accepted-byte records are not an independent wire capture.

Each opcode had a 3000 ms observation window, with a separate count by 1700 ms. First intent: 2026-10-07T14:24:20.841084+00:00; final result: 2026-10-07T14:38:33.204434+00:00. Total host duration including final cleanup: 852.945 seconds.

There were 4 responding opcodes and 252 silent opcodes, with 15 received bytes total. All received bytes arrived by 1700 ms. No late-response, overflow, partial-send or health guard stopped this run.

| Opcode | Response | First receive callback | Bytes by 1700 ms |
|---|---|---:|---:|
| `0x50` | `0x7A` | 112 ms | 1 |
| `0x51` | `0x70` | 1619 ms | 1 |
| `0x53` | `0x72` | 1618 ms | 1 |
| `0x5A` | 12-byte discovery response | 111 ms | 12 |

`0x47`, `0x55`, `0x57`, `0x59` and `0xA0` returned zero bytes within their full three-second windows. The complete per-opcode map, including every silent value, is [standalone JSON](https://github.com/marlov1974/procon-melcobems-mini-a1m/blob/main/docs/opcode-sweep-results.json); its raw-evidence inventory SHA256 is `26eed6fef16890fb01bd2a894122aa35a62eac61a6c8db5aef10e769a041f3fc`. The [standalone report](https://github.com/marlov1974/procon-melcobems-mini-a1m/blob/main/docs/opcode-sweep.md) owns detailed interpretation.

## Interpretation and limits

Opcode-only `51` and `53` produced the defined negative replies after about 1.62 seconds. This is consistent with finite incomplete-command handling, possibly a timeout, but the internal timer and rejection reason are unknown. The known updater's active commands responded; the unused declared flash/EEPROM/status commands did not. This strengthens an absent/disabled-read hypothesis without proving it. No evidence of a replacement read opcode was found by this particular one-byte method.

The sequence has no physical reset or liveness check between entries. A silent opcode may need parameters or state; three seconds does not prove parser reset, and later results can depend on earlier bytes. No conclusion of unchanged flash/ECC/persistent state, working firmware readback or normal heat-pump communication follows from the sweep.

This run is separate from the earlier 64 read candidates, 26 write/reference transactions and isolated `41` example. Their historical totals are not combined.

## Final bridge state and restoration handoff

Shelly-only management reads verified at 2026-10-07T14:39:00.294893+00:00: correct previously pinned identity/firmware, own slot 8 stopped and disabled, all original scripts still stopped/disabled, both relays off, Serial still `js_uart` at 115200 8N1. The slot is retained because deletion previously caused unexpected restarts. These checks sent no UART bytes to Procon; there was no final discovery command after `FF`.

Procon's last operator-confirmed DIP is `00000000`. Physical return to `10000110` with power removed and subsequent Procon restart remains deferred by the operator until evening. Status: `WAITING_FOR_OPERATOR_RESTORE`; readback remains `BLOCKED_READ_PROTOCOL`. No future automated probes or normal Modbus polls are scheduled. After physical confirmation, use the exact saved Serial configuration and approved Shelly reboot if required, then verify normal identity and advancing telemetry.

## Verification

`make readback-test PYTHON=python3` passed with the existing suites plus 46 write-reference cases, 34 fixed read/ACK cases, 12 pure-sweep cases (including 256 ordered mock requests) and 5 offline summary tests. Only three flash-read candidates from the read/ACK adapter ran on hardware; the separately defined `59` and `A0` candidates were not run through that adapter. They were covered as single bytes in this sweep.

Firmware source, release images and G2 runtime are unchanged. Raw traffic, credentials and site snapshots remain private. Both tracked-file indexes are regenerated for this scoped change. Knowhow promotion was considered and intentionally kept package-local: command support and timeout behavior remain profile-specific and unresolved.
