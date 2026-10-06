# Known facts from prior reverse engineering

## Original firmware

Verified from Procon v3.1.05:
- application `A1M_R5_Release_08008000.bin`
- size 96,692 bytes
- SHA-256 `2ae03b0cdc684bcccbf9f5281878175f5ca53b144e3e32cc223159fcc4654766`
- application flash base `0x08008000`
- ARM Cortex-M4 / Thumb-2
- vector table at `0x08008000`
- observed initial SP `0x20010000`
- Reset_Handler pointer `0x0800A341` (Thumb; code at `0x0800A340`)
- prior mapping: flash address = 0x08008000 + file offset

Exact STM32 part number remains to be verified before trusting a clean linker script.

## CN105 reference knowledge for later milestones

Open-source reference studied: `F1p/Home-Assistant-Mitsubishi-CN105-to-MQTT`.

Typical GET frame: `FC 42 02 7A 10` + 16-byte payload + checksum.

Reference checksum: `checksum = (0xFC - sum(all preceding frame bytes)) & 0xFF`.

A3 service 27: `FC 42 02 7A 10 A3 00 1B` + thirteen zero bytes + checksum `74`. Service 28 uses `A3 00 1C`.

The reference explicitly substitutes Geodan service 27 for TH32 and 28 for TH34. A3 response payload byte 3 values 1/2 are valid/result; 0 is not ready and is retried. Its service operation is separate from normal polling and uses roughly one-second retry cadence.

## Geodan observations

Controller service display:
- Ref. add. 0 / Information 027 -> 6
- Ref. add. 0 / Information 028 -> 6

These are consistent with brine temperatures. Do not infer all display information numbers equal A3 service numbers solely from the display.

## Procon A3 experiments

Modified firmware captured replies such as `A3 00 1B 00 00 ...`. Thus service code 27 was echoed, but status stayed 0 in tested builds.

A debug build captured the full 16-byte payload and counted responses. Eleven A3 replies were observed, but later evidence showed they occurred across normal Procon polling cycles, not as exclusive one-second retries.

Multiple scheduler-lock attempts failed because the internal scheduler/index model had been interpreted incorrectly. Do not reuse those hook assumptions.

## 0x08010EDC lead

A failed experiment treated `0x08010EDC` as raw UART TX and broke communication.

Later analysis of an original caller near flash `0x08012A7A` observed:
- compute index x 36;
- base pointer from `[r4+0xF0]`;
- r0 = selected 36-byte entry;
- r1 = byte [r0+32];
- r2 = byte [r0+33];
- r3 = uint16 [r0+34];
- call `0x08010EDC`;
- communication state then becomes 5.

Inside `0x08010EDC`, prior analysis observed copying toward RAM around `0x2000215F`, with r1 participating as copy length, and state/parameters around `0x2000211A`, `0x2000211C`, `0x2000219F`.

Treat this only as a reverse-engineering lead, not a callable API.

## Momentary power background

External CN105 0x07 decoding uses coarse byte-sized power fields. Prior work did not find evidence that Procon discards hidden decimal precision in these standard fields.

## P0069 update — 2026-10-06

Strong inferred MCU family: STM32L433xx; all99 vector positions match ST L433 startup reserved pattern. Physical package/density unverified. See HARDWARE.md for original addresses and trace confidence. New clean application uses USART3 PC10/11AF7, PD2 direction. Software tests passed; operator flash/readback pending. No new live readings or CN105 measurements.

P0069 attempt2: initial M1 hardware readback failed with seven timeouts. Shelly settings96008N1 verified; operator confirmed flash/reconnect/DIP/reset. Original USART3 SWAP=1 was omitted in M1; r2 corrects only CR2 bit15 and passes enhanced wiring-aware emulator. Physical r2 test pending.

## P0070 — 2026-10-06

M1 r2 hardware pass: operator reports blinking; five consecutive FC04 raw input0 reads returned888. Evidence: `analysis/live/20261006T190106Z-m1-r2-readback.json`. This supersedes older pending-M1 status.

P0070 adds USART1 read-only ATW connect/GET0x04. Input0 stays888; input1=70, input2=Hz or65535 unknown/stale; input3 validity, input4 age and further counters. UART/packet errors are visible. CN105 electrical communication remains unverified until operator flashes P0070 and live values are captured. No device setting writes by this package. Firmware tests pass; hardware milestone M3/M4 remains pending.
