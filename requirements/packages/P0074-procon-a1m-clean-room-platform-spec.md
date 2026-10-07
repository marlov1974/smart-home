# P0074 — Procon MELCOBEMS MINI A1M clean-room hardware and firmware specification

Operator request 2026-10-07: create a complete, standalone engineering specification of the Procon MELCOBEMS MINI (A1M) hardware/firmware interface so future development no longer requires reading the original vendor firmware or reverse-engineering our current implementation.

P0074 follows P0073. Reuse verified findings produced by P0069-P0073, including the CN105 cross-reference work, but independently document the device as a platform.

## Primary acceptance criterion

A competent embedded developer must be able to receive:
- an A1M device;
- this documentation;
- an appropriate ARM toolchain;

and implement a new compatible application firmware from an empty source tree **without reading our firmware source and without inspecting/decompiling the original Procon firmware**.

The documentation must therefore be normative and self-contained. Statements such as "see platform.c", "copy the existing implementation", or "look at the original BIN" do not satisfy the requirement.

Our current firmware may be used to verify facts while P0074 is authored, but the final specification must stand on its own.

## Evidence discipline

For every hardware/protocol fact record provenance and confidence:
- hardware measured/verified;
- P0069-P007x hardware verified;
- original-firmware static analysis;
- vendor documentation;
- external CN105 project;
- strong inference;
- hypothesis/unknown.

Do not silently turn an implementation detail into a hardware requirement. Distinguish:
1. what the A1M hardware requires;
2. what the vendor boot/update environment requires;
3. what CN105/Modbus protocols require;
4. design choices made only by our firmware.

Maintain a visible Known Unknowns section.

## Required document hierarchy

Create/update a standalone documentation set in the public-export project, organized approximately as:

```text
docs/
  hardware-reference/
    overview.md
    mcu-memory-map.md
    clocks.md
    pinout-gpio.md
    rs485-electrical.md
    cn105-electrical.md
    leds.md
    watchdog-reset.md
    timers.md
    boot-update.md
  protocol-reference/
    modbus-rtu.md
    modbus-register-map.md
    cn105-transport.md
    cn105-packets.md
    cn105-code-catalog.md
    a3-service-protocol.md
  clean-room-guide/
    from-zero-to-led.md
    rs485-bringup.md
    cn105-bringup.md
    build-link-flash.md
    verification-vectors.md
    recovery.md
  known-unknowns.md
```

Adapt names where useful, but preserve the separation between hardware reference, protocol reference, and from-scratch implementation guide.

## 1. MCU and memory map

Document:
- exact MCU part number/package if verified; otherwise exact supported assumption and unresolved marking;
- architecture/core and instruction mode;
- application flash base;
- flash regions;
- bootloader/reserved regions;
- application maximum bounds;
- SRAM regions and proven usable bounds;
- vector-table format and location;
- initial stack requirements;
- Reset_Handler requirements;
- alignment requirements;
- linker-script requirements;
- sections that must never be overwritten;
- padding/image-size requirements, distinguishing bootloader/updater requirements from our release packaging choices.

Provide a diagram/table with absolute addresses.

Where exact flash density remains unknown, state it explicitly and define only the verified safe application window.

## 2. Boot, reset, update and recovery

Describe the complete observable lifecycle:

```text
power/reset -> vendor boot/update environment -> application vector -> startup -> main
```

Document:
- what is known about the bootloader;
- what is known about the vendor host updater;
- application-entry expectations;
- vector validation if known;
- image transfer/package format if known;
- reset behavior;
- recovery procedure;
- what remains unknown about the device-resident bootloader;
- how to return to vendor firmware without overwriting unrelated flash.

A developer following only this document should understand how an application image becomes executable.

Do not reproduce proprietary updater binaries or vendor firmware.

## 3. Clock tree

Document every clock fact required to reproduce a working firmware:
- clock source;
- startup/default clock;
- selected system clock;
- peripheral clock domains;
- relevant prescalers;
- resulting CPU/peripheral frequencies;
- register-level initialization sequence where verified;
- timing assumptions used by UARTs/timers/watchdog.

