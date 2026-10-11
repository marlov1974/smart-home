# P0084 display transport investigation

**PARTIAL. Complete display parity: NOT ESTABLISHED.** Electrical identity is confirmed by documentation. A separate bit-oriented software path and its convergence with CN105 are established in the supplied image, but the final MCU-pin-to-CN22 connection and complete display response encoding are not established.

## Identity and proof convention

Every address below is hexadecimal in the supplied FTC image, candidate20.01, SHA256 `e94f9d9369b5efb9d2af66209fb431fde6ed0a1690b9ce0960adbf5cdb53b0c3` (MOT), reconstructed binary SHA256 `d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a`. Installed FTC21.00 is a different revision. Tool/module/manual identities are inherited exactly from [P83 provenance](../P0083/provenance.md). New compact evidence is [address-evidence.json](address-evidence.json); full instruction exports remain local. CONFIRMED means a local code/data or documentary fact, not a new physical test.

## Electrical connection — CONFIRMED

Mitsubishi OCH722A printed p11 shows the main remote controller attached by two conductors to CN22; p63 specifies CN22 10.4–13.7 V DC. CN105 is a separate five-position connector for the FTC/WiFi adapter; p63 gives supply pins1–2 as11.5–13.2 V DC. Both pages were rendered and visually checked. These voltages describe the documented supply connections, not UART signal levels. Neither diagram establishes standard RS485 or a TTL-compatible CN22 input.

## CN105 bytes to actual UART — CONFIRMED in image

- ROM table at84B2C supplies lifecycle callbacks A4E24/A36DA/A3710/A3722/A3760/A4F68/A5268/A535E/A393C/A4F3C. This table anchors the formerly missing low-level code.
- A36DA configures0268=65,0269=67,026C=11,026D=04, with interrupt controls004F/0050. Renesas M16C/65 hardware register map identifies these as UART2. Exact baud needs clock qualification; do not derive it from the divider alone.
- Vector FFD40 points to **A37A8**, whose PUSHM prologue precedes the RX body A37AA. RX reads026E, checks first byte FC or02, tracks length using A3882 and checksum with A38D8; buffer190C holds the frame. A3760 atA3797 copies190C→2343 when RX complete.
- A4F68 selects the P83 FC/41 or FC/42 descriptor/parser. A535E constructs the reply in2359 and sets transmit state through A39E6. A393C atA3963 copies2359→1922, then writes the first byte to026A. Vector FFD3C→**A397C** transmits the remainder through026A and ends with REIT.
- P83's **9D8FE is not the physical transmission routine**. RX calls it with selector06 and TX with46; it packs both into a diagnostic ring13B0 via9DA08. 9D8A0 consumes that ring into a larger diagnostic record1346. Its12-byte splitting must not be mistaken for wire fragmentation. This P84 finding resolves the P83 transport caveat without editing the P83 handoff.

CN105 attribution is strongly corroborated by the exact framing and P81 physical frames. Pin routing to the connector is not independently traced on a matching board.

## Separate bit-oriented path — code CONFIRMED, CN22 attribution STRONG HYPOTHESIS

The alternative hypothesis is another Mitsubishi internal/controller link, including CN3C. Therefore the following is called **D-path**, not a fully decoded CN22 specification.

1. **9E9AE** orchestrates sampling, RX and TX. 9E9BE at9E9D1 samples bit7 of peripheral03ED (P7.7 in the M16C/65 map). 9EA6E uses an eight-phase sampling cycle and a small sample vote. This is separate from UART2.
2. 9EB74 shifts sampled bits into141E. 9EB94 assembles bytes into08BD, initializes a six-byte frame length, checks parity and final-symbol position. 9ECB4 sums the bytes: modulo256 total0 sets RX status40; totalFF sets80. These are code facts, not captured electrical frames.
3. **9ED22** transmits a word-expanded buffer08B0 via1424, checks received levels against the intended output, and controls timer registers0320/032E/033A. A bit-clock/carrier generator is present. Its electrical modulation, baud and connector cannot be certified without clock/pin/board evidence.
4. **9F04C→9F152** normalizes the incoming low nibble through832FE, with a separate reply/transaction class. It compares a625-byte transition matrix at88F65 (25×25), storing normalized opcode1430 and class1431.
5. **9F2EA** uses a25-entry relative table at9F31A. Normalized opcode14/class0 reaches9F5CC, sets internal operation0D, then calls **9F788**. The frame's first low nibble B maps to14 in832FE; this is a parser relation, not a proposed complete wire command.
6. 9F788 copies08BD..08C1→3AB2..3AB6 and sets3AB0/3AAF. **A0662**, when operation0D is pending, sets0509 bit7 and copies3AB2..3AB6→050A..050E. **8B7E2** decodes the service selector as `(word050B >>3)&3FF`, classifies it with8C04E, and reaches8B980. Local classes call the same8C0B4 as CN105; forwarded classes use0409/040B–D and asynchronous flags0866/0868.

The software chain is reproducible. Complete screen menu identifiers, return-packet packing and physical connector ownership are still UNKNOWN. Do not send the abstract field relation as a CN22 packet.

## Convergence, restrictions and latency

**CONFIRMED arbitration:** CEA8A switches service mode3237. A CN105 internal8F can select mode2, but a pending0509 bit7 selects mode1 and takes precedence even from mode2. CEAEC's modes0/1 run the D-path service handler followed by **8B794**; an A3 arriving there gets format6 and zero value. This explains a possible busy/conflict response, not a measurement of the user's display activity.

**CONFIRMED A3 restriction:** CEDD6 checks internal8F and rejects selector200 or selectors>=700. CEBEE converts the rejection to format6. D-path8B7E2 does not have that same prefilter, but class/eligibility rules remain. This proves an A3-path restriction, not that every affected function is impossible through every CN105 command. The separate settings session uses other CN105 commands.

**Shared result semantics:** local8C0B4 provides format1 (including BCD/bitfields),2 (numeric),3 (fault structure),6 (default/unavailable), and mutating acknowledgments7. Forwarded responses include4 with incompletely understood semantics. Format6 also means access/eligibility/concurrency/timeout conditions; it is not synonymous with an absent function. 8BDE0 extracts the returned format from the upper bits of38A1 and values38A3/4; P83 records the byte-level evidence.

**10–15 seconds NOT ESTABLISHED:** D-path sampling, transaction acceptance, shared forwarded service scheduling and display refresh can all contribute. 9D29E turns0866=1 into pending083A bit15, and completion0868 clears it. CED4A maps terminal0866=3 to A3 format6. Local class2 and forwarded class1 have different work paths, so similar observed delays do not establish identical transports. A matching clock/timer qualification and timestamped display-request/response observation are needed to attribute seconds. No invented fixed10s or15s timeout is reported.
