# Source-link outgoing catalog

The bounded region 82A7A..8320C contains 37 terminated packet descriptors and 249 bit fields. All 37 have direct, qualified far-descriptor call sites to 9C228 in 9B9A8, 9BC40's switch, or their helpers. `source-tx-descriptors.json` records every field and call site; the main atlas includes every bit field. A template is not an externally callable command and does not establish its peer-side effect.

## Packing and transport

9C228 reads six-byte records: one-based destination bit, kind/width, four-byte source. Kind 0 supplies a constant, 1 reads one byte, 2 calls a function with profile 10 hex. It masks the value to the declared width and ORs it into the logical frame, least-significant bit first. FF terminates the field list. Header byte 2 selects length, checksum and symbol conversion. 9C34A checksum kind 1 makes sum zero; kind 2 makes sum FF; kind 0 does not append a checksum.

Most descriptors use header 66: six logical bytes, checksum kind 1, symbol conversion. 82CEA uses header 04 (four bytes, no checksum/conversion); 82F24 uses 21 (one byte, symbol conversion, no checksum). These exceptions must not be forced into the six-byte service-result decoder.

The logical bytes are expanded into words at 1318 before staging at 084B. 9C39E inserts the bit-level framing/parity and final-symbol marker. P88's offline packer intentionally stops at logical bytes; it does not claim a UART configuration or emulate line timing. 9D08C copies the selected number of words to 08C6 and records length at 08D2.

9D598 starts a request only when 0849=0 and 0857=0. It distinguishes direct request 0839=1 from queued-mask request 0839=2. Queued bits move to in-flight 083E/0840, then either return to pending on states 4/5 or move to acknowledged 0842/0844 on state 3. Thus packing alone is not completion. Service retry state 0866/0867 can reach a failure indication; no universal retry duration or idempotence follows from this scheduler.

## Qualified selection

All selector numbers in this section are hexadecimal internal IDs, not CN105 opcodes.

| Internal selection | Descriptor/helper | Proven distinction |
|---|---|---|
| Direct 18 | 82CEA | Four-byte repeated word from 99A0E |
| Direct 19 | 82D0E | Type 0D and local configuration fields |
| Direct 1A | 9C002 | Five templates 82D32/82D6E/82DAA/82DE0/82E28 selected by 0863 bits3–4 and profile flags |
| Direct 1B or 25 | 9BF0E or 9C0EE | 3AD2=4 selects the latter; other profiles use 82E94 |
| Direct 1C | 82A7A | Staged configuration/status, with 3D29=1 |
| Direct 1D/1E/1F | 82AF2/82B34/82B70 | Related variants with 3D29=1 |
| Direct 21 | 82BE2 | Type05 variant2, selected encoded temperature |
| Direct 22 | 82C2A | Type05 variant1, explicit target/feedback/return/flow |
| Direct 23 | 82C60 | Type05 variant3 |
| Direct 24 | 82F24 | Single-byte type from pending-mask state |
| Other direct | 82B94 | Type05 variant0, native state and virtual temperatures |
| Queue IDs01..17 | 23-entry switch at9BC57 | Default index11; aliases retained in atlas. IDs0D/0E share9BFD8/82ED0; ID10 selects82EEE service request |

9C0EE selects fifteen templates 82F3C..831DC based on 3404/3405. These convey staged bytes rather than a newly proven public update mechanism; their semantic ownership remains open. Other queue-only templates are 82C7E/82CB4/82E76. No descriptor in the bounded region is silently omitted.

## Explicit temperature/flow request: 82C2A

| Logical byte/bit | Source | Encoding / meaning |
|---|---|---|
| 0 bits0–4 | constant05 | Family |
| 0 bits5–7 | 39A7 | Three-bit peer/address field; physical addressing not qualified |
| 1 | 9A336,39EF | Selected target: signed input clamped0..8000 then `(value+49)//50` |
| 2 bits0–5 | 9A36A,39F3 | Return temperature: signed input clamped0..6000 then `(value+99)//100` |
| 2 bits6–7 | constant1 | Variant |
| 3 | 9A39E,39F1 | Selected feedback: same clamp/rounding as target |
| 4 | 9A3D2,39F5 | Feature-gated nonlinear flow encoding, below |
| 5 | 9C34A | Additive checksum |

BA962 supplies 39EF/39F1 from the current thermal mode. Mode1 selects DHW target3906 and tank0668; mode6 selects390E and tank0668; mode2 uses A2C6A/A2BE0; mode3 uses A2CEC/A2C9A; default uses390C and flow0662. It always supplies return0664→39F3 and primary flow322E→39F5. Consequently feedback is not always the same sensor.

9A3D2 returns zero if 06D5 bit7 is clear. Otherwise let `x=min(unsigned39F5//10,1000)`: for x<301 output `(x+1)//2+1`; for 301..600 output `(x+4)//5+91`; for x>600 output `(x+9)//10+151`. This is a nonlinear wire encoding, not a linear one-byte l/min field.

The half-degree target/feedback step is proven here; exact receipt/application and response on the connected Geodan remain untested. It does not establish that this is its active profile.

## Ordinary demand request: 82B94

Family05 variant0 combines 39C3 (native state), flag bits39DD/39CD/39C5/39C6, a six-bit virtual demand from997C6, an encoded secondary temperature from99846, and staged3D2A. For profile10,997C6 uses `(clamp(signed39C7,800,3950)-800)//50`;99846 uses `(clamp(signed39C9,-3900,8850)+3900)//50`. 3D2A is selected from998C6(39CE) or99906(39FC), both offset/clamped half-degree encoders.

Selection of 998C6 versus99906 depends on 0915, received capability05D3 bit2 and mode39EE/38C3. This corrects any assumption of one unconditional wire representation. No field in these two templates has been proven to be a direct compressor-Hz target.

Remaining semantics: name every staged configuration field, resolve the active Geodan personality and peer acknowledgment/limits, finish all source RX families and downstream consumers. The source MCU's internal control algorithm is absent from this FTC image.
