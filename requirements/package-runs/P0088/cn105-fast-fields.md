# CN105 frequent GET field contracts — FTC20.01

Offline continuation of the port sprint. Six payload layouts are now mapped to raw sources; this is not complete physical semantics or validation on installed21.00. All offsets below are payload offsets, with opcode at0. The frame dispatcher initializes22 bytes to zero before packing and adds the checksum afterward.

## Findings that matter for consumers

- A4DC4 returns the same low16 bits it receives. It does not clamp a temperature or introduce an invalid sentinel. The packers serialize high byte first. Signedness/engineering units and validity belong to the upstream source; rawFFFF must not automatically become a valid temperature.
- GET0C exposes the established flow0662, return0664 and tank0668 words alongside separate sampled bytes. GET0B uses selected/source values, including0686; neither report proves brine identity.
- A4144 simply reads0ACE+index.944E0 initializes this array from repeated samples of the03C0 register bank;94658 updates it using thresholds/history. These bytes are NOT established validity flags. Keep them raw until the sensor/sample mapping is qualified.
- GET14 p12 is `(unsigned322E //100) &255`. Division removes the fractional part and conversion to a byte wraps above255; there is no saturation. The ordinary physical range is separate. This is not the nonlinear source-link encoding of the same internal flow quantity.
- GET26 publishes mode/target selections and GET28 publishes flags. A boost request, reported mode and actual compressor output are separate observations. A45C0 translates a selected mode and phase7 overrides its report to5.
- GET15 has equality-to1 flags, raw state bytes, a two-byte table mapping and a permuted enumeration. Nonzero is not interchangeable with1 for equality flags.

## Payloads

### GET0B — Room/selected temperature sources

|Offset|Source|Encoding|
|---|---|---|
|0|11|opcode|
|1..2|066C|BE16 raw word|
|3..4|068C|BE16 raw word|
|5..6|0646|BE16 raw word|
|7|0ACE|raw byte|
|8..9|063A|BE16 raw word|
|10|0ACF|raw byte|
|11|0686|A4D5E(min=-4000,step=50); runtime division rounding not yet qualified|
|12|0|constant after frame initialization|
|13|0|constant after frame initialization|
|14|0|constant after frame initialization|
|15|0|constant after frame initialization|

### GET0C — Primary flow/return/DHW temperatures and sampled companions

|Offset|Source|Encoding|
|---|---|---|
|0|12|opcode|
|1..2|0662 (flow)|BE16 raw word|
|3|0AD0|raw byte|
|4..5|0664 (return)|BE16 raw word|
|6|0AD1|raw byte|
|7..8|0668 (tank)|BE16 raw word|
|9|0AD3|raw byte|
|10..11|0666|BE16 direct raw bits|
|12|0AD2|raw byte|
|13|0|constant after frame initialization|
|14|0|constant after frame initialization|
|15|0|constant after frame initialization|

### GET14 — Input flags, multi-unit words and quantized primary flow

|Offset|Source|Encoding|
|---|---|---|
|0|20|opcode|
|1|06CF|1 iff source ==1, else0|
|2|06C5|1 iff source ==1, else0|
|3|06C7|1 iff source ==1, else0|
|4|06C9|1 iff source ==1, else0|
|5|06CB|1 iff source ==1, else0|
|6..7|397F (record4)|BE16 raw word|
|8..9|398B (record5)|BE16 raw word|
|10..11|3997 (record6)|BE16 raw word|
|12|322E|(unsigned16 //100) &255; truncation, not saturation|
|13|0|constant after frame initialization|
|14|0|constant after frame initialization|
|15|0|constant after frame initialization|

### GET15 — Actuator/native-state report

|Offset|Source|Encoding|
|---|---|---|
|0|21|opcode|
|1|3A34|1 iff source ==1, else0|
|2|3A38|raw byte|
|3|3E9D|raw byte|
|4|06A9|1 iff source ==1, else0|
|5|06AB|1 iff source ==1, else0|
|6|3A3B|1 iff source ==1, else0|
|7|06B3|1 iff source ==1, else0|
|8|3FAB|8703E[2*index], index=3FAB if<=5 else0|
|9|3FAB|8703F[2*index], index=3FAB if<=5 else0|
|10|06C0|raw byte|
|11|06C2|0->0,1->2,2->1,3->3,4->4,other->0|
|12|0|constant after frame initialization|
|13|0|constant after frame initialization|
|14|0|constant after frame initialization|
|15|0|constant after frame initialization|

### GET26 — Reported modes and requested target words

|Offset|Source|Encoding|
|---|---|---|
|0|38|opcode|
|1|0|constant after frame initialization|
|2|0|constant after frame initialization|
|3|38BF|0..3 retained; other->0|
|4|A29EC()|0/FF->0,1->3,2->2,3->1,4->6,other->0; phase3CB7==7 overrides to5|
|5|3912|0/1 retained; other->0|
|6|3916|0..5 retained; other->0|
|7|3918|0..5 retained; other->0|
|8..9|3906 (DHW target)|BE16 raw word|
|10..11|38E8|BE16 raw word|
|12..13|3900|BE16 raw word|
|14|082A and0630|082A.bits11..13 -> bits0..2;0630.bit1 ->bit4|
|15|0|constant after frame initialization|

### GET28 — Boost, holiday and flag report

|Offset|Source|Encoding|
|---|---|---|
|0|40|opcode|
|1|0|constant after frame initialization|
|2|0|constant after frame initialization|
|3|3919 (boost)|1 iff source ==1, else0|
|4|391B (holiday)|1 iff source ==1, else0|
|5|399A|Boolean bit0|
|6|399A|Boolean bit1|
|7|399A|Boolean bit2|
|8|399A|Boolean bit3|
|9|399A|Boolean bit4|
|10|39A3|raw byte|
|11|39EC|raw byte|
|12|39A4|raw byte|
|13|0|constant after frame initialization|
|14|0|constant after frame initialization|
|15|0|constant after frame initialization|

## Remaining bounded questions

1. GET0B p11 usesA4D5E with minimum-4000 and step50, followed by a0..255 clamp. Its call ABI is poorly recovered in C. The signed division helperD4704 and exact negative rounding remain open; the pure model deliberately does not guess this conversion.
2. GET26 A29EC obtains a mode throughA225A and returnsFF whenA2248 is zero. Map those selectors before attaching universal names to every wire mode. Phase override is already explicit.
3. GET15 C4B32 clamps invalid3FAB>5 to index0. Table8703E rows are(0,0),(1,0),(0,1),(1,1),(0,1),(0,0). External meaning of the two output flags remains open.
4. Identify raw companion/sample sources and all remote-record sensor units; trace invalid/freshness propagation upstream. Neither packer nor a successful reply proves data freshness.
5. There are no counter-reset calls in these inspected packer/helper paths. That is not a global guarantee about every dispatcher side effect; full-command status remainsPARTIAL.

## Verification and scope

54 packer/helper assembly exports match across the two corrected M16C projects; hashes are stored inport-sprint-evidence.json. A4DC4/A4CDC/A4D00/A29EC/C4B32 were additionally inspected in the second project; earlier944E0 export and literal94658 instruction operands supply the sampled-byte provenance. These are targeted checks, not whole-firmware execution.
The table bytes are checked against the pinned image. Pure byte helpers exhaust all65,536 flow inputs and test flag and enumeration mappings. The generated port matrix validates that each of these six contracts covers exactly16 bytes without overlaps or omissions. No live device calls or production changes.
