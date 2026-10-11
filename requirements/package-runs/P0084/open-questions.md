# P0084 remaining evidence

1. **Physical D-path ownership:** match MCU P7.7 input and timer4 output to CN22 on the exact FTC board, using schematic/board continuity evidence or matching display firmware. The current manual shows connector wiring but not internal net routing. CN3C remains an alternative.
2. **Return framing and menu identifiers:** trace complete D reply packing and match a single display action to its code. Do not infer all menus from the shared service selector.
3. **Settings session completion:** resolve validation/default preservation, apply acknowledgment, persistence and rollback before implementing SET65/79. A90F8 stages several fields, so blindly setting a single byte is unsafe and unjustified. Match21.00 before any deployment.
4. **Latency:** qualify scheduler clock and separate request acceptance, forwarded sensor response and display refresh. No fixed10–15s software timeout is established.
5. **Parity gaps:** identify curve-point editing, pump-economy timer, energy-monitor calibration writes and screen-local menus. A missing entry in public protocol code is not a firmware impossibility proof.

## Smallest next verification experiment (not performed or authorized by P84)

First obtain exact-board schematic/net evidence or display firmware. If unavailable, a separately authorized qualified operator could make a **high-impedance isolated passive observation** on the documented display link while performing one ordinary Running Information read, e.g.506. Record waveform levels and timing without driving the link; correlate the display action and response. Keep native controls unchanged and do not simultaneously submit A3 requests. This would distinguish D from other links and establish electrical timing before any decoding assumptions.

A later second isolated test could compare a local service506 with a forwarded brine27 request. That would help separate transport latency from source-controller latency. Neither test occurred in P84; no new physical access is needed to preserve the offline result.
