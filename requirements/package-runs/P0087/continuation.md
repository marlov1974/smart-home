# P0087 continuation — executable native state, 2026-10-11

The original P87 delivery was insufficient for the user's reconstruction goal. This continuation is a checkpoint in that work, not a claim that the full Hz regulator or all firmware has been recovered. Production firmware and both pumps were untouched.

## What is now executable

`tools/ftc6/p87/native_state.py` reconstructs timer updates, two history-dependent heating limiters, their ordered arbitration and outgoing limit encoding. `FixedFlowLimits` connects these for an explicitly bounded single-circuit fixed-flow case. `P87RoutineProof.java` executes original ROM instructions with controlled synthetic RAM, including the complete AC16C call and its callees. `compare_rom_proof.py` independently runs the Python reconstruction and compares every captured result. It rejects incomplete logs, Ghidra script errors, uninitialized reads, duplicate or missing observations and mismatches.

The 51 observations cover A1ED8 lookup edges, 9A336 encoding edges, AC79A and AC880 multi-invocation histories, A3298 normal/accelerated timer increments and overflow, AC9A8 final arbitration, 99B8A encoding, and AC16C fixed-flow histories in profiles0/1/2. This is a significant improvement over checking selected opcodes or comparing two copies of a transcription. It is not exhaustive equivalence proof and uses the20.01 candidate, not installed21.00.

## Native memory and limits

| Routine/state | Verified behavior | Important boundary |
|---|---|---|
| AC79A / 3E02 | Enter state1 on transition into3D07=2 with error<200; leaving2 starts state2; state2 contributes cap70 until timer expiry or reentry | Enabled in profiles0900=0/2, disabled in1. Physical meaning of3D07 is not yet assigned |
| AC880 / 3E05 | Enter when4927=2, error<=200 and3DA4<3944; contributes cap50; remains latched even if error rises | Enabled in profile1. Clears on timer expiry,3D07=2 or4927!=2 |
| AC16C | Start100; apply4989,70,50,30,special10/0,zone0 in that order | Last applicable predicate wins; this is not a minimum reduction |
| AC29E / AC5A0 | Room-mode-specific start constraints |3915=0, not fixed-flow3915=1; do not apply them indiscriminately to the effect controller |
| AC272 | Zone transition readiness can force0 | Depends3F6D,3D07,A1DC0/3D97; not a generic compressor pause detector |
| AC9A8 |05FE=3935=min(100,0600,3933,3934) | This separate final stage IS a minimum reduction |
|99B8A| Personality10 encodes0,10,30,50,70,100 as10,9,7,5,3,0 | Numerical limit is not yet calibrated as physical percent or Hz |

The AC16C temperature difference uses signed32 subtraction of selected signed16 target and feedback. It has no25C target floor. The separate A1ED8 lookup DOES apply that floor. Combining these into one generic temperature-error function would be wrong.

## Time base

94324 TimerB2 vector dispatches normal3AD2=2 to94416. A3204 sets the pending bit3DA9 every40 interrupts. A3216 consumes that bit, generates mask1 every consumed event, mask2 every10, mask4 every100, mask8 every600, mask10hex every3000. Missed main-loop service coalesces events: the firmware does not reconstruct elapsed wall time from the number of missed events.

A3298 walks515 timer descriptors from8426C. An enabled timer advances only when its mask matches. Normally it adds1; with06DA bit0 it adds the descriptor's accelerated step, provided this does not overflow. It does not wrap.83BCA uses RAM16D0, mask2, accelerated step60, threshold600.83BD0 uses16D2, mask2, step60, threshold180.

9449A sets TB2MR=40hex and reload9999. With f8TIMAB and assumed fTIMAB=32MHz, the interrupt is2.5ms, mask1 is100ms and mask2 is1s. Actual oscillator/clock-route qualification is still required; the model uses counts and masks rather than presenting600 counts as a proven600 physical seconds. Source references: local M16C65 manual timer-B table and clock registers; P86 clock initialization,9156E/910E4.

## Outbound contract traced further

9B9A8 selects descriptors82B94 (ordinary operation/demand) and82C2A (explicit target/feedback).9C228 packs descriptor fields into a logical six-byte frame, computes a checksum through9C34A and expands it for9C40E.9C46C is called from TimerB1 ISR942E6, samples P6 bit3 and controls UART0 registers0264/0265 bit2. This is a bit-level transport path, not the CN105 UART2 byte transmitter.

