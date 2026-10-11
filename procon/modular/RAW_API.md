# P0081 asynchronous RAW GET API v1

The application opcodes FD (submit) and FC (result identity) are not Modbus function codes. Existing FC16 holding300/count8 remains exclusively heating control. Diagnostic FC16 holding600/count8 accepts only magic81d1/API1/FD and never arbitrary CN105 bytes.

Request words at600: magic0x81d1, version1, opcode0xFD, nonzero request_id, kind1 DIRECT or2 SERVICE_A3, code (8 or16bit), reserved0, reserved0. Modbus CRC16 covers the entire atomic envelope. No optional parameters are supported. FC16 acknowledgement means accepted, not answered. Latest identical request is idempotent; changed same-ID and stale sequence get exception3; concurrent request/control gets6; unavailable link gets4. Sequence advances modulo65536, skipping0, within signed16-bit forward distance. IDs do not survive reboot.

FC04 input600..631, max16 words per read:

|Offset|Meaning|
|---|---|
|600..602|magic81d1, API1, logicalFC|
|603..605|request_id, kind, code|
|606|0 IDLE,1 QUEUED,2 BUSY,3 DONE,4 TIMEOUT,5 UNSUPPORTED,6 BAD_RESPONSE,7 ERROR|
|607|raw CN105 frame length0..22|
|608|error:0 none,1 excluded A3,2 malformed/wrong response,3 retry exhausted/no response,4 disconnect,5 total expiry; service terminal status is retained here for UNSUPPORTED|
|609|valid only when DONE|
|610|generation; changes at submit/dispatch/raw-response/terminal transitions|
|611|seconds since accepted request while pending, since completion when terminal|
|612..615|attempt count, malformed/wrong frame seen, raw payload length, expiry30s|
|616..626|22 raw frame bytes, two little-endian bytes per register (Modbus words themselves big endian)|
|627|generation echo; compare with610 and reread610 after both blocks|
|628|pending flag|
|629..631|reserved0|

Terminal result is sticky until next accepted request. Submitting clears prior raw bytes and validity. CRC-invalid complete frame is retained but invalid; no response has zero length. An incomplete A3 pending frame may be retained on timeout but is never valid. Unknown/no-response is not proof of unsupported. No explicit cancel write: stop submitting and accepted request expires at30s including queue time. Immediate response timeout800ms, A3 max10 attempts with1s start spacing. Normal telemetry and background A3 are excluded during the whole diagnostic A3 operation, then resumed. No dynamic allocation. One request slot only.

Literal workflow: FD A3 001B sends an addressed FC16 request; FC04 polls return QUEUED/BUSY, then DONE with A3 00 1B status/raw. DIRECT07/A1/A2 use the same mechanism with kind1. DIRECTA3 means a zero-filled standard GET A3, including service-number bytes zero; it is distinct from kind2's validated/retried service request.

## Actual RTU examples (slave1)

- ID1, kind2, code27: `01 10 02 58 00 08 10 81 d1 00 01 00 fd 00 01 00 02 00 1b 00 00 00 00 d6 2a`
- ID2, kind1, code7: `01 10 02 58 00 08 10 81 d1 00 01 00 fd 00 02 00 01 00 07 00 00 00 00 20 18`
- ID3, kind1, code161: `01 10 02 58 00 08 10 81 d1 00 01 00 fd 00 03 00 01 00 a1 00 00 00 00 25 91`
- ID4, kind1, code162: `01 10 02 58 00 08 10 81 d1 00 01 00 fd 00 04 00 01 00 a2 00 00 00 00 47 a1`
- Poll header: `01 04 02 58 00 10 71 ad`
- Poll raw: `01 04 02 68 00 10 71 a2`

Shelly RPC: `MbRtuClient.WriteHoldingRegisters` with `{"id":100,"sid":1,"addr":600,"values":[33233,1,253,1,2,27,0,0]}`; poll `MbRtuClient.ReadInputRegisters` at600/count16 and616/count16. The official API is documented at https://shelly-api-docs.shelly.cloud/gen2/ComponentsAndServices/MbRtuClient/ . Native client mode and baud9600/8N1 must already be configured; mapper never changes serial configuration.

## Use

`python3 tools/raw_mapper.py --scope direct` prints the dry-run plan without network access. For hardware add `--execute --host HOST --sid SID --uid UID96 --scheduler-paused --out PRIVATE_PATH`; baseline is default. Extended scopes direct/a3 always validate the baseline first. Two separated passes, default2s inter-operation delay, default1800s total cap, maximum7200s. Create STOP-MAPPING (or selected --stop-file) to stop; no more submits occur. Pending request expires within30s. Resume uses existing JSONL and rejects another identity. Log paths must remain private; do not publish device identity/customer raw logs.

OCH722A pp30–32 identifies a noncontiguous service display list. Hazardous200/340/342/343/344 and all unlisted A3 codes are excluded in host and firmware. F1p commit7687d11e8f4ec23de13f2c95bcdf76ebe9daebb5 WriteServiceCodeCMD confirms high/low16-bit A3 encoding. Historical physical27/28 evidence supports exclusive retries. Manual labels remain hypotheses for other codes until correlated. Missing optional sensors are not zero.

The portable `tools/service_codes.json` catalog covers all 104 allowed service codes, including manual display units, page provenance and whether a value describes a past fault. These are display metadata, not confirmed CN105 scaling. In particular, code122 retains the manual's ambiguous fan-at-fault wording rather than silently relabeling it as live brine speed. JSONL/CSV include metadata separately from raw replies. `requests.jsonl` journals submit intent before RPC; a terminal reply is retained even if the next health check aborts the run.

Interpret API status `UNSUPPORTED` carefully: for an allowed A3 request with a captured reply, it means the firmware saw a nonzero service status other than the established 1/2. It does **not** establish that the service code is absent from the heat pump. The raw frame and service-status byte remain available; the unrecognized format requires further interpretation. Excluded host/firmware codes also use this API state but produce no physical service request.

CN105 provides no request sequence on wire. Ownership, command echo, bounded windows and1s post-request quarantine prevent ordinary stale cross-command results; an arbitrarily late identical-code reply cannot be distinguished mathematically from a new one. Mapper compares explicit Modbus request IDs and never reuses stale snapshots. Lengths above the established16-byte payload limit are rejected, not silently interpreted. Health monitoring covers link/freshness/control/parser/UART and known primary-pump warning candidates; it is not a complete vendor-fault decoder.

The full application retains its normal CN105 connect handshake and preexisting operator control API. The mapping path emits only GET0x42 and vetted A3 requests; it does not exercise SET0x41, vendor update commands or existing control registers.
