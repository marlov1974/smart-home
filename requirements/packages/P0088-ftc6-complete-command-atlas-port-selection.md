# P0088 — FTC6 complete command atlas, functional port identification and Procon port choice

## Status and operator intent
Ordered independent Codex research package after P0087. Do not expand, rewrite or interrupt P0086/P0087 work or reuse a Ghidra project while another run is writing it. Consume their committed handoffs and preserve historical findings; corrections belong here.

The operator wants a concrete answer to three questions:
1. What can each communication path and physical port read, configure, command or otherwise do — a complete itemized list, not a table of generic port roles?
2. Can the functions implemented on each path identify which UART belongs to CN22, CNRF, CNIT, CN105 or the internal control-board link?
3. Which previously missed direct/parameterized/indirect commands can our Procon use on CN105, and would a qualified CNIT connection actually provide a more complete feature set?

Primary deliverable: a reproducible, field-level command atlas and a defensible port-selection decision. This is NOT another zero-parameter live scan, a repetition of P0085's UNKNOWN matrix, or a search restricted to the publicly known GET list. Do not infer a universal YES/NO about display parity from a few selected handlers.

Authorized completion: offline firmware analysis, package-local extractors/decoders/tests, documentation and commit/push of verified scoped results. No device connections, live GET/SET, automatic serial discovery, mode/DIP changes, cable moves, heat-pump actuation, firmware deployment or protection changes. Catalog mutating operations as well as reads; cataloging a command does not authorize sending it. Missing hardware evidence must not stop software command enumeration.

Use supplied FTC20.01 as the working reference. Firmware21.00 is useful, not a general prerequisite. Separate command compatibility hypotheses, static reachability and actual P0081/21.00 observations. Never transplant absolute RAM addresses across revisions.

## Evidence and baseline
Follow AGENTS.md, package bootstrap and REPOSITORY_FILES.md. Read P0081 physical command-map and implementation-report; P0083 service/energy/pump traces; P0084 settings, screen and transport traces; P0085 protocol/access-gate findings; P0086 CHANGELOG, findings, energy-qualification, settings-session, UART1 reports; and P0087 CHANGELOG/controller-boundary plus relevant target/actuator traces. Read current Procon modular code and docs to compare capabilities, not historical firmware alone. Inspect the pinned F1p/gekkekoe implementations for the known-command baseline.

Use existing local Ghidra project and validated M16C decoder. Pin input/tool hashes. Prior reconstructed binary SHA-256: d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a. No full vendor binary, ID file, full proprietary listing, device identities or private raw traces should be published.

Important retained/corrected facts:
- P0081 scanned only standard zero-parameter GET0x42 codes and a documented A3 subset. A TIMEOUT, zero or FF reply does not establish absence; no broad parameterized/settings/other-frame-type inventory was performed.
- P0086 shows that A3 energy queries can fold pending accounting and lose remainders, and that the odd BCD result truncates digits. Preserve those side effects in the atlas. Service532 snapshots/clears counters;340 also mutates state. A3/GET is not synonymous with non-mutating.
- P0086 proves the reviewed UART1 memory load is near 16-bit even though its request accepts a wider address. Do not re-advertise it as a full-flash dump. Log reads drain a small buffer and omit some original wire data.
- CN105 settings routes and their incomplete internal handshakes are documented, including SET C8 and SET/GET65/79. Distinguish a command handler, a staged field, application, persistence and a complete operational transaction.
- The user provided M16C board photographs, including markings read as R5F3651TNFC and R5F364AENFB, plus a MAC-597IF-E label. Do not dismiss the M16C photographs as STM32 Procon photos. Confirm photograph-to-board association and exact package before using pin numbers. R5F3651TNFC is a 128-pin candidate; do not import a 100-pin pinout.
- MAC-597IF-E was attached to CNRF but never worked. It is not evidence of protocol equivalence. CN105 works with Procon. Do not ask again for the already supplied adapter model.

