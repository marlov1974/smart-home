# P0086 — running energy qualification

Analytical **PARTIAL**: decoding and query side effect confirmed in static 20.01; units, timebase, installation compatibility and atomic acquisition unqualified. Physical **NOT RUN**. All addresses use the image/tool identity in verification.json; evidence.json pins relevant operands. Production service allowlist and firmware are unchanged.

## Pair encoding — correction to P0083

CONFIRMED: CE0D2 computes even `floor(counter/1000)` and an intermediate odd `(counter%1000)*10`. However the odd handlers at 8CA39/8CA8F/8CAE5/8CB3B/8CB91/8CBE7 zero BOTH low nibbles of the returned word and pack only digits3188/3189 into its high byte. P83 described the intermediate value, not the complete emitted result. Its earlier recommendation to reread the high half is superseded here; no historical report was rewritten.

A3 payload0=A3, payload1–2=selector BE16, payload3=format1, payload4–5=BCD word LE16. Validate every nibble. Observed odd word must have low byte zero. Decode `BCD(even)*1000 + BCD(odd)/10`. The latter is a multiple of10 raw units. Example counter1,234,567 emits words1234h and5600h, reconstructing1,234,560, not the full counter. This is numeric resolution, not meter accuracy.

| Pair | U32 RAM | Bucket label (STRONG HYPOTHESIS) |
|---|---|---|
|520/521|3156|Consumed DHW|
|522/523|315A|Consumed heating|
|524/525|315E|Consumed cooling|
|526/527|3162|Delivered DHW|
|528/529|3166|Delivered heating|
|530/531|316A|Delivered cooling|

Bucket selection 496F=9/8/11 and P83's CD4C6 trace support labels. Counter>=10,000,000 emits9999h/9900h; that also matches values near the upper display limit. Mark censored, never infer an exact increment. CE20E separately saturates U32 arithmetic. A decrease means reset/restore/wrap UNKNOWN; no automatic unsigned correction. CDF46/service532 snapshots and clears the bank; 96AF4 can restore it. No proven midnight trigger: these are not qualified “today” counters. W-minute, Wh and kWh conversion remain UNKNOWN without input/timebase calibration.

## Reads affect accounting

CONFIRMED: each consumed even selector invokes CDF02; each delivered even invokes CDF24. They call A3468 to force the accounting descriptor timer expired; A3392/CD8F6/CDDCA then fold pending sums. Calculation mode1 divides pending integers by60 and clears the pending bank, including remainders. Thus two forced folds of59 yield0+0, whereas one fold of118 yields1. The fold affects all three buckets in its consumed/delivered bank. Mode2 copies meter increments without that divide, but still mutates the pending accounting state. It is incorrect to treat frequent reads as passive observations.

No blind high-low-high retry. Candidate bounded sequence is one high, one low, one repeated low, preserving acquisition times. A changed low invalidates that attempt; an equal low still cannot exclude a carry before both low reads. The tool reports **atomic=false, consistency=unverified**, even on equal samples. Do not silently subtract “validated” counters from these observations. No retry in a tight loop, no continuous production polling enabled.

## Tool and later comparison

energy.py validates full22-byte A3 frames, selector, format, BCD and captured values, retains timestamps, correlation, mode/raw capture metadata and uncertainty. api600 emits the unchanged eight-word candidate envelope only for520–531; 532/340 and all other selectors are rejected. Existing firmware and raw_mapper allowlists still exclude these candidates; there is no submission path here. This deliberate omission avoids enabling accounting-biased polling without a sampling policy.

Later separately authorized comparison: start with522/523 and528/529; record mode1/2 and shared interval boundaries, display readings, source ages, raw frames and original configured state. Compare sparse paired increments against GET07 full BE16 payload3–4/5–6 power integrated over time, independent water heat from synchronized flow/temperature measurements, and Shelly energy where available. Track forced-fold cadence as an experimental variable; compare a control interval with no forced folds. DHW pairs follow only after heating semantics agree. GET07 counter payload11–12 is a different bounded/wrapping path, not the six running banks. Reject zero denominators and mismatched heating/DHW intervals for COP. Physical outcome NOT RUN.
