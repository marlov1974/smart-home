# P0074 acceptance coverage

| Package area | Standalone artifact |
|---|---|
|1 MCU/memory/startup|hardware-reference/mcu-memory-map.md|
|2 Boot/update/recovery|hardware-reference/boot-update.md;clean-room-guide/recovery.md|
|3 Clocks|hardware-reference/clocks.md|
|4 Pins/peripherals|hardware-reference/pinout-gpio.md|
|5 RS485|hardware-reference/rs485-electrical.md|
|6 Modbus|protocol-reference/modbus-rtu.md;modbus-register-map.md|
|7 CN105 UART|hardware-reference/cn105-electrical.md|
|8 Framing/catalog|protocol-reference/cn105-packets.md;cn105-code-catalog.md;P0073catalogs|
|9 A3|protocol-reference/a3-service-protocol.md|
|10 LEDs|hardware-reference/leds.md|
|11 Watchdog/reset|hardware-reference/watchdog-reset.md|
|12 Timers|hardware-reference/timers.md|
|13 M0–M10|clean-room-guide/from-zero-to-led.md;rs485-bringup.md;cn105-bringup.md|
|14 Vectors|verification-vectors.json;clean-room-guide/verification-vectors.md|
|15 Pseudocode|protocol-reference/modbus-rtu.md;cn105-transport.md;a3-service-protocol.md;current commands explicitly absent|
|16 Development policy|known-unknowns.md, Continuing development without vendor firmware|
|17 Independence test|clean-room-guide/independence-review.md;tests/test_platform_spec.py|
|18 Machine description|platform-spec.json|

All paths above are relative to the standalone docs directory except tests/. Remaining limits are explicit: unknown exact MCU/electrical limits/bootloader/watchdog inheritance and unresolved protocol semantics. They do not become proven facts through publication. No current control acknowledgement/lease/fallback exists to specify.