Separate required hardware configuration from our preferred configuration.

## 4. Complete pin/peripheral map

Create a table for every identified MCU pin/peripheral used by the A1M board.

At minimum include:
- RS485 RX/TX;
- RS485 DE/RE or direction control;
- CN105 RX/TX;
- LEDs;
- watchdog-related signals if applicable;
- timers used/relevant;
- test/debug pins if identified;
- unused but confidently identified board-connected pins.

For each: MCU pin, peripheral/alternate function, direction, active polarity, electrical role, initialization, evidence and confidence.

## 5. RS485 electrical and UART specification

Document enough to implement RS485 without our source:
- USART instance;
- GPIO pins and alternate functions;
- SWAP/inversion or unusual USART configuration;
- transceiver direction GPIO and polarity;
- baud rate;
- data bits/parity/stop bits;
- TX enable/disable sequencing;
- turnaround timing;
- RX framing/error handling;
- Modbus inter-frame timing;
- bounded TX timeout behavior;
- relevant electrical observations/limitations.

Include a minimal register-level bring-up recipe and a known-good byte-level test.

## 6. Modbus RTU protocol

Document:
- slave/unit ID behavior;
- serial format;
- supported function codes;
- CRC16 algorithm and byte order;
- register word byte order;
- request/response examples;
- exceptions/silent-drop behavior;
- timing requirements;
- stable register map and scaling;
- validity/freshness conventions;
- command acknowledgement/lease semantics once P0072 defines them.

Include exact test vectors with request bytes, expected response bytes and CRC.

## 7. CN105 electrical/UART specification

Document enough to bring CN105 up from zero:
- USART instance;
- MCU pins/AF;
- baud/data/parity/stop configuration;
- any SWAP/inversion;
- direction/electrical assumptions;
- startup state;
- RX/TX timing;
- connect/handshake requirements;
- timeout/reconnect behavior;
- ownership rules.

Provide a minimal sequence that reaches a verified CN105 connection without relying on our implementation.

## 8. CN105 packet/protocol specification

Document:
- frame structure;
- sync/type/preamble/length/payload/checksum;
- checksum algorithm;
- GET/SET packet families;
- response matching;
- payload endianness/scaling conventions;
- connection packets;
- malformed-frame handling;
- transaction ownership;
- timing.

Integrate/link the complete CN105 code catalog produced by P0073, including codes not currently used by our firmware.

A reader should be able to construct and parse packets from the documentation alone.

## 9. A3/service protocol

Make the P0071 discovery explicit and normative.

Document:
- A3 frame structure;
- service-code field;
- known status semantics;
- service 27/TH32 brine inlet mapping;
- service 28/TH34 brine outlet mapping;
- checksum;
- retry timing;
- completion/exhaustion;
- raw payload retention;
- the hardware-confirmed rule that an active service operation requires whole-operation CN105 exclusivity.

Explicitly state that ordinary CN105 GET/connect/other traffic must not be inserted between not-ready retries for the working Geodan sequence.

Provide working byte examples and timing diagrams from independently summarized project evidence.

## 10. LEDs

Document every identified LED:
- MCU GPIO;
- polarity;
- physical identity/location if known;
- state after reset;
- vendor behavior if established;
- current clean-room heartbeat convention;
- register-level recipe to configure/toggle it.

The clean-room guide must use LED blink as the first physical bring-up milestone.

## 11. Watchdog and reset behavior

Document:
- watchdog type;
- whether it is already active when application starts;
- timeout/window if known;
- refresh mechanism;
- startup implications;
- what happens when refresh stops;
- reset-cause registers/interpretation if available;
- safe implementation pattern.

This must be sufficient to prevent a new firmware from unexpectedly resetting merely because the developer did not know a watchdog was inherited.

## 12. Timers and monotonic time

Document:
- timer/peripheral used or recommended;
- clock source;
- tick frequency;
- initialization;
- overflow/wrap behavior;
- unsigned-delta pattern;
- timing requirements for Modbus, CN105 and A3;
- distinction between required protocol timing and our implementation choices.

