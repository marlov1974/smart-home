# P0072 pump protocol research

Evidence reviewed: pinned F1p CN105 implementation7687d11, especially EcodanDecoder.cpp Process0x15 and available Encode*/ECODAN setter methods; existing Geodan project manual observations and completed A3/27/28 logs. Scope is not a proof that undiscovered writes cannot exist.

|Capability|Classification|Evidence/result|
|---|---|---|
|Primary water pump run state|strong read candidate requiring hardware test|GET15 byte1, reference0/1; decoded in MVP with strict range|
|Primary water pump output level|strong read candidate requiring hardware test|GET15 byte2:64hex→0,34→1,29→2,1F→3,14→4,00→5; unexpected values invalid; reference calls it speed, no measured-RPM claim|
|Brine pump run/step|P0080 A3/019 RPM-derived running, A3/018 output step|OCH722A p30; hardware response validation ongoing; no flow-direction inference|
|Command brine pump output|unsupported/unknown|no verified encoder or response/restore behavior found in reviewed paths|
|Command primary pump output|unsupported/unknown|read status does not imply writeability; no verified setter in reviewed reference|
|Manual pump operation with compressor off|unsupported/unknown|service/manual operation existence does not prove CN105 control|

None is classified verified writable. The reference read paths do not establish that pump functions are intrinsically read-only. No pump overrides or speculative writes were sent or implemented. Do not map service-menu numbers directly to A3/Modbus without evidence. No inference of brine-pump operation from compressor Hz.

Next evidence needed: observed service display values alongside raw GET15 (for primary pump), documented or captured requests and acknowledged/effective readback for overrides, bounds and restoration semantics. Preserve Mitsubishi protections and use one experimentally verified dimension at a time. Physical tests are pending operator flash, not part of this build run.

## P0080 brine pump A3 extension (2026-10-10)
OCH722A service manual p30 identifies decimal018 output step0..10 and019 RPM0..9999. A3 support is a wire-mapping candidate pending physical observations, not a confirmed flow sensor. Schedule27,28,18,19 with a full FAST round between service operations; original retry ownership/limits retained. Snapshot schema1 remains20 fields: index11 step, index10 running derived ONLY from valid in-range RPM>0. ZeroRPM is valid stopped feedback, never inferred from missing data or step0. Controller feedback still needs physical correlation for the hydraulic test.
FC04 zero-based87..92 (018) and93..98 (019): retained raw, protocol-valid flag, age_seconds, last status, completion generation, ever-completed. Raw/protocol-valid do not perform engineering range checks; snapshot does. Age TTL60s, link-down invalidates all four services, no stale value becomes valid zero. Temperature and pump sources are asynchronous; a stopped test must require fresh repeated RPM samples and actual water-pump stop feedback. No new pump commands. Only drift/service chunks differ from installed direct-flow; BL2/layout/ABI/control unchanged.

Initial physical response: D1 A3/018 raw10 and A3/019 raw3810; D2 A3/018 raw16 and A3/019 raw3810. D2 step exceeds manual0..10; snapshot step is correctly RANGE/null while FC04 raw retains16. Do not widen limits, assume BCD, or infer speed scaling without display correlation. RPM valid is a protocol/range qualification, not independent motor measurement.
