# Source/underboard receive path

The user's brine-underboard suggestion now has a concrete static receive chain. This is FTC 20.01 evidence; the physical connector and source-board firmware remain unverified.

| Stage | Evidence | Result |
|---|---|---|
| GPIO sample | 9C498 reads bit 3 of 03F1 | M16C65 P9.3, not P87's P6.3 label |
| Bit assembly | 9C5F0 uses sampled 3D3D; 9C644 shifts 1328 and inserts bit 10 | Interpret indexed bit operations using the manual, not the defective decompiler expression |
| Byte reception | 9C68D stores `(1328 >> 1) & FF` at `08D3 + 3D41` | A distinct software-serial receive buffer |
| Length | 9C696–9C6CD selects from first byte's low five bits | Type 03: one byte; type 08: three bytes; all others: six bytes |
| Checksum | 9C77C sums the selected bytes modulo 256 | Sum zero accepted; type 03 bypasses checksum. 9C7BE sets 08C4 bit 4; failure uses 9C7DE |
| Dispatch | 9CBF6 uses 8328E translation and bounded 16-way switch at 9CD67 | Low-five-bit type 1D maps to normalized 0A, switch index 9 |
| Service staging | 9CEFB calls 9CF66 with bank 1, length 5, type 0E/0F, ready 1 | Copies 08D3..08D7 to 085E..0862 only while 0857 is zero. Previous normalized type 0B selects 0E, otherwise 0F |
| Main-loop handoff | A04C4 accepts 0857=1 with 08F7=0 | Types 0E/0F set 389A bit 1 and copy bank 1 to 38A0..38A4; marks 0857=2 |
| Service consumer | 8BDE0 checks 389A bit 1 | `LE16(38A1)&03FF` is selector; upper three bits are format; 38A3/38A4 carry raw value |

For that six-byte service-result family, the raw layout is therefore:

| Byte | Meaning |
|---|---|
| 0 | Low five bits 1D; upper bits not fully qualified |
| 1–2 | Little-endian word: selector bits 0–9, format bits 13–15; bits 10–12 unresolved |
| 3–4 | Two raw result bytes; interpretation depends on format and service |
| 5 | Checksum making the complete six-byte sum zero modulo 256 |

This does not make every checksum-valid packet acceptable: transport state, transaction history, personality and pending-buffer gates still apply. No synthetic test below claims to emulate those gates or establish brine units.

P83 already classified decimal services 17/18/19/27/28/52/54 as forwarded class 1, rather than local sensor implementations. This new chain binds the externally supplied service buffer to the separate software receiver. It strengthens a control-board link interpretation; it does not prove which board measures each sensor or reveal the peer's compressor control law.

The outbound direction is independently present: 9C40E profile 10 stages the packed request at 084B; 9D08C copies it to 08C6 and the timer-driven serializer writes P9.4 through 9CA40. Complete outbound schemas and active-profile ownership remain open.

OCH722A printed page 63 explicitly identifies CN3C as transmission between FTC and C.B. That makes CN3C the leading physical candidate. The manual's 0–24 VDC label is not a TTL-level specification. No continuity measurement, passive capture or live transaction was performed.

Seven source functions and all sixteen switch branches were byte-identical across two fresh projects; see source-extraction.json. The byte receiver and checksum routine were separately exported from fresh-a. Exploratory source-isr output containing the invalid interior root 9CB0A is excluded.
