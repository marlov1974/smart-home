# P0075 pure opcode survey

## Review and authorization

Review: **WARN — explicitly risk-authorized hardware experiment.** The user requested `00..FF`, acknowledged possible erase or persistent changes and the absence of a recovery guarantee, then clarified that every trial must contain exactly one opcode byte, without parameters or helper traffic. This is a separate authorization from the earlier eight-byte FF write experiment. The survey is not read-only; its authorization does not establish that unknown opcodes are generally safe to send.

The earlier standalone `0x41` check sent exactly one byte. It observed no received bytes at 1,705 ms or 3,355 ms. That record remains separate. The full survey starts at `0x00` because the user clarified that `0x41` was an example.

## Core contract

`makeOpcodeSweepCore` accepts authenticated `probe`, `status` and `stop` operations. A probe must use the next integer opcode, from 0 through 255, with `seq = opcode + 1`. It submits exactly one byte to UART. A repeated request for the current sequence returns cached state without another transmission; older, skipped or out-of-order requests are rejected. Loading the script and running its timers do not transmit bytes.

Each trial has a 3,000 ms observation window and stores at most 128 received bytes. It records callback timestamps, first-response latency and the number of bytes received by 1,700 ms. These are Shelly callback observations, not measurements of arrival on the wire. A callback after 2,800 ms causes a stop at the observation deadline; late or unsolicited data, short sends, overflow and clock errors also stop the survey. The initial passive session expires after 15 minutes. After the first request, 120 seconds without host contact expires the session.

No discovery or last-ACK request is inserted between opcodes. In particular, `0x50` and `0x5A` appear only at their own positions in the requested range.

## Private host contract

The host verifies the saved Shelly identity, Serial configuration and owned script slot, uploads the exact source and reads it back before starting. It writes a one-byte intent record before each request and a result record afterward. Memory checks run every 16 opcodes. Completion or failure leads to a stop and disable attempt for the owned script, with stop verification.

Shelly HTTP status checks supervise the bridge; they do not establish that Procon remains responsive. The host does not retry uncertain transactions, automatically resume an interrupted run or delete the UART-owning script. Tokens, site addresses, generated source and raw records remain private.

## Offline aggregation contract

`summarize_opcode_sweep.summarize(input_dir)` snapshots only files named `XX-intent.json` and `XX-result.json`. It does not open session or RPC credential files and performs no network or device operations. It checks:

- Exactly one declared opcode byte per intent, `seq = opcode + 1`, matching result identity and a contiguous prefix starting at `00`.
- Accepted transmit counts, base64 decoding, the 128-byte response bound, callback metrics and consistency of `received_by_1700` with the recorded callback times.
- Terminal, waiting and halted states; missing tail results; gaps; and any further intents after a stop or unresolved waiting result.

The result is `COMPLETE`, `PARTIAL`, `STOPPED` or `INVALID`. A complete result requires validated terminal records for all 256 opcodes. A still-running prefix or missing final result never becomes a complete survey by assumption.

The sanitized output includes each opcode, documented enum label where available, state, accepted byte count, response count, first-response time and bytes received by 1,700 ms. Only one-byte responses are rendered as hexadecimal. Longer payloads are withheld. A valid 12-byte `0x5A` discovery response may be decoded into its four numeric fields and checksum status without publishing its raw bytes. Enum labels describe host constants; silence does not prove a command unsupported.

`write_summary(input_dir, output)` creates the output exclusively with mode `0600` and never changes input files. It refuses to overwrite an existing output. A final file snapshot cannot establish whether the original capture files were previously overwritten; the report explicitly preserves that provenance limit. Aggregation also makes no claim about persistent effects, successful cleanup or restoration of normal operation.

## Verification and handoff

The sweep core passes 12 offline cases, including a complete 256-opcode run that produces exactly 256 ordered single-byte transmissions. The suite covers authentication, ordering, replay, helper rejection, short sends, overflow, late or active reception, deadlines, expiry and a passive adapter.

The aggregator passes five offline tests covering a complete 256-record fixture, a partial tail, gaps, wrong sequences, overflow, the 1,700 ms boundary, halted state, sanitized discovery, exclusive output creation and unchanged input files. These fixtures are software tests, not physical observations. Final live findings are recorded separately after the survey finishes.

Existing firmware source and release files are unchanged. Their on-device contents and possible effects of unknown commands cannot be established from transport responses alone. After the survey, retain the owned script stopped and disabled. Restore the saved Serial profile and verify normal telemetry only after the operator confirms normal DIP settings and the Procon power cycle.
