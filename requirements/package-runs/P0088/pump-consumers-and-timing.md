# P0088 — pump consumers, persistence timing and status output

Static FTC20.01 only; no hardware calls. This extends the named [firmware model](firmware-model.md). All addresses belong to the SHA-pinned reference image, not installed firmware21.00.

## Pump-level selection now reaches an output

`AF400` produces active command byte3A33:

```text
select_primary_pump_level(demand):
    if demand == 2: level = 3
    elif demand != 1: level = 0
    elif operating_state3CB7 in {9,10} and3D07 != 2 and3A02 != 2:
        level = DHW_setting0770
    else:
        level = heating_setting07E6
    if demand == 1 and profile3AD2 == 2:
        if reduction49C7 in2..7:
            level = max(2, level - (reduction49C7 - 2))
    return level
```

Thus the stored heating-pump level is not always the final output level. Demand2 selects fixed3, and profile2 can reduce the selected level with a floor of2. Even selected1 becomes2 when that reduction branch is active. The49C7 callback/state chain is now traced in [reduction and energy](reduction-and-energy-chain.md); generic dispatch eligibility and the full demand scheduler remain open; do not call it a user percentage or compressor limit.

`B1A90` gates the output using3A32: zero calls B1B8A, nonzero calls B1AF0. B1AF0 maps level1/2/3/4 to intermediate52/41/31/20; other values map to0. It derives a16-bit timer value, stores3A36 and calls B1B9C. B1B9C configures Timer A2 through0338 and0320.bit2 and writes032A. Therefore we have reached a timer-backed actuator path. Actual duty polarity, physical connector and RPM calibration remain unresolved; the intermediate values are not asserted as RPM or duty percentages. The C representation of the multiword arithmetic is insufficient to qualify its physical transfer function.

## A separate accounting contribution

`CE2A4` uses the same level3A33 to return a bounded contribution consumed by CD5AA, which sums it with eight other contributions into a32-bit accumulator array at318E. If configured07D3 !=9999, use that raw configured value. Otherwise select a row at87F9A by38BD>21 and index by level0..5; other levels return0.

|Raw level|Row38BD<=21|Row38BD>21|
|---|---:|---:|
|0|0|0|
|1|29|38|
|2|41|68|
|3|56|105|
|4|63|153|
|5|63|180|

Cap the result at200; return0 if3A34==0. This is a configured/table-derived contribution, not a direct measured electrical value. Its engineering unit and final energy-report destination still require downstream qualification. Avoid using it as an independently measured pump wattage or calibrated COP input.

## Persistence delay is tied to Timer B2

Vector entryFFD70 points to94324. Profile3 dispatches9438E, profiles5/6 dispatch943DC, other nonzero profiles dispatch94416; these call94A46 once per interrupt. Profile0 dispatches9435C, which does not call that incrementer. The normal profile2 path therefore increments3CED each Timer B2 interrupt, capped at6. This resolves the caller of the previously isolated delay helper.

`9449A` sets TB2MR=40 hex and TB2 reload9999. M16C/65 hardware manual, Timer B count-source table (printedp335), makes this f8TIMAB. Given fTIMAB=32MHz, the nominal interrupt is2.5ms and six ticks are15ms. Oscillator/clock-route qualification remains open, so15ms is conditional. After a write reset, readiness occurs on the sixth subsequent interrupt; phase can shorten elapsed time by up to one tick, and main-loop scheduling can delay actual verification. It is not an exact wall-clock sleep.

## Corrected fault propagation and output

**Correction to the prior checkpoint:**984D9 is `BMNE/NZ 3ACF[A0]` with A0=1. Architecture-correct indexed-bit addressing targets **3ACF.bit1**, not075A.bit3. The latter was a known Ghidra addressing defect leaking into the report. The existing manual-qualified `bit_address` model now includes this explicit regression. No mutation of setting075A is established by this instruction.

Both89D6A and984D2 therefore feed the same status bit. B7954 can overwrite that bit based on3ECF==3, so it is not an immutable storage-fault latch. The originating08DA.bit2 and the indication request are separate state.

`9850E` consumes3ACF.bit0 as a new indication request, snapshots bit1 into3CF7, and loads transition count3AD0 and interval3AD1. It advances a toggled state3CF5, finally using3CF7 as the resting state. State1 clears P9.5 (03F1.bit5); state0 sets it. This closes a software path to an active-low GPIO indication, likely an LED, but physical component identity and a screen fault code remain unproved. Bit1 changes alone do not immediately change the latched indication: a request event is needed to snapshot them.

## Remaining precise edges

1. Qualify the oscillator route before converting timer counts into unconditional milliseconds.
2. Trace49C7's producer and3A32/3A34 demand/enable ownership.
3. Recover the Timer A2 arithmetic and electrical polarity before describing physical pump response.
4. Follow CD5AA's aggregate into dated consumption reports and establish units.
5. Attribute P9.5 on the actual board and distinguish local indication from screen alarm reporting.

The regulation model now has a concrete auxiliary-load/actuator dependency. It does not yet reconstruct the full compressor control law.
