# UART6: eight room channels and restricted user controls

Static FTC20.01. New physical tests: zero. Functional room-receiver attribution is strong; CNRF wiring remains unmeasured.

BFD16 writes U6MR0298=65, U6C0029C=11, U6BRG0299=67 and enables interrupts006F/0070. The Renesas M16C/65 register map identifies UART6, not UART2. VectorFFDBC→BFF8A transmits through029A; FFDC0→BFDE4 receives029E. RX staging2574 and application3F29 are separate from TX3F3F→258A. Lifecycle86C32 contains C0408/BFD16/.../C04F2/C06F0; C0408 enables only for argument1. Main loop92482 calls C0458 with08F9. The upstream physical origin of08F9 is not closed.

FC frames use type at byte1, **04/03** at bytes2/3, payload length at4, payload at5, checksum last. BFEB8 computes payload+6, receive capacity22. BFEE6 checks sum(bytes1..last)=0. Partial-frame counter2572 is compared with39; its wall-clock unit remains unqualified. Equal UART2/UART6 divider values do not imply protocol compatibility.

C0550 searches exactly7 rows of9 bytes at8966B; row0 defaults. C0748 searches7 rows of16 at86C5A after masking reply selector bit7. Payload positions below are zero-based.

| RX / selector | Reply | Input effects and gates |
|---|---|---|
|5A / CA|7A, payload00|C0362 translates payload1:1→connected,2→disconnected; other values reject. Header required; no prior connection required. C065E modifies3F28.bit0.|
|48 /27|68|Connected; eight room bytes p1..8; status p9→39E5 and NOT(p10)→39E6.|
|49 /28|69|Connected; target p1; eight room bytes p2..9; mode p10; status p11 and NOT(p12); zone p14.|
|4A /29|6A|Connected; eight room bytes p1..8; boost p9; status p10 and NOT(p11).|
|4B /2A|6B|Connected; eight room bytes p1..8; holiday p9; status p11 and NOT(p12).|
|4C /2B|6C|Connected; status p1 and NOT(p2). No eight-channel temperature import in8F75E for this ID.|

C00D2 consumes channels0..7. FF marks invalid (0820+i=1); other bytes clamp128..208, subtract128 and multiply50 into centi-degree storage0648+2*i, clearing invalid. It does not prove radio pairing IDs: channels are indexed, and status masks are retained raw. No battery label has been proved. 8F75E resets39E5 when08F9=0.

C006C accepts target128..248 and converts `(raw-128)*50`; invalid returnsFFFF and is ignored by B9930. C0154/86BEA accepts mode0..5 unchanged; C0394/86C02 accepts zone0/1. B9930 routes modes0/1/2/5 to38DC (zone0) or38EE (zone1), and modes3/4 to38E2/38F4. These are native target fields; this is not an unrestricted compressor demand. The consumer does not write flow-target38DE. Mode names and all subsequent native constraints must be kept separate from this data movement.

B958C consumes internalID3 (4A), C0176 maps0/1 and returnsFF otherwise, then B95E0 writes3919 **without an FF guard in that setter**. Thus an invalid value must not be called safely ignored. C0A80 consumesID4 (4B), C0198 maps0/1; C0AD0 changes391B only if notFF. Both shared setters also have CN105 callers (P84), explaining overlap rather than a new all-purpose control port.

Response68..6B payload fields: p0=0; p1 translated38BF (override3 when39E8=1); p2=399B; p3 encodes clamped38EA; p4=3916; p5=3919; p6=391B; p7=399A&7; p8=0; p9=393F|(3940<<4); p10 conditional fault/status; p11=(3999==2); p12 encodes3902; p13=076F. Response6C inserts the feature bitmap from06D4/06D5 atp11, moving the final three fields to12..14. Target encoders clamp0..6000 and compute raw/50+128. Individual unlabeled state fields are not claimed as battery, identity or measured temperature.

Operand audit matters: C01B6's FB-1 bit operations are misrepresented by the current decompiler as FB+31. Its actual low-three-bit status packing is taken from instructions. Likewise connect flag C065E was checked at instruction level. The shared processor module was not modified.

Working role: eight room reports plus target/boost/holiday strongly matches a wireless room receiver. OCH722A p11 and p63 identify CNRF as the wireless-receiver connector. Contradiction/limit: no pin continuity or captured04/03 frame on CNRF; no pairing/battery semantics yet. Smallest discriminator is an unpowered exact-board continuity trace, followed by a separately authorized passive capture of one known room report.
# Further status consumer trace

39E6 is now bound to per-room control eligibility, although its radio-level meaning remains unnamed. A2BA0/A2BC0 select a mask using zone room selections393F/3940. Tables8363A/8364A map selections1..8 to bits0..7 and all other entries to zero. A set39E6 bit makes these helpers return1.

BE2CC/BE43E (heating) and BEE16/BEF6C (cooling) require that helper result to be0, selection1..8,39E3=0, receiver enable08F9=1, valid zone temperature0828/0829=0 and connection3F28.bit0=1. Failure clears the respective room-control latch and timer. Thus the inverted incoming status byte participates in room-control inhibition; it is not safe to label it battery status from appearance alone. Its exact wire meaning still needs a source or passive observation.

Heating compares room066C/068C against room target38DC/38EE and correction39FA. Cooling compares target38E2/38F4 against room066C/068C. These are separate from fixed-flow control. Raw thresholds100,0,-100 are explicit, but this package does not reinterpret the timer counts as seconds or resume P87 regulator work.
