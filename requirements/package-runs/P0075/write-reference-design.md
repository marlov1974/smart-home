# P0075 follow-up: documented write reference

## Review and authorization

WARN. The operator explicitly requested learning write behavior before returning to 0x57. This authorizes a new bounded 0x53 experiment and supersedes the prior read-only restriction for this follow-up only. No erase, EEPROM, option bytes, bootloader region or heat-pump controls are included. Earlier P0075 reports remain dated read-only observations. Firmware backup is still unavailable; this is not a full updater.

Physical Procon DIP/power is controlled by the operator. Original Shelly profile/scripts are captured; only a new stopped-by-default maintenance slot and Serial profile may change. Retain the stopped/disabled slot after restoration because Script.Delete caused unexpected restarts even after a preceding reboot. No Modbus request is sent while boot mode is selected.

## Fixed target and packets

Reference r3 SHA256 f0d33dab1a181d133bc1d5b9c5501ceb1952e71b798d93514a6bf9a1932a2fde,98304bytes,last non-FF offset11319. Reference offset0x17000..0x177FF is allFF. The test target is only eight FF bytes at application-relative0x17000, corresponding0801F000..0801F007 under the exercised writer translation. It is inside existing padding and eight-byte aligned. The current physical flash/ECC state is not verified by a reference file.

On inferred STM32L433, programming includes hidden ECC. FF programming is not guaranteed to be a no-op, and already programmed flash can reject it. A correct-frame NAK need not mean bad framing. Do not automatically erase or retransmit to force ACK. No claim of physical successful writing without readback.

Frames: valid 53080000700100ffffffffffffffff22aae82ea6; wrong CRC with valid outer sum 53080000700100ffffffffffffffff23aae82ea7; correct CRC with wrong outer sum 53080000700100ffffffffffffffff22aae82ea7. All are20bytes. The invalid controls might still reach programming if unknown validation order differs; all use the same low-impact target. No tail byte is a known alternate command.

## Procedure and interpretation

First validate discovery; optionally capture a standalone last-ACK0x50 baseline. Send one complete negative control, save direct reply, then at most one0x50 query if useful. Repeat with the other complete control, then one valid packet. No automatic retries of writes. 0x50 can return stale ACK, so preserve provenance rather than count it as proof of current request acceptance.

Only after a complete negative control responds use its identical bytes split19+1, then7+13. Allowed local timer gaps20/200/1000/3500ms; record actual TX times, receive before/after tail, and stop further bytes if RX arrives early. Never put discovery or0x50 between fragments. Every probe has a bounded receive window and response limit32bytes. A response only after completion, relative to a replying whole-frame control, supports accumulation; different gap outcomes bracket rather than identify timeout. Full silence still leaves transport and session prerequisites open.

## Function design and tests

New makeWriteReferenceCore injects clock/send, hardcodes three frames and exposes only discover/probe/split/last_ack/status/stop. Session/token+sequence cache prevent retransmission on duplicate requests. Max16transactions, one valid-write request per initialized core, bounded32RX, no arbitrary address/payload, fail on short send and unsolicited/late overflow. Split only negative controls and defined boundaries/gaps. The HTTP adapter binds qualified UART0 and does not transmit on startup. Tests use fake I/O and independent frame arithmetic.

Host session captures exact Shelly identity/config/scripts, verifies source after upload, creates only its own slot, sets autostartfalse, changes Serial tojs_uart115200 and uses the already authorized required reboot. It arms passively before any Procon command. Host must persist every result and stop on ambiguous/invalid discovery, unexpected reply or memory error. No automated full-image programming or firmware source change.

Recovery: stop/disable ownslot, operatorProcon-onlynormalDIP10000110restart, exactSerialmb_client9600restore/approvedreboot if needed, identity3/1/3/0 plus advancing telemetry verification. Keep ownslot stopped; do not delete it automatically. Offline tests do not count as physical observations.
