# Settings application precedes transaction completion

Static FTC20.01 finding; no hardware calls. This closes application ordering, not persistence or a complete peer transaction.

## One-pass import event

`CF0E0` in write state3 receives C8 action1, callsCF846 and sets2372=4. CF846 copies the selected category1..7 to2373. The main pass90ABA calls the settings taskCEE20 near its beginning, then the target/control tasks, thenBC0D8. BC0D8 callsBC2C0, BC9DA, BD166 andBC0E6 in that order. BD166 consumes2373; for category6 it calls bothBD296 andBD780. The final main-pass cleanup90BD4 clears2373, along with transient communication/event flags.

The write handshake waits for CF978's extended end event while already in state4, and only then moves to5. Therefore the native import is **not deferred until transaction close**. An error or timeout that resets2372 does not establish that active settings remained unchanged. No rollback of imported values is present in the reviewed session-reset helperCF518; a global claim about every other recovery path would require further tracing.

## Concrete import groups

| Category/event | Consumer | Selected effects |
|---|---|---|
|1|BB9DC, BBFCA|1945 converts into DHW target3906;1951 becomes3912 boolean. BD166 also callsBD190.|
|2|B984A, BBBEA|Ten staged target bytes update zone target slots38DC..38F6 throughC50BC;1942/1945 feed mode slots3913/3914 throughC5176.|
|4|BD166|CallsBD20E; full field meanings still to qualify.|
|5|BD166|CallsBD28E; full field meanings still to qualify.|
|6|BD296 and BD780|Imports many DHW/heating parameters, including197B→0770 (DHW pump level) and1CB0→07E6 (heating pump level), plus all listed neighboring fields in these routines.|

This is a list of the reviewed direct consumers, not a proof that categories3/7 have no effects. No final per-setting persistence claim is made.

## Two input stores, shared active settings

BC9DA uses a different event4452. When4452=10(hex), it imports the ordinary store throughBCB0A andBCFF4. For the pump examples that is274F→0770 and2A84→07E6. In the same pass, BD166 runs **after** this importer and can override those active fields from CN105 staging when2373=6. Cleanup90BD4 clears both event fields.

These stores must not be confused with one another or with nonvolatile memory. Their later save/reload mechanisms remain a separate edge.

## Transfer-table coverage is not full setting coverage

The33 records at807EA map extended D selectors to three-byte staging records. Selectors120 and589 alias1979..197B; the final byte is consumed as the DHW pump level in category6. No selector in this finite table maps any byte of the heating-pump location1CB0. CN105 SET79 stages1CB0 directly, andBD780 imports it. Thus this transfer table is not a complete inventory of all reachable settings, and its numeric aliases cannot be used without category context.

## Direction correction and decoder caution

The previous P88 settings-d-events.md incorrectly said that bit5 was complemented. At8BD13 the firmware tests050B.bit5; STZX0,1 stores0 when clear and1 when set;8BD7E compares that result with4980. **The two directions must match.** This is supported by M16C/60 Software Manual STZX, printedp128, and a regression test for both directions. The caller sets the handler's transfer-kind argument to2 at8B916; this argument is not a fresh lookup of the A3 service-class table.

Separately,923BC's C output incorrectly collapses toreturn0 because local bit writes use the known signed-FB defect. Its assembly checks07E6 against3 as one of several gates; it does not clamp or rewrite the pump level. Do not infer validation or a universal1..5 limit from that helper.

The remaining end-to-end obstacle is the D peer's scheduling and accepted start/data/end/close behavior. FTC's internal1005 announcement and1002 responses now explain its side; the peer firmware is absent. This finding does not justify invented packet bytes or a live settings write.
