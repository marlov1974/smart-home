# P0069 original firmware map

Addresses refer only to immutable original SHA2562ae03b0c…6564766. See analysis/original-excerpts.txt; instruction decoding inside literal pools is not executable-code evidence.

| Address | Role / links | Evidence level |
|---|---|---|
|0x0800A340|Reset, calls0x0800A330, copies .data, clears .bss, calls main0x08009824|Verified instructions|
|0x0800A330|VTOR store at0xE000ED08 =0x08008000|Verified|
|0x080097B0|Original oscillator/PLL setup called by main; PLL source3, M2,N32,P7,Q2,R2|Verified arguments; HSE frequency not physically known|
|0x080099C2|USART3 handle0x20000FF0, base0x40004800, initial baud9600|Verified stores|
|0x08009F80|HAL-style UART MSP; USART3 branch0x0800A068 configures PC10/11AF7 and IRQ39|Verified|
|0x0800A24C|USART3 IRQ delegates via0x0800FE90 to0x08010AA4 in normal mode|Verified branch chain|
|0x08009794|Logical port1 ->0x20000FF0 (RS485), port3 ->0x20000EE8 (CN105)|Verified|
|0x08010AA4|RS485 UART IRQ accesses ISR+0x1C,RDR+0x24,TDR+0x28 and callbacks in RAM object|Verified; object semantic names inferred|
|0x08010988 /0x080109F4|GPIOD2 high/low around generic TX path|Verified stores; transceiver wiring strongly inferred|
|0x08010EDC|CN105 buffering helper, NOT raw TX API|Preserved earlier correction; not used|

Updater static IL: analysis/updater-il.txt. init_serialport uses1152008N1; worker sends0x5A discovery, reads device-reported sizes;0x51 erase offset0 and BINlength;0x53 writes file offsets starting0, block CRC/checksum. No host-side BIN signature/header validation beyond nonempty and device maximum size. Device address translation remains unavailable.

P0069 r2:0x080099CC–0x080099E8 sets USART3 AdvancedInit0x38 and Swap0x8000; USART3 uses swapped AF7 pin directions. Missing this caused the first candidate to disagree with original hardware configuration.

P0070: M1 r2 now hardware-confirmed; next experimental build adds CN10524008E1 on PA9/10AF7 and read-only compressor telemetry. See `../releases/P0070-compressor-r1/README.md` and `CN105.md`. Same conservative flash/RAM/vector limits and96KiB FF envelope. Physical CN105 result pending. No setting writes or physical flash by Codex.

## P0071 brine candidate

Adds a separate read-only service27/28 state machine with exclusive CN105 transaction ownership, bounded retries and continued GET04 telemetry. Preserves P0070 registers0–15 (build marker71); adds16–67, with max16 registers per read. Raw completed payloads are retained per service; temperature candidates use reference-backed signed little-endian encoding and remain experimental. See [BRINE.md](BRINE.md) and `../releases/P0071-brine-r1/README.md`. Software tests pass; no P0071 hardware readings or physical flash yet. Previous P0070 hardware result remains valid historical evidence.

## P0072 r1 — read-only MVP candidate

Latest build P0072-mvp-r1, operator flash pending. Implements FAST04/0C/14/0B/09/15/26 then one exclusive round-robin A3 service27/28 operation, preserving retry ownership. Adds20-field version1 API (18 mapped/derived candidates; brine pump run/step unavailable), status/age/generations, raw FAST payloads and fixed-point water heat. Marker1=72,revision68=1. Legacy addresses retained;42 counts individual service operations. See [MVP_API.md](MVP_API.md) and [PUMPS.md](PUMPS.md) for evidence and limits. No controls/SET/lease implementation; all writes rejected and control capability unavailable. P0071 physical evidence remains historical, not P0072 validation. No live actions performed in build.
