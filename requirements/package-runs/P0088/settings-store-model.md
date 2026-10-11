# P0088 — settings persistence model

Scope: static FTC20.01, image SHA256 d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a. Addresses are internal firmware addresses, not Modbus registers. Names below are analytical names, not recovered vendor symbols. No hardware was contacted.

## Contract and data ownership

An accepted setting, an active setting, a serialized setting and a physically saved setting are different states. The main loop92482 calls90ABA (including settings import) before9687C (background persistence). Import can therefore precede serialization in the same outer pass, subject to writer gates. See [application ordering](settings-apply-order.md).

| Store | Address | Role |
|---|---|---|
|Desired image|0CE4..0EE3|512 bytes assembled from active fields; frozen during an outstanding word write|
|Read/shadow image|0EE4..10E3|Startup read image, then writer bookkeeping; **not proof of successful persistence**|
|Startup copy|0AE4..0CE3|Copy of the last startup block read|
|Temporary comparison image|10E8..12E7|First of each pair of full-block reads|
|Verification results|10E4,10E6|Two reads of the word being written|
|Word offset|12E8|Even byte offset0..510; device word address is offset/2|

Two traced fields bridge the earlier input analysis to storage:

|Meaning|CN105 staging|Ordinary staging|Active|Image byte offset|Serialize / boot read|
|---|---|---|---|---|---|
|DHW pump level|197B|274F|0770|160 hex|0E44 /1044|
|Heating pump level|1CB0|2A84|07E6|1AB hex|0E8F /108F|

The heating pump byte shares its16-bit word with offset1AA. Neither this serializer nor this loader establishes a universal1..5 range. These are raw bytes.

## Named reconstruction

```text
settings_background_task()                         # 9687C
    if not writer.freeze_serialization:
        serialize_selected_profile()               # 94A54
    offset = first differing aligned word(desired, shadow)
    if offset exists:
        writer.current_offset = offset
        writer.pending = true
    if writer.pending:
        advance_word_writer()                      # 968E0

advance_word_writer()                              # simplified state semantics
    wait until delay_counter >= 6                  # wall-clock scale unresolved
    if not awaiting_verification:
        initialize retry count if starting a word
        request word write(offset/2, desired_word)  # 948A2 ->9495A
        reset delay_counter
        freeze serialization; await verification
    else:
        issue write-disable                        # 94998
        first = read_word(offset/2)
        second = read_word(offset/2)
        if first == second == desired_word:
            shadow_word = desired_word
            clear retry count and pending/freeze state
        else:
            increment failed-verification count
        leave verification phase
    if failed-verification count > 2:
        storage_status.bit2 = 1                    # 08DA
        shadow_word = desired_word                 # ALSO ON FAILURE
        clear retry count and pending/freeze state
```

The last branch is consequential: after three unsuccessful verifications, a word stops appearing dirty even though physical persistence has not been verified. The pure `settings_store.verify_word` model preserves `accounted` and `persistence_verified` separately. A caller must not equate desired==shadow with a saved configuration.

`94A54` chooses among serializers by3AD2. The default branch94A82 packs active fields, including the two pump bytes above. Profile6 instead uses8AE38. Other profiles3/4/5 have different serializers; their layouts are not generalized here.

## Boot and defaults

`911BC` calls96A18 to read the image,9804E for selected validation checks, and96AF4 to unpack settings. `96A18` tries up to three pairs of full512-byte reads. Each pair is compared byte-for-byte; a match ends retries. Even after the final mismatch, the last read is copied to0AE4. Do not infer rejection or a global512-byte checksum from this routine. `9804E` checks selected fields and sets3CEF; its full recovery implications remain open.

If3AE1==1,94A82 calls959DE before serializing and clears the request. `959DE` restores fields from a ROM profile, including the same160/1AB offsets. `91310` selects bases8000A,8020A or8040A using08F6. Profile identities and the external trigger are not yet established. This is a ROM-default restore path, not an EEPROM comparison routine.

## Serial-memory driver

`948A2` configures P1.7/P1.4/P1.5 as outputs and P1.6 as input (PD1=03E3). Read requests take priority over write requests. `949B0` shifts output MSB first; the read routine948D4 samples each incoming bit three times and uses a majority decision.

|Operation|Routine|Logical bits emitted|
|---|---|---|
|Read word|948D4|110 +8-bit word address, followed by16 received bits|
|Write word|9495A|101 +8-bit word address +16 data bits|
|Write enable|9497E|100 +11000000|
|Write disable|94998|100 +00000000|

The software organization is256×16 bits. This is consistent with a Microwire-style EEPROM interface. It does not identify the physical chip or establish board continuity. P1.7 acts as select, P1.4 as clock, P1.5 as output and P1.6 as input in these routines. MMIO optimizations and stale Ghidra function bodies make the decompiled clock helper misleading; its full bounded assembly is the source of truth.

## Fault and delay follow-through

`89D6A` sets3ACF.bit1 when08DA.bit2 is set (or33F9.bit4 independently requests it). `984D2` mirrors08DA.bit2 into075A.bit3. This proves propagation beyond the writer, but not a particular display fault code or whether every product profile uses both paths. Neither reviewed consumer clears08DA.bit2.

`94A46` increments3CED and caps it at6 during normal operation. Its caller/timebase is still unresolved, so the writer threshold cannot yet be labeled milliseconds. The bounded94A20..94A44 clock helper is31 instructions: bit set,28 NOPs, bit clear, return. Two private project exports agree. The first attempted bound included unmapped padding at94A45 and correctly failed; no missing bytes were manufactured.

## Separate bulk verification path

Profile6's8AE38 accepts a512-byte image plus an8-bit additive checksum from365F onward. On checksum match it acknowledges06, copies the incoming image to desired, and complements shadow to force writes. On mismatch it returns15. Later8AEC0 waits for desired==shadow, then **performs another physical block read** through96A18 and compares it with the incoming image before final06/15. Thus this path adds a physical verification that ordinary shadow equality lacks. Its connector/session reachability remains unresolved; this is not a proposed live command.

## What this unlocks next

Follow3ACF.bit1/075A.bit3 into visible fault behavior; qualify the delay-counter caller/timebase; connect default/profile selection to known product variants; then follow the active field consumers into control logic. The persistence model supplies reliable state names for those investigations without assuming every accepted command is durable.
