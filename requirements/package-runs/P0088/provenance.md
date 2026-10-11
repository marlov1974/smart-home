# P0088 provenance

Supplied FTC6 20.01 candidate, FF-filled binary base 80000, length 80000 hex. SHA256: `d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a`. This is not an identity claim for installed 21.00.

Ghidra 12.1.4 PUBLIC, Java 21.0.12.1+1, Python 3.14.7. P83 M16C language module remains unchanged, SHA256 `087e6afb29a7625e789b30467a12cad4ab2c2731e08a98c914969a308df3f46f`. EXITD, signed FB-bit displacement and indexed bit-address decompiler limitations are retained explicitly; see decoder-and-pin-corrections.md.

Private P88 work project and independent fresh-a/fresh-b copies derive from the completed P87 baseline. Prior package projects and published artifacts were not modified. P83Seed/P83Trace supplied targeted operands; P88SourceSwitch exports bounded branch control flow. No full firmware binary or assembly listing is included in this report.

Manuals already held locally: Mitsubishi OCH722A, printed pages 11–12, 20–23 and 63; Renesas M16C/60 software manual chapter 2.5, printed page 31; M16C/65 hardware manual R01UH0135EJ0210. Connector roles come from the Mitsubishi manual, while MCU pin/register identities come from the Renesas hardware manual. Their association to physical board wiring remains qualified.

The repeated extraction evidence covers twelve earlier targeted functions, seven source functions and sixteen bounded source switch branches. It does not establish complete semantic coverage. The later 9C660/9C77C receive/checksum extraction is a single clean-project extraction, separately qualified in source-link.md.

Continuation: nineteen further routines,23 outgoing switch branches and the24-instruction CECFA CFG match across fresh-a/fresh-b; hashes are in continuation-extraction.json. Scheduler/cancellation supporting exports are from fresh-a only. The A3 CFG exporter hashes the FF-filled reference and compares each used project byte; MOT gaps prevent treating one contiguous Ghidra memory read as the entire reconstructed binary.

Settings-transfer continuation:17 further assembly exports match across fresh-a/fresh-b; see settings-transfer-extraction.json. Direction polarity was checked against M16C/60 Software Manual STZX printedp128. This corrects a P88 prose error; the shared decoder and historical P86/P87 outputs remain unchanged.
