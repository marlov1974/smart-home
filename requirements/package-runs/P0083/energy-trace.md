# P0083 track C — running versus published energy

**PARTIAL.** Actual GET07/A1/A2 sources and six running accumulators have been located. A service read path exists to the running bank, but calling that bank “current day” is not yet justified. Automatic calendar rollover, exact scheduler timebase, calibration and behavior on installed21.00 remain open. All addresses apply to [the supplied image](provenance.md).

## CONFIRMED output sources

| Output | Packer/source | Observed implementation |
|---|---|---|
| GET07 payload3–4,5–6 | A5724→A3E98→CDFD2; A3EB2→CE01E | Two **16-bit big-endian** power fields, selected by099B/099C calculation mode and bounded toFFFF. F1p reads their low bytes; retaining both bytes is the faithful static mapping. |
| GET07 payload11–12 | A5724→A4C80→RAM3152/3154 | U32 running counter multiplied by10, divided by60, then1000, saturated toFFFF and serialized BE16. |
| GETA1 payload4–12 | A8E38→A490E(index0,1,2) | Published consumed bank:3172 heating,3176 cooling,316E DHW (eachU32). |
| GETA2 payload4–12 | A8EB6→A490E(index3,4,5) | Published delivered bank:317E heating,3182 cooling,317A DHW. |
| A1/A2 payload1–3 | A48F2 | Three saved date bytes496C–496E, not a fresh RTC read. |

A490E limits each source to0x00989676, divides by10, then separates division/remainder by100. A8E38/A8EB6 serialize whole high/low and fractional byte. This matches the published reference format, but the absolute physical unit still depends on the accumulator's input/timebase. No precision claim based solely on byte formatting.

## CONFIRMED running-bank and snapshot distinction

SixU32 running values are at3156(DHW consumed),315A(heating consumed),315E(cooling consumed),3162(DHW delivered),3166(heating delivered),316A(cooling delivered). Modes496F=9/8/11 select those buckets. CD4C6 derives this mode from3CB7/3915 and related operating flags. DHW/heating/cooling labels are **STRONG HYPOTHESIS** from this relationship, manual and A1/A2 reference ordering; the addresses and bucket selection are confirmed.

CD8F6 folds consumed interval buckets into3156/315A/315E usingCE20E (saturating add); CDDCA similarly updates3162/3166/316A. Calculation mode1 divides sampled interval totals by60. Mode2 uses external-meter increments. The timer descriptors are ROM**84080/84086/8408C/84092**, not RAM4080 etc. Descriptor values include60 and3600. This supports a minute/hour aggregation hypothesis but does not independently establish the scheduler tick frequency.

**CDF46** copies all six running values into the published316E–3184 bank, zeros all six running values, and copies date38B4–38B6 into496C–496E. A proven caller is **service532 at8CC0C**. No automatic midnight caller was established. Persistence/import routine96AF4 can also restore both banks and the saved date; not every observed date must have come from a fresh rollover. Do not call532 to refresh A1/A2: it changes the measurement state.

This explains how GET07 can advance while A1/A2 and their dates remain unchanged: they do not read the same bank. P81's increasing4770→4773 and static date26/10/5 are consistent with this design. They do not prove which scheduler/display/bridge event failed to refresh the saved bank on21.00. A time-of-day/current-day attribution remains **NOT ESTABLISHED**.

## Running-energy access via service selectors

8C0B4 has selectors**520–531**. CE0D2 reads the running bank above, converts to decimal digits3186–3189, and each handler packs fourBCD digits under format1. The even selector returns `floor(counter/1000)`; the odd selector returns `(counter mod1000)*10`, with saturation display handling for values>=10,000,000. The pair must be decoded asBCD, not raw binary/signed integer. Even consumed handlers first callCDF02; delivered handlers callCDF24, folding pending interval data. These are query-side accounting updates, not strictly immutable reads.

| Pair | Running RAM | Field interpretation |
|---|---|---|
|520/521|3156|Consumed DHW candidate|
|522/523|315A|Consumed heating candidate|
|524/525|315E|Consumed cooling candidate|
|526/527|3162|Delivered DHW candidate|
|528/529|3166|Delivered heating candidate|
|530/531|316A|Delivered cooling candidate|

The class2 route in `service-trace.md` connects these local handlers to the A3 response path. **No live requests were made** and these codes were not added to the production allowlist. A consecutive pair is not atomic: if the high/low portion changes between requests, repeat the first half or compare timestamps/consistency. This is a plausible way to obtain interval energy/COP with finer resolution than whole-kW power, pending21.00 confirmation. It is not established as a calendar-day API.

## Inputs, inclusion and arithmetic

CD5AA sumsCE296 (062A), CE2A4 (primary pump), CE2FA/CE31E/CE342 (other pump/configuration terms), and CE366/CE392/CE3BE/CE3EA (heater/auxiliary terms). CE2A4 uses configured07D3; sentinel9999 selects a factory-pump table at87F9A indexed by3A33 and a variant flag. It gates on run3A34 and caps at200. The heater terms cap configuration values and gate on their output states. This is **CONFIRMED inclusion of pump and heater contributions**, not compressor-only energy. Exact identification of every auxiliary bit remains unverified; OCH722A pp26–27 corroborates the intended total-system calculation.

CD62E averages up to17 collected samples into31D2. CD69A adds it to the mode bucket and running3152. CD744 divides that average by1000 for power3216. CD7DC uses meter events when mode2 is selected. CE24E implements a wrapping accumulator: CD69A supplies limit0x17700000 and a wrap flag4973. Therefore GET07 is not an unbounded lifetime counter; interval analysis must handle wrap/reset and calculation-mode changes. W-minute and0.1kWh interpretation is a **STRONG HYPOTHESIS**, consistent with the explicit scale and reference decoder, not a calibrated result.

CDAB4 derives thermal input from absolute signed flow/return difference0662−0664 and flow322E; applies constants6/86 and a bounded correction from07D7, then divides by1000 into31DA. CDBC0 adds a heater contribution and attributes it by496F; CDC62 divides by1000 for power3222. This is arithmetic from actual temperature/flow values, not a hidden precise compressor-COP sensor. P81's zero consumed-power field makes instantaneous COP undefined even though an energy counter changes.

Smallest follow-up: separately authorize a narrow repeated520–531 read-only-intent comparison, confirm format1BCD on21.00 against the display, exclude532 explicitly, and establish period boundaries before calling the counters “today”. Prefer exact21.00 firmware for further static work.
