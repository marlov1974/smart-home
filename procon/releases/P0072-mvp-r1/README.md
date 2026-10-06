# P0072 MVP r1 — read-only candidate

Operator flashes `procon-mvp.bin` using the same vendor procedure as P0071 r2. 98304bytes (96KiB), application base0x08008000, FF to0x0801FFFF, bootloader excluded. Code7596bytes,BSS844bytes. Inferred STM32L433 target unchanged. Recovery: previous immutable P0071-brine-r2 BIN or original via [RECOVERY](../../docs/RECOVERY.md).

**No controls in this revision.** FC04 only; every Modbus write rejected. No CN105 SET or pump override. 20-field API with18 mapped/derived candidates and2 explicit unavailable brine-pump fields. [Register map, units, evidence and limitations](../../docs/MVP_API.md). Physical new telemetry validation pending; P0071 hardware evidence does not automatically validate P0072.

Schedule FAST04/0C/14/0B/09/15/26 → full A3/27 → FAST → full A3/28 → repeat. Service owns link through up to10attempts at1s retry. Watchdog/Modbus remain live; Hz10s TTL can expire during extended retry operation. Other FAST TTL30s,brine60s; all expose status/age. Water-side power uses rho1kg/L,cp4180J/kg/K, no glycol correction/COP; requires fresh temperature/flow and<=2s acquisition skew.

Identification input0=888,input1=72,input68=1,input69=1,input70=1,input71=4. Do not use P0071 helper to decode this version. After flash use `python3 procon/tools/read_mvp.py --samples 10 --interval 2 --output <new-file.jsonl>`. Compare raw and decoded values with Mitsubishi display. No automatic physical tests/flash by Codex.

Software verification: native ASan/UBSan Modbus/parser/scheduler/telemetry tests,13 compiled-ELF ARM scenarios including MVP registers concurrent with service, deterministic rebuild,imagebounds/FFtail and prior-release hashes. Hardware attempts0/3. Controls,command acknowledgement and lease/fallback are explicitly deferred pending verified SET behavior. Pump output level is reference-backed,not calibrated RPM.

SHA256 `f8823fab325018c31f093215cd72d19c6d28dd28082bcd64d83df82e88b3b4a9`.