Official starting references: Renesas M16C/65 datasheet R01DS0031EJ0210 (https://www.renesas.com/en/document/dst/m16c65-group-datasheet), corresponding hardware/software manuals, and the supplied Geodan service/installation manuals. Product/connector names across Mitsubishi families are not transferable pinout evidence. The meaning of IT in Geodan CNIT requires a traceable source; leave the abbreviation unexpanded if none is found.

## A. Close the communication-path inventory first
Inventory every serial-capable path on the actual MCU profile, not just UART0/1/2. The M16C/65 datasheet lists UART0/1/2/5/6/7, synchronous SI/O3/4 and other serial/remote-control hardware. Check their actual use and GPIO/timer software links. Hardware availability does not prove active firmware use.

A new lead from the conversation is code around 0x0BFD16 apparently initializing U6MR=0x65 at0x0298, U6C0=0x11 at0x029C and U6BRG=0x67 at0x0299. Independently verify the opcodes, MCU register mapping, initialization caller, enable conditions, RX/TX vectors or polling, buffers and dispatcher. Equal UART2/UART6 register values do not prove equal protocols. Give this lead priority because prior inventories omitted UART5/6/7.

For each hardware/software path report: stable path ID; peripheral/registers; init/enable/disable conditions and variant selection; RX/TX root and buffer ownership; framing/length/checksum; parser and dispatcher roots; use as asynchronous UART versus synchronous peripheral; and active/conditional/init-only/unused/not-yet-established classification. Trace indexed and indirect register writes, callback tables and pin multiplexing, not literal-address matches only.

Include CN22, CN105, CNRF, CNIT and CN3C in the physical-port inventory. Also account for SD/storage controllers, internal daughterboards or shared/multiplexed routes if the code supports them. Do not force one port per UART, or count UART1's two personalities as two separate ports. A broad file/configuration transport could belong to a storage/service component rather than the screen.

## B. Exhaustive static command enumeration per active path
Work bidirectionally: RX parser -> dispatch -> operation/data -> response, and known setting/sensor -> readers/writers -> dispatch -> transport. Export command maps mechanically from bounded tables, switches and predicates, preserving default cases, aliases, subdispatchers and unresolved indirect targets.

Starting roots to revalidate, not an exhaustive inventory:
- CN105: descriptor family892A8, lookups84B56/84C56, output descriptors84D56, parserA4F68, SET dispatcherA90F8 and responseA535E. Enumerate ALL accepted frame descriptors, not only FC/42 GET: normal SET, connect/configuration and alternate 02-framed families where actually present. Interpret type0x5A by its handler, not as a presumed bootloader command.
- A3/shared services: class table806AC, selector dispatcher8C0B4, local and forwarded paths, filters and shared state. Recover the implemented selector domain and ranges from code, not an assumed0..255 or0..999 limit. Catalog internal services1002..1005 separately from externally accepted A3 selectors and do not equate their numerical identity with external reachability.
- Settings sessions: SET C8, state2372, category4981 and import phase2373, including prerequisite internal acknowledgment. Enumerate all categories and all recognized settings blocks, not just the pump pair.
- UART0: RX C4DFC/C4D04, table8740C (reported38 x14 bytes), table87A60 (reported38 x21 bytes), C921C/C9278 and C943E/C94A6. Account for every entry and callback and establish which traffic actually reaches it.
- UART1: both personalities and all low/high-nibble/subcommand branches, not only the offline reader's implemented safe subset. Statically classify service-loop and maintenance branches without activating them. Reuse P0086's completed proof.
- D-path: 9F152, translation832FE, transition matrix88F65, switch9F31A and all reachable normalized commands/classes, not only service-read opcode14. Trace outgoing response/event packing too.
- UART5/6/7 and any newly discovered path: apply the same extraction and coverage criteria after confirming active code.

For parameterized fields, represent accepted ranges/masks/conditions symbolically and test their boundaries offline. Do not brute-force every possible payload on hardware. Include asynchronous events, peer-originated requests, handshakes, bulk transfers and commands requiring state sequences; not every protocol is request/response or Procon-master compatible.

### Required row schema
Every command/subcommand/meaningful parameter field gets a stable identifier and a machine-readable record containing:
- firmware/profile; software path; physical port attribution/confidence kept separately;
- wire frame type, opcode, subopcode/service selector, address/zone/category and direction;
- exact RX and TX field positions, length, endianness, signedness, scale/unit/range or explicit unknown;
- functional name, operation class (read/status, setting, live control, transient state, persistent write, clear/reset, destructive/maintenance, forwarding, event);
- implemented accepted-value predicate, session/role/mode/category/ownership gates and scope;
- actual handler, data source/sink, shared setter/getter and forwarded peer boundary;
- acceptance versus completion, response/error semantics, latency/update cadence when established, persistence, side effects, retry/idempotence and failure/exit behavior;
- reachability proof and confidence in interpretation; physical validation status separately;
- baseline classification: already in Procon, known public reference only, newly explained from existing P81 reply, newly found static command, unresolved;
- minimal offline fixture/operand evidence and smallest later physical verification need.

A handler called internally is not an externally callable command until a complete accepted route is shown. Same numeric command on two paths need not mean the same function. Preserve unknown bytes and distinguish genuinely ignored bytes from fields tested only in another state.

## C. Complete functional catalog and role identification
Produce the primary human-readable output grouped by functions, one action per row with separate READ and WRITE columns per path. Obtain the screen menu inventory from the applicable manual, not from an assumed short feature list. At minimum cover:
- all temperature/flow/pressure/current/voltage/frequency readings present in the image; requested versus actual versus historical values;
- brine, water pumps, compressor requests/limits, valves, mixing circuits, heaters and operating states;
- configured heating/DHW pump levels versus instantaneous PWM, any automatic flow behavior and timers;
- normal power, heating/DHW/cooling permission, modes, targets, zones, curve-point editing (not merely selecting curve mode), schedules and holiday;
- DHW normal/ECO, boost, limits/priorities/timers and hygiene cycles; distinguish these semantics;
- room controllers: identity/pairing/zone assignment, temperature reporting, target changes, link supervision, battery/status where implemented, and user commands;
- energy running/snapshot/history counters, meter configuration/calibration, field precision and query side effects;
- service settings, thermistor adjustments, economy/flow settings, passwords/language/time/UI-local functions, error history/reset and manual test actions;
- diagnostic logs, bounded memory operations, configuration/files/SD transfers and maintenance/update paths if present.

Expand these categories into all found fields/actions; this list is a minimum taxonomy, not permission to report only those examples. For every documented menu action absent from located code, identify screen-local candidate versus untraced FTC function versus not applicable to this model. Do not mark UNKNOWN as NOT SUPPORTED.

Identify roles from multiple independent signatures, then seek documentary/pin confirmation:
- A room-receiver candidate should explain multiple room identities, reporting/link state and limited user requests. A narrow accessory UI alone does not prove a narrow parser capability set.
- A screen candidate should explain broad menu-setting transactions and bidirectional presentation/state traffic; generic bulk settings/file transfer alone is insufficient.
- A source-controller candidate should explain heating requests plus returned compressor/brine/limit data, not be misnamed screen because both use services.
- A service/IT candidate may expose maintenance/log/configuration functions. This is not proof that CNIT is that path or that it is a superset of CN105.

Provide a ranked path-to-port assignment with positive AND contradictory evidence and the smallest discriminating observation. Make a supported working assignment when evidence permits; avoid leaving all cells UNKNOWN without attempting the functional comparison. Keep physical identity distinct from strong software-role inference.

## D. Find missed CN105 capabilities explicitly
Cross-reference all atlas entries against the pinned public code, existing modular Procon implementations and P0081 raw coverage. Deliver a concise delta list with the exact functional benefit and complete/partial reachability:
1. New direct GET fields or commands.
2. Parameterized or session-dependent reads that zero-filled P81 requests could not reveal.
3. New direct SET fields/blocks and their full neighboring-field effects.
4. Indirect A3/service reads AND actions, with local versus forwarded distinction.
5. Other descriptor/frame families providing an alternative to an A3-restricted operation.
6. Functions genuinely blocked by a specific guard, not globally absent.

Do not stop at discovering another handler: trace where a useful function's value is loaded/stored, what acknowledges it, and whether the caller can reach it using an established protocol transaction. Where a sequence remains incomplete, give the precise missing edge rather than publishing guessed packet bytes. Existing service-query side effects and UART1 aliasing are required regression controls.

## E. Compare port choice and feasibility of Procon on CNIT
Calculate functional set differences relative to CN105 **including its special sessions**, not only its current public GET subset. For each attributed port state whether it is a demonstrated superset, subset, overlapping/incomparable set, or unresolved. Support any claim with individual action rows and conditions. More memory/debug access does not imply more normal heating-control authority.

Define two separate parity targets:
- All documented screen/FTC user-and-installer actions, with display-local actions explicitly accounted for.
- The operator's needed L2 feature set: stable AUTO/fixed-flow/heating-DHW permissions, primary pump levels, service/limit feedback, useful energy telemetry and recovery/ownership behavior.

For CNIT (and any stronger alternative) deliver a Procon adaptation assessment:
- exact electrical compatibility or required external adaptation: power, ground/reference, logic levels, inversion, protection/isolation and pinout; connector color/shape is not evidence;
- byte protocol, baud/parity/duplex, master/slave role, addressing, handshake/session and scheduling/unsolicited traffic;
- role coexistence with screen, native controller, source board and MELCloud, including loss-of-link and reboot behavior;
- which firmware modules need changes, effects on CN105 code/BL2 ownership, stable ABI and measured/estimated code/RAM impact using the current layout rather than obsolete8/4/2KiB assumptions;
- new usable functions, lost functions, control restrictions and unresolved dependencies;
- recommendation: keep CN105, extend CN105 support, candidate migration to CNIT with listed adaptation, an active bridge/multiplexer if actually justified, or insufficient evidence. Do not recommend passive parallel attachment of active transmitters.

The port map can be inferred functionally before wiring is measured. A physical migration recommendation still requires electrical qualification. Neither a different parser nor an apparent service role guarantees complete feature parity. Do not wait for21.00 just to implement the offline atlas, but do not claim20.01-specific addresses or behavior as physically proved21.00.

## F. Completeness and acceptance — measurable, not rhetorical
Keep three independent coverage metrics:
1. Structural inventory: peripheral/driver/descriptor/table/selector branches accounted for versus total verified entries; defaults, disabled variants, internal-only routes and unresolved callbacks listed.
2. Semantic coverage: named actions/fields with proven effects versus inventoried actions/fields. A table full of renamed UNKNOWN rows is not a complete semantic analysis.
3. Physical attribution/validation: connector mappings and command behaviors independently corroborated versus inferred/unverified.

For every table publish base, stride/count/bounds evidence, entry IDs and dispositions. No silent dropped entries or invented denominator. A remaining indirect branch prevents claiming closure of that path; it does not prevent useful per-path reports. Support count100% only for the explicitly proved finite scope, not every possible feature in unknown firmware or an absent peer MCU.

Report COMPLETE/PARTIAL/BLOCKED per path and the exact residual list. A time-bounded unfinished investigation must retain an executable extraction plan and last resolved edges, not declare that all functions are known. Do not turn unresolved physical connectors into a reason to omit the software catalogs.

Required checks: deterministic extraction on two fresh targeted runs; schema consistency; every extracted row represented in the human report; nested dispatch and alias coverage; known CN105/P81 mappings as regression anchors; corrupted table/invalid length/wrong image/missing reference rejection; separate MCU-only from physical tests; zero network/serial calls in default tooling; P86 energy-side-effect and UART1-addressing regressions; git diff --check and repository-index consistency. Synthetic success is not physical qualification.

## Deliverables and boundaries
Create requirements/package-runs/P0088/ with review.md, design.md, functions.md, provenance.md, transport-inventory.md, command-atlas.json, command-atlas.csv, function-matrix.md, cn105-new-capabilities.md, port-role-analysis.md, procon-port-choice.md, coverage.json, unresolved-handlers.md, findings.md, reproduce.md, verification.json and CHANGELOG.md. Keep per-path detail files where needed. Executive report must lead with concrete newly identified functions, strongest port assignments and Procon recommendation, not long lists of addresses.

Add portable extraction/report/test tools under tools/ftc6/p88/. Only minimal declared shared-helper changes are allowed with compatibility tests. Relevant function-catalog and knowhow updates are permitted. Current Procon firmware/deploy artifacts, P0086/P0087 outputs, device configuration and unrelated source are read-only. No new live mapper allowlist or production backend is enabled by this package.

Use official documents and source/code evidence with exact pages/addresses/hashes. Original board photographs supplied in the conversation may be needed locally; ask only for an actually missing exact view or board identifier. Finish by updating the tracked file index and reporting commits, reproducible commands, coverage, precise unknowns and zero live actions. This requirement orders the analysis; it does not predeclare its results.
