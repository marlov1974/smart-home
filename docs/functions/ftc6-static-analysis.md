# P0082 static analysis tooling

`tools/ftc6/inspect_image.py`: parse_srec validates records into a sparse map; inspect_image emits integrity/address/vector/string evidence. Optional reconstructed bytes go only to a caller-specified local path.

`P82Audit.java`: synthetic instruction decoding, documented direct-edge assistance, image-specific descriptor-table seeds, local listings/references and independent memory digest. No live I/O.

`run-analysis.sh`: rejects unrecognized input hash, requires explicit local output and executes MotorolaHexLoader at actual addresses.

`test_inspect_image.py`: six synthetic validation tests. Processor semantics remain partially qualified; see P0082 reports before use.
