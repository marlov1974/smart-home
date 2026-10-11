# FTC6 offline analysis — P0082

An S-record termination address is not necessarily the reset vector. Preserve sparse addresses and compare imported address-byte hashes. Test processor modules with documented instructions before trusting their call graphs; a plausible mnemonic can still have incorrect flow metadata. Distinguish decimal service selectors from direct GET bytes. Status 3 may be a structured format, not unsupported functionality. Match firmware identity/version before transferring any address or semantic claim. Full vendor images and disassembly stay local.

## P0083 lessons

Direct branch metadata and instruction p-code need separate tests. Synthetic rotate emulation must check carry/sign/zero as well as result. Far-pointer arguments in decompiled C can collapse into misleading RAM addresses; inspect stack operands. Table-seeded function discovery is safer than treating arbitrary byte offsets as entry points.

A service query may change accounting state: FTC image candidate 20.01 selector 532 snapshots and clears energy banks, and 340 mutates initialization state. Exclude these from read-only probing. Even normal counter queries can fold pending accounting into RAM.

A dated energy snapshot is not a live/current-day counter. Trace source banks, rollover trigger and timebase before assigning that label. Session-gated FF readbacks do not mean numeric zero or unsupported hardware. PWM readback alone does not prove actual hydraulic flow or direction. These findings must be revalidated across firmware revisions.

## P0084 lessons

A shared diagnostic-ring writer can resemble a transport wrapper: distinguish RX/TX logging from the actual peripheral path. FTC's 9D8FE records both directions; UART2 uses separate receive/transmit buffers and interrupt handlers. Use vector entries including the prologue, not a plausible ENTER in the middle of an ISR.

Shared internal setters do not imply transport parity. Preserve session/category gates, arbitration, direct-A3 restrictions and separate display-local behavior. Setting bytes staged by a CN105 command are not a complete safe write transaction, especially when neighboring fields are copied too. Similar response latency cannot identify a physical connector. Check indirect switch bounds from actual operands, and replay from a clean project after exploratory corrections.

## P0085 lessons

Do not map physical ports by elimination from UART numbers. One peripheral can have multiple protocol personalities (UART1 here), and similarly named connectors can have unrelated functions across Mitsubishi product families. A diagnostic memory-read path proves code capability, not connector access or complete flash readout. Keep electrical mapping, packet validation, session eligibility and per-function reachability as separate evidence layers.

An operator wiring correction supersedes a package premise: the reported CNRF WiFi installation is now probably installer miswiring, not evidence that CNRF supports MELCloud/CN105. Preserve the corrected provenance explicitly. Exact reset INTB and vector prologues resolved the D timer roots; mid-ISR exploratory seeds must not enter the final project.

## P0086 lessons

Inspect the final response packer as well as its numeric helper. The 20.01 odd energy helper computes four digits, but the service handler zeros two before transmission. Pair resolution is ten raw units. Forced reads divide pending accounting and discard remainders in calculation mode 1; repeating the high half can bias accounting. “Read intent” does not mean an operation is observationally neutral.

A wide parser address and a 32-bit intermediate do not prove a far memory access. At9E99C, MOV.b [A0] uses only16 bits despite the upstream ADD/ADC. Check actual load bytes against the architecture manual and emulator before trying flash addresses; an apparent flash read may alias MMIO.

A firmware log may be destructive and incomplete: this diagnostic reader drains its ring, flags loss without a count and omits the original CN105 checksum. Preserve raw fragments and unknown timestamps; do not retry drains or synthesize missing bytes as observed evidence. Session GET callbacks can also advance state. Keep an observer model distinct from a qualified wire transaction.

## P0087 lessons

Trace both target preparation and outgoing serialization. A temperature-error lookup can produce synthetic temperature feedback rather thanHz: here larger deficit lowers29..24C table output, while a separate path packs actual target/feedback. A memoryless local lookup does not prove a memoryless whole machine. Identify active profile and receiver before deducing a gain or adding an outer integrator.

Accepted fixed target38DE, effective heating3908 and fallback390C are different. Timer high-bit enable and low15 count semantics do not establish seconds. Preserve mode/age/generation confounders in historical replay; an old target command that transitions through curve mode cannot isolate fixed-flow stop behavior. P87 is a partial20.01 reconstruction, not installed21.00 address qualification.

## P87 continuation: original-ROM execution and two language defects

Do not treat decompiled C as authoritative even when all functions decode. The current pinned M16C module has an incorrect EXITD return composition/SP update, and `bit,base:8[FB]` incorrectly zero-extends the five-bit byte displacement. The latter makes local flag writes atFB-1 appear atFB+31 and can erase real conditions from decompiled C (C77B6 is a concrete example). Official M16C60 EXITD semantics and addressing table1.7.1 qualify the corrections. P87RoutineProof.java applies explicit emulator-only shims; the shared module has not been changed. Existing affected decompilations require review/re-extraction before reuse.

A zero Ghidra process exit code does not establish script success. Require completion markers, no script errors/uninitialized reads, expected full observation count, and independent reconstruction comparison. Do not put all of/tmp on the Ghidra script path: a dedicated script directory avoided a prolonged script-loader stall and shared-cache blockage. These lessons were promoted from the P87 continuation; see its continuation.md and rom-proof.json.

## P0088 command-atlas lessons

Count structural descriptors, interpreted semantic fields and physically verified connector mappings separately. A generated row per unknown byte is useful inventory, not a completed feature analysis. Room-report aggregation and settings-file transfers can identify likely CNRF/storage roles without proving wiring. Keep CN105, CNIT, CN22 and CN3C assignments qualified independently of software-path names.

For FTC20.01 forwarded A3 class1, the same selector normally polls a cached job/result rather than resubmitting it. Pending format0 replies must not be equated with lost transport. The completion consumer accepts class1 results without comparing the pending selector, so retain the client's selector check. Another command can clear request ownership and cancel the native service queue. Quiet waits and interleaved normal polling are not equivalent. A recently received cached value is not necessarily a new measurement; rearming remains a separate requirement. Local class2 has different execution and side-effect semantics.

A decompiler may follow instructions outside the saved function body: CECFA's saved body ended before ROT.w although its C output continued. Use a bounded CFG walk with image/operand validation, fail on undecodable or escaping flow, and repeat in an independent project. A contiguous Ghidra memory read may stop at MOT gaps; verify the hash of the explicitly FF-filled reconstruction and compare every project byte used by the bounded analysis.

Outgoing source descriptors prove quantization and packing, not which profile is active on a specific installed heat pump. The selected-target packet uses half-degree target/feedback fields and nonlinear flow feedback; establish mode/profile ownership before transferring those formulas into a whole-machine model.

P88 settings continuation: session acceptance, active application and persistence are separate milestones. C8 action1 can raise a one-pass import event consumed before peer completion; resetting the session state does not undo imported settings in the reviewed reset routine. Always inspect main-loop order and all consumers of transient event flags. Numeric selector ranges can alias shared staging and still omit fields staged through another transport; a finite-table gap is not global unreachability. Direction050B.bit5 matches4980 (not complemented), established from TST/STZX and tested explicitly.
