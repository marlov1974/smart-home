# Flow target to request, FTC20.01

**CONFIRMED STATIC** means the pinned image, not installed21.00. Addresses below are hexadecimal. The connected ordinary zone1 fixed-flow chain is:

`SET32 RX2352/2353 -> A46FA/A4DDA -> B9BFE ->38DE -> B9C9E ->38D6 -> B9E16 ->38D4 -> BAB56 ->3908 -> A2C6A -> BA962 ->39EF ->9A336 ->9AEDE(selector10) ->08AA`.

B9AD0 requires2340=1 and0900!=2. The zone1 enable is2349 bit80; zone2 uses234A bit02. Mode bytes234E/234F pass A468E; modes2/5 are excluded from this target assignment. A46FA returnsFFFF when disabled; otherwise A4DDA assembles the two bytes **high first**. B9BFE ignoresFFFF, selects zone/mode and for zone0 mode1 stores38DE. These inspected helpers do not clamp temperature to a user range. This is evidence of a field path, not a new safe write recipe or proof all upstream validation is exhausted.

B9C9E selects by3916: mode1 copies38DE to38D6; mode2 copies38E0; room0 copies38DC. It also stages alternate38D8 (0733 for modes1/2) and38DA=4000. B9E16 normally selects38D6, selects38D8 when391B=1, and38DA when38BF=2 (last override wins). Thus accepted target and effective target need not agree. BAB56 modes3915=1/2 copy38D4 into3908 and391E/3920. Special49B3=2/3 plus39F7 high nibble20/30 substitutes07EF/07F1. Room mode0 instead callsBAE26 and retains2550/2552-derived state. BA9FC initializes3908 from BB962/38DE/38E0 by mode. Full room adaptation is outside the qualified model.

A2C6A selects3908 except3A4F=2 with3A56=3, which selects3910. A2BE0 selects0662 for ordinary single-circuit operation; multi-circuit paths select067E/0690/0682. The model's inputs are already selected targets/feedback and explicitly exclude special-target and room/DHW branches. It does not silently equate SET payload with effective target.

Sensor writer986E2 sets0662=0658 plus0729 only if0909=1. Writer98702 analogously sets0664=065A plus072B if090A=1. These prove calibration addition, not ADC filtering or its delay. 322E is the previously qualified water-flow quantity. Raw sensor conversion/filter time remains UNKNOWN.

BA8F0 computes heating error `max(selected_target,2500)-selected_feedback`, with signed16 subtraction; profile0900=2 substitutes3947. This **25C floor is local error shaping**, not a universal minimum accepted setpoint. BA962 copies selected target/feedback to39EF/39F1 without that floor, plus return0664 to39F3 and flow322E to39F5. It switches these sources for DHW/cooling. BA856 chooses3908 for heating reported38C1,3906 for DHW,390E for alternate DHW and390A for cooling; default390C is a separate fallback. Earlier exploratory focus on390C was corrected, not used as ordinary heating target.

9A336/9A39E clamp signed centidegrees to0..8000 then encode `ceil(value/50)`;9AEDE selector10 stores bytes08AA/08AB. 99F5A encodes error3949 as signed-word `(error+4000)/50`, truncating toward zero and clamping0..255. Its serializer consumers are a separate path; no claim that every peer uses all representations simultaneously.

Repeated identical assignments are locally idempotent in B9BFE/BAB56. These routines do not establish acceptance-to-control latency or prove no timer elsewhere is refreshed. Scheduling, wire transport completion and profile eligibility remain PARTIAL. Reported target, requested target and effective target must stay separate in future diagnostics.
