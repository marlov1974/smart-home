# UART1 diagnostic snapshot families

New static reachability:9E77A low nibble2/high nibble1 →9DAC0, gated by diagnostic personality,3D4C=1 and transmitter3D53=0. Request byte1 selects00/01/02/10; others call9E92A. High nibble0 instead uses9D88C (F0 log); other high nibbles error. This is not a new opcode scan or a physical observation.

| Subcommand | Handler | Response total bytes | Proven selected response fields (frame byte0 origin) |
|---|---|---:|---|
|00|9DAF0|100|23..24 effective flow target3908;25..26 DHW target3906;62..63 flow0662;64..65 return0664; wordsLE|
|01|9DE68|66|61..62 primary flow source322E,LE; numerous native state/age nibble pairs|
|02|9E224|62|byte26 native request39C3; actuator states and timers; exact units not automaticallyHz|
|10|9E47C|13|Packed two-bit operation flags viaA24D4..A2700; full labels still open|

All responses start12,length,subcommand,02 and use UART1 additive checksum. `uart1_snapshot.py` accepts only these exact lengths/subcommands and preserves all unknown bytes. It returns raw values; no calibration or atomic snapshot claim. Tests are synthetic and offline. The P86 reader's77-byte cap was its safe subset, not the device's full response maximum; it was not silently enlarged in production.

The apparent peripheral write in decompiled9DAF0 is a processor-module addressing defect, explained in decoder-and-pin-corrections. Full side-effect freedom is still not claimed without the remaining called-function audit. These snapshots provide useful diagnostic content; they do not establish equivalent normal control authority or CNIT wiring.
