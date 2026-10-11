# UART0: storage-controller candidate

**Strong SD-controller hypothesis, not a measured CN108 binding.** User explicitly suggested SD during this package; the independent evidence matches it.

OCH722A p12 names CN108 as SD connector; p63 shows CN108 and LED4 for SD read/write. The firmware sends named files, reads512-byte blocks and writes dated logs. This is stronger evidence for storage than for a wall display. The UART would connect to a storage controller, not directly to an SD card's native SPI/SD bus.

C586C disables UART0, resets transport/application state and calls C4C7E for enable1. Main loop92482 invokes C5954(1) in both task phases; C5954 uses C921C for receive and C943E for transmit. C4C7E sets0248=65,024C=10,0249=CF; RX vectorFFD48→942A0→C4DFC, TXFFD44→944B8→C5004. RX3FB3→4455, TX41FA. Frame02, little-endian total length bytes1/2, additive checksum; capacity583, not a proven maximum for every operation.

There are38 receive records (8740C,14-byte stride) and38 transmit records (87A60,21-byte stride). Local transaction ID is not identical to a wire command. Output operation byte is52 ('R') or57 ('W') for file transactions,53/46 for two status/control forms. IDs1/2 use a dummy path;5 writes a dated log;6..21 read16 named settings files;22..37 write the corresponding files. The full row/handler inventory is in command-atlas and atlas-ledger.

| File | Read local ID | Write local ID | Working role |
|---|---:|---:|---|
|6_HW.DAT|6|22|DHW settings; C9760 packs3906 target and3912 mode|
|6_AC.DAT|7|23|Zone/mode/target settings; C979E packs3913/3914 and38DC..38F6|
|6_S1_1..5.DAT|8..12|24..28|Schedule family1; exact per-file/day layout remains open|
|6_HOL.DAT|13|29|Holiday block; fields not yet fully named|
|6_INI.DAT|14|30|Initial settings block; fields not yet fully named|
|6_SER1.DAT|15|31|Service block1; P84/P86 relate pump/energy imports|
|6_SER2.DAT|16|32|Service block2; field inventory incomplete|
|6_S2_1..5.DAT|17..21|33..37|Schedule family2; exact layout remains open|

C96E6 copies a64-byte filename entry from87620 into the outgoing block and invokes its selected payload callback. C94DC constructs A:\LOG\YYYY\MM\DD\HHMMSS.LOG. C939E copies512 bytes starting445C into2714+512*4454 for block index<5, then conditionally calls the import callback. C92BC checks the response operation against the selected record; response15 overrides normal matching with negative status. Internal26/27/28 mean accepted/mismatch-or-busy/negative; they are not proof of persisted disk writes.

Alternative: an external maintenance/file controller could implement this protocol and expose SD behind it. No literal filename proves the connector. No claimed direct SPI pins, SD card voltage, card controller model or MCU pin numbers. Next: trace enable/card-detect/LED4 GPIO and matched-board CN108 continuity; enumerate scheduler retry and file-import callbacks before constructing an emulator. No hardware action is enabled here.