## 13. From-scratch bring-up guide

Provide a staged implementation path that starts with an empty project:

```text
M0 vector table/linker/startup
M1 clock
M2 LED heartbeat
M3 watchdog survival
M4 RS485 UART
M5 Modbus FC04 register0 = 888
M6 CN105 UART
M7 CN105 connect
M8 GET04 compressor Hz
M9 A3/27
M10 alternating A3/27 and A3/28
```

For every milestone specify:
- minimum required code/peripherals;
- expected observable behavior;
- exact verification procedure;
- failure symptoms and likely causes;
- rollback/recovery.

Do not require copying any source from our implementation.

## 14. Verification vectors

Create implementation-independent golden vectors for:
- Modbus CRC;
- FC04 request/response for register0=888;
- invalid CRC;
- unsupported function behavior;
- CN105 checksum;
- connection frame(s);
- GET04 request/response parsing;
- A3/27 request;
- A3/28 request;
- status0 retry;
- completed A3 response examples when hardware evidence exists.

Where possible provide both human-readable hex and machine-readable JSON/test-vector files.

These vectors must be usable by a completely separate implementation.

## 15. Hardware-independent pseudocode

Where sequencing is nontrivial, provide implementation-neutral pseudocode/state diagrams for:
- RS485 receive/frame handling;
- CN105 transaction arbiter;
- CN105 reconnect;
- A3 exclusive service operation;
- FAST/SERVICE scheduler;
- command/failsafe handling.

Do not mirror our C source line-by-line. Describe behavior and invariants.

## 16. Development without original firmware

Create a dedicated section titled approximately "Continuing development without vendor firmware".

It must identify which artifacts replace future dependence on the original BIN/manual analysis:
- hardware map;
- boot/memory specification;
- complete CN105 catalog;
- Modbus semantics;
- golden vectors;
- protocol state machines;
- known unknowns;
- evidence/confidence metadata.

State a policy that new features should first consult these clean-room specifications. Original vendor firmware analysis becomes a last-resort research activity, not the normal development workflow.

## 17. Independence test

Before P0074 is accepted, perform a documentation-only review:

Pretend the reviewer has no access to:
- original Procon BIN;
- vendor updater internals;
- Smart Home private analysis;
- current firmware source.

Using only the P0074 docs and public/toolchain prerequisites, answer and demonstrate:
- where the application is linked;
- how reset reaches it;
- how to blink the LED;
- how to keep watchdog alive;
- how to initialize RS485;
- how to answer Modbus 888;
- how to initialize CN105;
- how to request compressor Hz;
- how to execute A3/27 correctly.

Any answer that requires "look in our source/original firmware" is a documentation defect and must be fixed or explicitly listed as an unresolved blocker.

## 18. Machine-readable platform specification

In addition to Markdown, create a machine-readable platform description, e.g. `docs/platform-spec.json` or YAML, containing verified:
- memory regions;
- peripherals;
- GPIO/pin mappings;
- UART configurations;
- protocol timing constants;
- LED/watchdog definitions;
- key packet constants;
- evidence/confidence metadata.

This is intended for future tooling and AI-assisted development.

## Public-repository constraints

P0074 documentation is intended for the standalone open-source repository prepared by P0073.

Do not include:
- original firmware;
- updater binaries;
- vendor PDFs;
- raw vendor disassembly/decompilation;
- substantial copied vendor text.

Write independent technical descriptions and preserve provenance/attribution where required.

## Completion criteria

P0074 is complete only when:
1. the standalone specification covers hardware, boot, RS485, Modbus, CN105, A3, LEDs, watchdog, clocks, timers and memory;
2. the complete P0073 CN105 catalog is integrated/referenced;
3. machine-readable platform data exists;
4. golden verification vectors exist;
5. known unknowns are explicit;
6. the documentation-only independence test passes as far as current evidence permits;
7. every remaining dependency on original firmware/source is listed as a concrete unresolved item rather than hidden.

No unrelated Smart Home/Shelly runtime changes.