The target/feedback descriptor includes9A336(target39EF),9A39E(feedback39F1),9A36A and9A3D2. Ordinary descriptor includes997C6's virtual temperature and3D2A. Received capability05D3 bit2 affects which representation9B9A8 selects;8EFA2 derives it from389F,8F17C clears it on peer identity/profile conditions. This is not a constant we can assume for our Geodan.

Frame field selection and CPU-port trace are stronger evidence of FTC's outgoing contract. They do not yet establish physical connector ownership or reconstruct the receiving board's compressor algorithm.9B2A8 is a change detector/cache comparator, not itself proof of a transmitted request.

## Emulator qualification and failures

The installed M16C SLEIGH module's EXITD implementation combines return-address halves with AND and adjusts SP incorrectly. The first original-code run failed because of this. The harness intercepts only opcode7DF2 and applies the documented EXITD operation: SP=FB; restore two-byte FB; restore three-byte PC; SP=oldFB+5. The module, ROM file and devices are unchanged. A JSR.a trampoline exists only in emulator memory at70000. Every invocation must return to70004 with SP7000 and FB0; nested original calls exercise nonzero return high/low bytes.

This is original ROM execution with a disclosed architecture shim, not unmodified-CPU-emulator validation. Other instructions are still subject to the existing processor module's correctness. A setup typo used nonexistent FLG before execution; it was removed. An exploratory script rooted at/tmp stalled script loading and blocked a second Ghidra instance; it was stopped and rerun from a dedicated directory. No failed/incomplete run is counted as validation.

## Remaining puzzle pieces

1. Determine actual profile0900 and peer capability route for Geodan; do not transfer alternate-profile restrictions to our pump without evidence.
2. Complete descriptor-based state production:3D07 has a record at817CE, callback table82198, including98BA6/98DEA.4912 has a record at817B4 and callbacks871BA, includingC6F90/C795A. Indirect state writes explain why searches for a literal MOV to those addresses missed their producers.
3. Resolve ordinary thermostat/run permission and restart delays separately from special4911/4912 hysteresis. AC3AE is gated to4912=12/22/14/24; it is not established as the universal fixed-flow thermostat.
4. Finish outgoing physical ownership and incoming Hz/state mapping. Then identify whether the receiving control firmware is present in the supplied image; do not replace a missing algorithm with an assumed PID.
5. Connect accepted target updates, scheduler, state production and outgoing frames into an executable cycle. Only then compare a native prediction with the historical physical trajectories and adjust production EFFECT.

## Further state-producer and toolchain findings

98BA6 uses A22CE/05D8 to maintain3D09;98DEA returns that state through callback table82198. For entry05D8=2 with0695!=2 it sets3D09=2; after05D8 leaves2 it waits for0695=2 or timer836EA expiry before clearing. This is a code-backed producer chain, but its physical label is still deliberately unresolved.

C6F90 maintains4913. C79C2 maps4913=0/1/2–4 to4911=0/1/2. C795A combines4913 with selected zone26F3 to produce4912=11–14 or21–24. C72EA classifies3915/3917=0 as room mode and other modes separately. In the non-room branch C74A4 detects entry into heating phase8 (previous3D9D!=8, current3CB7=8), excludes transitions from DHW9/10, and has separate zone gates. C701C counts these events; after more than2 it selects4913=4 for non-room modes. C731C includes0753 and other enable/inhibit conditions. Therefore the4911/4912 branch is not justified as an irrelevant factory-only mode: it contains a repeated-heating-entry mechanism potentially relevant to cycling. Actual activation on Geodan remains unproven.

A second processor-language error was found while following its exit routineC77B6. The module decodes `bit,base:8[FB]` byte displacement as unsigned5; the official M16C60 addressing table1.7.1 specifiesFB-16 throughFB+15. Thus raw displacement31 means-1, not+31. C77B6 sets bit7 in its local return byte; the wrong decode made decompiled C incorrectly discard all those exit conditions and return zero. This also affects other functions using local bit flags: their existing decompiled C must not be trusted without operand review.

The harness now corrects negative bit-FB displacement for one emulated instruction by temporarily subtracting32 from FB and then restoring it. It additionally executes originalC77B6 with a nonheating input, expects return128 and checks the incorrect positive alias stayed zero. The original51 results plus these2 checks form53 observations. Neither correction modifies the shared processor module; re-decompiling affected functions with a properly patched and regression-tested module remains necessary. This discovery explains an analysis blind spot, not a missing function in Mitsubishi's firmware.
