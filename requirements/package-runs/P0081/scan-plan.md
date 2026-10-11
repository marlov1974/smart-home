# P0081 staged mapping plan

One identified Procon first; both pumps remain under native curve control. Operator states VP1/VP2 run curve during investigation. No SET, heating control, original bootloader or EEPROM commands.

1. Install qualified diagnostic image only after operator activation authorization. Native Shelly Modbus mode, 9600 8N1; all scripts stopped. Current observed serial config is js_uart/115200; Schedule.List is empty and all eight scripts stopped/disabled. Confirm no external weekly mission can start.
2. Verify UID, native idle control state, fresh normal data and API81d1/v1. Firmware rejects concurrent control ownership. Baseline: two separated passes of DIRECT07/A1/A2 and A3/27/28. Known A3 must complete; unimplemented direct queries may time out without being called unsupported.
3. DIRECT00..FF, two separated passes, then vetted A3 list including codes above255. Default2s inter-operation gap;800ms wire timeout;10 exclusive A3 attempts spaced1000ms;30s total firmware expiry. Native FAST and one background service separate diagnostic operations.
4. Stop on changed identity, active control, stale link, increased parser/UART errors, pump warning candidate, BAD_RESPONSE/ERROR, stop file or cumulative cap. No automatic cancel writes: accepted operation completes/expires within30s.
5. Store device identity, raw frames/length/checksum/status/age/generation, timestamps/latency/retries and before/after health in private JSONL. CSV and Markdown compare observations without guessing semantics. No physical observations exist yet.

Default runtime1800s; a fully exhausted A3 list can need longer. Resume is explicit and preserves observations; no unbounded repeat loop.
