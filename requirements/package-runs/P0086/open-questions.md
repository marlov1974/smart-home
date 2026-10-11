# P0086 remaining questions

- **Energy:** timebase/unit calibration, 21.00 packing, coherent acquisition, mode/reset boundaries and a comparison interval without forced folds. Odd BCD truncation and fold loss are resolved for 20.01.
- **Settings:** external sequence producing internal service 1002 and CF978 acknowledgment; full import defaults/validation; persistence commit; rollback after link loss or restart. GET status alone is insufficient.
- **Personality:** upstream acquisition of 08EB and its physical input; dynamic UART reinitialization and native communication consequences. The ROM override is inactive in the supplied image.
- **Electrical:** exact MCU/package/oscillator, UART1 route through components to the connector, reference/levels/inversion/isolation, adapter DTR/RTS behavior. Conditional 9600 baud is not a measurement.
- **Installed 21.00:** a justified non-MMIO read address and expected meaning. Never transfer 20.01 RAM addresses blindly. The reviewed 20.01 near-load aliasing is resolved; no qualified full-flash route exists.
- **Logs:** D-field semantics and physical peer; fragments crossing response boundaries. Absolute event timestamps are absent. Reading drains the buffer and can lose frames.

These are bounded follow-ups, not permission for another broad scan. Offline codec/log tests do not depend on knowing the physical connector.
