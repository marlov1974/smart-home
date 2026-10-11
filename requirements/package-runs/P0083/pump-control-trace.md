# P0083 track B — water-pump levels

**PARTIAL.** Separate stored steps, operating-mode selection, PWM conversion/output and GET15 readback are established in [the supplied20.01 image](provenance.md). Complete validation/persistence and a usable CN105 write transaction are not established. No settings were changed.

## CONFIRMED code/data chain

1. C943E indexes38 descriptors at87A60 with stride21 and copies the chosen record into4930. Callback4939 executes C96E6; filename index4934 selects a64-byte name from87620. C96E6 then invokes493D (descriptor+13). The file-name table alone is not evidence of a controllable pump parameter.
2. Descriptor31 at87CEB names `6_SER1.DAT` and selects serializerC9958; descriptor32 at87D00 names `6_SER2.DAT` and selectsCA1D2. C9958 atC9B94 reads byte**0770**, callsCA488 with record offset7F. CA1D2 atCA2C7 reads byte**07E6**, record offset1B4. CA488 writes a marker/value triple into transport buffer469C; actual value offsets are81 and1B6. These are buffer offsets including headers, **not proven on-disk offsets**.
3. Settings-import paths BCB0A/BCC75 and BCFF4/BD085 copy staging274F→0770 and2A84→07E6. Alternative settings staging uses BD296/BD401:197B→0770 and BD780/BD811:1CB0→07E6. BC9DA and BD166 gate the bulk imports. Other persistence paths read/write the same RAM bytes at96338/9675D,97665/97939,955BB/957EE; persistence device/layout is not established here.
4. **AF400** chooses0770 for operating state3CB7=9/10 (with additional3D07/3A02 conditions) and07E6 otherwise when the pump is requested. It writes selected step to**3A33**. The 9/10 branch is the DHW branch, strongly corroborated by energy attribution and the manual; the other is heating/cooling. A special command2 requests step3; off requests0.
5. AECA4/AEE84→AEC0A use pump-type callbacks from table859C0 via24B4/24BC. Pump types2/3 route to **B1A90→B1AF0**. B1AF0 reads3A33: step1→52 (`34`),2→41 (`29`),3→31 (`1F`),4→20 (`14`), default→0. Valid step5 therefore produces0. **There is no exclusive check for step5 in that branch:** invalid values also fall through; this is not a safe clamping API. B1B8A stop sets100 (`64`). PWM value goes to**3A38**, timer duty to3A36.
6. **B1B9C** transfers3A36 to peripheral032A, configures0338 and enables bit2 of0320. This is a hardware timer/PWM path. OCH722A identifies CNPWM as Pump1 speed control. Mapping this exact MCU pin electrically to CNPWM remains **STRONG HYPOTHESIS**, pending exact-board pin/trace verification.
7. **GET15** packerA5BF8 callsA4334/A4344/A4350: payload1=`3A34==1` (run), payload2=low byte3A38 (commanded PWM), payload3=3E9D (feedback). It does not expose0770/07E6 directly and does not measure flow direction or RPM.

The P81 historical frames were rechecked offline: both GET15 samples contain payload1=1,payload2=0,payload3=56. This is consistent with running at step5 under the established PWM convention. It does not prove actual hydraulic flow, and does not prove both configured steps equal5. F1p's pinned decoder independently uses52/41/31/20/0 and100 for stopped. These water-pump values are unrelated to brine service18's0–10 display range; P81 brine18 raw16 remains unresolved.

## Existing CN105 paths and their limits

**CONFIRMED readback candidates:** GET65→A7D48 conditionally places0770 at payload10; GET79→A8BCC conditionally places07E6 at payload7. Both first call**CFB18** and only fill settings when its return is0. The response includes a status/gate byte at payload1. CFB18 checksCF832 and internal session state2372; it can returnFF. Physical P81 GET65/79 each returnedFF in both passes. Consequently their zero setting bytes are **not level0**. The exact session transitions needed for valid setting readback remain unverified.

**Write capability NOT ESTABLISHED end-to-end:** A504C's SET lookup84B56 plus input descriptors map SET65 to internal1A and SET79 to2E. CF67E's indirect dispatch and settings-state logic are present, and the RAM import paths above exist. But a validated link from each specific field/flag through range checks and persistence to0770/07E6 is missing. A recognized command or generic SET acknowledgement is not enough. Do not generate write packets or enable an installer session based on these constants.

Unresolved range validation1–5 belongs upstream of the output fallback. Smallest next work: recover CF67E's switch and session-state handlers, then trace the two field writes across the staging buffers. A separately authorized display-only comparison of GET15 at known pump levels can validate21.00 behavior without protocol writes.
