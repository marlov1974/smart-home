# P0072 r1 result — partial package implementation

Built read-only MVP firmware:20 stable signed32 fields with18 mapped/derived and2 unavailable; validity/age/generation, seven raw FAST payloads, alternating exclusive27/28 scheduler, signed water heat W and read-only capture helper. Version marker72/revision1. Added API and pump/control evidence docs; updated function catalog,living docs,file index. No platform changes, no G2/Shelly runtime changes, no device writes or physical flash.

WARN accepted under operator instruction "Bygg det du kan". Controls/command acknowledgements/lease+fallback are deferred, not simulated as applied or counted as passed. Pump output control remains unknown; water pump read level is reference-backed candidate. Hardware validation0/3 pending operator flash and display comparison. New direct GET mappings not physically verified.

Verification: `make -C procon verify` (native ASan/UBSan and13ARM cases); deterministic forced rebuild; original/old-release hashes; FFtail/bounds; git diff --check. Numeric fixture20L/min,5C→6966W; negative/zero/max/stale/skew tested. File index updated for new telemetry,tests,helper,docs,evidence and immutable release artifacts.

Knowhow promotion intentionally kept within MVP_API/PUMPS and package research: no new global Shelly/runtime lesson or live debugging occurred. Key local distinction is protocol freshness versus hardware correlation and source quantization versus representation precision.

Firmware SHA256 f8823fab325018c31f093215cd72d19c6d28dd28082bcd64d83df82e88b3b4a9
