# P0072 pump protocol research

Evidence reviewed: pinned F1p CN105 implementation7687d11, especially EcodanDecoder.cpp Process0x15 and available Encode*/ECODAN setter methods; existing Geodan project manual observations and completed A3/27/28 logs. Scope is not a proof that undiscovered writes cannot exist.

|Capability|Classification|Evidence/result|
|---|---|---|
|Primary water pump run state|strong read candidate requiring hardware test|GET15 byte1, reference0/1; decoded in MVP with strict range|
|Primary water pump output level|strong read candidate requiring hardware test|GET15 byte2:64hex→0,34→1,29→2,1F→3,14→4,00→5; unexpected values invalid; reference calls it speed, no measured-RPM claim|
|Brine pump run/step|unsupported/unknown CN105 mapping|manual/display awareness alone does not supply wire command/field; both API values unavailable|
|Command brine pump output|unsupported/unknown|no verified encoder or response/restore behavior found in reviewed paths|
|Command primary pump output|unsupported/unknown|read status does not imply writeability; no verified setter in reviewed reference|
|Manual pump operation with compressor off|unsupported/unknown|service/manual operation existence does not prove CN105 control|

None is classified verified writable. The reference read paths do not establish that pump functions are intrinsically read-only. No pump overrides or speculative writes were sent or implemented. Do not map service-menu numbers directly to A3/Modbus without evidence. No inference of brine-pump operation from compressor Hz.

Next evidence needed: observed service display values alongside raw GET15 (for primary pump), documented or captured requests and acknowledged/effective readback for overrides, bounds and restoration semantics. Preserve Mitsubishi protections and use one experimentally verified dimension at a time. Physical tests are pending operator flash, not part of this build run.
