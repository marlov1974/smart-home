# P0089 – nya styr- och läskontrakt

**PARTIAL, FTC20.01; fysisk verifiering NOT RUN.** Tidigare P88-fynd räknas inte som nya. Varje rad anger den nya slutna länken och vad som återstår.

|Kod / fält|Funktion|Nytt samband|Återläsning|Kvar|
|---|---|---|---|---|
|41/34 p5|Varmvattenspärr|Fjärrmasken väljs endast vid accepterat ägande; lokal39A5 väljs vid owner0|GET28 p5 plus p10 ownership|All downstream physical actuator conditions and installed21.00 behavior remain|
|41/34 p6|Värmespärr zon1|Fjärrmasken väljs endast vid accepterat ägande; lokal39A5 väljs vid owner0|GET28 p6 plus p10 ownership|All downstream physical actuator conditions and installed21.00 behavior remain|
|41/34 p7|Kylspärr zon1|Fjärrmasken väljs endast vid accepterat ägande; lokal39A5 väljs vid owner0|GET28 p7 plus p10 ownership|All downstream physical actuator conditions and installed21.00 behavior remain|
|41/34 p8|Värmespärr zon2|Fjärrmasken väljs endast vid accepterat ägande; lokal39A5 väljs vid owner0|GET28 p8 plus p10 ownership|All downstream physical actuator conditions and installed21.00 behavior remain|
|41/34 p9|Kylspärr zon2|Fjärrmasken väljs endast vid accepterat ägande; lokal39A5 väljs vid owner0|GET28 p9 plus p10 ownership|All downstream physical actuator conditions and installed21.00 behavior remain|
|41/34 p10|Begär/släpp fjärrstyrningsägande|Acquire only if38BF not2/3,39EA!=1,39ED==0; release also via4978; events cleared each pass|GET28 p10; then p5..9 selected inhibits|Peer owner release and controller profile must be observed; timers not seconds|
|41/34 p11|Räknare som kan återkalla fjärrägande|Ten increments from zero inhibit/release owner; byte wraps at256, zero resets|GET28 p11 echoes39EC, NOT counter33EA; p10 shows ownership|Timer timebase and hidden counter not directly read; CE920 is inheritedP88 proof|
|41/34 p12|Rått hjälptillstånd till D-publicering|Shared flag copied to D outgoing staging and compared for updates; physical meaning not closed|GET28 p12|No proved user label; no control planner|
|41/34 p13|Övre gräns för en intern, diskret styrstorhet|Can lower selected internal value but cannot raise above native/peer limits; overrides force active3933=100|GET05 p5 encodes floor(05FE/10) via8929D; not stored3E06|Physical units/source-board response unresolved; NOT kW,Hz or percentage command|
|42/05 p5|Återläs vald intern gränsnivå|Distinguishes selected aggregate from stored SET34 request; some quantization|Compare expected encoded selected state; cannot reconstruct individual limiting owner|No production decoder added; full GET05 remaining bytes inherited/unqualified|
|41/35 p4,5|Rumsmål zon1|Routes raw room target to heating/cooling store, not fixed-flow target|GET26 target selection or room-target getter requires matching selected native mode; physical effectiveness separate|Full target safety range and selected readback binding not completed|
|41/35 p6,7|Rumsmål zon2|Routes raw room target to heating/cooling store, not fixed-flow target|GET26 target selection or room-target getter requires matching selected native mode; physical effectiveness separate|Full target safety range and selected readback binding not completed|
|41/32 p6,7|Zonlägen kan kopplas ihop av kompatibilitetstabell|Setting one requested mode may also adjust zone2 requested mode; target-onlymodecontext remains required|GET26 p6/7 are selected3916/3918, not raw3913/3914|Need installed profile and complete selected-mode path; table bytes pinned|
|42/0b p11|Temperaturkodning med avrundning mot noll och klamp|Signed subtraction and signed division truncate toward zero, then clamp0..255|Raw companion/source validity remains independent|Rounding helper closed; invalid/freshness and physical sensor identity remain|

SET32 p4 och SET33 är uttryckligen kvar som ofullständiga. Ingen hel fysisk transaktion markeras klar. Se cn105-contracts.json för aktiveringsbitar, kodning, modellstatus och bevisadresser.
