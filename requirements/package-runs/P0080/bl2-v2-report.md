# P0080 BL2 protocol2 correction

Only BL2 changes relative to installed snapshot image; seven feature binaries identical. BL2 6584/8192 bytes. Layout3833993797 and ABI1 retained. Full image SHA256 c3f4cc3076e35df64b69efe81ce2a132d81b2e20d9c5d65b9cda11a485af8cb6. Manifest prefix fingerprint0xd9dd3c62.

Version2 in resident status and OTA wire prevents mixing with old tools. Fingerprint now covers first56 bytes, excluding stored CRC and commit trailer. Host plan requires v2 metadata; postboot verifies prefix CRC. Test with two internally valid manifests that share whole-buffer CRC rejects stale base before erase. Old wire ignored; old resident status rejected by host before maintenance commands.

Verification: real ELF module/ABI/status/snapshot and flash protection scenarios; native real-C OTA success/duplicate/repair/mismatch and523 mutation cuts; host delayedACK, lostACK, peer ordering and legacy rejection. Feature binaries unchanged, so prior37-case snapshot ARM regression remains applicable; targeted BL2 tests rerun. First-install flash started under explicit operator authorization. Normal boot verification pending physical DIP restoration.

## Transfer result

Operator authorized update with DIP00000000. Bootloader discovery/preflight passed. Full98304-byte application erase acknowledged71; all223 write packets acknowledged73, total53312 bytes. No retry. Original bootloader excluded, no option-byte changes. Image SHA256 c3f4cc3076e35df64b69efe81ce2a132d81b2e20d9c5d65b9cda11a485af8cb6.

Completed18:45:03 UTC. Cleanup verified: all scripts stopped/disabled, relays off, persisted Serial js_uart1152008N1. Firmware readback and normal boot NOT yet verified. Seven feature module binaries identical to installed snapshot version; BL2 changed to protocol2/data-only manifest fingerprint.

Next: power off Procon, DIP10000110, power on. Read-only verify via verify_bl2_v2_boot.py: status protocol2, full-set valid1, fingerprintd9dd3c62, same UID, snapshot sequence and CN105 updates; control idle. Do not use legacy protocol1 updater. No additional physical action performed.

## Normal boot verified

Operator restored normal DIP and restarted. Three read-only FC04 status reads passed protocol2 gate, full-set-valid1, mode0, layout3833993797, manifest prefix CRC0xd9dd3c62 (3655154786), matching local release. Same UID5898296/909201410/540096578. Snapshot sequence1/2/3 and sample generations advance. CN105 linked, error/UART-error counters zero, uptime rises with no reset observed.

Latest frozen capture: compressor0Hz, supply/return28/28C, brine7/7C, primary flow13L/min, DHW50.5C, native target30.5C. No control lease or effect target enabled. Device-reported values only; no diagnosis of why compressor is stopped. Brine pump status/step remain unavailable.

Temporary UART helper stopped/disabled; runtime restored115200 and cleanup verified. No actuator/control writes, OTA entry, or flash writes during this verification. This validates physical status fingerprint reporting and normal boot. Protocol2 transfer/base-mismatch behavior remains emulator-tested, not a new physical OTA test.

Raw provenance: rpc.jsonl, samples.json, result.json, cleanup.json in this directory.

## Second Procon BL2-only

Operator connected a different Procon in DIP00000000 and explicitly requested BL2 first, remaining firmware over OTA, next device address. Existing device1 UID remains5898296/909201410/540096578; new factory UID unknown until resident normal-mode read. No fabricated UID or persistent software address assigned: next Modbus address2 is selected with physical DIP01000110 (switches2,6,7 ON).

Exact protocol2 BL2 from release-bl2-v2 retained. Full application erase98304 bytes acknowledged71, only6584 load bytes written in28 packets, each direct73 ACK. Rest of application intentionally erased. Full image hash4670bb06b3ca0829106a5bb73141270dfcd77aafa05ac748f3c161a9ced84732. Original bootloader excluded, no option-byte writes. Transfer complete18:59:12 UTC; cleanup verified, scripts stopped/disabled, relays off. No normal-boot/readback verification yet.

Real C emulator test initialized this exact blank-feature image using all7 OTA chunks and compared all98304 bytes with release-bl2-v2: exact match,199 OTA frames. This is offline evidence; physical full-set initialization remains pending.

Next operator action: power off, DIP01000110, power on. Then read resident address2/status384: protocol2, valid0, CRC0, unique factory UID. Blank modules are expected and must not run CN105. Complete authorized OTA initialization with all7 modules, then verify valid1/fingerprintd9dd3c62 and telemetry. Native-state automatic gate cannot inspect FTC without modules; no pump commands have been sent by this BL2-only image.

## D2 OTA with D1 WAIT verified

Operator confirmed D2 reboot and both units on shared bus. D1 address1 factoryUID5898296/909201410/540096578 matched inventory, fullset valid/protocol2/fingerprintd9dd3c62 and native ready. Blank D2 address2 UID5373989/909201412/540096578 distinct, protocol2/valid0/CRC0 and same layout. No device identity was written: UID factory-read, address physically DIP-selected.

D1 acknowledged FE WAIT900s at2026-10-09T19:16:38.171761+00:00. D2 acknowledged FF ENTER. Native state on blank D2 is not observable before modules; known BL2-only image cannot issue FTC control. All7 modules installed,45056 padded firmware bytes,199 frames. Commit and EXIT succeeded with updated2s receiver window, no manual recovery. D2 rebooted, valid1/normal0/prefixCRC d9dd3c62/same UID confirmed. This is a successful physical protocol2 full-set OTA on a shared two-device bus.

Postboot three frozen snapshots1/2/3, CN105 linked, zero protocol/UART errors, generations advance. Latest device-reported values: compressor36Hz, flow34.5C, return30.5C, brine5.0/3.0C, primary flow14.0L/min, DHW51.5C. Control state0; no effect lease or pump setpoint writes.

Cleanup verified after uploader and reader: helper stopped/disabled, serial restored115200, relays off. D1 remains scheduled to leave WAIT approximately2026-10-09T21:31:38.171761+02:00; physical post-expiry D1 response not yet checked. WAIT retains native CN105 servicing and expires automatically; no early wake command exists in this implementation.

Evidence: device2-bl2-only/ota-20261009T191632Z and device2-normal-20261009T192246Z. Original earlier silent-D2 preflight retained; operator identified missing reboot. No Git commit/push.

D1 WAIT expiry physically verified2026-10-09 19:35:51–19:36:01 UTC: address1 sameUID, mode0, fullsetvalid1, correct prefixCRC, compressor26Hz valid, CN105 replies402→403, uptime2942→2952, errors0/UARTerrors0. No reset during observation. Read-only FC04; helper cleanup verified. Evidence P0080/d1-after-wait-20261009T193549Z.
